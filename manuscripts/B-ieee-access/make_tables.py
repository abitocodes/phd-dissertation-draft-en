#!/usr/bin/env python3
"""Tables of Manuscript B (IEEE Access), written from the published results of the study.

    python make_tables.py --repo /path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # or set CONTRACT_REP_REPO

The path is a checkout of the public repository
https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation, with its history.
That repository holds the study's folder of the authors' Git repository; the commits of the
registered record keep their times and file contents but have new identifiers, listed with
those of the authors' repository in its HISTORY.md. A checkout of the authors' repository that
contains the public repository as the submodule
1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation also works.

Writes tab_bench.tex, tab_timeline.tex, tab_ids.tex, tab_graph.tex, tab_cohorts.tex, tab_holdout.tex,
tab_contrasts.tex, tab_cpr.tex, tab_union.tex, tab_sybil.tex and tab_explore.tex next to this
file. Every number comes from one of these sources, named again in a comment at the top of
each table:

- the published summaries of both analyses: experiments/data/3-published-results-for-thesis/
  for the registered analysis and its subfolder revised-contract-12m/ for the contract-graph
  analysis, the main analysis of the paper; each file is checked against SHA256SUMS.txt, and
  the checksum list of the main analysis against the commit that published it;
- the extraction manifest of W1 and the job times in describe/describe.json;
- the commit history of the public repository (git log), and SHA-256 of the registration files
  as git stores them (LF line ends) and as the manifest recorded them (CRLF line ends);
- supplement/exploratory_checks.json (Appendix A of the paper).

Nothing is typed in by hand except the wording of the rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBMODULE = "1-Dissertation-Works/ERC20-Allowance-PageRank-Wallet-Reputation"  # the public repository inside the authors' one
APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
DELTA = 0.01
REVISED = "revised-contract-12m"  # subfolder of the published results that holds the contract-graph analysis (the main analysis)
# Commit identifiers in the public repository. The dated record of the registered test
# (commit times are printed in the timeline and identifier tables).
COMMITS = {
    "plan": "d060f3a",
    "registration": "1747e64",
    "registered_results": "344017e",
    "registered_benchmark": "7054746",
}
# The main analysis, defined after the registered results were known; listed without times.
MAIN_COMMITS = {
    "main_results": "6b389df",
    "main_code": "bb78da3",
    "drive_manifest": "7aa7928",
}
# The commits of the registered record in the authors' Git repository (HISTORY.md of the public
# repository). The extraction manifest and the registered digest, written there, record these.
AUTHORS_REPO = {"plan": "43d8045", "registration": "0d3a057", "registered_results": "8d8b568", "registered_benchmark": "f33a87a"}
W0_DAY, W1_DAY = "31 March 2026", "30 June 2026"


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def locate(path: Path) -> Path:
    """The checkout of the public repository: the path itself, or its submodule in the authors' repository."""
    for repo in (path, path / SUBMODULE):
        if (repo / "experiments" / "data" / "3-published-results-for-thesis" / REVISED / "results_digest.md").exists():
            return repo
    raise SystemExit(f"no checkout of the public repository with {REVISED} at {path}")


