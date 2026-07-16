#!/usr/bin/env python3
"""Build or semantically verify the two-stamp Study A freeze manifest.

Stamp 1 records a mutable checkpoint of the tracked design, analysis,
source-fingerprint record, provisional author snapshot, comparator outputs,
and gate code.  Stamp 2 adds the realized private row map and presentation
order plus the audited, role-isolated distribution packages.  Neither stamp
accomplishes a freeze or opens collection: those states require an explicit
commit/tag decision and the separate collection-ready gate.

Legacy v1 manifests can be inspected with ``--allow-legacy-v1``.  That mode is
only a compatibility checkpoint; it is never accepted by either readiness
gate and cannot authorize collection.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any
import zipfile

import build_independent_reassessment as package_builder


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "benchmark" / "study-a" / "FREEZE-MANIFEST.json"
DEFAULT_PRODUCTION_ROOT = ROOT / "private" / "study-a" / "production"
SEED_ITEMS_REL = "benchmark/items/seed-items.csv"
SOURCE_OUTPUT_REL = "benchmark/results/local-pilot-20260630-185417/outputs.csv"
AUTHOR_SNAPSHOT_REL = (
    "data/provisional/local-pilot-20260630-185417-provisional-author-labels.csv"
)
PILOT_MANIFEST_REL = "data/provisional/local-pilot-20260630-185417-freeze-manifest.json"
JUDGE_AUDIT_REL = "benchmark/study-a/judge-comparators/judge-condition-audit.json"
SENTINELS_REL = "benchmark/study-a/judge-comparators/visible-rule-sentinels.json"
STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
EXPECTED_ROW_COUNT = 54
EXPECTED_ITEM_COUNT = 18
EXPECTED_MODEL_COUNT = 3
EXPECTED_BLOCK_SIZE = 18
ROLE_ARCHIVES = {
    "linguistic_task": "study-a-linguistic-task.zip",
    "policy_safety": "study-a-policy-safety.zip",
}
CANONICAL_RESPONSES_SUBPATH = Path("private") / "responses"
LEGACY_RESPONSES_SUBPATH = Path("responses")
SEED_OUTPUT_BINDING_FIELDS = (
    "item_id",
    "split",
    "pair_id",
    "phenomenon",
    "variant",
    "control_dimension",
    "context_source",
    "source_role",
    "authority_level",
    "pragmatic_status",
    "response_act",
    "prompt",
    "expected_behavior",
    "task_success_label",
    "policy_compliance_label",
    "safety_risk_label",
    "risk_type_label",
    "refusal_outcome_label",
    "failure_attribution_label",
)
AUTHOR_SOURCE_BINDING_FIELDS = (
    "run_id",
    "item_id",
    "model",
    "pair_id",
    "phenomenon",
    "variant",
)

# Exact public-facing study materials that must be finalized and hash-bound by
# the collection gate. Internal preparation notes, outreach drafts, and the
# self-pilot runbook are intentionally outside the evaluator-distribution set.
OPERATIONAL_MATERIALS = (
    "benchmark/study-a/materials/data-return-instructions-draft.md",
    "benchmark/study-a/materials/evaluator-information-and-consent-draft.md",
    "benchmark/study-a/materials/evaluator-quick-start-draft.md",
    "benchmark/study-a/materials/independent-adjudication-one-page.md",
    "benchmark/study-a/materials/privacy-and-release-boundary-draft.md",
    "benchmark/study-a/materials/recruitment-notice-draft.md",
    "benchmark/study-a/materials/study-protocol-draft.md",
    "benchmark/study-a/materials/withdrawal-log-template.csv",
    "benchmark/study-a/materials/withdrawal-procedure-draft.md",
)

PUBLIC_ARTIFACTS = [
    "Makefile",
    SEED_ITEMS_REL,
    "benchmark/study-a/README.md",
    "benchmark/study-a/analysis-plan.md",
    "benchmark/study-a/revision-ledger.md",
    "benchmark/study-a/schema.json",
    "benchmark/study-a/schema.md",
    "benchmark/study-a/training-items.json",
    "benchmark/study-a/materials/README.md",
    *OPERATIONAL_MATERIALS,
    "benchmark/study-a/judge-comparators/judge-labels-mistral-7b.csv",
    "benchmark/study-a/judge-comparators/judge-labels-mistral-24b.csv",
    SENTINELS_REL,
    JUDGE_AUDIT_REL,
    AUTHOR_SNAPSHOT_REL,
    PILOT_MANIFEST_REL,
    "scripts/run_study_a_judge.py",
    "scripts/audit_study_a_judge_condition.py",
    "scripts/analyze_independent_reassessment.py",
    "scripts/ingest_independent_reassessment.py",
    "scripts/simulate_independent_reassessment.py",
    "scripts/study_a_synthetic_fixture.py",
    "scripts/validate_study_a_assignments.py",
    "scripts/build_independent_reassessment.py",
    "scripts/build_study_a_manifest.py",
    "scripts/check_study_a_freeze_ready.py",
    "scripts/check_study_a_collection_ready.py",
]

MODEL_DIGESTS = {
    "mistral:7b-instruct-v0.3-q4_K_M": "6577803aa9a0",
    "mistral-small:24b-instruct-2501-q4_K_M": "8039dd90c113",
}


class ManifestError(RuntimeError):
    """A fail-closed manifest construction error."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    return {"sha256": sha256_file(path), "bytes": path.stat().st_size}


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def read_csv(path: Path, *, delimiter: str = ",") -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=delimiter))


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def has_symlink_component(path: Path, root: Path = ROOT) -> bool:
    """Return true when a scoped path or any in-repository parent is a link."""
    try:
        relative = path.absolute().relative_to(root.absolute())
    except ValueError:
        return True
    current = root.absolute()
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            return True
    return False


def public_artifacts() -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    unsafe: list[str] = []
    for relative in sorted(PUBLIC_ARTIFACTS):
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
            continue
        if has_symlink_component(path):
            unsafe.append(relative)
            continue
        records[relative] = file_record(path)
    if missing:
        raise ManifestError("checkpoint-1 public artifacts are missing: " + ", ".join(missing))
    if unsafe:
        raise ManifestError(
            "checkpoint-1 public artifacts traverse symlinks: " + ", ".join(unsafe)
        )
    return records


