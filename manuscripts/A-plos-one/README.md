# Manuscript A: PLOS ONE submission package

**Title:** Does PageRank find the smart contracts users rely on sooner than counting? A crawl-ordering test on an Ethereum rollup

**Running title (61 characters, limit 70):** Crawl-ordering test of PageRank on a rollup's smart contracts

**Article type:** PLOS ONE Research Article

**Authors:** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

## What the paper reports

The paper asks whether PageRank walks on the contract graph of Arbitrum One find the contracts that users rely on sooner, and rank their later use better, than the counts they smooth. Every node is a contract other than a smart account (1,403,959 contracts over both freezes). The edges are transfers between contracts and latest allowances counted up to the owner's balance (the balance cap), on WETH, USDC, USDT0, ARB and WBTC, valued in US dollars, from the twelve months before each freeze: T_obs, 30 June 2026 (same window and W1), and t1, 31 March 2026 (W0). Main points:

- **Discovery-order test (lead result; Table 2, Fig 1 A and B).** The crawl-ordering experiment of Cho, Garcia-Molina and Page (1998) on the contract graph, with importance that no ordering reads: the dollars that user accounts paid a contract (I_T) and authorized it to spend (I_A). The decision concerns the coupled walk C-PR′ only. Deciding run (T_obs, `both` mode, 1,169,044 contracts, 20 seeds): D1 = C-PR′ − BFS is +0.0520 [+0.0485, +0.0558] on I_T and +0.0061 [+0.0014, +0.0111] on I_A; D2 = C-PR′ − IB′_U is −0.0051 [−0.0087, −0.0010] and −0.0571 [−0.0621, −0.0519]. Verdict V2 on both importances, with the added sentence that the backlink ordering was sooner; the statement is quoted from `discovery/discovery_tobs_both.json` : `decision.statements`, and `make_tables.py` stops if `main.tex` does not quote it word for word.
- **Outside the decision (Tables 3 and 4, S1 Table B to D).** AWP′ has the highest area of the crawls compared in the deciding run and lies above the transfer backlink count on both importances in all four runs. In the deciding run the walks on the allowance layer alone do not exceed the allowance backlink count on I_T; EndorseRank-activity′ lies above it on I_A there, and on both importances at t1 in the `both` mode. In the `out` mode, a sensitivity analysis without a verdict, all four decision contrasts are above zero at both freezes. At t1 in the `both` mode the signs are those of the deciding run. On the hot set of the union in-degree the backlink ordering is sooner than C-PR′ in all four runs. Every crawl is far from the ideal order.
- **Same window (Table 5).** Each single-layer score agrees most with the checks of its own edges, an intended-construct check that is partly built in.
- **Out of window (Table 6, Fig 1 C).** EndorseRank lies below the in-approve degree on new approval pairs in W0 and W1, with uniform and with activity restarts. AWP lies slightly above the transfer in-degree on new senders on the whole spender cohorts in both windows and below it among the W0 spenders that another contract had paid. Two facts frame every number: the labels count mostly user accounts, and about 27% of each spender cohort lies outside the union graph and scores zero.
- **Closed form (Table 1).** A spender whose owner contracts receive no allowance scores c(1 + d δ(v)); within 1% for every such spender (651 of 926 cohort spenders at T_obs are of depth one; 33.8% of the 275 deeper ones lie within 1%).
- **Cost.** One solve per graph (EndorseRank 0.101 s, AWP 2.821 s, C-PR 3.080 s) and the solves of a walk-ordered crawl (about 540 per crawl in the deciding run).
- **The registered analysis beside the main one (Table 7).** Raw base units, every ERC-20 token, every event since 1 October 2023, graphs with every account of the cohort's events, cohort 27,844. The discovery-order test has no registered counterpart.

C-PR is defined only as far as the test needs it. The paper reports no verdict under rule A or rule B; one sentence says that the companion manuscript reports them.

**Status words.** The contract-graph analysis (US dollars on five tokens, scores from the twelve months before each freeze, graphs of contracts other than smart accounts with edges read from the whole chain, the balance cap with balances reconstructed from Transfer logs, constants set on the contract graph, and the discovery-order test) was defined after the registered results were known and is the main analysis. None of its results is called registered, pre-specified or planned. The discovery-order test "was defined after the registered results were known" and "decides no rule of the plan or the registration"; no sentence gives a date or time of a definition or commit of the main analysis or of the protocol. The order-of-events passage of Methods keeps the dated entries of the plan, the extraction, the registration and the registered results, followed by one undated entry with the sentence of the context note. Registered values appear only in sentences and table columns labelled "registered analysis".

