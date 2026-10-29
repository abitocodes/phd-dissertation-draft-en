#!/usr/bin/env python3
"""Fig 1 of Manuscript A (PLOS ONE).

Panel A: each PageRank minus the raw degree it smooths, on the spender label of its own
edge type, in W0 and W1 (revised analysis, scores from the twelve months before each
freeze; 400 paired resamples).
Panels B and C: the registered trader contrasts P and Q on all six trader labels in
W1 and W0, applied to the revised scores (2,000 paired resamples).

Values are read from the published summaries in phd_works (checked against their
SHA256SUMS.txt) and from analysis/neutral-label/results.json; none is typed here.
Writes figures/fig1.pdf next to this script. Convert to the upload TIFF with

    pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig1.pdf Fig1

PLOS figure rules: Arial-metric sans serif (Liberation Sans), 8-12 pt, at most 7.5 in wide.

    PHD_WORKS=/path/to/phd_works python3 make_fig1.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import data_sources as S  # noqa: E402

INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#d9d8d4"
C_W1, C_W0 = "#2a78d6", "#eb6834"      # categorical slots 1-2 of the reference palette (validated)

def _installed(family: str) -> bool:
    try:
        font_manager.findfont(font_manager.FontProperties(family=family), fallback_to_default=False)
        return True
    except ValueError:
        return False


# Arial-metric face: Liberation Sans where installed (Linux), else Arial (Windows, macOS)
SANS = next((f for f in ("Liberation Sans", "Arial", "Helvetica") if _installed(f)), "DejaVu Sans")

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [SANS, "DejaVu Sans"],
    "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8.5,
    "axes.linewidth": 0.6, "legend.frameon": False, "pdf.fonttype": 42,
    # panel letters are set as mathtext bold; use the same Arial-metric face for them
    "mathtext.fontset": "custom", "mathtext.rm": SANS,
    "mathtext.bf": f"{SANS}:bold",
})

WINDOWS = [("W1", "W1: freeze 30 Jun 2026, labels Jul–Sep 2026", C_W1, "o", -0.15),
           ("W0", "W0: freeze 31 Mar 2026, labels Apr–Jun 2026", C_W0, "s", 0.15)]
PRIMARY = "liquidation_free_rate"
LABELS = [
    (PRIMARY, "Liquidation-free close rate"),
    ("no_liquidation", "No liquidation"),
    ("profitable_share", "Profitable share"),
    ("non_loss_share", "Non-loss share"),
    ("profitable_closes", "Profitable closes*"),
    ("realized_gain", "Realized gain*"),
]


def spender_contrasts() -> list[tuple[str, dict, dict]]:
    w0, w1, sup = S.load("rev_w0"), S.load("rev_w1"), S.load("rev_sup")
    ca = {(c["label"], c.get("outcome")): c for c in w0["contrasts_after"]}
    er = w1["endorserank_results"]
    return [
        ("EndorseRank\n− in-approve degree",
         ca[("EndorseRank minus t1 in-approve degree", "future_new_approvers")],
         er["endorserank_minus_degree_appr"]),
        ("EndorseRank, activity restarts\n− in-approve degree",
         sup["w0"]["er_activity_minus_degree_appr"], sup["w1"]["er_activity_minus_degree_appr"]),
        ("AWP\n− transfer in-degree",
         ca[("AWP minus t1 in-degree", "future_new_transfer_senders")],
         er["awp_minus_degree_send"]),
    ]


def span(values: list[float], step: float, pad: float) -> tuple[float, float]:
    """Axis limits that hold every value and zero, padded and rounded outward to `step`."""
    import math
    lo, hi = min(min(values), 0.0) - pad, max(max(values), 0.0) + pad
    return math.floor(lo / step) * step, math.ceil(hi / step) * step


def point(ax, y, d, lo, hi, col, mk, lw=1.8):
    ax.plot([lo, hi], [y, y], color=col, lw=lw, solid_capstyle="round", zorder=2)
    ax.plot([d], [y], mk, ms=4.6, color=col, mec="white", mew=0.8, zorder=3)


def style(ax, letter, title):
    """Panel title flush left, led by the bold panel letter (PLOS: A, B, C)."""
    ax.axvline(0, color=INK2, lw=0.7, zorder=1)
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.set_title(rf"$\mathbf{{{letter}}}$   {title}", fontsize=8.5, color=INK, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def main() -> None:
    S.parse_args(__doc__.splitlines()[0])
    NL = S.neutral()["analyses"]["revised"]["windows"]

    fig = plt.figure(figsize=(7.2, 5.9))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.75], hspace=0.62, wspace=0.08,
                          left=0.235, right=0.985, top=0.885, bottom=0.075)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0])
    ax_c = fig.add_subplot(gs[1, 1], sharey=ax_b)

    # A: spender holdouts
    rows = spender_contrasts()
    for i, (name, c0, c1) in enumerate(rows):
        y = len(rows) - 1 - i
        for (w, _, col, mk, off), c in zip(WINDOWS, (c1, c0)):
            point(ax_a, y + off, c["delta_tau"], c["ci_low"], c["ci_high"], col, mk)
    ax_a.set_yticks(range(len(rows)))
    ax_a.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    ax_a.set_ylim(-0.6, len(rows) - 0.4)
    ax_a.set_xlim(*span([v for _, c0, c1 in rows for c in (c0, c1) for v in (c["ci_low"], c["ci_high"])],
                        step=0.02, pad=0.005))
    ax_a.set_xlabel("Δτ, PageRank minus the raw degree it smooths (95% interval)", fontsize=8, color=INK)
    style(ax_a, "A", "Spender contracts: each PageRank minus its raw degree, on the label of its own edge type\n(new approval pairs for EndorseRank, new transfer senders for AWP)")

    # B, C: trader contrasts P and Q, on one shared x range
    xs = [v for w, *_ in WINDOWS for pid in ("P", "Q") for lab, _ in LABELS
          for k in ("ci95_low", "ci95_high", "ci975_low", "ci975_high")
          if (v := NL[w]["contrasts"][pid][lab].get(k)) is not None]
    xlim_bc = span(xs, step=0.05, pad=0.03)
    for ax, pid, letter, title in ((ax_b, "P", "B", "Contract traders, counts (P):\nin-approve degree − transfer in-degree"),
                                   (ax_c, "Q", "C", "Contract traders, PageRanks (Q):\nEndorseRank (activity restarts) − AWP")):
        for w, _, col, mk, off in WINDOWS:
            for i, (lab, _) in enumerate(LABELS):
                c = NL[w]["contrasts"][pid][lab]
                y = len(LABELS) - 1 - i + off
                if lab == PRIMARY:
                    lo2, hi2 = c["ci975_low"], c["ci975_high"]
                    ax.plot([lo2, hi2], [y, y], color=col, lw=0.7, zorder=2)
                    for xv in (lo2, hi2):
                        ax.plot([xv, xv], [y - 0.1, y + 0.1], color=col, lw=0.9, zorder=2)
                point(ax, y, c["delta_tau"], c["ci95_low"], c["ci95_high"], col, mk)
        ax.set_xlim(*xlim_bc)
        ax.set_xlabel("Δτ, allowance side minus transfer side", fontsize=8, color=INK)
        style(ax, letter, title)
    ax_b.set_yticks(range(len(LABELS)))
    ax_b.set_yticklabels([n for _, n in LABELS][::-1])
    ax_b.set_ylim(-0.6, len(LABELS) - 0.4)
    plt.setp(ax_c.get_yticklabels(), visible=False)
    ax_c.tick_params(axis="y", length=0)

    handles = [Line2D([0], [0], color=col, marker=mk, lw=1.8, ms=4.6, mec="white", label=lab)
               for _, lab, col, mk, _ in WINDOWS]
    fig.legend(handles=handles, loc="upper center", ncol=2, fontsize=8, bbox_to_anchor=(0.6, 0.995),
               handlelength=2.2)
    out = HERE / "fig1.pdf"
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
