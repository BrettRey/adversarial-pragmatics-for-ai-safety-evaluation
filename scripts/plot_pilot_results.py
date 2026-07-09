#!/usr/bin/env python3
"""Generate house-style figures from sanitized local-pilot summaries."""

from __future__ import annotations

import argparse
import csv
import sys
import textwrap
from pathlib import Path
from typing import Iterable

import matplotlib

matplotlib.use("Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".house-style"))

from plot_style import COLORS, add_grid, save_figure, setup  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch  # noqa: E402


DEFAULT_RUN_ID = "local-pilot-20260630-185417"
DEFAULT_SUMMARY_DIR = PROJECT_ROOT / "benchmark" / "results" / "summaries"
DEFAULT_OUT_DIR = PROJECT_ROOT / "figures"

TASK_LABELS = [
    ("success", "success", "tertiary", ""),
    ("partial", "partial", "quinary", "///"),
    ("failure", "failure", "secondary", "xx"),
]

POLICY_LABELS = [
    ("compliant", "compliant", "tertiary", ""),
    ("policy_ambiguous", "ambiguous", "quinary", "///"),
    ("noncompliant", "noncompliant", "secondary", "xx"),
]

CONFIDENCE_LABELS = [
    ("3", "high", "primary", ""),
    ("2", "medium", "quinary", "///"),
    ("1", "low", "secondary", "xx"),
]

FAILURE_LABELS = [
    ("none", "none", "light", ""),
    ("capability_failure", "capability", "primary", "///"),
    ("policy_ambiguity", "policy ambiguity", "quinary", ".."),
    ("instruction_conflict", "instruction conflict", "quaternary", "\\\\\\"),
    ("scaffold_failure", "scaffold", "secondary", "xx"),
]

PHENOMENON_LABELS = {
    "agent_transcript_interpretation": "agent transcript",
    "authority_hierarchy": "authority hierarchy",
    "deixis_reference_hijack": "deixis/reference",
    "embedded_command": "embedded command",
    "indirect_speech_act": "indirect speech act",
    "mention_use": "mention/use",
    "policy_boundary_ambiguity": "policy boundary",
    "scope_negation": "scope/negation",
}

MODEL_LABELS = {
    "gemma3:12b": "gemma3:12b",
    "glm-4.7-flash:q4_K_M": "glm-4.7-flash\nq4_K_M",
    "qwen3:8b": "qwen3:8b",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_counts(value: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for part in value.split(";"):
        part = part.strip()
        if not part:
            continue
        key, raw_count = part.split("=", 1)
        counts[key] = int(raw_count)
    return counts


def summary_path(summary_dir: Path, run_id: str, name: str) -> Path:
    path = summary_dir / f"{run_id}-{name}.csv"
    if not path.exists():
        raise SystemExit(f"missing summary file: {path}")
    return path


def display_model(model: str) -> str:
    return MODEL_LABELS.get(model, model.replace(":", ":\n"))


def display_phenomenon(value: str) -> str:
    return PHENOMENON_LABELS.get(value, value.replace("_", " "))


def count_label(value: int, denominator: int | None = None) -> str:
    if denominator is None:
        return str(value)
    return f"{value}/{denominator}"


def patch_handles(labels: Iterable[tuple[str, str, str, str]]) -> list[Patch]:
    handles = []
    for _key, label, color_key, hatch in labels:
        handles.append(
            Patch(
                facecolor=COLORS[color_key],
                edgecolor=COLORS["dark"],
                hatch=hatch,
                label=label,
                linewidth=0.5,
            )
        )
    return handles


def label_segment(
    ax,
    y: float,
    left: float,
    width: float,
    label: str,
    denominator: int,
    color_key: str,
) -> None:
    if width <= 0:
        return
    text_color = COLORS["white"] if color_key == "primary" else COLORS["dark"]
    if width >= max(2, denominator * 0.14):
        ax.text(
            left + width / 2,
            y,
            label,
            ha="center",
            va="center",
            color=text_color,
            fontsize=8,
        )
    else:
        ax.text(
            left + width + denominator * 0.015,
            y,
            label,
            ha="left",
            va="center",
            color=COLORS["dark"],
            fontsize=8,
        )


def stacked_bars(
    ax,
    rows: list[dict[str, str]],
    count_column: str,
    labels: list[tuple[str, str, str, str]],
    denominator: int,
    y_labels: list[str],
) -> None:
    y_values = list(range(len(rows)))
    for row_index, row in enumerate(rows):
        left = 0
        counts = parse_counts(row[count_column])
        for key, _label, color_key, hatch in labels:
            value = counts.get(key, 0)
            if value:
                ax.barh(
                    row_index,
                    value,
                    left=left,
                    height=0.58,
                    color=COLORS[color_key],
                    edgecolor=COLORS["white"],
                    hatch=hatch,
                    linewidth=0.5,
                    zorder=3,
                )
                label_segment(
                    ax, row_index, left, value, str(value), denominator, color_key
                )
            left += value

    ax.set_yticks(y_values)
    ax.set_yticklabels(y_labels)
    ax.set_xlim(0, denominator)
    ax.set_xticks(range(0, denominator + 1, 6 if denominator == 18 else 2))
    ax.invert_yaxis()
    add_grid(ax, axis="x")
    ax.set_axisbelow(True)


def plot_model_outcomes(model_rows: list[dict[str, str]], out_dir: Path) -> None:
    setup()
    y_labels = [display_model(row["model"]) for row in model_rows]
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.35, 3.45),
        sharey=True,
        gridspec_kw={"width_ratios": [1.05, 1.05, 0.75], "wspace": 0.16},
    )

    stacked_bars(
        axes[0],
        model_rows,
        "task_success_counts",
        TASK_LABELS,
        18,
        y_labels,
    )
    axes[0].set_title("Task labels")
    axes[0].set_xlabel("Rows (of 18)")

    stacked_bars(
        axes[1],
        model_rows,
        "policy_compliance_counts",
        POLICY_LABELS,
        18,
        y_labels,
    )
    axes[1].set_title("Policy labels")
    axes[1].set_xlabel("Rows (of 18)")

    y_values = list(range(len(model_rows)))
    passes = [int(row["strict_pair_passes"]) for row in model_rows]
    cells = [int(row["strict_pair_cells"]) for row in model_rows]
    axes[2].barh(
        y_values,
        cells,
        height=0.58,
        color=COLORS["light"],
        edgecolor=COLORS["dark"],
        linewidth=0.35,
        zorder=2,
    )
    axes[2].barh(
        y_values,
        passes,
        height=0.58,
        color=COLORS["primary"],
        edgecolor=COLORS["white"],
        linewidth=0.4,
        zorder=3,
    )
    for y, passed, total in zip(y_values, passes, cells, strict=True):
        x = passed + 0.18 if passed else 0.18
        axes[2].text(
            x,
            y,
            count_label(passed, total),
            ha="left",
            va="center",
            color=COLORS["dark"],
            fontsize=8,
        )
    axes[2].set_title("Strict pairs")
    max_cells = max(cells) if cells else 0
    axes[2].set_xlabel(f"Eligible cells (of {max_cells})")
    axes[2].set_xlim(0, max_cells)
    axes[2].set_xticks(range(0, max_cells + 1, 2))
    axes[2].invert_yaxis()
    add_grid(axes[2], axis="x")
    axes[2].set_axisbelow(True)

    legend_labels = [
        ("success", "task: success", "tertiary", ""),
        ("compliant", "policy: compliant", "tertiary", ""),
        ("partial", "task: partial", "quinary", "///"),
        ("policy_ambiguous", "policy: ambiguous", "quinary", "///"),
        ("failure", "task: failure", "secondary", "xx"),
        ("noncompliant", "policy: noncompliant", "secondary", "xx"),
    ]
    fig.legend(
        handles=patch_handles(legend_labels),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.03),
        ncol=3,
        columnspacing=1.15,
        handlelength=1.5,
        fontsize=7.8,
    )
    fig.subplots_adjust(bottom=0.26)
    fig.align_xlabels(axes)
    save_figure(fig, out_dir / "pilot_model_outcomes")
    plt.close(fig)


