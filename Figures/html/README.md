# Diagrams drawn in HTML

LaTeX cannot read HTML. A diagram drawn in HTML therefore lives here as its source and is printed to a PDF that the chapter includes with `\includegraphics`. The PDF keeps its text as text (it can be searched and copied), and each HTML file opens with a comment that says in words what the figure shows, so the figure can be understood without rendering it. The chapter marks each such figure with two comment lines that name its source.

## The figures

| Chapter | Source (`Figures/html/`) | PDF (`Figures/`) | Label | Section |
|---|---|---|---|---|
| 1 | `web-to-ledger.html` | `web-to-ledger.pdf` | `fig:web-to-ledger` | `sec:background` |
| 1 | `study-timeline.html` | `study-timeline.pdf` | `fig:study-timeline` | `sec:supplementary-extension` |
| 1 | `thesis-roadmap.html` | `thesis-roadmap.pdf` | `fig:thesis-roadmap` | `sec:roadmap` |
| 2 | `allowance-sequence.html` | `allowance-sequence.pdf` | `fig:allowance-sequence` | `sec:erc20-allowance-lifecycle` |
| 2 | `random-surfer.html` | `random-surfer.pdf` | `fig:random-surfer` | `sub:random-surfer` |
| 2 | `crawl-ordering.html` | `crawl-ordering.pdf` | `fig:crawl-ordering` | `sec:crawl-ordering` |
| 2 | `reputation-lineage.html` | `reputation-lineage.pdf` | `fig:reputation-lineage` | `sec:reputation-systems` |
| 2 | `kendall-pairs.html` | `kendall-pairs.pdf` | `fig:kendall-pairs` | `sec:rank-correlation-theory` |
| 2 | `conceptual-model.html` | `conceptual-model.pdf` | `fig:conceptual-model` | `sec:theoretical-framework` |
| 2 | `defi-risk.html` | `defi-risk.pdf` | `fig:defi-risk` | `sec:defi-risk-taxonomy` |
| 2 | `accounts-logs.html` | `accounts-logs.pdf` | `fig:accounts-logs` | `sec:account-model` |
| 3 | `data-overview.html` | `data-overview.pdf` | `fig:data-overview` | `sec:data-sources` |
| 3 | `pipeline-architecture.html` | `pipeline-architecture.pdf` | `fig:pipeline-architecture` | `sec:pipeline-architecture` |
| 3 | `balance-cap.html` | `balance-cap.pdf` | `fig:balance-cap` | `sub:endorserank-graph` |
| 3 | `cpr-schematic.html` | `cpr-schematic.pdf` | `fig:cpr-schematic` | `sub:coupled-graph` |
| 3 | `discovery-protocol.html` | `discovery-protocol.pdf` | `fig:discovery-protocol` | `sec:discovery-protocol` |
| 3 | `holdout-design.html` | `holdout-design.pdf` | `fig:holdout-design` | `sec:holdout-protocol` |
| 4 | `data-funnel.html` | `data-funnel.pdf` | `fig:data-funnel` | `sec:dataset` |
| 5 | `depth-one.html` | `depth-one.pdf` | `fig:depth-one` | `sub:theory-closed-form` |
| 5 | `practical-uses.html` | `practical-uses.pdf` | `fig:practical-uses` | `sub:deploy-industry` |
| 6 | `answers-glance.html` | `answers-glance.pdf` | `fig:answers-glance` | `sec:summary-findings` |

The data plots in `Figures/generated/` are not drawn here; `../../experiments/scripts/export_latex.py` writes them from the published summaries, in the same colours.

## Changing a figure

1. Edit the HTML file (open it in a browser to look at it) and keep its opening comment in step with the drawing.
2. From `overleaf-github/` run

       python Figures/html/render.py Figures/html/<name>.html

   (several files at once are fine). `render.py` prints the page with headless Chrome (set `CHROME` if Chrome is not found), crops the PDF to the drawing and clears its dates, so an unchanged figure renders to the same file. It needs PyMuPDF (`pip install pymupdf`); `--png` also writes a preview image beside the HTML file (not committed); `--out` takes an absolute path.
3. Rebuild the thesis and look at the page. Commit the HTML and the PDF together; Overleaf sees only the PDF.

Fonts: Segoe UI in the English figures (Consolas for code) and Noto Sans KR in the Korean ones. Another machine may substitute a font, so check the PDF after rendering there.

In the public repository the Korean edition keeps its own sources in `dissertation/overleaf-github-ko/Figures/html/` (the same layout with Korean text) and renders them with this `render.py`.

## Style

- `style.css` holds the look (colours, type, panels, chips, RQ cards, pills, legend) and `fig.js` the drawing helpers (`Fig.graph`, `Fig.edge`, `Fig.contract`, `Fig.person`, `Fig.text`, `Fig.icon`); each figure links both.
- Width 165 mm, the text width; text no smaller than about 7 pt at print size; most figures 35–75 mm tall.
- One colour per meaning: allowance orange `#D97706`, transfer blue `#2563EB`, C-PR violet `#7C3AED`, contracts teal `#0F766E`, user accounts grey and dashed `#7A8594`; RQ1 `#0891B2`, RQ2 `#059669`, RQ3 `#DB2777`, RQ4–5 `#7C3AED`.
- Short labels in the figure; the caption carries the sentence. No result number outside the figures of Chapter 4 and the worked examples.

## Pitfalls met so far

- Chrome prints an SVG `<pattern>` as a page-sized image, which defeats the crop: draw hatching as clipped vector lines or filled bands.
- A CSS gradient prints as an unbounded shading; `render.py` ignores its box, so the panel's border must bound it.
- PyMuPDF widens a stroke's box by the miter limit (about 1 mm per side), so a panel flush with the 165 mm edge crops to about 167 mm; `\includegraphics[width=\textwidth]` then scales it by about 0.99, which is harmless.
- CSS beats SVG presentation attributes: give fonts on SVG text through `fig.js` (attribute) or a class, and do not use `.mono` sizes inside SVG.
