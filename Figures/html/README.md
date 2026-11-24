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

The data plots in `Figures/generated/` are not drawn here; `../../experiments/scripts/export_latex.py` writes them from the published summaries. They take the colours and the faces of the diagrams (`STYLE.md`, "The data plots"): the `PAL` of that script, the semi-condensed Bahnschrift that it makes from the installed font in `experiments/data/_work/fonts/` (never committed), and Palatino for formulas and panel titles.

## Changing a figure

1. Edit the HTML file (open it in a browser to look at it) and keep its opening comment in step with the drawing.
2. From `overleaf-github/` run

       python Figures/html/render.py Figures/html/<name>.html

   (several files at once are fine). `render.py` prints the page with headless Chrome (set `CHROME` if Chrome is not found), crops the PDF to the drawing and clears its dates, so an unchanged figure renders to the same file. It needs PyMuPDF (`pip install pymupdf`); `--png` also writes a preview image beside the HTML file (not committed); `--out` takes an absolute path.
3. Check the layout:

       python -B -X utf8 Figures/html/check_layout.py <name>

   It reports anything that runs out of its box, cards of one group that are not equal, marks that do not share the centre of their ring or frame, and a crop wider than the figure; `0 finding(s)` is the aim.
4. Rebuild the thesis and look at the page. Commit the HTML and the PDF together; Overleaf sees only the PDF.

Fonts: in the English figures Palatino Linotype for headings, variables and formulas, Bahnschrift for all other text, Consolas for code and Cambria Math for the two ceiling brackets, all of which come with Windows (`STYLE.md`, "Type" and "Fonts, as they are in the PDF"). The Korean figures keep these faces for Latin letters, digits and formulas and take Hangul from Noto Sans KR (text) and Noto Serif KR (headings), without added letter spacing (`STYLE.md`, "Fonts, as they are in the PDF"). Another machine may substitute a font, so check the PDF after rendering there.

In the public repository the Korean edition keeps its own sources in `dissertation/overleaf-github-ko/Figures/html/` (the same layout with Korean text) and renders them with this `render.py`. They link this folder's `style.css` and `fig.js` and add only the Hangul faces, Korean line breaking and the spacing of Hangul, so a change to the look here reaches them too: render them again and check them after such a change.

## Style

- `style.css` holds the look (colours, type, cards, tags, chips, pills, discs, legends) and `fig.js` the drawing helpers (`Fig.edge`, `Fig.node`, `Fig.contract`, `Fig.person`, `Fig.text`, `Fig.rich`, `Fig.star`, `Fig.arrow`, `Fig.medal` and others); each figure links both. `STYLE.md` gives the rules of the look: the colours, the type, the marks and shapes, the patterns for each kind of figure and what must be exact in print.
- Width 165 mm, the text width; text no smaller than 7.1 pt at print size, subscripts no smaller than 5.6 pt; most figures 35–75 mm tall.
- One colour per meaning (`STYLE.md`, "Colour"): allowance gold `#B98A24` (`#CFA448` for a band), transfer ultramarine `#2340C8`, C-PR violet `#6A2C91`, contracts verdigris `#2A7A72`, user accounts grey and dashed `#8A8A8A`, a neutral step or raw count `#5A5A5A`; RQ1 and the web `#2C8FB3`, RQ2 `#2F7D45`, RQ3, labels and hot contracts `#C23B5E`, RQ4–5 the violet of C-PR.
- Short labels in the figure; the caption carries the sentence. No result number outside the figures of Chapter 4 and the worked examples.

## Pitfalls met so far

- Chrome prints an SVG `<pattern>` as a page-sized image, which defeats the crop: draw hatching as clipped vector lines or filled bands.
- A CSS gradient prints as an unbounded shading; `render.py` ignores its box, so the panel's border must bound it.
- PyMuPDF widens a stroke's box by the miter limit (about 1 mm per side), so a panel flush with the 165 mm edge crops to about 167 mm; `\includegraphics[width=\textwidth]` then scales it by about 0.99, which is harmless.
- CSS beats SVG presentation attributes: give fonts on SVG text through `fig.js` (attribute) or a class, and do not use `.mono` sizes inside SVG.
