#!/usr/bin/env python3
"""Check the closed form of EndorseRank on a depth-one allowance graph.

With uniform restarts and uniform dangling redistribution, a node whose
in-neighbours all lack in-edges has PageRank c * (1 + d * delta(v)), where
delta(v) = sum_u w(u,v) / W(u) is its owner-normalised in-strength and c is the
common score of nodes without in-edges. This script measures how closely the
EndorseRank actually computed in the thesis follows that form.

    python check_closed_form.py --experiments /path/to/wallet-reputation-experiments
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent


def analyse(edges: pd.DataFrame, scores: dict[str, float], damping: float) -> dict:
    e = edges.groupby(["from_node", "to_node"], as_index=False)["weight"].sum()
    e = e[e["from_node"] != e["to_node"]]
    out_w = e.groupby("from_node")["weight"].sum()
    e = e.assign(share=e["weight"] / e["from_node"].map(out_w))
    delta = e.groupby("to_node")["share"].sum()
    indeg = e.groupby("to_node")["from_node"].nunique()
    nodes = set(e["from_node"]) | set(e["to_node"])
    has_in = set(e["to_node"])
    has_out = set(e["from_node"])
    pure_owner = has_out - has_in
    pure_spender = has_in - has_out
    dual = has_in & has_out
    c = float(np.median([scores[u] for u in pure_owner if u in scores]))
    spenders = sorted(has_in)
    pr = np.array([scores.get(v, np.nan) for v in spenders])
    dl = delta.reindex(spenders).to_numpy()
    deg = indeg.reindex(spenders).to_numpy()
    pred = c * (1.0 + damping * dl)
    rel = np.abs(pr - pred) / pr
    # in-neighbours of each spender that themselves have in-edges
    e_dual_src = e[e["from_node"].isin(has_in)]
    affected = set(e_dual_src["to_node"])
    return {
        "n_nodes": len(nodes),
        "n_edges": int(len(e)),
        "n_pure_owners": len(pure_owner),
        "n_pure_spenders": len(pure_spender),
        "n_dual_role": len(dual),
        "n_spenders_with_a_dual_role_in_neighbour": len(affected),
        "common_owner_score_c": c,
        "spearman_er_vs_delta_spenders": float(spearmanr(pr, dl).statistic),
        "spearman_er_vs_in_degree_spenders": float(spearmanr(pr, deg).statistic),
        "spearman_delta_vs_in_degree_spenders": float(spearmanr(dl, deg).statistic),
        "median_relative_error_closed_form": float(np.nanmedian(rel)),
        "p95_relative_error_closed_form": float(np.nanquantile(rel, 0.95)),
        "share_spenders_within_1pct": float(np.nanmean(rel < 0.01)),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiments", required=True, type=Path)
    exp = ap.parse_args().experiments.resolve()
    os.chdir(exp)
    sys.path.insert(0, str(exp / "scripts"))
    from common import load_config
    from fresh_holdout import combine_events, load_fresh_events, load_registration, load_spring_events, window_config
    from holdout import holdout_bounds, latest_positive_as_of, pagerank_params
    from pagerank import build_endorserank_vt_edges, filter_subgraph_edges, weighted_pagerank
    from run_fresh_posthoc import _matched_wallets

    config = load_config()
    reg = load_registration()
    out = {}
    for name, cfg, events in (
        ("W0_freeze_2026-02-28", config, load_spring_events(config)),
        ("W1_freeze_2026-05-31", window_config(config, reg), None),
    ):
        if events is None:
            spring = load_spring_events(config)
            fresh = load_fresh_events(reg)
            events = {k: combine_events(spring[k], fresh[k]) for k in ("approvals", "transfers", "decoded")}
        score_end, _, _ = holdout_bounds(cfg)
        latest = latest_positive_as_of(events["approvals"], score_end)
        rep = cfg["reputation"]
        paper = rep.get("awp_paper") or {}
        edges, _ = build_endorserank_vt_edges(
            latest, score_end, float(rep["awp_decay_k"]), float(rep["awp_decay_t0_days"]), float(paper.get("value_b", 1.0))
        )
        edges = filter_subgraph_edges(edges, set(_matched_wallets(config)))
        damping, tol, max_iter = pagerank_params(cfg)
        scores = weighted_pagerank(edges, damping=damping, tol=tol, max_iter=max_iter)
        out[name] = analyse(edges, scores, damping)
        print(name, json.dumps(out[name], indent=1))
    (HERE / "closed_form_check.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
