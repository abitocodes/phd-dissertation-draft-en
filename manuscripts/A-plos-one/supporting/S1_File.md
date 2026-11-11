# S1 File. Excerpts of the analysis plan and of the W1 registration

Supporting information of the manuscript "Does PageRank find the smart contracts users rely on sooner than counting? A crawl-ordering test on an Ethereum rollup".

This file gives excerpts of the two documents that fixed the design of the registered analysis before this study extracted the data they judge: the analysis plan and the registration of the window W1. The excerpts keep the passages that the article relies on: the data and the windows, the cohort and account-type rules, the scores, the checks, the spender labels, the statistics, rule A, and the two criteria of rule B with the sensitivity analyses that the companion study applies. Every omitted passage is marked `[…]`; apart from the date in the first line of the plan, the omitted passages are passages on outcomes that this paper does not study. Everything outside the marks is verbatim.

The full files are `experiments/docs/analysis_plan.md` and `experiments/docs/registration_w1.md` of the public repository <https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation>, at the commit named in the Data availability statement of the article. The plan was committed before any log of the study was extracted, and the registration after the W0 results were known and before the July–September logs were extracted. The excerpt of the plan gives its text as the plan was committed; the registration commit changed only the heading of its section 7, from "(to be completed and registered before scan B)" to "(registered in docs/registration_w1.md before scan B)".

The two documents fix the registered analysis: amounts in raw base units over every ERC-20 token, every score computed from every extracted event since 1 October 2023, and graphs that hold every account of the cohort's events. The article reports the contract-graph analysis as its main analysis: amounts in US dollars on five tokens; scores from the twelve months before each freeze; graphs whose nodes are contracts other than smart accounts, with edges read from the whole chain; each allowance counted up to its owner's balance at the freeze, with balances reconstructed from Transfer logs; constants set on the contract graph; and the discovery-order test. It was defined after the registered results were known, so none of its results is a registered result, and the discovery-order test decides no rule of the plan or the registration. The documents that define it, with the protocol of the test, are published with its results (see the Data availability statement of the article), and the registered results are given beside the main ones in Table 7 of the article. Rule A (section 6 of the plan) and rule B (section 2 of the registration) concern the coupled walk. The article reports no verdict under them; the companion study reports them, applied to the scores of the contract graph as a re-analysis. Under the registration rule B holds only if each of its criteria holds.

---

## 1. Analysis plan, excerpt

````markdown
# Analysis plan: contract reputation from ERC-20 allowance edges

- Written and committed on […], before any log of this study was extracted.
- Settings live in `config/contract_reputation.yaml`; this plan states what they mean and which results decide which question.
- Sections 1–6 are fixed by this commit. Section 7 (the registered window) is completed and registered in a later commit, before scan B runs.

## 1. Data

- Chain: Arbitrum One (chain ID 42161). Source: `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`.
- Observation window: 2023-10-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC (33 months). The time decay is anchored at T_obs = 2026-06-30 23:59:59 UTC.
- Events: ERC-20 `Approval` and `Transfer` logs with exactly three topics (ERC-721 logs carry a fourth topic and are excluded), […]
- Scan A materialises these events for the observation window into the project table `contract_rep.logs_obs`; scan B does the same for 2026-07-01 to 2026-09-30 and runs only after section 7 is registered.
- Amounts stay in raw token base units. Addresses are lower-cased.
- Every file written under `data/` is split into parts below 90 MB so that it can be committed to GitHub.

## 2. Account type

An address is a contract when `eth_getCode` at one pinned block returns bytecode that is not an EIP-7702 delegation designator (`0xef0100` followed by 20 bytes). No bytecode, or a designator, makes it an externally owned account (EOA). The pinned block number and the date of the read are recorded with the result.

## 3. Cohorts

- Matched cohort W: every contract that, inside the observation window, received a non-zero `Approval` from at least three distinct owners. It is fixed from the approval logs and the code check alone, before any transfer is aggregated. Only cohort members are scored and evaluated; externally owned accounts enter the graphs as owners, senders and receivers but are never evaluated.
- Extraction filter: an approval is kept when a cohort contract is its owner or its spender; a transfer is kept when a cohort contract is its sender or its recipient. Each graph is therefore the ego network of the cohort.
- Holdout spender cohort (W0): every contract spender that holds at least one positive latest allowance at t1 in the extracted approval data.
- […]
- Expanded pool for runtime scaling: deterministic SHA256 subsamples of the cohort (seed `contract-benchmark-v1`); each stage keeps the extracted edges incident to its sampled contracts, so the edge count grows with the stage.

## 4. Scores

All PageRanks use one power-iteration solver: d = 0.85, tolerance 1e-8 (L1), at most 300 iterations, dangling mass returned through the restart distribution.