## Target journal and why it was chosen

- **PLOS ONE** is DHET-accredited through its Scopus and DOAJ indexing, which meets the UNISA requirement of a first-author article in an accredited journal.
- It reviews for scientific soundness, not perceived impact, and it publishes negative and null results. The lead result is negative (the coupled walk did not order a crawl better than a count of backlinks), and several others are losses of a walk to a count.
- The companion Manuscript B (the coupled walk C-PR, its two rules, its weight sweep, its seeded ablation and the Sybil exposure of the allowance layer) goes to IEEE Access. The Introduction of A states which results appear in both papers.

## Files

| File | What it is |
|---|---|
| `main.tex` | Manuscript in the PLOS ONE LaTeX layout (article class, rebuilt by hand from the PLOS template). Figures are **not** embedded, per PLOS policy. The Fig 1 caption follows the paragraph that first cites it, and each table follows the paragraph that first cites it. Tables 1 to 7 sit between `% BEGIN GENERATED tabN` / `% END GENERATED tabN` markers and are written by `make_tables.py`; do not edit them by hand. |
| `main.pdf` | Build of `main.tex`: submission layout with line numbers and no embedded figure. |
| `main_preview.tex`, `main_preview.pdf` | Reading copy for the authors with Fig 1 embedded (6.9 in wide). Not for submission. |
| `references.bib` | Bibliography: 60 entries. The 59 cited entries are each copied from the thesis bibliography `Config/references.bib` (same key) and converted to BibTeX for `vancouver.bst` (journaltitle to journal, report to techreport, online to misc, eid to pages, DOI as an `https://doi.org/` link and URL in `note`, accents as TeX accents). The uncited 60th entry, `kwon2026coupling`, is Manuscript B with its current title (see "References style"). |
| `cover-letter.tex`, `cover-letter.pdf` | One-page cover letter. Its date line still reads 29 October 2026; set it at submission. |
| `data_sources.py` | Shared loader for the scripts below. Needs `--repo PATH` or `CONTRACT_REP_REPO`, a checkout of the public repository `ERC20-Allowance-PageRank-Wallet-Reputation` (a checkout of the authors' repository, which holds it as a submodule, also works); nothing is guessed. Reads the registered summaries from `3-published-results-for-thesis/` and those of the main analysis from its subfolder `revised-contract-12m/` (constant `REV`), and checks every published summary against its `SHA256SUMS.txt` (CRLF form, as the checksums were taken on a Windows checkout) before use. The score windows are read from the published configuration files (`config/contract_reputation.yaml` with `overlay_contract12m.yaml`) and checked against the summaries. |
| `make_tables.py` | Writes Tables 1 to 7 into `main.tex` and the rows of the four panels of S1 Table (`supporting/S1_Table_rows.tex`, `_rows_b.tex`, `_rows_c.tex`, `_rows_d.tex`) from the published summaries and `analysis/closed-form/closed_form_check.json`. After writing, it checks that `main.tex` quotes the verdict sentence of the deciding run word for word. |
| `check_numbers.py` | Lists every number in the prose of a `.tex` file (tables skipped) that does not occur in a source: both results digests, the two documents that define the main analysis, the published summaries and `analysis/closed-form/closed_form_check.json`. The long per-seed lists and the curves of the discovery summaries are not read, so that a number does not pass by chance; the curve points that the text quotes (at 1% and 10% of the visits) are added one by one. |
| `figures/make_fig1.py` | Fig 1 from `discovery/discovery_tobs_both.json` (`curves.P_ST`, `sizes`, `hot_sets`) and, through `make_tables.spender_blocks()`, from `holdout-w0/eval_summary.json`, `window-w1/eval_summary.json` and `supplementary/supplementary.json`. Panels A and B: discovery curves of the deciding run for C-PR′, IB′_U, AWP′ and BFS on the two hot sets (mean over the 20 seeds, band = range over the seeds), with the random curve, the ideal order and a vertical line at 10% of the universe. Panel C: each single-layer walk minus the count it smooths on the spender labels. Arial-metric sans serif (Liberation Sans where installed, else Arial; the current `fig1.pdf`, built on Windows, embeds Arial), 8 pt or larger, 7.2 x 6.1 in. Colours: slots 1 to 3 of the dataviz reference palette (`#2a78d6`, `#eb6834`, `#1baf7a`; validated for all pairs on white, colour-vision-deficiency ΔE 9.2, normal vision 24.0); line styles and markers are the second encoding, and the caption names them. |
| `figures/fig1.pdf` | Vector source of Fig 1. |
| `figures/Fig1.tif` | Fig 1 for upload: 2160 x 1830 px (7.2 x 6.1 in) at 300 dpi, RGB, LZW-compressed TIFF. |
| `supporting/S1_Text.tex`, `.pdf` | **S1 Text.** Source, extraction and score windows; cohorts and spender lists; account types (rules, read set, reads, code families, result, limits); balances and the balance cap; tokens and prices; approvals and the allowance layer; transfers and the transfer layer; the discovery-order test in detail; label formulas (including the revocation and drain counts that the main text reports without offering them as evidence); same-window checks; query patterns. Constants are those of the pipeline configuration, SQL and scripts in the experiment folder of the public repository and of the published summaries (named in the file header). |
| `supporting/S1_File.md` | **S1 File.** Excerpts of the analysis plan (commit `d060f3a`) and of the W1 registration (commit `1747e64`) of the public repository, with every omitted passage marked `[…]`, both commit identifiers of each file (public and original) and the SHA-256 hashes of the full files (LF and CRLF). The omitted passages are passages on outcomes that this paper does not study. Each piece between two marks was checked to be verbatim and in order against `git show <commit>:experiments/docs/<file>`, and the four hashes were computed from that output (11 November 2026). |
| `supporting/S1_Table.tex`, `.pdf`, `S1_Table_rows*.tex` | **S1 Table**, four panels on five landscape pages: (A) events, account types, balances, graphs, universes, cohorts, labels and constants at both freezes; (B) AUC_10% of every ordering in the four runs; (C) the contrasts of items 1 and 2 of the protocol's list and the replication contrast in the three runs outside the decision; (D) readings of the deciding run by ordering (discovery curve at 10%, importance held at 1% and 10%, ties, wasted visits, solves and iterations). Rows generated by `make_tables.py`; the panel notes are typed. |

## Where each number comes from

All summaries are in the public repository `ERC20-Allowance-PageRank-Wallet-Reputation`, folder `experiments/data/3-published-results-for-thesis/` (registered analysis) and its subfolder `revised-contract-12m/` (main analysis); the two `results_digest.md` files name the JSON key of every value. `analysis/closed-form/closed_form_check.json` of this repository holds the closed-form values of both analyses (its "revised" rows are the contract-graph analysis; regenerated in commit `87dc532`).

| Table / figure | Content | Source of the numbers (under `revised-contract-12m/` unless a path says otherwise) |
|---|---|---|
| Table 1 | The contract graph at both freezes, coverage of the cohorts, fit of the closed form | `describe/describe.json` (`allowances`, `pairs`, `nodes`); `discovery/discovery_tobs_both.json`, `discovery_t1_both.json` (`sizes.graph`); `same-window`, `holdout-w0`, `window-w1/eval_summary.json` (`cohort_coverage`, `closed_form` through `analysis/closed-form/closed_form_check.json`); the configuration files for the windows |
| Table 2 | AUC_10% of every ordering in the deciding run with intervals, the references, D1, D2 and the verdict | `discovery/discovery_tobs_both.json` (`auc`, `decision`, `sizes`) |
| Table 3 | Contrasts outside the decision, items 1 to 4 of the protocol's list | `discovery/discovery_tobs_both.json` (`fixed_order`, items 1 to 4) |
| Table 4 | D1 and D2 under the sensitivities, in the other reveal mode and at the other freeze | `discovery/discovery_tobs_both.json` (`decision`, `fixed_order.5_sensitivities`); `discovery_tobs_out.json`, `discovery_t1_both.json`, `discovery_t1_out.json` (`decision`) |
| Table 5 | Same-window intended-construct check, agreement of the two rankings, isolated-node sensitivity | `same-window/eval_summary.json` (`families`, `per_proxy`, `contrasts`, `inter_method`, `isolated_rule`, `ties`, `graph`) |
| Table 6 | Spender holdouts W0 and W1, count contrasts, union-graph and receiving subsets, EndorseRank − AWP | `holdout-w0/eval_summary.json` (`taus`, `contrasts_after`, `receiving`, `in_union_graph`, `label_split`, `cohort_coverage`); `window-w1/eval_summary.json` (`spender_taus`, `endorserank_results`, `label_split`, `cohort_coverage`); `supplementary/supplementary.json` |
| Table 7 | The registered analysis beside the main analysis | the same-window, holdout-w0, registered-w1 / window-w1 summaries, `supplementary.json` and `benchmark.json` of each analysis; `closed_form_check.json`; the configuration files |
| Fig 1 | (A, B) discovery curves of the deciding run; (C) walk minus count on the spender labels | `discovery/discovery_tobs_both.json` (`curves.P_ST`, `hot_sets`, `sizes`); as Table 6 for C |
| S1 Table | Descriptive (four panels) | `describe/describe.json`, `cohort/*.json`, `typing/*.json`, `usd/constants.json`, the three evaluation summaries, `discovery/feasibility_t1.json` and the four `discovery/discovery_*.json` (`sizes`, `hot_sets`, `auc`, `fixed_order`, `curves`, `diagnostics`, `runs`) |

Numbers in the prose that `check_numbers.py` does not find in a source (run of 11 November 2026), each checked by hand:

- `main.tex`: 2612 and 721 (the names EIP-2612 and ERC-721); 179,000 (pages of the Stanford web in Cho, Garcia-Molina and Page, 1998, read in the paper); 1747 and 344017 (leading digits of the commits `1747e64` and `344017e`); 365 (days of a twelve-month score window, from the configured window ends).
- `supporting/S1_Text.tex`: 42161 (chain identifier of Arbitrum One, in the plan); 6780, 721 and 2612 (names of EIP-6780, ERC-721 and EIP-2612); 365.
- `supporting/S1_Table.tex`, `cover-letter.tex`: none.

Numbers that pass the check although they are not read from a summary, with their sources:

- From the cited papers, each read in the paper or its abstract: about 1,100 pages of the small site and the topic experiment (Cho et al.); 328 million pages (Najork and Wiener, 2001); 23 labeled protocols (Kitzler et al., 2023); the year 1998 in the cover letter.
- Computed from the stated formulas: the time weights σ(0) = 0.858, σ(90) = 0.711, σ(182) = 0.495 and σ(365) = 0.136 (k = 0.01, t0 = 180 days); the value weights 0.8 and 0.27 of twice and half the median amount (b = ln 3 / m); "about 0.13 bootstrap standard errors" (Monte Carlo error of a 2.5% percentile from 400 resamples).
- Rounded or counted from published values: "about 27%" (27.5% and 27.2% of the spender cohorts outside the union graph, `cohort_coverage`); "about a third of the matched cohort" (100% − 66.3%); "fewer than half of the event rows" (603,475,784 of 1,240,275,042); "more than 0.999 of the picks" (the lowest tie share of a count ordering is 0.99945, `diagnostics.ties` of the `out` run at T_obs); "between 0.835 and 0.911" (wasted visits in the first 10%, `diagnostics.wasted_visits`); "less than 0.002" (Table 3, block 1); "no crawl ... more than a quarter" (the highest discovery curve at 10% of the visits among the orderings compared is 24.7%); "about 540 recomputes" and "15 orderings" (`runs`); "eight seconds after the commit" (16:49:40 minus 16:49:32); "eighteen months" and "nine months" (from the window dates).

Other text sources: the candidate count 29,022 and the 27,844 candidates with code from the registered `results_digest.md` (`cohort/matched_cohort.json`); the cohort lists, cohorts and spender lists from `cohort/*.json` and the `cohort_coverage` and `spender_account_types` blocks of the evaluation summaries; the account types from `describe/describe.json` (`events`, `account_types`) and `typing/*.json`; the 115,084 contracts with a `validateUserOp` selector that stay contracts from `docs/revision_contract_graph.md` (section 13) of the published folder; the balance check from `describe/describe.json` (`balance_check`); the token rule and its counts (133, 64, 46, 75.75%) from `usd/usd_inputs.json`; the price days and the price check from `describe/describe.json` (`price_days`, `chainlink_check_in_windows`); the constants from `usd/constants.json` (164.05, 0.0707, 16,412.3 and 31,306.6 dollars before rounding to two significant digits); the pilot's sizes and its stop flag from `discovery/feasibility_t1.json` and the protocol; the BigQuery totals (8.78 TiB, USD 54.88; 26 jobs of this analysis, USD 12.63) from `describe/describe.json` (`timing`); the commit times of the plan and the registration from `git log` of the public repository (13:41:27 and 16:49:32 UTC on 9 October 2026, checked on 11 November 2026); the start of the extraction script (16:49:33) from the extraction manifest and the creation time of the scan B query (16:49:40) from `describe/describe.json` of the registered analysis (`timing.scan_b.created`); the library versions of the benchmark from `benchmark/benchmark.json` of the main analysis (`machine`), and the processor name and the memory from `machine_details` of the registered `benchmark/benchmark.json`, whose platform and processor strings are those of the main run (the same machine; build 26200 is Windows 11).

Statements about cited work that this revision added, and how each was checked (11 November 2026):

- Cho, Garcia-Molina and Page (1998): the question, the importance and ordering metrics, the 179,000 Stanford pages and the home page as the start of every crawl, the PageRank ordering against the backlink ordering when importance is the backlink count, the words "an excellent ordering metric", the small site of about 1,100 pages, and the topic experiment in which only the breadth-first crawler gave a reasonable result: read in the text of the paper (proceedings of WWW7).
- Najork and Wiener (2001): 328 million pages, breadth-first order finds pages of high PageRank early, steering a crawl of that size by PageRank is very expensive: read in the text of the paper (proceedings of WWW10).
- Baeza-Yates, Castillo, Marin and Rodriguez (2005): simulated crawls of two national domains, PageRank as importance, strategies more efficient than breadth-first and than strategies based on partial PageRank calculations: pages 1 to 4 of the authors' copy.
- Broder et al. (2000): the names SCC, IN and OUT for the parts of the web graph: pages 310, 317 and 318 of the article.
- Kitzler et al. (2023), Lin et al. (2024, account labeling), Victor and Weintraud (2021), Luo et al. (2025): each sentence follows the abstract (arXiv or Semantic Scholar).
- ERC-4337, ERC-1167 and ERC-1967: the EIP pages (EntryPoint, `validateUserOp`, `validatePaymasterUserOp`; the clone bytecode with the implementation address; the implementation slot). The Safe documentation page describes Safe as smart-account infrastructure and does not mention owners or a threshold; the sentence that cites it uses it only for what a Safe is, and the test (threshold and owners) is the study's own.
- Statements carried over with their citations from the version of 29 October 2026 were not read again in the sources.

## How to build

```bash
cd manuscripts/A-plos-one
export CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # checkout of the public repository; required by the generators
python3 -I make_tables.py                                # Tables 1-7 into main.tex, S1 Table rows; checks the quoted verdict
python3 -I figures/make_fig1.py                          # figures/fig1.pdf
(cd figures && pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig1.pdf Fig1)
latexmk -pdf -interaction=nonstopmode main.tex          # submission layout (bibtex runs automatically)
latexmk -pdf -interaction=nonstopmode main_preview.tex  # reading copy with Fig 1 embedded
latexmk -pdf -interaction=nonstopmode cover-letter.tex
cd supporting && for f in S1_Text S1_Table; do latexmk -pdf -interaction=nonstopmode $f.tex; done
```

Python 3 with matplotlib (3.11 used) and an Arial-metric font. The scripts add their own folder to `sys.path`, so they also run in isolated mode (`-I`). The supporting files use the default Computer Modern fonts (the `lmodern` package is not installed in the build environment). The generators read the four discovery summaries (about 9 MB each).

On the Windows checkout (11 November 2026) the scripts ran as `python -I -X utf8 <script>` and the PDFs were built with MiKTeX: `pdflatex -interaction=nonstopmode`, `bibtex` (main and main_preview), then `pdflatex` twice. MiKTeX's `pdftoppm` (poppler 24.04) has no `-tiff` option, so `Fig1.tif` was written in two steps: `pdftoppm -png -r 300 -singlefile fig1.pdf Fig1`, then Pillow, `Image.open("Fig1.png").convert("RGB").save("Fig1.tif", compression="tiff_lzw", dpi=(300, 300))`.

Checks:

```bash
python3 -I check_numbers.py main.tex cover-letter.tex supporting/S1_Text.tex supporting/S1_Table.tex
python3 -I ../tools/overlap_check.py main.tex
grep -nE "earlier|originally|instead of|33-month|no longer|removed|dropped|previously|formerly|replaced|redesign|reframe|wallet node|EOA node|user node|GMX|trader|liquidat|\bR[123]\b|\bF[345]\b|Bonferroni|neutral|2\{,\}000|credit|collateral|title" *.tex *.md supporting/*.tex supporting/*.md
```

The third command is the search check of the revision notes; every hit is sorted by hand (see the changes below).

## Changes of 11 November 2026

The paper reports the contract-graph analysis as its main analysis and leads with the discovery-order test. The numbers are those published in commit `6b389df` of the public repository (branch `contract-graph`), computed at code revision `bb78da3`; the per-contract parquet files are listed in `drive-manifest.json` at `7aa7928`.

What each file holds now:

- `data_sources.py`: reads `revised-contract-12m` (constant `REV`), the four discovery summaries (`discovery(tag, mode)`), the description, cohort, typing, constants and pilot summaries; reads the score windows from the published configuration; helpers for the areas (`auc`) and for a point of a curve (`curve_at`).
- `make_tables.py`: Tables 1 to 7 and the four panels of S1 Table (see "Where each number comes from"); checks that the verdict follows from the intervals and that `main.tex` quotes the recorded statement.
- `figures/make_fig1.py`, `figures/fig1.pdf`, `figures/Fig1.tif`: the discovery curves of the deciding run (A, B) and the walk-minus-count contrasts on the spender labels (C).
- `check_numbers.py`: also reads the two documents of the main analysis and the quoted curve points; skips the per-seed lists and curves; reads a value written as m × 10^e in the form of the sources; ignores lengths of the page layout.
- `main.tex`: new title, abstract, Introduction (three contributions, companion paragraph), Related work (crawl ordering; contracts as a population), Materials and methods (data, account types and graphs; order of the analyses; scores; the discovery-order test; checks and labels; statistics; closed-form check and runtime; ethics; data availability; use of generative AI), Results (the contract graph; the decision; outside the decision; other settings, the other reveal mode and the other freeze; same window; out of window; closed form; cost; the registered analysis), Discussion (what the test shows and what it does not; the walks against their counts; practical implications; limitations), Conclusions and the list of supporting information.
- `references.bib`: 60 entries. Entries added from the thesis bibliography: `cho1998crawling`, `najork2001breadth`, `baezayates2005crawling`, `kitzler2023defi`, `lin2024whoiswho`, `victor2021washtrading`, `broder2000graph`, `buterin2021erc4337`, `murray2018erc1167`, `palladino2019erc1967`, `safenddocs`. The entry `kwon2026coupling` carries the companion's current title. Entries that the text does not cite are not kept, the companion entry apart.
- `cover-letter.tex`: the title, the running title and the summary of this paper; the date line was left as it was.
- `supporting/S1_Text.tex`, `supporting/S1_Table.tex` with its four row files, `supporting/S1_File.md`: written for the contract-graph analysis (see "Files").
- Files deleted from the folder: `supporting/S2_Table.tex`, `S2_Table.pdf`, `S2_Table_rows.tex` and `supporting/make_s2_table.py`. New files: `supporting/S1_Table_rows_b.tex`, `_rows_c.tex`, `_rows_d.tex`.

Table and figure plan: Table 1 (graph, coverage, closed form), Table 2 (the decision), Table 3 (outside the decision, items 1 to 4), Table 4 (sensitivities, other mode, other freeze), Table 5 (same window), Table 6 (spender holdouts), Table 7 (registered beside main), Fig 1 (three panels), S1 Table (four panels). The share of the summed importance held by the visited contracts, which the protocol reports as curves only, is given in the text and in S1 Table D. Two items of the protocol's list are in the published summaries and are not reported in the paper: the second curve (`curves.P_CS`) and the share of the union pairs read (`curves.cost`).

Build and checks of 11 November 2026 (MiKTeX, Windows):

- `main.pdf` 32 pages, `main_preview.pdf` 33 pages (Fig 1 on page 17), `cover-letter.pdf` 1 page, S1 Text 9 pages, S1 Table 5 pages. No errors, no undefined references or citations, no overfull or underfull boxes, no LaTeX warnings. BibTeX issues 8 benign warnings for the four `@misc` web sources (Human Passport, DefiLlama, Chainlink, Safe: no editor or publisher), the same number as before.
- Abstract: 296 words in the PDF text (`pdftotext`, split on white space; limit 300), no citations.
- `make_tables.py`: wrote Tables 1 to 7 and the S1 Table rows; the verdict sentence is quoted word for word. `figures/make_fig1.py`: wrote `fig1.pdf`.
- `check_numbers.py` on the four `.tex` files: the numbers it does not find are listed above (6 in `main.tex`, 5 in S1 Text, none in S1 Table and the cover letter).
- Search check on the `.tex` and `.md` files of the folder, every hit sorted. `cover-letter.tex`: "Running title" (a label). `main.tex`: "title" in a comment of the PLOS template; "credit" three times in one sentence of Related work, where it describes other work (twice inside citation keys), and once in the last sentence of Practical implications, as a later use that was not tested. `README.md`: "title" in a label and in sentences about the titles of the two manuscripts, "journaltitle" (a BibTeX field), "accredited" (the journal's accreditation) and the command above. `supporting/`: no hit.
- Text overlap with the thesis as it stood on that day, while its chapters were being revised (`manuscripts/tools/overlap_check.py`, 8-word shingles): `main.tex` 4.8% of 13,968 words; the longest shared spans are the verdict statement (73 words), the sentence of the order-of-events passage (69 words) and the verdict wordings V1 and V3 (54 and 21 words), all quoted on purpose; the longest span that is not a quotation is the question of the test (38 words). S1 Text 1.7% (longest 21 words); cover letter 4.1% (longest 29 words, the verdict in the letter's words).
- S1 File: 4 pieces of the plan and 8 of the registration are verbatim and in order; 3 and 7 omissions are marked; the four hashes match.
- Order of the floats: each of Table 1, Table 2, Fig 1 and Tables 3 to 7 is first cited before it appears, and the first citations come in that order (checked by script). Every cited key has an entry in `references.bib`, and every entry is in the thesis bibliography except the companion's. Not run: the DOI link check.

The entries of this file for 29 October and 4 November 2026 are in its Git history.

## References style: vancouver.bst now, plos2015.bst at acceptance

The review PDF uses `\bibliographystyle{vancouver}` (numbered, in order of citation), which matches PLOS ONE in substance. PLOS's own `plos2015.bst` is not in TeX Live and is needed only for the final files. At acceptance:

1. Download `plos2015.bst` from https://journals.plos.org/plosone/s/latex.
2. Switch `\bibliographystyle{vancouver}` to `\bibliographystyle{plos2015}` and run bibtex.
3. Paste the contents of `main.bbl` into `main.tex` in place of `\bibliography{references}` (PLOS does not accept `.bib` files).
4. Check that each DOI, which sits in the `note` field, prints once.

**Companion manuscript.** PLOS ONE keeps submitted, unaccepted manuscripts out of the reference list. Manuscript A therefore mentions Manuscript B in the text only ("A companion manuscript by the same authors (unpublished)") and uploads it as a *Related manuscript* file. If B is posted as a preprint or accepted before A is published, cite it; the `kwon2026coupling` entry is ready and carries B's current title ("Coupling authorization and payment edges in one PageRank walk for ranking smart contracts: Commit-gated rules and a contract-graph re-analysis on an Ethereum rollup"); match it again if B's title changes.

## Statements to enter in the submission system (Editorial Manager)

- **Author contributions (CRediT; to be confirmed by all authors):** Taehong Kwon: Conceptualization, Methodology, Software, Data curation, Formal analysis, Writing – original draft. Ernest Mnkandla: Supervision, Writing – review & editing. Donatien Koulla Moulla: Supervision, Writing – review & editing. David Sena Attipoe: Supervision, Writing – review & editing.
- **Competing interests:** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
- **Funding:** The authors received no specific funding for this work.
- **Data availability:** use the "Data availability" subsection of `main.tex`. It names the public repository `ERC20-Allowance-PageRank-Wallet-Reputation`, folder `experiments`, which holds the study's folder of the authors' private repository with its history (new commit identifiers; `HISTORY.md` lists the original ones), with the plan `d060f3a`, the registration `1747e64` and the registered results `344017e`, the results of the main analysis `6b389df` computed at code revision `bb78da3` (commit-pinned link), the public Google Drive folder of the per-contract parquet files through `drive-manifest.json` at `7aa7928`, and `phd-dissertation-draft-en` (folders `analysis/` and `manuscripts/A-plos-one/`).
- **Ethics statement:** Only public blockchain data and public token prices were used; no human participants; only contracts are scored. [ethics clearance reference to be added by the authors] Do not submit while this bracket is in `main.tex`: PLOS's technical check returns a manuscript with a placeholder.
- **Use of AI tools:** the full statement is in Methods ("Use of generative AI"), with a pointer in Acknowledgments.
- **Related manuscript:** upload Manuscript B (`manuscripts/B-ieee-access/main.pdf`) as a "Related manuscript" file.

## Open items for the authors

1. **Ethics statement (required before submission):** insert the UNISA ethics clearance reference (committee name and number) and delete the bracket in `main.tex`; if the committee confirmed that no clearance was needed, state that with the committee's name.
2. **Cover letter date:** the date line reads 29 October 2026; set the date of submission.
3. **Branch of the cited commits:** `6b389df`, `bb78da3` and `7aa7928` are on the branch `contract-graph` of the public repository (pushed), not on `main`; the plan, the registration and the registered results are on `main`. The link of the Data availability statement is pinned to the commit and works while the commit stays reachable; merge the branch or tag the commit before submission.
4. **Archived release (required before submission):** a GitHub folder path is not a stable location (the parquet files are kept in a Google Drive folder), and both public repositories also hold material outside this study. Archive a tagged release on Zenodo that contains the experiment folder of the public repository and `analysis/` plus `manuscripts/A-plos-one/` of this repository, and cite its DOI in the Data availability statement and the cover letter.
5. **Use of generative AI:** confirm the sentence on the experiment repository ("Under the first author's direction it wrote and ran parts of the extraction and evaluation code in the first repository").
6. **Companion manuscript:** the Introduction of A, the Introduction of B and both cover letters must carry the same list: in both papers the data, the account types and the graphs, the spender holdout coefficients of the raw counts, EndorseRank and AWP with their count contrasts, the closed form of EndorseRank and the solver runtimes; only in A the discovery-order test; only in B the rules for C-PR, its weight sweep, the seeded ablation and the Sybil calibration. Check that B reports the same values before either is submitted. The cover letter of A says that B "is being submitted at the same time"; the Introduction calls it unpublished.
7. **Supervisors' confirmation** that the contract-graph analysis is the main analysis and that the discovery-order test leads the paper (open in the thesis notes as well).
8. **Approval and ORCID:** every co-author approves the final PDF; enter ORCID iDs and CRediT roles in the submission form.
9. **Fig 1:** run PACE (https://pacev2.apexcovantage.com/) on `figures/Fig1.tif`.
10. **Web sources:** the access dates of the four web sources are those of the thesis bibliography (9 and 10 October and 11 November 2026); update them if the pages are checked again before submission.
11. **Standards named without a reference:** ERC-721, EIP-6780 (S1 Text) and Permit2 are named in the text without a citation. The thesis bibliography has `ballet2023eip6780`; it has no entry for ERC-721 or Permit2. Decide whether to add them.
12. **The largest owner contract at T_obs** holds 98,073 of the 115,006 capped allowance pairs and lies outside the universe of the deciding run (16,776 capped allowance pairs lie inside it). The paper states the concentration and says that the study does not identify the contract; its address is in the per-contract files. Decide whether to describe it.
13. **Results that the summaries do not hold:** the receiving subset (spenders that another contract had paid) and the union-graph subset are computed for W0 only, so the paper gives no W1 value; the token share 75.75% is that of the five tokens among the events around the plan's cohort up to T_obs (`usd/usd_inputs.json`), not their share of the whole chain's events, which is not published.
14. **Cells that the short summaries state more coarsely:** in the deciding run EndorseRank-activity′ lies above the allowance backlink count on I_A (+0.0161 [+0.0136, +0.0185]) and is not resolved from it on I_T; at t1 in the `both` mode it lies above that count on both importances (+0.0049 [+0.0035, +0.0061] and +0.0332 [+0.0300, +0.0362], S1 Table C). The paper reports these cells, and says "not above on inflow" only of the deciding run.

## Claim discipline

- Scored and evaluated objects are always "contracts"; user accounts enter only as sums over accounts in the importance measures and the labels.
- The decision of the discovery-order test concerns C-PR′ only, and the answer to its question is no (V2 on both importances); what AWP′, the allowance-only walks, the `out` mode and the other freeze show is reported outside the decision and without a verdict.
- The test "was defined after the registered results were known" and "decides no rule of the plan or the registration"; nothing of the main analysis is called registered, pre-specified or planned, and no date or time of its definitions is given.
- Same-window agreement with a score's own edges is an "intended-construct check", never validation.
- Every τ and Δτ comes with its 95% interval, every discovery contrast with its interval at four decimals; no interpretation bands, no p-values.
- AWP against the transfer in-degree out of window is stated in both directions; EndorseRank below the in-approve degree is stated for both windows and both restart rules; the two frames (labels count mostly user accounts; about 27% of each spender cohort scores zero) accompany the out-of-window numbers.
- The runtime difference is a consequence of the graph (edges, nodes and the iterations a walk needs), not a contribution.
- No "significant", "demonstrates", "confirms" or "proves"; no claim that any score measures the safety of a contract's code; lending appears only as background of related work and as a later use that was not tested.
- Statements about a cited paper are limited to what was read in the paper or its abstract.
