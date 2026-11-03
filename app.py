#!/usr/bin/env python3
"""Notebooks: academic notes kept as books. Each book is a folder in ~/Notebooks, each page is a file in it."""
import json, mimetypes, os, re, shutil, subprocess, sys, tempfile, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote, unquote

ROOT = Path(os.environ.get("NOTEBOOKS_DIR", Path.home() / "Notebooks"))
HERE = Path(__file__).resolve().parent
IMAGES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
OFFICE = {".doc", ".docx", ".odt", ".rtf", ".ppt", ".pptx", ".odp", ".xls", ".xlsx", ".ods"}
VIDEOS = {".mp4", ".m4v", ".webm", ".mkv", ".mov", ".ogv"}
YTDLP = shutil.which("yt-dlp") or str(Path.home() / ".local/bin/yt-dlp")  # app-menu launches may not have ~/.local/bin on PATH
render_lock = threading.Lock()


def safe_name(name):
    name = name.strip()
    if not name or name.startswith(".") or "/" in name or "\\" in name or "\0" in name or len(name) > 200:
        raise ValueError(f"Invalid name: {name!r}")
    return name


def book_dir(book):
    return ROOT / safe_name(book)


def pages(book):
    return sorted(p.name for p in book_dir(book).iterdir() if p.is_file() and not p.name.startswith("."))


def new_page_path(book, name):
    # Number prefix keeps pages in the order they were added, also in a file manager.
    nums = [int(m[1]) for p in pages(book) if (m := re.match(r"(\d+) ", p))]
    return book_dir(book) / f"{max(nums, default=0) + 1:03d} {name}"


def run(cmd):
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3 * 3600)
    except FileNotFoundError:
        raise ValueError(f"{Path(cmd[0]).name} is not installed")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"{Path(cmd[0]).name} failed: {(e.stderr.strip().splitlines() or ['unknown error'])[-1]}")


def download_video(book, url, fmt):
    """Download a YouTube video into the book as a new page, in the chosen video format."""
    if f".{fmt}" not in VIDEOS:
        raise ValueError(f"Unsupported format: {fmt}")
    if urlparse(url).scheme not in ("http", "https"):
        raise ValueError("Paste the full link, starting with https://")
    book_dir(book)  # validates the book name before downloading anything
    with tempfile.TemporaryDirectory(prefix=".download-", dir=ROOT) as tmp:
        # WebM comes straight from YouTube; every other format starts from an H.264/AAC MP4, which plays everywhere.
        choice = "bv*[ext=webm]+ba[ext=webm]/b[ext=webm]" if fmt == "webm" else "bv*[vcodec^=avc1]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b"
        node = shutil.which("node")  # newer YouTube pages need a JS runtime for some formats; works without, with a warning
        run([YTDLP, "--no-playlist", "-f", choice, "--merge-output-format", "webm" if fmt == "webm" else "mp4",
             *(["--js-runtimes", f"node:{node}"] if node else []),
             "-P", tmp, "-o", "%(title).150B.%(ext)s", "--", url])  # .150B caps the title only; --trim-filenames would cut the folder path too
        src = next(Path(tmp).iterdir())
        if src.suffix != f".{fmt}":
            out = src.with_suffix(f".{fmt}")
            # OGV needs Theora/Vorbis, so it is re-encoded (slow); the others only change container (instant).
            codecs = ["-c:v", "libtheora", "-q:v", "7", "-c:a", "libvorbis", "-q:a", "5"] if fmt == "ogv" else ["-c", "copy"]
            run(["ffmpeg", "-loglevel", "error", "-i", str(src), *codecs, str(out)])
            src = out
        dest = new_page_path(book, src.name.replace("\\", "-"))
        if dest.exists():
            raise FileExistsError(dest)
        shutil.move(src, dest)
    return dest.name


def file_url(book, rel):
    return quote(f"/files/{book}/{rel}")


def render(book, page):
    """Turn one page's file into something the viewer can show: images (for PDFs and office docs) or text."""
    src = book_dir(book) / safe_name(page)
    if not src.is_file():
        raise FileNotFoundError(page)
    ext = src.suffix.lower()
    if ext in IMAGES:
        return {"kind": "images", "images": [file_url(book, page)]}
    if ext in VIDEOS:
        return {"kind": "video", "url": file_url(book, page)}
    if ext == ".pdf" or ext in OFFICE:
        cache = book_dir(book) / ".pages" / page
        with render_lock:
            if not cache.exists() or cache.stat().st_mtime < src.stat().st_mtime:
                shutil.rmtree(cache, ignore_errors=True)
                cache.mkdir(parents=True)
                try:
                    pdf = src
                    if ext in OFFICE:
                        # Own profile dir so conversion works even while LibreOffice is open.
                        profile = Path.home() / ".cache" / "notebooks-libreoffice"
                        subprocess.run(["libreoffice", f"-env:UserInstallation=file://{profile}", "--headless",
                                        "--convert-to", "pdf", "--outdir", str(cache), str(src)],
                                       check=True, capture_output=True, timeout=300)
                        pdf = cache / (src.stem + ".pdf")
                    subprocess.run(["pdftoppm", "-r", "130", "-png", str(pdf), str(cache / "p")],
                                   check=True, capture_output=True, timeout=300)
                except Exception:
                    shutil.rmtree(cache, ignore_errors=True)  # don't leave a half-rendered cache that looks fresh
                    raise
        # pdftoppm zero-pads page numbers, so name order is page order
        return {"kind": "images", "images": [file_url(book, f".pages/{page}/{i.name}") for i in sorted(cache.glob("p-*.png"))]}
    try:
        return {"kind": "text", "text": src.read_text()}
    except UnicodeDecodeError:
        return {"kind": "unsupported"}


