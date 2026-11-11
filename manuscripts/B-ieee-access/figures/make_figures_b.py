#!/usr/bin/env python3
"""Figures 2 and 3 of Manuscript B (static vector PDFs for print).

Fig. 2  fig_contrasts.pdf     Forest plot of the contrasts of rule A, of the two criteria of rule B
                              that the paper applies (F1, F2), of F6 and of the two sensitivity
                              analyses, in both analyses.
Fig. 3  fig_lambda_sweep.pdf  Kendall tau_b of C-PR against the authorization weight lambda, with
                              95% intervals, for both analyses and both spender cohorts; in the
                              main analysis the union in-degree is drawn beside it.

Both figures are 7.16 in wide and are scaled to the text width (about 0.98), so every text size
below is at least 8.2 pt in the figure and prints at 8 pt or more. The serif list puts a Times
face first, falling back to Liberation Serif (metric-compatible with Times New Roman; a TrueType
font, so it embeds cleanly with pdf.fonttype 42) and then to TeX Gyre Termes.

Every value is read from the published evaluation summaries of the experiment pipeline in the
public repository https://github.com/abitocodes/ERC20-Allowance-PageRank-Wallet-Reputation
(experiments/data/3-published-results-for-thesis/ for the registered analysis, its subfolder
revised-contract-12m/ for the contract-graph analysis, the main analysis of the paper); nothing
is typed in by hand.

    python make_figures_b.py --repo /path/to/ERC20-Allowance-PageRank-Wallet-Reputation   # or set CONTRACT_REP_REPO

A checkout of the authors' repository, which holds the public one as a submodule, also works.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent
PROJECTS = ("ERC20-Allowance-PageRank-Wallet-Reputation", "ERC20-Allowance-PageRank-Contract-Reputation")
MAIN = "revised-contract-12m"  # folder of the contract-graph analysis, the main analysis of the paper
DELTA = 0.01  # registered margin of rule B (docs/registration_w1.md)

FS = 8.2  # smallest text size in the figure (pt); prints at about 8 pt after scaling to the text width
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
S1, S2 = "#2a78d6", "#eb6834"  # categorical slots 1-2, validated as a pair (light)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "Liberation Serif", "TeX Gyre Termes", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": FS, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "legend.frameon": False,
    "pdf.fonttype": 42,
})

APPR, SEND = "future_new_approvers", "future_new_transfer_senders"
LAM = [0.0, 0.25, 0.5, 0.75, 1.0]
COL = {0.0: "cpr_l0", 0.25: "cpr_l25", 0.5: "cpr_l50", 0.75: "cpr_l75", 1.0: "cpr_l100"}
STYLE = {APPR: (S1, "o", "New approval pairs"), SEND: (S2, "s", "New transfer senders")}
UNION = {"w0": "t1_in_degree_union", "w1": "in_degree_union"}  # the count of the edges C-PR walks (main analysis)


def published_dirs(repo: Path) -> dict[str, Path]:
    """Published results in a checkout of the public repository, or in the authors' repository that holds it."""
    for exp in [repo / "experiments"] + [repo / "1-Dissertation-Works" / p / "experiments" for p in PROJECTS]:
        pub = exp / "data" / "3-published-results-for-thesis"
        if (pub / MAIN / "results_digest.md").exists():
            return {"main": pub / MAIN, "registered": pub}
    raise SystemExit(f"no published results of {MAIN} under {repo}")


def load(pub: dict[str, Path]) -> dict:
    out = {}
    for name, d in pub.items():
        w1 = "registered-w1" if name == "registered" else "window-w1"
        out[name] = {
            "w0": json.loads((d / "holdout-w0" / "eval_summary.json").read_text(encoding="utf-8")),
            "w1": json.loads((d / w1 / "eval_summary.json").read_text(encoding="utf-8")),
        }
    return out


