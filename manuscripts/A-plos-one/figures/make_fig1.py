#!/usr/bin/env python3
"""Fig 1 of Manuscript A (PLOS ONE): allowance side minus transfer side on six trader labels.

Reads analysis/neutral-label/results.json (read only) and writes
figures/fig_allowance_vs_transfer.pdf next to this script. Convert to the upload TIFF with

    pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig_allowance_vs_transfer.pdf Fig1

PLOS figure rules: Arial-metric sans serif (Liberation Sans, falling back to Arial), 8-12 pt,
at most 7.5 in wide. This replaces fig_a1 of ../../figures/make_figures.py for Manuscript A only.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
R = json.loads((ROOT / "analysis/neutral-label/results.json").read_text())

INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#d9d8d4"
S1, S2 = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8.5,
    "axes.linewidth": 0.6, "legend.frameon": False, "pdf.fonttype": 42,
})

PRIMARY = "future_liquidation_free_rate"
LABELS = [
    (PRIMARY, "Liquidation-free close rate"),
    ("future_zero_liquidation", "No liquidation"),
    ("close_success_rate", "Profitable share"),
    ("non_loss_close_rate", "Non-loss share"),
    ("close_success_count", "Profitable closes*"),
    ("realized_gain_proxy", "Realized gain*"),
]
WINDOWS = [("W1_registered_jun_aug_2026", "Jun–Aug 2026 (W1)", S1, -0.14),
           ("W0_spring_mar_may_2026", "Mar–May 2026 (W0)", S2, 0.14)]
PANELS = [("P", "(a) Counts (contrast P):\nin-approve degree − transfer in-degree"),
          ("Q", "(b) PageRanks (contrast Q):\nEndorseRank (activity restarts) − AWP")]


def main() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5), sharey=True)
    for ax, (cid, title) in zip(axes, PANELS):
        for wkey, wname, col, off in WINDOWS:
            for i, (lab, _) in enumerate(LABELS):
                c = R["windows"][wkey]["plain"][lab]["contrasts"][cid]
                y = len(LABELS) - 1 - i + off
                lo, hi = c["ci95"]
                if lab == PRIMARY:
                    # 97.5% interval (Bonferroni level of the decision pair): thin line with end ticks
                    lo2, hi2 = c["ci975"]
                    ax.plot([lo2, hi2], [y, y], color=col, lw=0.7, zorder=2)
                    for xv in (lo2, hi2):
                        ax.plot([xv, xv], [y - 0.09, y + 0.09], color=col, lw=0.9, zorder=2)
                ax.plot([lo, hi], [y, y], color=col, lw=1.8, solid_capstyle="round", zorder=2)
                ax.plot([c["delta"]], [y], "o", ms=4.4, color=col, mec="white", mew=0.8, zorder=3,
                        label=wname if i == 0 else None)
        ax.axvline(0, color=INK2, lw=0.7, zorder=1)
        ax.set_xlim(-0.3, 0.36)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.supxlabel("Δτ (Kendall), allowance side minus transfer side; thick line: 95% interval; "
                  "end ticks (first row only): 97.5% interval", fontsize=8, color=INK)
    axes[0].set_yticks(range(len(LABELS)))
    axes[0].set_yticklabels([n for _, n in LABELS][::-1])
    h, lab = axes[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="upper center", ncol=2, fontsize=8, bbox_to_anchor=(0.55, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(HERE / "fig_allowance_vs_transfer.pdf")


if __name__ == "__main__":
    main()
    print("ok")