class Handler(BaseHTTPRequestHandler):
    def send(self, code, body, ctype="application/json"):
        if not isinstance(body, bytes):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, f):
        """Stream a file in chunks, honouring Range requests so videos can seek without loading into memory."""
        size = f.stat().st_size
        start, end = 0, size - 1
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if m and (m[1] or m[2]):
            if m[1]:
                start, end = int(m[1]), min(int(m[2]), size - 1) if m[2] else size - 1
            else:
                start = max(size - int(m[2]), 0)  # "bytes=-N" means the last N bytes
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.send_header("Content-Length", "0")
                return self.end_headers()
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(f.name)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        self.end_headers()
        with open(f, "rb") as fh:
            fh.seek(start)
            left = end - start + 1
            try:
                while left and (chunk := fh.read(min(left, 1 << 20))):
                    self.wfile.write(chunk)
                    left -= len(chunk)
            except (BrokenPipeError, ConnectionResetError):
                pass  # the player dropped the connection after seeking elsewhere

    def handle_request(self, method):
        # Host check blocks DNS rebinding; the custom header forces a CORS preflight, so websites can't POST here.
        if self.headers.get("Host") != f"127.0.0.1:{self.server.server_port}":
            return self.send(403, {"error": "Bad host"})
        if method == "POST" and self.headers.get("X-Notebooks") != "1":
            return self.send(403, {"error": "Missing header"})
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            self.route(method, url.path, q)
        except ValueError as e:
            self.send(400, {"error": str(e)})
        except FileExistsError:
            self.send(409, {"error": "That name already exists"})
        except FileNotFoundError:
            self.send(404, {"error": "Not found"})
        except subprocess.SubprocessError as e:
            self.send(500, {"error": f"Could not render this file ({e})"})

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def log_message(self, *args):
        pass

    def route(self, method, path, q):
        if method == "GET" and path == "/":
            return self.send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if method == "GET" and path == "/api/books":
            books = [b.name for b in sorted(ROOT.iterdir()) if b.is_dir() and not b.name.startswith(".")]
            return self.send(200, [{"name": b, "pages": len(pages(b))} for b in books])
        if method == "GET" and path == "/api/book":
            return self.send(200, pages(q.get("name", "")))
        if method == "GET" and path == "/api/page":
            return self.send(200, render(q.get("book", ""), q.get("page", "")))
        if method == "GET" and path.startswith("/files/"):
            book, _, rel = unquote(path[len("/files/"):]).partition("/")
            base = book_dir(book).resolve()
            f = (base / rel).resolve()
            if not f.is_relative_to(base) or not f.is_file():
                raise FileNotFoundError(rel)
            return self.send_file(f)
        if method == "POST" and path == "/api/books":
            book_dir(q.get("name", "")).mkdir()
            return self.send(201, {})
        if method == "POST" and path == "/api/upload":
            dest = new_page_path(q.get("book", ""), safe_name(q.get("name", "")))
            left = int(self.headers.get("Content-Length", 0))
            with open(dest, "xb") as f:
                while left and (chunk := self.rfile.read(min(left, 1 << 20))):
                    f.write(chunk)
                    left -= len(chunk)
            if left:
                dest.unlink()
                raise ValueError("Upload was interrupted")
            return self.send(201, {"page": dest.name})
        if method == "POST" and path == "/api/youtube":
            # shortcut: no progress bar, the request waits until the download finishes; add a job + polling if long videos feel stuck.
            return self.send(201, {"page": download_video(q.get("book", ""), q.get("url", ""), q.get("format", "mp4"))})
        raise FileNotFoundError(path)


def open_window(url):
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("WebKit2", "4.1")
    from gi.repository import Gtk, WebKit2
    win = Gtk.Window(title="Notebooks")
    win.set_default_size(1200, 900)
    view = WebKit2.WebView()
    view.load_uri(url)
    win.add(view)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    ROOT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", int(os.environ.get("NOTEBOOKS_PORT", 0))), Handler)
    url = f"http://127.0.0.1:{server.server_port}/"
    if "--serve" not in sys.argv:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            open_window(url)
            sys.exit()
        except (ImportError, ValueError):
            webbrowser.open(url)  # no GTK/WebKit: fall back to the default browser
    print(f"Notebooks running at {url} (Ctrl+C to stop). Books are in {ROOT}")
    server.serve_forever() if "--serve" in sys.argv else threading.Event().wait()
