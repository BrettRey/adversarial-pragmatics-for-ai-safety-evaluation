#!/usr/bin/env python3
"""Fail-closed validation for privacy-minimized naturalistic corpus v2."""

from __future__ import annotations

import argparse
import base64
import binascii
import csv
import hashlib
import hmac
import json
import os
import re
import stat
import subprocess
from collections import defaultdict
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "private"
DISCOVERY_ROOT = PRIVATE_ROOT / "discovery"
RESTRICTED_ROOT = PRIVATE_ROOT / "restricted"

CLASSES = {"likely_pragmatic_failure", "surprising_success_candidate"}
SOURCES = {"codex", "claude"}
RECONSTRUCTION_STATUSES = {
    "automatic_minimization",
    "manual_controlled_reconstruction_required",
}
PRIVACY_DISPOSITION = "internal_review_only"
MAX_TEXT_FIELD_CHARS = 1_600
MAX_PRECEDING_TURN_CHARS = 900
MAX_PRECEDING_TURNS = 2
MAX_EPISODE_TEXT_CHARS = 7_000
EXPECTED_RESIDUAL_CATEGORIES = {
    "absolute_or_home_path",
    "email",
    "phone",
    "url",
    "handle",
    "credential_context",
    "private_key",
    "active_markup",
    "network_code",
    "correspondence_header",
    "code_fence",
    "honorific_name",
    "organization_pattern",
    "proper_name_pattern",
}
CANONICAL_ALTERNATIVE_EXPLANATIONS = {
    "user_changed_request",
    "clarification_needed",
    "non_pragmatic_error",
    "lost_or_hidden_context",
    "reasonable_competing_reading",
    "insufficient_evidence",
}
CANONICAL_PRIMARY_PHENOMENA = {
    "repair_uptake",
    "scope_and_authorization",
    "task_type_recognition",
    "completion_and_status_reporting",
    "reference_and_ellipsis",
    "state_and_compaction",
    "negative_constraint_persistence",
    "tool_action_alignment",
    "general_assessment",
    "other_pragmatic_candidate",
    "insufficient_evidence",
}
FAILURE_EVIDENCE_SIGNAL_WEIGHTS = {
    "explicit_not_requested": 5,
    "explicit_misunderstanding": 4,
    "scope_or_file_correction": 4,
    "reasserted_negative_constraint": 2,
    "instruction_repetition": 3,
    "stop_or_revert": 4,
    "completion_or_status_challenge": 3,
    "action_answer_mismatch": 4,
    "strong_negative_assessment": 2,
    "repair_non_uptake": 3,
}
SUCCESS_EVIDENCE_SIGNAL_WEIGHTS = {
    "explicit_exactness": 4,
    "explicit_catch": 4,
    "strong_positive_assessment": 3,
    "explicit_worked": 3,
    "dependent_continuation": 2,
    "explicit_acknowledgment": 2,
    "verified_tool_success": 1,
}
PRAGMATIC_LOAD_SIGNAL_WEIGHTS = {
    "negative_constraint": 2,
    "scope_boundary": 2,
    "reference_or_ellipsis": 1,
    "authority_or_permission": 2,
    "task_type_boundary": 2,
    "multi_stage_or_stop_condition": 1,
    "short_context_dependent_request": 1,
    "post_compaction_state_recovery": 2,
    "repair_conditioned_turn": 2,
}
CANONICAL_TOOL_ACTION_CLASSES = {
    "messaging",
    "scheduling",
    "web_or_browser",
    "artifact_change",
    "artifact_read",
    "version_control",
    "delegation",
    "shell_or_process",
    "other_tool_action",
}
CANONICAL_REDACTION_COUNT_KEYS = {
    "credential_context_withheld",
    "correspondence_withheld",
    "active_content_withheld",
    "raw_tool_text_withheld",
    "pasted_material_withheld",
    "acronym",
    "proper_token",
    "code_block",
    "owner_identifier",
    "private_context",
    "url",
    "email",
    "local_path",
    "phone",
    "handle",
    "network_identifier",
    "identifier",
    "date",
    "file_name",
    "address",
    "postal_code",
    "person",
    "organization",
    "proper_name",
    "markup",
    "residual_risk_withheld",
}

REQUIRED_CORPUS_FILES = {
    "README.md",
    "candidate-index.jsonl",
    "corpus-manifest.json",
    "reports/corpus-profile.md",
    "reports/privatization-audit.json",
    "reports/residual-risk-audit.json",
    "reports/retrieval-audit.json",
    "review-corpus.jsonl",
    "review/README.md",
    "review/index.html",
}
OPTIONAL_AUDIT_KINDS = {
    "reports/contextual-privacy-audit.json": (
        "naturalistic_corpus_contextual_privacy_audit"
    ),
    "reports/legacy-v1-aggregate-privacy-audit.json": (
        "aggregate_naturalistic_corpus_privacy_audit"
    ),
    "reports/legacy-audit-derivative-aggregate-privacy-audit.json": (
        "aggregate_naturalistic_corpus_privacy_audit"
    ),
}
AGGREGATE_AUDIT_TOP_LEVEL_FIELDS = {
    "aggregate_findings",
    "audit_policy",
    "detected_layout",
    "duplication",
    "files",
    "generated_at",
    "inventory",
    "kind",
    "provenance_and_linkage",
    "renderer_structural_totals",
    "schema_version",
    "tree_security",
}
CONTEXTUAL_AUDIT_TOP_LEVEL_FIELDS = {
    "corpus_version",
    "disposition_counts",
    "generated_at",
    "interpretation_codes",
    "kind",
    "manual_pattern_review",
    "overlapping_row_counts",
    "sample_size",
    "sampling_method",
    "schema_version",
}
ALLOWED_CORPUS_FILES = REQUIRED_CORPUS_FILES | set(OPTIONAL_AUDIT_KINDS)
RESTRICTED_FILES = {"id-key.bin", "source-linkage.csv", "source-fingerprints.csv"}

README_HEADINGS = {
    "README.md": "# Privacy-Minimized Naturalistic Pragmatic Extremes Corpus",
    "review/README.md": "# Private Pragmatic-Extremes Review",
}

CANDIDATE_FIELDS = {
    "candidate_id",
    "session_ref",
    "source",
    "session_mode",
    "month",
    "candidate_class",
    "candidate_score",
    "evidence_strength",
    "primary_phenomenon",
    "evidence_signals",
    "pragmatic_load_signals",
    "alternative_explanations",
    "compaction_before",
    "tool_event_count",
    "tool_action_classes",
    "content_withheld_fields",
    "redaction_counts",
    "privacy_disposition",
    "reconstruction_status",
    "review_selected",
}
DIRECT_REVIEW_TEXT_FIELDS = {
    "triggering_request",
    "model_visible_response",
    "user_followup",
    "immediate_model_response",
}
REVIEW_FIELDS = (
    CANDIDATE_FIELDS
    - {"review_selected"}
    | DIRECT_REVIEW_TEXT_FIELDS
    | {"preceding_context", "text_char_count"}
)

LINKAGE_FIELDS = [
    "candidate_id",
    "session_ref",
    "source",
    "source_ref",
    "raw_path",
    "session_id",
    "trigger_turn_index",
    "feedback_turn_index",
    "trigger_node_id",
    "feedback_node_id",
    "start_line",
    "end_line",
]
FINGERPRINT_FIELDS = ["source_ref", "source", "raw_path", "source_sha256", "byte_size"]

CANDIDATE_ID_RE = re.compile(r"^NPE2-[A-F0-9]{24}$")
SESSION_REF_RE = re.compile(r"^SES2-[A-F0-9]{20}$")
ROW_ID_IN_TEXT_RE = re.compile(r"\b(?:NPE2-[A-F0-9]{24}|SES2-[A-F0-9]{20})\b")
SOURCE_REF_RE = re.compile(r"^[A-Z][A-Z0-9]*2-[A-F0-9]{16,64}$")
MONTH_RE = re.compile(r"^\d{4}-(?:0[1-9]|1[0-2])$")
SNAKE_RE = re.compile(r"^[a-z][a-z0-9_]{0,79}$")
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")

# Deterministic residual-risk rules deliberately trade recall for false positives:
# questionable fields should have been withheld, not waved through here.
EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]{1,64}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HTTP_URL_RE = re.compile(r"(?i)\bhttps?://[^\s<>'\"]+")
WWW_RE = re.compile(r"(?i)\bwww\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
HANDLE_RE = re.compile(r"(?<![\w@])@[A-Za-z][A-Za-z0-9_.-]{2,30}\b")
PHONE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:\+?1[\s.()-]*)?(?:\(?\d{3}\)?[\s.-]*)\d{3}[\s.-]*\d{4}"
    r"(?![A-Za-z0-9])"
)
POSIX_PATH_RE = re.compile(
    r"(?<![\w])/(?:Users|home|private|tmp|var|etc|opt|Volumes)/[^\s<>'\"]+"
)
GENERIC_ABSOLUTE_PATH_RE = re.compile(
    r"(?:~/(?:[^\s<>\"']+)|(?<![:\w])/(?:[^/\s<>\"']+/)+[^\s<>\"']*)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:\\|\\\\)[^\r\n<>\"']+")