def command_inventory(production_root: Path) -> dict[str, Any]:
    production = display_path(production_root)
    package = f"{production}/package"
    private = f"{production}/private"
    responses = f"{private}/responses"
    processed = f"{private}/processed"
    analysis = f"{private}/analysis"
    config = f"{production}/operational-config.json"
    return {
        "judge_comparators": [
            {
                "judge_model": "mistral:7b-instruct-v0.3-q4_K_M",
                "argv": [
                    "python3",
                    "scripts/run_study_a_judge.py",
                    "--judge-model",
                    "mistral:7b-instruct-v0.3-q4_K_M",
                    "--out",
                    "benchmark/study-a/judge-comparators/judge-labels-mistral-7b.csv",
                    "--outputs",
                    SOURCE_OUTPUT_REL,
                    "--keys-from",
                    "benchmark/results/local-pilot-20260630-185417/adjudication_responses.csv",
                    "--seed",
                    "1",
                    "--temperature",
                    "0",
                    "--num-predict",
                    "256",
                    "--timeout",
                    "180",
                ],
                "expected_existing_run_id": "study-a-judge-20260716T095320Z",
                "rerun_required": False,
                "command_would_create_a_new_timestamped_run_id": True,
            },
            {
                "judge_model": "mistral-small:24b-instruct-2501-q4_K_M",
                "argv": [
                    "python3",
                    "scripts/run_study_a_judge.py",
                    "--judge-model",
                    "mistral-small:24b-instruct-2501-q4_K_M",
                    "--out",
                    "benchmark/study-a/judge-comparators/judge-labels-mistral-24b.csv",
                    "--outputs",
                    SOURCE_OUTPUT_REL,
                    "--keys-from",
                    "benchmark/results/local-pilot-20260630-185417/adjudication_responses.csv",
                    "--seed",
                    "1",
                    "--temperature",
                    "0",
                    "--num-predict",
                    "256",
                    "--timeout",
                    "180",
                ],
                "expected_existing_run_id": "study-a-judge-20260716T095536Z",
                "rerun_required": False,
                "command_would_create_a_new_timestamped_run_id": True,
            },
        ],
        "production_package_build": {
            "argv": [
                "python3",
                "scripts/build_independent_reassessment.py",
                "--source",
                SOURCE_OUTPUT_REL,
                "--out-dir",
                package,
                "--private-dir",
                private,
                "--author-labels",
                AUTHOR_SNAPSHOT_REL,
                "--block-size",
                str(EXPECTED_BLOCK_SIZE),
            ],
            "row_salt": "auto_generated_and_retained_only_in_private_metadata",
        },
        "ingest_returns": {
            "argv": [
                "python3",
                "scripts/ingest_independent_reassessment.py",
                "--private-dir",
                private,
                "--responses",
                responses,
                "--out-dir",
                processed,
            ]
        },
        "analyze_returns": {
            "argv": [
                "python3",
                "scripts/analyze_independent_reassessment.py",
                "--private-dir",
                private,
                "--ratings",
                f"{processed}/ratings-long.csv",
                "--out-dir",
                analysis,
                "--judge-labels",
                "benchmark/study-a/judge-comparators/judge-labels-mistral-7b.csv",
                "--judge-labels",
                "benchmark/study-a/judge-comparators/judge-labels-mistral-24b.csv",
            ]
        },
        "write_stamp_2": {
            "argv": [
                "python3",
                "scripts/build_study_a_manifest.py",
                "--write",
                "--stamp",
                "2",
                "--production-root",
                production,
            ]
        },
        "verify_stamp_2": {
            "argv": [
                "python3",
                "scripts/build_study_a_manifest.py",
                "--verify",
                "--require-stamp",
                "2",
                "--production-root",
                production,
            ]
        },
        "freeze_ready": {
            "argv": [
                "python3",
                "scripts/check_study_a_freeze_ready.py",
                "--production-root",
                production,
            ]
        },
        "collection_ready": {
            "argv": [
                "python3",
                "scripts/check_study_a_collection_ready.py",
                "--production-root",
                production,
                "--config",
                config,
            ]
        },
    }


def load_pilot_source_fingerprint() -> dict[str, Any]:
    path = ROOT / PILOT_MANIFEST_REL
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read tracked pilot manifest: {exc}") from exc
    matches = [
        record
        for record in manifest.get("local_source_fingerprints", [])
        if record.get("path") == SOURCE_OUTPUT_REL
    ]
    if len(matches) != 1:
        raise ManifestError(
            f"tracked pilot manifest must contain exactly one fingerprint for {SOURCE_OUTPUT_REL}"
        )
    record = matches[0]
    if record.get("records") != EXPECTED_ROW_COUNT:
        raise ManifestError("tracked source fingerprint does not declare 54 records")
    if not isinstance(record.get("sha256"), str) or len(record["sha256"]) != 64:
        raise ManifestError("tracked source fingerprint has an invalid SHA-256")
    return {
        "path": SOURCE_OUTPUT_REL,
        "sha256": record["sha256"],
        "bytes": record.get("bytes"),
        "records": record.get("records"),
        "declared_in": PILOT_MANIFEST_REL,
    }


def load_pilot_seed_fingerprint() -> dict[str, Any]:
    path = ROOT / PILOT_MANIFEST_REL
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read tracked pilot manifest: {exc}") from exc
    matches = [
        record
        for record in manifest.get("public_files", [])
        if record.get("path") == SEED_ITEMS_REL
    ]
    if len(matches) != 1:
        raise ManifestError(
            f"tracked pilot manifest must contain exactly one fingerprint for "
            f"{SEED_ITEMS_REL}"
        )
    record = matches[0]
    if record.get("records") != EXPECTED_ITEM_COUNT:
        raise ManifestError("tracked seed fingerprint does not declare 18 records")
    if not isinstance(record.get("sha256"), str) or len(record["sha256"]) != 64:
        raise ManifestError("tracked seed fingerprint has an invalid SHA-256")
    return record


