#!/usr/bin/env python3
"""Neutral-label analysis fixed in analysis/neutral-label/PLAN.md (pre-specified, post hoc).

Compares allowance-side and transfer-side scores, like with like, on the six GMX V2
trader labels of the registered June-August 2026 window (W1) and of the spring window
(W0). Run from anywhere with the phd_works experiments folder as --experiments:

    python neutral_label_analysis.py --experiments /path/to/wallet-reputation-experiments

Writes results.json next to this file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau

HERE = Path(__file__).resolve().parent

LABELS = (
    "future_liquidation_free_rate",
    "future_zero_liquidation",
    "close_success_count",
    "realized_gain_proxy",
    "close_success_rate",
    "non_loss_close_rate",
)
PRIMARY_LABEL = "future_liquidation_free_rate"

METHODS = (
    "t1_in_approve_degree",
    "t1_in_degree",
    "endorserank_vt_activity",
    "awp_paper",
    "endorserank_vt",
    "endorserank",  # C-PR lambda=1 (raw-amount allowance layer)
    "awp",  # C-PR lambda=0 (raw-amount transfer layer)
    "coupled_pr",  # C-PR lambda=0.5
)

# (id, a, b, role)
CONTRASTS = (
    ("P", "t1_in_approve_degree", "t1_in_degree", "decision"),
    ("Q", "endorserank_vt_activity", "awp_paper", "decision"),
    ("L1-L0", "endorserank", "awp", "reported"),
    ("ER-AWP", "endorserank_vt", "awp_paper", "reported"),
    ("L0-AWP", "awp", "awp_paper", "decomposition"),
    ("ER-deg", "endorserank_vt", "t1_in_approve_degree", "unfavourable"),
    ("CPR-deg", "coupled_pr", "t1_in_approve_degree", "unfavourable"),
)

STRATA = ((3, 4), (5, 9), (10, 24), (25, 10**9))
N_BOOT = 2000
SEED = 42


def tau(x: np.ndarray, y: np.ndarray) -> float:
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        return float("nan")
    t, _ = kendalltau(x, y)
    return float(t) if t is not None else float("nan")


def stratified_tau(x: np.ndarray, y: np.ndarray, closes: np.ndarray) -> float:
    num = 0.0
    den = 0.0
    for lo, hi in STRATA:
        m = (closes >= lo) & (closes <= hi)
        n_s = int(m.sum())
        if n_s < 5:
            continue
        t = tau(x[m], y[m])
        if not np.isfinite(t):
            continue
        w = n_s * (n_s - 1) / 2.0
        num += w * t
        den += w
    return num / den if den > 0 else float("nan")


def ci(arr: list[float], level: float) -> tuple[float | None, float | None]:
    a = np.asarray([v for v in arr if np.isfinite(v)], dtype=float)
    if a.size < 20:
        return None, None
    alpha = (1.0 - level) / 2.0
    return float(np.quantile(a, alpha)), float(np.quantile(a, 1.0 - alpha))


def contrast_grid(frame: pd.DataFrame, stratify: bool) -> dict:
    """Paired bootstrap for every contrast on every label, shared resamples per label."""
    out: dict = {}
    for label in LABELS:
        if label not in frame.columns:
            continue
        cols = [f"{m}_score" for m in METHODS]
        sub = frame[[*cols, label, "future_close_count"]].dropna()
        n = len(sub)
        y = sub[label].to_numpy(float)
        closes = sub["future_close_count"].to_numpy(float)
        X = {m: sub[f"{m}_score"].to_numpy(float) for m in METHODS}
        stat = (lambda x, yy, cc: stratified_tau(x, yy, cc)) if stratify else (lambda x, yy, cc: tau(x, yy))
        point = {m: stat(X[m], y, closes) for m in METHODS}
        rng = np.random.default_rng(SEED)
        boots: dict[str, list[float]] = {m: [] for m in METHODS}
        for _ in range(N_BOOT):
            idx = rng.integers(0, n, n)
            for m in METHODS:
                boots[m].append(stat(X[m][idx], y[idx], closes[idx]))
        bm = {m: np.asarray(v, float) for m, v in boots.items()}
        rows = {}
        for cid, a, b, role in CONTRASTS:
            d = bm[a] - bm[b]
            lo95, hi95 = ci(list(d), 0.95)
            lo975, hi975 = ci(list(d), 0.975)
            rows[cid] = {
                "a": a,
                "b": b,
                "role": role,
                "tau_a": point[a],
                "tau_b": point[b],
                "delta": point[a] - point[b],
                "ci95": [lo95, hi95],
                "ci975": [lo975, hi975],
                "share_positive": float(np.mean(d[np.isfinite(d)] > 0)),
            }
        method_ci = {m: {"tau": point[m], "ci95": list(ci(list(bm[m]), 0.95))} for m in METHODS}
        out[label] = {"n": n, "methods": method_ci, "contrasts": rows}
    return out


def recipients_block(frame: pd.DataFrame, account_types: pd.DataFrame) -> dict:
    lab = frame[frame[PRIMARY_LABEL].notna()].copy()
    lab["recipient"] = lab["t1_in_approve_degree_score"] > 0
    k = int(lab["recipient"].sum())
    acct = account_types.set_index("wallet")["account_class"].to_dict()
    lab["account_class"] = lab["wallet"].map(acct).fillna("unknown")
    rec = lab[lab["recipient"]]
    cross = rec["account_class"].value_counts().to_dict()

    def group_stats(g: pd.DataFrame) -> dict:
        return {
            "n": int(len(g)),
            "zero_liquidation_share": float(g["future_zero_liquidation"].mean()),
            "mean_lfcr": float(g[PRIMARY_LABEL].mean()),
            "mean_profitable_share": float(g["close_success_rate"].mean()),
            "mean_non_loss_share": float(g["non_loss_close_rate"].mean()),
            "median_closes": float(g["future_close_count"].median()),
        }

    rng = np.random.default_rng(SEED)
    r = lab["recipient"].to_numpy(bool)
    z = lab["future_zero_liquidation"].to_numpy(float)
    rd_point = float(z[r].mean() - z[~r].mean()) if k > 0 else float("nan")
    rds = []
    n = len(lab)
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, n)
        rr, zz = r[idx], z[idx]
        if rr.sum() == 0 or (~rr).sum() == 0:
            continue
        rds.append(float(zz[rr].mean() - zz[~rr].mean()))
    lo, hi = ci(rds, 0.95)

    def p_on(sub: pd.DataFrame) -> dict:
        s = sub[["t1_in_approve_degree_score", "t1_in_degree_score", PRIMARY_LABEL]].dropna()
        a = s["t1_in_approve_degree_score"].to_numpy(float)
        b = s["t1_in_degree_score"].to_numpy(float)
        y = s[PRIMARY_LABEL].to_numpy(float)
        rng2 = np.random.default_rng(SEED)
        ds = []
        for _ in range(N_BOOT):
            idx = rng2.integers(0, len(y), len(y))
            ds.append(tau(a[idx], y[idx]) - tau(b[idx], y[idx]))
        lo2, hi2 = ci(ds, 0.95)
        return {"n": int(len(s)), "tau_a": tau(a, y), "tau_b": tau(b, y), "delta": tau(a, y) - tau(b, y), "ci95": [lo2, hi2]}

    eoa_mask = (~lab["recipient"]) | (lab["account_class"] == "eoa")
    k_eoa = int((lab["recipient"] & (lab["account_class"] == "eoa")).sum())
    top10 = rec.sort_values("t1_in_approve_degree_score", ascending=False).head(10)["wallet"]
    return {
        "k_recipients": k,
        "n_labelled": int(n),
        "recipient_account_classes": cross,
        "k_eoa": k_eoa,
        "recipients": group_stats(rec),
        "non_recipients": group_stats(lab[~lab["recipient"]]),
        "zero_liquidation_risk_difference": {"point": rd_point, "ci95": [lo, hi]},
        "P_eoa_only": p_on(lab[eoa_mask]) if k_eoa >= 30 else {"skipped": True, "k_eoa": k_eoa},
        "P_without_top10_recipients": p_on(lab[~lab["wallet"].isin(top10)]),
        "in_approve_degree_distribution_recipients": rec["t1_in_approve_degree_score"].describe().to_dict(),
    }


def build_w1(exp: Path) -> pd.DataFrame:
    sys.path.insert(0, str(exp / "scripts"))
    from common import load_config
    from fresh_holdout import build_cohort_frame, combine_events, load_fresh_events, load_registration, load_spring_events, window_config
    from holdout import holdout_bounds, latest_positive_as_of, score_endorserank_vt
    from run_fresh_posthoc import _add_scores, _matched_wallets

    config = load_config()
    reg = load_registration()
    cfg = window_config(config, reg)
    score_end, _, _ = holdout_bounds(cfg)
    spring = load_spring_events(config)
    fresh = load_fresh_events(reg)
    events = {k: combine_events(spring[k], fresh[k]) for k in ("approvals", "transfers", "decoded")}
    latest_t1 = latest_positive_as_of(events["approvals"], score_end)
    merged, _, _ = build_cohort_frame(cfg, events, "traders", _matched_wallets(config))
    wallets = merged["wallet"].tolist()
    return _add_scores(
        merged,
        {
            "endorserank_vt": score_endorserank_vt(latest_t1, score_end, wallets, cfg),
            "endorserank_vt_activity": score_endorserank_vt(latest_t1, score_end, wallets, cfg, activity_restarts=True),
        },
    )


def build_w0(exp: Path) -> pd.DataFrame:
    from common import load_config
    from fresh_holdout import build_cohort_frame, load_spring_events
    from holdout import holdout_bounds, latest_positive_as_of, score_endorserank_vt
    from run_fresh_posthoc import _add_scores, _matched_wallets

    config = load_config()
    score_end, _, _ = holdout_bounds(config)
    events = load_spring_events(config)
    latest_t1 = latest_positive_as_of(events["approvals"], score_end)
    merged, _, _ = build_cohort_frame(config, events, "traders", _matched_wallets(config))
    wallets = merged["wallet"].tolist()
    return _add_scores(
        merged,
        {
            "endorserank_vt": score_endorserank_vt(latest_t1, score_end, wallets, config),
            "endorserank_vt_activity": score_endorserank_vt(latest_t1, score_end, wallets, config, activity_restarts=True),
        },
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiments", required=True, type=Path)
    args = ap.parse_args()
    exp = args.experiments.resolve()
    import os

    os.chdir(exp)
    account_types = pd.read_csv(
        exp / "data/2-processed-tables-and-evaluations/spring-holdout-2026-03-to-2026-05/spender_account_types.csv"
    )
    account_types["wallet"] = account_types["wallet"].str.lower()

    report: dict = {"plan": "analysis/neutral-label/PLAN.md", "n_boot": N_BOOT, "seed": SEED, "windows": {}}
    for name, builder in (("W1_registered_jun_aug_2026", build_w1), ("W0_spring_mar_may_2026", build_w0)):
        frame = builder(exp)
        frame.to_parquet(HERE / f"frame_{name}.parquet")
        block = {
            "n_cohort": int(len(frame)),
            "plain": contrast_grid(frame, stratify=False),
            "stratified_by_closes": {PRIMARY_LABEL: contrast_grid(frame, stratify=True)[PRIMARY_LABEL]},
            "recipients": recipients_block(frame, account_types),
        }
        report["windows"][name] = block
        print(f"== {name}: cohort {len(frame)}")
        for label, res in block["plain"].items():
            print(f"  {label} (n={res['n']})")
            for cid, row in res["contrasts"].items():
                print(
                    f"    {cid:8s} {row['tau_a']:+.3f} vs {row['tau_b']:+.3f}  d={row['delta']:+.3f} "
                    f"95%[{row['ci95'][0]:+.3f},{row['ci95'][1]:+.3f}] 97.5%[{row['ci975'][0]:+.3f},{row['ci975'][1]:+.3f}]"
                )
        st = block["stratified_by_closes"][PRIMARY_LABEL]["contrasts"]
        for cid in ("P", "Q", "L1-L0", "ER-AWP"):
            row = st[cid]
            print(f"  stratified {cid}: d={row['delta']:+.3f} 95%[{row['ci95'][0]:+.3f},{row['ci95'][1]:+.3f}]")
        print("  recipients:", json.dumps(block["recipients"], default=str)[:1500])
    (HERE / "results.json").write_text(json.dumps(report, indent=1, default=float))
    print("wrote", HERE / "results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
