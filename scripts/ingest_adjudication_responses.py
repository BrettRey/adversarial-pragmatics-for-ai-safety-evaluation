#!/usr/bin/env python3
"""Merge downloaded adjudication response JSON files."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "benchmark" / "results"

FLAT_COLUMNS = [
    "source_file",
    "coder",
    "set",
    "run_id",
    "saved_at",
    "review_id",
    "item_id",
    "model",
    "pair_id",
    "phenomenon",
    "variant",
    "review_priority",
    "cell_code",
    "task_success",
    "policy_compliance",
    "safety_risk",
    "risk_type",
    "refusal_outcome",
    "failure_attribution",
    "confidence",
    "item_problem",
    "boundary_decision_needed",
    "rerun_needed",
    "diagnostic_disagrees",
    "exemplar_for_paper",
    "rationale",
    "updated_at",
]

SUMMARY_COLUMNS = [
    "review_id",
    "item_id",
    "model",
    "pair_id",
    "phenomenon",
    "variant",
    "review_priority",
    "cell_code",
    "n_coders",
    "complete_n",
    "task_success_counts",
    "policy_compliance_counts",
    "failure_attribution_counts",
    "confidence_counts",
    "item_problem_n",
    "boundary_decision_needed_n",
    "rerun_needed_n",
    "diagnostic_disagrees_n",
    "exemplar_for_paper_n",
]


def latest_run_dir(results_dir: Path) -> Path:
    candidates = [
        path
        for path in results_dir.glob("local-pilot-*")
        if path.is_dir() and (path / "review_app").exists()
    ]
    if not candidates:
        raise SystemExit(
            f"no local pilot review app found under {results_dir}; run make pilot-review-app first"
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def read_items(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["review_id"]: row for row in csv.DictReader(handle, delimiter="\t")}


def response_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.glob("*.json"))


def read_payload(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or "responses" not in payload:
        raise ValueError(f"{path} is not an adjudication response JSON file")
    return payload


def bool_int(value: Any) -> int:
    return int(bool(value))


def complete(row: dict[str, Any]) -> bool:
    required = [
        "task_success",
        "policy_compliance",
        "safety_risk",
        "risk_type",
        "refusal_outcome",
        "failure_attribution",
        "confidence",
        "rationale",
    ]
    return all(str(row.get(field, "")).strip() for field in required)


def flatten(paths: list[Path], items: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        payload = read_payload(path)
        coder = str(payload.get("coder", "")).strip()
        set_name = str(payload.get("set", "")).strip()
        run_id = str(payload.get("run_id", "")).strip()
        saved_at = str(payload.get("saved_at", "")).strip()
        for response in payload.get("responses", []):
            if not isinstance(response, dict):
                continue
            review_id = str(response.get("review_id", "")).strip()
            item = items.get(review_id, {})
            flags = response.get("flags", {})
            if not isinstance(flags, dict):
                flags = {}
            rows.append(
                {
                    "source_file": path.name,
                    "coder": coder,
                    "set": set_name,
                    "run_id": run_id,
                    "saved_at": saved_at,
                    "review_id": review_id,
                    "item_id": response.get("item_id") or item.get("item_id", ""),
                    "model": response.get("model") or item.get("model", ""),
                    "pair_id": item.get("pair_id", ""),
                    "phenomenon": item.get("phenomenon", ""),
                    "variant": item.get("variant", ""),
                    "review_priority": item.get("review_priority", response.get("review_priority", "")),
                    "cell_code": item.get("cell_code", ""),
                    "task_success": response.get("task_success", ""),
                    "policy_compliance": response.get("policy_compliance", ""),
                    "safety_risk": response.get("safety_risk", ""),
                    "risk_type": response.get("risk_type", ""),
                    "refusal_outcome": response.get("refusal_outcome", ""),
                    "failure_attribution": response.get("failure_attribution", ""),
                    "confidence": response.get("confidence", ""),
                    "item_problem": bool_int(flags.get("item_problem")),
                    "boundary_decision_needed": bool_int(
                        flags.get("boundary_decision_needed")
                    ),
                    "rerun_needed": bool_int(flags.get("rerun_needed")),
                    "diagnostic_disagrees": bool_int(flags.get("diagnostic_disagrees")),
                    "exemplar_for_paper": bool_int(flags.get("exemplar_for_paper")),
                    "rationale": response.get("rationale", ""),
                    "updated_at": response.get("updated_at", ""),
                }
            )
    return rows


def counts_text(counter: Counter[str]) -> str:
    return ";".join(f"{key}={value}" for key, value in sorted(counter.items()) if key)


def summarize(rows: list[dict[str, Any]], items: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    grouped: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["review_id"])].append(row)

    summary: list[dict[str, Any]] = []
    for review_id in sorted(items):
        item = items[review_id]
        item_rows = grouped.get(review_id, [])
        task_counts = Counter(str(row.get("task_success", "")) for row in item_rows)
        policy_counts = Counter(str(row.get("policy_compliance", "")) for row in item_rows)
        failure_counts = Counter(
            str(row.get("failure_attribution", "")) for row in item_rows
        )
        confidence_counts = Counter(str(row.get("confidence", "")) for row in item_rows)
        summary.append(
            {
                "review_id": review_id,
                "item_id": item.get("item_id", ""),
                "model": item.get("model", ""),
                "pair_id": item.get("pair_id", ""),
                "phenomenon": item.get("phenomenon", ""),
                "variant": item.get("variant", ""),
                "review_priority": item.get("review_priority", ""),
                "cell_code": item.get("cell_code", ""),
                "n_coders": len({row["coder"] for row in item_rows if row.get("coder")}),
                "complete_n": sum(1 for row in item_rows if complete(row)),
                "task_success_counts": counts_text(task_counts),
                "policy_compliance_counts": counts_text(policy_counts),
                "failure_attribution_counts": counts_text(failure_counts),
                "confidence_counts": counts_text(confidence_counts),
                "item_problem_n": sum(int(row["item_problem"]) for row in item_rows),
                "boundary_decision_needed_n": sum(
                    int(row["boundary_decision_needed"]) for row in item_rows
                ),
                "rerun_needed_n": sum(int(row["rerun_needed"]) for row in item_rows),
                "diagnostic_disagrees_n": sum(
                    int(row["diagnostic_disagrees"]) for row in item_rows
                ),
                "exemplar_for_paper_n": sum(
                    int(row["exemplar_for_paper"]) for row in item_rows
                ),
            }
        )
    return summary


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest downloaded adjudication JSON files for a pilot run."
    )
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument(
        "--responses",
        type=Path,
        default=None,
        help="response JSON file or directory; defaults to run_dir/review_app/responses",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = (args.run_dir or latest_run_dir(RESULTS_DIR)).resolve()
    review_dir = run_dir / "review_app"
    items_path = review_dir / "adjudication_items.tsv"
    if not items_path.exists():
        raise SystemExit(f"missing review app items file: {items_path}")

    responses_path = args.responses or review_dir / "responses"
    paths = response_files(responses_path)
    if not paths:
        raise SystemExit(f"no response JSON files found in {responses_path}")

    items = read_items(items_path)
    rows = flatten(paths, items)
    summary_rows = summarize(rows, items)

    write_csv(run_dir / "adjudication_responses.csv", FLAT_COLUMNS, rows)
    write_csv(run_dir / "adjudication_summary.csv", SUMMARY_COLUMNS, summary_rows)

    complete_n = sum(1 for row in rows if complete(row))
    print(f"Read {len(paths)} response file(s).")
    print(f"Flattened {len(rows)} adjudication row(s); complete={complete_n}.")
    print(f"Wrote {run_dir / 'adjudication_responses.csv'}")
    print(f"Wrote {run_dir / 'adjudication_summary.csv'}")


if __name__ == "__main__":
    main()
