#!/usr/bin/env python3
"""Analyze role-separated Study A ratings without collapsing criteria."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from study_a_synthetic_fixture import validate_synthetic_fixture
from validate_study_a_assignments import verify_assignment_attestation
from validate_study_a_assignments import verify_assignment_attestation


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "benchmark" / "study-a" / "schema.json"
STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
ASSIGNMENT_REGISTRY_NAME = "assignment-registry.csv"
ASSIGNMENT_ATTESTATION_NAME = "assignment-attestation.json"
MIN_PANEL_RATERS = 2
EXPECTED_SOURCE_ROWS = 54
COHERENCE_FLAG_FIELD = "cross_field_coherence_flags"
ASSIGNMENT_REGISTRY_NAME = "assignment-registry.csv"
ASSIGNMENT_ATTESTATION_NAME = "assignment-attestation.json"
SUPPORT_PATTERN_STRATA = (
    ("support_2_of_2", "2/2"),
    ("support_2_of_3", "2/3"),
    ("support_3_of_3", "3/3"),
    ("support_other", "other"),
)
# Values that are NOT a substantive criterion judgment: the evaluator is saying
# the visible record cannot support a judgment (or the item is broken). A modal
# panel label that resolves to one of these is an *escape*, not a substantive
# label, and per the analysis plan it is excluded from author–panel and
# judge–panel agreement. refusal_outcome has no such escape value.
ESCAPE_VALUES = {"item_problem", "insufficient_visible_context"}
# Pair excluded from the narrower paired-contrast score: it is a confidentiality
# contrast, not a clean controlled contrast (A1; DECISIONS 2026-07-15). Retained
# for row-level analyses. The constant name remains for output compatibility.
PAIRED_CONTRAST_EXCLUDE = {"P008"}
# The value on the two compared policy criteria that means "no policy/authority
# was at stake" — the trivial majority class on this benign set. Policy-compliance
# agreement is reported both overall and on the policy-at-stake subset so trivial
# no-stakes agreement does not dominate the planned primary summary.
NOT_AT_STAKE = "no_policy_or_authority_limit"
# The criteria compared against author and judge panel labels, by role.
COMPARABLE = {
    "linguistic_task": ["task_success"],
    "policy_safety": ["policy_compliance", "refusal_outcome"],
}
# Frozen historical author-snapshot vocabulary crosswalks. Normalization is
# criterion-scoped so identically spelled labels in other criteria are untouched.
AUTHOR_LABEL_NORMALIZATION = {
    "refusal_outcome": {"not_applicable": "not_a_refusal"},
}
# Paired panel-outcome divergence is a response-mediated descriptive summary,
# not a measure of authority sensitivity. Refusal outcome is intentionally not
# included in this paired summary.
PAIR_DIVERGENCE_CRITERIA = {
    "linguistic_task": ["task_success"],
    "policy_safety": ["policy_compliance"],
}
# Exact generated filenames superseded by the panel-relative output contract.
# Remove only these known analyzer artifacts when reusing an output directory;
# unknown files and directories are never touched.
RETIRED_ANALYSIS_OUTPUTS = frozenset(
    {
        "authority-sensitivity.csv",
        "independent-reference-labels.csv",
        "source-roles-exact-set-reference.csv",
        "source-roles-per-label-reference.csv",
        "source-role-clarity-vs-exact-set-stability.csv",
        "author-label-comparison.csv",
        "author-vs-independent-confusion.csv",
        "author-label-revision-summary.csv",
        "judge-vs-independent-summary.csv",
        "judge-minority-class-recall.csv",
        "judge-vs-independent-confusion.csv",
        "unstable-or-ambiguous-rows.csv",
    }
)
EVALUATOR_COVERAGE_FIELDS = [
    "role",
    "rater_id",
    "rated_rows",
    "target_rows",
    "coverage_status",
    "missing_rows",
    "completed_blocks",
]
DEPRECATED_SOURCE_ROLE = "task_giver_directive"
CURRENT_TASK_GIVER_ROLE = "task_giver_contribution"


def read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def remove_retired_analysis_outputs(out_dir: Path) -> None:
    """Remove only known superseded files from a reused analysis directory."""
    for filename in sorted(RETIRED_ANALYSIS_OUTPUTS):
        path = out_dir / filename
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.exists():
            raise SystemExit(f"retired analysis output path is not a file: {path}")


def counts_text(values: Iterable[str]) -> str:
    counts = Counter(value for value in values if value)
    return "; ".join(f"{value}:{counts[value]}" for value in sorted(counts))


def normalize_author_label(criterion: str, label: str) -> str:
    """Normalize a frozen author label only through its declared crosswalk."""
    return AUTHOR_LABEL_NORMALIZATION.get(criterion, {}).get(label, label)


def support_pattern_bucket(value: str) -> str:
    """Map a realized support-count/N string to a predeclared reporting stratum."""
    known = {pattern for _, pattern in SUPPORT_PATTERN_STRATA if pattern != "other"}
    return value if value in known else "other"


def split_coherence_flags(value: str) -> list[str]:
    return [flag for flag in value.split(";") if flag]


def author_stratum_fields(prefix: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Return complete author--panel agreement counts for one reporting stratum."""
    matches = sum(row["comparison_status"] == "author_panel_match" for row in rows)
    mismatches = sum(
        row["comparison_status"] == "author_panel_mismatch" for row in rows
    )
    denominator = len(rows)
    return {
        f"{prefix}_panel_comparable": denominator,
        f"{prefix}_author_panel_match": matches,
        f"{prefix}_author_panel_mismatch": mismatches,
        f"{prefix}_author_panel_agreement_rate": (
            f"{matches / denominator:.3f}" if denominator else ""
        ),
        f"{prefix}_author_panel_mismatch_rate": (
            f"{mismatches / denominator:.3f}" if denominator else ""
        ),
    }


def blank_author_stratum_fields(prefix: str) -> dict[str, str]:
    return {
        f"{prefix}_panel_comparable": "",
        f"{prefix}_author_panel_match": "",
        f"{prefix}_author_panel_mismatch": "",
        f"{prefix}_author_panel_agreement_rate": "",
        f"{prefix}_author_panel_mismatch_rate": "",
    }


def judge_matches(
    rows: list[dict[str, Any]],
    judge_by_key: dict[tuple[str, str], dict[str, str]],
    criterion: str,
) -> int:
    return sum(
        judge_value(judge_by_key[(row["item_id"], row["model"])], criterion)
        == row["panel_modal_label"]
        for row in rows
    )


def judge_stratum_fields(
    prefix: str,
    rows: list[dict[str, Any]],
    judge_by_key: dict[tuple[str, str], dict[str, str]],
    criterion: str,
) -> dict[str, Any]:
    """Return complete judge--panel agreement counts for one reporting stratum."""
    matches = judge_matches(rows, judge_by_key, criterion)
    denominator = len(rows)
    return {
        f"eligible_{prefix}_panel_labels": denominator,
        f"{prefix}_judge_panel_matches": matches,
        f"{prefix}_judge_panel_agreement_rate": (
            f"{matches / denominator:.3f}" if denominator else ""
        ),
    }


def judge_class_stratum_fields(
    prefix: str,
    rows: list[dict[str, Any]],
    judge_by_key: dict[tuple[str, str], dict[str, str]],
    criterion: str,
) -> dict[str, Any]:
    matches = judge_matches(rows, judge_by_key, criterion)
    denominator = len(rows)
    return {
        f"{prefix}_panel_class_rows": denominator,
        f"{prefix}_judge_panel_matches": matches,
        f"{prefix}_panel_class_agreement_rate": (
            f"{matches / denominator:.3f}" if denominator else ""
        ),
    }


def panel_class_summary(
    values: Iterable[str],
) -> tuple[Counter[str], list[str], int, float]:
    """Return counts, all co-majority classes, top count, and top-class share."""
    counts: Counter[str] = Counter(value for value in values if value)
    if not counts:
        return counts, [], 0, 0.0
    top_count = max(counts.values())
    top_classes = sorted(label for label, count in counts.items() if count == top_count)
    return counts, top_classes, top_count, top_count / sum(counts.values())


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def parse_source_roles(value: str, options: list[str], *, context: str) -> tuple[list[str], str]:
    """Validate and canonicalize a source-role set stored as compact JSON."""
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid source_roles JSON for {context}: {value!r}") from exc
    if not isinstance(parsed, list) or not parsed:
        raise SystemExit(f"source_roles must be a nonempty JSON array for {context}")
    if any(not isinstance(label, str) for label in parsed):
        raise SystemExit(f"source_roles must contain only strings for {context}")
    if len(parsed) != len(set(parsed)):
        raise SystemExit(f"source_roles contains duplicate labels for {context}")
    if DEPRECATED_SOURCE_ROLE in parsed:
        raise SystemExit(
            f"source_roles contains deprecated v5 label {DEPRECATED_SOURCE_ROLE!r} "
            f"for {context}; use {CURRENT_TASK_GIVER_ROLE!r}"
        )
    invalid = sorted(set(parsed) - set(options))
    if invalid:
        raise SystemExit(
            f"source_roles contains undeclared labels for {context}: {', '.join(invalid)}"
        )
    canonical = [option for option in options if option in parsed]
    return canonical, compact_json(canonical)


def source_role_set_counts(signatures: Iterable[str]) -> str:
    counts = Counter(signatures)
    payload = [
        {"source_roles": json.loads(signature), "ratings": count}
        for signature, count in sorted(counts.items())
    ]
    return compact_json(payload)


