#!/usr/bin/env python3
"""Read-only Study A gate for opening external evaluator returns.

The gate requires a verified stamp 2, a byte-identical tracked manifest at
HEAD, an annotated freeze tag at that exact commit, at least three strictly
registered assignments per role, exact finalized material hashes, an
access-controlled return channel, and a hash-bound written Humber scope
determination or REB approval. The assignment attestation binds the registry's
bytes and checks its internal IDs; it does not establish the real-world
identity or disjointness of the people behind those IDs. It never creates or
changes any of these records.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
from typing import Any

import build_study_a_manifest as freeze_manifest
from check_study_a_freeze_ready import check_freeze_ready
from validate_study_a_assignments import verify_assignment_attestation


CONFIG_VERSION = 3
EVIDENCE_DIRECTORY = "evidence"
PRIVATE_EVIDENCE_DIRECTORY = Path("private") / "evidence"
HUMBER_SCOPE_AUTHORITY = "Humber Research Ethics Board"
SCOPE_STATUSES = frozenset({"no_reb_review_required", "reb_approved"})
SCOPE_DOCUMENT_EXTENSIONS = frozenset(
    {".docx", ".eml", ".html", ".md", ".msg", ".pdf", ".txt"}
)
ASSIGNMENT_REGISTRY_NAME = "assignment-registry.csv"
ASSIGNMENT_ATTESTATION_NAME = "assignment-attestation.json"
INVESTIGATOR_ROSTER_REVIEW_NAME = "investigator-roster-review.json"
INVESTIGATOR_ROSTER_REVIEW_SCHEMA_VERSION = 1
MIN_ASSIGNMENTS_PER_ROLE = 3
MIN_SENT_REQUEST_BYTES = 500
MIN_HUMBER_RESPONSE_BYTES = 100
MIN_ROSTER_REVIEW_BYTES = 200
FINALIZATION_FLAGS = (
    "evaluator_information_finalized",
    "recruitment_notice_finalized",
)
PLACEHOLDER_MARKERS = (
    "todo",
    "tbd",
    "placeholder",
    "replace me",
    "replace_me",
    "example.com",
    "example@",
    ".invalid",
    "draft",
    "<",
    ">",
)
UNFINALIZED_MATERIAL_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(?im)^\s{0,3}#{1,6}[^\n]*\bdraft\b",
        r"(?i)\bdrafts?\s+only\b",
        r"(?i)\bdo not (?:circulate|use|send)\b",
        r"(?i)\bnot (?:an?\s+)?(?:live|active) (?:collection|evaluator|recruitment|study)\b",
        r"(?i)\bfill in\b",
        r"(?i)\bplaceholder\b",
        r"(?i)\bworking (?:policy )?draft\b",
        r"(?i)\bthis draft\b",
        r"(?i)\bdraft (?:for|materials?|methodological|orientation|procedure|protocol|recruitment|study)\b",
    )
)
MIN_OPERATIONAL_MARKDOWN_CHARS = 500
WITHDRAWAL_LOG_FIELDS = (
    "rater_id",
    "request_received_at",
    "cutoff_status",
    "source_files_deleted_at",
    "derived_outputs_rebuilt_at",
    "completion_status",
    "notes",
)
REQUIRED_MATERIAL_SECTIONS = {
    "benchmark/study-a/materials/data-return-instructions-draft.md": (
        "## Evaluator Return Instructions",
        "## Investigator Handling After Receipt",
    ),
    "benchmark/study-a/materials/evaluator-information-and-consent-draft.md": (
        "## What You Would Do",
        "## Voluntary Evaluator Agreement and Privacy",
    ),
    "benchmark/study-a/materials/evaluator-quick-start-draft.md": (
        "## Before You Begin",
        "## How To Rate A Row",
    ),
    "benchmark/study-a/materials/independent-adjudication-one-page.md": (
        "## Design",
        "## What the Study Can Establish",
    ),
    "benchmark/study-a/materials/privacy-and-release-boundary-draft.md": (
        "## Local-Only Material",
        "## Potentially Shareable Material",
    ),
    "benchmark/study-a/materials/recruitment-notice-draft.md": (
        "I am seeking two kinds of evaluator:",
        "unpaid volunteer contribution",
    ),
    "benchmark/study-a/materials/study-protocol-draft.md": (
        "## Materials and Design",
        "## Recruitment and Independence",
        "## Data Handling and Analysis",
    ),
    "benchmark/study-a/materials/withdrawal-procedure-draft.md": (
        "## Rule",
        "## Before Analysis Begins",
        "## Cutoff Procedure",
    ),
}
CONFIG_KEYS = {
    "config_version",
    "study",
    "freeze_tag",
    "role_pool_policy",
    "return_channel",
    "investigator_contact",
    "withdrawal_route",
    "collection_close_at",
    "analysis_start_at",
    "retention_until",
    *FINALIZATION_FLAGS,
    "workload_estimate_minutes_per_block",
    "institutional_scope",
    "investigator_roster_review",
    "finalized_materials",
    "external_returns_opened",
}
RETURN_CHANNEL_KEYS = {
    "description",
    "access_control",
    "investigator_access_only",
    "public_link",
    "not_long_term_store",
}
WORKLOAD_ESTIMATE_KEYS = {"minimum", "maximum", "basis"}
EVIDENCE_FILE_KEYS = {"path", "sha256"}
SCOPE_BASIS_ARTIFACTS = {
    "analysis_plan": "benchmark/study-a/analysis-plan.md",
    "study_protocol": "benchmark/study-a/materials/study-protocol-draft.md",
}
INSTITUTIONAL_SCOPE_KEYS = {
    "status",
    "authority",
    "request_sent_at",
    "response_received_at",
    "determined_at",
    "reference_id",
    "sent_request",
    "humber_response",
    "scope_basis_artifacts",
    "scope_basis_accurately_represented_in_sent_request",
    "humber_response_provenance_manually_verified",
    "scope_meaning_manually_reviewed",
    "participant_role_question_addressed_or_inapplicable",
    "humber_jurisdiction_question_addressed_or_inapplicable",
    "scope_conditions_implemented",
    "approval_expires_at",
}
ROSTER_REVIEW_REFERENCE_KEYS = {"path", "sha256"}
ROSTER_REVIEW_PAYLOAD_KEYS = {
    "review_schema_version",
    "study",
    "reviewed_at",
    "reviewer",
    "assignment_registry_sha256",
    "checks",
}
ROSTER_REVIEW_CHECK_KEYS = {
    "unique_real_people_confirmed",
    "role_eligibility_confirmed",
    "cross_role_disjointness_confirmed",
}
HASH_LIMITATION = (
    "file hashes prove byte integrity only; they do not establish a response's "
    "provenance, authority, or meaning"
)


def git(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=freeze_manifest.ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def parse_aware_datetime(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} is missing")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field} is not an ISO-8601 datetime")
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        errors.append(f"{field} is not timezone-aware")
        return None
    return parsed


def valid_final_text(value: Any) -> bool:
    if not isinstance(value, str) or len(value.strip()) < 5:
        return False
    lowered = value.strip().lower()
    return not any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def require_exact_keys(
    payload: dict[str, Any], expected: set[str], label: str, errors: list[str]
) -> None:
    actual = set(payload)
    if actual != expected:
        errors.append(
            f"{label} keys differ from the strict schema; "
            f"missing={sorted(expected - actual)!r}, extra={sorted(actual - expected)!r}"
        )


def resolve_confined_evidence_path(
    config_path: Path,
    value: Any,
    *,
    field: str,
    relative_directory: Path,
    allowed_extensions: frozenset[str],
    minimum_bytes: int,
    errors: list[str],
) -> Path | None:
    """Resolve a non-symlink evidence file confined beneath ``config_path``."""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"operational config {field} is missing")
        return None
    raw = Path(value)
    prefix = relative_directory.parts
    if (
        raw.is_absolute()
        or ".." in raw.parts
        or not raw.parts
        or raw.parts[: len(prefix)] != prefix
        or len(raw.parts) <= len(prefix)
    ):
        errors.append(
            f"operational config {field} must be relative and confined to "
            f"{relative_directory.as_posix()}/"
        )
        return None
    if raw.suffix.lower() not in allowed_extensions:
        allowed = ", ".join(sorted(allowed_extensions))
        errors.append(
            f"operational config {field} must name an evidence file "
            f"with one of these extensions: {allowed}"
        )
        return None

    base = config_path.parent.absolute()
    evidence_root = base / relative_directory
    lexical = base / raw
    current = base
    for part in raw.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"operational config {field} traverses a symlink")
            return None
    if not evidence_root.is_dir() or evidence_root.is_symlink():
        errors.append(
            f"private {relative_directory.as_posix()}/ directory is missing or unsafe"
        )
        return None
    try:
        resolved_root = evidence_root.resolve(strict=True)
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (FileNotFoundError, OSError, ValueError):
        errors.append(
            f"operational config {field} evidence file is missing, unsafe, or escapes "
            f"{relative_directory.as_posix()}/"
        )
        return None
    if not resolved.is_file() or resolved.is_symlink():
        errors.append(f"operational config {field} is missing or unsafe")
        return None
    try:
        size = resolved.stat().st_size
    except OSError:
        errors.append(f"operational config {field} cannot be inspected")
        return None
    if size < minimum_bytes:
        errors.append(
            f"operational config {field} is empty or implausibly small "
            f"({size} bytes; minimum {minimum_bytes})"
        )
        return None
    return resolved


def validate_evidence_file_reference(
    value: Any,
    config_path: Path,
    *,
    field: str,
    relative_directory: Path,
    allowed_extensions: frozenset[str],
    minimum_bytes: int,
    errors: list[str],
) -> Path | None:
    if not isinstance(value, dict):
        errors.append(f"operational config {field} must be an object")
        return None
    require_exact_keys(value, EVIDENCE_FILE_KEYS, f"operational config {field}", errors)
    path = resolve_confined_evidence_path(
        config_path,
        value.get("path"),
        field=f"{field}.path",
        relative_directory=relative_directory,
        allowed_extensions=allowed_extensions,
        minimum_bytes=minimum_bytes,
        errors=errors,
    )
    digest = value.get("sha256")
    if not is_sha256(digest):
        errors.append(f"operational config {field}.sha256 is invalid")
    if (
        path is not None
        and is_sha256(digest)
        and freeze_manifest.sha256_file(path) != str(digest).lower()
    ):
        errors.append(
            f"operational config {field} hash does not match; {HASH_LIMITATION}"
        )
    return path


def validate_return_channel(value: Any, errors: list[str]) -> None:
    label = "operational config return_channel"
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    require_exact_keys(value, RETURN_CHANNEL_KEYS, label, errors)
    if not valid_final_text(value.get("description")):
        errors.append(f"{label}.description is missing or still a placeholder")
    if not valid_final_text(value.get("access_control")):
        errors.append(f"{label}.access_control is missing or still a placeholder")
    for field in ("investigator_access_only", "not_long_term_store"):
        if value.get(field) is not True:
            errors.append(f"{label}.{field} must be explicitly true")
    if value.get("public_link") is not False:
        errors.append(f"{label}.public_link must be explicitly false")


def validate_workload_estimate(value: Any, errors: list[str]) -> None:
    label = "operational config workload_estimate_minutes_per_block"
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    require_exact_keys(value, WORKLOAD_ESTIMATE_KEYS, label, errors)
    if value.get("minimum") != 30:
        errors.append(f"{label}.minimum must equal 30")
    if value.get("maximum") != 40:
        errors.append(f"{label}.maximum must equal 40")
    if value.get("basis") != "planning_estimate_only":
        errors.append(f"{label}.basis must equal 'planning_estimate_only'")


def validate_scope_basis_artifacts(
    value: Any,
    manifest_payload: Any,
    errors: list[str],
) -> None:
    label = "operational config institutional_scope.scope_basis_artifacts"
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return
    require_exact_keys(value, set(SCOPE_BASIS_ARTIFACTS), label, errors)
    public = (
        manifest_payload.get("public_artifacts")
        if isinstance(manifest_payload, dict)
        else None
    )
    if not isinstance(public, dict):
        errors.append(
            "stamp-2 public artifact hashes are unavailable for the institutional "
            "scope basis"
        )
        public = {}
    for key, expected_path in SCOPE_BASIS_ARTIFACTS.items():
        record = value.get(key)
        record_label = f"{label}.{key}"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue
        require_exact_keys(record, {"path", "sha256"}, record_label, errors)
        if record.get("path") != expected_path:
            errors.append(f"{record_label}.path must equal {expected_path!r}")
        digest = record.get("sha256")
        if not is_sha256(digest):
            errors.append(f"{record_label}.sha256 is invalid")
        manifest_record = public.get(expected_path)
        manifest_digest = (
            manifest_record.get("sha256")
            if isinstance(manifest_record, dict)
            else None
        )
        if digest != manifest_digest:
            errors.append(
                f"{record_label}.sha256 does not equal the current stamp-2 manifest hash"
            )
        path = freeze_manifest.ROOT / expected_path
        if not path.is_file() or freeze_manifest.has_symlink_component(path):
            errors.append(f"institutional scope-basis artifact is missing or unsafe: {expected_path}")
            continue
        if is_sha256(digest) and freeze_manifest.sha256_file(path) != str(digest).lower():
            errors.append(
                f"{record_label}.sha256 does not equal the current artifact bytes"
            )


def validate_institutional_scope(
    value: Any,
    config_path: Path,
    *,
    now: datetime,
    manifest_payload: Any = None,
    required_active_through: datetime | None = None,
    errors: list[str],
) -> datetime | None:
    label = "operational config institutional_scope"
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    require_exact_keys(value, INSTITUTIONAL_SCOPE_KEYS, label, errors)

    status = value.get("status")
    if status not in SCOPE_STATUSES:
        errors.append(
            f"{label}.status must be 'no_reb_review_required' or 'reb_approved'"
        )
    if value.get("authority") != HUMBER_SCOPE_AUTHORITY:
        errors.append(f"{label}.authority must equal {HUMBER_SCOPE_AUTHORITY!r}")
    request_sent_at = parse_aware_datetime(
        value.get("request_sent_at"), f"{label}.request_sent_at", errors
    )
    response_received_at = parse_aware_datetime(
        value.get("response_received_at"), f"{label}.response_received_at", errors
    )
    determined_at = parse_aware_datetime(
        value.get("determined_at"), f"{label}.determined_at", errors
    )
    for field, timestamp in (
        ("request_sent_at", request_sent_at),
        ("response_received_at", response_received_at),
        ("determined_at", determined_at),
    ):
        if timestamp and timestamp > now:
            errors.append(f"{label}.{field} is in the future")
    if request_sent_at and response_received_at and response_received_at <= request_sent_at:
        errors.append(f"{label}.response_received_at must follow request_sent_at")
    if request_sent_at and determined_at and determined_at <= request_sent_at:
        errors.append(f"{label}.determined_at must follow request_sent_at")
    if not valid_final_text(value.get("reference_id")):
        errors.append(f"{label}.reference_id is missing or still a placeholder")

    sent_request = validate_evidence_file_reference(
        value.get("sent_request"),
        config_path,
        field="institutional_scope.sent_request",
        relative_directory=Path(EVIDENCE_DIRECTORY),
        allowed_extensions=SCOPE_DOCUMENT_EXTENSIONS,
        minimum_bytes=MIN_SENT_REQUEST_BYTES,
        errors=errors,
    )
    humber_response = validate_evidence_file_reference(
        value.get("humber_response"),
        config_path,
        field="institutional_scope.humber_response",
        relative_directory=Path(EVIDENCE_DIRECTORY),
        allowed_extensions=SCOPE_DOCUMENT_EXTENSIONS,
        minimum_bytes=MIN_HUMBER_RESPONSE_BYTES,
        errors=errors,
    )
    if sent_request is not None and humber_response is not None:
        if sent_request == humber_response:
            errors.append(
                f"{label} must retain separate sent-request and Humber-response files"
            )
        elif freeze_manifest.sha256_file(sent_request) == freeze_manifest.sha256_file(
            humber_response
        ):
            errors.append(
                f"{label} sent-request and Humber-response files must not have identical bytes"
            )

    validate_scope_basis_artifacts(
        value.get("scope_basis_artifacts"), manifest_payload, errors
    )
    for field, meaning in {
        "scope_basis_accurately_represented_in_sent_request": (
            "whether the hash-bound analysis plan and protocol were accurately "
            "represented in the sent request"
        ),
        "humber_response_provenance_manually_verified": "response provenance and Humber authority",
        "scope_meaning_manually_reviewed": "the response's substantive meaning",
        "participant_role_question_addressed_or_inapplicable": (
            "whether the participant-role question was addressed or expressly deemed inapplicable"
        ),
        "humber_jurisdiction_question_addressed_or_inapplicable": (
            "whether the Humber-jurisdiction question was addressed or expressly deemed inapplicable"
        ),
        "scope_conditions_implemented": "all stated scope or approval conditions",
    }.items():
        if value.get(field) is not True:
            errors.append(
                f"{label}.{field} must be explicitly true after manual review of {meaning}; "
                f"{HASH_LIMITATION}"
            )

    expires_value = value.get("approval_expires_at")
    if status == "no_reb_review_required":
        if expires_value is not None:
            errors.append(
                f"{label}.approval_expires_at must be null for no_reb_review_required"
            )
    elif status == "reb_approved":
        approval_expires_at = parse_aware_datetime(
            expires_value, f"{label}.approval_expires_at", errors
        )
        if approval_expires_at and approval_expires_at <= now:
            errors.append(f"{label}.approval_expires_at must be in the future")
        if determined_at and approval_expires_at and approval_expires_at <= determined_at:
            errors.append(f"{label}.approval_expires_at must follow determined_at")
        if (
            required_active_through
            and approval_expires_at
            and approval_expires_at < required_active_through
        ):
            errors.append(
                f"{label}.approval_expires_at must cover analysis_start_at"
            )
    return determined_at


def local_material_dependencies(
    path: Path, text: str
) -> tuple[set[str], list[str]]:
    candidates = re.findall(r"\]\(([^)]+)\)", text) + re.findall(
        r"`([^`]+\.(?:csv|json|md))`", text
    )
    dependencies: set[str] = set()
    errors: list[str] = []
    for candidate in candidates:
        target_text = candidate.split("#", 1)[0].split("?", 1)[0].strip()
        if (
            not target_text
            or target_text.startswith("#")
            or "://" in target_text
            or target_text.startswith("mailto:")
        ):
            continue
        raw = Path(target_text)
        if raw.is_absolute():
            errors.append(
                f"finalized material has an unsafe absolute local dependency: "
                f"{path.relative_to(freeze_manifest.ROOT).as_posix()} -> {target_text}"
            )
            continue
        lexical = path.parent / raw
        try:
            resolved = lexical.resolve(strict=True)
            relative = resolved.relative_to(freeze_manifest.ROOT.resolve()).as_posix()
        except FileNotFoundError:
            errors.append(
                f"finalized material has a missing local dependency: "
                f"{path.relative_to(freeze_manifest.ROOT).as_posix()} -> {target_text}"
            )
            continue
        except (OSError, ValueError):
            errors.append(
                f"finalized material has an unsafe local dependency outside the repository: "
                f"{path.relative_to(freeze_manifest.ROOT).as_posix()} -> {target_text}"
            )
            continue
        if (
            not resolved.is_file()
            or freeze_manifest.has_symlink_component(lexical)
        ):
            errors.append(
                f"finalized material has a missing or symlinked local dependency: "
                f"{path.relative_to(freeze_manifest.ROOT).as_posix()} -> {target_text}"
            )
            continue
        dependencies.add(relative)
    return dependencies, errors


def validate_finalized_materials(
    config: dict[str, Any], manifest_payload: dict[str, Any], errors: list[str]
) -> None:
    declared = config.get("finalized_materials")
    expected_paths = list(freeze_manifest.OPERATIONAL_MATERIALS)
    if not isinstance(declared, list):
        errors.append("operational config finalized_materials is missing")
        return
    if len(declared) != len(expected_paths):
        errors.append("operational config finalized_materials does not have the exact artifact count")
    public = manifest_payload.get("public_artifacts")
    if not isinstance(public, dict):
        errors.append("stamp-2 public artifact hashes are unavailable for material finalization")
        public = {}
    declared_paths: list[Any] = []
    dependencies: set[str] = set()
    for index, expected_path in enumerate(expected_paths):
        if index >= len(declared) or not isinstance(declared[index], dict):
            errors.append(f"operational config finalized_materials[{index}] is missing or invalid")
            continue
        record = declared[index]
        require_exact_keys(record, {"path", "sha256"}, f"finalized_materials[{index}]", errors)
        declared_paths.append(record.get("path"))
        if record.get("path") != expected_path:
            errors.append(f"finalized_materials[{index}].path must equal {expected_path!r}")
        digest = record.get("sha256")
        if not is_sha256(digest):
            errors.append(f"finalized_materials[{index}].sha256 is invalid")
        manifest_record = public.get(expected_path)
        manifest_digest = manifest_record.get("sha256") if isinstance(manifest_record, dict) else None
        if digest != manifest_digest:
            errors.append(f"finalized material hash does not equal the stamp-2 hash for {expected_path}")
        path = freeze_manifest.ROOT / expected_path
        if not path.is_file() or freeze_manifest.has_symlink_component(path):
            errors.append(f"finalized material is missing or unsafe: {expected_path}")
            continue
        actual = freeze_manifest.sha256_file(path)
        if digest != actual:
            errors.append(f"finalized material hash does not equal current bytes for {expected_path}")
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            errors.append(f"finalized material is not readable UTF-8: {expected_path}")
            continue
        if path.suffix == ".md":
            if len(text.strip()) < MIN_OPERATIONAL_MARKDOWN_CHARS:
                errors.append(
                    f"finalized Markdown material is empty or implausibly short: "
                    f"{expected_path}"
                )
            first_content_line = next(
                (line.strip() for line in text.splitlines() if line.strip()), ""
            )
            if not first_content_line.startswith("# "):
                errors.append(
                    f"finalized Markdown material lacks a top-level title: {expected_path}"
                )
            missing_sections = [
                section
                for section in REQUIRED_MATERIAL_SECTIONS.get(expected_path, ())
                if section not in text
            ]
            if missing_sections:
                errors.append(
                    f"finalized Markdown material lacks required sections for "
                    f"{expected_path}: {missing_sections!r}"
                )
        elif expected_path.endswith("withdrawal-log-template.csv"):
            csv_rows = list(csv.reader(text.splitlines()))
            if csv_rows != [list(WITHDRAWAL_LOG_FIELDS)]:
                errors.append(
                    "finalized withdrawal-log template must contain exactly the "
                    "canonical nonempty header"
                )
        matched = [pattern.pattern for pattern in UNFINALIZED_MATERIAL_PATTERNS if pattern.search(text)]
        if matched:
            errors.append(f"finalized material still contains draft/placeholder status markers: {expected_path}")
        material_dependencies, dependency_errors = local_material_dependencies(path, text)
        dependencies.update(material_dependencies)
        errors.extend(dependency_errors)
    if declared_paths != expected_paths:
        errors.append("operational config finalized_materials must use the exact canonical order and set")
    missing_dependencies = sorted(dependencies - set(expected_paths))
    if missing_dependencies:
        errors.append(
            "finalized material dependency closure is incomplete: " + ", ".join(missing_dependencies)
        )


def validate_config_location(config_path: Path, production_root: Path) -> list[str]:
    """Require the config to be a regular file on a non-symlink path in production."""
    errors: list[str] = []
    root = production_root.absolute()
    candidate = config_path.absolute()
    if not root.is_dir() or root.is_symlink():
        return [f"Study A production root is missing or unsafe: {production_root}"]
    try:
        root.relative_to(freeze_manifest.ROOT.absolute())
    except ValueError:
        try:
            if root.resolve(strict=True) != root:
                return [
                    f"Study A production root traverses a symlink: {production_root}"
                ]
        except (FileNotFoundError, OSError):
            return [f"Study A production root is missing or unsafe: {production_root}"]
    else:
        if freeze_manifest.has_symlink_component(root):
            return [f"Study A production root traverses a symlink: {production_root}"]
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        return ["final operational config must be confined beneath the production root"]
    if not relative.parts or ".." in relative.parts:
        return ["final operational config must be confined beneath the production root"]
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"final operational config traverses a symlink: {current}")
            return errors
    try:
        resolved_root = root.resolve(strict=True)
        resolved_candidate = candidate.resolve(strict=True)
        resolved_candidate.relative_to(resolved_root)
    except (FileNotFoundError, OSError, ValueError):
        return ["final operational config is missing, unsafe, or escapes the production root"]
    if not resolved_candidate.is_file():
        errors.append(f"final operational config is not a regular file: {config_path}")
    return errors


def has_symlink_component_beneath(path: Path, root: Path) -> bool:
    """Return true if ``path`` escapes ``root`` or traverses a link below it."""
    base = root.absolute()
    candidate = path.absolute()
    try:
        relative = candidate.relative_to(base)
    except ValueError:
        return True
    current = base
    if current.is_symlink():
        return True
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def validate_operational_config(
    config_path: Path,
    *,
    production_root: Path | None = None,
    manifest_payload: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    current_time = now or datetime.now(timezone.utc)
    scoped_root = (production_root or config_path.parent).absolute()
    location_errors = validate_config_location(config_path, scoped_root)
    if location_errors:
        return {}, location_errors
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, [f"final operational config is invalid JSON: {exc}"]
    if not isinstance(config, dict):
        return {}, ["final operational config must be a JSON object"]
    require_exact_keys(config, CONFIG_KEYS, "operational config", errors)
    for field, expected in {
        "config_version": CONFIG_VERSION,
        "study": "A",
        "role_pool_policy": "person_disjoint",
        "external_returns_opened": False,
    }.items():
        if config.get(field) != expected:
            errors.append(f"operational config {field} must equal {expected!r}")
    tag = config.get("freeze_tag")
    if not isinstance(tag, str) or not tag.strip() or any(ch.isspace() for ch in tag):
        errors.append("operational config freeze_tag is missing or invalid")
    validate_return_channel(config.get("return_channel"), errors)
    for field in ("investigator_contact", "withdrawal_route"):
        if not valid_final_text(config.get(field)):
            errors.append(f"operational config {field} is missing or still a placeholder")
    for field in FINALIZATION_FLAGS:
        if config.get(field) is not True:
            errors.append(f"operational config {field} must be explicitly true")
    validate_workload_estimate(config.get("workload_estimate_minutes_per_block"), errors)
    roster_reference = config.get("investigator_roster_review")
    if not isinstance(roster_reference, dict):
        errors.append("operational config investigator_roster_review must be an object")
    else:
        require_exact_keys(
            roster_reference,
            ROSTER_REVIEW_REFERENCE_KEYS,
            "operational config investigator_roster_review",
            errors,
        )
        if roster_reference.get("path") != (
            PRIVATE_EVIDENCE_DIRECTORY / INVESTIGATOR_ROSTER_REVIEW_NAME
        ).as_posix():
            errors.append(
                "operational config investigator_roster_review.path must equal "
                f"{(PRIVATE_EVIDENCE_DIRECTORY / INVESTIGATOR_ROSTER_REVIEW_NAME).as_posix()!r}"
            )
        if not is_sha256(roster_reference.get("sha256")):
            errors.append(
                "operational config investigator_roster_review.sha256 is invalid"
            )

    close_at = parse_aware_datetime(
        config.get("collection_close_at"), "operational config collection_close_at", errors
    )
    analysis_at = parse_aware_datetime(
        config.get("analysis_start_at"), "operational config analysis_start_at", errors
    )
    retention_at = parse_aware_datetime(
        config.get("retention_until"), "operational config retention_until", errors
    )
    if close_at and close_at <= current_time:
        errors.append("collection_close_at must be in the future when the gate is run")
    if close_at and analysis_at and analysis_at < close_at:
        errors.append("analysis_start_at precedes collection_close_at")
    if analysis_at and retention_at and retention_at <= analysis_at:
        errors.append("retention_until must be after analysis_start_at")

    validate_institutional_scope(
        config.get("institutional_scope"),
        config_path,
        now=current_time,
        manifest_payload=manifest_payload,
        required_active_through=analysis_at,
        errors=errors,
    )
    validate_finalized_materials(config, manifest_payload or {}, errors)
    return config, errors


def current_package_ids(production_root: Path) -> tuple[dict[str, str], list[str]]:
    package_ids: dict[str, str] = {}
    errors: list[str] = []
    for role in freeze_manifest.ROLE_ARCHIVES:
        metadata_path = production_root / "package" / role / "package-metadata.json"
        if not metadata_path.is_file() or metadata_path.is_symlink():
            errors.append(f"current package metadata is missing or unsafe for role {role}")
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"current package metadata is invalid for role {role}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"current package metadata is not a JSON object for role {role}")
            continue
        package_id = metadata.get("package_id")
        if metadata.get("role") != role or not isinstance(package_id, str) or not package_id:
            errors.append(f"current package metadata has an invalid role/package_id for {role}")
            continue
        package_ids[role] = package_id
    return package_ids, errors


def validate_investigator_roster_review(
    reference: Any,
    config_path: Path,
    registry_path: Path,
    *,
    attestation_validated_at: datetime | None,
    now: datetime,
    errors: list[str],
) -> None:
    label = "investigator_roster_review"
    if isinstance(reference, dict):
        require_exact_keys(
            reference,
            ROSTER_REVIEW_REFERENCE_KEYS,
            f"operational config {label}",
            errors,
        )
        if reference.get("path") != (
            PRIVATE_EVIDENCE_DIRECTORY / INVESTIGATOR_ROSTER_REVIEW_NAME
        ).as_posix():
            errors.append(
                f"operational config {label}.path must equal "
                f"{(PRIVATE_EVIDENCE_DIRECTORY / INVESTIGATOR_ROSTER_REVIEW_NAME).as_posix()!r}"
            )
    review_path = validate_evidence_file_reference(
        reference,
        config_path,
        field=label,
        relative_directory=PRIVATE_EVIDENCE_DIRECTORY,
        allowed_extensions=frozenset({".json"}),
        minimum_bytes=MIN_ROSTER_REVIEW_BYTES,
        errors=errors,
    )
    if review_path is None:
        return
    try:
        payload = json.loads(review_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"private investigator roster review is invalid JSON: {exc}")
        return
    if not isinstance(payload, dict):
        errors.append("private investigator roster review must be a JSON object")
        return
    require_exact_keys(
        payload,
        ROSTER_REVIEW_PAYLOAD_KEYS,
        "private investigator roster review",
        errors,
    )
    if payload.get("review_schema_version") != INVESTIGATOR_ROSTER_REVIEW_SCHEMA_VERSION:
        errors.append(
            "private investigator roster review review_schema_version must equal "
            f"{INVESTIGATOR_ROSTER_REVIEW_SCHEMA_VERSION}"
        )
    if payload.get("study") != "A":
        errors.append("private investigator roster review study must equal 'A'")
    if not valid_final_text(payload.get("reviewer")):
        errors.append("private investigator roster review reviewer is missing or a placeholder")
    reviewed_at = parse_aware_datetime(
        payload.get("reviewed_at"),
        "private investigator roster review reviewed_at",
        errors,
    )
    if reviewed_at and reviewed_at > now:
        errors.append("private investigator roster review reviewed_at is in the future")
    if (
        reviewed_at
        and attestation_validated_at
        and reviewed_at < attestation_validated_at
    ):
        errors.append(
            "private investigator roster review must not predate the assignment attestation"
        )
    registry_digest = payload.get("assignment_registry_sha256")
    if not is_sha256(registry_digest):
        errors.append(
            "private investigator roster review assignment_registry_sha256 is invalid"
        )
    elif freeze_manifest.sha256_file(registry_path) != str(registry_digest).lower():
        errors.append(
            "private investigator roster review is not bound to the current assignment "
            f"registry bytes; {HASH_LIMITATION}"
        )
    checks = payload.get("checks")
    if not isinstance(checks, dict):
        errors.append("private investigator roster review checks must be an object")
        return
    require_exact_keys(
        checks,
        ROSTER_REVIEW_CHECK_KEYS,
        "private investigator roster review checks",
        errors,
    )
    for field in sorted(ROSTER_REVIEW_CHECK_KEYS):
        if checks.get(field) is not True:
            errors.append(
                f"private investigator roster review checks.{field} must be explicitly "
                "true based on the investigator's identity-side roster review; "
                f"{HASH_LIMITATION}"
            )


def validate_assignment_contract(
    production_root: Path,
    *,
    expected_package_ids: dict[str, str] | None = None,
    roster_review_reference: Any = None,
    config_path: Path | None = None,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    private_dir = production_root / "private"
    registry_path = private_dir / ASSIGNMENT_REGISTRY_NAME
    attestation_path = private_dir / ASSIGNMENT_ATTESTATION_NAME
    if (
        not registry_path.is_file()
        or registry_path.is_symlink()
        or has_symlink_component_beneath(registry_path, production_root)
    ):
        errors.append("private assignment registry is missing or unsafe")
    if (
        not attestation_path.is_file()
        or attestation_path.is_symlink()
        or has_symlink_component_beneath(attestation_path, production_root)
    ):
        errors.append("private assignment attestation is missing or unsafe")
    if errors:
        return errors
    try:
        registry = verify_assignment_attestation(
            registry_path,
            attestation_path,
            allowed_roles=set(freeze_manifest.ROLE_ARCHIVES),
            study_id=freeze_manifest.STUDY_ID,
        )
    except ValueError:
        return [
            "private assignment registry/attestation failed strict byte-integrity and "
            "internal-ID verification; attestation does not establish real-world "
            "identity or role-pool disjointness"
        ]

    try:
        attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ["private assignment attestation became unreadable after verification"]
    if not isinstance(attestation, dict):
        return ["private assignment attestation became a non-object after verification"]
    validated_at_errors: list[str] = []
    validated_at = parse_aware_datetime(
        attestation.get("validated_at"),
        "assignment attestation validated_at",
        validated_at_errors,
    )
    errors.extend(validated_at_errors)
    if validated_at and validated_at > (now or datetime.now(timezone.utc)):
        errors.append("assignment attestation validated_at is in the future")

    validate_investigator_roster_review(
        roster_review_reference,
        config_path or (production_root / "operational-config.json"),
        registry_path,
        attestation_validated_at=validated_at,
        now=now or datetime.now(timezone.utc),
        errors=errors,
    )

    package_ids = expected_package_ids
    if package_ids is None:
        package_ids, metadata_errors = current_package_ids(production_root)
        errors.extend(metadata_errors)
    for role in freeze_manifest.ROLE_ARCHIVES:
        if registry.counts_by_role.get(role, 0) < MIN_ASSIGNMENTS_PER_ROLE:
            errors.append(
                f"assignment registry has fewer than {MIN_ASSIGNMENTS_PER_ROLE} "
                f"registered assignments for role {role}"
            )
        if not isinstance(package_ids, dict):
            errors.append("current role package ID mapping is unavailable")
            break
        if registry.package_ids_by_role.get(role) != [package_ids.get(role, "")]:
            errors.append(f"assignment registry package_id does not match current role package for {role}")
    return errors


def check_manifest_at_head(
    manifest_path: Path, manifest_payload: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []
    if manifest_path.is_symlink() or freeze_manifest.has_symlink_component(manifest_path):
        return ["collection-ready manifest path is symlinked or unsafe"]
    try:
        relative = manifest_path.absolute().relative_to(
            freeze_manifest.ROOT.absolute()
        ).as_posix()
    except ValueError:
        return ["collection-ready manifest must be inside the project repository"]
    tree = git(["ls-tree", "-z", "HEAD", "--", relative])
    entry = tree.stdout.rstrip(b"\0").split(b"\t", 1)[0].split()
    if tree.returncode != 0 or len(entry) != 3 or entry[0] != b"100644":
        return ["the Study A manifest is not a regular tracked JSON file at HEAD"]
    if manifest_path.stat().st_mode & 0o111:
        return ["working Study A manifest mode differs from its regular mode at HEAD"]
    result = git(["show", f"HEAD:{relative}"])
    if result.returncode != 0:
        return ["the Study A manifest is not tracked at HEAD"]
    if result.stdout != manifest_path.read_bytes():
        errors.append("working Study A manifest bytes differ from the manifest tracked at HEAD")

    payload = manifest_payload
    if payload is None:
        try:
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            loaded = {}
        payload = loaded if isinstance(loaded, dict) else {}
    public = payload.get("public_artifacts")
    if not isinstance(public, dict) or not public:
        errors.append("stamp-2 public artifact inventory is unavailable at the tag gate")
        return errors
    for artifact_path, record in sorted(public.items()):
        raw = Path(artifact_path)
        if (
            raw.is_absolute()
            or not raw.parts
            or ".." in raw.parts
            or not isinstance(record, dict)
        ):
            errors.append(f"manifest public artifact path is invalid: {artifact_path!r}")
            continue
        current = freeze_manifest.ROOT / raw
        if not current.is_file() or freeze_manifest.has_symlink_component(current):
            errors.append(f"manifest public artifact is missing or unsafe: {artifact_path}")
            continue
        tree = git(["ls-tree", "-z", "HEAD", "--", artifact_path])
        entry = tree.stdout.rstrip(b"\0").split(b"\t", 1)[0].split()
        if tree.returncode != 0 or len(entry) != 3 or entry[0] not in {b"100644", b"100755"}:
            errors.append(
                f"manifest public artifact is not a regular tracked file at HEAD: "
                f"{artifact_path}"
            )
            continue
        current_mode = b"100755" if current.stat().st_mode & 0o111 else b"100644"
        if entry[0] != current_mode:
            errors.append(
                f"manifest public artifact mode at HEAD/current differs: {artifact_path}"
            )
            continue
        head = git(["show", f"HEAD:{artifact_path}"])
        if head.returncode != 0:
            errors.append(f"manifest public artifact is absent from HEAD: {artifact_path}")
            continue
        current_bytes = current.read_bytes()
        expected_sha = record.get("sha256")
        expected_size = record.get("bytes")
        if (
            head.stdout != current_bytes
            or freeze_manifest.sha256_bytes(head.stdout) != expected_sha
            or len(head.stdout) != expected_size
        ):
            errors.append(
                f"manifest public artifact bytes at HEAD/current/manifest differ: "
                f"{artifact_path}"
            )
    return errors


def check_annotated_tag_at_head(
    tag: str, *, after_scope_recorded_at: datetime | None = None
) -> list[str]:
    errors: list[str] = []
    valid = git(["check-ref-format", f"refs/tags/{tag}"])
    if valid.returncode != 0:
        return ["configured freeze_tag is not a valid git tag name"]
    head = git(["rev-parse", "HEAD"])
    tagged_commit = git(["rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"])
    object_type = git(["cat-file", "-t", f"refs/tags/{tag}"])
    if head.returncode != 0 or tagged_commit.returncode != 0:
        return ["configured freeze_tag does not exist or cannot be resolved"]
    if tagged_commit.stdout.strip() != head.stdout.strip():
        errors.append("configured freeze_tag does not point at HEAD")
    if object_type.returncode != 0 or object_type.stdout.strip() != b"tag":
        errors.append("configured freeze_tag is lightweight; an annotated tag is required")
    pointed = git(
        [
            "for-each-ref",
            "--points-at",
            "HEAD",
            "--format=%(refname:strip=2)|%(objecttype)",
            "refs/tags",
        ]
    )
    lines = set(pointed.stdout.decode("utf-8", errors="replace").splitlines())
    if f"{tag}|tag" not in lines:
        errors.append("configured annotated freeze_tag is not reported as pointing at HEAD")
    tagger_result = git(
        [
            "for-each-ref",
            "--format=%(taggerdate:iso-strict)",
            f"refs/tags/{tag}",
        ]
    )
    tagger_text = tagger_result.stdout.decode("utf-8", errors="replace").strip()
    tagger_errors: list[str] = []
    tagger_at = parse_aware_datetime(
        tagger_text,
        "configured annotated freeze_tag tagger date",
        tagger_errors,
    )
    if tagger_result.returncode != 0:
        errors.append("configured annotated freeze_tag tagger date cannot be read")
    else:
        errors.extend(tagger_errors)
    if (
        after_scope_recorded_at
        and tagger_at
        and tagger_at <= after_scope_recorded_at
    ):
        errors.append(
            "configured annotated freeze_tag must be created after the written Humber "
            "response was received and its determination recorded"
        )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=freeze_manifest.DEFAULT_MANIFEST)
    parser.add_argument(
        "--production-root", type=Path, default=freeze_manifest.DEFAULT_PRODUCTION_ROOT
    )
    parser.add_argument("--config", type=Path, default=None)
    args = parser.parse_args()
    manifest_path = args.manifest.absolute()
    production_root = args.production_root.absolute()
    config_path = (
        args.config.absolute()
        if args.config is not None
        else production_root / "operational-config.json"
    )

    errors = check_freeze_ready(manifest_path, production_root)
    manifest_payload: dict[str, Any] = {}
    if manifest_path.is_file():
        try:
            loaded_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(loaded_manifest, dict):
                manifest_payload = loaded_manifest
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass
    errors.extend(
        check_manifest_at_head(manifest_path, manifest_payload)
        if manifest_path.is_file()
        else []
    )
    production_candidate_value = manifest_payload.get("production_candidate")
    production_candidate = (
        production_candidate_value
        if isinstance(production_candidate_value, dict)
        else {}
    )
    role_archives_value = production_candidate.get("role_archives")
    role_archives = role_archives_value if isinstance(role_archives_value, dict) else {}
    manifest_package_ids = {
        role: str(
            role_archives.get(role, {}).get("package_id", "")
            if isinstance(role_archives.get(role), dict)
            else ""
        )
        for role in freeze_manifest.ROLE_ARCHIVES
    }
    package_ids, package_id_errors = current_package_ids(production_root)
    errors.extend(package_id_errors)
    if package_ids != manifest_package_ids:
        errors.append("current role package IDs do not equal the stamp-2 manifest")
    config, config_errors = validate_operational_config(
        config_path,
        production_root=production_root,
        manifest_payload=manifest_payload,
    )
    errors.extend(config_errors)
    errors.extend(
        validate_assignment_contract(
            production_root,
            expected_package_ids=package_ids,
            roster_review_reference=config.get("investigator_roster_review"),
            config_path=config_path,
        )
    )
    tag = config.get("freeze_tag")
    if isinstance(tag, str) and tag.strip():
        scope = config.get("institutional_scope")
        scope_recorded_at: datetime | None = None
        if isinstance(scope, dict):
            timestamp_errors: list[str] = []
            determined_at = parse_aware_datetime(
                scope.get("determined_at"),
                "operational config institutional_scope.determined_at",
                timestamp_errors,
            )
            response_received_at = parse_aware_datetime(
                scope.get("response_received_at"),
                "operational config institutional_scope.response_received_at",
                timestamp_errors,
            )
            recorded_times = [
                timestamp
                for timestamp in (determined_at, response_received_at)
                if timestamp is not None
            ]
            scope_recorded_at = max(recorded_times) if recorded_times else None
        errors.extend(
            check_annotated_tag_at_head(
                tag.strip(), after_scope_recorded_at=scope_recorded_at
            )
        )
    if errors:
        print("Study A is not collection-ready:")
        for error in dict.fromkeys(errors):
            print(f"  - {error}")
        raise SystemExit(1)
    print(
        "OK: Study A collection gate passes for the annotated freeze tag and finalized "
        "operational config. The assignment attestation binds registry bytes and internal "
        "IDs only; the hash-bound investigator roster review remains the basis for "
        "real-world identity, role eligibility, and cross-role disjointness. Scope and "
        f"roster hashes prove byte integrity only, not authority or meaning. "
        "This check made no changes."
    )


if __name__ == "__main__":
    main()
