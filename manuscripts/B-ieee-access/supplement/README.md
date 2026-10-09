# Supplement to Manuscript B

| File | Content |
|---|---|
| `sql/arbitrum_approvals.sql`, `sql/arbitrum_transfers.sql`, `sql/gmx_event_logs.sql` | The three BigQuery queries of the extraction, copied unchanged from the experiments folder of the authors' repository (`wallet-reputation-experiments/sql/`). Parameters: time window, event signature, wallet list. |
| `exploratory_checks.py` | Exploratory checks of Appendix A and of Sections V–VIII (run 9 October 2026, after every registered and post hoc result was known). |
| `exploratory_checks.json` | Output of that script; every number in Table V (exploratory checks), Appendix A and the exploratory sentences of the text comes from it. |

Run (needs the experiments folder with its `data/`, Python with pandas, NumPy, SciPy, PyArrow and PyYAML):

```bash
python exploratory_checks.py --experiments /path/to/wallet-reputation-experiments
```

The script imports the evaluation modules of the experiments folder unchanged and adds only a vectorised edge-matrix builder; its first check (`solver_check_max_abs_diff`) confirms that it reproduces the registered scores exactly. The run used Python 3.13, NumPy 2.5, SciPy 1.18, pandas 3.0 and PyArrow 25 on a four-core cloud container and took about ten minutes.

Not computed, and why: the fee of an approval transaction (`c_gas`) and the allowance in force at the freeze block (`allowance()` via `eth_call`) need an Arbitrum node or a further BigQuery scan of the transactions table, neither of which was available or authorized for this run; a two-hop expansion of the sample needs a new extraction.
