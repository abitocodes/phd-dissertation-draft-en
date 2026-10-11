# S1 File. Pre-specification documents

Supporting information of the manuscript "Allowance edges or transfer edges? Evaluating on-chain smart contract reputation out of window against degree baselines".

This file reproduces verbatim the three documents that fixed, in order, the design of the study: the analysis plan, the registration of the window W1, and the revision of the amounts. Each is copied with `git show <commit>:<path>` from the authors' public repository <https://github.com/abitocodes/phd_works>, folder `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments/docs/` at these commits, all on the repository's default branch `master`. Times are UTC; the commits record the local time of the machine on which they were made (UTC+9).

| Document | Commit | Committed (UTC) | SHA-256 of the text as stored (LF line ends) | SHA-256 with CRLF line ends |
|---|---|---|---|---|
| Analysis plan, `analysis_plan.md` | `43d80457142dc002c4410d4af1c3c164f39a3272` | 2026-10-09 13:41:27 | `7ec80d49c17331bd10e086fecd909a3f36020dbb284f0dbfbb81a8549f84fd9f` | `35195ab5675c05c9a892d16a899a981be49aa564e00081a004fda3583f293212` |
| W1 registration, `registration_w1.md` | `0d3a057e4f0c8473d36d89fbe33c24deff0c9911` | 2026-10-09 16:49:32 | `34cd6dfeb56b8fb8a553cb24afbff06c6a94e6f69a2eb7f7d642b0cc39e54b2c` | `2126c8dc3fe3c0f9273aa4ecfc1e15bddc1f5a6f65e98548b9528f2b18ca2a6b` |
| Revision of the amounts, `revision_price_weighting.md` | `2705b28a4653d47a6940cca064bf923562db8f9d` | 2026-10-10 11:24:01 | `80cae0735ae97bfb743dbac98a39e2f35f41bf3621a340db8ed01385f70febc6` | `3db11f1f27f45ffba4f58f866494f774e541fec4e9601532f7ddec4b49e6aeab` |

What each hash can be checked against:

- The plan was committed before any log of the study was extracted. Its only later change is the heading of its section 7, which commit `0d3a057` changed from "(to be completed and registered before scan B)" to "(registered in docs/registration_w1.md before scan B)"; the published checksum of the plan (`SHA256SUMS.txt` of the results, CRLF form `2558729a...`) is that of the changed version.
- The registration's CRLF hash is the one recorded in the extraction manifest of the July–September logs (`data/3-published-results-for-thesis/registered-w1/extraction_manifest.json`, key `sha256`). The manifest records the registration commit, no use of the testing override, and an extraction run from 16:49:33 to 16:50:55 UTC on 9 October 2026. The manifest was written on a Windows checkout, hence the CRLF form.
- The revision was decided after the registered results of the same window, W0 and W1 were known, and committed before any revised score was computed, in three steps: `a8974759f8a8e6e0c8b07c23481ff429eaa492ee` (07:54:35, the reasons, the token rule, prices, weights and scope), `09dfc323de2c3f0ffa40c7a6a0c5adf0b94c1122` (08:12:44, the selection of five tokens) and `2705b28a4653d47a6940cca064bf923562db8f9d` (11:24:01, the amendment of the allowance cap). The version reproduced here is the last; the file has not changed since, and its CRLF hash equals the published checksum (`revised-usd/SHA256SUMS.txt`).

The article reports the revised analysis. Its scores were defined after the registered results were known, so the rules of the registration (R1–R3 in section 3) are applied to them as a re-analysis, not as registered tests; the registered results are given beside them in Table 6 of the article. Rule A (section 6 of the plan) and rule B (section 2 of the registration) concern the coupled walk of a companion study and are not reported in this article.

---

## 1. Analysis plan (commit 43d8045)

````markdown
# Analysis plan: contract reputation from ERC-20 allowance edges

