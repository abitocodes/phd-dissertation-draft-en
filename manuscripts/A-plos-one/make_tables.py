#!/usr/bin/env python3
"""Tables 1-6 of Manuscript A and the rows of S1 Table, generated from the published JSON.

PLOS ONE wants the tables inside the single main.tex, so this script writes each table
between the markers

    % BEGIN GENERATED tabN (make_tables.py; do not edit by hand)
    ...
    % END GENERATED tabN

of main.tex, and writes supporting/S1_Table_rows.tex for S1 Table. No number is typed by
hand: every value is read from the summaries in phd_works (checked against their
SHA256SUMS.txt by data_sources.py) or from analysis/*.json.

    PHD_WORKS=/path/to/phd_works python3 make_tables.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import data_sources as S
from data_sources import ci, delta_ci, intc, num, pct, tau_ci

HERE = Path(__file__).resolve().parent
MAIN = HERE / "main.tex"
S1_ROWS = HERE / "supporting" / "S1_Table_rows.tex"

LABEL_ORDER = ["liquidation_free_rate", "no_liquidation", "profitable_closes",
               "realized_gain", "profitable_share", "non_loss_share"]


def contrast(lst: list[dict], label: str, outcome: str | None = None) -> dict:
    for c in lst:
        if c["label"] == label and (outcome is None or c.get("outcome") == outcome):
            return c
    sys.exit(f"contrast not found: {label} / {outcome}")


def sci(x: float) -> str:
    m, e = f"{x:.2e}".split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


# --------------------------------------------------------------------------- Table 1
def table1() -> str:
    sw, w0 = S.load("rev_same"), S.load("rev_w0")
    cf_t, cf_0 = S.closed_form()[("revised", "same_window")], S.closed_form()[("revised", "W0")]
    assert cf_t["allowance_graph_edges"] == sw["graph"]["allowance"]["edges"]
    assert cf_0["allowance_graph_edges"] == w0["graph"]["allowance_edges"]
    g = sw["graph"]
    rows = [
        ("Allowance graph, nodes", intc(g["allowance"]["nodes"]), "--"),
        ("Allowance graph, edges", intc(g["allowance"]["edges"]), intc(w0["graph"]["allowance_edges"]) + "$^{a}$"),
        ("Transfer graph, nodes", intc(g["transfer"]["nodes"]), "--"),
        ("Transfer graph, edges", intc(g["transfer"]["edges"]), intc(w0["graph"]["transfer_edges"]) + "$^{a}$"),
        ("Contracts checked", f"{intc(cf_t['scored_set_size'])} (matched cohort)",
         f"{intc(cf_0['scored_set_size'])} (W0 spenders)"),
        ("Spenders among them (allowance in-edge)", intc(cf_t["spenders"]), intc(cf_0["spenders"])),
        ("\\quad depth one (no owner has an in-edge)", intc(cf_t["depth_one_spenders"]), intc(cf_0["depth_one_spenders"])),
        ("\\quad deeper (an owner is itself approved)", intc(cf_t["deeper_spenders"]), intc(cf_0["deeper_spenders"])),
        ("Common score $c$ of nodes without in-edges", sci(cf_t["c"]), sci(cf_0["c"])),
        ("Within 1\\% of the closed form$^{b}$: depth-one spenders", pct(cf_t["within_1pct_depth_one"]), pct(cf_0["within_1pct_depth_one"])),
        ("Within 1\\% of the closed form$^{b}$: deeper spenders", pct(cf_t["within_1pct_deeper"]), pct(cf_0["within_1pct_deeper"])),
        ("Within 1\\% of the closed form$^{b}$: all spenders", pct(cf_t["within_1pct_all"]), pct(cf_0["within_1pct_all"])),
    ]
    body = "\n".join(f"{a} & {b} & {c} \\\\" for a, b, c in rows)
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Graphs at the two freeze dates and fit of the closed form for EndorseRank.}}}}
\small
\begin{{tabular}}{{lrr}}
\toprule
 & $T_{{\mathrm{{obs}}}}$, 30 Jun 2026 & $t_1$, 31 Mar 2026 \\
 & (same window and W1) & (W0) \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\begin{{flushleft}}Graphs built from the ego events of the matched cohort up to each freeze date (revised analysis: approvals and transfers of WETH, USDC, USDT0, ARB and WBTC, amounts in US dollars). At $T_{{\mathrm{{obs}}}}$ the edge counts are those of pairs with a positive EndorseRank or AWP weight. A spender is a contract of the checked set with an allowance in-edge of positive weight; it has depth one when none of its owners has an in-edge itself. Damping $d=0.85$. $^{{a}}$Owner--spender and sender--recipient pairs in the pair tables at $t_1$, counted before pairs whose value weight is zero in floating point are dropped; the node counts at $t_1$ are not recorded. $^{{b}}$\Eq{{eq:closed-form}}, derived in Results (What EndorseRank computes on depth-one spenders). Sources: \texttt{{same-window}} and \texttt{{holdout-w0/eval\_summary.json}}, keys \texttt{{graph}} and \texttt{{closed\_form}}, through \texttt{{analysis/closed-form/closed\_form\_check.json}}.
\end{{flushleft}}
\label{{tab1}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- Table 2
def table2() -> str:
    sw = S.load("rev_same")
    fam, prx = sw["families"], sw["per_proxy"]
    meths = ["endorserank", "endorserank_activity", "awp"]

    def row(name, f):
        return name + " & " + " & ".join(f(m) for m in meths) + " \\\\"

    lines = [
        row("Transfer family (mean)", lambda m: tau_ci(fam[m]["transfer"])),
        row("\\quad in-degree", lambda m: tau_ci(prx[m]["in_degree"])),
        row("\\quad in-value (USD)", lambda m: tau_ci(prx[m]["in_value"])),
        row("Allowance family (mean)", lambda m: tau_ci(fam[m]["allowance"])),
        row("\\quad in-approve degree", lambda m: tau_ci(prx[m]["in_approve_degree"])),
        row("\\quad in-approve value (USD, capped)", lambda m: tau_ci(prx[m]["in_approve_value"])),
        row("Sybil-stability family (mean)", lambda m: tau_ci(fam[m]["sybil_stability"])),
    ]
    con = {c["label"]: c for c in sw["contrasts"]}
    er_awp_all = con["EndorseRank allowance minus AWP allowance"]
    awp_er_tr = con["AWP transfer minus EndorseRank transfer"]
    im = sw["inter_method"]
    body = "\n".join(lines)
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Same-window agreement of each score with the checks of each edge type (intended-construct check).}}}}
\small
\begin{{tabular}}{{lccc}}
\toprule
Check (Kendall $\tau_b$ [95\% CI]) & EndorseRank & EndorseRank, activity restarts & AWP \\
\midrule
{body}
\midrule
\multicolumn{{4}}{{l}}{{\emph{{Paired differences $\dt$ [95\% CI] and agreement of the two rankings}}}} \\
EndorseRank $-$ AWP, allowance family & \multicolumn{{3}}{{l}}{{{delta_ci(er_awp_all)}}} \\
AWP $-$ EndorseRank, transfer family & \multicolumn{{3}}{{l}}{{{delta_ci(awp_er_tr)}}} \\
$\tau_b$ between EndorseRank and AWP & \multicolumn{{3}}{{l}}{{{tau_ci(im['endorserank_vs_awp'])}}} \\
\quad with missing contracts as isolated nodes & \multicolumn{{3}}{{l}}{{{tau_ci(im['isolated'])}}} \\
\bottomrule
\end{{tabular}}
\begin{{flushleft}}Matched cohort, $n={intc(sw['cohort'])}$ contracts, scores at $T_{{\mathrm{{obs}}}}$ (30 June 2026). Each check is computed from the events of one graph: the transfer family from inbound transfers, the allowance family from latest allowances received. Agreement of a score with the checks of its own edge type is therefore partly built in. The Sybil-stability family averages the inbound-counterparty ratio, transfer tenure and active months. Family means are plain averages of the coefficients of their checks. Paired contract bootstrap, {fam['endorserank']['allowance']['n_boot']} resamples (seed 42); intervals are unadjusted. None of these comparisons decides a rule. Source: \texttt{{revised-usd/same-window/eval\_summary.json}}, keys \texttt{{families}}, \texttt{{per\_proxy}}, \texttt{{contrasts}}, \texttt{{inter\_method}}.
\end{{flushleft}}
\label{{tab2}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- Table 3
def spender_blocks():
    w0, w1, sup = S.load("rev_w0"), S.load("rev_w1"), S.load("rev_sup")
    t0, t1 = w0["taus"], w1["spender_taus"]
    A, T = "future_new_approvers", "future_new_transfer_senders"
    taus = [
        ("In-approve degree (count)", t0["t1_in_approve_degree"], t1["in_approve_degree"]),
        ("Transfer in-degree (count)", t0["t1_in_degree"], t1["in_degree"]),
        ("EndorseRank", t0["endorserank"], t1["endorserank"]),
        ("EndorseRank, activity restarts", t0["endorserank_activity"], t1["endorserank_activity"]),
        ("AWP", t0["awp"], t1["awp"]),
    ]
    ca = w0["contrasts_after"]
    er_deg0 = contrast(ca, "EndorseRank minus t1 in-approve degree", A)
    awp_deg0 = contrast(ca, "AWP minus t1 in-degree", T)
    er_awp0_a = contrast(ca, "EndorseRank minus AWP", A)
    er_awp0_t = contrast(ca, "EndorseRank minus AWP", T)
    er_res = w1["endorserank_results"]
    diffs = {
        "er_deg": (er_deg0, er_res["endorserank_minus_degree_appr"]),
        "act_deg": (sup["w0"]["er_activity_minus_degree_appr"], sup["w1"]["er_activity_minus_degree_appr"]),
        "awp_deg": (awp_deg0, er_res["awp_minus_degree_send"]),
        "er_awp_a": (er_awp0_a, sup["w1"]["er_minus_awp_appr"]),
        "er_awp_t": (er_awp0_t, sup["w1"]["er_minus_awp_send"]),
    }
    # the two EndorseRank-AWP contrasts appear in both files for W0; they must agree
    assert abs(er_awp0_a["delta_tau"] - sup["w0"]["er_minus_awp_appr"]["delta_tau"]) < 1e-12
    return w0, w1, taus, (A, T), diffs


def table3() -> str:
    w0, w1, taus, (A, T), d = spender_blocks()
    lines = [f"{name} & {tau_ci(a[A])} & {tau_ci(a[T])} & {tau_ci(b[A])} & {tau_ci(b[T])} \\\\"
             for name, a, b in taus]
    body = "\n".join(lines)
    e = ""
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Spender holdouts: scores frozen at each date against labels counted over the next three months.}}}}
\footnotesize
\setlength{{\tabcolsep}}{{3pt}}
\begin{{tabular}}{{>{{\raggedright\arraybackslash}}p{{1.85in}}cccc}}
\toprule
 & \multicolumn{{2}}{{c}}{{W0: freeze 31 Mar 2026 ($n={intc(w0['spenders'])}$)}} & \multicolumn{{2}}{{c}}{{W1: freeze 30 Jun 2026 ($n={intc(w1['spenders'])}$)}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
Score at the freeze & New approval pairs & New senders & New approval pairs & New senders \\
\midrule
{body}
\midrule
\multicolumn{{5}}{{l}}{{\emph{{Each PageRank against the raw degree it smooths, on the label of its own edge type: $\dt$ [95\% CI]}}}} \\
EndorseRank $-$ in-approve degree & {delta_ci(d['er_deg'][0])} & {e} & {delta_ci(d['er_deg'][1])} & {e} \\
EndorseRank, activity restarts $-$ in-approve degree & {delta_ci(d['act_deg'][0])} & {e} & {delta_ci(d['act_deg'][1])} & {e} \\
AWP $-$ transfer in-degree & {e} & {delta_ci(d['awp_deg'][0])} & {e} & {delta_ci(d['awp_deg'][1])} \\
\multicolumn{{5}}{{l}}{{\emph{{Allowance walk against transfer walk: $\dt$ [95\% CI]}}}} \\
EndorseRank $-$ AWP & {delta_ci(d['er_awp_a'][0])} & {delta_ci(d['er_awp_t'][0])} & {delta_ci(d['er_awp_a'][1])} & {delta_ci(d['er_awp_t'][1])} \\
\bottomrule
\end{{tabular}}
\begin{{flushleft}}Kendall $\tau_b$ with 95\% percentile interval from 400 paired contract resamples (seed 42); intervals are unadjusted. Spenders are the contracts with a positive latest allowance of one of the five tokens at the freeze. In W0, {intc(w0['gained_new_approvals'])} spenders gained at least one new approval pair and {intc(w0['gained_new_senders'])} at least one new transfer sender; in W1, {intc(w1['gained_new_approvals'])} and {intc(w1['gained_new_senders'])} did. Every paired difference in this table was computed after the labels of its window were known, and none of them decides a rule; the variant with activity restarts was set against the in-approve degree last. Sources: \texttt{{revised-usd/holdout-w0/eval\_summary.json}} (\texttt{{taus}}, \texttt{{contrasts\_after}}), \texttt{{window-w1/eval\_summary.json}} (\texttt{{spender\_taus}}, \texttt{{endorserank\_results}}), \texttt{{supplementary/supplementary.json}}.
\end{{flushleft}}
\label{{tab3}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- Table 4
NAMES = {
    "P": "P: in-approve degree $-$ transfer in-degree",
    "Q": "Q: EndorseRank (activity restarts) $-$ AWP",
    "er_awp": "EndorseRank $-$ AWP",
    "er_degree": "EndorseRank $-$ in-approve degree$^{a}$",
    "layers": "C-PR($\\lambda{=}1$) $-$ C-PR($\\lambda{=}0$)$^{b}$",
    "cpr0_awp": "C-PR($\\lambda{=}0$) $-$ AWP$^{b}$",
}


def crow(name: str, c: dict) -> str:
    c975 = ci(c["ci975_low"], c["ci975_high"]) if c.get("ci975_low") is not None else "--"
    return (f"{name} & {num(c['tau_a'])} & {num(c['tau_b'])} & {num(c['delta_tau'], sign=True)} & "
            f"{ci(c['ci95_low'], c['ci95_high'])} & {c975} \\\\")


def table4() -> str:
    R = S.neutral()["analyses"]["revised"]["windows"]
    lab = "liquidation_free_rate"
    out = []
    for w, head in (("W1", "W1: freeze 30 June 2026, labels July--September 2026"),
                    ("W0", "W0: freeze 31 March 2026, labels April--June 2026")):
        W = R[w]
        out.append(f"\\multicolumn{{6}}{{l}}{{\\emph{{{head} ($n={W['n']}$ contract traders)}}}} \\\\")
        out.append(crow(NAMES["P"], W["contrasts"]["P"][lab]))
        out.append(crow("\\quad P, stratified by closes", W["stratified"]["P"]))
        out.append(crow(NAMES["Q"], W["contrasts"]["Q"][lab]))
        out.append(crow("\\quad Q, stratified by closes", W["stratified"]["Q"]))
        for p in ("er_awp", "er_degree", "layers", "cpr0_awp"):
            out.append(crow(NAMES[p], W["contrasts"][p][lab]))
        if w == "W1":
            out.append("\\midrule")
    body = "\n".join(out)
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Allowance-side minus transfer-side scores on the later liquidation-free close rate of contract traders.}}}}
\footnotesize
\setlength{{\tabcolsep}}{{4pt}}
\begin{{tabular}}{{lccccc}}
\toprule
Contrast ($a-b$) & $\tau(a)$ & $\tau(b)$ & $\dt$ & 95\% CI & 97.5\% CI \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\begin{{flushleft}}Kendall $\tau_b$ of score $a$ and score $b$ on the GMX~V2 contract traders with at least three closes in the label window, and their difference. Paired contract bootstrap with 2,000 resamples (seed 42). The pairs, P and Q with their Bonferroni 97.5\% intervals, the stratified rows and the rules R1--R3 were registered for W1 before its logs were extracted; here they are applied to the revised scores, after the registered results were known, so no row is a registered test. Only the 97.5\% intervals of P and Q in W1 enter a rule; every other interval is unadjusted. Stratified rows combine $\tau_b$ within strata of 3--4, 5--9, 10--24 and 25 or more label-window closes, weighted by contract pairs. $^{{a}}$Not named in the registration document; computed by the code committed with it. $^{{b}}$Amount-weighted allowance and transfer layers walked alone with uniform restarts. Source: \texttt{{analysis/neutral-label/results.json}}, \texttt{{analyses.revised.windows}}; S2 Table gives all six labels.
\end{{flushleft}}
\label{{tab4}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- Table 5
def table5() -> str:
    R = S.neutral()["analyses"]["revised"]["windows"]
    r1, r0 = R["W1"]["recipients"], R["W0"]["recipients"]

    def f(x, nd=3):
        return num(x, nd=nd)

    rows = [
        ("Traders", lambda r: str(r["n"])),
        ("Share with no liquidation", lambda r: f(r["share_no_liquidation"])),
        ("Mean liquidation-free close rate", lambda r: f(r["mean_liquidation_free_rate"])),
        ("Mean profitable share", lambda r: f(r["mean_profitable_share"])),
        ("Mean non-loss share", lambda r: f(r["mean_non_loss_share"])),
        ("Median closes in the label window", lambda r: f(r["median_closes"], 1)),
    ]
    lines = []
    for name, g in rows:
        lines.append(f"{name} & {g(r1['recipients'])} & {g(r1['others'])} & {g(r0['recipients'])} & {g(r0['others'])} \\\\")
    i1, i0 = R["W1"]["influence_without_top10"], R["W0"]["influence_without_top10"]
    body = "\n".join(lines)
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Contract traders that had received an approval at the freeze (recipients) against all other traders.}}}}
\small
\begin{{tabular}}{{lcccc}}
\toprule
 & \multicolumn{{2}}{{c}}{{W1 (July--September 2026)}} & \multicolumn{{2}}{{c}}{{W0 (April--June 2026)}} \\
\cmidrule(lr){{2-3}}\cmidrule(lr){{4-5}}
 & Recipients & Other traders & Recipients & Other traders \\
\midrule
{body}
Highest in-approve degree at the freeze & {int(R['W1']['max_in_approve_degree'])} & 0 & {int(R['W0']['max_in_approve_degree'])} & 0 \\
\midrule
P without the ten recipients of highest in-approve degree & \multicolumn{{2}}{{c}}{{{delta_ci(i1)} ($n={i1['n']}$)}} & \multicolumn{{2}}{{c}}{{{delta_ci(i0)} ($n={i0['n']}$)}} \\
\bottomrule
\end{{tabular}}
\begin{{flushleft}}Recipients have an in-approve degree above zero at the freeze. Every trader in both windows holds contract code. The comparison and the influence check (P on the liquidation-free close rate, 95\% interval from 2,000 paired resamples) were registered with the contrasts of Table~\ref{{tab4}} and are applied here to the revised scores. With tied in-approve degrees, the ten recipients left out are taken in node order. Source: \texttt{{analysis/neutral-label/results.json}}, keys \texttt{{recipients}} and \texttt{{influence\_without\_top10}}.
\end{{flushleft}}
\label{{tab5}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- Table 6
def table6() -> str:
    rs, rv = S.load("reg_same"), S.load("rev_same")
    r0, v0 = S.load("reg_w0"), S.load("rev_w0")
    r1, v1 = S.load("reg_w1"), S.load("rev_w1")
    rsup, vsup = S.load("reg_sup"), S.load("rev_sup")
    cfr, cfv = S.closed_form()[("registered", "same_window")], S.closed_form()[("revised", "same_window")]
    NL = S.neutral()["analyses"]
    A, T = "future_new_approvers", "future_new_transfer_senders"

    def both(fn):
        return f"{fn('reg')} & {fn('rev')}"

    pick = {"reg": dict(same=rs, w0=r0, w1=r1, sup=rsup, cf=cfr, nl=NL["registered"]),
            "rev": dict(same=rv, w0=v0, w1=v1, sup=vsup, cf=cfv, nl=NL["revised"])}

    def lfcr(k, w, p):
        return pick[k]["nl"]["windows"][w]["contrasts"][p]["liquidation_free_rate"]

    def c975(c):
        return f"{num(c['delta_tau'], sign=True)} {ci(c['ci975_low'], c['ci975_high'])}"

    def verdict(k, r):
        return "holds" if pick[k]["nl"]["rules"][r]["holds"] else "does not hold"

    def applies(k):
        return "applies" if pick[k]["nl"]["rules"]["R3"]["holds"] else "does not apply"

    lines = [
        "\\multicolumn{3}{l}{\\emph{Data and same window}} \\\\",
        f"Amounts; tokens & raw base units; every ERC-20 & US dollars; five tokens \\\\",
        f"Matched cohort (contracts) & {both(lambda k: intc(pick[k]['same']['cohort']))} \\\\",
        f"Allowance / transfer edges at $T_{{\\mathrm{{obs}}}}$ & "
        + both(lambda k: intc(pick[k]['same']['graph']['allowance']['edges']) + " / " + intc(pick[k]['same']['graph']['transfer']['edges'])) + " \\\\",
        f"EndorseRank, allowance family & {both(lambda k: tau_ci(pick[k]['same']['families']['endorserank']['allowance']))} \\\\",
        f"AWP, transfer family & {both(lambda k: tau_ci(pick[k]['same']['families']['awp']['transfer']))} \\\\",
        f"$\\tau_b$ between EndorseRank and AWP & {both(lambda k: tau_ci(pick[k]['same']['inter_method']['endorserank_vs_awp']))} \\\\",
        f"Depth-one / all spenders within 1\\% of \\Eq{{eq:closed-form}} & "
        + both(lambda k: pct(pick[k]['cf']['within_1pct_depth_one']) + " / " + pct(pick[k]['cf']['within_1pct_all'])) + " \\\\",
        "\\midrule",
        "\\multicolumn{3}{l}{\\emph{Spender holdouts, PageRank minus its raw degree (computed after the labels)}} \\\\",
        f"Spender cohorts, W0 / W1 & {both(lambda k: intc(pick[k]['w0']['spenders']) + ' / ' + intc(pick[k]['w1']['spenders']))} \\\\",
        f"W0: EndorseRank $-$ in-approve degree, new pairs & "
        + both(lambda k: delta_ci(contrast(pick[k]['w0']['contrasts_after'], 'EndorseRank minus t1 in-approve degree', A))) + " \\\\",
        f"W0: EndorseRank (activity) $-$ in-approve degree & "
        + both(lambda k: delta_ci(pick[k]['sup']['w0']['er_activity_minus_degree_appr'])) + " \\\\",
        f"W0: AWP $-$ transfer in-degree, new senders & "
        + both(lambda k: delta_ci(contrast(pick[k]['w0']['contrasts_after'], 'AWP minus t1 in-degree', T))) + " \\\\",
        f"W1: EndorseRank $-$ in-approve degree, new pairs & "
        + both(lambda k: delta_ci(pick[k]['w1']['endorserank_results']['endorserank_minus_degree_appr'])) + " \\\\",
        f"W1: EndorseRank (activity) $-$ in-approve degree & "
        + both(lambda k: delta_ci(pick[k]['sup']['w1']['er_activity_minus_degree_appr'])) + " \\\\",
        f"W1: AWP $-$ transfer in-degree, new senders & "
        + both(lambda k: delta_ci(pick[k]['w1']['endorserank_results']['awp_minus_degree_send'])) + " \\\\",
        "\\midrule",
        "\\multicolumn{3}{l}{\\emph{Contract traders, liquidation-free close rate (registered pairs and rules)}} \\\\",
        f"P, W1, 95\\% CI & {both(lambda k: delta_ci(lfcr(k, 'W1', 'P')))} \\\\",
        f"P, W1, 97.5\\% CI & {both(lambda k: c975(lfcr(k, 'W1', 'P')))} \\\\",
        f"P stratified by closes, W1, 95\\% CI & {both(lambda k: delta_ci(pick[k]['nl']['windows']['W1']['stratified']['P']))} \\\\",
        f"P, W0 & {both(lambda k: delta_ci(lfcr(k, 'W0', 'P')))} \\\\",
        f"Q, W1, 97.5\\% CI & {both(lambda k: c975(lfcr(k, 'W1', 'Q')))} \\\\",
        f"Q, W0 & {both(lambda k: delta_ci(lfcr(k, 'W0', 'Q')))} \\\\",
        f"EndorseRank $-$ AWP, W1 & {both(lambda k: delta_ci(lfcr(k, 'W1', 'er_awp')))} \\\\",
        f"EndorseRank $-$ AWP, W0 & {both(lambda k: delta_ci(lfcr(k, 'W0', 'er_awp')))} \\\\",
        f"C-PR($\\lambda{{=}}1$) $-$ C-PR($\\lambda{{=}}0$), W1 & {both(lambda k: delta_ci(lfcr(k, 'W1', 'layers')))} \\\\",
        f"C-PR($\\lambda{{=}}1$) $-$ C-PR($\\lambda{{=}}0$), W0 & {both(lambda k: delta_ci(lfcr(k, 'W0', 'layers')))} \\\\",
        f"R1 (count-level lead) & {both(lambda k: verdict(k, 'R1'))} \\\\",
        f"R2 (PageRank-level lead) & {both(lambda k: verdict(k, 'R2'))} \\\\",
        f"R3 (specific to liquidation avoidance) & {both(applies)} \\\\",
    ]
    body = "\n".join(lines)
    return rf"""\begin{{table}}[!ht]
