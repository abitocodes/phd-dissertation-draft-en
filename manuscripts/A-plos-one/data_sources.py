#!/usr/bin/env python3
"""Shared loader for the scripts of Manuscript A (PLOS ONE).

Every number in the tables, Fig 1 and S2 Table comes from one of two places:

* the machine-readable summaries published in the experiment repository ``phd_works``
  (``experiments/data/3-published-results-for-thesis/`` for the registered analysis and
  its subfolder ``revised-usd-12m/`` for the revised analysis, whose scores come from the
  twelve months before each freeze), each checked here against the ``SHA256SUMS.txt``
  published next to it;
* the two JSON files of ``analysis/`` in this repository
  (``analysis/closed-form/closed_form_check.json`` and
  ``analysis/neutral-label/results.json``), which copy and check values from the same
  summaries.

The path to a ``phd_works`` checkout must be given with ``--phd-works PATH`` or the
environment variable ``PHD_WORKS``; nothing is guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent          # manuscripts/A-plos-one
ROOT = HERE.parents[1]                          # repository root
ANALYSIS = ROOT / "analysis"

# The experiment folder has two names in the history: in the commits of the plan, the
# registration and the registered results (43d8045 to 8d8b568) it was the second entry,
# and in the commit of the revised results (950a7a4) it is the first.
EXPERIMENT_DIRS = (
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
REV = "revised-usd-12m"          # revised analysis: twelve-month score windows

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
    "rev_tokens": (REV, "usd/token_rows_12m.json"),
    "rev_constants": (REV, "usd/constants.json"),
    "rev_manifest": (REV, "registered-w1/extraction_manifest.json"),
    "reg_same": ("", "same-window/eval_summary.json"),
    "reg_w0": ("", "holdout-w0/eval_summary.json"),
    "reg_w1": ("", "registered-w1/eval_summary.json"),
    "reg_sup": ("", "supplementary/supplementary.json"),
    "reg_desc": ("", "describe/describe.json"),
}

_ARGS: argparse.Namespace | None = None


def parse_args(description: str) -> argparse.Namespace:
    global _ARGS
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"),
                   help="path to a phd_works checkout (or set PHD_WORKS)")
    a, _ = p.parse_known_args()
    if not a.phd_works:
        p.error("give --phd-works PATH or set the environment variable PHD_WORKS")
    _ARGS = a
    return a


@lru_cache(maxsize=None)
def experiments_dir() -> Path:
    if _ARGS is None:
        raise RuntimeError("call parse_args() first")
    base = Path(_ARGS.phd_works).expanduser().resolve()
    for rel in EXPERIMENT_DIRS:
        d = base / rel
        if (d / PUB).is_dir():
            return d
    sys.exit(f"no experiment folder with {PUB} under {base}")


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


def source_path(name: str) -> Path:
    folder, rel = FILES[name]
    return experiments_dir() / PUB / folder / rel


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Load a published summary after checking it against SHA256SUMS.txt."""
    folder, rel = FILES[name]
    pub_dir = experiments_dir() / PUB / folder
    path = pub_dir / rel
    want = _sums(pub_dir).get(rel)
    if want is None:
        sys.exit(f"{rel} is not listed in {pub_dir / 'SHA256SUMS.txt'}")
    got = sha256_published(path)
    if got != want:
        sys.exit(f"checksum mismatch for {path}: {got} != {want}")
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def closed_form() -> dict:
    """analysis/closed-form/closed_form_check.json, rows keyed by (analysis, window)."""
    d = json.loads((ANALYSIS / "closed-form/closed_form_check.json").read_text(encoding="utf-8"))
    return {(r["analysis"], r["window"]): r for r in d["rows"]}


@lru_cache(maxsize=None)
def neutral() -> dict:
    """analysis/neutral-label/results.json."""
    return json.loads((ANALYSIS / "neutral-label/results.json").read_text(encoding="utf-8"))


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


def intc(n: int) -> str:
    return f"{n:,}".replace(",", "{,}")


def pct(x: float, nd: int = 1) -> str:
    return f"{100 * x:.{nd}f}\\%"