- Written and committed on 9 October 2026, before any log of this study was extracted.
- Settings live in `config/contract_reputation.yaml`; this plan states what they mean and which results decide which question.
- Sections 1–6 are fixed by this commit. Section 7 (the registered window) is completed and registered in a later commit, before scan B runs.

## 1. Data

- Chain: Arbitrum One (chain ID 42161). Source: `bigquery-public-data.goog_blockchain_arbitrum_one_us.logs`.
- Observation window: 2023-10-01 00:00:00 UTC to 2026-06-30 23:59:59 UTC (33 months). The time decay is anchored at T_obs = 2026-06-30 23:59:59 UTC.
- Events: ERC-20 `Approval` and `Transfer` logs with exactly three topics (ERC-721 logs carry a fourth topic and are excluded), GMX V2 `EventLog1` logs named `PositionDecrease` from the EventEmitter, and Aave V3 pool `Borrow`, `Repay` and `LiquidationCall` logs.
- Scan A materialises these events for the observation window into the project table `contract_rep.logs_obs`; scan B does the same for 2026-07-01 to 2026-09-30 and runs only after section 7 is registered.
- Amounts stay in raw token base units. Addresses are lower-cased.
- Every file written under `data/` is split into parts below 90 MB so that it can be committed to GitHub.

## 2. Account type

An address is a contract when `eth_getCode` at one pinned block returns bytecode that is not an EIP-7702 delegation designator (`0xef0100` followed by 20 bytes). No bytecode, or a designator, makes it an externally owned account (EOA). The pinned block number and the date of the read are recorded with the result.

## 3. Cohorts

- Matched cohort W: every contract that, inside the observation window, received a non-zero `Approval` from at least three distinct owners. It is fixed from the approval logs and the code check alone, before any transfer is aggregated. Only cohort members are scored and evaluated; externally owned accounts enter the graphs as owners, senders and receivers but are never evaluated.
- Extraction filter: an approval is kept when a cohort contract is its owner or its spender; a transfer is kept when a cohort contract is its sender or its recipient. Each graph is therefore the ego network of the cohort.
- Holdout spender cohort (W0): every contract spender that holds at least one positive latest allowance at t1 in the extracted approval data.
- Trader cohort: GMX V2 accounts that are contracts, appear in the freeze-date graph, and close at least three positions in the label window.
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

Scores frozen at 2026-06-30 23:59:59 UTC, labels from 2026-07-01 to 2026-09-30. The decision rule for whether C-PR improves on its transfer layer walked alone, its margin, the trader label and any comparison on outcomes built from neither edge type are written here after the W0 results are known and committed with `registered_window.status: registered` before scan B is run.
````

---

## 2. Registration of the window W1 (commit 0d3a057)

````markdown
# Registration of the window W1 (July–September 2026)

- Written after the W0 holdout results were known, and committed with `registered_window.status: registered` in `config/contract_reputation.yaml` **before** scan B, the only query that reads logs dated after 30 June 2026. `scripts/extract_w1.py` refuses to run unless this file and the configuration are committed with that status, and it records their SHA-256 hashes in the extraction manifest.
- Nothing below changes after the July–September logs are extracted.

## 1. Window and cohorts

- Scores are frozen at 2026-06-30 23:59:59 UTC and use every extracted event from 2023-10-01; the decay is anchored at the freeze (these are the same graphs as the same-window evaluation).
- Labels are counted from 2026-07-01 00:00:00 to 2026-09-30 23:59:59 UTC.
- Spender cohort: every contract spender with a positive latest allowance at the freeze in the extracted approval data. Labels: new approval pairs and new transfer senders, defined as in the analysis plan (section 5), with the approvals and transfers of the window extracted under the same cohort filter.
- Trader cohort: GMX V2 accounts that hold contract code, are nodes of the freeze-date graph (either layer), and close at least three positions in the label window. Label: the liquidation-free close rate, one minus the share of the account's closes in the window that were liquidations.
- Methods, solver settings, SQL and bootstrap (400 paired resamples, seed 42) are those of the analysis plan.