def validate_source_output(errors: list[str]) -> tuple[list[dict[str, str]], dict[str, Any]]:
    declared = load_pilot_source_fingerprint()
    declared_seed = load_pilot_seed_fingerprint()
    path = ROOT / SOURCE_OUTPUT_REL
    if not path.is_file():
        errors.append(f"local source output is missing: {SOURCE_OUTPUT_REL}")
        return [], declared
    actual = file_record(path)
    if actual["sha256"] != declared["sha256"]:
        errors.append("local source output SHA-256 does not match the tracked pilot manifest")
    if actual["bytes"] != declared["bytes"]:
        errors.append("local source output byte count does not match the tracked pilot manifest")
    rows = read_csv(path)
    if len(rows) != EXPECTED_ROW_COUNT:
        errors.append(f"local source output has {len(rows)} rows, expected 54")
    required = {"item_id", "model", "prompt", "response"}
    if not rows or not required.issubset(rows[0]):
        errors.append("local source output lacks required item/model/prompt/response columns")
    keys = [(row.get("item_id", ""), row.get("model", "")) for row in rows]
    if len(set(keys)) != EXPECTED_ROW_COUNT:
        errors.append("local source output does not have 54 unique item/model keys")

    seed_path = ROOT / SEED_ITEMS_REL
    seed_rows: list[dict[str, str]] = []
    if not seed_path.is_file():
        errors.append(f"seed item source is missing: {SEED_ITEMS_REL}")
    else:
        seed_record = file_record(seed_path)
        if seed_record["sha256"] != declared_seed.get("sha256"):
            errors.append("seed item SHA-256 does not match the tracked pilot manifest")
        if seed_record["bytes"] != declared_seed.get("bytes"):
            errors.append("seed item byte count does not match the tracked pilot manifest")
        seed_rows = read_csv(seed_path)
        if len(seed_rows) != EXPECTED_ITEM_COUNT:
            errors.append(f"seed item source has {len(seed_rows)} rows, expected 18")

    if seed_rows and rows:
        missing_seed_fields = sorted(
            set(SEED_OUTPUT_BINDING_FIELDS) - set(seed_rows[0])
        )
        missing_output_fields = sorted(
            set(SEED_OUTPUT_BINDING_FIELDS) - set(rows[0])
        )
        if missing_seed_fields:
            errors.append(
                "seed item source lacks binding columns: "
                + ", ".join(missing_seed_fields)
            )
        if missing_output_fields:
            errors.append(
                "local source output lacks seed-binding columns: "
                + ", ".join(missing_output_fields)
            )
        seed_ids = [row.get("item_id", "") for row in seed_rows]
        seed_by_id = {row.get("item_id", ""): row for row in seed_rows}
        if any(not item_id for item_id in seed_ids) or len(seed_by_id) != len(seed_rows):
            errors.append("seed item source has empty or duplicate item_id values")
        output_item_ids = {row.get("item_id", "") for row in rows}
        if output_item_ids != set(seed_by_id):
            errors.append("local source output item IDs do not exactly match seed items")
        models = {row.get("model", "") for row in rows}
        if "" in models or len(models) != EXPECTED_MODEL_COUNT:
            errors.append("local source output does not contain exactly three models")
        item_models: dict[str, set[str]] = {
            item_id: {
                row.get("model", "")
                for row in rows
                if row.get("item_id", "") == item_id
            }
            for item_id in seed_by_id
        }
        if any(item_model_set != models for item_model_set in item_models.values()):
            errors.append("each seed item must have exactly one output from every model")
        if not missing_seed_fields and not missing_output_fields:
            mismatches = [
                f"{row.get('item_id', '')}/{row.get('model', '')}:{field}"
                for row in rows
                if row.get("item_id", "") in seed_by_id
                for field in SEED_OUTPUT_BINDING_FIELDS
                if row.get(field, "")
                != seed_by_id[row.get("item_id", "")].get(field, "")
            ]
            if mismatches:
                preview = ", ".join(mismatches[:8])
                suffix = " ..." if len(mismatches) > 8 else ""
                errors.append(
                    "local source output disagrees with the seed definition at "
                    + preview
                    + suffix
                )
    return rows, {
        **declared,
        "verified_locally": actual["sha256"] == declared["sha256"]
        and actual["bytes"] == declared["bytes"]
        and len(rows) == EXPECTED_ROW_COUNT,
    }


def presentation_digest(row_ids: list[str]) -> str:
    return sha256_bytes(("\n".join(row_ids) + "\n").encode("ascii"))


