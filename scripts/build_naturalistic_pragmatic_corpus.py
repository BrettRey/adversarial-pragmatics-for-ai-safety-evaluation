#!/usr/bin/env python3
"""Build a privacy-minimized corpus of pragmatic-extremes candidates.

The source adapters read local Codex and Claude Code JSONL records without
calling an external service. Candidate labels are deterministic retrieval
classes, not adjudicated outcomes or prevalence estimates. The corpus contains
keyed pseudonyms and minimized excerpts; direct provenance is written to a
separate restricted directory. No raw episode derivative is retained.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import hmac
import json
import os
import re
import shutil
import stat
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, TypeVar
from zoneinfo import ZoneInfo


ADAPTER_VERSION = 1
PRIVACY_MODEL_VERSION = 1
DEFAULT_START = date(2026, 1, 1)
DEFAULT_END = date(2026, 7, 15)
TORONTO = ZoneInfo("America/Toronto")
T = TypeVar("T")
REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = (REPO_ROOT / "private").resolve()
DISCOVERY_ROOT = PRIVATE_ROOT / "discovery"
RESTRICTED_ROOT = PRIVATE_ROOT / "restricted"
REVIEW_FIELD_LIMIT = 1600
PRECEDING_FIELD_LIMIT = 900
EPISODE_TEXT_LIMIT = 7000


FAILURE_PATTERNS: list[tuple[str, int, re.Pattern[str]]] = [
    (
        "explicit_not_requested",
        5,
        re.compile(
            r"\b(?:that(?:\s+is|'s|\s+was)\s+not\s+what\s+i\s+asked|"
            r"not\s+what\s+i\s+(?:asked|meant)|i\s+(?:didn'?t|did\s+not)\s+ask)\b",
            re.I,
        ),
    ),
    (
        "explicit_misunderstanding",
        4,
        re.compile(
            r"\b(?:you\s+(?:misunderstood|misread|misinterpreted)|you\s+missed\s+(?:the|my)|"
            r"that(?:'s|\s+is)\s+not\s+the\s+(?:point|request|question))\b",
            re.I,
        ),
    ),
    (
        "scope_or_file_correction",
        4,
        re.compile(
            r"\b(?:wrong\s+(?:file|folder|project|scope|document)|"
            r"re-?add(?:ed|ing)?|reintroduc(?:e|ed|ing)|"
            r"why\s+did\s+you\s+(?:edit|change|modify|add|remove))\b",
            re.I,
        ),
    ),
    (
        "reasserted_negative_constraint",
        2,
        re.compile(
            r"^\s*(?:no[,!. ]+)?(?:do\s+not|don'?t)\s+"
            r"(?:edit|change|modify|touch|add|remove|send|publish|push|commit|open)\b",
            re.I,
        ),
    ),
    (
        "instruction_repetition",
        3,
        re.compile(
            r"\b(?:i\s+(?:said|told\s+you|asked\s+you)\b|as\s+i\s+(?:said|asked)|"
            r"i\s+already\s+(?:said|asked|told)|again[, :]\s*(?:do|don'?t|the|you))",
            re.I,
        ),
    ),
    (
        "stop_or_revert",
        4,
        re.compile(
            r"^\s*(?:no[,!. ]+)?(?:stop|undo|revert|roll\s+back|back\s+that\s+out|"
            r"restore\s+the\s+(?:file|previous|original))\b",
            re.I,
        ),
    ),
    (
        "completion_or_status_challenge",
        3,
        re.compile(
            r"\b(?:you\s+(?:haven'?t|have\s+not|didn'?t|did\s+not)\s+(?:finish|complete|"
            r"provide|include|do|fix|answer)|that(?:'s|\s+is)\s+not\s+(?:done|fixed|complete)|"
            r"you\s+(?:said|claimed)\s+(?:you|it)\s+(?:did|was)|still\s+(?:not|missing|wrong))\b",
            re.I,
        ),
    ),
    (
        "action_answer_mismatch",
        4,
        re.compile(
            r"\b(?:i\s+asked\s+(?:for|you\s+to)\s+(?:review|diagnos|explain|answer)|"
            r"instead\s+of\s+(?:editing|changing|implementing|explaining|answering)|"
            r"asked\s+you\s+to\s+(?:review|diagnose|explain).{0,60}(?:not|without)\s+(?:edit|chang))",
            re.I,
        ),
    ),
    (
        "strong_negative_assessment",
        2,
        re.compile(
            r"\b(?:this\s+(?:makes\s+no\s+sense|is\s+wrong|is\s+incorrect)|"
            r"you\s+(?:ignored|failed\s+to\s+follow)|fuck\s+off)\b",
            re.I,
        ),
    ),
]


UPTAKE_PATTERNS: list[tuple[str, int, re.Pattern[str]]] = [
    (
        "explicit_exactness",
        4,
        re.compile(
            r"^\s*(?:yes[,!. ]+)?(?:exactly|that(?:'s|\s+is)\s+(?:right|it)|"
            r"you\s+(?:got|nailed)\s+it)\b",
            re.I,
        ),
    ),
    (
        "explicit_catch",
        4,
        re.compile(
            r"\b(?:nice\s+catch|good\s+catch|you\s+caught\s+(?:it|that|a\s+real)|"
            r"caught\s+a\s+real\s+(?:bug|problem|defect))\b",
            re.I,
        ),
    ),
    (
        "strong_positive_assessment",
        3,
        re.compile(
            r"^\s*(?:yes[,!. ]+)?(?:perfect|excellent|brilliant|impressive|well\s+done|"
            r"much\s+better|beautiful|great\s+work)\b",
            re.I,
        ),
    ),
    (
        "explicit_worked",
        3,
        re.compile(
            r"\b(?:that\s+worked|it\s+worked|works\s+now|that\s+fixed\s+it|"
            r"looks\s+(?:good|right|correct)\s+now)\b",
            re.I,
        ),
    ),
]


LOAD_PATTERNS: list[tuple[str, int, re.Pattern[str]]] = [
    (
        "negative_constraint",
        2,
        re.compile(
            r"\b(?:do\s+not|don'?t|without\s+(?:editing|changing|adding|removing|touching)|"
            r"only\s+(?:review|diagnose|explain|answer|change|edit|use|include))\b",
            re.I,
        ),
    ),
    (
        "scope_boundary",
        2,
        re.compile(
            r"\b(?:only\s+(?:this|that|the)|just\s+(?:this|that|the)|"
            r"nothing\s+else|leave\s+.+\s+unchanged|keep\s+.+\s+fixed|"
            r"review\s+only|diagnos(?:e|is)\s+only|no\s+(?:edits|changes))\b",
            re.I,
        ),
    ),
    (
        "reference_or_ellipsis",
        1,
        re.compile(
            r"\b(?:this|that|it|these|those|the\s+other|the\s+previous|the\s+one\s+above|"
            r"the\s+last\s+one|same\s+(?:thing|file|plan)|continue|resume)\b",
            re.I,
        ),
    ),
    (
        "authority_or_permission",
        2,
        re.compile(
            r"\b(?:permission|authori[sz](?:e|ed|ation)|approval|without\s+asking|"
            r"ask\s+me\s+(?:before|first)|do\s+not\s+(?:send|publish|push|commit|open)|"
            r"don'?t\s+(?:send|publish|push|commit|open))\b",
            re.I,
        ),
    ),
    (
        "task_type_boundary",
        2,
        re.compile(
            r"\b(?:review|diagnose|explain|answer|comment)\b.{0,80}\b(?:not|without|only)\b|"
            r"\b(?:not|without|only)\b.{0,80}\b(?:edit|implement|change|fix|act)\b",
            re.I,
        ),
    ),
    (
        "multi_stage_or_stop_condition",
        1,
        re.compile(
            r"\b(?:first|then|after\s+that|before\s+you|once\s+.+[, ]|until|"
            r"stop\s+(?:when|after)|wait\s+(?:until|for))\b",
            re.I,
        ),
    ),
]


DEPENDENT_CONTINUATION = re.compile(
    r"^\s*(?:(?:ok(?:ay)?|thanks|great|good)[,!. ]+)?"
    r"(?:now|next|then|proceed|ship|continue|resume|turning\s+back|let(?:'s|\s+us))\b",
    re.I,
)
EXPLICIT_ACKNOWLEDGMENT = re.compile(
    r"^\s*(?:ok(?:ay)?|thanks|thank\s+you|good|great|nice|yes|all\s+good)[.!]*\s*$",
    re.I,
)


PRIVACY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("email_like", re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")),
    (
        "phone_like",
        re.compile(r"\b(?:\+?\d{1,2}[ .-]?)?(?:\(?\d{3}\)?[ .-]?)\d{3}[ .-]\d{4}\b"),
    ),
    ("url", re.compile(r"https?://\S+", re.I)),
    (
        "credential_word",
        re.compile(r"\b(?:password|api[_ -]?key|access[_ -]?token|secret|credential)\b", re.I),
    ),
    ("local_path", re.compile(r"(?:/Users/|[A-Z]:\\|~/(?:Documents|Downloads|projects)/)")),
    ("private_key_marker", re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I)),
]
THIRD_PARTY_PATTERN = re.compile(
    r"\b(?:from:|to:|subject:|student|client|customer|colleague|employee|applicant|candidate)\b",
    re.I,
)


@dataclass
class ToolEvent:
    kind: str
    name: str
    text: str
    line_number: int
    success: bool | None = None


@dataclass
class Turn:
    user_text: str
    timestamp: str
    start_line: int
    node_id: str = ""
    model: str = ""
    cwd: str = ""
    version: str = ""
    git_branch: str = ""
    prompt_provenance: str = ""
    governing_context: list[str] = field(default_factory=list)
    compaction_before: bool = False
    compaction_summary: str = ""
    permission_mode: str = ""
    assistant_texts: list[str] = field(default_factory=list)
    tool_events: list[ToolEvent] = field(default_factory=list)
    infrastructure_error: bool = False
    end_line: int = 0

    def assistant_text(self, limit: int) -> str:
        return truncate("\n\n".join(text for text in self.assistant_texts if text), limit)

    def has_tool_success(self) -> bool:
        return any(event.success is True for event in self.tool_events)


@dataclass
class Session:
    source: str
    session_mode: str
    session_id: str
    timestamp: str
    local_date: str
    cwd: str
    version: str
    model: str
    distinct_cwds: list[str]
    distinct_versions: list[str]
    distinct_models: list[str]
    path: Path
    turns: list[Turn]
    event_count: int
    excluded_branch_records: int = 0


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def opaque(value: str, length: int = 20) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length].upper()


def hmac_ref(key: bytes, prefix: str, domain: str, value: str, length: int) -> str:
    digest = hmac.new(key, f"{domain}\0{value}".encode("utf-8"), hashlib.sha256)
    return f"{prefix}-{digest.hexdigest()[:length].upper()}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_state(path: Path) -> tuple[int, int]:
    info = path.stat()
    if not stat.S_ISREG(info.st_mode):
        raise OSError("source is not a regular file")
    return info.st_size, info.st_mtime_ns


def stable_source_fingerprint(path: Path) -> tuple[str, int]:
    before = source_state(path)
    digest = sha256_file(path)
    after = source_state(path)
    if before != after:
        raise RuntimeError("source changed while fingerprinting")
    return digest, after[0]


def reject_symlink_components(path: Path, label: str) -> None:
    """Reject existing symlinks from the repository root through ``path``."""

    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must be inside the repository private boundary") from exc
    current = REPO_ROOT
    for part in relative.parts:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise SystemExit(f"{label} contains an unreadable path component") from exc
        if stat.S_ISLNK(info.st_mode):
            raise SystemExit(f"{label} must not traverse a symlink")


def require_role_leaf(path: Path, parent: Path, label: str) -> Path:
    absolute = Path(os.path.abspath(path))
    reject_symlink_components(absolute, label)
    if absolute.parent != parent or not absolute.name.startswith(
        "naturalistic-pragmatic-extremes-"
    ):
        raise SystemExit(
            f"{label} must be a named direct child of {parent} with the "
            "naturalistic-pragmatic-extremes- prefix"
        )
    return absolute


def secure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode):
        raise SystemExit("private output path is not a regular directory")
    os.chmod(path, 0o700, follow_symlinks=False)


def assert_regular_tree(root: Path, label: str) -> None:
    """Fail before destructive or chmod operations if a tree has special entries."""

    if not root.exists():
        return
    for current, directory_names, file_names in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in [*directory_names, *file_names]:
            path = current_path / name
            info = path.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise SystemExit(f"{label} contains a symlink")
            if not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode)):
                raise SystemExit(f"{label} contains a non-regular filesystem entry")


def assert_owned_output_tree(path: Path) -> None:
    """Require the v2 corpus marker before recursively replacing an output tree."""

    assert_regular_tree(path, "existing corpus output")
    manifest_path = path / "corpus-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "refusing to overwrite an unmarked private directory; expected a readable "
            "v2 corpus manifest"
        ) from exc
    if not isinstance(manifest, dict) or manifest.get("kind") != (
        "privacy_minimized_naturalistic_pragmatic_extremes_corpus"
    ):
        raise SystemExit("refusing to overwrite a directory not marked as this v2 corpus")


def assert_restricted_tree_owned(path: Path) -> None:
    """Reject stale or unknown vault entries instead of deleting or chmodding them."""

    if not path.exists():
        return
    assert_regular_tree(path, "restricted vault")
    allowed = {"id-key.bin", "source-linkage.csv", "source-fingerprints.csv"}
    entries = {entry.name for entry in path.iterdir()}
    unknown = entries - allowed
    if unknown:
        raise SystemExit("restricted vault contains an unexpected entry; refusing overwrite")


def load_or_create_id_key(restricted_dir: Path) -> bytes:
    key_path = restricted_dir / "id-key.bin"
    if key_path.exists():
        info = key_path.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise SystemExit("restricted HMAC key is not a regular file")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(key_path, flags)
        try:
            key = os.read(descriptor, 33)
        finally:
            os.close(descriptor)
        if len(key) != 32:
            raise SystemExit(f"invalid HMAC key length: {key_path}")
    else:
        key = os.urandom(32)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(key_path, flags, 0o600)
        try:
            os.write(descriptor, key)
        finally:
            os.close(descriptor)
    os.chmod(key_path, 0o600, follow_symlinks=False)
    return key


EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]{1,64}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:\+?1[\s.()-]*)?(?:\(?\d{3}\)?[\s.-]*)\d{3}[\s.-]*\d{4}"
    r"(?![A-Za-z0-9])"
)
URL_RE = re.compile(r"(?:https?|file)://[^\s<>\"']+", re.I)
WWW_RE = re.compile(r"(?i)\bwww\.[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ABSOLUTE_PATH_RE = re.compile(
    r"(?:~/(?:[^\s<>\"']+)|[A-Za-z]:\\(?:[^\s<>\"']+)|"
    r"(?<![:\w])/(?:[^/\s<>\"']+/)+[^\s<>\"']*)"
)
WINDOWS_PATH_RE = re.compile(r"(?i)(?<![A-Za-z0-9])(?:[A-Z]:\\|\\\\)[^\r\n<>\"']+")
RELATIVE_FILE_PATH_RE = re.compile(
    r"(?<![\w.-])(?:\.\.?/)?(?:[A-Za-z0-9_.-]+/)+"
    r"[A-Za-z0-9_.-]+\.[A-Za-z0-9]{1,12}(?![\w.-])"
)
HANDLE_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9_][A-Za-z0-9_.-]{1,}")
IP_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
UUID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
    re.I,
)
LONG_IDENTIFIER_RE = re.compile(r"\b(?:[A-Fa-f0-9]{20,}|[A-Za-z0-9_-]{32,})\b")
EXACT_DATE_RE = re.compile(
    r"\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}(?:[T ][0-9:.+-Z]+)?\b"
)
FILE_NAME_RE = re.compile(
    r"\b[\w.-]+\.(?:bib|csv|docx?|eml|html?|ipynb|jpe?g|jsonl?|md|pdf|png|pptx?|py|"
    r"qmd|r|sh|tex|tsv|tsx?|xml|ya?ml|zip)\b",
    re.I,
)
POSTAL_RE = re.compile(
    r"\b[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z][ -]?\d[ABCEGHJ-NPRSTV-Z]\d\b",
    re.I,
)
STREET_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+(?:[A-Z][\w.-]*\s+){0,4}(?:Street|St\.?|Road|Rd\.?|Avenue|"
    r"Ave\.?|Boulevard|Blvd\.?|Drive|Dr\.?|Lane|Ln\.?|Court|Ct\.?|Way)\b",
    re.I,
)
CORRESPONDENCE_RE = re.compile(r"(?im)^\s*(?:from|to|cc|bcc|subject|sent):\s*\S+")
CREDENTIAL_RE = re.compile(
    r"\b(?:password|passwd|api[_ -]?key|access[_ -]?token|auth[_ -]?token|"
    r"private[_ -]?key|client[_ -]?secret|secret|credential)\b",
    re.I,
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", re.I)
ACTIVE_MARKUP_RE = re.compile(
    r"(?is)<\s*/?\s*(?:script|iframe|frame|object|embed|img|svg|math|link|meta|base|"
    r"form|style)\b|\bon[a-z]{3,}\s*=|\b(?:javascript|data\s*:\s*text/html)\s*:|"
    r"\bsrcdoc\s*="
)
NETWORK_CODE_RE = re.compile(
    r"\b(?:fetch\s*\(|XMLHttpRequest|WebSocket\s*\(|EventSource\s*\(|"
    r"sendBeacon\s*\(|importScripts\s*\()",
    re.I,
)
CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.M)
CODE_FENCE_RE = re.compile(r"```|~~~")
HTML_TAG_RE = re.compile(r"<[^>]{1,500}>")
HONORIFIC_NAME_RE = re.compile(
    r"\b(?:Dr|Prof|Professor|Mr|Mrs|Ms|Mx)\.?\s+[A-Z][A-Za-z'’-]+"
    r"(?:\s+[A-Z][A-Za-z'’-]+){0,2}\b"
)
GREETING_NAME_RE = re.compile(r"\b(Dear|Hi|Hello)\s+([A-Z][A-Za-z'’-]{2,})\b")
ORG_RE = re.compile(
    r"\b(?:[A-Z][A-Za-z&'’-]+\s+){1,5}(?:University|College|Polytechnic|Institute|"
    r"Association|Society|Corporation|Corp\.?|Company|Inc\.?|Ltd\.?|LLC|Press|Journal|"
    r"Department|Ministry)\b"
)
PROPER_NAME_RE = re.compile(
    r"\b[A-Z][a-z'’-]{2,}\s+(?:[A-Z][a-z'’-]{1,}\s+)?[A-Z][a-z'’-]{2,}\b"
)
ALL_CAPS_TOKEN_RE = re.compile(r"\b[A-Z]{2,12}\b")
CAMEL_TOKEN_RE = re.compile(r"\b(?:[a-z]+[A-Z][A-Za-z0-9]*|[A-Z][a-z]+[A-Z][A-Za-z0-9]*)\b")
POSSESSIVE_NAME_RE = re.compile(r"\b[A-Z][a-z]{2,}(?=['’]s\b)")
CONTEXTUAL_NAME_RE = re.compile(
    r"\b((?i:ask|tell|email|notify|contact|from|with|for|by|to))\s+([A-Z][a-z]{2,})\b"
)
CONTEXTUAL_ORG_RE = re.compile(
    r"\b([A-Z][A-Za-z&.-]{3,})\s+(employee|account|project|team|department|campus|policy)\b"
)
KNOWN_PRIVATE_CONTEXT_RE = re.compile(
    r"(?i)\b(?:Brett(?:\s+Reynolds)?|Reynolds|Humber)\b"
)
TOOL_TEXT_RE = re.compile(
    r"(?im)^(?:chunk id|process exited with code|wall time|command output|"
    r"original_token_count):|</?(?:tool_result|tool_call|function_call)\b|"
    r"script running with cell id|\"(?:cmd|command|tool_trace|tool_output|stdout|stderr)\"\s*:"
)


@dataclass
class SanitizedText:
    text: str
    redactions: Counter[str]
    withheld_reason: str = ""


class EpisodeSanitizer:
    def __init__(self, sensitive_literals: Iterable[str] = ()) -> None:
        self.mapping: dict[tuple[str, str], str] = {}
        self.counts: Counter[str] = Counter()
        self.sensitive_literals = sorted(
            {value for value in sensitive_literals if len(value) >= 4},
            key=len,
            reverse=True,
        )

    def placeholder(self, category: str, value: str) -> str:
        key = (category, value.casefold())
        if key not in self.mapping:
            number = 1 + sum(1 for existing in self.mapping if existing[0] == category)
            self.mapping[key] = f"[{category.upper()}_{number}]"
        self.counts[category] += 1
        return self.mapping[key]

    def substitute(self, pattern: re.Pattern[str], category: str, text: str) -> str:
        return pattern.sub(lambda match: self.placeholder(category, match.group(0)), text)

    def sanitize(self, value: str, limit: int) -> SanitizedText:
        text = value.strip()
        before = self.counts.copy()
        if not text:
            return SanitizedText("", Counter())
        if PRIVATE_KEY_RE.search(text) or CREDENTIAL_RE.search(text):
            self.counts["credential_context_withheld"] += 1
            return SanitizedText(
                "[FIELD_WITHHELD:SENSITIVE_ACCESS_CONTEXT]",
                self.counts - before,
                "credential_context",
            )
        if CORRESPONDENCE_RE.search(text):
            self.counts["correspondence_withheld"] += 1
            return SanitizedText("[FIELD_WITHHELD:CORRESPONDENCE]", self.counts - before, "correspondence")
        if ACTIVE_MARKUP_RE.search(text) or NETWORK_CODE_RE.search(text):
            self.counts["active_content_withheld"] += 1
            return SanitizedText("[FIELD_WITHHELD:ACTIVE_CONTENT]", self.counts - before, "active_content")
        if TOOL_TEXT_RE.search(text):
            self.counts["raw_tool_text_withheld"] += 1
            return SanitizedText(
                "[FIELD_WITHHELD:RAW_TOOL_TEXT]",
                self.counts - before,
                "raw_tool_text",
            )
        if len(text) > limit and text.count("\n") >= 12:
            self.counts["pasted_material_withheld"] += 1
            return SanitizedText("[FIELD_WITHHELD:PASTED_MATERIAL]", self.counts - before, "pasted_material")

        text = self.substitute(ALL_CAPS_TOKEN_RE, "acronym", text)
        text = self.substitute(CAMEL_TOKEN_RE, "proper_token", text)

        def code_replacement(match: re.Match[str]) -> str:
            return self.placeholder("code_block", match.group(0))

        text = CODE_BLOCK_RE.sub(code_replacement, text)
        for literal in self.sensitive_literals:
            text = re.sub(
                rf"(?<!\w){re.escape(literal)}(?!\w)",
                lambda match: self.placeholder("owner_identifier", match.group(0)),
                text,
                flags=re.I,
            )
        text = self.substitute(KNOWN_PRIVATE_CONTEXT_RE, "private_context", text)
        text = self.substitute(URL_RE, "url", text)
        text = self.substitute(WWW_RE, "url", text)
        text = self.substitute(EMAIL_RE, "email", text)
        text = self.substitute(WINDOWS_PATH_RE, "local_path", text)
        text = self.substitute(ABSOLUTE_PATH_RE, "local_path", text)
        text = self.substitute(RELATIVE_FILE_PATH_RE, "local_path", text)
        text = self.substitute(PHONE_RE, "phone", text)
        text = self.substitute(HANDLE_RE, "handle", text)
        text = self.substitute(IP_RE, "network_identifier", text)
        text = self.substitute(UUID_RE, "identifier", text)
        text = self.substitute(LONG_IDENTIFIER_RE, "identifier", text)
        text = self.substitute(EXACT_DATE_RE, "date", text)
        text = self.substitute(FILE_NAME_RE, "file_name", text)
        text = self.substitute(STREET_ADDRESS_RE, "address", text)
        text = self.substitute(POSTAL_RE, "postal_code", text)
        text = self.substitute(HONORIFIC_NAME_RE, "person", text)
        text = self.substitute(POSSESSIVE_NAME_RE, "person", text)
        text = GREETING_NAME_RE.sub(
            lambda match: f"{match.group(1)} {self.placeholder('person', match.group(2))}", text
        )
        text = CONTEXTUAL_NAME_RE.sub(
            lambda match: f"{match.group(1)} {self.placeholder('person', match.group(2))}", text
        )
        text = CONTEXTUAL_ORG_RE.sub(
            lambda match: f"{self.placeholder('organization', match.group(1))} {match.group(2)}",
            text,
        )
        text = self.substitute(ORG_RE, "organization", text)
        text = self.substitute(PROPER_NAME_RE, "proper_name", text)
        text = HTML_TAG_RE.sub(lambda match: self.placeholder("markup", match.group(0)), text)
        text = text.replace("<", "[LT]").replace(">", "[GT]")
        text = truncate(text, limit)
        # These checks intentionally mirror or exceed the independent validator's
        # retained-text policy. Any questionable remainder causes the entire field
        # to be omitted; it is never emitted as a visible placeholder.
        residual_patterns = (
            EMAIL_RE,
            URL_RE,
            WWW_RE,
            ABSOLUTE_PATH_RE,
            WINDOWS_PATH_RE,
            RELATIVE_FILE_PATH_RE,
            PHONE_RE,
            CREDENTIAL_RE,
            ACTIVE_MARKUP_RE,
            PRIVATE_KEY_RE,
            IP_RE,
            UUID_RE,
            LONG_IDENTIFIER_RE,
            FILE_NAME_RE,
            STREET_ADDRESS_RE,
            POSTAL_RE,
            EXACT_DATE_RE,
            CORRESPONDENCE_RE,
            CODE_FENCE_RE,
            KNOWN_PRIVATE_CONTEXT_RE,
            HONORIFIC_NAME_RE,
            GREETING_NAME_RE,
            PROPER_NAME_RE,
            ORG_RE,
            NETWORK_CODE_RE,
            TOOL_TEXT_RE,
        )
        if any(pattern.search(text) for pattern in residual_patterns):
            self.counts["residual_risk_withheld"] += 1
            return SanitizedText("[FIELD_WITHHELD:RESIDUAL_RISK]", self.counts - before, "residual_risk")
        return SanitizedText(text, self.counts - before)


def sensitive_literals_from_sessions(sessions: Iterable[Session]) -> set[str]:
    values: set[str] = set()
    for session in sessions:
        for path_text in [str(session.path), session.cwd, *session.distinct_cwds]:
            match = re.search(r"/(?:Users|home)/([^/\s]+)", path_text)
            if match:
                values.add(match.group(1))
    return values


def generalize_tool_action(event: dict[str, Any]) -> str:
    name = f"{event.get('kind', '')} {event.get('name', '')}".lower()
    if any(word in name for word in ("gmail", "email", "mail", "message")):
        return "messaging"
    if any(word in name for word in ("calendar", "schedule", "event")):
        return "scheduling"
    if any(word in name for word in ("browser", "web", "http", "search", "open_url")):
        return "web_or_browser"
    if any(word in name for word in ("apply_patch", "write", "edit", "create", "delete", "move")):
        return "artifact_change"
    if any(word in name for word in ("read", "view", "list", "find", "stat")):
        return "artifact_read"
    if any(word in name for word in ("git", "commit", "push", "branch")):
        return "version_control"
    if any(word in name for word in ("agent", "delegate", "followup", "collaboration")):
        return "delegation"
    if any(word in name for word in ("shell", "bash", "exec", "command", "terminal")):
        return "shell_or_process"
    return "other_tool_action"


def iso_date(value: str) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def local_date_from_timestamp(value: str) -> date | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(TORONTO).date()
    except ValueError:
        return None


def read_json_lines(
    path: Path, source_hasher: Any | None = None
) -> Iterator[tuple[int, dict[str, Any]]]:
    """Yield strict JSON objects and optionally hash the exact bytes parsed."""

    with path.open("rb") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            if source_hasher is not None:
                source_hasher.update(raw_line)
            line = raw_line.decode("utf-8", errors="strict").strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON object at line {line_number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"non-object JSON value at line {line_number}")
            yield line_number, row


def block_text(content: Any, allowed: set[str]) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    texts: list[str] = []
    for block in content:
        if isinstance(block, str):
            texts.append(block)
            continue
        if not isinstance(block, dict) or block.get("type") not in allowed:
            continue
        value = block.get("text")
        if isinstance(value, str):
            texts.append(value)
    return "\n".join(texts)


def claude_human_prompt(row: dict[str, Any]) -> tuple[str, str] | None:
    if row.get("type") != "user" or row.get("isSidechain") is True:
        return None
    if row.get("isMeta") is True or row.get("toolUseResult") is not None:
        return None
    if row.get("sourceToolUseID") is not None:
        return None
    if row.get("entrypoint") not in {None, "cli"}:
        return None
    origin = row.get("origin") or {}
    origin_kind = origin.get("kind") if isinstance(origin, dict) else None
    if origin_kind in {"task-notification", "system"}:
        return None
    prompt_source = row.get("promptSource")
    if prompt_source in {"system", "sdk"}:
        return None
    message = row.get("message") or {}
    if not isinstance(message, dict) or message.get("role") not in {None, "user"}:
        return None
    content = message.get("content")
    text = ""
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        text = block_text(content, {"text", "input_text"})
    if not text.strip():
        return None
    if prompt_source in {"queued", "suggestion_accepted"}:
        provenance = str(prompt_source)
    elif origin_kind == "human" or prompt_source == "typed":
        provenance = "human"
    else:
        provenance = "human_inferred"
    return text, provenance


def nested_text(value: Any, limit: int) -> str:
    if isinstance(value, str):
        return truncate(value, limit)
    if isinstance(value, list):
        pieces: list[str] = []
        for item in value:
            if isinstance(item, str):
                pieces.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if isinstance(text, str):
                    pieces.append(text)
        return truncate("\n".join(pieces), limit)
    if isinstance(value, dict):
        try:
            return truncate(json.dumps(value, ensure_ascii=False, sort_keys=True), limit)
        except (TypeError, ValueError):
            return ""
    return ""


def tool_success_from_text(text: str) -> bool | None:
    if re.search(r'"(?:exit_code|exitCode)"\s*:\s*0\b', text):
        return True
    if re.search(r'"(?:exit_code|exitCode)"\s*:\s*[1-9]\d*\b', text):
        return False
    if re.search(r"\b(?:all tests passed|tests? passed|build succeeded|script completed)\b", text, re.I):
        return True
    if re.search(r"\b(?:traceback|tests? failed|build failed|exit code [1-9])\b", text, re.I):
        return False
    return None


def peek_codex(
    path: Path, source_hasher: Any | None = None
) -> dict[str, Any] | None:
    meta: dict[str, Any] | None = None
    for _, row in read_json_lines(path, source_hasher):
        if meta is None and row.get("type") == "session_meta":
            payload = row.get("payload") or {}
            if not isinstance(payload, dict):
                return None
            source_value = payload.get("source")
            thread_source = payload.get("thread_source")
            parent_thread_id = payload.get("parent_thread_id")
            is_subagent = (
                parent_thread_id is not None
                or isinstance(source_value, dict)
                or thread_source == "subagent"
            )
            local_date = ""
            for index in range(max(0, len(path.parts) - 7), len(path.parts) - 2):
                parts = path.parts[index : index + 3]
                if (
                    len(parts) == 3
                    and re.fullmatch(r"20\d{2}", parts[0])
                    and re.fullmatch(r"\d{2}", parts[1])
                    and re.fullmatch(r"\d{2}", parts[2])
                ):
                    local_date = "-".join(parts)
                    break
            meta = {
                "session_id": str(payload.get("id") or payload.get("session_id") or path.stem),
                "timestamp": str(payload.get("timestamp") or row.get("timestamp") or ""),
                "local_date": local_date,
                "cwd": str(payload.get("cwd") or ""),
                "version": str(payload.get("cli_version") or ""),
                "parent_thread_id": parent_thread_id,
                "session_mode": source_value if isinstance(source_value, str) else "unknown",
                "is_subagent": is_subagent,
            }
    return meta


def peek_claude(
    path: Path, source_hasher: Any | None = None
) -> dict[str, Any] | None:
    if "subagents" in path.parts:
        return {
            "session_id": path.stem,
            "timestamp": "",
            "cwd": "",
            "version": "",
            "session_mode": "subagent",
            "is_subagent": True,
        }
    first_human: dict[str, Any] | None = None
    first_programmatic: dict[str, Any] | None = None
    session_id = path.stem
    for _, row in read_json_lines(path, source_hasher):
        if row.get("agentId") is not None or row.get("isSidechain") is True:
            return {
                "session_id": session_id,
                "timestamp": "",
                "cwd": "",
                "version": "",
                "session_mode": "subagent",
                "is_subagent": True,
            }
        session_id = str(row.get("sessionId") or row.get("session_id") or session_id)
        if claude_human_prompt(row) is not None and first_human is None:
            first_human = row
        if (
            row.get("type") == "user"
            and row.get("entrypoint") == "sdk-cli"
            and first_programmatic is None
        ):
            first_programmatic = row
    anchor = first_human or first_programmatic
    if anchor is None:
        return None
    timestamp = str(anchor.get("timestamp") or "")
    mode = "interactive" if first_human is not None else "programmatic_sdk"
    return {
        "session_id": session_id,
        "timestamp": timestamp,
        "local_date": (
            local_date_from_timestamp(timestamp).isoformat()
            if local_date_from_timestamp(timestamp)
            else ""
        ),
        "cwd": str(anchor.get("cwd") or ""),
        "version": str(anchor.get("version") or ""),
        "session_mode": mode,
        "is_subagent": False,
    }


def discover_paths(
    root: Path,
    source: str,
    start: date,
    end: date,
    allowed_modes: set[str] | None = None,
    modified_before: float | None = None,
) -> tuple[list[tuple[Path, dict[str, Any]]], Counter[str]]:
    selected: dict[str, tuple[Path, dict[str, Any]]] = {}
    excluded: Counter[str] = Counter()
    peeker = peek_codex if source == "codex" else peek_claude
    for path in sorted(root.rglob("*.jsonl")):
        if modified_before is not None and path.stat().st_mtime > modified_before:
            excluded["recently_modified_source"] += 1
            continue
        try:
            discovery_hasher = hashlib.sha256()
            meta = peeker(path, discovery_hasher)
        except (OSError, UnicodeDecodeError, ValueError):
            excluded["malformed_source"] += 1
            continue
        if meta is None:
            excluded["unrecognized_or_subagent"] += 1
            continue
        if meta.get("is_subagent"):
            excluded["subagent"] += 1
            continue
        if allowed_modes is not None and str(meta.get("session_mode")) not in allowed_modes:
            excluded["excluded_session_mode"] += 1
            continue
        day = iso_date(str(meta.get("local_date") or meta.get("timestamp") or ""))
        if day is None:
            excluded["missing_date"] += 1
            continue
        if day < start or day > end:
            excluded["outside_date_window"] += 1
            continue
        cwd = str(meta.get("cwd") or "").lower()
        if "/data/fixtures/" in cwd or "/private/discovery/synthetic" in cwd:
            excluded["synthetic_fixture"] += 1
            continue
        try:
            discovery_size, discovery_mtime_ns = source_state(path)
        except OSError:
            excluded["source_changed_during_discovery"] += 1
            continue
        meta["_discovery_sha256"] = discovery_hasher.hexdigest()
        meta["_discovery_size"] = discovery_size
        meta["_discovery_mtime_ns"] = discovery_mtime_ns
        session_id = str(meta["session_id"])
        current = selected.get(session_id)
        if current is None or path.stat().st_size > current[0].stat().st_size:
            if current is not None:
                excluded["duplicate_session_file"] += 1
            selected[session_id] = (path, meta)
        else:
            excluded["duplicate_session_file"] += 1
    return sorted(selected.values(), key=lambda item: (item[1]["timestamp"], str(item[0]))), excluded


def discovery_snapshot_matches(
    meta: dict[str, Any], parsed_digest: str, parsed_state: tuple[int, int]
) -> bool:
    return (
        meta.get("_discovery_sha256") == parsed_digest
        and meta.get("_discovery_size") == parsed_state[0]
        and meta.get("_discovery_mtime_ns") == parsed_state[1]
    )


def evenly_spaced(rows: list[T], limit: int) -> list[T]:
    if limit <= 0 or len(rows) <= limit:
        return rows
    if limit == 1:
        return [rows[len(rows) // 2]]
    indexes = [round(index * (len(rows) - 1) / (limit - 1)) for index in range(limit)]
    return [rows[index] for index in indexes]


def parse_codex(
    path: Path,
    meta: dict[str, Any],
    max_chars: int,
    source_hasher: Any | None = None,
) -> Session:
    turns: list[Turn] = []
    current: Turn | None = None
    developer_context: deque[str] = deque(maxlen=3)
    pending_compaction = False
    compaction_summary = ""
    current_model = ""
    current_cwd = str(meta.get("cwd") or "")
    event_count = 0

    def start_turn(text: str, timestamp: str, line_number: int) -> Turn:
        nonlocal current, pending_compaction, compaction_summary
        if current is not None:
            current.end_line = max(current.end_line, line_number - 1)
        current = Turn(
            user_text=truncate(text, max_chars),
            timestamp=timestamp,
            start_line=line_number,
            node_id=f"line-{line_number}",
            model=current_model,
            cwd=current_cwd,
            version=str(meta.get("version") or ""),
            governing_context=[truncate(item, max_chars) for item in developer_context],
            compaction_before=pending_compaction,
            compaction_summary=truncate(compaction_summary, max_chars),
        )
        turns.append(current)
        pending_compaction = False
        compaction_summary = ""
        return current

    def ensure_current(line_number: int, timestamp: str) -> Turn | None:
        del line_number, timestamp
        return current

    for line_number, row in read_json_lines(path, source_hasher):
        event_count += 1
        timestamp = str(row.get("timestamp") or "")
        top_type = row.get("type")
        payload = row.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}

        if top_type == "turn_context":
            current_model = str(payload.get("model") or current_model)
            current_cwd = str(payload.get("cwd") or current_cwd)
            continue

        if top_type == "compacted":
            pending_compaction = True
            compaction_summary = str(payload.get("message") or "")
            continue

        if top_type == "response_item" and payload.get("type") == "message":
            role = payload.get("role")
            text = block_text(payload.get("content"), {"input_text", "output_text", "text"})
            if role == "developer" and text:
                developer_context.append(text)
            elif role == "user":
                # The canonical human message is event_msg/user_message. These
                # response_item records are either duplicates or injected
                # startup context and must not become human turns.
                pass
            elif role == "assistant" and text:
                turn = ensure_current(line_number, timestamp)
                if turn is not None:
                    turn.assistant_texts.append(truncate(text, max_chars))
                    turn.end_line = line_number
            continue

        if top_type == "event_msg" and payload.get("type") == "user_message":
            text = payload.get("message")
            if isinstance(text, str) and text.strip():
                start_turn(text, timestamp, line_number)
            continue

        if top_type == "response_item" and payload.get("type") in {
            "function_call",
            "custom_tool_call",
        }:
            turn = ensure_current(line_number, timestamp)
            if turn is not None:
                name = str(payload.get("name") or payload.get("tool_name") or payload.get("type"))
                arguments = payload.get("arguments")
                if arguments is None:
                    arguments = payload.get("input")
                turn.tool_events.append(
                    ToolEvent(
                        kind="tool_call",
                        name=name,
                        text=nested_text(arguments, max_chars),
                        line_number=line_number,
                    )
                )
                turn.end_line = line_number
            continue

        if top_type == "response_item" and payload.get("type") in {
            "function_call_output",
            "custom_tool_call_output",
        }:
            turn = ensure_current(line_number, timestamp)
            if turn is not None:
                output = nested_text(payload.get("output"), max_chars)
                turn.tool_events.append(
                    ToolEvent(
                        kind="tool_result",
                        name=str(payload.get("name") or "tool_result"),
                        text=output,
                        line_number=line_number,
                        success=tool_success_from_text(output),
                    )
                )
                turn.end_line = line_number
            continue

    if current is not None:
        current.end_line = max(current.end_line, event_count)
    model = next((turn.model for turn in reversed(turns) if turn.model), "")
    return Session(
        source="codex",
        session_mode=str(meta.get("session_mode") or "unknown"),
        session_id=str(meta["session_id"]),
        timestamp=str(meta["timestamp"]),
        local_date=str(meta.get("local_date") or str(meta.get("timestamp") or "")[:10]),
        cwd=str(meta.get("cwd") or ""),
        version=str(meta.get("version") or ""),
        model=model,
        distinct_cwds=sorted(
            {turn.cwd for turn in turns if turn.cwd}
            | ({str(meta.get("cwd"))} if meta.get("cwd") else set())
        ),
        distinct_versions=[str(meta.get("version"))] if meta.get("version") else [],
        distinct_models=sorted({turn.model for turn in turns if turn.model}),
        path=path,
        turns=turns,
        event_count=event_count,
    )


def parse_claude(
    path: Path,
    meta: dict[str, Any],
    max_chars: int,
    source_hasher: Any | None = None,
) -> Session:
    physical = list(read_json_lines(path, source_hasher))
    event_count = len(physical)
    canonical: dict[str, tuple[int, dict[str, Any]]] = {}
    last_leaf = ""
    permission_events: list[tuple[int, str]] = []
    sidecars: list[tuple[int, dict[str, Any]]] = []
    distinct_cwds: set[str] = set()
    distinct_versions: set[str] = set()
    distinct_models: set[str] = set()

    for line_number, row in physical:
        cwd = row.get("cwd")
        version = row.get("version")
        if isinstance(cwd, str) and cwd:
            distinct_cwds.add(cwd)
        if isinstance(version, str) and version:
            distinct_versions.add(version)
        message = row.get("message") or {}
        if isinstance(message, dict):
            model = message.get("model")
            if isinstance(model, str) and model and model != "<synthetic>":
                distinct_models.add(model)
        if row.get("type") == "last-prompt" and row.get("leafUuid"):
            last_leaf = str(row["leafUuid"])
        if row.get("type") == "permission-mode":
            mode = str(row.get("permissionMode") or row.get("mode") or "")
            permission_events.append((line_number, mode))
        if row.get("type") in {"file-history-snapshot", "file-history-delta"}:
            sidecars.append((line_number, row))
        uuid = row.get("uuid")
        if isinstance(uuid, str) and uuid and row.get("isSidechain") is not True:
            # Later copies add metadata and occasionally repair parentage. The
            # last occurrence is the canonical graph node.
            canonical[uuid] = (line_number, row)

    active_ids: set[str] = set()
    ordered_nodes: list[tuple[int, dict[str, Any]]] = []
    if last_leaf and last_leaf in canonical:
        cursor = last_leaf
        seen: set[str] = set()
        reverse_chain: list[tuple[int, dict[str, Any]]] = []
        while cursor and cursor in canonical and cursor not in seen:
            seen.add(cursor)
            node = canonical[cursor]
            reverse_chain.append(node)
            parent = node[1].get("parentUuid")
            cursor = str(parent) if isinstance(parent, str) else ""
        ordered_nodes = list(reversed(reverse_chain))
        active_ids = seen
    else:
        # Synthetic and legacy records without a branch marker retain their
        # last-wins canonical nodes in physical order.
        ordered_nodes = sorted(canonical.values(), key=lambda item: item[0])
        active_ids = set(canonical)

    def permission_at(line_number: int) -> str:
        value = ""
        for state_line, mode in permission_events:
            if state_line > line_number:
                break
            value = mode
        return value

    turns: list[Turn] = []
    current: Turn | None = None
    current_index = -1
    uuid_to_turn: dict[str, int] = {}
    seen_blocks: set[tuple[str, int, str, str]] = set()
    pending_compaction = False

    for line_number, row in ordered_nodes:
        top_type = row.get("type")
        uuid = str(row.get("uuid") or "")
        if top_type == "system" and (
            row.get("subtype") == "compact_boundary" or row.get("compactMetadata") is not None
        ):
            pending_compaction = True
            if current is not None and uuid:
                uuid_to_turn[uuid] = current_index
            continue

        human = claude_human_prompt(row)
        if human is not None:
            text, provenance = human
            if current is not None:
                current.end_line = max(current.end_line, line_number - 1)
            current = Turn(
                user_text=truncate(text, max_chars),
                timestamp=str(row.get("timestamp") or ""),
                start_line=line_number,
                node_id=uuid or f"line-{line_number}",
                cwd=str(row.get("cwd") or meta.get("cwd") or ""),
                version=str(row.get("version") or meta.get("version") or ""),
                git_branch=str(row.get("gitBranch") or ""),
                prompt_provenance=provenance,
                permission_mode=str(row.get("permissionMode") or permission_at(line_number)),
                compaction_before=pending_compaction,
            )
            pending_compaction = False
            turns.append(current)
            current_index = len(turns) - 1
            if uuid:
                uuid_to_turn[uuid] = current_index
            continue

        if current is None:
            continue
        if uuid:
            uuid_to_turn[uuid] = current_index

        if top_type == "assistant":
            message = row.get("message") or {}
            if not isinstance(message, dict):
                continue
            model = str(message.get("model") or "")
            if (
                row.get("isApiErrorMessage") is True
                or row.get("error") is not None
                or row.get("apiErrorStatus") is not None
            ):
                current.infrastructure_error = True
                continue
            if model == "<synthetic>":
                continue
            current.infrastructure_error = False
            if model:
                current.model = model
            if not current.cwd:
                current.cwd = str(row.get("cwd") or "")
            if not current.version:
                current.version = str(row.get("version") or "")
            message_id = str(message.get("id") or row.get("requestId") or uuid or line_number)
            content = message.get("content")
            if isinstance(content, str):
                signature = (message_id, current_index, "text", opaque(content))
                if signature not in seen_blocks:
                    seen_blocks.add(signature)
                    current.assistant_texts.append(truncate(content, max_chars))
            elif isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = str(block.get("type") or "")
                    if block_type == "text" and isinstance(block.get("text"), str):
                        value = str(block["text"])
                        signature = (message_id, current_index, "text", opaque(value))
                        if signature not in seen_blocks:
                            seen_blocks.add(signature)
                            current.assistant_texts.append(truncate(value, max_chars))
                    elif block_type == "tool_use":
                        block_id = str(block.get("id") or opaque(json.dumps(block, sort_keys=True)))
                        signature = (message_id, current_index, "tool_use", block_id)
                        if signature in seen_blocks:
                            continue
                        seen_blocks.add(signature)
                        current.tool_events.append(
                            ToolEvent(
                                kind="tool_call",
                                name=str(block.get("name") or "tool_use"),
                                text=nested_text(block.get("input"), max_chars),
                                line_number=line_number,
                            )
                        )
                    # Deliberately exclude thinking/signature blocks.
            current.end_line = line_number
            continue

        if top_type == "user":
            message = row.get("message") or {}
            content = message.get("content") if isinstance(message, dict) else None
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                output = nested_text(block.get("content"), max_chars)
                explicit = block.get("is_error")
                success = False if explicit is True else tool_success_from_text(output)
                current.tool_events.append(
                    ToolEvent(
                        kind="tool_result",
                        name="tool_result",
                        text=output,
                        line_number=line_number,
                        success=success,
                    )
                )
                current.end_line = line_number

    def linked_turn(row: dict[str, Any]) -> Turn | None:
        links = [row.get("messageId"), (row.get("snapshot") or {}).get("messageId")]
        for link in links:
            cursor = str(link) if isinstance(link, str) else ""
            seen: set[str] = set()
            while cursor and cursor not in seen:
                seen.add(cursor)
                if cursor in uuid_to_turn:
                    return turns[uuid_to_turn[cursor]]
                node = canonical.get(cursor)
                if node is None:
                    break
                parent = node[1].get("parentUuid")
                cursor = str(parent) if isinstance(parent, str) else ""
        return None

    for line_number, row in sidecars:
        turn = linked_turn(row)
        if turn is None:
            continue
        if row.get("type") == "file-history-delta":
            paths = [row.get("trackingPath"), (row.get("backup") or {}).get("backupFileName")]
            path_refs = ["PATH-" + opaque(str(value)) for value in paths if value]
            text = "file-history delta recorded"
            if path_refs:
                text += ": " + ", ".join(path_refs)
            kind = "artifact_delta"
        else:
            snapshot = row.get("snapshot") or {}
            backups = snapshot.get("trackedFileBackups") or {}
            path_refs = ["PATH-" + opaque(str(value)) for value in backups] if isinstance(backups, dict) else []
            text = f"file-history snapshot recorded ({len(path_refs)} tracked paths)"
            kind = "artifact_snapshot"
        turn.tool_events.append(
            ToolEvent(
                kind=kind,
                name=str(row.get("type")),
                text=text,
                line_number=line_number,
            )
        )
        turn.end_line = max(turn.end_line, line_number)

    if current is not None:
        current.end_line = max(current.end_line, event_count)
    models = sorted(distinct_models | {turn.model for turn in turns if turn.model})
    return Session(
        source="claude",
        session_mode=str(meta.get("session_mode") or "interactive"),
        session_id=str(meta["session_id"]),
        timestamp=str(meta["timestamp"]),
        local_date=str(meta.get("local_date") or ""),
        cwd=str(meta.get("cwd") or ""),
        version=str(meta.get("version") or ""),
        model=next((turn.model for turn in reversed(turns) if turn.model), ""),
        distinct_cwds=sorted(distinct_cwds),
        distinct_versions=sorted(distinct_versions),
        distinct_models=models,
        path=path,
        turns=turns,
        event_count=event_count,
        excluded_branch_records=max(0, len(canonical) - len(active_ids)),
    )


def matching_signals(
    text: str,
    patterns: list[tuple[str, int, re.Pattern[str]]],
) -> list[dict[str, Any]]:
    return [
        {"signal": name, "weight": weight}
        for name, weight, pattern in patterns
        if pattern.search(text)
    ]


def failure_signals(text: str, previous_was_repair: bool = False) -> list[dict[str, Any]]:
    signals = matching_signals(text, FAILURE_PATTERNS)
    if previous_was_repair and signals:
        signals.append({"signal": "repair_non_uptake", "weight": 3})
    return signals


def load_signals(turn: Turn, previous_was_repair: bool) -> list[dict[str, Any]]:
    signals = matching_signals(turn.user_text, LOAD_PATTERNS)
    word_count = len(turn.user_text.split())
    if word_count <= 12 and any(item["signal"] == "reference_or_ellipsis" for item in signals):
        signals.append({"signal": "short_context_dependent_request", "weight": 1})
    if turn.compaction_before:
        signals.append({"signal": "post_compaction_state_recovery", "weight": 2})
    if previous_was_repair:
        signals.append({"signal": "repair_conditioned_turn", "weight": 2})
    return deduplicate_signals(signals)


def uptake_signals(text: str, prior_turn: Turn) -> list[dict[str, Any]]:
    # Limit explicit-praise matching to the opening portion. Long pasted reports
    # often quote praise about a different agent and otherwise inflate this cue.
    opening = text[:500]
    signals = matching_signals(opening, UPTAKE_PATTERNS)
    if DEPENDENT_CONTINUATION.search(opening) and not failure_signals(opening):
        signals.append({"signal": "dependent_continuation", "weight": 2})
    if EXPLICIT_ACKNOWLEDGMENT.fullmatch(opening) and not failure_signals(opening):
        signals.append({"signal": "explicit_acknowledgment", "weight": 2})
    if prior_turn.has_tool_success():
        signals.append({"signal": "verified_tool_success", "weight": 1})
    return deduplicate_signals(signals)


def deduplicate_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, int] = {}
    for signal in signals:
        name = str(signal["signal"])
        best[name] = max(best.get(name, 0), int(signal["weight"]))
    return [{"signal": name, "weight": best[name]} for name in sorted(best)]


def signal_score(signals: list[dict[str, Any]]) -> int:
    return sum(int(item["weight"]) for item in signals)


def privacy_flags(text: str) -> list[str]:
    flags = [name for name, pattern in PRIVACY_PATTERNS if pattern.search(text)]
    if THIRD_PARTY_PATTERN.search(text):
        flags.append("possible_third_party_content")
    if "```" in text:
        flags.append("code_or_quoted_block")
    if len(text) > 16000:
        flags.append("long_context")
    return sorted(set(flags))


def alternative_explanations(
    feedback: str,
    trigger: Turn,
    failure: list[dict[str, Any]],
) -> list[str]:
    alternatives: list[str] = []
    if re.search(r"\b(?:actually|instead|changed\s+my\s+mind|new\s+request)\b", feedback, re.I):
        alternatives.append("user_changed_request")
    if re.search(r"\b(?:i\s+mean|to\s+be\s+clear|what\s+i\s+meant)\b", feedback, re.I):
        alternatives.append("clarification_needed")
    if re.search(r"\b(?:factually|incorrect|wrong\s+(?:number|date|fact|claim))\b", feedback, re.I):
        alternatives.append("non_pragmatic_error")
    if trigger.compaction_before:
        alternatives.append("lost_or_hidden_context")
    if not alternatives and failure:
        alternatives.extend(["reasonable_competing_reading", "insufficient_evidence"])
    return sorted(set(alternatives))


def primary_phenomenon(polarity: str, signals: list[dict[str, Any]]) -> str:
    names = {str(item["signal"]) for item in signals}
    priorities = [
        ("repair_uptake", {"repair_non_uptake", "repair_conditioned_turn"}),
        ("scope_and_authorization", {"scope_or_file_correction", "scope_boundary", "authority_or_permission"}),
        ("task_type_recognition", {"action_answer_mismatch", "task_type_boundary"}),
        ("completion_and_status_reporting", {"completion_or_status_challenge"}),
        ("reference_and_ellipsis", {"reference_or_ellipsis", "short_context_dependent_request"}),
        ("state_and_compaction", {"post_compaction_state_recovery"}),
        ("negative_constraint_persistence", {"negative_constraint", "instruction_repetition"}),
        ("tool_action_alignment", {"verified_tool_success", "stop_or_revert"}),
        (
            "general_assessment",
            {"strong_negative_assessment", "strong_positive_assessment", "explicit_acknowledgment"},
        ),
    ]
    for phenomenon, relevant in priorities:
        if names & relevant:
            return phenomenon
    return "other_pragmatic_candidate" if polarity else "insufficient_evidence"


def context_window(turns: list[Turn], trigger_index: int, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for turn in turns[max(0, trigger_index - 2) : trigger_index]:
        rows.append(
            {
                "user": truncate(turn.user_text, limit),
                "assistant": turn.assistant_text(limit),
            }
        )
    return rows


def tool_trace(turn: Turn, limit: int) -> list[dict[str, Any]]:
    return [
        {
            "kind": event.kind,
            "name": event.name,
            "text": truncate(event.text, limit),
            "success": event.success,
        }
        for event in turn.tool_events
    ]


def make_candidate(
    session: Session,
    turns: list[Turn],
    feedback_index: int,
    polarity: str,
    evidence: list[dict[str, Any]],
    load: list[dict[str, Any]],
    alternatives: list[str],
    max_chars: int,
) -> dict[str, Any]:
    trigger_index = feedback_index - 1
    trigger = turns[trigger_index]
    feedback = turns[feedback_index]
    session_ref = f"SES-{opaque(session.source + '|' + session.session_id)}"
    candidate_id = "NPE-" + opaque(
        f"{session.source}|{session.session_id}|{trigger.node_id}|{feedback.node_id}|{polarity}", 24
    )
    combined = "\n".join(
        [
            *(item for item in trigger.governing_context if item),
            trigger.compaction_summary,
            trigger.user_text,
            trigger.assistant_text(max_chars),
            *(event.text for event in trigger.tool_events),
            feedback.user_text,
            feedback.assistant_text(max_chars),
        ]
    )
    score = signal_score(evidence) if polarity == "likely_pragmatic_failure" else signal_score(evidence) + signal_score(load)
    strength = "high" if score >= 6 else "moderate" if score >= 3 else "low"
    all_signals = deduplicate_signals(evidence + load)
    return {
        "candidate_id": candidate_id,
        "candidate_class": polarity,
        "candidate_score": score,
        "evidence_strength": strength,
        "source": session.source,
        "session_mode": session.session_mode,
        "session_ref": session_ref,
        "project_ref": "PRJ-" + opaque(trigger.cwd or session.cwd or "unknown"),
        "session_timestamp": session.timestamp,
        "session_local_date": session.local_date,
        "feedback_timestamp": feedback.timestamp,
        "software_version": trigger.version or session.version,
        "model": trigger.model or session.model,
        "git_branch": trigger.git_branch,
        "prompt_provenance": trigger.prompt_provenance,
        "primary_phenomenon": primary_phenomenon(polarity, all_signals),
        "evidence_signals": evidence,
        "pragmatic_load_signals": load,
        "alternative_explanations": alternatives,
        "privacy_flags": privacy_flags(combined),
        "governing_context": [truncate(item, max_chars) for item in trigger.governing_context],
        "compaction_before": trigger.compaction_before,
        "compaction_summary": truncate(trigger.compaction_summary, max_chars),
        "permission_mode": trigger.permission_mode,
        "preceding_context": context_window(turns, trigger_index, min(max_chars, 1800)),
        "triggering_request": truncate(trigger.user_text, max_chars),
        "model_visible_response": trigger.assistant_text(max_chars),
        "tool_trace": tool_trace(trigger, min(max_chars, 2200)),
        "user_followup": truncate(feedback.user_text, max_chars),
        "immediate_model_response": feedback.assistant_text(max_chars),
        "retrieval_note": (
            "Deterministic private-discovery candidate; not a gold label, representative "
            "observation, prevalence datum, or vendor comparison."
        ),
        "_provenance": {
            "raw_path": str(session.path),
            "session_id": session.session_id,
            "trigger_turn_index": trigger_index,
            "feedback_turn_index": feedback_index,
            "trigger_node_id": trigger.node_id,
            "feedback_node_id": feedback.node_id,
            "start_line": trigger.start_line,
            "end_line": feedback.end_line or feedback.start_line,
        },
    }


def candidates_for_session(session: Session, max_chars: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    turns = session.turns
    prior_feedback_was_repair = False
    for index in range(1, len(turns)):
        trigger = turns[index - 1]
        feedback = turns[index]
        if trigger.infrastructure_error:
            prior_feedback_was_repair = False
            continue
        failure = failure_signals(feedback.user_text, previous_was_repair=prior_feedback_was_repair)
        previous_trigger_was_repair = signal_score(
            failure_signals(trigger.user_text, previous_was_repair=False)
        ) >= 3
        load = load_signals(trigger, previous_was_repair=previous_trigger_was_repair)
        if signal_score(failure) >= 3:
            candidates.append(
                make_candidate(
                    session,
                    turns,
                    index,
                    "likely_pragmatic_failure",
                    failure,
                    load,
                    alternative_explanations(feedback.user_text, trigger, failure),
                    max_chars,
                )
            )
            prior_feedback_was_repair = True
            continue
        uptake = uptake_signals(feedback.user_text, trigger)
        if signal_score(uptake) >= 2 and signal_score(load) >= 2:
            candidates.append(
                make_candidate(
                    session,
                    turns,
                    index,
                    "surprising_success_candidate",
                    uptake,
                    load,
                    [],
                    max_chars,
                )
            )
        prior_feedback_was_repair = False
    return candidates


def select_review_corpus(
    candidates: list[dict[str, Any]],
    max_per_session: int,
    review_limit: int,
) -> list[dict[str, Any]]:
    per_session: defaultdict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        key = (str(candidate["session_ref"]), str(candidate["candidate_class"]))
        per_session[key].append(candidate)
    capped: list[dict[str, Any]] = []
    for rows in per_session.values():
        rows.sort(key=lambda row: (-int(row["candidate_score"]), str(row["candidate_id"])))
        capped.extend(rows[:max_per_session])

    strata: defaultdict[tuple[str, ...], deque[dict[str, Any]]] = defaultdict(deque)
    for candidate in sorted(
        capped,
        key=lambda row: (-int(row["candidate_score"]), str(row["candidate_id"])),
    ):
        month = str(candidate.get("feedback_timestamp") or candidate.get("session_timestamp") or "")[:7]
        key = (
            str(candidate["source"]),
            str(candidate.get("session_mode") or "unknown"),
            str(candidate["candidate_class"]),
            str(candidate["primary_phenomenon"]),
            month,
        )
        strata[key].append(candidate)

    selected: list[dict[str, Any]] = []
    active = sorted(strata)
    while active and len(selected) < review_limit:
        next_active: list[tuple[str, ...]] = []
        for key in active:
            queue = strata[key]
            if queue and len(selected) < review_limit:
                selected.append(queue.popleft())
            if queue:
                next_active.append(key)
        active = next_active
    return selected


def candidate_refs(candidate: dict[str, Any], key: bytes) -> tuple[str, str, str]:
    provenance = candidate["_provenance"]
    session_value = f"{candidate['source']}|{provenance['session_id']}"
    identity = "|".join(
        [
            session_value,
            str(provenance["trigger_node_id"]),
            str(provenance["feedback_node_id"]),
            str(candidate["candidate_class"]),
        ]
    )
    source_value = f"{candidate['source']}|{provenance['raw_path']}"
    return (
        hmac_ref(key, "NPE2", "candidate", identity, 24),
        hmac_ref(key, "SES2", "session", session_value, 20),
        hmac_ref(key, "SRC2", "source", source_value, 20),
    )


OMITTED_CONTENT_FIELDS = [
    "governing_context",
    "compaction_summary",
    "tool_trace.text",
    "prompt_provenance",
]


def base_index_row(
    candidate: dict[str, Any],
    key: bytes,
    review_selected: bool,
) -> dict[str, Any]:
    candidate_id, session_ref, _ = candidate_refs(candidate, key)
    tool_events = candidate.get("tool_trace") or []
    return {
        "candidate_id": candidate_id,
        "session_ref": session_ref,
        "source": candidate["source"],
        "session_mode": candidate["session_mode"],
        "month": str(candidate.get("feedback_timestamp") or candidate.get("session_timestamp") or "")[:7],
        "candidate_class": candidate["candidate_class"],
        "candidate_score": candidate["candidate_score"],
        "evidence_strength": candidate["evidence_strength"],
        "primary_phenomenon": candidate["primary_phenomenon"],
        "evidence_signals": candidate["evidence_signals"],
        "pragmatic_load_signals": candidate["pragmatic_load_signals"],
        "alternative_explanations": candidate["alternative_explanations"],
        "compaction_before": bool(candidate.get("compaction_before")),
        "tool_event_count": len(tool_events),
        "tool_action_classes": sorted({generalize_tool_action(event) for event in tool_events}),
        "content_withheld_fields": list(OMITTED_CONTENT_FIELDS),
        "redaction_counts": {},
        "privacy_disposition": "internal_review_only",
        "reconstruction_status": "automatic_minimization",
        "review_selected": review_selected,
    }


def needs_preceding_context(candidate: dict[str, Any]) -> bool:
    names = {
        str(item.get("signal"))
        for item in candidate.get("evidence_signals", [])
        + candidate.get("pragmatic_load_signals", [])
        if isinstance(item, dict)
    }
    return bool(
        names
        & {
            "reference_or_ellipsis",
            "instruction_repetition",
            "repair_non_uptake",
            "post_compaction_state_recovery",
        }
    )


def minimized_review_row(
    candidate: dict[str, Any],
    key: bytes,
    sensitive_literals: Iterable[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    index = base_index_row(candidate, key, review_selected=True)
    sanitizer = EpisodeSanitizer(sensitive_literals)
    withheld = set(index["content_withheld_fields"])
    manual_required = False

    def clean(field_name: str, text: str, limit: int) -> str:
        nonlocal manual_required
        result = sanitizer.sanitize(text, limit)
        if result.withheld_reason:
            withheld.add(field_name)
            manual_required = True
            return ""
        return result.text

    preceding: list[dict[str, str]] = []
    if needs_preceding_context(candidate):
        for pair in (candidate.get("preceding_context") or [])[-2:]:
            if not isinstance(pair, dict):
                continue
            preceding.append(
                {
                    "user": clean("preceding_context.user", str(pair.get("user") or ""), PRECEDING_FIELD_LIMIT),
                    "assistant": clean(
                        "preceding_context.assistant",
                        str(pair.get("assistant") or ""),
                        PRECEDING_FIELD_LIMIT,
                    ),
                }
            )
        if {"preceding_context.user", "preceding_context.assistant"} & withheld:
            preceding = []
            withheld.discard("preceding_context.user")
            withheld.discard("preceding_context.assistant")
            withheld.add("preceding_context")
            manual_required = True
    else:
        withheld.add("preceding_context")

    text_fields = {
        "triggering_request": clean(
            "triggering_request", str(candidate.get("triggering_request") or ""), REVIEW_FIELD_LIMIT
        ),
        "model_visible_response": clean(
            "model_visible_response",
            str(candidate.get("model_visible_response") or ""),
            REVIEW_FIELD_LIMIT,
        ),
        "user_followup": clean(
            "user_followup", str(candidate.get("user_followup") or ""), REVIEW_FIELD_LIMIT
        ),
        "immediate_model_response": clean(
            "immediate_model_response",
            str(candidate.get("immediate_model_response") or ""),
            REVIEW_FIELD_LIMIT,
        ),
    }
    text_char_count = sum(len(value) for value in text_fields.values()) + sum(
        len(value) for pair in preceding for value in pair.values()
    )
    if text_char_count > EPISODE_TEXT_LIMIT and preceding:
        preceding = []
        withheld.add("preceding_context")
        manual_required = True
        sanitizer.counts["episode_cap_omission"] += 1
        text_char_count = sum(len(value) for value in text_fields.values())
    if text_char_count > EPISODE_TEXT_LIMIT:
        raise RuntimeError("minimized episode exceeds the total text cap")

    index["content_withheld_fields"] = sorted(withheld)
    index["redaction_counts"] = dict(sorted(sanitizer.counts.items()))
    if manual_required:
        index["reconstruction_status"] = "manual_controlled_reconstruction_required"
    review = {key_name: value for key_name, value in index.items() if key_name != "review_selected"}
    review.update(
        {
            "preceding_context": preceding,
            **text_fields,
            "text_char_count": text_char_count,
        }
    )
    return index, review


def linkage_row(candidate: dict[str, Any], key: bytes) -> dict[str, Any]:
    candidate_id, session_ref, source_ref = candidate_refs(candidate, key)
    provenance = candidate["_provenance"]
    return {
        "candidate_id": candidate_id,
        "session_ref": session_ref,
        "source": candidate["source"],
        "source_ref": source_ref,
        "raw_path": provenance["raw_path"],
        "session_id": provenance["session_id"],
        "trigger_turn_index": provenance["trigger_turn_index"],
        "feedback_turn_index": provenance["feedback_turn_index"],
        "trigger_node_id": provenance["trigger_node_id"],
        "feedback_node_id": provenance["feedback_node_id"],
        "start_line": provenance["start_line"],
        "end_line": provenance["end_line"],
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def candidate_text_fields(row: dict[str, Any]) -> Iterator[tuple[str, str]]:
    for name in (
        "triggering_request",
        "model_visible_response",
        "user_followup",
        "immediate_model_response",
    ):
        value = row.get(name)
        if isinstance(value, str):
            yield name, value
    for pair in row.get("preceding_context") or []:
        if not isinstance(pair, dict):
            continue
        for role in ("user", "assistant"):
            value = pair.get(role)
            if isinstance(value, str):
                yield f"preceding_context.{role}", value


def residual_risk_report(
    candidate_index: list[dict[str, Any]], review_rows: list[dict[str, Any]]
) -> dict[str, Any]:
    patterns: dict[str, re.Pattern[str]] = {
        "absolute_or_home_path": ABSOLUTE_PATH_RE,
        "email": EMAIL_RE,
        "phone": PHONE_RE,
        "url": URL_RE,
        "handle": HANDLE_RE,
        "credential_context": CREDENTIAL_RE,
        "private_key": PRIVATE_KEY_RE,
        "active_markup": ACTIVE_MARKUP_RE,
        "network_code": NETWORK_CODE_RE,
        "correspondence_header": CORRESPONDENCE_RE,
        "code_fence": re.compile(r"```"),
        "honorific_name": HONORIFIC_NAME_RE,
        "organization_pattern": ORG_RE,
        "proper_name_pattern": PROPER_NAME_RE,
    }
    matches: Counter[str] = Counter()
    records: dict[str, set[str]] = defaultdict(set)
    field_matches: dict[str, Counter[str]] = defaultdict(Counter)
    for row in review_rows:
        for field_name, text in candidate_text_fields(row):
            for pattern_name, pattern in patterns.items():
                count = len(pattern.findall(text))
                if count:
                    matches[pattern_name] += count
                    records[pattern_name].add(str(row["candidate_id"]))
                    field_matches[pattern_name][field_name] += count
    redactions: Counter[str] = Counter()
    for row in review_rows:
        redactions.update(
            {name: int(count) for name, count in (row.get("redaction_counts") or {}).items()}
        )
    reconstructions = Counter(row["reconstruction_status"] for row in review_rows)
    return {
        "schema_version": 1,
        "kind": "naturalistic_corpus_residual_risk_audit",
        "privacy_model_version": PRIVACY_MODEL_VERSION,
        "candidate_index_rows": len(candidate_index),
        "review_rows": len(review_rows),
        "residual_identifier_counts": {
            name: {
                "matches": matches[name],
                "records": len(records[name]),
                "fields": dict(sorted(field_matches[name].items())),
            }
            for name in patterns
        },
        "redaction_counts": dict(redactions.most_common()),
        "reconstruction_status_counts": dict(sorted(reconstructions.items())),
        "text_character_total": sum(int(row["text_char_count"]) for row in review_rows),
        "max_episode_text_characters": max(
            (int(row["text_char_count"]) for row in review_rows), default=0
        ),
        "interpretation": (
            "Deterministic residual-pattern audit only; automatic minimization is not "
            "anonymization or authorization for release."
        ),
    }


def file_inventory(root: Path, exclude: set[str] | None = None) -> list[dict[str, Any]]:
    excluded = exclude or set()
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = str(path.relative_to(root))
        if relative in excluded:
            continue
        stat_result = path.stat()
        rows.append(
            {
                "relative_path": relative,
                "sha256": sha256_file(path),
                "byte_size": stat_result.st_size,
                "mode": f"{stat_result.st_mode & 0o777:04o}",
            }
        )
    return rows


def duplicate_groups(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: defaultdict[str, list[str]] = defaultdict(list)
    for row in inventory:
        groups[str(row["sha256"])].append(str(row["relative_path"]))
    return [
        {"sha256": digest, "relative_paths": sorted(paths)}
        for digest, paths in sorted(groups.items())
        if len(paths) > 1
    ]


V1_CONTEXT_RISK_FIELDS = {
    "absolute_or_home_paths",
    "correspondence_related_material",
    "employer_identity_or_context",
    "owner_direct_identifiers",
    "reidentifying_combinations",
    "source_code_or_data_material",
    "third_party_personal_data",
    "unpublished_manuscript_or_research_material",
}
V1_CONTEXT_DISPOSITION_FIELDS = {
    "contextual_rewrite_and_trace_minimization_required",
    "exclude_or_reconstruct_from_abstract_event",
    "safe_by_simple_token_redaction",
}
V1_CONTEXT_COMPOSITION_FIELDS = {
    "claude_likely_pragmatic_failure",
    "claude_surprising_success_candidate",
    "codex_likely_pragmatic_failure",
    "codex_surprising_success_candidate",
}
V1_ALLOWED_FILES = {
    "README.md",
    "all-candidates.jsonl",
    "corpus-manifest.json",
    "normalized-events/candidate-episodes.jsonl",
    "provenance-index.csv",
    "reports/contextual-privacy-audit.json",
    "reports/corpus-profile.md",
    "reports/retrieval-audit.json",
    "review/README.md",
    "review/index.html",
    "review-corpus.jsonl",
    "source-index.jsonl",
}


def canonical_nonnegative_counts(value: Any, fields: set[str], label: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != fields:
        raise SystemExit(f"{label} has an unexpected aggregate schema")
    if any(isinstance(count, bool) or not isinstance(count, int) or count < 0 for count in value.values()):
        raise SystemExit(f"{label} contains an invalid aggregate count")
    return {name: int(value[name]) for name in sorted(fields)}


def sanitize_contextual_privacy_audit(value: Any) -> dict[str, Any]:
    """Retain only fixed-schema counts/digests; never copy legacy prose wholesale."""

    if not isinstance(value, dict) or value.get("kind") != (
        "naturalistic_corpus_contextual_privacy_audit"
    ):
        raise SystemExit("legacy contextual privacy audit has an invalid kind")
    audit_date = value.get("audit_date")
    try:
        date.fromisoformat(str(audit_date))
    except ValueError as exc:
        raise SystemExit("legacy contextual privacy audit has an invalid date") from exc
    sample = value.get("sample")
    if not isinstance(sample, dict):
        raise SystemExit("legacy contextual privacy audit lacks a fixed sample record")
    size = sample.get("size")
    digest = sample.get("sorted_id_manifest_sha256")
    if (
        isinstance(size, bool)
        or not isinstance(size, int)
        or size < 1
        or not isinstance(digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", digest)
    ):
        raise SystemExit("legacy contextual privacy audit sample record is invalid")
    authentication = value.get("authentication_material")
    if not isinstance(authentication, dict) or not isinstance(
        authentication.get("high_confidence_live_secret_found"), bool
    ):
        raise SystemExit("legacy contextual privacy audit authentication record is invalid")
    return {
        "schema_version": 1,
        "kind": "naturalistic_corpus_contextual_privacy_audit",
        "audit_date": str(audit_date),
        "sample": {
            "size": size,
            "composition": canonical_nonnegative_counts(
                sample.get("composition"),
                V1_CONTEXT_COMPOSITION_FIELDS,
                "legacy contextual sample composition",
            ),
            "sorted_id_manifest_sha256": digest,
        },
        "overlapping_risk_counts": canonical_nonnegative_counts(
            value.get("overlapping_risk_counts"),
            V1_CONTEXT_RISK_FIELDS,
            "legacy contextual risk counts",
        ),
        "disposition": canonical_nonnegative_counts(
            value.get("disposition"),
            V1_CONTEXT_DISPOSITION_FIELDS,
            "legacy contextual disposition",
        ),
        "authentication_material": {
            "high_confidence_live_secret_found": authentication[
                "high_confidence_live_secret_found"
            ]
        },
    }


def legacy_before_snapshot(legacy_dir: Path | None) -> dict[str, Any]:
    if legacy_dir is None:
        return {"available": False}
    root = require_role_leaf(legacy_dir, DISCOVERY_ROOT, "--legacy-before-dir")
    if not root.is_dir():
        raise SystemExit(f"legacy before-state directory does not exist: {root}")
    assert_regular_tree(root, "legacy before-state corpus")
    inventory = file_inventory(root)
    if {row["relative_path"] for row in inventory} != V1_ALLOWED_FILES:
        raise SystemExit("legacy before-state corpus contains unexpected or missing files")
    manifest_path = root / "corpus-manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        value = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(value, dict):
            manifest = value
    renderer: dict[str, Any] = {}
    html_path = root / "review" / "index.html"
    if html_path.is_file():
        html = html_path.read_text(encoding="utf-8", errors="replace")
        renderer = {
            "opening_script_tags": len(re.findall(r"<script\b", html, re.I)),
            "closing_script_tags": len(re.findall(r"</script\s*>", html, re.I)),
            "external_resource_like_attributes": len(
                re.findall(r"\b(?:src|href)\s*=\s*[\\\"']*https?://", html, re.I)
            ),
            "browser_storage_markers": len(re.findall(r"\b(?:localStorage|sessionStorage)\b", html)),
        }
    contextual_path = root / "reports" / "contextual-privacy-audit.json"
    contextual: dict[str, Any] | None = None
    if contextual_path.is_file():
        loaded = json.loads(contextual_path.read_text(encoding="utf-8"))
        contextual = sanitize_contextual_privacy_audit(loaded)
    return {
        "available": True,
        "schema_version": manifest.get("schema_version"),
        "kind": manifest.get("kind"),
        "session_count": manifest.get("session_count"),
        "candidate_count": manifest.get("candidate_count"),
        "review_corpus_count": manifest.get("review_corpus_count"),
        "file_inventory": inventory,
        "duplicate_groups": duplicate_groups(inventory),
        "renderer_structure": renderer,
        "contextual_privacy_audit": contextual,
    }


def write_profile(
    path: Path,
    sessions: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    start: date,
    end: date,
) -> None:
    session_sources = Counter(row["source"] for row in sessions)
    session_modes = Counter((row["source"], row["session_mode"]) for row in sessions)
    candidate_classes = Counter(
        (row["source"], row["candidate_class"]) for row in candidates
    )
    phenomena = Counter(row["primary_phenomenon"] for row in candidates)
    redactions: Counter[str] = Counter()
    for row in selected:
        redactions.update(
            {name: int(count) for name, count in (row.get("redaction_counts") or {}).items()}
        )
    reconstructions = Counter(row["reconstruction_status"] for row in selected)
    lines = [
        "# Private Naturalistic Pragmatic Extremes Corpus Profile",
        "",
        "This report describes a deterministic private retrieval queue. Candidate counts are",
        "not failure rates, success rates, prevalence estimates, or vendor comparisons.",
        "",
        f"- Sampling window: {start.isoformat()} through {end.isoformat()}",
        f"- Included primary sessions: {len(sessions)}",
        f"- All retrieval candidates: {len(candidates)}",
        f"- Stratified review corpus: {len(selected)}",
        "",
        "## Included sessions by source",
        "",
    ]
    lines.extend(f"- {source}: {count}" for source, count in sorted(session_sources.items()))
    lines.extend(["", "## Included sessions by source mode", ""])
    lines.extend(
        f"- {source} / {mode}: {count}"
        for (source, mode), count in sorted(session_modes.items())
    )
    lines.extend(["", "## Candidates by source and retrieval class", ""])
    lines.extend(
        f"- {source} / {candidate_class}: {count}"
        for (source, candidate_class), count in sorted(candidate_classes.items())
    )
    lines.extend(["", "## Provisional phenomenon profile", ""])
    lines.extend(f"- {name}: {count}" for name, count in phenomena.most_common())
    lines.extend(["", "## Privacy minimization", ""])
    lines.extend(f"- redaction `{name}`: {count}" for name, count in redactions.most_common())
    lines.extend(
        f"- reconstruction status `{name}`: {count}"
        for name, count in sorted(reconstructions.items())
    )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A repair turn records the user's subsequent stance, not a uniquely correct",
            "interpretation. A positive follow-up is evidence of uptake, not proof that success",
            "was unlikely. Manual review and controlled reconstruction are required before any",
            "candidate informs a public artifact. This corpus is privacy-minimized and",
            "pseudonymized, not anonymized or public-safe; public cases require new controlled",
            "reconstructions.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-root", type=Path)
    parser.add_argument("--claude-root", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--restricted-dir", required=True, type=Path)
    parser.add_argument(
        "--legacy-before-dir",
        type=Path,
        help="optional v1 directory to inventory in the aggregate privatization audit",
    )
    parser.add_argument("--start-date", type=date.fromisoformat, default=DEFAULT_START)
    parser.add_argument("--end-date", type=date.fromisoformat, default=DEFAULT_END)
    parser.add_argument("--max-chars", type=int, default=5000)
    parser.add_argument("--max-per-session", type=int, default=3)
    parser.add_argument("--review-limit", type=int, default=300)
    parser.add_argument("--session-limit", type=int, default=0)
    parser.add_argument("--session-limit-per-source", type=int, default=0)
    parser.add_argument(
        "--minimum-source-age-minutes",
        type=int,
        default=60,
        help=(
            "exclude source files modified more recently than this many minutes; "
            "use 0 only for immutable fixtures"
        ),
    )
    parser.add_argument(
        "--include-codex-exec",
        action="store_true",
        help="include headless Codex exec sessions as a separate source mode",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    os.umask(0o077)
    args = parse_args()
    if not args.codex_root and not args.claude_root:
        raise SystemExit("provide --codex-root and/or --claude-root")
    if args.start_date > args.end_date:
        raise SystemExit("--start-date must not follow --end-date")
    if (
        args.max_chars < 500
        or args.max_per_session < 1
        or args.review_limit < 1
        or args.minimum_source_age_minutes < 0
    ):
        raise SystemExit("invalid corpus size or truncation option")
    out_dir = require_role_leaf(args.out_dir, DISCOVERY_ROOT, "--out-dir")
    restricted_dir = require_role_leaf(
        args.restricted_dir, RESTRICTED_ROOT, "--restricted-dir"
    )
    if out_dir.exists() and any(out_dir.iterdir()):
        if not args.overwrite:
            raise SystemExit(f"output directory exists: {out_dir}; pass --overwrite")
        assert_owned_output_tree(out_dir)
        shutil.rmtree(out_dir)
    secure_directory(out_dir)
    secure_directory(out_dir / "reports")
    assert_restricted_tree_owned(restricted_dir)
    secure_directory(restricted_dir)
    for name in ("source-linkage.csv", "source-fingerprints.csv"):
        path = restricted_dir / name
        if path.exists() and not args.overwrite:
            raise SystemExit(f"restricted output exists: {path}; pass --overwrite")
        if path.exists():
            if not stat.S_ISREG(path.lstat().st_mode):
                raise SystemExit("restricted output is not a regular file")
            path.unlink()
    id_key = load_or_create_id_key(restricted_dir)

    discovered: list[tuple[str, Path, dict[str, Any]]] = []
    exclusions: dict[str, Counter[str]] = {}
    modified_before = time.time() - (args.minimum_source_age_minutes * 60)
    for source, root in (("codex", args.codex_root), ("claude", args.claude_root)):
        if root is None:
            continue
        root = root.resolve()
        if not root.exists():
            raise SystemExit(f"{source} root does not exist: {root}")
        allowed_modes = None
        if source == "codex":
            allowed_modes = {"cli"}
            if args.include_codex_exec:
                allowed_modes.add("exec")
        elif source == "claude":
            allowed_modes = {"interactive"}
        paths, excluded = discover_paths(
            root,
            source,
            args.start_date,
            args.end_date,
            allowed_modes=allowed_modes,
            modified_before=modified_before,
        )
        if excluded.get("malformed_source"):
            raise SystemExit(
                f"{source} discovery found {excluded['malformed_source']} malformed "
                "source file(s); refusing a partial build"
            )
        if args.session_limit_per_source:
            paths = evenly_spaced(paths, args.session_limit_per_source)
        exclusions[source] = excluded
        discovered.extend((source, path, meta) for path, meta in paths)
    discovered.sort(key=lambda item: (item[2]["timestamp"], item[0], str(item[1])))
    if args.session_limit:
        discovered = discovered[: args.session_limit]

    session_rows: list[dict[str, Any]] = []
    parsed_sessions: list[Session] = []
    parsed_source_fingerprints: dict[str, tuple[str, int]] = {}
    candidates: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    for source, path, meta in discovered:
        parsed_hasher = hashlib.sha256()
        try:
            parser = parse_codex if source == "codex" else parse_claude
            session = parser(path, meta, args.max_chars, parsed_hasher)
        except Exception as exc:  # record the aggregate failure before refusing partial output
            parse_errors.append(
                {
                    "source": source,
                    "path_ref": hmac_ref(id_key, "PATH2", "parse-error", str(path), 20),
                    "error_type": type(exc).__name__,
                }
            )
            continue
        try:
            parsed_state = source_state(path)
            fingerprint_after_parse = stable_source_fingerprint(path)
        except (OSError, RuntimeError):
            parsed_state = (-1, -1)
            fingerprint_after_parse = ("", -1)
        if not discovery_snapshot_matches(
            meta, parsed_hasher.hexdigest(), parsed_state
        ):
            exclusions[source]["source_changed_between_discovery_and_parse"] += 1
            continue
        if parsed_hasher.hexdigest() != fingerprint_after_parse[0]:
            exclusions[source]["source_changed_during_parse"] += 1
            continue
        parsed_source_fingerprints[str(path)] = fingerprint_after_parse
        parsed_sessions.append(session)
        session_ref = "SES-" + opaque(source + "|" + session.session_id)
        session_rows.append(
            {
                "source": source,
                "session_mode": session.session_mode,
                "session_ref": session_ref,
                "session_timestamp": session.timestamp,
                "session_local_date": session.local_date,
                "project_ref": "PRJ-" + opaque(session.cwd or "unknown"),
                "software_version": session.version,
                "model": session.model,
                "distinct_cwds": session.distinct_cwds,
                "distinct_versions": session.distinct_versions,
                "distinct_models": session.distinct_models,
                "event_count": session.event_count,
                "turn_count": len(session.turns),
                "excluded_branch_records": session.excluded_branch_records,
                "raw_path": str(session.path),
            }
        )
        candidates.extend(candidates_for_session(session, args.max_chars))

    if parse_errors:
        raise SystemExit(
            f"strict source parsing failed for {len(parse_errors)} session file(s); "
            "refusing a partial corpus"
        )

    candidates.sort(
        key=lambda row: (
            str(row["feedback_timestamp"]),
            str(row["source"]),
            str(row["candidate_id"]),
        )
    )
    selected = select_review_corpus(candidates, args.max_per_session, args.review_limit)
    selected_old_ids = {str(row["candidate_id"]) for row in selected}
    sensitive_literals = sensitive_literals_from_sessions(parsed_sessions)
    candidate_index: list[dict[str, Any]] = []
    review_by_old_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        old_id = str(candidate["candidate_id"])
        if old_id in selected_old_ids:
            index_row, review_row = minimized_review_row(candidate, id_key, sensitive_literals)
            review_by_old_id[old_id] = review_row
        else:
            index_row = base_index_row(candidate, id_key, review_selected=False)
        candidate_index.append(index_row)
    review_rows = [review_by_old_id[str(row["candidate_id"])] for row in selected]
    linkage_rows = [linkage_row(candidate, id_key) for candidate in candidates]

    fingerprint_rows: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    for candidate in candidates:
        _, _, source_ref = candidate_refs(candidate, id_key)
        if source_ref in seen_sources:
            continue
        seen_sources.add(source_ref)
        raw_path = Path(str(candidate["_provenance"]["raw_path"]))
        try:
            source_digest, source_size = stable_source_fingerprint(raw_path)
        except (OSError, RuntimeError) as exc:
            raise SystemExit(
                "a candidate-bearing source changed during final fingerprinting; "
                "refusing an unstable corpus"
            ) from exc
        if parsed_source_fingerprints.get(str(raw_path)) != (source_digest, source_size):
            raise SystemExit(
                "a candidate-bearing source changed after parsing; refusing a corpus "
                "whose final fingerprint differs from the exact parsed bytes"
            )
        fingerprint_rows.append(
            {
                "source_ref": source_ref,
                "source": candidate["source"],
                "raw_path": str(raw_path),
                "source_sha256": source_digest,
                "byte_size": source_size,
            }
        )

    write_jsonl(out_dir / "candidate-index.jsonl", candidate_index)
    write_jsonl(out_dir / "review-corpus.jsonl", review_rows)
    linkage_fields = [
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
    with (restricted_dir / "source-linkage.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=linkage_fields)
        writer.writeheader()
        writer.writerows(linkage_rows)
    fingerprint_fields = ["source_ref", "source", "raw_path", "source_sha256", "byte_size"]
    with (restricted_dir / "source-fingerprints.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fingerprint_fields)
        writer.writeheader()
        writer.writerows(sorted(fingerprint_rows, key=lambda row: str(row["source_ref"])))

    class_counts = Counter((row["source"], row["candidate_class"]) for row in candidates)
    signal_counts = Counter(
        item["signal"]
        for row in candidates
        for item in row["evidence_signals"] + row["pragmatic_load_signals"]
    )
    audit = {
        "adapter_version": ADAPTER_VERSION,
        "privacy_model_version": PRIVACY_MODEL_VERSION,
        "sampling_window": {
            "start": args.start_date.isoformat(),
            "end": args.end_date.isoformat(),
        },
        "sessions_discovered": len(discovered),
        "sessions_parsed": len(session_rows),
        "parse_errors": parse_errors,
        "exclusions": {source: dict(counter) for source, counter in exclusions.items()},
        "candidate_counts": {
            f"{source}/{candidate_class}": count
            for (source, candidate_class), count in sorted(class_counts.items())
        },
        "signal_counts": dict(signal_counts.most_common()),
        "review_corpus_count": len(review_rows),
        "max_per_session": args.max_per_session,
        "review_limit": args.review_limit,
        "minimum_source_age_minutes": args.minimum_source_age_minutes,
        "raw_episode_derivative_retained": False,
        "tool_output_text_retained": False,
        "direct_provenance_in_corpus": False,
        "external_api_calls": False,
        "interpretation": "candidate retrieval only; manual review required",
    }
    (out_dir / "reports" / "retrieval-audit.json").write_text(
        json.dumps(audit, indent=2) + "\n", encoding="utf-8"
    )
    write_profile(
        out_dir / "reports" / "corpus-profile.md",
        session_rows,
        candidate_index,
        review_rows,
        args.start_date,
        args.end_date,
    )
    residual = residual_risk_report(candidate_index, review_rows)
    (out_dir / "reports" / "residual-risk-audit.json").write_text(
        json.dumps(residual, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "schema_version": 2,
        "kind": "privacy_minimized_naturalistic_pragmatic_extremes_corpus",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "adapter_version": ADAPTER_VERSION,
        "privacy_model_version": PRIVACY_MODEL_VERSION,
        "sampling_window": {
            "start": args.start_date.isoformat(),
            "end": args.end_date.isoformat(),
        },
        "sources": [source for source, root in (("codex", args.codex_root), ("claude", args.claude_root)) if root],
        "session_count": len({row["session_ref"] for row in candidate_index}),
        "candidate_count": len(candidate_index),
        "review_corpus_count": len(review_rows),
        "candidate_classes": ["likely_pragmatic_failure", "surprising_success_candidate"],
        "restricted_linkage_separate": True,
        "raw_episode_derivative_retained": False,
        "claim_boundary": (
            "Privacy-minimized internal discovery corpus only; pseudonymized, not anonymous "
            "or public-safe; not gold labels, prevalence estimates, vendor comparisons, "
            "Study A observations, or publication-ready excerpts."
        ),
    }
    (out_dir / "corpus-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "README.md").write_text(
        "# Privacy-Minimized Naturalistic Pragmatic Extremes Corpus\n\n"
        "This ignored internal corpus contains keyed candidate pseudonyms, structured "
        "retrieval metadata, and aggressively minimized review excerpts. It contains no raw "
        "episode derivative or direct provenance. Exact source linkage is stored separately "
        "under the restricted private boundary and is never loaded by the reviewer.\n\n"
        "The corpus is pseudonymized, not anonymized or public-safe. Public cases require "
        "new benign controlled reconstructions.\n",
        encoding="utf-8",
    )
    before = legacy_before_snapshot(args.legacy_before_dir)
    withheld_counts = Counter(
        field_name for row in review_rows for field_name in row["content_withheld_fields"]
    )
    redaction_counts: Counter[str] = Counter()
    for row in review_rows:
        redaction_counts.update(
            {name: int(count) for name, count in row["redaction_counts"].items()}
        )
    privatization_audit = {
        "schema_version": 1,
        "kind": "naturalistic_corpus_privatization_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "before": before,
        "transformations": {
            "keyed_hmac_candidate_ids": len(candidate_index),
            "keyed_hmac_session_ids": len({row["session_ref"] for row in candidate_index}),
            "raw_episode_derivatives_retained": 0,
            "direct_provenance_rows_moved_to_restricted_vault": len(linkage_rows),
            "candidate_bearing_source_files_fingerprinted": len(fingerprint_rows),
            "tool_events_reduced_to_metadata": sum(row["tool_event_count"] for row in candidate_index),
            "redaction_counts": dict(redaction_counts.most_common()),
            "withheld_field_counts": dict(withheld_counts.most_common()),
            "manual_controlled_reconstruction_rows": sum(
                row["reconstruction_status"] == "manual_controlled_reconstruction_required"
                for row in review_rows
            ),
        },
        "after": {
            "corpus_file_inventory": file_inventory(
                out_dir, exclude={"reports/privatization-audit.json"}
            ),
            "restricted_file_inventory": file_inventory(restricted_dir),
            "duplicate_groups": duplicate_groups(
                file_inventory(out_dir, exclude={"reports/privatization-audit.json"})
            ),
            "residual_identifier_counts": residual["residual_identifier_counts"],
            "reviewer_finalized": False,
        },
        "claim_boundary": manifest["claim_boundary"],
    }
    (out_dir / "reports" / "privatization-audit.json").write_text(
        json.dumps(privatization_audit, indent=2) + "\n", encoding="utf-8"
    )
    for root in (out_dir, restricted_dir):
        assert_regular_tree(root, "generated private tree")
        os.chmod(root, 0o700, follow_symlinks=False)
        for path in root.rglob("*"):
            info = path.lstat()
            if stat.S_ISDIR(info.st_mode):
                os.chmod(path, 0o700, follow_symlinks=False)
            elif stat.S_ISREG(info.st_mode):
                os.chmod(path, 0o600, follow_symlinks=False)
    print(
        f"Built {len(candidate_index)} privacy-minimized candidates from "
        f"{len(session_rows)} primary sessions; selected {len(review_rows)} for internal review."
    )


if __name__ == "__main__":
    main()
