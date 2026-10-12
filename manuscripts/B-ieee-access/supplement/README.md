# Supplement to Manuscript B

| File | Content |
|---|---|
| `sql/01_materialize_logs.sql` | Scan A and scan B: copies the ERC-20 `Approval` and `Transfer` logs (exactly three topics), the GMX V2 `PositionDecrease` logs and the Aave V3 logs of a time window from the public Arbitrum One table into a project table. Parameters `@start_ts`, `@end_ts`. Committed in `43d8045` with the plan. |
| `sql/02_spender_candidates.sql` | Spenders that received non-zero approvals from at least three distinct owners in the observation window (the cohort candidates, before the account-type check). |
| `sql/03_ego_events.sql` | Ego extraction: approvals with a cohort contract as owner or spender, non-zero transfers with a cohort contract as sender or recipient. Run for the observation window and, after the registration, for July to September 2026. |
| `sql/04_anchor_pairs.sql` | Pair tables at an anchor date, registered analysis: latest allowance per (token, owner, spender), EndorseRank, AWP and raw-amount C-PR weights, activeness. |
| `sql/05_proxies_same_window.sql`, `sql/15_usd_proxies.sql` | Same-window transfer and Sybil-stability proxies of the matched cohort (Rule A, secondary part; the authorization proxies are computed from the pair tables), registered and revised. Query 05 entered with the registration (`0d3a057`), query 15 with the revision (`a897475`, amended in `09dfc32`). |
| `sql/06_holdout_labels.sql` | Spender labels of a holdout window: new approval pairs, new transfer senders (and the revocation and drain counts, not used in this paper). |
| `sql/07_gmx_accounts.sql`, `sql/09_gmx_contract_closes.sql` | GMX V2 accounts and the closes of contract accounts, decoded locally into the trader label. |
| `sql/12_usd_ego.sql`, `sql/13_usd_constants.sql`, `sql/14_usd_anchor_pairs.sql`, `sql/16_usd_labels.sql` | The same steps in the revised analysis: ego tables of the five tokens valued in US dollars, the slopes and the cap (from events up to 31 March 2026), pair tables with the capped C-PR authorization layer, labels. |
| `exploratory_checks.py` | Exploratory checks of Appendix A (run on 11 October 2026, after every result of both analyses was known). |
| `exploratory_checks.json` | Output of that script; every number in Table 6 and Appendix A comes from it. |
| `github_push_events.json` | Push events of `github.com/abitocodes/phd_works` on 9 and 10 October 2026 as GitHub's events interface returned them on 11 October 2026 (Section IV-C). GitHub keeps these events for 90 days, so the file preserves them. |

The SQL files are copied unchanged from `experiments/sql/` of the authors' repository `phd_works` (current folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/`; in the commits of the study the same folder was `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments/`). Each file is byte-identical to its version in commit `77e71f5`. Query 01 was committed with the plan (`43d8045`); queries 02 to 09 entered the repository with the registration (`0d3a057`), after the queries of the observation window had run; queries 12 to 16 were committed with the revision (`a897475`, `09dfc32`, `2705b28`) before any revised score was computed. The placeholders `__DEST__` and the parameters are filled in by `scripts/run_bq.py` of the experiment folder. Queries 08, 10, 11 and 17 to 19 (identifier export, data description, top-token check, loading) are in `phd_works` only (`experiments/sql/`); 10 and 18 compute the counts and shares of the data description.

## Running the exploratory checks

```bash
export PHD_WORKS=/path/to/phd_works        # or pass --phd-works PATH
python exploratory_checks.py --workers 4
```

Needs Python 3.10 or later with NumPy, SciPy, pandas and PyArrow (run with Python 3.13.16, NumPy 2.5.3, SciPy 1.18.1, pandas 3.0.5 on four cores; about ten minutes). The script reads only the per-contract score files (`data/2-processed-tables-and-evaluations/[revised-usd/]{holdout-w0,registered-w1|window-w1,same-window}/*_scores.part*.parquet`) and the published summaries (`data/3-published-results-for-thesis/[revised-usd/]`), records their SHA-256 hashes in the output, and builds no graph. It does four things:

1. recomputes A1, A2, F1 to F6 and S1 from the score files with the pipeline's resampling (`numpy.random.default_rng(42).integers(0, n, size=(400, n))` over the cohort sorted by contract id) and SciPy's tau_b, and stops if any value differs from the published summary (largest difference: 0);
2. repeats the five decision contrasts with 50 further seeds (43 to 92) of 400 resamples;
3. computes paired contrasts between neighbouring values of lambda (0, 0.25, 0.5, 0.75, 1) and between 0.25 and 0.75 on every label (seed 42);
4. computes Kendall tau_b between the C-PR score vectors at two values of lambda over each cohort, with paired-bootstrap intervals (seed 42).

## Not computed, and why

- S2 (isolated nodes) cannot be recomputed: the isolated-node scores of the single-layer walks are not in the score files.
- Checks that need the edges (bounded or binary weights in the coupled walk, the mass `r(B)` of Proposition 1, farms on the coupled graph, two-way bootstraps over the owners or senders behind the labels) need the graph tables, which are kept in the authors' BigQuery project and not in either repository.
- The fee of an approval (`c_gas` in the Sybil cost model) and the allowance in force at the freeze block need an Arbitrum node or further scans of the transactions table.
