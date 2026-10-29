#!/usr/bin/env python3
"""Compare the JSON files of analysis/ with the results digests of phd_works.

Each digest (``results_digest.md`` of the registered analysis and of the revised one)
lists every quoted number with the summary file and key it comes from. This script
formats the matching values of ``closed-form/closed_form_check.json`` and
``neutral-label/results.json`` exactly as the digest does (the functions ``num``,
``tau`` and ``contrast`` below are those of ``scripts/publish_results.py``) and
compares the strings. It reports how many digest rows of the closed-form and
neutral-label sections were matched, lists any difference, and prints a sample.

Usage:

    PHD_WORKS=/path/to/phd_works python compare_with_digest.py [--show 12]
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
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation/experiments",
    "1-Dissertation-Works/ERC20-Allowance-PageRank-Contract-Reputation/experiments",
)
PUB = "data/3-published-results-for-thesis"
PREFIX = {"revised": f"{PUB}/revised-usd-12m/", "registered": f"{PUB}/"}
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
    ("revised", "window-w1/eval_summary.json", "neutral_w1.grid.P.liquidation_free_rate"),
    ("revised", "window-w1/eval_summary.json", "neutral_w1.grid.Q.liquidation_free_rate"),
    ("revised", "window-w1/eval_summary.json", "neutral_w1.stratified.P"),
    ("revised", "window-w1/eval_summary.json", "neutral_w0.grid.P.liquidation_free_rate"),
    ("revised", "window-w1/eval_summary.json", "neutral_w1.grid.P.non_loss_share"),
    ("revised", "window-w1/eval_summary.json", "neutral_rules.R3"),
    ("revised", "window-w1/eval_summary.json", "neutral_w1.taus.awp.liquidation_free_rate"),
    ("registered", "registered-w1/eval_summary.json", "neutral_w1.grid.P.liquidation_free_rate"),
    ("registered", "registered-w1/eval_summary.json", "neutral_w0.influence_without_top10"),
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


def tau(d: dict | None) -> str:
    if not d:
        return "None"
    point = d.get("kendall_tau", d.get("mean_tau"))
    out = f"{num(point)} [{num(d.get('ci_low'))}, {num(d.get('ci_high'))}]"
    if d.get("n_boot") is not None:
        out += f"; B={d['n_boot']}"
    return out


def contrast(d: dict | None) -> str:
    if not d:
        return "None"
    out = (f"Δτ {num(d.get('delta_tau'))} [{num(d.get('ci_low'))}, {num(d.get('ci_high'))}]; "
           f"τa {num(d.get('a_tau'))}, τb {num(d.get('b_tau'))}")
    if d.get("ci975_low") is not None:
        out += f"; 97.5% [{num(d['ci975_low'])}, {num(d['ci975_high'])}]"
    if d.get("share_positive") is not None:
        out += f"; P(Δτ>0) {num(d['share_positive'])}"
    if d.get("n_boot") is not None:
        out += f"; B={d['n_boot']}"
    return out


# ------------------------------------------------------------- expected digest strings from analysis/


def as_contrast(r: dict) -> dict:
    return {"delta_tau": r["delta_tau"], "ci_low": r["ci95_low"], "ci_high": r["ci95_high"], "a_tau": r["tau_a"],
            "b_tau": r["tau_b"], "ci975_low": r["ci975_low"], "ci975_high": r["ci975_high"],
            "share_positive": r["share_positive"], "n_boot": r["B"]}


def expected_strings() -> dict[tuple[str, str, str], str]:
    exp: dict[tuple[str, str, str], str] = {}
    cf = json.loads((HERE / "closed-form" / "closed_form_check.json").read_text(encoding="utf-8"))
    for row in cf["rows"]:
        f = row["source"]["file"].removeprefix(PREFIX[row["analysis"]])
        for k, field in CF_FIELDS.items():
            exp[(row["analysis"], f, f"closed_form.{k}")] = num(row[field], 4)
    nl = json.loads((HERE / "neutral-label" / "results.json").read_text(encoding="utf-8"))
    for analysis, A in nl["analyses"].items():
        f = A["source"]["file"].removeprefix(PREFIX[analysis])
        for r, v in A["rules"].items():
            exp[(analysis, f, v["source_key"])] = "holds" if v["holds"] else "does not hold"
        for w, key in (("W1", "neutral_w1"), ("W0", "neutral_w0")):
            W = A["windows"][w]
            exp[(analysis, f, f"{key}.n")] = num(W["n"])
            exp[(analysis, f, f"{key}.max_in_approve_degree")] = num(W["max_in_approve_degree"])
            for labs in W["contrasts"].values():
                for rec in labs.values():
                    exp[(analysis, f, rec["source_key"])] = contrast(as_contrast(rec))
            for rec in W["stratified"].values():
                exp[(analysis, f, rec["source_key"])] = contrast(as_contrast(rec))
            for grp in ("recipients", "others"):
                for k, v in W["recipients"][grp].items():
                    exp[(analysis, f, f"{key}.recipients.{grp}.{k}")] = num(v)
            rec = W["influence_without_top10"]
            exp[(analysis, f, rec["source_key"])] = contrast(as_contrast(rec))
            for labs in W["taus"].values():
                for rec in labs.values():
                    exp[(analysis, f, rec["source_key"])] = tau({"kendall_tau": rec["tau"], "ci_low": rec["ci95_low"],
                                                                 "ci_high": rec["ci95_high"], "n_boot": rec["B"]})
            if "trader_counts" in W:
                tc = W["trader_counts"]
                for k, field in (("traders", "traders"), ("traders_liquidated", "traders_with_a_liquidation"),
                                 ("traders_all_liquidated", "traders_all_closes_liquidated")):
                    exp[(analysis, f, k)] = num(tc[field])
    return exp


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"),
                   help="path to a phd_works checkout (or set PHD_WORKS)")
    p.add_argument("--show", type=int, default=len(SAMPLE), help="number of sample rows to print")
    a = p.parse_args()
    if not a.phd_works:
        p.error("give --phd-works PATH or set the environment variable PHD_WORKS")
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
    relevant = [k for k in digest if k[2].startswith(("closed_form.", "neutral_"))
                or (k[1].endswith("w1/eval_summary.json") and k[2] in ("traders", "traders_liquidated",
                                                                      "traders_all_liquidated"))]
    not_covered = [k for k in relevant if k not in expected]
    no_digest_row = [k for k in expected if k not in digest]

    print(f"digest rows of the closed-form and neutral-label sections: {len(relevant)}; "
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
    return 1 if (mismatched or not_covered) else 0


if __name__ == "__main__":
    sys.exit(main())
