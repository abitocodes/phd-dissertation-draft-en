#!/usr/bin/env python3
"""Check that every number in the prose of main.tex (and the cover letter) occurs in a source.

The sources are the two results digests published in phd_works (each row names its JSON
file and key), the JSON summaries themselves, analysis/closed-form/closed_form_check.json
and analysis/neutral-label/results.json. Tables are skipped (make_tables.py writes them from
the JSON). A number counts as found when its text, or for a percentage its value divided
by 100 at three decimals, appears among the source values. Numbers that are not data
(dates, times, commit fragments, section counts) are listed separately for a manual look.

    PHD_WORKS=/path/to/phd_works python3 check_numbers.py [file.tex ...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import data_sources as S

HERE = Path(__file__).resolve().parent


def source_values() -> set[str]:
    vals: set[str] = set()
    exp = S.experiments_dir() / S.PUB
    texts = [(exp / "results_digest.md").read_text(encoding="utf-8"),
             (exp / "revised-usd" / "results_digest.md").read_text(encoding="utf-8")]
    for t in texts:
        vals.update(re.findall(r"-?\d[\d,]*\.?\d*(?:e-?\d+)?", t))

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, bool):
            return
        elif isinstance(x, (int, float)):
            for nd in (0, 1, 2, 3, 4):
                vals.add(f"{x:,.{nd}f}")
                vals.add(f"{x:.{nd}f}")
            vals.add(f"{x:.2e}")
        elif isinstance(x, str):
            vals.update(re.findall(r"-?\d[\d,]*\.?\d*", x))

    for name in S.FILES:
        walk(S.load(name))
    walk(json.loads((S.ANALYSIS / "closed-form/closed_form_check.json").read_text()))
    walk(S.neutral())
    return {v.lstrip("-").rstrip(".") for v in vals}


def prose(tex: str) -> str:
    tex = re.sub(r"% BEGIN GENERATED.*?% END GENERATED \w+\n", " ", tex, flags=re.S)
    tex = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in tex.splitlines())
    tex = re.sub(r"\\(label|ref|cite|url|nolinkurl|href|includegraphics|input|bibliography\w*)\*?(\[[^\]]*\])?\{[^}]*\}", " ", tex)
    tex = tex.replace("{,}", ",").replace("$-$", "-")
    return tex


def main() -> None:
    S.parse_args(__doc__.splitlines()[0])
    vals = source_values()
    files = [Path(a) for a in sys.argv[1:] if not a.startswith("--")] or [HERE / "main.tex"]
    for f in files:
        text = prose(f.read_text(encoding="utf-8"))
        begin = text.find("\\begin{document}")
        text = text[begin:]
        missing = {}
        for m in re.finditer(r"(?<![\w.])(-?\d[\d,]*(?:\.\d+)?)(\\%)?", text):
            num, pct = m.group(1).lstrip("-").rstrip(","), m.group(2)
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
