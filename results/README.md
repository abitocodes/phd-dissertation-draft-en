# Results tables

LaTeX fragments read by Chapter 4 and the appendix. Every file is written by `scripts/export_latex.py` in
`1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/` of `phd_works` from the evaluation
summaries in its `data/2-processed-tables-and-evaluations/` (revised analysis: `revised-usd/`); the copies behind the
thesis, with every number and its JSON key, are in `data/3-published-results-for-thesis/revised-usd/results_digest.md`.
Do not edit these files by hand; regenerate them:

```bash
cd 1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments
CONTRACT_REP_VARIANT=usd python scripts/export_latex.py
```

The same command writes the five figures in `Figures/generated/`.

## Chapter 4

| File | Caption |
|------|---------|
| `alignment-hybrid.tex` | Same-window family-mean Kendall τ for every score of this study. |
| `benchmark-runtime.tex` | Computational benchmark on the full graphs of the matched cohort. |
| `benchmark-scaling.tex` | Runtime against the size of the evaluation set. |
| `endorserank-restarts.tex` | EndorseRank with uniform and with activity-weighted restarts, next to AWP. |
| `fresh-contrasts.tex` | Window W1: the contrasts of rule B with their verdicts and the sensitivity analyses. |
| `fresh-holdout.tex` | Window W1: Kendall τ on the three labels of rule B. |
| `fresh-posthoc.tex` | EndorseRank and its variant with activity restarts in the window W1. |
| `fresh-traders.tex` | Window W1: Kendall τ on the other trader labels. |
| `holdout-diff.tex` | Paired bootstrap differences on the spender holdout W0. |
| `holdout-receiving.tex` | Spender holdout W0 restricted to spenders that had received a transfer before the freeze. |
| `holdout-spenders.tex` | Temporal holdout W0 on the spender cohort. |
| `holdout-traders.tex` | W0 trader run on the GMX V2 profit labels. |
| `neutral-label-contrasts.tex` | Allowance-side against transfer-side scores on the liquidation-free close rate. |
| `neutral-label-recipients.tex` | Traders that receive approvals against all other labelled traders. |
| `robustness-damping.tex` | Robustness: family-mean Kendall τ under PageRank damping d. |
| `robustness-sample-size.tex` | Sensitivity of the family means to the evaluation set. |
| `robustness-slope.tex` | Robustness: family-mean Kendall τ under ten times smaller and larger value slopes. |
| `tau-diff-hybrid.tex` | Same-window paired contrasts of C-PR and S-PR against their two layers and of C-PR against EndorseRank and AWP. |
| `tie-sensitivity.tex` | Same-window family means with missing contracts scored zero or kept as isolated nodes. |

## Appendix

| File | Caption |
|------|---------|
| `alignment-allowance.tex` | Domain alignment of EndorseRank and AWP with the allowance proxies. |
| `alignment-family-ci.tex` | Family-mean Kendall τ of EndorseRank and AWP with bootstrap intervals. |
| `alignment-sybil-stability.tex` | Domain alignment of EndorseRank and AWP with the Sybil-adjusted stability proxies. |
| `alignment-transfer.tex` | Domain alignment of EndorseRank and AWP with the transfer proxies. |
| `benchmark-runs.tex` | Every timed solver call of the benchmark. |
| `endorserank-awp-holdout.tex` | Paired bootstrap differences between EndorseRank and AWP out of window. |
| `neutral-label-grid.tex` | Allowance-side minus transfer-side scores on every trader label in both windows. |
| `registered-vs-revised.tex` | Decision contrasts of the registered analysis and of the revised analysis. |
| `tau-diff.tex` | Same-window paired contrasts between EndorseRank and AWP. |
| `usd-tokens.tex` | The five tokens of the revised analysis, the rows they keep and their prices. |