def validate_json_status(path: Path, label: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing {label}: {display_path(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {label}: {exc}")
        return {}
    if payload.get("status") != "pass":
        errors.append(f"{label} status is not pass")
    if payload.get("errors") not in (None, []):
        errors.append(f"{label} reports errors")
    return payload


def deterministic_zip_bytes(source_dir: Path) -> bytes:
    buffer = io.BytesIO()
    files = sorted(path for path in source_dir.rglob("*") if path.is_file())
    with zipfile.ZipFile(buffer, "w") as archive:
        for source in files:
            relative = source.relative_to(source_dir).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = (0o100644 & 0xFFFF) << 16
            archive.writestr(
                info,
                source.read_bytes(),
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
    return buffer.getvalue()


def validate_role_archive(
    role: str,
    package_dir: Path,
    expected_order_sha: str,
    expected_build_fingerprint: str,
    schema: dict[str, Any],
    isolation_audit: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    role_dir = package_dir / role
    archive_path = package_dir / "distribution" / ROLE_ARCHIVES[role]
    if not role_dir.is_dir():
        errors.append(f"missing role package directory: {display_path(role_dir)}")
        return {}
    required = [
        role_dir / "index.html",
        role_dir / "package-metadata.json",
        role_dir / "training" / "index.html",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"role package is missing {display_path(path)}")
    block_dirs = sorted(role_dir.glob("block-??-of-03"))
    if len(block_dirs) != 3:
        errors.append(f"{role} has {len(block_dirs)} block directories, expected 3")
    if not archive_path.is_file():
        errors.append(f"missing role distribution archive: {display_path(archive_path)}")
        return {}

    # A self-consistent subtree, ZIP, and edited audit JSON could otherwise
    # conceal a copied private file. Independently re-run the builder's exact
    # 12-member allowlist plus opposite-role/content/link checks here against
    # the realized package bytes.
    try:
        independent_isolation = package_builder.role_package_isolation_audit(
            role_dir,
            archive_path,
            role=role,
            schema=schema,
        )
    except SystemExit as exc:
        errors.append(f"{role} independent role-package isolation failed: {exc}")
        independent_isolation = {}
    if independent_isolation.get("status") != "pass":
        errors.append(f"{role} independent role-package isolation did not pass")

    source_files = sorted(path for path in role_dir.rglob("*") if path.is_file())
    source_members = [path.relative_to(role_dir).as_posix() for path in source_files]
    zip_errors_before = len(errors)
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if names != sorted(names) or names != source_members:
                errors.append(f"{role} ZIP members do not match the sorted role subtree")
            for info in infos:
                member = Path(info.filename)
                if member.is_absolute() or ".." in member.parts:
                    errors.append(f"{role} ZIP contains unsafe member {info.filename!r}")
                if info.date_time != (1980, 1, 1, 0, 0, 0):
                    errors.append(f"{role} ZIP member has a non-deterministic timestamp")
                if info.create_system != 3 or ((info.external_attr >> 16) & 0o777) != 0o644:
                    errors.append(f"{role} ZIP member has non-canonical permissions")
                source = role_dir / info.filename
                if source.is_file() and archive.read(info) != source.read_bytes():
                    errors.append(f"{role} ZIP member bytes differ from the role subtree")
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"cannot read {role} distribution archive: {exc}")

    rebuilt = deterministic_zip_bytes(role_dir)
    actual_bytes = archive_path.read_bytes()
    if rebuilt != actual_bytes:
        errors.append(f"{role} distribution archive is not the canonical deterministic ZIP")

    metadata_path = role_dir / "package-metadata.json"
    metadata: dict[str, Any] = {}
    if metadata_path.is_file():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid {role} package metadata: {exc}")
        expected_fields = {
            "study_id": STUDY_ID,
            "schema_version": 7,
            "role": role,
            "package_purpose": "independent_rating",
            "block_count": 3,
            "block_size": EXPECTED_BLOCK_SIZE,
            "presentation_order_sha256": expected_order_sha,
            "package_build_fingerprint_sha256": expected_build_fingerprint,
        }
        for field, expected in expected_fields.items():
            if metadata.get(field) != expected:
                errors.append(f"{role} package metadata {field} is not {expected!r}")
        if not isinstance(metadata.get("package_id"), str) or not metadata.get("package_id"):
            errors.append(f"{role} package metadata lacks a nonblank package_id")

    role_audit = isolation_audit.get("roles", {}).get(role, {})
    actual_sha = sha256_bytes(actual_bytes)
    if role_audit.get("status") != "pass":
        errors.append(f"role isolation audit does not pass for {role}")
    if role_audit.get("archive") != ROLE_ARCHIVES[role]:
        errors.append(f"role isolation audit names the wrong archive for {role}")
    if role_audit.get("archive_sha256") != actual_sha:
        errors.append(f"role isolation audit archive hash is stale for {role}")
    if role_audit.get("file_count") != len(source_files):
        errors.append(f"role isolation audit file count is stale for {role}")
    checks = role_audit.get("checks", {})
    if not checks or not all(value is True for value in checks.values()):
        errors.append(f"role isolation audit checks do not all pass for {role}")

    member_records = [
        {
            "path": path.relative_to(role_dir).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in source_files
    ]
    return {
        "path": display_path(archive_path),
        "sha256": actual_sha,
        "bytes": len(actual_bytes),
        "member_count": len(source_files),
        "member_tree_sha256": sha256_bytes(
            json.dumps(member_records, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ),
        "deterministic_zip_verified": len(errors) == zip_errors_before,
        "package_id": metadata.get("package_id"),
    }


def package_tree_record(package_dir: Path) -> dict[str, Any]:
    files = sorted(path for path in package_dir.rglob("*") if path.is_file())
    records = [
        {
            "path": path.relative_to(package_dir).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
        }
        for path in files
    ]
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "file_count": len(records),
        "total_bytes": sum(record["bytes"] for record in records),
        "sha256": sha256_bytes(encoded),
    }


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def normalized_private_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize only builder-declared volatile fields for exact comparison."""
    normalized = json.loads(json.dumps(payload))
    normalized.pop("generated_at", None)
    presentation = normalized.get("presentation_order")
    if isinstance(presentation, dict):
        presentation["path"] = "<PRIVATE>/presentation-order.tsv"
        presentation["audit_path"] = "<PRIVATE>/presentation-order-audit.json"
    return normalized


def validate_canonical_rebuild(
    production_root: Path,
    row_salt: str,
    errors: list[str],
) -> None:
    """Require realized package bytes to equal a fresh current-builder run.

    This is the primary defense against a self-consistent edit to a permitted
    HTML/TSV/README member followed by rebuilt ZIPs and edited audit hashes.
    The private metadata itself contains a timestamp and absolute paths, so we
    compare the deterministic private artifacts separately.
    """
    if len(row_salt) < 32:
        return
    with tempfile.TemporaryDirectory(prefix="study-a-canonical-rebuild-") as temporary:
        temporary_root = Path(temporary)
        canonical_package = temporary_root / "package"
        canonical_private = temporary_root / "private"
        command = [
            sys.executable,
            str(ROOT / "scripts" / "build_independent_reassessment.py"),
            "--source",
            str(ROOT / SOURCE_OUTPUT_REL),
            "--out-dir",
            str(canonical_package),
            "--private-dir",
            str(canonical_private),
            "--author-labels",
            AUTHOR_SNAPSHOT_REL,
            "--row-salt",
            row_salt,
            "--block-size",
            str(EXPECTED_BLOCK_SIZE),
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            errors.append(
                "canonical package rebuild failed with the current scoped builder"
                + (f": {detail[-1000:]}" if detail else "")
            )
            return

        actual_tree = tree_hashes(production_root / "package")
        canonical_tree = tree_hashes(canonical_package)
        if actual_tree != canonical_tree:
            missing = sorted(set(canonical_tree) - set(actual_tree))
            extra = sorted(set(actual_tree) - set(canonical_tree))
            changed = sorted(
                path
                for path in set(actual_tree) & set(canonical_tree)
                if actual_tree[path] != canonical_tree[path]
            )
            errors.append(
                "realized package tree is not byte-identical to a canonical current-builder rebuild; "
                f"missing={missing!r}, extra={extra!r}, changed={changed!r}"
            )

        for name in (
            "row_map.tsv",
            "presentation-order.tsv",
            "presentation-order-audit.json",
            "author_labels.csv",
        ):
            actual = production_root / "private" / name
            canonical = canonical_private / name
            if not actual.is_file() or actual.is_symlink() or actual.read_bytes() != canonical.read_bytes():
                errors.append(
                    f"private {name} is not byte-identical to the canonical current-builder rebuild"
                )

        actual_metadata_path = production_root / "private" / "study-private-metadata.json"
        canonical_metadata_path = canonical_private / "study-private-metadata.json"
        try:
            actual_metadata = json.loads(actual_metadata_path.read_text(encoding="utf-8"))
            canonical_metadata = json.loads(canonical_metadata_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"cannot compare canonical private metadata: {exc}")
        else:
            if not isinstance(actual_metadata, dict) or not isinstance(canonical_metadata, dict):
                errors.append("private metadata must be JSON objects for canonical comparison")
            elif normalized_private_metadata(actual_metadata) != normalized_private_metadata(
                canonical_metadata
            ):
                errors.append(
                    "private metadata differs from canonical current-builder metadata after "
                    "normalizing only generated_at and private presentation paths"
                )


def response_boundary_errors(production_root: Path) -> list[str]:
    """Require the actual ingestion return store to be empty and unaliased."""
    errors: list[str] = []
    canonical = production_root / CANONICAL_RESPONSES_SUBPATH
    legacy = production_root / LEGACY_RESPONSES_SUBPATH
    if canonical.is_symlink():
        errors.append("canonical private responses path must not be a symlink")
    elif canonical.exists():
        if not canonical.is_dir():
            errors.append("canonical private responses path is not a directory")
        elif any(canonical.iterdir()):
            errors.append("canonical private responses directory is not empty")
    if legacy.is_symlink() or legacy.exists():
        errors.append(
            "legacy production responses path must be absent; returns belong under "
            "production/private/responses"
        )
    return errors


def validate_production(production_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    source_rows, source_fingerprint = validate_source_output(errors)
    expected_build_fingerprint = (
        package_builder.package_build_fingerprint(ROOT / SOURCE_OUTPUT_REL)
        if (ROOT / SOURCE_OUTPUT_REL).is_file()
        else ""
    )
    schema = package_builder.load_schema()
    source_keys = {
        (row.get("item_id", ""), row.get("model", "")) for row in source_rows
    }
    private_dir = production_root / "private"
    package_dir = production_root / "package"
    if production_root.is_symlink():
        errors.append("production root must not be a symlink")
    if private_dir.is_symlink():
        errors.append("production private directory must not be a symlink")
    if not private_dir.is_dir():
        errors.append(f"production private directory is missing: {display_path(private_dir)}")
    if package_dir.is_symlink():
        errors.append("production package directory must not be a symlink")
    if not package_dir.is_dir():
        errors.append(f"production package directory is missing: {display_path(package_dir)}")
    errors.extend(response_boundary_errors(production_root))
    if package_dir.exists():
        symlinks = [
            display_path(path)
            for path in package_dir.rglob("*")
            if path.is_symlink()
        ]
        if symlinks:
            errors.append(f"production package contains symlinks: {symlinks!r}")
        distribution_dir = package_dir / "distribution"
        distribution_files = (
            {path.name for path in distribution_dir.iterdir() if path.is_file()}
            if distribution_dir.is_dir()
            else set()
        )
        expected_distribution_files = set(ROLE_ARCHIVES.values())
        if distribution_files != expected_distribution_files:
            errors.append(
                "distribution directory must contain exactly the two canonical role ZIPs"
            )

    row_map_path = private_dir / "row_map.tsv"
    order_path = private_dir / "presentation-order.tsv"
    order_audit_path = private_dir / "presentation-order-audit.json"
    metadata_path = private_dir / "study-private-metadata.json"
    author_path = private_dir / "author_labels.csv"
    required_private = [row_map_path, order_path, order_audit_path, metadata_path, author_path]
    for path in required_private:
        if not path.is_file() or path.is_symlink():
            errors.append(
                f"required production artifact is missing or symlinked: "
                f"{display_path(path)}"
            )

    mapping = read_csv(row_map_path, delimiter="\t") if row_map_path.is_file() else []
    required_map_fields = {"row_id", "item_id", "model", "source_record_index"}
    if not mapping or not required_map_fields.issubset(mapping[0]):
        errors.append("row_map.tsv lacks required fields")
    if len(mapping) != EXPECTED_ROW_COUNT:
        errors.append(f"row_map.tsv has {len(mapping)} rows, expected 54")
    row_ids = [row.get("row_id", "") for row in mapping]
    map_keys = [(row.get("item_id", ""), row.get("model", "")) for row in mapping]
    if len(set(row_ids)) != EXPECTED_ROW_COUNT or "" in row_ids:
        errors.append("row_map.tsv does not contain 54 unique nonblank row IDs")
    if len(set(map_keys)) != EXPECTED_ROW_COUNT or set(map_keys) != source_keys:
        errors.append("row_map.tsv item/model keys do not exactly match the source output")
    for row in mapping:
        try:
            source_index = int(row.get("source_record_index", ""))
        except ValueError:
            errors.append(f"invalid source_record_index for row {row.get('row_id')!r}")
            continue
        if not 1 <= source_index <= len(source_rows):
            errors.append(f"source_record_index out of range for row {row.get('row_id')!r}")
            continue
        source = source_rows[source_index - 1]
        if (row.get("item_id"), row.get("model")) != (source.get("item_id"), source.get("model")):
            errors.append(f"row map source join mismatch for row {row.get('row_id')!r}")

    order_rows = read_csv(order_path, delimiter="\t") if order_path.is_file() else []
    order_ids = [row.get("row_id", "") for row in order_rows]
    if len(order_rows) != EXPECTED_ROW_COUNT or order_ids != row_ids:
        errors.append("presentation-order.tsv does not exactly record row_map.tsv order")
    for index, row in enumerate(order_rows, start=1):
        expected_block = f"block-{((index - 1) // EXPECTED_BLOCK_SIZE) + 1:02d}-of-03"
        expected_position = ((index - 1) % EXPECTED_BLOCK_SIZE) + 1
        if row.get("global_position") != str(index):
            errors.append("presentation-order.tsv global positions are not sequential")
            break
        if row.get("block_id") != expected_block or row.get("block_position") != str(expected_position):
            errors.append("presentation-order.tsv block positions are inconsistent")
            break
    order_sha = presentation_digest(row_ids) if row_ids and all(row_ids) else ""
    order_audit = validate_json_status(order_audit_path, "presentation-order audit", errors)
    if order_audit:
        if order_audit.get("row_count") != EXPECTED_ROW_COUNT:
            errors.append("presentation-order audit row_count is not 54")
        if order_audit.get("algorithm") != "balanced-item-model-grid-v1":
            errors.append("presentation-order audit algorithm is unexpected")
        if order_audit.get("adjacent_same_item_pairs") != 0:
            errors.append("presentation-order audit reports adjacent same-item rows")
        invariants = order_audit.get("invariants", {})
        if not invariants or not all(value is True for value in invariants.values()):
            errors.append("presentation-order audit invariants do not all pass")

    mapping_by_id = {row.get("row_id", ""): row for row in mapping}
    source_by_key = {
        (row.get("item_id", ""), row.get("model", "")): row for row in source_rows
    }
    role_orders: dict[str, list[str]] = {}
    for role in ROLE_ARCHIVES:
        blind_rows: list[dict[str, str]] = []
        block_dirs = sorted((package_dir / role).glob("block-??-of-03"))
        for block_dir in block_dirs:
            blind_path = block_dir / "blind-items.tsv"
            if not blind_path.is_file():
                errors.append(f"missing blind item table: {display_path(blind_path)}")
                continue
            block_rows = read_csv(blind_path, delimiter="\t")
            if len(block_rows) != EXPECTED_BLOCK_SIZE:
                errors.append(f"{display_path(blind_path)} does not have 18 rows")
            blind_rows.extend(block_rows)
        role_order = [row.get("row_id", "") for row in blind_rows]
        role_orders[role] = role_order
        if role_order != row_ids:
            errors.append(f"{role} blind tables do not follow the fixed presentation order")
        for blind in blind_rows:
            mapped = mapping_by_id.get(blind.get("row_id", ""))
            if mapped is None:
                errors.append(f"{role} blind table contains an unknown row ID")
                continue
            source = source_by_key.get((mapped.get("item_id", ""), mapped.get("model", "")))
            if source is None or blind.get("prompt") != source.get("prompt") or blind.get("response") != source.get("response"):
                errors.append(f"{role} blind prompt/response does not match source for one row")
    if role_orders.get("linguistic_task") != role_orders.get("policy_safety"):
        errors.append("the two roles do not use the same fixed presentation order")

    if len(mapping) == EXPECTED_ROW_COUNT:
        adjacent = [
            index
            for index, (left, right) in enumerate(zip(mapping, mapping[1:]), start=1)
            if left.get("item_id") == right.get("item_id")
        ]
        if adjacent:
            errors.append(f"same-item rows are adjacent after positions {adjacent!r}")
        item_ids = {row.get("item_id", "") for row in mapping}
        models = {row.get("model", "") for row in mapping}
        if len(item_ids) != EXPECTED_ITEM_COUNT or len(models) != EXPECTED_MODEL_COUNT:
            errors.append("row map is not the expected 18-item by 3-model grid")
        for block_index in range(3):
            block = mapping[
                block_index * EXPECTED_BLOCK_SIZE : (block_index + 1) * EXPECTED_BLOCK_SIZE
            ]
            item_counts = Counter(row.get("item_id", "") for row in block)
            model_counts = Counter(row.get("model", "") for row in block)
            if set(item_counts.values()) != {1} or set(item_counts) != item_ids:
                errors.append(f"presentation block {block_index + 1} lacks one row per item")
            if set(model_counts) != models or any(count != 6 for count in model_counts.values()):
                errors.append(f"presentation block {block_index + 1} is not six-per-model")

    author_snapshot = ROOT / AUTHOR_SNAPSHOT_REL
    author_rows = read_csv(author_snapshot)
    author_keys = [
        (row.get("item_id", ""), row.get("model", "")) for row in author_rows
    ]
    if len(author_rows) != EXPECTED_ROW_COUNT or len(set(author_keys)) != EXPECTED_ROW_COUNT:
        errors.append("tracked author snapshot does not contain 54 unique item/model keys")
    if set(author_keys) != source_keys:
        errors.append("tracked author snapshot keys do not exactly match the source output")
    author_source_mismatches = [
        f"{row.get('item_id', '')}/{row.get('model', '')}:{field}"
        for row in author_rows
        if (row.get("item_id", ""), row.get("model", "")) in source_by_key
        for field in AUTHOR_SOURCE_BINDING_FIELDS
        if row.get(field, "")
        != source_by_key[(row.get("item_id", ""), row.get("model", ""))].get(
            field, ""
        )
    ]
    if author_source_mismatches:
        preview = ", ".join(author_source_mismatches[:8])
        suffix = " ..." if len(author_source_mismatches) > 8 else ""
        errors.append(
            "tracked author snapshot metadata disagrees with the source output at "
            + preview
            + suffix
        )
    schema = json.loads((ROOT / "benchmark/study-a/schema.json").read_text(encoding="utf-8"))
    allowed_author_targets: dict[str, set[str]] = {}
    for role_schema in schema.get("roles", {}).values():
        for field in role_schema.get("fields", []):
            name = field.get("name")
            if name in {"task_success", "policy_compliance", "refusal_outcome"}:
                allowed_author_targets[name] = set(field.get("options", []))
    for row in author_rows:
        for field in ("task_success", "policy_compliance", "refusal_outcome"):
            value = row.get(field, "")
            if field == "refusal_outcome" and value == "not_applicable":
                value = "not_a_refusal"
            if value not in allowed_author_targets.get(field, set()):
                errors.append(
                    f"tracked author snapshot has an invalid {field} value for one row"
                )
                break
    if author_path.is_file() and author_path.read_bytes() != author_snapshot.read_bytes():
        errors.append("private author_labels.csv is not byte-identical to the tracked snapshot")

    private_metadata: dict[str, Any] = {}
    row_salt = ""
    if metadata_path.is_file():
        try:
            private_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid private package metadata: {exc}")
        for field, expected in {
            "study_id": STUDY_ID,
            "package_purpose": "independent_rating",
            "row_count": EXPECTED_ROW_COUNT,
            "block_size": EXPECTED_BLOCK_SIZE,
            "block_count": 3,
        }.items():
            if private_metadata.get(field) != expected:
                errors.append(f"private package metadata {field} is not {expected!r}")
        presentation = private_metadata.get("presentation_order", {})
        if presentation.get("algorithm") != "balanced-item-model-grid-v1":
            errors.append("private package metadata presentation-order algorithm is unexpected")
        if presentation.get("sha256") != order_sha:
            errors.append("private package metadata presentation-order hash is stale")
        if presentation.get("common_fixed_order_across_roles") is not True:
            errors.append("private package metadata does not declare one common fixed order")
        if presentation.get("path") not in {
            "presentation-order.tsv",
            str(order_path),
            display_path(order_path),
        }:
            errors.append("private package metadata presentation-order path is unexpected")
        if presentation.get("audit_path") not in {
            "presentation-order-audit.json",
            str(order_audit_path),
            display_path(order_audit_path),
        }:
            errors.append("private package metadata presentation-order audit path is unexpected")
        metadata_row_salt = private_metadata.get("row_salt")
        if not isinstance(metadata_row_salt, str) or len(metadata_row_salt) < 32:
            errors.append("private package metadata lacks a nontrivial private row salt")
        else:
            row_salt = metadata_row_salt
        if (
            private_metadata.get("package_build_fingerprint_sha256")
            != expected_build_fingerprint
        ):
            errors.append("private package metadata has a stale package-build fingerprint")
        source_value = private_metadata.get("source")
        if not isinstance(source_value, str) or Path(source_value).resolve() != (ROOT / SOURCE_OUTPUT_REL).resolve():
            errors.append("private package metadata source does not resolve to the pinned output")

    validate_canonical_rebuild(production_root, row_salt, errors)

    blind_audit = validate_json_status(
        package_dir / "blind-package-audit.json", "blind-package audit", errors
    )
    training_audit = validate_json_status(
        package_dir / "training-package-audit.json", "training-package audit", errors
    )
    if blind_audit.get("checks") and not all(
        value is True for value in blind_audit["checks"].values()
    ):
        errors.append("blind-package audit checks do not all pass")
    if training_audit and (
        training_audit.get("practice_only") is not True
        or training_audit.get("separate_from_blind_study_rows") is not True
    ):
        errors.append("training-package audit does not establish practice-only separation")
    isolation_audit = validate_json_status(
        package_dir / "role-package-isolation-audit.json", "role-package isolation audit", errors
    )
    if isolation_audit.get("combined_role_chooser_distributed") is not False:
        errors.append("role-package isolation audit does not bar a combined role chooser")
    if (package_dir / "index.html").exists():
        errors.append("independent production package contains a combined role chooser")

    role_records: dict[str, dict[str, Any]] = {}
    for role in ROLE_ARCHIVES:
        role_records[role] = validate_role_archive(
            role,
            package_dir,
            order_sha,
            expected_build_fingerprint,
            schema,
            isolation_audit,
            errors,
        )
    if role_records.get("linguistic_task", {}).get("package_id") == role_records.get(
        "policy_safety", {}
    ).get("package_id"):
        errors.append("role packages do not have distinct package IDs")

    if private_metadata:
        package_ids = private_metadata.get("package_ids", {})
        distributions = private_metadata.get("distribution_archives", {})
        row_salt = private_metadata.get("row_salt", "")
        for role, record in role_records.items():
            if package_ids.get(role) != record.get("package_id"):
                errors.append(f"private package metadata has a stale package_id for {role}")
            declared_archive = distributions.get(role, {})
            if declared_archive.get("sha256") != record.get("sha256"):
                errors.append(f"private package metadata has a stale archive hash for {role}")
            if Path(str(declared_archive.get("path", ""))).name != ROLE_ARCHIVES[role]:
                errors.append(f"private package metadata has a stale archive path for {role}")
            if isinstance(row_salt, str):
                expected_package_id = package_builder.opaque_package_id(
                    row_salt, STUDY_ID, role, expected_build_fingerprint
                )
                if record.get("package_id") != expected_package_id:
                    errors.append(
                        f"role package ID is not bound to the current build fingerprint for {role}"
                    )

    if errors:
        raise ManifestError("stamp-2 production validation failed:\n  - " + "\n  - ".join(errors))

    private_records = {
        "row_map": {"path": display_path(row_map_path), **file_record(row_map_path)},
        "presentation_order": {
            "path": display_path(order_path),
            **file_record(order_path),
            "row_id_sequence_sha256": order_sha,
            "row_count": len(row_ids),
        },
        "presentation_order_audit": {
            "path": display_path(order_audit_path),
            **file_record(order_audit_path),
            "status": order_audit.get("status"),
        },
        "private_metadata": {
            "path": display_path(metadata_path),
            **file_record(metadata_path),
            "contents_exposed_in_manifest": False,
        },
        "author_snapshot": {"path": display_path(author_path), **file_record(author_path)},
    }
    package_audits = {
        "blind_package": {
            "path": display_path(package_dir / "blind-package-audit.json"),
            **file_record(package_dir / "blind-package-audit.json"),
            "status": blind_audit.get("status"),
        },
        "training_package": {
            "path": display_path(package_dir / "training-package-audit.json"),
            **file_record(package_dir / "training-package-audit.json"),
            "status": training_audit.get("status"),
        },
        "role_isolation": {
            "path": display_path(package_dir / "role-package-isolation-audit.json"),
            **file_record(package_dir / "role-package-isolation-audit.json"),
            "status": isolation_audit.get("status"),
        },
    }
    return {
        "production_root": display_path(production_root),
        "source_output": source_fingerprint,
        "package_build_fingerprint_sha256": expected_build_fingerprint,
        "presentation": {
            "row_count": EXPECTED_ROW_COUNT,
            "block_count": 3,
            "block_size": EXPECTED_BLOCK_SIZE,
            "row_id_sequence_sha256": order_sha,
            "same_order_across_roles": True,
            "adjacent_same_item_pairs": 0,
            "each_block_has_each_item_once": True,
            "each_block_has_six_rows_per_model": True,
        },
        "private_artifacts": private_records,
        "package_tree": package_tree_record(package_dir),
        "package_audits": package_audits,
        "role_archives": role_records,
        "responses_absent_or_empty": True,
    }


def build_manifest(stamp: int, production_root: Path = DEFAULT_PRODUCTION_ROOT) -> dict[str, Any]:
    if stamp not in {1, 2}:
        raise ManifestError("freeze stamp must be 1 or 2")
    manifest: dict[str, Any] = {
        "manifest_version": 2,
        "study": "A",
        "purpose": (
            "two-stage pre-unblinding checkpoint record; no freeze is accomplished and "
            "collection remains closed until the annotated-tag and operational-config "
            "collection gate passes"
        ),
        "schema_version": 7,
        "freeze_stamp": stamp,
        "freeze_status": "pre_freeze_checkpoint" if stamp == 1 else "ready_for_tag",
        "freeze_accomplished": False,
        "checkpoint_mutability": (
            "mutable_pre_freeze_checkpoint" if stamp == 1 else "candidate_pending_explicit_tag"
        ),
        "open_returns_authorized": False,
        "model_digests": MODEL_DIGESTS,
        "judge_condition": {
            "prompt_variant": "option_a_v7_roleseparated",
            "role_separated": True,
            "scaffold": "outcome_only",
            "human_full_role_scaffold_matched": False,
            "structural_audit": JUDGE_AUDIT_REL,
            "visible_rule_sentinels": SENTINELS_REL,
            "sentinel_selection_timing": "post_comparator_output_pre_freeze",
            "sentinel_mismatches_invalidate_comparators": False,
        },
        "commands": command_inventory(production_root),
        "public_artifacts": public_artifacts(),
        "checkpoint_1_inputs": {
            "pilot_source_fingerprint_manifest": {
                "path": PILOT_MANIFEST_REL,
                **file_record(ROOT / PILOT_MANIFEST_REL),
            },
            "provisional_author_snapshot": {
                "path": AUTHOR_SNAPSHOT_REL,
                **file_record(ROOT / AUTHOR_SNAPSHOT_REL),
                "interpretation": (
                    "historical provisional author labels for comparison, not independent "
                    "response-level gold"
                ),
            },
        },
        "deviations_recorded_in": "benchmark/study-a/revision-ledger.md",
    }
    if stamp == 1:
        manifest["source_fingerprint_record"] = load_pilot_source_fingerprint()
        manifest["not_yet_frozen"] = [
            "local_source_fingerprint_verification",
            "production_row_map",
            "production_presentation_order",
            "production_private_metadata",
            "production_role_packages_and_distribution_archives",
        ]
    else:
        manifest["production_candidate"] = validate_production(production_root)
        manifest["not_yet_frozen"] = []
    return manifest


def compare_payloads(recorded: dict[str, Any], expected: dict[str, Any]) -> list[str]:
    if recorded == expected:
        return []
    errors = ["manifest semantics or recorded artifact hashes differ from the current expected state"]
    all_keys = sorted(set(recorded) | set(expected))
    for key in all_keys:
        if recorded.get(key) != expected.get(key):
            errors.append(f"top-level field differs: {key}")
    return errors


def legacy_v1_checkpoint(recorded: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = [
        "legacy manifest v1 accepted only as a readable historical checkpoint; "
        "it does not establish semantic freeze readiness or authorize collection"
    ]
    if recorded.get("manifest_version") not in (None, 1):
        errors.append("unsupported manifest version cannot be treated as legacy v1")
    if recorded.get("study") != "A" or recorded.get("freeze_stamp") != 1:
        errors.append("legacy manifest is not a Study A stamp-1 record")
    if recorded.get("model_digests") != MODEL_DIGESTS:
        errors.append("legacy manifest model digests are not the pinned comparator digests")
    artifacts = recorded.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts:
        errors.append("legacy manifest has no artifact inventory")
        return errors, warnings
    for relative, metadata in artifacts.items():
        if not isinstance(relative, str) or not isinstance(metadata, dict):
            errors.append("legacy artifact inventory is malformed")
            continue
        digest = metadata.get("sha256")
        size = metadata.get("bytes")
        if not isinstance(digest, str) or len(digest) != 64 or not isinstance(size, int):
            errors.append(f"legacy artifact metadata is malformed: {relative}")
            continue
        path = ROOT / relative
        if not path.is_file():
            warnings.append(f"legacy artifact is no longer present: {relative}")
        elif sha256_file(path) != digest or path.stat().st_size != size:
            warnings.append(f"legacy checkpoint drift is present: {relative}")
    return errors, warnings


def verify_manifest(
    manifest_path: Path = DEFAULT_MANIFEST,
    production_root: Path = DEFAULT_PRODUCTION_ROOT,
    *,
    require_stamp: int | None = None,
    allow_legacy_v1: bool = False,
) -> list[str]:
    if not manifest_path.is_file():
        return [f"manifest is missing: {display_path(manifest_path)}"]
    try:
        recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"manifest is not valid JSON: {exc}"]
    if recorded.get("manifest_version") != 2:
        if not allow_legacy_v1:
            return [
                "manifest is legacy v1; semantic verification requires manifest_version 2 "
                "(use --allow-legacy-v1 only for a non-authorizing checkpoint inspection)"
            ]
        errors, _warnings = legacy_v1_checkpoint(recorded)
        if require_stamp == 2:
            errors.append("legacy v1 can never satisfy a required stamp 2")
        return errors
    stamp = recorded.get("freeze_stamp")
    if stamp not in {1, 2}:
        return [f"manifest freeze_stamp is invalid: {stamp!r}"]
    if require_stamp is not None and stamp != require_stamp:
        return [f"manifest stamp is {stamp}, required {require_stamp}"]
    try:
        expected = build_manifest(int(stamp), production_root)
    except ManifestError as exc:
        return [str(exc)]
    return compare_payloads(recorded, expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the selected stamp")
    mode.add_argument("--print", dest="print_output", action="store_true", help="print it")
    mode.add_argument("--verify", action="store_true", help="verify an existing manifest")
    parser.add_argument("--stamp", type=int, choices=(1, 2), default=1)
    parser.add_argument("--require-stamp", type=int, choices=(1, 2), default=None)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--production-root", type=Path, default=DEFAULT_PRODUCTION_ROOT)
    parser.add_argument("--allow-legacy-v1", action="store_true")
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    production_root = args.production_root.absolute()
    if not args.verify and args.require_stamp is not None:
        parser.error("--require-stamp is valid only with --verify")
    if not args.verify and args.allow_legacy_v1:
        parser.error("--allow-legacy-v1 is valid only with --verify")

    if args.verify:
        errors = verify_manifest(
            manifest_path,
            production_root,
            require_stamp=args.require_stamp,
            allow_legacy_v1=args.allow_legacy_v1,
        )
        try:
            recorded = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            recorded = {}
        if recorded.get("manifest_version") != 2 and args.allow_legacy_v1:
            _legacy_errors, warnings = legacy_v1_checkpoint(recorded)
            for warning in warnings:
                print(f"WARNING: {warning}")
        if errors:
            print("Study A manifest verification failed:")
            for error in errors:
                print(f"  - {error}")
            raise SystemExit(1)
        if recorded.get("manifest_version") == 2:
            print(
                f"OK: semantic Study A manifest v2 stamp {recorded['freeze_stamp']} verifies."
            )
        else:
            print("OK: legacy Study A checkpoint is readable (not freeze-ready).")
        return

    try:
        payload = build_manifest(args.stamp, production_root)
    except ManifestError as exc:
        print(exc)
        raise SystemExit(1) from exc
    rendered = canonical_json(payload)
    if args.print_output:
        print(rendered, end="")
        return
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {display_path(manifest_path)} as semantic manifest v2 stamp {args.stamp}. "
        "No tag was created and returns remain closed."
    )


if __name__ == "__main__":
    main()
