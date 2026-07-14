#!/usr/bin/env python3
"""Ingest Study A response JSON without touching the historic pilot labels."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmark" / "study-a" / "schema.json"
STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
DEPRECATED_SOURCE_ROLE = "task_giver_directive"
CURRENT_TASK_GIVER_ROLE = "task_giver_contribution"


def read_tsv(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["row_id"]: row for row in csv.DictReader(handle, delimiter="\t")}


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def response_paths(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("*.json"))


def read_payload(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("responses"), list):
        raise ValueError(f"not a Study A response payload: {path}")
    return payload


def rater_id_is_safe(value: str) -> bool:
    """Permit pseudonymous assigned IDs, reject obvious contact details."""
    return bool(value) and "@" not in value and len(value) <= 64


def field_is_missing(field: dict[str, Any], value: Any) -> bool:
    """Apply required-field checks without stringifying structured values."""
    if field.get("required", True) is False:
        return False
    if field.get("type") == "multiselect":
        return value is None or value == []
    if field.get("type") == "textarea":
        return not isinstance(value, str) or not value.strip()
    return value is None or value == ""


def categorical_error(field: dict[str, Any], value: Any) -> str | None:
    """Return a categorical validation error, including multiselect shape errors."""
    if field.get("type") == "textarea":
        return None
    options = field.get("options") or []
    if field.get("type") == "multiselect":
        if not isinstance(value, list):
            return "expected a nonempty JSON array"
        if not value:
            return "expected at least one selected value"
        if any(not isinstance(selected, str) for selected in value):
            return "all selected values must be strings"
        if len(value) != len(set(value)):
            return "selected values must be unique"
        if DEPRECATED_SOURCE_ROLE in value:
            return (
                f"deprecated v5 selected value {DEPRECATED_SOURCE_ROLE!r}; "
                f"use {CURRENT_TASK_GIVER_ROLE!r}"
            )
        undeclared = [selected for selected in value if selected not in options]
        if undeclared:
            return f"undeclared selected value(s): {undeclared!r}"
        return None
    if value not in options:
        return "value is not one of the declared options"
    return None


def csv_field_value(field: dict[str, Any], value: Any) -> Any:
    """Serialize multiselects canonically only at the CSV boundary."""
    if field.get("type") != "multiselect":
        return value
    selected = set(value)
    canonical = [option for option in field.get("options", []) if option in selected]
    return json.dumps(canonical, ensure_ascii=False, separators=(",", ":"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument(
        "--responses",
        type=Path,
        default=None,
        help="JSON file or directory; defaults to PRIVATE_DIR/responses",
    )
    parser.add_argument("--out-dir", type=Path, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    private_dir = args.private_dir.resolve()
    mapping_path = private_dir / "row_map.tsv"
    if not mapping_path.exists():
        raise SystemExit(f"missing private rejoin map: {mapping_path}")
    mapping = read_tsv(mapping_path)
    schema = load_schema()
    roles = schema["roles"]
    schema_version = schema["schema_version"]
    union_fields = sorted(
        {
            field["name"]
            for role_schema in roles.values()
            for field in role_schema["fields"]
        }
    )
    columns = [
        "study_id",
        "role",
        "block_id",
        "rater_id",
        "rater_role_coverage",
        "source_file",
        "started_at",
        "completed_at",
        "elapsed_seconds",
        "saved_at",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        *union_fields,
    ]
    response_dir = (args.responses or private_dir / "responses").resolve()
    paths = response_paths(response_dir)
    if not paths:
        raise SystemExit(f"no Study A response JSON files found in {response_dir}")
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
        if payload.get("study_id") != STUDY_ID:
            errors.append(f"{path.name}: wrong study_id")
            continue
        if payload.get("schema_version") != schema_version:
            errors.append(f"{path.name}: unsupported schema_version")
            continue
        if role not in roles:
            errors.append(f"{path.name}: unknown role {role!r}")
            continue
        if not rater_id_is_safe(rater_id):
            errors.append(f"{path.name}: rater_id must be an assigned pseudonymous identifier")
            continue
        started_at = str(payload.get("started_at", "")).strip()
        completed_at = str(payload.get("completed_at", "")).strip()
        try:
            elapsed_seconds = int(payload.get("elapsed_seconds", -1))
        except (TypeError, ValueError):
            elapsed_seconds = -1
        if not started_at or not completed_at or elapsed_seconds < 0:
            errors.append(f"{path.name}: missing or invalid block timing fields")
            continue
        role_fields = roles[role]["fields"]
        fields_by_name = {field["name"]: field for field in role_fields}
        for response in payload["responses"]:
            if not isinstance(response, dict):
                errors.append(f"{path.name}: response is not an object")
                continue
            row_id = str(response.get("row_id", "")).strip()
            if row_id not in mapping:
                errors.append(f"{path.name}: unknown opaque row_id {row_id!r}")
                continue
            duplicate_key = (role, rater_id, row_id)
            if duplicate_key in seen:
                errors.append(f"{path.name}: duplicate rating for {role}/{rater_id}/{row_id}")
                continue
            seen.add(duplicate_key)
            missing = [
                field_name
                for field_name, field in fields_by_name.items()
                if field_is_missing(field, response.get(field_name))
            ]
            if missing:
                errors.append(
                    f"{path.name}: incomplete rating for {row_id}: {', '.join(missing)}"
                )
                continue
            invalid_categorical = []
            for field in role_fields:
                value = response.get(field["name"])
                reason = categorical_error(field, value)
                if reason:
                    invalid_categorical.append((field["name"], value, reason))
            if invalid_categorical:
                for field_name, invalid_value, reason in invalid_categorical:
                    errors.append(
                        f"{path.name}: invalid categorical value for row {row_id!r}, "
                        f"field {field_name!r}: {reason}; got {invalid_value!r}"
                    )
                continue
            source = mapping[row_id]
            row: dict[str, Any] = {
                "study_id": STUDY_ID,
                "role": role,
                "block_id": payload.get("block_id", ""),
                "rater_id": rater_id,
                "source_file": path.name,
                "started_at": started_at,
                "completed_at": completed_at,
                "elapsed_seconds": elapsed_seconds,
                "saved_at": payload.get("saved_at", ""),
                "row_id": row_id,
                "item_id": source["item_id"],
                "model": source["model"],
                "pair_id": source.get("pair_id", ""),
                "phenomenon": source.get("phenomenon", ""),
                "variant": source.get("variant", ""),
            }
            for field_name in union_fields:
                field = fields_by_name.get(field_name)
                row[field_name] = (
                    csv_field_value(field, response.get(field_name, ""))
                    if field is not None
                    else ""
                )
            rows.append(row)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    expected_rows = set(mapping)
    by_rater_role: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in rows:
        by_rater_role[(row["role"], row["rater_id"])].add(row["row_id"])
    coverage_by_rater_role: dict[tuple[str, str], str] = {}
    coverage_rows: list[dict[str, Any]] = []
    for (role, rater_id), row_ids in sorted(by_rater_role.items()):
        status = "complete" if row_ids == expected_rows else "partial"
        coverage_by_rater_role[(role, rater_id)] = status
        coverage_rows.append(
            {
                "role": role,
                "rater_id": rater_id,
                "rated_rows": len(row_ids),
                "target_rows": len(expected_rows),
                "coverage_status": status,
                "missing_rows": len(expected_rows - row_ids),
                "completed_blocks": ";".join(
                    sorted(
                        {
                            row["block_id"]
                            for row in rows
                            if row["role"] == role and row["rater_id"] == rater_id
                        }
                    )
                ),
            }
        )
    for row in rows:
        row["rater_role_coverage"] = coverage_by_rater_role[
            (row["role"], row["rater_id"])
        ]
    out_dir = (args.out_dir or private_dir / "processed").resolve()
    write_csv(out_dir / "ratings-long.csv", columns, rows)
    write_csv(
        out_dir / "rater-role-coverage.csv",
        list(coverage_rows[0]) if coverage_rows else ["role", "rater_id", "coverage_status"],
        coverage_rows,
    )
    coverage_counts = Counter(row["coverage_status"] for row in coverage_rows)
    summary = {
        "study_id": STUDY_ID,
        "source_response_files": [path.name for path in paths],
        "ratings": len(rows),
        "rows_per_target_rater_role": len(expected_rows),
        "blocks": sorted({row["block_id"] for row in rows if row["block_id"]}),
        "roles": dict(Counter(row["role"] for row in rows)),
        "rater_ids": sorted(set(row["rater_id"] for row in rows)),
        "rater_role_coverage": dict(coverage_counts),
        "contains_real_identity_mapping": False,
        "timing_fields_retained": True,
    }
    (out_dir / "ingestion-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    partial_count = coverage_counts.get("partial", 0)
    print(
        f"Ingested {len(rows)} independent ratings into {out_dir / 'ratings-long.csv'} "
        f"({partial_count} partial rater-role return(s) retained)"
    )


if __name__ == "__main__":
    main()
