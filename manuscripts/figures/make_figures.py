#!/usr/bin/env python3
"""Figures for the two journal manuscripts (static PDFs, light print mode).

Fig A1: allowance-side minus transfer-side, counts and PageRanks, six trader labels, two windows.
Fig B1: coupled PageRank coefficient against the allowance weight lambda, both windows.
Data: analysis/neutral-label/results.json and the published thesis tables (values copied below
with their table names).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R = json.loads((ROOT / "analysis/neutral-label/results.json").read_text())

INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#d9d8d4"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1-3 (validated all-pairs)

plt.rcParams.update({
    "font.family": "serif", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "legend.frameon": False,
})

LABELS = [
    ("future_liquidation_free_rate", "Liquidation-free close rate"),
    ("future_zero_liquidation", "No liquidation"),
    ("close_success_rate", "Profitable share"),
    ("non_loss_close_rate", "Non-loss share"),
    ("close_success_count", "Profitable closes*"),
    ("realized_gain_proxy", "Realized gain*"),
]
WINDOWS = [("W1_registered_jun_aug_2026", "Jun–Aug 2026 (registered window)", S1, -0.14),
           ("W0_spring_mar_may_2026", "Mar–May 2026 (spring window)", S2, 0.14)]


def fig_a1():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=True)
    for ax, (cid, title) in zip(axes, [("P", "(a) Counts: in-approve − transfer in-degree"),
                                       ("Q", "(b) PageRanks: EndorseRank* − AWP")]):
        for wkey, wname, col, off in WINDOWS:
            for i, (lab, _) in enumerate(LABELS):
                c = R["windows"][wkey]["plain"][lab]["contrasts"][cid]
                y = len(LABELS) - 1 - i + off
                lo, hi = c["ci95"]
                ax.plot([lo, hi], [y, y], color=col, lw=1.6, solid_capstyle="round", zorder=2)
                ax.plot([c["delta"]], [y], "o", ms=4.2, color=col, mec="white", mew=0.8, zorder=3,
                        label=wname if i == 0 else None)
        ax.axvline(0, color=INK2, lw=0.7, zorder=1)
        ax.set_xlim(-0.3, 0.36)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.supxlabel("Δτ (Kendall), allowance side minus transfer side, with 95% paired bootstrap interval", fontsize=8, color=INK)
    axes[0].set_yticks(range(len(LABELS)))
    axes[0].set_yticklabels([n for _, n in LABELS][::-1])
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, fontsize=7.5, bbox_to_anchor=(0.55, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(HERE / "fig_allowance_vs_transfer.pdf")


def fig_b1():
    lam = [0.0, 0.25, 0.5, 0.75, 1.0]
    # results/tables/holdout-spenders.tex (spring) and fresh-holdout.tex (registered)
    spring = {"New approval pairs": [0.044, 0.271, 0.295, 0.314, 0.479],
              "New transfer senders": [0.270, 0.266, 0.277, 0.287, 0.372]}
    reg = {"New approval pairs": [0.058, 0.228, 0.238, 0.243, 0.338],
           "New transfer senders": [0.257, 0.245, 0.246, 0.248, 0.289],
           "Liquidation-free close rate (traders)": [0.065, 0.077, 0.083, 0.086, 0.086]}
    colors = {"New approval pairs": S1, "New transfer senders": S2, "Liquidation-free close rate (traders)": S3}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
    for ax, (title, data) in zip(axes, [("Spring holdout (freeze 28 Feb 2026)", spring),
                                        ("Registered window (freeze 31 May 2026)", reg)]):
        for name, ys in data.items():
            ax.plot(lam, ys, "-o", color=colors[name], lw=1.6, ms=4.2, mec="white", mew=0.8, label=name)
            ax.text(1.03, ys[-1], name.replace(" (traders)", ""), color=INK2, fontsize=6.8, va="center")
        ax.set_xticks(lam)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_xlim(-0.05, 1.45)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("Kendall τ with the later label")
    fig.supxlabel("allowance weight λ in C-PR (0 = transfer layer alone, 1 = allowance layer alone)", fontsize=8, color=INK)
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=3, fontsize=7, bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(HERE / "fig_lambda_sweep.pdf")


if __name__ == "__main__":
    fig_a1()
    fig_b1()
    print("ok")
