#!/usr/bin/env python3
"""Validate adversarial-pragmatics benchmark item CSV files."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path


REQUIRED_COLUMNS = [
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
    "judge_validation_flag",
    "notes",
]

PHENOMENA = {
    "embedded_command",
    "mention_use",
    "authority_hierarchy",
    "scope_negation",
    "deixis_reference_hijack",
    "indirect_speech_act",
    "policy_boundary_ambiguity",
    "agent_transcript_interpretation",
}

SAFETY_RISK = {"low", "medium", "high", "not_applicable"}

RISK_TYPES = {
    "none",
    "confidentiality",
    "integrity",
    "tool_misuse",
    "policy_bypass",
    "evaluator_deception",
}

REFUSAL_OUTCOMES = {
    "not_applicable",
    "appropriate_policy_refusal",
    "over_refusal_probe",
    "under_refusal_probe",
    "policy_ambiguous_refusal",
    "incapability_possible",
    "safe_redirection",
}

AUTHORITY_LEVELS = {
    "trusted_user",
    "untrusted_content",
    "quoted_content",
    "policy_constraint",
    "ambiguous",
}

FAILURE_ATTRIBUTIONS = {
    "none",
    "instruction_conflict",
    "policy_ambiguity",
    "capability_failure",
    "safety_refusal",
    "tool_error",
    "scaffold_failure",
    "goal_drift",
    "misreporting",
    "grader_error",
    "taxonomy_instability",
}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            errors.append(f"columns differ from required schema: {reader.fieldnames!r}")
            return errors

        rows = list(reader)

    if not rows:
        return ["file contains no rows"]

    item_ids = Counter(row["item_id"] for row in rows)
    for item_id, count in item_ids.items():
        if count > 1:
            errors.append(f"duplicate item_id: {item_id}")

    pairs: dict[str, list[str]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        prefix = f"line {index} ({row['item_id']})"
        for column in REQUIRED_COLUMNS:
            if not row[column].strip():
                errors.append(f"{prefix}: empty {column}")
        if row["phenomenon"] not in PHENOMENA:
            errors.append(f"{prefix}: unknown phenomenon {row['phenomenon']!r}")
        if row["safety_risk_label"] not in SAFETY_RISK:
            errors.append(f"{prefix}: unknown safety_risk_label {row['safety_risk_label']!r}")
        if row["risk_type_label"] not in RISK_TYPES:
            errors.append(f"{prefix}: unknown risk_type_label {row['risk_type_label']!r}")
        if row["refusal_outcome_label"] not in REFUSAL_OUTCOMES:
            errors.append(
                f"{prefix}: unknown refusal_outcome_label {row['refusal_outcome_label']!r}"
            )
        if row["authority_level"] not in AUTHORITY_LEVELS:
            errors.append(f"{prefix}: unknown authority_level {row['authority_level']!r}")
        if row["failure_attribution_label"] not in FAILURE_ATTRIBUTIONS:
            errors.append(
                f"{prefix}: unknown failure_attribution_label {row['failure_attribution_label']!r}"
            )
        if row["judge_validation_flag"] not in {"true", "false"}:
            errors.append(
                f"{prefix}: judge_validation_flag must be 'true' or 'false', got {row['judge_validation_flag']!r}"
            )
        pairs[row["pair_id"]].append(row["item_id"])

    for pair_id, members in pairs.items():
        if len(members) < 2:
            errors.append(f"pair_id {pair_id} has fewer than 2 items")

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_items.py PATH", file=sys.stderr)
        return 2

    path = Path(argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"ok: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
