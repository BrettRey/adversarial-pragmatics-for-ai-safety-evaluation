#!/usr/bin/env python3
"""Exact identity contract for the deterministic Study A synthetic fixture."""

from __future__ import annotations

import hashlib
from typing import Any, Iterable, Mapping


STUDY_ID = "AP-STUDY-A-INDEPENDENT-READJUDICATION"
FIXTURE_KIND = "study_a_deterministic_synthetic_v1"
ROW_SALT = "synthetic-study-a-salt-v1"
ITEMS = tuple(f"SYN-{index:03d}" for index in range(1, 19))
MODELS = (
    "synthetic-system-a",
    "synthetic-system-b",
    "synthetic-system-c",
)
PAIR_PHENOMENA = (
    "embedded_command",
    "mention_use",
    "authority_hierarchy",
    "scope_negation",
    "deixis_reference_hijack",
    "indirect_speech_act",
    "agent_transcript_interpretation",
    "policy_boundary_ambiguity",
    "embedded_command",
)
EXPECTED_ROWS = len(ITEMS) * len(MODELS)


def reject() -> None:
    raise SystemExit(
        "synthetic mode is restricted to the deterministic Study A fixture"
    )


def validate_synthetic_fixture(
    metadata: Mapping[str, Any], map_rows: Iterable[Mapping[str, str]]
) -> None:
    """Require the exact deterministic map before allowing test-only bypasses."""
    rows = list(map_rows)
    expected_keys = {(item_id, model) for item_id in ITEMS for model in MODELS}
    if (
        metadata.get("synthetic_fixture_kind") != FIXTURE_KIND
        or metadata.get("study_id") != STUDY_ID
        or metadata.get("package_purpose") != "independent_rating"
        or metadata.get("row_salt") != ROW_SALT
        or len(rows) != EXPECTED_ROWS
        or {(row.get("item_id", ""), row.get("model", "")) for row in rows}
        != expected_keys
    ):
        reject()

    for row in rows:
        item_id = row["item_id"]
        model = row["model"]
        item_number = ITEMS.index(item_id) + 1
        model_number = MODELS.index(model) + 1
        source_index = (item_number - 1) * len(MODELS) + model_number
        pair_number = (item_number - 1) // 2 + 1
        expected_pair = "P008" if pair_number == 8 else f"SP{pair_number:02d}"
        expected_row_id = "R-" + hashlib.sha256(
            f"{ROW_SALT}|{item_id}|{model}|{source_index}".encode("utf-8")
        ).hexdigest()[:12].upper()
        if (
            row.get("source_record_index") != str(source_index)
            or row.get("row_id") != expected_row_id
            or row.get("pair_id") != expected_pair
            or row.get("phenomenon") != PAIR_PHENOMENA[pair_number - 1]
            or row.get("variant") != ("a" if item_number % 2 else "b")
        ):
            reject()
