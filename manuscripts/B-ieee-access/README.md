# Manuscript B: IEEE Access

**Title.** Coupling Authorization and Payment Edges in One PageRank Walk for Ranking Smart Contracts: Commit-Gated Rules and a Contract-Graph Re-Analysis on an Ethereum Rollup

**Article type.** Research Article

**Authors.** Taehong Kwon (corresponding, thkwon@enu-tech.co.kr), Ernest Mnkandla, Donatien Koulla Moulla, David Sena Attipoe

"Commit-gated" refers to the rules and to the registered analysis: the extraction script refuses to run unless the registration files are committed without local changes, and it records their SHA-256 hashes; it compares no hash. No result of the main analysis is a registered result, and the paper keeps that distinction in the text, the table captions and the figure legends.

## Target journal and why

*IEEE Access* (IEEE, open access, multidisciplinary engineering and computing).

- **DHET accreditation.** The journal is indexed in Scopus, so it is on the DHET-accredited list that UNISA uses for the two first-author manuscripts.
- **Acceptance likelihood.** The official acceptance rate is about 27%. Reviewers are asked to judge technical soundness, not novelty. This paper's central findings are two decision rules that were **not met**, so a venue that judges soundness rather than novelty of a positive result fits it best.
- **Scope.** Graph ranking, blockchain and network security papers appear in the journal regularly; three of the cited works (Bellini et al., Thibault et al., Liu et al.) are IEEE Access papers on blockchain reputation, rollups and cryptocurrency transaction analysis.
- **Binary decision.** IEEE Access accepts or rejects; there is no major-revision round, so the first submission has to pre-empt the predictable objections: the limits of the commit-gated record, a main analysis that was defined after the registered results were known, cohort members without an edge to another contract, and labels that count mostly user accounts.

## What the paper reports

