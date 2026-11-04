<p align="center">
  <img src="docs/banner.svg" alt="Notebooks: a pixel-art bookshelf with Claw'd mascots hopping and carrying a book" width="100%">
</p>

<p align="center">
  <b>A Linux app that keeps your academic notes as books on a shelf.</b><br>
  Each subject gets a book, and each page holds one of your documents, however long it runs.<br>
  A small crew of Claw'ds lives on the shelf too. They turn your pages for you and hammer every new book together by hand.
</p>

<p align="center">
  <img alt="Linux" src="https://img.shields.io/badge/Linux-desktop%20app-d77757?logo=linux&logoColor=white">
  <img alt="Python 3" src="https://img.shields.io/badge/Python-3-d77757?logo=python&logoColor=white">
  <img alt="GTK + WebKit" src="https://img.shields.io/badge/GTK%20%2B%20WebKit-window-d77757?logo=gnome&logoColor=white">
  <img alt="No pip installs" src="https://img.shields.io/badge/pip%20installs-none-d77757">
  <img alt="Runs offline" src="https://img.shields.io/badge/your%20notes-stay%20on%20your%20machine-d77757">
</p>

<p align="center">
  <img src="docs/screenshots/shelf.png" alt="The bookshelf: coloured books for each subject, a 'Good evening, twin' greeting, and Claw'ds playing on the floor" width="88%">
</p>

---

## ✨ What it does

📚 **A book per subject.** History, Physics, Chemistry, whatever you're taking. Each one sits on the shelf in its own colour.

📖 **Opens like a real book.** First the cover, then two pages side by side with the spine down the middle. Page 1 goes on the left, page 2 on the right.

📄 **One document per page, any length.** Drop in a 40-page PDF and you get one long page to scroll through. A three-line note stays short. Nothing gets cropped.

🔍 **Close-up view.** Click a page to open it big. Zoom runs from 50% up to 400%.

🎬 **Videos are pages too.** Drag in a lecture recording and it plays right there on the page. You can skip around in it.

▶️ **YouTube import.** Paste a link and pick a format (MP4, M4V, WebM, MKV, MOV or OGV). The video shows up in your book as a new page.

🦀 **A crew of Claw'ds.** Five of them hang around your shelf, and two handle all the page turning. [Meet them below.](#-meet-the-crew)

☀️ **It says hi.** Depending on the hour you get "Good morning, twin", "Good noon, twin", "Good afternoon, twin" or "Good evening, twin".

## 📸 A look inside

<table>
  <tr>
    <td width="50%"><img src="docs/screenshots/book.png" alt="An open book with two pages side by side"><p align="center"><b>Two pages, split at the spine</b><br>Each one scrolls by itself.</p></td>
    <td width="50%"><img src="docs/screenshots/turn.png" alt="Two Claw'ds holding the edge of a page as it turns"><p align="center"><b>Turning a page</b><br>One Claw'd takes the bottom corner, the other takes the top, and they walk it over together.</p></td>
  </tr>
  <tr>
    <td width="50%"><img src="docs/screenshots/closeup.png" alt="The close-up view of a PDF page with zoom controls"><p align="center"><b>Close-up view</b><br>Zoom, flip pages, hit Esc to get out.</p></td>
    <td width="50%"><img src="docs/screenshots/build.png" alt="Five Claw'ds in a ring around a small new book they are building"><p align="center"><b>Building a new book</b><br>The whole crew shows up and hammers it together.</p></td>
  </tr>
</table>

## 🦀 Meet the crew

Claw'd is Claude Code's little pixel mascot. In this app he has four friends.

| When… | the Claw'ds… |
|---|---|
| you're on the bookshelf | wander around, stop for a breather, blink now and then |
| two of them bump into each other | walk up face to face, throw their arms up and bounce with happy `>` `<` eyes |
| they're feeling playful | play tag. One runs off and the other chases close behind. After three rounds they both laugh |
| you make a new book | everyone runs in carrying parts in the book's colour, forms a ring and hammers away. The book grows a little each round, they cheer when it's done, and it opens |
| you turn a page | two of them walk to the page corner, grab it (one low, one high), carry it over the spine, lay it down and smile |
| you **grab one** with the mouse | he dangles from the cursor, sways, kicks his legs, flails his arms and squeezes his eyes shut until you let go. Then he drops, bounces and runs back to whatever he was doing |

> [!TIP]
> Pages won't turn while you're holding one of the two page-turners. They need both hands for the job.
> With **reduce motion** switched on in your system settings, the shelf crew stays hidden and pages change instantly.