FILE_PATH_RE = re.compile(
    r"(?<![\w.-])(?:\.\.?/)?(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,12}(?![\w.-])"
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", re.I)
IP_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.I,
)
FILE_NAME_RE = re.compile(
    r"\b[\w.-]+\.(?:bib|csv|docx?|eml|html?|ipynb|jpe?g|jsonl?|md|pdf|png|pptx?|py|"
    r"qmd|r|sh|tex|tsv|tsx?|xml|ya?ml|zip)\b",
    re.I,
)
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")
TOKEN_RE = re.compile(
    r"\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|hf_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,})\b"
)
CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:api[_ -]?key|access[_ -]?token|auth[_ -]?token|password|passwd|secret)\b"
    r"\s*[:=]\s*['\"]?[A-Za-z0-9_./+\-=]{8,}"
)
ACTIVE_MARKUP_RE = re.compile(
    r"(?is)<\s*/?\s*(?:script|iframe|frame|object|embed|img|svg|math|link|meta|base|form|style)\b"
    r"|\bon[a-z]{3,}\s*=|\b(?:javascript|data\s*:\s*text/html)\s*:|\bsrcdoc\s*="
)
HTML_TAG_RE = re.compile(r"<[^>]{1,500}>")
NETWORK_CODE_RE = re.compile(
    r"\b(?:fetch\s*\(|XMLHttpRequest|WebSocket\s*\(|sendBeacon\s*\()", re.I
)
EXPLICIT_NAME_RE = re.compile(r"(?i)\b(?:Brett(?:\s+Reynolds)?|Reynolds|Humber)\b")
HONORIFIC_NAME_RE = re.compile(
    r"\b(?:Dr|Prof|Professor|Mr|Mrs|Ms|Mx)\.?\s+[A-Z][A-Za-z'’-]{2,}\b"
)
VOCATIVE_NAME_RE = re.compile(r"\b(?i:dear|hello|hi)\s+[A-Z][a-z'’-]{2,}\b")
MULTIWORD_PROPER_NAME_RE = re.compile(
    r"\b[A-Z][a-z'’-]{2,}\s+(?:[A-Z][a-z'’-]{1,}\s+)?[A-Z][a-z'’-]{2,}\b"
)
ORGANIZATION_RE = re.compile(
    r"\b[A-Z][A-Za-z&'’-]*(?:\s+[A-Z][A-Za-z&'’-]*){0,4}\s+"
    r"(?:University|College|Institute|Corporation|Corp|Company|Ltd|LLC|Department|Ministry)\b"
)
STREET_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[A-Z][A-Za-z0-9'’.-]*(?:\s+[A-Z][A-Za-z0-9'’.-]*){0,4}\s+"
    r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)\.?\b"
)
POSTAL_CODE_RE = re.compile(r"(?i)\b[A-Z]\d[A-Z][ -]?\d[A-Z]\d\b")
EXACT_DATE_RE = re.compile(r"\b(?:19|20)\d{2}[-/]\d{2}[-/]\d{2}\b")
LONG_IDENTIFIER_RE = re.compile(r"\b(?:[a-fA-F0-9]{32,}|[A-Za-z0-9_-]{48,})\b")
CORRESPONDENCE_RE = re.compile(r"(?im)^(?:from|to|cc|bcc|subject|sent):\s*\S")
CODE_FENCE_RE = re.compile(r"```|~~~")
WITHHELD_PLACEHOLDER_RE = re.compile(r"^\[FIELD_WITHHELD:[A-Z0-9_]+\]$")
TOOL_TEXT_RE = re.compile(
    r"(?im)^(?:chunk id|process exited with code|wall time|command output|original_token_count):"
    r"|<\/?(?:tool_result|tool_call|function_call)\b"
    r"|script running with cell id|\"(?:cmd|command|tool_trace|tool_output|stdout|stderr)\"\s*:"
)

FORBIDDEN_NESTED_KEYS = {
    "raw_path",
    "session_id",
    "source_ref",
    "trigger_turn_index",
    "feedback_turn_index",
    "trigger_node_id",
    "feedback_node_id",
    "start_line",
    "end_line",
    "project_ref",
    "project_hash",
    "software_version",
    "branch",
    "permission_mode",
    "prompt_provenance",
    "tool_trace",
    "tool_output",
    "tool_arguments",
    "stdout",
    "stderr",
    "thinking",
    "signature",
    "encrypted_content",
    "replacement_history",
}