def load_schema() -> dict[str, Any]:
    with SCHEMA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def panel_modal_summary(
    values: list[str], minimum_raters: int = MIN_PANEL_RATERS
) -> tuple[str, str, int, float]:
    """Return panel modal label, status, top support count, and share."""
    if not values:
        return "", "missing", 0, 0.0
    counts = Counter(values)
    top = max(counts.values())
    winners = sorted(label for label, count in counts.items() if count == top)
    share = top / len(values)
    if len(values) < minimum_raters:
        return "no_consensus", "insufficient_raters", top, share
    if len(winners) != 1:
        return "no_consensus", "tie", top, share
    if top == len(values):
        return winners[0], "unanimous", top, share
    if top > len(values) / 2:
        return winners[0], "majority", top, share
    return "no_consensus", "no_majority", top, share


def source_key(row: dict[str, str]) -> tuple[str, str]:
    return row.get("item_id", ""), row.get("model", "")


def judge_value(row: dict[str, str], criterion: str) -> str:
    # The real judge producer (run_llm_judge_validation.py) writes columns as
    # judge_<criterion> alongside human_<criterion>/match_<criterion>; the
    # synthetic fixture and simulate_* path write the bare <criterion>. Accept
    # either so the analyzer reads real producer output and synthetic fixtures
    # alike, and does not silently score zero rows on prefixed files.
    if f"judge_{criterion}" in row:
        return row.get(f"judge_{criterion}", "")
    return row.get(criterion, "")


