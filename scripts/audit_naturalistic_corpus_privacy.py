#!/usr/bin/env python3
"""Audit a private naturalistic corpus without disclosing matched content.

The report contains only aggregate counts, schema-safe field labels, opaque file
references, permissions, sizes, and cryptographic file hashes. It never records
source paths, filenames outside a fixed role vocabulary, matched values, excerpts,
or parser exception text.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import csv
import hashlib
import json
import math
import os
import re
import secrets
import stat
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator


AUDIT_SCHEMA_VERSION = 1
PATTERN_POLICY_VERSION = 2
REVIEW_FIELD_LIMIT = 1600
PRECEDING_FIELD_LIMIT = 900
EPISODE_TEXT_LIMIT = 7000
ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = ROOT / "private"

FINAL_CORPUS_FILES = {
    "README.md",
    "candidate-index.jsonl",
    "corpus-manifest.json",
    "reports/contextual-privacy-audit.json",
    "reports/corpus-profile.md",
    "reports/legacy-audit-derivative-aggregate-privacy-audit.json",
    "reports/legacy-v1-aggregate-privacy-audit.json",
    "reports/privatization-audit.json",
    "reports/residual-risk-audit.json",
    "reports/retrieval-audit.json",
    "review/README.md",
    "review/index.html",
    "review-corpus.jsonl",
}
FINAL_RESTRICTED_FILES = {
    "id-key.bin",
    "source-fingerprints.csv",
    "source-linkage.csv",
}


SAFE_FIELDS = {
    "adapter_version",
    "adjudicated_class",
    "alternative_explanation",
    "alternative_explanations",
    "assistant",
    "byte_size",
    "candidate_class",
    "candidate_count",
    "candidate_counts",
    "candidate_id",
    "candidate_score",
    "candidate_classes",
    "claim_boundary",
    "compaction_before",
    "compaction_summary",
    "content_withheld_fields",
    "decision",
    "end",
    "end_line",
    "error",
    "evidence_signals",
    "evidence_strength",
    "excluded_branch_records",
    "exclusions",
    "exported_at",
    "external_api_calls",
    "feedback_turn_index",
    "feedback_timestamp",
    "generated_at",
    "git_branch",
    "governing_context",
    "immediate_model_response",
    "interpretation",
    "kind",
    "max_per_session",
    "model",
    "month",
    "notes",
    "phenomenon",
    "preceding_context",
    "primary_phenomenon",
    "privacy_disposition",
    "privacy_flags",
    "privacy_model_version",
    "pragmatic_load_signals",
    "raw_path",
    "raw_text_local_only",
    "reconstruction_status",
    "redaction_counts",
    "restricted_linkage_separate",
    "review_corpus_count",
    "review_limit",
    "review_selected",
    "sampling_window",
    "schema_version",
    "session_count",
    "session_id",
    "session_local_date",
    "session_mode",
    "session_ref",
    "session_timestamp",
    "sessions_discovered",
    "sessions_parsed",
    "signal",
    "signal_counts",
    "source",
    "source_ref",
    "source_sha256",
    "sources",
    "start",
    "start_line",
    "text",
    "text_char_count",
    "tool_trace",
    "tool_action_classes",
    "tool_event_count",
    "success",
    "name",
    "permission_mode",
    "project_ref",
    "prompt_provenance",
    "software_version",
    "trigger_node_id",
    "trigger_turn_index",
    "triggering_request",
    "updated_at",
    "user",
    "user_followup",
    "value",
    "weight",
}


DIRECT_IDENTIFIER_RULES = (
    (
        "email_address",
        re.compile(r"(?i)(?<![A-Z0-9._%+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}(?![A-Z0-9._%+-])"),
    ),
    (
        "posix_home_path",
        re.compile(r"(?<![A-Za-z0-9:])/(?:Users|home)/[^\s\"'<>/]+(?:/[^\s\"'<>]*)?"),
    ),
    (
        "other_absolute_path",
        re.compile(r"(?<![A-Za-z0-9:])/(?:private|var|tmp|opt|etc)/[^\s\"'<>]+"),
    ),
    (
        "windows_user_path",
        re.compile(r"(?i)(?<![A-Z0-9])(?:[A-Z]:\\|\\\\)[^\r\n\"'<>]{3,}"),
    ),
    (
        "phone_number",
        re.compile(r"(?<![A-Za-z0-9])(?:\+?1[ .()-]*)?(?:\d{3}[ .()-]*)\d{3}[ .-]*\d{4}(?![A-Za-z0-9])"),
    ),
    (
        "probable_street_address",
        re.compile(
            r"(?i)\b\d{1,6}\s+[A-Z][A-Za-z0-9'’.-]*(?:\s+[A-Z][A-Za-z0-9'’.-]*){0,4}\s+"
            r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Drive|Dr|Lane|Ln|Court|Ct)\.?\b"
        ),
    ),
    ("canadian_postal_code", re.compile(r"(?i)\b[A-Z]\d[A-Z][ -]?\d[A-Z]\d\b")),
    (
        "ipv4_address",
        re.compile(
            r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\."
            r"(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])"
        ),
    ),
    ("url", re.compile(r"(?i)\bhttps?://[^\s\"'<>]+")),
    (
        "probable_multiword_name",
        re.compile(r"\b[A-Z][a-z'’-]{2,}\s+(?:[A-Z][a-z'’-]{1,}\s+)?[A-Z][a-z'’-]{2,}\b"),
    ),
)


HIGH_CONFIDENCE_SECRET_RULES = (
    (
        "private_key_material",
        re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY(?: BLOCK)?-----"),
    ),
    (
        "openai_or_anthropic_token",
        re.compile(r"\b(?:sk-(?:proj-|svcacct-)?|sk-ant-)[A-Za-z0-9_-]{20,}\b"),
    ),
    (
        "github_token",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    ),
    ("hugging_face_token", re.compile(r"\bhf_[A-Za-z0-9]{20,}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    (
        "slack_token",
        re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    ),
    (
        "jwt",
        re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
    ),
    (
        "bearer_credential",
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/-]{24,}={0,2}\b"),
    ),
    ("aws_access_identifier", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
)


ACTIVE_PRIMITIVE_RULES = (
    ("script_tag", re.compile(r"(?i)<\s*/?\s*script\b")),
    ("active_html_element", re.compile(r"(?i)<\s*(?:img|iframe|object|embed|link|base|form|svg|math)\b")),
    ("event_handler_attribute", re.compile(r"(?i)\bon[a-z]{3,}\s*=")),
    ("javascript_scheme", re.compile(r"(?i)\bjavascript\s*:")),
    ("html_data_scheme", re.compile(r"(?i)\bdata\s*:\s*text/html")),
    ("network_fetch_call", re.compile(r"(?i)\bfetch\s*\(")),
    ("xml_http_request", re.compile(r"\bXMLHttpRequest\b")),
    ("websocket_call", re.compile(r"\bWebSocket\s*\(")),
    ("event_source_call", re.compile(r"\bEventSource\s*\(")),
    ("beacon_call", re.compile(r"(?i)\b(?:navigator\s*\.\s*)?sendBeacon\s*\(")),
    ("worker_import", re.compile(r"\bimportScripts\s*\(")),
    ("meta_refresh", re.compile(r"(?i)<\s*meta\b[^>]*http-equiv\s*=\s*[\"']?refresh")),
)


CATEGORY_RULES = {
    "direct_identifiers": DIRECT_IDENTIFIER_RULES,
    "high_confidence_secrets": HIGH_CONFIDENCE_SECRET_RULES,
    "active_markup_network_primitives": ACTIVE_PRIMITIVE_RULES,
}


CREDENTIAL_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(?:api[_ -]?key|client[_ -]?secret|access[_ -]?token|auth[_ -]?token|password|passwd)"
    r"\s*[:=]\s*[\"']?([A-Za-z0-9_./+=-]{24,})"
)
PLACEHOLDER_TERMS = (
    "example",
    "placeholder",
    "dummy",
    "synthetic",
    "redacted",
    "not-a-real",
    "replace-me",
    "your-key",
    "test-token",
)


ROLE_BY_RELATIVE_PATH = {
    "corpus-manifest.json": "corpus_manifest",
    "candidate-index.jsonl": "candidate_index",
    "all-candidates.jsonl": "all_candidates",
    "review-corpus.jsonl": "review_corpus",
    "provenance-index.csv": "provenance_index",
    "review/index.html": "reviewer_html",
    "review/README.md": "reviewer_readme",
    "reports/corpus-profile.md": "corpus_profile",
    "reports/retrieval-audit.json": "retrieval_audit",
    "reports/privatization-audit.json": "privatization_audit",
    "reports/residual-risk-audit.json": "residual_risk_audit",
    "README.md": "corpus_readme",
    "id-key.bin": "restricted_id_key",
    "source-linkage.csv": "source_linkage",
    "source-fingerprints.csv": "source_fingerprints",
}


RECORD_ROLES = {
    "candidate_index",
    "all_candidates",
    "review_corpus",
    "provenance_index",
    "source_linkage",
    "source_fingerprints",
    "renderer_payload",
}


EXTERNAL_ATTRIBUTES = {
    ("a", "href"),
    ("audio", "src"),
    ("base", "href"),
    ("button", "formaction"),
    ("embed", "src"),
    ("form", "action"),
    ("iframe", "src"),
    ("img", "src"),
    ("input", "formaction"),
    ("link", "href"),
    ("object", "data"),
    ("script", "src"),
    ("source", "src"),
    ("video", "poster"),
}


SAFE_CSP_DIRECTIVES = {
    "base-uri",
    "child-src",
    "connect-src",
    "default-src",
    "font-src",
    "form-action",
    "frame-ancestors",
    "frame-src",
    "img-src",
    "manifest-src",
    "media-src",
    "object-src",
    "script-src",
    "script-src-attr",
    "script-src-elem",
    "style-src",
    "style-src-attr",
    "style-src-elem",
    "worker-src",
}


def safe_field_name(name: Any) -> str:
    value = str(name)
    return value if value in SAFE_FIELDS else "other_field"


def field_path(parts: tuple[str, ...]) -> str:
    return ".".join(parts) if parts else "document_text"


def walk_strings(value: Any, path: tuple[str, ...] = ()) -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield field_path(path), value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from walk_strings(child, path + (safe_field_name(key),))
    elif isinstance(value, list):
        list_path = path
        if path:
            list_path = path[:-1] + (path[-1] + "[]",)
        for child in value:
            yield from walk_strings(child, list_path)


def token_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    length = len(value)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def credential_assignment_count(text: str) -> int:
    count = 0
    for match in CREDENTIAL_ASSIGNMENT_RE.finditer(text):
        token = match.group(1)
        lowered = token.lower()
        if any(term in lowered for term in PLACEHOLDER_TERMS):
            continue
        if len(set(token)) < 8 or token_entropy(token) < 3.5:
            continue
        count += 1
    return count


@dataclass
class FindingAccumulator:
    totals: dict[str, Counter[str]] = field(
        default_factory=lambda: {category: Counter() for category in CATEGORY_RULES}
    )
    by_pattern: dict[str, Counter[str]] = field(
        default_factory=lambda: {category: Counter() for category in CATEGORY_RULES}
    )
    by_field: dict[str, dict[str, Counter[str]]] = field(
        default_factory=lambda: {
            category: defaultdict(Counter) for category in CATEGORY_RULES
        }
    )

    def scan(
        self,
        text: str,
        field_name: str,
        categories: Iterable[str] | None = None,
    ) -> None:
        selected = tuple(categories) if categories is not None else tuple(CATEGORY_RULES)
        for category in selected:
            match_count = 0
            for pattern_name, pattern in CATEGORY_RULES[category]:
                count = sum(1 for _ in pattern.finditer(text))
                if count:
                    self.by_pattern[category][pattern_name] += count
                    match_count += count
            if category == "high_confidence_secrets":
                count = credential_assignment_count(text)
                if count:
                    self.by_pattern[category]["credential_assignment"] += count
                    match_count += count
            if match_count:
                self.totals[category]["match_count"] += match_count
                self.totals[category]["affected_values"] += 1
                self.by_field[category][field_name]["match_count"] += match_count
                self.by_field[category][field_name]["affected_values"] += 1

    def merge(self, other: "FindingAccumulator") -> None:
        for category in CATEGORY_RULES:
            self.totals[category].update(other.totals[category])
            self.by_pattern[category].update(other.by_pattern[category])
            for name, counts in other.by_field[category].items():
                self.by_field[category][name].update(counts)

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for category in CATEGORY_RULES:
            result[category] = {
                "match_count": self.totals[category]["match_count"],
                "affected_value_count": self.totals[category]["affected_values"],
                "by_pattern": dict(sorted(self.by_pattern[category].items())),
                "by_field": {
                    name: {
                        "match_count": counts["match_count"],
                        "affected_value_count": counts["affected_values"],
                    }
                    for name, counts in sorted(self.by_field[category].items())
                },
            }
        return result


@dataclass
class ContentMetrics:
    findings: FindingAccumulator = field(default_factory=FindingAccumulator)
    string_value_count: int = 0
    total_text_chars: int = 0
    max_text_chars: int = 0
    fields: dict[str, Counter[str]] = field(default_factory=lambda: defaultdict(Counter))
    input_record_count: int = 0
    parsed_record_count: int = 0
    parse_errors: Counter[str] = field(default_factory=Counter)
    caps: Counter[str] = field(default_factory=Counter)

    def scan_text(
        self,
        text: str,
        name: str,
        categories: Iterable[str] | None = None,
    ) -> None:
        self.string_value_count += 1
        self.total_text_chars += len(text)
        self.max_text_chars = max(self.max_text_chars, len(text))
        stats = self.fields[name]
        stats["value_count"] += 1
        stats["total_chars"] += len(text)
        stats["max_chars"] = max(stats["max_chars"], len(text))
        self.findings.scan(text, name, categories)

    def scan_value(self, value: Any) -> None:
        for name, text in walk_strings(value):
            self.scan_text(text, name)

    def observe_review_caps(self, record: dict[str, Any]) -> None:
        text_fields = (
            "triggering_request",
            "model_visible_response",
            "user_followup",
            "immediate_model_response",
        )
        total = 0
        for name in text_fields:
            value = record.get(name)
            if isinstance(value, str):
                total += len(value)
                if len(value) > REVIEW_FIELD_LIMIT:
                    self.caps["review_fields_over_limit"] += 1
        preceding = record.get("preceding_context")
        if isinstance(preceding, list):
            for pair in preceding:
                if not isinstance(pair, dict):
                    continue
                for name in ("user", "assistant"):
                    value = pair.get(name)
                    if isinstance(value, str):
                        total += len(value)
                        if len(value) > PRECEDING_FIELD_LIMIT:
                            self.caps["preceding_fields_over_limit"] += 1
        if total > EPISODE_TEXT_LIMIT:
            self.caps["episodes_over_total_limit"] += 1
        declared = record.get("text_char_count")
        if declared is not None and (isinstance(declared, bool) or not isinstance(declared, int) or declared != total):
            self.caps["declared_text_count_mismatches"] += 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "input_record_count": self.input_record_count,
            "parsed_record_count": self.parsed_record_count,
            "parse_error_count": sum(self.parse_errors.values()),
            "parse_errors_by_type": dict(sorted(self.parse_errors.items())),
            "string_value_count": self.string_value_count,
            "total_text_chars": self.total_text_chars,
            "max_text_chars": self.max_text_chars,
            "text_sizes_by_field": {
                name: {
                    "value_count": counts["value_count"],
                    "total_chars": counts["total_chars"],
                    "max_chars": counts["max_chars"],
                }
                for name, counts in sorted(self.fields.items())
            },
            "current_review_cap_findings": {
                "review_field_limit_chars": REVIEW_FIELD_LIMIT,
                "preceding_field_limit_chars": PRECEDING_FIELD_LIMIT,
                "episode_text_limit_chars": EPISODE_TEXT_LIMIT,
                **dict(sorted(self.caps.items())),
            },
            "findings": self.findings.as_dict(),
        }


class LinkageTracker:
    TRACKED_FIELDS = (
        "candidate_id",
        "session_ref",
        "source_ref",
        "raw_path",
        "session_id",
        "source_sha256",
    )

    def __init__(self) -> None:
        self.records: Counter[str] = Counter()
        self.values: dict[str, dict[str, Counter[str]]] = defaultdict(
            lambda: {name: Counter() for name in self.TRACKED_FIELDS}
        )

    def observe(self, role: str, record: Any) -> None:
        if role not in RECORD_ROLES or not isinstance(record, dict):
            return
        self.records[role] += 1
        for name in self.TRACKED_FIELDS:
            value = record.get(name)
            if value is None or value == "":
                continue
            self.values[role][name][str(value)] += 1

    def domain_summary(self, role: str) -> dict[str, Any]:
        fields: dict[str, Any] = {}
        for name in self.TRACKED_FIELDS:
            values = self.values[role][name]
            fields[name] = {
                "nonempty_count": sum(values.values()),
                "unique_count": len(values),
                "duplicate_value_count": sum(max(0, count - 1) for count in values.values()),
                "duplicate_distinct_count": sum(1 for count in values.values() if count > 1),
            }
        return {"record_count": self.records[role], "fields": fields}

    def comparison(self, left: str, right: str, name: str) -> dict[str, int]:
        left_values = set(self.values[left][name])
        right_values = set(self.values[right][name])
        return {
            "left_unique_count": len(left_values),
            "right_unique_count": len(right_values),
            "intersection_count": len(left_values & right_values),
            "left_only_count": len(left_values - right_values),
            "right_only_count": len(right_values - left_values),
        }

    def as_dict(self) -> dict[str, Any]:
        roles = sorted(RECORD_ROLES)
        comparisons = {
            "v2_candidate_index_to_source_linkage_candidate_id": self.comparison(
                "candidate_index", "source_linkage", "candidate_id"
            ),
            "v2_review_to_candidate_index_candidate_id": self.comparison(
                "review_corpus", "candidate_index", "candidate_id"
            ),
            "renderer_payload_to_review_candidate_id": self.comparison(
                "renderer_payload", "review_corpus", "candidate_id"
            ),
            "v2_source_linkage_to_fingerprint_source_ref": self.comparison(
                "source_linkage", "source_fingerprints", "source_ref"
            ),
            "v1_all_candidates_to_provenance_candidate_id": self.comparison(
                "all_candidates", "provenance_index", "candidate_id"
            ),
            "v1_review_to_all_candidates_candidate_id": self.comparison(
                "review_corpus", "all_candidates", "candidate_id"
            ),
        }
        return {
            "domains": {role: self.domain_summary(role) for role in roles},
            "coverage_comparisons": comparisons,
        }


class RendererParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.element_count = 0
        self.tag_counts: Counter[str] = Counter()
        self.script_nonces: list[str] = []
        self.style_nonce_count = 0
        self.external_attribute_count = 0
        self.event_handler_attribute_count = 0
        self.csp_values: list[str] = []
        self.candidate_template_count = 0
        self.encoded_payloads: list[str] = []
        self.script_texts: list[str] = []
        self._capture: str | None = None
        self._chunks: list[str] = []
        self._template_is_candidate = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {name.lower(): value or "" for name, value in attrs}
        self.element_count += 1
        self.tag_counts[tag] += 1
        for name, _value in attrs:
            lowered = name.lower()
            if lowered.startswith("on"):
                self.event_handler_attribute_count += 1
            if (tag, lowered) in EXTERNAL_ATTRIBUTES:
                self.external_attribute_count += 1
        if tag == "meta" and values.get("http-equiv", "").lower() == "content-security-policy":
            self.csp_values.append(values.get("content", ""))
        elif tag == "script":
            self.script_nonces.append(values.get("nonce", ""))
            self._capture = "script"
            self._chunks = []
        elif tag == "style":
            if values.get("nonce"):
                self.style_nonce_count += 1
        elif tag == "template":
            self._template_is_candidate = (
                values.get("id") == "candidate-data" and values.get("data-encoding") == "base64"
            )
            if self._template_is_candidate:
                self.candidate_template_count += 1
                self._capture = "template"
                self._chunks = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "script" and self._capture == "script":
            self.script_texts.append("".join(self._chunks))
            self._capture = None
            self._chunks = []
        elif tag == "template" and self._capture == "template":
            self.encoded_payloads.append("".join(self._chunks).strip())
            self._capture = None
            self._chunks = []
            self._template_is_candidate = False

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._chunks.append(data)


def renderer_metrics(
    document: str,
    content: ContentMetrics,
    linkage: LinkageTracker,
) -> dict[str, Any]:
    parser = RendererParser()
    try:
        parser.feed(document)
        parser.close()
    except Exception:
        content.parse_errors["html_parse_error"] += 1

    nonce_sources: set[str] = set()
    directive_counts: Counter[str] = Counter()
    none_directives: Counter[str] = Counter()
    for csp in parser.csp_values:
        for raw_directive in csp.split(";"):
            tokens = raw_directive.strip().split()
            if not tokens:
                continue
            raw_name = tokens[0].lower()
            name = raw_name if raw_name in SAFE_CSP_DIRECTIVES else "other-directive"
            if re.fullmatch(r"[a-z-]+", raw_name):
                directive_counts[name] += 1
                if tokens[1:] == ["'none'"]:
                    none_directives[name] += 1
            if raw_name == "script-src":
                for token in tokens[1:]:
                    match = re.fullmatch(r"'nonce-([^']+)'", token)
                    if match:
                        nonce_sources.add(match.group(1))

    for text in parser.script_texts:
        content.scan_text(
            text,
            "renderer_script_text",
            categories=("active_markup_network_primitives",),
        )

    decoded_payload_count = 0
    decoded_record_count = 0
    decoded_hashes: list[str] = []
    decode_error_count = 0
    for encoded in parser.encoded_payloads:
        try:
            raw = base64.b64decode(encoded, validate=True)
            decoded_hashes.append(hashlib.sha256(raw).hexdigest())
            value = json.loads(raw.decode("utf-8"))
        except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValueError):
            decode_error_count += 1
            continue
        decoded_payload_count += 1
        content.scan_value(value)
        records = value if isinstance(value, list) else [value]
        decoded_record_count += len(records)
        for record in records:
            linkage.observe("renderer_payload", record)

    authorized_script_count = sum(
        1 for value in parser.script_nonces if value and value in nonce_sources
    )
    return {
        "element_count": parser.element_count,
        "script_element_count": parser.tag_counts["script"],
        "style_element_count": parser.tag_counts["style"],
        "template_element_count": parser.tag_counts["template"],
        "candidate_data_template_count": parser.candidate_template_count,
        "script_nonce_attribute_count": sum(1 for value in parser.script_nonces if value),
        "style_nonce_attribute_count": parser.style_nonce_count,
        "csp_meta_count": len(parser.csp_values),
        "csp_directive_counts": dict(sorted(directive_counts.items())),
        "csp_none_directive_counts": dict(sorted(none_directives.items())),
        "csp_script_nonce_source_count": len(nonce_sources),
        "csp_authorized_script_count": authorized_script_count,
        "external_resource_attribute_count": parser.external_attribute_count,
        "event_handler_attribute_count": parser.event_handler_attribute_count,
        "script_closing_sequence_count": len(re.findall(r"(?i)</script\s*>", document)),
        "encoded_payload_count": len(parser.encoded_payloads),
        "decoded_payload_count": decoded_payload_count,
        "decoded_record_count": decoded_record_count,
        "payload_decode_error_count": decode_error_count,
        "decoded_payload_sha256": decoded_hashes,
    }


@dataclass(frozen=True)
class Node:
    root_label: str
    path: Path
    relative: Path
    is_symlink: bool
    is_directory_symlink: bool = False


def absolute_no_resolve(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def role_for(relative: Path, root_label: str, is_directory_symlink: bool = False) -> str:
    relative_name = relative.as_posix()
    if is_directory_symlink:
        return "symlink_directory"
    if relative_name in ROLE_BY_RELATIVE_PATH:
        return ROLE_BY_RELATIVE_PATH[relative_name]
    if relative_name.startswith("normalized-events/") and relative.suffix.lower() == ".jsonl":
        return "normalized_events"
    suffix = relative.suffix.lower()
    if suffix == ".jsonl":
        return "other_jsonl"
    if suffix == ".json":
        return "other_json"
    if suffix == ".csv":
        return "other_csv"
    if suffix in {".md", ".txt"}:
        return "other_text"
    if suffix in {".html", ".htm"}:
        return "other_html"
    if root_label == "restricted":
        return "other_restricted_file"
    return "other_file"


def discover_nodes(
    root: Path,
    root_label: str,
    excluded: set[Path],
) -> tuple[list[Node], dict[str, Any]]:
    nodes: list[Node] = []
    directory_modes: Counter[str] = Counter()
    directory_count = 0
    owner_only_directory_count = 0
    current_owner_directory_count = 0
    traversal_error_count = 0
    root_is_symlink = root.is_symlink()
    if root_is_symlink:
        return nodes, {
            "root_is_symlink": True,
            "directory_count": 0,
            "owner_only_directory_count": 0,
            "non_owner_only_directory_count": 0,
            "current_owner_directory_count": 0,
            "directory_modes": {},
            "directory_symlink_count": 1,
            "traversal_error_count": 0,
        }

    def onerror(_error: OSError) -> None:
        nonlocal traversal_error_count
        traversal_error_count += 1

    directory_symlink_count = 0
    for base, dirnames, filenames in os.walk(root, followlinks=False, onerror=onerror):
        base_path = Path(base)
        try:
            info = base_path.lstat()
            mode = stat.S_IMODE(info.st_mode)
            directory_modes[f"{mode:04o}"] += 1
            directory_count += 1
            if mode & 0o077 == 0:
                owner_only_directory_count += 1
            if info.st_uid == os.getuid():
                current_owner_directory_count += 1
        except OSError:
            traversal_error_count += 1

        retained_dirs: list[str] = []
        for name in sorted(dirnames):
            path = base_path / name
            if path.is_symlink():
                directory_symlink_count += 1
                nodes.append(
                    Node(root_label, path, path.relative_to(root), True, is_directory_symlink=True)
                )
            else:
                retained_dirs.append(name)
        dirnames[:] = retained_dirs
        for name in sorted(filenames):
            path = base_path / name
            if absolute_no_resolve(path) in excluded:
                continue
            nodes.append(Node(root_label, path, path.relative_to(root), path.is_symlink()))

    return nodes, {
        "root_is_symlink": False,
        "directory_count": directory_count,
        "owner_only_directory_count": owner_only_directory_count,
        "non_owner_only_directory_count": directory_count - owner_only_directory_count,
        "current_owner_directory_count": current_owner_directory_count,
        "directory_modes": dict(sorted(directory_modes.items())),
        "directory_symlink_count": directory_symlink_count,
        "traversal_error_count": traversal_error_count,
    }


def file_hash_and_lines(path: Path) -> tuple[str, int, int]:
    digest = hashlib.sha256()
    line_count = 0
    max_line_bytes = 0
    with path.open("rb") as handle:
        for line in handle:
            digest.update(line)
            line_count += 1
            max_line_bytes = max(max_line_bytes, len(line))
    return digest.hexdigest(), line_count, max_line_bytes


def probably_binary(path: Path, role: str) -> bool:
    if role == "restricted_id_key":
        return True
    try:
        with path.open("rb") as handle:
            sample = handle.read(8192)
    except OSError:
        return True
    return b"\x00" in sample


def scan_records(
    records: Iterable[Any],
    role: str,
    content: ContentMetrics,
    linkage: LinkageTracker,
) -> None:
    for record in records:
        content.input_record_count += 1
        content.parsed_record_count += 1
        content.scan_value(record)
        if role == "review_corpus" and isinstance(record, dict):
            content.observe_review_caps(record)
        linkage.observe(role, record)


def scan_jsonl(path: Path, role: str, content: ContentMetrics, linkage: LinkageTracker) -> None:
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                content.input_record_count += 1
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    content.parse_errors["json_decode_error"] += 1
                    content.scan_text(line, "unparsed_text")
                    continue
                content.parsed_record_count += 1
                content.scan_value(record)
                if role == "review_corpus" and isinstance(record, dict):
                    content.observe_review_caps(record)
                linkage.observe(role, record)
    except UnicodeDecodeError:
        content.parse_errors["unicode_decode_error"] += 1
    except OSError:
        content.parse_errors["io_error"] += 1


def scan_json(path: Path, role: str, content: ContentMetrics, linkage: LinkageTracker) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content.parse_errors["unicode_decode_error"] += 1
        return
    except OSError:
        content.parse_errors["io_error"] += 1
        return
    content.input_record_count += 1
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        content.parse_errors["json_decode_error"] += 1
        content.scan_text(text, "unparsed_text")
        return
    content.parsed_record_count += 1
    content.scan_value(value)
    linkage.observe(role, value)


def scan_csv(path: Path, role: str, content: ContentMetrics, linkage: LinkageTracker) -> None:
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                content.input_record_count += 1
                content.parsed_record_count += 1
                safe_row: dict[str, str] = {}
                for key, value in row.items():
                    safe_key = safe_field_name(key)
                    text = value or ""
                    content.scan_text(text, safe_key)
                    if key in LinkageTracker.TRACKED_FIELDS:
                        safe_row[key] = text
                linkage.observe(role, safe_row)
    except UnicodeDecodeError:
        content.parse_errors["unicode_decode_error"] += 1
    except (csv.Error, OSError):
        content.parse_errors["csv_or_io_error"] += 1


def scan_text_file(path: Path, content: ContentMetrics) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content.parse_errors["unicode_decode_error"] += 1
        return
    except OSError:
        content.parse_errors["io_error"] += 1
        return
    content.input_record_count += 1
    content.parsed_record_count += 1
    content.scan_text(text, "document_text")


def scan_html(
    path: Path,
    content: ContentMetrics,
    linkage: LinkageTracker,
) -> dict[str, Any]:
    try:
        document = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content.parse_errors["unicode_decode_error"] += 1
        return {}
    except OSError:
        content.parse_errors["io_error"] += 1
        return {}
    content.input_record_count += 1
    content.parsed_record_count += 1
    content.scan_text(
        document,
        "renderer_document",
        categories=("direct_identifiers", "high_confidence_secrets"),
    )
    return renderer_metrics(document, content, linkage)


def scan_file(
    node: Node,
    file_ref: str,
    linkage: LinkageTracker,
) -> tuple[dict[str, Any], FindingAccumulator, tuple[int, int] | None]:
    role = role_for(node.relative, node.root_label, node.is_directory_symlink)
    try:
        info = node.path.lstat()
    except OSError:
        return (
            {
                "file_ref": file_ref,
                "root": node.root_label,
                "role": role,
                "node_type": "unreadable",
                "is_symlink": node.is_symlink,
                "metadata_error_count": 1,
            },
            FindingAccumulator(),
            None,
        )
    mode = stat.S_IMODE(info.st_mode)
    base = {
        "file_ref": file_ref,
        "root": node.root_label,
        "role": role,
        "node_type": "symlink" if node.is_symlink else "regular_file",
        "is_symlink": node.is_symlink,
        "mode": f"{mode:04o}",
        "owner_only": mode & 0o077 == 0,
        "owned_by_current_user": info.st_uid == os.getuid(),
        "size_bytes": info.st_size,
    }
    if node.is_symlink:
        base.update(
            {
                "sha256": None,
                "line_count": 0,
                "max_line_bytes": 0,
                "content": ContentMetrics().as_dict(),
            }
        )
        return base, FindingAccumulator(), None

    try:
        digest, line_count, max_line_bytes = file_hash_and_lines(node.path)
    except OSError:
        base.update(
            {
                "sha256": None,
                "line_count": 0,
                "max_line_bytes": 0,
                "read_error_count": 1,
                "content": ContentMetrics().as_dict(),
            }
        )
        return base, FindingAccumulator(), (info.st_dev, info.st_ino)
    base.update(
        {
            "sha256": digest,
            "line_count": line_count,
            "max_line_bytes": max_line_bytes,
        }
    )
    content = ContentMetrics()
    renderer: dict[str, Any] | None = None
    if probably_binary(node.path, role):
        base["content_kind"] = "binary_not_content_scanned"
    elif role in {"reviewer_html", "other_html"}:
        base["content_kind"] = "html"
        renderer = scan_html(node.path, content, linkage)
    elif node.path.suffix.lower() == ".jsonl":
        base["content_kind"] = "jsonl"
        scan_jsonl(node.path, role, content, linkage)
    elif node.path.suffix.lower() == ".json":
        base["content_kind"] = "json"
        scan_json(node.path, role, content, linkage)
    elif node.path.suffix.lower() == ".csv":
        base["content_kind"] = "csv"
        scan_csv(node.path, role, content, linkage)
    elif node.path.suffix.lower() in {".md", ".txt"} or role.endswith("readme"):
        base["content_kind"] = "text"
        scan_text_file(node.path, content)
    else:
        base["content_kind"] = "unparsed_nonbinary"
    base["content"] = content.as_dict()
    if renderer is not None:
        base["renderer"] = renderer
    return base, content.findings, (info.st_dev, info.st_ino)


def detected_layout(roles: Counter[str]) -> str:
    has_v2 = bool(roles["candidate_index"] or roles["source_linkage"] or roles["source_fingerprints"])
    has_v1 = bool(roles["all_candidates"] or roles["provenance_index"] or roles["normalized_events"])
    if has_v1 and has_v2:
        return "mixed_v1_v2"
    if has_v2:
        return "v2_privacy_minimized"
    if has_v1:
        return "v1_raw_derivative"
    return "unrecognized_or_partial"


def build_audit(
    corpus_dir: Path,
    restricted_dir: Path | None = None,
    excluded_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    corpus = absolute_no_resolve(corpus_dir)
    restricted = absolute_no_resolve(restricted_dir) if restricted_dir else None
    if not corpus.exists() or not corpus.is_dir():
        raise ValueError("corpus directory is missing or is not a directory")
    if restricted is not None and (not restricted.exists() or not restricted.is_dir()):
        raise ValueError("restricted directory is missing or is not a directory")
    if restricted is not None and (
        corpus == restricted or corpus in restricted.parents or restricted in corpus.parents
    ):
        raise ValueError("corpus and restricted directories must be separate and non-nested")
    excluded = {absolute_no_resolve(path) for path in excluded_paths}

    roots = [("corpus", corpus)]
    if restricted is not None:
        roots.append(("restricted", restricted))
    all_nodes: list[Node] = []
    tree_security: dict[str, Any] = {}
    for label, root in roots:
        nodes, security = discover_nodes(root, label, excluded)
        all_nodes.extend(nodes)
        tree_security[label] = security
    all_nodes.sort(key=lambda node: (node.root_label, node.relative.as_posix()))

    linkage = LinkageTracker()
    aggregate_findings = FindingAccumulator()
    files: list[dict[str, Any]] = []
    hash_members: dict[str, list[str]] = defaultdict(list)
    inode_members: dict[tuple[int, int], list[str]] = defaultdict(list)
    roles: Counter[str] = Counter()
    renderer_aggregate: Counter[str] = Counter()
    root_sequence: Counter[str] = Counter()
    for node in all_nodes:
        root_sequence[node.root_label] += 1
        prefix = "C" if node.root_label == "corpus" else "R"
        file_ref = f"{prefix}{root_sequence[node.root_label]:06d}"
        report, findings, inode = scan_file(node, file_ref, linkage)
        files.append(report)
        roles[report["role"]] += 1
        aggregate_findings.merge(findings)
        digest = report.get("sha256")
        if isinstance(digest, str):
            hash_members[digest].append(file_ref)
        if inode is not None:
            inode_members[inode].append(file_ref)
        renderer = report.get("renderer")
        if isinstance(renderer, dict):
            for name in (
                "script_element_count",
                "style_element_count",
                "candidate_data_template_count",
                "script_nonce_attribute_count",
                "style_nonce_attribute_count",
                "csp_meta_count",
                "csp_authorized_script_count",
                "external_resource_attribute_count",
                "event_handler_attribute_count",
                "script_closing_sequence_count",
                "encoded_payload_count",
                "decoded_payload_count",
                "decoded_record_count",
                "payload_decode_error_count",
            ):
                renderer_aggregate[name] += int(renderer.get(name, 0))

    duplicate_hash_groups = [members for members in hash_members.values() if len(members) > 1]
    hardlink_groups = [members for members in inode_members.values() if len(members) > 1]
    regular_files = [row for row in files if row.get("node_type") == "regular_file"]
    symlinks = [row for row in files if row.get("is_symlink")]
    non_owner_only = [row for row in regular_files if not row.get("owner_only")]
    wrong_owner = [row for row in regular_files if not row.get("owned_by_current_user")]
    restricted_key_files = [row for row in files if row.get("role") == "restricted_id_key"]

    return {
        "schema_version": AUDIT_SCHEMA_VERSION,
        "kind": "aggregate_naturalistic_corpus_privacy_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_policy": {
            "pattern_policy_version": PATTERN_POLICY_VERSION,
            "content_disclosure": "aggregate_counts_only",
            "matched_values_or_excerpts_in_report": False,
            "input_paths_or_unrecognized_filenames_in_report": False,
            "symlinks_followed": False,
            "binary_content_scanned": False,
            "file_reference_scheme": "root-class plus deterministic ordinal",
            "direct_identifier_patterns": [name for name, _pattern in DIRECT_IDENTIFIER_RULES],
            "high_confidence_secret_patterns": [
                *(name for name, _pattern in HIGH_CONFIDENCE_SECRET_RULES),
                "credential_assignment",
            ],
            "active_primitive_patterns": [name for name, _pattern in ACTIVE_PRIMITIVE_RULES],
        },
        "detected_layout": detected_layout(roles),
        "tree_security": tree_security,
        "inventory": {
            "regular_file_count": len(regular_files),
            "symlink_count": len(symlinks),
            "owner_only_file_count": len(regular_files) - len(non_owner_only),
            "non_owner_only_file_count": len(non_owner_only),
            "current_owner_file_count": len(regular_files) - len(wrong_owner),
            "wrong_owner_file_count": len(wrong_owner),
            "total_regular_file_bytes": sum(int(row.get("size_bytes", 0)) for row in regular_files),
            "role_counts": dict(sorted(roles.items())),
            "restricted_key_file_count": len(restricted_key_files),
            "restricted_32_byte_key_file_count": sum(
                1 for row in restricted_key_files if row.get("size_bytes") == 32
            ),
        },
        "aggregate_findings": aggregate_findings.as_dict(),
        "renderer_structural_totals": dict(sorted(renderer_aggregate.items())),
        "provenance_and_linkage": linkage.as_dict(),
        "duplication": {
            "byte_identical_group_count": len(duplicate_hash_groups),
            "byte_identical_groups": duplicate_hash_groups,
            "hardlink_group_count": len(hardlink_groups),
            "hardlink_groups": hardlink_groups,
        },
        "files": files,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-dir", required=True, type=Path)
    parser.add_argument("--restricted-dir", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def private_output_path(output: Path) -> Path:
    destination = absolute_no_resolve(output)
    try:
        relative = destination.relative_to(PRIVATE_ROOT)
    except ValueError as exc:
        raise ValueError("audit output must remain under the repository private boundary") from exc
    current = PRIVATE_ROOT
    for part in relative.parts:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise ValueError("audit output path contains an unreadable component") from exc
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("audit output path must not traverse a symlink")
    if destination.suffix.lower() != ".json":
        raise ValueError("audit output must be a JSON file")
    return destination


def write_report(report: dict[str, Any], output: Path) -> None:
    destination = private_output_path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / (
        f".{destination.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}"
    )
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600, follow_symlinks=False)
        # Atomic replacement changes only the destination directory entry. It does
        # not truncate an existing hardlink target, and the earlier path check
        # rejects an existing symlink outright.
        os.replace(temporary, destination)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def finalized_inventory(
    root: Path,
    allowed: set[str],
    excluded: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Return the exact validator-compatible inventory without following symlinks."""

    omitted = excluded or set()
    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative in omitted or path.is_symlink() or not path.is_file():
            continue
        if relative not in allowed:
            raise ValueError("finalized tree contains an unrecognized filename")
        info = path.stat()
        digest, _line_count, _max_line_bytes = file_hash_and_lines(path)
        records.append(
            {
                "relative_path": relative,
                "sha256": digest,
                "byte_size": info.st_size,
                "mode": f"{stat.S_IMODE(info.st_mode):04o}",
            }
        )
    return records