ALLOWED_WITHHELD_FIELDS = DIRECT_REVIEW_TEXT_FIELDS | {
    "preceding_context",
    "preceding_context.user",
    "preceding_context.assistant",
    "governing_context",
    "compaction_summary",
    "tool_trace.text",
    "prompt_provenance",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", required=True, type=Path)
    parser.add_argument(
        "--restricted-dir",
        required=True,
        type=Path,
        help="separate owner-only v2 source-linkage vault",
    )
    return parser.parse_args()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def nested_keys(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from nested_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_keys(child)


def nested_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from nested_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_strings(child)


def read_json_object(path: Path, errors: list[str], label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"{label} is unreadable or invalid JSON ({type(exc).__name__})")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object")
        return {}
    return value


def read_jsonl(path: Path, errors: list[str], label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    errors.append(f"{label} row {line_number} is invalid JSON")
                    continue
                if not isinstance(value, dict):
                    errors.append(f"{label} row {line_number} is not an object")
                    continue
                rows.append(value)
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{label} is unreadable ({type(exc).__name__})")
    return rows


def read_csv_rows(
    path: Path, expected_fields: list[str], errors: list[str], label: str
) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected_fields:
                errors.append(f"{label} headers do not match the v2 schema")
                return []
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"{label} is unreadable or invalid CSV ({type(exc).__name__})")
        return []
    if any(None in row for row in rows):
        errors.append(f"{label} contains a row with extra columns")
    return rows


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def strict_jsonl_object_count(path: Path) -> int:
    """Read a source file as strict UTF-8 JSONL without retaining its values."""

    count = 0
    with path.open(encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON at source line {line_number}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"non-object JSON at source line {line_number}")
            count += 1
    return count


def keyed_ref(key: bytes, prefix: str, domain: str, value: str, length: int) -> str:
    digest = hmac.new(key, f"{domain}\0{value}".encode("utf-8"), hashlib.sha256)
    return f"{prefix}-{digest.hexdigest()[:length].upper()}"


def check_no_symlink_path(raw_path: Path, label: str, errors: list[str]) -> None:
    absolute = Path(os.path.abspath(raw_path))
    if not is_relative_to(absolute, ROOT):
        return
    current = ROOT
    for part in absolute.relative_to(ROOT).parts:
        current /= part
        try:
            if current.is_symlink():
                errors.append(f"{label} path traverses a symlink")
                return
        except OSError:
            return


def iter_tree(root: Path) -> Iterator[Path]:
    yield root
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directory_names:
            yield current_path / name
        for name in file_names:
            yield current_path / name


def check_tree_safety(root: Path, label: str, errors: list[str]) -> list[Path]:
    regular_files: list[Path] = []
    if not root.is_dir():
        errors.append(f"{label} is missing or is not a directory")
        return regular_files
    for path in iter_tree(root):
        try:
            info = path.lstat()
        except OSError:
            errors.append(f"{label} contains an unreadable entry")
            continue
        relative = "." if path == root else path.relative_to(root).as_posix()
        if stat.S_ISLNK(info.st_mode):
            errors.append(f"{label} contains a symlink: {relative}")
        elif stat.S_ISDIR(info.st_mode):
            mode = stat.S_IMODE(info.st_mode)
            if mode != 0o700:
                errors.append(f"{label} directory mode must be 0700: {relative} is {mode:04o}")
        elif stat.S_ISREG(info.st_mode):
            regular_files.append(path)
            mode = stat.S_IMODE(info.st_mode)
            if mode != 0o600:
                errors.append(f"{label} file mode must be 0600: {relative} is {mode:04o}")
        else:
            errors.append(f"{label} contains a non-regular filesystem entry: {relative}")
    return regular_files


def git_ignored(path: Path) -> bool:
    completed = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", str(path)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return completed.returncode == 0


def check_private_placement(
    raw_corpus: Path,
    raw_restricted: Path,
    corpus_dir: Path,
    restricted_dir: Path,
    errors: list[str],
) -> None:
    check_no_symlink_path(raw_corpus, "corpus directory", errors)
    check_no_symlink_path(raw_restricted, "restricted directory", errors)
    if not is_relative_to(corpus_dir, DISCOVERY_ROOT):
        errors.append("corpus directory must resolve under repository private/discovery/")
    if not is_relative_to(restricted_dir, RESTRICTED_ROOT):
        errors.append("restricted directory must resolve under repository private/restricted/")
    if (
        corpus_dir == restricted_dir
        or is_relative_to(corpus_dir, restricted_dir)
        or is_relative_to(restricted_dir, corpus_dir)
    ):
        errors.append("corpus and restricted directories must be disjoint")
    for path, label in ((corpus_dir, "corpus directory"), (restricted_dir, "restricted directory")):
        if path.exists() and not git_ignored(path):
            errors.append(f"{label} is not Git-ignored")


def check_every_file_ignored(
    paths: Iterable[Path], root: Path, label: str, errors: list[str]
) -> None:
    for path in paths:
        if not git_ignored(path):
            relative = path.relative_to(root).as_posix()
            errors.append(f"{label} contains a non-ignored file: {relative}")


def signal_score(
    value: Any,
    label: str,
    errors: list[str],
    canonical_weights: dict[str, int],
) -> int | None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return None
    total = 0
    seen: set[str] = set()
    for position, row in enumerate(value, start=1):
        if not isinstance(row, dict) or set(row) != {"signal", "weight"}:
            errors.append(f"{label} signal {position} has the wrong schema")
            continue
        signal = row.get("signal")
        weight = row.get("weight")
        if not isinstance(signal, str) or signal not in canonical_weights:
            errors.append(f"{label} signal {position} is outside the fixed vocabulary")
        elif signal in seen:
            errors.append(f"{label} repeats a signal")
        else:
            seen.add(signal)
        if (
            isinstance(weight, bool)
            or not isinstance(weight, int)
            or not isinstance(signal, str)
            or canonical_weights.get(signal) != weight
        ):
            errors.append(f"{label} signal {position} has a noncanonical weight")
        else:
            total += weight
    return total


def list_of_canonical_strings(
    value: Any,
    label: str,
    errors: list[str],
    allowed: set[str],
    maximum: int = 64,
) -> None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    if len(value) > maximum:
        errors.append(f"{label} exceeds its item cap")
    if len(value) != len(set(item for item in value if isinstance(item, str))):
        errors.append(f"{label} contains duplicates")
    for item in value:
        if not isinstance(item, str) or item not in allowed:
            errors.append(f"{label} contains a non-canonical value")
            break


def privacy_hits(text: str, *, proper_names: bool = True, tool_text: bool = False) -> list[str]:
    rules: list[tuple[str, re.Pattern[str]]] = [
        ("email", EMAIL_RE),
        ("HTTP URL", HTTP_URL_RE),
        ("www URL", WWW_RE),
        ("user handle", HANDLE_RE),
        ("phone number", PHONE_RE),
        ("POSIX path", POSIX_PATH_RE),
        ("absolute path", GENERIC_ABSOLUTE_PATH_RE),
        ("Windows path", WINDOWS_PATH_RE),
        ("file path", FILE_PATH_RE),
        ("file name", FILE_NAME_RE),
        ("IP address", IP_RE),
        ("UUID", UUID_RE),
        ("private-key marker", PRIVATE_KEY_RE),
        ("JWT-like credential", JWT_RE),
        ("credential token", TOKEN_RE),
        ("credential assignment", CREDENTIAL_ASSIGNMENT_RE),
        ("active markup", ACTIVE_MARKUP_RE),
        ("HTML tag", HTML_TAG_RE),
        ("network-capable code", NETWORK_CODE_RE),
        ("street address", STREET_ADDRESS_RE),
        ("postal code", POSTAL_CODE_RE),
        ("exact date", EXACT_DATE_RE),
        ("long identifier", LONG_IDENTIFIER_RE),
        ("correspondence header", CORRESPONDENCE_RE),
        ("code fence", CODE_FENCE_RE),
    ]
    if proper_names:
        rules.extend(
            [
                ("explicit forbidden name", EXPLICIT_NAME_RE),
                ("honorific/name", HONORIFIC_NAME_RE),
                ("vocative/name", VOCATIVE_NAME_RE),
                ("multiword proper name", MULTIWORD_PROPER_NAME_RE),
                ("organization name", ORGANIZATION_RE),
            ]
        )
    if tool_text:
        rules.append(("raw tool text", TOOL_TEXT_RE))
    return [label for label, pattern in rules if pattern.search(text)]


def validate_candidate_row(
    row: dict[str, Any], row_number: int, errors: list[str]
) -> tuple[str | None, str | None]:
    label = f"candidate-index row {row_number}"
    if set(row) != CANDIDATE_FIELDS:
        missing = sorted(CANDIDATE_FIELDS - set(row))
        extra = sorted(set(row) - CANDIDATE_FIELDS)
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} has prohibited fields: {', '.join(extra)}")
        return None, None
    candidate_id = row["candidate_id"]
    session_ref = row["session_ref"]
    if not isinstance(candidate_id, str) or not CANDIDATE_ID_RE.fullmatch(candidate_id):
        errors.append(f"{label} has an invalid keyed candidate ID")
        candidate_id = None
    if not isinstance(session_ref, str) or not SESSION_REF_RE.fullmatch(session_ref):
        errors.append(f"{label} has an invalid keyed session reference")
        session_ref = None
    source = row["source"]
    mode = row["session_mode"]
    if source not in SOURCES:
        errors.append(f"{label} has an invalid source class")
    elif (source == "codex" and mode != "cli") or (
        source == "claude" and mode != "interactive"
    ):
        errors.append(f"{label} admits a noninteractive source mode")
    if not isinstance(row["month"], str) or not MONTH_RE.fullmatch(row["month"]):
        errors.append(f"{label} has an invalid coarsened month")
    else:
        try:
            date.fromisoformat(f"{row['month']}-01")
        except ValueError:
            errors.append(f"{label} has an impossible coarsened month")
    if not isinstance(row["candidate_class"], str) or row["candidate_class"] not in CLASSES:
        errors.append(f"{label} has an invalid candidate class")
    if (
        isinstance(row["candidate_score"], bool)
        or not isinstance(row["candidate_score"], int)
        or row["candidate_score"] < 0
    ):
        errors.append(f"{label} has an invalid candidate score")
    if row["evidence_strength"] not in {"low", "moderate", "high"}:
        errors.append(f"{label} has an invalid evidence strength")
    if (
        not isinstance(row["primary_phenomenon"], str)
        or row["primary_phenomenon"] not in CANONICAL_PRIMARY_PHENOMENA
    ):
        errors.append(f"{label} has an invalid primary phenomenon")
    evidence_vocabulary = (
        FAILURE_EVIDENCE_SIGNAL_WEIGHTS
        if row["candidate_class"] == "likely_pragmatic_failure"
        else SUCCESS_EVIDENCE_SIGNAL_WEIGHTS
    )
    evidence = signal_score(
        row["evidence_signals"],
        f"{label} evidence_signals",
        errors,
        evidence_vocabulary,
    )
    load = signal_score(
        row["pragmatic_load_signals"],
        f"{label} pragmatic_load_signals",
        errors,
        PRAGMATIC_LOAD_SIGNAL_WEIGHTS,
    )
    if evidence is not None and load is not None and isinstance(row["candidate_score"], int):
        expected = evidence
        if row["candidate_class"] == "surprising_success_candidate":
            expected += load
            if evidence < 2 or load < 2:
                errors.append(f"{label} success evidence/load is below retrieval thresholds")
        elif evidence < 3:
            errors.append(f"{label} failure evidence is below the retrieval threshold")
        if row["candidate_score"] != expected:
            errors.append(f"{label} has a score inconsistent with its signal weights")
    alternatives = row["alternative_explanations"]
    if (
        not isinstance(alternatives, list)
        or alternatives != sorted(set(item for item in alternatives if isinstance(item, str)))
        or any(item not in CANONICAL_ALTERNATIVE_EXPLANATIONS for item in alternatives)
    ):
        errors.append(
            f"{label} alternative_explanations must use the fixed canonical vocabulary"
        )
    if not isinstance(row["compaction_before"], bool):
        errors.append(f"{label} compaction_before must be boolean")
    if (
        isinstance(row["tool_event_count"], bool)
        or not isinstance(row["tool_event_count"], int)
        or not 0 <= row["tool_event_count"] <= 100_000
    ):
        errors.append(f"{label} has an invalid tool-event count")
    list_of_canonical_strings(
        row["tool_action_classes"],
        f"{label} tool_action_classes",
        errors,
        CANONICAL_TOOL_ACTION_CLASSES,
    )
    withheld = row["content_withheld_fields"]
    if not isinstance(withheld, list) or len(withheld) > len(ALLOWED_WITHHELD_FIELDS):
        errors.append(f"{label} content_withheld_fields must be a bounded list")
    elif len(withheld) != len(set(item for item in withheld if isinstance(item, str))):
        errors.append(f"{label} content_withheld_fields contains duplicates")
    elif any(item not in ALLOWED_WITHHELD_FIELDS for item in withheld):
        errors.append(f"{label} content_withheld_fields names a prohibited field")
    counts = row["redaction_counts"]
    if not isinstance(counts, dict) or any(
        not isinstance(key, str)
        or key not in CANONICAL_REDACTION_COUNT_KEYS
        or isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        for key, value in (counts.items() if isinstance(counts, dict) else [])
    ):
        errors.append(f"{label} has invalid redaction counts")
    if row["privacy_disposition"] != PRIVACY_DISPOSITION:
        errors.append(f"{label} is not marked internal_review_only")
    if row["reconstruction_status"] not in RECONSTRUCTION_STATUSES:
        errors.append(f"{label} has an invalid reconstruction status")
    if not isinstance(row["review_selected"], bool):
        errors.append(f"{label} review_selected must be boolean")
    forbidden = FORBIDDEN_NESTED_KEYS & set(nested_keys(row))
    if forbidden:
        errors.append(f"{label} contains forbidden provenance/tool keys")
    for text in nested_strings(row):
        hits = privacy_hits(text, proper_names=False)
        if hits:
            errors.append(f"{label} metadata contains prohibited private syntax: {hits[0]}")
            break
    return candidate_id, session_ref


def review_text_parts(row: dict[str, Any], label: str, errors: list[str]) -> list[str]:
    parts: list[str] = []
    for field in sorted(DIRECT_REVIEW_TEXT_FIELDS):
        value = row.get(field)
        if not isinstance(value, str):
            errors.append(f"{label} {field} must be a string")
            continue
        if len(value) > MAX_TEXT_FIELD_CHARS:
            errors.append(f"{label} {field} exceeds the {MAX_TEXT_FIELD_CHARS}-character cap")
        parts.append(value)
    context = row.get("preceding_context")
    if not isinstance(context, list):
        errors.append(f"{label} preceding_context must be a list")
    elif len(context) > MAX_PRECEDING_TURNS:
        errors.append(f"{label} has more than two preceding turns")
    else:
        for position, turn in enumerate(context, start=1):
            if not isinstance(turn, dict) or set(turn) != {"user", "assistant"}:
                errors.append(f"{label} preceding turn {position} has the wrong schema")
                continue
            for role in ("user", "assistant"):
                text = turn.get(role)
                if not isinstance(text, str):
                    errors.append(f"{label} preceding turn {position} {role} must be a string")
                    continue
                if len(text) > MAX_PRECEDING_TURN_CHARS:
                    errors.append(
                        f"{label} preceding turn {position} {role} exceeds the "
                        f"{MAX_PRECEDING_TURN_CHARS}-character cap"
                    )
                parts.append(text)
    return parts


def validate_review_row(
    row: dict[str, Any],
    row_number: int,
    candidates_by_id: dict[str, dict[str, Any]],
    errors: list[str],
) -> str | None:
    label = f"review-corpus row {row_number}"
    if set(row) != REVIEW_FIELDS:
        missing = sorted(REVIEW_FIELDS - set(row))
        extra = sorted(set(row) - REVIEW_FIELDS)
        if missing:
            errors.append(f"{label} is missing fields: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} has prohibited fields: {', '.join(extra)}")
        return None
    candidate_id = row["candidate_id"]
    if not isinstance(candidate_id, str) or not CANDIDATE_ID_RE.fullmatch(candidate_id):
        errors.append(f"{label} has an invalid keyed candidate ID")
        return None
    candidate = candidates_by_id.get(candidate_id)
    if candidate is None:
        errors.append(f"{label} has no candidate-index row")
    else:
        for field in CANDIDATE_FIELDS - {"review_selected"}:
            if row[field] != candidate[field]:
                errors.append(f"{label} disagrees with candidate-index field {field}")
        if candidate.get("review_selected") is not True:
            errors.append(f"{label} candidate is not marked review_selected")
    parts = review_text_parts(row, label, errors)
    actual_count = sum(len(text) for text in parts)
    count = row["text_char_count"]
    if isinstance(count, bool) or not isinstance(count, int):
        errors.append(f"{label} text_char_count must be an integer")
    elif count != actual_count:
        errors.append(f"{label} text_char_count does not equal retained text")
    if actual_count > MAX_EPISODE_TEXT_CHARS:
        errors.append(f"{label} exceeds the {MAX_EPISODE_TEXT_CHARS}-character episode cap")
    withheld = row["content_withheld_fields"]
    if isinstance(withheld, list):
        if any(field not in ALLOWED_WITHHELD_FIELDS for field in withheld):
            errors.append(f"{label} names an invalid withheld-content field")
        for field in withheld:
            if field in DIRECT_REVIEW_TEXT_FIELDS:
                value = row.get(field)
                if not (
                    value == ""
                    or value is None
                    or (isinstance(value, str) and WITHHELD_PLACEHOLDER_RE.fullmatch(value))
                ):
                    errors.append(f"{label} retains content for withheld field {field}")
            elif field == "preceding_context" and row.get(field) != []:
                errors.append(f"{label} retains content for withheld field {field}")
            elif field in {"preceding_context.user", "preceding_context.assistant"}:
                role = field.rsplit(".", 1)[1]
                for turn in row.get("preceding_context", []):
                    value = turn.get(role) if isinstance(turn, dict) else None
                    if not (
                        value == ""
                        or value is None
                        or (
                            isinstance(value, str)
                            and WITHHELD_PLACEHOLDER_RE.fullmatch(value)
                        )
                    ):
                        errors.append(f"{label} retains content for withheld field {field}")
                        break
    forbidden = FORBIDDEN_NESTED_KEYS & set(nested_keys(row))
    if forbidden:
        errors.append(f"{label} contains forbidden provenance/tool keys")
    for text in parts:
        hits = privacy_hits(text, proper_names=True, tool_text=True)
        if hits:
            errors.append(f"{label} retains prohibited content: {hits[0]}")
            break
    return candidate_id


class ReviewerHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str | None]]] = []
        self.meta_csp: list[str] = []
        self.scripts: list[dict[str, Any]] = []
        self.styles: list[dict[str, Any]] = []
        self.data_elements: list[dict[str, Any]] = []
        self._script_depth = 0
        self._style_depth = 0
        self._data_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.append((tag.lower(), attributes))
        if tag.lower() == "meta" and str(attributes.get("http-equiv", "")).lower() == (
            "content-security-policy"
        ):
            self.meta_csp.append(attributes.get("content") or "")
        if tag.lower() == "script":
            self.scripts.append({"attrs": attributes, "text": ""})
            self._script_depth += 1
        if tag.lower() == "style":
            self.styles.append({"attrs": attributes, "text": ""})
            self._style_depth += 1
        if attributes.get("id") == "candidate-data":
            self.data_elements.append({"tag": tag.lower(), "attrs": attributes, "text": ""})
            self._data_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._script_depth:
            self._script_depth -= 1
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1
        if tag.lower() == "template" and self._data_depth:
            self._data_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._script_depth and self.scripts:
            self.scripts[-1]["text"] += data
        if self._style_depth and self.styles:
            self.styles[-1]["text"] += data
        if self._data_depth and self.data_elements:
            self.data_elements[-1]["text"] += data


