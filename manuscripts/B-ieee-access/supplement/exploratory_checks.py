#!/usr/bin/env python3
"""Exploratory diagnostics for Manuscript B (IEEE Access), computed on 9 October 2026.

Every registered result was known when this script was written, so nothing here enters
a decision rule and nothing here was fixed in advance. The checks answer reviewer
questions about the coupled walk C-PR: how much the coupling weight acts through the
wallets active in both layers, whether bounded or binary weights change the picture,
how the scores do in AUC terms, how precise the bootstrap endpoints are, how much
dependence between spenders widens the intervals, whether the spring sample looks
ahead, how often an apparently new approval pair is an old one, and how cheaply a farm
inflates each walk.

It reuses the evaluation code of the experiments folder (phd_works) unchanged and adds
only a vectorised edge-matrix builder, checked below against the pipeline's own scores.

    python exploratory_checks.py --experiments /path/to/wallet-reputation-experiments

Writes exploratory_checks.json next to this file.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.stats import kendalltau, norm, rankdata

HERE = Path(__file__).resolve().parent
N_BOOT = 400
SEED = 42
ZERO = "0x0000000000000000000000000000000000000000"
PERMIT2 = "0x000000000022d473030f116ddee9f6b43ac78ba3"
LAMBDAS_EXTRA = (0.0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1.0)
APPROVE = "future_new_approvers"
SENDERS = "future_new_transfer_senders"
LFCR = "future_liquidation_free_rate"


# ---------------------------------------------------------------------------
# Solver: the pipeline's coupled walk with a vectorised edge-matrix builder
# ---------------------------------------------------------------------------


def adjacency(edges: pd.DataFrame, idx: dict[str, int], n: int) -> tuple[sparse.csr_matrix, np.ndarray]:
    w = edges["weight"].astype(float)
    e = edges[w > 0]
    u = e["from_node"].map(idx)
    v = e["to_node"].map(idx)
    ok = u.notna() & v.notna()
    ui = u[ok].astype(np.int64).to_numpy()
    vi = v[ok].astype(np.int64).to_numpy()
    wi = e.loc[ok, "weight"].astype(float).to_numpy()
    adj = sparse.csr_matrix((wi, (ui, vi)), shape=(n, n))
    out = np.bincount(ui, weights=wi, minlength=n).astype(np.float64)
    return adj, out


def coupled(layers, d=0.85, teleport=None, tol=1e-8, max_iter=300, extra_nodes=()):
    """C-PR exactly as pagerank.coupled_pagerank (and weighted_pagerank for one layer).

    ``layers`` is a list of (edges, weight). Returns (scores, nodes, rank, presence).
    ``teleport`` maps node -> restart mass (uniform when None).
    """
    from pagerank import _power_iterate, _row_normalise, _teleport_vector

    active = [(e, float(w)) for e, w in layers if e is not None and not e.empty and float(w) > 0]
    node_set: set[str] = set(extra_nodes)
    for e, _ in active:
        node_set.update(e["from_node"])
        node_set.update(e["to_node"])
    nodes = sorted(node_set)
    idx = {x: i for i, x in enumerate(nodes)}
    n = len(nodes)
    denom = np.zeros(n)
    trans, pres, ws = [], [], []
    for e, w in active:
        adj, out = adjacency(e, idx, n)
        trans.append(_row_normalise(adj, out))
        pres.append((out > 0).astype(float))
        ws.append(w)
        denom += w * pres[-1]
    mixed = sparse.csr_matrix((n, n))
    for w, has, tr in zip(ws, pres, trans):
        alpha = np.zeros(n)
        pos = denom > 0
        alpha[pos] = w * has[pos] / denom[pos]
        mixed = mixed + sparse.diags(alpha, format="csr") @ tr
    restart = _teleport_vector(nodes, teleport)
    rank, _ = _power_iterate(mixed, denom <= 0, restart, d, tol, max_iter)
    return {nodes[i]: float(rank[i]) for i in range(n)}, nodes, rank, pres


def on_wallets(scores: dict[str, float], wallets: list[str]) -> np.ndarray:
    return np.array([scores.get(w, 0.0) for w in wallets], dtype=float)


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


def tau(x, y) -> float:
    return float(kendalltau(x, y).statistic)


def auc(score, positive) -> float:
    r = rankdata(score)
    npos = int(positive.sum())
    nneg = len(positive) - npos
    return float((r[positive].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def paired_boot(a, b, y, stat="tau", n_boot=N_BOOT, seed=SEED):
    """Point estimates and the 95% percentile interval of stat(a)-stat(b), as holdout_tau_diff."""
    mask = ~np.isnan(y)
    a, b, y = a[mask], b[mask], y[mask]
    n = len(y)
    f = (lambda s, t: tau(s, t)) if stat == "tau" else (lambda s, t: auc(s, t > 0))
    rng = np.random.default_rng(seed)
    ta, tb = f(a, y), f(b, y)
    d, sa, sb = [], [], []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        ys, xa, xb = y[i], a[i], b[i]
        if np.unique(ys).size < 2 or np.unique(xa).size < 2 or np.unique(xb).size < 2:
            continue
        va, vb = f(xa, ys), f(xb, ys)
        if np.isfinite(va) and np.isfinite(vb):
            sa.append(va)
            sb.append(vb)
            d.append(va - vb)
    d, sa, sb = np.array(d), np.array(sa), np.array(sb)
    q = lambda arr: [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))]
    return {
        "a": ta, "a_ci": q(sa), "b": tb, "b_ci": q(sb),
        "delta": ta - tb, "ci": q(d), "sd": float(d.std(ddof=1)), "n": int(n), "n_boot": int(len(d)),
    }


def r3(x):
    if isinstance(x, dict):
        return {k: r3(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r3(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return float(round(float(x), 6))
    if isinstance(x, np.integer):
        return int(x)
    return x


# ---------------------------------------------------------------------------
# Label events (same rules as holdout.future_approval_labels / future_transfer_labels)
# ---------------------------------------------------------------------------


def approval_label_events(approvals, latest_t1, start, end, wallets):
    from holdout import normalize_approvals, t1_positive_pairs

    pairs = t1_positive_pairs(latest_t1)
    work = normalize_approvals(approvals)
    win = work[(work["block_timestamp"] >= start) & (work["block_timestamp"] <= end) & (work["value"] > 0)]
    ws = set(wallets)
    ev = win[["spender", "owner"]].astype(str).drop_duplicates()
    ev = ev[ev["spender"].isin(ws)]
    keep = [(o, s) not in pairs for s, o in zip(ev["spender"], ev["owner"])]
    return ev[keep].reset_index(drop=True)


def sender_label_events(transfers, transfers_t1, start, end, wallets):
    from holdout import normalize_transfers

    ws = set(wallets)
    t1 = normalize_transfers(transfers_t1)
    t1 = t1[t1["to_address"].isin(ws) & (t1["from_address"] != t1["to_address"])]
    seen = set(zip(t1["to_address"].astype(str), t1["from_address"].astype(str)))
    work = normalize_transfers(transfers)
    win = work[(work["block_timestamp"] >= start) & (work["block_timestamp"] <= end)
               & work["to_address"].isin(ws) & (work["from_address"] != work["to_address"])]
    ev = win[["to_address", "from_address"]].astype(str).drop_duplicates()
    keep = [(t, f) not in seen for t, f in zip(ev["to_address"], ev["from_address"])]
    out = ev[keep].rename(columns={"to_address": "spender", "from_address": "counterparty"})
    return out.reset_index(drop=True), win


def incidence(events: pd.DataFrame, wallets: list[str], col: str) -> sparse.csr_matrix:
    widx = {w: i for i, w in enumerate(wallets)}
    cps = sorted(set(events[col]))
    cidx = {c: j for j, c in enumerate(cps)}
    rows = events["spender"].map(widx).to_numpy()
    cols = events[col].map(cidx).to_numpy()
    return sparse.csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(wallets), len(cps)))


def twoway_boot(a, b, M, n_boot=N_BOOT, seed=SEED):
    """Pigeonhole bootstrap: resample spenders and Poisson-reweight the counterparties that
    generate their label events, so spenders that share a new owner or sender move together."""
    rng = np.random.default_rng(seed)
    n, m = M.shape
    d = []
    for _ in range(n_boot):
        i = rng.integers(0, n, n)
        w = rng.poisson(1.0, size=m).astype(float)
        y = (M @ w)[i]
        if np.unique(y).size < 2:
            continue
        d.append(tau(a[i], y) - tau(b[i], y))
    d = np.array(d)
    return {"ci": [float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))], "sd": float(d.std(ddof=1))}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiments", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=HERE / "exploratory_checks.json")
    ap.add_argument("--mc-seeds", type=int, default=50)
    args = ap.parse_args()
    exp = args.experiments.resolve()
    os.chdir(exp)
    sys.path.insert(0, str(exp / "scripts"))
    from common import load_config
    from fresh_holdout import (build_cohort_frame, combine_events, load_fresh_events, load_registration,
                               load_spring_events, window_config)
    from holdout import (filter_subgraph_edges, filter_transfers_as_of, holdout_bounds, latest_positive_as_of,
                         normalize_approvals, normalize_transfers, score_awp_paper, score_endorserank_vt)
    from pagerank import build_awp_edges, build_awp_paper_edges, build_endorserank_edges, build_endorserank_vt_edges
    from run_fresh_holdout import _matched_wallets

    t0 = time.time()
    log = lambda *a: print(f"[{time.time() - t0:7.1f}s]", *a, flush=True)
    config = load_config()
    reg = load_registration()
    rep = config["reputation"]
    K, T0, BV = float(rep["awp_decay_k"]), float(rep["awp_decay_t0_days"]), float(rep["awp_paper"]["value_b"])
    spring = load_spring_events(config)
    fresh = load_fresh_events(reg)
    allev = {k: combine_events(spring[k], fresh[k]) for k in ("approvals", "transfers", "decoded")}
    matched = _matched_wallets(config)
    cfg = {"spring": config, "registered": window_config(config, reg)}
    events = {"spring": spring, "registered": allev}
    out: dict = {"computed": time.strftime("%Y-%m-%d"), "note": "exploratory; computed after every registered result was known"}

    # -- cohort frames from the pipeline (scores and labels exactly as registered) --
    frames, ctx = {}, {}
    for win in ("spring", "registered"):
        c = cfg[win]
        se, os_, oe = holdout_bounds(c)
        latest = latest_positive_as_of(events[win]["approvals"], se)
        trans = filter_transfers_as_of(events[win]["transfers"], se)
        ctx[win] = {"se": se, "os": os_, "oe": oe, "latest": latest, "trans": trans}
        for cohort in (("spenders", "traders") if win == "registered" else ("spenders",)):
            merged, _, meta = build_cohort_frame(c, events[win], cohort, matched if cohort == "traders" else None,
                                                 with_liquidation=(win == "registered"))
            frames[(win, cohort)] = merged
            log("frame", win, cohort, meta["n_wallets"])

    def layers(win, wallets, k=K, t0_=T0, kind="raw"):
        x = ctx[win]
        seed = set(wallets)
        if kind == "raw":
            ea = filter_subgraph_edges(build_endorserank_edges(x["latest"]), seed)
            et = filter_subgraph_edges(build_awp_edges(x["trans"], x["se"], k, t0_), seed)
        elif kind == "bounded":
            ea = filter_subgraph_edges(build_endorserank_vt_edges(x["latest"], x["se"], k, t0_, BV)[0], seed)
            et = filter_subgraph_edges(build_awp_paper_edges(x["trans"], x["se"], k, t0_, BV)[0], seed)
        elif kind == "binary":
            ea, et = layers(win, wallets, k, t0_, "raw")
            ea, et = ea.assign(weight=1.0), et[et["weight"] > 0].assign(weight=1.0)
        return ea, et

    def cpr(win, wallets, lam, d=0.85, kind="raw", k=K, t0_=T0):
        ea, et = layers(win, wallets, k, t0_, kind)
        s, *_ = coupled([(ea, lam), (et, 1.0 - lam)], d=d)
        return on_wallets(s, wallets)

    # -- 0. the vectorised solver reproduces the pipeline's scores --
    check = {}
    for (win, cohort), m in frames.items():
        w = m["wallet"].tolist()
        for col, lam in (("awp", 0.0), ("coupled_pr_l25", 0.25), ("coupled_pr", 0.5), ("coupled_pr_l75", 0.75), ("endorserank", 1.0)):
            mine = cpr(win, w, lam)
            check[f"{win}/{cohort}/{col}"] = float(np.max(np.abs(mine - m[f"{col}_score"].to_numpy())))
    out["solver_check_max_abs_diff"] = check
    log("solver check", max(check.values()))

    # -- 1. graph sizes, self-loops, the set B --
    sizes = {}
    for (win, cohort), m in frames.items():
        w = m["wallet"].tolist()
        ea, et = layers(win, w)
        na = set(ea["from_node"]) | set(ea["to_node"])
        nt = set(et["from_node"]) | set(et["to_node"])
        oa, ot = set(ea["from_node"]), set(et[et["weight"] > 0]["from_node"])
        sizes[f"{win}/{cohort}"] = {
            "auth_nodes": len(na), "auth_edges": int(len(ea)), "auth_self_loops": int((ea["from_node"] == ea["to_node"]).sum()),
            "pay_nodes": len(nt), "pay_edges": int((et["weight"] > 0).sum()),
            "union_nodes": len(na | nt), "B_size": len(oa & ot), "auth_out_nodes": len(oa),
        }
    if matched:
        ea, et = layers("registered", [x.lower() for x in matched])
        sizes["registered/matched_5521"] = {
            "auth_nodes": len(set(ea["from_node"]) | set(ea["to_node"])), "auth_edges": int(len(ea)),
            "auth_self_loops": int((ea["from_node"] == ea["to_node"]).sum()),
            "pay_edges": int((et["weight"] > 0).sum()),
            "union_nodes": len(set(ea["from_node"]) | set(ea["to_node"]) | set(et["from_node"]) | set(et["to_node"])),
            "B_size": len(set(ea["from_node"]) & set(et[et["weight"] > 0]["from_node"])),
        }
    out["graph_sizes"] = sizes
    log("sizes", sizes)

    # -- 2. where the weight acts: r(B), interior distances, extra lambda values --
    lam_block = {}
    for (win, cohort), m in frames.items():
        w = m["wallet"].tolist()
        ea, et = layers(win, w)
        rows = {}
        interior = {}
        for lam in LAMBDAS_EXTRA:
            s, nodes, rank, pres = coupled([(ea, lam), (et, 1.0 - lam)])
            entry = {}
            if 0 < lam < 1:
                inB = (pres[0] > 0) & (pres[1] > 0)
                entry["r_B"] = float(rank[inB].sum())
                entry["bound_2d_rB_over_1_minus_d"] = float(2 * 0.85 * rank[inB].sum() / 0.15)
                interior[lam] = (nodes, rank)
            sc = on_wallets(s, w)
            labs = (APPROVE, SENDERS) if cohort == "spenders" else (LFCR,)
            for lab in labs:
                y = m[lab].to_numpy(float)
                mask = ~np.isnan(y)
                entry[lab] = tau(sc[mask], y[mask])
            rows[str(lam)] = entry
        n25, r25 = interior[0.25]
        n75, r75 = interior[0.75]
        assert n25 == n75
        s25 = dict(zip(n25, r25))
        s75 = dict(zip(n75, r75))
        rows["l1_r075_minus_r025"] = float(np.abs(r75 - r25).sum())
        rows["tau_between_lambda025_and_075_on_cohort"] = tau(on_wallets(s25, w), on_wallets(s75, w))
        lam_block[f"{win}/{cohort}"] = rows
    out["lambda_sweep"] = lam_block
    log("lambda sweep done")

    # -- 3. AUC beside tau (binary label: at least one arrival) --
    auc_block = {}
    for win in ("spring", "registered"):
        m = frames[(win, "spenders")]
        res = {}
        for lab in (APPROVE, SENDERS):
            y = m[lab].to_numpy(float)
            pos = y > 0
            entry = {"n_positive": int(pos.sum()), "n": int(len(y))}
            for col in ("t1_in_approve_degree", "t1_in_degree", "awp_paper", "awp", "coupled_pr", "endorserank", "seeded_pr"):
                entry[col] = auc(m[f"{col}_score"].to_numpy(float), pos)
            entry["cpr_minus_l0"] = paired_boot(m["coupled_pr_score"].to_numpy(float), m["awp_score"].to_numpy(float), y, stat="auc")
            entry["cpr_minus_l1"] = paired_boot(m["coupled_pr_score"].to_numpy(float), m["endorserank_score"].to_numpy(float), y, stat="auc")
            res[lab] = entry
        auc_block[win] = res
    out["auc"] = auc_block
    log("auc done")

    # -- 4. bounded and binary weights on both layers --
    weights_block = {}
    for kind in ("bounded", "binary"):
        res = {}
        for (win, cohort), m in frames.items():
            w = m["wallet"].tolist()
            sc = {lam: cpr(win, w, lam, kind=kind) for lam in (0.0, 0.25, 0.5, 0.75, 1.0)}
            labs = (APPROVE, SENDERS) if cohort == "spenders" else (LFCR,)
            entry = {}
            for lab in labs:
                y = m[lab].to_numpy(float)
                mask = ~np.isnan(y)
                entry[lab] = {str(l): tau(s[mask], y[mask]) for l, s in sc.items()}
                entry[lab]["mid_minus_l0"] = paired_boot(sc[0.5], sc[0.0], y)
                entry[lab]["mid_minus_l1"] = paired_boot(sc[0.5], sc[1.0], y)
            res[f"{win}/{cohort}"] = entry
        weights_block[kind] = res
        log("weights", kind)
    out["weights"] = weights_block

    # -- 5. Monte Carlo spread of the decision endpoints over bootstrap seeds --
    contrasts = {
        "A1": ("spring", "spenders", "coupled_pr", "endorserank", APPROVE),
        "A2": ("spring", "spenders", "coupled_pr", "awp", SENDERS),
        "F1": ("registered", "spenders", "coupled_pr", "awp", APPROVE),
        "F2": ("registered", "spenders", "coupled_pr", "awp", SENDERS),
        "F3": ("registered", "traders", "coupled_pr", "awp", LFCR),
        "S1_F2": ("registered", "spenders", "coupled_pr", "awp_paper", SENDERS),
    }
    mc = {}
    for cid, (win, cohort, a, b, lab) in contrasts.items():
        m = frames[(win, cohort)]
        av, bv, y = m[f"{a}_score"].to_numpy(float), m[f"{b}_score"].to_numpy(float), m[lab].to_numpy(float)
        reg42 = paired_boot(av, bv, y, seed=SEED)
        lows, highs = [], []
        for s in range(args.mc_seeds):
            r = paired_boot(av, bv, y, seed=1000 + s)
            lows.append(r["ci"][0])
            highs.append(r["ci"][1])
        lows, highs = np.array(lows), np.array(highs)
        mc[cid] = {
            "seed42": reg42, "lower_mean": float(lows.mean()), "lower_sd": float(lows.std(ddof=1)),
            "lower_min": float(lows.min()), "lower_max": float(lows.max()),
            "upper_mean": float(highs.mean()), "upper_sd": float(highs.std(ddof=1)),
            "share_seeds_lower_above_minus_0.02": float(np.mean(lows > -0.02)),
            "share_seeds_lower_above_0": float(np.mean(lows > 0)),
        }
        log("mc", cid, mc[cid]["lower_sd"])
    out["monte_carlo"] = mc

    # -- 6. prospective chance of passing F2 (normal approximation, bootstrap SD) --
    sd_spring, sd_reg = mc["A2"]["seed42"]["sd"], mc["F2"]["seed42"]["sd"]
    power = {}
    for name, sd in (("spring_precision", sd_spring), ("registered_precision", sd_reg)):
        power[name] = {"sd": sd}
        for true in (0.0, 0.007):
            power[name][f"P_pass_if_true_{true}"] = float(norm.cdf((true + 0.02 - 1.96 * sd) / sd))
    out["f2_pass_probability"] = power

    # -- 7. dependence: pigeonhole bootstrap for spender labels, week blocks for traders --
    dep = {}
    for cid in ("A1", "A2", "F1", "F2"):
        win, cohort, a, b, lab = contrasts[cid]
        m = frames[(win, cohort)]
        w = m["wallet"].tolist()
        x = ctx[win]
        if lab == APPROVE:
            ev = approval_label_events(events[win]["approvals"], x["latest"], x["os"], x["oe"], w)
            M = incidence(ev, w, "owner")
        else:
            ev, _ = sender_label_events(events[win]["transfers"], x["trans"], x["os"], x["oe"], w)
            M = incidence(ev, w, "counterparty")
        assert np.allclose(np.asarray(M.sum(axis=1)).ravel(), m[lab].to_numpy(float)), cid
        dep[cid] = {"wallet_only": mc[cid]["seed42"]["ci"], "two_way": twoway_boot(m[f"{a}_score"].to_numpy(float), m[f"{b}_score"].to_numpy(float), M),
                    "n_counterparties": int(M.shape[1]), "events": int(M.sum())}
    # traders: resample traders and calendar weeks of the label window
    m = frames[("registered", "traders")]
    x = ctx["registered"]
    dec = allev["decoded"].copy()
    dec["block_timestamp"] = pd.to_datetime(dec["block_timestamp"], utc=True)
    dec = dec[(dec["block_timestamp"] >= x["os"]) & (dec["block_timestamp"] <= x["oe"])]
    dec["wallet"] = dec["account"].astype(str).str.lower()
    lab_mask = m[LFCR].notna().to_numpy()
    tw = m.loc[lab_mask, "wallet"].tolist()
    widx = {wv: i for i, wv in enumerate(tw)}
    dec = dec[dec["wallet"].isin(widx)]
    week = ((dec["block_timestamp"] - x["os"]).dt.days // 7).to_numpy()
    nw = int(week.max()) + 1
    rows = dec["wallet"].map(widx).to_numpy()
    C = sparse.csr_matrix((np.ones(len(rows)), (rows, week)), shape=(len(tw), nw))
    L = sparse.csr_matrix((dec["is_liquidation"].fillna(False).astype(float).to_numpy(), (rows, week)), shape=(len(tw), nw))
    base_rate = 1 - np.asarray(L.sum(axis=1)).ravel() / np.asarray(C.sum(axis=1)).ravel()
    assert np.allclose(base_rate, m.loc[lab_mask, LFCR].to_numpy(float))
    a = m.loc[lab_mask, "coupled_pr_score"].to_numpy(float)
    b = m.loc[lab_mask, "awp_score"].to_numpy(float)
    rng = np.random.default_rng(SEED)
    d = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(tw), len(tw))
        ww = rng.multinomial(nw, np.full(nw, 1.0 / nw)).astype(float)
        c = (C @ ww)[i]
        ok = c > 0
        y = 1 - (L @ ww)[i][ok] / c[ok]
        d.append(tau(a[i][ok], y) - tau(b[i][ok], y))
    d = np.array(d)
    dep["F3"] = {"wallet_only": mc["F3"]["seed42"]["ci"], "two_way_weeks": {"ci": [float(np.quantile(d, 0.025)), float(np.quantile(d, 0.975))], "sd": float(d.std(ddof=1))}, "weeks": nw}
    out["dependence"] = dep
    log("dependence", dep)

    # -- 8. spring sample and look-ahead --
    sample = sorted({x.lower() for x in matched})
    dsp = spring["decoded"].copy()
    dsp["block_timestamp"] = pd.to_datetime(dsp["block_timestamp"], utc=True)
    dsp["wallet"] = dsp["account"].astype(str).str.lower()
    se0 = ctx["spring"]["se"]
    pre = dsp[dsp["block_timestamp"] <= se0].groupby("wallet").size()
    total = dsp.groupby("wallet").size()
    late = {w for w in sample if pre.get(w, 0) < 3}
    early = set(sample) - late
    x = ctx["spring"]
    m = frames[("spring", "spenders")]
    w = m["wallet"].tolist()
    ev_a = approval_label_events(spring["approvals"], x["latest"], x["os"], x["oe"], w)
    ev_s, _ = sender_label_events(spring["transfers"], x["trans"], x["os"], x["oe"], w)
    look = {
        "sample": len(sample), "sample_min_total_closes": int(min(total.get(s, 0) for s in sample)),
        "late_entrants_lt3_closes_by_freeze": len(late),
        "approval_events": int(len(ev_a)), "approval_events_owner_in_sample": int(ev_a["owner"].isin(set(sample)).sum()),
        "approval_events_owner_late": int(ev_a["owner"].isin(late).sum()),
        "sender_events": int(len(ev_s)), "sender_events_sender_in_sample": int(ev_s["counterparty"].isin(set(sample)).sum()),
        "sender_events_sender_late": int(ev_s["counterparty"].isin(late).sum()),
        "spenders_that_are_late_entrants": int(sum(1 for s in w if s in late)),
    }
    # registered window: who generates the label events
    xr = ctx["registered"]
    mr = frames[("registered", "spenders")]
    wr = mr["wallet"].tolist()
    ev_ar = approval_label_events(allev["approvals"], xr["latest"], xr["os"], xr["oe"], wr)
    ev_sr, win_tr = sender_label_events(allev["transfers"], xr["trans"], xr["os"], xr["oe"], wr)
    look["registered_approval_events"] = int(len(ev_ar))
    look["registered_approval_events_owner_in_sample"] = int(ev_ar["owner"].isin(set(sample)).sum())
    look["registered_sender_events"] = int(len(ev_sr))
    look["registered_sender_events_sender_in_sample"] = int(ev_sr["counterparty"].isin(set(sample)).sum())
    # rerun the spring holdout on a sample chosen from December-February closes only
    def keep_early(ev):
        a = ev["approvals"].copy()
        t = ev["transfers"].copy()
        ao, asp = a["owner"].astype(str).str.lower(), a["spender"].astype(str).str.lower()
        tf, tt = t["from_address"].astype(str).str.lower(), t["to_address"].astype(str).str.lower()
        return {"approvals": a[ao.isin(early) | asp.isin(early)], "transfers": t[tf.isin(early) | tt.isin(early)], "decoded": ev["decoded"]}
    ev_early = keep_early(spring)
    me, _, meta_e = build_cohort_frame(config, ev_early, "spenders", None, with_liquidation=False)
    rerun = {"n_spenders": int(meta_e["n_wallets"]), "early_sample": len(early)}
    for lab in (APPROVE, SENDERS):
        rerun[f"positives_{lab}"] = int((me[lab] > 0).sum())
        rerun[lab] = {c: tau(me[f"{c}_score"].to_numpy(float), me[lab].to_numpy(float))
                      for c in ("t1_in_approve_degree", "t1_in_degree", "awp", "coupled_pr", "endorserank", "awp_paper")}
    rerun["A1"] = paired_boot(me["coupled_pr_score"].to_numpy(float), me["endorserank_score"].to_numpy(float), me[APPROVE].to_numpy(float))
    rerun["A2"] = paired_boot(me["coupled_pr_score"].to_numpy(float), me["awp_score"].to_numpy(float), me[SENDERS].to_numpy(float))
    rerun["exploratory_cpr_minus_l0_new_pairs"] = paired_boot(me["coupled_pr_score"].to_numpy(float), me["awp_score"].to_numpy(float), me[APPROVE].to_numpy(float))
    look["rerun_dec_feb_sample"] = rerun
    out["lookahead"] = look
    log("lookahead", look)

    # -- 9. edge-definition diagnostics --
    diag = {}
    apr = normalize_approvals(allev["approvals"])
    full = latest_positive_as_of(allev["approvals"], xr["se"])
    trunc = latest_positive_as_of(allev["approvals"][pd.to_datetime(allev["approvals"]["block_timestamp"], utc=True) >= pd.Timestamp("2026-03-01", tz="UTC")], xr["se"])
    fullp = set(zip(full["owner"], full["spender"]))
    truncp = set(zip(trunc["owner"], trunc["spender"]))
    win_pos = apr[(apr["block_timestamp"] >= xr["os"]) & (apr["block_timestamp"] <= xr["oe"]) & (apr["value"] > 0)]
    lab_pairs = set(zip(win_pos["owner"], win_pos["spender"]))
    new_trunc = {p for p in lab_pairs if p not in truncp}
    new_full = {p for p in lab_pairs if p not in fullp}
    pre_apr = apr[apr["block_timestamp"] <= xr["se"]]
    seen_pairs = set(zip(pre_apr["owner"], pre_apr["spender"]))
    diag["left_censoring_proxy"] = {
        "label_window_positive_pairs": len(lab_pairs),
        "new_with_mar_may_history": len(new_trunc), "new_with_dec_may_history": len(new_full),
        "share_of_mar_may_new_that_were_held_at_freeze": len(new_trunc - new_full) / max(len(new_trunc), 1),
        "new_full_pairs_seen_earlier_but_zero_at_freeze": len({p for p in new_full if p in seen_pairs}),
    }
    diag["permit2"] = {
        "registered_latest_allowances": int(len(full)), "to_permit2": int((full["spender"] == PERMIT2).sum()),
        "owners_approving_permit2": int(full.loc[full["spender"] == PERMIT2, "owner"].nunique()),
        "registered_label_pairs": int(len(ev_ar)), "label_pairs_to_permit2": int((ev_ar["spender"] == PERMIT2).sum()),
        "spring_label_pairs_to_permit2": int((ev_a["spender"] == PERMIT2).sum()),
        "permit2_in_spender_cohort_registered": PERMIT2 in set(wr),
    }
    tr = normalize_transfers(allev["transfers"])
    win_tr_all = win_tr
    zero_only = win_tr_all.groupby(["to_address", "from_address"])["value"].max()
    zero_pairs = {(t, f) for (t, f), v in zero_only.items() if v == 0}
    diag["transfers"] = {
        "logs": int(len(tr)), "zero_value_logs": int((tr["value"] == 0).sum()),
        "mints_from_zero": int((tr["from_address"] == ZERO).sum()), "burns_to_zero": int((tr["to_address"] == ZERO).sum()),
        "self_transfers": int((tr["from_address"] == tr["to_address"]).sum()),
        "registered_sender_events": int(len(ev_sr)),
        "registered_sender_events_from_zero_address": int((ev_sr["counterparty"] == ZERO).sum()),
        "registered_sender_events_zero_value_only": int(sum((s, c) in zero_pairs for s, c in zip(ev_sr["spender"], ev_sr["counterparty"]))),
    }
    diag["approvals"] = {"logs": int(len(apr)), "zero_value_logs": int((apr["value"] == 0).sum())}
    out["edge_diagnostics"] = diag
    log("diag", diag)

    # -- 10. trader ties under the authorization walks --
    mt = frames[("registered", "traders")]
    lab = mt[LFCR]
    ok = lab.notna()
    sub = mt[ok]
    er_vt = score_endorserank_vt(xr["latest"], xr["se"], mt["wallet"].tolist(), cfg["registered"])
    sub = sub.assign(endorserank_vt_score=on_wallets(er_vt, sub["wallet"].tolist()))
    ties = {}
    for col in ("endorserank", "endorserank_isolated", "endorserank_vt", "t1_in_approve_degree"):
        s = sub[f"{col}_score"].to_numpy(float)
        vals, counts = np.unique(s, return_counts=True)
        top = sorted(zip(counts, vals), reverse=True)[:3]
        ties[col] = {"distinct_levels": int(len(vals)), "zero": int((s == 0).sum()),
                     "largest_tied_groups": [[int(c), float(v)] for c, v in top],
                     "tau": tau(s, sub[LFCR].to_numpy(float))}
    s1 = sub["endorserank_score"].to_numpy(float)
    nonzero = s1[s1 > 0]
    cval = float(np.median(nonzero)) if len(nonzero) else 0.0
    grp = np.where(s1 == 0, "absent", np.where(np.isclose(s1, cval, rtol=1e-9), "no_in_edges", "in_edges"))
    ties["groups_lambda1"] = {g: {"n": int((grp == g).sum()), "mean_label": float(sub[LFCR].to_numpy(float)[grp == g].mean())} for g in ("absent", "no_in_edges", "in_edges") if (grp == g).any()}
    out["trader_ties"] = ties
    log("ties", ties)

    # -- 11. S-PR at d = 0.5 --
    spr = {}
    for win in ("spring", "registered"):
        m = frames[(win, "spenders")]
        w = m["wallet"].tolist()
        ea, et = layers(win, w)
        er_s, *_ = coupled([(ea, 1.0)], d=0.85)
        res = {}
        for d_ in (0.85, 0.5):
            pay, *_ = coupled([(et, 1.0)], d=d_)
            seeded, *_ = coupled([(et, 1.0)], d=d_, teleport=er_s)
            pv, sv = on_wallets(pay, w), on_wallets(seeded, w)
            res[str(d_)] = {lab: paired_boot(sv, pv, m[lab].to_numpy(float)) for lab in (APPROVE, SENDERS)}
        spr[win] = res
    out["spr_damping"] = spr
    log("spr done")

    # -- 12. sensitivity of the decision contrasts to d, k and t0 --
    sens = {}
    for name, d_, k_, t0__ in (("d0.75", 0.75, K, T0), ("d0.95", 0.95, K, T0), ("k0.005", 0.85, 0.005, T0),
                              ("k0.02", 0.85, 0.02, T0), ("t0_90", 0.85, K, 90.0), ("t0_270", 0.85, K, 270.0)):
        res = {}
        for cid in ("F1", "F2", "F3"):
            win, cohort, _, _, lab = contrasts[cid]
            m = frames[(win, cohort)]
            w = m["wallet"].tolist()
            a = cpr(win, w, 0.5, d=d_, k=k_, t0_=t0__)
            b = cpr(win, w, 0.0, d=d_, k=k_, t0_=t0__)
            res[cid] = paired_boot(a, b, m[lab].to_numpy(float))
        sens[name] = res
        log("sens", name)
    out["parameter_sensitivity"] = sens

    # -- 13. farms on each walk (matched-cohort graphs at 31 May 2026) --
    sybil = {}
    W = [x.lower() for x in matched]
    Wset = set(W)
    farm = [f"0xfa{i:038x}" for i in range(1, 11)]
    target = "0xfb" + "0" * 38
    ring = [f"0xfc{i:038x}" for i in range(20)]
    se = xr["se"]

    def star_edges(src_dst_weight):
        return pd.DataFrame(src_dst_weight, columns=["from_node", "to_node", "weight"])

    # (a) EndorseRank: bounded weights, uniform restarts
    ea_vt = filter_subgraph_edges(build_endorserank_vt_edges(xr["latest"], se, K, T0, BV)[0], Wset)
    base, nodes, rank, _ = coupled([(ea_vt, 1.0)])
    has_in = set(ea_vt["to_node"])
    c_common = float(np.median([base[u] for u in nodes if u not in has_in]))
    w_sampled = max(base.get(u, 0.0) for u in W)
    s_edges = star_edges([(f, target, 1.0) for f in farm] + [(target, f, 1.0) for f in farm])
    aug, *_ = coupled([(pd.concat([ea_vt, s_edges], ignore_index=True), 1.0)])
    r_edges = star_edges([(ring[i], ring[(i + 1) % 20], 1.0) for i in range(20)])
    augr, nodes_r, _, _ = coupled([(pd.concat([ea_vt, r_edges], ignore_index=True), 1.0)])
    sybil["endorserank"] = {"nodes": len(nodes), "b_common": c_common, "max_sampled": w_sampled,
                            "max_all_nodes": max(base.values()), "star_target": aug[target],
                            "star_over_max_sampled": aug[target] / w_sampled, "star_over_max_all": aug[target] / max(base.values()),
                            "ring_multiple_of_share": sum(augr[x] for x in ring) / (20 / len(nodes_r))}
    # (b) AWP, published form: bounded weights and activity restarts; the farm pays one base unit
    trans = xr["trans"]
    def fake_transfers(pairs):
        return pd.DataFrame({"block_timestamp": se, "block_number": 0, "transaction_hash": [f"0xf{i}" for i in range(len(pairs))],
                             "log_index": 0, "token_address": "0xfeed", "from_address": [p[0] for p in pairs],
                             "to_address": [p[1] for p in pairs], "value": 1})
    def awp_scores(tr_frame, wallets):
        edges, act = build_awp_paper_edges(tr_frame, se, K, T0, BV)
        edges = filter_subgraph_edges(edges, set(wallets))
        s, nd, _, _ = coupled([(edges, 1.0)], teleport=act or None)
        return s, nd
    base_awp, nodes_awp = awp_scores(trans, W)
    max_awp = max(base_awp.get(u, 0.0) for u in W)
    star_tr = fake_transfers([(f, target) for f in farm] + [(target, f) for f in farm])
    aug_awp, _ = awp_scores(pd.concat([trans, star_tr], ignore_index=True), W + farm + [target])
    ring_tr = fake_transfers([(ring[i], ring[(i + 1) % 20]) for i in range(20)])
    augr_awp, nodes_r_awp = awp_scores(pd.concat([trans, ring_tr], ignore_index=True), W + ring)
    sybil["awp_published"] = {"nodes": len(nodes_awp), "max_sampled": max_awp, "max_all_nodes": max(base_awp.values()),
                              "star_target": aug_awp[target], "star_over_max_sampled": aug_awp[target] / max_awp,
                              "ring_multiple_of_share": sum(augr_awp[x] for x in ring) / (20 / len(nodes_r_awp))}
    # (c) C-PR at lambda = 0.5 on the raw layers; farm edges in the authorization layer only
    ea_raw, et_raw = layers("registered", W)
    base_c, nodes_c, _, _ = coupled([(ea_raw, 0.5), (et_raw, 0.5)])
    max_c = max(base_c.get(u, 0.0) for u in W)
    aug_c, *_ = coupled([(pd.concat([ea_raw, s_edges], ignore_index=True), 0.5), (et_raw, 0.5)])
    augr_c, nodes_rc, _, _ = coupled([(pd.concat([ea_raw, r_edges], ignore_index=True), 0.5), (et_raw, 0.5)])
    sybil["cpr_0.5"] = {"nodes": len(nodes_c), "max_sampled": max_c, "max_all_nodes": max(base_c.values()),
                        "star_target": aug_c[target], "star_over_max_sampled": aug_c[target] / max_c,
                        "ring_multiple_of_share": sum(augr_c[x] for x in ring) / (20 / len(nodes_rc))}
    out["sybil"] = sybil
    log("sybil", sybil)

    args.out.write_text(json.dumps(r3(out), indent=1), encoding="utf-8")
    log("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
