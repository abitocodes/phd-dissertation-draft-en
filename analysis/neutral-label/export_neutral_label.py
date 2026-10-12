#!/usr/bin/env python3
"""Export the comparison on trader outcomes built from neither edge type (rules R1-R3).

The W1 registration of phd_works (docs/registration_w1.md, commit 0d3a057; quoted in
PLAN.md) sets allowance-side against transfer-side scores on GMX V2 contract traders,
whose closes enter neither graph, in W1 (primary) and W0 (secondary). The pipeline
computes every value (scripts/run_registered.py, function ``neutral``) and stores it
under the keys ``neutral_w1``, ``neutral_w0`` and ``neutral_rules`` of the W1 evaluation
summary. This script

1. verifies the registration file against the SHA-256 in the W1 extraction manifest,
   the quotes in PLAN.md against the documents, the six pairs against the code, and the
   two summaries against the SHA256SUMS.txt published next to them;
2. copies every contrast of the grid (pairs P, Q, layers, er_awp, cpr0_awp, er_degree;
   six labels; W1 and W0; revised and registered analysis), the stratified contrasts,
   the single-score coefficients, the recipient comparison, the influence check and
   the verdicts of R1-R3 into results.json, under names that the manuscripts use;
3. recomputes the same values from the per-contract trader score files with an
   independent implementation of Kendall's tau_b and of the paired bootstrap
   (2,000 resamples, seed 42) and reports the largest differences (``recompute_check``).
   This is a check of the copy; results.json reports the pipeline's values.

Usage (the path to a phd_works checkout is required):

    PHD_WORKS=/path/to/phd_works python export_neutral_label.py
    python export_neutral_label.py --phd-works /path/to/phd_works [--no-recompute]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
OUT = HERE / "results.json"
PLAN = HERE / "PLAN.md"

EXPERIMENT_DIRS = (
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
PROC = "data/2-processed-tables-and-evaluations"
REGISTRATION_COMMIT = "0d3a057e4f0c8473d36d89fbe33c24deff0c9911"
REGISTRATION_COMMITTED_UTC = "2026-10-09T16:49:32Z"
REVISION_COMMITS = {"a897475": "2026-10-10T07:54:35Z", "09dfc32": "2026-10-10T08:12:44Z",
                    "2705b28": "2026-10-10T11:24:01Z"}

N_BOOT, SEED = 2000, 42
LIQ = "liquidation_free_rate"
STRATA_EDGES = (3, 5, 10, 25)  # strata of closes 3-4, 5-9, 10-24, 25+ (labels.strata_tau)

# (name, a, b, description, role); a, b and their order as NEUTRAL_PAIRS in scripts/run_registered.py.
PAIRS = (
    ("P", "in_approve_degree", "in_degree", "in-approve degree minus transfer in-degree",
     "decision contrast (R1, R3); Bonferroni 97.5% interval on the liquidation-free close rate"),
    ("Q", "endorserank_activity", "awp", "EndorseRank (activity restarts) minus AWP",
     "decision contrast (R2); Bonferroni 97.5% interval on the liquidation-free close rate"),
    ("layers", "cpr_l100", "cpr_l0", "C-PR (λ=1) minus C-PR (λ=0)", "registered pair, reported"),
    ("er_awp", "endorserank", "awp", "EndorseRank minus AWP", "registered pair, reported"),
    ("cpr0_awp", "cpr_l0", "awp", "C-PR (λ=0) minus AWP",
     "registered, reported to isolate AWP's weights and restarts"),
    ("er_degree", "endorserank", "in_approve_degree", "EndorseRank minus in-approve degree",
     "not named in the registration document; in the evaluation code committed with it"),
)
LABELS = {
    "liquidation_free_rate": ("liquidation-free close rate", "primary label"),
    "no_liquidation": ("no liquidation", "reported"),
    "profitable_closes": ("profitable closes", "reported; grows with the number of closes"),
    "realized_gain": ("realized gain", "reported; grows with the number of closes"),
    "profitable_share": ("profitable share", "reported; enters R3"),
    "non_loss_share": ("non-loss share", "reported; enters R3"),
}
METHODS = {
    "endorserank": "EndorseRank",
    "endorserank_activity": "EndorseRank (activity restarts)",
    "awp": "AWP",
    "cpr_l100": "C-PR (λ=1)",
    "cpr_l0": "C-PR (λ=0)",
    "cpr_l25": "C-PR (λ=0.25)",
    "cpr_l50": "C-PR (λ=0.5)",
    "cpr_l75": "C-PR (λ=0.75)",
    "spr": "S-PR",
    "in_approve_degree": "in-approve degree at the freeze",
    "in_degree": "transfer in-degree at the freeze",
}
# Wording of the conclusions, fixed in the registration (section 3, last paragraph).
WORDING = {
    ("R1", True): "the approval count at the freeze ranked contract traders above the transfer count on later "
                  "liquidation avoidance",
    ("R1", False): "no count-level lead of allowance over transfer on later liquidation avoidance",
    ("R2", True): "the same sentence for the PageRank pair",
    ("R2", False): "the PageRank versions are not resolved",
    ("R3", True): "the signal concerns forced-liquidation avoidance, not trading success",
}
ANALYSES = {
    "revised": {
        "pub": f"{PUB}/revised-usd",
        "proc": f"{PROC}/revised-usd",
        "w1_dir": "window-w1",
        "status": ("Re-analysis: amounts in USD over WETH, USDC, USDT0, ARB and WBTC "
                   "(docs/revision_price_weighting.md), decided after the registered results were known and "
                   "committed before any revised score (a897475, 09dfc32, 2705b28). The registered rules and "
                   "thresholds are applied to it. Main analysis of the thesis (Chapter 4); never a registered result."),
    },
    "registered": {
        "pub": PUB,
        "proc": PROC,
        "w1_dir": "registered-w1",
        "status": ("Registered analysis (raw base units, every ERC-20): rules fixed in docs/registration_w1.md "
                   "(commit 0d3a057) before the W1 logs were extracted. Thesis Appendix 8.6."),
    },
}


# --------------------------------------------------------------------------- paths and provenance


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"),
                   help="path to a phd_works checkout (or set PHD_WORKS)")
    p.add_argument("--experiments-subdir", default=None,
                   help="experiment folder relative to phd_works (default: the first of "
                        + ", ".join(EXPERIMENT_DIRS) + " that exists)")
    p.add_argument("--out", default=str(OUT), help="output JSON (default: %(default)s)")
    p.add_argument("--no-recompute", action="store_true",
                   help="skip the recomputation from the trader score files")
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


def git(repo: Path, *args: str) -> bytes | None:
    try:
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def crlf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def published_sums(pub_dir: Path) -> dict[str, str]:
    sums = {}
    for line in (pub_dir / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            sums[name.strip().lstrip("*")] = h
    return sums


def verify_registration(phd: Path, exp: Path) -> dict:
    """Hash the registration file wherever it is kept and compare with the manifest.

    The manifest hashed a Windows checkout (CRLF line ends), so each copy is hashed
    in its CRLF form; the LF form, as git stores it, is reported as well.
    """
    manifest_rel = f"{PUB}/registered-w1/extraction_manifest.json"
    manifest = json.loads((exp / manifest_rel).read_text(encoding="utf-8"))
    expected = manifest["sha256"]["docs/registration_w1.md"]
    copies = {}
    for rel in ("docs/registration_w1.md", f"{PUB}/docs/registration_w1.md", f"{PUB}/revised-usd/docs/registration_w1.md"):
        b = (exp / rel).read_bytes()
        copies[rel] = {"sha256_lf": sha(b.replace(b"\r\n", b"\n")), "sha256_crlf": sha(crlf(b)),
                       "matches_manifest": sha(crlf(b)) == expected}
    at_commit = None
    for rel in EXPERIMENT_DIRS:
        b = git(phd, "show", f"{REGISTRATION_COMMIT}:{rel}/docs/registration_w1.md")
        if b is not None:
            at_commit = {"path": f"{rel}/docs/registration_w1.md", "sha256_lf": sha(b),
                         "sha256_crlf": sha(crlf(b)), "matches_manifest": sha(crlf(b)) == expected}
            break
    return {
        "file": "docs/registration_w1.md",
        "commit": REGISTRATION_COMMIT,
        "committed_utc": REGISTRATION_COMMITTED_UTC,
        "manifest": manifest_rel,
        "sha256_in_manifest": expected,
        "manifest_registration_commit": manifest.get("registration_commit"),
        "w1_extraction_started_utc": manifest.get("started_at"),
        "w1_extraction_finished_utc": manifest.get("finished_at"),
        "override_used": manifest.get("override_used"),
        "copies": copies,
        "at_commit": at_commit,
        "verified": all(c["matches_manifest"] for c in copies.values())
                    and (at_commit is None or at_commit["matches_manifest"]),
    }


def verify_plan_quotes(exp: Path) -> dict:
    """Every line of each ```text block of PLAN.md must be a whole line of a source document."""
    docs = {name: (exp / "docs" / name).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
            for name in ("registration_w1.md", "revision_price_weighting.md")}
    blocks = re.findall(r"```text\n(.*?)\n```", PLAN.read_text(encoding="utf-8"), flags=re.S)
    lines = [ln for blk in blocks for ln in blk.split("\n") if ln.strip()]
    missing = [ln for ln in lines if not any(ln in d for d in docs.values())]
    reg_text = "\n".join(docs["registration_w1.md"])
    wording = {f"{k[0]}_{'holds' if k[1] else 'fails'}": v in reg_text for k, v in WORDING.items()}
    return {"quoted_blocks": len(blocks), "quoted_lines": len(lines), "lines_not_found": missing,
            "wording_found_in_registration": wording,
            "verified": bool(blocks) and not missing and all(wording.values())}


def verify_pairs(exp: Path) -> dict:
    code = (exp / "scripts" / "run_registered.py").read_text(encoding="utf-8")
    m = re.search(r"NEUTRAL_PAIRS = \[(.*?)\]", code, flags=re.S)
    found = re.findall(r'\("(\w+)", "(\w+)", "(\w+)"\)', m.group(1)) if m else []
    mine = [(n, a, b) for n, a, b, _, _ in PAIRS]
    return {"code": "scripts/run_registered.py (NEUTRAL_PAIRS)", "pairs_in_code": [list(t) for t in found],
            "verified": found == mine}


# --------------------------------------------------------------------------- copy of the published values


def contrast_rec(r: dict | None, n: int, key: str) -> dict:
    r = r or {}
    return {
        "delta_tau": r.get("delta_tau"),
        "ci95_low": r.get("ci_low"),
        "ci95_high": r.get("ci_high"),
        "ci975_low": r.get("ci975_low"),
        "ci975_high": r.get("ci975_high"),
        "tau_a": r.get("a_tau"),
        "tau_b": r.get("b_tau"),
        "share_positive": r.get("share_positive"),
        "n": n,
        "B": r.get("n_boot"),
        "source_key": key,
    }


def tau_rec(r: dict, n: int, key: str) -> dict:
    return {"tau": r.get("kendall_tau"), "ci95_low": r.get("ci_low"), "ci95_high": r.get("ci_high"),
            "n": n, "B": r.get("n_boot"), "source_key": key}


def window_rec(nb: dict, key: str, window: str, dates: dict, w1_summary: dict) -> dict:
    n = int(nb["n"])
    pairs = {name: (a, b) for name, a, b, _, _ in PAIRS}
    contrasts = {}
    for name in pairs:
        contrasts[name] = {lab: contrast_rec(nb["grid"][name].get(lab), n, f"{key}.grid.{name}.{lab}")
                           for lab in LABELS}
    stratified = {}
    for name, r in nb["stratified"].items():
        rec = contrast_rec(r, n, f"{key}.stratified.{name}")
        rec["label"] = LIQ
        rec["B_note"] = (f"{N_BOOT} resamples drawn (the main index matrix); the summary does not record how many "
                         "gave a stratified value (see recompute_check)")
        stratified[name] = rec
    infl = contrast_rec(nb["influence_without_top10"], n - 10, f"{key}.influence_without_top10")
    infl.update({"pair": "P", "label": LIQ, "dropped": "the ten traders of highest in-approve degree"})
    out = {
        "freeze": dates["freeze"],
        "label_window": dates["labels"],
        "role": dates["role"],
        "n": n,
        "B": N_BOOT,
        "seed": SEED,
        "max_in_approve_degree": nb["max_in_approve_degree"],
        "contrasts": contrasts,
        "stratified": stratified,
        "taus": {m: {lab: tau_rec(nb["taus"][m][lab], n, f"{key}.taus.{m}.{lab}") for lab in LABELS}
                 for m in nb["taus"]},
        "recipients": {**nb["recipients"], "definition": "recipients: traders with in-approve degree above zero "
                                                          "at the freeze; others: the rest",
                       "source_key": f"{key}.recipients"},
        "influence_without_top10": infl,
    }
    if window == "W1":
        out["trader_counts"] = {
            "traders": w1_summary.get("traders"),
            "traders_with_a_liquidation": w1_summary.get("traders_liquidated"),
            "traders_all_closes_liquidated": w1_summary.get("traders_all_liquidated"),
            "source_keys": ["traders", "traders_liquidated", "traders_all_liquidated"],
        }
    return out


def rules_rec(w1: dict, w0: dict, published: dict) -> dict:
    p1, q1 = w1["contrasts"]["P"][LIQ], w1["contrasts"]["Q"][LIQ]
    inputs = {
        "R1": {"P_W1_ci975_low": p1["ci975_low"], "P_W1_stratified_ci95_low": w1["stratified"]["P"]["ci95_low"],
               "P_W0_delta_tau": w0["contrasts"]["P"][LIQ]["delta_tau"]},
        "R2": {"Q_W1_ci975_low": q1["ci975_low"], "Q_W0_delta_tau": w0["contrasts"]["Q"][LIQ]["delta_tau"]},
        "R3": {"P_W1_profitable_share_ci95_high": w1["contrasts"]["P"]["profitable_share"]["ci95_high"],
               "P_W1_non_loss_share_ci95_high": w1["contrasts"]["P"]["non_loss_share"]["ci95_high"]},
    }
    holds = {
        "R1": inputs["R1"]["P_W1_ci975_low"] > 0 and inputs["R1"]["P_W1_stratified_ci95_low"] > 0
              and inputs["R1"]["P_W0_delta_tau"] > 0,
        "R2": inputs["R2"]["Q_W1_ci975_low"] > 0 and inputs["R2"]["Q_W0_delta_tau"] > 0,
        "R3": inputs["R3"]["P_W1_profitable_share_ci95_high"] < 0 or inputs["R3"]["P_W1_non_loss_share_ci95_high"] < 0,
    }
    conditions = {
        "R1": "P_W1_ci975_low > 0 and P_W1_stratified_ci95_low > 0 and P_W0_delta_tau > 0",
        "R2": "Q_W1_ci975_low > 0 and Q_W0_delta_tau > 0",
        "R3": "P_W1_profitable_share_ci95_high < 0 or P_W1_non_loss_share_ci95_high < 0",
    }
    names = {"R1": "count-level lead", "R2": "PageRank-level lead", "R3": "specificity"}
    return {r: {"name": names[r], "holds": bool(published[r]), "condition": conditions[r], "inputs": inputs[r],
                "recomputed_from_inputs": bool(holds[r]), "matches_published": bool(holds[r]) == bool(published[r]),
                "registered_wording": WORDING.get((r, bool(published[r]))),
                "source_key": f"neutral_rules.{r}"} for r in ("R1", "R2", "R3")}


# --------------------------------------------------------------------------- independent recomputation


def _sign_cube(v: np.ndarray, idx: np.ndarray, chunk: int = 250) -> np.ndarray:
    """sign(v[i] - v[j]) for every pair of positions of every resample, as int8 (B x n x n)."""
    out = np.empty((idx.shape[0], idx.shape[1], idx.shape[1]), dtype=np.int8)
    for s in range(0, idx.shape[0], chunk):
        x = v[idx[s:s + chunk]]
        out[s:s + chunk] = (x[:, :, None] > x[:, None, :]).astype(np.int8) - (x[:, :, None] < x[:, None, :])
    return out


class Bootstrap:
    """Paired bootstrap over traders with tau_b from pair counts.

    tau_b = sum_{i<j} sign(dx) sign(dy) / sqrt(n_x n_y), where n_x (n_y) counts the pairs
    not tied in x (y); a resample with fewer than five members or a constant vector
    gives no value. Row b of the index matrix is the b-th row of
    numpy.random.default_rng(seed).integers(0, n, size=(B, n)).
    """

    def __init__(self, frame: pd.DataFrame, n_boot: int = N_BOOT, seed: int = SEED):
        self.f = frame
        self.n = len(frame)
        self.idx = np.random.default_rng(seed).integers(0, self.n, size=(n_boot, self.n))
        self.point_idx = np.arange(self.n)[None, :]
        self._cube: dict = {}
        self._samples: dict = {}

    def cube(self, col: str, point: bool = False) -> np.ndarray:
        k = (col, point)
        if k not in self._cube:
            self._cube[k] = _sign_cube(self.f[col].to_numpy(np.float64), self.point_idx if point else self.idx)
        return self._cube[k]

    def _tau(self, a: str, b: str, point: bool, mask: np.ndarray | None = None,
             size: np.ndarray | None = None) -> np.ndarray:
        ca, cb = self.cube(a, point), self.cube(b, point)
        if mask is None:
            s = (ca * cb).sum(axis=(1, 2), dtype=np.int64)
            na = np.abs(ca).sum(axis=(1, 2), dtype=np.int64)
            nb = np.abs(cb).sum(axis=(1, 2), dtype=np.int64)
            size = np.full(ca.shape[0], ca.shape[1])
        else:
            s = (ca * cb * mask).sum(axis=(1, 2), dtype=np.int64)
            na = (np.abs(ca) * mask).sum(axis=(1, 2), dtype=np.int64)
            nb = (np.abs(cb) * mask).sum(axis=(1, 2), dtype=np.int64)
        ok = (size >= 5) & (na > 0) & (nb > 0)
        t = np.full(ca.shape[0], np.nan)
        t[ok] = s[ok] / np.sqrt(na[ok].astype(np.float64) * nb[ok])
        return t

    def point(self, a: str, b: str) -> float | None:
        t = self._tau(a, b, True)[0]
        return None if np.isnan(t) else float(t)

    def samples(self, a: str, b: str) -> np.ndarray:
        if (a, b) not in self._samples:
            self._samples[(a, b)] = self._tau(a, b, False)
        return self._samples[(a, b)]

    def strata(self, a: str, b: str, closes: str, point: bool) -> np.ndarray:
        idx = self.point_idx if point else self.idx
        bins = np.digitize(self.f[closes].to_numpy(), STRATA_EDGES[1:])[idx]
        num = np.zeros(idx.shape[0])
        den = np.zeros(idx.shape[0])
        for k in np.unique(bins):
            inb = bins == k
            mask = (inb[:, :, None] & inb[:, None, :]).astype(np.int8)
            size = inb.sum(axis=1)
            t = self._tau(a, b, point, mask, size)
            ok = ~np.isnan(t)
            pairs = size * (size - 1) / 2
            num[ok] += t[ok] * pairs[ok]
            den[ok] += pairs[ok]
        out = np.full(idx.shape[0], np.nan)
        out[den > 0] = num[den > 0] / den[den > 0]
        return out


def _pct(x: np.ndarray, ci: float) -> tuple[float | None, float | None]:
    if x.size == 0:
        return None, None
    return float(np.percentile(x, (1 - ci) / 2 * 100)), float(np.percentile(x, (1 + ci) / 2 * 100))


def _contrast(bt: Bootstrap, a: str, c: str, lab: str, with_975: bool) -> dict | None:
    sa, sc = bt.samples(a, lab), bt.samples(c, lab)
    pa, pc = bt.point(a, lab), bt.point(c, lab)
    if pa is None or pc is None or np.isnan(sa).any() or np.isnan(sc).any():
        return None
    d = sa - sc
    lo, hi = _pct(d, 0.95)
    r = {"a_tau": pa, "b_tau": pc, "delta_tau": pa - pc, "ci_low": lo, "ci_high": hi,
         "share_positive": float(np.mean(d > 0)), "n_boot": int(d.size)}
    if with_975:
        r["ci975_low"], r["ci975_high"] = _pct(d, 0.975)
    return r


def recompute(frame: pd.DataFrame, methods: list[str]) -> dict:
    """The neutral block of run_registered.py, recomputed from a trader score frame (sorted by id)."""
    bt = Bootstrap(frame)
    grid = {}
    for name, a, c, _, _ in PAIRS:
        grid[name] = {lab: _contrast(bt, a, c, lab, name in ("P", "Q") and lab == LIQ) or {} for lab in LABELS}
    strat, strat_valid = {}, {}
    for name, a, c, _, _ in PAIRS[:2]:
        ta, tc = bt.strata(a, LIQ, "closes", True)[0], bt.strata(c, LIQ, "closes", True)[0]
        sa, sc = bt.strata(a, LIQ, "closes", False), bt.strata(c, LIQ, "closes", False)
        ok = ~np.isnan(sa) & ~np.isnan(sc)
        lo, hi = _pct(sa[ok] - sc[ok], 0.95)
        strat[name] = {"a_tau": float(ta), "b_tau": float(tc), "delta_tau": float(ta - tc), "ci_low": lo, "ci_high": hi}
        strat_valid[name] = int(ok.sum())
    taus = {}
    for m in methods:
        taus[m] = {}
        for lab in LABELS:
            s = bt.samples(m, lab)
            s = s[~np.isnan(s)]
            lo, hi = _pct(s, 0.95)
            taus[m][lab] = {"kendall_tau": bt.point(m, lab), "ci_low": lo, "ci_high": hi, "n_boot": int(s.size)}
    rec = frame["in_approve_degree"] > 0
    recipients = {}
    for grp, mask in (("recipients", rec), ("others", ~rec)):
        sub = frame.loc[mask]
        recipients[grp] = {"n": int(mask.sum()), "share_no_liquidation": float(sub["no_liquidation"].mean()),
                           **{f"mean_{lab}": float(sub[lab].mean()) for lab in (LIQ, "profitable_share", "non_loss_share")},
                           "median_closes": float(sub["closes"].median())}
    top = frame["in_approve_degree"].nlargest(10).index
    sub = frame.loc[~frame.index.isin(top)]
    influence = _contrast(Bootstrap(sub), "in_approve_degree", "in_degree", LIQ, False)
    return {"n": int(len(frame)), "taus": taus, "grid": grid, "stratified": strat, "recipients": recipients,
            "influence_without_top10": influence, "max_in_approve_degree": float(frame["in_approve_degree"].max()),
            "_stratified_valid_resamples": strat_valid}


def compare(pub, mine, path="", out=None):
    """Largest absolute difference per leaf name, and every leaf that differs beyond tolerance."""
    out = out if out is not None else {"max_abs_diff": {}, "mismatches": [], "leaves": 0}
    if isinstance(pub, dict):
        for k, v in pub.items():
            compare(v, (mine or {}).get(k) if isinstance(mine, dict) else None, f"{path}.{k}" if path else k, out)
        return out
    if isinstance(pub, bool) or pub is None or isinstance(pub, str):
        out["leaves"] += 1
        if pub != mine:
            out["mismatches"].append({"key": path, "published": pub, "recomputed": mine})
        return out
    out["leaves"] += 1
    leaf = path.rsplit(".", 1)[-1]
    if mine is None:
        out["mismatches"].append({"key": path, "published": pub, "recomputed": None})
        return out
    diff = abs(float(pub) - float(mine))
    out["max_abs_diff"][leaf] = max(out["max_abs_diff"].get(leaf, 0.0), diff)
    tol = 0 if isinstance(pub, int) else (1.0 / N_BOOT if leaf == "share_positive" else 1e-9)
    if diff > tol:
        out["mismatches"].append({"key": path, "published": pub, "recomputed": mine})
    return out


def load_frame(proc_dir: Path, stem: str) -> tuple[pd.DataFrame, list[dict]]:
    parts = sorted((proc_dir / stem).parent.glob(Path(stem).name + ".part*.parquet"))
    if not parts:
        raise SystemExit(f"no parquet parts for {proc_dir / stem}")
    df = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    df = df.rename(columns={"t1_in_approve_degree": "in_approve_degree", "t1_in_degree": "in_degree"})
    df = df.sort_values("id").set_index("id")
    return df, [{"file": str(p), "sha256": sha(p.read_bytes())} for p in parts]


# --------------------------------------------------------------------------- main


def main() -> int:
    a = parse_args()
    phd = Path(a.phd_works).expanduser().resolve()
    exp, exp_rel = experiments_dir(phd, a.experiments_subdir)
    cfg = yaml.safe_load((exp / PUB / "config" / "contract_reputation.yaml").read_text(encoding="utf-8"))
    dates = {
        "W1": {"freeze": cfg["registered_window"]["score_end"],
               "labels": [cfg["registered_window"]["outcome_start"], cfg["registered_window"]["outcome_end"]],
               "role": "primary window"},
        "W0": {"freeze": cfg["holdout"]["score_end"],
               "labels": [cfg["holdout"]["outcome_start"], cfg["holdout"]["outcome_end"]],
               "role": "secondary window"},
    }
    failures: list[str] = []
    registration = verify_registration(phd, exp)
    plan_quotes = verify_plan_quotes(exp)
    pairs_check = verify_pairs(exp)
    for name, chk in (("registration hash", registration), ("PLAN.md quotes", plan_quotes), ("pairs", pairs_check)):
        if not chk["verified"]:
            failures.append(f"{name} not verified")

    analyses, rows, recheck, frames = {}, [], {}, {}
    for analysis, A in ANALYSES.items():
        rel = f"{A['pub']}/{A['w1_dir']}/eval_summary.json"
        path = exp / rel
        h = sha(crlf(path.read_bytes()))
        listed = published_sums(exp / A["pub"]).get(f"{A['w1_dir']}/eval_summary.json")
        if listed != h:
            failures.append(f"{rel}: checksum differs from SHA256SUMS.txt")
        s = json.loads(path.read_text(encoding="utf-8"))
        windows = {w: window_rec(s[key], key, w, dates[w], s) for w, key in (("W1", "neutral_w1"), ("W0", "neutral_w0"))}
        rules = rules_rec(windows["W1"], windows["W0"], s["neutral_rules"])
        for r, v in rules.items():
            if not v["matches_published"]:
                failures.append(f"{analysis} {r}: verdict from the copied inputs differs from the summary")
        analyses[analysis] = {
            "status": A["status"],
            "source": {"file": rel, "sha256_published": h, "checksum_matches_SHA256SUMS": listed == h},
            "rules": rules,
            "windows": windows,
        }
        for w, W in windows.items():
            for name, pa, pb, desc, _ in PAIRS:
                for lab in LABELS:
                    rows.append({"analysis": analysis, "window": w, "pair": name, "a": pa, "b": pb,
                                 "contrast": desc, "label": lab, **W["contrasts"][name][lab]})

        if not a.no_recompute:
            recheck[analysis] = {}
            for w, key, stem in (("W1", "neutral_w1", f"{A['w1_dir']}/trader_scores"),
                                 ("W0", "neutral_w0", "holdout-w0/trader_scores")):
                frame, parts = load_frame(exp / A["proc"], stem)
                frames[(analysis, w)] = frame
                mine = recompute(frame, list(s[key]["taus"]))
                valid = mine.pop("_stratified_valid_resamples")
                cmp = compare(s[key], mine)
                r_pub = s["neutral_rules"]
                recheck[analysis][w] = {
                    "frame": [{"file": str(Path(p["file"]).relative_to(exp)), "sha256": p["sha256"]} for p in parts],
                    "leaves_compared": cmp["leaves"],
                    "max_abs_diff": cmp["max_abs_diff"],
                    "mismatches": cmp["mismatches"],
                    "stratified_valid_resamples": valid,
                    "agrees": not cmp["mismatches"],
                }
                if cmp["mismatches"]:
                    failures.append(f"{analysis} {w}: {len(cmp['mismatches'])} recomputed values differ")
                if w == "W1":
                    recheck[analysis]["_w1"] = mine
            # Verdicts of R1-R3 from the recomputed values.
            w1m = recheck[analysis].pop("_w1")
            p1, q1 = w1m["grid"]["P"][LIQ], w1m["grid"]["Q"][LIQ]
            w0p = analyses[analysis]["windows"]["W0"]["contrasts"]
            recheck[analysis]["rules_from_recomputed_W1"] = {
                "R1": bool(p1["ci975_low"] > 0 and w1m["stratified"]["P"]["ci_low"] > 0 and w0p["P"][LIQ]["delta_tau"] > 0),
                "R2": bool(q1["ci975_low"] > 0 and w0p["Q"][LIQ]["delta_tau"] > 0),
                "R3": bool(any(w1m["grid"]["P"][lab]["ci_high"] < 0 for lab in ("profitable_share", "non_loss_share"))),
            }
            if recheck[analysis]["rules_from_recomputed_W1"] != {k: bool(v) for k, v in s["neutral_rules"].items()}:
                failures.append(f"{analysis}: verdicts from recomputed W1 values differ")

    if not a.no_recompute:
        label_cols = list(LABELS) + ["closes", "liquidations", "losses"]
        recheck["label_columns_identical_across_analyses"] = {
            w: bool(len(frames[("revised", w)]) == len(frames[("registered", w)]) and all(
                np.array_equal(frames[("revised", w)][c].to_numpy(), frames[("registered", w)][c].to_numpy())
                for c in label_cols)) for w in ("W1", "W0")}
        recheck["method"] = ("Independent implementation in this script: tau_b from pair counts, index matrix "
                             "numpy.random.default_rng(42).integers(0, n, size=(2000, n)) over the score frame sorted "
                             "by contract id, percentile intervals (numpy.percentile, linear). W0 frames are the "
                             "holdout trader score files, whose t1 degree columns are the freeze-date degrees of W0. "
                             "Tolerance 1e-9 for coefficients and interval ends, 1/B for share_positive, exact for counts.")

    report = {
        "what": ("Allowance-side against transfer-side scores on GMX V2 contract traders, an outcome built from neither "
                 "edge type: every contrast of the grid, the stratified contrasts, single-score coefficients, the "
                 "recipient comparison, the influence check and the verdicts of R1-R3, for the revised and the "
                 "registered analysis in W1 (primary) and W0 (secondary). Copied from the evaluation summaries of "
                 "phd_works; nothing is computed here except recompute_check."),
        "generated_by": "analysis/neutral-label/export_neutral_label.py",
        "plan": "analysis/neutral-label/PLAN.md",
        "phd_works": {
            "repository": "https://github.com/abitocodes/phd_works",
            "head": (git(phd, "rev-parse", "HEAD") or b"").decode().strip() or None,
            "experiments_dir": exp_rel,
            "computed_by": ("scripts/run_registered.py, function neutral (pairs NEUTRAL_PAIRS); revised analysis with "
                            "CONTRACT_REP_VARIANT=usd, registered analysis with the variable unset"),
            "revision_commits_utc": REVISION_COMMITS,
        },
        "registration": registration,
        "plan_quotes": plan_quotes,
        "pairs_check": pairs_check,
        "bootstrap": {"B": N_BOOT, "seed": SEED, "paired": True, "interval": "percentile",
                      "ci975": "Bonferroni 97.5% interval, only for P and Q on the liquidation-free close rate; "
                               "null elsewhere"},
        "pairs": {n: {"a": pa, "b": pb, "a_name": METHODS[pa], "b_name": METHODS[pb], "contrast": d, "role": r}
                  for n, pa, pb, d, r in PAIRS},
        "labels": {k: {"name": v[0], "role": v[1]} for k, v in LABELS.items()},
        "methods": METHODS,
        "strata": "closes 3-4, 5-9, 10-24, 25 or more; tau_b within each stratum weighted by its pairs",
        "analyses": analyses,
        "contrast_rows": rows,
        "recompute_check": recheck if not a.no_recompute else None,
    }
    Path(a.out).write_text(json.dumps(report, indent=1, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

    print(f"wrote {a.out}: {len(rows)} contrast rows from {exp_rel}")
    print(f"  registration: manifest {registration['sha256_in_manifest'][:12]}..., verified={registration['verified']}"
          f"; PLAN.md quotes verified={plan_quotes['verified']} ({plan_quotes['quoted_lines']} lines)"
          f"; pairs verified={pairs_check['verified']}")
    for analysis, A in analyses.items():
        w1, w0 = A["windows"]["W1"], A["windows"]["W0"]
        p, q = w1["contrasts"]["P"][LIQ], w1["contrasts"]["Q"][LIQ]
        print(f"  {analysis:10s} W1 n={w1['n']} P {p['delta_tau']:+.3f} [{p['ci95_low']:.3f}, {p['ci95_high']:.3f}] "
              f"97.5% [{p['ci975_low']:.3f}, {p['ci975_high']:.3f}]; Q {q['delta_tau']:+.3f} "
              f"97.5% [{q['ci975_low']:.3f}, {q['ci975_high']:.3f}]; W0 n={w0['n']}; "
              + ", ".join(f"{r} {'holds' if v['holds'] else 'does not hold'}" for r, v in A["rules"].items()))
        if not a.no_recompute:
            for w in ("W1", "W0"):
                c = recheck[analysis][w]
                worst = max(c["max_abs_diff"].values()) if c["max_abs_diff"] else 0.0
                print(f"    recompute {w}: {c['leaves_compared']} values, largest difference {worst:.2e}, "
                      f"mismatches {len(c['mismatches'])}, stratified resamples {c['stratified_valid_resamples']}")
    if not a.no_recompute:
        print(f"  label columns identical across analyses: {recheck['label_columns_identical_across_analyses']}")
    if failures:
        print("FAILED:\n  " + "\n  ".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
