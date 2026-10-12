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
- **Binary decision.** IEEE Access accepts or rejects; there is no major-revision round, so the first submission has to pre-empt the predictable objections (the limits of the commit-gated record, the post hoc revision, the margin that the trader cohort could not reach).

## What the paper reports

- **The pre-specified test is the registered analysis** (raw token base units, every ERC-20, cohort 27,844 contracts): plan commit `43d8045` at 2026-10-09 13:41:27 UTC, ten seconds before the BigQuery job of scan A was created; registration commit `0d3a057` at 16:49:32 UTC, eight seconds before the job of scan B was created; the gated extraction script wrote its manifest at 16:49:33.
- **The revised analysis** (US dollars, five tokens WETH/USDC/USDT0/ARB/WBTC, cohort 15,107; commits `a897475`, `09dfc32`, `2705b28` on 10 October 2026, after the registered results were known and before any revised score) is reported beside it as a re-analysis under the same rules, never as a registered result.
- Verdicts are identical in the two analyses: rule A not met (A1 holds, A2 fails; the same-window part fails on all three families); rule B not met (F1 holds, F2 and F3 fail); F4, F5, F6 fail with F6a holding; S1 and S2 not met; R1 and R2 do not hold and R3 holds (reported in the companion paper). F3 fails differently: in the registered analysis C-PR was worse than the payment walk on the trader label (−0.044 [−0.100, −0.002]); in the revised analysis the two were level (+0.000 [−0.014, 0.010]) and F3 failed on precision.
- The Sybil model is reported on the revised EndorseRank graph (22 / about 2,074 / about 135,895 farm addresses to pass the 90th percentile, the 99th percentile and the top of the cohort; `sybil_model.json` gives 21.4, 2,073.9 and 135,894.8), with the registered graph's 13 / 1,253 / about 1,080,271 beside it.
- The record of the registration is described with its limits: commit times come from the committer's clock; the BigQuery job times are kept by Google but visible only to the project owner; no third-party timestamp anchors the commits. The queries of the cohort, ego network, pair tables and W0 labels, the score and bootstrap implementations, the same-window and W0 drivers and the unit tests were committed with the registration, after they had run on the observation window and after rule A had been judged. The script has no override; the manifest's `override_used` field is a constant.

## Files

| File | Content |
|---|---|
| `main.tex` | Manuscript source (`ieeeaccess.cls`, two columns) |
| `references.bib` | 51 references: 50 copied from the thesis bibliography (`Config/references.bib`) and converted from biblatex to BibTeX for IEEEtran.bst, plus the companion manuscript (`kwon2026companion`) |
| `fig_layers.tex` | Fig. 1 wrapper (caption) |
| `figures/fig_layers_standalone.tex`, `figures/fig_layers.pdf` | Fig. 1, schematic of the two layers, C-PR and S-PR (TikZ, compiled separately because the class clashes with TikZ) |
| `figures/make_figures_b.py` | Writes Figs. 2 and 3 from the published summaries in `phd_works` |
| `figures/fig_contrasts.pdf` | Fig. 2, forest plot of A1–A2, F1–F6, S1, S2 in both analyses |
| `figures/fig_lambda_sweep.pdf` | Fig. 3, tau_b of C-PR against lambda, both analyses, W0 spenders, W1 spenders, W1 traders |
| `make_tables.py` | Writes every `tab_*.tex` from the published summaries, the extraction manifest, the job times, the git history of `phd_works` and `supplement/exploratory_checks.json`; checks each summary against `SHA256SUMS.txt` and the manifest hashes against the committed files |
| `tab_bench.tex` | Table 1, solver time with \|V\| and \|E\|, both analyses |
| `tab_timeline.tex` | Table 2, order of commitments with UTC times, records and what was known |
| `tab_ids.tex` | Table 3, full commit identifiers (including `f33a87a`, which committed the registered benchmark and the data description with the BigQuery job times) and SHA-256 of the registration files (CRLF as recorded, LF as stored) and of the plan |
| `tab_holdout.tex` | Table 4, out-of-window tau_b with intervals, both analyses, W0 and W1 |
| `tab_contrasts.tex` | Table 5, paired contrasts and verdicts of rules A and B, F4–F6, S1, S2 and the contrasts computed after the labels, both analyses |
| `tab_explore.tex` | Table 6, exploratory checks (Appendix A) |
| `supplement/` | The queries behind the reported results (extraction, pair tables, same-window proxies, labels), the exploratory-check script and its output (see `supplement/README.md`) |
| `cover-letter.tex` / `.pdf` | One-page cover letter, dated 11 October 2026 |
| `main.pdf` | Built manuscript |
| `ieeeaccess.cls`, `IEEEtran.bst`, `spotcolor.sty`, `t1*`, `*.png` | Official IEEE Access template files (pristine copy in `ieee-template/`) |

