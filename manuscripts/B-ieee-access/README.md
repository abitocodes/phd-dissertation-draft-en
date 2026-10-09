# Manuscript B: IEEE Access

**Title.** Coupling Authorization and Payment Layers in a PageRank Walk: A Pre-Specified, Hash-Gated Out-of-Window Test on an Ethereum Rollup

**Article type.** Research Article

**Authors.** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

## Target journal and why

*IEEE Access* (IEEE, open access, multidisciplinary engineering and computing).

- **DHET accreditation.** The journal is indexed in Scopus, so it is on the DHET-accredited list that UNISA uses for the two first-author manuscripts.
- **Acceptance likelihood.** The official acceptance rate is about 27%. Review judges technical soundness, and negative results are explicitly "especially encouraged". This paper's central findings are two decision rules that were **not met**, so a venue that judges soundness rather than novelty of a positive result fits it best.
- **Scope.** Graph ranking, blockchain and network security papers appear in the journal regularly. Three of the cited works are IEEE Access papers on blockchain reputation, rollups and cryptocurrency transaction analysis.
- **Binary decision.** IEEE Access accepts or rejects; there is no major-revision round. The revision of 9 October 2026 answers two internal reviews (summary below) so that the first submission pre-empts the predictable objections.

## Files

| File | Content |
|---|---|
| `main.tex` | Manuscript source (IEEEtran journal class, two columns) |
| `references.bib` | 47 references: 46 taken from the thesis list (`Chapter-07-References/index.tex`) with their bibliographic details, plus the companion manuscript. EIP-20 and EIP-2612 carry the authors named in the EIP headers (checked in `github.com/ethereum/ERCs`). |
| `fig_layers.tex` | Fig. 1, schematic of the two layers, C-PR and S-PR (TikZ) |
| `tab_timeline.tex` | Table I, order of commitments, their records and what was known |
| `tab_ids.tex` | Table II, full commit identifiers and SHA-256 hashes of the registration files |
| `tab_holdout.tex` | Table III, out-of-window Kendall tau with intervals (both windows) |
| `tab_contrasts.tex` | Table IV, paired contrasts grouped by when they were fixed |
| `tab_explore.tex` | Table V, exploratory checks (Appendix A) |
| `figures/fig_lambda_sweep.pdf` | Fig. 2, lambda sweep with intervals, end points shown as separate operators, exploratory lambda values |
| `figures/fig_contrasts.pdf` | Fig. 3, forest plot of A1–A2, F1–F6, S1, S2 |
| `figures/make_figures_b.py` | Script for Figs. 2 and 3 (values from the thesis tables and `supplement/exploratory_checks.json`) |
| `supplement/` | Extraction queries, the exploratory-check script and its JSON output (see `supplement/README.md`) |
| `cover-letter.tex` / `.pdf` | One-page cover letter |
| `main.pdf` | Built manuscript (16 pages in IEEEtran) |

Every number in the tables and text comes from `results/tables/holdout-spenders.tex`, `holdout-diff.tex`, `fresh-holdout.tex`, `fresh-contrasts.tex`, `fresh-posthoc.tex`, `alignment-hybrid.tex`, `tau-diff-hybrid.tex`, `benchmark-runtime.tex`, `neutral-label-contrasts.tex`, `analysis/neutral-label/results.json`, `analysis/closed-form/closed_form_check.json`, the thesis text (Sybil model in Chapter 5, data counts in Chapters 3 and 4), the registration plan and extraction manifest in `phd_works`, the GitHub records of `phd_works` (commit, push-event and pull-request times, read through the GitHub API on 9 October 2026), or `supplement/exploratory_checks.json`. The source file of each table names its sources in a comment.

## Lengths and checks (9 October 2026)

- Abstract: 248 words, one paragraph, no abbreviations, references or equations (limit 150 to 250).
- Body text, Introduction to Conclusion plus Appendix A, without equations, proofs, tables and captions: about 9,500 words; 5 tables, 3 figures; 16 pages. This is above the brief's 5,500–7,000 words because the revision adds the reproducibility details, the record of the registration and the exploratory checks the reviewers asked for. IEEE Access recommends under 20 pages.
- `overlap_check.py`: 0.6% 8-gram overlap with the thesis; longest shared span 12 words (a list of numbers).
- Build: no errors, no undefined citations or references, no overfull boxes; four underfull lines in the bibliography and a few underfull page boxes (cosmetic).

## Distinctness from Manuscript A (PLOS ONE)