def sweep(S: dict) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.16, 4.7), sharey="row")
    rows = [("main", "Contract-graph analysis (main analysis, a re-analysis; contracts only, US dollars, five tokens, twelve-month windows)"),
            ("registered", "Registered analysis (the test the rules were fixed for; raw base units, every ERC-20 token, all accounts)")]
    cols = [("W0 spenders (scores 31 March 2026, labels April–June)", "w0", "taus"),
            ("W1 spenders (scores 30 June 2026, labels July–September)", "w1", "spender_taus")]
    for r, (name, rtitle) in enumerate(rows):
        for c, (ctitle, win, block) in enumerate(cols):
            ax = axes[r, c]
            src = S[name][win][block]
            for lab in (APPR, SEND):
                col, mk, _ = STYLE[lab]
                if name == "main":  # the union in-degree, a count, drawn across the panel
                    u = src[UNION[win]][lab]["kendall_tau"]
                    ax.plot([-0.08, 1.08], [u, u], color=col, lw=0.9, ls=(0, (1, 1.6)), zorder=1)
                pts = []
                for lam in LAM:
                    e = src[COL[lam]][lab]
                    pts.append((lam, e["kendall_tau"], e["ci_low"], e["ci_high"]))
                inner = [p for p in pts if 0 < p[0] < 1]
                ax.plot([p[0] for p in inner], [p[1] for p in inner], "-", color=col, lw=1.4, zorder=2)
                for lam, t, lo, hi in pts:
                    interior = 0 < lam < 1
                    ax.plot([lam, lam], [lo, hi], color=col, lw=1.0, zorder=2)
                    ax.plot([lam], [t], mk, ms=4.6, color=col if interior else "white", mec=col, mew=1.1, zorder=4)
            ax.axvspan(-0.04, 0.04, color=GRID, alpha=0.35, lw=0, zorder=0)
            ax.axvspan(0.96, 1.04, color=GRID, alpha=0.35, lw=0, zorder=0)
            ax.set_xticks(LAM)
            ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
            ax.set_xlim(-0.08, 1.08)
            ax.grid(axis="y", color=GRID, lw=0.5)
            ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            if r == 0:
                ax.set_title(ctitle, fontsize=FS, color=INK, loc="left")
            if c == 0:
                ax.set_ylabel(r"Kendall $\tau_b$")
    for ax in axes[1]:
        ax.set_xlabel(r"weight $\lambda$ on the authorization layer", fontsize=FS)
    handles = [Line2D([0], [0], color=STYLE[k][0], marker=STYLE[k][1], lw=1.4, ms=4.6, label=STYLE[k][2])
               for k in (APPR, SEND)]
    handles.append(Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.6, mfc="white", mec=INK2,
                          label=r"$\lambda=0$ or $1$: one layer walked alone"))
    handles.append(Line2D([0], [0], color=INK2, lw=0.9, ls=(0, (1, 1.6)),
                          label="dotted: union in-degree (top row)"))
    fig.legend(handles=handles, loc="upper center", ncol=4, fontsize=FS, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.8, columnspacing=1.0)
    fig.subplots_adjust(left=0.075, right=0.99, top=0.855, bottom=0.09, hspace=0.62, wspace=0.08)
    for r, (_, rtitle) in enumerate(rows):
        box = axes[r, 0].get_position()
        fig.text(box.x0 - 0.06, box.y1 + (0.058 if r == 0 else 0.045), rtitle, fontsize=FS + 0.2, color=INK,
                 fontweight="bold", va="bottom", ha="left")
    fig.savefig(HERE / "fig_lambda_sweep.pdf")
    plt.close(fig)


def _w0(a: str, b: str, outcome: str):
    def get(d: dict) -> dict:
        return next(r for r in d["w0"]["contrasts_prefixed"] if r["a"] == a and r["b"] == b and r["outcome"] == outcome)
    return get


def _w1(block: str, key: str):
    return lambda d: d["w1"][block][key]


# (group, [(label, getter of the contrast, test)])
ROWS = [
    ("Rule A, primary part (plan, 13:41:27 UTC); W0", [
        ("A1  C-PR − C-PR(1) · new approval pairs", _w0("cpr_l50", "cpr_l100", APPR), "no worse"),
        ("A2  C-PR − C-PR(0) · new transfer senders", _w0("cpr_l50", "cpr_l0", SEND), "superiority"),
    ]),
    ("Rule B (registration, 16:49:32 UTC); W1; its criteria F1 and F2", [
        ("F1  C-PR − C-PR(0) · new approval pairs", _w1("rule_b", "F1"), "superiority"),
        ("F2  C-PR − C-PR(0) · new transfer senders", _w1("rule_b", "F2"), "non-inferiority"),
    ]),
    ("F6, rule A on W1, reported beside rule B (nominal)", [
        ("F6a C-PR − C-PR(1) · new approval pairs", _w1("rule_b", "F6a"), "no worse"),
        ("F6b C-PR − C-PR(0) · new transfer senders", _w1("rule_b", "F6b"), "superiority"),
    ]),
    ("Sensitivity 1: AWP as comparator (nominal)", [
        ("F1  C-PR − AWP · new approval pairs", _w1("sensitivity_awp", "F1"), "superiority"),
        ("F2  C-PR − AWP · new transfer senders", _w1("sensitivity_awp", "F2"), "non-inferiority"),
    ]),
    ("Sensitivity 2: contracts outside a graph as isolated nodes (nominal)", [
        ("F1  C-PR − C-PR(0) · new approval pairs", _w1("sensitivity_isolated", "F1"), "superiority"),
        ("F2  C-PR − C-PR(0) · new transfer senders", _w1("sensitivity_isolated", "F2"), "non-inferiority"),
        ("F6a C-PR − C-PR(1) · new approval pairs", _w1("sensitivity_isolated", "F6a"), "no worse"),
        ("F6b C-PR − C-PR(0) · new transfer senders", _w1("sensitivity_isolated", "F6b"), "superiority"),
    ]),
]
XMIN, XMAX = -0.11, 0.13


