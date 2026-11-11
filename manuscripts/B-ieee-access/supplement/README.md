# Supplement to Manuscript B

| File | Content |
|---|---|
| `sql/02_spender_candidates.sql` | Registered analysis. Spenders that received non-zero approvals from at least three distinct owners in the observation window (the cohort candidates, before the account-type check). |
| `sql/03_ego_events.sql` | Registered analysis. Extraction around the cohort: approvals with a cohort contract as owner or spender, non-zero transfers with a cohort contract as sender or recipient. Run for the observation window and, after the registration, for July to September 2026. |
| `sql/04_anchor_pairs.sql` | Registered analysis. Pair tables at an anchor date: latest allowance per (token, owner, spender), EndorseRank, AWP and raw-amount C-PR weights, activeness. |
| `sql/05_proxies_same_window.sql` | Registered analysis. Same-window transfer and Sybil-stability proxies of the matched cohort (Rule A, secondary part; the authorization proxies are computed from the pair tables). |
| `sql/06_holdout_labels.sql` | Registered analysis. Spender labels of a holdout window: new approval pairs, new transfer senders (and the revocation and drain counts, not used in this paper). |
| `exploratory_checks.py` | Exploratory checks of Appendix A (run after every result of both analyses was known). |
| `exploratory_checks.json` | Output of that script; every number in Table 11 and Appendix A comes from it. |

## Which queries are copied, and from which commit

The public repository [ERC20-Allowance-PageRank-Wallet-Reputation](https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation) holds the study's folder of the authors' private Git repository with its commit history; the commits of the registered record keep their times and contents but have new identifiers, and its `HISTORY.md` lists those of the authors' repository.

- **Copied here: the five queries of the registered analysis above.** Each file is identical, line ends aside, to `experiments/sql/` of the public repository at commit `1747e64`, the registration commit, and has not changed since (checked against commit `6b389df` as well). They entered the repository with the registration, after the queries of the observation window had run. The placeholders `__DEST__` and the parameters are filled in by `scripts/run_bq.py` of the experiment folder.
- **Not copied: the rest of the SQL of the registered analysis.** The full set is in `experiments/sql/` of the public repository at commit `344017e`, the commit of the registered results, and is read there. It includes the query that copies the logs of a time window from the public table (scan A and scan B; committed with the plan in `d060f3a`), the identifier export, the data description and the top-token check.
- **Not copied: the queries of the main analysis (the contract-graph analysis).** They are in `experiments/sql/` of the public repository at commit `6b389df`, the commit of the published results, and are read there:
  - `24_c12_logs5.sql` (the five-token events of the whole chain), `25_c12_ends.sql`, `26_c12_tx_senders.sql` and `29_c12_rpc_queue.sql` (the addresses, the transaction senders and the addresses whose code is read), `31_c12_contracts.sql` (contracts, user accounts and the events between contracts);
  - `32_c12_bal_pre.sql`, `33_c12_bal.sql`, `34_c12_anchor_blocks.sql` and `43_c12_bal_audit.sql` (balances from `Transfer` logs, the blocks of the freezes and the sample of the balance check);
  - `36_c12_allow_triples.sql` (latest allowances between contracts with the balance cap), `36_c12_constants.sql` (m_T, m_A, U), `37_c12_pairs.sql` (the pairs of both layers, capped and uncapped);
  - `38_c12_cohorts.sql` and `38_c12_proxies.sql` (the cohorts and the same-window proxies), `39_c12_label_parts.sql` (the labels split by the class of the counted account), `42_c12_checks.sql` (64 invariants, all zero before the download);
  - the cohort lists and the labels themselves are computed on the five-token events that name a cohort address, by `12_usd_ego.sql`, `14_usd_anchor_pairs.sql`, `16_usd_labels.sql` and `21_usd12m_cohorts.sql` of the same folder;
  - `27`, `28`, `35`, `36_c12_user_events.sql`, `40` and `41` serve cross-checks, the export and the discovery-order test of the companion manuscript.

  The definitions that these queries implement are in `experiments/docs/revision_contract_graph.md` of the public repository, and the published summaries with their checksums in `experiments/data/3-published-results-for-thesis/revised-contract-12m/`.

## Running the exploratory checks

```bash
export CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # checkout of the public repository, or pass --repo PATH
python -I -X utf8 exploratory_checks.py --workers 4
```

The per-contract score files are not in the Git history; `experiments/scripts/drive_sync.py` downloads them from the public Google Drive folder listed in `experiments/drive-manifest.json`. The field `repository_head` of the published `exploratory_checks.json` gives the head commit of the public repository at the run. Needs Python 3.10 or later with NumPy, SciPy, pandas and PyArrow (run with Python 3.11.9, NumPy 2.3.2, SciPy 1.16.1, pandas 3.0.3; 277 s with six workers). The script reads only the per-contract score files (`data/2-processed-tables-and-evaluations/revised-contract-12m/{holdout-w0,window-w1,same-window}/*_scores.part*.parquet` for the main analysis and `data/2-processed-tables-and-evaluations/{holdout-w0,registered-w1,same-window}/` for the registered one; of the registered folders only the spender and cohort score files) and the published summaries, records their SHA-256 hashes in the output, and builds no graph. It does four things:

1. recomputes A1, A2, F1, F2, F6 and the two contrasts of the first sensitivity analysis from the score files with the pipeline's resampling (`numpy.random.default_rng(42).integers(0, n, size=(400, n))` over the cohort sorted by contract id) and SciPy's tau_b, and, for the main analysis, the contrasts of C-PR with the union in-degree and the contrasts on the spenders inside the union graph; it stops if any value differs from the published summary (largest difference: 0);
2. repeats the four rule contrasts (A1, A2, F1, F2) with 50 further seeds (43 to 92) of 400 resamples, in both analyses, and A1 and F6a on the spenders inside the union graph in the main analysis;
3. computes paired contrasts between neighbouring values of lambda (0, 0.25, 0.5, 0.75, 1) and between 0.25 and 0.75 on both spender labels (seed 42);
4. computes Kendall tau_b between the C-PR score vectors at two values of lambda over each cohort, with paired-bootstrap intervals (seed 42).

## Not computed, and why

- The second sensitivity analysis (isolated nodes) cannot be recomputed: its isolated-node scores are not in the score files.
- Checks that need the edges (the mass `r(B)` of Proposition 1, the analysis without the owner contract that holds most authorization pairs at the freeze of 30 June 2026, farms on the coupled graph, two-way bootstraps over the owners or senders behind the labels) need the pair tables; they are in the public Drive folder, and this script does not read them.
- The fees of a deployment and of an approval (`c_dep` and `c_app` in the Sybil cost model) and the allowance in force at the freeze block need an Arbitrum node or further scans of the transactions table.
