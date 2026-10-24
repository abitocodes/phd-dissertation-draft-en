# Manuscript A: PLOS ONE submission package

**Title:** Allowance edges or transfer edges? Evaluating on-chain smart contract reputation out of window against degree baselines

**Running title (61 characters, limit 70):** Allowance versus transfer edges for smart contract reputation

**Article type:** PLOS ONE Research Article

**Authors:** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

## What the paper reports

The study scores and evaluates only smart contracts on Arbitrum One: 15,107 contracts that at least three owners approved on WETH, USDC, USDT0, ARB or WBTC between 1 October 2023 and 30 June 2026. It compares EndorseRank (PageRank on the latest ERC-20 allowances, with AWP's edge weights and uniform restarts) with the transfer-based AWP of Do, Do and Nguyen (2023) and with the raw in-approve degree and transfer in-degree. Main points:

- Intended-construct checks in the same window: each score agrees most with the checks of its own edges, partly by construction (Table 2).
- Out of window, in W0 (freeze 31 March 2026, labels April to June) and W1 (freeze 30 June, labels July to September): AWP beats the transfer in-degree on new senders; EndorseRank with uniform restarts falls below the in-approve degree on new approval pairs; the activity-restart variant beats the count and is reported as a hypothesis. All degree contrasts were computed after the labels (none is named in the plan or the registration document) (Table 3, Fig 1A).
- Closed form: a spender whose owners are not themselves approved scores c(1 + d δ(v)); this holds within 1% for every such spender (Table 1).
- Outcomes built from neither edge type (GMX V2 contract traders): the registered rules R1 to R3 applied to the revised scores give R1 not met, R2 not met, R3 applies (Tables 4 and 5, Fig 1B and 1C).
- The registered analysis (raw base units, every ERC-20, cohort 27,844) reached the same verdicts; the unresolved PageRank pairs on the trader label (Q, EndorseRank − AWP, the amount-weighted layers) changed sign between the two analyses (Table 6).
- The 2.23 edge ratio and the 2.17 time ratio are reported as a consequence of |E| only.

**Status words.** The revised analysis (US dollars, five tokens) was decided after the registered results were known and is the main analysis here. Its verdicts under R1 to R3 are always called a re-analysis with the registered rules, never registered results. Registered values appear only in sentences and table columns labelled "registered analysis".

## Target journal and why it was chosen

- **PLOS ONE** is DHET-accredited through its Scopus and DOAJ indexing, which meets the UNISA requirement of a first-author article in an accredited journal.
- It reviews for scientific soundness, not perceived impact, and it publishes negative and null results. Several central results here are negative or qualified: EndorseRank with the planned restarts does not beat the approval count; the comparison on trader outcomes does not separate the edge types; the one positive allowance-side result (activity restarts) was found after the labels.
- The companion Manuscript B (coupled walk C-PR and its ablation S-PR, rules A and B, the registered test, Sybil exposure) goes to IEEE Access. The Introduction of A states which results appear in both papers.

## Files

| File | What it is |
|---|---|
| `main.tex` | Manuscript in the PLOS ONE LaTeX layout (article class, rebuilt by hand from the PLOS template). Figures are **not** embedded, per PLOS policy. The Fig 1 caption follows the paragraph that first cites it, and each table follows the paragraph that first cites it. Tables 1 to 6 sit between `% BEGIN GENERATED tabN` / `% END GENERATED tabN` markers and are written by `make_tables.py`; do not edit them by hand. |
| `main.pdf` | Build of `main.tex`: submission layout with line numbers and no embedded figure. |
| `main_preview.tex`, `main_preview.pdf` | Reading copy for the authors with Fig 1 embedded. Not for submission. |
| `references.bib` | Bibliography: 53 entries. The 52 cited entries are each copied from the thesis bibliography `Config/references.bib` (same key) and converted to BibTeX for `vancouver.bst` (journaltitle to journal, report to techreport, online to misc, eid to pages, DOI as an `https://doi.org/` link and URL in `note`, accents as TeX accents). The uncited 53rd entry, `kwon2026coupling`, is Manuscript B with its current title (see "References style"). |
| `cover-letter.tex`, `cover-letter.pdf` | One-page cover letter dated 11 October 2026. |
| `data_sources.py` | Shared loader for the scripts below. Needs `--phd-works PATH` or `PHD_WORKS`; nothing is guessed. Checks every published summary against its `SHA256SUMS.txt` (CRLF form, as the checksums were taken on a Windows checkout) before use. |
| `make_tables.py` | Writes Tables 1 to 6 into `main.tex` and the rows of S1 Table (`supporting/S1_Table_rows.tex`) from the published summaries and `analysis/*.json`. |
| `check_numbers.py` | Lists every number in the prose of a `.tex` file (tables skipped) that does not occur in a source (both results digests, the published summaries, `analysis/*.json`). |
| `figures/make_fig1.py` | Fig 1 (panels A, B, C, bold uppercase letters as in PLOS figures; the line styles are explained in the caption, not in the figure) from `revised-usd/holdout-w0/eval_summary.json`, `window-w1/eval_summary.json`, `supplementary/supplementary.json` and `analysis/neutral-label/results.json`. Liberation Sans (metrically identical to Arial), 8 pt or larger, 7.2 in wide. Categorical colours: slots 1 and 2 of the dataviz reference palette (validated, CVD ΔE 24.7), plus circle/square markers as a second encoding. |
| `figures/fig1.pdf` | Vector source of Fig 1. |
| `figures/Fig1.tif` | Fig 1 for upload: 2160 x 1770 px (7.2 x 5.9 in) at 300 dpi, RGB, LZW-compressed TIFF. |
| `supporting/S1_Text.tex`, `.pdf` | **S1 Text.** Event decoding, account type, token rule and US-dollar valuation, graph weights and constants, GMX decoding, label formulas (including the revocation and drain counts that the main text reports without offering them as evidence), same-window checks, SQL patterns, properties not quantified. Constants copied from the pipeline config, SQL and scripts in `phd_works` (named in the file header). |
| `supporting/S1_File.md` | **S1 File.** The three pre-specification documents verbatim: analysis plan at `43d8045`, W1 registration at `0d3a057`, revision of the amounts at `2705b28`, with full commit ids and SHA-256 hashes (LF and CRLF). The embedded copies were checked byte for byte against `git show <commit>:<path>`. |
| `supporting/S1_Table.tex`, `.pdf`, `S1_Table_rows.tex` | **S1 Table.** Windows, cohorts, graphs and amounts. Rows generated by `make_tables.py`. |
| `supporting/S2_Table.tex`, `.pdf`, `S2_Table_rows.tex`, `make_s2_table.py` | **S2 Table.** Every registered pair (P, Q, EndorseRank − AWP, C-PR(λ=1) − C-PR(λ=0), C-PR(λ=0) − AWP, and EndorseRank − in-approve degree from the committed code) on all six trader labels, both windows, both analyses, with the stratified rows; 95% and 97.5% intervals. Generated from `analysis/neutral-label/results.json`; the share of positive resamples is not exported. |

## Where each number comes from

All summaries are in `phd_works`, folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/data/3-published-results-for-thesis/` (registered analysis) and its subfolder `revised-usd/` (revised analysis); the two `results_digest.md` files name the JSON key of every value.

| Table / figure | Content | Source of the numbers |
|---|---|---|
| Table 1 | Graphs at both freezes and fit of the closed form | `revised-usd/same-window` and `holdout-w0/eval_summary.json` (`graph`, `closed_form`), through `analysis/closed-form/closed_form_check.json` |
| Table 2 | Same-window intended-construct check, ranking agreement | `revised-usd/same-window/eval_summary.json` (`families`, `per_proxy`, `contrasts`, `inter_method`) |
| Table 3 | Spender holdouts W0 and W1, degree contrasts, EndorseRank − AWP | `revised-usd/holdout-w0/eval_summary.json` (`taus`, `contrasts_after`), `window-w1/eval_summary.json` (`spender_taus`, `endorserank_results`), `supplementary/supplementary.json` |
| Table 4 | Trader comparison on the liquidation-free close rate, both windows | `analysis/neutral-label/results.json`, `analyses.revised.windows.<W1,W0>.contrasts` and `.stratified` |
| Table 5 | Recipients against other traders, influence check | `analysis/neutral-label/results.json`, `recipients`, `influence_without_top10`, `max_in_approve_degree` |
| Table 6 | Registered analysis beside the revised analysis, including EndorseRank − AWP and C-PR(λ=1) − C-PR(λ=0) on the liquidation-free close rate in both windows | same-window, holdout-w0, registered-w1 / window-w1 summaries and `supplementary.json` of both analyses; `closed_form_check.json`; `results.json` (both analyses, `windows.<W1,W0>.contrasts`, `rules`) |
| Fig 1 | (A) PageRank minus raw degree on spender labels; (B) P and (C) Q on six trader labels | as Table 3 for A; `analysis/neutral-label/results.json` for B, C |
| S1 Table | Descriptive | `revised-usd` summaries (`same-window`, `holdout-w0`, `window-w1`, `describe/describe.json`, `cohort/matched_cohort.json`), `results.json`; footnote counts 17,167 = 17,050 + 104 + 13 (`spender_account_types`) and 12 W0 traders with a liquidation = 48 × (1 − 0.750) (`recipients.others`) |
| S2 Table | All trader contrasts | `analysis/neutral-label/results.json` |

Numbers in the prose that `check_numbers.py` does not find in a source (last run 13 October 2026), all checked by hand:

- `main.tex`: EIP numbers (721, 2612); block 513,216,506 (thesis Section 3.2 and Appendix 8.1.3), the 133 mapped tokens (thesis Section 3.5.1 and `docs/revision_price_weighting.md`) and the 75.75% row share (thesis Appendix 8.4.2 and `usd/usd_inputs.json` : `selected_share_of_rows_tobs`); 17,167 W0 spenders (17,050 + 104 + 13); σ(0) = 0.858, σ(90) = 0.711, σ(182) = 0.495, σ(365) = 0.136 (computed from k = 0.01, t0 = 180; 0.495 also occurs in an unrelated source value, so the script passes it by chance); c = 7.64 × 10⁻⁸ (7.639e-08 rounded); the layout length 2.25 in.
- `S1_Text.tex`: chain id 42161, block 513,216,506, EIP numbers, 133 tokens, 75.75%.
- Derived in the text and stated as such: 2.23 (edge ratio, in the digest), "0.21 wide" (97.5% interval of Q in W1: 0.064 − (−0.148)) and "an estimate of 0.1 or less" (about the half-width of that interval, 0.106; every degree contrast in Table 3 and EndorseRank − AWP on new approval pairs are below it), "one in six" (2,367 / 14,406), "one in three" (5,706 / 17,032), and the AWP tie share 2.87% (`ties.awp`, share of pairs tied 0.0287).

Other text sources: the candidate count 29,022 = 27,844 + 1,121 + 57 is in the registered `results_digest.md` (`cohort/matched_cohort.json` : `candidates`); the pinned block number, the token rule and the price check come from thesis Sections 3.2 and 3.5.1 and Appendices 8.1.3 and 8.4.2 and from `usd/chainlink_check.json`; commit times from `git -C phd_works log`; the creation time of the scan B query (16:49:40) from `describe/describe.json` (registered analysis); the benchmark machine from thesis Appendix 8.1.1 (Pipeline stages).

## How to build

```bash
cd manuscripts/A-plos-one
export PHD_WORKS=/path/to/phd_works                     # required by the generators
python3 make_tables.py                                   # Tables 1-6 into main.tex, S1 Table rows
python3 supporting/make_s2_table.py                      # S2 Table rows (reads analysis/ only)
python3 figures/make_fig1.py                             # figures/fig1.pdf
(cd figures && pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig1.pdf Fig1)
latexmk -pdf -interaction=nonstopmode main.tex          # submission layout (bibtex runs automatically)
latexmk -pdf -interaction=nonstopmode main_preview.tex  # reading copy with Fig 1 embedded
latexmk -pdf -interaction=nonstopmode cover-letter.tex
cd supporting && for f in S1_Text S1_Table S2_Table; do latexmk -pdf -interaction=nonstopmode $f.tex; done
```

Python 3 with matplotlib (3.11 used) and the Liberation fonts. The supporting files use the default Computer Modern fonts (the `lmodern` package is not installed in the build environment).

Checks:

```bash
python3 check_numbers.py main.tex cover-letter.tex supporting/S1_Text.tex supporting/S1_Table.tex
python3 ../tools/overlap_check.py main.tex
```

## Changes of 22 October 2026

- The companion paragraph of the Introduction calls Manuscript B "unpublished" instead of "submitted to IEEE Access", and the uncited entry `kwon2026coupling` has the note "Unpublished manuscript"; restore the journal name when B is submitted.
- Rebuilt `main.pdf` (25 pages) and `main_preview.pdf` (26 pages): no errors or undefined references; `check_numbers.py main.tex` lists the same 11 documented exceptions.
- The thesis now presents C-PR as its method; this paper stays the single-layer comparison (EndorseRank, AWP and the raw degrees), as before.

## Last build and checks (13 October 2026)

- `main.pdf` 25 pages, `main_preview.pdf` 26 pages and S1 Text 5 pages, rebuilt with pdflatex, bibtex and pdflatex twice; `cover-letter.pdf` 1 page, S1 Table 1 page and S2 Table 5 pages, whose sources did not change, are the builds of 12 October. No errors, no undefined references or citations, no overfull boxes. All 42 DOIs in the reference list link to `https://doi.org/` (no relative links). Tables 1 to 6 and Fig 1 are first cited in ascending order, and each float follows the paragraph that first cites it (checked by script). BibTeX issues 8 benign warnings for the four `@misc` web sources (GMX, Human Passport, DefiLlama, Chainlink: no editor or publisher).
- Abstract: 292 words in the PDF text (limit 300), no citations. Body from Introduction to Conclusions about 9,600 words counting numbers, without tables, the figure caption and display equations; about 400 of them are the required statements (Ethics, Data availability, Use of generative AI). 6 tables, 1 figure.
- Text overlap with the thesis (`manuscripts/tools/overlap_check.py`, 8-word shingles; the tool now strips biblatex `\textcite`/`\parencite` keys as well as `\cite` keys): `main.tex` 1.7%, longest shared span 17 words (the registered wording of the decision contrasts, quoted on purpose); S1 Text 0.4%, longest 15 words; cover letter 0.0%.
- `check_numbers.py`: every data number in the prose occurs in a source; the exceptions are listed above.

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
- **Data availability:** use the "Data availability" subsection of `main.tex`. It names `phd_works`, folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments` as it stood at these commits of the default branch `master` (plan `43d8045`, registration `0d3a057`, registered results `8d8b568`, revision `a897475`/`09dfc32`/`2705b28`, revised results `77e71f5`, all on `origin/master`), with a commit-pinned link to that folder at `77e71f5`, and `phd-dissertation-draft-en` (folders `analysis/` and `manuscripts/A-plos-one/`). Both repositories are public. On `master` the folder is now `...-Wallet-Reputation/experiments`, the name the thesis uses (Appendix 8.1.1), and its parquet files (extracted graph tables, per-contract scores and labels) are kept in a public Google Drive folder whose link and checksums are in the committed `drive-manifest.json`. The commit-pinned folder and link of the statement remain valid; whether to name the new folder and the Drive folder as well is for the authors (item 9).
- **Ethics statement:** Only public blockchain data and public token prices were used; no human participants; only contracts are scored. [ethics clearance reference to be added by the authors] Do not submit while this bracket is in `main.tex`: PLOS's technical check returns a manuscript with a placeholder.
- **Use of AI tools:** the full statement is in Methods ("Use of generative AI"), with a pointer in Acknowledgments.
- **Related manuscript:** upload Manuscript B (`manuscripts/B-ieee-access/main.pdf`) as a "Related manuscript" file.

## Open items for the authors

1. **Ethics statement (required before submission):** insert the UNISA ethics clearance reference (committee name and number) and delete the bracket in `main.tex`; if the committee confirmed that no clearance was needed, state that with the committee's name instead. The thesis also has it as [TBD].
2. **Tag a release of the second repository:** `analysis/` and every file of this folder, the generators included, are committed on `main` (`__pycache__/` is ignored). Tag a release (the existing tag `manuscripts-2026-11` points to an older state and must not be cited for this version) and add the commit or tag to the Data availability statement.
3. **Use of generative AI:** confirm the sentence on the experiment repository ("Under the first author's direction it wrote and ran parts of the extraction and evaluation code in the first repository"). The commits `43d8045` to `77e71f5` carry the first author's account name; commit `7129981` set the repository so that Claude attribution lines are not added.
4. **Companion manuscript:** the Introduction of A, the Introduction of B and both cover letters now use the same list of shared results (spender holdout coefficients of the raw degrees, EndorseRank and AWP with their degree contrasts; the closed form of EndorseRank; the solver runtimes), say that P, Q and R1–R3 are reported only in A and that B reports on the same trader cohort only the contrasts of its coupled walk that its own rule names. Check this again if either paper changes; `kwon2026coupling` now carries B's current title.
5. **Supervisors' confirmation** that the revised analysis replaces the registered one as the main analysis (open in the thesis notes as well).
6. **Approval and ORCID:** every co-author approves the final PDF; enter ORCID iDs and CRediT roles in the submission form.
7. **Fig 1:** run PACE (https://pacev2.apexcovantage.com/) on `figures/Fig1.tif`.
8. **Web sources:** access dates of the four web sources are those of the thesis bibliography (9 and 10 October 2026); update them if the pages are checked again before submission.
9. **Archived release (required before submission):** a GitHub folder path is not a stable location (on `master` the experiment folder has been renamed since the cited commits, and its parquet files have moved to a Google Drive folder), and both repositories also hold material outside this study. Archive a tagged release on Zenodo that contains only the experiment folder of `phd_works` and `analysis/` plus `manuscripts/A-plos-one/` of this repository, and cite its DOI in the Data availability statement and the cover letter. Until then the statement points to commit `77e71f5` on `master`.

## Claim discipline

- Scored and evaluated objects are always "contracts"; externally owned accounts appear only as owners, senders and recipients.
- Same-window agreement with a score's own edges is an "intended-construct check", never validation.
- Every τ comes with its 95% interval and every comparison is a paired contrast with its interval. `tau_score_vs_delta` of the closed-form check has no interval and is therefore not reported.
- The text says plainly that the in-approve degree beats EndorseRank with uniform restarts in both windows; the activity-restart lead is a hypothesis.
- Revised results are a re-analysis with the registered rules; registered values are labelled as such (Table 6, one paragraph in Results).
- The runtime difference is a consequence of |E|, not a contribution.
- No interpretation bands for τ, no p-values, no "significant", "demonstrates", "confirms" or "proves", no claim that any score measures creditworthiness, default risk, trading skill or code safety.
- No mention of any earlier thesis, draft, pilot or proposal of the authors.
