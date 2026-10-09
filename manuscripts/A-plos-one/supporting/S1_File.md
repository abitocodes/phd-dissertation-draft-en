# Neutral-label analysis: plan and claim ledger (fixed before computation)

Written and committed on 2026-10-09, **before** any of the analyses below were run.
The registered June–August 2026 labels and the published coefficients in
`results/tables/` (fresh-holdout, fresh-traders, fresh-posthoc, endorserank-awp-holdout,
holdout-traders, alignment-liquidation) were already known when this plan was written.
Everything here is therefore a **pre-specified post hoc analysis of existing data**, not a
registration. The thesis must label it that way.

The only check run before this commit was a reproduction of the already-published
post hoc EndorseRank run (`scripts/run_fresh_posthoc.py` in `abitocodes/phd_works`,
commit `71299818af9b47059279f73b7fa691967420d395`), which returned the published values
(in-approve degree 0.144, transfer in-degree −0.006, EndorseRank 0.081, AWP 0.045 on the
liquidation-free close rate; EndorseRank − AWP +0.035 [−0.017, 0.087]).

## Question

On outcomes built from neither edge type (GMX V2 trader outcomes), measured after the
scores were frozen, does allowance-edge information rank traders better than
transfer-edge information, comparing like with like?

## Data and cohorts

- **Registered window (W1):** scores frozen 2026-05-31 23:59:59 UTC, labels 2026-06-01 to
  2026-08-31, trader cohort and label definitions exactly as in `fresh_holdout.py`
  (`build_cohort_frame`, `min_closes = 3`; n = 1,402 for the GMX labels).
- **Spring window (W0):** scores frozen 2026-02-28 23:59:59 UTC, labels 2026-03-01 to
  2026-05-31, matched traders, same label code. The score–label associations for the
  liquidation labels in W0 have never been computed (Ch3: "It has no GMX liquidation
  label"). Known beforehand and unfavourable to the allowance side: the same-window
  Dec–May liquidation-free rate favoured the raw-amount transfer layer (0.083 vs 0.075).

## Scores (method IDs in phd_works)

| Role | Allowance side | Transfer side |
|---|---|---|
| Count | `t1_in_approve_degree` | `t1_in_degree` |
| Like-for-like PageRank (same σ·V weights, activity restarts, d = 0.85) | `endorserank_vt_activity` | `awp_paper` (AWP) |
| Thesis PageRank pair (restarts differ) | `endorserank_vt` (EndorseRank) | `awp_paper` (AWP) |
| Same raw-amount build, uniform restarts | `endorserank` (= C-PR λ=1) | `awp` (= C-PR λ=0) |

Decomposition row: C-PR(λ=0) − AWP (weighting and restart effect only).
Unfavourable rows: EndorseRank − in-approve degree; C-PR(λ=0.5) − in-approve degree.

## Labels (all six registered trader labels, all reported)

`future_liquidation_free_rate` (LFCR, primary), `future_zero_liquidation`,
`close_success_count`, `realized_gain_proxy`, `close_success_rate` (profitable share),
`non_loss_close_rate`.

## Contrasts and inference

- **P (primary):** in-approve degree − transfer in-degree on LFCR in W1.
- **Q (PageRank, decision):** EndorseRank(activity restarts) − AWP on LFCR in W1.
- **Reported, not decisive:** λ1 − λ0; EndorseRank − AWP; λ0 − AWP; the unfavourable rows;
  P, Q and the reported contrasts on the other five labels; all of the above in W0.
- Paired wallet bootstrap, **B = 2,000**, seed 42, percentile intervals. The decision family
  {P, Q} uses **Bonferroni 97.5 %** intervals; every row also shows the 95 % interval.
  B = 400 results are reproduced for continuity only.
- **Stratification:** Kendall τ_b within strata of the number of label-window closes
  {3–4, 5–9, 10–24, ≥25}, combined with weights proportional to the number of wallet pairs
  in each stratum; same bootstrap resamples.
- **Recipients:** k = number of labelled traders with in-approve degree > 0 at the freeze;
  2×2 table of recipient × zero-liquidation flag with risk difference and bootstrap 95 % CI;
  group means of LFCR, profitable share, non-loss share and median closes.
- **Account type:** recipients cross-tabulated with
  `spring-holdout-2026-03-to-2026-05/spender_account_types.csv` (contract / EOA / unknown).
  P on EOA-only traders (recipients restricted to EOAs, non-recipients kept) if k_EOA ≥ 30;
  otherwise descriptive only.
- **Influence:** P after dropping the 10 recipients with the highest in-approve degree.

## Decision rules

- **R1 — count-level lead on liquidation avoidance (post hoc):** all of
  (a) P's 97.5 % interval lies above 0 in W1;
  (b) the stratified P's 95 % interval lies above 0 in W1;
  (c) P's point estimate is above 0 in W0;
  (d) if k_EOA ≥ 30, the EOA-only P point estimate is above 0.
- **R2 — PageRank-level lead:** Q's 97.5 % interval lies above 0 in W1 **and** Q's point
  estimate is above 0 in W0.
- **R3 — scope:** if P is below 0 with its 95 % interval excluding 0 on profitable share or
  non-loss share (W1), the thesis must say the allowance signal is specific to
  liquidation avoidance and runs against loss avoidance.

## Claim ledger (sentences the thesis may use, fixed now)

- **R1 and R2 hold:** "On the trader outcome built from neither edge type, later
  liquidation avoidance, allowance-edge information ranked traders above transfer-edge
  information both as raw counts and as like-for-like PageRanks; the count-level lead
  survives stratification by the number of closes and points the same way in the spring
  window. These are pre-specified post hoc analyses of existing data."
- **R1 holds, R2 fails:** "On the one trader outcome built from neither edge type, later
  liquidation avoidance, the approval count at the freeze ranked traders above the transfer
  count (Δτ = …, 97.5 % CI …); the lead survives stratification by the number of closes and
  points the same way in the spring window (post hoc). The PageRank versions point the same
  way but are not resolved (…)."
- **R1 fails:** "The marginal difference between the approval and transfer counts on
  liquidation avoidance did not survive [pairing / stratification / the spring window];
  the thesis makes no claim that either edge type ranks liquidation avoidance better."
- **Account type, if most recipients are contracts or k_EOA < 30:** "Most approval-receiving
  traders are contract accounts, so account type is an unresolved confound of this
  signal."
- **R3 triggered:** "The same signal is lower on the share of closes that were profitable or
  not losing, so the construct it ranks is forced-liquidation avoidance, not trading
  success."
- In every case: the registered rule for C-PR stays **not met**; F4 is reported only as a
  pre-specified secondary result; no new research question is added; the title stays a
  statement of purpose and the abstract states the answers.
