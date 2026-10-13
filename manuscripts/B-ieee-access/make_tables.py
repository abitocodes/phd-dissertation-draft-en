#!/usr/bin/env python3
"""Tables of Manuscript B (IEEE Access), written from the published results of phd_works.

    python make_tables.py --phd-works /path/to/phd_works      # or set PHD_WORKS

Writes tab_timeline.tex, tab_ids.tex, tab_holdout.tex, tab_contrasts.tex, tab_bench.tex and
tab_explore.tex next to this file. Every number comes from one of these sources, named again
in a comment at the top of each table:

- the published evaluation summaries, Sybil model and benchmark of both analyses
  (experiments/data/3-published-results-for-thesis/ for the registered analysis and its
  subfolder revised-usd/ for the revised analysis), each checked against SHA256SUMS.txt;
- the extraction manifest of W1 and the job times in describe/describe.json;
- the commit history of phd_works (git log), and SHA-256 of the registration files as git
  stores them (LF line ends) and as the manifest recorded them (CRLF line ends);
- supplement/exploratory_checks.json (Appendix A of the paper).

Nothing is typed in by hand except the wording of the rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECTS = ("ERC20-Allowance-PageRank-Wallet-Reputation", "ERC20-Allowance-PageRank-Contract-Reputation")
APPR, SEND, LIQ = "future_new_approvers", "future_new_transfer_senders", "liquidation_free_rate"
DELTA = 0.01
COMMITS = {
    "plan": "43d8045",
    "registration": "0d3a057",
    "registered_results": "8d8b568",
    "registered_benchmark": "f33a87a",
    "revision_doc": "a897475",
    "revision_tokens": "09dfc32",
    "revision_cap": "2705b28",
    "revised_results": "77e71f5",
}


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def locate(phd: Path) -> tuple[Path, str]:
    for p in PROJECTS:
        exp = phd / "1-Dissertation-Works" / p / "experiments"
        if (exp / "data" / "3-published-results-for-thesis" / "results_digest.md").exists():
            return exp, p
    raise SystemExit(f"no published results under {phd}")


def sha_crlf(path: Path) -> str:
    """SHA-256 of a file as the authors' Windows checkout held it (CRLF), as SHA256SUMS.txt records it."""
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return hashlib.sha256(data).hexdigest()


def check_sums(pub: Path, files: list[str]) -> None:
    sums = {}
    for line in (pub / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        h, f = line.split(maxsplit=1)
        sums[f.strip()] = h
    for f in files:
        if sums.get(f) != sha_crlf(pub / f):
            raise SystemExit(f"{pub / f} does not match SHA256SUMS.txt")


def git(phd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(phd), *args], capture_output=True, text=True, check=True).stdout


def commit_info(phd: Path, short: str) -> tuple[str, datetime]:
    out = git(phd, "show", "-s", "--format=%H %cI", short).split()
    return out[0], datetime.fromisoformat(out[1]).astimezone(timezone.utc)


def blob_sha(phd: Path, commit: str, project_dirs: list[str], rel: str) -> tuple[str, str]:
    """SHA-256 of a file in a commit, with LF line ends (as stored) and with CRLF line ends."""
    for d in project_dirs:
        try:
            data = subprocess.run(["git", "-C", str(phd), "show", f"{commit}:{d}/{rel}"], capture_output=True,
                                  check=True).stdout
        except subprocess.CalledProcessError:
            continue
        crlf = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        return hashlib.sha256(data).hexdigest(), hashlib.sha256(crlf).hexdigest()
    raise SystemExit(f"{rel} not found in {commit}")


def load(phd: Path) -> dict:
    exp, _ = locate(phd)
    base = exp / "data" / "3-published-results-for-thesis"
    pubs = {"registered": base, "revised": base / "revised-usd"}
    D: dict = {}
    for name, pub in pubs.items():
        w1 = "registered-w1" if name == "registered" else "window-w1"
        files = ["same-window/eval_summary.json", "holdout-w0/eval_summary.json", f"{w1}/eval_summary.json",
                 "sybil-model/sybil_model.json", "benchmark/benchmark.json", "describe/describe.json",
                 "registered-w1/extraction_manifest.json"]
        check_sums(pub, files)
        D[name] = {k: json.loads((pub / f).read_text(encoding="utf-8"))
                   for k, f in zip(("same", "w0", "w1", "sybil", "bench", "describe", "manifest"), files)}
    D["explore"] = json.loads((HERE / "supplement" / "exploratory_checks.json").read_text(encoding="utf-8"))
    return D


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def f3(x: float) -> str:
    s = f"{x:.3f}"
    if s in ("-0.000", "0.000"):
        s = "0.000"
    return s.replace("-", "$-$")