- **Aim.** A rollup holds very many contracts (1,829,719 typed contracts on Arbitrum One in the eighteen months read). The paper asks whether one PageRank walk over authorization edges and payment edges (C-PR) ranks the contracts users rely on better than a walk over either layer alone, and judges it by two decision rules fixed before the data that judge them were extracted.
- **The main analysis is the contract-graph analysis** (`revised-contract-12m/` of the published results): amounts in US dollars on five tokens (WETH, USDC, USDT0, ARB, WBTC); scores from the twelve months before each freeze (W0: 1 April 2025 to 31 March 2026; same window and W1: 1 July 2025 to 30 June 2026); graphs whose nodes are contracts other than smart accounts (Safe, ERC-4337), with edges read from the whole chain; each allowance counted up to its owner's balance at the freeze (the balance cap), with balances reconstructed from `Transfer` logs; constants m_T 160, m_A 0.071 and U 16,000 USD set on the contract graph. Cohorts: matched cohort 6,443 contracts, W0 spenders 7,864, W1 spenders 7,915. The abstract, the text, the conclusion, every table and both data figures report it first, as a re-analysis under the same rules.
- **The registered analysis** (raw base units, every ERC-20 token, every event since 1 October 2023, graphs that hold every account of the cohort's events; cohort 27,844 contracts) is the test that the rules were fixed for. It is reported beside the main analysis in Tables 1, 6, 7 and 11 and in Figs. 2 and 3. Its record: plan commit `d060f3a` (`43d8045` in the authors' repository) at 2026-10-09 13:41:27 UTC, ten seconds before the BigQuery job of scan A was created; registration commit `1747e64` (`0d3a057`) at 16:49:32 UTC, eight seconds before the job of scan B was created; the gated extraction script wrote its manifest at 16:49:33.
- **How the main analysis is described.** Section IV-D and the undated row ("Later") of Table 2 carry one sentence: "After the registered results were known, the revised analysis was defined: amounts in US dollars on five tokens; scores from the twelve months before each freeze; graphs whose nodes are contracts other than smart accounts, with edges read from the whole chain; each allowance counted up to its owner's balance at the freeze, with balances reconstructed from Transfer logs; constants set on the contract graph; and the discovery-order test." The paper gives no date or time of any definition or commit of the main analysis; Table 3 lists its commits (`6b389df`, `bb78da3`, `7aa7928`) without times. The dated record of the registered test (plan, registration, scan jobs, manifest, registered results, registered benchmark) is as committed. Rules A and B are "applied to the scores of the contract graph", and a result of the main analysis is never called registered or pre-specified.
- **Verdicts.** Rule A is not met in both analyses, and its parts fail differently. Main analysis: A1 −0.025 [−0.045, −0.004] fails (C-PR ranks new approval pairs below the authorization walk), A2 −0.014 [−0.019, −0.008] fails; registered analysis: A1 +0.008 [0.003, 0.013] holds, A2 −0.030 [−0.034, −0.026] fails; the same-window part is not met in either. For Rule B the paper applies two of the registered criteria, F1 and F2, says that under the registration the rule holds only if each of its criteria holds, and writes "Rule B is not met." Main analysis: F1 +0.074 [0.060, 0.087] holds, F2 −0.016 [−0.022, −0.012] fails; registered analysis: F1 +0.101 [0.092, 0.111] holds, F2 −0.025 [−0.029, −0.021] fails. Beside the decision: F6a −0.043 [−0.061, −0.024] in the main analysis (+0.010 [0.005, 0.014] registered), and the two registered sensitivity analyses S1 and S2 by F1 and F2 (not met in both analyses).
- **Coverage frames every out-of-window number.** 72.5% of the W0 spenders, 72.8% of the W1 spenders and 66.3% of the matched cohort are in the union graph; the others have no edge to another contract and score zero. 90.4% and 87.9% of the new approval pairs and 86.3% and 82.3% of the new transfer senders (W0, W1) come from user accounts, which no score reads. Among the spenders inside the union graph A1 is +0.020 [−0.002, 0.043] and F6a +0.007 [−0.017, 0.029]; without the balance cap A1 is +0.064 [0.051, 0.076] and F6a +0.041 [0.031, 0.053]; A2 and F2 fail in every setting (Table 8). The paper reads the failure of A1 as consistent with the place the coupled walk gives to spenders reached only by the payment layer, and does not claim a cause.
- **Contrasts computed after the labels** (no rule; every loss of C-PR is reported, Table 9). C-PR ranks new approval pairs below the in-approve degree (−0.062 in W0, −0.077 in W1) and below EndorseRank (−0.026, −0.043), and new transfer senders below the transfer in-degree (−0.064, −0.066) and below AWP (−0.077, −0.077). Against the union in-degree, the count of the edges it walks, it lies slightly above on new approval pairs (+0.016, +0.011) and below on new transfer senders (−0.053, −0.056). It ranks new approval pairs above AWP (+0.044, +0.040); among the spenders with a payment in-edge the lead is +0.026 [0.013, 0.041] in W0 and +0.007 [−0.008, 0.021] in W1.
- **Sybil section, for farms whose addresses are contracts.** A farm address must be deployed, and its allowance counts only up to the balance it holds. On the EndorseRank graph of 30 June 2026: dangling mass r_D 0.911; a closed farm collects 3.73, 6.16 and 18.30 times its population share at d = 0.75, 0.85 and 0.95; a star of ten farm contracts reaches 3.0% of the cohort's highest score; about 374 farm contracts reach it. A balance threshold of USD 1, 10 or 100 keeps 3.7%, 1.9% or 0.9% of the pairs and lowers the farm that reaches the top to 119, 33 or 9 contracts, so it raises the capital of a farm and shrinks the honest graph faster. The model decides no rule. The registered graph's figures (13, 1,253 and about 1,080,271 farm addresses; factors 2.01, 2.96, 6.62) stand beside them.
- **The companion's test.** Section VI-H quotes the companion's verdict on the coupled walk in the discovery-order test, with the citation; no other result of that test appears here.
- **Who can use the result.** Wallets, explorers and integrations (Section IX), at the size the results support: every score is a weak hint (the best coefficients are about 0.2 on later approvals and about 0.3 on later payers); the two counts, or AWP and an approval count, can be shown side by side; contracts without an edge to another contract, about 27% of each spender cohort, should be shown as unranked; and an authorization score with uniform restarts can be inflated by a farm of contracts.
- **Where the record is.** The plan and the registration were committed to the authors' Git repository, which is private. The paper cites the public repository [ERC20-Allowance-PageRank-Wallet-Reputation](https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation), which holds the study's folder with its history: every copied commit of the registered record keeps its author, committer, times, message and file contents but has a new identifier. Tables 2, 3 and 7 and the text give the public identifiers; Table 3 also gives those of the authors' repository, which the extraction manifest and the registered digest record (the manifest names the registration as `0d3a057`), and the repository's `HISTORY.md` lists both. The published results of the main analysis are in commit `6b389df`, computed at code revision `bb78da3`; the per-contract score files and the tables of the contract graph are in the public Google Drive folder listed in `experiments/drive-manifest.json` at commit `7aa7928`.
- **Limits of the record, as the paper states them.** Commit times come from the committer's clock; the BigQuery job times are kept by Google but visible only to the project owner; no third-party timestamp anchors the commits. The queries of the registered cohort, ego network, pair tables and W0 labels, the score and bootstrap implementations, the same-window and W0 drivers and the unit tests were committed with the registration, after they had run on the observation window and after rule A had been judged. The script has no override; the manifest's `override_used` field is a constant.