def holds(e: dict, test: str) -> bool:
    if test == "superiority":
        ok = e["ci_low"] > 0
    elif test == "non-inferiority":
        ok = e["ci_low"] > -DELTA
    else:  # no worse
        ok = e["ci_high"] >= 0
    if "holds" in e and bool(e["holds"]) != ok:
        raise SystemExit("a published verdict does not follow from its interval")
    return ok


def forest(S: dict) -> None:
    n = sum(len(r) for _, r in ROWS) + len(ROWS)
    fig, ax = plt.subplots(figsize=(7.16, 0.235 * n + 0.85))
    y = n
    tf = ax.get_yaxis_transform()
    offs = {"main": (+0.17, S1, "o"), "registered": (-0.17, S2, "s")}  # the main analysis on top
    headers = []
    for group, rows in ROWS:
        y -= 1
        headers.append((y, group))  # drawn at the left edge of the figure once the layout is fixed
        for lab, get, test in rows:
            y -= 1
            ax.text(-0.01, y, lab, transform=tf, fontsize=FS, color=INK, va="center", ha="right")
            for name, (dy, col, mk) in offs.items():
                e = get(S[name])
                d, lo, hi = e["delta_tau"], e["ci_low"], e["ci_high"]
                if lo < XMIN or hi > XMAX:
                    raise SystemExit(f"{lab}: interval outside the plotted range")
                yy = y + dy
                ax.plot([lo, hi], [yy, yy], color=col, lw=1.3, solid_capstyle="butt", zorder=2)
                ok = holds(e, test)
                ax.plot([d], [yy], mk, ms=4.3, color=col if ok else "white", mec=col, mew=1.1, zorder=4)
            ax.text(1.01, y, test, transform=tf, fontsize=FS, color=INK2, va="center", ha="left")
    ax.axvline(0, color=INK2, lw=0.7, zorder=1)
    ax.axvline(-DELTA, color=INK2, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.set_yticks([])
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlim(XMIN, XMAX)
    ticks = [-0.10, -0.05, 0, 0.05, 0.10]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["−0.10", "−0.05", "0", "0.05", "0.10"])
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel(r"$\Delta\tau_b$ with 95% paired-bootstrap interval; dashed line: margin $-\delta=-0.01$", fontsize=FS)
    handles = [
        Line2D([0], [0], color=S1, marker="o", lw=1.3, ms=4.3, label="contract-graph analysis (main; re-analysis)"),
        Line2D([0], [0], color=S2, marker="s", lw=1.3, ms=4.3, label="registered analysis (the registered test)"),
        Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.3, mfc=INK2, mec=INK2, label="filled: criterion met"),
        Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.3, mfc="white", mec=INK2, label="open: not met"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=4, fontsize=FS,
               handlelength=1.4, columnspacing=0.9)
    fig.subplots_adjust(left=0.40, right=0.885, top=0.94, bottom=0.095)
    for yh, group in headers:  # group headers start at the left edge of the figure
        _, ydisp = ax.transData.transform((0, yh))
        _, yfig = fig.transFigure.inverted().transform((0, ydisp))
        fig.text(0.008, yfig, group, fontsize=FS, color=INK, fontweight="bold", va="center", ha="left")
    fig.savefig(HERE / "fig_contrasts.pdf")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.environ.get("CONTRACT_REP_REPO") or os.environ.get("PHD_WORKS"),
                    help="checkout of the public repository (or set CONTRACT_REP_REPO)")
    args = ap.parse_args()
    if not args.repo:
        raise SystemExit("pass --repo PATH or set CONTRACT_REP_REPO")
    S = load(published_dirs(Path(args.repo).resolve()))
    sweep(S)
    forest(S)
    print("ok")


if __name__ == "__main__":
    main()
