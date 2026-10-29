# Supplement to Manuscript B

| File | Content |
|---|---|
| `sql/01_materialize_logs.sql` | Scan A and scan B: copies the ERC-20 `Approval` and `Transfer` logs (exactly three topics), the GMX V2 `PositionDecrease` logs and the Aave V3 logs of a time window from the public Arbitrum One table into a project table. Parameters `@start_ts`, `@end_ts`. Committed in `43d8045` with the plan. |
| `sql/02_spender_candidates.sql` | Spenders that received non-zero approvals from at least three distinct owners in the observation window (the cohort candidates, before the account-type check). |
| `sql/03_ego_events.sql` | Ego extraction: approvals with a cohort contract as owner or spender, non-zero transfers with a cohort contract as sender or recipient. Run for the observation window and, after the registration, for July to September 2026. |
| `sql/04_anchor_pairs.sql` | Pair tables at an anchor date, registered analysis: latest allowance per (token, owner, spender), EndorseRank, AWP and raw-amount C-PR weights, activeness. |
| `sql/05_proxies_same_window.sql`, `sql/15_usd_proxies.sql` | Same-window transfer and Sybil-stability proxies of the matched cohort (Rule A, secondary part; the authorization proxies are computed from the pair tables), registered and revised. Query 05 entered with the registration (`0d3a057`); query 15 belongs to the revised analysis. |
| `sql/06_holdout_labels.sql` | Spender labels of a holdout window: new approval pairs, new transfer senders (and the revocation and drain counts, not used in this paper). |
| `sql/07_gmx_accounts.sql`, `sql/09_gmx_contract_closes.sql` | GMX V2 accounts and the closes of contract accounts, decoded locally into the trader label. |
| `sql/12_usd_ego.sql`, `sql/13_usd_constants.sql`, `sql/14_usd_anchor_pairs.sql`, `sql/16_usd_labels.sql` | The same steps in the revised analysis: events of the five tokens valued in US dollars, the slopes and the cap (from the events of the twelve months up to 31 March 2026), pair tables with the capped C-PR authorization layer, labels. Queries 13 to 16 run on the cohort and the twelve-month score window of each freeze, which query 21 of `phd_works` defines. |
| `exploratory_checks.py` | Exploratory checks of Appendix A (run after every result of both analyses was known). |
| `exploratory_checks.json` | Output of that script; every number in Table 6 and Appendix A, and the seed and half-width figures of Section VI-I, come from it. |

The SQL files are copied unchanged from `experiments/sql/` of the authors' repository `phd_works` (current folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/`; in the commits of the plan, the registration and the registered results the same folder was `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments/`). Each file is identical, line ends aside, to its version in commit `950a7a4`, the commit of the revised results. Query 01 was committed with the plan (`43d8045`); queries 02 to 09 entered the repository with the registration (`0d3a057`), after the queries of the observation window had run; queries 12 to 16 belong to the revised analysis (US-dollar amounts, five tokens, scores from the twelve months before each freeze), which was defined after the registered results were known; Table 3 of the paper lists its commits. The placeholders `__DEST__` and the parameters are filled in by `scripts/run_bq.py` of the experiment folder. Queries 08, 10, 11 and 17 to 23 (identifier export, data description, top-token check, loading, and the token counts, cohorts, window views, counts and consistency checks of the twelve-month score windows) are in `phd_works` only (`experiments/sql/`); 10 and 22 compute the counts and shares of the data description.

## Running the exploratory checks

```bash
export PHD_WORKS=/path/to/phd_works        # or pass --phd-works PATH
python exploratory_checks.py --workers 4
```

Needs Python 3.10 or later with NumPy, SciPy, pandas and PyArrow (run with Python 3.11.9, NumPy 2.3.2, SciPy 1.16.1, pandas 3.0.3 with four workers; about four minutes). The script reads only the per-contract score files (`data/2-processed-tables-and-evaluations/[revised-usd-12m/]{holdout-w0,registered-w1|window-w1,same-window}/*_scores.part*.parquet`) and the published summaries (`data/3-published-results-for-thesis/[revised-usd-12m/]`), records their SHA-256 hashes in the output, and builds no graph. It does four things:

1. recomputes A1, A2, F1 to F6 and S1 from the score files with the pipeline's resampling (`numpy.random.default_rng(42).integers(0, n, size=(400, n))` over the cohort sorted by contract id) and SciPy's tau_b, and stops if any value differs from the published summary (largest difference: 0);
2. repeats the five decision contrasts with 50 further seeds (43 to 92) of 400 resamples;
3. computes paired contrasts between neighbouring values of lambda (0, 0.25, 0.5, 0.75, 1) and between 0.25 and 0.75 on every label (seed 42);
4. computes Kendall tau_b between the C-PR score vectors at two values of lambda over each cohort, with paired-bootstrap intervals (seed 42).

## Not computed, and why

- S2 (isolated nodes) cannot be recomputed: the isolated-node scores of the single-layer walks are not in the score files.
- Checks that need the edges (bounded or binary weights in the coupled walk, the mass `r(B)` of Proposition 1, farms on the coupled graph, two-way bootstraps over the owners or senders behind the labels) need the graph tables, which are kept in the authors' BigQuery project and not in either repository.
- The fee of an approval (`c_gas` in the Sybil cost model) and the allowance in force at the freeze block need an Arbitrum node or further scans of the transactions table.
