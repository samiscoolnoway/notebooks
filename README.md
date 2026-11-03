# Notebooks

A Linux app for academic notes, laid out as books. Each subject is a book on a shelf; each page holds one document
(PDF, Word/LibreOffice file, image, text or video) and is as long as that document. Open a book and it shows two
pages side by side; click a page for a zoomable close-up. YouTube videos can be added as pages (MP4, M4V, WebM, MKV, MOV, OGV).
A crew of pixel Claw'ds roams the shelf, turns your pages and builds every new book. Grab one and he squirms.

## Install

```sh
./install.sh
```

Then open **Notebooks** from the app menu. Books are stored as folders in `~/Notebooks`.

Needs Python 3, GTK 3 with WebKit2GTK 4.1 (falls back to your browser without it), `pdftoppm` (poppler-utils) and
LibreOffice for documents, and `yt-dlp` plus `ffmpeg` for YouTube.

## Test

```sh
python3 test_app.py
```