def crlf(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


def sha_crlf(path: Path) -> str:
    """SHA-256 of a file with CRLF line ends, the form SHA256SUMS.txt records."""
    return hashlib.sha256(crlf(path.read_bytes())).hexdigest()


def check_sums(pub: Path, files: list[str]) -> None:
    sums = {}
    for line in (pub / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if line.strip():
            h, f = line.split(maxsplit=1)
            sums[f.strip().lstrip("*")] = h
    for f in files:
        if sums.get(f) != sha_crlf(pub / f):
            raise SystemExit(f"{pub / f} does not match SHA256SUMS.txt")


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def git_bytes(repo: Path, spec: str) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(repo), "show", spec], capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        raise SystemExit(f"{spec} not found in the repository")


def commit_info(repo: Path, short: str) -> tuple[str, datetime]:
    out = git(repo, "show", "-s", "--format=%H %cI", short).split()
    return out[0], datetime.fromisoformat(out[1]).astimezone(timezone.utc)


def blob_sha(repo: Path, commit: str, rel: str) -> tuple[str, str]:
    """SHA-256 of a file of experiments/ in a commit, with LF line ends (as stored) and with CRLF line ends."""
    data = git_bytes(repo, f"{commit}:experiments/{rel}")
    return hashlib.sha256(data).hexdigest(), hashlib.sha256(crlf(data)).hexdigest()


def check_main_commit(repo: Path, pub: Path) -> None:
    """The summaries read here are those of the commit that published them, at the code revision the digest names."""
    rel = f"experiments/data/3-published-results-for-thesis/{REVISED}/SHA256SUMS.txt"
    committed = git_bytes(repo, f"{MAIN_COMMITS['main_results']}:{rel}")
    if crlf(committed) != crlf((pub / "SHA256SUMS.txt").read_bytes()):
        raise SystemExit(f"SHA256SUMS.txt of {REVISED} differs from commit {MAIN_COMMITS['main_results']}")
    m = re.search(r"Code revision: `([0-9a-f]{40})`", (pub / "results_digest.md").read_text(encoding="utf-8"))
    if not m or m.group(1) != commit_info(repo, MAIN_COMMITS["main_code"])[0]:
        raise SystemExit(f"the digest of {REVISED} does not name code revision {MAIN_COMMITS['main_code']}")


def load(repo: Path) -> dict:
    base = repo / "experiments" / "data" / "3-published-results-for-thesis"
    spec = {
        "main": (base / REVISED, {
            "same": "same-window/eval_summary.json", "w0": "holdout-w0/eval_summary.json",
            "w1": "window-w1/eval_summary.json", "sybil": "sybil-model/sybil_model.json",
            "bench": "benchmark/benchmark.json", "describe": "describe/describe.json",
            "supp": "supplementary/supplementary.json", "rob": "robustness/robustness.json"}),
        "registered": (base, {
            "same": "same-window/eval_summary.json", "w0": "holdout-w0/eval_summary.json",
            "w1": "registered-w1/eval_summary.json", "sybil": "sybil-model/sybil_model.json",
            "bench": "benchmark/benchmark.json", "describe": "describe/describe.json",
            "manifest": "registered-w1/extraction_manifest.json"}),
    }
    D: dict = {}
    for name, (pub, files) in spec.items():
        check_sums(pub, list(files.values()))
        D[name] = {k: json.loads((pub / f).read_text(encoding="utf-8")) for k, f in files.items()}
    check_main_commit(repo, base / REVISED)
    D["explore"] = json.loads((HERE / "supplement" / "exploratory_checks.json").read_text(encoding="utf-8"))
    return D


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def _fixed(x: float, signed: bool) -> str:
    """Three decimals; more when the value is not zero but would print as zero."""
    for nd in (3, 4, 5, 6):
        s = f"{x:+.{nd}f}" if signed else f"{x:.{nd}f}"
        if float(s) != 0.0 or x == 0.0:
            break
    if float(s) == 0.0:
        s = ("+" if signed else "") + s.lstrip("+-")
    return s.replace("-", "$-$")


def f3(x: float) -> str:
    return _fixed(x, False)


def sgn(x: float) -> str:
    return _fixed(x, True)


def f4(x: float) -> str:
    s = f"{x:.4f}"
    if float(s) == 0.0:
        s = s.lstrip("-")
    return s.replace("-", "$-$")


def ci(e: dict, lo: str = "ci_low", hi: str = "ci_high") -> str:
    return f"[{f3(e[lo])}, {f3(e[hi])}]"


def tau_cell(e: dict) -> str:
    return f"{f3(e['kendall_tau'])} {ci(e)}"


def delta_cell(e: dict) -> str:
    return f"{sgn(e['delta_tau'])} {ci(e)}"


def n(x) -> str:
    return f"{int(x):,}".replace(",", "{,}")


def pct(x: float, nd: int = 1) -> str:
    return f"{100 * x:.{nd}f}\\%"


def utc(t: datetime) -> str:
    return t.strftime("%H:%M:%S")


def header(sources: list[str]) -> str:
    return "% Generated by make_tables.py -- do not edit by hand.\n" + "".join(f"% Source: {s}\n" for s in sources)


def row(rows: list, a: str, b: str, outcome: str) -> dict:
    return next(r for r in rows if r["a"] == a and r["b"] == b and r["outcome"] == outcome)


def check_verdicts(D: dict) -> None:
    """Every verdict printed below follows from its interval, in both analyses."""
    for name in ("main", "registered"):
        w0, w1 = D[name]["w0"], D[name]["w1"]
        a1 = row(w0["contrasts_prefixed"], "cpr_l50", "cpr_l100", APPR)
        a2 = row(w0["contrasts_prefixed"], "cpr_l50", "cpr_l0", SEND)
        ra = w0["rule_a_primary"]
        if (a1["ci_high"] >= 0) != ra["no_worse_on_new_approvals"] or (a2["ci_low"] > 0) != ra["better_on_new_senders"]:
            raise SystemExit(f"{name}: a verdict of rule A does not follow from its interval")
        if ra["pass"] != (ra["no_worse_on_new_approvals"] and ra["better_on_new_senders"]):
            raise SystemExit(f"{name}: the primary part of rule A does not follow from its two parts")
        for block in ("rule_b", "sensitivity_awp", "sensitivity_isolated"):
            b = w1[block]
            if (b["F1"]["ci_low"] > 0) != b["F1"]["holds"] or (b["F2"]["ci_low"] > -DELTA) != b["F2"]["holds"]:
                raise SystemExit(f"{name} {block}: a verdict of F1 or F2 does not follow from its interval")
    m = D["main"]["w1"]
    if sorted(m["applied_criteria"]) != ["F1", "F2"] or abs(m["delta"] - DELTA) > 1e-12:
        raise SystemExit("the main analysis does not apply F1 and F2 with the margin 0.01")
    for block in ("rule_b", "sensitivity_awp", "sensitivity_isolated"):
        b = m[block]
        both = b["F1"]["holds"] and b["F2"]["holds"]
        if b["f1_f2_hold"] != both or b["rule_b_reading"] != ("both applied criteria hold" if both else "not met"):
            raise SystemExit(f"main {block}: the reading does not follow from F1 and F2")


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def tab_bench(D: dict) -> str:
    rows = [("EndorseRank", "endorserank"), ("AWP", "awp"), ("C-PR ($\\lambda=0.5$)", "cpr_l50"), ("S-PR", "spr")]
    out = [header([f"benchmark/benchmark.json : main ({REVISED}/ and the registered analysis)"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{Solver Time at the Freeze of 30 June 2026 on the Whole Contract Graph and on the Graphs of the Registered "
           "Analysis (Mean and SD of Five Timed Runs After One Warm-Up)}",
           "\\label{tab:bench}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3pt}",
           "\\begin{tabular}{@{}lrrrr@{}}",
           "\\toprule",
           "Score & $|V|$ & $|E|$ & Iter. & Time (s) \\\\"]
    for name, title in (("main", "Main analysis: the whole contract graph"),
                        ("registered", "Registered analysis: the graphs of its cohort's events")):
        out += ["\\midrule", f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"]
        B = D[name]["bench"]["main"]
        nd = 3 if name == "main" else 2
        for label, k in rows:
            e = B[k]
            out.append(f"{label} & {n(e['nodes'])} & {n(e['edges'])} & {e['iterations']} & "
                       f"{e['mean_s']:.{nd}f} ({e['sd_s']:.{nd}f}) \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\columnwidth}{\\footnotesize One session of one warm-up and five timed runs per graph and setting, the "
            "measurement cited throughout; the time covers matrix assembly and power "
            "iteration ($d=0.85$, tolerance $10^{-8}$, at most 300 iterations) on edge lists built in advance. S-PR includes the solve "
            "of the authorization layer that supplies its restart vector. $|V|$ and $|E|$ are those of each solver graph, which holds "
            "the pairs of positive weight (Section~\\ref{sec:graphs}); C-PR walks the union of both layers. In the main analysis the "
            "timed graph is the whole contract graph (all pairs between contracts, whether or not they touch the matched "
            "cohort); the registered graphs hold the events that name a contract of the registered cohort, user accounts "
            "included. Same machine for both analyses (Section~\\ref{sec:cost}).}",
            "\\end{table}", ""]
    return "\n".join(out)


def tab_timeline(repo: Path, D: dict) -> str:
    desc, man = D["registered"]["describe"]["timing"], D["registered"]["manifest"]
    t = {k: commit_info(repo, v)[1] for k, v in COMMITS.items()}
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
         f"\\sha{{{COMMITS['plan']}}}", "No log of this study extracted"),
        (f"9 Oct, {utc(scan_a_c)}--{utc(scan_a_e)}", f"Scan~A of the observation window; the BigQuery job was created {gap_a}~s after the plan commit",
         "Job metadata; cost ledger", "---"),
        ("9 Oct, before 16:49", f"Cohort of {n(rg['same']['cohort'])} contracts, extraction of the events that name one of them, "
         "same-window and W0 evaluation; rule~A judged", f"Summaries committed in \\sha{{{COMMITS['registration']}}}",
         "Logs of the observation window"),
        (f"9 Oct, {utc(t['registration'])}", "Registration of W1: rule~B with $\\delta=0.01$, of which this paper applies the criteria F1 and F2; "
         "F6 and two sensitivity analyses to be reported beside it; configuration status set to registered",
         f"\\sha{{{COMMITS['registration']}}}", "Every same-window and W0 result of the registered analysis"),
        (f"9 Oct, {utc(m_s)}", f"Extraction script checks the committed registration and writes its manifest ({gap_m}~s after the commit): "
         "commit and both SHA-256 hashes", "Manifest", "---"),
        (f"9 Oct, {utc(scan_b_c)}--{utc(scan_b_e)}", f"Scan~B of July--September 2026; job created {gap_b}~s after the commit; manifest closed at {utc(m_f)}",
         "Job metadata; manifest", "No July--September log extracted for this study before this"),
        (f"9 Oct, {utc(t['registered_results'])}", "Registered W1 evaluation, then robustness and Sybil model, committed",
         f"\\sha{{{COMMITS['registered_results']}}}", "W1 labels"),
        (f"{t['registered_benchmark'].day} {t['registered_benchmark'].strftime('%b')}, {utc(t['registered_benchmark'])}",
         "Registered benchmark and data description (BigQuery job times, amount shares) committed",
         f"\\sha{{{COMMITS['registered_benchmark']}}}", "W1 labels"),
        ("Later", "After the registered results were known, the revised analysis was defined: amounts in US dollars on five tokens; "
         "scores from the twelve months before each freeze; graphs whose nodes are contracts other than smart accounts, with edges "
         "read from the whole chain; each allowance counted up to its owner's balance at the freeze, with balances reconstructed "
         "from \\texttt{Transfer} logs; constants set on the contract graph; and the discovery-order test. It is the main analysis of "
         "this paper. Rule~A and the criteria F1 and F2 of rule~B are applied to its scores as a re-analysis; the discovery-order "
         "test is reported in \\cite{kwon2026companion}; the exploratory checks of Appendix~\\ref{app:explore} followed",
         f"Definitions and results in the public repository (Table~\\ref{{tab:ids}})", "Every registered result"),
    ]
    out = [header(["git log of the public repository (committer times of the registered record, converted to UTC; "
                   "the main analysis is listed without a time)",
                   "registered-w1/extraction_manifest.json : started_at, finished_at",
                   "describe/describe.json : timing (BigQuery job creation and end times of scans A and B)"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Order of Commitments, the Record of Each, and What Was Known When It Was Made (2026, Times in UTC)}",
           "\\label{tab:timeline}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3pt}",
           "\\renewcommand{\\arraystretch}{1.08}",
           "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.13\\textwidth}>{\\raggedright\\arraybackslash}p{0.47\\textwidth}"
           ">{\\raggedright\\arraybackslash}p{0.16\\textwidth}>{\\raggedright\\arraybackslash}p{0.20\\textwidth}@{}}",
           "\\toprule",
           "When & Commitment or event & Record & Already known \\\\",
           "\\midrule"]
    for r in rows:
        out.append(" & ".join(r) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize Commit times are committer times, recorded in UTC+9 and converted. Job times are the "
            "creation and end times that BigQuery reports for each job. Commit identifiers are those of the public repository; "
            "the full identifiers, those of the authors' repository and the file hashes are in Table~\\ref{tab:ids}. The last row "
            "carries no date: no definition of the main analysis preceded the registered results.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def tab_ids(repo: Path, D: dict) -> str:
    man = D["registered"]["manifest"]
    for field in ("head", "registration_commit"):
        if not str(man[field]).startswith(AUTHORS_REPO["registration"]):
            raise SystemExit(f"manifest {field} is not the registration commit {AUTHORS_REPO['registration']} of the authors' repository")
    rows = [
        ("Plan and configuration (rule A)", "plan"),
        ("Registration of W1 (rule B)", "registration"),
        ("Registered results committed", "registered_results"),
        ("Registered benchmark and data description", "registered_benchmark"),
    ]
    main_rows = [
        ("Published results: summaries, digest and checksums", "main_results"),
        ("Code revision at which they were computed", "main_code"),
        ("List of the per-contract files in the public Drive folder", "drive_manifest"),
    ]
    out = [header(["git log of the public repository (commit identifiers; committer times of the registered record, converted "
                   "to UTC; the main analysis is listed without times); identifiers of the authors' repository from its HISTORY.md",
                   "registered-w1/extraction_manifest.json : sha256 (CRLF checkout), head and registration_commit",
                   "git show <commit>:experiments/docs/registration_w1.md and config/contract_reputation.yaml (LF, as stored)",
                   f"{REVISED}/results_digest.md : code revision; {REVISED}/SHA256SUMS.txt compared with commit "
                   f"{MAIN_COMMITS['main_results']}"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{Commit Identifiers of the Registered Record (Times in UTC) and of the Main Analysis, "
           "and SHA-256 Hashes of the Registration Files and the Plan}",
           "\\label{tab:ids}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{0pt}",
           "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{\\columnwidth}@{}}",
           "\\toprule"]
    for label, key in rows:
        full, t = commit_info(repo, COMMITS[key])
        out.append(f"{label}, {t.day} {t.strftime('%b')} {utc(t)}; \\sha{{{AUTHORS_REPO[key]}}} in the authors' repository\\\\")
        out.append(f"\\quad\\sha{{{full}}}\\\\")
    out.append("\\midrule")
    out.append("\\emph{Main analysis (contract graph), defined after the registered results were known}\\\\")
    for label, key in main_rows:
        full, _ = commit_info(repo, MAIN_COMMITS[key])
        out.append(f"{label}\\\\")
        out.append(f"\\quad\\sha{{{full}}}\\\\")
    out.append("\\midrule")
    files = [("docs/registration_w1.md", "registration document"), ("config/contract_reputation.yaml", "configuration")]
    for rel, label in files:
        lf, crlf_hash = blob_sha(repo, COMMITS["registration"], rel)
        recorded = man["sha256"][rel]
        if recorded != crlf_hash:
            raise SystemExit(f"manifest hash of {rel} is not the CRLF hash of the committed file")
        out.append(f"SHA-256 of the {label}, CRLF line ends (recorded in the manifest)\\\\")
        out.append(f"\\quad\\sha{{{recorded[:32]}}}\\\\")
        out.append(f"\\quad\\sha{{{recorded[32:]}}}\\\\")
        out.append(f"SHA-256 of the {label}, LF line ends (as git stores it)\\\\")
        out.append(f"\\quad\\sha{{{lf[:32]}}}\\\\")
        out.append(f"\\quad\\sha{{{lf[32:]}}}\\\\")
    lf, _ = blob_sha(repo, COMMITS["plan"], "docs/analysis_plan.md")
    out.append(f"SHA-256 of the plan in \\sha{{{COMMITS['plan']}}}, LF line ends\\\\")
    out.append(f"\\quad\\sha{{{lf[:32]}}}\\\\")
    out.append(f"\\quad\\sha{{{lf[32:]}}}\\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\columnwidth}{\\footnotesize Identifiers are those of the public repository. For the registered record the "
            "table also names the commit of the authors' Git repository from which each was copied with its times and contents, "
            "as the extraction manifest, the registered digest and the repository's HISTORY.md record it. The commits of the main "
            "analysis carry no time here: none of them preceded the registered results. "
            "Each SHA-256 value is printed over two lines; join them without a space.}",
            "\\end{table}", ""]
    return "\n".join(out)


def tab_graph(D: dict) -> str:
    """The contract graph of the main analysis at the two freezes: allowances and the balance cap, the two layers
    and the union graph."""
    M = D["main"]
    desc = M["describe"]
    al, pr = desc["allowances"], desc["pairs"]
    un = {"t1": M["w0"]["union_graph"], "tobs": M["w1"]["union_graph"]}
    if M["same"]["union_graph"] != un["tobs"]:
        raise SystemExit("the union graph at the W1 freeze differs between the same-window and the W1 summaries")

    def both(get) -> str:
        return f"{get('t1')} & {get('tobs')}"

    def tot(tag: str) -> dict:
        t = al[tag]["total"]
        if t["n_positive_eff"] + t["n_capped_to_zero"] != t["n_latest_positive"]:
            raise SystemExit(f"{tag}: positive after the cap and capped to zero do not sum to the allowances")
        return t

    rows = [
        "\\multicolumn{3}{@{}l}{\\emph{Latest allowances between contracts (token, owner, spender)}} \\\\",
        "Positive latest allowances & " + both(lambda g: n(tot(g)["n_latest_positive"])) + " \\\\",
        "\\quad unlimited & " + both(lambda g: n(tot(g)["n_unlimited"])) + " \\\\",
        "\\quad\\quad share & " + both(lambda g: pct(tot(g)["share_unlimited"])) + " \\\\",
        "\\quad capped to zero (no balance held) & " + both(lambda g: n(tot(g)["n_capped_to_zero"])) + " \\\\",
        "\\quad\\quad share & " + both(lambda g: pct(tot(g)["share_capped_to_zero"])) + " \\\\",
        "\\quad capped below the allowance & " + both(lambda g: n(tot(g)["n_capped_below_allowance"])) + " \\\\",
        "\\quad positive after the cap & " + both(lambda g: n(tot(g)["n_positive_eff"])) + " \\\\",
        "\\midrule",
        "\\multicolumn{3}{@{}l}{\\emph{Authorization layer (owner, spender)}} \\\\",
        "Pairs & " + both(lambda g: n(pr[g]["allowance_capped"]["pairs"])) + " \\\\",
        "\\quad owner contracts & " + both(lambda g: n(pr[g]["allowance_capped"]["sources"])) + " \\\\",
        "\\quad spender contracts & " + both(lambda g: n(pr[g]["allowance_capped"]["destinations"])) + " \\\\",
        "\\quad pairs of the largest owner & " + both(lambda g: n(pr[g]["allowance_capped"]["largest_source_pairs"])) + " \\\\",
        "Pairs without the cap (sensitivity) & " + both(lambda g: n(pr[g]["allowance_uncapped"]["pairs"])) + " \\\\",
        "\\midrule",
        "\\multicolumn{3}{@{}l}{\\emph{Payment layer (sender, recipient)}} \\\\",
        "Pairs & " + both(lambda g: n(pr[g]["transfer"]["pairs"])) + " \\\\",
        "\\quad sender contracts & " + both(lambda g: n(pr[g]["transfer"]["sources"])) + " \\\\",
        "\\quad recipient contracts & " + both(lambda g: n(pr[g]["transfer"]["destinations"])) + " \\\\",
        "\\midrule",
        "\\multicolumn{3}{@{}l}{\\emph{Union graph (either layer, two different contracts)}} \\\\",
        "Pairs & " + both(lambda g: n(un[g]["pairs"])) + " \\\\",
        "Contracts & " + both(lambda g: n(un[g]["nodes"])) + " \\\\",
    ]
    c = desc["constants"]
    out = [header([f"{REVISED}/describe/describe.json : allowances, pairs, constants",
                   f"{REVISED}/holdout-w0 and window-w1/eval_summary.json : union_graph"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{The Contract Graph of the Main Analysis at the Two Freezes}",
           "\\label{tab:graph}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{4pt}",
           "\\begin{tabular}{@{}lrr@{}}",
           "\\toprule",
           f"Freeze & {W0_DAY} & {W1_DAY} \\\\",
           "\\midrule",
           *rows,
           "\\bottomrule",
           "\\end{tabular}",
           "",
           "\\vspace{2pt}",
           "\\parbox{\\columnwidth}{\\footnotesize Every end of every pair is a contract; no user account is a node. An allowance "
           "is the latest \\texttt{Approval} of a (token, owner, spender) triple in the score window, kept when positive and "
           "counted up to the owner's balance of the token at the freeze; a pair sums two contracts over the five tokens. "
           f"Constants set on this graph: $m_T={c['m_transfer_usd']:.0f}$, $m_A={c['m_allowance_usd']:.3f}$ and "
           f"$U={n(round(c['cap_allowance_usd']))}$ dollars (Section~\\ref{{sec:constants}}).}}",
           "\\end{table}", ""]
    return "\n".join(out)


def tab_cohorts(D: dict) -> str:
    """Where the cohorts lie in the contract graph, and what their labels count (main analysis)."""
    M = D["main"]
    cov = [("W0 spenders", M["w0"]["cohort_coverage"]["spenders_w0"]),
           ("W1 spenders", M["w1"]["cohort_coverage"]["spenders_w1"]),
           ("Matched cohort", M["same"]["cohort_coverage"]["cohort_tobs"])]
    a = []
    for name, c in cov:
        if c["union_graph"]["n"] + c["outside_contract_graph"]["n"] + c["self_pairs_only"]["n"] != c["n"]:
            raise SystemExit(f"{name}: union graph, self-pairs only and outside do not sum to the cohort")
        a.append(f"{name} & {n(c['n'])} & {n(c['union_graph']['n'])} & {pct(c['union_graph']['share'])} & "
                 f"{pct(c['allowance_layer']['share'])} & {pct(c['outside_contract_graph']['share'])} \\\\")
    ls = [M["w0"]["label_split"], M["w1"]["label_split"]]
    gained = [(M["w0"]["gained_new_approvals"], M["w0"]["gained_new_senders"]),
              (M["w1"]["gained_new_approvals"], M["w1"]["gained_new_senders"])]
    for (ga, gs), sp in zip(gained, ls):
        lab = sp["labels"]
        for k in (APPR, SEND):
            v = lab[k]
            if v["user_accounts"] + v["contracts"] + v["other"] != v["total"]:
                raise SystemExit(f"label split of {k}: the parts do not sum to the label")
        if ga != lab[APPR]["spenders_with_label"] or gs != lab[SEND]["spenders_with_label"]:
            raise SystemExit("the spenders that gained a label differ between the summary and its label split")
        o = sp["owners_at_freeze"]
        if o["user_accounts"] + o["contracts"] + o["other"] != o["total"]:
            raise SystemExit("owners at the freeze: the classes do not sum to the total")

    def lb(key: str, field: str, fmt) -> str:
        return " & ".join(fmt(sp["labels"][key][field]) for sp in ls)

    def own(field: str) -> str:
        return " & ".join(n(sp["owners_at_freeze"][field]) for sp in ls)

    b = [
        "New approval pairs in the label window & " + lb(APPR, "total", n) + " \\\\",
        "\\quad from user accounts & " + lb(APPR, "share_user_accounts", pct) + " \\\\",
        "\\quad spenders that gained one & " + lb(APPR, "spenders_with_label", n) + " \\\\",
        "New transfer senders in the label window & " + lb(SEND, "total", n) + " \\\\",
        "\\quad from user accounts & " + lb(SEND, "share_user_accounts", pct) + " \\\\",
        "\\quad spenders that gained one & " + lb(SEND, "spenders_with_label", n) + " \\\\",
        "\\midrule",
        "Positive allowance pairs at the freeze & " + own("total") + " \\\\",
        "\\quad owner is a user account & " + own("user_accounts") + " \\\\",
        "\\quad owner is a contract & " + own("contracts") + " \\\\",
    ]
    out = [header([f"{REVISED}/holdout-w0, window-w1 and same-window/eval_summary.json : cohort_coverage, label_split, "
                   "gained_new_approvals, gained_new_senders"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{The Cohorts in the Contract Graph, and What Their Labels Count (Main Analysis)}",
           "\\label{tab:cohorts}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{4pt}",
           "\\begin{tabular}{@{}lrrrrr@{}}",
           "\\toprule",
           " & & \\multicolumn{2}{c}{In the} & In the author- & In no \\\\",
           "(a) Cohort & Contracts & \\multicolumn{2}{c}{union graph} & ization layer & pair \\\\",
           "\\midrule",
           *a,
           "\\bottomrule",
           "\\end{tabular}",
           "",
           "\\vspace{4pt}",
           "\\setlength{\\tabcolsep}{4pt}",
           "\\begin{tabular}{@{}lrr@{}}",
           "\\toprule",
           "(b) Labels and standing allowances & W0 spenders & W1 spenders \\\\",
           "\\midrule",
           *b,
           "\\bottomrule",
           "\\end{tabular}",
           "",
           "\\vspace{2pt}",
           f"\\parbox{{\\columnwidth}}{{\\footnotesize (a) W0 spenders at the freeze of {W0_DAY}; W1 spenders and the matched cohort at "
           f"that of {W1_DAY}. A contract in no pair between two different contracts lies outside the union graph and scores "
           "zero under every score and count. (b) The labels count every account, user accounts included, which no score "
           "reads. The lower block counts, without the balance cap, the pairs of an owner and a spender of the cohort with a "
           "positive latest allowance at the freeze, the pairs against which a new approval pair is new.}",
           "\\end{table}", ""]
    return "\n".join(out)


HOLDOUT_ROWS = [
    ("In-approve degree at the freeze", "t1_in_approve_degree", "in_approve_degree"),
    ("In-approve value at the freeze", "t1_in_approve_value", "in_approve_value"),
    ("Transfer in-degree at the freeze", "t1_in_degree", "in_degree"),
    ("Union in-degree at the freeze", "t1_in_degree_union", "in_degree_union"),
    ("EndorseRank", "endorserank", "endorserank"),
    ("EndorseRank with activity restarts", "endorserank_activity", "endorserank_activity"),
    ("AWP", "awp", "awp"),
    ("C-PR ($\\lambda=1$), authorization walk", "cpr_l100", "cpr_l100"),
    ("C-PR ($\\lambda=0.75$)", "cpr_l75", "cpr_l75"),
    ("C-PR ($\\lambda=0.5$), primary", "cpr_l50", "cpr_l50"),
    ("C-PR ($\\lambda=0.25$)", "cpr_l25", "cpr_l25"),
    ("C-PR ($\\lambda=0$), payment walk", "cpr_l0", "cpr_l0"),
    ("S-PR", "spr", "spr"),
]


def tab_holdout(D: dict) -> str:
    out = [header([f"holdout-w0/eval_summary.json : taus ({REVISED}/ and the registered analysis)",
                   f"{REVISED}/window-w1/eval_summary.json and registered-w1/eval_summary.json : spender_taus"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Kendall $\\tau_b$ Between Scores at the Freeze and Later Labels, With 95\\% Paired-Bootstrap Intervals}",
           "\\label{tab:holdout}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{4pt}",
           "\\begin{tabular}{@{}lcccc@{}}",
           "\\toprule"]
    titles = (("main", "Contract-graph analysis (the main analysis; a re-analysis defined after the registered results were known)"),
              ("registered", "Registered analysis (the test that the rules were fixed for)"))
    for k, (name, title) in enumerate(titles):
        w0, w1 = D[name]["w0"], D[name]["w1"]
        if k:
            out.append("\\midrule")
        out.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\")
        out.append(" & \\multicolumn{2}{c}{W0 spenders ($n=" + n(w0["spenders"]) + "$)} & \\multicolumn{2}{c}{W1 spenders ($n="
                   + n(w1["spenders"]) + "$)} \\\\")
        out.append("\\cmidrule(lr){2-3}\\cmidrule(l){4-5}")
        out.append("Score & New approval pairs & New transfer senders & New approval pairs & New transfer senders \\\\")
        out.append("\\midrule")
        for label, k0, k1 in HOLDOUT_ROWS:
            if k0 not in w0["taus"] or k1 not in w1["spender_taus"]:
                continue  # a count that the registered analysis does not have
            cells = [tau_cell(w0["taus"][k0][APPR]), tau_cell(w0["taus"][k0][SEND]),
                     tau_cell(w1["spender_taus"][k1][APPR]), tau_cell(w1["spender_taus"][k1][SEND])]
            out.append(f"{label} & " + " & ".join(cells) + " \\\\")
    rg, rv = D["registered"], D["main"]
    cov0 = rv["w0"]["cohort_coverage"]["spenders_w0"]["union_graph"]
    cov1 = rv["w1"]["cohort_coverage"]["spenders_w1"]["union_graph"]
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize W0: scores frozen on 31 March 2026, labels counted from April to June 2026. "
            "W1: scores frozen on 30 June 2026, labels counted from July to September 2026. In the main analysis every score is "
            "computed from the twelve months before its freeze on the graph of contracts (amounts in US dollars on five tokens, "
            "allowances counted up to the owner's balance), and the counts are taken on that graph: "
            "owner contracts with a capped allowance to the contract (in-approve degree), the summed capped value of those "
            "allowances (in-approve value), other contracts that sent it a transfer (transfer in-degree), and other contracts "
            "with an edge to it in either layer (union in-degree). "
            f"{n(cov0['n'])} of the W0 spenders ({pct(cov0['share'])}) and {n(cov1['n'])} of the W1 spenders ({pct(cov1['share'])}) "
            "lie in the union graph; the others score zero in every row of the upper block. "
            f"{n(rv['w0']['gained_new_approvals'])} W0 spenders gained a new approval pair and "
            f"{n(rv['w0']['gained_new_senders'])} a new transfer sender, and {n(rv['w1']['gained_new_approvals'])} and "
            f"{n(rv['w1']['gained_new_senders'])} W1 spenders did; in the registered analysis {n(rg['w0']['gained_new_approvals'])}, "
            f"{n(rg['w0']['gained_new_senders'])}, {n(rg['w1']['gained_new_approvals'])} and {n(rg['w1']['gained_new_senders'])}. "
            "In the registered analysis every score is computed in raw base units from every extracted event of every ERC-20 "
            "token since 1 October 2023, and the two counts are taken over all accounts. No value of the upper block is a "
            "registered result. "
            "The count, EndorseRank and AWP rows are reference scores that the companion study \\cite{kwon2026companion} also "
            "reports. Intervals: 400 paired resamples over the contracts of the cohort, seed 42.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def verdict_word(e: dict) -> str:
    return "holds" if e["holds"] else "fails"


def reading(block: dict) -> str:
    """'not met' when F1 or F2 fails; never a verdict that the rule is met (it has further registered criteria)."""
    return "\\textbf{not met}" if not (block["F1"]["holds"] and block["F2"]["holds"]) else "both applied criteria hold"


def tab_contrasts(D: dict) -> str:
    R, V = D["registered"], D["main"]

    def get(an: dict, path: tuple) -> dict:
        x = an
        for p in path:
            x = x[p]
        return x

    def after(an: dict, a: str, b: str, outcome: str) -> dict:
        return row(an["w0"]["contrasts_after"], a, b, outcome)

    def ruled(label: str, path: tuple, test: str) -> str:
        r, v = get(R, path), get(V, path)
        return f"{label} & {test} & {delta_cell(v)} & {verdict_word(v)} & {delta_cell(r)} & {verdict_word(r)} \\\\"

    def a_row(label: str, b: str, outcome: str, test: str, key: str) -> str:
        r = row(R["w0"]["contrasts_prefixed"], "cpr_l50", b, outcome)
        v = row(V["w0"]["contrasts_prefixed"], "cpr_l50", b, outcome)
        rr, vv = R["w0"]["rule_a_primary"][key], V["w0"]["rule_a_primary"][key]
        return (f"{label} & {test} & {delta_cell(v)} & {'holds' if vv else 'fails'} & {delta_cell(r)} & "
                f"{'holds' if rr else 'fails'} \\\\")

    def plain(label: str, r: dict, v: dict) -> str:
        return f"{label} & --- & {delta_cell(v)} & & {delta_cell(r)} & \\\\"

    def met(x: bool) -> str:
        return "met" if x else "\\textbf{not met}"

    def group(title: str) -> list[str]:
        return ["\\midrule", f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"]

    out = [header([f"holdout-w0/eval_summary.json : contrasts_prefixed, rule_a_primary, contrasts_after ({REVISED}/ and the registered analysis)",
                   "same-window/eval_summary.json : rule_a_secondary (both analyses)",
                   f"{REVISED}/window-w1/eval_summary.json and registered-w1/eval_summary.json : rule_b (F1, F2, F6a, F6b), "
                   "sensitivity_awp, sensitivity_isolated, endorserank_results"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Paired Contrasts in Both Analyses: Rule~A, the Two Applied Criteria of Rule~B, the Reports and Sensitivity "
           "Analyses Registered With Them, and Contrasts Computed After the Labels Were Known}",
           "\\label{tab:contrasts}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{2.6pt}",
           "\\begin{tabular}{@{}llcccc@{}}",
           "\\toprule",
           " & & \\multicolumn{2}{c}{Contract-graph analysis (re-analysis)} & \\multicolumn{2}{c}{Registered analysis (the test)} \\\\",
           "\\cmidrule(lr){3-4}\\cmidrule(l){5-6}",
           "Contrast ($a$ minus $b$) and label & Test & $\\Delta\\tau$ [95\\% CI] & Verdict & $\\Delta\\tau$ [95\\% CI] & Verdict \\\\"]
    out += group(f"Rule A, fixed in the plan ({COMMITS['plan']}) before any log of this study was extracted; W0 spenders")
    out.append(a_row("A1: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", "cpr_l100", APPR, "no worse", "no_worse_on_new_approvals"))
    out.append(a_row("A2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", "cpr_l0", SEND, "superiority", "better_on_new_senders"))
    out.append(f"Rule A, primary part (A1 and A2) & & & {met(V['w0']['rule_a_primary']['pass'])} & & {met(R['w0']['rule_a_primary']['pass'])} \\\\")
    out.append(f"Rule A, secondary part (same window) & & & {met(V['same']['rule_a_secondary']['pass'])} & & "
               f"{met(R['same']['rule_a_secondary']['pass'])} \\\\")
    out += group(f"Rule B, registered ({COMMITS['registration']}) before this study extracted the W1 logs: two of its registered "
                 "criteria, F1 and F2; margin $\\delta=0.01$; W1 spenders")
    out.append(ruled("F1: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs", ("w1", "rule_b", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "rule_b", "F2"), "non-inferiority"))
    out.append(f"Rule B, by F1 and F2 & & & {reading(V['w1']['rule_b'])} & & {reading(R['w1']['rule_b'])} \\\\")
    out += group("F6, the primary part of rule A on W1, registered to be reported beside the decision (nominal)")
    out.append(ruled("F6a: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", ("w1", "rule_b", "F6a"), "no worse"))
    out.append(ruled("F6b: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "rule_b", "F6b"), "superiority"))
    out += group("Registered sensitivity analysis S1: AWP as the comparator (nominal)")
    out.append(ruled("F1: C-PR $-$ AWP, new approval pairs", ("w1", "sensitivity_awp", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ AWP, new transfer senders", ("w1", "sensitivity_awp", "F2"), "non-inferiority"))
    out.append(f"S1, by F1 and F2 & & & {reading(V['w1']['sensitivity_awp'])} & & {reading(R['w1']['sensitivity_awp'])} \\\\")
    out += group("Registered sensitivity analysis S2: contracts outside a graph kept as isolated nodes (nominal)")
    out.append(ruled("F1: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs", ("w1", "sensitivity_isolated", "F1"), "superiority"))
    out.append(ruled("F2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "sensitivity_isolated", "F2"), "non-inferiority"))
    out.append(ruled("F6a: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", ("w1", "sensitivity_isolated", "F6a"), "no worse"))
    out.append(ruled("F6b: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", ("w1", "sensitivity_isolated", "F6b"), "superiority"))
    out.append(f"S2, by F1 and F2 & & & {reading(V['w1']['sensitivity_isolated'])} & & {reading(R['w1']['sensitivity_isolated'])} \\\\")
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
            "\\parbox{\\textwidth}{\\footnotesize $\\Delta\\tau=\\tau_a-\\tau_b$ on the same resamples. C-PR without a $\\lambda$ is the "
            "primary setting $\\lambda=0.5$. Superiority holds "
            "when the interval lies above zero, non-inferiority when its lower end lies above $-\\delta=-0.01$, and ``no worse'' when "
            "the interval contains zero or lies above it. This paper applies two of the registered criteria of rule~B, F1 and F2; "
            "under the registration the rule holds only if each of its criteria holds, so a failure of either gives ``not met''. "
            "The left column, the main analysis, applies the rules and thresholds of the "
            "plan and the registration to scores defined after the registered results were known (graphs of contracts, amounts in "
            "US dollars on five tokens, scores from the twelve months before each freeze, allowances counted up to the owner's "
            "balance), so none of its verdicts is a "
            "registered result; the right column is the test that the plan and the registration fixed. Nominal verdicts use "
            "unadjusted 95\\% intervals. The count, EndorseRank and AWP rows are reference contrasts that the companion study "
            "\\cite{kwon2026companion} also reports. Intervals: 400 paired resamples, seed 42.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def tab_cpr(D: dict) -> str:
    """C-PR (lambda = 0.5) against every other score and the four counts, main analysis, both windows."""
    V = D["main"]
    w0, w1, supp = V["w0"], V["w1"], V["supp"]
    s0, s1 = supp["w0"], supp["w1"]
    if s0["n"] != w0["spenders"] or s1["n"] != w1["spenders"]:
        raise SystemExit("supplementary spender cohorts differ from the holdout summaries")
    rb, sa, er, b1 = w1["rule_b"], w1["sensitivity_awp"], w1["endorserank_results"], w1["baseline_contrasts"]
    A, B, S = "$^{a}$", "$^{b}$", "$^{s}$"

    def pre(b, o):
        return row(w0["contrasts_prefixed"], "cpr_l50", b, o)

    def aft(b, o):
        return row(w0["contrasts_after"], "cpr_l50", b, o)

    def base0(o):
        return row(w0["baseline_contrasts"], "cpr_l50", "t1_in_degree_union", o)

    def both(key: str):
        return [(s0[f"cpr_minus_{key}_appr"], ""), (s0[f"cpr_minus_{key}_send"], ""),
                (s1[f"cpr_minus_{key}_appr"], ""), (s1[f"cpr_minus_{key}_send"], "")]

    rows = [
        ("Authorization walk, C-PR ($\\lambda=1$)", [(pre("cpr_l100", APPR), A), (s0["cpr_minus_l100_send"], ""),
                                                     (rb["F6a"], B), (s1["cpr_minus_l100_send"], "")]),
        ("Payment walk, C-PR ($\\lambda=0$)", [(aft("cpr_l0", APPR), ""), (pre("cpr_l0", SEND), A), (rb["F1"], B), (rb["F2"], B)]),
        ("EndorseRank", [(aft("endorserank", APPR), ""), (s0["cpr_minus_er_send"], ""),
                         (er["cpr_minus_endorserank_appr"], ""), (s1["cpr_minus_er_send"], "")]),
        ("EndorseRank, activity restarts", both("er_activity")),
        ("AWP", [(aft("awp", APPR), ""), (aft("awp", SEND), ""), (sa["F1"], S), (sa["F2"], S)]),
        ("S-PR", both("spr")),
        None,
        ("In-approve degree", both("degree")),
        ("In-approve value", both("approve_value")),
        ("Transfer in-degree", both("in_degree")),
        ("Union in-degree", [(base0(APPR), ""), (base0(SEND), ""),
                             (b1["cpr_minus_union_in_degree_appr"], ""), (b1["cpr_minus_union_in_degree_send"], "")]),
    ]

    def cell(r: dict, mark: str) -> str:
        return f"{sgn(r['delta_tau'])}{mark} {ci(r)}"

    lines = []
    for item in rows:
        if item is None:
            lines.append("\\midrule")
            continue
        label, cells = item
        lines.append(f"{label} & " + " & ".join(cell(r, m) for r, m in cells) + " \\\\")
    lines += ["\\midrule",
              f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{Spenders that another contract had paid before the freeze "
              f"(W0 $n={n(s0['recv_n'])}$, W1 $n={n(s1['recv_n'])}$)}}}} \\\\",
              "AWP & " + " & ".join(cell(s[f"recv_cpr_minus_awp_{k}"], "") for s in (s0, s1) for k in ("appr", "send")) + " \\\\",
              f"In-approve degree & {cell(s0['recv_cpr_minus_degree_appr'], '')} & --- & "
              f"{cell(s1['recv_cpr_minus_degree_appr'], '')} & --- \\\\"]
    out = [header([f"{REVISED}/holdout-w0/eval_summary.json : contrasts_prefixed, contrasts_after, baseline_contrasts",
                   f"{REVISED}/window-w1/eval_summary.json : rule_b, sensitivity_awp, endorserank_results, baseline_contrasts",
                   f"{REVISED}/supplementary/supplementary.json : w0, w1"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{C-PR Beside Every Other Score and Count of the Main Analysis: $\\Delta\\tau=\\tau_{\\text{C-PR}}-\\tau_b$ "
           "With 95\\% Paired-Bootstrap Intervals}",
           "\\label{tab:cpr}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{4pt}",
           "\\begin{tabular}{@{}lcccc@{}}",
           "\\toprule",
           " & \\multicolumn{2}{c}{W0 spenders ($n=" + n(w0["spenders"]) + "$)} & \\multicolumn{2}{c}{W1 spenders ($n="
           + n(w1["spenders"]) + "$)} \\\\",
           "\\cmidrule(lr){2-3}\\cmidrule(l){4-5}",
           "C-PR ($\\lambda=0.5$) minus & New approval pairs & New transfer senders & New approval pairs & New transfer senders \\\\",
           "\\midrule",
           *lines,
           "\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
           "\\parbox{\\textwidth}{\\footnotesize A negative value means that C-PR ranks the label below the other score. The "
           "counts are taken on the contract graph at the freeze. "
           "$^{a}$The two contrasts of rule~A. $^{b}$F6a, F1 and F2 of the registration of W1. $^{s}$F1 and F2 of its first "
           "sensitivity analysis. These rules were fixed for the registered analysis and are applied here to the scores of the "
           "contract graph, as a re-analysis. The contrasts with the union in-degree belong to the definition of the main "
           "analysis and to no rule; every other cell was computed after the labels were known and belongs to no rule. No cell is "
           "a registered result. The lower block repeats two rows on the spenders that AWP can order, a restriction also chosen "
           "after the results were known. Within a cohort every cell uses the same 400 resamples (seed 42).}",
           "\\end{table*}", ""]
    return "\n".join(out)


def tab_union(D: dict) -> str:
    """The rule contrasts and the union in-degree contrasts on the whole cohorts, inside the union graph and with the
    uncapped authorization layer (main analysis)."""
    V = D["main"]
    w0, w1, unc = V["w0"], V["w1"], V["rob"]["uncapped_allowances"]
    u0, u1, x0, x1 = w0["in_union_graph"], w1["in_union_graph"], unc["w0"], unc["w1"]
    if x0["spenders"] != w0["spenders"] or x1["spenders"] != w1["spenders"]:
        raise SystemExit("the uncapped sensitivity is not on the spender cohorts of the main analysis")
    UN0, UN1 = "t1_in_degree_union", "in_degree_union"

    def find0(d: dict, b: str, o: str) -> dict:
        for key in ("contrasts_prefixed", "contrasts_after", "baseline_contrasts"):
            for r in d.get(key) or []:
                if r["a"] == "cpr_l50" and r["b"] == b and r["outcome"] == o:
                    return r
        raise SystemExit(f"no W0 contrast of C-PR with {b} on {o}")

    rb, bc = w1["rule_b"], w1["baseline_contrasts"]
    c1, cx = u1["contrasts"], x1["contrasts"]
    rows = [
        ("W0, A1: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs",
         find0(w0, "cpr_l100", APPR), find0(u0, "cpr_l100", APPR), find0(x0, "cpr_l100", APPR)),
        ("W0, A2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders",
         find0(w0, "cpr_l0", SEND), find0(u0, "cpr_l0", SEND), find0(x0, "cpr_l0", SEND)),
        ("W0: C-PR $-$ union in-degree, new approval pairs", find0(w0, UN0, APPR), find0(u0, UN0, APPR), find0(x0, UN0, APPR)),
        ("W0: C-PR $-$ union in-degree, new transfer senders", find0(w0, UN0, SEND), find0(u0, UN0, SEND), find0(x0, UN0, SEND)),
        None,
        ("W1, F1: C-PR $-$ C-PR ($\\lambda=0$), new approval pairs", rb["F1"], c1["cpr_minus_cpr_l0_appr"], cx["cpr_minus_cpr_l0_appr"]),
        ("W1, F2: C-PR $-$ C-PR ($\\lambda=0$), new transfer senders", rb["F2"], c1["cpr_minus_cpr_l0_send"], cx["cpr_minus_cpr_l0_send"]),
        ("W1, F6a: C-PR $-$ C-PR ($\\lambda=1$), new approval pairs", rb["F6a"], c1["cpr_minus_cpr_l100_appr"], cx["cpr_minus_cpr_l100_appr"]),
        ("W1: C-PR $-$ union in-degree, new approval pairs", bc["cpr_minus_union_in_degree_appr"],
         c1["cpr_minus_union_in_degree_appr"], cx["cpr_minus_union_in_degree_appr"]),
        ("W1: C-PR $-$ union in-degree, new transfer senders", bc["cpr_minus_union_in_degree_send"],
         c1["cpr_minus_union_in_degree_send"], cx["cpr_minus_union_in_degree_send"]),
    ]

    def taus(r: dict) -> str:
        return f"{{\\scriptsize {f3(r['a_tau'])}, {f3(r['b_tau'])}}}"

    lines = []
    for item in rows:
        if item is None:
            lines.append("\\midrule")
            continue
        label, full, inside, uncapped = item
        lines.append(f"{label} & {delta_cell(full)} & {delta_cell(inside)} & {delta_cell(uncapped)} \\\\")
        if label.startswith(("W0, A1", "W1, F6a")):  # the two contrasts whose reading moves: show both coefficients
            lines.append(f"\\quad{{\\scriptsize $\\tau_a$, $\\tau_b$}} & {taus(full)} & {taus(inside)} & {taus(uncapped)} \\\\")
    p0, p1 = x0["allowance_pairs"], x1["allowance_pairs"]
    out = [header([f"{REVISED}/holdout-w0/eval_summary.json : contrasts_prefixed, baseline_contrasts, in_union_graph",
                   f"{REVISED}/window-w1/eval_summary.json : rule_b, baseline_contrasts, in_union_graph",
                   f"{REVISED}/robustness/robustness.json : uncapped_allowances"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{The Contrasts of the Rules and of C-PR With the Union In-Degree in Three Settings of the Main Analysis: "
           "$\\Delta\\tau$ [95\\% CI]}",
           "\\label{tab:union}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{3pt}",
           "\\begin{tabular}{@{}lccc@{}}",
           "\\toprule",
           "Contrast ($a$ minus $b$) and label & Whole spender cohort & Spenders inside the union graph & "
           "Whole cohort, no balance cap \\\\",
           "\\midrule",
           *lines,
           "\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
           "\\parbox{\\textwidth}{\\footnotesize Left: the main analysis, as in Tables~\\ref{tab:contrasts} and~\\ref{tab:cpr} "
           f"(W0 $n={n(w0['spenders'])}$, W1 $n={n(w1['spenders'])}$). Middle: the same scores on the spenders that end a pair "
           f"between two different contracts ({n(u0['n'])} in W0 and {n(u1['n'])} in W1), with a bootstrap of that subset; a spender "
           "outside the union graph scores zero under every score and count, so on the whole cohort a contrast also reflects "
           "how the two scores order the spenders with a pair against those without one. Right: scores and the union in-degree "
           "recomputed with every positive latest allowance between contracts counted at its own value, which gives "
           f"{n(p0['uncapped'])} authorization pairs at the W0 freeze where the cap leaves {n(p0['capped'])}, and {n(p1['uncapped'])} "
           f"where it leaves {n(p1['capped'])} at the W1 freeze. Under the two contrasts with the authorization walk, "
           "whose reading differs between the settings, the small figures give the two coefficients. The middle and right "
           "columns decide no rule. "
           "Intervals: 400 paired resamples, seed 42.}",
           "\\end{table*}", ""]
    return "\n".join(out)


def tab_sybil(D: dict) -> str:
    S = D["main"]["sybil"]
    th = S["balance_threshold"]
    cols = [("None", S, None)] + [(f"\\${int(float(k))}", th[k], k) for k in sorted(th, key=float)]
    farm, gas = S["contract_farm"], S["contract_farm"]["evm_gas"]
    m = S["star"]["m"]

    def cells(fn) -> str:
        return " & ".join(fn(x, k) for _, x, k in cols)

    def reach(x: dict) -> int:
        return math.ceil(x["farm_size_to_reach_cohort_quantile"]["p100"]["farm_addresses"])

    lines = [
        "Authorization pairs kept & " + cells(lambda x, k: n(x["graph"]["edges"])) + " \\\\",
        "\\quad share of the pairs & " + cells(lambda x, k: "100\\%" if k is None else pct(x["share_of_pairs_kept"])) + " \\\\",
        "Owner contracts & " + cells(lambda x, k: n(x["owners"] if k is None else x["owners_kept"])) + " \\\\",
        "Nodes of the graph & " + cells(lambda x, k: n(x["graph"]["nodes"])) + " \\\\",
        "Cohort contracts with a positive score & "
        + cells(lambda x, k: n(S["cohort"]["with_positive_score"] if k is None else x["cohort_with_positive_score"])) + " \\\\",
        "$\\tau_b$ of the cohort's scores with the main ones & "
        + cells(lambda x, k: "1" if k is None else f3(x["cohort_tau_with_main"])) + " \\\\",
        "Dangling mass $r_D$ & " + cells(lambda x, k: f3(x["r_D"])) + " \\\\",
        "\\midrule",
        f"Target of a star of {m}: share of the cohort's highest score & " + cells(lambda x, k: f3(x["star"]["ratio_to_highest"])) + " \\\\",
        "Farm contracts that reach the cohort's highest score & " + cells(lambda x, k: n(reach(x))) + " \\\\",
        f"Balance the {m + 1} contracts of the star hold (USD) & "
        + cells(lambda x, k: "---" if k is None else n(x["star_balance_usd"])) + " \\\\",
    ]
    if S["graph"]["edges"] != D["main"]["same"]["graph"]["allowance"]["edges"]:
        raise SystemExit("the Sybil model is not on the EndorseRank graph of the same-window summary")
    out = [header([f"{REVISED}/sybil-model/sybil_model.json : graph, owners, cohort, r_D, star, "
                   "farm_size_to_reach_cohort_quantile, balance_threshold, contract_farm"]),
           "\\begin{table}[!t]",
           "\\centering",
           "\\caption{Farms of Contracts on the Authorization Graph at the Freeze of 30 June 2026, Without and With a Balance "
           "Threshold $\\theta$}",
           "\\label{tab:sybil}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{2.5pt}",
           "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.43\\columnwidth}rrrr@{}}",
           "\\toprule",
           "Threshold $\\theta$ & " + " & ".join(c for c, _, _ in cols) + " \\\\",
           "\\midrule",
           *lines,
           "\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
           "\\parbox{\\columnwidth}{\\footnotesize EndorseRank graph of contracts in the main analysis. With a threshold the graph "
           "keeps only the pairs whose capped value is at least $\\theta$, so every farm contract that approves must hold $\\theta$ "
           "of a token at the freeze. A farm address is a contract: its creation costs at least "
           f"{n(gas['creation_by_create_at_least'])} gas from a factory and {n(gas['creation_by_transaction_at_least'])} gas by a "
           f"transaction of its own, plus {n(gas['G_codedeposit_per_byte'])} gas per byte of code (execution gas, without the fee "
           "for posting data to Ethereum). The farm sizes come from the closed form (\\ref{eq:star}) and count the farm contracts "
           "beside the target. Computed after the W1 labels were known; the model decides no rule.}",
           "\\end{table}", ""]
    return "\n".join(out)


def tab_explore(D: dict) -> str:
    E = D["explore"]
    names = (("main", "Contract-graph analysis"), ("registered", "Registered analysis"))
    for name, _ in names:
        for k in ("A1", "A2", "F1", "F2"):
            pubd = E["recompute"][name][k]
            if pubd["max_abs_diff_from_published"] > 1e-9:
                raise SystemExit(f"exploratory checks: {name} {k} does not reproduce the published value")
    out = [header(["supplement/exploratory_checks.json (script supplement/exploratory_checks.py)"]),
           "\\begin{table*}[!t]",
           "\\centering",
           "\\caption{Exploratory Checks, Computed After Every Result of Both Analyses Was Known}",
           "\\label{tab:explore}",
           "\\footnotesize",
           "\\setlength{\\tabcolsep}{2.4pt}",
           "\\begin{tabular}{@{}llcc@{}}",
           "\\toprule",
           " & & Contract-graph analysis (main) & Registered analysis \\\\"]
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(a) Rule contrasts under 50 further seeds of 400 resamples: interval end, mean (SD) [range]; "
            "seeds with another verdict than seed 42}} \\\\"]
    lab = [("A1", "A1, W0, new approval pairs", "ci_high", "upper end"), ("A2", "A2, W0, new transfer senders", "ci_low", "lower end"),
           ("F1", "F1, W1, new approval pairs", "ci_low", "lower end"), ("F2", "F2, W1, new transfer senders", "ci_low", "lower end"),
           ("F2", "", "ci_high", "upper end")]
    for k, text, end, endname in lab:
        cells = []
        for name, _ in names:
            s = E["seed_spread"][name][k]
            tail = (f"{s['seeds_interval_beyond_margin']} of {s['seeds']}$^{{\\dagger}}$" if (k, end) == ("F2", "ci_high")
                    else f"{s['seeds_with_other_verdict']} of {s['seeds']}")
            cells.append(f"{f4(s[end + '_mean'])} ({s[end + '_sd']:.4f}) [{f4(s[end + '_min'])}, {f4(s[end + '_max'])}]; {tail}")
        out.append(f"{text} & {endname} & " + " & ".join(cells) + " \\\\")
    for k, text in (("union:A1", "A1 in the union graph, W0"), ("union:F6a", "F6a in the union graph, W1")):
        s = E["seed_spread"]["main"][k]
        out.append(f"{text} & lower end & {f4(s['ci_low_mean'])} ({s['ci_low_sd']:.4f}) [{f4(s['ci_low_min'])}, {f4(s['ci_low_max'])}]; "
                   f"{s['seeds_interval_contains_zero']} of {s['seeds']}$^{{\\ddagger}}$ & --- \\\\")
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(b) Steps of the weight: $\\tau_b$ of C-PR at the higher $\\lambda$ minus at the lower one, paired, 400 resamples, seed 42}} \\\\"]
    cohorts = [("w0_spenders", APPR, "W0, new approval pairs"), ("w0_spenders", SEND, "W0, new transfer senders"),
               ("w1_spenders", APPR, "W1, new approval pairs"), ("w1_spenders", SEND, "W1, new transfer senders")]
    steps = [("0.25-0.0", "$0\\to0.25$"), ("0.75-0.25", "$0.25\\to0.75$"), ("1.0-0.75", "$0.75\\to1$")]
    for c, l, text in cohorts:
        for i, (key, st) in enumerate(steps):
            cells = [delta_cell(E["lambda_steps"][name][f"{c}:{l}"][key]) for name, _ in names]
            out.append(f"{text if i == 0 else ''} & {st} & " + " & ".join(cells) + " \\\\")
    out += ["\\midrule",
            "\\multicolumn{4}{@{}l}{\\emph{(c) Rank agreement: $\\tau_b$ between the C-PR scores at two values of $\\lambda$ over the cohort, 400 resamples, seed 42}} \\\\"]
    coh = [("same_window", "Matched cohort"), ("w0_spenders", "W0 spenders"), ("w1_spenders", "W1 spenders")]
    pairs = [("0.0-0.25", "$\\lambda=0$ and $0.25$"), ("0.25-0.75", "$\\lambda=0.25$ and $0.75$"), ("0.75-1.0", "$\\lambda=0.75$ and $1$")]
    for c, text in coh:
        for i, (key, pl) in enumerate(pairs):
            cells = []
            for name, _ in names:
                e = E["lambda_rank_agreement"][name][c][key]
                cells.append(f"{f3(e['tau_b'])} [{f3(e['ci_low'])}, {f3(e['ci_high'])}]")
            out.append(f"{text if i == 0 else ''} & {pl} & " + " & ".join(cells) + " \\\\")
    out += ["\\bottomrule", "\\end{tabular}", "", "\\vspace{2pt}",
            "\\parbox{\\textwidth}{\\footnotesize Computed from the per-contract score files of the pipeline after every result of "
            "both analyses was known; no row enters a rule and none is a registered result. The script first recomputes the "
            "contrasts of Table~\\ref{tab:contrasts} except those of S2, the contrasts of C-PR with the union in-degree and "
            "those inside the union graph (Table~\\ref{tab:union}), and reproduces the published values exactly. In (a) the A1 "
            "row reports the upper end, which decides ``no worse''. $^{\\dagger}$Seeds in which the whole F2 interval lies "
            "beyond the margin $-0.01$. $^{\\ddagger}$Seeds in which the interval contains zero, on the spenders inside the "
            "union graph.}",
            "\\end{table*}", ""]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS"),
                    help="checkout of the public repository (or set CONTRACT_REP_REPO)")
    args = ap.parse_args()
    if not args.repo:
        raise SystemExit("pass --repo PATH or set CONTRACT_REP_REPO")
    repo = locate(Path(args.repo).resolve())
    D = load(repo)
    check_verdicts(D)
    tables = {
        "tab_bench.tex": tab_bench(D),
        "tab_timeline.tex": tab_timeline(repo, D),
        "tab_ids.tex": tab_ids(repo, D),
        "tab_graph.tex": tab_graph(D),
        "tab_cohorts.tex": tab_cohorts(D),
        "tab_holdout.tex": tab_holdout(D),
        "tab_contrasts.tex": tab_contrasts(D),
        "tab_cpr.tex": tab_cpr(D),
        "tab_union.tex": tab_union(D),
        "tab_sybil.tex": tab_sybil(D),
        "tab_explore.tex": tab_explore(D),
    }
    for name, text in tables.items():
        (HERE / name).write_text(text, encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