## Where each table and figure gets its numbers

`phd_works` paths are relative to `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/data/`; `pub` is `3-published-results-for-thesis/` (registered analysis) and `pub/revised-usd/` (revised analysis).

| Item | Source |
|---|---|
| Table 1 (bench) | `pub[/revised-usd]/benchmark/benchmark.json` : `main` |
| Table 2 (timeline) | `git log` of `phd_works`; `pub/registered-w1/extraction_manifest.json` : `started_at`, `finished_at`; `pub/describe/describe.json` : `timing`; thesis Chapter 4, Implementation (revised scores from 11:36 UTC) |
| Table 3 (ids) | `git show -s` of the eight commits; manifest : `sha256` (CRLF); `git show <commit>:<path>` hashed as stored (LF) |
| Table 4 (holdout) | `pub[/revised-usd]/holdout-w0/eval_summary.json` : `taus`; `registered-w1` or `window-w1/eval_summary.json` : `spender_taus`, `trader_taus` |
| Table 5 (contrasts) | `holdout-w0/eval_summary.json` : `contrasts_prefixed`, `rule_a_primary`, `contrasts_after`; `same-window/eval_summary.json` : `rule_a_secondary`; W1 summary : `rule_b`, `sensitivity_awp`, `sensitivity_isolated`, `endorserank_results` |
| Table 6 (explore) | `supplement/exploratory_checks.json` |
| Fig. 2 (forest) | the same keys as Table 5 |
| Fig. 3 (sweep) | the same keys as Table 4 |
| Text: same window, Rule A secondary | `same-window/eval_summary.json` : `families`, `contrasts[0..1]`, `rule_a_secondary` |
| Text: closed form | `analysis/closed-form/closed_form_check.json` (thesis repository) |
| Text: Sybil model | `pub[/revised-usd]/sybil-model/sybil_model.json` |
| Text: data counts | `pub[/revised-usd]/describe/describe.json`, `cohort/matched_cohort.json`, the eval summaries' `graph` blocks, `gmx/*.json`; revision constants from `pub/revised-usd/describe/describe.json` : `constants`; thesis Chapter 3 (account-type counts, token rule) |

Every number in the text was checked against these sources; derived ratios (time and edge ratios, interval widths) were computed from the same JSON files.

## Distinctness from Manuscript A (PLOS ONE)

Manuscript A compares the allowance edge and the transfer edge as separate scores against their raw degrees and compares them on GMX trader outcomes built from neither edge type (P, Q, R1–R3). Manuscript B covers the coupling operator (C-PR, S-PR), the two pre-specified rules, the commit-gated record, the revision as a deviation, and the Sybil exposure of the authorization layer. Results that appear in both: the data description, the reference rows (raw degrees, EndorseRank, AWP) and their degree contrasts in Tables 4–5, the closed form of the authorization walk (Section III-G), and the solver times of EndorseRank and AWP (Table 1); B attributes them to A (`kwon2026companion`) and states this in the Introduction. R1–R3 are named in B (Introduction, Tables 2 and 3) without their verdicts. A reports the revised analysis in its Results with the registered values beside them; B leads with the registered analysis because it is about the rules fixed for it, and says so in the Introduction.

