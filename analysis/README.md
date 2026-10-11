# Supporting analyses for the manuscripts

Two analyses that the journal manuscripts (`manuscripts/A-plos-one/`, `manuscripts/B-ieee-access/`) report beyond the thesis tables: the closed form of EndorseRank on depth-one spenders, and the comparison of allowance-side with transfer-side scores on GMX V2 contract traders, an outcome built from neither edge type (rules R1–R3). The experiment pipeline in `phd_works` computes both. The scripts here copy the values of both analyses, the revised one (USD amounts, five tokens, cohort 15,107; the thesis's main analysis) and the registered one (raw base units, every ERC-20, cohort 27,844; thesis Appendix 8.6), into JSON files with their sources, and check them against the published checksums, the per-contract score files and the results digests. They compute no new statistic.

| Path | Content |
|---|---|
| `closed-form/export_closed_form.py` | Writes `closed-form/closed_form_check.json` from the `closed_form` blocks of the same-window and W0 summaries of both analyses, with checks on the score files |
| `closed-form/closed_form_check.json` | Output: one row per analysis and graph (4 rows) |
| `neutral-label/PLAN.md` | The registered rules R1–R3 and comparisons, quoted verbatim from `docs/registration_w1.md` (commit `0d3a057`, SHA-256 from the W1 extraction manifest), and what was computed after the labels were known |
| `neutral-label/export_neutral_label.py` | Writes `neutral-label/results.json` from the `neutral_w1`, `neutral_w0` and `neutral_rules` blocks of the W1 summaries of both analyses, and recomputes them from the trader score files as a check |
| `neutral-label/results.json` | Output: every contrast of the grid, stratified contrasts, single-score τ, recipient comparison, influence check, verdicts of R1–R3 |
| `compare_with_digest.py` | Formats the outputs as the results digests do and compares every digest row of the two sections |

## Where the numbers are computed

Repository <https://github.com/abitocodes/phd_works>, experiment folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/`. In the commits that produced the results (`43d8045` to `77e71f5`) the same folder was `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments/`; the scripts look for both.

| Quantity | Code (in `experiments/`) | Summary file and key |
|---|---|---|
| Closed form at T_obs (also the W1 freeze) | `scripts/run_same_window.py`, function `closed_form` | `same-window/eval_summary.json` : `closed_form` |
| Closed form at t1 (W0 freeze) | `scripts/run_holdout.py`, calling the same function | `holdout-w0/eval_summary.json` : `closed_form` |
| Trader comparison, W1 and W0, rules R1–R3 | `scripts/run_registered.py`, function `neutral`, pairs `NEUTRAL_PAIRS`, rules in `main` | W1 summary : `neutral_w1`, `neutral_w0`, `neutral_rules` |

- The switch `CONTRACT_REP_VARIANT=usd` selects the revised analysis; without it the registered one runs (`scripts/common.py`).
- Published summaries: registered in `data/3-published-results-for-thesis/` (W1 summary `registered-w1/eval_summary.json`; published in commit `8d8b568`, 2026-10-09 18:00:55 UTC), revised in `data/3-published-results-for-thesis/revised-usd/` (W1 summary `window-w1/eval_summary.json`; commit `77e71f5`, 2026-10-10 12:48:00 UTC). Each folder holds `results_digest.md`, which names the code revision of the run (`8d8b568` and `2705b28`, each with the uncommitted changes it lists), and `SHA256SUMS.txt`. The checksums were taken on a Windows checkout with CRLF line ends, so the scripts hash each file in its CRLF form.
- Per-contract score files used for the checks: `data/2-processed-tables-and-evaluations/[revised-usd/]same-window/cohort_scores`, `holdout-w0/spender_scores`, `holdout-w0/trader_scores` and `registered-w1/trader_scores` (registered) or `window-w1/trader_scores` (revised), as parquet parts.
- Pre-specification: `docs/analysis_plan.md` (commit `43d8045`, 2026-10-09 13:41:27 UTC), `docs/registration_w1.md` (commit `0d3a057`, 2026-10-09 16:49:32 UTC), `docs/revision_price_weighting.md` (commits `a897475`, `09dfc32`, `2705b28`, 2026-10-10 07:54:35 to 11:24:01 UTC, after the registered results were known and before any revised score). R1–R3 are defined only in the registration, section 3; the plan (section 7) leaves the comparison to it.

## How to regenerate

Python 3.10 or later with numpy, pandas, pyarrow and PyYAML (run here with Python 3.13, numpy 2.5, pandas 3.0, pyarrow 26, PyYAML 6.0). The path to a `phd_works` checkout is required; nothing is guessed.

```bash
export PHD_WORKS=/path/to/phd_works          # or pass --phd-works PATH to each script
python analysis/closed-form/export_closed_form.py
python analysis/neutral-label/export_neutral_label.py      # about 15 s; --no-recompute skips the check
python analysis/compare_with_digest.py
```

Each script exits with status 1 if a checksum, a quote, a verdict or a recomputed value does not match. On 11 October 2026 all three passed: every summary matched `SHA256SUMS.txt`, every score-file check passed, the recomputation reproduced all 2,204 neutral-label values to within 2 × 10⁻¹⁶, and the 520 digest rows of the closed-form and neutral-label sections equal the outputs.

The summaries themselves can only be recomputed in `phd_works` with the graph tables, which are kept in BigQuery (project `dissertation-bq`, dataset `contract_rep`) and not in either repository (`data/1-raw-blockchain-extracts/graph-tables*/` hold only their manifests). After downloading them (`scripts/download_graph_tables.sh`; for the revised analysis `scripts/run_usd_pipeline.py download`), run `scripts/run_same_window.py`, `scripts/run_holdout.py` and `scripts/run_registered.py` from `experiments/` without the switch and again with `CONTRACT_REP_VARIANT=usd` (`scripts/run_usd_local.ps1` runs the revised steps in order), then `scripts/publish_results.py` for each analysis, and the three scripts above.

## closed-form/closed_form_check.json

For PageRank with damping d and uniform restarts, every node without in-edges has the same score c, and a spender v whose owners have no in-edges scores c (1 + d δ(v)), with δ(v) = Σ_u w(u,v)/o(u) (thesis, Section "EndorseRank on depth-one spenders"). Keys of each element of `rows`:

| Key | Meaning |
|---|---|
| `analysis` | `revised` or `registered` |
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

The edges are not in the repository, so the counts of depth-one spenders, the within-1% shares, τ(score, δ) and c itself cannot be recomputed here. The score files allow four checks, all of which pass for the four rows: the file holds exactly the scored set; no contract scores strictly between 0 and c (every node of the solver graph scores at least c; a contract outside it scores 0); every contract scoring above c has received an approval; and the spender count lies between the number of contracts scoring above c and the number scoring at least c. In the registered analysis the spender count equals the number above c. In the revised analysis 7 (T_obs) and 8 (t1) spenders score exactly c; this fits spenders whose increment c d δ(v) is below the floating-point spacing at c, which cannot be confirmed without the edges. For `same_window`, c also exceeds the restart floor (1 − d)/|V|.

## neutral-label/results.json

Use the revised values as the main results and call them a re-analysis with the registered rules; use the registered values only as registered results (`PLAN.md` says what was fixed when). In both analyses R1 does not hold, R2 does not hold and R3 holds.

| Key | Content |
|---|---|
| `analyses.<revised\|registered>.windows.<W1\|W0>.contrasts.<pair>.<label>` | One contrast: `delta_tau`, `ci95_low`, `ci95_high`, `ci975_low`, `ci975_high` (Bonferroni 97.5%, only P and Q on `liquidation_free_rate`, otherwise null), `tau_a`, `tau_b`, `share_positive` (share of resamples with Δτ > 0), `n` (traders), `B` (resamples), `source_key` |
| `contrast_rows` | The same 144 contrasts (2 analyses × 2 windows × 6 pairs × 6 labels) as a flat list, each with `analysis`, `window`, `pair`, `a`, `b`, `contrast`, `label` |
| `...windows.<w>.stratified.<P\|Q>` | Liquidation-free close rate, τ_b within strata of closes (3–4, 5–9, 10–24, 25+), weighted by pairs; no `share_positive`; `B` null because the summary does not record the number of usable resamples (`recompute_check` gives it) |
| `...windows.<w>.taus.<method>.<label>` | Single-score τ_b: `tau`, `ci95_low`, `ci95_high`, `n`, `B` |
| `...windows.<w>.recipients` | Traders with in-approve degree above zero at the freeze against the others: `n`, `share_no_liquidation`, means of three labels, `median_closes` |
| `...windows.<w>.influence_without_top10` | P on the liquidation-free close rate without the ten traders of highest in-approve degree (`n` = traders − 10) |
| `...windows.<w>.max_in_approve_degree`, `n`, `freeze`, `label_window`, `role`; W1 also `trader_counts` | Window facts |
| `analyses.<a>.rules.<R1\|R2\|R3>` | `holds`, `condition`, `inputs` (the values the rule reads), `registered_wording` (the sentence the registration fixed for that verdict), `matches_published` |
| `analyses.<a>.source`, `registration`, `plan_quotes`, `pairs_check` | Provenance and the checks of the registration hash, the quotes in `PLAN.md` and the pairs in the code |
| `pairs`, `labels`, `methods`, `bootstrap`, `strata` | Definitions: P = in-approve degree − transfer in-degree; Q = EndorseRank (activity restarts) − AWP; `layers` = C-PR (λ=1) − C-PR (λ=0); `er_awp` = EndorseRank − AWP; `cpr0_awp` = C-PR (λ=0) − AWP; `er_degree` = EndorseRank − in-approve degree (not named in the registration document) |
| `recompute_check` | Per analysis and window: score files and their SHA-256, number of values compared, largest absolute difference per quantity, mismatches, usable stratified resamples; verdicts from the recomputed W1 values; whether the label columns are identical in the two analyses |

The recomputation uses its own τ_b (from pair counts) and its own resampling (`numpy.random.default_rng(42).integers(0, n, size=(2000, n))` over the score frame sorted by contract id), not the pipeline's code. The trader cohorts have the same size in both analyses (70 in W1, 88 in W0), and their label columns are identical in contract-id order.
