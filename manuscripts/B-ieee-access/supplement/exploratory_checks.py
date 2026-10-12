#!/usr/bin/env python3
"""Exploratory checks for Manuscript B (IEEE Access), run on 11 October 2026.

Every result of both analyses (registered and revised) was known when this script was
written, so nothing here enters a decision rule and nothing here was fixed in advance.
The script reads only the per-contract score files and the published evaluation
summaries of the experiment pipeline in the authors' repository ``phd_works``; it builds
no graph and computes no new score. It does four things.

1. ``recompute``: recomputes the decision contrasts of rule A (W0) and rule B (W1, with
   F4-F6 and the first sensitivity analysis) from the score files, with the pipeline's
   resampling (400 paired resamples drawn by ``numpy.random.default_rng(42)`` over the
   cohort sorted by contract id) and SciPy's tau_b, and compares every value with the
   published summary. The second sensitivity analysis (isolated nodes) cannot be
   recomputed: its single-layer scores are not in the score files.
2. ``seed_spread``: repeats the five decision contrasts (A1, A2, F1, F2, F3) with 50
   further seeds (43-92) of 400 resamples and reports how far the interval ends move and
   whether any verdict changes.
3. ``lambda_steps``: paired contrasts between neighbouring values of the coupling weight
   (0, 0.25, 0.5, 0.75, 1) and between 0.25 and 0.75, on every label, seed 42.
4. ``lambda_rank_agreement``: Kendall tau_b between the C-PR score vectors at two values
   of the weight over each cohort, with paired-bootstrap intervals (seed 42).

    python exploratory_checks.py --phd-works /path/to/phd_works      # or set PHD_WORKS

Writes exploratory_checks.json next to this file. About eight minutes on four cores.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
from scipy.stats import kendalltau

HERE = Path(__file__).resolve().parent
N_BOOT = 400
SEED = 42
EXTRA_SEEDS = list(range(43, 93))
DELTA = 0.01  # margin of rule B, docs/registration_w1.md section 2
APPR = "future_new_approvers"
SEND = "future_new_transfer_senders"
LIQ = "liquidation_free_rate"
LAMBDA_COLS = {0.0: "cpr_l0", 0.25: "cpr_l25", 0.5: "cpr_l50", 0.75: "cpr_l75", 1.0: "cpr_l100"}
PROJECTS = ("ERC20-Allowance-PageRank-Wallet-Reputation", "ERC20-Allowance-PageRank-Contract-Reputation")

# Score files (data/2-processed-tables-and-evaluations/...) and published summaries
# (data/3-published-results-for-thesis/...) of each analysis.
ANALYSES = {
    "registered": {
        "proc": "2-processed-tables-and-evaluations",
        "pub": "3-published-results-for-thesis",
        "w0": "holdout-w0",
        "w1": "registered-w1",
        "same": "same-window",
    },
    "revised": {
        "proc": "2-processed-tables-and-evaluations/revised-usd",
        "pub": "3-published-results-for-thesis/revised-usd",
        "w0": "holdout-w0",
        "w1": "window-w1",
        "same": "same-window",
    },
}

# name, cohort, score a, score b, label, test, where the published value lives
DECISION = [
    ("A1", "w0_spenders", "cpr_l50", "cpr_l100", APPR, "no_worse", ("w0", "contrasts_prefixed", 0)),
    ("A2", "w0_spenders", "cpr_l50", "cpr_l0", SEND, "superiority", ("w0", "contrasts_prefixed", 1)),
    ("F1", "w1_spenders", "cpr_l50", "cpr_l0", APPR, "superiority", ("w1", "rule_b", "F1")),
    ("F2", "w1_spenders", "cpr_l50", "cpr_l0", SEND, "non_inferiority", ("w1", "rule_b", "F2")),
    ("F3", "w1_traders", "cpr_l50", "cpr_l0", LIQ, "non_inferiority", ("w1", "rule_b", "F3")),
]
BESIDE = [
    ("F4", "w1_traders", "cpr_l50", "cpr_l0", LIQ, "superiority", ("w1", "rule_b", "F4")),
    ("F5", "w1_traders", "cpr_l50", "cpr_l100", LIQ, "superiority", ("w1", "rule_b", "F5")),
    ("F6a", "w1_spenders", "cpr_l50", "cpr_l100", APPR, "no_worse", ("w1", "rule_b", "F6a")),
    ("F6b", "w1_spenders", "cpr_l50", "cpr_l0", SEND, "superiority", ("w1", "rule_b", "F6b")),
    ("S1-F1", "w1_spenders", "cpr_l50", "awp", APPR, "superiority", ("w1", "sensitivity_awp", "F1")),
    ("S1-F2", "w1_spenders", "cpr_l50", "awp", SEND, "non_inferiority", ("w1", "sensitivity_awp", "F2")),
    ("S1-F3", "w1_traders", "cpr_l50", "awp", LIQ, "non_inferiority", ("w1", "sensitivity_awp", "F3")),
    ("W0 C-PR minus C-PR(0), new approval pairs", "w0_spenders", "cpr_l50", "cpr_l0", APPR, "none",
     ("w0", "contrasts_after", 5)),
]
COHORT_LABELS = {"w0_spenders": [APPR, SEND], "w1_spenders": [APPR, SEND], "w1_traders": [LIQ]}


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def experiments_dir(phd_works: Path) -> Path:
    for p in PROJECTS:
        d = phd_works / "1-Dissertation-Works" / p / "experiments"
        if (d / "data" / "3-published-results-for-thesis" / "results_digest.md").exists():
            return d
    raise SystemExit(f"no experiments folder with published results under {phd_works}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def head_commit(repo: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def read_parts(folder: Path, stem: str) -> pd.DataFrame:
    parts = sorted(folder.glob(f"{stem}.part*.parquet"))
    if not parts:
        raise SystemExit(f"missing {folder}/{stem}.part*.parquet")
    return pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)


# ---------------------------------------------------------------------------
# Statistics (as in experiments/scripts/stats.py)
# ---------------------------------------------------------------------------


def dense(x: np.ndarray) -> np.ndarray:
    values, inverse = np.unique(x, return_inverse=True)
    return inverse.astype(np.int16 if values.size < 2**15 else np.int32)


def tau(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 5 or x.min() == x.max() or y.min() == y.max():
        return float("nan")
    t = kendalltau(x, y).statistic
    return float(t) if np.isfinite(t) else float("nan")


def resample_matrix(n: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, n, size=(N_BOOT, n))


def taus_on(x: np.ndarray, y: np.ndarray, idx: np.ndarray) -> np.ndarray:
    """tau_b on every resample; NaN where the pipeline would skip the resample."""
    rx, ry = dense(x), dense(y)
    return np.array([tau(rx[row], ry[row]) for row in idx])


def pct(a: np.ndarray, q: float) -> float:
    return float(np.percentile(a, q))


def contrast(sa: np.ndarray, sb: np.ndarray, pa: float, pb: float, ci: float = 0.95) -> dict:
    ok = np.isfinite(sa) & np.isfinite(sb)
    d = sa[ok] - sb[ok]
    lo, hi = (1 - ci) / 2 * 100, (1 + ci) / 2 * 100
    return {"a_tau": pa, "b_tau": pb, "delta_tau": pa - pb, "ci_low": pct(d, lo), "ci_high": pct(d, hi),
            "sd": float(np.std(d, ddof=1)), "share_positive": float(np.mean(d > 0)),
            "n_boot": int(d.size), "skipped": int((~ok).sum())}


def verdict(r: dict, test: str) -> bool | None:
    if test == "superiority":
        return r["ci_low"] > 0
    if test == "non_inferiority":
        return r["ci_low"] > -DELTA
    if test == "no_worse":
        return r["ci_high"] >= 0
    return None


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------


def load(exp: Path) -> tuple[dict, dict, dict]:
    data = exp / "data"
    frames, summaries, files = {}, {}, {}
    for name, a in ANALYSES.items():
        proc, pub = data / a["proc"], data / a["pub"]
        w0 = read_parts(proc / a["w0"], "spender_scores").sort_values("id").reset_index(drop=True)
        w1 = read_parts(proc / a["w1"], "spender_scores").sort_values("id").reset_index(drop=True)
        tr = read_parts(proc / a["w1"], "trader_scores").sort_values("id").reset_index(drop=True)
        same = read_parts(proc / a["same"], "cohort_scores").sort_values("id").reset_index(drop=True)
        frames[name] = {"w0_spenders": w0, "w1_spenders": w1, "w1_traders": tr, "same_window": same}
        summaries[name] = {
            "w0": json.loads((pub / a["w0"] / "eval_summary.json").read_text(encoding="utf-8")),
            "w1": json.loads((pub / a["w1"] / "eval_summary.json").read_text(encoding="utf-8")),
        }
        files[name] = {
            str(p.relative_to(exp)): sha256(p)
            for sub in (a["w0"], a["w1"], a["same"])
            for p in sorted((proc / sub).glob("*.part*.parquet"))
        } | {str((pub / s / "eval_summary.json").relative_to(exp)): sha256(pub / s / "eval_summary.json")
             for s in (a["w0"], a["w1"])}
    return frames, summaries, files


def published(summ: dict, where: tuple) -> dict:
    block = summ[where[0]][where[1]]
    return block[where[2]]


# ---------------------------------------------------------------------------
# Worker for the seed spread (one analysis, cohort and seed per task)
# ---------------------------------------------------------------------------

_FRAMES: dict | None = None


def _init(frames: dict) -> None:
    global _FRAMES
    _FRAMES = frames


def _seed_task(args: tuple[str, str, int, list]) -> tuple[str, str, int, dict]:
    analysis, cohort, seed, specs = args
    df = _FRAMES[analysis][cohort]
    idx = resample_matrix(len(df), seed)
    cache: dict = {}
    out = {}
    for name, a, b, lab, test in specs:
        for s in (a, b):
            if (s, lab) not in cache:
                cache[(s, lab)] = taus_on(df[s].to_numpy(float), df[lab].to_numpy(float), idx)
        pa = tau(dense(df[a].to_numpy(float)), dense(df[lab].to_numpy(float)))
        pb = tau(dense(df[b].to_numpy(float)), dense(df[lab].to_numpy(float)))
        r = contrast(cache[(a, lab)], cache[(b, lab)], pa, pb)
        r["holds"] = verdict(r, test)
        out[name] = r
    return analysis, cohort, seed, out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"))
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    if not args.phd_works:
        raise SystemExit("pass --phd-works PATH or set PHD_WORKS")
    phd = Path(args.phd_works).resolve()
    exp = experiments_dir(phd)
    t0 = time.time()
    frames, summaries, files = load(exp)

    result: dict = {
        "what": "Exploratory checks of Manuscript B; computed after every registered and revised result was known",
        "generated_by": "manuscripts/B-ieee-access/supplement/exploratory_checks.py",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phd_works_head": head_commit(phd),
        "experiments": str(exp.relative_to(phd)),
        "inputs_sha256": files,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "pandas": pd.__version__},
        "bootstrap": {"resamples": N_BOOT, "seed": SEED, "extra_seeds": [EXTRA_SEEDS[0], EXTRA_SEEDS[-1]],
                      "draw": "numpy.random.default_rng(seed).integers(0, n, size=(400, n)) over the cohort sorted by contract id"},
        "margin_delta": DELTA,
        "cohort_sizes": {a: {c: int(len(f)) for c, f in fr.items()} for a, fr in frames.items()},
    }

    # 1. Recompute the decision contrasts and those reported beside them (seed 42).
    recompute, worst = {}, 0.0
    for name in ANALYSES:
        rows = {}
        for spec in DECISION + BESIDE:
            label, cohort, a, b, lab, test, where = spec
            df = frames[name][cohort]
            idx = resample_matrix(len(df), SEED)
            sa = taus_on(df[a].to_numpy(float), df[lab].to_numpy(float), idx)
            sb = taus_on(df[b].to_numpy(float), df[lab].to_numpy(float), idx)
            pa = tau(dense(df[a].to_numpy(float)), dense(df[lab].to_numpy(float)))
            pb = tau(dense(df[b].to_numpy(float)), dense(df[lab].to_numpy(float)))
            r = contrast(sa, sb, pa, pb)
            r["test"], r["holds"] = test, verdict(r, test)
            pubr = published(summaries[name], where)
            diffs = {k: abs(r[k] - pubr[k]) for k in ("delta_tau", "ci_low", "ci_high")}
            r["published"] = {k: pubr[k] for k in ("delta_tau", "ci_low", "ci_high")}
            if "holds" in pubr:
                r["published"]["holds"] = pubr["holds"]
            r["max_abs_diff_from_published"] = max(diffs.values())
            r["half_width"] = (r["ci_high"] - r["ci_low"]) / 2
            worst = max(worst, r["max_abs_diff_from_published"])
            rows[label] = r
        recompute[name] = rows
    result["recompute"] = recompute
    result["recompute_max_abs_diff"] = worst
    print(f"recompute: largest difference from the published values {worst:.2e}")
    if worst > 1e-9:
        print("recomputed values differ from the published summaries", file=sys.stderr)
        return 1

    # 2. Seed spread of the five decision contrasts.
    tasks = []
    for name in ANALYSES:
        for cohort in ("w0_spenders", "w1_spenders", "w1_traders"):
            specs = [(n_, a, b, lab, test) for n_, c, a, b, lab, test, _ in DECISION if c == cohort]
            for seed in EXTRA_SEEDS:
                tasks.append((name, cohort, seed, specs))
    spread_raw: dict = {}
    with ProcessPoolExecutor(max_workers=args.workers, initializer=_init, initargs=(frames,)) as pool:
        for analysis, cohort, seed, out in pool.map(_seed_task, tasks, chunksize=2):
            for k, r in out.items():
                spread_raw.setdefault(analysis, {}).setdefault(k, []).append({"seed": seed, **r})
    spread = {}
    for name, per in spread_raw.items():
        spread[name] = {}
        for k, rows in per.items():
            lo = np.array([r["ci_low"] for r in rows])
            hi = np.array([r["ci_high"] for r in rows])
            base = recompute[name][k]["holds"]
            spread[name][k] = {
                "seeds": len(rows),
                "ci_low_mean": float(lo.mean()), "ci_low_sd": float(lo.std(ddof=1)),
                "ci_low_min": float(lo.min()), "ci_low_max": float(lo.max()),
                "ci_high_mean": float(hi.mean()), "ci_high_sd": float(hi.std(ddof=1)),
                "ci_high_min": float(hi.min()), "ci_high_max": float(hi.max()),
                "verdict_seed42": base,
                "seeds_with_other_verdict": int(sum(r["holds"] != base for r in rows)),
                "seeds_interval_contains_zero": int(sum(r["ci_low"] <= 0 <= r["ci_high"] for r in rows)),
                "resamples_skipped_total": int(sum(r["skipped"] for r in rows)),
            }
    result["seed_spread"] = spread
    print(f"seed spread done after {time.time() - t0:.0f} s")

    # 3. Steps of the coupling weight (seed 42).
    steps_def = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0), (0.25, 0.75)]
    steps = {}
    for name in ANALYSES:
        steps[name] = {}
        for cohort, labels in COHORT_LABELS.items():
            df = frames[name][cohort]
            idx = resample_matrix(len(df), SEED)
            for lab in labels:
                samp = {l: taus_on(df[c].to_numpy(float), df[lab].to_numpy(float), idx) for l, c in LAMBDA_COLS.items()}
                pts = {l: tau(dense(df[c].to_numpy(float)), dense(df[lab].to_numpy(float))) for l, c in LAMBDA_COLS.items()}
                key = f"{cohort}:{lab}"
                steps[name][key] = {
                    f"{hi_}-{lo_}": contrast(samp[hi_], samp[lo_], pts[hi_], pts[lo_]) for lo_, hi_ in steps_def
                }
    result["lambda_steps"] = steps
    print(f"lambda steps done after {time.time() - t0:.0f} s")

    # 4. Rank agreement between values of the coupling weight (seed 42).
    pairs = [(0.0, 0.25), (0.25, 0.75), (0.75, 1.0)]
    agree = {}
    for name in ANALYSES:
        agree[name] = {}
        for cohort in ("same_window", "w0_spenders", "w1_spenders"):
            df = frames[name][cohort]
            idx = resample_matrix(len(df), SEED)
            agree[name][cohort] = {}
            for l1, l2 in pairs:
                x, y = df[LAMBDA_COLS[l1]].to_numpy(float), df[LAMBDA_COLS[l2]].to_numpy(float)
                s = taus_on(x, y, idx)
                s = s[np.isfinite(s)]
                agree[name][cohort][f"{l1}-{l2}"] = {
                    "tau_b": tau(dense(x), dense(y)), "ci_low": pct(s, 2.5), "ci_high": pct(s, 97.5),
                    "n": int(len(df)), "n_boot": int(s.size),
                }
    result["lambda_rank_agreement"] = agree
    result["runtime_s"] = round(time.time() - t0, 1)

    out = HERE / "exploratory_checks.json"
    out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {out} after {result['runtime_s']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
