#!/usr/bin/env python3
"""Fig 1 of Manuscript A (PLOS ONE).

Panels A and B: discovery curves of the deciding run of the discovery-order test (freeze
T_obs, both mode): the share of the hot contracts visited against the contracts visited,
for a breadth-first crawl and for crawls ordered by the number of contract backlinks, by
the coupled walk C-PR' and by the transfer walk AWP', on the hot sets of the two
importances (mean over the 20 seeds, with the range over the seeds as a band).
Panel C: each single-layer walk minus the count it smooths on the spender label of its own
edge type, in W0 and W1, and in W0 among the spenders that another contract had paid.

Values are read from the published summaries in the public repository (checked against their
SHA256SUMS.txt); none is typed here. Writes figures/fig1.pdf next to this script. Convert
to the upload TIFF with

    pdftoppm -tiff -tiffcompression lzw -r 300 -singlefile fig1.pdf Fig1

PLOS figure rules: Arial-metric sans serif (Liberation Sans or Arial), 8-12 pt, at most
7.5 in wide and 8.75 in tall.

    CONTRACT_REP_REPO=/path/to/ERC20-Allowance-PageRank-Wallet-Reputation python3 make_fig1.py
"""
from __future__ import annotations

import math
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
import make_tables as M  # noqa: E402

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#d9d8d4"
# Categorical slots 1-3 of the reference palette (validated on a white surface for all pairs:
# colour-vision-deficiency Delta E 9.2, normal vision 24.0); line styles are the second encoding.
C_BLUE, C_ORANGE, C_AQUA = "#2a78d6", "#eb6834", "#1baf7a"
C_W1, C_W0 = C_BLUE, C_ORANGE


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
    "xtick.color": INK2, "ytick.color": INK2, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.linewidth": 0.6, "legend.frameon": False, "pdf.fonttype": 42,
    # panel letters and primes are set as mathtext; use the same Arial-metric face for them
    "mathtext.fontset": "custom", "mathtext.rm": SANS, "mathtext.it": f"{SANS}:italic",
    "mathtext.bf": f"{SANS}:bold",
})

# ordering key, legend label, colour, line style, line width
CURVES = (
    ("cpr_l50", "C-PR′ (coupled walk)", C_BLUE, "-", 1.9),
    ("ib_u", "IB′$_U$ (contract backlinks)", C_ORANGE, (0, (5, 1.6)), 1.6),
    ("awp", "AWP′ (transfer walk)", C_AQUA, (0, (6, 1.5, 1.2, 1.5)), 1.6),
    ("bfs", "BFS (breadth-first)", INK2, "-", 1.0),
)
X_MAX = 0.20          # share of the universe shown
X_AUC = 0.10          # the area of the statistic is taken over this share
WINDOWS = [("W1", "W1: freeze 30 Jun 2026, labels Jul–Sep 2026", C_W1, "o", -0.16),
           ("W0", "W0: freeze 31 Mar 2026, labels Apr–Jun 2026", C_W0, "s", 0.16)]


def span(values: list[float], step: float, pad: float) -> tuple[float, float]:
    """Axis limits that hold every value and zero, padded and rounded outward to `step`."""
    lo, hi = min(min(values), 0.0) - pad, max(max(values), 0.0) + pad
    return math.floor(lo / step) * step, math.ceil(hi / step) * step