- AWP (Do, Do and Nguyen, IEEE RIVF 2023): transfer graph; each transfer weighs sigma(Δt)·V(x), sigma(Δt) = 1/(1+exp(k(Δt−t0))) with k = 0.01 and t0 = 180 days, V(z) = 2/(1+exp(−bz))−1 with b = 1 on raw base units; restarts proportional to activeness X_u = Σ_{v≠u} max_e sigma(Δt_e).
- EndorseRank: the latest in-window allowance of each (token, owner, spender), ordered by (block number, log index); a zero allowance deletes the edge; weight sigma(Δt*)·V(a*) summed over tokens; uniform restarts. The variant with AWP's activity restarts is reported beside it.
- C-PR: one walk over a raw-amount allowance layer (Σ_token a*) and a raw-amount transfer layer (Σ_e x_e·sigma(Δt_e)), rows mixed per node with weights λ and 1−λ over the layers in which the node has out-edges; uniform restarts. λ = 0.5 primary, 0.25 and 0.75 sensitivity; λ = 1 and λ = 0 walk one layer alone (C-PR(λ=1), C-PR(λ=0)).
- S-PR: the transfer layer walked with restarts from C-PR(λ=1), restricted to the transfer-layer nodes and renormalised (uniform if that mass is zero).
- Raw degrees: in-approve degree (distinct owners with a positive latest allowance) and transfer in-degree (distinct senders other than the address itself).
- A cohort contract absent from a graph scores 0 under that graph's method; the isolated-node alternative is reported as a sensitivity analysis.

## 5. Checks, labels and statistics

- Same-window families on W: transfer (in-degree including self-transfers, in-value), allowance (in-approve degree, in-approve value), Sybil-adjusted stability (inbound counterparty ratio, transfer tenure in days, active months). Family mean = plain average of the proxies' Kendall tau_b.
- Holdout labels on the spender cohort, counted from 2026-04-01 to 2026-06-30: new owner–spender approval pairs absent from the positive snapshot at t1, and new transfer senders not seen between 2023-10-01 and t1 (self-transfers excluded). Scores and degrees use events up to t1 only, with the decay anchored at t1.
- Statistics: Kendall tau_b and Spearman rho on raw scores; 95% percentile intervals from a paired bootstrap over cohort members, B = 400, seed 42, one index matrix shared by all methods; every comparison is a paired difference on the same resamples; no interpretation thresholds; no p-values.
- Benchmark: one untimed warm-up run (peak memory tracked there), five timed runs; times reported with |V| and |E| of the solver graph.
- Robustness: damping {0.75, 0.85, 0.95}; top-20 token subgraph (largest summed raw amounts, and most rows); isolated-node rule.

## 6. Rule A for the coupled operator (fixed now, before any score exists)

- Primary part, spender holdout W0: C-PR at λ = 0.5 does no worse than C-PR(λ=1) on new approval pairs (95% interval of Δtau contains zero or lies above it) and does better than C-PR(λ=0) on new transfer senders (interval above zero).
- Secondary part, matched cohort, same window: C-PR's point estimate lies inside the 95% interval of the better single layer on the transfer family and on the allowance family, and C-PR exceeds both layers on the Sybil-stability family.
- If the primary part fails, the question whether C-PR beats a walk over either layer alone is answered in the negative. λ is not tuned after any label is seen.

## 7. Registered window W1 (to be completed and registered before scan B)

Scores frozen at 2026-06-30 23:59:59 UTC, labels from 2026-07-01 to 2026-09-30. The decision rule for whether C-PR improves on its transfer layer walked alone, its margin, […] are written here after the W0 results are known and committed with `registered_window.status: registered` before scan B is run.
````

---

## 2. Registration of the window W1, excerpt

````markdown
# Registration of the window W1 (July–September 2026)

- Written after the W0 holdout results were known, and committed with `registered_window.status: registered` in `config/contract_reputation.yaml` **before** scan B, the only query that reads logs dated after 30 June 2026. `scripts/extract_w1.py` refuses to run unless this file and the configuration are committed with that status, and it records their SHA-256 hashes in the extraction manifest.
- Nothing below changes after the July–September logs are extracted.

## 1. Window and cohorts

- Scores are frozen at 2026-06-30 23:59:59 UTC and use every extracted event from 2023-10-01; the decay is anchored at the freeze (these are the same graphs as the same-window evaluation).
- Labels are counted from 2026-07-01 00:00:00 to 2026-09-30 23:59:59 UTC.
- Spender cohort: every contract spender with a positive latest allowance at the freeze in the extracted approval data. Labels: new approval pairs and new transfer senders, defined as in the analysis plan (section 5), with the approvals and transfers of the window extracted under the same cohort filter.
- […]
- Methods, solver settings, SQL and bootstrap (400 paired resamples, seed 42) are those of the analysis plan.

## 2. Decision rule B: does C-PR improve on its transfer layer walked alone?

Contrast Δτ = τ(C-PR, λ = 0.5) − τ(C-PR, λ = 0), paired over the cohort's members, 95% percentile interval.

- F1 (spenders, new approval pairs): the interval lies above zero.
- F2 (spenders, new transfer senders): the lower end lies above −δ.
- […]

C-PR improves on its transfer layer walked alone only if F1, F2 […] all hold. The margin is δ = 0.01, the half-width of the paired interval of the corresponding contrast on new transfer senders in W0 (0.0040: Δτ = -0.030, interval [-0.034, -0.026]), rounded up to two decimals; a smaller difference cannot be resolved at these sample sizes. […]

Reported in this order, outside the decision:
- […]
- F6: the primary part of rule A on W1 (C-PR no worse than C-PR(λ = 1) on new approval pairs; better than C-PR(λ = 0) on new senders).
- Sensitivity 1: […] with AWP in place of C-PR(λ = 0).
- Sensitivity 2: F1–F6 with the cohort members that a graph leaves out kept as isolated nodes.

[…]
````