## 2. Decision rule B: does C-PR improve on its transfer layer walked alone?

Contrast Δτ = τ(C-PR, λ = 0.5) − τ(C-PR, λ = 0), paired over the cohort's members, 95% percentile interval.

- F1 (spenders, new approval pairs): the interval lies above zero.
- F2 (spenders, new transfer senders): the lower end lies above −δ.
- F3 (traders, liquidation-free close rate): the lower end lies above −δ.

C-PR improves on its transfer layer walked alone only if F1, F2 and F3 all hold. The margin is δ = 0.01, the half-width of the paired interval of the corresponding contrast on new transfer senders in W0 (0.0040: Δτ = -0.030, interval [-0.034, -0.026]), rounded up to two decimals; a smaller difference cannot be resolved at these sample sizes. If neither score predicts the trader label, F3 can pass with both coefficients near zero; the two coefficients are therefore reported next to the verdict.

Reported in this order, outside the decision:
- F4: C-PR against C-PR(λ = 0) on the liquidation-free close rate, as a superiority test.
- F5: C-PR against C-PR(λ = 1) on the same label.
- F6: the primary part of rule A on W1 (C-PR no worse than C-PR(λ = 1) on new approval pairs; better than C-PR(λ = 0) on new senders).
- Sensitivity 1: F1–F4 with AWP in place of C-PR(λ = 0).
- Sensitivity 2: F1–F6 with the cohort members that a graph leaves out kept as isolated nodes.

## 3. Comparison on an outcome built from neither edge type

The trader labels come from GMX closes, which enter neither graph. Two windows: W1 (primary; freeze 30 June, labels July–September) and W0 (secondary; freeze 31 March, labels April–June, trader cohort defined in the same way). The trader liquidation labels of W0 have not been computed for any score when this file is committed.

Four pairs set allowance against transfer: in-approve degree and transfer in-degree; EndorseRank with AWP's activity restarts and AWP; EndorseRank and AWP; C-PR(λ = 1) and C-PR(λ = 0). C-PR(λ = 0) minus AWP is reported to isolate AWP's weights and restarts. Six labels are reported: liquidation-free close rate (primary), no-liquidation flag, profitable closes, realized gain, profitable share, non-loss share.

Decision contrasts on the liquidation-free close rate in W1, each with a Bonferroni 97.5% interval from 2,000 paired resamples (seed 42):
- P: in-approve degree minus transfer in-degree.
- Q: EndorseRank with activity restarts minus AWP.

Because the chance of a liquidation rises with the number of closes, τ_b is also computed within strata of 3–4, 5–9, 10–24 and 25 or more closes and weighted by each stratum's pairs.

- R1 (count-level lead): the 97.5% interval of P and the 95% interval of the stratified P lie above zero in W1, and P is positive in W0.
- R2 (PageRank-level lead): the 97.5% interval of Q lies above zero in W1 and Q is positive in W0.
- R3 (specificity): if P on the profitable share or on the non-loss share in W1 is below zero with a 95% interval excluding zero, the allowance signal is read as specific to liquidation avoidance.

Recipients (traders with in-approve degree above zero at the freeze) are compared with the other traders on every label; an influence check drops the ten recipients of highest in-approve degree.

Wording of the conclusions, fixed now: if R1 holds, "the approval count at the freeze ranked contract traders above the transfer count on later liquidation avoidance"; if R1 fails, "no count-level lead of allowance over transfer on later liquidation avoidance"; if R2 holds, the same sentence for the PageRank pair, otherwise "the PageRank versions are not resolved"; if R3 applies, "the signal concerns forced-liquidation avoidance, not trading success".
````

---

## 3. Revision of the amounts (commits a897475, 09dfc32, 2705b28; text as of 2705b28)

````markdown
# Revision: amounts in USD over five price-verified tokens

