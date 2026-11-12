# EN Dissertation (Overleaf / GitHub)

English PhD dissertation, University of South Africa: *Integrating ERC-20 Allowance Edges into PageRank for Enhanced On-Chain Wallet Reputation Scoring* (Taehong Kwon). Overleaf project; root document `main.tex`. The study ranks smart contracts on Arbitrum One with EndorseRank (PageRank on ERC-20 allowances), AWP (transfer PageRank) and the coupled walk C-PR, and tests them out of window.

| Path | Content |
|------|---------|
| `main.tex`, `01-Intro/`, `Chapter-01-…/` … `Chapter-08-Appendix/` | Thesis sources (front matter, six chapters, references, appendices) |
| `Config/preamble.tex`, `Config/references.bib` | Layout (XeLaTeX) and APA 7 bibliography (biblatex, biber); `refmap.csv` and `references-candidates.md` are working notes for the bibliography |
| `results/tables/`, `Figures/generated/` | Generated tables and figures (see `results/README.md`; never edited by hand) |
| `Figures/html/`, `Figures/*.pdf` | The 21 diagrams, drawn in HTML: `Figures/html/<name>.html` is the source and describes the figure in words; `python Figures/html/render.py Figures/html/<name>.html` prints it to `Figures/<name>.pdf`, which the chapter includes (`Figures/html/README.md` lists them) |
| `main.pdf`, `Chapter-0*.pdf` | Built thesis and per-chapter PDFs |
| `manuscripts/` | Two journal manuscripts drawn from the thesis (`A-plos-one/`, `B-ieee-access/`) |
| `analysis/` | Supporting analyses for the manuscripts |

Build: `build.ps1` (XeLaTeX, biber, XeLaTeX twice, then one PDF per chapter). On Overleaf, set the compiler to XeLaTeX (`latexmkrc` does this).

The evaluation code, data and the Korean edition are in the public repository [ERC20-Allowance-PageRank-Wallet-Reputation](https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation), where this repository is the submodule `dissertation/overleaf-github`.