## 🚀 Install

```sh
git clone https://github.com/samiscoolnoway/notebooks.git
cd notebooks
./install.sh
```

Then find **Notebooks** in your app menu under *Education* and open it.

`install.sh` copies the app into `~/.local/share/notebooks-app` and adds a menu entry. You don't need root.

### What it needs

Package names below are for Debian and Ubuntu. Most desktops ship the first two already.

| For | Package | |
|---|---|---|
| the app itself | `python3` | required |
| the app window | `python3-gi`, `gir1.2-webkit2-4.1` | optional: without them it opens in your browser instead |
| PDF pages | `poppler-utils` (`pdftoppm`) | for PDFs |
| Word, PowerPoint, Excel and LibreOffice files | `libreoffice` | for office documents |
| YouTube import | `yt-dlp` (e.g. `pipx install yt-dlp`) and `ffmpeg` | for YouTube |

The app only uses Python's standard library, so there's nothing to `pip install` and no virtualenv to set up.

## 🗂️ Using it

**Adding pages:** open a book and click **+ Add pages**, or drag files straight onto it. Each file lands as the next page.

**Adding a YouTube video:** click **+ YouTube**, paste the link and pick a format. MP4 is the safe bet. OGV re-encodes the whole video, which takes a while. A link from inside a playlist saves just that one video.

### What can go on a page

| Kind | File types | Shown as |
|---|---|---|
| Documents | `.pdf` | every PDF page as an image, top to bottom |
| Office files | `.doc` `.docx` `.odt` `.rtf` `.ppt` `.pptx` `.odp` `.xls` `.xlsx` `.ods` | converted with LibreOffice, then shown like a PDF |
| Images | `.png` `.jpg` `.jpeg` `.gif` `.webp` `.svg` `.bmp` | the image |
| Videos | `.mp4` `.m4v` `.webm` `.mkv` `.mov` `.ogv` | a video player you can skip around in |
| Text | `.txt`, `.md`, anything else that's plain text | the text |

Other files still get saved in the book. You just won't see a preview.

### Keyboard

| Where | Key | Does |
|---|---|---|
| Open book | <kbd>→</kbd> / <kbd>←</kbd> | next / previous pages |
| Open book | <kbd>Esc</kbd> | back to the shelf |
| Close-up | <kbd>→</kbd> / <kbd>←</kbd> | next / previous page |
| Close-up | <kbd>+</kbd> / <kbd>−</kbd>, or <kbd>Ctrl</kbd> + scroll | zoom in / out |
| Close-up | <kbd>Esc</kbd> | close |

## 💾 Where your notes live

Everything is plain folders and files you can open yourself:

```
~/Notebooks/
├── History/
│   ├── 001 The Roman Empire.pdf
│   └── 002 Lecture recording.mp4
└── Physics/
    ├── 001 Newton's laws.docx
    └── 002 Energy summary.txt
```

Each book is a folder and each page is a file inside it. The number at the start of the name sets the page order, so you can rename, reorder, copy or back up your books with any file manager you like. Page images get cached in a hidden `.pages` folder inside each book and rebuilt when the file changes.

## 🔒 It stays on your computer

The app runs a tiny web server that only listens on `127.0.0.1` (your own computer) and shows it in its own window. Nothing gets uploaded. It only goes online when you ask it to download a YouTube video.

Every request gets checked, so a website open in your browser can't read or change your books, and no file path can reach outside your Notebooks folder.

## 🛠️ For tinkerers

```sh
python3 app.py            # run without installing
python3 app.py --serve    # just the server; open the printed address in a browser
python3 test_app.py       # self-check (uses a temporary folder, never touches ~/Notebooks)
```

| Setting | Default | |
|---|---|---|
| `NOTEBOOKS_DIR` | `~/Notebooks` | where books are stored |
| `NOTEBOOKS_PORT` | a free port | the port the local server uses |

| File | What's in it |
|---|---|
| `app.py` | the local server: books, uploads, PDF/office rendering, video streaming, YouTube import, and the GTK window |
| `index.html` | everything you see: the shelf, the open book, the close-up view, and the Claw'd crew |
| `install.sh` | copies the app into place and adds the menu entry |
| `test_app.py` | end-to-end checks against a throwaway library |

---

<p align="center">
  Built with <a href="https://claude.com/claude-code">Claude Code</a>. Claw'd is Claude Code's mascot, redrawn here in pixels.<br>
  <sub>No Claw'ds were harmed in the making of this app. A few got picked up and squirmed a bit.</sub>
</p>
