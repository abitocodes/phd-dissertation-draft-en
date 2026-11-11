#!/usr/bin/env python3
"""Tables 1-7 of Manuscript A and the rows of S1 Table, generated from the published JSON.

PLOS ONE wants the tables inside the single main.tex, so this script writes each table
between the markers

    % BEGIN GENERATED tabN (make_tables.py; do not edit by hand)
    ...
    % END GENERATED tabN

of main.tex, and writes the four row files of S1 Table (supporting/S1_Table_rows*.tex). No
number is typed by hand: every value is read from the summaries in the public repository
(checked against their SHA256SUMS.txt by data_sources.py) or from
analysis/closed-form/closed_form_check.json.

    Table 1  data and graphs of the contract graph at both freezes, closed-form fit
    Table 2  discovery-order test: AUC of every ordering in the deciding run, the decision
    Table 3  contrasts outside the decision, items 1 to 4 of the protocol's list
    Table 4  the decision contrasts under other settings (items 5 and 6; no verdict)
    Table 5  same-window intended-construct check
    Table 6  spender holdouts W0 and W1 with the count contrasts
    Table 7  the registered analysis beside the main analysis

After writing, the script checks that main.tex quotes the verdict sentence of the deciding
run word for word (discovery/discovery_tobs_both.json : decision.statements).

    CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation python3 make_tables.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))                   # also under python -I (isolated mode)
import data_sources as S  # noqa: E402
from data_sources import auc_ci, ci, d4, delta_ci, intc, num, pct, tau_ci  # noqa: E402

MAIN = HERE / "main.tex"
SUPP = HERE / "supporting"
A, T = "future_new_approvers", "future_new_transfer_senders"
TOBS = "$T_{\\mathrm{obs}}$"

# Orderings of the discovery-order test in the order of the protocol (section 4).
ORDERINGS = (
    ("bfs", "Breadth-first (BFS)"), ("random", "Random"), None,
    ("ib_a", "$\\mathrm{IB}'_A$ (allowance backlinks)"), ("ib_t", "$\\mathrm{IB}'_T$ (transfer backlinks)"),
    ("ib_u", "$\\mathrm{IB}'_U$ (contract backlinks)"), None,
    ("endorserank", "EndorseRank$'$"), ("endorserank_activity", "EndorseRank-activity$'$"), ("awp", "AWP$'$"), None,
    ("cpr_l100", "C-PR$'$ ($\\lambda=1$)"), ("cpr_l0", "C-PR$'$ ($\\lambda=0$)"),
    ("cpr_l25", "C-PR$'$ ($\\lambda=0.25$)"), ("cpr_l50", "C-PR$'$ ($\\lambda=0.5$)"),
    ("cpr_l75", "C-PR$'$ ($\\lambda=0.75$)"), ("spr", "S-PR$'$"),
)
SHORT = {"bfs": "BFS", "ib_a": "$\\mathrm{IB}'_A$", "ib_t": "$\\mathrm{IB}'_T$", "ib_u": "$\\mathrm{IB}'_U$",
         "endorserank": "EndorseRank$'$", "endorserank_activity": "EndorseRank-activity$'$", "awp": "AWP$'$",
         "cpr_l100": "C-PR$'$ ($\\lambda=1$)", "cpr_l0": "C-PR$'$ ($\\lambda=0$)", "cpr_l50": "C-PR$'$",
         "cpr_l25": "C-PR$'$ ($\\lambda=0.25$)", "cpr_l75": "C-PR$'$ ($\\lambda=0.75$)", "spr": "S-PR$'$"}
RUN_NAMES = {("tobs", "both"): f"{TOBS}, \\texttt{{both}}", ("tobs", "out"): f"{TOBS}, \\texttt{{out}}",
             ("t1", "both"): "$t_1$, \\texttt{both}", ("t1", "out"): "$t_1$, \\texttt{out}"}


def contrast(lst: list[dict], label: str, outcome: str | None = None) -> dict:
    for c in lst:
        if c["label"] == label and (outcome is None or c.get("outcome") == outcome):
            return c
    sys.exit(f"contrast not found: {label} / {outcome}")


def sci(x: float) -> str:
    m, e = f"{x:.2e}".split("e")
    return f"${m}\\times10^{{{int(e)}}}$"


def n_pct(d: dict) -> str:
    """'4{,}270 (66.3\\%)' from a coverage block with n and share."""
    return f"{intc(d['n'])} ({pct(d['share'])})"


def frame(caption: str, size: str, colspec: str, head: str, body: str, note: str, label: str,
          extra: str = "") -> str:
    """One PLOS table: bold caption, booktabs body, notes in flushleft, label at the end."""
    return (
        "\\begin{table}[!ht]\n\\begin{adjustwidth}{-2.25in}{0in}\n\\centering\n"
        f"\\caption{{{{\\bf {caption}}}}}\n{size}\n{extra}"
        f"\\begin{{tabular}}{{{colspec}}}\n\\toprule\n{head}\n\\midrule\n{body}\n\\bottomrule\n\\end{{tabular}}\n"
        f"\\begin{{flushleft}}{note}\n\\end{{flushleft}}\n\\label{{{label}}}\n\\end{{adjustwidth}}\n\\end{{table}}"
    )


def hdr(text: str, cols: int) -> str:
    return f"\\multicolumn{{{cols}}}{{l}}{{\\emph{{{text}}}}} \\\\"


def boot(run: dict) -> str:
    b = run["protocol"]["bootstrap"]
    return f"{intc(b['resamples'])} resamples (seed {b['seed']})"


def statement() -> str:
    """The verdict sentence of the deciding run, as the summary records it."""
    st = S.discovery("tobs", "both")["decision"]["statements"]
    assert len(st) == 1, "the two importances were expected to share one statement"
    return st[0]


# --------------------------------------------------------------------------- Table 1
def table1() -> str:
    de, sw, w0, w1 = S.load("rev_desc"), S.load("rev_same"), S.load("rev_w0"), S.load("rev_w1")
    coh, coh0 = S.load("rev_cohort"), S.load("rev_cohort_t1")
    cf = {"tobs": S.closed_form()[("revised", "same_window")], "t1": S.closed_form()[("revised", "W0")]}
    g = {t: S.discovery(t, "both")["sizes"]["graph"] for t in ("tobs", "t1")}
    al, pr = de["allowances"], de["pairs"]
    cov = {"tobs": (sw["cohort_coverage"]["cohort_tobs"], w1["cohort_coverage"]["spenders_w1"]),
           "t1": (w0["cohort_coverage"]["cohort_t1"], w0["cohort_coverage"]["spenders_w0"])}
    for t in ("tobs", "t1"):
        assert g[t]["allow_pairs"] == pr[t]["allowance_capped"]["pairs"]
        assert g[t]["transfer_pairs"] == pr[t]["transfer"]["pairs"]
        tot = al[t]["total"]
        assert tot["n_positive_eff"] + tot["n_capped_to_zero"] == tot["n_latest_positive"]
    assert g["tobs"]["nodes"] == sw["union_graph"]["nodes"] and g["tobs"]["edges"] == sw["union_graph"]["pairs"]
    assert g["t1"]["nodes"] == w0["union_graph"]["nodes"] and g["t1"]["edges"] == w0["union_graph"]["pairs"]
    assert cf["tobs"]["scored_set_size"] == coh["cohort"] == sw["cohort"] == cov["tobs"][0]["n"]
    assert cf["t1"]["scored_set_size"] == w0["spenders"] == cov["t1"][1]["n"]
    assert coh0["cohort"] == cov["t1"][0]["n"] and w1["spenders"] == cov["tobs"][1]["n"]
    assert cf["tobs"]["allowance_graph_edges"] == sw["graph"]["allowance"]["edges"]
    assert cf["t1"]["allowance_graph_edges"] == w0["graph"]["allowance_edges"]

    def both(fn) -> str:
        return f"{fn('tobs')} & {fn('t1')}"

    def share(t: str, key: str, sh: str) -> str:
        tot = al[t]["total"]
        return f"{intc(tot[key])} ({pct(tot[sh])})"

    def union(t: str) -> str:
        return f"{intc(g[t]['nodes'])} / {intc(g[t]['edges'])}"

    rows = [
        f"Score window & {S.span('score_tobs')} & {S.span('score_t1')} \\\\",
        f"Positive latest allowances between contracts$^{{a}}$ & {both(lambda t: intc(al[t]['total']['n_latest_positive']))} \\\\",
        f"\\quad unlimited & {both(lambda t: share(t, 'n_unlimited', 'share_unlimited'))} \\\\",
        f"\\quad capped to zero (the owner holds no balance) & {both(lambda t: share(t, 'n_capped_to_zero', 'share_capped_to_zero'))} \\\\",
        f"\\quad positive after the balance cap & {both(lambda t: intc(al[t]['total']['n_positive_eff']))} \\\\",
        f"Allowance layer: owner--spender pairs & {both(lambda t: intc(pr[t]['allowance_capped']['pairs']))} \\\\",
        "\\quad owner contracts / spender contracts & "
        + both(lambda t: f"{intc(pr[t]['allowance_capped']['sources'])} / {intc(pr[t]['allowance_capped']['destinations'])}") + " \\\\",
        f"\\quad pairs of the owner contract with the most pairs & {both(lambda t: intc(pr[t]['allowance_capped']['largest_source_pairs']))} \\\\",
        f"Transfer layer: sender--recipient pairs & {both(lambda t: intc(pr[t]['transfer']['pairs']))} \\\\",
        f"Union graph: contracts with a pair / pairs & {both(union)} \\\\",
        "\\quad giant SCC / IN / OUT / other & "
        + both(lambda t: " / ".join(intc(g[t][k]) for k in ("scc", "in", "out", "other"))) + " \\\\",
        "\\midrule",
        f"Cohort of the freeze (contracts) & {intc(coh['cohort'])} (matched cohort) & {intc(coh0['cohort'])} (W0 cohort) \\\\",
        f"\\quad in the union graph & {both(lambda t: n_pct(cov[t][0]['union_graph']))} \\\\",
        f"\\quad in the allowance layer & {both(lambda t: n_pct(cov[t][0]['allowance_layer']))} \\\\",
        f"Spender cohort (contracts) & {intc(w1['spenders'])} (W1) & {intc(w0['spenders'])} (W0) \\\\",
        f"\\quad in the union graph & {both(lambda t: n_pct(cov[t][1]['union_graph']))} \\\\",
        f"\\quad in the allowance layer & {both(lambda t: n_pct(cov[t][1]['allowance_layer']))} \\\\",
        "\\midrule",
        f"Closed form of EndorseRank$^{{b}}$: contracts checked & {intc(cf['tobs']['scored_set_size'])} (matched cohort) & "
        f"{intc(cf['t1']['scored_set_size'])} (W0 spenders) \\\\",
        f"\\quad spenders among them (allowance in-edge) & {both(lambda t: intc(cf[t]['spenders']))} \\\\",
        f"\\quad depth one (no owner has an in-edge) & {both(lambda t: intc(cf[t]['depth_one_spenders']))} \\\\",
        f"\\quad deeper (an owner is itself approved) & {both(lambda t: intc(cf[t]['deeper_spenders']))} \\\\",
        f"\\quad common score $c$ of nodes without in-edges & {both(lambda t: sci(cf[t]['c']))} \\\\",
        f"\\quad within 1\\% of the closed form: depth-one spenders & {both(lambda t: pct(cf[t]['within_1pct_depth_one']))} \\\\",
        f"\\quad within 1\\% of the closed form: deeper spenders & {both(lambda t: pct(cf[t]['within_1pct_deeper']))} \\\\",
        f"\\quad within 1\\% of the closed form: all spenders & {both(lambda t: pct(cf[t]['within_1pct_all']))} \\\\",
    ]
    unl = sci(de["constants"]["unlimited_base_units"])
    er_edges = sw["graph"]["allowance"]["edges"]
    note = (
        "Every node is a contract other than a smart account, and every edge joins two contracts; the edges are read "
        "from the events of WETH, USDC, USDT0, ARB and WBTC on the whole chain inside the score window, the twelve "
        f"months before the freeze. The graph numbers {intc(de['nodes']['contracts'])} contracts over both freezes. The "
        "union graph holds the distinct ordered pairs of different contracts with an edge in either layer; the pair "
        "counts of the two layers also include the pairs of a contract with itself ("
        + "; ".join(f"{intc(pr[t]['transfer']['self_pairs'])} transfer pairs and {intc(pr[t]['allowance_capped']['self_pairs'])} "
                    f"allowance pairs at {lab}" for t, lab in (("tobs", TOBS), ("t1", "$t_1$")))
        + "). The bow-tie (giant strongly connected component, SCC; contracts that reach it, IN; contracts reached from "
        "it, OUT) is that of the union graph. A member of a cohort outside a graph scores zero under that graph's scores. "
        "$^{a}$The latest \\texttt{Approval} of each (token, owner contract, spender contract) in the score window, kept "
        f"when its value is positive; unlimited means at least {unl} base units. Each allowance counts up to the owner's "
        "balance of the token at the freeze, so an allowance whose owner holds no balance is no edge. A pair sums its "
        f"tokens; at {TOBS} {intc(er_edges)} of the pairs have a positive EndorseRank weight in floating point. "
        "$^{b}$\\Eq{eq:closed-form}, derived in Results; a spender is a contract of the checked set with an allowance "
        "in-edge of positive weight, and it has depth one when none of its owner contracts has an in-edge itself. "
        "Damping $d=0.85$. Sources: \\texttt{describe/describe.json} (\\texttt{allowances}, \\texttt{pairs}, "
        "\\texttt{nodes}); \\texttt{discovery/discovery\\_tobs\\_both.json} and \\texttt{discovery\\_t1\\_both.json} "
        "(\\texttt{sizes.graph}); \\texttt{same-window}, \\texttt{holdout-w0} and \\texttt{window-w1/eval\\_summary.json} "
        "(\\texttt{cohort\\_coverage}, \\texttt{closed\\_form}, the last through "
        "\\texttt{analysis/closed-form/closed\\_form\\_check.json}); the configuration files for the windows."
    )
    head = (f" & {TOBS}, {S.day(S.windows()['score_tobs'][1])} & $t_1$, {S.day(S.windows()['score_t1'][1])} \\\\\n"
            " & (same window and W1) & (W0) \\\\")
    return frame("The contract graph at the two freezes and the fit of the closed form for EndorseRank.",
                 "\\footnotesize", "lrr", head, "\n".join(rows), note, "tab1")


# --------------------------------------------------------------------------- Table 2
def table2() -> str:
    d = S.discovery("tobs", "both")
    assert d["decides"] and d["is_primary"] and d["mode"] == "both" and d["window"] == "tobs"
    hots = ("i_t@q", "i_a@q")
    lines = []
    for item in ORDERINGS:
        if item is None:
            lines.append("\\addlinespace")
            continue
        key, name = item
        lines.append(f"{name} & " + " & ".join(auc_ci(S.auc(d, h, key)) for h in hots) + " \\\\")
    lines.append("\\midrule")
    lines.append("$\\delta'$ (diagnostic, outside every comparison) & "
                 + " & ".join(auc_ci(S.auc(d, h, "delta")) for h in hots) + " \\\\")
    lines.append("\\midrule")
    lines.append(hdr("References that are not crawls", 3))
    for key, name in (("ref_cpr", "Order by C-PR of the full graph"),
                      ("ref_ib_u", "Order by union in-degree of the full graph"),
                      ("ref_ideal", "Ideal order (hot contracts first)")):
        lines.append(f"{name} & " + " & ".join(auc_ci(S.auc(d, h, key)) for h in hots) + " \\\\")
    lines.append("Random curve & " + " & ".join(num(S.auc(d, h, "random_curve"), nd=4) for h in hots) + " \\\\")
    lines.append("\\midrule")
    lines.append(hdr("The decision", 3))
    dec = d["decision"]
    for h, imp in zip(hots, ("i_t", "i_a")):
        v = dec[imp]
        lo1, lo2, hi2 = v["D1"]["lo"], v["D2"]["lo"], v["D2"]["hi"]
        want = "V3" if not lo1 > 0 else ("V1" if lo2 > 0 else "V2")
        assert v["verdict"] == want, f"verdict on {imp} does not follow from its intervals"
        assert v["n_hot"] == d["hot_sets"][h]
        assert (hi2 < 0) == bool(v.get("extra")), "the added sentence does not follow from the interval of D2"
    lines.append("Hot contracts, $|H_q|$ & " + " & ".join(intc(dec[i]["n_hot"]) for i in ("i_t", "i_a")) + " \\\\")
    lines.append("$D_1$: C-PR$'$ $-$ BFS & " + " & ".join(d4(dec[i]["D1"]) for i in ("i_t", "i_a")) + " \\\\")
    lines.append("$D_2$: C-PR$'$ $-$ $\\mathrm{IB}'_U$ & " + " & ".join(d4(dec[i]["D2"]) for i in ("i_t", "i_a")) + " \\\\")
    words = {"V1": "V1", "V2": "V2", "V3": "V3"}

    def verdict(i: str) -> str:
        v = dec[i]
        return words[v["verdict"]] + ("; $\\mathrm{IB}'_U$ sooner" if v.get("extra") else "")

    lines.append("Verdict & " + " & ".join(verdict(i) for i in ("i_t", "i_a")) + " \\\\")
    u = d["sizes"]["universe"]
    p = d["protocol"]
    note = (
        f"Deciding run: freeze {TOBS}, \\texttt{{both}} mode (a visit reveals a contract's in-edges and out-edges). The "
        f"universe $\\mathcal{{U}}$ is the weakly connected component that holds the giant strongly connected component: "
        f"{intc(u['U'])} contracts and {intc(u['E_U'])} union pairs. $\\mathrm{{AUC}}_{{10\\%}}$ is the mean over the hot "
        "contracts of $\\max(0,1-t_h/\\lceil 0.1|\\mathcal{U}|\\rceil)$, with $t_h$ the visit at which the crawl reaches "
        f"hot contract $h$, averaged over {len(d['seeds'])} seeds from the giant strongly connected component; a crawl "
        f"recomputes its ordering each time its visits have grown by the share $\\rho={p['rho']}$. $H_q(I_T)$ and "
        f"$H_q(I_A)$ hold the contracts of the universe with the largest positive user-account inflow and "
        f"user-authorized value, $q={p['q']}$ of the universe with ties. A primed name is the count or walk computed on "
        "the contracts read so far. Brackets: 95\\% percentile intervals of a paired bootstrap over the hot contracts, "
        f"{boot(d)}. V1: both intervals of $D_1$ and $D_2$ above 0; V2: the interval of $D_1$ above 0 and that of "
        "$D_2$ not; V3: the interval of $D_1$ not above 0; an interval of $D_2$ below 0 adds that the crawl ordered by "
        f"contract backlinks was sooner. Statement recorded with the verdict: ``{statement()}'' The test was defined "
        "after the registered results were known; it decides no rule of the analysis plan or the registration. Source: "
        "\\texttt{discovery/discovery\\_tobs\\_both.json}, keys \\texttt{auc}, \\texttt{decision}, \\texttt{sizes}."
    )
    head = ("Ordering & $\\mathrm{AUC}_{10\\%}$ on $H_q(I_T)$ [95\\% interval] & "
            "$\\mathrm{AUC}_{10\\%}$ on $H_q(I_A)$ [95\\% interval] \\\\")
    return frame("Discovery-order test: every ordering in the deciding run, and the decision.",
                 "\\footnotesize", "lcc", head, "\n".join(lines), note, "tab2")


# --------------------------------------------------------------------------- Table 3
def pair_rows(items: list[dict]) -> list[str]:
    by: dict[tuple[str, str], dict[str, dict]] = {}
    for x in items:
        by.setdefault((x["a"], x["b"]), {})[x["hot_set"]] = x
    return [f"{SHORT[a]} $-$ {SHORT[b]} & {d4(hs['i_t@q'])} & {d4(hs['i_a@q'])} \\\\" for (a, b), hs in by.items()]


def table3() -> str:
    d = S.discovery("tobs", "both")
    fo = d["fixed_order"]
    lines = [hdr("1. Each walk$'$ against the count it smooths", 3), *pair_rows(fo["1_walk_vs_count"]),
             "\\midrule", hdr("2. Among the walks", 3), *pair_rows(fo["2_walk_contrasts"]),
             "\\midrule", hdr("3. Other values of $\\lambda$", 3)]
    for m, lam in (("cpr_l25", "0.25"), ("cpr_l75", "0.75")):
        hs = fo["3_lambda"][m]
        for key, label in (("D1", f"C-PR$'$ ($\\lambda={lam}$) $-$ BFS"),
                           ("D2", f"C-PR$'$ ($\\lambda={lam}$) $-$ $\\mathrm{{IB}}'_U$"),
                           ("vs_cpr_l50", f"C-PR$'$ ($\\lambda={lam}$) $-$ C-PR$'$ ($\\lambda=0.5$)")):
            lines.append(f"{label} & {d4(hs['i_t@q'][key])} & {d4(hs['i_a@q'][key])} \\\\")
    cho = fo["4_cho"]
    assert cho["replication_contrast"]["point"] == cho["hot_sets"]["ib_u@q"]["D2"]["point"]
    lines += ["\\midrule", hdr("4. Hot sets in the manner of Cho et al.\\ (an intended-construct check)", 3)]
    names = {"ib_u@q": "$H_q(\\mathrm{IB}_U)$", "ir@q": "$H_q(\\mathrm{IR})$"}
    for h in ("ib_u@q", "ir@q"):
        v = cho["hot_sets"][h]
        n = intc(d["hot_sets"][h])
        for key, label in (("D1", "C-PR$'$ $-$ BFS"), ("D2", "C-PR$'$ $-$ $\\mathrm{IB}'_U$")):
            lines.append(f"{label} on {names[h]} ({n} contracts) & \\multicolumn{{2}}{{c}}{{{d4(v[key])}}} \\\\")
    note = (
        f"Deciding run ({TOBS}, \\texttt{{both}} mode); the rows follow the order of the protocol's list. Each cell is a "
        "difference of $\\mathrm{AUC}_{10\\%}$ between two orderings with the 95\\% percentile interval of the paired "
        f"bootstrap over the hot contracts, {boot(d)}; an interval above 0 means that the first ordering reached the hot "
        "contracts sooner. C-PR$'$ without a value of $\\lambda$ is C-PR$'$ at $\\lambda=0.5$; C-PR$'$ ($\\lambda=1$) "
        "and C-PR$'$ ($\\lambda=0$) are its allowance and transfer layers walked alone. Block 1 sets each walk beside the "
        "backlink count of the layer it walks. In block 2, C-PR$'$ against C-PR$'$ ($\\lambda=0$) shows what the "
        "allowance layer adds to the coupled walk; C-PR$'$ and AWP$'$ differ in the weights and restarts of their "
        "transfer layer as well. In block 4 the hot sets are defined on the edges that the orderings read, "
        "the union in-degree $\\mathrm{IB}_U$ and C-PR of the full graph ($\\mathrm{IR}$), so agreement there is an "
        "intended-construct check; C-PR$'$ minus $\\mathrm{IB}'_U$ on $H_q(\\mathrm{IB}_U)$ is the contrast that the "
        "protocol calls the replication contrast. None of these rows carries a verdict. Source: "
        "\\texttt{discovery/discovery\\_tobs\\_both.json}, key \\texttt{fixed\\_order} (items 1 to 4)."
    )
    head = "Contrast & On $H_q(I_T)$ & On $H_q(I_A)$ \\\\"
    return frame("Discovery-order test: the contrasts reported outside the decision, in the order of the protocol.",
                 "\\footnotesize", "lcc", head, "\n".join(lines), note, "tab3")


# --------------------------------------------------------------------------- Table 4
def table4() -> str:
    d = S.discovery("tobs", "both")
    sens = d["fixed_order"]["5_sensitivities"]
    dec = d["decision"]

    def two(label: str, it: dict, ia: dict) -> list[str]:
        return [f"{label} & $D_1$ & {d4(it['D1'])} & {d4(ia['D1'])} \\\\",
                f" & $D_2$ & {d4(it['D2'])} & {d4(ia['D2'])} \\\\"]

    q2, nh, cnt = sens["q_secondary"], sens["no_hubs"], sens["importance_counts"]
    sb, rq, xs = sens["seed_bootstrap"], sens["rho_quarter"], sens["x"]
    p = d["protocol"]
    assert rq["rho"] == p["rho_quarter"]
    o = S.discovery("tobs", "out")
    # the rows of block 5 keep the order in which the protocol lists its sensitivities (section 6, item 5)
    lines = [hdr(f"The decision ({TOBS}, \\texttt{{both}} mode, $x=10\\%$, $q=1\\%$, $\\rho={p['rho']}$)", 4),
             *two("As decided", dec["i_t"], dec["i_a"]), "\\midrule",
             hdr("5. Sensitivities of the deciding run, one setting varied at a time", 4),
             *two("Area over $x=5\\%$ of the visits", xs["x=0.05"]["i_t@q"], xs["x=0.05"]["i_a@q"]),
             *two("Area over $x=20\\%$ of the visits", xs["x=0.2"]["i_t@q"], xs["x=0.2"]["i_a@q"]),
             *two(f"Hot share $q={100 * q2['q']:.0f}\\%$$^{{a}}$", q2["i_t@q2"], q2["i_a@q2"]),
             *two(f"Hot sets without the {intc(nh['hubs'])} hubs$^{{b}}$", nh["i_t@q-nohubs"], nh["i_a@q-nohubs"]),
             *two("Importance by counts ($N_T$, $N_A$)$^{c}$", cnt["n_t@q"], cnt["n_a@q"]),
             *two(f"The other reveal mode (\\texttt{{out}}) at {TOBS}$^{{d}}$", o["decision"]["i_t"], o["decision"]["i_a"]),
             *two(f"Recomputed four times as often ($\\rho={rq['rho']}$, {rq['seeds']} seeds)",
                  rq["contrasts"]["i_t@q"], rq["contrasts"]["i_a@q"]),
             *two("Bootstrap over the seeds", sb["i_t@q"], sb["i_a@q"])]
    lines += ["\\midrule", hdr("6. The other freeze, $t_1$", 4)]
    for mode in ("both", "out"):
        r = S.discovery("t1", mode)
        assert not r["decides"] and not r["decision"]["statements"]
        lines += two(f"\\texttt{{{mode}}} mode$^{{d}}$", r["decision"]["i_t"], r["decision"]["i_a"])
    assert not o["decides"] and not o["decision"]["statements"]
    hot = d["hot_sets"]
    same = hot["i_a@q"] == hot["i_a@q2"]
    sizes = "; ".join(
        f"{RUN_NAMES[(t, m)]}: {intc(S.discovery(t, m)['sizes']['universe']['U'])} contracts, "
        f"{intc(S.discovery(t, m)['hot_sets']['i_t@q'])} and {intc(S.discovery(t, m)['hot_sets']['i_a@q'])} hot contracts"
        for t, m in S.RUNS[1:])
    note = (
        "Differences of $\\mathrm{AUC}$ with 95\\% percentile intervals: $D_1$ is C-PR$'$ minus BFS and $D_2$ is C-PR$'$ "
        f"minus $\\mathrm{{IB}}'_U$. Unless a row says otherwise the interval is that of the paired bootstrap over the hot "
        f"contracts, {boot(d)}. The decision is read in the first block only; no other row carries a verdict. The rows "
        "of block 5 keep the order of the protocol's list. Three items of that list have no row: the share of the "
        "summed importance held by the visited contracts (given in the text and in S1 Table), a second curve and the "
        "share of the union pairs read (in the published summaries, not reported here). "
        + (f"$^{{a}}$Only {intc(hot['i_a@q'])} contracts of the universe have a positive $I_A$, fewer than 1\\% of it, so "
           "the hot set of $I_A$ is the same at both shares. " if same else "$^{a}$The secondary share of the protocol. ")
        + "$^{b}$The contracts with the highest union in-degree of the full graph, taken out of the hot sets and kept "
        "in the graph. $^{c}$Hot sets by the number of user accounts that transferred, or had authorized, at least one "
        "US dollar. $^{d}$In the \\texttt{out} mode a visit reveals out-edges only and the universe is the giant "
        "strongly connected component with the contracts reached from it. Universes and hot sets ($I_T$ and $I_A$) of "
        f"the three runs outside the decision: {sizes}. The two freezes share nine months of their score windows and "
        "are not independent. Sources: \\texttt{discovery/discovery\\_tobs\\_both.json} (\\texttt{decision}, "
        "\\texttt{fixed\\_order.5\\_sensitivities}), \\texttt{discovery\\_tobs\\_out.json}, "
        "\\texttt{discovery\\_t1\\_both.json} and \\texttt{discovery\\_t1\\_out.json} (\\texttt{decision})."
    )
    head = "Setting & Contrast & On $H_q(I_T)$ & On $H_q(I_A)$ \\\\"
    return frame("Discovery-order test: the two decision contrasts under other settings, in the other reveal mode "
                 "and at the other freeze.", "\\footnotesize", "llcc", head, "\n".join(lines), note, "tab4")


# --------------------------------------------------------------------------- Table 5
def table5() -> str:
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
    im, iso, ties = sw["inter_method"], sw["isolated_rule"], sw["ties"]
    cc = im["concordance"]
    body = "\n".join(lines) + "\n" + "\n".join([
        "\\midrule",
        hdr("Paired differences $\\dt$ [95\\% CI] and agreement of the two rankings", 4),
        f"EndorseRank $-$ AWP, allowance family & \\multicolumn{{3}}{{l}}{{{delta_ci(er_awp_all)}}} \\\\",
        f"AWP $-$ EndorseRank, transfer family & \\multicolumn{{3}}{{l}}{{{delta_ci(awp_er_tr)}}} \\\\",
        f"$\\tau_b$ between EndorseRank and AWP & \\multicolumn{{3}}{{l}}{{{tau_ci(im['endorserank_vs_awp'])}}} \\\\",
        f"\\quad pairs of contracts ordered by both scores & \\multicolumn{{3}}{{l}}{{{intc(cc['ordered_by_both'])} of "
        f"{intc(cc['pairs'])} ({pct(cc['share_ordered_by_both'])}); {pct(cc['discordant_share_of_ordered'])} of them discordant}} \\\\",
        "\\midrule",
        hdr("Contracts outside a graph kept as isolated nodes (the sensitivity analysis fixed in the plan)", 4),
        f"EndorseRank, allowance family & \\multicolumn{{3}}{{l}}{{{tau_ci(iso['endorserank_iso']['allowance'])}}} \\\\",
        f"AWP, transfer family & \\multicolumn{{3}}{{l}}{{{tau_ci(iso['awp_iso']['transfer'])}}} \\\\",
        f"$\\tau_b$ between EndorseRank and AWP & \\multicolumn{{3}}{{l}}{{{tau_ci(im['isolated'])}}} \\\\",
    ])
    g = sw["graph"]
    note = (
        f"Matched cohort, $n={intc(sw['cohort'])}$ contracts, scores at {TOBS} "
        f"({S.day(S.windows()['score_tobs'][1])}) from the score window {S.span('score_tobs', ' to ')}; the checks are "
        "computed over the same window from the events between contracts. Each check is computed from the events of one "
        "layer: the transfer family from inbound transfers, the allowance family from the capped latest allowances "
        "received. Agreement of a score with the checks of its own edge type is therefore partly built in. The "
        "in-degree of this check counts the distinct sender contracts with self-transfers included, whereas the transfer "
        "in-degree that serves as the baseline out of window (Table~\\ref{tab6}) counts other contracts only. The "
        "Sybil-stability family averages the inbound-counterparty ratio, transfer tenure and active months. Family "
        "means are plain averages of the coefficients of their checks. A contract outside a graph scores zero: "
        f"{intc(ties['endorserank']['zeros'])} cohort contracts score zero under EndorseRank and "
        f"{intc(ties['awp']['zeros'])} under AWP ({intc(g['cohort_outside_allowance'])} and "
        f"{intc(g['cohort_outside_transfer'])} lie outside the allowance and the transfer graph, "
        f"{intc(g['cohort_outside_both'])} outside both), so the scores tie on these contracts. Paired contract "
        f"bootstrap, {fam['endorserank']['allowance']['n_boot']} resamples (seed 42); intervals are unadjusted. None of "
        "these comparisons decides a rule. Source: \\texttt{same-window/eval\\_summary.json}, keys \\texttt{families}, "
        "\\texttt{per\\_proxy}, \\texttt{contrasts}, \\texttt{inter\\_method}, \\texttt{isolated\\_rule}, \\texttt{ties}, "
        "\\texttt{graph}."
    )
    head = "Check (Kendall $\\tau_b$ [95\\% CI]) & EndorseRank & EndorseRank, activity restarts & AWP \\\\"
    return frame("Same-window agreement of each score with the checks of each edge type (intended-construct check).",
                 "\\footnotesize", "lccc", head, body, note, "tab5")


# --------------------------------------------------------------------------- Table 6
def spender_blocks() -> dict:
    """The coefficients and contrasts of the two spender holdouts (also read by figures/make_fig1.py)."""
    w0, w1, sup = S.load("rev_w0"), S.load("rev_w1"), S.load("rev_sup")
    t0, t1 = w0["taus"], w1["spender_taus"]
    ca = w0["contrasts_after"]
    er_res = w1["endorserank_results"]
    assert sup["w0"]["n"] == w0["spenders"] and sup["w1"]["n"] == w1["spenders"]
    er_awp0_a, er_awp0_t = contrast(ca, "EndorseRank minus AWP", A), contrast(ca, "EndorseRank minus AWP", T)
    # the two EndorseRank-AWP contrasts appear in both files for W0; they must agree
    assert abs(er_awp0_a["delta_tau"] - sup["w0"]["er_minus_awp_appr"]["delta_tau"]) < 1e-12
    assert abs(er_awp0_t["delta_tau"] - sup["w0"]["er_minus_awp_send"]["delta_tau"]) < 1e-12
    rec, uni = w0["receiving"], w0["in_union_graph"]
    return {
        "w0": w0, "w1": w1,
        "taus": [
            ("In-approve degree (count)", t0["t1_in_approve_degree"], t1["in_approve_degree"]),
            ("Transfer in-degree (count)", t0["t1_in_degree"], t1["in_degree"]),
            ("EndorseRank", t0["endorserank"], t1["endorserank"]),
            ("EndorseRank, activity restarts", t0["endorserank_activity"], t1["endorserank_activity"]),
            ("AWP", t0["awp"], t1["awp"]),
        ],
        "er_deg": (contrast(ca, "EndorseRank minus t1 in-approve degree", A), er_res["endorserank_minus_degree_appr"]),
        "act_deg": (sup["w0"]["er_activity_minus_degree_appr"], sup["w1"]["er_activity_minus_degree_appr"]),
        "awp_deg": (contrast(ca, "AWP minus t1 in-degree", T), er_res["awp_minus_degree_send"]),
        "act_er_a": (sup["w0"]["er_activity_minus_er_appr"], sup["w1"]["er_activity_minus_er_appr"]),
        "er_awp_a": (er_awp0_a, sup["w1"]["er_minus_awp_appr"]),
        "er_awp_t": (er_awp0_t, sup["w1"]["er_minus_awp_send"]),
        "rec_n": rec["n"],
        "rec_er_deg": contrast(rec["contrasts"], "EndorseRank minus t1 in-approve degree", A),
        "rec_awp_deg": contrast(rec["contrasts"], "AWP minus t1 in-degree", T),
        "uni_n": uni["n"],
        "uni_er_deg": contrast(uni["contrasts_after"], "EndorseRank minus t1 in-approve degree", A),
        "uni_awp_deg": contrast(uni["contrasts_after"], "AWP minus t1 in-degree", T),
    }


def table6() -> str:
    b = spender_blocks()
    w0, w1 = b["w0"], b["w1"]
    e = ""
    lines = [f"{name} & {tau_ci(a[A])} & {tau_ci(a[T])} & {tau_ci(c[A])} & {tau_ci(c[T])} \\\\"
             for name, a, c in b["taus"]]
    lines += [
        "\\midrule",
        hdr("Each walk against the count it smooths, on the label of its own edge type: $\\dt$ [95\\% CI]", 5),
        f"EndorseRank $-$ in-approve degree & {delta_ci(b['er_deg'][0])} & {e} & {delta_ci(b['er_deg'][1])} & {e} \\\\",
        f"EndorseRank, activity restarts $-$ in-approve degree & {delta_ci(b['act_deg'][0])} & {e} & {delta_ci(b['act_deg'][1])} & {e} \\\\",
        f"AWP $-$ transfer in-degree & {e} & {delta_ci(b['awp_deg'][0])} & {e} & {delta_ci(b['awp_deg'][1])} \\\\",
        hdr(f"The same in W0 among the {intc(b['uni_n'])} spenders inside the union graph$^{{a}}$", 5),
        f"EndorseRank $-$ in-approve degree & {delta_ci(b['uni_er_deg'])} & {e} & -- & {e} \\\\",
        f"AWP $-$ transfer in-degree & {e} & {delta_ci(b['uni_awp_deg'])} & {e} & -- \\\\",
        hdr(f"The same in W0 among the {intc(b['rec_n'])} spenders that another contract had paid before the freeze$^{{a}}$", 5),
        f"EndorseRank $-$ in-approve degree & {delta_ci(b['rec_er_deg'])} & {e} & -- & {e} \\\\",
        f"AWP $-$ transfer in-degree & {e} & {delta_ci(b['rec_awp_deg'])} & {e} & -- \\\\",
        "\\midrule",
        hdr("Allowance walk against transfer walk: $\\dt$ [95\\% CI]", 5),
        f"EndorseRank $-$ AWP & {delta_ci(b['er_awp_a'][0])} & {delta_ci(b['er_awp_t'][0])} & {delta_ci(b['er_awp_a'][1])} & {delta_ci(b['er_awp_t'][1])} \\\\",
    ]
    ls0, ls1 = w0["label_split"]["labels"], w1["label_split"]["labels"]
    c0, c1 = w0["cohort_coverage"]["spenders_w0"], w1["cohort_coverage"]["spenders_w1"]
    assert b["uni_n"] == c0["union_graph"]["n"]
    note = (
        "Kendall $\\tau_b$ with 95\\% percentile interval from 400 paired contract resamples (seed 42); intervals are "
        "unadjusted. Scores and counts are computed on the contract graph of the freeze. Spenders are the contracts "
        "that hold a positive latest allowance of one of the five tokens from any account, set in the score window, at "
        "the freeze. The labels count every account that newly approves or pays a spender, user accounts included: in W0 "
        f"{pct(ls0[A]['share_user_accounts'])} of the {intc(ls0[A]['total'])} new approval pairs and "
        f"{pct(ls0[T]['share_user_accounts'])} of the {intc(ls0[T]['total'])} new senders are user accounts, in W1 "
        f"{pct(ls1[A]['share_user_accounts'])} of {intc(ls1[A]['total'])} and {pct(ls1[T]['share_user_accounts'])} of "
        f"{intc(ls1[T]['total'])}. In W0, {intc(w0['gained_new_approvals'])} spenders gained at least one new approval "
        f"pair and {intc(w0['gained_new_senders'])} at least one new transfer sender; in W1, "
        f"{intc(w1['gained_new_approvals'])} and {intc(w1['gained_new_senders'])} did. "
        f"{intc(c0['outside_contract_graph']['n'])} W0 spenders ({pct(c0['outside_contract_graph']['share'])}) and "
        f"{intc(c1['outside_contract_graph']['n'])} W1 spenders ({pct(c1['outside_contract_graph']['share'])}) end no "
        "pair between contracts and score zero under every score and count. Every paired difference in this table was "
        "computed after the labels of its window were known, and none of them decides a rule. $^{a}$Subsets chosen "
        "after the results were known; -- marks contrasts that were not computed for W1. Sources: "
        "\\texttt{holdout-w0/eval\\_summary.json} (\\texttt{taus}, \\texttt{contrasts\\_after}, \\texttt{receiving}, "
        "\\texttt{in\\_union\\_graph}, \\texttt{label\\_split}, \\texttt{cohort\\_coverage}), "
        "\\texttt{window-w1/eval\\_summary.json} (\\texttt{spender\\_taus}, \\texttt{endorserank\\_results}, "
        "\\texttt{label\\_split}, \\texttt{cohort\\_coverage}), \\texttt{supplementary/supplementary.json}."
    )
    head = (f" & \\multicolumn{{2}}{{c}}{{W0: freeze {S.day(S.windows()['score_t1'][1])} ($n={intc(w0['spenders'])}$)}} & "
            f"\\multicolumn{{2}}{{c}}{{W1: freeze {S.day(S.windows()['score_tobs'][1])} ($n={intc(w1['spenders'])}$)}} \\\\\n"
            "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
            "Score at the freeze & New approval pairs & New senders & New approval pairs & New senders \\\\")
    return frame("Spender holdouts: scores frozen at each date against labels counted over the next three months.",
                 "\\footnotesize", ">{\\raggedright\\arraybackslash}p{1.95in}cccc", head, "\n".join(lines), note, "tab6",
                 extra="\\setlength{\\tabcolsep}{3pt}\n")


# --------------------------------------------------------------------------- Table 7
def table7() -> str:
    rs, rv = S.load("reg_same"), S.load("rev_same")
    r0, v0 = S.load("reg_w0"), S.load("rev_w0")
    r1, v1 = S.load("reg_w1"), S.load("rev_w1")
    rsup, vsup = S.load("reg_sup"), S.load("rev_sup")
    rb, vb = S.load("reg_bench"), S.load("rev_bench")
    cfr, cfv = S.closed_form()[("registered", "same_window")], S.closed_form()[("revised", "same_window")]
    d = S.discovery("tobs", "both")
    pick = {"reg": dict(same=rs, w0=r0, w1=r1, sup=rsup, cf=cfr, bench=rb),
            "rev": dict(same=rv, w0=v0, w1=v1, sup=vsup, cf=cfv, bench=vb)}

    def both(fn) -> str:
        return f"{fn('reg')} & {fn('rev')}"

    def ratio(k: str) -> str:
        m = pick[k]["bench"]["main"]
        return (f"{m['awp']['mean_s'] / m['endorserank']['mean_s']:.2f} / "
                f"{m['awp']['edges'] / m['endorserank']['edges']:.2f}")

    reg_start = S.day(S.windows()["registered_score_start"][0])
    tobs_end, t1_end = S.day(S.windows()["score_tobs"][1]), S.day(S.windows()["score_t1"][1])
    verdicts = " and ".join(d["decision"][i]["verdict"] for i in ("i_t", "i_a"))
    lines = [
        hdr("Definitions", 3),
        "Amounts; tokens & raw base units; every ERC-20 & US dollars; five tokens \\\\",
        f"Events behind the scores at {TOBS} & {reg_start} -- {tobs_end} & {S.span('score_tobs')} \\\\",
        f"Events behind the scores at $t_1$ & {reg_start} -- {t1_end} & {S.span('score_t1')} \\\\",
        "Nodes of the graphs & every account of the cohort's events & contracts other than smart accounts \\\\",
        "Events read for the edges & with a cohort contract at one end & between contracts, whole chain \\\\",
        "Each latest allowance counted & in full & up to the owner's balance \\\\",
        "\\midrule",
        hdr("Same window", 3),
        f"Matched cohort (contracts) & {both(lambda k: intc(pick[k]['same']['cohort']))} \\\\",
        f"Allowance / transfer edges at {TOBS} & "
        + both(lambda k: intc(pick[k]['same']['graph']['allowance']['edges']) + " / "
               + intc(pick[k]['same']['graph']['transfer']['edges'])) + " \\\\",
        f"EndorseRank, allowance family & {both(lambda k: tau_ci(pick[k]['same']['families']['endorserank']['allowance']))} \\\\",
        f"AWP, transfer family & {both(lambda k: tau_ci(pick[k]['same']['families']['awp']['transfer']))} \\\\",
        f"$\\tau_b$ between EndorseRank and AWP & {both(lambda k: tau_ci(pick[k]['same']['inter_method']['endorserank_vs_awp']))} \\\\",
        "Depth-one / all spenders within 1\\% of \\Eq{eq:closed-form} & "
        + both(lambda k: pct(pick[k]['cf']['within_1pct_depth_one']) + " / " + pct(pick[k]['cf']['within_1pct_all'])) + " \\\\",
        f"Solver time / edges, AWP over EndorseRank & {both(ratio)} \\\\",
        "\\midrule",
        hdr("Spender holdouts, each walk minus the count it smooths (computed after the labels)", 3),
        f"Spender cohorts, W0 / W1 & {both(lambda k: intc(pick[k]['w0']['spenders']) + ' / ' + intc(pick[k]['w1']['spenders']))} \\\\",
        "W0: EndorseRank $-$ in-approve degree, new pairs & "
        + both(lambda k: delta_ci(contrast(pick[k]['w0']['contrasts_after'], 'EndorseRank minus t1 in-approve degree', A))) + " \\\\",
        "W0: EndorseRank (activity) $-$ in-approve degree & "
        + both(lambda k: delta_ci(pick[k]['sup']['w0']['er_activity_minus_degree_appr'])) + " \\\\",
        "W0: AWP $-$ transfer in-degree, new senders & "
        + both(lambda k: delta_ci(contrast(pick[k]['w0']['contrasts_after'], 'AWP minus t1 in-degree', T))) + " \\\\",
        "W1: EndorseRank $-$ in-approve degree, new pairs & "
        + both(lambda k: delta_ci(pick[k]['w1']['endorserank_results']['endorserank_minus_degree_appr'])) + " \\\\",
        "W1: EndorseRank (activity) $-$ in-approve degree & "
        + both(lambda k: delta_ci(pick[k]['sup']['w1']['er_activity_minus_degree_appr'])) + " \\\\",
        "W1: AWP $-$ transfer in-degree, new senders & "
        + both(lambda k: delta_ci(pick[k]['w1']['endorserank_results']['awp_minus_degree_send'])) + " \\\\",
        "\\midrule",
        hdr("Discovery-order test", 3),
        f"Verdict on $I_T$ and on $I_A$ & no registered counterpart & {verdicts} (Table~\\ref{{tab2}}) \\\\",
    ]
    note = (
        "The registered analysis follows the analysis plan and the W1 registration as committed: amounts in raw base "
        f"units of every ERC-20 token, scores from every event since {S.day(S.windows()['registered_score_start'][0])} "
        "and graphs that hold every account of the cohort's events. The main analysis is the contract-graph analysis; "
        "it was defined after the registered results were known, so no value of its column is a registered result. No "
        "rule of the plan or the registration decides any row of this table: the count contrasts were computed after "
        "the labels of their windows were known in both analyses, and the discovery-order test belongs to the main "
        "analysis only. $\\dt$ and $\\tau_b$ with 95\\% interval from 400 paired contract resamples (seed 42). The "
        "ratios of solver time and of edges divide the values of AWP's graph by those of EndorseRank's graph in each "
        "analysis. Sources: "
        "\\texttt{same-window}, \\texttt{holdout-w0}, \\texttt{registered-w1} and \\texttt{window-w1} summaries, "
        "\\texttt{supplementary.json} and \\texttt{benchmark.json} of each analysis; "
        "\\texttt{analysis/closed-form/closed\\_form\\_check.json}; the configuration files for the windows."
    )
    head = " & Registered analysis & Main analysis (contract graph) \\\\"
    return frame("The registered analysis beside the main analysis.", "\\footnotesize", "lcc", head,
                 "\n".join(lines), note, "tab7")


# --------------------------------------------------------------------------- S1 Table rows
def s1_rows_a() -> str:
    """Panel A: events, account types, balances, graphs, universes, cohorts, labels, constants."""
    de, sw, w0, w1 = S.load("rev_desc"), S.load("rev_same"), S.load("rev_w0"), S.load("rev_w1")
    coh, coh0 = S.load("rev_cohort"), S.load("rev_cohort_t1")
    sp0, sp1 = S.load("rev_spenders_w0"), S.load("rev_spenders_w1")
    co, pilot = S.load("rev_constants"), S.load("rev_pilot")
    ev, at, al, pr, bc, imp = de["events"], de["account_types"], de["allowances"], de["pairs"], de["balance_check"], de["importance"]
    run = {(t, m): S.discovery(t, m) for t, m in S.RUNS}
    g = {t: run[(t, "both")]["sizes"]["graph"] for t in ("tobs", "t1")}
    cov = {(t, m): run[(t, m)]["diagnostics"]["coverage"] for t, m in S.RUNS}
    assert at["wallet_kind_typed"]["safe"] + at["wallet_kind_typed"]["erc4337"] + at["extension"]["moved"] \
        == at["after_extension"]["smart_account"]
    assert sum(at["after_extension"].values()) == at["addresses"] == ev["rpc_queue"]
    assert pilot["U"] == g["t1"]["U"] and pilot["WCC"] == g["t1"]["WCC"]
    L: list[str] = []
    add = L.append

    def both(label: str, fn) -> None:
        add(f"{label} & {fn('tobs')} & {fn('t1')} \\\\")

    def one(label: str, value: str) -> None:
        add(f"{label} & \\multicolumn{{2}}{{l}}{{{value}}} \\\\")

    add(hdr("Windows", 3))
    add(f"Freeze & {S.day(S.windows()['score_tobs'][1])}, 23:59:59 UTC & {S.day(S.windows()['score_t1'][1])}, 23:59:59 UTC \\\\")
    add(f"Score window (events behind the scores) & {S.span('score_tobs')} & {S.span('score_t1')} \\\\")
    add(f"Label window & {S.span('label_w1')} (W1) & {S.span('label_w0')} (W0) \\\\")
    add("\\addlinespace")
    add(hdr(f"Events of the five tokens, {S.day('2025-04-01')} to {S.day('2026-09-30')} (both freezes)", 3))
    one("\\texttt{Approval} rows of any value and non-zero \\texttt{Transfer} rows", intc(ev["five_token_rows"]))
    one("\\quad with a contract at both ends", intc(ev["rows_between_contracts"]))
    one("Distinct addresses other than the zero address", intc(ev["addresses"]))
    add("\\addlinespace")
    add(hdr(f"Account types (code read at block {intc(at['block'])})", 3))
    one("Addresses that sent a transaction (user accounts)", intc(ev["transaction_senders"]))
    one("Addresses read with \\texttt{eth\\_getCode}$^{a}$", intc(at["addresses"]))
    one("\\quad no code (user account)", intc(at["after_extension"]["eoa"]))
    one("\\quad EIP-7702 delegation designator (user account)", intc(at["after_extension"]["eoa_7702"]))
    one("\\quad Safe (smart account, user account)", intc(at["wallet_kind_typed"]["safe"]))
    one("\\quad ERC-4337 account by the rule of the reads (smart account, user account)", intc(at["wallet_kind_typed"]["erc4337"]))
    one("\\quad ERC-4337 account by the listed code families (smart account, user account)",
        f"{intc(at['extension']['moved'])} ({intc(at['extension']['by_code_hash'])} by code hash, "
        f"{intc(at['extension']['by_implementation'])} by code hash and implementation)")
    one("\\quad any other code (contract)", intc(at["after_extension"]["contract"]))
    one("Typed user accounts / contracts, with the transaction senders", f"{intc(ev['user_accounts'])} / {intc(ev['contracts'])}")
    one("Audited transaction senders with code / addresses with a call aborted at every attempt",
        f"{at['audit_senders_with_code']} of 1{{,}}000 / {at['aborted_addresses']}")
    add("\\addlinespace")
    add(hdr("Balances and the balance cap", 3))
    one(f"Sampled (token, owner) pairs whose balance equals \\texttt{{balanceOf}} at the {TOBS} block",
        f"{intc(bc['matched'])} of {intc(bc['rows'])} ({pct(bc['share'])}; threshold {pct(bc['threshold'], 0)})")
    both("Positive latest allowances between contracts", lambda t: intc(al[t]["total"]["n_latest_positive"]))
    both("\\quad unlimited", lambda t: f"{intc(al[t]['total']['n_unlimited'])} ({pct(al[t]['total']['share_unlimited'])})")
    both("\\quad capped to zero (the owner holds no balance)",
         lambda t: f"{intc(al[t]['total']['n_capped_to_zero'])} ({pct(al[t]['total']['share_capped_to_zero'])})")
    both("\\quad capped below the allowance", lambda t: intc(al[t]["total"]["n_capped_below_allowance"]))
    both("\\quad positive after the cap", lambda t: intc(al[t]["total"]["n_positive_eff"]))
    both("\\quad sum of the capped values (USD)", lambda t: intc(round(al[t]["total"]["sum_usd_eff"])))
    add("\\addlinespace")
    add(hdr(f"Contract graph ({intc(de['nodes']['contracts'])} contracts numbered over both freezes)", 3))
    both("Allowance layer: pairs (owner contracts / spender contracts)",
         lambda t: f"{intc(pr[t]['allowance_capped']['pairs'])} ({intc(pr[t]['allowance_capped']['sources'])} / "
                   f"{intc(pr[t]['allowance_capped']['destinations'])})")
    both("\\quad pairs of the largest owner contract / of the largest spender contract",
         lambda t: f"{intc(pr[t]['allowance_capped']['largest_source_pairs'])} / "
                   f"{intc(pr[t]['allowance_capped']['largest_destination_pairs'])}")
    both("\\quad pairs without the balance cap", lambda t: intc(pr[t]["allowance_uncapped"]["pairs"]))
    both("Transfer layer: pairs (sender contracts / recipient contracts)",
         lambda t: f"{intc(pr[t]['transfer']['pairs'])} ({intc(pr[t]['transfer']['sources'])} / "
                   f"{intc(pr[t]['transfer']['destinations'])})")
    both("\\quad pairs of the largest sender contract / of the largest recipient contract",
         lambda t: f"{intc(pr[t]['transfer']['largest_source_pairs'])} / {intc(pr[t]['transfer']['largest_destination_pairs'])}")
    both("Union graph: contracts with a pair / pairs", lambda t: f"{intc(g[t]['nodes'])} / {intc(g[t]['edges'])}")
    both("\\quad giant SCC / IN / OUT / other", lambda t: " / ".join(intc(g[t][k]) for k in ("scc", "in", "out", "other")))
    add("\\addlinespace")
    add(hdr("Universes, importance and hot sets of the discovery-order test", 3))
    both("Universe of the \\texttt{both} mode (WCC of the giant SCC): contracts / union pairs",
         lambda t: f"{intc(g[t]['WCC'])} / {intc(g[t]['E_WCC'])}")
    both("\\quad capped allowance pairs / transfer pairs inside it",
         lambda t: f"{intc(run[(t, 'both')]['sizes']['universe']['allow_pairs'])} / "
                   f"{intc(run[(t, 'both')]['sizes']['universe']['transfer_pairs'])}")
    both("Universe of the \\texttt{out} mode (giant SCC and OUT): contracts / union pairs",
         lambda t: f"{intc(g[t]['U'])} / {intc(g[t]['E_U'])}")
    both("Typed contracts with a positive importance / with a positive $I_A$",
         lambda t: f"{intc(imp[t]['contracts'])} / {intc(imp[t]['with_i_a'])}")
    both("Sum of $I_T$ / of $I_A$ over the typed contracts (USD)",
         lambda t: f"{intc(round(imp[t]['i_t_usd']))} / {intc(round(imp[t]['i_a_usd']))}")
    both("\\quad share held by the WCC: $I_T$ / $I_A$",
         lambda t: f"{pct(cov[(t, 'both')]['i_t']['share_U'])} / {pct(cov[(t, 'both')]['i_a']['share_U'])}")
    both("\\quad share held by the giant SCC and OUT: $I_T$ / $I_A$",
         lambda t: f"{pct(cov[(t, 'out')]['i_t']['share_U'])} / {pct(cov[(t, 'out')]['i_a']['share_U'])}")
    both("Hot contracts $|H_q(I_T)|$ / $|H_q(I_A)|$, \\texttt{both} mode",
         lambda t: f"{intc(run[(t, 'both')]['hot_sets']['i_t@q'])} / {intc(run[(t, 'both')]['hot_sets']['i_a@q'])}")
    both("Hot contracts $|H_q(I_T)|$ / $|H_q(I_A)|$, \\texttt{out} mode",
         lambda t: f"{intc(run[(t, 'out')]['hot_sets']['i_t@q'])} / {intc(run[(t, 'out')]['hot_sets']['i_a@q'])}")
    one("Structure pilot at $t_1$: share of the giant SCC and OUT with a capped allowance in-edge",
        f"{pct(pilot['capped_allowance_in_edge_share']['U'], 2)} (stop threshold of the protocol "
        f"{pct(pilot['discovery_config']['stop_min_allow_share'], 0)})")
    add("\\addlinespace")
    add(hdr("Cohorts (contracts) and where they lie in the contract graph of their freeze", 3))
    c_t, c_0 = sw["cohort_coverage"]["cohort_tobs"], w0["cohort_coverage"]["cohort_t1"]
    s_1, s_0 = w1["cohort_coverage"]["spenders_w1"], w0["cohort_coverage"]["spenders_w0"]
    add(f"Cohort of the freeze ($\\geq 3$ owners on the five tokens in the score window) & {intc(coh['cohort'])} of "
        f"{intc(coh['listed'])} listed ({intc(coh['by_class']['user_account'])} smart accounts are user accounts) & "
        f"{intc(coh0['cohort'])} of {intc(coh0['listed'])} listed ({intc(coh0['by_class']['user_account'])} smart accounts); "
        f"{intc(coh0['in_tobs_cohort'])} also in the matched cohort \\\\")
    add(f"\\quad in the allowance layer / transfer layer / union graph & {n_pct(c_t['allowance_layer'])} / "
        f"{n_pct(c_t['transfer_layer'])} / {n_pct(c_t['union_graph'])} & {n_pct(c_0['allowance_layer'])} / "
        f"{n_pct(c_0['transfer_layer'])} / {n_pct(c_0['union_graph'])} \\\\")
    add(f"Spender cohort & {intc(sp1['cohort'])} of {intc(sp1['listed'])} listed "
        f"({intc(sp1['by_class']['user_account'])} user accounts, {sp1['by_class']['system']} system address); W1 & "
        f"{intc(sp0['cohort'])} of {intc(sp0['listed'])} listed ({intc(sp0['by_class']['user_account'])} user accounts, "
        f"{sp0['by_class']['system']} system address); W0 \\\\")
    add(f"\\quad in the allowance layer / transfer layer / union graph & {n_pct(s_1['allowance_layer'])} / "
        f"{n_pct(s_1['transfer_layer'])} / {n_pct(s_1['union_graph'])} & {n_pct(s_0['allowance_layer'])} / "
        f"{n_pct(s_0['transfer_layer'])} / {n_pct(s_0['union_graph'])} \\\\")
    add(f"\\quad outside the contract graph (score zero) & {n_pct(s_1['outside_contract_graph'])} & "
        f"{n_pct(s_0['outside_contract_graph'])} \\\\")
    add("\\addlinespace")
    add(hdr("Labels of the spender cohorts (they count every account, user accounts included)", 3))
    for key, name in ((A, "New approval pairs"), (T, "New transfer senders"),
                      ("future_revoke_count", "Revocations"), ("future_drain_owners", "Drained owners (heuristic)")):
        v1, v0 = w1["label_split"]["labels"][key], w0["label_split"]["labels"][key]
        add(f"{name}: total (share from user accounts); spenders with the label & "
            f"{intc(v1['total'])} ({pct(v1['share_user_accounts'])}); {intc(v1['spenders_with_label'])} & "
            f"{intc(v0['total'])} ({pct(v0['share_user_accounts'])}); {intc(v0['spenders_with_label'])} \\\\")
    add("\\addlinespace")
    add(hdr("Constants (USD, from the W0 score window of the contract graph, two significant digits)", 3))
    one("Median transfer $m_T$ / median positive capped allowance $m_A$",
        f"{co['m_transfer_usd']:.0f} / {co['m_allowance_usd']:.3f}")
    one("Cap $U$ of the amount-weighted allowance layer / cap $U_{\\mathrm{user}}$ per user account in the importance",
        f"{intc(co['cap_allowance_usd'])} / {intc(co['cap_user_usd'])}")
    return "\n".join(L) + "\n"


def s1_rows_b() -> str:
    """Panel B: AUC of every ordering in the four runs."""
    cols = [(t, m, h) for t, m in S.RUNS for h in ("i_t@q", "i_a@q")]
    L = []
    for item in ORDERINGS:
        if item is None:
            L.append("\\addlinespace")
            continue
        key, name = item
        L.append(f"{name} & " + " & ".join(num(S.auc(S.discovery(t, m), h, key)["auc"], nd=4) for t, m, h in cols) + " \\\\")
    L.append("\\midrule")
    L.append("$\\delta'$ (diagnostic, outside every comparison) & "
             + " & ".join(num(S.auc(S.discovery(t, m), h, "delta")["auc"], nd=4) for t, m, h in cols) + " \\\\")
    L.append("\\midrule")
    for key, name in (("ref_cpr", "Reference: order by C-PR of the full graph"),
                      ("ref_ib_u", "Reference: order by union in-degree of the full graph"),
                      ("ref_ideal", "Reference: ideal order")):
        L.append(f"{name} & " + " & ".join(num(S.auc(S.discovery(t, m), h, key)["auc"], nd=4) for t, m, h in cols) + " \\\\")
    L.append("Reference: random curve & "
             + " & ".join(num(S.auc(S.discovery(t, m), h, "random_curve"), nd=4) for t, m, h in cols) + " \\\\")
    L.append("\\midrule")
    L.append("Contracts of the universe & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{{intc(S.discovery(t, m)['sizes']['universe']['U'])}}}" for t, m in S.RUNS) + " \\\\")
    L.append("Hot contracts & " + " & ".join(intc(S.discovery(t, m)["hot_sets"][h]) for t, m, h in cols) + " \\\\")
    return "\n".join(L) + "\n"


def s1_rows_c() -> str:
    """Panel C: items 1 and 2 of the protocol's list in the three runs outside the decision."""
    runs = S.RUNS[1:]
    L = []
    for block, title in (("1_walk_vs_count", "1. Each walk$'$ against the count it smooths"),
                         ("2_walk_contrasts", "2. Among the walks")):
        L.append(hdr(title, 7))
        by: dict[tuple[str, str], dict] = {}
        for t, m in runs:
            for x in S.discovery(t, m)["fixed_order"][block]:
                by.setdefault((x["a"], x["b"]), {})[(t, m, x["hot_set"])] = x
        for (a, b), cells in by.items():
            L.append(f"{SHORT[a]} $-$ {SHORT[b]} & "
                     + " & ".join(d4(cells[(t, m, h)]) for t, m in runs for h in ("i_t@q", "i_a@q")) + " \\\\")
        L.append("\\addlinespace")
    L.append(hdr("4. Replication contrast: C-PR$'$ $-$ $\\mathrm{IB}'_U$ on the hot set of the union in-degree", 7))
    L.append("C-PR$'$ $-$ $\\mathrm{IB}'_U$ on $H_q(\\mathrm{IB}_U)$ & " + " & ".join(
        f"\\multicolumn{{2}}{{c}}{{{d4(S.discovery(t, m)['fixed_order']['4_cho']['replication_contrast'])}}}"
        for t, m in runs) + " \\\\")
    return "\n".join(L) + "\n"


