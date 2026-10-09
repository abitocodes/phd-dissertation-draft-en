#!/usr/bin/env python3
"""Rough text-overlap check between a manuscript and the thesis.

Reports the share of the manuscript's 8-word shingles that also occur in the thesis
(main chapters and abstract) and lists the longest shared spans, so that reused
sentences can be rewritten before submission. LaTeX commands and math are stripped.

    python overlap_check.py manuscripts/A-.../main.tex
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
N = 8


def words(tex: str) -> list[str]:
    tex = "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in tex.splitlines())
    tex = re.sub(r"\\begin\{(table|figure|tabular|equation|align)\*?\}.*?\\end\{\1\*?\}", " ", tex, flags=re.S)
    tex = re.sub(r"\$[^$]*\$", " ", tex)
    tex = re.sub(r"\\(cite|cend|ref|label|eqref|input|url|href)\*?(\[[^\]]*\])?\{[^}]*\}", " ", tex)
    tex = re.sub(r"\\[a-zA-Z]+\*?", " ", tex)
    tex = re.sub(r"[^A-Za-z0-9\-']+", " ", tex).lower()
    return tex.split()


def main() -> int:
    ms = words(Path(sys.argv[1]).read_text())
    thesis_files = [ROOT / "01-Intro/02-Abstract.tex"] + sorted(ROOT.glob("Chapter-0[1-6]*/index.tex"))
    th = []
    for f in thesis_files:
        th += words(f.read_text())
    th_sh = {tuple(th[i:i + N]) for i in range(len(th) - N + 1)}
    ms_sh = [tuple(ms[i:i + N]) for i in range(len(ms) - N + 1)]
    hit = [s in th_sh for s in ms_sh]
    share = sum(hit) / max(1, len(hit))
    spans, i = [], 0
    while i < len(hit):
        if hit[i]:
            j = i
            while j < len(hit) and hit[j]:
                j += 1
            spans.append((j - i + N - 1, " ".join(ms[i:j + N - 1])))
            i = j
        else:
            i += 1
    spans.sort(reverse=True)
    print(f"manuscript words: {len(ms)}; 8-gram overlap with thesis: {share:.1%}")
    for length, text in spans[:15]:
        print(f"  [{length} words] {text[:220]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
