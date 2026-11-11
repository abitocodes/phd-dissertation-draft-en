# Results tables

LaTeX fragments read by the chapters and the appendix. Every file is written by `scripts/export_latex.py` in
`experiments/` of the public repository [ERC20-Allowance-PageRank-Wallet-Reputation](https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation) from the evaluation
summaries in its `data/2-processed-tables-and-evaluations/` (main analysis, the contract-graph analysis: `revised-contract-12m/`); the copies behind the
thesis, with every number and its JSON key, are in `data/3-published-results-for-thesis/revised-contract-12m/results_digest.md`.
Do not edit these files by hand; regenerate them:

```bash
cd experiments                                  # of the public repository
CONTRACT_REP_VARIANT=contract12m python scripts/export_latex.py --into-manuscript
```

The same command writes the seven figures in `Figures/generated/`. Each table is input once in the thesis; the lists below
are rebuilt from the manuscript with `dissertation/tools/toc/make_results_readme.py` of the public repository.

## Chapter 4

| File | Section | Entry in the List of Tables |
|------|---------|-----------------------------|
| `graph-layers.tex` | Case study setting: Arbitrum One | The two layers of the contract graph at both freezes. |
| `cohort-coverage.tex` | Cohorts | Where the members of each cohort lie in the contract graph. |
| `benchmark-runtime.tex` | Computational benchmark (Claim C6) | Computational benchmark on the contract graph. |
| `benchmark-scaling.tex` | Runtime on subsamples of the matched cohort | Runtime on subsamples of the matched cohort and on the whole contract graph. |
| `alignment-hybrid.tex` | Same-window alignment (Claim C5) | Same-window family-mean Kendall τ for every score of this study. |
| `tie-sensitivity.tex` | Rank divergence (H1 / RQ1) | Same-window family means with missing contracts scored zero or kept as isolated nodes. |
| `robustness-damping.tex` | Damping | Robustness: family-mean Kendall τ under PageRank damping d. |
| `robustness-slope.tex` | Value-slope sensitivity | Robustness: family-mean Kendall τ under ten times smaller and larger value slopes. |
| `robustness-sample-size.tex` | Sample-definition sensitivity | Sensitivity of the family means to the evaluation set. |
| `endorserank-restarts.tex` | Restarts of EndorseRank | EndorseRank with uniform and with activity-weighted restarts, next to AWP. |
| `uncapped-sensitivity.tex` | Balance-cap sensitivity | Sensitivity to the balance cap. |
| `discovery-decision.tex` | Discovery order (RQ2) | Discovery-order test: the decision contrasts and their reading. |
| `discovery-auc.tex` | Discovery order (RQ2) | Discovery-order test: AUC_10% of every ordering in the four runs. |
| `discovery-contrasts.tex` | Discovery order (RQ2) | Discovery-order test: the contrasts reported outside the decision. |
| `holdout-spenders.tex` | Temporal holdout of the single-layer walks (RQ3) | Temporal holdout W0 on the spender cohort. |
| `holdout-diff.tex` | Temporal holdout of the single-layer walks (RQ3) | Paired bootstrap differences on the spender holdout W0. |
| `holdout-receiving.tex` | Temporal holdout of the single-layer walks (RQ3) | Spender holdout W0 restricted to spenders that had received a transfer before the freeze. |
| `fresh-posthoc.tex` | The single-layer walks in the registered window W1 | EndorseRank and its variant with activity restarts in window W1. |
| `tau-diff-hybrid.tex` | The coupled walk within the window | Same-window paired contrasts of C-PR and S-PR against their two layers and of C-PR against EndorseRank and AWP. |
| `fresh-holdout.tex` | Rule B in the registered window W1 | Window W1: Kendall τ on the two spender labels. |
| `fresh-contrasts.tex` | Rule B in the registered window W1 | Window W1: F1 and F2, two of rule B's registered criteria, with their verdicts and the sensitivity analyses. |
| `cpr-contrasts.tex` | C-PR beside every other score | C-PR against every other score and the raw counts out of window. |
| `union-members.tex` | C-PR beside every other score | The main out-of-window contrasts inside the union graph. |

## Chapter 5

| File | Section | Entry in the List of Tables |
|------|---------|-----------------------------|
| `sybil-threshold.tex` | A threshold on the balance | The Sybil cost model on the contract graph and its sensitivity to a balance threshold. |

## Appendix

| File | Section | Entry in the List of Tables |
|------|---------|-----------------------------|
| `benchmark-runs.tex` | Benchmark run logs | Every timed solver call of the benchmark. |
| `usd-tokens.tex` | Tokens, prices and allowance amounts | The five tokens, their allowances between contracts and their prices. |
| `contract-types.tex` | Contract graph: account types, smart accounts and balances | Account types of the contract graph. |
| `allowance-cap.tex` | Contract graph: account types, smart accounts and balances | Latest allowances between contracts and the balance cap. |
| `label-split.tex` | Contract graph: account types, smart accounts and balances | The labels by the class of the account they count. |
| `discovery-sizes.tex` | Discovery-order test: universes, coverage, sensitivity and diagnostics | Sizes of the contract graph and of the universes of the discovery-order test. |
| `discovery-coverage.tex` | Discovery-order test: universes, coverage, sensitivity and diagnostics | Coverage of the two importances by the contract graph and the universes. |
| `discovery-sensitivity.tex` | Discovery-order test: universes, coverage, sensitivity and diagnostics | Discovery-order test: sensitivity of the decision contrasts. |
| `discovery-diagnostics.tex` | Discovery-order test: universes, coverage, sensitivity and diagnostics | Discovery-order test: ties, wasted visits and hub visits. |
| `tau-diff.tex` | Same window | Same-window paired contrasts between EndorseRank and AWP. |
| `alignment-transfer.tex` | Proxy detail | Domain alignment of EndorseRank and AWP with the transfer proxies. |
| `alignment-allowance.tex` | Proxy detail | Domain alignment of EndorseRank and AWP with the allowance proxies. |
| `alignment-sybil-stability.tex` | Proxy detail | Domain alignment of EndorseRank and AWP with the Sybil-adjusted stability proxies. |
| `endorserank-awp-holdout.tex` | Out of window | Paired bootstrap differences between EndorseRank and AWP out of window. |
| `registered-vs-revised.tex` | The Registered Analysis | Decision contrasts of the registered analysis and of the contract-graph analysis. |

## Generated but not input

| File | Entry in the List of Tables |
|------|-----------------------------|
| `alignment-family-ci.tex` | Family-mean Kendall τ of EndorseRank and AWP with bootstrap intervals. |
