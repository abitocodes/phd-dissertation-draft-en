#!/usr/bin/env python3
"""Check that every number in the prose of main.tex (and the other .tex files) occurs in a source.

The sources are the two results digests published in the public repository (each row names
its JSON file and key), the JSON summaries themselves, the two documents that define the main
analysis (docs/revision_contract_graph.md and docs/discovery_protocol.md of the published
folder) and analysis/closed-form/closed_form_check.json. Tables are skipped (make_tables.py
writes them from the JSON). A number counts as found when its text, or for a percentage its
value divided by 100 at three or four decimals, appears among the source values. Numbers that
are not data (dates, times, commit fragments, section counts) are listed with the others for a
manual look; README.md names the source of each.

The long per-seed lists and curves of the discovery summaries are not read as sources, so that
a number does not pass by chance; the points of the curves that the text quotes (the discovery
curve and the captured importance at 1% and 10% of the visits) are added one by one.

    CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation python3 check_numbers.py [file.tex ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                   # also under python -I (isolated mode)
import data_sources as S  # noqa: E402

# Keys of the summaries that hold long lists (per-seed values, curves, hub lists) or hashes.
SKIP_KEYS = {"curves", "per_seed", "visits_50", "visits_90", "hubs", "hub_visits", "seeds", "provenance",
             "sha256", "code_families", "resume_key", "resume_key_history"}
CURVE_SHARES = (0.01, 0.10)
NUMBER = r"-?\d[\d,]*\.?\d*(?:e-?\d+)?"


def source_values() -> set[str]:
    vals: set[str] = set()
    exp = S.experiments_dir() / S.PUB
    texts = [S.digest_text(""), S.digest_text(S.REV),
             (exp / S.REV / "docs" / "revision_contract_graph.md").read_text(encoding="utf-8"),
             (exp / S.REV / "docs" / "discovery_protocol.md").read_text(encoding="utf-8")]
    for t in texts:
        vals.update(re.findall(NUMBER, t))

    def add(x: float) -> None:
        for nd in (0, 1, 2, 3, 4):
            vals.add(f"{x:,.{nd}f}")
            vals.add(f"{x:.{nd}f}")
        vals.add(f"{x:.2e}")

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k not in SKIP_KEYS:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, bool):
            return
        elif isinstance(x, (int, float)):
            add(x)
        elif isinstance(x, str):
            vals.update(re.findall(r"-?\d[\d,]*\.?\d*", x))

    for name in S.FILES:
        walk(S.load(name))
    walk(json.loads((S.ANALYSIS / "closed-form/closed_form_check.json").read_text(encoding="utf-8")))
    # the points of the curves that the text and S1 Table quote
    for tag, mode in S.RUNS:
        run = S.discovery(tag, mode)
        for kind in ("P_ST", "captured"):
            for imp, by in run["curves"][kind].items():
                for ordering in by:
                    for share in CURVE_SHARES:
                        add(S.curve_at(run, kind, imp, ordering, share))
    return {v.lstrip("-").rstrip(".") for v in vals}


def prose(tex: str) -> str:
    tex = re.sub(r"% BEGIN GENERATED.*?% END GENERATED \w+\n", " ", tex, flags=re.S)
    tex = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in tex.splitlines())
    tex = re.sub(r"\\(label|ref|cite|url|nolinkurl|href|includegraphics|input|bibliography\w*)\*?(\[[^\]]*\])?\{[^}]*\}", " ", tex)
    tex = tex.replace("{,}", ",").replace("$-$", "-").replace("$+$", "+")
    # a value written as m \times 10^{e} is compared in the form the sources are read in (8.45e-06)
    tex = re.sub(r"(\d+\.\d+)\\times\s*10\^\{(-?\d+)\}",
                 lambda m: f"{float(m.group(1)) * 10.0 ** int(m.group(2)):.2e}", tex)
    # lengths of the page layout (p{9.8cm}, {-2.25in}) are not results
    tex = re.sub(r"-?\d+(?:\.\d+)?(?:in|cm|mm|pt|em|ex)\b", " ", tex)
    return tex


def main() -> None:
    args = S.parse_args(__doc__.splitlines()[0])
    vals = source_values()
    files = [Path(a) for a in args.rest if not a.startswith("--")] or [HERE / "main.tex"]
    for f in files:
        text = prose(f.read_text(encoding="utf-8"))
        begin = text.find("\\begin{document}")
        text = text[max(begin, 0):]
        missing = {}
        # digits are grouped by commas only in threes, so that max(0,1-t) reads as 0 and 1
        for m in re.finditer(r"(?<![\w.])(-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:e[+-]\d+)?)(\\%)?", text):
            num, pct = m.group(1).lstrip("-"), m.group(2)
            if num in vals:
                continue
            if pct:
                try:
                    v = float(num.replace(",", "")) / 100
                except ValueError:
                    v = None
                if v is not None and any(f"{v:.{nd}f}" in vals for nd in (3, 4)):
                    continue
            ctx = text[max(0, m.start() - 40): m.end() + 20].replace("\n", " ")
            missing.setdefault(num + ("%" if pct else ""), ctx)
        print(f"== {f.name}: {len(missing)} numbers not found verbatim in a source")
        for k, ctx in missing.items():
            print(f"  {k:>14}  ...{ctx}...")


if __name__ == "__main__":
    main()