def parse_csp(value: str) -> dict[str, list[str]]:
    directives: dict[str, list[str]] = {}
    for segment in value.split(";"):
        tokens = segment.strip().split()
        if not tokens:
            continue
        directive = tokens[0].lower()
        if directive in directives:
            directives[directive].extend(tokens[1:])
        else:
            directives[directive] = tokens[1:]
    return directives


def validate_reviewer(path: Path, review: list[dict[str, Any]], errors: list[str]) -> None:
    try:
        html = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"reviewer HTML is unreadable ({type(exc).__name__})")
        return
    parser = ReviewerHTMLParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as exc:  # HTMLParser failures must fail closed.
        errors.append(f"reviewer HTML cannot be parsed ({type(exc).__name__})")
        return
    if len(parser.meta_csp) != 1:
        errors.append("reviewer must contain exactly one CSP meta element")
        directives: dict[str, list[str]] = {}
    else:
        directives = parse_csp(parser.meta_csp[0])
    denied = {
        "default-src",
        "connect-src",
        "img-src",
        "media-src",
        "font-src",
        "object-src",
        "frame-src",
        "child-src",
        "form-action",
        "base-uri",
        "worker-src",
        "manifest-src",
    }
    for directive in sorted(denied):
        if directives.get(directive) != ["'none'"]:
            errors.append(f"reviewer CSP must set {directive} 'none'")
    if len(parser.scripts) != 1:
        errors.append("reviewer must contain exactly one script element")
        script: dict[str, Any] = {"attrs": {}, "text": ""}
    else:
        script = parser.scripts[0]
    script_attrs = script["attrs"]
    nonce = script_attrs.get("nonce")
    if set(script_attrs) != {"nonce"} or not isinstance(nonce, str) or not re.fullmatch(
        r"[A-Za-z0-9+/_-]{16,128}={0,2}", nonce
    ):
        errors.append("reviewer script must have exactly one nontrivial nonce attribute")
    expected_script_source = [f"'nonce-{nonce}'"] if isinstance(nonce, str) else []
    if directives.get("script-src") != expected_script_source:
        errors.append("reviewer CSP script-src must authorize only its one inline nonce")
    if len(parser.styles) != 1:
        errors.append("reviewer must contain exactly one style element")
        style_element: dict[str, Any] = {"attrs": {}, "text": ""}
    else:
        style_element = parser.styles[0]
    style_attrs = style_element["attrs"]
    style_nonce = style_attrs.get("nonce")
    if set(style_attrs) != {"nonce"} or not isinstance(style_nonce, str) or not re.fullmatch(
        r"[A-Za-z0-9+/_-]{16,128}={0,2}", style_nonce
    ):
        errors.append("reviewer style must have exactly one nontrivial nonce attribute")
    expected_style_source = [f"'nonce-{style_nonce}'"] if isinstance(style_nonce, str) else []
    if directives.get("style-src") != expected_style_source:
        errors.append("reviewer CSP style-src must authorize only its one inline nonce")
    if nonce and style_nonce and nonce == style_nonce:
        errors.append("reviewer script and style must use distinct nonces")
    if re.search(
        r"(?i)url\s*\(|@import|\bhttps?://|\bdata\s*:|image-set\s*\(|-moz-binding|behavior\s*:",
        str(style_element.get("text") or ""),
    ):
        errors.append("reviewer style contains a URL-capable construct")
    resource_attributes = {
        "src",
        "srcset",
        "href",
        "action",
        "formaction",
        "poster",
        "data",
        "ping",
        "xlink:href",
    }
    prohibited_static_tags = {
        "base",
        "iframe",
        "frame",
        "object",
        "embed",
        "link",
        "img",
        "audio",
        "video",
        "source",
        "track",
        "form",
    }
    for tag, attrs in parser.tags:
        if tag in prohibited_static_tags:
            errors.append(f"reviewer contains prohibited static <{tag}> content")
        if any(key.lower().startswith("on") for key in attrs):
            errors.append(f"reviewer contains an inline event-handler attribute on <{tag}>")
        if resource_attributes & set(attrs):
            errors.append(f"reviewer contains a resource/navigation attribute on <{tag}>")
        style = attrs.get("style")
        if isinstance(style, str) and re.search(r"(?i)url\s*\(|@import", style):
            errors.append(f"reviewer contains a URL-capable style attribute on <{tag}>")
        if (
            tag == "meta"
            and "http-equiv" in attrs
            and str(attrs.get("http-equiv", "")).lower() != "content-security-policy"
        ):
            errors.append("reviewer contains a prohibited non-CSP http-equiv meta element")
    script_text = str(script.get("text") or "")
    forbidden_script = [
        r"\bfetch\s*\(",
        r"\bXMLHttpRequest\b",
        r"\bWebSocket\b",
        r"\bEventSource\b",
        r"\bsendBeacon\b",
        r"\blocalStorage\b",
        r"\bsessionStorage\b",
        r"\bindexedDB\b",
        r"\bserviceWorker\b",
        r"\bcaches\s*\.",
        r"\bdocument\s*\.\s*cookie\b",
        r"\bwindow\s*\.\s*open\b",
        r"\blocation\s*(?:=|\.|\[)",
        r"\bpostMessage\b",
        r"\beval\s*\(",
        r"\bnew\s+Function\b",
        r"\bimport\s*\(",
        r"\b(?:innerHTML|outerHTML|insertAdjacentHTML|document\s*\.\s*write)\b",
        r"(?i)\bhttps?://|\bwss?://",
    ]
    for pattern in forbidden_script:
        if re.search(pattern, script_text):
            errors.append("reviewer script contains a forbidden network/persistence/eval primitive")
            break
    if len(parser.data_elements) != 1:
        errors.append("reviewer must contain exactly one inert #candidate-data element")
        return
    data_element = parser.data_elements[0]
    if data_element["tag"] != "template":
        errors.append("reviewer #candidate-data element must be a template")
    attrs = data_element["attrs"]
    if set(attrs) != {"id", "data-encoding"} or attrs.get("data-encoding") != "base64":
        errors.append(
            "reviewer #candidate-data must have only id and data-encoding=base64 attributes"
        )
    payload = re.sub(r"\s+", "", str(data_element["text"]))
    if not payload or not re.fullmatch(r"[A-Za-z0-9+/]*={0,2}", payload):
        errors.append("reviewer data is not inert canonical base64")
        return
    try:
        decoded_bytes = base64.b64decode(payload, validate=True)
        decoded_text = decoded_bytes.decode("utf-8")
        decoded = json.loads(decoded_text)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        errors.append("reviewer base64 payload is not valid UTF-8 JSON")
        return
    if decoded != review:
        errors.append("reviewer base64 rows do not exactly match review-corpus.jsonl")


