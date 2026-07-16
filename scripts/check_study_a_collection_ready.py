#!/usr/bin/env python3
"""Read-only Study A gate for opening external evaluator returns.

The gate requires a verified stamp 2, a byte-identical tracked manifest at
HEAD, an annotated freeze tag at that exact commit, at least three strictly
pre-attested and person-disjoint assignments per role, exact finalized
material hashes, and content-valid transfer/timing evidence bound to the
realized role packages. It never creates or changes any of them.
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


CONFIG_VERSION = 2
EVIDENCE_SCHEMA_VERSION = 1
EVIDENCE_DIRECTORY = "evidence"
ASSIGNMENT_REGISTRY_NAME = "assignment-registry.csv"
ASSIGNMENT_ATTESTATION_NAME = "assignment-attestation.json"
MIN_ASSIGNMENTS_PER_ROLE = 3
FINALIZATION_FLAGS = (
    "data_transfer_tested",
    "evaluator_information_finalized",
    "recruitment_notice_finalized",
    "final_interface_timed",
    "institutional_posture_confirmed",
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
    "dedicated_return_address",
    "investigator_contact",
    "deletion_route",
    "collection_close_at",
    "analysis_start_at",
    "retention_until",
    *FINALIZATION_FLAGS,
    "timing_minutes_per_block",
    "data_transfer_test_evidence",
    "final_interface_timing_evidence",
    "finalized_materials",
    "institutional_posture_basis",
    "institutional_posture_confirmed_at",
    "external_returns_opened",
}
TRANSFER_EVIDENCE_KEYS = {
    "evidence_schema_version",
    "study",
    "test_result",
    "tested_at",
    "package_build_fingerprint_sha256",
    "package_ids_by_role",
    "method",
    "synthetic_payload_only",
}
TIMING_EVIDENCE_KEYS = {
    "evidence_schema_version",
    "study",
    "timed_at",
    "package_build_fingerprint_sha256",
    "observed_minutes_per_block",
    "sample_size_blocks_by_role",
    "method",
}


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


def role_mapping(
    value: Any,
    label: str,
    errors: list[str],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return {}
    expected_roles = set(freeze_manifest.ROLE_ARCHIVES)
    if set(value) != expected_roles:
        errors.append(f"{label} must contain exactly the two Study A roles")
    return value


def resolve_evidence_path(
    config_path: Path,
    value: Any,
    field: str,
    errors: list[str],
) -> Path | None:
    """Resolve only a real, non-symlink JSON file under private evidence/."""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"operational config {field}.path is missing")
        return None
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts or not raw.parts or raw.parts[0] != EVIDENCE_DIRECTORY:
        errors.append(
            f"operational config {field}.path must be relative and confined to {EVIDENCE_DIRECTORY}/"
        )
        return None
    if raw.suffix.lower() != ".json":
        errors.append(f"operational config {field}.path must name a JSON evidence file")
        return None

    base = config_path.parent.absolute()
    evidence_root = base / EVIDENCE_DIRECTORY
    lexical = base / raw
    current = base
    for part in raw.parts:
        current = current / part
        if current.is_symlink():
            errors.append(f"operational config {field}.path traverses a symlink")
            return None
    if not evidence_root.is_dir() or evidence_root.is_symlink():
        errors.append(f"private {EVIDENCE_DIRECTORY}/ directory is missing or unsafe")
        return None
    try:
        resolved_root = evidence_root.resolve(strict=True)
        resolved = lexical.resolve(strict=True)
        resolved.relative_to(resolved_root)
    except (FileNotFoundError, OSError, ValueError):
        errors.append(
            f"operational config {field} evidence file is missing, unsafe, or escapes {EVIDENCE_DIRECTORY}/"
        )
        return None
    if not resolved.is_file() or resolved.is_symlink():
        errors.append(f"operational config {field} evidence file is missing or unsafe")
        return None
    return resolved


def load_strict_evidence(
    config: dict[str, Any],
    config_path: Path,
    field: str,
    payload_keys: set[str],
    errors: list[str],
) -> dict[str, Any]:
    reference = config.get(field)
    if not isinstance(reference, dict):
        errors.append(f"operational config {field} is missing")
        return {}
    require_exact_keys(reference, {"path", "sha256", *payload_keys}, f"operational config {field}", errors)
    evidence_path = resolve_evidence_path(config_path, reference.get("path"), field, errors)
    digest = reference.get("sha256")
    if not is_sha256(digest):
        errors.append(f"operational config {field}.sha256 is invalid")
    if evidence_path is None:
        return {}
    if is_sha256(digest) and freeze_manifest.sha256_file(evidence_path) != str(digest).lower():
        errors.append(f"operational config {field} evidence hash does not match")
    try:
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"operational config {field} evidence is not a JSON object: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"operational config {field} evidence is not a JSON object")
        return {}
    require_exact_keys(payload, payload_keys, f"{field} evidence payload", errors)
    for key in payload_keys:
        if reference.get(key) != payload.get(key):
            errors.append(f"operational config {field}.{key} does not equal the evidence file")
    return payload


def validate_transfer_evidence(
    config: dict[str, Any],
    config_path: Path,
    *,
    expected_build_fingerprint: str,
    expected_package_ids: dict[str, str],
    now: datetime,
    errors: list[str],
) -> None:
    field = "data_transfer_test_evidence"
    payload = load_strict_evidence(config, config_path, field, TRANSFER_EVIDENCE_KEYS, errors)
    if not payload:
        return
    if payload.get("evidence_schema_version") != EVIDENCE_SCHEMA_VERSION:
        errors.append("data transfer evidence has the wrong evidence_schema_version")
    if payload.get("study") != "A":
        errors.append("data transfer evidence study must equal 'A'")
    if payload.get("test_result") != "pass":
        errors.append("data transfer evidence test_result must equal 'pass'")
    tested_at = parse_aware_datetime(payload.get("tested_at"), "data transfer evidence tested_at", errors)
    if tested_at and tested_at > now:
        errors.append("data transfer evidence tested_at is in the future")
    if payload.get("package_build_fingerprint_sha256") != expected_build_fingerprint:
        errors.append("data transfer evidence is not bound to the current package-build fingerprint")
    package_ids = role_mapping(payload.get("package_ids_by_role"), "data transfer evidence package_ids_by_role", errors)
    if package_ids != expected_package_ids:
        errors.append("data transfer evidence package IDs do not match the current role packages")
    if not valid_final_text(payload.get("method")):
        errors.append("data transfer evidence method is missing or a placeholder")
    if payload.get("synthetic_payload_only") is not True:
        errors.append("data transfer evidence must attest that only a synthetic payload was used")


def validate_timing_evidence(
    config: dict[str, Any],
    config_path: Path,
    *,
    expected_build_fingerprint: str,
    timing_minutes_per_block: Any,
    now: datetime,
    errors: list[str],
) -> None:
    field = "final_interface_timing_evidence"
    payload = load_strict_evidence(config, config_path, field, TIMING_EVIDENCE_KEYS, errors)
    if not payload:
        return
    if payload.get("evidence_schema_version") != EVIDENCE_SCHEMA_VERSION:
        errors.append("interface timing evidence has the wrong evidence_schema_version")
    if payload.get("study") != "A":
        errors.append("interface timing evidence study must equal 'A'")
    timed_at = parse_aware_datetime(payload.get("timed_at"), "interface timing evidence timed_at", errors)
    if timed_at and timed_at > now:
        errors.append("interface timing evidence timed_at is in the future")
    if payload.get("package_build_fingerprint_sha256") != expected_build_fingerprint:
        errors.append("interface timing evidence is not bound to the current package-build fingerprint")
    observed = role_mapping(
        payload.get("observed_minutes_per_block"),
        "interface timing evidence observed_minutes_per_block",
        errors,
    )
    for role in freeze_manifest.ROLE_ARCHIVES:
        value = observed.get(role)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"interface timing evidence observed minutes for {role} must be positive")
    if observed != timing_minutes_per_block:
        errors.append("operational timing_minutes_per_block does not equal the timing evidence")
    sample_sizes = role_mapping(
        payload.get("sample_size_blocks_by_role"),
        "interface timing evidence sample_size_blocks_by_role",
        errors,
    )
    for role in freeze_manifest.ROLE_ARCHIVES:
        value = sample_sizes.get(role)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            errors.append(f"interface timing evidence sample size for {role} must be a positive integer")
    if not valid_final_text(payload.get("method")):
        errors.append("interface timing evidence method is missing or a placeholder")


def local_material_dependencies(path: Path, text: str) -> set[str]:
    candidates = re.findall(r"\]\(([^)]+)\)", text) + re.findall(
        r"`([^`]+\.(?:csv|json|md))`", text
    )
    dependencies: set[str] = set()
    for candidate in candidates:
        target_text = candidate.split("#", 1)[0].split("?", 1)[0].strip()
        if not target_text or "://" in target_text or target_text.startswith("mailto:"):
            continue
        target = (path.parent / target_text).resolve()
        try:
            relative = target.relative_to(freeze_manifest.ROOT).as_posix()
        except ValueError:
            continue
        if target.is_file():
            dependencies.add(relative)
    return dependencies


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
        dependencies.update(local_material_dependencies(path, text))
    if declared_paths != expected_paths:
        errors.append("operational config finalized_materials must use the exact canonical order and set")
    missing_dependencies = sorted(dependencies - set(expected_paths))
    if missing_dependencies:
        errors.append(
            "finalized material dependency closure is incomplete: " + ", ".join(missing_dependencies)
        )


def validate_operational_config(
    config_path: Path,
    *,
    expected_build_fingerprint: str = "",
    expected_package_ids: dict[str, str] | None = None,
    manifest_payload: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    current_time = now or datetime.now(timezone.utc)
    package_ids = expected_package_ids or {}
    if config_path.is_symlink():
        return {}, [f"final operational config is a symlink: {config_path}"]
    if not config_path.is_file():
        return {}, [f"final operational config is missing: {config_path}"]
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
    for field in ("dedicated_return_address", "investigator_contact", "deletion_route"):
        if not valid_final_text(config.get(field)):
            errors.append(f"operational config {field} is missing or still a placeholder")
    for field in FINALIZATION_FLAGS:
        if config.get(field) is not True:
            errors.append(f"operational config {field} must be explicitly true")

    timing = role_mapping(
        config.get("timing_minutes_per_block"),
        "operational config timing_minutes_per_block",
        errors,
    )
    for role in freeze_manifest.ROLE_ARCHIVES:
        value = timing.get(role)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            errors.append(f"operational config timing_minutes_per_block.{role} must be positive")

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

    if not expected_build_fingerprint:
        errors.append("stamp-2 package-build fingerprint is unavailable")
    if set(package_ids) != set(freeze_manifest.ROLE_ARCHIVES) or not all(package_ids.values()):
        errors.append("current role package IDs are unavailable")
    validate_transfer_evidence(
        config,
        config_path,
        expected_build_fingerprint=expected_build_fingerprint,
        expected_package_ids=package_ids,
        now=current_time,
        errors=errors,
    )
    validate_timing_evidence(
        config,
        config_path,
        expected_build_fingerprint=expected_build_fingerprint,
        timing_minutes_per_block=timing,
        now=current_time,
        errors=errors,
    )
    validate_finalized_materials(config, manifest_payload or {}, errors)

    if not valid_final_text(config.get("institutional_posture_basis")):
        errors.append("operational config institutional_posture_basis is missing or a placeholder")
    posture_at = parse_aware_datetime(
        config.get("institutional_posture_confirmed_at"),
        "operational config institutional_posture_confirmed_at",
        errors,
    )
    if posture_at and posture_at > current_time:
        errors.append("institutional_posture_confirmed_at is in the future")
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
        package_id = metadata.get("package_id")
        if metadata.get("role") != role or not isinstance(package_id, str) or not package_id:
            errors.append(f"current package metadata has an invalid role/package_id for {role}")
            continue
        package_ids[role] = package_id
    return package_ids, errors


def validate_assignment_contract(
    production_root: Path,
    *,
    expected_package_ids: dict[str, str] | None = None,
    now: datetime | None = None,
) -> list[str]:
    errors: list[str] = []
    private_dir = production_root / "private"
    registry_path = private_dir / ASSIGNMENT_REGISTRY_NAME
    attestation_path = private_dir / ASSIGNMENT_ATTESTATION_NAME
    if not registry_path.is_file() or registry_path.is_symlink():
        errors.append("private assignment registry is missing or unsafe")
    if not attestation_path.is_file() or attestation_path.is_symlink():
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
        return ["private assignment registry/attestation failed strict verification"]

    try:
        attestation = json.loads(attestation_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return ["private assignment attestation became unreadable after verification"]
    validated_at_errors: list[str] = []
    validated_at = parse_aware_datetime(
        attestation.get("validated_at"),
        "assignment attestation validated_at",
        validated_at_errors,
    )
    errors.extend(validated_at_errors)
    if validated_at and validated_at > (now or datetime.now(timezone.utc)):
        errors.append("assignment attestation validated_at is in the future")

    package_ids = expected_package_ids
    if package_ids is None:
        package_ids, metadata_errors = current_package_ids(production_root)
        errors.extend(metadata_errors)
    for role in freeze_manifest.ROLE_ARCHIVES:
        if registry.counts_by_role.get(role, 0) < MIN_ASSIGNMENTS_PER_ROLE:
            errors.append(
                f"assignment registry has fewer than {MIN_ASSIGNMENTS_PER_ROLE} "
                f"pre-attested assignments for role {role}"
            )
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


def check_annotated_tag_at_head(tag: str) -> list[str]:
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
    production_candidate = manifest_payload.get("production_candidate", {})
    expected_build_fingerprint = str(
        production_candidate.get("package_build_fingerprint_sha256", "")
    )
    manifest_package_ids = {
        role: str(production_candidate.get("role_archives", {}).get(role, {}).get("package_id", ""))
        for role in freeze_manifest.ROLE_ARCHIVES
    }
    package_ids, package_id_errors = current_package_ids(production_root)
    errors.extend(package_id_errors)
    if package_ids != manifest_package_ids:
        errors.append("current role package IDs do not equal the stamp-2 manifest")
    config, config_errors = validate_operational_config(
        config_path,
        expected_build_fingerprint=expected_build_fingerprint,
        expected_package_ids=package_ids,
        manifest_payload=manifest_payload,
    )
    errors.extend(config_errors)
    errors.extend(validate_assignment_contract(production_root, expected_package_ids=package_ids))
    tag = config.get("freeze_tag")
    if isinstance(tag, str) and tag.strip():
        errors.extend(check_annotated_tag_at_head(tag.strip()))
    if errors:
        print("Study A is not collection-ready:")
        for error in dict.fromkeys(errors):
            print(f"  - {error}")
        raise SystemExit(1)
    print(
        "OK: Study A collection gate passes for the annotated freeze tag and finalized "
        "operational config. This check made no changes."
    )


if __name__ == "__main__":
    main()