def s1_rows_d() -> str:
    """Panel D: descriptive readings of the deciding run, by ordering."""
    d, o = S.discovery("tobs", "both"), S.discovery("tobs", "out")
    dg, og = d["diagnostics"], o["diagnostics"]
    rho = d["protocol"]["rho"]
    L = []
    for item in (*ORDERINGS, None, ("delta", "$\\delta'$ (diagnostic)")):
        if item is None:
            L.append("\\addlinespace")
            continue
        key, name = item
        r = d["runs"][f"{key}@{rho}"]
        cells = [
            *(pct(S.curve_at(d, "P_ST", imp, key, 0.10)) for imp in ("i_t", "i_a")),
            *(pct(S.curve_at(d, "captured", imp, key, 0.01)) for imp in ("i_t", "i_a")),
            *(pct(S.curve_at(d, "captured", imp, key, 0.10)) for imp in ("i_t", "i_a")),
            num(dg["ties"][key]), num(og["ties"][key]),
            num(dg["wasted_visits"][key]["first_1pct"]), num(dg["wasted_visits"][key]["first_10pct"]),
            intc(round(r["solves"])) if r["solves"] else "0", intc(round(r["iterations"])) if r["iterations"] else "0",
        ]
        L.append(f"{name} & " + " & ".join(cells) + " \\\\")
    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- write
