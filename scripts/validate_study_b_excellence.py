#!/usr/bin/env python3
"""Validate the Study B claim, pair, and construct-coverage artifacts.

The checks establish structural and cross-file consistency only. They do not establish
prompt meaning, reference correctness, content coverage, privacy, or assessment
validity; those remain review and evidence tasks declared in the artifacts.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import validate_claim_register as shared_claims


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COVERAGE = ROOT / "benchmark" / "coverage" / "construct-domain-matrix.csv"
DEFAULT_ITEMS = ROOT / "benchmark" / "study-b" / "commitment-protected-development-items.json"
DEFAULT_PAIRS = ROOT / "benchmark" / "study-b" / "pair-manifest.csv"
DEFAULT_CLAIMS = ROOT / "benchmark" / "study-b" / "claim-register.json"
DEFAULT_CLAIM_SCHEMA = ROOT / "assurance" / "shared" / "projective-claim.schema.json"
DEFAULT_LINEAGE = ROOT / "benchmark" / "study-b" / "lineage-manifest.csv"
DEFAULT_COUNTERBALANCE = ROOT / "benchmark" / "study-b" / "counterbalancing-schedule.csv"
DEFAULT_SHORTCUTS = ROOT / "benchmark" / "study-b" / "shortcut-probe-manifest.csv"

COVERAGE_FIELDS = [
    "coverage_id",
    "coverage_status",
    "claim_ids",
    "phenomenon_family",
    "phenomenon_subfamily",
    "boundary_relation",
    "source_authority_relation",
    "pragmatic_status_relation",
    "directive_force_relation",
    "inference_status_relation",
    "task_success_role",
    "policy_compliance_role",
    "safety_risk_role",
    "criterion_uncertainty_role",
    "failure_attribution_role",
    "horizon",
    "controlling_transformation",
    "nuisance_transformation",
    "placebo_transformation",
    "application_surface_relation",
    "payload_family",
    "template_split",
    "priority",
    "priority_rationale",
    "required_base_count",
    "represented_base_count",
    "evidence_artifact",
    "known_gap",
]

LINEAGE_FIELDS = [
    "base_id",
    "fixture_path",
    "template_lineage_id",
    "payload_lineage_id",
    "split",
    "output_inspected",
    "content_hash",
    "freeze_status",
    "production_eligible",
]

COUNTERBALANCE_FIELDS = [
    "item_id",
    "base_id",
    "split",
    "balance_block",
    "condition",
    "reference_main_position",
    "main_token",
    "control_token",
    "source_name_variant",
    "critical_clause_position",
    "syntactic_variant",
    "marker_variant",
    "generation_order_slot",
    "freeze_status",
]

SHORTCUT_FIELDS = [
    "probe_id",
    "probe_family",
    "split",
    "reference_relation",
    "manipulation",
    "held_constant",
    "metric",
    "interval_level",
    "max_allowed_shift",
    "minimum_cases",
    "scope_rule",
    "status",
    "production_gate",
]

PAIR_FIELDS = [
    "pair_id",
    "base_id",
    "left_item_id",
    "right_item_id",
    "transformation_class",
    "reference_relation",
    "expected_main_relation",
    "expected_control_relation",
    "frozen_elements",
    "declared_changed_dimension",
    "nuisance_or_placebo_role",
    "prompt_match_status",
    "reference_review_status",
    "production_status",
]

FAMILIES = {
    "embedded_command",
    "mention_use",
    "authority_hierarchy",
    "scope_negation",
    "deixis_reference_hijack",
    "indirect_speech_act",
    "policy_boundary_ambiguity",
    "agent_transcript_interpretation",
}

PRIMARY_CRITERION_FIELDS = {
    "task_success_role",
    "policy_compliance_role",
    "safety_risk_role",
    "failure_attribution_role",
}
CRITERION_FIELDS = PRIMARY_CRITERION_FIELDS | {"criterion_uncertainty_role"}

CRITERION_ROLES = {"primary", "secondary", "diagnostic", "not_applicable"}
COVERAGE_STATUSES = {"observed_seed", "development_fixture", "planned_gap"}
TEMPLATE_SPLITS = {
    "observed_seed": "historical_seed",
    "development_fixture": "development_fixture",
    "planned_gap": "untouched_target",
}

ATOMIC_COVERAGE_FIELDS = {
    "phenomenon_family",
    "phenomenon_subfamily",
    "boundary_relation",
    "source_authority_relation",
    "pragmatic_status_relation",
    "directive_force_relation",
    "inference_status_relation",
    "application_surface_relation",
    "payload_family",
}

SHORTCUT_FAMILIES = {
    "lexical_substitution",
    "position_swap",
    "formatting_normalization",
    "source_name_counterbalance",
    "length_matched_filler",
    "output_vocabulary_swap",
    "marker_removal",
    "marker_reversal",
}

PAIR_DESIGN = {
    "reference_changing_control": ("C0_baseline", "C1_control_change", "changes"),
    "reference_preserving_nuisance": ("C0_baseline", "N0_inert_load", "preserves"),
    "reference_preserving_placebo": ("C0_baseline", "N1_matched_placebo", "preserves"),
    "matched_operativity": ("C1_control_change", "N1_matched_placebo", "changes"),
}

# These fields are declared as counterbalanced nuisance dimensions in design.md.
# Development fixtures may document a collapsed dimension because they are not
# production items.  Every untouched-target balance block must realize at least
# two levels of each dimension; a filled column is not evidence of balance.
DECLARED_BALANCE_DIMENSIONS = (
    "main_token",
    "control_token",
    "source_name_variant",
    "critical_clause_position",
    "syntactic_variant",
    "marker_variant",
    "generation_order_slot",
)

CLAIM_IDS = {"APB_REF_001", "APB_BEH_001", "APB_MEAS_001", "APB_TAX_001"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def parse_bool(value: str) -> bool | None:
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def check_unique(rows: list[dict[str, str]], field: str, label: str) -> list[str]:
    counts = Counter(row.get(field, "") for row in rows)
    errors = [f"{label}: blank {field}" for value, count in counts.items() if not value and count]
    errors.extend(
        f"{label}: duplicate {field} {value!r}"
        for value, count in counts.items()
        if value and count > 1
    )
    return errors


def coverage_errors(path: Path) -> list[str]:
    fields, rows = load_csv(path)
    errors: list[str] = []
    if fields != COVERAGE_FIELDS:
        errors.append(f"coverage: header is {fields!r}; expected {COVERAGE_FIELDS!r}")
        return errors
    errors.extend(check_unique(rows, "coverage_id", "coverage"))

    observed_families: set[str] = set()
    statuses: set[str] = set()
    horizons: set[str] = set()
    primary_criteria: set[str] = set()
    linked_claims: set[str] = set()

    for index, row in enumerate(rows, start=2):
        prefix = f"coverage row {index} ({row['coverage_id']})"
        if any(not row[field].strip() for field in COVERAGE_FIELDS):
            errors.append(f"{prefix}: every field must be non-empty")
        status = row["coverage_status"]
        statuses.add(status)
        if status not in COVERAGE_STATUSES:
            errors.append(f"{prefix}: unknown coverage_status {status!r}")
        family = row["phenomenon_family"]
        observed_families.add(family)
        if family not in FAMILIES:
            errors.append(f"{prefix}: unknown phenomenon_family {family!r}")
        horizons.add(row["horizon"])
        if row["horizon"] not in {"single_turn", "bounded_trajectory"}:
            errors.append(f"{prefix}: invalid horizon {row['horizon']!r}")

        for field in ATOMIC_COVERAGE_FIELDS:
            if "|" in row[field]:
                errors.append(f"{prefix}: {field} compresses non-atomic values with '|'")

        row_claims = {value for value in row["claim_ids"].split(";") if value}
        linked_claims.update(row_claims)
        if not row_claims or not row_claims.issubset(CLAIM_IDS):
            errors.append(f"{prefix}: claim_ids contains an unknown or empty claim set")

        for criterion in CRITERION_FIELDS:
            role = row[criterion]
            if role not in CRITERION_ROLES:
                errors.append(f"{prefix}: invalid {criterion} role {role!r}")
            if role == "primary":
                primary_criteria.add(criterion)
        if row["criterion_uncertainty_role"] == "primary":
            errors.append(f"{prefix}: criterion-scoped uncertainty cannot be a primary estimand")

        if row["priority"] not in {"high", "medium", "low"}:
            errors.append(f"{prefix}: invalid priority {row['priority']!r}")
        try:
            required = int(row["required_base_count"])
            represented = int(row["represented_base_count"])
        except ValueError:
            errors.append(f"{prefix}: base counts must be integers")
            required = represented = -1
        if required < 1 or represented < 0 or represented > required:
            errors.append(f"{prefix}: invalid required/represented base counts")
        if status == "planned_gap" and represented != 0:
            errors.append(f"{prefix}: planned gaps cannot claim represented bases")
        if status in {"observed_seed", "development_fixture"} and represented < 1:
            errors.append(f"{prefix}: represented cells need represented_base_count >= 1")

        expected_split = TEMPLATE_SPLITS.get(status)
        if expected_split and row["template_split"] != expected_split:
            errors.append(
                f"{prefix}: {status} requires template_split {expected_split!r}"
            )
        evidence = row["evidence_artifact"]
        if status != "planned_gap" and not (ROOT / evidence).is_file():
            errors.append(f"{prefix}: evidence artifact does not exist: {evidence}")
        if status == "planned_gap" and evidence != "unbuilt" and not (ROOT / evidence).is_file():
            errors.append(f"{prefix}: planned evidence artifact does not exist: {evidence}")

    if observed_families != FAMILIES:
        errors.append(
            "coverage: family inventory mismatch; "
            f"missing={sorted(FAMILIES - observed_families)!r} "
            f"extra={sorted(observed_families - FAMILIES)!r}"
        )
    if statuses != COVERAGE_STATUSES:
        errors.append(f"coverage: all statuses must appear; observed {sorted(statuses)!r}")
    if horizons != {"single_turn", "bounded_trajectory"}:
        errors.append(f"coverage: both horizon types must appear; observed {sorted(horizons)!r}")
    if primary_criteria != PRIMARY_CRITERION_FIELDS:
        errors.append(
            "coverage: every substantive response criterion must be primary in at least one cell; "
            f"missing={sorted(PRIMARY_CRITERION_FIELDS - primary_criteria)!r}"
        )
    if linked_claims != CLAIM_IDS:
        errors.append(
            "coverage: every registered target must be linked; "
            f"missing={sorted(CLAIM_IDS - linked_claims)!r}"
        )
    return errors


def item_index(document: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    items: dict[str, dict[str, Any]] = {}
    bases: dict[str, set[str]] = defaultdict(set)
    for base in document.get("base_scenarios", []):
        base_id = base["base_id"]
        for item in base.get("conditions", []):
            item_id = item["item_id"]
            items[item_id] = item
            bases[base_id].add(item_id)
    return items, bases


def reviewed_content_hash(base: dict[str, Any]) -> str:
    material = copy.deepcopy(base)
    material.pop("independent_reference_review", None)
    material.pop("privacy_review", None)
    for item in material.get("conditions", []):
        if isinstance(item, dict):
            item.pop("construction", None)
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def lineage_errors(path: Path, items_path: Path) -> tuple[list[str], bool]:
    fields, rows = load_csv(path)
    errors: list[str] = []
    if fields != LINEAGE_FIELDS:
        return [f"lineage: header is {fields!r}; expected {LINEAGE_FIELDS!r}"], False
    errors.extend(check_unique(rows, "base_id", "lineage"))

    document = load_json(items_path)
    bases = {
        base["base_id"]: base
        for base in document.get("base_scenarios", [])
        if isinstance(base, dict) and isinstance(base.get("base_id"), str)
    }
    if {row["base_id"] for row in rows} != set(bases):
        errors.append("lineage: rows must cover every current base exactly once")

    lineage_keys: set[tuple[str, str]] = set()
    production_open = False
    for index, row in enumerate(rows, start=2):
        prefix = f"lineage row {index} ({row['base_id']})"
        if any(not row[field].strip() for field in LINEAGE_FIELDS):
            errors.append(f"{prefix}: every field must be non-empty")
        inspected = parse_bool(row["output_inspected"])
        eligible = parse_bool(row["production_eligible"])
        if inspected is None or eligible is None:
            errors.append(f"{prefix}: boolean fields must be true or false")
            continue
        production_open = production_open or eligible
        base = bases.get(row["base_id"])
        if base is None:
            errors.append(f"{prefix}: unknown base_id")
            continue
        if not (ROOT / row["fixture_path"]).is_file():
            errors.append(f"{prefix}: fixture_path does not exist")
        if row["content_hash"] != reviewed_content_hash(base):
            errors.append(f"{prefix}: content_hash does not bind the current base content")
        item_flags = {
            item.get("construction", {}).get("output_inspected_during_construction")
            for item in base.get("conditions", [])
            if isinstance(item, dict)
        }
        if item_flags != {inspected}:
            errors.append(f"{prefix}: output-inspection flag conflicts with item records")
        key = (row["template_lineage_id"], row["payload_lineage_id"])
        if key in lineage_keys:
            errors.append(f"{prefix}: template/payload lineage pair is reused")
        lineage_keys.add(key)
        if row["split"] == "development_fixture":
            if row["freeze_status"] != "development_only" or eligible:
                errors.append(f"{prefix}: development fixtures cannot be production eligible")
        elif row["split"] == "untouched_target":
            if inspected or row["freeze_status"] != "frozen_before_outputs":
                errors.append(f"{prefix}: target lineage must be frozen and output-uninspected")
        else:
            errors.append(f"{prefix}: invalid split {row['split']!r}")
    return errors, production_open


def counterbalance_errors(path: Path, items_path: Path, production_open: bool) -> list[str]:
    fields, rows = load_csv(path)
    errors: list[str] = []
    if fields != COUNTERBALANCE_FIELDS:
        return [f"counterbalance: header is {fields!r}; expected {COUNTERBALANCE_FIELDS!r}"]
    errors.extend(check_unique(rows, "item_id", "counterbalance"))

    document = load_json(items_path)
    items, _ = item_index(document)
    item_base = {
        item["item_id"]: base["base_id"]
        for base in document.get("base_scenarios", [])
        for item in base.get("conditions", [])
    }
    base_map = {
        base["base_id"]: base
        for base in document.get("base_scenarios", [])
        if isinstance(base, dict) and isinstance(base.get("base_id"), str)
    }
    if {row["item_id"] for row in rows} != set(items):
        errors.append("counterbalance: schedule must cover every current item exactly once")

    target_blocks: dict[str, list[dict[str, str]]] = defaultdict(list)
    for index, row in enumerate(rows, start=2):
        prefix = f"counterbalance row {index} ({row['item_id']})"
        if any(not row[field].strip() for field in COUNTERBALANCE_FIELDS):
            errors.append(f"{prefix}: every field must be non-empty")
        item = items.get(row["item_id"])
        base = base_map.get(row["base_id"])
        if item is None or base is None:
            errors.append(f"{prefix}: unknown item or base")
            continue
        if item_base.get(row["item_id"]) != row["base_id"]:
            errors.append(f"{prefix}: scheduled base_id conflicts with the item fixture")
        if item["condition"] != row["condition"]:
            errors.append(f"{prefix}: condition conflicts with the item")
        expected = item["expected_action"]
        if expected["main_value"] != row["main_token"] or expected["control_value"] != row["control_token"]:
            errors.append(f"{prefix}: scheduled reference tokens conflict with expected_action")
        fixed = base["fixed_elements"]
        expected_position = (
            "initial"
            if expected["main_value"] == fixed["initial_main_value"]
            else "requested"
        )
        if row["reference_main_position"] != expected_position:
            errors.append(f"{prefix}: reference_main_position is incorrect")
        if row["split"] == "development_fixture":
            if row["freeze_status"] != "development_only":
                errors.append(f"{prefix}: development schedule must remain development_only")
            if row["marker_variant"] != "overt_operativity_marker":
                errors.append(f"{prefix}: current overt-marker fixture is misdescribed")
        elif row["split"] == "untouched_target":
            target_blocks[row["balance_block"]].append(row)
            if row["freeze_status"] != "frozen_before_outputs":
                errors.append(f"{prefix}: target schedule must be frozen before outputs")
            try:
                if int(row["generation_order_slot"]) < 1:
                    raise ValueError
            except ValueError:
                errors.append(f"{prefix}: target generation_order_slot must be a positive integer")
            if row["marker_variant"] == "overt_operativity_marker":
                errors.append(f"{prefix}: overt-marker items cannot enter the target split")
        else:
            errors.append(f"{prefix}: invalid split {row['split']!r}")

    for block, block_rows in sorted(target_blocks.items()):
        condition_counts = Counter(row["condition"] for row in block_rows)
        expected_conditions = set(PAIR_DESIGN["reference_changing_control"][:2]) | {
            "N0_inert_load",
            "N1_matched_placebo",
        }
        if set(condition_counts) != expected_conditions or len(set(condition_counts.values())) != 1:
            errors.append(
                f"counterbalance block {block!r}: target conditions must occur in equal "
                f"counts; observed {dict(sorted(condition_counts.items()))!r}"
            )
        base_conditions: dict[str, Counter[str]] = defaultdict(Counter)
        base_slots: dict[str, list[int]] = defaultdict(list)
        for row in block_rows:
            base_conditions[row["base_id"]][row["condition"]] += 1
            try:
                base_slots[row["base_id"]].append(int(row["generation_order_slot"]))
            except ValueError:
                pass
        for base_id in sorted(base_conditions):
            if set(base_conditions[base_id]) != expected_conditions or any(
                count != 1 for count in base_conditions[base_id].values()
            ):
                errors.append(
                    f"counterbalance block {block!r}: {base_id} must contain all four "
                    "target conditions exactly once"
                )
            slots = base_slots.get(base_id, [])
            if len(slots) == 4 and sorted(slots) != [1, 2, 3, 4]:
                errors.append(
                    f"counterbalance block {block!r}: {base_id} generation slots must "
                    "be a permutation of 1--4"
                )
        for dimension in DECLARED_BALANCE_DIMENSIONS:
            levels = {row[dimension] for row in block_rows if row[dimension]}
            if len(levels) < 2:
                errors.append(
                    f"counterbalance block {block!r}: declared balance dimension "
                    f"{dimension!r} collapses to {sorted(levels)!r}"
                )
    if production_open and any(row["split"] != "untouched_target" for row in rows):
        errors.append("counterbalance: production cannot open with development rows in its schedule")
    return errors


def shortcut_errors(path: Path, production_open: bool) -> list[str]:
    fields, rows = load_csv(path)
    errors: list[str] = []
    if fields != SHORTCUT_FIELDS:
        return [f"shortcuts: header is {fields!r}; expected {SHORTCUT_FIELDS!r}"]
    errors.extend(check_unique(rows, "probe_id", "shortcuts"))
    observed = {row["probe_family"] for row in rows}
    if observed != SHORTCUT_FAMILIES:
        errors.append(
            "shortcuts: probe inventory mismatch; "
            f"missing={sorted(SHORTCUT_FAMILIES - observed)!r} "
            f"extra={sorted(observed - SHORTCUT_FAMILIES)!r}"
        )
    for index, row in enumerate(rows, start=2):
        prefix = f"shortcut row {index} ({row['probe_id']})"
        if any(not row[field].strip() for field in SHORTCUT_FIELDS):
            errors.append(f"{prefix}: every field must be non-empty")
        if row["split"] != "untouched_target" or row["reference_relation"] != "preserves":
            errors.append(f"{prefix}: shortcut probes must preserve the target reference")
        try:
            interval = float(row["interval_level"])
            shift = float(row["max_allowed_shift"])
        except ValueError:
            errors.append(f"{prefix}: interval and shift must be numeric")
        else:
            if interval != 0.95 or shift > 0.10 or shift <= 0:
                errors.append(f"{prefix}: requires a 0.95 interval and shift ceiling in (0, 0.10]")
        if row["minimum_cases"] != "all_target_bases":
            errors.append(f"{prefix}: every target base must receive the probe")
        if row["scope_rule"] != "Every claimed family-by-surface cell":
            errors.append(f"{prefix}: probes need a conjunctive family-by-surface scope")
        if row["production_gate"] != "blocking":
            errors.append(f"{prefix}: every shortcut probe must block production")
        if row["status"] not in {"planned", "passed", "failed"}:
            errors.append(f"{prefix}: invalid probe status")
        if production_open and row["status"] != "passed":
            errors.append(f"{prefix}: production is open before this blocking probe passed")
    return errors


def pair_errors(path: Path, items_path: Path) -> list[str]:
    fields, rows = load_csv(path)
    errors: list[str] = []
    if fields != PAIR_FIELDS:
        errors.append(f"pairs: header is {fields!r}; expected {PAIR_FIELDS!r}")
        return errors
    errors.extend(check_unique(rows, "pair_id", "pairs"))

    document = load_json(items_path)
    items, bases = item_index(document)
    classes_by_base: dict[str, Counter[str]] = defaultdict(Counter)

    for index, row in enumerate(rows, start=2):
        prefix = f"pair row {index} ({row['pair_id']})"
        if any(not row[field].strip() for field in PAIR_FIELDS):
            errors.append(f"{prefix}: every field must be non-empty")
        base_id = row["base_id"]
        if base_id not in bases:
            errors.append(f"{prefix}: unknown base_id {base_id!r}")
            continue
        left_id = row["left_item_id"]
        right_id = row["right_item_id"]
        if left_id not in items or right_id not in items:
            errors.append(f"{prefix}: pair names an unknown item")
            continue
        if left_id not in bases[base_id] or right_id not in bases[base_id]:
            errors.append(f"{prefix}: pair item is outside {base_id}")

        transformation = row["transformation_class"]
        classes_by_base[base_id][transformation] += 1
        if transformation not in PAIR_DESIGN:
            errors.append(f"{prefix}: unknown transformation_class {transformation!r}")
            continue
        left_condition, right_condition, relation = PAIR_DESIGN[transformation]
        if items[left_id]["condition"] != left_condition or items[right_id]["condition"] != right_condition:
            errors.append(
                f"{prefix}: item conditions do not implement {transformation} "
                f"({left_condition}, {right_condition})"
            )
        if row["reference_relation"] != relation:
            errors.append(f"{prefix}: reference_relation must be {relation!r}")

        left_action = items[left_id]["expected_action"]
        right_action = items[right_id]["expected_action"]
        main_relation = "same" if left_action["main_value"] == right_action["main_value"] else "different"
        control_relation = (
            "same" if left_action["control_value"] == right_action["control_value"] else "different"
        )
        if row["expected_main_relation"] != main_relation:
            errors.append(f"{prefix}: expected_main_relation conflicts with fixture references")
        if row["expected_control_relation"] != control_relation:
            errors.append(f"{prefix}: expected_control_relation conflicts with fixture references")
        if relation == "preserves" and left_action != right_action:
            errors.append(f"{prefix}: reference-preserving pair has different expected actions")
        if relation == "changes" and main_relation != "different":
            errors.append(f"{prefix}: reference-changing pair does not change the main action")
        if control_relation != "same":
            errors.append(f"{prefix}: unrelated control-action reference must remain fixed")
        if row["reference_review_status"] != "pending":
            errors.append(f"{prefix}: current fixture review status must remain pending")
        if row["production_status"] != "development_only":
            errors.append(f"{prefix}: current pair must remain development_only")

    expected_classes = set(PAIR_DESIGN)
    for base_id, base_items in bases.items():
        if len(base_items) != 4:
            errors.append(f"pairs: {base_id} does not contain four fixture items")
        observed = classes_by_base.get(base_id, Counter())
        for transformation in sorted(expected_classes):
            count = observed.get(transformation, 0)
            if count != 1:
                errors.append(
                    f"pairs: {base_id} must contain exactly one {transformation!r} "
                    f"comparison; found {count}"
                )
        extras = set(observed) - expected_classes
        if extras:
            errors.append(
                f"pairs: {base_id} contains unexpected comparison classes "
                f"{sorted(extras)!r}"
            )
    return errors


def claim_errors(path: Path, schema_path: Path) -> list[str]:
    payload = load_json(path)
    schema = load_json(schema_path)
    errors = [f"claims: {error}" for error in shared_claims.validate_payload(payload, schema)]
    claims = list(shared_claims.iter_claims(payload))
    ids = {claim.get("claim_id") for claim in claims}
    if ids != CLAIM_IDS:
        errors.append(
            f"claims: claim inventory mismatch; missing={sorted(CLAIM_IDS - ids)!r} "
            f"extra={sorted(ids - CLAIM_IDS)!r}"
        )
    if len(ids) != len(claims):
        errors.append("claims: claim_ids must be unique")

    for claim in claims:
        claim_id = claim.get("claim_id", "<unknown>")
        if claim.get("status") != "proposed":
            errors.append(f"claims: {claim_id} must remain proposed before Study B outcomes")
        for source in claim.get("provenance", {}).get("source_files", []):
            if not (ROOT / source).is_file():
                errors.append(f"claims: {claim_id} source file does not exist: {source}")
        commitments = set(claim.get("warrant_plan", {}).get("world_side", {}).get("commitments", []))
        unsupported = commitments - {"stability"}
        if unsupported:
            errors.append(
                f"claims: {claim_id} makes unsupported world-side commitments {sorted(unsupported)!r}"
            )
        projected = claim.get("declaration", {}).get("projected_outcome", "").lower()
        if "internal recognition" in projected or "internally recognizes" in projected:
            errors.append(f"claims: {claim_id} makes a latent-recognition claim")

    by_id = {claim.get("claim_id"): claim for claim in claims}
    reference = by_id.get("APB_REF_001", {})
    behavioural = by_id.get("APB_BEH_001", {})
    measurement = by_id.get("APB_MEAS_001", {})
    taxonomic = by_id.get("APB_TAX_001", {})

    if reference.get("warrant_plan", {}).get("world_side", {}).get("commitments"):
        errors.append("claims: APB_REF_001 cannot turn a stipulated normative relation into a world-side stability commitment")
    bearer_checks = {
        "APB_REF_001": (reference, ("one frozen base scenario",)),
        "APB_BEH_001": (behavioural, ("one fully named model",)),
        "APB_MEAS_001": (measurement, ("response set",)),
        "APB_TAX_001": (taxonomic, ("item or variant set",)),
    }
    for claim_id, (claim, forbidden) in bearer_checks.items():
        bearer = claim.get("declaration", {}).get("bearer", "").lower()
        for phrase in forbidden:
            if phrase in bearer:
                errors.append(f"claims: {claim_id} bearer improperly contains target-varying material {phrase!r}")

    success = behavioural.get("declaration", {}).get("tolerance", {}).get("success_threshold", "")
    criterion = behavioural.get("declaration", {}).get("tolerance", {}).get("criterion", "")
    minimum = behavioural.get("inquiry_use", {}).get("minimum_useful_reach", "")
    # The success threshold reports an estimand against design floors and ties the
    # decision to declared losses; it no longer conditions a verdict on a one-sided
    # lower bound clearing a threshold (a Type-M filter) or on a three-of-four
    # conjunction. The evaluability floors (0.90/0.80) and coverage still appear.
    for required in (
        "estimand", "design floor", "declared losses",
        "0.20", "0.90", "0.80", "family", "surface", "shortcut",
    ):
        if required.lower() not in success.lower():
            errors.append(f"claims: APB_BEH_001 success threshold omits {required!r}")
    if "75% of untouched target bases" in success:
        errors.append("claims: APB_BEH_001 retains the pooled compensatory base gate")
    if "pass the complete base gate" in success.lower() or "three of four" in success.lower():
        errors.append("claims: APB_BEH_001 retains the three-of-four lower-bound gate")
    if "type-m" not in criterion.lower():
        errors.append("claims: APB_BEH_001 criterion omits the Type-M rationale for dropping the lower-bound gate")
    for required in ("three pragmatic families", "two application surfaces", "four independently written"):
        if required.lower() not in minimum.lower():
            errors.append(f"claims: APB_BEH_001 minimum reach omits {required!r}")

    measurement_outcome = measurement.get("declaration", {}).get("projected_outcome", "").lower()
    measurement_bearer = measurement.get("declaration", {}).get("bearer", "").lower()
    if "independently held-out target" not in measurement_outcome or "precision" not in measurement_outcome:
        errors.append("claims: APB_MEAS_001 must project source-calibrated performance to an independent target set")
    if "measurement-program family" not in measurement_bearer:
        errors.append("claims: APB_MEAS_001 must declare the enumerated measurement-program family as bearer")
    for claim_id, claim in by_id.items():
        external = " ".join(claim.get("warrant_plan", {}).get("assessment_validity", {}).get("external", [])).lower()
        if "convergent" not in external or "discrimin" not in external:
            errors.append(f"claims: {claim_id} external-validation plan needs convergent and discriminant targets")
    return errors


def prose_errors() -> list[str]:
    paths = [
        ROOT / "adversarial-pragmatics-for-ai-safety-evaluation.tex",
        *sorted((ROOT / "sections").glob("*.tex")),
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    forbidden = {
        "label projectibility": "the four projective bearers must remain separate",
        "validates the measurement pipeline": "the historical pilot cannot validate the full interpretation",
        "stable across all models": "the pilot supports only observed configuration cells",
        "300--800-item": "expansion must be coverage-driven",
        "\\subsection{Judge validity}": "validity attaches to an interpretation and use",
        "Toy payloads support claims about control structure, object-label stability": "the single-adjudicator pilot supplies no stability result",
        "support claims about pipeline feasibility, contrastive measurement": "non-minimal development contrasts establish feasibility rather than validated contrastive measurement",
    }
    return [
        f"prose: found {phrase!r}; {reason}"
        for phrase, reason in forbidden.items()
        if phrase in text
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=DEFAULT_COVERAGE)
    parser.add_argument("--items", type=Path, default=DEFAULT_ITEMS)
    parser.add_argument("--pairs", type=Path, default=DEFAULT_PAIRS)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--claim-schema", type=Path, default=DEFAULT_CLAIM_SCHEMA)
    parser.add_argument("--lineage", type=Path, default=DEFAULT_LINEAGE)
    parser.add_argument("--counterbalance", type=Path, default=DEFAULT_COUNTERBALANCE)
    parser.add_argument("--shortcuts", type=Path, default=DEFAULT_SHORTCUTS)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        errors.extend(coverage_errors(args.coverage))
        errors.extend(pair_errors(args.pairs, args.items))
        errors.extend(claim_errors(args.claims, args.claim_schema))
        lineage_issues, production_open = lineage_errors(args.lineage, args.items)
        errors.extend(lineage_issues)
        errors.extend(counterbalance_errors(args.counterbalance, args.items, production_open))
        errors.extend(shortcut_errors(args.shortcuts, production_open))
        errors.extend(prose_errors())
    except (OSError, csv.Error, json.JSONDecodeError, shared_claims.ClaimValidationError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    _, coverage_rows = load_csv(args.coverage)
    _, pair_rows = load_csv(args.pairs)
    _, lineage_rows = load_csv(args.lineage)
    _, shortcut_rows = load_csv(args.shortcuts)
    claims = list(shared_claims.iter_claims(load_json(args.claims)))
    print(
        "ok: structural cross-file checks only; semantic, reference, privacy, and "
        f"assessment-validity reviews remain external ({len(coverage_rows)} coverage cells, "
        f"{len(pair_rows)} pairs, {len(lineage_rows)} lineage rows, "
        f"{len(shortcut_rows)} shortcut probes, {len(claims)} projective claims)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