\begin{{adjustwidth}}{{-2.25in}}{{0in}}
\centering
\caption{{{{\bf Registered analysis beside the revised analysis.}}}}
\footnotesize
\begin{{tabular}}{{lcc}}
\toprule
 & Registered analysis & Revised analysis (re-analysis) \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\begin{{flushleft}}The registered analysis follows the analysis plan and the W1 registration as committed; its values and verdicts are registered results only where a rule of the registration decides them (P, Q, R1--R3); the other trader rows are registered pairs that decide no rule. The revised analysis values amounts in US dollars over five tokens; it was decided after every registered result was known, and its verdicts apply the registered rules to scores defined afterwards. Degree contrasts are not decided by any rule in either analysis. $\dt$ with 95\% interval unless marked 97.5\% (spenders 400, traders 2,000 paired resamples, seed 42). Sources: same-window, \texttt{{holdout-w0}}, \texttt{{registered-w1}} and \texttt{{window-w1}} summaries and \texttt{{supplementary.json}} of each analysis in \texttt{{phd\_works}}; \texttt{{analysis/closed-form/closed\_form\_check.json}}; \texttt{{analysis/neutral-label/results.json}}.
\end{{flushleft}}
\label{{tab6}}
\end{{adjustwidth}}
\end{{table}}"""


# --------------------------------------------------------------------------- S1 Table rows
def s1_rows() -> str:
    sw, w0, w1, de = S.load("rev_same"), S.load("rev_w0"), S.load("rev_w1"), S.load("rev_desc")
    coh = S.load("rev_cohort")
    NL = S.neutral()["analyses"]["revised"]["windows"]
    rows, am, co = de["rows"], de["amounts"], de["constants"]
    at = w0["spender_account_types"]
    n1, n0 = NL["W1"], NL["W0"]
    # traders with a liquidation in W0: not stored as such; all recipients and the
    # stated share of the others had none
    o0 = n0["recipients"]["others"]
    liq0 = round(o0["n"] * (1 - o0["share_no_liquidation"]))
    assert abs(o0["n"] * (1 - o0["share_no_liquidation"]) - liq0) < 1e-9
    assert n1["recipients"]["recipients"]["share_no_liquidation"] == 1.0
    assert n0["recipients"]["recipients"]["share_no_liquidation"] == 1.0
    o1 = n1["recipients"]["others"]
    assert round(o1["n"] * (1 - o1["share_no_liquidation"])) == w1["traders_liquidated"]
    g = sw["graph"]
    L = []
    add = L.append
    add(r"\multicolumn{4}{l}{\emph{Windows}} \\")
    add(r"Scores frozen at & 30 Jun 2026, 23:59:59 UTC & 31 Mar 2026, 23:59:59 UTC & 30 Jun 2026, 23:59:59 UTC \\")
    add(r"Events behind the scores & 1 Oct 2023 -- 30 Jun 2026 & 1 Oct 2023 -- 31 Mar 2026 & 1 Oct 2023 -- 30 Jun 2026 \\")
    add(r"Labels counted & -- & 1 Apr -- 30 Jun 2026 & 1 Jul -- 30 Sep 2026 \\")
    add(r"\addlinespace")
    add(r"\multicolumn{4}{l}{\emph{Contracts scored}} \\")
    add(f"Matched cohort & {intc(coh['cohort'])} (of the plan's {intc(coh['registered_cohort'])}) & -- & -- \\\\")
    add(f"Spender cohort & -- & {intc(w0['spenders'])}$^{{a}}$ & {intc(w1['spenders'])} \\\\")
    add(f"\\quad gained $\\geq 1$ new approval pair & -- & {intc(w0['gained_new_approvals'])} & {intc(w1['gained_new_approvals'])} \\\\")
    add(f"\\quad gained $\\geq 1$ new transfer sender & -- & {intc(w0['gained_new_senders'])} & {intc(w1['gained_new_senders'])} \\\\")
    add(f"Trader cohort (GMX~V2 contract accounts, $\\geq 3$ closes) & -- & {n0['n']} & {n1['n']} \\\\")
    add(f"\\quad recipients (in-approve degree above zero) & -- & {n0['recipients']['recipients']['n']} & {n1['recipients']['recipients']['n']} \\\\")
    add(f"\\quad highest in-approve degree & -- & {int(n0['max_in_approve_degree'])} & {int(n1['max_in_approve_degree'])} \\\\")
    add(f"\\quad traders with $\\geq 1$ liquidation & -- & {liq0}$^{{b}}$ & {w1['traders_liquidated']} \\\\")
    add(f"\\quad traders with every close liquidated & -- & not recorded & {w1['traders_all_liquidated']} \\\\")
    add(r"\addlinespace")
    add(r"\multicolumn{4}{l}{\emph{Graphs (five tokens, ego network of the matched cohort)}} \\")
    add(f"Allowance graph, nodes / edges & {intc(g['allowance']['nodes'])} / {intc(g['allowance']['edges'])} & -- / {intc(w0['graph']['allowance_edges'])}$^{{c}}$ & as same window \\\\")
    add(f"Transfer graph, nodes / edges & {intc(g['transfer']['nodes'])} / {intc(g['transfer']['edges'])} & -- / {intc(w0['graph']['transfer_edges'])}$^{{c}}$ & as same window \\\\")
    add(f"Cohort contracts outside the allowance / transfer / both graphs & {intc(g['cohort_outside_allowance'])} / {intc(g['cohort_outside_transfer'])} / {intc(g['cohort_outside_both'])} & -- & -- \\\\")
    add(r"\addlinespace")
    add(r"\multicolumn{4}{l}{\emph{Events and amounts}} \\")
    add(f"Approval logs kept (share of the plan's ego extraction) & {intc(rows['revised_ego']['approvals'])} ({pct(rows['revised_share_of_registered']['approvals'])}) & -- & {intc(rows['revised_ego']['approvals_w1'])} in Jul--Sep \\\\")
    add(f"Transfer logs kept (share of the plan's ego extraction) & {intc(rows['revised_ego']['transfers'])} ({pct(rows['revised_share_of_registered']['transfers'])}) & -- & {intc(rows['revised_ego']['transfers_w1'])} in Jul--Sep \\\\")
    add(f"Positive latest allowances at the anchor & {intc(am['latest_allowances_tobs'])} & -- & -- \\\\")
    add(f"\\quad unlimited & {intc(am['unlimited_allowances'])} ({pct(am['unlimited_share'])}) & -- & -- \\\\")
    add(f"\\quad worth at least the cap $U$ & {intc(am['allowances_at_or_above_cap'])} ({pct(am['allowances_at_or_above_cap_share'])}) & -- & -- \\\\")
    add(f"Owners with a positive latest allowance & {intc(am['owners'])} & -- & -- \\\\")
    add(f"Medians $m_T$ / $m_A$ and cap $U$ (USD, from events up to $t_1$) & \\multicolumn{{3}}{{l}}{{{co['m_transfer_usd']:.0f} / {co['m_allowance_usd']:.0f} / {intc(int(co['cap_allowance_usd']))}}} \\\\")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- write
def replace_block(text: str, tag: str, content: str) -> str:
    pat = re.compile(rf"(% BEGIN GENERATED {tag} \(make_tables\.py; do not edit by hand\)\n).*?(% END GENERATED {tag}\n)", re.S)
    if not pat.search(text):
        sys.exit(f"markers for {tag} not found in main.tex")
    return pat.sub(lambda m: m.group(1) + content + "\n" + m.group(2), text)


def main() -> None:
    S.parse_args(__doc__.splitlines()[0])
    text = MAIN.read_text(encoding="utf-8")
    for tag, fn in (("tab1", table1), ("tab2", table2), ("tab3", table3),
                    ("tab4", table4), ("tab5", table5), ("tab6", table6)):
        text = replace_block(text, tag, fn())
    MAIN.write_text(text, encoding="utf-8")
    S1_ROWS.write_text("% Generated by make_tables.py from the published summaries; do not edit by hand.\n"
                       + s1_rows(), encoding="utf-8")
    print("wrote tables 1-6 into", MAIN.name, "and", S1_ROWS.relative_to(HERE))


if __name__ == "__main__":
    main()