## Lengths and checks (12 October 2026)

- Abstract: 250 words, one paragraph, no references or equations (IEEE Access limit 150 to 250).
- Body text, Introduction to Conclusion plus Appendix A, without tables, captions, equations and the bibliography: about 9,700 words; 6 tables, 3 figures; 18 pages (IEEE Access recommends under 20). Fig. 2 sits in Section VI and Fig. 3 at the top of the second page of Section VII (two full-width floats may share a page top).
- `../tools/overlap_check.py main.tex`: 1.3% 8-gram overlap with the thesis; longest shared span 13 words (the name of the public BigQuery table).
- `make_tables.py`: every published summary matched `SHA256SUMS.txt` (CRLF form); the manifest hashes equal the CRLF hashes of the files committed in `0d3a057`.
- `supplement/exploratory_checks.py` (run on 11 October 2026; its inputs and output are unchanged since): every recomputed decision contrast (A1, A2, F1–F6, S1) equals the published value (largest difference 0).
- Build: no errors, no undefined citations or references. Remaining warnings: the template's own overfull header and title boxes and its font-shape substitutions (the same as when the pristine `ieee-template/access.tex` is built), a harmless T1/pcr font-series substitution from `\texttt`, and a few underfull lines in number-heavy paragraphs and the bibliography.

## Still for the authors

1. All co-authors approve the submission (the cover letter states that they have).
2. The companion entry (`kwon2026companion`) carries Manuscript A's title as of 11 October 2026 ("Allowance edges or transfer edges? Evaluating on-chain smart contract reputation out of window against degree baselines"); keep it in step with A. A's entry for this paper (`kwon2026coupling`) carries the title above, with "commit-gated".
3. ORCID iDs in ScholarOne; optional author photographs and longer biographies (IEEE asks for them at the final-files stage).
4. Optional: anchor future registrations with a third-party timestamp (Section IV-C names the gap); measure the approval fee `c_gas` and the allowance state at the freeze block.
5. Check the current IEEE Access APC and arrange payment or a waiver before acceptance.
6. The thesis and the companion report the revised analysis as their main analysis; this paper leads with the registered one because it is about the rules fixed for it, and its Introduction says so.

## Submission checklist (IEEE Access, ScholarOne)

- [x] Repositories public; URLs in Data Availability (a Zenodo DOI is optional).
- [x] Official IEEE Access template, under 20 pages.
- [x] Abstract 150 to 250 words, single paragraph; index terms in alphabetical order.
- [x] Figures as vector PDF; Figs. 2 and 3 span both columns, set in Liberation Serif (metric-compatible with Times) with text of 8 pt or more after scaling; colors are paired with marker shapes and fills, so the figures read in grayscale.
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
python3 supplement/exploratory_checks.py                  # about 10 minutes on four cores (numpy, scipy, pandas, pyarrow)
python3 make_tables.py                                    # all tab_*.tex (needs git and the phd_works history)
python3 figures/make_figures_b.py                         # Figs. 2 and 3 (needs matplotlib)
(cd figures && pdflatex fig_layers_standalone.tex && mv fig_layers_standalone.pdf fig_layers.pdf)   # Fig. 1
latexmk -pdf -interaction=nonstopmode main.tex            # runs bibtex automatically
latexmk -pdf -interaction=nonstopmode cover-letter.tex
python3 ../tools/overlap_check.py main.tex                # overlap with the thesis (run from this folder)
latexmk -c                                                # optional: remove auxiliary files
```

Requires a TeX Live installation (TeX Live 2023 was used) with TikZ; `ieeeaccess.cls` and `IEEEtran.bst` are in this folder. The thesis repository's own `latexmkrc` (XeLaTeX) lives in the repository root and is not read when latexmk runs in this folder.
