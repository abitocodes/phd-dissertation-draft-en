"""Render an HTML figure of the thesis to the vector PDF that LaTeX includes.

LaTeX cannot read HTML, so each diagram is kept as an HTML file (the source to edit and to read) and printed
by headless Chrome to a PDF whose text stays text. The PDF page is cropped to the drawn content.

Usage (from the thesis folder, overleaf-github/ or overleaf-github-ko/):
    python Figures/html/render.py Figures/html/conceptual-model.html            -> Figures/conceptual-model.pdf
    python Figures/html/render.py Figures/html/conceptual-model.html --png      -> also Figures/html/conceptual-model.png
    python Figures/html/render.py <file.html> --out <file.pdf>

Needs Google Chrome (or set CHROME to its path) and PyMuPDF (pip install pymupdf). The figures use the fonts
named in their CSS (Segoe UI; Noto Sans KR in the Korean edition); another machine may substitute a font.
"""
import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

CANDIDATES = [os.environ.get("CHROME", ""),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              "/usr/bin/google-chrome", "/usr/bin/chromium", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
MARGIN_PT = 1.5


def chrome() -> str:
    for c in CANDIDATES:
        if c and Path(c).exists():
            return c
    raise SystemExit("Chrome not found; set CHROME to its path")


def render(html: Path, out: Path, png: bool) -> None:
    raw = out.with_suffix(".raw.pdf")
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run([chrome(), "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
                        "--no-pdf-header-footer", "--print-to-pdf-no-header", "--virtual-time-budget=4000",
                        "--run-all-compositor-stages-before-draw", f"--print-to-pdf={raw}", html.as_uri()],
                       check=True, capture_output=True, timeout=180)
    doc = fitz.open(raw)
    if doc.page_count != 1:
        raise SystemExit(f"{html.name}: {doc.page_count} pages; enlarge the @page size in its CSS")
    page = doc[0]
    full, box = page.rect, fitz.Rect()
    for kind, r in page.get_bboxlog():
        r = fitz.Rect(r)
        # Chrome writes a CSS gradient as a shading whose box is unbounded; the border drawn with it bounds it.
        if kind == "fill-shade" or r.is_infinite or r.is_empty:
            continue
        r &= full
        if r.is_empty or (abs(r.width - full.width) < 1 and abs(r.height - full.height) < 1):
            continue
        box |= r
    box = fitz.Rect(box.x0 - MARGIN_PT, box.y0 - MARGIN_PT, box.x1 + MARGIN_PT, box.y1 + MARGIN_PT) & full
    page.set_cropbox(box)
    # No creation or modification time, so that an unchanged figure renders to the same file.
    doc.set_metadata({"title": html.stem, "author": "", "subject": "", "keywords": "", "creator": "",
                      "producer": "", "creationDate": "", "modDate": ""})
    doc.save(out, garbage=4, deflate=True, no_new_id=True)
    if png:
        page.get_pixmap(dpi=220).save(html.with_suffix(".png"))
    doc.close()
    raw.unlink()
    print(f"{html.name}: {box.width / 72 * 25.4:.1f} x {box.height / 72 * 25.4:.1f} mm -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, help="PDF path (one HTML file only); default Figures/<name>.pdf")
    ap.add_argument("--png", action="store_true", help="also write a PNG preview beside the HTML file")
    a = ap.parse_args()
    if a.out and len(a.html) > 1:
        raise SystemExit("--out takes one HTML file")
    for h in a.html:
        h = h.resolve()
        render(h, (a.out.resolve() if a.out else h.parent.parent / f"{h.stem}.pdf"), a.png)


if __name__ == "__main__":
    main()
