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
- **Port to `ieeeaccess.cls`.** The class is not available offline and the template site could not be reached from the build environment; the porting steps are below.
- **Placeholders** (affiliations, e-mails, funding, acknowledgment, biographies, contribution confirmation): only the authors can fill them.
- **Gas cost of an approval, allowance state at the freeze block, two-hop expansion.** These need an Arbitrum node or new BigQuery scans billed to the authors' project; the text says `c_gas` was not measured and gives a proxy for left-censoring (15.8% of "new" pairs under a three-month history were allowances already held).

## What the authors must still fill in

1. Affiliations and e-mail addresses of Donatien Koulla Moulla and David Sena Attipoe (placeholders: "[affiliation to be confirmed]", "[to be added]"), and the e-mail of Ernest Mnkandla.
2. Funding statement (`\thanks{Funding: ...}` now; `\tfootnote{...}` in the official template).
3. Acknowledgment text before the AI-use disclosure (placeholder in `\section*{Acknowledgment}`).
4. Confirmation of the author contribution statement by all authors (the section starts with "[To be confirmed by all authors.]").
5. Author biographies and photographs (IEEE Access prints both; placeholders "[Biography to be added.]").
6. **Make `phd_works` public before submission** (it is private as of 9 October 2026, checked through the GitHub API) and archive a frozen snapshot with a DOI (Zenodo or Software Heritage); add the URL and DOI to the Data Availability section. Check that commits `0097fdb`, `f54d10c`, `4085ab9`, `f701400`, `d6d26c4`, `1462d76`, `ce50659` and `7129981` are visible after release, since the paper cites them.
7. **Correct the thesis wording on the repository.** Chapter 1 (Section 1 design summary), Chapter 3 (`sub:fresh-holdout`), Chapter 4 (`sub:fresh-results`) and Appendix 8 (reproducibility, around line 36) call `phd_works` a "public repository". Either make it public before the thesis is examined or change those sentences to "the authors' repository"; otherwise reviewers comparing the thesis with either manuscript will see a contradiction.
8. Consider whether the thesis should also state that Rule A's configuration entered version control on 28 September (see "Rule A timing" above), so the thesis and Manuscript B agree.
9. Confirm the privacy plan in Data Availability (release aggregate results and code; address-level score files only with salted address hashes) or replace it with the release policy you prefer.
10. Verify and add the related-work references listed under "Not done" (exact bibliographic details), and add access dates to the GMX and Human Passport documentation entries (IEEE style asks for "Accessed: Mon. DD, YYYY"; the sites could not be reached from the build environment).
11. Optional, to strengthen Sections VII and VIII-A: measure the fee of an approval on Arbitrum One from a sample of the window's approval transactions, and read `allowance(owner, spender)` at the freeze block for a random sample of label pairs to quantify left-censoring.
12. Final title and journal of Manuscript A in `references.bib` (`KwonA2026`). Update the note from "Manuscript submitted" to the citation once either paper is accepted.
13. Date of submission and all-author approval in `cover-letter.tex`; upload Manuscript A as confidential material for the reviewers, as the cover letter says.
14. ORCID iDs for the authors in the submission system.

## Submission checklist (IEEE Access, ScholarOne)

- [ ] Repository public and archived with a DOI; URL and DOI in Data Availability (to-do 6).
- [ ] Placeholders filled (to-dos 1–5).
- [ ] Port the source to the official template (steps below) and rebuild; check that the page count stays under 20.
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

## Porting to the official IEEE Access template

`ieeeaccess.cls` is not available offline, so the draft uses `IEEEtran`, from which the IEEE Access class is derived. On Overleaf, open "IEEE Access LaTeX Template" (or download it from the IEEE Access author resources page) and then:

1. Upload `main.tex`, `references.bib`, `fig_layers.tex`, `tab_timeline.tex`, `tab_ids.tex`, `tab_holdout.tex`, `tab_contrasts.tex`, `tab_explore.tex` and the folder `figures/` into the template project (keep the template's `ieeeaccess.cls`, logos and `IEEEtran.bst`).
2. Replace `\documentclass[journal]{IEEEtran}` with `\documentclass{ieeeaccess}`. Keep `cite`, `amsmath`, `amssymb`, `graphicx`, `booktabs`, `array`, `url`, `xcolor` and `tikz` (with `\usetikzlibrary{arrows.meta}`). If the class already loads `hyperref` or `xcolor`, delete our `\usepackage` lines for them (keep the two `\definecolor` lines).
3. Directly after `\begin{document}` insert the template's front-matter commands:
   ```latex
   \history{Date of publication xxxx 00, 0000, date of current version xxxx 00, 0000.}
   \doi{10.1109/ACCESS.2017.DOI}
   ```
   Leave both as the template placeholders; the journal fills them in.
4. Replace the `\author{...}` block (with its four `\thanks`) by
   ```latex
   \author{\uppercase{Taehong Kwon}\authorrefmark{1},
   \uppercase{Ernest Mnkandla}\authorrefmark{1},
   \uppercase{Donatien Koulla Moulla}\authorrefmark{2},
   and \uppercase{David Sena Attipoe}\authorrefmark{2}}
   \address[1]{School of Computing, College of Science, Engineering and Technology,
     University of South Africa, South Africa (e-mail: thkwon@enu-tech.co.kr)}
   \address[2]{[affiliation to be confirmed]}
   \tfootnote{[Funding statement to be completed by the authors.]}
   \markboth
   {Kwon \headeretal: Coupling Authorization and Payment Layers in a PageRank Walk}
   {Kwon \headeretal: Coupling Authorization and Payment Layers in a PageRank Walk}
   \corresp{Corresponding author: Taehong Kwon (e-mail: thkwon@enu-tech.co.kr).}
   ```
   and delete our `\markboth{IEEE Access}{...}` line.
5. Keep `\begin{abstract}...\end{abstract}`. Rename `IEEEkeywords` to `keywords`: `\begin{keywords} ... \end{keywords}`.
6. Insert `\titlepgskip=-15pt` before `\maketitle`, and delete `\IEEEpeerreviewmaketitle`.
7. Replace `\IEEEPARstart{L}{enders}` with `\PARstart{L}{enders}`.
8. Leave `\newtheorem{proposition}{Proposition}` and the `IEEEproof` environment as they are (the class inherits them from IEEEtran). If the build complains, load `amsthm` and use `proof`.
9. Keep `\appendices` before the Acknowledgment. Keep `\bibliographystyle{IEEEtran}` and `\bibliography{references}`; Overleaf runs BibTeX. Some editorial offices ask for the bibliography inline: then paste the contents of `main.bbl` in place of the two commands.
10. Replace each `IEEEbiographynophoto` by
    ```latex
    \begin{IEEEbiography}[{\includegraphics[width=1in,height=1.25in,clip,keepaspectratio]{kwon.jpg}}]{Taehong Kwon}
    ...
    \end{IEEEbiography}
    ```
    with one photograph per author.
11. Put `\EOD` on the line before `\end{document}`.
12. The unnumbered end sections (Acknowledgment with the AI-use disclosure, Author Contributions, Conflict of Interest, Data Availability) can stay as `\section*{...}`. If the editorial office prefers fewer headings, merge the author contributions and conflict-of-interest statements into the Acknowledgment.
13. Recompile, then check the two-column floats (Tables I, III, IV, V and Figs. 2, 3), the page count and the absence of overfull boxes.