def validate_aggregate_report(
    path: Path,
    label: str,
    review_texts: set[str],
    errors: list[str],
) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{label} is unreadable ({type(exc).__name__})")
        return
    aggregate_rules = [
        ("email", EMAIL_RE),
        ("HTTP URL", HTTP_URL_RE),
        ("www URL", WWW_RE),
        ("user handle", HANDLE_RE),
        ("phone number", PHONE_RE),
        ("POSIX path", POSIX_PATH_RE),
        ("absolute path", GENERIC_ABSOLUTE_PATH_RE),
        ("Windows path", WINDOWS_PATH_RE),
        ("IP address", IP_RE),
        ("private-key marker", PRIVATE_KEY_RE),
        ("JWT-like credential", JWT_RE),
        ("credential token", TOKEN_RE),
        ("credential assignment", CREDENTIAL_ASSIGNMENT_RE),
        ("active markup", ACTIVE_MARKUP_RE),
        ("explicit forbidden name", EXPLICIT_NAME_RE),
        ("street address", STREET_ADDRESS_RE),
        ("postal code", POSTAL_CODE_RE),
    ]
    hits = [name for name, pattern in aggregate_rules if pattern.search(text)]
    if hits:
        errors.append(f"{label} contains direct-identifier/private syntax: {hits[0]}")
    if ROW_ID_IN_TEXT_RE.search(text):
        errors.append(f"{label} contains row-level pseudonyms instead of aggregates")
    for value in review_texts:
        if len(value) >= 32 and value in text:
            errors.append(f"{label} reproduces a retained candidate text value")
            break


def validate_readme(
    path: Path,
    relative: str,
    review_texts: set[str],
    errors: list[str],
) -> None:
    label = "corpus README" if relative == "README.md" else "reviewer README"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{label} is unreadable ({type(exc).__name__})")
        return
    if len(text) > 4_096 or "\x00" in text:
        errors.append(f"{label} is not a bounded plain-text notice")
    heading, separator, body = text.partition("\n")
    if heading != README_HEADINGS[relative] or not separator:
        errors.append(f"{label} heading is not the fixed v2 heading")
    hits = [
        hit
        for hit in privacy_hits(body, proper_names=True, tool_text=True)
        if hit != "file name"
    ]
    if hits:
        errors.append(f"{label} contains prohibited private/narrative syntax: {hits[0]}")
    lowered = body.lower()
    required_boundaries = (
        ("pseudonym", "not anonym", "public-safe")
        if relative == "README.md"
        else ("in memory", "not anonym", "private")
    )
    if any(fragment not in lowered for fragment in required_boundaries):
        errors.append(f"{label} omits a required privacy boundary")
    validate_aggregate_report(path, label, review_texts, errors)


OPTIONAL_PII_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email", EMAIL_RE),
    ("HTTP URL", HTTP_URL_RE),
    ("www URL", WWW_RE),
    ("user handle", HANDLE_RE),
    ("phone number", PHONE_RE),
    ("POSIX path", POSIX_PATH_RE),
    ("absolute path", GENERIC_ABSOLUTE_PATH_RE),
    ("Windows path", WINDOWS_PATH_RE),
    ("private-key marker", PRIVATE_KEY_RE),
    ("credential token", TOKEN_RE),
    ("credential assignment", CREDENTIAL_ASSIGNMENT_RE),
    ("active markup", ACTIVE_MARKUP_RE),
    ("HTML tag", HTML_TAG_RE),
    ("network-capable code", NETWORK_CODE_RE),
    ("explicit forbidden name", EXPLICIT_NAME_RE),
    ("honorific/name", HONORIFIC_NAME_RE),
    ("vocative/name", VOCATIVE_NAME_RE),
    ("multiword proper name", MULTIWORD_PROPER_NAME_RE),
    ("organization name", ORGANIZATION_RE),
    ("street address", STREET_ADDRESS_RE),
    ("postal code", POSTAL_CODE_RE),
    ("correspondence header", CORRESPONDENCE_RE),
)
ISO_TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$"
)
ISO_DATE_ONLY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CANONICAL_AUDIT_TOKEN_RE = re.compile(r"^[a-z0-9_.:+\[\]-]{1,200}$")
OPAQUE_AUDIT_REF_RE = re.compile(r"^[A-F0-9]{7}$")
CANONICAL_AUDIT_KEY_RE = re.compile(r"^[a-z0-9_.\[\]-]{1,160}$")
CANONICAL_AUDIT_STRING_VOCABULARY = {
    "active_html_element",
    "aggregate_counts_only",
    "aggregate_naturalistic_corpus_privacy_audit",
    "aggregate_overlapping_counts",
    "all_candidates",
    "aws_access_identifier",
    "beacon_call",
    "bearer_credential",
    "canadian_postal_code",
    "contextual_reidentification_risk_remains",
    "corpus",
    "corpus_manifest",
    "corpus_profile",
    "corpus_readme",
    "credential_assignment",
    "csv",
    "email_address",
    "event_handler_attribute",
    "event_source_call",
    "external_use_requires_new_controlled_reconstruction",
    "github_token",
    "google_api_key",
    "hugging_face_token",
    "html",
    "html_data_scheme",
    "internal_only",
    "ipv4_address",
    "javascript_scheme",
    "json",
    "jsonl",
    "jwt",
    "meta_refresh",
    "naturalistic_corpus_contextual_privacy_audit",
    "network_fetch_call",
    "no_excerpt_or_matched_value_retained",
    "no_sampled_direct_identifier",
    "no_sampled_authentication_material_identified",
    "no_sampled_third_party_pii",
    "normalized_events",
    "openai_or_anthropic_token",
    "other_absolute_path",
    "other_csv",
    "other_file",
    "other_html",
    "other_json",
    "other_jsonl",
    "other_restricted_file",
    "other_text",
    "phone_number",
    "posix_home_path",
    "private_key_material",
    "probable_multiword_name",
    "probable_street_address",
    "provenance_index",
    "regular_file",
    "restricted",
    "retrieval_audit",
    "review_corpus",
    "reviewer_html",
    "reviewer_readme",
    "script_tag",
    "sha256_seed_domain_nul_candidate_pseudonym_within_source_and_class_stratum",
    "slack_token",
    "source_fingerprints",
    "source_linkage",
    "symlink_directory",
    "text",
    "url",
    "v1_raw_derivative",
    "websocket_call",
    "windows_user_path",
    "worker_import",
    "xml_http_request",
}