Manuscript A compares the allowance edge and the transfer edge as separate scores against their raw degrees and studies trader outcomes built from neither edge type. Manuscript B covers the coupling operator (C-PR, S-PR), the two pre-specified rules and the registered replication, and the Sybil exposure of the authorization layer. B cites A (`KwonA2026`, note "Manuscript submitted") for the data pipeline, the closed form of the authorization walk and the reference rows (EndorseRank, AWP, raw degrees), which Tables III–IV and Section VI-G label as reported in full in A. The post hoc trader comparison appears in B only as the decomposition rows of Table IV and one sentence pointing to A. The cover letter states the delineation and says that A is uploaded as confidential material for the reviewers.

## Revision of 9 October 2026: what changed and what was not done

Two internal reviews were checked against the thesis, the analysis outputs, the authors' repository (`phd_works`) and its GitHub record. Changes:

- **Title and registration record.** "Registered" became "Pre-Specified, Hash-Gated". Section IV-C and Tables I–II now give the full 40-hex commit identifiers, the SHA-256 hashes of both registration files (as recorded on the CRLF checkout and as they are with LF endings), GitHub's server-side push and merge times, the BigQuery job times from the manifest, and the code revision behind the registered summary (code as committed at `4085ab9`; summary `1462d76` byte-identical today).
- **Rule A timing (new disclosure).** The repository shows that the 14 September plan and the configuration encoding Rule A were first committed on 28 September in `0097fdb`, the same commit that holds the first coupled spring results (whose summary file records a run at 14 September 08:54 UTC). The manuscript now says that Rule A's precedence over the coupled scores rests on the dated plan, not on a commit. The thesis says the rule was "written to the configuration" on 14 September; that is not contradicted, but it cannot be checked from the repository.
- **Construct and data.** Labels are now described as counted on sample-filtered events (future attachment inside a trader-centered ego network; 5,346 of 5,353 spring and 2,163 of 2,168 registered approval-pair events come from a sampled owner); the edge is redefined as the latest in-window approval with caveats (pre-window allowances, `transferFrom`, Permit2, native ether, ERC-721); the extraction filter, GMX decoding, cohort graph filtering (the spender cohort's payment layer holds only transfers touching a spender), zero-score rule, RNG and hardware are stated; the proof of the closed form is included.
- **Look-ahead and window asymmetry.** Disclosed (1,584 sampled traders qualified only through spring-label-window closes and generated most spring label events; score history 90 vs 182 days) and checked: the spring rerun on a December–February sample gives A1 −0.172, A2 +0.014 and the exploratory gain +0.251 again.
- **Weighting vs coupling.** Exploratory reruns with bounded and binary weights: the approval-side picture holds, but the payer contrast moves to either side of the margin (bounded −0.022, binary −0.017 lower end). The abstract and conclusion now scope the negative result to this operator on this sample.
- **Proposition 1.** r(B) (0.44 on the spender graphs, 0.36 on the trader graph), the l1 movement (0.60, 0.52) and the Kendall tau between interior rankings (0.91, 0.93) are reported; the text now says the proposition locates the weight's action but does not explain the flat interior, and addresses the lambda = 0 step (most of the F1 gain appears at lambda = 0.01). The sparsity claim was removed from the conclusion.
- **Statistics.** The margin is described as precision-based, with prospective pass probabilities for F2 (0.51/0.77 at spring precision, 0.78/0.96 at registered precision); the intersection–union logic is stated; Rule A's weak criteria are acknowledged; "fixed order" is defined and F4–F6, S1, S2 are marked nominal; the invented "±0.005" Monte Carlo precision was replaced by a 50-seed computation (F2 endpoint SD 0.0008); two-way bootstraps (spenders × owners/senders; traders × weeks) are reported.
- **Other corrections.** AWP's decay parameters are now attributed to the authors, not to the AWP paper; AWP's units are stated as our reading; the decomposition is hedged; missing intervals were added (−0.317, 0.127, 0.116); the in-approve degree on the trader label carries the account-type caveat; F4 carries the "secondary, outside the failed rule" qualifier everywhere; S2's change in F5 is explained through ties; the Sybil section is framed as a calibration, gives the top spender score for context (the 11-address star reaches 1.7% of it) and adds the same attacks on AWP and on C-PR; S-PR at d = 0.5 and sensitivity to d, k and t0 are reported; a short section on implications for lending and margin protocols was added; acronyms ERC, EIP and HITS are expanded; the Bordeianu citation is narrowed; `howpublished = {Online}` was removed; Nosek et al. is cited only for preregistration on existing data; the competing-interest heading and the AI-use wording ("the authors ... take") were adapted; a privacy plan for released scores was added.

Not done, with reasons:

- **New references outside the thesis list** (multiplex PageRank: Pedroche et al. 2016, Iacovacci & Bianconi 2016, Kivelä et al. 2014, De Domenico et al. 2013, MultiRank; growing networks: Mariani et al. 2015, Liao et al. 2017; PageRank sensitivity: Ng, Zheng & Jordan 2001, Bianchini et al. 2005, Boldi et al. 2005; Sybil defenses: SybilGuard, SybilRank, Viswanath et al. 2010; Qin et al. IMC 2021; Victor & Lüders FC 2019; Chen et al. INFOCOM 2018; Berger 1982 on intersection–union tests; Piaggio et al. 2012 CONSORT non-inferiority; registered reports in computing). The manuscript brief allows only references from the thesis list. Perez et al. 2021 and Bartoletti et al. 2021, which are on the list, were added. The authors should verify and add the others (author to-do 10).
- **Placeholders** (affiliations, e-mails, funding, acknowledgment, biographies, contribution confirmation): only the authors can fill them.
- **Gas cost of an approval, allowance state at the freeze block, two-hop expansion.** These need an Arbitrum node or new BigQuery scans billed to the authors' project; the text says `c_gas` was not measured and gives a proxy for left-censoring (15.8% of "new" pairs under a three-month history were allowances already held).

## Status of the author items (updated 9 October 2026)

Planned submission date: **2 November 2026** (same day as Manuscript A), after all co-authors have approved both manuscripts.

Done:
- **Official template**: the source now uses `ieeeaccess.cls` from the IEEE Template Selector (pristine copy in `ieee-template/`; the class, fonts and logos are copied next to `main.tex`). Fig. 1 is precompiled from `figures/fig_layers_standalone.tex` because the class clashes with TikZ. The PDF has 17 pages.
- Affiliations (CAIDS for Koulla Moulla and Attipoe), corresponding author, funding footnote ("no external funding"), acknowledgment, AI-use statement, short biographies without photos, `\EOD`.
- Data Availability and Section on the registration now point to the public repositories; the thesis repository tag `manuscripts-2026-11` fixes the reported state.
- The thesis now states Rule A's commit timing and the weighting sensitivity, so thesis and paper agree.
- Cover letter dated 2 November 2026.

Still for the authors:
1. All co-authors approve the submission (the cover letter states that they have).
2. ORCID iDs in ScholarOne; optional author photographs and longer biographies (IEEE asks for them at the final-files stage).
3. Access dates for the GMX and Human Passport documentation entries; optional literature listed under "Not done".
4. Optional: measure the approval gas fee and allowance state at the freeze block (Section VII/VIII-A).
5. Check the current IEEE Access APC and arrange payment or a waiver before acceptance.

## Submission checklist (IEEE Access, ScholarOne)

- [x] Repositories public; URLs in Data Availability (a Zenodo DOI is optional).
- [x] Placeholders filled (affiliations, funding, acknowledgment, biographies).
- [x] Official IEEE Access template (17 pages, under 20).
- [ ] Abstract 150 to 250 words, single paragraph; index terms in alphabetical order.
- [ ] Figures as vector PDF; Figs. 2 and 3 span both columns (`figure*`); colors are paired with marker shapes and line styles, so the figures read in grayscale.
- [ ] Tables: captions above, booktabs rules; Tables I, III, IV and V span both columns.
- [ ] References in IEEE style, numbered in order of citation (IEEEtran.bst); access dates for the two documentation entries (to-do 10).
- [ ] AI-use disclosure in the Acknowledgment (IEEE policy).
- [ ] Supplementary material: `supplement/` (queries, exploratory script and output); Manuscript A as confidential material for reviewers.
- [ ] Cover letter uploaded; disclose that the work derives from the first author's UNISA doctoral thesis and that a related manuscript is under review at PLOS ONE. IEEE runs a similarity check, and the thesis will be in the UNISA repository.
- [ ] Article processing charge: check the current IEEE Access APC and arrange payment or a waiver before acceptance.
- [ ] Optional: suggested reviewers; graphical abstract.

## How to build

```bash
cd manuscripts/B-ieee-access
python3 figures/make_figures_b.py                         # Figs. 2 and 3 (needs matplotlib)
latexmk -pdf -interaction=nonstopmode main.tex            # runs bibtex automatically
latexmk -pdf -interaction=nonstopmode cover-letter.tex
python3 ../tools/overlap_check.py main.tex                # overlap with the thesis
latexmk -c                                                # optional: remove auxiliary files
```

Requires a TeX Live installation with `IEEEtran.cls`, `IEEEtran.bst` and TikZ (TeX Live 2023 was used). The thesis repository's own `latexmkrc` (XeLaTeX) lives in the repository root and is not read when latexmk runs in this folder. To recompute the exploratory checks, see `supplement/README.md`.

## Template

The manuscript is already on the official IEEE Access template (see Status above). To rebuild Fig. 1: `cd figures && pdflatex fig_layers_standalone.tex && mv fig_layers_standalone.pdf fig_layers.pdf`.