## Files

| File | Content |
|---|---|
| `main.tex` | Manuscript source (`ieeeaccess.cls`, two columns); 22 pages when built |
| `references.bib` | 51 references: 50 copied from the thesis bibliography (`Config/references.bib`, same keys) and converted from biblatex to BibTeX for IEEEtran.bst, plus the companion manuscript (`kwon2026companion`); all 51 are cited |
| `fig_layers.tex` | Fig. 1 wrapper (caption) |
| `figures/fig_layers_standalone.tex`, `figures/fig_layers.pdf` | Fig. 1, schematic of the two layers on one set of contracts, with a user account that is no node (TikZ, compiled separately because the class clashes with TikZ) |
| `figures/make_figures_b.py` | Writes Figs. 2 and 3 from the published summaries of the public repository (`revised-contract-12m/` for the main analysis); stops if an interval leaves the plotted range or a published verdict does not follow from its interval |
| `figures/fig_contrasts.pdf` | Fig. 2, forest plot of A1, A2, F1, F2, F6a, F6b and the contrasts of S1 and S2; circles for the contract-graph analysis, squares for the registered analysis |
| `figures/fig_lambda_sweep.pdf` | Fig. 3, tau_b of C-PR against lambda for the W0 and W1 spenders; top row the contract-graph analysis with the union in-degree as dotted lines, bottom row the registered analysis |
| `make_tables.py` | Writes every `tab_*.tex` from the published summaries, the extraction manifest, the job times, the Git history of the public repository and `supplement/exploratory_checks.json`. It checks each summary against `SHA256SUMS.txt`, the checksum file of the main analysis against commit `6b389df`, the digest's code revision against `bb78da3`, the manifest hashes against the committed files, and each printed verdict against its interval |
| `tab_bench.tex` | Table 1, solver time with \|V\|, \|E\| and iterations: the whole contract graph of the main analysis and the graphs of the registered analysis |
| `tab_timeline.tex` | Table 2, order of commitments with UTC times for the registered record, the record of each and what was known; the main analysis is one undated row ("Later") |
| `tab_ids.tex` | Table 3, commit identifiers of the registered record with times and the identifiers of the authors' repository, the commits of the main analysis without times, and SHA-256 of the registration files (CRLF as recorded, LF as stored) and of the plan |
| `tab_graph.tex` | Table 4, the contract graph at both freezes: latest allowances and the balance cap, authorization layer, payment layer, union graph; constants |
| `tab_cohorts.tex` | Table 5, (a) coverage of the W0 spenders, the W1 spenders and the matched cohort by the union graph and the authorization layer; (b) label totals, their share from user accounts, spenders that gained a label, standing allowance pairs by owner class |
| `tab_holdout.tex` | Table 6, out-of-window tau_b with intervals for every score and count, both analyses, W0 and W1 |
| `tab_contrasts.tex` | Table 7, paired contrasts and verdicts: Rule A, the two applied criteria of Rule B, F6, S1, S2 and contrasts computed after the labels, both analyses |
| `tab_union.tex` | Table 8, the rule contrasts and C-PR minus the union in-degree in three settings of the main analysis: whole cohort, spenders inside the union graph, no balance cap |
| `tab_cpr.tex` | Table 9, C-PR minus every other score and count of the main analysis, both windows and both labels, with the subset of spenders that have a payment in-edge |
| `tab_sybil.tex` | Table 10, farms of contracts on the authorization graph, without and with a balance threshold of USD 1, 10 and 100 |
| `tab_explore.tex` | Table 11, exploratory checks (Appendix A): seed spread, steps of the weight, rank agreement between values of lambda, both analyses |
| `supplement/` | Five queries of the registered analysis, a list that locates the queries of the main analysis in the public repository, the exploratory-check script and its output (see `supplement/README.md`) |
| `cover-letter.tex` / `.pdf` | One-page cover letter, dated 29 October 2026 (the date is for the author to set at submission) |
| `main.pdf` | Built manuscript |
| `ieeeaccess.cls`, `IEEEtran.bst`, `spotcolor.sty`, `t1*`, `*.png` | Official IEEE Access template files (pristine copy in `ieee-template/`) |

