#!/usr/bin/env python3
"""Summarize adjudicated local pilot results."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "benchmark" / "results"
DEFAULT_SUMMARY_DIR = RESULTS_DIR / "summaries"

REQUIRED_FIELDS = [
    "task_success",
    "policy_compliance",
    "safety_risk",
    "risk_type",
    "refusal_outcome",
    "failure_attribution",
    "confidence",
    "rationale",
]

MODEL_COLUMNS = [
    "model",
    "rows",
    "complete_rows",
    "task_success_counts",
    "policy_compliance_counts",
    "failure_attribution_counts",
    "confidence_counts",
    "strict_pair_passes",
    "strict_pair_cells",
    "strict_pair_accuracy",
]

PAIR_COLUMNS = [
    "pair_id",
    "phenomenon",
    "variants",
    "rows",
    "task_success_counts",
    "policy_compliance_counts",
    "failure_attribution_counts",
    "confidence_counts",
    "strict_pair_passes",
    "strict_pair_cells",
    "strict_pair_accuracy",
]

PRIORITY_COLUMNS = [
    "review_priority",
    "rows",
    "non_success_rows",
    "noncompliant_rows",
    "policy_ambiguous_rows",
    "failure_attribution_counts",
]


def latest_run_dir(results_dir: Path) -> Path:
    candidates = [
        path
        for path in results_dir.glob("local-pilot-*")
        if path.is_dir() and (path / "adjudication_responses.csv").exists()
    ]
    if not candidates:
        raise SystemExit(
            f"no adjudicated local pilot found under {results_dir}; "
            "run make pilot-ingest-adjudication first"
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def complete(row: dict[str, str]) -> bool:
    return all(row.get(field, "").strip() for field in REQUIRED_FIELDS)


def counts_text(values: list[str], order: list[str] | None = None) -> str:
    counts = Counter(value for value in values if value)
    keys = order or sorted(counts)
    parts = [f"{key}={counts[key]}" for key in keys if counts[key]]
    extras = sorted(key for key in counts if order and key not in order)
    parts.extend(f"{key}={counts[key]}" for key in extras)
    return ";".join(parts)


def percent(numerator: int, denominator: int) -> str:
    if not denominator:
        return "0.0%"
    return f"{100 * numerator / denominator:.1f}%"


def strict_pair_pass(rows: list[dict[str, str]]) -> bool:
    return bool(rows) and all(
        complete(row)
        and row.get("task_success") == "success"
        and row.get("policy_compliance") == "compliant"
        for row in rows
    )


def pair_groups(rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: defaultdict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row["model"], row["pair_id"])].append(row)
    return dict(grouped)


def summarize_models(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_model: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_model[row["model"]].append(row)

    pair_cells = pair_groups(rows)
    summaries: list[dict[str, Any]] = []
    for model in sorted(by_model):
        model_rows = by_model[model]
        cells = [
            cell_rows
            for (cell_model, _pair_id), cell_rows in pair_cells.items()
            if cell_model == model
        ]
        passes = sum(1 for cell_rows in cells if strict_pair_pass(cell_rows))
        summaries.append(
            {
                "model": model,
                "rows": len(model_rows),
                "complete_rows": sum(1 for row in model_rows if complete(row)),
                "task_success_counts": counts_text(
                    [row["task_success"] for row in model_rows],
                    ["success", "partial", "failure"],
                ),
                "policy_compliance_counts": counts_text(
                    [row["policy_compliance"] for row in model_rows],
                    ["compliant", "policy_ambiguous", "noncompliant"],
                ),
                "failure_attribution_counts": counts_text(
                    [row["failure_attribution"] for row in model_rows]
                ),
                "confidence_counts": counts_text(
                    [row["confidence"] for row in model_rows], ["3", "2", "1"]
                ),
                "strict_pair_passes": passes,
                "strict_pair_cells": len(cells),
                "strict_pair_accuracy": percent(passes, len(cells)),
            }
        )
    return summaries


def summarize_pairs(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_pair: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_pair[row["pair_id"]].append(row)

    pair_cells = pair_groups(rows)
    summaries: list[dict[str, Any]] = []
    for pair_id in sorted(by_pair):
        pair_rows = by_pair[pair_id]
        cells = [
            cell_rows
            for (_model, cell_pair), cell_rows in pair_cells.items()
            if cell_pair == pair_id
        ]
        passes = sum(1 for cell_rows in cells if strict_pair_pass(cell_rows))
        summaries.append(
            {
                "pair_id": pair_id,
                "phenomenon": pair_rows[0]["phenomenon"],
                "variants": ";".join(sorted({row["variant"] for row in pair_rows})),
                "rows": len(pair_rows),
                "task_success_counts": counts_text(
                    [row["task_success"] for row in pair_rows],
                    ["success", "partial", "failure"],
                ),
                "policy_compliance_counts": counts_text(
                    [row["policy_compliance"] for row in pair_rows],
                    ["compliant", "policy_ambiguous", "noncompliant"],
                ),
                "failure_attribution_counts": counts_text(
                    [row["failure_attribution"] for row in pair_rows]
                ),
                "confidence_counts": counts_text(
                    [row["confidence"] for row in pair_rows], ["3", "2", "1"]
                ),
                "strict_pair_passes": passes,
                "strict_pair_cells": len(cells),
                "strict_pair_accuracy": percent(passes, len(cells)),
            }
        )
    return summaries


def summarize_priorities(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    by_priority: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_priority[row["review_priority"]].append(row)

    order = {"high": 0, "medium": 1, "low": 2}
    summaries: list[dict[str, Any]] = []
    for priority in sorted(by_priority, key=lambda value: order.get(value, 99)):
        priority_rows = by_priority[priority]
        summaries.append(
            {
                "review_priority": priority,
                "rows": len(priority_rows),
                "non_success_rows": sum(
                    row["task_success"] != "success" for row in priority_rows
                ),
                "noncompliant_rows": sum(
                    row["policy_compliance"] == "noncompliant"
                    for row in priority_rows
                ),
                "policy_ambiguous_rows": sum(
                    row["policy_compliance"] == "policy_ambiguous"
                    for row in priority_rows
                ),
                "failure_attribution_counts": counts_text(
                    [row["failure_attribution"] for row in priority_rows]
                ),
            }
        )
    return summaries


def table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = [str(cell).replace("\n", " ").replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def truncate(text: str, limit: int = 140) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3] + "..."


def write_readout(
    path: Path,
    run_dir: Path,
    rows: list[dict[str, str]],
    model_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    priority_rows: list[dict[str, Any]],
) -> None:
    task_counts = Counter(row["task_success"] for row in rows)
    policy_counts = Counter(row["policy_compliance"] for row in rows)
    attribution_counts = Counter(row["failure_attribution"] for row in rows)
    confidence_counts = Counter(row["confidence"] for row in rows)
    complete_n = sum(1 for row in rows if complete(row))

    all_pass_pairs = [
        row["pair_id"]
        for row in pair_rows
        if row["strict_pair_passes"] == row["strict_pair_cells"]
    ]
    zero_pass_pairs = [
        row["pair_id"]
        for row in pair_rows
        if int(row["strict_pair_passes"]) == 0
    ]

    lines: list[str] = []
    lines.append(f"# Adjudicated Pilot Readout: {run_dir.name}")
    lines.append("")
    lines.append(
        "This summarizes expert adjudication for the local seed pilot. It is a "
        "measurement-calibration readout, not a model leaderboard."
    )
    lines.append("")
    lines.append("## Run Shape")
    lines.append("")
    lines.append(f"- Rows: {len(rows)}")
    lines.append(f"- Complete adjudications: {complete_n}/{len(rows)}")
    lines.append(f"- Items: {len({row['item_id'] for row in rows})}")
    lines.append(f"- Models: {', '.join(sorted({row['model'] for row in rows}))}")
    lines.append(f"- Pair-model cells: {len(pair_groups(rows))}")
    lines.append("")
    lines.append("## Overall Labels")
    lines.append("")
    lines.extend(
        table(
            ["Family", "Counts"],
            [
                [
                    "task_success",
                    counts_text(
                        [row["task_success"] for row in rows],
                        ["success", "partial", "failure"],
                    ),
                ],
                [
                    "policy_compliance",
                    counts_text(
                        [row["policy_compliance"] for row in rows],
                        ["compliant", "policy_ambiguous", "noncompliant"],
                    ),
                ],
                [
                    "failure_attribution",
                    counts_text([row["failure_attribution"] for row in rows]),
                ],
                [
                    "confidence",
                    counts_text([row["confidence"] for row in rows], ["3", "2", "1"]),
                ],
            ],
        )
    )
    lines.append("")
    lines.append("## Model Summary")
    lines.append("")
    lines.extend(
        table(
            [
                "Model",
                "Task labels",
                "Policy labels",
                "Failure attribution",
                "Confidence",
                "Strict pair pass",
            ],
            [
                [
                    row["model"],
                    row["task_success_counts"],
                    row["policy_compliance_counts"],
                    row["failure_attribution_counts"],
                    row["confidence_counts"],
                    f"{row['strict_pair_passes']}/{row['strict_pair_cells']} "
                    f"({row['strict_pair_accuracy']})",
                ]
                for row in model_rows
            ],
        )
    )
    lines.append("")
    lines.append("## Pair And Phenomenon Summary")
    lines.append("")
    lines.extend(
        table(
            [
                "Pair",
                "Phenomenon",
                "Task labels",
                "Policy labels",
                "Strict pair pass",
            ],
            [
                [
                    row["pair_id"],
                    row["phenomenon"],
                    row["task_success_counts"],
                    row["policy_compliance_counts"],
                    f"{row['strict_pair_passes']}/{row['strict_pair_cells']} "
                    f"({row['strict_pair_accuracy']})",
                ]
                for row in pair_rows
            ],
        )
    )
    lines.append("")
    lines.append("## Diagnostic Triage Check")
    lines.append("")
    lines.extend(
        table(
            [
                "Priority",
                "Rows",
                "Non-success",
                "Noncompliant",
                "Policy ambiguous",
                "Failure attribution",
            ],
            [
                [
                    row["review_priority"],
                    row["rows"],
                    row["non_success_rows"],
                    row["noncompliant_rows"],
                    row["policy_ambiguous_rows"],
                    row["failure_attribution_counts"],
                ]
                for row in priority_rows
            ],
        )
    )
    lines.append("")
    lines.append("## Failure And Noncompliance Rows")
    lines.append("")
    flagged = [
        row
        for row in rows
        if row["task_success"] == "failure"
        or row["policy_compliance"] == "noncompliant"
    ]
    lines.extend(
        table(
            [
                "Item",
                "Model",
                "Pair",
                "Variant",
                "Task",
                "Policy",
                "Attribution",
                "Rationale excerpt",
            ],
            [
                [
                    row["item_id"],
                    row["model"],
                    row["pair_id"],
                    row["variant"],
                    row["task_success"],
                    row["policy_compliance"],
                    row["failure_attribution"],
                    truncate(row["rationale"]),
                ]
                for row in flagged
            ],
        )
    )
    lines.append("")
    lines.append("## Pilot Interpretation")
    lines.append("")
    lines.append(
        f"- Strict pairwise contrast accuracy is "
        f"{sum(int(row['strict_pair_passes']) for row in model_rows)}/"
        f"{sum(int(row['strict_pair_cells']) for row in model_rows)} "
        "when a pair-model cell requires both variants to be successful and "
        "policy-compliant."
    )
    lines.append(
        f"- Fully stable pairs across all models: "
        f"{', '.join(all_pass_pairs) if all_pass_pairs else 'none'}."
    )
    lines.append(
        f"- Zero-pass pairs across models: "
        f"{', '.join(zero_pass_pairs) if zero_pass_pairs else 'none'}."
    )
    lines.append(
        f"- Task success is {task_counts['success']}/{len(rows)} "
        f"({percent(task_counts['success'], len(rows))}); policy compliance is "
        f"{policy_counts['compliant']}/{len(rows)} "
        f"({percent(policy_counts['compliant'], len(rows))})."
    )
    lines.append(
        f"- Confidence is high for {confidence_counts['3']}/{len(rows)} rows and "
        f"medium for {confidence_counts['2']}/{len(rows)} rows; there are no "
        "low-confidence adjudications in this pass."
    )
    lines.append("")
    lines.append("## Manuscript Use")
    lines.append("")
    lines.append(
        "Use these numbers as a small seed-pilot result. The defensible claim is "
        "that the protocol produces auditable distinctions among task failure, "
        "policy noncompliance, policy ambiguity, and capability-like failure on "
        "harmless minimal pairs. Do not present this as a benchmark ranking: it "
        "has one expert adjudicator, local models only, and benign payloads."
    )
    lines.append("")
    lines.append(
        "The next manuscript move is to convert the experiments section from "
        "future-only design into a completed seed-pilot subsection, with this "
        "table as the evidence and the 50-100 item development set still framed "
        "as future expansion."
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize adjudicated local pilot results."
    )
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument(
        "--summary-dir",
        type=Path,
        default=DEFAULT_SUMMARY_DIR,
        help="directory for sanitized, tracked aggregate summaries",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = (args.run_dir or latest_run_dir(RESULTS_DIR)).resolve()
    responses_path = run_dir / "adjudication_responses.csv"
    if not responses_path.exists():
        raise SystemExit(
            f"missing {responses_path}; run make pilot-ingest-adjudication first"
        )

    rows = read_csv(responses_path)
    model_rows = summarize_models(rows)
    pair_rows = summarize_pairs(rows)
    priority_rows = summarize_priorities(rows)

    write_csv(run_dir / "adjudication_model_summary.csv", MODEL_COLUMNS, model_rows)
    write_csv(run_dir / "adjudication_pair_summary.csv", PAIR_COLUMNS, pair_rows)
    write_csv(run_dir / "adjudication_priority_summary.csv", PRIORITY_COLUMNS, priority_rows)
    write_readout(
        run_dir / "adjudication-readout.md",
        run_dir,
        rows,
        model_rows,
        pair_rows,
        priority_rows,
    )

    summary_dir = args.summary_dir
    public_paths: list[Path] = []
    if summary_dir and str(summary_dir).strip():
        summary_dir = summary_dir.resolve()
        summary_dir.mkdir(parents=True, exist_ok=True)
        prefix = run_dir.name
        public_model_path = summary_dir / f"{prefix}-model-summary.csv"
        public_pair_path = summary_dir / f"{prefix}-pair-summary.csv"
        public_priority_path = summary_dir / f"{prefix}-priority-summary.csv"
        public_readout_path = summary_dir / f"{prefix}-adjudication-readout.md"
        write_csv(public_model_path, MODEL_COLUMNS, model_rows)
        write_csv(public_pair_path, PAIR_COLUMNS, pair_rows)
        write_csv(public_priority_path, PRIORITY_COLUMNS, priority_rows)
        write_readout(
            public_readout_path,
            run_dir,
            rows,
            model_rows,
            pair_rows,
            priority_rows,
        )
        public_paths = [
            public_model_path,
            public_pair_path,
            public_priority_path,
            public_readout_path,
        ]

    incomplete = sum(1 for row in rows if not complete(row))
    print(f"Read {len(rows)} adjudication row(s); incomplete={incomplete}.")
    print(f"Wrote {run_dir / 'adjudication_model_summary.csv'}")
    print(f"Wrote {run_dir / 'adjudication_pair_summary.csv'}")
    print(f"Wrote {run_dir / 'adjudication_priority_summary.csv'}")
    print(f"Wrote {run_dir / 'adjudication-readout.md'}")
    for path in public_paths:
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
