#!/usr/bin/env python3
"""Figures 2 and 3 of Manuscript B (static vector PDFs for print).

Fig. 2  fig_contrasts.pdf     Forest plot of the contrasts of rules A and B, of the results reported
                              beside rule B and of its two sensitivity analyses, both analyses.
Fig. 3  fig_lambda_sweep.pdf  Kendall tau_b of C-PR against the authorization weight lambda,
                              with 95% intervals, for both analyses and three cohort-label panels.

Both figures are 7.16 in wide and are scaled to the text width (about 0.98), so every text size
below is at least 8.2 pt in the figure and prints at 8 pt or more. The serif list puts a Times
face first, falling back to Liberation Serif (metric-compatible with Times New Roman; a TrueType
font, so it embeds cleanly with pdf.fonttype 42) and then to TeX Gyre Termes.

Every value is read from the published evaluation summaries of the experiment pipeline in the
authors' repository phd_works (data/3-published-results-for-thesis/ for the registered analysis,
its subfolder revised-usd-12m/ for the revised analysis); nothing is typed in by hand.

    python make_figures_b.py --phd-works /path/to/phd_works      # or set PHD_WORKS
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
DELTA = 0.01  # registered margin of rule B (docs/registration_w1.md)

FS = 8.2  # smallest text size in the figure (pt); prints at about 8 pt after scaling to the text width
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1-3, validated all-pairs (light)
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "Liberation Serif", "TeX Gyre Termes", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": FS, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "legend.frameon": False,
    "pdf.fonttype": 42,
})

APPR, SEND, LIQ = "future_new_approvers", "future_new_transfer_senders", "liquidation_free_rate"
LAM = [0.0, 0.25, 0.5, 0.75, 1.0]
COL = {0.0: "cpr_l0", 0.25: "cpr_l25", 0.5: "cpr_l50", 0.75: "cpr_l75", 1.0: "cpr_l100"}
STYLE = {APPR: (S1, "o", "New approval pairs"), SEND: (S2, "s", "New transfer senders"),
         LIQ: (S3, "^", "Liquidation-free close rate")}


def published_dirs(phd_works: Path) -> dict[str, Path]:
    for p in PROJECTS:
        pub = phd_works / "1-Dissertation-Works" / p / "experiments" / "data" / "3-published-results-for-thesis"
        if (pub / "results_digest.md").exists():
            return {"registered": pub, "revised": pub / "revised-usd-12m"}
    raise SystemExit(f"no published results under {phd_works}")


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
    fig, axes = plt.subplots(2, 3, figsize=(7.16, 4.7), sharey="row")
    rows = [("revised", "Revised analysis (main analysis, a re-analysis; US dollars, five tokens, twelve-month score windows)"),
            ("registered", "Registered analysis (the pre-specified test; raw base units, every ERC-20)")]
    cols = [("W0 spenders (labels Apr–Jun)", "w0", "taus", [APPR, SEND]),
            ("W1 spenders (labels Jul–Sep)", "w1", "spender_taus", [APPR, SEND]),
            ("W1 traders (labels Jul–Sep)", "w1", "trader_taus", [LIQ])]
    for r, (name, rtitle) in enumerate(rows):
        for c, (ctitle, win, block, labels) in enumerate(cols):
            ax = axes[r, c]
            src = S[name][win][block]
            for lab in labels:
                col, mk, _ = STYLE[lab]
                pts = []
                for lam in LAM:
                    e = src[COL[lam]][lab] if lab != LIQ else src[COL[lam]]
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
               for k in (APPR, SEND, LIQ)]
    handles.append(Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.6, mfc="white", mec=INK2,
                          label=r"$\lambda=0$ or $1$: one layer walked alone"))
    fig.legend(handles=handles, loc="upper center", ncol=4, fontsize=FS, bbox_to_anchor=(0.5, 1.0),
               handlelength=1.6, columnspacing=1.0)
    fig.subplots_adjust(left=0.075, right=0.99, top=0.855, bottom=0.09, hspace=0.62, wspace=0.10)
    for r, (_, rtitle) in enumerate(rows):
        box = axes[r, 0].get_position()
        fig.text(box.x0 - 0.06, box.y1 + (0.058 if r == 0 else 0.045), rtitle, fontsize=FS + 0.2, color=INK,
                 fontweight="bold", va="bottom", ha="left")
    fig.savefig(HERE / "fig_lambda_sweep.pdf")
    plt.close(fig)


# (group, label, block path, test)
ROWS = [
    ("Rule A, primary part (plan, 13:41:27 UTC); W0", [
        ("A1  C-PR − C-PR(1) · new approval pairs", ("w0", "contrasts_prefixed", 0), "no worse"),
        ("A2  C-PR − C-PR(0) · new transfer senders", ("w0", "contrasts_prefixed", 1), "superiority"),
    ]),
    ("Rule B (registration, 16:49:32 UTC); W1; all three required", [
        ("F1  C-PR − C-PR(0) · new approval pairs", ("w1", "rule_b", "F1"), "superiority"),
        ("F2  C-PR − C-PR(0) · new transfer senders", ("w1", "rule_b", "F2"), "non-inferiority"),
        ("F3  C-PR − C-PR(0) · liquidation-free rate", ("w1", "rule_b", "F3"), "non-inferiority"),
    ]),
    ("Reported beside rule B (nominal)", [
        ("F4  as F3, superiority", ("w1", "rule_b", "F4"), "superiority"),
        ("F5  C-PR − C-PR(1) · liquidation-free rate", ("w1", "rule_b", "F5"), "superiority"),
        ("F6a C-PR − C-PR(1) · new approval pairs", ("w1", "rule_b", "F6a"), "no worse"),
        ("F6b C-PR − C-PR(0) · new transfer senders", ("w1", "rule_b", "F6b"), "superiority"),
    ]),
    ("Sensitivity 1: AWP as comparator (nominal)", [
        ("F1  C-PR − AWP · new approval pairs", ("w1", "sensitivity_awp", "F1"), "superiority"),
        ("F2  C-PR − AWP · new transfer senders", ("w1", "sensitivity_awp", "F2"), "non-inferiority"),
        ("F3  C-PR − AWP · liquidation-free rate", ("w1", "sensitivity_awp", "F3"), "non-inferiority"),
    ]),
    ("Sensitivity 2: contracts outside a graph as isolated nodes (nominal)", [
        ("F1  C-PR − C-PR(0) · new approval pairs", ("w1", "sensitivity_isolated", "F1"), "superiority"),
        ("F2  C-PR − C-PR(0) · new transfer senders", ("w1", "sensitivity_isolated", "F2"), "non-inferiority"),
        ("F3  C-PR − C-PR(0) · liquidation-free rate", ("w1", "sensitivity_isolated", "F3"), "non-inferiority"),
        ("F5  C-PR − C-PR(1) · liquidation-free rate", ("w1", "sensitivity_isolated", "F5"), "superiority"),
    ]),
]
XMIN, XMAX = -0.25, 0.20


def holds(e: dict, test: str) -> bool:
    if "holds" in e:
        return bool(e["holds"])
    if test == "superiority":
        return e["ci_low"] > 0
    if test == "non-inferiority":
        return e["ci_low"] > -DELTA
    return e["ci_high"] >= 0  # no worse


def forest(S: dict) -> None:
    n = sum(len(r) for _, r in ROWS) + len(ROWS)
    fig, ax = plt.subplots(figsize=(7.16, 0.235 * n + 0.85))
    y = n
    tf = ax.get_yaxis_transform()
    offs = {"revised": (+0.17, S1, "o"), "registered": (-0.17, S2, "s")}  # the main analysis on top
    headers = []
    for group, rows in ROWS:
        y -= 1
        headers.append((y, group))  # drawn at the left edge of the figure once the layout is fixed
        for lab, (win, block, key), test in rows:
            y -= 1
            ax.text(-0.01, y, lab, transform=tf, fontsize=FS, color=INK, va="center", ha="right")
            for name, (dy, col, mk) in offs.items():
                e = S[name][win][block][key]
                d, lo, hi = e["delta_tau"], e["ci_low"], e["ci_high"]
                yy = y + dy
                clo = lo if lo >= XMIN else XMIN + 0.016  # a clipped end becomes an arrowhead
                chi = hi if hi <= XMAX else XMAX - 0.016
                ax.plot([clo, chi], [yy, yy], color=col, lw=1.3, solid_capstyle="butt", zorder=2)
                if lo < XMIN:
                    ax.annotate("", xy=(XMIN, yy), xytext=(XMIN + 0.016, yy),
                                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0, mutation_scale=7, shrinkA=0, shrinkB=0), zorder=3)
                if hi > XMAX:
                    ax.annotate("", xy=(XMAX, yy), xytext=(XMAX - 0.016, yy),
                                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.0, mutation_scale=7, shrinkA=0, shrinkB=0), zorder=3)
                ok = holds(e, test)
                ax.plot([d], [yy], mk, ms=4.3, color=col if ok else "white", mec=col, mew=1.1, zorder=4)
            ax.text(1.01, y, test, transform=tf, fontsize=FS, color=INK2, va="center", ha="left")
    ax.axvline(0, color=INK2, lw=0.7, zorder=1)
    ax.axvline(-DELTA, color=INK2, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.set_yticks([])
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlim(XMIN, XMAX)
    ticks = [-0.2, -0.1, 0, 0.1, 0.2]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["−0.2", "−0.1", "0", "0.1", "0.2"])
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel(r"$\Delta\tau_b$ with 95% paired-bootstrap interval; dashed line: margin $-\delta=-0.01$", fontsize=FS)
    handles = [
        Line2D([0], [0], color=S1, marker="o", lw=1.3, ms=4.3, label="revised analysis (main; re-analysis)"),
        Line2D([0], [0], color=S2, marker="s", lw=1.3, ms=4.3, label="registered analysis (pre-specified test)"),
        Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.3, mfc=INK2, mec=INK2, label="filled: criterion met"),
        Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.3, mfc="white", mec=INK2, label="open: not met"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.0), ncol=4, fontsize=FS,
               handlelength=1.4, columnspacing=0.9)
    fig.subplots_adjust(left=0.40, right=0.885, top=0.95, bottom=0.075)
    for yh, group in headers:  # group headers start at the left edge of the figure
        _, ydisp = ax.transData.transform((0, yh))
        _, yfig = fig.transFigure.inverted().transform((0, ydisp))
        fig.text(0.008, yfig, group, fontsize=FS, color=INK, fontweight="bold", va="center", ha="left")
    fig.savefig(HERE / "fig_contrasts.pdf")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phd-works", default=os.environ.get("PHD_WORKS"))
    args = ap.parse_args()
    if not args.phd_works:
        raise SystemExit("pass --phd-works PATH or set PHD_WORKS")
    S = load(published_dirs(Path(args.phd_works).resolve()))
    sweep(S)
    forest(S)
    print("ok")


if __name__ == "__main__":
    main()
