"""Check the layout of the figures: nothing runs out of its box, equal things are equal, marks share their centres.

Usage (from overleaf-github/):
    python -B -X utf8 Figures/html/check_layout.py              all figures of this folder
    python -B -X utf8 Figures/html/check_layout.py thesis-roadmap kendall-pairs

For each <name>.html it opens the page in headless Chrome (a copy with a short script added, removed afterwards) and
reads the rendered Figures/<name>.pdf, and reports

  in the page
    - text or a drawing that runs past the inner edge (the padding) of a framed or tinted box that holds it;
    - a heading whose text is wider than its line;
    - groups of cards (the children of one grid or row that carry a frame) with their widths and heights, and
      whether the widths are whole pixels (only then do they print equal: see the note on whole pixels in the
      stylesheet);
    - a card whose inside, or whose drawing, does not start on a whole pixel;
  in the PDF
    - a disc that does not share the centre of its ring, or a square that does not share the centre of its frame;
    - small boxes with a line of text (tags, chips, pills) of one size of type and one height that hold their text
      at different heights, or of one colour that differ in height by a pixel;
    - a crop wider than the figure by more than its margin (a stroked frame at the edge of the figure makes the
      crop about 1 mm wider on that side, and the figure smaller on the page).

Run render.py first: the PDF must be that of the HTML.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from render import chrome  # noqa: E402  (the same browser as the renderer)

MM = 25.4 / 72
MARGIN_MM = 1.5 * MM                     # the margin the renderer leaves around the drawing, a side

PROBE = r"""
<script>
window.addEventListener("load", () => setTimeout(() => {
  const PX = 25.4 / 96, mm = v => +(v * PX).toFixed(2);
  const out = { overflow: [], headings: [], groups: [], width: mm(document.querySelector(".fig").getBoundingClientRect().width) };
  // a frame: a shadow, a tint, or a border on two opposite sides (one rule, as under a heading, is no frame)
  const framed = e => { const s = getComputedStyle(e), b = k => parseFloat(s["border" + k + "Width"]) > 0;
    return s.boxShadow !== "none" || (b("Left") && b("Right")) || (b("Top") && b("Bottom")) ||
      (s.backgroundColor !== "rgba(0, 0, 0, 0)" && s.backgroundColor !== "rgb(255, 255, 255)"); };
  const name = e => (e.id ? "#" + e.id : "") + "." + String(e.getAttribute("class") || e.tagName).trim().replace(/\s+/g, ".");
  const inSvg = n => n.parentElement && n.parentElement.closest("svg");
  for (const b of document.querySelectorAll(".fig *")) {
    if (b.closest("svg") || !framed(b) || b.children.length + b.childNodes.length === 0) continue;
    const r = b.getBoundingClientRect(), s = getComputedStyle(b);
    if (r.width < 12 || r.height < 8) continue;                       // a swatch, a bar
    if (s.position === "absolute" || b.dataset.nocheck !== undefined) continue;
    const L = r.left + parseFloat(s.borderLeftWidth) + parseFloat(s.paddingLeft) - 0.6;
    const R = r.right - parseFloat(s.borderRightWidth) - parseFloat(s.paddingRight) + 0.6;
    const T = r.top - 0.6, B = r.bottom + 0.6;
    const bad = (q, what) => { if (q.width && (q.left < L || q.right > R || q.top < T || q.bottom > B))
      out.overflow.push(`${name(b)}: ${what} at x ${mm(q.left)}..${mm(q.right)}, y ${mm(q.top)}..${mm(q.bottom)} passes the inside ${mm(L)}..${mm(R)}, ${mm(T)}..${mm(B)}`); };
    const w = document.createTreeWalker(b, NodeFilter.SHOW_TEXT);
    for (let n; (n = w.nextNode());) {
      if (!n.textContent.trim() || inSvg(n)) continue;
      const g = document.createRange(); g.selectNodeContents(n);
      for (const q of g.getClientRects()) bad(q, `text "${n.textContent.trim().slice(0, 28)}"`);
    }
    for (const v of b.querySelectorAll("svg")) if (!v.parentElement.closest("svg")) bad(v.getBoundingClientRect(), "drawing " + name(v));
  }
  for (const h of document.querySelectorAll(".h")) {
    let right = 0; for (const c of h.children) right = Math.max(right, c.getBoundingClientRect().right);
    const g = document.createRange(); g.selectNodeContents(h);
    for (const q of g.getClientRects()) right = Math.max(right, q.right);
    const r = h.getBoundingClientRect();
    if (right > r.right + 0.6) out.headings.push(`heading "${h.textContent.trim().slice(0, 30)}" is ${mm(right - r.right)} mm wider than its line`);
  }
  // a card with a drawing that fills it: its inside and the drawing start on a whole pixel, or the rule under the
  // heading, the text and the drawing print up to a pixel apart
  for (const c of document.querySelectorAll(".part.panel")) {
    const r = c.getBoundingClientRect(), s = getComputedStyle(c);
    const L = r.left + parseFloat(s.borderLeftWidth) + parseFloat(s.paddingLeft);
    const W = r.width - 2 * (parseFloat(s.borderLeftWidth) + parseFloat(s.paddingLeft));
    const big = [...c.children].filter(v => v.tagName === "svg" && v.getBoundingClientRect().width > 0.6 * W);
    if (!big.length) continue;
    if (Math.abs(L - Math.round(L)) > 0.02)
      out.overflow.push(`${name(c)}: its inside starts at ${L.toFixed(2)} px, not on a whole pixel, and it holds a drawing`);
    for (const v of big) { const x = v.getBoundingClientRect().left;
      if (Math.abs(x - Math.round(x)) > 0.02) out.overflow.push(`${name(c)}: drawing ${name(v)} starts at ${x.toFixed(2)} px, not on a whole pixel`); }
  }
  // cards: the framed children of one parent, when there are two or more of them
  for (const p of document.querySelectorAll(".fig, .fig *")) {
    if (p.closest("svg")) continue;
    const kids = [...p.children].filter(c => !c.closest("svg") && c.tagName !== "svg" && framed(c) && c.getBoundingClientRect().width >= 60);
    if (kids.length < 2) continue;
    out.groups.push({ parent: name(p), cards: kids.map(c => { const r = c.getBoundingClientRect();
      return { w: +r.width.toFixed(3), h: +r.height.toFixed(3), x: +r.left.toFixed(3), cls: name(c).slice(0, 26) }; }) });
  }
  const pre = document.createElement("pre"); pre.id = "layout-probe"; pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
}, 300));
</script>
"""


def probe(html: Path) -> dict:
    tmp = html.with_name(f"_{html.stem}.probe.html")
    tmp.write_text(html.read_text(encoding="utf-8").replace("</body>", PROBE + "</body>", 1), encoding="utf-8", newline="\n")
    try:
        with tempfile.TemporaryDirectory() as profile:
            run = subprocess.run([chrome(), "--headless=new", "--disable-gpu", f"--user-data-dir={profile}",
                                  "--virtual-time-budget=4000", "--dump-dom", tmp.as_uri()],
                                 capture_output=True, timeout=180)
        dom = run.stdout.decode("utf-8", "replace")
    finally:
        tmp.unlink()
    m = re.search(r'<pre id="layout-probe">(.*?)</pre>', dom, re.S)
    if not m:
        raise SystemExit(f"{html.name}: the page gave no report")
    text = m.group(1).replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return json.loads(text)


def pdf_checks(pdf: Path, fig_width_mm: float) -> list[str]:
    notes = []
    page = fitz.open(pdf)[0]
    w = page.rect.width * MM
    round_shapes, squares = [], []
    for d in page.get_drawings():
        r = d["rect"]
        bw, bh = r.width * MM, r.height * MM
        kinds = [it[0] for it in d["items"]]
        if abs(bw - bh) > 0.2 or not 0.6 < bw < 12:
            continue
        cx, cy = (r.x0 + r.x1) / 2 * MM, (r.y0 + r.y1) / 2 * MM
        stroke_only = d.get("type") == "s"
        if kinds.count("c") >= 4 and kinds.count("l") <= 1:
            round_shapes.append((cx, cy, bw, stroke_only))
        elif kinds.count("re") or kinds.count("l") >= 3:
            squares.append((cx, cy, bw, stroke_only or (d.get("type") == "fs" and d.get("fill") in (None, (1.0, 1.0, 1.0)))))
    for shapes, what in ((round_shapes, "disc"), (squares, "square")):
        rings = [s for s in shapes if s[3]]
        fills = [s for s in shapes if not s[3]]
        seen = set()
        for rx, ry, rd, _ in rings:
            for fx, fy, fd, _ in fills:
                dx, dy = fx - rx, fy - ry
                if fd < rd and rd - fd < 2.2 and max(abs(dx), abs(dy)) < 0.45 and max(abs(dx), abs(dy)) > 0.03:
                    key = (round(dx, 2), round(dy, 2), round(fd, 1), round(rd, 1))
                    if key not in seen:
                        seen.add(key)
                        notes.append(f"a {what} of {fd:.2f} mm stands {dx:+.2f}, {dy:+.2f} mm off the centre of its {rd:.2f} mm frame (at {rx:.1f}, {ry:.1f} mm)")
    # Small boxes with a line of text, drawn as CSS boxes (their top and height are whole pixels): the baseline must
    # lie the same number of pixels below the top of every box of one height and one size of type, and boxes of one
    # colour may not differ in height by a pixel. (Boxes of a drawing are not on the pixel grid and are left out.)
    px = 25.4 / 96
    spans = [s for b in page.get_text("dict")["blocks"] for ln in b.get("lines", []) for s in ln["spans"] if s["text"].strip()]
    small, seen_boxes = [], set()
    for d in page.get_drawings():
        if d.get("type") != "f" or not d.get("fill"):
            continue
        r = d["rect"]
        bw, bh, top = r.width * MM / px, r.height * MM / px, r.y0 * MM / px
        if bw < 11 or not 6 <= bh <= 24.5 or abs(bh - round(bh)) > 0.03 or abs(top - round(top)) > 0.03:
            continue
        key = (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1))
        if key in seen_boxes:
            continue
        seen_boxes.add(key)
        inside = [s for s in spans if r.x0 - 1 <= s["origin"][0] <= r.x1 and r.y0 <= s["origin"][1] <= r.y1 + 1]
        if not inside or len({round(s["origin"][1], 1) for s in inside}) > 1:      # no text, or more than one line
            continue
        s = min(inside, key=lambda s: s["origin"][0])
        colour = "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in d["fill"])
        small.append((round(s["size"], 1), round(bh), round((s["origin"][1] - r.y0) * MM / px, 1), colour, s["text"].strip()[:14]))
    by = {}
    for size, bh, base, colour, text in small:
        by.setdefault((size, bh), {}).setdefault(base, []).append(text)
    for (size, bh), bases in sorted(by.items()):
        if len(bases) > 1:
            notes.append(f"boxes {bh} px high with {size} pt text hold it at different heights: " +
                         "; ".join(f"{b} px below the top in {v[:3]}" for b, v in sorted(bases.items())))
    by_colour = {}
    for size, bh, base, colour, text in small:
        by_colour.setdefault((size, colour), {}).setdefault(bh, []).append(text)
    for (size, colour), hs in sorted(by_colour.items()):
        for a in sorted(hs):
            if a + 1 in hs:
                notes.append(f"{colour} boxes with {size} pt text are {a} px high ({hs[a][:3]}) and {a + 1} px high ({hs[a + 1][:3]})")
    # a dashed frame at an edge is measured 0.29 mm wider than it is and a line of text about 0.3 mm; a stroked
    # frame with corners about 1 mm, which is what this looks for
    extra = w - fig_width_mm - 2 * MARGIN_MM
    if extra > 0.7:
        notes.append(f"the crop is {extra:.2f} mm wider than the figure ({fig_width_mm:.2f} mm) and its margin: something at an edge is measured wider than it is")
    return notes


def main() -> None:
    names = sys.argv[1:] or sorted(p.stem for p in HERE.glob("*.html") if not p.name.startswith("_"))
    worst = 0
    for name in names:
        html, pdf = HERE / f"{name}.html", HERE.parent / f"{name}.pdf"
        rep = probe(html)
        notes = rep["overflow"] + rep["headings"] + (pdf_checks(pdf, rep["width"]) if pdf.exists() else [])
        lines = []
        for g in rep["groups"]:
            ws = sorted({c["w"] for c in g["cards"]})
            hs = sorted({c["h"] for c in g["cards"]})
            xs = sorted({c["x"] for c in g["cards"]})
            gaps = sorted({round(b["x"] - a["x"] - a["w"], 3) for a, b in zip(g["cards"], g["cards"][1:]) if b["x"] > a["x"]})
            # boxes side by side that are meant to be equal print equal only if their widths and their pitch are
            # whole pixels; boxes one above the other (one x) print equal anyway
            alike = ws[-1] - ws[0] < 1.5
            whole = all(abs(v - round(v)) < 0.01 for v in ws) and all(abs((b - a) - round(b - a)) < 0.01 for a, b in zip(xs, xs[1:]))
            flag = ""
            if alike and len(xs) > 1 and (len(ws) > 1 or not whole):
                flag = "  <-- side by side and alike, but not whole pixels: they print up to 0.26 mm apart"
                notes.append(f"{len(g['cards'])} boxes in {g['parent'][:34]} are alike in width ({ws} px) but not whole pixels")
            lines.append(f"    {len(g['cards'])} boxes in {g['parent'][:34]}: widths {ws} px, heights {hs} px"
                         + (f", gaps {gaps} px" if gaps else "") + flag)
        print(f"{name}: figure {rep['width']} mm wide; {len(notes)} finding(s)" + ("" if pdf.exists() else " (no PDF: the page only)"))
        for n in notes:
            print("    <-- " + n)
        for ln in lines:
            print(ln)
        worst = max(worst, len(notes))
    if worst:
        sys.exit(1)


if __name__ == "__main__":
    main()
