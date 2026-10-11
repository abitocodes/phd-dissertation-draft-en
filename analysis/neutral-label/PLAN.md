# Comparison on trader outcomes built from neither edge type: pre-specified rules

The comparison of allowance-side with transfer-side scores on GMX V2 contract traders, its decision contrasts P and Q and its rules R1–R3 were fixed in the W1 registration of the experiment repository `phd_works`. They are not fixed in this folder, and nothing here computes them: the pipeline computes every value (`scripts/run_registered.py`, function `neutral`), and `export_neutral_label.py` copies the values into `results.json` and checks them against the per-contract trader score files. The analysis plan (`docs/analysis_plan.md`, commit `43d8045`, section 7) leaves this comparison to the registration, and R1–R3 are defined nowhere else.

## Registration document

| Item | Value |
|---|---|
| File | `docs/registration_w1.md` of the experiment folder (at the commit `1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments/`, now `1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments/`), lines 11–12 and 31–49 quoted below |
| Commit | `0d3a057e4f0c8473d36d89fbe33c24deff0c9911`, 2026-10-09 16:49:32 UTC; the file is unchanged since |
| SHA-256 in the extraction manifest | `2126c8dc3fe3c0f9273aa4ecfc1e15bddc1f5a6f65e98548b9528f2b18ca2a6b` (`data/3-published-results-for-thesis/registered-w1/extraction_manifest.json`, key `sha256`). The manifest hashed a Windows checkout with CRLF line ends; the same text with LF line ends, as git stores it, hashes to `34cd6dfeb56b8fb8a553cb24afbff06c6a94e6f69a2eb7f7d642b0cc39e54b2c` |
| W1 extraction | `scripts/extract_w1.py` started at 2026-10-09 16:49:33 UTC and finished at 16:50:55 UTC (manifest keys `started_at`, `finished_at`; `override_used: false`) |

`export_neutral_label.py` verifies both hashes and that every line of the quotes below occurs verbatim in the documents.

Trader cohort and label (section 1 of the registration):

```text
- Trader cohort: GMX V2 accounts that hold contract code, are nodes of the freeze-date graph (either layer), and close at least three positions in the label window. Label: the liquidation-free close rate, one minus the share of the account's closes in the window that were liquidations.
- Methods, solver settings, SQL and bootstrap (400 paired resamples, seed 42) are those of the analysis plan.
```

Section 3 of the registration, complete:

```text
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
```

Every contrast and every single-score τ of this comparison uses 2,000 paired resamples (seed 42), the number that section 3 fixes for the decision contrasts; the 400 resamples of line 12 are those of rule B and of the spender analyses.

## Application to the revised analysis

The revised analysis (amounts in USD over WETH, USDC, USDT0, ARB and WBTC) was decided after the registered results were known and committed before any revised score was computed: `a897475` (2026-10-10 07:54:35 UTC), `09dfc32` (08:12:44 UTC) and `2705b28` (11:24:01 UTC). Lines 18–19 of `docs/revision_price_weighting.md`, present since `a897475`:

```text
- The registered analysis is reported as registered, with the verdicts of rule A, rule B (F1–F6 and its two sensitivity analyses) and R1–R3 exactly as they were obtained, in an appendix and in one table that sets the registered and revised decision contrasts side by side.
- On the revised scores, rules A and B and R1–R3 are applied with the thresholds that were registered (including δ = 0.01). Those results are a re-analysis after the registered results were known, and the thesis says so wherever it reports them.
```

The revised results of this comparison are therefore a re-analysis with the registered rules and thresholds, never registered results. The thesis reports them as its main results (Chapter 4) and the registered ones in Appendix 8.6 (Table `registered-vs-revised`).

## What was fixed before the labels were known, and what was not

- Registered analysis, W1. The registration and the evaluation code (`scripts/run_registered.py`) were committed together in `0d3a057`, before the July–September logs were extracted; the code of that file has not changed since except for its input and output paths (`a897475`). The six pairs (`NEUTRAL_PAIRS`), the 97.5% intervals of P and Q, the stratified contrasts, the recipient comparison, the influence check and the rules R1–R3 were therefore all computed by code written before the W1 labels existed.
- Registered analysis, W0. The registration states that the W0 liquidation labels had not been computed for any score. The holdout code committed in the same commit (`scripts/run_holdout.py`) scores the same W0 trader contracts on the four profit labels (profitable closes, realized gain, profitable share, non-loss share) in an exploratory run and leaves the liquidation labels to the registered analysis, so the W0 profit-label coefficients may have been seen before the registration.
- Not named in the registration document, though fixed in the code of `0d3a057`: the pair EndorseRank minus in-approve degree (`er_degree`) and the τ of each single score with its 95% interval. The stratified Q is computed with the stratified P, but only the stratified P enters a rule (R1). Only P and Q on the liquidation-free close rate have 97.5% intervals; every other contrast has a 95% interval.
- Revised analysis, both windows. Every revised value, including the verdicts of R1–R3, was computed after all registered results, the W1 trader labels included, were known. The code is the same file, run with `CONTRACT_REP_VARIANT=usd`. The trader labels do not depend on the token weighting (GMX closes enter neither graph); `export_neutral_label.py` checks that the label columns of the trader score files are identical in the two analyses.
- `results.json` adds no statistic. Its `recompute_check` block recomputes the published values from the trader score files with an independent implementation of τ_b and of the paired bootstrap; it is a check of the copy, not a new result.