def sgn(x: float) -> str:
    s = f"{x:+.3f}"
    if s in ("-0.000", "+0.000"):
        s = "+0.000"
    return s.replace("-", "$-$")


def ci(e: dict, lo: str = "ci_low", hi: str = "ci_high") -> str:
    return f"[{f3(e[lo])}, {f3(e[hi])}]"


def tau_cell(e: dict) -> str:
    return f"{f3(e['kendall_tau'])} {ci(e)}"


def delta_cell(e: dict) -> str:
    return f"{sgn(e['delta_tau'])} {ci(e)}"


def n(x: int) -> str:
    return f"{x:,}".replace(",", "{,}")


def utc(t: datetime) -> str:
    return t.strftime("%H:%M:%S")


def header(sources: list[str]) -> str:
    return "% Generated by make_tables.py -- do not edit by hand.\n" + "".join(f"% Source: {s}\n" for s in sources)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def tab_holdout(D: dict) -> str:
    rows = [
        ("In-approve degree at the freeze", "t1_in_approve_degree", "in_approve_degree"),
        ("Transfer in-degree at the freeze", "t1_in_degree", "in_degree"),
        ("EndorseRank", "endorserank", "endorserank"),
        ("AWP", "awp", "awp"),
        ("C-PR ($\\lambda=1$), authorization walk", "cpr_l100", "cpr_l100"),
        ("C-PR ($\\lambda=0.75$)", "cpr_l75", "cpr_l75"),
        ("C-PR ($\\lambda=0.5$), primary", "cpr_l50", "cpr_l50"),
        ("C-PR ($\\lambda=0.25$)", "cpr_l25", "cpr_l25"),
        ("C-PR ($\\lambda=0$), payment walk", "cpr_l0", "cpr_l0"),
        ("S-PR", "spr", "spr"),
    ]
    out = [header(["holdout-w0/eval_summary.json : taus (both analyses)",
                   "registered-w1/eval_summary.json and revised-usd/window-w1/eval_summary.json : spender_taus, trader_taus"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Kendall $\\tau_b$ Between Scores at the Freeze and Later Labels, With 95\\% Paired-Bootstrap Intervals}",
           "\\label{tab:holdout}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{2.4pt}",
           "\\begin{tabular}{@{}lccccc@{}}",
           "\\toprule"]
    for k, (name, title) in enumerate((("revised", "Revised analysis, the main analysis: a re-analysis under the pre-specified rules (US dollars, five tokens)"),
                                       ("registered", "Registered analysis, the pre-specified test (raw base units, every ERC-20 token)"))):
        w0, w1 = D[name]["w0"], D[name]["w1"]
        if k:
            out.append("\\midrule")
        out.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\")
        out.append(" & \\multicolumn{2}{c}{W0 spenders ($n=" + n(w0["spenders"]) + "$)} & \\multicolumn{2}{c}{W1 spenders ($n="
                   + n(w1["spenders"]) + "$)} & W1 traders ($n=" + n(w1["traders"]) + "$) \\\\")
        out.append("\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(l){6-6}")
        out.append("Score & New approval pairs & New transfer senders & New approval pairs & New transfer senders & Liquidation-free close rate \\\\")
        out.append("\\midrule")
        for label, k0, k1 in rows:
            cells = [tau_cell(w0["taus"][k0][APPR]), tau_cell(w0["taus"][k0][SEND]),
                     tau_cell(w1["spender_taus"][k1][APPR]), tau_cell(w1["spender_taus"][k1][SEND]),
                     tau_cell(w1["trader_taus"][k1])]
            out.append(f"{label} & " + " & ".join(cells) + " \\\\")
    rg, rv = D["registered"], D["revised"]
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize W0: scores frozen on 31 March 2026, labels counted from April to June 2026. "
            "W1: scores frozen on 30 June 2026, labels counted from July to September 2026. Spenders are the contracts that hold a "
            "positive latest allowance at the freeze; traders are the GMX~V2 accounts that hold contract code, are nodes of the "
            "freeze-date graph and close at least three positions in the label window. "
            f"In the revised analysis {n(rv['w0']['gained_new_approvals'])} W0 spenders gained a new approval pair and "
            f"{n(rv['w0']['gained_new_senders'])} a new transfer sender, and {n(rv['w1']['gained_new_approvals'])} and "
            f"{n(rv['w1']['gained_new_senders'])} W1 spenders did; in the registered analysis {n(rg['w0']['gained_new_approvals'])}, "
            f"{n(rg['w0']['gained_new_senders'])}, {n(rg['w1']['gained_new_approvals'])} and {n(rg['w1']['gained_new_senders'])}. "
            f"Of the {rv['w1']['traders']} W1 traders, {rv['w1']['traders_liquidated']} had at least one liquidation. "
            "The degree, EndorseRank and AWP rows are reference scores; the companion study \\cite{kwon2026companion} reports their "
            "comparisons in full. Intervals: 400 paired resamples over the contracts of the cohort, seed 42.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def verdict_word(e: dict) -> str:
    return "holds" if e["holds"] else "fails"


def tab_contrasts(D: dict) -> str:
    R, V = D["registered"], D["revised"]

    def get(an: dict, path: tuple) -> dict:
        x = an
        for p in path:
            x = x[p]
        return x

    def after(an: dict, a: str, b: str, outcome: str) -> dict:
        return next(c for c in an["w0"]["contrasts_after"] if c["a"] == a and c["b"] == b and c["outcome"] == outcome)

    def ruled(label: str, path: tuple, test: str) -> str:
        r, v = get(R, path), get(V, path)
        return f"{label} & {test} & {delta_cell(v)} & {verdict_word(v)} & {delta_cell(r)} & {verdict_word(r)} \\\\"

    def a_row(label: str, idx: int, test: str, key: str) -> str:
        r, v = R["w0"]["contrasts_prefixed"][idx], V["w0"]["contrasts_prefixed"][idx]
        rr, vv = R["w0"]["rule_a_primary"][key], V["w0"]["rule_a_primary"][key]
        return (f"{label} & {test} & {delta_cell(v)} & {'holds' if vv else 'fails'} & {delta_cell(r)} & "
                f"{'holds' if rr else 'fails'} \\\\")

    def plain(label: str, r: dict, v: dict) -> str:
        return f"{label} & --- & {delta_cell(v)} & & {delta_cell(r)} & \\\\"

    def met(x: bool) -> str:
        return "met" if x else "\\textbf{not met}"

    def group(title: str) -> list[str]:
        return ["\\midrule", f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"]

    out = [header(["holdout-w0/eval_summary.json : contrasts_prefixed, rule_a_primary, contrasts_after (both analyses)",
                   "same-window/eval_summary.json : rule_a_secondary (both analyses)",
                   "registered-w1/eval_summary.json and revised-usd/window-w1/eval_summary.json : rule_b, "
                   "sensitivity_awp, sensitivity_isolated, endorserank_results"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Paired Contrasts in Both Analyses: The Pre-Specified Rules, the Registered Reports and Sensitivity Analyses, "
           "and Contrasts Computed After the Labels Were Known}",
           "\\label{tab:contrasts}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{2.6pt}",
           "\\begin{tabular}{@{}llcccc@{}}",
           "\\toprule",
           " & & \\multicolumn{2}{c}{Revised analysis (re-analysis)} & \\multicolumn{2}{c}{Registered analysis (the test)} \\\\",
           "\\cmidrule(lr){3-4}\\cmidrule(l){5-6}",
           "Contrast ($a$ minus $b$) and label & Test & $\\Delta\\tau$ [95\\% CI] & Verdict & $\\Delta\\tau$ [95\\% CI] & Verdict \\\\"]
    out += group("Rule A, fixed in the plan (43d8045) before any log of this study was extracted; W0 spenders")
    out.append(a_row("A1: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", 0, "no worse", "no_worse_on_new_approvals"))
    out.append(a_row("A2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", 1, "superiority", "better_on_new_senders"))
    out.append(f"Rule A, primary part (A1 and A2) & & & {met(V['w0']['rule_a_primary']['pass'])} & & {met(R['w0']['rule_a_primary']['pass'])} \\\\")
    out.append(f"Rule A, secondary part (same window) & & & {met(V['same']['rule_a_secondary']['pass'])} & & "
               f"{met(R['same']['rule_a_secondary']['pass'])} \\\\")
    out += group("Rule B, registered (0d3a057) before this study extracted the W1 logs; F1, F2 and F3 all required; margin $\\delta=0.01$")
    out.append(ruled("F1: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs", ("w1", "rule_b", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "rule_b", "F2"), "non-inferiority"))
    out.append(ruled("F3: C-PR $-$ C-PR ($\\lambda=0$), liquidation-free rate", ("w1", "rule_b", "F3"), "non-inferiority"))
    out.append(f"Rule B (F1, F2 and F3) & & & {met(V['w1']['rule_b']['decision'])} & & {met(R['w1']['rule_b']['decision'])} \\\\")
    out += group("Registered to be reported in a fixed order beside the decision (nominal)")
    out.append(ruled("F4: as F3", ("w1", "rule_b", "F4"), "superiority"))
    out.append(ruled("F5: C-PR $-$ C-PR ($\\lambda=1$), liquidation-free rate", ("w1", "rule_b", "F5"), "superiority"))
    out.append(ruled("F6a: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", ("w1", "rule_b", "F6a"), "no worse"))
    out.append(ruled("F6b: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "rule_b", "F6b"), "superiority"))
    out += group("Registered sensitivity analysis S1: AWP as the comparator (nominal)")
    out.append(ruled("F1: C-PR $-$ AWP, new approval pairs", ("w1", "sensitivity_awp", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ AWP, new transfer senders", ("w1", "sensitivity_awp", "F2"), "non-inferiority"))
    out.append(ruled("F3: C-PR $-$ AWP, liquidation-free rate", ("w1", "sensitivity_awp", "F3"), "non-inferiority"))
    out += group("Registered sensitivity analysis S2: contracts outside a graph kept as isolated nodes (nominal)")
    out.append(ruled("F1: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs", ("w1", "sensitivity_isolated", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "sensitivity_isolated", "F2"), "non-inferiority"))
    out.append(ruled("F3: C-PR $-$ C-PR ($\\lambda=0$), liquidation-free rate", ("w1", "sensitivity_isolated", "F3"), "non-inferiority"))
    out.append(ruled("F5: C-PR $-$ C-PR ($\\lambda=1$), liquidation-free rate", ("w1", "sensitivity_isolated", "F5"), "superiority"))
    out.append(f"S1, decision (F1, F2 and F3) & & & {met(V['w1']['sensitivity_awp']['decision'])} & & "
               f"{met(R['w1']['sensitivity_awp']['decision'])} \\\\")
    out.append(f"S2, decision (F1, F2 and F3) & & & {met(V['w1']['sensitivity_isolated']['decision'])} & & "
               f"{met(R['w1']['sensitivity_isolated']['decision'])} \\\\")
    out += group("Computed after the labels of the window were known; no rule")
    out.append(plain("W0: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs",
                     after(R, "cpr_l50", "cpr_l0", APPR), after(V, "cpr_l50", "cpr_l0", APPR)))
    out.append(plain("W0: S-PR $-$ C-PR ($\\lambda=1$), new approval pairs",
                     after(R, "spr", "cpr_l100", APPR), after(V, "spr", "cpr_l100", APPR)))
    out.append(plain("W0: S-PR $-$ C-PR ($\\lambda=0$), new transfer senders",
                     after(R, "spr", "cpr_l0", SEND), after(V, "spr", "cpr_l0", SEND)))
    out.append(plain("W0: C-PR $-$ AWP, new transfer senders",
                     after(R, "cpr_l50", "awp", SEND), after(V, "cpr_l50", "awp", SEND)))
    out.append(plain("W0: C-PR ($\\lambda=1$) $-$ in-approve degree, new approval pairs",
                     after(R, "cpr_l100", "t1_in_approve_degree", APPR), after(V, "cpr_l100", "t1_in_approve_degree", APPR)))
    out.append(plain("W0: EndorseRank $-$ in-approve degree, new approval pairs",
                     after(R, "endorserank", "t1_in_approve_degree", APPR), after(V, "endorserank", "t1_in_approve_degree", APPR)))
    out.append(plain("W0: AWP $-$ transfer in-degree, new transfer senders",
                     after(R, "awp", "t1_in_degree", SEND), after(V, "awp", "t1_in_degree", SEND)))
    er_r, er_v = R["w1"]["endorserank_results"], V["w1"]["endorserank_results"]
    out.append(plain("W1: EndorseRank $-$ in-approve degree, new approval pairs",
                     er_r["endorserank_minus_degree_appr"], er_v["endorserank_minus_degree_appr"]))
    out.append(plain("W1: AWP $-$ transfer in-degree, new transfer senders",
                     er_r["awp_minus_degree_send"], er_v["awp_minus_degree_send"]))
    out.append(plain("W1: C-PR $-$ EndorseRank, new approval pairs",
                     er_r["cpr_minus_endorserank_appr"], er_v["cpr_minus_endorserank_appr"]))
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize $\\Delta\\tau=\\tau_a-\\tau_b$ on the same resamples. C-PR without a $\\lambda$ is the primary setting $\\lambda=0.5$; liquidation-free rate: the liquidation-free close rate of the W1 traders. Superiority holds "
            "when the interval lies above zero, non-inferiority when its lower end lies above $-\\delta=-0.01$, and ``no worse'' when "
            "the interval contains zero or lies above it. The revised column, the main analysis, applies the rules and thresholds of the "
            "plan and the registration to scores defined after the registered results were known, so none of its verdicts is a "
            "registered result; the registered column is the test that the plan and the registration fixed. Nominal verdicts use unadjusted 95\\% intervals; the fixed order was an "
            "order of reporting, not a gatekeeping sequence. The degree, EndorseRank and AWP rows are reference contrasts reported in "
            "full in \\cite{kwon2026companion}. Intervals: 400 paired resamples, seed 42.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def tab_bench(D: dict) -> str:
    rows = [("EndorseRank", "endorserank"), ("AWP", "awp"), ("C-PR ($\\lambda=0.5$)", "cpr_l50"), ("S-PR", "spr")]
    out = [header(["benchmark/benchmark.json : main (registered analysis and revised-usd/)"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{Solver Time on the Full Graphs at the End of the Observation Window (Mean and SD of Five Timed Runs After One Warm-Up)}",
           "\\label{tab:bench}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3pt}",
           "\\begin{tabular}{@{}lrrrr@{}}",
           "\\toprule",
           "Score & $|V|$ & $|E|$ & Iter. & Time (s) \\\\"]
    for name, title in (("revised", "Revised analysis"), ("registered", "Registered analysis")):
        out += ["\\midrule", f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"]
        B = D[name]["bench"]["main"]
        for label, k in rows:
            e = B[k]
            out.append(f"{label} & {n(e['nodes'])} & {n(e['edges'])} & {e['iterations']} & "
                       f"{e['mean_s']:.2f} ({e['sd_s']:.2f}) \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\columnwidth}{\\footnotesize One session of one warm-up and five timed runs per graph and setting, the "
            "measurement cited throughout; the time covers matrix assembly and power "
            "iteration ($d=0.85$, tolerance $10^{-8}$, at most 300 iterations) on edge lists built in advance. S-PR includes the solve "
            "of the authorization layer that supplies its restart vector. $|V|$ and $|E|$ are those of each solver graph, which drops "
            "pairs whose weight is zero in floating point; in the revised analysis this removes dust pairs from the graphs of "
            "EndorseRank and AWP (Section~\\ref{sec:graphs}). Same machine for both analyses (Section~\\ref{sec:cost}).}",
            "\\end{table}", ""]
    return "\n".join(out)


def tab_ids(phd: Path, D: dict, project_dirs: list[str]) -> str:
    man = D["registered"]["manifest"]
    rows = [
        ("Plan and configuration (rule A)", "plan"),
        ("Registration of W1 (rule B, R1--R3)", "registration"),
        ("Registered results committed", "registered_results"),
        ("Registered benchmark and data description", "registered_benchmark"),
        ("Revision document", "revision_doc"),
        ("Revision: five tokens and prices", "revision_tokens"),
        ("Revision: cap amended, constants", "revision_cap"),
        ("Revised results committed", "revised_results"),
    ]
    out = [header(["git log of phd_works (commit identifiers and committer times, converted to UTC)",
                   "registered-w1/extraction_manifest.json : sha256 (CRLF checkout)",
                   "git show <commit>:<experiments>/docs/registration_w1.md and config/contract_reputation.yaml (LF, as stored)"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{Commit Identifiers and SHA-256 Hashes of the Pre-Specification Record (Times in UTC)}",
           "\\label{tab:ids}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{0pt}",
           "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{\\columnwidth}@{}}",
           "\\toprule"]
    for label, key in rows:
        full, t = commit_info(phd, COMMITS[key])
        out.append(f"{label}, {t.day} {t.strftime('%b')} {utc(t)}\\\\")
        out.append(f"\\quad\\sha{{{full}}}\\\\")
    out.append("\\midrule")
    files = [("docs/registration_w1.md", "registration document"), ("config/contract_reputation.yaml", "configuration")]
    for rel, label in files:
        lf, crlf = blob_sha(phd, COMMITS["registration"], project_dirs, rel)
        recorded = man["sha256"][rel]
        if recorded != crlf:
            raise SystemExit(f"manifest hash of {rel} is not the CRLF hash of the committed file")
        out.append(f"SHA-256 of the {label}, CRLF line ends (recorded in the manifest)\\\\")
        out.append(f"\\quad\\sha{{{recorded[:32]}}}\\\\")
        out.append(f"\\quad\\sha{{{recorded[32:]}}}\\\\")
        out.append(f"SHA-256 of the {label}, LF line ends (as git stores it)\\\\")
        out.append(f"\\quad\\sha{{{lf[:32]}}}\\\\")
        out.append(f"\\quad\\sha{{{lf[32:]}}}\\\\")
    lf, _ = blob_sha(phd, COMMITS["plan"], project_dirs, "docs/analysis_plan.md")
    out.append("SHA-256 of the plan in \\sha{43d8045}, LF line ends\\\\")
    out.append(f"\\quad\\sha{{{lf[:32]}}}\\\\")
    out.append(f"\\quad\\sha{{{lf[32:]}}}\\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\columnwidth}{\\footnotesize Each SHA-256 value is printed over two lines; join them without a space.}",
            "\\end{table}", ""]
    return "\n".join(out)


def tab_timeline(phd: Path, D: dict) -> str:
    desc, man = D["registered"]["describe"]["timing"], D["registered"]["manifest"]
    t = {k: commit_info(phd, v)[1] for k, v in COMMITS.items()}
    scan_a_c = datetime.fromisoformat(desc["scan_a"]["created"]).astimezone(timezone.utc)
    scan_a_e = datetime.fromisoformat(desc["scan_a"]["ended"]).astimezone(timezone.utc)
    scan_b_c = datetime.fromisoformat(desc["scan_b"]["created"]).astimezone(timezone.utc)
    scan_b_e = datetime.fromisoformat(desc["scan_b"]["ended"]).astimezone(timezone.utc)
    m_s = datetime.fromisoformat(man["started_at"]).astimezone(timezone.utc)
    m_f = datetime.fromisoformat(man["finished_at"]).astimezone(timezone.utc)
    if datetime.fromisoformat(desc["plan_commit_43d8045_utc"]) != t["plan"]:
        raise SystemExit("plan commit time differs between git and describe.json")
    if datetime.fromisoformat(desc["registration_commit_0d3a057_utc"]) != t["registration"]:
        raise SystemExit("registration commit time differs between git and describe.json")
    gap_a = int((scan_a_c - t["plan"]).total_seconds())
    gap_b = int((scan_b_c - t["registration"]).total_seconds())
    gap_m = int((m_s - t["registration"]).total_seconds())
    rg = D["registered"]
    rows = [
        (f"9 Oct, {utc(t['plan'])}", "Analysis plan and configuration committed: cohort rule, scores (C-PR at $\\lambda\\in\\{0.25,0.5,0.75\\}$ "
         "and its end points, S-PR), W0 labels, statistics and rule~A; amounts in raw base units, every ERC-20 token",
         "\\sha{43d8045}", "No log of this study extracted"),
        (f"9 Oct, {utc(scan_a_c)}--{utc(scan_a_e)}", f"Scan~A of the observation window; the BigQuery job was created {gap_a}~s after the plan commit",
         "Job metadata; cost ledger", "---"),
        ("9 Oct, before 16:49", f"Cohort of {n(rg['same']['cohort'])} contracts, ego extraction, same-window and W0 evaluation; "
         "rule~A judged", "Summaries committed in \\sha{0d3a057}", "Logs of the observation window"),
        (f"9 Oct, {utc(t['registration'])}", "Registration of W1: rule~B with $\\delta=0.01$, F4--F6, sensitivity analyses S1 and S2, "
         "the companion study's comparison on trader outcomes (its rules R1--R3 and their wording); configuration status set to registered",
         "\\sha{0d3a057}", "Every same-window and W0 result of the registered analysis; W0 profit labels of the traders (exploratory run)"),
        (f"9 Oct, {utc(m_s)}", f"Extraction script checks the committed registration and writes its manifest ({gap_m}~s after the commit): "
         "commit and both SHA-256 hashes", "Manifest", "---"),
        (f"9 Oct, {utc(scan_b_c)}--{utc(scan_b_e)}", f"Scan~B of July--September 2026; job created {gap_b}~s after the commit; manifest closed at {utc(m_f)}",
         "Job metadata; manifest", "No July--September log extracted for this study before this"),
        (f"9 Oct, {utc(t['registered_results'])}", "Registered W1 evaluation, then robustness and Sybil model, committed",
         "\\sha{8d8b568}", "W1 labels"),
        (f"{t['registered_benchmark'].day} {t['registered_benchmark'].strftime('%b')}, {utc(t['registered_benchmark'])}",
         "Registered benchmark and data description (BigQuery job times, amount shares) committed",
         "\\sha{f33a87a}", "W1 labels"),
        (f"10 Oct, {utc(t['revision_doc'])}", "Revision document: amounts in US dollars, token rule, slopes $b=\\ln 3/m$; a deviation from the plan and the registration",
         "\\sha{a897475}", "Every registered result"),
        (f"10 Oct, {utc(t['revision_tokens'])}", "Five tokens (WETH, USDC, USDT0, ARB, WBTC) and the price inputs", "\\sha{09dfc32}", "Every registered result"),
        (f"10 Oct, {utc(t['revision_cap'])}", "Cap $U=20{,}000$ dollars of the C-PR authorization layer; $m_T=200$, $m_A=62$ dollars",
         "\\sha{2705b28}", "Revised medians and percentiles; no revised score"),
        ("10 Oct, from 11:36", "Revised scores computed; rules A, B and R1--R3 applied unchanged", "Authors' account; no commit", "Every registered result"),
        (f"10 Oct, {utc(t['revised_results'])}", "Revised results committed", "\\sha{77e71f5}", "---"),
        ("11 Oct", "Exploratory checks of Appendix~\\ref{app:explore}", "This paper's supplement", "Every result above"),
    ]
    out = [header(["git log of phd_works (committer times converted to UTC)",
                   "registered-w1/extraction_manifest.json : started_at, finished_at",
                   "describe/describe.json : timing (BigQuery job creation and end times of scans A and B)",
                   "thesis Chapter 4, Section Implementation (revised scores computed from 11:36 UTC)"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Order of Commitments, the Record That Dates Each, and What Was Known When It Was Made (2026, Times in UTC)}",
           "\\label{tab:timeline}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3pt}",
           "\\renewcommand{\\arraystretch}{1.08}",
           "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.13\\textwidth}>{\\raggedright\\arraybackslash}p{0.45\\textwidth}"
           ">{\\raggedright\\arraybackslash}p{0.16\\textwidth}>{\\raggedright\\arraybackslash}p{0.22\\textwidth}@{}}",
           "\\toprule",
           "When & Commitment or event & Record & Already known \\\\",
           "\\midrule"]
    for row in rows:
        out.append(" & ".join(row) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize Commit times are committer times, recorded in UTC+9 and converted. Job times are the "
            "creation and end times that BigQuery reports for each job. Full commit identifiers and file hashes are in "
            "Table~\\ref{tab:ids}.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def tab_explore(D: dict) -> str:
    E = D["explore"]
    names = (("revised", "Revised"), ("registered", "Registered"))
    out = [header(["supplement/exploratory_checks.json (script supplement/exploratory_checks.py)"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Exploratory Checks, Computed After Every Result of Both Analyses Was Known}",
           "\\label{tab:explore}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3.2pt}",
           "\\begin{tabular}{@{}llcc@{}}",
           "\\toprule",
           " & & Revised analysis & Registered analysis \\\\"]
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(a) Decision contrasts under 50 further bootstrap seeds of 400 resamples: lower interval end, mean (SD) [range]; "
            "seeds whose verdict differs from seed 42}} \\\\"]
    lab = {"A1": "A1, W0, new approval pairs", "A2": "A2, W0, new transfer senders", "F1": "F1, W1, new approval pairs",
           "F2": "F2, W1, new transfer senders", "F3": "F3, W1, liquidation-free close rate"}
    for k, text in lab.items():
        cells = []
        for name, _ in names:
            s = E["seed_spread"][name][k]
            end = "ci_high" if k == "A1" else "ci_low"
            cells.append(f"{f3(s[end + '_mean'])} ({s[end + '_sd']:.4f}) [{f3(s[end + '_min'])}, {f3(s[end + '_max'])}]; "
                         f"{s['seeds_with_other_verdict']} of {s['seeds']}")
        endname = "upper end" if k == "A1" else "lower end"
        out.append(f"{text} & {endname} & " + " & ".join(cells) + " \\\\")
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(b) Steps of the weight: $\\tau_b$ of C-PR at the higher $\\lambda$ minus at the lower one, paired, 400 resamples, seed 42}} \\\\"]
    cohorts = [("w0_spenders", APPR, "W0 spenders, new approval pairs"), ("w0_spenders", SEND, "W0 spenders, new transfer senders"),
               ("w1_spenders", APPR, "W1 spenders, new approval pairs"), ("w1_spenders", SEND, "W1 spenders, new transfer senders"),
               ("w1_traders", LIQ, "W1 traders, liquidation-free close rate")]
    steps = [("0.25-0.0", "$0\\to0.25$"), ("0.75-0.25", "$0.25\\to0.75$"), ("1.0-0.75", "$0.75\\to1$")]
    for c, l, text in cohorts:
        for i, (key, st) in enumerate(steps):
            cells = [delta_cell(E["lambda_steps"][name][f"{c}:{l}"][key]) for name, _ in names]
            out.append(f"{text if i == 0 else ''} & {st} & " + " & ".join(cells) + " \\\\")
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(c) Rank agreement: $\\tau_b$ between the C-PR scores at two values of $\\lambda$ over the cohort, 400 resamples, seed 42}} \\\\"]
    coh = [("same_window", "Matched cohort, end of window"), ("w0_spenders", "W0 spenders"), ("w1_spenders", "W1 spenders")]
    pairs = [("0.0-0.25", "$\\lambda=0$ and $0.25$"), ("0.25-0.75", "$\\lambda=0.25$ and $0.75$"), ("0.75-1.0", "$\\lambda=0.75$ and $1$")]
    for c, text in coh:
        for i, (key, pl) in enumerate(pairs):
            cells = []
            for name, _ in names:
                e = E["lambda_rank_agreement"][name][c][key]
                cells.append(f"{f3(e['tau_b'])} [{f3(e['ci_low'])}, {f3(e['ci_high'])}]")
            out.append(f"{text if i == 0 else ''} & {pl} & " + " & ".join(cells) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize Computed on 11 October 2026 from the per-contract score files of the pipeline; "
            "no row enters a rule. The script first recomputes every decision contrast of Table~\\ref{tab:contrasts} except those "
            "of S2 and reproduces the published values exactly. In (a) the A1 row reports the upper end, which decides "
            "``no worse''; every other row the lower end.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"))
    args = ap.parse_args()
    if not args.phd_works:
        raise SystemExit("pass --phd-works PATH or set PHD_WORKS")
    phd = Path(args.phd_works).resolve()
    _, project = locate(phd)
    project_dirs = [f"1-Dissertation-Works/{p}/experiments" for p in (project,) + PROJECTS]
    D = load(phd)
    tables = {
        "tab_timeline.tex": tab_timeline(phd, D),
        "tab_ids.tex": tab_ids(phd, D, project_dirs),
        "tab_holdout.tex": tab_holdout(D),
        "tab_contrasts.tex": tab_contrasts(D),
        "tab_bench.tex": tab_bench(D),
        "tab_explore.tex": tab_explore(D),
    }
    for name, text in tables.items():
        (HERE / name).write_text(text, encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
