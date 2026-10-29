#!/usr/bin/env python3
"""Export the closed-form check of EndorseRank for the journal manuscripts.

For PageRank with damping d and uniform restarts, every node without in-edges has
the same score c, and a spender v whose owners have no in-edges themselves (a
depth-one spender) scores exactly

    s(v) = c * (1 + d * delta(v)),   delta(v) = sum_u w(u, v) / o(u),

where o(u) is the out-strength of owner u (thesis, Chapter 5, "EndorseRank on
depth-one spenders"). The experiment pipeline in phd_works computes the check on
the allowance edges (function ``closed_form`` in ``scripts/run_same_window.py``,
called by ``run_same_window.py`` on the graph at T_obs and by ``run_holdout.py`` on
the graph at t1) and stores it under the key ``closed_form`` of each
``eval_summary.json``. The edges are kept in BigQuery only, so this script does not
recompute the check. It

1. copies the ``closed_form`` blocks of both analyses (revised and registered) and
   both graphs (T_obs, which is also the W1 freeze, and the W0 freeze t1) into
   ``closed_form_check.json``, after verifying each summary against the
   ``SHA256SUMS.txt`` published next to it;
2. runs the checks that the per-contract score files allow without the edges
   (see ``score_file_check`` in the output and analysis/README.md).

Usage (the path to a phd_works checkout is required):

    PHD_WORKS=/path/to/phd_works python export_closed_form.py
    python export_closed_form.py --phd-works /path/to/phd_works
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE / "closed_form_check.json"

# Location of the experiment folder inside phd_works. The first entry is the
# current folder; the second is where the same folder sat in the commits that
# produced the results (43d8045 to 77e71f5).
EXPERIMENT_DIRS = (
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
PROC = "data/2-processed-tables-and-evaluations"

ANALYSES = {
    "revised": {
        "pub": f"{PUB}/revised-usd-12m",
        "proc": f"{PROC}/revised-usd-12m",
        "status": ("Main analysis of the thesis: amounts in USD over WETH, USDC, USDT0, ARB and WBTC "
                   "(docs/revision_price_weighting.md) and score windows of the twelve months before each "
                   "freeze (docs/revision_one_year_window.md). Defined after the registered results were known; "
                   "never a registered result."),
        "scored_set": {
            "same_window": ("matched cohort: contracts approved on WETH, USDC, USDT0, ARB or WBTC by >= 3 distinct "
                            "owners in the twelve months before T_obs"),
            "W0": ("W0 spender cohort: contract spenders with a positive latest allowance of one of the five tokens, "
                   "set in the twelve months before t1, at t1"),
        },
    },
    "registered": {
        "pub": PUB,
        "proc": PROC,
        "status": ("Registered analysis as fixed in docs/analysis_plan.md (raw base units, every ERC-20); "
                   "reported in thesis Appendix 8.6."),
        "scored_set": {
            "same_window": "plan cohort: contracts approved on any ERC-20 by >= 3 distinct owners",
            "W0": "W0 spender cohort: contract spenders with a positive latest allowance of any ERC-20 at t1",
        },
    },
}
WINDOWS = {
    "same_window": {
        "summary": "same-window/eval_summary.json",
        "scores": "same-window/cohort_scores",
        "date_key": "anchor",
        "size_key": "cohort",
        "graph": "allowance graph at T_obs = 2026-06-30 23:59:59 UTC (the W1 freeze; the W1 scores use the same graphs)",
        "degree_col": "in_approve_degree",
    },
    "W0": {
        "summary": "holdout-w0/eval_summary.json",
        "scores": "holdout-w0/spender_scores",
        "date_key": "freeze",
        "size_key": "spenders",
        "graph": "allowance graph at t1 = 2026-03-31 23:59:59 UTC (the W0 freeze)",
        "degree_col": "t1_in_approve_degree",
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"),
                   help="path to a phd_works checkout (or set PHD_WORKS)")
    p.add_argument("--experiments-subdir", default=None,
                   help="experiment folder relative to phd_works (default: the first of "
                        + ", ".join(EXPERIMENT_DIRS) + " that exists)")
    p.add_argument("--out", default=str(OUT), help="output JSON (default: %(default)s)")
    a = p.parse_args()
    if not a.phd_works:
        p.error("give --phd-works PATH or set the environment variable PHD_WORKS")
    return a


def experiments_dir(phd_works: Path, subdir: str | None) -> tuple[Path, str]:
    for rel in ((subdir,) if subdir else EXPERIMENT_DIRS):
        d = phd_works / rel
        if (d / PUB).is_dir():
            return d, rel
    raise SystemExit(f"no experiment folder with {PUB} under {phd_works}")


def git_head(repo: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def sha256_published(path: Path) -> str:
    """SHA-256 of the file with CRLF line ends.

    The checksums in SHA256SUMS.txt were taken on a Windows checkout, where text
    files have CRLF line ends; a Linux checkout has LF. Hashing the CRLF form makes
    the comparison independent of the checkout.
    """
    b = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(b).hexdigest()


def published_sums(pub_dir: Path) -> dict[str, str]:
    sums = {}
    for line in (pub_dir / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            sums[name.strip().lstrip("*")] = h
    return sums


def read_parts(stem: Path) -> tuple[pd.DataFrame, list[Path]]:
    parts = sorted(stem.parent.glob(stem.name + ".part*.parquet"))
    if not parts:
        raise SystemExit(f"no parquet parts for {stem}")
    return pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True), parts


def score_file_check(df: pd.DataFrame, degree_col: str, cf: dict, size: int, d: float,
                     nodes: int | None) -> dict:
    """Checks on the EndorseRank scores of the scored set that need no edges.

    Facts used (weighted_pagerank in scripts/scoring.py and the proposition of the
    thesis): the solver graph holds the end points of the edges with positive weight;
    a contract outside it gets score 0; every node of it scores at least c, and a node
    scores above c only if it has an in-edge of positive weight, i.e. only if it is
    one of the spenders of the check.
    """
    c = cf["common_value_c"]
    s = df["endorserank"].to_numpy(dtype=np.float64)
    deg = df[degree_col].to_numpy(dtype=np.float64)
    above = int((s > c).sum())
    at_c = int((s == c).sum())
    out = {
        "rows": int(len(s)),
        "score_zero": int((s == 0).sum()),
        "score_equal_c": at_c,
        "score_above_c": above,
        "score_between_0_and_c": int(((s > 0) & (s < c)).sum()),
        "min_score_over_c_among_nonzero": float((s[s > 0] / c).min()) if (s > 0).any() else None,
        "above_c_without_any_approval": int(((s > c) & (deg == 0)).sum()),
    }
    checks = {
        # The score file covers exactly the scored set of the summary.
        "rows_equal_scored_set": out["rows"] == size,
        # Every node of the solver graph scores at least c.
        "no_score_between_0_and_c": out["score_between_0_and_c"] == 0,
        # Spenders of the check: at least the contracts above c, at most those at or above c
        # (a spender whose c * d * delta(v) is below the float spacing of c prints as c).
        "spenders_within_bounds": above <= cf["spenders"] <= above + at_c,
        # A score above c needs an approval received.
        "above_c_implies_approval_received": out["above_c_without_any_approval"] == 0,
    }
    if nodes:
        # c = (1 - d + d r_D) / |V_solver| >= (1 - d) / |V_solver| >= (1 - d) / |V|, where |V| counts the
        # end points of all allowance edges in the summary and the solver graph is a subset of them.
        out["restart_floor"] = (1 - d) / nodes
        checks["c_at_least_restart_floor"] = c >= out["restart_floor"]
    out["spenders_equal_score_above_c"] = above == cf["spenders"]
    out["checks"] = checks
    out["all_checks_pass"] = all(checks.values())
    out["not_checkable_without_edges"] = ["depth_one_spenders", "within_1pct_all", "within_1pct_depth_one",
                                          "within_1pct_deeper", "tau_score_vs_delta", "common_value_c (needs r_D)"]
    return out


def main() -> int:
    a = parse_args()
    phd = Path(a.phd_works).expanduser().resolve()
    exp, exp_rel = experiments_dir(phd, a.experiments_subdir)
    cfg = yaml.safe_load((exp / PUB / "config" / "contract_reputation.yaml").read_text(encoding="utf-8"))
    d = float(cfg["reputation"]["damping"])

    rows, failures = [], []
    for analysis, A in ANALYSES.items():
        pub_dir, proc_dir = exp / A["pub"], exp / A["proc"]
        sums = published_sums(pub_dir)
        for window, W in WINDOWS.items():
            path = pub_dir / W["summary"]
            h = sha256_published(path)
            verified = sums.get(W["summary"]) == h
            if not verified:
                failures.append(f"{A['pub']}/{W['summary']}: checksum differs from SHA256SUMS.txt")
            summary = json.loads(path.read_text(encoding="utf-8"))
            cf = summary["closed_form"]
            graph = summary.get("graph") or {}
            nodes = (graph.get("allowance") or {}).get("nodes")
            edges = (graph.get("allowance") or {}).get("edges", graph.get("allowance_edges"))
            df, parts = read_parts(proc_dir / W["scores"])
            check = score_file_check(df, W["degree_col"], cf, int(summary[W["size_key"]]), d, nodes)
            check["files"] = [{"file": str(p.relative_to(exp)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                              for p in parts]
            if not check["all_checks_pass"]:
                failures.append(f"{analysis} {window}: score-file check failed {check['checks']}")
            rows.append({
                "analysis": analysis,
                "window": window,
                "graph": W["graph"],
                "graph_date": summary[W["date_key"]],
                "scored_set": A["scored_set"][window],
                "scored_set_size": int(summary[W["size_key"]]),
                "damping": d,
                "c": cf["common_value_c"],
                "spread_of_c": cf["spread_of_c"],
                "spenders": cf["spenders"],
                "depth_one_spenders": cf["depth_one_spenders"],
                "deeper_spenders": cf["spenders"] - cf["depth_one_spenders"],
                "within_1pct_all": cf["within_1pct_all"],
                "within_1pct_depth_one": cf["within_1pct_depth_one"],
                "within_1pct_deeper": cf["within_1pct_deeper"],
                "tau_score_vs_delta": cf["tau_score_vs_delta"],
                "allowance_graph_nodes": nodes,
                "allowance_graph_edges": edges,
                "source": {
                    "file": f"{A['pub']}/{W['summary']}",
                    "key": "closed_form",
                    "sha256_published": h,
                    "checksum_matches_SHA256SUMS": verified,
                },
                "score_file_check": check,
            })

    report = {
        "what": ("Closed-form check of EndorseRank, s(v) = c (1 + d delta(v)) for spenders whose owners have no "
                 "in-edges, copied from the evaluation summaries of phd_works for both analyses and both graphs."),
        "generated_by": "analysis/closed-form/export_closed_form.py",
        "phd_works": {
            "repository": "https://github.com/abitocodes/phd_works",
            "head": git_head(phd),
            "experiments_dir": exp_rel,
            "computed_by": ("scripts/run_same_window.py (function closed_form; graph at T_obs) and "
                            "scripts/run_holdout.py (same function; graph at t1); revised analysis with "
                            "CONTRACT_REP_VARIANT=usd, registered analysis with the variable unset"),
        },
        "definitions": {
            "c": "common score of the nodes without in-edges (median over them; spread_of_c = max/min over them)",
            "spenders": "contracts of the scored set with at least one allowance in-edge of positive weight",
            "depth_one_spenders": "spenders none of whose owners has an in-edge; the closed form is exact for them",
            "deeper_spenders": "spenders - depth_one_spenders (at least one owner is itself approved)",
            "within_1pct_*": "share of the spenders whose EndorseRank is within 1% of c (1 + d delta(v))",
            "tau_score_vs_delta": ("Kendall tau_b between EndorseRank and delta(v) over all spenders; a point value "
                                   "without interval (the pipeline computes no bootstrap for it)"),
            "damping": "d, reputation.damping in config/contract_reputation.yaml",
        },
        "rows": rows,
    }
    Path(a.out).write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: {len(rows)} rows from {exp_rel}")
    for r in rows:
        k = r["score_file_check"]
        print(f"  {r['analysis']:10s} {r['window']:11s} c={r['c']:.4g} spenders={r['spenders']:,} "
              f"depth-one={r['depth_one_spenders']:,} within1%={r['within_1pct_all']:.4f} "
              f"tau={r['tau_score_vs_delta']:.4f} checksum={'ok' if r['source']['checksum_matches_SHA256SUMS'] else 'FAIL'} "
              f"score-file checks={'ok' if k['all_checks_pass'] else 'FAIL'} "
              f"(above c {k['score_above_c']:,}, at c {k['score_equal_c']:,})")
    if failures:
        print("FAILED:\n  " + "\n  ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
