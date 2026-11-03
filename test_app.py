"""Self-check: python3 test_app.py (uses a temp folder, never touches ~/Notebooks)."""
import json, os, subprocess, tempfile, threading, urllib.request, urllib.error
from urllib.parse import quote

os.environ["NOTEBOOKS_DIR"] = tempfile.mkdtemp()
import app

server = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{server.server_port}"


def call(path, data=None, headers={"X-Notebooks": "1"}):
    req = urllib.request.Request(BASE + path, data=data, headers=headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# Two-page PDF made with LibreOffice from a text file containing a page break.
tmp = tempfile.mkdtemp()
with open(f"{tmp}/notes.txt", "w") as f:
    f.write("Page one\n\fPage two\n")
subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, f"{tmp}/notes.txt"], check=True, capture_output=True)
pdf = open(f"{tmp}/notes.pdf", "rb").read()

assert call("/api/books?name=History", b"")[0] == 201
assert call("/api/books?name=History", b"")[0] == 409
assert call("/api/books?name=..", b"")[0] == 400
assert call("/api/books?name=a/b", b"")[0] == 400
assert call("/api/books?name=x", b"", headers={})[0] == 403          # no custom header
assert call("/api/upload?book=History&name=" + quote("Week 1 #intro.pdf"), pdf)[0] == 201
assert call("/api/upload?book=History&name=summary.txt", "Rome fell in 476.".encode())[0] == 201

books = json.loads(call("/api/books")[1])
assert books == [{"name": "History", "pages": 2}], books
pages = json.loads(call("/api/book?name=History")[1])
assert pages == ["001 Week 1 #intro.pdf", "002 summary.txt"], pages

pdf_page = json.loads(call(f"/api/page?book=History&page={quote(pages[0])}")[1])
assert pdf_page["kind"] == "images" and len(pdf_page["images"]) >= 1, pdf_page
status, png = call(pdf_page["images"][0])
assert status == 200 and png[:4] == b"\x89PNG"
assert json.loads(call(f"/api/page?book=History&page={quote(pages[1])}")[1]) == {"kind": "text", "text": "Rome fell in 476."}

video = bytes(range(10))  # contents don't matter, only how the bytes are served
assert call("/api/upload?book=History&name=lecture.mp4", video)[0] == 201
video_page = json.loads(call(f"/api/page?book=History&page={quote('003 lecture.mp4')}")[1])
assert video_page["kind"] == "video", video_page
assert call(video_page["url"]) == (200, video)
assert call(video_page["url"], headers={"Range": "bytes=2-5"}) == (206, video[2:6])
assert call(video_page["url"], headers={"Range": "bytes=7-"}) == (206, video[7:])
assert call(video_page["url"], headers={"Range": "bytes=-3"}) == (206, video[-3:])
assert call(video_page["url"], headers={"Range": "bytes=50-"})[0] == 416

assert call("/files/History/../../../etc/passwd")[0] == 404
assert call("/files/History/" + quote("../../etc/passwd", safe=""))[0] == 404
print("all checks passed, PDF rendered to", len(pdf_page["images"]), "image(s)")