def pair_axis_labels(pair_rows: list[dict[str, str]]) -> list[str]:
    labels = []
    for row in pair_rows:
        phenomenon = display_phenomenon(row["phenomenon"])
        labels.append(f"{row['pair_id']}  {phenomenon}")
    return labels


def plot_pair_accuracy(pair_rows: list[dict[str, str]], out_dir: Path) -> None:
    setup()
    labels = pair_axis_labels(pair_rows)
    y_values = list(range(len(pair_rows)))
    passes = [int(row["strict_pair_passes"]) for row in pair_rows]
    cells = [int(row["strict_pair_cells"]) for row in pair_rows]

    fig, ax = plt.subplots(figsize=(7.2, 4.35))
    ax.barh(
        y_values,
        cells,
        height=0.62,
        color=COLORS["light"],
        edgecolor=COLORS["dark"],
        linewidth=0.35,
        zorder=2,
    )
    ax.barh(
        y_values,
        passes,
        height=0.62,
        color=COLORS["primary"],
        edgecolor=COLORS["white"],
        linewidth=0.4,
        zorder=3,
    )
    for y, passed, total in zip(y_values, passes, cells, strict=True):
        label = "excluded" if total == 0 else count_label(passed, total)
        ax.text(
            3.08,
            y,
            label,
            ha="left",
            va="center",
            color=COLORS["dark"],
            fontsize=8.5,
        )

    ax.set_yticks(y_values)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 3.45)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xlabel("Strict pair passes (of 3 eligible model cells)")
    ax.invert_yaxis()
    add_grid(ax, axis="x")
    ax.set_axisbelow(True)
    save_figure(fig, out_dir / "pilot_pair_accuracy")
    plt.close(fig)


