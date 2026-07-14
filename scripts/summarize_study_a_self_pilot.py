#!/usr/bin/env python3
"""Summarize local Study A self-pilot timing without reading rating labels.

The self-pilot forms use a distinct study ID, so this script cannot be confused
with independent-rating ingestion. It deliberately reports only form-level
timing and completion metadata, never per-row judgments or rationales.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION-SELF-PILOT"
SCHEMA_VERSION = 6
ROLES = ("linguistic_task", "policy_safety")
EXPECTED_BLOCKS = {f"block-{index:02d}-of-03" for index in range(1, 4)}


def response_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def read_payload(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("responses"), list):
        raise ValueError(f"not a self-pilot response payload: {path}")
    return payload


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--responses",
        type=Path,
        default=ROOT / "private" / "study-a" / "self-pilot" / "responses",
        help="self-pilot JSON file or directory",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "private" / "study-a" / "self-pilot" / "report",
        help="local-only timing report directory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = response_paths(args.responses.resolve())
    if not paths:
        raise SystemExit(f"no self-pilot response JSON files found in {args.responses}")
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for path in paths:
        try:
            payload = read_payload(path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
            continue
        role = str(payload.get("role", "")).strip()
        rater_id = str(payload.get("rater_id", "")).strip()
        block_id = str(payload.get("block_id", "")).strip()
        if payload.get("study_id") != STUDY_ID:
            errors.append(f"{path.name}: wrong self-pilot study ID")
            continue
        if payload.get("schema_version") != SCHEMA_VERSION:
            errors.append(f"{path.name}: wrong self-pilot schema version")
            continue
        if role not in ROLES:
            errors.append(f"{path.name}: unknown role {role!r}")
            continue
        if block_id not in EXPECTED_BLOCKS:
            errors.append(f"{path.name}: unexpected block ID {block_id!r}")
            continue
        if not rater_id or "@" in rater_id:
            errors.append(f"{path.name}: use a pseudonymous self-pilot rater ID")
            continue
        try:
            elapsed_seconds = int(payload.get("elapsed_seconds", -1))
        except (TypeError, ValueError):
            elapsed_seconds = -1
        if elapsed_seconds < 0:
            errors.append(f"{path.name}: invalid elapsed_seconds")
            continue
        key = (role, rater_id, block_id)
        if key in seen:
            errors.append(f"{path.name}: duplicate self-pilot block for {role}/{rater_id}/{block_id}")
            continue
        seen.add(key)
        rows.append(
            {
                "role": role,
                "rater_id": rater_id,
                "block_id": block_id,
                "started_at": payload.get("started_at", ""),
                "completed_at": payload.get("completed_at", ""),
                "elapsed_seconds": elapsed_seconds,
                "rated_rows": len(payload["responses"]),
                "seconds_per_rated_row": f"{elapsed_seconds / len(payload['responses']):.1f}"
                if payload["responses"]
                else "",
                "source_file": path.name,
            }
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rows.sort(key=lambda row: (row["role"], row["block_id"], row["rater_id"]))
    write_csv(out_dir / "self-pilot-timing.csv", list(rows[0]), rows)

    completed = {(row["role"], row["block_id"]) for row in rows}
    role_lines: list[str] = []
    total_elapsed = sum(int(row["elapsed_seconds"]) for row in rows)
    for role in ROLES:
        role_rows = [row for row in rows if row["role"] == role]
        seconds = [int(row["elapsed_seconds"]) for row in role_rows]
        role_blocks = {row["block_id"] for row in role_rows}
        median = statistics.median(seconds) if seconds else 0
        role_lines.append(
            f"- `{role}`: {len(role_blocks)}/3 blocks; total {sum(seconds)} seconds; "
            f"median {median:.0f} seconds per completed block."
        )
    missing = [
        f"{role}/{block_id}"
        for role in ROLES
        for block_id in sorted(EXPECTED_BLOCKS)
        if (role, block_id) not in completed
    ]
    complete = not missing
    status = "complete" if complete else "incomplete"
    readout = [
        "# Study A Interface Self-Pilot Timing",
        "",
        "PRIVATE, NON-EMPIRICAL. This report contains only form-level timing and "
        "completion metadata. It does not inspect, score, or publish self-pilot ratings.",
        "",
        f"- Status: **{status}** ({len(completed)}/6 expected role-blocks).",
        f"- Total recorded form time: {total_elapsed} seconds ({total_elapsed / 60:.1f} minutes).",
        *role_lines,
        "",
        "Use these measurements to state a realistic volunteer workload. Do not use "
        "self-pilot judgments as independent Study A labels or include them in the "
        "independent-rating ingestion path.",
    ]
    if missing:
        readout.extend(["", "## Missing Blocks", "", *[f"- `{item}`" for item in missing]])
    (out_dir / "self-pilot-readout.md").write_text("\n".join(readout) + "\n", encoding="utf-8")
    print(f"Wrote self-pilot timing report to {out_dir / 'self-pilot-readout.md'}")
    if not complete:
        print("Self-pilot is incomplete; no final volunteer workload should be stated yet.")


if __name__ == "__main__":
    main()