def letter(ax, char: str, title: str) -> None:
    """Panel title flush left, led by the bold panel letter (PLOS: A, B, C)."""
    ax.set_title(rf"$\mathbf{{{char}}}$   {title}", fontsize=8.5, color=INK, loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def curves_panel(ax, run: dict, imp: str, char: str, title: str) -> None:
    grid = run["curves"]["grid"]
    n = run["sizes"]["universe"]["U"]
    keep = [i for i, k in enumerate(grid) if k / n <= X_MAX + 1e-9]
    x = [100.0 * grid[i] / n for i in keep]
    by = run["curves"]["P_ST"][imp]
    top = 0.0
    for key, _, col, style, lw in CURVES:
        c = by[key]
        mean = [c["mean"][i] for i in keep]
        lo, hi = [c["min"][i] for i in keep], [c["max"][i] for i in keep]
        ax.fill_between(x, lo, hi, color=col, alpha=0.10, lw=0, zorder=1)
        ax.plot(x, mean, color=col, ls=style, lw=lw, solid_capstyle="round", zorder=3)
        top = max(top, max(mean))
    # references: the random curve K/|U| and the ideal curve min(1, K/|H|)
    ax.plot(x, [v / 100.0 for v in x], color=MUTED, ls=(0, (1, 1.6)), lw=1.0, zorder=2)
    ideal = by["ideal"]
    ax.plot(x, [(ideal["mean"] if isinstance(ideal, dict) else ideal)[i] for i in keep],
            color=INK, ls=(0, (1, 1.6)), lw=1.0, zorder=2)
    ax.axvline(100 * X_AUC, color=INK2, lw=0.6, zorder=1)
    ax.set_xlim(0, 100 * X_MAX)
    ax.set_ylim(0, min(1.0, math.ceil(1.25 * top / 0.05) * 0.05))
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.grid(axis="y", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    ax.set_xlabel("Contracts visited (% of the universe)", fontsize=8, color=INK)
    letter(ax, char, title)


def point(ax, y, d, col, mk):
    ax.plot([d["ci_low"], d["ci_high"]], [y, y], color=col, lw=1.8, solid_capstyle="round", zorder=2)
    ax.plot([d["delta_tau"]], [y], mk, ms=4.8, color=col, mec="white", mew=0.8, zorder=3)


def main() -> None:
    S.parse_args(__doc__.splitlines()[0])
    run = S.discovery("tobs", "both")
    assert run["decides"], "Fig 1 draws the run that decides"
    b = M.spender_blocks()

    fig = plt.figure(figsize=(7.2, 6.1))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], hspace=0.56, wspace=0.22,
                          left=0.085, right=0.972, top=0.882, bottom=0.128)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    hot = run["hot_sets"]
    curves_panel(ax_a, run, "i_t", "A", f"Hot set of user-account inflow, $I_T$ (n = {hot['i_t@q']:,})")
    curves_panel(ax_b, run, "i_a", "B", f"Hot set of user-authorized value, $I_A$ (n = {hot['i_a@q']:,})")
    ax_a.set_ylabel("Share of the hot contracts visited", fontsize=8, color=INK)

    handles = [Line2D([0], [0], color=col, ls=style, lw=lw, label=lab) for _, lab, col, style, lw in CURVES]
    handles += [Line2D([0], [0], color=MUTED, ls=(0, (1, 1.6)), lw=1.0, label="Random curve"),
                Line2D([0], [0], color=INK, ls=(0, (1, 1.6)), lw=1.0, label="Ideal order")]
    fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=8, bbox_to_anchor=(0.535, 1.0),
               handlelength=3.0, columnspacing=1.6, labelcolor=INK)

    # C: each walk minus the count it smooths on the spender labels
    sub = gs[1, :].subgridspec(1, 2, width_ratios=[0.44, 0.56], wspace=0.0)
    ax_c = fig.add_subplot(sub[0, 1])
    rec = f"{b['rec_n']:,}"
    rows = [
        ("EndorseRank − in-approve degree\n(new approval pairs)", b["er_deg"][0], b["er_deg"][1]),
        ("EndorseRank, activity restarts − in-approve degree\n(new approval pairs)", b["act_deg"][0], b["act_deg"][1]),
        ("AWP − transfer in-degree\n(new transfer senders)", b["awp_deg"][0], b["awp_deg"][1]),
        (f"EndorseRank − in-approve degree, among the {rec} W0\nspenders that another contract had paid", b["rec_er_deg"], None),
        (f"AWP − transfer in-degree, among the {rec} W0\nspenders that another contract had paid", b["rec_awp_deg"], None),
    ]
    values = []
    for i, (_, c0, c1) in enumerate(rows):
        y = len(rows) - 1 - i
        for (_, _, col, mk, off), c in zip(WINDOWS, (c1, c0)):
            if c is None:
                continue
            point(ax_c, y + (off if c1 is not None else 0.0), c, col, mk)
            values += [c["ci_low"], c["ci_high"]]
    ax_c.axvline(0, color=INK2, lw=0.7, zorder=1)
    ax_c.grid(axis="x", color=GRID, lw=0.5)
    ax_c.set_axisbelow(True)
    ax_c.set_yticks(range(len(rows)))
    ax_c.set_yticklabels([r[0] for r in rows][::-1], fontsize=8, color=INK)
    ax_c.set_ylim(-0.6, len(rows) - 0.4)
    ax_c.set_xlim(*span(values, step=0.02, pad=0.004))
    ax_c.set_xlabel("Δτ, walk minus the count it smooths (95% interval)", fontsize=8, color=INK)
    for s in ("top", "right"):
        ax_c.spines[s].set_visible(False)
    top_c = ax_c.get_position().y1
    fig.text(0.085, top_c + 0.012, r"$\mathbf{C}$   Spender contracts: each walk minus the count it smooths, on the label of its own edge type",
             fontsize=8.5, color=INK, ha="left", va="bottom")
    w_handles = [Line2D([0], [0], color=col, marker=mk, lw=1.8, ms=4.8, mec="white", label=lab)
                 for _, lab, col, mk, _ in WINDOWS]
    fig.legend(handles=w_handles, loc="lower center", bbox_to_anchor=(0.535, 0.004), ncol=2, fontsize=8,
               handlelength=2.2, columnspacing=1.6, labelcolor=INK)

    out = HERE / "fig1.pdf"
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