All eleven `tab_*.tex` files are written by `make_tables.py` and read by `main.tex` with `\input`; none is edited by hand.

## Where each table and figure gets its numbers

Paths are relative to `experiments/data/` of the public repository; `pub` is `3-published-results-for-thesis/` (registered analysis) and `pub/revised-contract-12m/` is the main analysis. Its `results_digest.md` names the file and key of every value and records the code revision `bb78da3`; the folder was committed in `6b389df`.

| Item | Source |
|---|---|
| Table 1 (bench) | `pub[/revised-contract-12m]/benchmark/benchmark.json` : `main` |
| Table 2 (timeline) | `git log` of the public repository (registered record only); `pub/registered-w1/extraction_manifest.json` : `started_at`, `finished_at`; `pub/describe/describe.json` : `timing` |
| Table 3 (ids) | `git show -s` of the commits in the public repository (times printed for the registered record only); identifiers of the authors' repository from `HISTORY.md`; manifest : `sha256` (CRLF), `registration_commit`; `git show <commit>:experiments/<path>` hashed as stored (LF); `pub/revised-contract-12m/results_digest.md` (code revision) and `SHA256SUMS.txt` compared with commit `6b389df` |
| Table 4 (graph) | `pub/revised-contract-12m/describe/describe.json` : `allowances`, `pairs`, `constants`; `holdout-w0` and `window-w1/eval_summary.json` : `union_graph` |
| Table 5 (cohorts) | `pub/revised-contract-12m/holdout-w0`, `window-w1` and `same-window/eval_summary.json` : `cohort_coverage`, `label_split`, `gained_new_approvals`, `gained_new_senders` |
| Table 6 (holdout) | `pub[/revised-contract-12m]/holdout-w0/eval_summary.json` : `taus`; `registered-w1` or `window-w1/eval_summary.json` : `spender_taus` |
| Table 7 (contrasts) | `holdout-w0/eval_summary.json` : `contrasts_prefixed`, `rule_a_primary`, `contrasts_after`; `same-window/eval_summary.json` : `rule_a_secondary`; W1 summary : `rule_b` (F1, F2, F6a, F6b), `sensitivity_awp`, `sensitivity_isolated`, `endorserank_results` |
| Table 8 (union) | `pub/revised-contract-12m/holdout-w0/eval_summary.json` : `contrasts_prefixed`, `baseline_contrasts`, `in_union_graph`; `window-w1/eval_summary.json` : `rule_b`, `baseline_contrasts`, `in_union_graph`; `robustness/robustness.json` : `uncapped_allowances` |
| Table 9 (C-PR) | `pub/revised-contract-12m/holdout-w0/eval_summary.json` : `contrasts_prefixed`, `contrasts_after`, `baseline_contrasts`; `window-w1/eval_summary.json` : `rule_b`, `sensitivity_awp`, `endorserank_results`, `baseline_contrasts`; `supplementary/supplementary.json` : `w0`, `w1` |
| Table 10 (Sybil) | `pub/revised-contract-12m/sybil-model/sybil_model.json` : `graph`, `owners`, `cohort`, `r_D`, `star`, `farm_size_to_reach_cohort_quantile`, `balance_threshold`, `contract_farm` |
| Table 11 (explore) | `supplement/exploratory_checks.json` |
| Fig. 2 (forest) | the same keys as Table 7 |
| Fig. 3 (sweep) | the same keys as Table 6; the dotted lines are the union in-degree rows of the main analysis (`t1_in_degree_union`, `in_degree_union`) |
| Text: same window, Rule A secondary part | `same-window/eval_summary.json` : `families`, `contrasts`, `rule_a_secondary`, `in_union_graph` |
| Text: closed form (Section III-G) | `analysis/closed-form/closed_form_check.json` of the thesis repository (rows of the same window, both analyses) |
| Text: contrasts after the labels | `pub/revised-contract-12m/supplementary/supplementary.json` : `w0.*`, `w1.*`; `holdout-w0` : `contrasts_after`, `baseline_contrasts`; `window-w1` : `endorserank_results`, `baseline_contrasts` |
| Text: seed spread, steps of the weight, rank agreement | `supplement/exploratory_checks.json` |
| Text: Sybil model | `pub[/revised-contract-12m]/sybil-model/sybil_model.json` |
| Text: data counts | `pub/revised-contract-12m/describe/describe.json` (`events`, `account_types`, `nodes`, `pairs`, `allowances`, `constants`, `balance_check`, `timing.bigquery_usd_total`); `typing/c12_account_types.json`; `typing/balance_audit.json`; `cohort/*.json`; the eval summaries' `graph`, `union_graph`, `cohort_coverage` and `label_split` blocks; the registered `pub/describe/describe.json` and `pub/cohort/matched_cohort.json` |