- Written on 10 October 2026, after the registered results of the same window, W0 and W1 were known, and committed **before any revised score, proxy or label was computed**. The commit that adds this file is the reference point of the revision.
- This is a deviation from the analysis plan (`docs/analysis_plan.md`, commit 43d8045) and from the W1 registration (`docs/registration_w1.md`, commit 0d3a057). It is decided after results were seen, so the revised results are post hoc and are never called registered.
- The registered analysis stays as it was committed. Its configuration, SQL (`sql/01`–`11`), code path and outputs (`data/2-processed-tables-and-evaluations/*`, `data/3-published-results-for-thesis/*`) are not changed and can be rerun with `CONTRACT_REP_VARIANT` unset.

## 1. Why the amounts are revised

1. **The amount played no part in EndorseRank and AWP.** The plan applied V(z) = 2/(1+exp(−bz)) − 1 with b = 1 to raw base units. V(z) is within 10⁻⁴ of 1 for z ≥ 10 base units, and 99.52% of the ego transfers and 99.78% of the latest allowances at T_obs are at least 10 base units (`describe/describe.json`). An AWP edge therefore counts transfers and an EndorseRank edge counts approved tokens, each weighted by age. Do, Do and Nguyen (2023) introduce V so that larger transactions weigh more; the registered setting did not do that.
2. **The C-PR layers added incommensurable numbers.** The C-PR allowance layer summed raw allowances over tokens and the transfer layer summed raw transfer amounts over tokens. One USDC is 10⁶ base units and one WETH 10¹⁸, so a layer weight mixed scales that differ by twelve orders of magnitude, and unlimited allowances (2²⁵⁶ − 1, 45.3% of the latest allowances at T_obs) took almost the whole row of every owner that held one.
3. **Every ERC-20 contract counted.** A token contract can emit `Approval` and `Transfer` logs that name any address as owner or sender, without that address taking part; spam and address-poisoning tokens do this. A log of such a token is not evidence that the named owner endorsed the spender or paid the recipient. For widely used tokens with standard implementations, an `Approval` records an allowance that the owner set by calling `approve` or by signing a `permit` (or what is left of it after a `transferFrom`), and a `Transfer` moves a balance the sender held.

The three points are defects of the registered measurement, found after the registered results were known. They are corrected here by valuing every amount in USD and keeping only tokens whose USD price is reliable.

## 2. Status of the two analyses (decision of 10 October 2026)

- The revised analysis is the main analysis of the thesis. Chapter 4 reports it.
- The registered analysis is reported as registered, with the verdicts of rule A, rule B (F1–F6 and its two sensitivity analyses) and R1–R3 exactly as they were obtained, in an appendix and in one table that sets the registered and revised decision contrasts side by side.
- On the revised scores, rules A and B and R1–R3 are applied with the thresholds that were registered (including δ = 0.01). Those results are a re-analysis after the registered results were known, and the thesis says so wherever it reports them.
- Chapter 3 states the deviation, its reasons (section 1) and its date.
- The supervisors have not yet confirmed this decision.

## 3. Token list

A token is listed when all three conditions hold.

1. **A Chainlink market-price feed of low or medium risk.** Chainlink's directory of data feeds on Arbitrum One, read on 10 October 2026 (snapshot in `data/0-usd-token-list-and-prices/sources/`), has a standard market-price feed (product type `RefPrice`) quoted in USD or in ETH whose market-risk category is `low` or `medium`. Chainlink assigns the category from the depth, spread and concentration of the asset's markets; feeds rated `high`, `new` or not rated, exchange-rate and other custom feeds, hidden feeds and feeds scheduled for shutdown do not qualify. An exchange-rate feed reads a conversion rate from a contract and does not follow the market (on 10 October 2026 the USR exchange-rate feed read 1.000 while DefiLlama priced USR at 0.083).
2. **The feed prices this token.** The feed's base asset is the token itself; or the asset that the token wraps one-to-one through its issuer (WETH for ETH); or the Ethereum token of which the token is the copy minted by Arbitrum's canonical token bridge, when that Ethereum token is the asset's own issue (USDC.e for USDC). Tokens issued by other bridges (Axelar, Wormhole, Hyperlane and the like), copies of assets native to another chain, tokens for which the feed prices only an underlying asset (tokenised shares, cbBTC through BTC / USD) and tokens that copy a listed symbol at another address are not listed. Each identification was checked against the issuer's documentation, the Aave address book, the Arbitrum bridge token lists or CoinGecko's platform addresses, and against `symbol()`, `name()` and `decimals()` on the chain.
3. **The token occurs in the observation-window data** (ego transfers or latest allowances at T_obs).

