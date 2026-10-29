# Manuscript B: IEEE Access

**Title.** Coupling Authorization and Payment Layers in a PageRank Walk for Smart-Contract Reputation: A Pre-Specified, Commit-Gated Out-of-Window Test on an Ethereum Rollup

**Article type.** Research Article

**Authors.** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

"Commit-gated" replaces the earlier "hash-gated": the extraction script refuses to run unless the registration files are committed without local changes, and it only records their SHA-256 hashes; it compares no hash.

## Target journal and why

*IEEE Access* (IEEE, open access, multidisciplinary engineering and computing).

- **DHET accreditation.** The journal is indexed in Scopus, so it is on the DHET-accredited list that UNISA uses for the two first-author manuscripts.
- **Acceptance likelihood.** The official acceptance rate is about 27%. Reviewers are asked to judge technical soundness, not novelty. This paper's central findings are two decision rules that were **not met**, so a venue that judges soundness rather than novelty of a positive result fits it best.
- **Scope.** Graph ranking, blockchain and network security papers appear in the journal regularly; three of the cited works (Bellini et al., Thibault et al., Liu et al.) are IEEE Access papers on blockchain reputation, rollups and cryptocurrency transaction analysis.
- **Binary decision.** IEEE Access accepts or rejects; there is no major-revision round, so the first submission has to pre-empt the predictable objections (the limits of the commit-gated record, the post hoc revision, the margin that the trader cohort barely allows).

## What the paper reports

- **The pre-specified test is the registered analysis** (raw token base units, every ERC-20, cohort 27,844 contracts): plan commit `43d8045` at 2026-10-09 13:41:27 UTC, ten seconds before the BigQuery job of scan A was created; registration commit `0d3a057` at 16:49:32 UTC, eight seconds before the job of scan B was created; the gated extraction script wrote its manifest at 16:49:33.
- **The revised analysis** is the main analysis, as in the thesis and Manuscript A: amounts in US dollars on five tokens (WETH, USDC, USDT0, ARB, WBTC) and every score computed from the twelve months before its freeze (same window and W1: 1 July 2025 to 30 June 2026; W0: 1 April 2025 to 31 March 2026), one cohort per freeze (matched cohort 6,483 contracts approved on the five tokens by at least three distinct owners in the twelve months before 30 June 2026; W0 cohort 6,343; 5,383 in both), constants m_T 170, m_A 100 and U 19,000 USD from the W0 score window. The abstract, the text, the conclusion, every table (revised block or column first) and both data figures (top row, upper marker) report it first, as a re-analysis under the same rules and never as a registered result. The registered analysis is reported beside it everywhere, as the test that the rules were fixed for. The one exception is the W0 contrast that motivated Rule B, given from the registered analysis because no revised score existed when Rule B was written.
- **How the revised analysis is described.** The paper says that it was defined after the registered results were known, and every such sentence lists the score windows with the amounts and the tokens. It never says that the windows were planned or registered and never says when the revised definitions were fixed: no date or time of the revision commits, no claim that they preceded any revised score. Table 2 gives the revised analysis one row with "Later" in the time column; Table 3 lists its commits (`a897475`, `09dfc32`, `2705b28`, `e6c352d`, `0a94215`, `950a7a4`) without times. The dated record of the registered test (plan, registration, scan jobs, manifest, registered results, registered benchmark) is unchanged. Outside the passages on the registered analysis and the plan, no sentence narrates a change; a search for the change words of the writing brief (`_writing-brief.md`, "Score windows", rule 5) finds none anywhere in `main.tex`.
- **Verdicts.** Rules A and B and every component have the same verdict in both analyses: rule A not met (A1 holds, A2 fails; the same-window part fails on all three families); rule B not met (F1 holds, F2 and F3 fail); F4, F5 and F6 fail with F6a holding; S1 and S2 not met. Revised: A1 +0.031 [0.021, 0.042], A2 −0.030 [−0.040, −0.020], F1 +0.170 [0.149, 0.189], F2 −0.025 [−0.038, −0.015], F3 +0.000 [−0.010, 0.010]. F3 fails differently: in the registered analysis C-PR was worse than the payment walk on the trader label (−0.044 [−0.100, −0.002]); in the revised analysis the two have the same coefficient (0.282) and F3 fails on precision, with a lower end of −0.01005 that clears the margin in 1 of 50 further bootstrap seeds (Appendix A); Rule B fails in every seed because F2 does. R1–R3 are the companion's rules and are named here without verdicts (in the revised analysis R1 and R3 hold and R2 does not; the registered analysis did not meet R1).
- **Contrasts after the labels** (revised score files, outside every rule), every loss of C-PR reported: C-PR leads EndorseRank on both spender labels in both windows and AWP on new approval pairs (largely through the spenders AWP scores zero; among the spenders with an incoming transfer it is level in W0 and leads by 0.022 in W1); it trails the in-approve degree on new approval pairs (−0.063, −0.065) and the transfer in-degree on new senders (−0.111, −0.115) in both windows, AWP on new senders in every subset and window, EndorseRank with activity restarts on new approval pairs in W1 (−0.019), S-PR on new senders in both windows, and the in-approve degree on the traders' liquidation-free close rate (−0.112 [−0.194, −0.026]). In the revised analysis every walk, AWP included, ranks its own label below the raw count of its edge type.
- The Sybil model is reported on the revised EndorseRank graph (26 / about 2,292 / about 47,073 farm addresses to pass the 90th percentile, the 99th percentile and the top of the cohort; `sybil_model.json` gives 25.19, 2,291.7 and 47,072.6; closed-farm factor 3.23 at d = 0.85), with the registered graph's 13 / 1,253 / about 1,080,271 (factor 2.96) beside it. Because the graphs hold the approvals of the past year only, the cost model counts re-emissions per year.
- The record of the registration is described with its limits: commit times come from the committer's clock; the BigQuery job times are kept by Google but visible only to the project owner; no third-party timestamp anchors the commits. The queries of the cohort, ego network, pair tables and W0 labels, the score and bootstrap implementations, the same-window and W0 drivers and the unit tests were committed with the registration, after they had run on the observation window and after rule A had been judged. The script has no override; the manifest's `override_used` field is a constant.