## Numbers of the prose that the check does not find

The check is a read-only script after `../A-plos-one/check_numbers.py`: it reads both results digests, the JSON summaries of both analyses, `analysis/closed-form/closed_form_check.json` and `supplement/exploratory_checks.json`, and looks up every number of the prose (891 in `main.tex`, 5 in `cover-letter.tex`). The cover letter has none that it does not find; `main.tex` has 14:

| Number | Where | Source |
|---|---|---|
| 374 | abstract, Introduction, Section VII | ceiling of 373.23, `sybil-model/sybil_model.json` : `farm_size_to_reach_cohort_quantile.p100.farm_addresses` |
| 119 | Section VII-D | ceiling of 118.34, `sybil_model.json` : `balance_threshold.1.farm_size_to_reach_cohort_quantile.p100.farm_addresses` (33 and 9 are the ceilings of 32.28 and 8.86 for USD 10 and USD 100) |
| 109,000 | Section III-G | rounding of the node count of the authorization graph at 30 June 2026 (109,381 in `benchmark.json` : `main.endorserank.nodes`; 109,389 with the nine pairs of zero weight, `closed_form_check.json`) |
| 1.004 | Section III-H | `benchmark.json` : `main.cpr_l50.edges / main.awp.edges` = 2,591,253 / 2,580,381 |
| 1.51, 1.19 | Section III-H | registered `benchmark.json` : `main.cpr_l50.mean_s / main.awp.mean_s` = 105.51 / 69.82 and the edge ratio 71,375,442 / 59,737,617 |
| 27.9 | Section III-H | `main.awp.mean_s / main.endorserank.mean_s`; the digest prints 27.90 |
| 389,866,882 | Section V-A | sum of the `monthly_counts` rows of stream `approval_ego` (October 2023 to June 2026) in the registered `describe/describe.json`; the transfer count beside it, 1,538,404,067, is the same sum for `transfer_ego` |
| 115,084 | Section VIII-A | `experiments/docs/revision_contract_graph.md`, section 13 ("What stays a contract") |
| 2612, 3607, 721, 42161, (0,1) | Sections I, V, III | not data: EIP-2612, EIP-3607, ERC-721, the chain ID of Arbitrum One, the open interval of lambda |

