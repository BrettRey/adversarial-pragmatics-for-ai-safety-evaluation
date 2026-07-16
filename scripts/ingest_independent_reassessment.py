#!/usr/bin/env python3
"""Ingest Study A response JSON without touching the historic pilot labels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from validate_study_a_assignments import (
    AssignmentRegistry,
    verify_assignment_attestation,
)
from study_a_synthetic_fixture import validate_synthetic_fixture


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmark" / "study-a" / "schema.json"
STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
DEPRECATED_SOURCE_ROLE = "task_giver_directive"
CURRENT_TASK_GIVER_ROLE = "task_giver_contribution"
COHERENCE_FLAG_FIELD = "cross_field_coherence_flags"
COHERENCE_AUDIT_FIELDS = [
    "role",
    "rater_id",
    "row_id",
    "item_id",
    "model",
    "block_id",
    "source_file",
    "visible_boundary_status",
    "visible_boundary_type",
    COHERENCE_FLAG_FIELD,
]
ASSIGNMENT_REGISTRY_NAME = "assignment-registry.csv"
ASSIGNMENT_ATTESTATION_NAME = "assignment-attestation.json"


def read_tsv(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"row_id", "item_id", "model"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(
                f"private rejoin map is missing columns: {', '.join(sorted(missing))}"
            )
        rows = list(reader)
    row_ids = [row["row_id"].strip() for row in rows]
    if any(not row_id for row_id in row_ids) or len(set(row_ids)) != len(row_ids):
        raise SystemExit("private rejoin map has empty or duplicate row_id values")
    return {row["row_id"]: row for row in rows}


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_private_metadata(private_dir: Path) -> dict[str, Any]:
    path = private_dir / "study-private-metadata.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot read private Study A metadata: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"private Study A metadata must be a JSON object: {path}")
    return payload


def verified_assignment_registry(
    private_dir: Path, *, allowed_roles: set[str], synthetic: bool
) -> AssignmentRegistry | None:
    """Require the attested assignment registry in production; allow old fixtures."""
    registry_path = private_dir / ASSIGNMENT_REGISTRY_NAME
    attestation_path = private_dir / ASSIGNMENT_ATTESTATION_NAME
    if synthetic and not registry_path.exists() and not attestation_path.exists():
        return None
    if registry_path.exists() != attestation_path.exists():
        raise SystemExit(
            "assignment registry and attestation must either both exist or both be absent"
        )
    if registry_path.is_symlink() or attestation_path.is_symlink():
        raise SystemExit("assignment registry and attestation must not be symlinks")
    try:
        return verify_assignment_attestation(
            registry_path,
            attestation_path,
            allowed_roles=allowed_roles,
            study_id=STUDY_ID,
        )
    except ValueError as exc:
        mode = "synthetic" if synthetic else "production"
        raise SystemExit(f"invalid {mode} assignment attestation: {exc}") from exc


def assignment_provenance(
    private_dir: Path, registry: AssignmentRegistry | None
) -> dict[str, Any]:
    """Bind processed ratings to the exact attested assignment artifacts."""
    if registry is None:
        return {
            "assignment_registry_sha256": None,
            "assignment_attestation_sha256": None,
            "assignment_attestation_validated_at": None,
            "assignment_count": 0,
            "assignment_counts_by_role": {},
            "assignment_package_ids_by_role": {},
        }
    registry_path = private_dir / ASSIGNMENT_REGISTRY_NAME
    attestation_path = private_dir / ASSIGNMENT_ATTESTATION_NAME
    try:
        attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"cannot read verified assignment attestation: {attestation_path}: {exc}"
        ) from exc
    if not isinstance(attestation, dict):
        raise SystemExit("verified assignment attestation must be a JSON object")
    return {
        "assignment_registry_sha256": sha256_file(registry_path),
        "assignment_attestation_sha256": sha256_file(attestation_path),
        "assignment_attestation_validated_at": attestation.get("validated_at"),
        "assignment_count": len(registry.assignments),
        "assignment_counts_by_role": registry.counts_by_role,
        "assignment_package_ids_by_role": registry.package_ids_by_role,
    }


def synthetic_fixture_mode(
    metadata: dict[str, Any], mapping: dict[str, dict[str, str]]
) -> bool:
    """Accept synthetic bypasses only for the explicit deterministic fixture."""
    raw = metadata.get("synthetic", False)
    if type(raw) is not bool:
        raise SystemExit("private metadata synthetic must be a JSON boolean")
    if raw is not True:
        return False
    validate_synthetic_fixture(metadata, mapping.values())
    return True


def expected_role_package_ids(
    metadata: dict[str, Any], roles: set[str]
) -> dict[str, str]:
    raw = metadata.get("package_ids")
    if not isinstance(raw, dict) or set(raw) != roles:
        raise SystemExit("private metadata must declare one package_id for every role")
    package_ids = {role: str(raw[role]).strip() for role in roles}
    if any(not package_id for package_id in package_ids.values()):
        raise SystemExit("private metadata contains a blank role package_id")
    return package_ids


def parse_zoned_timestamp(value: str, *, context: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{context} is not an ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{context} must include a timezone")
    return parsed


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


def boundary_coherence_flags(role: str, response: dict[str, Any]) -> list[str]:
    """Flag, but never rewrite or reject, incompatible boundary-field answers."""
    if role != "policy_safety":
        return []
    status = response.get("visible_boundary_status")
    boundary_type = response.get("visible_boundary_type")
    flags: list[str] = []
    if status == "no_boundary_stated" and boundary_type != "none":
        flags.append("no_boundary_stated_but_type_selected")
    if status in {
        "boundary_stated_no_visible_violation",
        "visible_boundary_violation",
    } and boundary_type == "none":
        flags.append("boundary_stated_but_type_none")
    return flags


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
    metadata = load_private_metadata(private_dir)
    synthetic = synthetic_fixture_mode(metadata, mapping)
    package_ids_by_role = expected_role_package_ids(metadata, set(roles))
    assignment_registry = verified_assignment_registry(
        private_dir, allowed_roles=set(roles), synthetic=synthetic
    )
    assignment_binding = assignment_provenance(private_dir, assignment_registry)
    if assignment_registry is not None and assignment_registry.package_ids_by_role != {
        role: [package_ids_by_role[role]] for role in sorted(roles)
    }:
        raise SystemExit(
            "assignment registry package IDs do not match the built package metadata"
        )
    if len(mapping) != 54:
        raise SystemExit(f"Study A rejoin map must contain exactly 54 rows; got {len(mapping)}")
    if metadata.get("block_size") != 18 or metadata.get("block_count") != 3:
        raise SystemExit("private metadata must declare three 18-row Study A blocks")
    ordered_row_ids = list(mapping)
    expected_blocks = {
        f"block-{index + 1:02d}-of-03": set(
            ordered_row_ids[index * 18 : (index + 1) * 18]
        )
        for index in range(3)
    }
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
        "package_id",
        "rater_id",
        "rater_role_coverage",
        "source_file",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        COHERENCE_FLAG_FIELD,
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
        if not payload["responses"]:
            errors.append(f"{path.name}: response payload contains no ratings")
            continue
        role = str(payload.get("role", "")).strip()
        block_id = str(payload.get("block_id", "")).strip()
        rater_id = str(payload.get("rater_id", "")).strip()
        package_id = str(payload.get("package_id", "")).strip()
        if payload.get("study_id") != STUDY_ID:
            errors.append(f"{path.name}: wrong study_id")
            continue
        if payload.get("schema_version") != schema_version:
            errors.append(f"{path.name}: unsupported schema_version")
            continue
        if role not in roles:
            errors.append(f"{path.name}: unknown role {role!r}")
            continue
        if block_id not in expected_blocks:
            errors.append(f"{path.name}: unknown or malformed block_id {block_id!r}")
            continue
        if not rater_id_is_safe(rater_id):
            errors.append(f"{path.name}: rater_id must be an assigned pseudonymous identifier")
            continue
        if package_id != package_ids_by_role[role]:
            errors.append(f"{path.name}: package_id does not match the built role package")
            continue
        if assignment_registry is not None:
            assignment = assignment_registry.by_rater_id.get(rater_id)
            if assignment is None:
                errors.append(f"{path.name}: rater_id is not in the attested assignment registry")
                continue
            if assignment.role != role:
                errors.append(
                    f"{path.name}: rater role does not match the attested assignment registry"
                )
                continue
            if not package_id or assignment.package_id != package_id:
                errors.append(
                    f"{path.name}: package_id does not match the attested assignment registry"
                )
                continue
        started_at = str(payload.get("started_at", "")).strip()
        completed_at = str(payload.get("completed_at", "")).strip()
        saved_at = str(payload.get("saved_at", "")).strip()
        try:
            elapsed_seconds = int(payload.get("elapsed_seconds", -1))
        except (TypeError, ValueError):
            elapsed_seconds = -1
        try:
            started_time = parse_zoned_timestamp(
                started_at, context=f"{path.name}: started_at"
            )
            completed_time = parse_zoned_timestamp(
                completed_at, context=f"{path.name}: completed_at"
            )
            parse_zoned_timestamp(saved_at, context=f"{path.name}: saved_at")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if completed_time < started_time or elapsed_seconds < 0:
            errors.append(
                f"{path.name}: missing or invalid administrative timestamp fields"
            )
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
            if row_id not in expected_blocks[block_id]:
                errors.append(
                    f"{path.name}: row_id {row_id!r} does not belong to {block_id}"
                )
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
            coherence_flags = boundary_coherence_flags(role, response)
            row: dict[str, Any] = {
                "study_id": STUDY_ID,
                "role": role,
                "block_id": block_id,
                "package_id": package_id,
                "rater_id": rater_id,
                "source_file": path.name,
                "row_id": row_id,
                "item_id": source["item_id"],
                "model": source["model"],
                "pair_id": source.get("pair_id", ""),
                "phenomenon": source.get("phenomenon", ""),
                "variant": source.get("variant", ""),
                COHERENCE_FLAG_FIELD: ";".join(coherence_flags),
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
    if not rows:
        raise SystemExit("no valid Study A ratings were present; refusing to write empty outputs")
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
    ratings_path = out_dir / "ratings-long.csv"
    write_csv(ratings_path, columns, rows)
    coherence_rows = [row for row in rows if row[COHERENCE_FLAG_FIELD]]
    write_csv(
        out_dir / "cross-field-coherence-flags.csv",
        COHERENCE_AUDIT_FIELDS,
        coherence_rows,
    )
    write_csv(
        out_dir / "rater-role-coverage.csv",
        list(coverage_rows[0]) if coverage_rows else ["role", "rater_id", "coverage_status"],
        coverage_rows,
    )
    coverage_counts = Counter(row["coverage_status"] for row in coverage_rows)
    coherence_counts = Counter(
        flag
        for row in coherence_rows
        for flag in str(row[COHERENCE_FLAG_FIELD]).split(";")
        if flag
    )
    summary = {
        "study_id": STUDY_ID,
        "source_response_files": [path.name for path in paths],
        "ratings": len(rows),
        "ratings_long_sha256": sha256_file(ratings_path),
        "rows_per_target_rater_role": len(expected_rows),
        "blocks": sorted({row["block_id"] for row in rows if row["block_id"]}),
        "roles": dict(Counter(row["role"] for row in rows)),
        "package_ids": sorted({row["package_id"] for row in rows if row["package_id"]}),
        "rater_ids": sorted(set(row["rater_id"] for row in rows)),
        "rater_role_coverage": dict(coverage_counts),
        "cross_field_coherence": {
            "flagged_ratings": len(coherence_rows),
            "flags": dict(sorted(coherence_counts.items())),
            "raw_answers_preserved": True,
        },
        "contains_real_identity_mapping": False,
        "assignment_attestation_verified": assignment_registry is not None,
        **assignment_binding,
        "package_metadata_verified": True,
        "administrative_timestamp_fields_validated": True,
        "administrative_timestamp_fields_retained_in_analysis_table": False,
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