def validate_canonical_audit_value(
    value: Any,
    label: str,
    errors: list[str],
    path: tuple[str, ...] = (),
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            normalized_key = key_text.replace("_", " ").replace("-", " ")
            if (
                not CANONICAL_AUDIT_KEY_RE.fullmatch(key_text)
                or any(pattern.search(normalized_key) for _name, pattern in OPTIONAL_PII_RULES)
            ):
                errors.append(f"{label} contains a noncanonical or private JSON key")
                return
            validate_canonical_audit_value(child, label, errors, path + (key_text,))
        return
    if isinstance(value, list):
        for child in value:
            validate_canonical_audit_value(child, label, errors, path + ("[]",))
        return
    if not isinstance(value, str):
        return
    hit = next((name for name, pattern in OPTIONAL_PII_RULES if pattern.search(value)), None)
    if hit:
        errors.append(f"{label} contains prohibited private syntax: {hit}")
        return
    if not value:
        return
    if path[-2:] == ("audit_policy", "file_reference_scheme"):
        if value != "root-class plus deterministic ordinal":
            errors.append(f"{label} has a noncanonical file-reference policy")
        return
    if path and path[-1] in {"generated_at", "finalized_at"}:
        if not ISO_TIMESTAMP_RE.fullmatch(value):
            errors.append(f"{label} has a noncanonical timestamp")
        return
    if path and path[-1] == "audit_date":
        try:
            parsed_audit_date = date.fromisoformat(value)
        except ValueError:
            parsed_audit_date = None
        if not ISO_DATE_ONLY_RE.fullmatch(value) or parsed_audit_date is None:
            errors.append(f"{label} has a noncanonical audit date")
        return
    if path[-2:] == ("sampling_method", "seed_domain"):
        if value != "privacy-context-v2":
            errors.append(f"{label} has a noncanonical sampling seed domain")
        return
    if OPAQUE_AUDIT_REF_RE.fullmatch(value):
        return
    if SHA256_RE.fullmatch(value) or value.isdigit():
        return
    if (
        not CANONICAL_AUDIT_TOKEN_RE.fullmatch(value)
        or value not in CANONICAL_AUDIT_STRING_VOCABULARY
    ):
        errors.append(f"{label} contains an arbitrary narrative string")


def validate_optional_audit(
    path: Path,
    relative: str,
    expected_kind: str,
    review_texts: set[str],
    errors: list[str],
) -> None:
    label = f"optional aggregate audit {relative.rsplit('/', 1)[-1]}"
    value = read_json_object(path, errors, label)
    if value.get("kind") != expected_kind:
        errors.append(f"{label} kind is wrong")
    if value.get("schema_version") != 1:
        errors.append(f"{label} schema_version must equal 1")
    expected_fields = (
        CONTEXTUAL_AUDIT_TOP_LEVEL_FIELDS
        if expected_kind == "naturalistic_corpus_contextual_privacy_audit"
        else AGGREGATE_AUDIT_TOP_LEVEL_FIELDS
    )
    if set(value) != expected_fields:
        errors.append(f"{label} top-level schema is not the fixed aggregate schema")
    validate_canonical_audit_value(value, label, errors)
    validate_aggregate_report(path, label, review_texts, errors)


def integer_string(value: str) -> int | None:
    if not re.fullmatch(r"\d+", value or ""):
        return None
    return int(value)


def validate_restricted_vault(
    restricted_dir: Path,
    candidates_by_id: dict[str, dict[str, Any]],
    corpus_files: list[Path],
    errors: list[str],
) -> None:
    key_path = restricted_dir / "id-key.bin"
    linkage_path = restricted_dir / "source-linkage.csv"
    fingerprint_path = restricted_dir / "source-fingerprints.csv"
    for path in (key_path, linkage_path, fingerprint_path):
        if not path.is_file():
            errors.append(f"restricted vault is missing {path.name}")
    if not all(path.is_file() for path in (key_path, linkage_path, fingerprint_path)):
        return
    try:
        key = key_path.read_bytes()
    except OSError:
        errors.append("restricted id key is unreadable")
        key = b""
    if len(key) != 32 or key == b"\x00" * 32:
        errors.append("restricted id-key.bin must contain exactly 32 nonzero random bytes")
    linkage = read_csv_rows(linkage_path, LINKAGE_FIELDS, errors, "source-linkage.csv")
    fingerprints = read_csv_rows(
        fingerprint_path, FINGERPRINT_FIELDS, errors, "source-fingerprints.csv"
    )
    candidate_ids = [row.get("candidate_id", "") for row in linkage]
    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("source-linkage.csv contains duplicate candidate IDs")
    if set(candidate_ids) != set(candidates_by_id):
        errors.append("source-linkage.csv is not one-to-one with candidate-index.jsonl")
    source_refs = [row.get("source_ref", "") for row in fingerprints]
    if len(source_refs) != len(set(source_refs)):
        errors.append("source-fingerprints.csv contains duplicate source references")
    fingerprints_by_ref = {row.get("source_ref", ""): row for row in fingerprints}
    linkage_source_refs = {row.get("source_ref", "") for row in linkage}
    if linkage_source_refs != set(fingerprints_by_ref):
        errors.append("restricted source-reference coverage is inconsistent")
    sensitive_values: set[bytes] = set()
    for row_number, row in enumerate(linkage, start=1):
        label = f"source-linkage.csv row {row_number}"
        candidate = candidates_by_id.get(row.get("candidate_id", ""))
        if candidate is not None:
            for field in ("session_ref", "source"):
                if row.get(field) != candidate.get(field):
                    errors.append(f"{label} disagrees with candidate index field {field}")
        if not SOURCE_REF_RE.fullmatch(row.get("source_ref", "")):
            errors.append(f"{label} has an invalid keyed source reference")
        raw_path = Path(row.get("raw_path", ""))
        if not raw_path.is_absolute() or not raw_path.is_file():
            errors.append(f"{label} does not identify an existing absolute source file")
        if not row.get("session_id"):
            errors.append(f"{label} lacks a raw session identifier")
        elif candidate is not None and row.get("source") in SOURCES:
            session_value = f"{row['source']}|{row['session_id']}"
            expected_session_ref = keyed_ref(key, "SES2", "session", session_value, 20)
            identity = "|".join(
                [
                    session_value,
                    row.get("trigger_node_id", ""),
                    row.get("feedback_node_id", ""),
                    str(candidate.get("candidate_class", "")),
                ]
            )
            expected_candidate_id = keyed_ref(key, "NPE2", "candidate", identity, 24)
            expected_source_ref = keyed_ref(
                key,
                "SRC2",
                "source",
                f"{row['source']}|{row.get('raw_path', '')}",
                20,
            )
            if row.get("session_ref") != expected_session_ref:
                errors.append(f"{label} keyed session reference does not reproduce")
            if row.get("candidate_id") != expected_candidate_id:
                errors.append(f"{label} keyed candidate ID does not reproduce")
            if row.get("source_ref") != expected_source_ref:
                errors.append(f"{label} keyed source reference does not reproduce")
        for field in ("trigger_turn_index", "feedback_turn_index"):
            if integer_string(row.get(field, "")) is None:
                errors.append(f"{label} has an invalid {field}")
        for field in ("start_line", "end_line"):
            value = row.get(field, "")
            if value and integer_string(value) is None:
                errors.append(f"{label} has an invalid {field}")
        start = integer_string(row.get("start_line", ""))
        end = integer_string(row.get("end_line", ""))
        if start is not None and end is not None and start > end:
            errors.append(f"{label} has reversed line bounds")
        for field in (
            "source_ref",
            "raw_path",
            "session_id",
            "trigger_node_id",
            "feedback_node_id",
        ):
            value = row.get(field, "")
            if len(value.encode("utf-8")) >= 8:
                sensitive_values.add(value.encode("utf-8"))
    for row_number, row in enumerate(fingerprints, start=1):
        label = f"source-fingerprints.csv row {row_number}"
        if not SOURCE_REF_RE.fullmatch(row.get("source_ref", "")):
            errors.append(f"{label} has an invalid keyed source reference")
        if row.get("source") not in SOURCES:
            errors.append(f"{label} has an invalid source class")
        raw_path = Path(row.get("raw_path", ""))
        digest = row.get("source_sha256", "")
        size = integer_string(row.get("byte_size", ""))
        if not raw_path.is_absolute() or not raw_path.is_file():
            errors.append(f"{label} does not identify an existing absolute source file")
            continue
        expected_source_ref = keyed_ref(
            key,
            "SRC2",
            "source",
            f"{row.get('source', '')}|{row.get('raw_path', '')}",
            20,
        )
        if row.get("source_ref") != expected_source_ref:
            errors.append(f"{label} keyed source reference does not reproduce")
        if not SHA256_RE.fullmatch(digest):
            errors.append(f"{label} has an invalid SHA-256 fingerprint")
        else:
            try:
                if file_sha256(raw_path) != digest.lower():
                    errors.append(f"{label} source SHA-256 is stale")
                else:
                    strict_jsonl_object_count(raw_path)
                    if file_sha256(raw_path) != digest.lower():
                        errors.append(f"{label} source changed during strict JSONL validation")
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                errors.append(f"{label} is not strict UTF-8 object-only JSONL")
            except OSError:
                errors.append(f"{label} source file cannot be hashed or parsed")
        try:
            actual_size = raw_path.stat().st_size
        except OSError:
            actual_size = None
        if size is None or size != actual_size:
            errors.append(f"{label} byte size is stale or invalid")
        for value in (row.get("source_ref", ""), row.get("raw_path", ""), digest):
            if len(value.encode("utf-8")) >= 8:
                sensitive_values.add(value.encode("utf-8"))
    for corpus_path in corpus_files:
        try:
            data = corpus_path.read_bytes()
        except OSError:
            continue
        if any(value in data for value in sensitive_values):
            errors.append(
                "privacy-minimized corpus contains a restricted linkage/fingerprint value: "
                f"{corpus_path.relative_to(corpus_path.parents[2]).as_posix()}"
            )
            break


def validate_no_duplicate_files(
    corpus_files: list[Path], restricted_files: list[Path], errors: list[str]
) -> None:
    by_hash: dict[str, list[Path]] = defaultdict(list)
    by_inode: dict[tuple[int, int], list[Path]] = defaultdict(list)
    for path in corpus_files + restricted_files:
        try:
            by_hash[file_sha256(path)].append(path)
            info = path.stat()
            by_inode[(info.st_dev, info.st_ino)].append(path)
        except OSError:
            errors.append("a derivative file could not be hashed")
    duplicate_hashes = [paths for paths in by_hash.values() if len(paths) > 1]
    if duplicate_hashes:
        errors.append(
            f"derivative trees contain {len(duplicate_hashes)} byte-identical file group(s)"
        )
    hardlinks = [paths for paths in by_inode.values() if len(paths) > 1]
    if hardlinks:
        errors.append(f"derivative trees contain {len(hardlinks)} hard-linked file group(s)")


def inventory_records(root: Path, *, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative in excluded or path.is_symlink() or not path.is_file():
            continue
        info = path.stat()
        records.append(
            {
                "relative_path": relative,
                "sha256": file_sha256(path),
                "byte_size": info.st_size,
                "mode": f"{stat.S_IMODE(info.st_mode):04o}",
            }
        )
    return records


def validate_finalized_privatization_audit(
    audit: dict[str, Any],
    residual_audit: dict[str, Any],
    corpus_dir: Path,
    restricted_dir: Path,
    candidates: list[dict[str, Any]],
    review: list[dict[str, Any]],
    errors: list[str],
) -> None:
    after = audit.get("after")
    if not isinstance(after, dict):
        return
    if after.get("reviewer_finalized") is not True:
        errors.append("privatization audit does not attest a finalized reviewer")
    expected_corpus_inventory = inventory_records(
        corpus_dir, exclude={"reports/privatization-audit.json"}
    )
    if after.get("corpus_file_inventory") != expected_corpus_inventory:
        errors.append("privatization audit corpus inventory/hash/mode/size is stale")
    expected_restricted_inventory = inventory_records(restricted_dir)
    if after.get("restricted_file_inventory") != expected_restricted_inventory:
        errors.append("privatization audit restricted inventory/hash/mode/size is stale")
    if after.get("duplicate_groups") != []:
        errors.append("privatization audit does not report zero duplicate derivative groups")
    if after.get("residual_identifier_counts") != residual_audit.get(
        "residual_identifier_counts"
    ):
        errors.append("privatization and residual-risk audits disagree")
    aggregate_scan = after.get("aggregate_privacy_scan")
    if not isinstance(aggregate_scan, dict) or aggregate_scan.get("kind") != (
        "aggregate_naturalistic_corpus_privacy_audit"
    ):
        errors.append("privatization audit lacks the finalized aggregate privacy scan")
    else:
        policy = aggregate_scan.get("audit_policy")
        if not isinstance(policy, dict) or any(
            policy.get(field) is not expected
            for field, expected in {
                "input_paths_or_unrecognized_filenames_in_report": False,
                "matched_values_or_excerpts_in_report": False,
                "symlinks_followed": False,
            }.items()
        ):
            errors.append("aggregate privacy scan has an unsafe disclosure/traversal policy")
        findings = aggregate_scan.get("aggregate_findings")
        if not isinstance(findings, dict):
            errors.append("aggregate privacy scan lacks aggregate findings")
        else:
            for category in (
                "high_confidence_secrets",
                "active_markup_network_primitives",
            ):
                values = findings.get(category)
                if (
                    not isinstance(values, dict)
                    or values.get("match_count") != 0
                    or values.get("affected_value_count") != 0
                ):
                    errors.append(f"aggregate privacy scan reports unsafe {category}")
        scan_inventory = aggregate_scan.get("inventory")
        expected_regular_files = len(expected_corpus_inventory) + len(
            expected_restricted_inventory
        )
        if not isinstance(scan_inventory, dict) or any(
            scan_inventory.get(field) != expected
            for field, expected in {
                "regular_file_count": expected_regular_files,
                "owner_only_file_count": expected_regular_files,
                "non_owner_only_file_count": 0,
                "wrong_owner_file_count": 0,
                "symlink_count": 0,
                "restricted_key_file_count": 1,
                "restricted_32_byte_key_file_count": 1,
            }.items()
        ):
            errors.append("aggregate privacy scan inventory/security counts are inconsistent")
        duplication = aggregate_scan.get("duplication")
        if not isinstance(duplication, dict) or any(
            duplication.get(field) != 0
            for field in ("byte_identical_group_count", "hardlink_group_count")
        ):
            errors.append("aggregate privacy scan reports duplicate or hard-linked files")
        renderer = aggregate_scan.get("renderer_structural_totals")
        expected_renderer = {
            "candidate_data_template_count": 1,
            "csp_authorized_script_count": 1,
            "csp_meta_count": 1,
            "decoded_payload_count": 1,
            "decoded_record_count": len(review),
            "encoded_payload_count": 1,
            "event_handler_attribute_count": 0,
            "external_resource_attribute_count": 0,
            "payload_decode_error_count": 0,
            "script_closing_sequence_count": 1,
            "script_element_count": 1,
            "script_nonce_attribute_count": 1,
            "style_element_count": 1,
            "style_nonce_attribute_count": 1,
        }
        if not isinstance(renderer, dict) or any(
            renderer.get(field) != expected
            for field, expected in expected_renderer.items()
        ):
            errors.append("aggregate privacy scan renderer counts are inconsistent")
    transformations = audit.get("transformations")
    if not isinstance(transformations, dict):
        errors.append("privatization audit lacks aggregate transformation counts")
        return
    expected_transformations = {
        "keyed_hmac_candidate_ids": len(candidates),
        "keyed_hmac_session_ids": len({row.get("session_ref") for row in candidates}),
        "raw_episode_derivatives_retained": 0,
        "direct_provenance_rows_moved_to_restricted_vault": len(candidates),
        "manual_controlled_reconstruction_rows": sum(
            row.get("reconstruction_status")
            == "manual_controlled_reconstruction_required"
            for row in review
        ),
    }
    for field, expected in expected_transformations.items():
        if transformations.get(field) != expected:
            errors.append(f"privatization audit transformation count is stale: {field}")


def main() -> None:
    args = parse_args()
    raw_corpus = args.corpus_dir.expanduser()
    raw_restricted = args.restricted_dir.expanduser()
    corpus_dir = raw_corpus.resolve(strict=False)
    restricted_dir = raw_restricted.resolve(strict=False)
    errors: list[str] = []

    check_private_placement(
        raw_corpus, raw_restricted, corpus_dir, restricted_dir, errors
    )
    for relative in sorted(REQUIRED_CORPUS_FILES):
        if not (corpus_dir / relative).is_file():
            errors.append(f"missing required v2 corpus file: {relative}")
    for name in sorted(RESTRICTED_FILES):
        if not (restricted_dir / name).is_file():
            errors.append(f"missing required restricted-vault file: {name}")

    corpus_files = check_tree_safety(corpus_dir, "corpus tree", errors)
    restricted_files = check_tree_safety(restricted_dir, "restricted tree", errors)
    check_every_file_ignored(corpus_files, corpus_dir, "corpus tree", errors)
    check_every_file_ignored(restricted_files, restricted_dir, "restricted tree", errors)

    actual_corpus_files = {
        path.relative_to(corpus_dir).as_posix() for path in corpus_files
    }
    unexpected_corpus_files = actual_corpus_files - ALLOWED_CORPUS_FILES
    if unexpected_corpus_files:
        errors.append(
            f"corpus tree contains {len(unexpected_corpus_files)} unexpected file(s)"
        )
    actual_restricted_files = {
        path.relative_to(restricted_dir).as_posix() for path in restricted_files
    }
    unexpected_restricted_files = actual_restricted_files - RESTRICTED_FILES
    if unexpected_restricted_files:
        errors.append(
            f"restricted tree contains {len(unexpected_restricted_files)} unexpected file(s)"
        )

    # Do not try to parse partial state: placement, permissions, and required-file
    # errors are reported first, with no sensitive values echoed.
    if any(not (corpus_dir / relative).is_file() for relative in REQUIRED_CORPUS_FILES):
        finish(errors)

    manifest = read_json_object(
        corpus_dir / "corpus-manifest.json", errors, "corpus manifest"
    )
    retrieval_audit = read_json_object(
        corpus_dir / "reports" / "retrieval-audit.json", errors, "retrieval audit"
    )
    privatization_audit = read_json_object(
        corpus_dir / "reports" / "privatization-audit.json", errors, "privatization audit"
    )
    residual_audit = read_json_object(
        corpus_dir / "reports" / "residual-risk-audit.json", errors, "residual-risk audit"
    )
    candidates = read_jsonl(
        corpus_dir / "candidate-index.jsonl", errors, "candidate index"
    )
    review = read_jsonl(corpus_dir / "review-corpus.jsonl", errors, "review corpus")

    expected_manifest = {
        "schema_version": 2,
        "kind": "privacy_minimized_naturalistic_pragmatic_extremes_corpus",
        "privacy_model_version": 1,
        "restricted_linkage_separate": True,
    }
    for field, expected in expected_manifest.items():
        if manifest.get(field) != expected:
            errors.append(f"manifest {field} must equal {expected!r}")
    for field in ("session_count", "candidate_count", "review_corpus_count"):
        if isinstance(manifest.get(field), bool) or not isinstance(manifest.get(field), int):
            errors.append(f"manifest {field} must be an integer")
    if retrieval_audit.get("external_api_calls") is not False:
        errors.append("retrieval audit must affirm zero external API calls")
    if retrieval_audit.get("parse_errors") not in ([], 0):
        errors.append("retrieval audit contains parse errors")
    if privatization_audit.get("kind") != "naturalistic_corpus_privatization_audit":
        errors.append("privatization audit kind is wrong")
    if not isinstance(privatization_audit.get("before"), dict) or not isinstance(
        privatization_audit.get("after"), dict
    ):
        errors.append("privatization audit must contain aggregate before and after objects")
    if residual_audit.get("kind") != "naturalistic_corpus_residual_risk_audit":
        errors.append("residual-risk audit kind is wrong")
    residual_counts = residual_audit.get("residual_identifier_counts")
    if not isinstance(residual_counts, dict) or not residual_counts:
        errors.append("residual-risk audit must contain residual_identifier_counts")
    else:
        missing_residual_categories = EXPECTED_RESIDUAL_CATEGORIES - set(residual_counts)
        if missing_residual_categories:
            errors.append("residual-risk audit omits required identifier categories")
        for name, value in residual_counts.items():
            if not isinstance(name, str) or not isinstance(value, dict):
                errors.append("residual-risk audit has an invalid residual-count entry")
                break
            if set(value) != {"matches", "records", "fields"}:
                errors.append("residual-risk audit residual-count schema is wrong")
                break
            fields = value.get("fields")
            if (
                isinstance(value.get("matches"), bool)
                or not isinstance(value.get("matches"), int)
                or value.get("matches") != 0
                or isinstance(value.get("records"), bool)
                or not isinstance(value.get("records"), int)
                or value.get("records") != 0
                or not isinstance(fields, dict)
                or any(
                    isinstance(count, bool) or not isinstance(count, int) or count != 0
                    for count in (fields.values() if isinstance(fields, dict) else [])
                )
            ):
                errors.append("residual-risk audit reports nonzero or invalid residual identifiers")
                break

    candidates_by_id: dict[str, dict[str, Any]] = {}
    session_refs: set[str] = set()
    for row_number, row in enumerate(candidates, start=1):
        candidate_id, session_ref = validate_candidate_row(row, row_number, errors)
        if candidate_id is not None:
            if candidate_id in candidates_by_id:
                errors.append("candidate index contains duplicate candidate IDs")
            candidates_by_id[candidate_id] = row
        if session_ref is not None:
            session_refs.add(session_ref)
    review_ids: list[str] = []
    review_texts: set[str] = set()
    for row_number, row in enumerate(review, start=1):
        candidate_id = validate_review_row(row, row_number, candidates_by_id, errors)
        if candidate_id is not None:
            review_ids.append(candidate_id)
        for field in DIRECT_REVIEW_TEXT_FIELDS:
            value = row.get(field)
            if isinstance(value, str) and value:
                review_texts.add(value)
        preceding = row.get("preceding_context", [])
        for turn in preceding if isinstance(preceding, list) else []:
            if not isinstance(turn, dict):
                continue
            for role in ("user", "assistant"):
                value = turn.get(role)
                if isinstance(value, str) and value:
                    review_texts.add(value)
    if len(review_ids) != len(set(review_ids)):
        errors.append("review corpus contains duplicate candidate IDs")
    selected_ids = {
        candidate_id
        for candidate_id, row in candidates_by_id.items()
        if row.get("review_selected") is True
    }
    if set(review_ids) != selected_ids:
        errors.append("review corpus does not exactly match review_selected candidate rows")
    if manifest.get("session_count") != len(session_refs):
        errors.append("manifest session_count is inconsistent")
    if manifest.get("candidate_count") != len(candidates):
        errors.append("manifest candidate_count is inconsistent")
    if manifest.get("review_corpus_count") != len(review):
        errors.append("manifest review_corpus_count is inconsistent")

    for relative in README_HEADINGS:
        validate_readme(corpus_dir / relative, relative, review_texts, errors)
    for relative, expected_kind in OPTIONAL_AUDIT_KINDS.items():
        path = corpus_dir / relative
        if path.is_file():
            validate_optional_audit(
                path, relative, expected_kind, review_texts, errors
            )
    before = privatization_audit.get("before")
    embedded_contextual = (
        before.get("contextual_privacy_audit") if isinstance(before, dict) else None
    )
    if embedded_contextual is not None:
        validate_canonical_audit_value(
            embedded_contextual,
            "embedded legacy contextual privacy audit",
            errors,
        )

    validate_finalized_privatization_audit(
        privatization_audit,
        residual_audit,
        corpus_dir,
        restricted_dir,
        candidates,
        review,
        errors,
    )

    aggregate_paths = [
        (corpus_dir / "corpus-manifest.json", "corpus manifest"),
        (corpus_dir / "reports" / "retrieval-audit.json", "retrieval audit"),
        (corpus_dir / "reports" / "corpus-profile.md", "corpus profile"),
        (corpus_dir / "reports" / "privatization-audit.json", "privatization audit"),
        (corpus_dir / "reports" / "residual-risk-audit.json", "residual-risk audit"),
    ]
    for path, label in aggregate_paths:
        validate_aggregate_report(path, label, review_texts, errors)
    validate_reviewer(corpus_dir / "review" / "index.html", review, errors)
    validate_restricted_vault(restricted_dir, candidates_by_id, corpus_files, errors)

    corpus_linkage_names = {
        "source-linkage.csv",
        "source-fingerprints.csv",
        "id-key.bin",
        "source-index.jsonl",
        "provenance-index.csv",
        "all-candidates.jsonl",
        "candidate-episodes.jsonl",
    }
    leaked_names = [path.name for path in corpus_files if path.name in corpus_linkage_names]
    if leaked_names:
        errors.append("corpus tree retains a raw/provenance derivative")
    validate_no_duplicate_files(corpus_files, restricted_files, errors)
    finish(errors, sessions=len(session_refs), candidates=len(candidates), review=len(review))


def finish(
    errors: list[str], *, sessions: int = 0, candidates: int = 0, review: int = 0
) -> None:
    if errors:
        for error in errors[:150]:
            print(f"ERROR: {error}")
        if len(errors) > 150:
            print(f"ERROR: {len(errors) - 150} further errors suppressed")
        raise SystemExit(1)
    print(
        f"ok: v2 privacy-minimized corpus; {sessions} keyed sessions, "
        f"{candidates} candidate-index rows, {review} review rows; placement, minimization, "
        "restricted linkage, residual risk, rendering, duplication, and permissions verify"
    )


if __name__ == "__main__":
    main()
