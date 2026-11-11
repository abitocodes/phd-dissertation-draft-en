#!/usr/bin/env python3
"""Compare the JSON file of analysis/ with the results digests of the experiment pipeline.

Each digest (``results_digest.md`` of the registered analysis and of the main one, the
contract-graph analysis) lists every quoted number with the summary file and key it comes
from. This script formats the values of ``closed-form/closed_form_check.json`` exactly as
the digests do (the function ``num`` below is that of ``scripts/publish_results.py``) and
compares the strings. It reports how many digest rows of the closed-form sections were
matched, lists any difference, and prints a sample.

Usage:

    CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation python compare_with_digest.py [--show 6]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPERIMENT_DIRS = (
    "experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
PREFIX = {"revised": f"{PUB}/revised-contract-12m/", "registered": f"{PUB}/"}
CF_FIELDS = {"common_value_c": "c", "spread_of_c": "spread_of_c", "spenders": "spenders",
             "depth_one_spenders": "depth_one_spenders", "within_1pct_all": "within_1pct_all",
             "within_1pct_depth_one": "within_1pct_depth_one", "within_1pct_deeper": "within_1pct_deeper",
             "tau_score_vs_delta": "tau_score_vs_delta"}
ROW = re.compile(r"^\| (?P<q>.*?) \| (?P<v>.*?) \| `(?P<file>[^`]+)` : `(?P<key>[^`]+)` \|$")
# Rows printed as the sample: (analysis, digest file, key).
SAMPLE = [
    ("revised", "same-window/eval_summary.json", "closed_form.common_value_c"),
    ("revised", "same-window/eval_summary.json", "closed_form.spenders"),
    ("revised", "same-window/eval_summary.json", "closed_form.within_1pct_deeper"),
    ("revised", "holdout-w0/eval_summary.json", "closed_form.tau_score_vs_delta"),
    ("registered", "same-window/eval_summary.json", "closed_form.depth_one_spenders"),
    ("registered", "holdout-w0/eval_summary.json", "closed_form.within_1pct_all"),
]


# ------------------------------------------------------------- formatting of scripts/publish_results.py


def num(v, digits: int = 3) -> str:
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return f"{v:,}"
    v = float(v)
    if v != 0 and abs(v) < 1e-3:
        return f"{v:.4g}"
    if abs(v) >= 1e3:
        return f"{int(v):,}" if v.is_integer() else f"{v:,.1f}"
    return f"{v:.{digits}f}"


# ------------------------------------------------------------- expected digest strings from analysis/


def expected_strings() -> dict[tuple[str, str, str], str]:
    exp: dict[tuple[str, str, str], str] = {}
    cf = json.loads((HERE / "closed-form" / "closed_form_check.json").read_text(encoding="utf-8"))
    for row in cf["rows"]:
        f = row["source"]["file"].removeprefix(PREFIX[row["analysis"]])
        for k, field in CF_FIELDS.items():
            exp[(row["analysis"], f, f"closed_form.{k}")] = num(row[field], 4)
    return exp


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--repo", "--phd-works", dest="phd_works",
                   default=os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS"),
                   help="path to a checkout of the public repository (or set CONTRACT_REP_REPO)")
    p.add_argument("--show", type=int, default=len(SAMPLE), help="number of sample rows to print")
    a = p.parse_args()
    if not a.phd_works:
        p.error("give --repo PATH or set the environment variable CONTRACT_REP_REPO")
    phd = Path(a.phd_works).expanduser().resolve()
    exp_dir = next((phd / rel for rel in EXPERIMENT_DIRS if (phd / rel / PUB).is_dir()), None)
    if exp_dir is None:
        raise SystemExit(f"no experiment folder with {PUB} under {phd}")

    digest: dict[tuple[str, str, str], tuple[str, str]] = {}
    for analysis, prefix in PREFIX.items():
        for line in (exp_dir / prefix / "results_digest.md").read_text(encoding="utf-8").splitlines():
            m = ROW.match(line)
            if m:
                digest[(analysis, m["file"], m["key"])] = (m["q"], m["v"].replace("\\|", "|"))

    expected = expected_strings()
    compared = mismatched = 0
    problems = []
    for k, want in expected.items():
        if k not in digest:
            continue
        compared += 1
        if digest[k][1] != want:
            mismatched += 1
            problems.append((k, digest[k][1], want))
    relevant = [k for k in digest if k[2].startswith("closed_form.")]
    not_covered = [k for k in relevant if k not in expected]
    no_digest_row = [k for k in expected if k not in digest]

    print(f"digest rows of the closed-form sections: {len(relevant)}; "
          f"compared with analysis/ outputs: {compared}; equal: {compared - mismatched}; differ: {mismatched}")
    print(f"digest rows without a value in analysis/: {len(not_covered)}; "
          f"analysis/ values without a digest row: {len(no_digest_row)}")
    for k, have, want in problems[:20]:
        print(f"  DIFFERS {k}: digest {have!r} vs analysis/ {want!r}")
    for k in not_covered[:10]:
        print(f"  NOT COVERED {k}")
    print()
    print("Sample (digest value, then the same value formatted from analysis/):")
    for k in SAMPLE[: a.show]:
        q, have = digest.get(k, ("", "(no row)"))
        want = expected.get(k, "(no value)")
        print(f"[{'equal' if have == want else 'DIFFERENT'}] {k[0]} {k[1]} : {k[2]}")
        print(f"    digest    : {have}")
        print(f"    analysis/ : {want}")
    return 1 if (mismatched or not_covered or no_digest_row) else 0


if __name__ == "__main__":
    sys.exit(main())
