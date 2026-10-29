# Manuscript A: PLOS ONE submission package

**Title:** Allowance edges or transfer edges? Evaluating on-chain smart contract reputation out of window against degree baselines

**Running title (61 characters, limit 70):** Allowance versus transfer edges for smart contract reputation

**Article type:** PLOS ONE Research Article

**Authors:** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

## What the paper reports

The study scores and evaluates only smart contracts on Arbitrum One. Every score of the analysis it reports is computed from the twelve months before its freeze: 1 July 2025 to 30 June 2026 for the same-window evaluation and W1, 1 April 2025 to 31 March 2026 for W0. The matched cohort holds the 6,483 contracts that at least three owners approved on WETH, USDC, USDT0, ARB or WBTC in the score window of T_obs; W0 draws its own cohort by the same rule in its window (6,343 contracts, 5,383 of them also in the matched cohort). It compares EndorseRank (PageRank on the latest ERC-20 allowances, with AWP's edge weights and uniform restarts) with the transfer-based AWP of Do, Do and Nguyen (2023) and with the raw in-approve degree and transfer in-degree. Main points:

- Intended-construct checks in the same window: each score agrees most with the checks of its own edges, partly by construction (Table 2).
- Out of window, in W0 (freeze 31 March 2026, labels April to June) and W1 (freeze 30 June, labels July to September): neither walk beats its raw degree. AWP falls below the transfer in-degree on new senders, EndorseRank below the in-approve degree on new approval pairs, and the activity-restart variant, although above EndorseRank, also below the in-approve degree. All degree contrasts were computed after the labels (none is named in the plan or the registration document) (Table 3, Fig 1A).
- Closed form: a spender whose owners are not themselves approved scores c(1 + d δ(v)); this holds within 1% for every such spender (Table 1).
- Outcomes built from neither edge type (GMX V2 contract traders): the registered rules R1 to R3 applied to the revised scores give R1 holds (P in W1 +0.141, 97.5% interval [0.026, 0.256]), R2 does not hold, R3 applies (Tables 4 and 5, Fig 1B and 1C).
- The registered analysis (raw base units, every ERC-20, every event since 1 October 2023, cohort 27,844) reached the same verdicts on R2 and R3 but did not meet R1, and there AWP and the activity variant rose above their degrees (Table 6).
- The 2.21 edge ratio and the 3.21 time ratio (94 against 57 iterations) are reported as a consequence of graph size and iteration count only.

**Status words.** The revised analysis (US dollars, five tokens, scores from the twelve months before each freeze) was defined after the registered results were known and is the main analysis here. Its verdicts under R1 to R3 are always called a re-analysis with the registered rules, never registered results; R1 holding is a result of the re-analysis only. Registered values appear only in sentences and table columns labelled "registered analysis". No sentence says or implies that the twelve-month windows were planned or registered, or says when the definitions of the revised analysis were fixed; every sentence that says what was defined after the registered results were known names the score windows with the amounts and the tokens.

## Target journal and why it was chosen

- **PLOS ONE** is DHET-accredited through its Scopus and DOAJ indexing, which meets the UNISA requirement of a first-author article in an accredited journal.
- It reviews for scientific soundness, not perceived impact, and it publishes negative and null results. Several central results here are negative or qualified: no PageRank beats the raw count of its edges out of window, with uniform or activity restarts; the PageRank comparison on trader outcomes is not resolved; the one positive trader result (R1) holds in the re-analysis but not in the registered analysis.
- The companion Manuscript B (coupled walk C-PR and its ablation S-PR, rules A and B, the registered test, Sybil exposure) goes to IEEE Access. The Introduction of A states which results appear in both papers.

## Files

| File | What it is |
|---|---|
| `main.tex` | Manuscript in the PLOS ONE LaTeX layout (article class, rebuilt by hand from the PLOS template). Figures are **not** embedded, per PLOS policy. The Fig 1 caption follows the paragraph that first cites it, and each table follows the paragraph that first cites it. Tables 1 to 6 sit between `% BEGIN GENERATED tabN` / `% END GENERATED tabN` markers and are written by `make_tables.py`; do not edit them by hand. |
| `main.pdf` | Build of `main.tex`: submission layout with line numbers and no embedded figure. |
| `main_preview.tex`, `main_preview.pdf` | Reading copy for the authors with Fig 1 embedded (6.9 in wide). Not for submission. |
| `references.bib` | Bibliography: 53 entries. The 52 cited entries are each copied from the thesis bibliography `Config/references.bib` (same key) and converted to BibTeX for `vancouver.bst` (journaltitle to journal, report to techreport, online to misc, eid to pages, DOI as an `https://doi.org/` link and URL in `note`, accents as TeX accents). The uncited 53rd entry, `kwon2026coupling`, is Manuscript B with its current title (see "References style"). |
| `cover-letter.tex`, `cover-letter.pdf` | One-page cover letter dated 29 October 2026. |
| `data_sources.py` | Shared loader for the scripts below. Needs `--phd-works PATH` or `PHD_WORKS`; nothing is guessed. Reads the registered summaries from `3-published-results-for-thesis/` and the revised ones from its subfolder `revised-usd-12m/` (constant `REV`), and checks every published summary against its `SHA256SUMS.txt` (CRLF form, as the checksums were taken on a Windows checkout) before use. |
| `make_tables.py` | Writes Tables 1 to 6 into `main.tex` and the rows of S1 Table (`supporting/S1_Table_rows.tex`) from the published summaries and `analysis/*.json`. The score windows in Tables 1 and 6 and S1 Table are read from the cohort rules (`cohort/matched_cohort.json`, `cohort/cohort_t1.json`). |
| `check_numbers.py` | Lists every number in the prose of a `.tex` file (tables skipped) that does not occur in a source (both results digests, the published summaries, `analysis/*.json`). |
| `figures/make_fig1.py` | Fig 1 (panels A, B, C, bold uppercase letters as in PLOS figures; the line styles are explained in the caption, not in the figure) from `revised-usd-12m/holdout-w0/eval_summary.json`, `window-w1/eval_summary.json`, `supplementary/supplementary.json` and `analysis/neutral-label/results.json`. Arial-metric sans serif: Liberation Sans where installed, else Arial (the current `fig1.pdf`, built on Windows, embeds Arial and Arial Bold), 8 pt or larger, 7.2 in wide; axis ranges follow the data. Categorical colours: slots 1 and 2 of the dataviz reference palette (validated, CVD ΔE 24.7), plus circle/square markers as a second encoding. |
| `figures/fig1.pdf` | Vector source of Fig 1. |
| `figures/Fig1.tif` | Fig 1 for upload: 2160 x 1770 px (7.2 x 5.9 in) at 300 dpi, RGB, LZW-compressed TIFF. |
| `supporting/S1_Text.tex`, `.pdf` | **S1 Text.** Event decoding, score windows and the cohort of each freeze, account type, token rule and US-dollar valuation, graph weights and constants, GMX decoding, label formulas (including the revocation and drain counts that the main text reports without offering them as evidence), same-window checks, SQL patterns, properties not quantified. Constants copied from the pipeline config, SQL and scripts in `phd_works` and from `revised-usd-12m/usd/constants.json` (named in the file header). |
| `supporting/S1_File.md` | **S1 File.** The two pre-specification documents verbatim: analysis plan at `43d8045` and W1 registration at `0d3a057`, with full commit ids and SHA-256 hashes (LF and CRLF). The embedded copies were checked byte for byte against `git show <commit>:<path>` (29 October 2026). The documents that define the revised analysis are not reproduced; they are published with the revised results (Data availability). |
| `supporting/S1_Table.tex`, `.pdf`, `S1_Table_rows.tex` | **S1 Table.** Windows, cohorts, graphs and amounts. Rows generated by `make_tables.py`; the footnotes are typed (sources below). |
| `supporting/S2_Table.tex`, `.pdf`, `S2_Table_rows.tex`, `make_s2_table.py` | **S2 Table.** Every registered pair (P, Q, EndorseRank − AWP, C-PR(λ=1) − C-PR(λ=0), C-PR(λ=0) − AWP, and EndorseRank − in-approve degree from the committed code) on all six trader labels, both windows, both analyses, with the stratified rows; 95% and 97.5% intervals. Generated from `analysis/neutral-label/results.json`; the share of positive resamples is not exported. |

## Where each number comes from

All summaries are in `phd_works`, folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/data/3-published-results-for-thesis/` (registered analysis) and its subfolder `revised-usd-12m/` (revised analysis); the two `results_digest.md` files name the JSON key of every value. `analysis/closed-form/closed_form_check.json` and `analysis/neutral-label/results.json` hold the twelve-month values in their "revised" entries (regenerated in commit `3cf5dc8` of this repository).

| Table / figure | Content | Source of the numbers |
|---|---|---|
| Table 1 | Score windows, cohorts, graphs at both freezes and fit of the closed form | `revised-usd-12m/same-window` and `holdout-w0/eval_summary.json` (`graph`, `closed_form`), through `analysis/closed-form/closed_form_check.json`; `cohort/matched_cohort.json` and `cohort/cohort_t1.json` (`rule`, `cohort`) |
| Table 2 | Same-window intended-construct check, ranking agreement | `revised-usd-12m/same-window/eval_summary.json` (`families`, `per_proxy`, `contrasts`, `inter_method`) |
| Table 3 | Spender holdouts W0 and W1, degree contrasts, EndorseRank − AWP | `revised-usd-12m/holdout-w0/eval_summary.json` (`taus`, `contrasts_after`), `window-w1/eval_summary.json` (`spender_taus`, `endorserank_results`), `supplementary/supplementary.json` |
| Table 4 | Trader comparison on the liquidation-free close rate, both windows | `analysis/neutral-label/results.json`, `analyses.revised.windows.<W1,W0>.contrasts` and `.stratified` |
| Table 5 | Recipients against other traders, influence check | `analysis/neutral-label/results.json`, `recipients`, `influence_without_top10`, `max_in_approve_degree` |
| Table 6 | Registered analysis beside the revised analysis, including the score windows, the trader cohorts, EndorseRank − AWP and C-PR(λ=1) − C-PR(λ=0) on the liquidation-free close rate in both windows | same-window, holdout-w0, registered-w1 / window-w1 summaries and `supplementary.json` of both analyses; the cohort rules of `revised-usd-12m`; `closed_form_check.json`; `results.json` (both analyses, `windows.<W1,W0>.n`, `.contrasts`, `rules`) |
| Fig 1 | (A) PageRank minus raw degree on spender labels; (B) P and (C) Q on six trader labels | as Table 3 for A; `analysis/neutral-label/results.json` for B, C |
| S1 Table | Descriptive | `revised-usd-12m` summaries (`same-window`, `holdout-w0`, `window-w1`, `describe/describe.json`, `cohort/matched_cohort.json`, `cohort/cohort_t1.json`), `results.json`; footnote counts 7,962 = 7,914 + 39 + 9 (`holdout-w0` : `spender_account_types`) and 12 W0 traders with a liquidation = 48 × (1 − 0.750) (`recipients.others`) |
| S2 Table | All trader contrasts | `analysis/neutral-label/results.json` |

Numbers in the prose that `check_numbers.py` does not find in a source (last run 29 October 2026), all checked by hand:

- `main.tex`: EIP numbers (721, 2612); block 513,216,506 (thesis Section 3.2 and Appendix 8.1.3); 79.40%, the share of the five tokens in the rows of all tokens in the score window of T_obs (467,345,054 / 588,568,431 from `revised-usd-12m/usd/token_rows_12m.json`, `per_listed_token[].rows_total` of the selected tokens over `rows_in_window`; thesis Appendix 8.4.2); 7,962 W0 spenders (7,914 + 39 + 9); 365 (days in a score window); σ(0) = 0.858 and σ(90) = 0.711 (computed from k = 0.01, t0 = 180; σ(182) = 0.495 and σ(365) = 0.136 pass by chance); c = 1.93 × 10⁻⁷ (1.928e-07 rounded); "950", the leading digits of commit `950a7a4`; the layout length 2.25 in.
- `S1_Text.tex`: chain id 42161; block 513,216,506; EIP numbers (721, 2612, 6780); 79.40%; 365.
- `S1_Table.tex`: the layout lengths 7.2, 4.3 and 22.5 cm; 7,962 (as above).
- `cover-letter.tex`: none.
- Derived in the text and stated as such (they pass the check, some by chance): 2.21 (edge ratio, in the digest); "0.20 wide" (97.5% interval of Q in W1: 0.127 − (−0.071)) and "an estimate of 0.1 or less" (about the half-width of that interval, 0.099; every degree contrast in Table 3 is smaller in size); "one in six" (992 / 6,224 deeper spenders at T_obs; 1,342 / 7,914 W0 spenders without a transfer edge) and "one in three" (2,813 / 7,905); 21.9% (1,732 / 7,914) and 18.0% (1,422 / 7,914); the tie shares 2.87% (AWP, `holdout-w0` : `ties.awp`, 0.0287) and 0.058% (EndorseRank, 0.0005817).

Other text sources: the candidate count 29,022 = 27,844 + 1,121 + 57 is in the registered `results_digest.md` (`cohort/matched_cohort.json` : `candidates`); the score windows from the cohort rules and the header of the revised digest; the constants from `usd/constants.json` (raw medians 169.33 and 99.97 dollars, 99th percentile 18,575.3 dollars, each rounded to two significant digits); the token rule, the 548 priced days and the price check from thesis Sections 3.2 and 3.5.1 and Appendix 8.4.2 and from `describe/describe.json` (`price_days`, `chainlink_check_in_windows`); the BigQuery totals (6.76 TiB, USD 42.24) from `describe/describe.json` : `timing`; commit times of the plan and the registration from `git -C phd_works log`; the creation time of the scan B query (16:49:40) from `describe/describe.json` (registered analysis); the benchmark machine from thesis Appendix 8.1.1 (Pipeline stages).

## How to build

```bash
cd manuscripts/A-plos-one
export PHD_WORKS=/path/to/phd_works                     # required by the generators
python3 -I make_tables.py                                # Tables 1-6 into main.tex, S1 Table rows
python3 -I supporting/make_s2_table.py                   # S2 Table rows (reads analysis/ only)
python3 -I figures/make_fig1.py                          # figures/fig1.pdf
(cd figures && pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig1.pdf Fig1)
latexmk -pdf -interaction=nonstopmode main.tex          # submission layout (bibtex runs automatically)
latexmk -pdf -interaction=nonstopmode main_preview.tex  # reading copy with Fig 1 embedded
latexmk -pdf -interaction=nonstopmode cover-letter.tex
cd supporting && for f in S1_Text S1_Table S2_Table; do latexmk -pdf -interaction=nonstopmode $f.tex; done
```

Python 3 with matplotlib (3.11 used) and an Arial-metric font. The scripts add their own folder to `sys.path`, so they also run in isolated mode (`-I`). The supporting files use the default Computer Modern fonts (the `lmodern` package is not installed in the build environment).

On the Windows checkout (29 October 2026) the scripts ran as `python -I -X utf8 <script>` and the PDFs were built with MiKTeX from PowerShell: `pdflatex -interaction=nonstopmode`, `bibtex` (main and main_preview), then `pdflatex` twice. MiKTeX's `pdftoppm` (poppler 24.04) has no `-tiff` option, so `Fig1.tif` was written in two steps: `pdftoppm -png -r 300 -singlefile fig1.pdf Fig1`, then Pillow, `Image.open("Fig1.png").convert("RGB").save("Fig1.tif", compression="tiff_lzw", dpi=(300, 300))`.

Checks:

```bash
python3 -I check_numbers.py main.tex cover-letter.tex supporting/S1_Text.tex supporting/S1_Table.tex
python3 -I ../tools/overlap_check.py main.tex
```

## Changes of 29 October 2026

- The paper reports the revised analysis with scores from the twelve months before each freeze, published in `phd_works` commit `950a7a4` (code revision `0a94215`, named in the digest), folder `revised-usd-12m/`. `data_sources.py` reads that folder; `make_tables.py` adds the score windows and the cohort of each freeze to Table 1, the score windows and the trader cohorts to Table 6 and the cohort of each freeze to S1 Table; `make_fig1.py` sets its axis ranges from the data and falls back to Arial where Liberation Sans is missing; `make_tables.py` and `check_numbers.py` run under `python -I`.
- Regenerated Tables 1 to 6, S1 and S2 Table rows and Fig 1 (`fig1.pdf`, `Fig1.tif`), and rewrote from the twelve-month digest every number and claim of the abstract, the main text, the cover letter (dated 29 October 2026), S1 Text (score windows, cohorts, constants m_T = 170, m_A = 100 and U = 19,000 dollars, prices, labels, SQL patterns), the S1 Table footnotes and the S2 Table note.
- Verdicts reported: out of window no PageRank beats the raw degree it smooths, in either window; R1 holds in the re-analysis but not in the registered analysis; R2 does not hold; R3 applies. Discussion, practical implications, limitations and conclusions follow these verdicts; the next step named is a registered test of the count-level lead on more contract traders.
- Wording rules applied: wherever the text says what was defined after the registered results were known, it names the score windows with the amounts and the tokens; it gives no date or time of the commits of the revised analysis and does not say when its definitions were fixed; no change-narrative words outside the passages about the plan and the registered analysis.
- S1 File holds the plan and the W1 registration only; the documents of the revised analysis are reached through the Data availability statement. That statement names the plan, the registration and the registered results (folder `...-Contract-Reputation/experiments` at those commits), the revised results `950a7a4` with code revision `0a94215` (folder `...-Wallet-Reputation/experiments`, commit-pinned link), the per-contract parquet files through `drive-manifest.json` at `ac7d32a`, and the BigQuery totals of the whole study (6.76 TiB, USD 42.24).
- The preview embeds Fig 1 at 6.9 in (at 7.0 in a float page was 3.2 pt too tall).

## Last build and checks (29 October 2026)

- `main.pdf` 26 pages, `main_preview.pdf` 27 pages, `cover-letter.pdf` 1 page, S1 Text 6 pages, S1 Table 1 page, S2 Table 5 pages, all rebuilt with MiKTeX pdflatex (with bibtex for `main` and `main_preview`). No errors, no undefined references or citations, no overfull boxes. The preview build notes that a `!h` float became `!ht` and that one page holds only floats. BibTeX issues the 8 benign warnings for the four `@misc` web sources (GMX, Human Passport, DefiLlama, Chainlink: no editor or publisher).
- Abstract: 296 words in the PDF text (`pdftotext`, split on white space; limit 300), no citations.
- Text overlap with the thesis (`manuscripts/tools/overlap_check.py`, 8-word shingles): `main.tex` 1.4%, longest shared span 17 words (the registered wording of the decision contrasts, quoted on purpose); S1 Text 0.7%, longest 15 words; cover letter 0.1%, longest 8 words.
- `check_numbers.py`: every data number in the prose occurs in a source; the exceptions are listed above.
- Not re-run on 29 October: the DOI link check and the script that checks the order of first citations of the floats (the bibliography and the order of the floats did not change).

## References style: vancouver.bst now, plos2015.bst at acceptance

The review PDF uses `\bibliographystyle{vancouver}` (numbered, in order of citation), which matches PLOS ONE in substance. PLOS's own `plos2015.bst` is not in TeX Live and is needed only for the final files. At acceptance:

1. Download `plos2015.bst` from https://journals.plos.org/plosone/s/latex.
2. Switch `\bibliographystyle{vancouver}` to `\bibliographystyle{plos2015}` and run bibtex.
3. Paste the contents of `main.bbl` into `main.tex` in place of `\bibliography{references}` (PLOS does not accept `.bib` files).
4. Check that each DOI, which sits in the `note` field, prints once.

**Companion manuscript.** PLOS ONE keeps submitted, unaccepted manuscripts out of the reference list. Manuscript A therefore mentions Manuscript B in the text only ("submitted to *IEEE Access*; unpublished") and uploads it as a *Related manuscript* file. If B is posted as a preprint or accepted before A is published, cite it; the `kwon2026coupling` entry is ready and carries B's current title ("Coupling authorization and payment layers in a PageRank walk for smart-contract reputation: A pre-specified, commit-gated out-of-window test on an Ethereum rollup"); match it again if B's title changes.

## Statements to enter in the submission system (Editorial Manager)

- **Author contributions (CRediT; to be confirmed by all authors):** Taehong Kwon: Conceptualization, Methodology, Software, Data curation, Formal analysis, Writing – original draft. Ernest Mnkandla: Supervision, Writing – review & editing. Donatien Koulla Moulla: Supervision, Writing – review & editing. David Sena Attipoe: Supervision, Writing – review & editing.
- **Competing interests:** The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.
- **Funding:** The authors received no specific funding for this work.
- **Data availability:** use the "Data availability" subsection of `main.tex`. It names `phd_works` with the plan `43d8045`, the registration `0d3a057` and the registered results `8d8b568` (folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments` at those commits) and the revised results `950a7a4`, computed at code revision `0a94215` (folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments`, with a commit-pinned link), the public Google Drive folder of the per-contract parquet files through `drive-manifest.json` at `ac7d32a`, and `phd-dissertation-draft-en` (folders `analysis/` and `manuscripts/A-plos-one/`). `950a7a4` and `ac7d32a` are on the branch `claude/score-windows-12m` of `phd_works` and not yet on GitHub; the link resolves only once they are pushed (item 10).
- **Ethics statement:** Only public blockchain data and public token prices were used; no human participants; only contracts are scored. [ethics clearance reference to be added by the authors] Do not submit while this bracket is in `main.tex`: PLOS's technical check returns a manuscript with a placeholder.
- **Use of AI tools:** the full statement is in Methods ("Use of generative AI"), with a pointer in Acknowledgments.
- **Related manuscript:** upload Manuscript B (`manuscripts/B-ieee-access/main.pdf`) as a "Related manuscript" file.

## Open items for the authors

1. **Ethics statement (required before submission):** insert the UNISA ethics clearance reference (committee name and number) and delete the bracket in `main.tex`; if the committee confirmed that no clearance was needed, state that with the committee's name instead. The thesis also has it as [TBD].
2. **Tag a release of the second repository:** `analysis/` and every file of this folder, the generators included, are committed on `main` (`__pycache__/` is ignored). Tag a release (the existing tag `manuscripts-2026-11` points to an older state and must not be cited for this version) and add the commit or tag to the Data availability statement.
3. **Use of generative AI:** confirm the sentence on the experiment repository ("Under the first author's direction it wrote and ran parts of the extraction and evaluation code in the first repository"). The commits from `43d8045` onward, `950a7a4` included, carry the first author's account name; commit `7129981` set the repository so that Claude attribution lines are not added.
4. **Companion manuscript:** the Introduction of A, the Introduction of B and both cover letters use the same list of shared results (spender holdout coefficients of the raw degrees, EndorseRank and AWP with their degree contrasts; the closed form of EndorseRank; the solver runtimes), say that P, Q and R1–R3 are reported only in A and that B reports on the same trader cohort only the contrasts of its coupled walk that its own rule names. A also says that both papers report the same values for both analyses: check that B reports the same twelve-month revised analysis before either is submitted. The cover letter of A still says that B "has been submitted to *IEEE Access*", while the Introduction calls it unpublished; align both when B is submitted.
5. **Supervisors' confirmation** that the revised analysis, with its twelve-month score windows, replaces the registered one as the main analysis (open in the thesis notes as well).
6. **Approval and ORCID:** every co-author approves the final PDF; enter ORCID iDs and CRediT roles in the submission form.
7. **Fig 1:** run PACE (https://pacev2.apexcovantage.com/) on `figures/Fig1.tif`.
8. **Web sources:** access dates of the four web sources are those of the thesis bibliography (9 and 10 October 2026); update them if the pages are checked again before submission.
9. **Archived release (required before submission):** a GitHub folder path is not a stable location (the experiment folder has two names in the cited commits, and its parquet files are kept in a Google Drive folder), and both repositories also hold material outside this study. Archive a tagged release on Zenodo that contains only the experiment folder of `phd_works` and `analysis/` plus `manuscripts/A-plos-one/` of this repository, and cite its DOI in the Data availability statement and the cover letter. Until then the statement points to commit `950a7a4`.
10. **Publish the cited commits:** `950a7a4` (revised results) and `ac7d32a` (Drive manifest with the twelve-month parquet files) are on the local branch `claude/score-windows-12m` of `phd_works`, not on GitHub. Push and merge that branch before submission, or the commit-pinned link and the commits named in the Data availability statement cannot be checked.
11. **Recipients of W1 and W0:** the thesis (Chapter 3, protocol of the comparison on outcomes built from neither edge type; Chapter 5, its discussion) states that every W1 recipient and 38 of the 39 W0 recipients were approved by one cohort contract, and that the two trader cohorts share 56 contracts. These counts are not in the published summaries, so the paper does not state them; it says only that recipients may be one kind of contract. Decide whether to publish them in a summary and add them to Results ("Who the recipients are"), since R1 rests on these traders.

## Claim discipline

- Scored and evaluated objects are always "contracts"; externally owned accounts appear only as owners, senders and recipients.
- Same-window agreement with a score's own edges is an "intended-construct check", never validation.
- Every τ comes with its 95% interval and every comparison is a paired contrast with its interval. `tau_score_vs_delta` of the closed-form check has no interval and is therefore not reported.
- The text says plainly that neither walk beats the raw degree it smooths, in either window, with uniform or with activity restarts.
- Revised results are a re-analysis with the registered rules; registered values are labelled as such (Table 6, one paragraph in Results). R1 holds only in the re-analysis, and every sentence that reports it says so and names the registered verdict.
- The twelve-month score windows are never called planned, pre-specified or registered, and no sentence says when the definitions of the revised analysis were fixed.
- The runtime difference is a consequence of the graph (|E|, |V| and the iterations its walk needs), not a contribution.
- No interpretation bands for τ, no p-values, no "significant", "demonstrates", "confirms" or "proves", no claim that any score measures creditworthiness, default risk, trading skill or code safety.
- No mention of any earlier thesis, draft, pilot or proposal of the authors.