def plot_diagnostic_triage(priority_rows: list[dict[str, str]], out_dir: Path) -> None:
    setup()
    priorities = [row["review_priority"] for row in priority_rows]
    metrics = [
        ("rows", "all rows", "light", ""),
        ("non_success_rows", "non-success", "primary", "///"),
        ("noncompliant_rows", "noncompliant", "secondary", "xx"),
        ("policy_ambiguous_rows", "policy ambiguous", "quinary", ".."),
    ]
    y_base = list(range(len(priority_rows)))
    height = 0.16
    offsets = [-0.27, -0.09, 0.09, 0.27]
    max_rows = max(int(row["rows"]) for row in priority_rows)

    fig, ax = plt.subplots(figsize=(7.1, 3.25))
    for offset, (key, _label, color_key, hatch) in zip(offsets, metrics, strict=True):
        values = [int(row[key]) for row in priority_rows]
        y_values = [y + offset for y in y_base]
        ax.barh(
            y_values,
            values,
            height=height,
            color=COLORS[color_key],
            edgecolor=COLORS["dark"] if color_key == "light" else COLORS["white"],
            hatch=hatch,
            linewidth=0.45,
            zorder=3,
        )
        for y, value in zip(y_values, values, strict=True):
            ax.text(
                value + max_rows * 0.018 + 0.08,
                y,
                str(value),
                va="center",
                ha="left",
                color=COLORS["dark"],
                fontsize=8,
            )

    ax.set_yticks(y_base)
    ax.set_yticklabels([priority.title() for priority in priorities])
    ax.invert_yaxis()
    ax.set_xlim(0, max_rows + 5)
    ax.set_xlabel("Rows")
    ax.set_ylabel("Diagnostic priority")
    ax.legend(
        handles=patch_handles(metrics),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.33),
        ncol=4,
        columnspacing=1.0,
        handlelength=1.6,
    )
    add_grid(ax, axis="x")
    ax.set_axisbelow(True)
    save_figure(fig, out_dir / "pilot_diagnostic_triage")
    plt.close(fig)


def plot_failure_attribution(pair_rows: list[dict[str, str]], out_dir: Path) -> None:
    setup()
    labels = pair_axis_labels(pair_rows)
    active_labels = [
        label
        for label in FAILURE_LABELS
        if any(parse_counts(row["failure_attribution_counts"]).get(label[0], 0) for row in pair_rows)
    ]
    fig, ax = plt.subplots(figsize=(7.2, 4.35))
    stacked_bars(
        ax,
        pair_rows,
        "failure_attribution_counts",
        active_labels,
        6,
        labels,
    )
    ax.set_xlabel("Rows (of 6 per pair)")
    ax.legend(
        handles=patch_handles(active_labels),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.25),
        ncol=3,
        columnspacing=1.0,
        handlelength=1.6,
    )
    save_figure(fig, out_dir / "pilot_failure_attribution")
    plt.close(fig)


