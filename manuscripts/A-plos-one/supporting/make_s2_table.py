#!/usr/bin/env python3
"""S2 Table of Manuscript A: every contrast of the pre-specified trader comparison.

Reads analysis/neutral-label/results.json (read only) and writes S2_Table_rows.tex, which
S2_Table.tex inputs. No number is typed by hand. The share of resamples with a positive
difference, which results.json also stores, is deliberately not exported.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = json.loads((ROOT / "analysis/neutral-label/results.json").read_text())

WINDOWS = [("W1_registered_jun_aug_2026", "W1: freeze 31 May 2026, labels June--August 2026"),
           ("W0_spring_mar_may_2026", "W0: freeze 28 February 2026, labels March--May 2026")]
LABELS = [("future_liquidation_free_rate", "Liquidation-free close rate"),
          ("future_zero_liquidation", "No-liquidation flag"),
          ("close_success_count", "Profitable closes$^{\\dagger}$"),
          ("realized_gain_proxy", "Realized gain$^{\\dagger}$"),
          ("close_success_rate", "Profitable share"),
          ("non_loss_close_rate", "Non-loss share")]
CONTRASTS = [("P", "P: in-approve degree $-$ transfer in-degree"),
             ("Q", "Q: EndorseRank (activity restarts) $-$ AWP"),
             ("ER-AWP", "EndorseRank $-$ AWP"),
             ("ER-deg", "EndorseRank $-$ in-approve degree"),
             ("L1-L0", "C-PR($\\lambda{=}1$) $-$ C-PR($\\lambda{=}0$)$^{\\ddagger}$"),
             ("L0-AWP", "C-PR($\\lambda{=}0$) $-$ AWP$^{\\ddagger}$"),
             ("CPR-deg", "C-PR($\\lambda{=}0.5$) $-$ in-approve degree$^{\\ddagger}$")]


def f(x: float) -> str:
    s = f"{x:+.3f}" if x != 0 else "0.000"
    return s.replace("-", "$-$")


def ci(pair) -> str:
    lo, hi = pair
    return f"[{f(lo)}, {f(hi)}]"


def main() -> None:
    out = []
    for wkey, wname in WINDOWS:
        win = R["windows"][wkey]
        out.append(f"\\midrule\n\\multicolumn{{6}}{{l}}{{\\textbf{{{wname}}}}} \\\\")
        for lab, lname in LABELS:
            block = win["plain"][lab]
            out.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{lname}}} ($n={block['n']:,}$)}} \\\\".replace(",", "{,}"))
            for cid, cname in CONTRASTS:
                r = block["contrasts"][cid]
                out.append(f"\\quad {cname} & {f(r['tau_a'])} & {f(r['tau_b'])} & {f(r['delta'])} & "
                           f"{ci(r['ci95'])} & {ci(r['ci975'])} \\\\")
        st = win["stratified_by_closes"]["future_liquidation_free_rate"]["contrasts"]
        out.append("\\multicolumn{6}{l}{\\emph{Liquidation-free close rate, stratified by the number of closes}} \\\\")
        for cid, cname in CONTRASTS:
            if cid not in st:
                continue
            r = st[cid]
            out.append(f"\\quad {cname} & {f(r['tau_a'])} & {f(r['tau_b'])} & {f(r['delta'])} & "
                       f"{ci(r['ci95'])} & {ci(r['ci975'])} \\\\")
    (HERE / "S2_Table_rows.tex").write_text("\n".join(out) + "\n")
    print("wrote", HERE / "S2_Table_rows.tex")


if __name__ == "__main__":
    main()