Derived values that the check finds only because another source value prints the same way were recomputed from the same files: 1.09 (3.080 / 2.821), 4.5% and 37.4% (edges of the authorization graph over those of the payment graph, main and registered), 2.36, 22.4 and 2.68 (time and edge ratios of AWP to EndorseRank), the star ratios 3.0%, 9.2%, 32.5% and 105.4% (`star.ratio_to_highest` without and with a threshold), the ceilings 3, 13, 1,253 and 1,080,271 of the farm sizes, "about 27%" (100% less 72.5% and 72.8%), "about two thirds" (67.4% and 66.0% of the positive latest allowances between contracts are unlimited), and the 82 BigQuery jobs (entries of `data/bq_ledger.json`; the total, USD 54.88, is `describe.json` : `timing.bigquery_usd_total`).

## Distinctness from Manuscript A (PLOS ONE)

Manuscript A reports the discovery-order test, a crawl-ordering experiment on the same contract graph, and sets the single-layer walks, EndorseRank and AWP, against the counts they smooth. Manuscript B covers the coupling operator (C-PR, S-PR), the two pre-specified rules and their commit-gated record, the main analysis as a deviation from the plan and the registration, and the Sybil exposure of the authorization layer. Both describe the same data, account types and graphs. Results that appear in both: the spender holdout coefficients of the raw counts, EndorseRank and AWP with their count contrasts (Tables 6, 7 and 9), the closed form of the authorization walk (Section III-G) and the solver times (Table 1); B attributes them to A (`kwon2026companion`) and says so in the Introduction. The discovery-order test appears only in A; B quotes A's verdict on the coupled walk once (Section VI-H). A's entry for this paper (`kwon2026coupling`) carries the title above.

## Layout rules kept

- Class `ieeeaccess`, two columns; the template files, the author line, the affiliations and the biographies are as they were.
- Abstract: 246 words in one paragraph (limit 150 to 250), no references or equations, in the structure co-supervisor D. K. Moulla asked for on 4 November 2026: the first sentences name the problems of the existing scores and the gap, and the last sentence gives the conclusion and the intended use, here by wallets, explorers and integrations.
- Index terms: the same seven, in alphabetical order (Blockchain, decentralized finance, PageRank, reputation systems, smart contracts, Sybil attacks, token allowances).
- Author line as Moulla edited it on Overleaf: Ernest Mnkandla under affiliation 2 (CAIDS) and "David Attipoe". The biographies, the author contributions and the companion entry read "David Sena Attipoe", and Mnkandla's biography places him in the School of Computing.

## Changes of 11 November 2026

The paper reports the contract-graph analysis as its main analysis, with the registered analysis and its record beside it. The change logs of 22 and 29 October and 4 November 2026 are in this file's Git history (commit `4bcdf02`).

Generators.

- `make_tables.py` (constant `REVISED = "revised-contract-12m"`), `figures/make_figures_b.py` and `supplement/exploratory_checks.py` read the summaries and the per-contract score files of the contract-graph analysis. Rule B appears by its two applied criteria, F1 and F2, with F6 and the spender parts of the two registered sensitivity analyses. Every row, panel and criterion of the cohort that the main analysis does not have is gone from the generators, the tables and the figures.
- `make_tables.py` writes eleven tables. Five are new files (`tab_graph.tex`, `tab_cohorts.tex`, `tab_union.tex`, `tab_cpr.tex`, `tab_sybil.tex`); `tab_bench.tex`, `tab_timeline.tex`, `tab_ids.tex`, `tab_holdout.tex`, `tab_contrasts.tex` and `tab_explore.tex` keep their names and are written anew. The benchmark table and Section III-H say that the main analysis is timed on the whole contract graph (all pairs between contracts, whether or not they touch the matched cohort).
- `supplement/exploratory_checks.py` adds the contrasts of C-PR with the union in-degree, the rule contrasts on the spenders inside the union graph, and a seed spread for A1 and F6a inside the union graph. Run of 11 November 2026: Python 3.11.9, NumPy 2.3.2, SciPy 1.16.1, pandas 3.0.3; 277 s with six workers; every recomputed contrast equals the published value in both analyses (largest difference 0). Over 50 further seeds no verdict of A1, A2, F1 or F2 changes in either analysis; in the main analysis the upper end of A1 stays between −0.0078 and −0.0031 and the whole interval of F2 lies beyond the margin in every seed; inside the union graph the interval of A1 contains zero in 49 of 50 seeds and that of F6a in all 50.