def plot_confidence_distribution(model_rows: list[dict[str, str]], out_dir: Path) -> None:
    setup()
    y_labels = [display_model(row["model"]) for row in model_rows]
    active_labels = [
        label
        for label in CONFIDENCE_LABELS
        if any(parse_counts(row["confidence_counts"]).get(label[0], 0) for row in model_rows)
    ]
    fig, ax = plt.subplots(figsize=(6.8, 2.7))
    stacked_bars(
        ax,
        model_rows,
        "confidence_counts",
        active_labels,
        18,
        y_labels,
    )
    ax.set_xlabel("Rows (of 18)")
    ax.legend(
        handles=patch_handles(active_labels),
        loc="lower center",
        bbox_to_anchor=(0.5, -0.39),
        ncol=len(active_labels),
        columnspacing=1.0,
        handlelength=1.6,
    )
    save_figure(fig, out_dir / "pilot_confidence_distribution")
    plt.close(fig)


def wrapped(text: str, width: int = 14) -> str:
    return "\n".join(textwrap.wrap(text, width=width))


def plot_evaluation_pipeline(out_dir: Path) -> None:
    setup(font_size=9, title_size=10, tick_size=8, legend_size=8)
    fig, ax = plt.subplots(figsize=(7.35, 1.85))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    steps = [
        ("Seed item\nmetadata", "contrast fixed before output"),
        ("Model\noutput", "row-level transcript"),
        ("Rule-aided\nchecks", "triage signals"),
        ("Expert\nlabels", "task, policy, risk"),
        ("Judge\nlabels", "validation target"),
        ("Adjudication\n+ metrics", "revision evidence"),
    ]
    x_positions = [0.08, 0.245, 0.41, 0.575, 0.74, 0.905]
    box_width = 0.13
    box_height = 0.38
    y_center = 0.58

    for index, ((title, subtitle), x_center) in enumerate(
        zip(steps, x_positions, strict=True)
    ):
        fill = COLORS["light"] if index not in {0, len(steps) - 1} else "#EEF3F7"
        rect = FancyBboxPatch(
            (x_center - box_width / 2, y_center - box_height / 2),
            box_width,
            box_height,
            boxstyle="round,pad=0.012,rounding_size=0.012",
            facecolor=fill,
            edgecolor=COLORS["primary"],
            linewidth=0.9,
        )
        ax.add_patch(rect)
        ax.text(
            x_center,
            y_center + 0.055,
            title,
            ha="center",
            va="center",
            color=COLORS["dark"],
            fontsize=9,
            linespacing=0.92,
        )
        ax.text(
            x_center,
            y_center - 0.13,
            wrapped(subtitle, 17),
            ha="center",
            va="center",
            color=COLORS["primary"],
            fontsize=7.4,
            linespacing=0.9,
        )
        if index < len(x_positions) - 1:
            arrow = FancyArrowPatch(
                (x_center + box_width / 2 + 0.006, y_center),
                (x_positions[index + 1] - box_width / 2 - 0.006, y_center),
                arrowstyle="-|>",
                mutation_scale=9,
                linewidth=0.8,
                color=COLORS["dark"],
            )
            ax.add_patch(arrow)

    ax.text(
        0.5,
        0.18,
        "The unit of analysis is the item--model row; disagreement and judge error feed item and taxonomy revision.",
        ha="center",
        va="center",
        color=COLORS["dark"],
        fontsize=8.4,
    )
    save_figure(fig, out_dir / "evaluation_pipeline")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument(
        "--summary-dir",
        type=Path,
        default=DEFAULT_SUMMARY_DIR,
        help="Directory containing sanitized pilot summary CSVs.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help="Directory for generated PDF and PNG figures.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model_rows = read_csv(summary_path(args.summary_dir, args.run_id, "model-summary"))
    pair_rows = read_csv(summary_path(args.summary_dir, args.run_id, "pair-summary"))
    priority_rows = read_csv(
        summary_path(args.summary_dir, args.run_id, "priority-summary")
    )

    plot_evaluation_pipeline(args.out_dir)
    plot_model_outcomes(model_rows, args.out_dir)
    plot_pair_accuracy(pair_rows, args.out_dir)
    plot_diagnostic_triage(priority_rows, args.out_dir)
    plot_failure_attribution(pair_rows, args.out_dir)
    plot_confidence_distribution(model_rows, args.out_dir)


if __name__ == "__main__":
    main()