An ETH-quoted feed qualifies a token as a USD-quoted one does (wstETH, weETH, rETH, cbETH); the feeds decide only which tokens are listed, and every listed token's USD price comes from DefiLlama (section 4).

**Selection of five tokens (decision of 10 October 2026, before any revised score was computed).** The three conditions list 64 of the 133 candidates, holding 86.1% of the rows (transfers plus latest allowances at T_obs) of the registered ego data. Eighteen of them, all small (at most 23,211 rows each), have no DefiLlama point under their Arbitrum address on any day, so every event of theirs would be unpriced; 46 have a price and hold 86.09% of the rows. The analysis keeps the **five priced listed tokens with the most rows**: WETH (`0x82af…bab1`), USDC (`0xaf88…5831`), USD₮0 (`0xfd08…cbb9`), ARB (`0x912c…6548`) and WBTC (`0x2f2a…5b0f`). Together they hold 1,186,529,660 rows, 75.75% of the rows of all tokens. All five are priced by Chainlink feeds rated low market risk and are Aave V3 reserves on Arbitrum One. The sixth, bridged USDC.e (71.3 million rows), and every other token are left out. The reason is to weight endorsements and transfers only by the assets whose markets are deepest and hardest to manipulate, so that the USD value of an edge does not depend on a thinly traded token's price; the 64-token list and the prices of all 46 priced tokens stay in `data/0-usd-token-list-and-prices/` with the rule that produced them. `scripts/usd_inputs.py` applies the selection (column `selected`, `TOP_N = 5`), and only the selected tokens are loaded into BigQuery.

Wrapped XRP is not listed. Hex Trust's wXRP is not deployed on Arbitrum One (no code at its address; the issuer lists Ethereum, Optimism, HyperEVM and Solana). The XRP-backed tokens that do exist there are tiny and have no Chainlink feed of their own: uXRP of Universal Protocol (about 25,000 tokens, 11,729 rows of the data) and a canonical-bridge copy of Wrapped.com's Ethereum WXRP (2.13 tokens, 38 rows), whose Ethereum token is itself a custodial wrapper, not XRP.

- Each listed token is recorded in `data/0-usd-token-list-and-prices/listed_tokens.csv` with address, symbol, name, decimals (read with `eth_call` at one pinned block), the feed, its category and the evidence that puts it on the list; `token_candidates.csv` in the same folder lists every token the Chainlink directory mapped to an Arbitrum One address, with the reason it is or is not listed.
- Every other token is left out. The number of tokens and the rows left out are counted per stream and window in `u_describe_tokens` (section 9) and reported; nothing is dropped without being counted.
- Native ETH is not an ERC-20 token and moves without `Transfer` logs (top-level value transfers and internal calls), so the logs used here never contained it. ETH enters the graphs through WETH only, and the thesis states this limitation.

## 4. Prices