Text (`main.tex`, written anew).

- Working title of the context note; abstract of 246 words; Introduction with the aim, four contributions and the companion paragraph; Related Work; Model (every node is a contract, user accounts are in no graph, the balance cap in both allowance weights, restarts over contracts, Propositions 1 and 2, cost); Section IV with Rule A, Rule B and the sentence on its two applied criteria, the gate on extraction, the main analysis with its one-sentence definition, and what was not pre-specified; Data and Measurement (events of the whole chain, account types, balances and the balance cap, constants, graphs, cohorts with coverage and labels, statistics); Results (same window; W0 and Rule A; W1 and "Rule B is not met."; results beside the decision; inside the union graph and without the balance cap; the weight sweep; seeded restarts; walks against counts with the union in-degree and the companion's verdict; C-PR against the reference walks); the Sybil section for farms of contracts; Threats to Validity; "Implications for Wallets, Explorers and Integrations"; Conclusion; Appendix A; Data Availability with `6b389df`, `bb78da3` and `7aa7928`.
- Readings that follow the data of the contract graph: A1 lies below zero in the main analysis; C-PR lies below EndorseRank and below the in-approve degree on new approval pairs, and below AWP and the transfer in-degree on new transfer senders; against the union in-degree it lies slightly above on approval pairs and below on senders; S-PR is level with the payment walk on new senders in W0 (−0.003 [−0.013, 0.008]).
- `fig_layers.tex` and `figures/fig_layers_standalone.tex`: every node is a contract, the cohort contracts are shaded, and a user account is drawn as no node.

Supplement, bibliography, cover letter.

- `supplement/sql/` holds the five queries of the registered analysis (`02` to `06`), each identical, line ends aside, to `experiments/sql/` of the public repository at commit `1747e64`. Deleted from the folder: `01_materialize_logs.sql`, `07_gmx_accounts.sql`, `09_gmx_contract_closes.sql`, and `12_usd_ego.sql` to `16_usd_labels.sql`. The queries of the main analysis are not copied: `supplement/README.md` lists them by file name at commit `6b389df` of the public repository, and Data Availability says so.
- `references.bib`: `kwon2026companion` carries the companion's working title ("Does PageRank find the smart contracts users rely on sooner than counting? A crawl-ordering test on an Ethereum rollup"); seven entries that the text does not cite any more were taken out, and seven were copied from the thesis bibliography (`cho1998crawling`, `kitzler2023defi`, `luo2025airdrop`, `liu2025sybil`, `wood2025yellowpaper`, `buterin2021erc4337`, `safenddocs`).
- `cover-letter.tex`: the new title and a summary of the contract-graph analysis; one page; its date is unchanged (29 October 2026).

Build and checks.

- Build (MiKTeX pdflatex, bibtex, pdflatex twice): 22 pages, no errors, no undefined citations or references, no BibTeX warnings. Overfull boxes: only the template's own title box (9.3 pt at `\maketitle`) and its header boxes, the same as when the committed version of 4 November is built. `cover-letter.pdf`: one page, no errors.
- Lengths: abstract 246 words; body text from the Introduction to Appendix A without tables, captions, equations and the bibliography about 12,900 words; 11 tables, 3 figures.
- Number check: the table above. `../A-plos-one/check_numbers.py main.tex cover-letter.tex` (A's checker as it stood on 11 November 2026; it does not read the Sybil summaries) lists 25 numbers for `main.tex` and none for the cover letter: twelve values of `sybil-model/sybil_model.json` of the two analyses, six of the table above (1.004, 1.51, 1.19, 27.9, 389,866,882, 119), three that are not data (2612, 42161, 721), two commit fragments (`1747`, `7054746`) and two placeholders of the template (`0000`, `10.1109`).
- Search check of `_revision-context.md` on the `.tex` and `.md` files of this folder (the template's sample file `ieee-template/access.tex` aside). `main.tex`: three hits of "title" (`\title`, `\titlepgskip`, `\maketitle`), "social credit" in the Introduction, where it names what Do and Do measure, and "credit decisions about contracts", the one sentence of the Conclusion on an untested later use. `tab_sybil.tex`: "32{,}000" (gas of a contract creation), which the pattern for a number matches by accident. `README.md`: "title", "accreditation" and "accredited" (which contain a word of the pattern), and the quotations of this paragraph. `supplement/README.md`: none.
- `../tools/overlap_check.py main.tex`: 1.7% 8-gram overlap with the thesis as it stood on 11 November 2026 while its chapters were being revised. The longest shared spans are the one-sentence definition of the main analysis (72 words), the quoted verdict of the companion (70 words), the sentence on the two applied criteria of Rule B (16 words, twice) and the name of the BigQuery table (13 words).
- `make_tables.py`: every published summary of both analyses matched `SHA256SUMS.txt` (CRLF form); the checksum file of the main analysis equals that of commit `6b389df`, and the digest's code revision is `bb78da3`; the manifest hashes equal the CRLF hashes of the files committed in `0d3a057` (`1747e64` in the public repository).

## Still for the authors

1. All co-authors approve the submission (the cover letter states that they have).
2. Length: the build has 22 pages; the checklist below recommends under 20. Decide whether to shorten (candidates: Table 3 or Table 11 to the supplement, Section II) or to submit at this length.
3. The date of the cover letter (29 October 2026) is to be set at submission.
4. The companion entry (`kwon2026companion`) carries Manuscript A's working title and the note "Unpublished manuscript"; keep it in step with A and change the note to the journal name once A is submitted.
5. EIP-3607 is named in Section V-B without a reference, because the thesis bibliography has no entry for it; add one there first if a citation is wanted.
6. The owner contract that holds 98,073 of the 115,006 capped authorization pairs at 30 June 2026 is not identified in the published results, and no analysis without it exists; Section VIII states both. Decide whether to name it or to add that analysis.
7. The supplement points to the queries of the main analysis at commit `6b389df` and does not copy them, because their comments carry dates of the definitions, which the paper does not give. Decide whether to copy them after editing the comments.
8. ORCID iDs in ScholarOne; optional author photographs and longer biographies (IEEE asks for them at the final-files stage).
9. Optional: anchor future registrations with a third-party timestamp (Section IV-C names the gap); measure the fees of a deployment and of an approval (`c_dep`, `c_app`) and the allowance state at the freeze block.
10. Check the current IEEE Access APC and arrange payment or a waiver before acceptance.
11. The thesis, the companion and this paper report the contract-graph analysis as their main analysis, with the registered analysis beside it; keep the three in step if the summaries are published again, and run the overlap check again once the thesis chapters are final.

## Submission checklist (IEEE Access, ScholarOne)

- [x] Repositories public; URLs in Data Availability (a Zenodo DOI is optional).
- [x] Official IEEE Access template.
- [ ] Under 20 pages (recommended): the build has 22.
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
export CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # checkout of github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation
(cd "$CONTRACT_REP_REPO/experiments" && python3 scripts/drive_sync.py pull "*2-processed-tables-and-evaluations/*")   # per-contract score files from the Drive folder
python3 supplement/exploratory_checks.py --workers 6      # about 5 minutes (numpy, scipy, pandas, pyarrow)
python3 make_tables.py                                    # all tab_*.tex (needs git and the public repository's history)
python3 figures/make_figures_b.py                         # Figs. 2 and 3 (needs matplotlib)
(cd figures && pdflatex fig_layers_standalone.tex && mv fig_layers_standalone.pdf fig_layers.pdf)   # Fig. 1
latexmk -pdf -interaction=nonstopmode main.tex            # runs bibtex automatically
latexmk -pdf -interaction=nonstopmode cover-letter.tex
python3 ../tools/overlap_check.py main.tex                # overlap with the thesis (run from this folder)
latexmk -c                                                # optional: delete auxiliary files
```

Requires a TeX installation with TikZ. The build of 11 November 2026 used MiKTeX on Windows, running pdflatex and bibtex directly (pdflatex, bibtex, pdflatex twice); `ieeeaccess.cls` and `IEEEtran.bst` are in this folder. The thesis repository's own `latexmkrc` (XeLaTeX) lives in the repository root and is not read when latexmk runs in this folder. On Windows run the Python scripts with `python -I -X utf8`.
