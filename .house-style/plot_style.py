#!/usr/bin/env python3
"""House-style helpers for Matplotlib figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


COLORS = {
    "primary": "#2E5077",
    "secondary": "#E85D4C",
    "secondary-text": "#C74F41",
    "tertiary": "#4DA375",
    "tertiary-text": "#3D825D",
    "quaternary": "#9B6B9E",
    "quaternary-text": "#946697",
    "quinary": "#D4A03E",
    "quinary-text": "#94702B",
    "light": "#E8E8E8",
    "dark": "#2D2D2D",
    "accent": "#6AADE4",
    "accent-text": "#4B7AA1",
    "link": "#800020",
    "white": "#FFFFFF",
}

COLOR_CYCLE = [
    COLORS["primary"],
    COLORS["secondary"],
    COLORS["tertiary"],
    COLORS["quaternary"],
    COLORS["quinary"],
    COLORS["accent"],
]


def setup(
    font_size: float = 9.5,
    title_size: float = 10.5,
    tick_size: float = 8.5,
    legend_size: float = 8.5,
) -> None:
    """Apply house typography and restrained plot defaults."""

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
            "font.family": "serif",
            "font.serif": [
                "EB Garamond",
                "Garamond",
                "Georgia",
                "Times New Roman",
                "Times",
            ],
            "font.size": font_size,
            "axes.titlesize": title_size,
            "axes.labelsize": font_size,
            "xtick.labelsize": tick_size,
            "ytick.labelsize": tick_size,
            "legend.fontsize": legend_size,
            "axes.facecolor": "white",
            "axes.edgecolor": COLORS["dark"],
            "axes.linewidth": 0.75,
            "axes.grid": False,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.prop_cycle": plt.cycler("color", COLOR_CYCLE),
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.75,
            "ytick.major.width": 0.75,
            "legend.frameon": False,
            "legend.loc": "best",
            "lines.linewidth": 1.4,
            "lines.markersize": 5.5,
            "patch.linewidth": 0.7,
        }
    )


def add_grid(ax, axis: str = "x", color: str | None = None) -> None:
    """Add a subtle reference grid."""

    ax.grid(
        True,
        axis=axis,
        linestyle=":",
        linewidth=0.55,
        color=color or COLORS["light"],
        zorder=0,
    )


def save_figure(fig, path: str | Path, formats: tuple[str, ...] = ("pdf", "png")) -> None:
    """Save a figure in the project-standard formats."""

    base = Path(path)
    base.parent.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        out_path = base.with_suffix(f".{fmt}")
        fig.savefig(out_path)
        print(f"saved {out_path}")
