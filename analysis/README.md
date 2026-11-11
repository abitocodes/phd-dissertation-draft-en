# Supporting analysis for the manuscripts

One analysis that the journal manuscripts (`manuscripts/A-plos-one/`, `manuscripts/B-ieee-access/`) report from a file of this folder: the closed form of EndorseRank on depth-one spenders. The experiment pipeline (folder `experiments/` of the public repository [ERC20-Allowance-PageRank-Wallet-Reputation](https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation)) computes it. The script here copies its values for both analyses into a JSON file with their sources and checks them against the published checksums, the per-contract score files and the results digests. It computes no new statistic.

- **Main analysis (contract-graph analysis):** amounts in US dollars on five tokens, scores from the twelve months before each freeze, graphs whose nodes are contracts, each allowance counted up to its owner's balance at the freeze; matched cohort 6,443. Thesis Chapter 4.
- **Registered analysis:** raw base units, every ERC-20, cohort 27,844. Thesis Appendix 8.6.

| Path | Content |
|---|---|
| `closed-form/export_closed_form.py` | Writes `closed-form/closed_form_check.json` from the `closed_form` blocks of the same-window and W0 summaries of both analyses, with checks on the score files |
| `closed-form/closed_form_check.json` | Output: one row per analysis and graph (4 rows) |
| `compare_with_digest.py` | Formats the output as the results digests do and compares every digest row of the closed-form sections |

## Where the numbers are computed

Public repository <https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation>, experiment folder `experiments/`. It holds the study's folder of the authors' private repository with its commit history; the copied commits keep the original times and contents but have new identifiers, and its `HISTORY.md` lists the original ones, which the manifests and the digest of the registered analysis record. The scripts also run in a checkout of the authors' repository, where the folder is the submodule `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/`.

| Quantity | Code (in `experiments/`) | Summary file and key |
|---|---|---|
| Closed form at T_obs (also the W1 freeze) | `scripts/run_same_window.py`, function `closed_form` | `same-window/eval_summary.json` : `closed_form` |
| Closed form at t1 (W0 freeze) | `scripts/run_holdout.py`, calling the same function | `holdout-w0/eval_summary.json` : `closed_form` |

- The switch `CONTRACT_REP_VARIANT=contract12m` selects the main analysis; without it the registered one runs (`scripts/common.py`).
- Published summaries: registered in `data/3-published-results-for-thesis/`, main analysis in `data/3-published-results-for-thesis/revised-contract-12m/`. Each folder holds `results_digest.md`, which names the code revision of its run, and `SHA256SUMS.txt`. The checksums were taken on a Windows checkout with CRLF line ends, so the scripts hash each file in its CRLF form.
- Per-contract score files used for the checks: `data/2-processed-tables-and-evaluations/[revised-contract-12m/]same-window/cohort_scores` and `holdout-w0/spender_scores`, as parquet parts.
- Pre-specification: `docs/analysis_plan.md` (commit `d060f3a`, 2026-10-09 13:41:27 UTC) and `docs/registration_w1.md` (commit `1747e64`, 2026-10-09 16:49:32 UTC). The definitions of the main analysis (`docs/revision_price_weighting.md`, `docs/revision_one_year_window.md`, `docs/revision_contract_graph.md`, `docs/discovery_protocol.md`) were made after the registered results were known. The closed-form check decides no rule of the plan or the registration.

## How to regenerate

Python 3.10 or later with numpy, pandas, pyarrow and PyYAML (run here with Python 3.13, numpy 2.5, pandas 3.0, pyarrow 26, PyYAML 6.0). The path to a checkout of the public repository is required (a checkout of the authors' repository also works); nothing is guessed. The per-contract score files are in the Google Drive folder listed in `experiments/drive-manifest.json`; `experiments/scripts/drive_sync.py pull` downloads them.

```bash
export CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # or pass --repo PATH to each script
python analysis/closed-form/export_closed_form.py
python analysis/compare_with_digest.py
```

Each script exits with status 1 if a checksum or a compared value does not match. On 11 November 2026 both passed: the four summaries matched `SHA256SUMS.txt`, every score-file check passed, and the 32 digest rows of the closed-form sections equal the output.

The summaries themselves can only be recomputed in the experiment folder with the graph tables, which are kept in BigQuery and on Google Drive, not in the repository. After downloading them (`scripts/download_graph_tables.sh` for the registered analysis; `scripts/drive_sync.py pull` for the main analysis), run `scripts/run_same_window.py` and `scripts/run_holdout.py` from `experiments/` without the switch and again with `CONTRACT_REP_VARIANT=contract12m`, then `scripts/publish_results.py` for each analysis, and the two scripts above.

## closed-form/closed_form_check.json

For PageRank with damping d and uniform restarts, every node without in-edges has the same score c, and a spender v whose owners have no in-edges scores c (1 + d δ(v)), with δ(v) = Σ_u w(u,v)/o(u) (thesis, Section "EndorseRank on depth-one spenders"). Keys of each element of `rows`:

| Key | Meaning |
|---|---|
| `analysis` | `revised` (the main analysis, on the contract graph) or `registered` |
| `window` | `same_window` (graph at T_obs = 2026-06-30 23:59:59 UTC, the W1 freeze) or `W0` (graph at t1 = 2026-03-31 23:59:59 UTC) |
| `graph_date`, `scored_set`, `scored_set_size` | Freeze of the graph; the contracts checked (cohort, or W0 spender cohort) and their number |
| `damping` | d = 0.85 |
| `c`, `spread_of_c` | Common score of the nodes without in-edges; max/min of their scores |
| `spenders`, `depth_one_spenders`, `deeper_spenders` | Contracts of the scored set with a positive-weight in-edge; those none of whose owners has an in-edge; the rest |
| `within_1pct_all`, `within_1pct_depth_one`, `within_1pct_deeper` | Share of the spenders whose EndorseRank is within 1% of the closed form |
| `tau_score_vs_delta` | Kendall τ_b of EndorseRank and δ(v) over all spenders, a point value: the pipeline computes no interval for it, so a manuscript must not present it as an estimate with a confidence interval |
| `allowance_graph_nodes`, `allowance_graph_edges` | Size of the allowance graph in the summary (nodes are not recorded for W0) |
| `source` | Summary file (relative to `experiments/`), key `closed_form`, SHA-256, checksum result |
| `score_file_check` | Checks on the EndorseRank column of the score file (below) |

In the main analysis the allowance graph holds contracts only, so far fewer members of a scored set receive an allowance from another contract than in the registered analysis: 926 of the 6,443 cohort contracts at T_obs (651 of them at depth one) and 1,362 of the 7,864 W0 spenders at t1 (810 at depth one). The closed form holds within 1% for every depth-one spender in all four rows.

The edges are not in the repository, so the counts of depth-one spenders, the within-1% shares, τ(score, δ) and c itself cannot be recomputed here. The score files allow four checks, all of which pass for the four rows: the file holds exactly the scored set; no contract scores strictly between 0 and c (every node of the solver graph scores at least c; a contract outside it scores 0); every contract scoring above c has received an approval; and the spender count lies between the number of contracts scoring above c and the number scoring at least c. In all four rows the spender count equals the number of contracts scoring above c. For `same_window`, c also exceeds the restart floor (1 − d)/|V|.