def finalized_duplicate_groups(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for row in inventory:
        groups[str(row["sha256"])].append(str(row["relative_path"]))
    return [
        {"sha256": digest, "relative_paths": sorted(paths)}
        for digest, paths in sorted(groups.items())
        if len(paths) > 1
    ]


def read_existing_privatization_audit(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("existing output is not a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("existing output is unreadable or invalid JSON") from None
    if not isinstance(value, dict):
        raise ValueError("existing output must be a JSON object")
    if value.get("kind") == "naturalistic_corpus_privatization_audit":
        return value
    return None


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


def fixed_nonnegative_counts(value: Any, fields: set[str], label: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} has an unexpected schema")
    if any(isinstance(count, bool) or not isinstance(count, int) or count < 0 for count in value.values()):
        raise ValueError(f"{label} contains an invalid count")
    return {name: int(value[name]) for name in sorted(fields)}


def sanitized_legacy_context(value: Any) -> dict[str, Any]:
    """Drop all legacy prose and retain only a fixed aggregate schema."""

    if not isinstance(value, dict) or value.get("kind") != (
        "naturalistic_corpus_contextual_privacy_audit"
    ):
        raise ValueError("legacy contextual audit has an invalid kind")
    audit_date = value.get("audit_date")
    if not isinstance(audit_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", audit_date):
        raise ValueError("legacy contextual audit has an invalid date")
    sample = value.get("sample")
    authentication = value.get("authentication_material")
    if not isinstance(sample, dict) or not isinstance(authentication, dict):
        raise ValueError("legacy contextual audit lacks fixed aggregate sections")
    size = sample.get("size")
    digest = sample.get("sorted_id_manifest_sha256")
    secret_found = authentication.get("high_confidence_live_secret_found")
    if (
        isinstance(size, bool)
        or not isinstance(size, int)
        or size < 1
        or not isinstance(digest, str)
        or not re.fullmatch(r"[a-f0-9]{64}", digest)
        or not isinstance(secret_found, bool)
    ):
        raise ValueError("legacy contextual audit contains an invalid aggregate value")
    return {
        "schema_version": 1,
        "kind": "naturalistic_corpus_contextual_privacy_audit",
        "audit_date": audit_date,
        "sample": {
            "size": size,
            "composition": fixed_nonnegative_counts(
                sample.get("composition"),
                V1_CONTEXT_COMPOSITION_FIELDS,
                "legacy contextual sample composition",
            ),
            "sorted_id_manifest_sha256": digest,
        },
        "overlapping_risk_counts": fixed_nonnegative_counts(
            value.get("overlapping_risk_counts"),
            V1_CONTEXT_RISK_FIELDS,
            "legacy contextual risk counts",
        ),
        "disposition": fixed_nonnegative_counts(
            value.get("disposition"),
            V1_CONTEXT_DISPOSITION_FIELDS,
            "legacy contextual disposition",
        ),
        "authentication_material": {
            "high_confidence_live_secret_found": secret_found
        },
    }


def sanitize_existing_before(existing: dict[str, Any]) -> dict[str, Any]:
    before = existing.get("before")
    if not isinstance(before, dict):
        raise ValueError("existing privatization audit lacks a before object")
    contextual = before.get("contextual_privacy_audit")
    if contextual is None:
        return dict(before)
    safe_before = dict(before)
    safe_before["contextual_privacy_audit"] = sanitized_legacy_context(contextual)
    return safe_before


def finalize_privatization_audit(
    existing: dict[str, Any],
    aggregate_report: dict[str, Any],
    corpus_dir: Path,
    restricted_dir: Path,
) -> dict[str, Any]:
    """Finalize the builder's audit after the static reviewer has been generated."""

    after = existing.get("after")
    if not isinstance(after, dict):
        raise ValueError("existing privatization audit lacks an after object")
    corpus_inventory = finalized_inventory(
        corpus_dir,
        FINAL_CORPUS_FILES,
        excluded={"reports/privatization-audit.json"},
    )
    restricted_inventory = finalized_inventory(restricted_dir, FINAL_RESTRICTED_FILES)
    finalized = dict(existing)
    finalized["before"] = sanitize_existing_before(existing)
    finalized_after = dict(after)
    finalized_after.update(
        {
            "corpus_file_inventory": corpus_inventory,
            "restricted_file_inventory": restricted_inventory,
            "duplicate_groups": finalized_duplicate_groups(corpus_inventory),
            "reviewer_finalized": True,
            "aggregate_privacy_scan": aggregate_report,
        }
    )
    finalized["after"] = finalized_after
    finalized["finalized_at"] = datetime.now(timezone.utc).isoformat()
    return finalized


def main() -> None:
    os.umask(0o077)
    args = parse_args()
    excluded = [args.output] if args.output else []
    try:
        report = build_audit(args.corpus_dir, args.restricted_dir, excluded)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    audited_file_count = report["inventory"]["regular_file_count"]
    if args.output:
        try:
            destination = private_output_path(args.output)
            existing = read_existing_privatization_audit(destination)
            if destination.name == "privatization-audit.json" and existing is None:
                raise ValueError(
                    "privatization-audit.json must be created by the corpus builder before finalization"
                )
            if existing is not None:
                if args.restricted_dir is None:
                    raise ValueError(
                        "finalizing the privatization audit requires --restricted-dir"
                    )
                report = finalize_privatization_audit(
                    existing,
                    report,
                    absolute_no_resolve(args.corpus_dir),
                    absolute_no_resolve(args.restricted_dir),
                )
            write_report(report, destination)
        except ValueError as exc:
            raise SystemExit(str(exc)) from None
        print(
            f"Wrote aggregate-only privacy audit for {audited_file_count} files."
        )
    else:
        json.dump(report, os.sys.stdout, indent=2, sort_keys=True)
        os.sys.stdout.write("\n")


if __name__ == "__main__":
    main()