## Files

| File | Content |
|---|---|
| `main.tex` | Manuscript source (`ieeeaccess.cls`, two columns) |
| `references.bib` | 51 references: 50 copied from the thesis bibliography (`Config/references.bib`) and converted from biblatex to BibTeX for IEEEtran.bst, plus the companion manuscript (`kwon2026companion`) |
| `fig_layers.tex` | Fig. 1 wrapper (caption) |
| `figures/fig_layers_standalone.tex`, `figures/fig_layers.pdf` | Fig. 1, schematic of the two layers, C-PR and S-PR (TikZ, compiled separately because the class clashes with TikZ) |
| `figures/make_figures_b.py` | Writes Figs. 2 and 3 from the published summaries in `phd_works` (`revised-usd-12m/` for the revised analysis) |
| `figures/fig_contrasts.pdf` | Fig. 2, forest plot of A1–A2, F1–F6, S1, S2 in both analyses |
| `figures/fig_lambda_sweep.pdf` | Fig. 3, tau_b of C-PR against lambda, both analyses, W0 spenders, W1 spenders, W1 traders |
| `make_tables.py` | Writes every `tab_*.tex` from the published summaries, the extraction manifest, the job times, the git history of `phd_works` and `supplement/exploratory_checks.json`; checks each summary against `SHA256SUMS.txt` and the manifest hashes against the committed files |
| `tab_bench.tex` | Table 1, solver time with \|V\| and \|E\|, both analyses |
| `tab_timeline.tex` | Table 2, order of commitments with UTC times for the registered record, records and what was known; the revised analysis is one undated row ("Later") |
| `tab_ids.tex` | Table 3, full commit identifiers of the registered record with times (including `f33a87a`, which committed the registered benchmark and the data description with the BigQuery job times), the commits of the revised analysis without times, and SHA-256 of the registration files (CRLF as recorded, LF as stored) and of the plan |
| `tab_holdout.tex` | Table 4, out-of-window tau_b with intervals, both analyses, W0 and W1 |
| `tab_contrasts.tex` | Table 5, paired contrasts and verdicts of rules A and B, F4–F6, S1, S2 and the contrasts computed after the labels, both analyses |
| `tab_explore.tex` | Table 6, exploratory checks (Appendix A); panel (a) at four decimals |
| `supplement/` | The queries behind the reported results (extraction, pair tables, same-window proxies, labels), the exploratory-check script and its output (see `supplement/README.md`) |
| `cover-letter.tex` / `.pdf` | One-page cover letter, dated 29 October 2026 |
| `main.pdf` | Built manuscript |
| `ieeeaccess.cls`, `IEEEtran.bst`, `spotcolor.sty`, `t1*`, `*.png` | Official IEEE Access template files (pristine copy in `ieee-template/`) |

