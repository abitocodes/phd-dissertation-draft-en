#!/usr/bin/env python3
"""Shared loader for the scripts of Manuscript A (PLOS ONE).

Every number in the tables, Fig 1 and S1 Table comes from one of two places:

* the machine-readable summaries published in the public repository
  https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation
  (``experiments/data/3-published-results-for-thesis/`` for the registered analysis and
  its subfolder ``revised-contract-12m/`` for the contract-graph analysis, the main
  analysis of the paper), each checked here against the ``SHA256SUMS.txt`` published
  next to it;
* ``analysis/closed-form/closed_form_check.json`` of this repository, which copies the
  closed-form check from the same summaries and checks it against the per-contract scores.

The path to a checkout of that repository must be given with ``--repo PATH`` or the
environment variable ``CONTRACT_REP_REPO``; nothing is guessed. A checkout of the authors'
private repository, which holds the public one as a submodule, also works (``--phd-works``
and ``PHD_WORKS`` are kept as aliases).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent          # manuscripts/A-plos-one
ROOT = HERE.parents[1]                          # repository root
ANALYSIS = ROOT / "analysis"

# The experiment folder: experiments/ in a checkout of the public repository; in a checkout
# of the authors' repository, the first of the other two (the submodule that holds the public
# repository); the last is its name in the authors' repository before the study moved.
EXPERIMENT_DIRS = (
    "experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
REV = "revised-contract-12m"     # main analysis: the contract-graph analysis

# The four runs of the discovery-order test: (freeze, reveal mode). The first one decides.
RUNS = (("tobs", "both"), ("tobs", "out"), ("t1", "both"), ("t1", "out"))

# name -> (analysis folder relative to PUB, file inside it)
FILES = {
    "rev_same": (REV, "same-window/eval_summary.json"),
    "rev_w0": (REV, "holdout-w0/eval_summary.json"),
    "rev_w1": (REV, "window-w1/eval_summary.json"),
    "rev_sup": (REV, "supplementary/supplementary.json"),
    "rev_bench": (REV, "benchmark/benchmark.json"),
    "rev_desc": (REV, "describe/describe.json"),
    "rev_cohort": (REV, "cohort/matched_cohort.json"),
    "rev_cohort_t1": (REV, "cohort/cohort_t1.json"),
    "rev_spenders_w0": (REV, "cohort/spenders_w0.json"),
    "rev_spenders_w1": (REV, "cohort/spenders_w1.json"),
    "rev_constants": (REV, "usd/constants.json"),
    "rev_usd_inputs": (REV, "usd/usd_inputs.json"),
    "rev_balance": (REV, "typing/balance_audit.json"),
    "rev_pilot": (REV, "discovery/feasibility_t1.json"),
    **{f"rev_disc_{t}_{m}": (REV, f"discovery/discovery_{t}_{m}.json") for t, m in RUNS},
    "reg_same": ("", "same-window/eval_summary.json"),
    "reg_w0": ("", "holdout-w0/eval_summary.json"),
    "reg_w1": ("", "registered-w1/eval_summary.json"),
    "reg_sup": ("", "supplementary/supplementary.json"),
    "reg_desc": ("", "describe/describe.json"),
    "reg_cohort": ("", "cohort/matched_cohort.json"),
    "reg_bench": ("", "benchmark/benchmark.json"),
    "reg_manifest": ("", "registered-w1/extraction_manifest.json"),
}
# Text files of the published folder that the scripts read (checked like the summaries).
TEXT_FILES = {
    "rev_overlay": (REV, "config/overlay_contract12m.yaml"),
    "rev_config": (REV, "config/contract_reputation.yaml"),
}

_ARGS: argparse.Namespace | None = None


def parse_args(description: str) -> argparse.Namespace:
    global _ARGS
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--repo", "--phd-works", dest="phd_works",
                   default=os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS"),
                   help="path to a checkout of the public repository (or set CONTRACT_REP_REPO)")
    a, rest = p.parse_known_args()
    if not a.phd_works:
        p.error("give --repo PATH or set the environment variable CONTRACT_REP_REPO")
    a.rest = rest                                   # what the calling script reads itself (file names)
    _ARGS = a
    return a


@lru_cache(maxsize=None)
def experiments_dir() -> Path:
    if _ARGS is None:
        raise RuntimeError("call parse_args() first")
    base = Path(_ARGS.phd_works).expanduser().resolve()
    for rel in EXPERIMENT_DIRS:
        d = base / rel
        if (d / PUB / REV).is_dir():
            return d
    sys.exit(f"no experiment folder with {PUB}/{REV} under {base}")


def sha256_published(path: Path) -> str:
    """SHA-256 of the file with CRLF line ends (SHA256SUMS.txt was written on a CRLF checkout)."""
    b = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(b).hexdigest()


@lru_cache(maxsize=None)
def _sums(pub_dir: Path) -> dict[str, str]:
    out = {}
    for line in (pub_dir / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, name = line.split(None, 1)
            out[name.strip().lstrip("*")] = h
    return out


def _checked_path(folder: str, rel: str) -> Path:
    pub_dir = experiments_dir() / PUB / folder
    path = pub_dir / rel
    want = _sums(pub_dir).get(rel)
    if want is None:
        sys.exit(f"{rel} is not listed in {pub_dir / 'SHA256SUMS.txt'}")
    got = sha256_published(path)
    if got != want:
        sys.exit(f"checksum mismatch for {path}: {got} != {want}")
    return path


def source_path(name: str) -> Path:
    folder, rel = {**FILES, **TEXT_FILES}[name]
    return experiments_dir() / PUB / folder / rel


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Load a published summary after checking it against SHA256SUMS.txt."""
    return json.loads(_checked_path(*FILES[name]).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_text(name: str) -> str:
    """A published text file (configuration), checked against SHA256SUMS.txt."""
    return _checked_path(*TEXT_FILES[name]).read_text(encoding="utf-8")


def discovery(tag: str, mode: str) -> dict:
    """One run of the discovery-order test: tag 'tobs' or 't1', mode 'both' or 'out'."""
    return load(f"rev_disc_{tag}_{mode}")


@lru_cache(maxsize=None)
def digest_text(folder: str = REV) -> str:
    return _checked_path(folder, "results_digest.md").read_text(encoding="utf-8")


@lru_cache(maxsize=None)
def closed_form() -> dict:
    """analysis/closed-form/closed_form_check.json, rows keyed by (analysis, window)."""
    d = json.loads((ANALYSIS / "closed-form/closed_form_check.json").read_text(encoding="utf-8"))
    return {(r["analysis"], r["window"]): r for r in d["rows"]}


# --------------------------------------------------------------------------- windows
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _ymd(ts: str) -> tuple[int, int, int]:
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", ts)
    if not m:
        sys.exit(f"not a timestamp: {ts}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def day(ts: str, year: bool = True) -> str:
    """'1 Jul 2025' from '2025-07-01 00:00:00 UTC'."""
    y, m, d = _ymd(ts)
    return f"{d} {MONTHS[m - 1]} {y}" if year else f"{d} {MONTHS[m - 1]}"


def _yaml_value(text: str, block: str, key: str) -> str:
    """The quoted value of ``key`` inside the top-level block ``block`` of a small YAML file."""
    m = re.search(rf"^{block}:[^\n]*\n((?:[ \t]+[^\n]*\n|[ \t]*\n)+)", text, re.M)
    if not m:
        sys.exit(f"no block {block} in the configuration")
    k = re.search(rf"^[ \t]+{key}:\s*\"([^\"]+)\"", m.group(1), re.M)
    if not k:
        sys.exit(f"no key {block}.{key} in the configuration")
    return k.group(1)


@lru_cache(maxsize=None)
def windows() -> dict[str, tuple[str, str]]:
    """Score and label windows of the main analysis, each as (first instant, last instant).

    The window starts come from the published overlay of the contract-graph analysis, the
    freezes and label windows from the published base configuration; the summaries must agree.
    """
    ov, cfg = load_text("rev_overlay"), load_text("rev_config")
    w = {
        "score_tobs": (_yaml_value(ov, "period", "start_ts"), _yaml_value(cfg, "period", "observation_end")),
        "score_t1": (_yaml_value(ov, "holdout", "start_ts"), _yaml_value(cfg, "holdout", "score_end")),
        "label_w0": (_yaml_value(cfg, "holdout", "outcome_start"), _yaml_value(cfg, "holdout", "outcome_end")),
        "label_w1": (_yaml_value(cfg, "registered_window", "outcome_start"),
                     _yaml_value(cfg, "registered_window", "outcome_end")),
        "registered_score_start": (_yaml_value(cfg, "period", "start_ts"), ""),
    }
    assert w["score_tobs"][1] == load("rev_same")["anchor"], "T_obs differs from the same-window summary"
    assert w["score_t1"][1] == load("rev_w0")["freeze"], "t1 differs from the W0 summary"
    assert list(w["label_w0"]) == load("rev_w0")["labels"], "the W0 label window differs from the W0 summary"
    assert list(w["score_t1"]) == load("rev_constants")["window"], "the W0 score window differs from constants.json"
    return w


def span(key: str, sep: str = " -- ") -> str:
    """'1 Jul 2025 -- 30 Jun 2026' for a window of windows()."""
    a, b = windows()[key]
    return f"{day(a)}{sep}{day(b)}"


# --------------------------------------------------------------------------- discovery helpers
def auc(run: dict, hot: str, ordering: str, x: str = "x=0.1") -> dict | float:
    """The AUC entry of an ordering (a dict with auc, lo, hi) or the value of a reference curve."""
    v = run["auc"][hot][ordering]
    return v[x] if isinstance(v, dict) else v


def curve_at(run: dict, kind: str, imp: str, ordering: str, share: float) -> float:
    """Mean over seeds of a curve (P_ST, P_CS, captured) at the grid point nearest ``share`` of the visits."""
    grid = run["curves"]["grid"]
    n = run["sizes"]["universe"]["U"]
    i = min(range(len(grid)), key=lambda j: abs(grid[j] / n - share))
    c = run["curves"][kind][imp][ordering]
    return (c["mean"] if isinstance(c, dict) else c)[i]


# --------------------------------------------------------------------------- formatting
def num(x: float, sign: bool = False, nd: int = 3) -> str:
    """Number in LaTeX text mode: minus as $-$, optional plus sign."""
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    if s.lstrip("+-") == f"{0:.{nd}f}":           # avoid -0.000
        s = ("+" if sign else "") + s.lstrip("+-")
    return s.replace("-", "$-$")


def ci(lo: float, hi: float, nd: int = 3) -> str:
    return f"[{num(lo, nd=nd)}, {num(hi, nd=nd)}]"


def tau_ci(d: dict) -> str:
    """'0.585 [0.578, 0.592]' from a block with kendall_tau/mean_tau/tau and ci_low/ci_high."""
    t = d.get("kendall_tau", d.get("mean_tau", d.get("tau")))
    lo = d.get("ci_low", d.get("ci95_low"))
    hi = d.get("ci_high", d.get("ci95_high"))
    return f"{num(t)} {ci(lo, hi)}"


def delta_ci(d: dict) -> str:
    """'+0.392 [0.380, 0.405]' from a contrast block."""
    lo = d.get("ci_low", d.get("ci95_low"))
    hi = d.get("ci_high", d.get("ci95_high"))
    return f"{num(d['delta_tau'], sign=True)} {ci(lo, hi)}"


def auc_ci(d: dict) -> str:
    """'0.1085 [0.1036, 0.1136]' from an AUC entry (auc, lo, hi), four decimals."""
    return f"{num(d['auc'], nd=4)} {ci(d['lo'], d['hi'], nd=4)}"


def d4(d: dict) -> str:
    """'+0.0520 [+0.0485, +0.0558]' from a discovery contrast (point, lo, hi), four decimals."""
    return (f"{num(d['point'], sign=True, nd=4)} "
            f"[{num(d['lo'], sign=True, nd=4)}, {num(d['hi'], sign=True, nd=4)}]")


def intc(n: int) -> str:
    return f"{int(n):,}".replace(",", "{,}")


def pct(x: float, nd: int = 1) -> str:
    return f"{100 * x:.{nd}f}\\%"