def build_judge_lookup(judge_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for row in judge_rows:
        key = source_key(row)
        if key in lookup:
            raise SystemExit(
                "Duplicate judge row for item_id/model "
                f"{key}: judge_labels.csv holds more than one comparator "
                "condition (e.g. multiple prompt_variant or judge runs). Filter "
                "it to a single retained comparator before analysis instead of "
                "letting rows overwrite silently."
            )
        lookup[key] = row
    return lookup


def build_unique_lookup(
    rows: list[dict[str, str]], *, kind: str, path: Path
) -> dict[tuple[str, str], dict[str, str]]:
    """Build a source-key lookup without allowing empty or duplicate keys."""
    lookup: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = source_key(row)
        if not all(key):
            raise SystemExit(f"{kind} input has an empty item_id/model key: {path}")
        if key in lookup:
            raise SystemExit(f"duplicate {kind} item_id/model key {key}: {path}")
        lookup[key] = row
    return lookup


def scalar_schema_options(schema: dict[str, Any]) -> dict[str, set[str]]:
    options: dict[str, set[str]] = {}
    for role_schema in schema["roles"].values():
        for field in role_schema["fields"]:
            if field.get("type") not in {"multiselect", "textarea"}:
                options[field["name"]] = set(field.get("options") or [])
    return options


def require_exact_keys(
    lookup: dict[tuple[str, str], dict[str, str]],
    expected_keys: set[tuple[str, str]],
    *,
    kind: str,
    path: Path,
) -> None:
    missing = sorted(expected_keys - set(lookup))
    extra = sorted(set(lookup) - expected_keys)
    if len(lookup) != EXPECTED_SOURCE_ROWS or missing or extra:
        raise SystemExit(
            f"{kind} input must contain exactly the {EXPECTED_SOURCE_ROWS} source keys: "
            f"{path} (rows={len(lookup)}, missing={missing[:3]!r}, extra={extra[:3]!r})"
        )


def require_consistent_nonempty_field(
    rows: list[dict[str, str]], field: str, *, kind: str, path: Path
) -> str:
    raw_values = [row.get(field, "") for row in rows]
    if any(value != value.strip() for value in raw_values):
        raise SystemExit(f"{kind} input has noncanonical whitespace in {field}: {path}")
    values = {value.strip() for value in raw_values}
    if len(values) != 1 or "" in values:
        raise SystemExit(
            f"{kind} input must have one nonempty {field} value throughout: {path}"
        )
    return next(iter(values))


def validate_production_comparison_inputs(
    *,
    private_dir: Path,
    judge_label_paths: list[Path],
    map_rows: list[dict[str, str]],
    schema: dict[str, Any],
) -> tuple[
    list[dict[str, str]],
    dict[tuple[str, str], dict[str, str]],
    list[tuple[Path, list[dict[str, str]], dict[tuple[str, str], dict[str, str]]]],
]:
    """Fail closed on every required production comparison input."""
    if len(map_rows) != EXPECTED_SOURCE_ROWS:
        raise SystemExit(
            f"production row map must contain exactly {EXPECTED_SOURCE_ROWS} rows; "
            f"got {len(map_rows)}"
        )
    row_ids = [row.get("row_id", "") for row in map_rows]
    if any(not row_id for row_id in row_ids) or len(set(row_ids)) != len(row_ids):
        raise SystemExit("production row map has empty or duplicate row_id values")
    expected_keys = {source_key(row) for row in map_rows}
    if len(expected_keys) != EXPECTED_SOURCE_ROWS or any(not all(key) for key in expected_keys):
        raise SystemExit("production row map must have 54 unique nonempty item_id/model keys")

    author_path = private_dir / "author_labels.csv"
    if not author_path.exists():
        raise SystemExit(f"missing required production author snapshot: {author_path}")
    author_rows = read_csv(author_path)
    author_lookup = build_unique_lookup(author_rows, kind="author", path=author_path)
    require_exact_keys(
        author_lookup, expected_keys, kind="author", path=author_path
    )
    allowed = scalar_schema_options(schema)
    comparable_criteria = [
        criterion for criteria in COMPARABLE.values() for criterion in criteria
    ]
    for key, row in author_lookup.items():
        for criterion in comparable_criteria:
            source_raw = row.get(criterion, "")
            if source_raw != source_raw.strip():
                raise SystemExit(
                    f"noncanonical whitespace in production author label for "
                    f"{key}/{criterion}"
                )
            raw = source_raw.strip()
            value = normalize_author_label(criterion, raw)
            if not raw or value not in allowed[criterion]:
                raise SystemExit(
                    f"invalid or missing production author label for {key}/{criterion}: "
                    f"{raw!r}"
                )

    if len(judge_label_paths) != 2:
        raise SystemExit(
            "production analysis requires exactly two explicit --judge-labels inputs"
        )
    if len(set(judge_label_paths)) != 2:
        raise SystemExit("production judge inputs must be two distinct files")
    judge_inputs = []
    judge_models: set[str] = set()
    for path in judge_label_paths:
        if not path.exists():
            raise SystemExit(f"missing required production judge comparator: {path}")
        rows = read_csv(path)
        required_columns = {
            "item_id",
            "model",
            "judge_run_id",
            "judge_model",
            "prompt_variant",
            "judge_task_success",
            "judge_policy_compliance",
            "judge_refusal_outcome",
            "parse_error",
            "raw_response",
        }
        present_columns = set(rows[0]) if rows else set()
        missing_columns = sorted(required_columns - present_columns)
        if missing_columns:
            raise SystemExit(
                f"production judge comparator is missing required columns in {path}: "
                + ", ".join(missing_columns)
            )
        lookup = build_unique_lookup(rows, kind="judge", path=path)
        require_exact_keys(lookup, expected_keys, kind="judge", path=path)
        judge_model = require_consistent_nonempty_field(
            rows, "judge_model", kind="judge", path=path
        )
        require_consistent_nonempty_field(
            rows, "judge_run_id", kind="judge", path=path
        )
        require_consistent_nonempty_field(
            rows, "prompt_variant", kind="judge", path=path
        )
        if judge_model in judge_models:
            raise SystemExit(
                f"production judge comparators must use distinct judge models: {judge_model}"
            )
        judge_models.add(judge_model)
        for key, row in lookup.items():
            parse_error = row.get("parse_error", "").strip()
            if not row.get("raw_response", "").strip():
                raise SystemExit(
                    f"production judge comparator is missing raw_response for {key} in {path}"
                )
            for criterion in comparable_criteria:
                source_value = judge_value(row, criterion)
                if source_value != source_value.strip():
                    raise SystemExit(
                        f"noncanonical whitespace in production judge label for "
                        f"{key}/{criterion} in {path}"
                    )
                value = source_value.strip()
                if value and value not in allowed[criterion]:
                    raise SystemExit(
                        f"invalid production judge label for {key}/{criterion} in "
                        f"{path}: {value!r}"
                    )
                if not value and not parse_error:
                    raise SystemExit(
                        f"missing production judge label without an explicit parse_error "
                        f"for {key}/{criterion} in {path}"
                    )
        judge_inputs.append((path, rows, lookup))
    return author_rows, author_lookup, judge_inputs


def load_optional_rows(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def derive_evaluator_coverage_rows(
    ratings: list[dict[str, str]], map_rows: list[dict[str, str]]
) -> list[dict[str, Any]]:
    """Reconstruct evaluator coverage from the validated vote table."""
    expected_rows = {row["row_id"] for row in map_rows}
    by_evaluator: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ratings:
        by_evaluator[(row["role"], row["rater_id"])].append(row)
    coverage_rows: list[dict[str, Any]] = []
    for (role, rater_id), rows in sorted(by_evaluator.items()):
        row_ids = {row["row_id"] for row in rows}
        coverage_rows.append(
            {
                "role": role,
                "rater_id": rater_id,
                "rated_rows": len(row_ids),
                "target_rows": len(expected_rows),
                "coverage_status": (
                    "complete" if row_ids == expected_rows else "partial"
                ),
                "missing_rows": len(expected_rows - row_ids),
                "completed_blocks": ";".join(
                    sorted({row["block_id"] for row in rows})
                ),
            }
        )
    return coverage_rows


def validate_coverage_sidecar(
    path: Path,
    sidecar_rows: list[dict[str, str]],
    derived_rows: list[dict[str, Any]],
) -> None:
    """Reject a stale or tampered redundant coverage sidecar."""
    if not sidecar_rows:
        return
    actual_fields = set(sidecar_rows[0])
    expected_fields = set(EVALUATOR_COVERAGE_FIELDS)
    if actual_fields != expected_fields or any(None in row for row in sidecar_rows):
        raise SystemExit(
            "rater-role coverage must have exactly these fields: "
            + ", ".join(EVALUATOR_COVERAGE_FIELDS)
        )
    normalized_derived = [
        {field: str(row[field]) for field in EVALUATOR_COVERAGE_FIELDS}
        for row in derived_rows
    ]
    if sidecar_rows != normalized_derived:
        raise SystemExit(
            f"rater-role coverage does not match coverage reconstructed from "
            f"validated ratings: {path}"
        )


def primary_criteria(schema: dict[str, Any]) -> dict[str, list[str]]:
    return {
        role: [
            field["name"]
            for field in role_schema["fields"]
            if field["name"] not in {"confidence", "rationale", "source_roles"}
            and field.get("type") != "multiselect"
        ]
        for role, role_schema in schema["roles"].items()
    }


def analysis_metadata(private_dir: Path) -> dict[str, Any]:
    path = private_dir / "study-private-metadata.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def synthetic_fixture_mode(
    metadata: dict[str, Any], map_rows: list[dict[str, str]]
) -> bool:
    """Accept comparison-input bypasses only for the explicit test fixture."""
    raw = metadata.get("synthetic", False)
    if type(raw) is not bool:
        raise SystemExit("private metadata synthetic must be a JSON boolean")
    if raw is not True:
        return False
    validate_synthetic_fixture(metadata, map_rows)
    return True


def validate_ratings_input(
    *,
    private_dir: Path,
    ratings: list[dict[str, str]],
    ratings_path: Path,
    map_rows: list[dict[str, str]],
    metadata: dict[str, Any],
    schema: dict[str, Any],
    synthetic: bool,
) -> None:
    """Reject stale, duplicate, cross-package, or structurally invalid votes."""
    if not ratings:
        raise SystemExit("ratings-long.csv contains no Study A ratings")
    role_fields = {
        role: {field["name"]: field for field in role_schema["fields"]}
        for role, role_schema in schema["roles"].items()
    }
    union_fields = {
        field_name for fields in role_fields.values() for field_name in fields
    }
    required_columns = {
        "study_id",
        "role",
        "block_id",
        "package_id",
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
        COHERENCE_FLAG_FIELD,
        *union_fields,
    }
    missing_columns = sorted(required_columns - set(ratings[0]))
    if missing_columns:
        raise SystemExit(
            "ratings-long.csv is missing required columns: "
            + ", ".join(missing_columns)
        )
    map_by_row = {row["row_id"]: row for row in map_rows}
    if len(map_by_row) != len(map_rows):
        raise SystemExit("row map contains duplicate row_id values")
    raw_package_ids = metadata.get("package_ids")
    roles = set(role_fields)
    if not isinstance(raw_package_ids, dict) or set(raw_package_ids) != roles:
        raise SystemExit("private metadata must declare one package_id for every role")
    package_ids = {role: str(raw_package_ids[role]).strip() for role in roles}
    if metadata.get("block_size") != 18 or metadata.get("block_count") != 3:
        raise SystemExit("private metadata must declare three 18-row Study A blocks")
    ordered_row_ids = [row["row_id"] for row in map_rows]
    expected_blocks = {
        f"block-{index + 1:02d}-of-03": set(
            ordered_row_ids[index * 18 : (index + 1) * 18]
        )
        for index in range(3)
    }
    assignment_registry = None
    assignment_attestation: dict[str, Any] = {}
    registry_path = private_dir / ASSIGNMENT_REGISTRY_NAME
    attestation_path = private_dir / ASSIGNMENT_ATTESTATION_NAME
    if not synthetic:
        if registry_path.is_symlink() or attestation_path.is_symlink():
            raise SystemExit(
                "current production assignment registry and attestation must not "
                "be symlinks"
            )
        try:
            assignment_registry = verify_assignment_attestation(
                registry_path,
                attestation_path,
                allowed_roles=roles,
                study_id=STUDY_ID,
            )
        except ValueError as exc:
            raise SystemExit(
                f"invalid current production assignment attestation: {exc}"
            ) from exc
        if assignment_registry.package_ids_by_role != {
            role: [package_ids[role]] for role in sorted(roles)
        }:
            raise SystemExit(
                "current assignment registry package IDs disagree with private metadata"
            )
        try:
            assignment_attestation = json.loads(
                attestation_path.read_text(encoding="utf-8")
            )
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(
                f"cannot read current production assignment attestation: {exc}"
            ) from exc
        if not isinstance(assignment_attestation, dict):
            raise SystemExit(
                "current production assignment attestation must be a JSON object"
            )
    seen_votes: set[tuple[str, str, str]] = set()
    rated_by_evaluator: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row_number, row in enumerate(ratings, start=2):
        context = f"{ratings_path}:{row_number}"
        role = row.get("role", "")
        row_id = row.get("row_id", "")
        rater_id = row.get("rater_id", "")
        block_id = row.get("block_id", "")
        if row.get("study_id") != STUDY_ID:
            raise SystemExit(f"{context}: wrong study_id")
        if role not in role_fields:
            raise SystemExit(f"{context}: undeclared evaluator role {role!r}")
        if row.get("package_id") != package_ids[role]:
            raise SystemExit(f"{context}: stale or wrong package_id")
        if not rater_id:
            raise SystemExit(f"{context}: blank rater_id")
        if assignment_registry is not None:
            assignment = assignment_registry.by_rater_id.get(rater_id)
            if assignment is None:
                raise SystemExit(
                    f"{context}: rater_id is absent from the current attested "
                    "assignment registry"
                )
            if assignment.role != role or assignment.package_id != row.get("package_id"):
                raise SystemExit(
                    f"{context}: rating role/package disagrees with the current "
                    "attested assignment registry"
                )
        if row_id not in map_by_row:
            raise SystemExit(f"{context}: row_id is absent from the current row map")
        if block_id not in expected_blocks or row_id not in expected_blocks[block_id]:
            raise SystemExit(f"{context}: row_id does not belong to block_id")
        source = map_by_row[row_id]
        for field in ("item_id", "model", "pair_id", "phenomenon", "variant"):
            if row.get(field, "") != source.get(field, ""):
                raise SystemExit(f"{context}: {field} disagrees with the current row map")
        vote_key = (role, rater_id, row_id)
        if vote_key in seen_votes:
            raise SystemExit(f"{context}: duplicate evaluator vote {vote_key!r}")
        seen_votes.add(vote_key)
        rated_by_evaluator[(role, rater_id)].add(row_id)

        own_fields = role_fields[role]
        for field_name in union_fields - set(own_fields):
            if row.get(field_name, ""):
                raise SystemExit(f"{context}: cross-role field {field_name!r} is nonempty")
        if synthetic:
            continue
        for field_name, field in own_fields.items():
            value = row.get(field_name, "")
            if field.get("required", True) and value == "":
                raise SystemExit(f"{context}: required field {field_name!r} is blank")
            if value == "" or field.get("type") == "textarea":
                continue
            if field.get("type") == "multiselect":
                try:
                    selected = json.loads(value)
                except json.JSONDecodeError as exc:
                    raise SystemExit(
                        f"{context}: multiselect {field_name!r} is not JSON"
                    ) from exc
                if (
                    not isinstance(selected, list)
                    or not selected
                    or len(selected) != len(set(selected))
                    or any(option not in field.get("options", []) for option in selected)
                ):
                    raise SystemExit(f"{context}: invalid multiselect {field_name!r}")
            elif value not in (field.get("options") or []):
                raise SystemExit(
                    f"{context}: invalid categorical value for {field_name!r}: {value!r}"
                )
    expected_rows = set(map_by_row)
    for key, row_ids in rated_by_evaluator.items():
        expected_coverage = "complete" if row_ids == expected_rows else "partial"
        observed = {
            row["rater_role_coverage"]
            for row in ratings
            if (row["role"], row["rater_id"]) == key
        }
        if observed != {expected_coverage}:
            raise SystemExit(
                f"ratings-long.csv has inconsistent coverage for {key!r}: {observed!r}"
            )

    if synthetic:
        return
    summary_path = ratings_path.parent / "ingestion-summary.json"
    if not summary_path.exists():
        raise SystemExit(f"missing production ingestion summary: {summary_path}")
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid production ingestion summary: {summary_path}") from exc
    expected_coverage_counts = Counter(
        "complete" if row_ids == expected_rows else "partial"
        for row_ids in rated_by_evaluator.values()
    )
    if (
        summary.get("study_id") != STUDY_ID
        or summary.get("ratings") != len(ratings)
        or summary.get("ratings_long_sha256") != sha256_file(ratings_path)
        or summary.get("assignment_attestation_verified") is not True
        or summary.get("assignment_registry_sha256") != sha256_file(registry_path)
        or summary.get("assignment_attestation_sha256")
        != sha256_file(attestation_path)
        or summary.get("assignment_attestation_validated_at")
        != assignment_attestation.get("validated_at")
        or summary.get("assignment_count") != len(assignment_registry.assignments)
        or summary.get("assignment_counts_by_role")
        != assignment_registry.counts_by_role
        or summary.get("assignment_package_ids_by_role")
        != assignment_registry.package_ids_by_role
        or summary.get("package_metadata_verified") is not True
        or set(summary.get("package_ids", [])) != set(package_ids.values())
        or summary.get("rater_role_coverage") != dict(expected_coverage_counts)
    ):
        raise SystemExit("production ratings do not match the verified ingestion summary")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-dir", required=True, type=Path)
    parser.add_argument("--ratings", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument(
        "--judge-labels",
        type=Path,
        action="append",
        default=None,
        help=(
            "Path to a pinned judge comparator judge_labels.csv (repeatable, one "
            "per judge). Production requires exactly two explicit inputs; a "
            "synthetic run may fall back to <private-dir>/judge_labels.csv."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    private_dir = args.private_dir.resolve()
    judge_label_paths = [path.resolve() for path in (args.judge_labels or [])]
    ratings_path = (args.ratings or private_dir / "processed" / "ratings-long.csv").resolve()
    if not ratings_path.exists():
        raise SystemExit(f"missing ingested Study A ratings: {ratings_path}")
    map_path = private_dir / "row_map.tsv"
    if not map_path.exists():
        raise SystemExit(f"missing private row map: {map_path}")
    schema = load_schema()
    criteria_by_role = primary_criteria(schema)
    source_role_fields = {
        role: field
        for role, role_schema in schema["roles"].items()
        for field in role_schema["fields"]
        if field["name"] == "source_roles"
    }
    map_rows = read_csv(map_path, delimiter="\t")
    map_by_row = {row["row_id"]: row for row in map_rows}
    ratings = read_csv(ratings_path)
    metadata = analysis_metadata(private_dir)
    synthetic = synthetic_fixture_mode(metadata, map_rows)
    validate_ratings_input(
        private_dir=private_dir,
        ratings=ratings,
        ratings_path=ratings_path,
        map_rows=map_rows,
        metadata=metadata,
        schema=schema,
        synthetic=synthetic,
    )
    if synthetic:
        author_path = private_dir / "author_labels.csv"
        author_rows = load_optional_rows(author_path)
        author_by_key = (
            build_unique_lookup(author_rows, kind="author", path=author_path)
            if author_rows
            else {}
        )
        judge_files = judge_label_paths or [private_dir / "judge_labels.csv"]
        judge_inputs = []
        for judge_file in judge_files:
            judge_rows = load_optional_rows(judge_file)
            if judge_rows:
                judge_inputs.append(
                    (judge_file, judge_rows, build_judge_lookup(judge_rows))
                )
    else:
        author_rows, author_by_key, judge_inputs = validate_production_comparison_inputs(
            private_dir=private_dir,
            judge_label_paths=judge_label_paths,
            map_rows=map_rows,
            schema=schema,
        )
    out_dir = (args.out_dir or private_dir / "analysis").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    remove_retired_analysis_outputs(out_dir)

    coverage_rows = derive_evaluator_coverage_rows(ratings, map_rows)
    coverage_path = ratings_path.parent / "rater-role-coverage.csv"
    validate_coverage_sidecar(
        coverage_path,
        load_optional_rows(coverage_path),
        coverage_rows,
    )
    write_csv(
        out_dir / "evaluator-role-coverage.csv",
        EVALUATOR_COVERAGE_FIELDS,
        coverage_rows,
    )

    sessions: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ratings:
        sessions[
            (row["role"], row["rater_id"], row["block_id"], row["source_file"])
        ].append(row)
    burden_rows: list[dict[str, Any]] = []
    for (role, rater_id, block_id, source_file), rows in sorted(sessions.items()):
        timing = {
            (row.get("started_at", ""), row.get("completed_at", ""), row.get("elapsed_seconds", ""))
            for row in rows
        }
        if len(timing) != 1:
            raise SystemExit(f"inconsistent timing metadata within {source_file}")
        started_at, completed_at, elapsed_seconds = timing.pop()
        seconds = int(elapsed_seconds)
        burden_rows.append(
            {
                "role": role,
                "rater_id": rater_id,
                "block_id": block_id,
                "source_file": source_file,
                "started_at": started_at,
                "completed_at": completed_at,
                "elapsed_seconds": seconds,
                "rated_rows": len(rows),
                "seconds_per_rated_row": f"{seconds / len(rows):.1f}" if rows else "",
            }
        )
    write_csv(
        out_dir / "evaluator-burden.csv",
        list(burden_rows[0]) if burden_rows else ["role", "rater_id", "block_id"],
        burden_rows,
    )

    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in ratings:
        for criterion in criteria_by_role.get(row.get("role", ""), []):
            if row.get(criterion, ""):
                grouped[(row["role"], row["row_id"], criterion)].append(row)

    panel_rows: list[dict[str, Any]] = []
    panel_lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    for (role, row_id, criterion), rows in sorted(grouped.items()):
        values = [row[criterion] for row in rows]
        label, agreement_status, modal_support_n, modal_share = panel_modal_summary(
            values
        )
        source = map_by_row[row_id]
        # Flag rows where panelists split across two or more substantive labels.
        # This is a candidate locus of construct, rubric, or rater disagreement;
        # modal aggregation alone should not hide it.
        distinct = set(values)
        substantive_distinct = sorted(distinct - ESCAPE_VALUES)
        substantive_contested = len(substantive_distinct) >= 2
        coherence_flags = sorted(
            {
                flag
                for row in rows
                for flag in split_coherence_flags(row.get(COHERENCE_FLAG_FIELD, ""))
            }
        )
        coherence_flagged_ratings = sum(
            bool(split_coherence_flags(row.get(COHERENCE_FLAG_FIELD, "")))
            for row in rows
        )
        panel_row = {
            "role": role,
            "row_id": row_id,
            "item_id": source["item_id"],
            "model": source["model"],
            "pair_id": source.get("pair_id", ""),
            "phenomenon": source.get("phenomenon", ""),
            "variant": source.get("variant", ""),
            "criterion": criterion,
            "rater_n": len(rows),
            "rater_ids": ";".join(sorted({row["rater_id"] for row in rows})),
            "label_counts": counts_text(row[criterion] for row in rows),
            "panel_modal_label": label,
            "panel_agreement_status": agreement_status,
            "modal_support_n": modal_support_n,
            "support_pattern": f"{modal_support_n}/{len(rows)}",
            "modal_share": f"{modal_share:.3f}",
            "substantive_contested": substantive_contested,
            "substantive_labels": ";".join(substantive_distinct),
            "coherence_flagged_ratings": coherence_flagged_ratings,
            COHERENCE_FLAG_FIELD: ";".join(coherence_flags),
        }
        panel_rows.append(panel_row)
        panel_lookup[(role, row_id, criterion)] = panel_row
    panel_fields = list(panel_rows[0]) if panel_rows else [
        "role",
        "row_id",
        "item_id",
        "model",
        "criterion",
        "panel_modal_label",
        "panel_agreement_status",
        "modal_support_n",
        "support_pattern",
    ]
    write_csv(out_dir / "panel-modal-labels.csv", panel_fields, panel_rows)

    coherence_audit_fields = [
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
    coherence_audit_rows = [
        row for row in ratings if split_coherence_flags(row.get(COHERENCE_FLAG_FIELD, ""))
    ]
    write_csv(
        out_dir / "cross-field-coherence-flags.csv",
        coherence_audit_fields,
        coherence_audit_rows,
    )

    # Panel-label yield is computed over the full presented row set (the row map),
    # not over the rows that happened to get rated. A criterion-row with no
    # ratings is an unrated cell, not an absent one; folding it into an
    # available-case denominator would silently inflate yield (plan blocker 4).
    presented_rows = len(map_by_row)
    agreement_rows: list[dict[str, Any]] = []
    for role, criteria in criteria_by_role.items():
        for criterion in criteria:
            rows = [
                row for row in panel_rows if row["role"] == role and row["criterion"] == criterion
            ]
            modal_shares = [float(row["modal_share"]) for row in rows]
            supported = [
                row
                for row in rows
                if row["panel_agreement_status"] in {"unanimous", "majority"}
            ]
            supported_substantive = sum(
                row["panel_modal_label"] not in ESCAPE_VALUES for row in supported
            )
            supported_escape = len(supported) - supported_substantive
            # Do not collapse unanimous and majority panel support.
            unanimous_substantive = sum(
                row["panel_agreement_status"] == "unanimous"
                and row["panel_modal_label"] not in ESCAPE_VALUES
                for row in supported
            )
            majority_substantive = supported_substantive - unanimous_substantive
            substantive_supported_rows = [
                row for row in supported if row["panel_modal_label"] not in ESCAPE_VALUES
            ]
            support_pattern_fields: dict[str, Any] = {}
            for slug, pattern in SUPPORT_PATTERN_STRATA:
                stratum = [
                    row
                    for row in substantive_supported_rows
                    if support_pattern_bucket(row["support_pattern"]) == pattern
                ]
                support_pattern_fields[f"{slug}_substantive"] = len(stratum)
                support_pattern_fields[
                    f"{slug}_substantive_yield_over_presented"
                ] = f"{len(stratum) / presented_rows:.3f}" if presented_rows else ""
            agreement_rows.append(
                {
                    "role": role,
                    "criterion": criterion,
                    "presented_rows": presented_rows,
                    "rated_rows": len(rows),
                    "unrated_rows": presented_rows - len(rows),
                    "unanimous": sum(
                        row["panel_agreement_status"] == "unanimous" for row in rows
                    ),
                    "majority": sum(
                        row["panel_agreement_status"] == "majority" for row in rows
                    ),
                    "insufficient_raters": sum(
                        row["panel_agreement_status"] == "insufficient_raters" for row in rows
                    ),
                    "ties_or_no_majority": sum(
                        row["panel_agreement_status"] in {"tie", "no_majority"} for row in rows
                    ),
                    "supported_panel_label_rows": len(supported),
                    "supported_substantive_panel_labels": supported_substantive,
                    "unanimous_substantive": unanimous_substantive,
                    "majority_substantive": majority_substantive,
                    **support_pattern_fields,
                    "supported_escape_panel_labels": supported_escape,
                    # Rows where evaluators split across >=2 substantive labels:
                    # a candidate locus of construct, rubric, or rater disagreement,
                    # reported separately and never hidden by the modal label.
                    "substantive_contested": sum(row["substantive_contested"] for row in rows),
                    "coherence_flagged_panel_rows": sum(
                        int(row["coherence_flagged_ratings"]) > 0 for row in rows
                    ),
                    # Planned-primary yield: supported substantive panel labels
                    # over the full presented set. This is a fixed-set fraction.
                    "yield_substantive_over_presented": (
                        f"{supported_substantive / presented_rows:.3f}"
                        if presented_rows
                        else ""
                    ),
                    "mean_modal_share": (
                        f"{sum(modal_shares) / len(modal_shares):.3f}"
                        if modal_shares
                        else ""
                    ),
                }
            )
    # Keep substantive panel disagreement visible as a separate artifact.
    contested_rows = [
        {
            "role": row["role"],
            "criterion": row["criterion"],
            "item_id": row["item_id"],
            "model": row["model"],
            "pair_id": row["pair_id"],
            "rater_n": row["rater_n"],
            "label_counts": row["label_counts"],
            "substantive_labels": row["substantive_labels"],
            "panel_agreement_status": row["panel_agreement_status"],
            "panel_modal_label": row["panel_modal_label"],
            "modal_support_n": row["modal_support_n"],
            "support_pattern": row["support_pattern"],
            "coherence_flagged_ratings": row["coherence_flagged_ratings"],
            COHERENCE_FLAG_FIELD: row[COHERENCE_FLAG_FIELD],
            "feeds_planned_primary": row["panel_agreement_status"]
            in {"unanimous", "majority"}
            and row["panel_modal_label"] not in ESCAPE_VALUES,
        }
        for row in panel_rows
        if row["substantive_contested"]
    ]
    write_csv(
        out_dir / "contested-items.csv",
        list(contested_rows[0]) if contested_rows else ["role", "criterion", "item_id"],
        contested_rows,
    )
    write_csv(
        out_dir / "agreement-by-criterion.csv",
        list(agreement_rows[0]) if agreement_rows else ["role", "criterion", "rows"],
        agreement_rows,
    )

    # Descriptive paired panel-outcome divergence. Both the prompt and observed
    # response differ across variants, so this is response-mediated and is neither
    # necessary nor sufficient for authority sensitivity. Preserve the complete
    # transitions in authored item-ID order instead of collapsing changes into a rate.
    divergence_rows: list[dict[str, Any]] = []
    transition_rows: list[dict[str, Any]] = []
    for role, criteria in PAIR_DIVERGENCE_CRITERIA.items():
        for criterion in criteria:
            cells: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
            for row in panel_rows:
                if (
                    row["role"] == role
                    and row["criterion"] == criterion
                    and row["panel_agreement_status"] in {"unanimous", "majority"}
                    and row["panel_modal_label"] not in ESCAPE_VALUES
                    and row.get("pair_id")
                ):
                    cells[(row["pair_id"], row["model"])][row["variant"]] = row
            for exclude_p008 in (False, True):
                scope = "excl_P008" if exclude_p008 else "all_pairs"
                eligible = [
                    (pair_id, model, cell)
                    for (pair_id, model), cell in sorted(cells.items())
                    if len(cell) == 2
                    and not (exclude_p008 and pair_id in PAIRED_CONTRAST_EXCLUDE)
                ]
                divergent = 0
                for pair_id, model, cell in eligible:
                    row_a, row_b = sorted(
                        cell.values(), key=lambda row: (row["item_id"], row["variant"])
                    )
                    variant_a = row_a["variant"]
                    variant_b = row_b["variant"]
                    diverged = row_a["panel_modal_label"] != row_b["panel_modal_label"]
                    divergent += int(diverged)
                    transition_rows.append(
                        {
                            "role": role,
                            "criterion": criterion,
                            "scope": scope,
                            "pair_id": pair_id,
                            "model": model,
                            "order_basis": "item_id",
                            "variant_a": variant_a,
                            "item_id_a": row_a["item_id"],
                            "panel_label_a": row_a["panel_modal_label"],
                            "variant_b": variant_b,
                            "item_id_b": row_b["item_id"],
                            "panel_label_b": row_b["panel_modal_label"],
                            "diverged": int(diverged),
                        }
                    )
                divergence_rows.append(
                    {
                        "role": role,
                        "criterion": criterion,
                        "scope": scope,
                        "eligible_pair_model_cells": len(eligible),
                        "divergent_cells": divergent,
                        "divergence_rate": f"{divergent / len(eligible):.3f}"
                        if eligible
                        else "",
                    }
                )
    write_csv(
        out_dir / "paired-panel-outcome-divergence.csv",
        list(divergence_rows[0])
        if divergence_rows
        else ["role", "criterion", "scope", "eligible_pair_model_cells"],
        divergence_rows,
    )
    write_csv(
        out_dir / "paired-panel-outcome-transitions.csv",
        list(transition_rows[0])
        if transition_rows
        else [
            "role",
            "criterion",
            "scope",
            "pair_id",
            "model",
            "order_basis",
            "variant_a",
            "item_id_a",
            "panel_label_a",
            "variant_b",
            "item_id_b",
            "panel_label_b",
            "diverged",
        ],
        transition_rows,
    )

    source_role_groups: dict[tuple[str, str], list[tuple[dict[str, str], set[str], str]]] = (
        defaultdict(list)
    )
    for row in ratings:
        role = row.get("role", "")
        field = source_role_fields.get(role)
        if field is None:
            continue
        options = list(field.get("options") or [])
        selected, signature = parse_source_roles(
            row.get("source_roles", ""),
            options,
            context=f"{role}/{row.get('rater_id', '')}/{row.get('row_id', '')}",
        )
        source_role_groups[(role, row["row_id"])].append((row, set(selected), signature))

    source_exact_rows: list[dict[str, Any]] = []
    source_exact_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    source_binary_rows: list[dict[str, Any]] = []
    for (role, row_id), rated_sets in sorted(source_role_groups.items()):
        source = map_by_row[row_id]
        signatures = [signature for _, _, signature in rated_sets]
        (
            exact_panel_label,
            exact_agreement_status,
            exact_modal_support_n,
            exact_modal_share,
        ) = panel_modal_summary(signatures)
        exact_row = {
            "role": role,
            "row_id": row_id,
            "item_id": source["item_id"],
            "model": source["model"],
            "pair_id": source.get("pair_id", ""),
            "phenomenon": source.get("phenomenon", ""),
            "variant": source.get("variant", ""),
            "criterion": "source_roles_exact_set",
            "rater_n": len(rated_sets),
            "rater_ids": ";".join(sorted({row["rater_id"] for row, _, _ in rated_sets})),
            "set_counts": source_role_set_counts(signatures),
            "exact_set_panel_modal_label": exact_panel_label,
            "panel_agreement_status": exact_agreement_status,
            "modal_support_n": exact_modal_support_n,
            "support_pattern": f"{exact_modal_support_n}/{len(rated_sets)}",
            "modal_share": f"{exact_modal_share:.3f}",
        }
        source_exact_rows.append(exact_row)
        source_exact_lookup[(role, row_id)] = exact_row

        options = list(source_role_fields[role].get("options") or [])
        for source_role in options:
            binary_values = [
                "selected" if source_role in selected else "not_selected"
                for _, selected, _ in rated_sets
            ]
            (
                binary_panel_label,
                binary_agreement_status,
                binary_modal_support_n,
                binary_modal_share,
            ) = panel_modal_summary(binary_values)
            selected_n = sum(value == "selected" for value in binary_values)
            source_binary_rows.append(
                {
                    "role": role,
                    "row_id": row_id,
                    "item_id": source["item_id"],
                    "model": source["model"],
                    "pair_id": source.get("pair_id", ""),
                    "phenomenon": source.get("phenomenon", ""),
                    "variant": source.get("variant", ""),
                    "source_role": source_role,
                    "rater_n": len(rated_sets),
                    "rater_ids": ";".join(
                        sorted({row["rater_id"] for row, _, _ in rated_sets})
                    ),
                    "selected_n": selected_n,
                    "not_selected_n": len(binary_values) - selected_n,
                    "selection_share": f"{selected_n / len(binary_values):.3f}",
                    "binary_panel_modal_label": binary_panel_label,
                    "panel_agreement_status": binary_agreement_status,
                    "modal_support_n": binary_modal_support_n,
                    "support_pattern": f"{binary_modal_support_n}/{len(rated_sets)}",
                    "modal_share": f"{binary_modal_share:.3f}",
                }
            )

    source_exact_fields = [
        "role",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        "criterion",
        "rater_n",
        "rater_ids",
        "set_counts",
        "exact_set_panel_modal_label",
        "panel_agreement_status",
        "modal_support_n",
        "support_pattern",
        "modal_share",
    ]
    write_csv(
        out_dir / "source-roles-exact-set-panel-label.csv",
        list(source_exact_rows[0]) if source_exact_rows else source_exact_fields,
        source_exact_rows,
    )

    source_exact_agreement_rows: list[dict[str, Any]] = []
    exact_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in source_exact_rows:
        exact_groups[row["role"]].append(row)
    for role, rows in sorted(exact_groups.items()):
        modal_shares = [float(row["modal_share"]) for row in rows]
        source_exact_agreement_rows.append(
            {
                "role": role,
                "criterion": "source_roles_exact_set",
                "rows": len(rows),
                "unanimous": sum(
                    row["panel_agreement_status"] == "unanimous" for row in rows
                ),
                "majority": sum(
                    row["panel_agreement_status"] == "majority" for row in rows
                ),
                "insufficient_raters": sum(
                    row["panel_agreement_status"] == "insufficient_raters" for row in rows
                ),
                "ties_or_no_majority": sum(
                    row["panel_agreement_status"] in {"tie", "no_majority"}
                    for row in rows
                ),
                "mean_modal_share": f"{sum(modal_shares) / len(modal_shares):.3f}",
                "supported_panel_label_rows": sum(
                    row["panel_agreement_status"] in {"unanimous", "majority"}
                    for row in rows
                ),
            }
        )
    write_csv(
        out_dir / "source-roles-exact-set-agreement.csv",
        list(source_exact_agreement_rows[0])
        if source_exact_agreement_rows
        else ["role", "criterion", "rows"],
        source_exact_agreement_rows,
    )

    source_binary_fields = [
        "role",
        "row_id",
        "item_id",
        "model",
        "pair_id",
        "phenomenon",
        "variant",
        "source_role",
        "rater_n",
        "rater_ids",
        "selected_n",
        "not_selected_n",
        "selection_share",
        "binary_panel_modal_label",
        "panel_agreement_status",
        "modal_support_n",
        "support_pattern",
        "modal_share",
    ]
    write_csv(
        out_dir / "source-roles-per-label-panel-label.csv",
        list(source_binary_rows[0]) if source_binary_rows else source_binary_fields,
        source_binary_rows,
    )

    source_binary_agreement_rows: list[dict[str, Any]] = []
    binary_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in source_binary_rows:
        binary_groups[(row["role"], row["source_role"])].append(row)
    for (role, source_role), rows in sorted(binary_groups.items()):
        selected_ratings = sum(int(row["selected_n"]) for row in rows)
        total_ratings = sum(int(row["rater_n"]) for row in rows)
        modal_shares = [float(row["modal_share"]) for row in rows]
        source_binary_agreement_rows.append(
            {
                "role": role,
                "source_role": source_role,
                "rows": len(rows),
                "selected_ratings": selected_ratings,
                "total_ratings": total_ratings,
                "selection_prevalence": f"{selected_ratings / total_ratings:.3f}"
                if total_ratings
                else "",
                "unanimous": sum(
                    row["panel_agreement_status"] == "unanimous" for row in rows
                ),
                "majority": sum(
                    row["panel_agreement_status"] == "majority" for row in rows
                ),
                "insufficient_raters": sum(
                    row["panel_agreement_status"] == "insufficient_raters" for row in rows
                ),
                "ties_or_no_majority": sum(
                    row["panel_agreement_status"] in {"tie", "no_majority"}
                    for row in rows
                ),
                "supported_selected_panel_label_rows": sum(
                    row["panel_agreement_status"] in {"unanimous", "majority"}
                    and row["binary_panel_modal_label"] == "selected"
                    for row in rows
                ),
                "supported_not_selected_panel_label_rows": sum(
                    row["panel_agreement_status"] in {"unanimous", "majority"}
                    and row["binary_panel_modal_label"] == "not_selected"
                    for row in rows
                ),
                "supported_panel_label_rows": sum(
                    row["panel_agreement_status"] in {"unanimous", "majority"}
                    for row in rows
                ),
                "mean_modal_share": f"{sum(modal_shares) / len(modal_shares):.3f}",
            }
        )
    write_csv(
        out_dir / "source-roles-per-label-agreement.csv",
        list(source_binary_agreement_rows[0])
        if source_binary_agreement_rows
        else ["role", "source_role", "rows"],
        source_binary_agreement_rows,
    )

    clarity_exact_rows: list[dict[str, Any]] = []
    for (role, row_id), exact in sorted(source_exact_lookup.items()):
        clarity = panel_lookup.get((role, row_id, "source_role_clarity"))
        if clarity is None:
            continue
        clarity_supported = clarity["panel_agreement_status"] in {"unanimous", "majority"}
        exact_supported = exact["panel_agreement_status"] in {"unanimous", "majority"}
        clarity_uncertain = clarity["panel_modal_label"] in {
            "genuinely_ambiguous",
            "insufficient_visible_context",
        }
        if not clarity_supported:
            diagnostic = "clarity_no_supported_panel_label"
        elif clarity_uncertain:
            diagnostic = "clarity_ambiguous_or_insufficient"
        elif exact_supported:
            diagnostic = "clarity_other_with_supported_exact_set_panel_label"
        else:
            diagnostic = "clarity_other_without_supported_exact_set_panel_label"
        clarity_exact_rows.append(
            {
                "role": role,
                "row_id": row_id,
                "item_id": exact["item_id"],
                "model": exact["model"],
                "phenomenon": exact["phenomenon"],
                "clarity_panel_modal_label": clarity["panel_modal_label"],
                "clarity_panel_agreement_status": clarity["panel_agreement_status"],
                "exact_set_panel_modal_label": exact["exact_set_panel_modal_label"],
                "exact_set_panel_agreement_status": exact["panel_agreement_status"],
                "diagnostic": diagnostic,
            }
        )
    write_csv(
        out_dir / "source-role-clarity-vs-exact-set-agreement.csv",
        list(clarity_exact_rows[0])
        if clarity_exact_rows
        else [
            "role",
            "row_id",
            "clarity_panel_modal_label",
            "clarity_panel_agreement_status",
            "exact_set_panel_modal_label",
            "exact_set_panel_agreement_status",
            "diagnostic",
        ],
        clarity_exact_rows,
    )

    comparable = COMPARABLE
    author_comparison_rows: list[dict[str, Any]] = []
    for panel_row in panel_rows:
        role, criterion = panel_row["role"], panel_row["criterion"]
        if criterion not in comparable.get(role, []):
            continue
        author = author_by_key.get((panel_row["item_id"], panel_row["model"]), {})
        author_label_raw = author.get(criterion, "")
        author_comparison_label = normalize_author_label(criterion, author_label_raw)
        panel_label = panel_row["panel_modal_label"]
        if not author_label_raw:
            status = "author_label_not_available"
        elif panel_row["panel_agreement_status"] not in {"unanimous", "majority"}:
            status = "no_supported_panel_label"
        elif panel_label in ESCAPE_VALUES:
            status = "escape_panel_label_excluded"
        elif author_comparison_label == panel_label:
            status = "author_panel_match"
        else:
            status = "author_panel_mismatch"
        author_comparison_rows.append(
            {
                **panel_row,
                "author_provisional_label_raw": author_label_raw,
                "author_normalized_comparison_label": author_comparison_label,
                "comparison_status": status,
            }
        )
    author_comparison_fields = (
        list(author_comparison_rows[0])
        if author_comparison_rows
        else ["role", "row_id", "criterion"]
    )
    write_csv(
        out_dir / "author-vs-panel-comparison.csv",
        author_comparison_fields,
        author_comparison_rows,
    )
    author_confusion = Counter(
        (
            row["role"],
            row["criterion"],
            row["panel_modal_label"],
            row["author_normalized_comparison_label"],
        )
        for row in author_comparison_rows
        if row["comparison_status"] in {"author_panel_match", "author_panel_mismatch"}
    )
    author_confusion_rows = [
        {
            "role": role,
            "criterion": criterion,
            "panel_modal_label": panel_label,
            "author_normalized_comparison_label": author,
            "rows": count,
        }
        for (role, criterion, panel_label, author), count in sorted(author_confusion.items())
    ]
    write_csv(
        out_dir / "author-vs-panel-confusion.csv",
        list(author_confusion_rows[0]) if author_confusion_rows else ["role", "criterion", "rows"],
        author_confusion_rows,
    )
    author_summary_rows: list[dict[str, Any]] = []
    author_groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in author_comparison_rows:
        author_groups[(row["role"], row["criterion"])].append(row)
    for (role, criterion), rows in sorted(author_groups.items()):
        comparable_rows = [
            row
            for row in rows
            if row["comparison_status"] in {"author_panel_match", "author_panel_mismatch"}
        ]
        mismatches = sum(
            row["comparison_status"] == "author_panel_mismatch" for row in comparable_rows
        )
        matches = len(comparable_rows) - mismatches
        unanimous_comparable = [
            row
            for row in comparable_rows
            if row["panel_agreement_status"] == "unanimous"
        ]
        majority_comparable = [
            row
            for row in comparable_rows
            if row["panel_agreement_status"] == "majority"
        ]
        unanimous_mismatches = sum(
            row["comparison_status"] == "author_panel_mismatch"
            for row in unanimous_comparable
        )
        majority_mismatches = sum(
            row["comparison_status"] == "author_panel_mismatch"
            for row in majority_comparable
        )
        unanimous_author_matches = len(unanimous_comparable) - unanimous_mismatches
        majority_author_matches = len(majority_comparable) - majority_mismatches
        # For policy_compliance only, report author–panel agreement on the
        # policy-at-stake subset and the not-at-stake share. The other criteria do
        # not use the NOT_AT_STAKE vocabulary, so no pseudo-subset is constructed.
        at_stake: list[dict[str, Any]] = []
        at_stake_mismatches = 0
        at_stake_matches = 0
        if criterion == "policy_compliance":
            at_stake = [
                row
                for row in comparable_rows
                if row["panel_modal_label"] != NOT_AT_STAKE
            ]
            at_stake_mismatches = sum(
                row["comparison_status"] == "author_panel_mismatch" for row in at_stake
            )
            at_stake_matches = len(at_stake) - at_stake_mismatches
        author_support_fields: dict[str, Any] = {}
        for slug, pattern in SUPPORT_PATTERN_STRATA:
            author_support_fields.update(
                author_stratum_fields(
                    slug,
                    [
                        row
                        for row in comparable_rows
                        if support_pattern_bucket(row["support_pattern"]) == pattern
                    ],
                )
            )
        at_stake_split_fields: dict[str, Any] = {}
        for prefix, status in (
            ("at_stake_unanimous", "unanimous"),
            ("at_stake_majority", "majority"),
        ):
            at_stake_split_fields.update(
                author_stratum_fields(
                    prefix,
                    [
                        row
                        for row in at_stake
                        if row["panel_agreement_status"] == status
                    ],
                )
                if criterion == "policy_compliance"
                else blank_author_stratum_fields(prefix)
            )
        for slug, pattern in SUPPORT_PATTERN_STRATA:
            prefix = f"at_stake_{slug}"
            at_stake_split_fields.update(
                author_stratum_fields(
                    prefix,
                    [
                        row
                        for row in at_stake
                        if support_pattern_bucket(row["support_pattern"]) == pattern
                    ],
                )
                if criterion == "policy_compliance"
                else blank_author_stratum_fields(prefix)
            )
        author_summary_rows.append(
            {
                "role": role,
                "criterion": criterion,
                "supported_panel_label_rows": len(comparable_rows),
                "author_panel_match": matches,
                "author_panel_agreement_rate": (
                    f"{matches / len(comparable_rows):.3f}" if comparable_rows else ""
                ),
                "author_panel_mismatch": mismatches,
                "author_panel_mismatch_rate": f"{mismatches / len(comparable_rows):.3f}"
                if comparable_rows
                else "",
                "at_stake_rows": (
                    len(at_stake) if criterion == "policy_compliance" else ""
                ),
                "not_at_stake_share": (
                    f"{(len(comparable_rows) - len(at_stake)) / len(comparable_rows):.3f}"
                    if comparable_rows
                    else ""
                )
                if criterion == "policy_compliance"
                else "",
                "at_stake_author_panel_mismatch": (
                    at_stake_mismatches if criterion == "policy_compliance" else ""
                ),
                "at_stake_author_panel_mismatch_rate": (
                    f"{at_stake_mismatches / len(at_stake):.3f}"
                )
                if criterion == "policy_compliance" and at_stake
                else "",
                "at_stake_author_panel_match": (
                    at_stake_matches if criterion == "policy_compliance" else ""
                ),
                "at_stake_author_panel_agreement_rate": (
                    f"{at_stake_matches / len(at_stake):.3f}"
                    if at_stake
                    else ""
                )
                if criterion == "policy_compliance"
                else "",
                # Split author–panel agreement by unanimous versus majority panel
                # support so the two support levels remain visible.
                "unanimous_panel_comparable": len(unanimous_comparable),
                "unanimous_author_panel_match": unanimous_author_matches,
                "unanimous_author_panel_mismatch": unanimous_mismatches,
                "unanimous_author_panel_agreement_rate": (
                    f"{unanimous_author_matches / len(unanimous_comparable):.3f}"
                    if unanimous_comparable
                    else ""
                ),
                "majority_panel_comparable": len(majority_comparable),
                "majority_author_panel_match": majority_author_matches,
                "majority_author_panel_mismatch": majority_mismatches,
                "majority_author_panel_agreement_rate": (
                    f"{majority_author_matches / len(majority_comparable):.3f}"
                    if majority_comparable
                    else ""
                ),
                "unanimous_author_panel_mismatch_rate": (
                    f"{unanimous_mismatches / len(unanimous_comparable):.3f}"
                    if unanimous_comparable
                    else ""
                ),
                "majority_author_panel_mismatch_rate": (
                    f"{majority_mismatches / len(majority_comparable):.3f}"
                    if majority_comparable
                    else ""
                ),
                **author_support_fields,
                **at_stake_split_fields,
                "no_supported_panel_label": sum(
                    row["comparison_status"] == "no_supported_panel_label" for row in rows
                ),
            }
        )
    write_csv(
        out_dir / "author-vs-panel-summary.csv",
        list(author_summary_rows[0]) if author_summary_rows else ["role", "criterion"],
        author_summary_rows,
    )

    # Production comparison inputs were validated before any analysis artifact
    # was written. Synthetic fixtures retain their explicit single-file fallback.
    judge_summary_rows: list[dict[str, Any]] = []
    judge_class_rows: list[dict[str, Any]] = []
    judge_confusion_rows: list[dict[str, Any]] = []
    for judge_file, judge_rows, judge_by_key in judge_inputs:
        judge_name = judge_rows[0].get("judge_model") or Path(judge_file).stem
        judge_confusion: dict[
            tuple[str, str, str, str], list[dict[str, Any]]
        ] = defaultdict(list)
        for role, criteria in comparable.items():
            for criterion in criteria:
                # Predictions present for this criterion, independent of whether
                # the panel produced a unanimous- or majority-supported label.
                comparator_parse_failure_rows = sum(
                    bool(row.get("parse_error", "").strip()) for row in judge_rows
                )
                predictions_present = sum(
                    1
                    for row in panel_rows
                    if row["role"] == role
                    and row["criterion"] == criterion
                    and judge_value(judge_by_key.get((row["item_id"], row["model"]), {}), criterion)
                )
                panel_substantive = [
                    row
                    for row in panel_rows
                    if row["role"] == role
                    and row["criterion"] == criterion
                    and row["panel_agreement_status"] in {"unanimous", "majority"}
                    and row["panel_modal_label"] not in ESCAPE_VALUES
                ]
                eligible = [
                    row
                    for row in panel_substantive
                    if judge_value(
                        judge_by_key.get((row["item_id"], row["model"]), {}), criterion
                    )
                ]
                panel_rows_unscored_with_explicit_parse_error = sum(
                    not judge_value(
                        judge_by_key.get((row["item_id"], row["model"]), {}), criterion
                    )
                    and bool(
                        judge_by_key.get(
                            (row["item_id"], row["model"]), {}
                        ).get("parse_error", "").strip()
                    )
                    for row in panel_substantive
                )
                matched = sum(
                    judge_value(judge_by_key[(row["item_id"], row["model"])], criterion)
                    == row["panel_modal_label"]
                    for row in eligible
                )
                unanimous_eligible = [
                    row
                    for row in eligible
                    if row["panel_agreement_status"] == "unanimous"
                ]
                majority_eligible = [
                    row
                    for row in eligible
                    if row["panel_agreement_status"] == "majority"
                ]
                unanimous_matches = sum(
                    judge_value(
                        judge_by_key[(row["item_id"], row["model"])], criterion
                    )
                    == row["panel_modal_label"]
                    for row in unanimous_eligible
                )
                majority_matches = sum(
                    judge_value(
                        judge_by_key[(row["item_id"], row["model"])], criterion
                    )
                    == row["panel_modal_label"]
                    for row in majority_eligible
                )
                for row in eligible:
                    judge_confusion[
                        (
                            role,
                            criterion,
                            row["panel_modal_label"],
                            judge_value(judge_by_key[(row["item_id"], row["model"])], criterion),
                        )
                    ].append(row)
                availability = "available" if predictions_present else "no_predictions"
                (
                    panel_counts,
                    majority_panel_classes,
                    majority_panel_class_count,
                    majority_panel_class_share,
                ) = panel_class_summary(
                    row["panel_modal_label"] for row in eligible
                )
                # The 54 rows are not independent (18 items, 9 pairs, 3 outputs
                # each). Report item-macro judge–panel agreement and cluster counts
                # alongside the descriptive row-micro agreement.
                by_item: dict[str, list[bool]] = defaultdict(list)
                for row in eligible:
                    hit = (
                        judge_value(judge_by_key[(row["item_id"], row["model"])], criterion)
                        == row["panel_modal_label"]
                    )
                    by_item[row["item_id"]].append(hit)
                item_agreements = [sum(hits) / len(hits) for hits in by_item.values()]
                item_macro = (
                    sum(item_agreements) / len(item_agreements) if item_agreements else 0.0
                )
                n_pairs = len({row.get("pair_id", "") for row in eligible if row.get("pair_id")})
                judge_support_fields: dict[str, Any] = {}
                for slug, pattern in SUPPORT_PATTERN_STRATA:
                    judge_support_fields.update(
                        judge_stratum_fields(
                            slug,
                            [
                                row
                                for row in eligible
                                if support_pattern_bucket(row["support_pattern"])
                                == pattern
                            ],
                            judge_by_key,
                            criterion,
                        )
                    )
                judge_summary_rows.append(
                    {
                        "judge": judge_name,
                        "role": role,
                        "criterion": criterion,
                        "panel_presented_rows": presented_rows,
                        "panel_substantive_label_rows": len(panel_substantive),
                        "panel_substantive_label_yield": (
                            f"{len(panel_substantive) / presented_rows:.3f}"
                            if presented_rows
                            else ""
                        ),
                        "judge_scored_panel_label_rows": len(eligible),
                        "comparator_parse_failure_rows": comparator_parse_failure_rows,
                        "panel_rows_unscored_with_explicit_parse_error": (
                            panel_rows_unscored_with_explicit_parse_error
                        ),
                        "eligible_unanimous_panel_labels": len(unanimous_eligible),
                        "unanimous_judge_panel_matches": unanimous_matches,
                        "unanimous_judge_panel_agreement_rate": (
                            f"{unanimous_matches / len(unanimous_eligible):.3f}"
                            if unanimous_eligible
                            else ""
                        ),
                        "eligible_majority_panel_labels": len(majority_eligible),
                        "majority_judge_panel_matches": majority_matches,
                        "majority_judge_panel_agreement_rate": (
                            f"{majority_matches / len(majority_eligible):.3f}"
                            if majority_eligible
                            else ""
                        ),
                        **judge_support_fields,
                        "judge_panel_matches": matched,
                        "judge_panel_agreement": (
                            f"{matched / len(eligible):.3f}" if eligible else ""
                        ),
                        "item_macro_panel_agreement": (
                            f"{item_macro:.3f}" if eligible else ""
                        ),
                        "n_items": len(by_item),
                        "n_pairs": n_pairs,
                        "majority_panel_class_share": (
                            f"{majority_panel_class_share:.3f}" if eligible else ""
                        ),
                        "majority_panel_classes": ";".join(majority_panel_classes),
                        "availability": availability,
                    }
                )
                labels = sorted({row["panel_modal_label"] for row in eligible})
                for label in labels:
                    cases = [row for row in eligible if row["panel_modal_label"] == label]
                    recovered = sum(
                        judge_value(
                            judge_by_key[(row["item_id"], row["model"])], criterion
                        )
                        == label
                        for row in cases
                    )
                    class_split_fields: dict[str, Any] = {}
                    for prefix, status in (
                        ("unanimous", "unanimous"),
                        ("majority", "majority"),
                    ):
                        class_split_fields.update(
                            judge_class_stratum_fields(
                                prefix,
                                [
                                    row
                                    for row in cases
                                    if row["panel_agreement_status"] == status
                                ],
                                judge_by_key,
                                criterion,
                            )
                        )
                    for slug, pattern in SUPPORT_PATTERN_STRATA:
                        class_split_fields.update(
                            judge_class_stratum_fields(
                                slug,
                                [
                                    row
                                    for row in cases
                                    if support_pattern_bucket(row["support_pattern"])
                                    == pattern
                                ],
                                judge_by_key,
                                criterion,
                            )
                        )
                    judge_class_rows.append(
                        {
                            "judge": judge_name,
                            "role": role,
                            "criterion": criterion,
                            "panel_class": label,
                            "is_minority_panel_class": (
                                panel_counts[label] < majority_panel_class_count
                            ),
                            "panel_class_rows": len(cases),
                            "judge_panel_matches": recovered,
                            "panel_class_agreement_rate": (
                                f"{recovered / len(cases):.3f}" if cases else ""
                            ),
                            **class_split_fields,
                        }
                    )
        for (role, criterion, panel_label, judge), cases in sorted(
            judge_confusion.items()
        ):
            confusion_split_fields = {
                "unanimous_rows": sum(
                    row["panel_agreement_status"] == "unanimous" for row in cases
                ),
                "majority_rows": sum(
                    row["panel_agreement_status"] == "majority" for row in cases
                ),
            }
            for slug, pattern in SUPPORT_PATTERN_STRATA:
                confusion_split_fields[f"{slug}_rows"] = sum(
                    support_pattern_bucket(row["support_pattern"]) == pattern
                    for row in cases
                )
            judge_confusion_rows.append(
                {
                    "judge": judge_name,
                    "role": role,
                    "criterion": criterion,
                    "panel_modal_label": panel_label,
                    "judge_label": judge,
                    "rows": len(cases),
                    **confusion_split_fields,
                }
            )
    write_csv(
        out_dir / "judge-vs-panel-summary.csv",
        list(judge_summary_rows[0]) if judge_summary_rows else ["judge", "role", "criterion"],
        judge_summary_rows,
    )
    write_csv(
        out_dir / "judge-panel-class-agreement.csv",
        list(judge_class_rows[0]) if judge_class_rows else ["judge", "role", "criterion"],
        judge_class_rows,
    )
    write_csv(
        out_dir / "judge-vs-panel-confusion.csv",
        list(judge_confusion_rows[0])
        if judge_confusion_rows
        else ["judge", "role", "criterion", "rows"],
        judge_confusion_rows,
    )

    by_row: dict[str, dict[tuple[str, str], dict[str, Any]]] = defaultdict(dict)
    for panel_row in panel_rows:
        by_row[panel_row["row_id"]][(panel_row["role"], panel_row["criterion"])] = panel_row
    cross_rows: list[dict[str, Any]] = []
    panel_review_rows: list[dict[str, Any]] = []
    for row_id, evidence in sorted(by_row.items()):
        task = evidence.get(("linguistic_task", "task_success"), {})
        policy = evidence.get(("policy_safety", "policy_compliance"), {})
        if task and policy:
            relation = "same_direction_or_not_comparable"
            if (
                task["panel_modal_label"] == "success"
                and policy["panel_modal_label"] == "noncompliant"
            ):
                relation = "task_success_with_policy_noncompliance"
            elif (
                task["panel_modal_label"] in {"partial", "failure"}
                and policy["panel_modal_label"] == "compliant"
            ):
                relation = "task_failure_with_policy_compliance"
            cross_rows.append(
                {
                    "row_id": row_id,
                    "item_id": task["item_id"],
                    "model": task["model"],
                    "phenomenon": task["phenomenon"],
                    "task_success_panel_modal_label": task["panel_modal_label"],
                    "task_panel_agreement_status": task["panel_agreement_status"],
                    "policy_compliance_panel_modal_label": policy["panel_modal_label"],
                    "policy_panel_agreement_status": policy["panel_agreement_status"],
                    "cross_criterion_pattern": relation,
                }
            )
        for panel_row in evidence.values():
            if panel_row["panel_agreement_status"] not in {
                "unanimous",
                "majority",
            } or panel_row["panel_modal_label"] in {
                "item_problem",
                "policy_ambiguous",
                "genuinely_ambiguous",
                "insufficient_visible_context",
            }:
                panel_review_rows.append(panel_row)
    write_csv(
        out_dir / "linguistic-policy-patterns.csv",
        list(cross_rows[0]) if cross_rows else ["row_id", "item_id", "model"],
        cross_rows,
    )
    write_csv(
        out_dir / "panel-disagreement-or-ambiguous-rows.csv",
        panel_fields,
        panel_review_rows,
    )

    phenomenon_rows: list[dict[str, Any]] = []
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for panel_row in panel_rows:
        groups[(panel_row["phenomenon"], panel_row["role"], panel_row["criterion"])].append(
            panel_row
        )
    for (phenomenon, role, criterion), rows in sorted(groups.items()):
        phenomenon_rows.append(
            {
                "phenomenon": phenomenon,
                "role": role,
                "criterion": criterion,
                "rows": len(rows),
                "supported_panel_label_rows": sum(
                    row["panel_agreement_status"] in {"unanimous", "majority"}
                    for row in rows
                ),
                "panel_modal_label_counts": counts_text(
                    row["panel_modal_label"] for row in rows
                ),
            }
        )
    write_csv(
        out_dir / "phenomenon-summary.csv",
        list(phenomenon_rows[0]) if phenomenon_rows else ["phenomenon", "role", "criterion"],
        phenomenon_rows,
    )

    prefix = "SYNTHETIC TEST RUN. " if synthetic else ""
    author_panel_mismatches = sum(
        row["comparison_status"] == "author_panel_mismatch"
        for row in author_comparison_rows
    )
    supported_panel_labels = sum(
        row["panel_agreement_status"] in {"unanimous", "majority"} for row in panel_rows
    )
    supported_exact_set_panel_labels = sum(
        row["panel_agreement_status"] in {"unanimous", "majority"}
        for row in source_exact_rows
    )
    coverage_counts = Counter(row["coverage_status"] for row in coverage_rows)
    coherence_counts = Counter(
        flag
        for row in coherence_audit_rows
        for flag in split_coherence_flags(row.get(COHERENCE_FLAG_FIELD, ""))
    )
    coverage_line = (
        "- Evaluator-role coverage: "
        + "; ".join(
            f"{status}={coverage_counts[status]}" for status in sorted(coverage_counts)
        )
        + "; see `evaluator-role-coverage.csv`."
        if coverage_rows
        else "- Evaluator-role coverage was unavailable beside the ratings input."
    )
    source_role_lines = (
        [
            "- Source-role exact-set panel-label rows: "
            f"{len(source_exact_rows)}; unanimous- or majority-supported: "
            f"{supported_exact_set_panel_labels}.",
            "- Source-role per-label binary panel-label rows: "
            f"{len(source_binary_rows)} across "
            f"{len(source_binary_agreement_rows)} labels.",
            "- Source-role multiplicity, exact-set disagreement, and "
            "source-role ambiguity are reported separately.",
        ]
        if source_exact_rows
        else []
    )
    write_markdown(
        out_dir / "analysis-readout.md",
        [
            "# Study A Independent-Panel Reassessment Readout",
            "",
            f"{prefix}This report preserves role-specific criteria and does not "
            "create a combined score.",
            "",
            f"- Ratings ingested: {len(ratings)}.",
            f"- Criterion-level panel-label rows: {len(panel_rows)}; unanimous- or "
            f"majority-supported: {supported_panel_labels}.",
            coverage_line,
            *source_role_lines,
            "- Minimum panel ratings required for a unanimous- or "
            f"majority-supported panel label: {MIN_PANEL_RATERS}.",
            "- Historical safety-risk severity and risk-type labels are not "
            "compared to the revised visible-boundary fields.",
            f"- Author–panel mismatches: {author_panel_mismatches}.",
            f"- Rows requiring panel-disagreement or ambiguity review: {len(panel_review_rows)}.",
            "- Raw ratings carrying boundary status/type coherence flags: "
            f"{len(coherence_audit_rows)}"
            + (
                " (" + "; ".join(
                    f"{flag}={coherence_counts[flag]}" for flag in sorted(coherence_counts)
                ) + ")."
                if coherence_counts
                else "."
            ),
            f"- Completed rating blocks with retained burden timing: {len(burden_rows)}.",
            "",
            "Author–panel mismatch identifies a candidate locus of construct, "
            "rubric, or rater disagreement; it does not make the panel label "
            "ground truth or overwrite the frozen author snapshot. Failure "
            "attribution remains out of first-pass analysis. Timing estimates "
            "describe form burden, not evaluator performance or representativeness.",
        ],
    )
    print(f"Wrote Study A analysis to {out_dir}")
    if synthetic:
        print("Synthetic workflow only: do not treat these outputs as empirical findings.")


if __name__ == "__main__":
    main()