- Source: the DefiLlama coins API, daily chart of each listed token by its Arbitrum One address (`coins.llama.fi/chart/arbitrum:<address>`, `period=1d`), fetched once and stored in `data/0-usd-token-list-and-prices/daily_prices_usd.csv` with DefiLlama's confidence value, the key used and the fetch time.
- Day alignment: DefiLlama's daily point is the price record nearest a 00:00 UTC grid time (within about ±2.4 hours). The point nearest 00:00 UTC of day D+1 is the closing price of day D, and it is the price of day D.
- Second key: for several canonical tokens DefiLlama's Arbitrum series starts long after the token's first use (WETH on 16 August 2024, USD₮0 on 24 January 2025). A day without a point under the Arbitrum key takes the point of a second DefiLlama key for the same asset (`coingecko:<id>` or the asset's Ethereum address), provided that on the days both keys have a point their median absolute relative difference is below 1%. The key of every day is recorded.
- Errors: a daily point that is more than twice, or less than half, both the previous and the next day's point, while those two lie within a factor of two of each other, is treated as a data error, replaced by the previous day's price and flagged.
- Gaps: a day still without a price takes the previous day's price (`filled`); filled days are counted per token. No price is carried backwards before a token's first point; an event on such a day has no price and is counted.
- Check: for a sample of tokens and dates the DefiLlama price is compared with the Chainlink feed on Arbitrum One read on-chain (`scripts/chainlink_check.py`); the differences are reported in the appendix. A scouting run before this file was written found median absolute differences of 0.01–0.04% and at most 0.56% for ETH and USDC on 37 dates.
- A transfer is valued at the price of its UTC day. A latest allowance is valued at the price of the anchor's UTC day (30 June 2026 at T_obs, 31 March 2026 at t1), since it is the permission in force at the anchor that the edge represents.
- USD value = raw value / 10^decimals × price, in double precision (`scripts/usd.py`, mirrored in SQL).

## 5. Amount weights

- EndorseRank and AWP keep V(z) = 2/(1+exp(−bz)) − 1, now with z in USD. The slope is set so that V of the median amount is one half: b = ln 3 / m. m_T is the median USD value of the ego transfers of the selected tokens from 1 October 2023 to t1, and m_A the median USD value at t1 prices of the finite latest allowances at t1 (below 1.15 × 10⁷⁷ base units). Both use only events up to t1 = 31 March 2026, the earlier freeze, so no label window enters them. The medians are computed by `sql/13_usd_constants.sql` (BigQuery `APPROX_QUANTILES`, 10,000 buckets) and rounded to two significant digits; b is computed from the rounded value.
- An unlimited allowance has V = 1, the most an approval can weigh.
- C-PR transfer layer: Σ_e usd_e · σ(Δt_e), the registered form with USD in place of base units.
- C-PR allowance layer: Σ_token min(usd, U), where U is the 99th percentile of the USD values of the ego transfers of the selected tokens up to t1, rounded to two significant digits (`sql/13_usd_constants.sql`). Every allowance at or above U counts U, so an unlimited allowance, and any allowance too large to be spent, weighs as much as an allowance of the size that 99% of transfers do not exceed, instead of taking the owner's whole row. The number of allowances at or above U is reported.
  - *Amendment of 10 October 2026, made after the constants were computed and before any revised score:* this file first defined U as the 99th percentile of the finite positive latest allowances at t1 (below 1.15 × 10⁷⁷ base units). On the five tokens that percentile is about 10⁴⁷ USD: of the 11,982,356 positive latest allowances at t1, 5,490,386 are exactly unlimited and a further 702,599 are below that threshold but above 10⁹ USD (values such as 2²⁵⁵ or 2¹²⁸), so the 'finite' set is itself dominated by allowances that are unlimited in effect, and a cap at its 99th percentile would leave them in charge of every owner's row. Allowances split into amounts below about 10⁶ USD and amounts above 10⁹ USD, while single transfers have a median of about 204 USD, a 99th percentile of about 20,320 USD and a largest value of about 10⁸ USD up to t1. The transfer percentile measures what accounts actually move, so it replaces the allowance percentile. The medians m_T and m_A are unchanged.
- S-PR walks the USD transfer layer with restarts from C-PR (λ = 1) on the USD allowance layer.
- Proxies: in-value is the USD sum of inbound transfers; in-approve value is the spender's sum of the C-PR allowance layer weights.

## 6. Scope

Every quantity is restricted to the five selected tokens:

- Matched cohort: contracts that, inside the observation window, received a non-zero `Approval` of a selected token from at least three distinct owners. Such a contract received non-zero approvals from three owners on some token, so it is a member of the registered cohort; its account type is already known, and no new `eth_getCode` read is needed.
- Graphs: approvals and transfers of the selected tokens with a contract of the revised cohort as owner, spender, sender or recipient. These events are a subset of the registered ego tables, which hold every event touching a registered cohort contract; no public log is scanned again.
- Spender cohorts of W0 and W1: contract spenders with a positive latest allowance of a selected token at the freeze in the revised approval data (a subset of the registered spender cohorts, whose account types are known).
- Trader cohort: as registered (GMX V2 contract accounts with at least three closes in the window), with membership in the revised freeze-date graph.
- Labels: new approval pairs, new transfer senders, revocations and the drain heuristic count events of the selected tokens only. The GMX trader labels do not depend on tokens and are unchanged.

## 7. Unchanged

Windows and anchors, the logistic decay (k = 0.01, t0 = 180 days), the solver (d = 0.85, tolerance 10⁻⁸, at most 300 iterations, dangling mass through the restarts), restarts of each method, λ values, the raw degree baselines (now counted on selected tokens), the statistics (Kendall τ_b, Spearman ρ, 400 paired bootstrap resamples with seed 42, 2,000 for the outcome comparison), the decision thresholds of rules A and B and R1–R3, the benchmark protocol and the Sybil model.

## 8. Robustness

The top-20-token subgraph check of the plan (section 5) loses its point once every graph keeps only selected tokens. It is replaced by a check of the new free parameter: EndorseRank and AWP are recomputed at T_obs with the slope b multiplied and divided by ten (the edge weights come from the same query as the main weights), and their family means on the matched cohort and their rank agreement with the main scores are reported without intervals, as the token check was. The damping sweep, the isolated-node rule and the sample-definition stages are unchanged.

The registered analysis keeps its top-20-token check as registered.

## 9. Execution

Inputs: `scripts/usd_inputs.py` applies the rule of section 3 to the Chainlink directory snapshot and the reviewed candidate table, reads symbol, name and decimals at one pinned block, fetches and builds the daily prices of section 4 and writes `data/0-usd-token-list-and-prices/`; `scripts/chainlink_check.py` writes the Chainlink comparison.

BigQuery (each query dry-run first by `scripts/run_bq.py`, all within the study's USD 50 budget; `scripts/run_usd_pipeline.py` runs the steps in order):

1. Load `u_tokens` and `u_prices` from the CSV files (load jobs are not billed).
2. `sql/12_usd_ego.sql`: revised cohort and selected-token ego tables (`u_cohort`, `u_approvals`, `u_transfers`, `u_approvals_w1`, `u_transfers_w1`).
3. `sql/13_usd_constants.sql`: medians and quantiles up to t1 (`u_constants`).
4. `sql/14_usd_anchor_pairs.sql` at T_obs and t1.
5. `sql/15_usd_proxies.sql`; `sql/16_usd_labels.sql` for W0 and W1; `sql/17_usd_export_ids.sql`; `sql/18_usd_describe.sql`.
6. Download the `u_x_*`, `u_proxies_tobs` and `u_labels_*` tables into `data/1-raw-blockchain-extracts/graph-tables-usd/`.

Locally, with `CONTRACT_REP_VARIANT=usd` (outputs under `data/2-processed-tables-and-evaluations/revised-usd/` and `data/3-published-results-for-thesis/revised-usd/`): `run_same_window.py`, `run_holdout.py`, `run_registered.py`, `run_robustness.py`, `run_benchmark.py`, `run_supplementary.py`, `sybil_model.py`, the descriptive summary, `publish_results.py`, `export_latex.py`.
````