def replace_block(text: str, tag: str, content: str) -> str:
    pat = re.compile(rf"(% BEGIN GENERATED {tag} \(make_tables\.py; do not edit by hand\)\n).*?(% END GENERATED {tag}\n)", re.S)
    if not pat.search(text):
        sys.exit(f"markers for {tag} not found in main.tex")
    return pat.sub(lambda m: m.group(1) + content + "\n" + m.group(2), text)


def check_statement(text: str) -> None:
    """The verdict sentence must be quoted word for word in the prose of main.tex (outside the tables)."""
    prose = re.sub(r"% BEGIN GENERATED.*?% END GENERATED \w+\n", " ", text, flags=re.S)
    flat = re.sub(r"\s+", " ", prose)
    first, second = statement().split(". ", 1)
    for part in (first + ".", second):
        if part not in flat:
            sys.exit("main.tex does not quote the verdict sentence of the deciding run word for word:\n  " + part)


def main() -> None:
    S.parse_args(__doc__.splitlines()[0])
    text = MAIN.read_text(encoding="utf-8")
    for tag, fn in (("tab1", table1), ("tab2", table2), ("tab3", table3), ("tab4", table4),
                    ("tab5", table5), ("tab6", table6), ("tab7", table7)):
        text = replace_block(text, tag, fn())
    MAIN.write_text(text, encoding="utf-8")
    stamp = "% Generated by make_tables.py from the published summaries; do not edit by hand.\n"
    for name, fn in (("S1_Table_rows.tex", s1_rows_a), ("S1_Table_rows_b.tex", s1_rows_b),
                     ("S1_Table_rows_c.tex", s1_rows_c), ("S1_Table_rows_d.tex", s1_rows_d)):
        (SUPP / name).write_text(stamp + fn(), encoding="utf-8")
    check_statement(text)
    print("wrote tables 1-7 into", MAIN.name, "and the rows of S1 Table (supporting/S1_Table_rows*.tex);",
          "the verdict sentence is quoted word for word")


if __name__ == "__main__":
    main()
