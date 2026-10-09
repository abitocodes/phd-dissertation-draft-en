#!/usr/bin/env python3
"""Figures of Manuscript B (static vector PDFs for print).

Fig. 2  fig_lambda_sweep.pdf  Kendall tau_b of C-PR against lambda, with 95% intervals.
Fig. 3  fig_contrasts.pdf     Forest plot of the decision and reported contrasts.

Values with intervals are copied from the thesis tables named beside them; the
extra lambda values are the exploratory point estimates in
../supplement/exploratory_checks.json.
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
EXPL = json.loads((HERE.parent / "supplement" / "exploratory_checks.json").read_text())

INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
S1, S2, S3 = "#2a78d6", "#eb6834", "#1baf7a"  # validated categorical slots 1-3
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Times", "Nimbus Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.linewidth": 0.6, "legend.frameon": False,
    "pdf.fonttype": 42,
})

# results/tables/holdout-spenders.tex (spring) and fresh-holdout.tex (registered):
# tau [low, high] at lambda = 0, 0.25, 0.5, 0.75, 1.
SPRING = {
    "New approval pairs": [(0.044, -0.011, 0.098), (0.271, 0.231, 0.314), (0.295, 0.252, 0.336), (0.314, 0.271, 0.357), (0.479, 0.427, 0.529)],
    "New transfer senders": [(0.270, 0.235, 0.310), (0.266, 0.231, 0.306), (0.277, 0.241, 0.318), (0.287, 0.253, 0.330), (0.372, 0.325, 0.424)],
}
REG = {
    "New approval pairs": [(0.058, 0.012, 0.103), (0.228, 0.190, 0.265), (0.238, 0.200, 0.274), (0.243, 0.206, 0.280), (0.338, 0.292, 0.388)],
    "New transfer senders": [(0.257, 0.229, 0.286), (0.245, 0.217, 0.273), (0.246, 0.218, 0.274), (0.248, 0.219, 0.275), (0.289, 0.247, 0.332)],
    "Liquidation-free close rate": [(0.065, 0.030, 0.102), (0.077, 0.042, 0.114), (0.083, 0.047, 0.119), (0.086, 0.051, 0.121), (0.086, 0.037, 0.129)],
}
KEYS = {"New approval pairs": "future_new_approvers", "New transfer senders": "future_new_transfer_senders",
        "Liquidation-free close rate": "future_liquidation_free_rate"}
STYLE = {"New approval pairs": (S1, "o"), "New transfer senders": (S2, "s"), "Liquidation-free close rate": (S3, "^")}
LAM = [0.0, 0.25, 0.5, 0.75, 1.0]
EXTRA = [0.01, 0.05, 0.95, 0.99]


def sweep():
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.1), sharey=True)
    panels = [("(a) Spring: freeze 28 Feb, labels Mar–May", SPRING, "spring/spenders", None),
              ("(b) Registered: freeze 31 May, labels Jun–Aug", REG, "registered/spenders", "registered/traders")]
    for ax, (title, data, key_sp, key_tr) in zip(axes, panels):
        for name, pts in data.items():
            col, mk = STYLE[name]
            key = key_tr if name == "Liquidation-free close rate" else key_sp
            sweep_pts = EXPL["lambda_sweep"][key]
            # interior: lambda in (0, 1), joined; intervals at the registered grid
            xs = sorted([0.25, 0.5, 0.75] + EXTRA)
            ys = [sweep_pts[str(x)][KEYS[name]] for x in xs]
            ax.plot(xs, ys, "-", color=col, lw=1.4, zorder=2)
            ax.plot(EXTRA, [sweep_pts[str(x)][KEYS[name]] for x in EXTRA], mk, ms=3.6, mfc="white", mec=col, mew=0.9, zorder=3)
            for x, (t, lo, hi) in zip(LAM, pts):
                interior = 0 < x < 1
                ax.plot([x, x], [lo, hi], color=col, lw=1.0, alpha=0.9, zorder=2)
                ax.plot([x], [t], mk, ms=4.6, color=col if interior else "white", mec=col, mew=1.1, zorder=4)
        ax.axvspan(-0.03, 0.03, color=GRID, alpha=0.35, lw=0, zorder=0)
        ax.axvspan(0.97, 1.03, color=GRID, alpha=0.35, lw=0, zorder=0)
        ax.set_xticks(LAM)
        ax.set_xticklabels(["0\npayment\nwalk", "0.25", "0.5", "0.75", "1\nauthorization\nwalk"])
        ax.set_xlim(-0.06, 1.06)
        ax.set_title(title, fontsize=7.6, color=INK, loc="left")
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel(r"Kendall $\tau_b$ with the later label")
    fig.supxlabel(r"weight $\lambda$ on the authorization layer in C-PR", fontsize=8, color=INK, y=0.03)
    handles = [Line2D([0], [0], color=STYLE[n][0], marker=STYLE[n][1], lw=1.4, ms=4.6, label=n) for n in KEYS]
    handles += [Line2D([0], [0], color=INK2, marker="o", lw=0, ms=4.6, mfc="white", mec=INK2, label="end point (separate operator)"),
                Line2D([0], [0], color=INK2, marker="o", lw=0, ms=3.6, mfc="white", mec=INK2, label="exploratory λ, point estimate")]
    fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=6.8, bbox_to_anchor=(0.5, 1.0), handlelength=1.8, columnspacing=1.4)
    fig.tight_layout(rect=(0, 0.02, 1, 0.84))
    fig.savefig(HERE / "fig_lambda_sweep.pdf")


# results/tables/holdout-diff.tex and fresh-contrasts.tex
ROWS = [
    ("Rule A (spring)", [
        ("A1  C-PR − authorization walk · approval pairs", -0.184, -0.213, -0.149, "no worse", "fails"),
        ("A2  C-PR − payment walk · transfer senders", 0.007, -0.012, 0.028, "superiority", "fails"),
    ]),
    ("Rule B (registered)", [
        ("F1  C-PR − payment walk · approval pairs", 0.179, 0.132, 0.225, "superiority", "holds"),
        ("F2  C-PR − payment walk · transfer senders", -0.011, -0.025, 0.003, "non-inferiority", "fails"),
        ("F3  C-PR − payment walk · liquidation-free rate", 0.018, 0.011, 0.024, "non-inferiority", "holds"),
    ]),
    ("Reported beside Rule B (nominal)", [
        ("F4  as F3, superiority", 0.018, 0.011, 0.024, "superiority", "holds"),
        ("F5  C-PR − authorization walk · liquidation-free rate", -0.003, -0.060, 0.051, "superiority", "fails"),
        ("F6a  C-PR − authorization walk · approval pairs", -0.101, -0.127, -0.076, "no worse", "fails"),
        ("F6b  C-PR − payment walk · transfer senders", -0.011, -0.025, 0.003, "superiority", "fails"),
    ]),
    ("S1: AWP as comparator (nominal)", [
        ("F1  C-PR − AWP · approval pairs", 0.119, 0.075, 0.169, "superiority", "holds"),
        ("F2  C-PR − AWP · transfer senders", -0.073, -0.092, -0.055, "non-inferiority", "fails"),
        ("F3/F4  C-PR − AWP · liquidation-free rate", 0.037, 0.011, 0.066, "both", "holds"),
    ]),
    ("S2: absent wallets as isolated nodes (nominal)", [
        ("F1  C-PR − payment walk · approval pairs", 0.185, 0.137, 0.232, "superiority", "holds"),
        ("F2  C-PR − payment walk · transfer senders", -0.012, -0.027, 0.003, "non-inferiority", "fails"),
        ("F3/F4  C-PR − payment walk · liquidation-free rate", 0.018, 0.010, 0.024, "both", "holds"),
        ("F5  C-PR − authorization walk · liquidation-free rate", -0.072, -0.118, -0.028, "superiority", "fails"),
    ]),
]


def fmt(x):
    return ("+" if x > 0 else "\u2212" if x < 0 else "") + f"{abs(x):.3f}"


def forest():
    n = sum(len(r) for _, r in ROWS) + len(ROWS)
    fig, ax = plt.subplots(figsize=(7.16, 0.19 * n + 0.75))
    y = n
    yt = []
    lab_tf = ax.get_yaxis_transform()
    for group, rows in ROWS:
        y -= 1
        ax.text(-0.02, y, group, transform=lab_tf, fontsize=7.2, color=INK, fontweight="bold", va="center", ha="right")
        for lab, d, lo, hi, test, verdict in rows:
            y -= 1
            ax.plot([lo, hi], [y, y], color=S1, lw=1.4, solid_capstyle="round", zorder=2)
            ax.plot([d], [y], "o", ms=4.4, color=S1 if verdict == "holds" else "white", mec=S1, mew=1.1, zorder=3)
            ax.text(-0.02, y, lab, transform=lab_tf, fontsize=6.6, color=INK, va="center", ha="right")
            ax.text(1.02, y, f"{fmt(d)} [{fmt(lo)}, {fmt(hi)}]  {verdict}", transform=lab_tf,
                    fontsize=6.5, color=INK2, va="center", ha="left")
            yt.append(y)
    ax.axvline(0, color=INK2, lw=0.7, zorder=1)
    ax.axvline(-0.02, color=INK2, lw=0.7, ls=(0, (3, 2)), zorder=1)
    ax.set_yticks([])
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlim(-0.24, 0.25)
    ax.set_xticks([-0.2, -0.1, 0, 0.1, 0.2])
    ax.set_xticklabels(["\u22120.2", "\u22120.1", "0", "0.1", "0.2"])
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.set_xlabel(r"$\Delta\tau_b$ with 95% interval; dashed line: margin $-0.02$; filled: criterion met", fontsize=7.2)
    fig.subplots_adjust(left=0.39, right=0.76, top=0.99, bottom=0.085)
    fig.savefig(HERE / "fig_contrasts.pdf")


if __name__ == "__main__":
    sweep()
    forest()
    print("ok")