## Where each table and figure gets its numbers

`phd_works` paths are relative to `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/data/`; `pub` is `3-published-results-for-thesis/` (registered analysis) and `pub/revised-usd-12m/` (revised analysis; its `results_digest.md` names the file and key of every value and records the code revision `0a94215`; the folder was committed in `950a7a4`).

| Item | Source |
|---|---|
| Table 1 (bench) | `pub[/revised-usd-12m]/benchmark/benchmark.json` : `main` |
| Table 2 (timeline) | `git log` of `phd_works` (registered record only); `pub/registered-w1/extraction_manifest.json` : `started_at`, `finished_at`; `pub/describe/describe.json` : `timing`; `pub/revised-usd-12m/describe/describe.json` : `constants` (m_T, m_A, U of the undated revised row) |
| Table 3 (ids) | `git show -s` of the ten commits (times printed for the four of the registered record only); manifest : `sha256` (CRLF); `git show <commit>:<path>` hashed as stored (LF) |
| Table 4 (holdout) | `pub[/revised-usd-12m]/holdout-w0/eval_summary.json` : `taus`; `registered-w1` or `window-w1/eval_summary.json` : `spender_taus`, `trader_taus` |
| Table 5 (contrasts) | `holdout-w0/eval_summary.json` : `contrasts_prefixed`, `rule_a_primary`, `contrasts_after`; `same-window/eval_summary.json` : `rule_a_secondary`; W1 summary : `rule_b`, `sensitivity_awp`, `sensitivity_isolated`, `endorserank_results` |
| Table 6 (explore) | `supplement/exploratory_checks.json` |
| Fig. 2 (forest) | the same keys as Table 5 |
| Fig. 3 (sweep) | the same keys as Table 4 |
| Text: same window, Rule A secondary | `same-window/eval_summary.json` : `families`, `contrasts[0..1]`, `rule_a_secondary` |
| Text: closed form | `analysis/closed-form/closed_form_check.json` (thesis repository; regenerated for the twelve-month analysis) |
| Text: contrasts after the labels | `pub/revised-usd-12m/supplementary/supplementary.json` : `w0.*`, `w1.*` (C-PR against the degrees, EndorseRank with activity restarts, S-PR, AWP among the spenders with a transfer, the in-approve degree on the traders); `holdout-w0` : `contrasts_after`; `window-w1` : `endorserank_results` |
| Text: precision, seed spread, half-width of F3 | `supplement/exploratory_checks.json` : `seed_spread`, `recompute.revised.F3.half_width` |
| Text: Sybil model | `pub[/revised-usd-12m]/sybil-model/sybil_model.json` |
| Text: data counts | `pub/revised-usd-12m/describe/describe.json` : `rows` (revised ego logs of the T_obs score window and their share of the plan's), `amounts` (unlimited and capped shares), `constants` (raw medians and percentiles), `timing.bigquery_usd_total`; `cohort/matched_cohort.json`, `cohort/cohort_t1.json`; the eval summaries' `graph` blocks; `gmx/*.json`; registered ego approval logs = sum of `monthly_counts` (`approval_ego`, October 2023 to June 2026) in `pub/describe/describe.json`; job count from `data/bq_ledger.json` (56 jobs); thesis Chapter 3 (account-type counts, block of the code read, token rule) |

Every number in the text was checked against these sources; derived ratios (time and edge ratios, interval widths) were computed from the same JSON files.

## Distinctness from Manuscript A (PLOS ONE)

Manuscript A compares the allowance edge and the transfer edge as separate scores against their raw degrees and compares them on GMX trader outcomes built from neither edge type (P, Q, R1–R3). Manuscript B covers the coupling operator (C-PR, S-PR), the two pre-specified rules, the commit-gated record, the revision as a deviation, and the Sybil exposure of the authorization layer. Results that appear in both: the data description, the reference rows (raw degrees, EndorseRank, AWP) and their degree contrasts in Tables 4–5, the closed form of the authorization walk (Section III-G), and the solver times of EndorseRank and AWP (Table 1); B attributes them to A (`kwon2026companion`) and states this in the Introduction. R1–R3 are named in B (Introduction, Tables 2 and 3) without their verdicts. On the trader cohort B reports the contrasts that Rule B and its sensitivity analyses name and one contrast computed after the labels (C-PR against the in-approve degree), and its Introduction says so. Both report the revised analysis first, with the registered values beside them, and say so in the Introduction.

## Changes of 29 October 2026

The paper now reports the thesis's current main analysis, the twelve-month revised analysis of `pub/revised-usd-12m/` (thesis manuscript `392937a`); the registered analysis and its record are unchanged.

- `make_tables.py`, `figures/make_figures_b.py`, `supplement/exploratory_checks.py`: read `revised-usd-12m/` (published summaries) and `2-processed-tables-and-evaluations/revised-usd-12m/` (score files). Every `tab_*.tex`, Figs. 2 and 3 and `supplement/exploratory_checks.json` regenerated (the recomputation of A1, A2, F1–F6 and S1 again equals the published values, largest difference 0).
- Tables 2 and 3: the revision rows carry no date or time. Table 2 has one revised row ("Later": definitions, constants m_T 170, m_A 100, U 19,000 from `describe.json`, rules applied, results in `950a7a4`) and an undated row for the exploratory checks; Table 3 lists the commits of the revised analysis (`a897475`, `09dfc32`, `2705b28`, `e6c352d`, `0a94215`, `950a7a4`) without times under a heading that names the windows with the amounts and tokens. The registered rows (plan, scans, registration, manifest, registered results, registered benchmark) are as before. Table 6, panel (a): four decimals, so that the one revised F3 seed whose lower end clears −0.01 is visible; `\tabcolsep` 2.4 pt to fit.
- Tables 1, 4 and 5 and the captions of Table 4, Table 5 and Fig. 2 and the row title of Fig. 3 name the twelve-month score windows of the revised analysis.
- Text: every number of the revised analysis (abstract, Introduction, Sections III to X, Appendix A); the cohort (6,483 at T_obs, 6,343 at the W0 freeze), the score windows, the constants (m_T 170 from 169.3, m_A 100 from 99.97, U 19,000 from 18,575; the 99th percentile of the finite allowances near 10^63), the ego log counts and shares, the graphs, the closed form (5,232 of 6,224; 87.5%, 21.9%), the solver times (C-PR 1.36 times AWP on 1.25 times its edges; the AWP-to-EndorseRank time ratio, 3.21, now exceeds the edge ratio, 2.21, so the text gives the iteration counts too), the Sybil model, the BigQuery total (56 jobs, USD 42.24). Section IV-D is now "The Revised Analysis" and says what was defined after the registered results (amounts, tokens, score windows, one cohort per freeze) without dating it; the cap amendment story and "before any revised score" are gone.
- Results whose reading in the text was rewritten: S-PR ranks new senders slightly above the payment walk in W0 (+0.011); C-PR ranks new senders below S-PR in both windows; C-PR falls below the in-approve degree on new approval pairs in both windows and below the in-approve degree on the traders; AWP ranks new senders below the transfer in-degree in both windows of the revised analysis (above it in the registered one); EndorseRank with activity restarts is level with C-PR in W0 and ahead in W1; among the spenders with a transfer, C-PR and AWP are level on new approval pairs in W0 and C-PR leads in W1. The F3 story: the revised F3 lower end clears the margin in 1 of 50 further seeds, so the precision subsection, Appendix A and the statistical-conclusion threat say that its failure depends on resampling, while Rule B fails in every seed through F2.
- Sybil cost model: the graphs keep the approvals of the past year only, so a farm re-emits its approvals once a year; the cost is counted per period (`q` periods) instead of per refresh, and the sentence on C-PR keeping an edge without refresh is gone.
- Introduction and cover letter: on the trader cohort the paper now also reports one post hoc contrast (C-PR against the in-approve degree). Cover letter dated 29 October 2026, still one page.
- Change words: "instead of" (Related Work) and "changed the ranking" (Implications) reworded, so that the change words of the writing brief occur nowhere in `main.tex`.
- `supplement/README.md`: sources and commit `950a7a4`, the run environment of the exploratory checks, queries 20 to 23 listed as phd_works-only; no dating of the revision.

## Changes of 22 October 2026

- Thesis restructure: the thesis now presents C-PR as its method, with EndorseRank and AWP as single-layer references; this paper was already built around C-PR and keeps its structure.
- New subsection "Against the Reference Walks, After the Labels" (Results) and one sentence in the Conclusion: post hoc contrasts from the revised score files, published in `supplementary/supplementary.json` of the revised analysis (outside every rule).
- "Walks Against Counts": the C-PR contrasts with the in-approve degree and the transfer in-degree (revised analysis) replace "no paired contrast was computed"; the registered analysis still has none.
- Threats: other couplings "are not evaluated in this paper" (they were explored after the labels, outside this paper).
- The companion entry's note is now "Unpublished manuscript"; change it to the journal name once Manuscript A is submitted.
- Rebuilt: 18 pages, no errors or undefined references; `make_tables.py` regenerated identical tables; every new number occurs in the revised digest (`../A-plos-one/check_numbers.py main.tex` flags none of them).

## Lengths and checks (29 October 2026)

- Abstract: 250 words, one paragraph, no references or equations (IEEE Access limit 150 to 250).
- Body text, Introduction to Conclusion plus Appendix A, without tables, captions, equations and the bibliography: about 10,600 words (7% more than on 13 October); 6 tables, 3 figures; 19 pages (IEEE Access recommends under 20). Figs. 2 and 3 sit in Section VI.
- `../tools/overlap_check.py main.tex`: 0.9% 8-gram overlap with the thesis (manuscript `392937a`); longest shared span 13 words (the BigQuery table name).
- `../A-plos-one/check_numbers.py main.tex cover-letter.tex` (A's checker, already pointed at `revised-usd-12m/`): cover letter 0 numbers not found; `main.tex` 33. Of these, 20 come from sources the checker does not read and were checked by hand against them: the Sybil models of both analyses (`sybil_model.json`: 3.23, 2.10, 8.96, 2.96, 2.01, 2,292, 47,073, 1,253, 1,080,271 and the five values written as powers of ten, 1.93, 6.60, 5.82, 1.56, 1.35), the registered benchmark (105.51) and `supplement/exploratory_checks.json` (0.01004, 0.0146, 0.869, 0.596, 0.660). The four solver ratios (1.36, 1.25, 1.51, 1.19) are derived from `benchmark.json`; 389,866,882 is the sum of the registered `monthly_counts`; 513,216,506 is the block of the account-type read (thesis Chapter 3); the other seven are not data (0000, 10.1109, 2612, (0,1), 42161, ERC-721, the commit fragment 950).
- Build (MiKTeX pdflatex, bibtex, pdflatex twice, from PowerShell): no errors, no undefined citations or references. Remaining warnings: the template's own overfull header and title boxes and its font-shape substitutions (the same as when the pristine `ieee-template/access.tex` is built), a harmless T1/pcr font-series substitution from `\texttt`, and underfull lines in number-heavy paragraphs and the bibliography.
- `make_tables.py`: every published summary of both analyses matched `SHA256SUMS.txt` (CRLF form); the manifest hashes equal the CRLF hashes of the files committed in `0d3a057`.
- `supplement/exploratory_checks.py` (Python 3.11.9, NumPy 2.3.2, SciPy 1.16.1, pandas 3.0.3; 217 s with four workers): every recomputed decision contrast (A1, A2, F1–F6, S1) equals the published value in both analyses (largest difference 0).

## Still for the authors

1. All co-authors approve the submission (the cover letter states that they have).
2. The companion entry (`kwon2026companion`) carries Manuscript A's title as of 11 October 2026 ("Allowance edges or transfer edges? Evaluating on-chain smart contract reputation out of window against degree baselines"); keep it in step with A. A's entry for this paper (`kwon2026coupling`) carries the title above, with "commit-gated".
3. ORCID iDs in ScholarOne; optional author photographs and longer biographies (IEEE asks for them at the final-files stage).
4. Optional: anchor future registrations with a third-party timestamp (Section IV-C names the gap); measure the approval fee `c_gas` and the allowance state at the freeze block.
5. Check the current IEEE Access APC and arrange payment or a waiver before acceptance.
6. The thesis, the companion and this paper report the twelve-month revised analysis as their main analysis, with the registered analysis beside it; keep the three in step if the revised summaries are published again.
7. The supplement copies its queries unchanged from `phd_works`, comments included. The comment of `sql/13_usd_constants.sql` dates the cap rule relative to the revised scores ("as amended before any revised score"), and the comments of queries 21 and 23 (twelve-month cohorts, window views, consistency checks) describe their source tables in a way the paper does not; 20 to 23 are therefore listed as `phd_works`-only. Decide whether to keep 13 as it is and whether to add 20 to 23.

## Submission checklist (IEEE Access, ScholarOne)

- [x] Repositories public; URLs in Data Availability (a Zenodo DOI is optional).
- [x] Official IEEE Access template, under 20 pages.
- [x] Abstract 150 to 250 words, single paragraph; index terms in alphabetical order.
- [x] Figures as vector PDF; Figs. 2 and 3 span both columns, set in Times New Roman (embedded; Liberation Serif where Times is absent) with text of 8 pt or more after scaling; colors are paired with marker shapes and fills, so the figures read in grayscale.
- [x] Tables: captions above, booktabs rules.
- [x] References in IEEE style, numbered in order of citation (IEEEtran.bst).
- [x] AI-use disclosure in the Acknowledgment (IEEE policy).
- [ ] Supplementary material: `supplement/` (queries, exploratory script and output); Manuscript A as confidential material for reviewers.
- [ ] Cover letter uploaded; it discloses that the work derives from the first author's UNISA doctoral research and that a related manuscript goes to PLOS ONE. IEEE runs a similarity check, and the thesis will be in the UNISA repository.
- [ ] Article processing charge.
- [ ] Optional: suggested reviewers; graphical abstract.

## How to build

```bash
cd manuscripts/B-ieee-access
export PHD_WORKS=/path/to/phd_works                       # checkout of github.com/abitocodes/phd_works
python3 supplement/exploratory_checks.py                  # about 4 minutes with four workers (numpy, scipy, pandas, pyarrow)
python3 make_tables.py                                    # all tab_*.tex (needs git and the phd_works history)
python3 figures/make_figures_b.py                         # Figs. 2 and 3 (needs matplotlib)
(cd figures && pdflatex fig_layers_standalone.tex && mv fig_layers_standalone.pdf fig_layers.pdf)   # Fig. 1
latexmk -pdf -interaction=nonstopmode main.tex            # runs bibtex automatically
latexmk -pdf -interaction=nonstopmode cover-letter.tex
python3 ../tools/overlap_check.py main.tex                # overlap with the thesis (run from this folder)
latexmk -c                                                # optional: remove auxiliary files
```

Requires a TeX installation with TikZ (TeX Live 2023 was used up to 22 October 2026; the build of 29 October 2026 used MiKTeX on Windows, running pdflatex and bibtex from PowerShell, since xelatex crashed under Git Bash in this checkout); `ieeeaccess.cls` and `IEEEtran.bst` are in this folder. The thesis repository's own `latexmkrc` (XeLaTeX) lives in the repository root and is not read when latexmk runs in this folder.
