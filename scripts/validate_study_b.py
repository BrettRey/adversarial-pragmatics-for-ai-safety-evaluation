#!/usr/bin/env python3
"""Validate declared Study B structure and cross-condition invariants.

This validator checks machine-readable consistency. It cannot establish that prompt
prose has the intended semantics, that a reconstruction is private, or that a
minimal pair changes only the intended pragmatic fact; those require frozen human
review records before production eligibility.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised only in an incomplete environment
    Draft202012Validator = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ITEMS = ROOT / "benchmark" / "study-b" / "commitment-protected-development-items.json"
DEFAULT_SCHEMA = ROOT / "benchmark" / "study-b" / "schema.json"

CONDITIONS = {
    "C0_baseline": ("C0", "baseline", "valid_amendment", True),
    "C1_control_change": (
        "C1",
        "control_change",
        "operative_commitment_protection",
        True,
    ),
    "N0_inert_load": ("N0", "inert_load", "inert_load", False),
    "N1_matched_placebo": (
        "N1",
        "matched_placebo",
        "surface_matched_nonoperative_protection",
        False,
    ),
}

EXPECTED_FAMILIES = {
    "ordinary_unilateral_amendment",
    "joint_amendment",
    "expiry_release",
    "operative_ceremonial",
}

EXPECTED_GATE_STAGES = {
    "private_candidate",
    "abstract_card_eligibility",
    "reconstructability_privacy_pass",
    "pilot_survival",
    "production_inclusion",
}

TAG_PATTERN = re.compile(r"\[([a-z][a-z0-9_]*)\]")
PRIVATE_MARKERS = re.compile(
    r"(?:/Users/|\\Users\\|\bDownloads\b|https?://|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|"
    r"\b(?:NPE2|SES2|SRC2)-[A-Z0-9]+\b|\b(?:Brett|Humber|Claude|Codex)\b)",
    flags=re.IGNORECASE,
)

SPAN_SEMANTICS = {
    "mandate": ("governing_rule", True, "instrument"),
    "event_fact": ("event_fact", True, "event_assertion"),
    "later_directive": ("directive", True, "directive"),
    "inert_context": ("inert_load", False, "inventory_sentence"),
    "placebo": ("matched_placebo", False, "example_or_quotation"),
}

EXPECTED_SPANS = {
    "C0_baseline": {"mandate", "event_fact", "later_directive"},
    "C1_control_change": {"mandate", "event_fact", "later_directive"},
    "N0_inert_load": {"mandate", "event_fact", "inert_context", "later_directive"},
    "N1_matched_placebo": {"mandate", "event_fact", "placebo", "later_directive"},
}

SOURCE_KIND_BY_CONTENT_TYPE = {
    "instrument": "instrument",
    "event_assertion": "record",
    "directive": "directive",
    "inventory_sentence": "filler",
    "example_or_quotation": "quotation",
}

NARRATOR_SPANS = {"event_fact", "inert_context", "placebo"}
NON_GOVERNING_SPANS = {"event_fact", "inert_context", "placebo"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def iter_strings(value: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, member in enumerate(value):
            yield from iter_strings(member, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, member in value.items():
            yield from iter_strings(member, f"{path}.{key}")


def schema_errors(document: Any, schema: Any) -> list[str]:
    if Draft202012Validator is None:
        return ["jsonschema is required to run the Study B validator"]
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path)):
        location = "$"
        for part in error.absolute_path:
            location += f"[{part}]" if isinstance(part, int) else f".{part}"
        errors.append(f"{location}: {error.message}")
    return errors


def token_count(text: str, token: Any) -> int:
    if not isinstance(token, str):
        return 0
    return len(re.findall(rf"(?<![A-Z0-9_-]){re.escape(token)}(?![A-Z0-9_-])", text))


def time_index(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"T([0-9]+)", value)
    return int(match.group(1)) if match else None


def interval_contains(event_time: Any, interval: Any) -> bool | None:
    """Return interval membership, or None when schema-level parsing has failed."""

    event = time_index(event_time)
    if event is None or not isinstance(interval, dict):
        return None
    start = time_index(interval.get("start"))
    end_value = interval.get("end")
    end = None if end_value == "open" else time_index(end_value)
    if start is None or (end_value != "open" and end is None):
        return None
    if end is not None and end < start:
        return False
    return event >= start and (end is None or event <= end)


def guard_roles_are_typed(
    required_events: set[str],
    required_roles: set[str],
    guard_text: Any,
    available_roles: set[str],
) -> bool:
    """Check that every required role is linked to a declared guard event.

    The current schema has event and role identifiers rather than an event-evidence
    object.  The frozen naming convention therefore requires a shared identifier
    token among the role, an event, and the structured amend-standing guard.  This
    makes the role part of the checked guard rather than an unused annotation while
    still permitting roleless events such as automatic expiry.
    """

    if not required_roles:
        return True
    if not required_events or not isinstance(guard_text, str):
        return False
    guard_tokens = set(re.findall(r"[a-z0-9]+", guard_text.lower()))
    candidates: dict[str, set[str]] = {}
    for role in required_roles:
        role_candidates: set[str] = set()
        for event in required_events:
            event_guard_tokens = set(event.split("_")).intersection(guard_tokens)
            scores = {
                actor: len(set(actor.split("_")).intersection(event_guard_tokens))
                for actor in available_roles
            }
            role_score = scores.get(role, 0)
            if role_score > 0 and all(
                role_score > score for actor, score in scores.items() if actor != role
            ):
                role_candidates.add(event)
        if not role_candidates:
            return False
        candidates[role] = role_candidates

    # A single event cannot silently stand as typed evidence for two roles.
    ordered_roles = sorted(required_roles, key=lambda role: len(candidates[role]))

    def has_injective_binding(index: int, used_events: set[str]) -> bool:
        if index == len(ordered_roles):
            return True
        role = ordered_roles[index]
        return any(
            event not in used_events
            and has_injective_binding(index + 1, used_events | {event})
            for event in candidates[role]
        )

    return has_injective_binding(0, set())


def normalized_control_record(record: Any) -> Any:
    """Normalize condition-specific explanatory prose from a control record."""

    material = copy.deepcopy(record)
    if isinstance(material, dict):
        transition = material.get("purported_transition")
        if isinstance(transition, dict):
            transition.pop("reason", None)
    return material


def stable_c1_projection(record: Any) -> Any:
    """Project the fields that must not vary in the C1 guard-failure package."""

    material = copy.deepcopy(record)
    if not isinstance(material, dict):
        return material
    material.pop("regime_id", None)

    standing = material.get("operation_standing")
    if isinstance(standing, dict):
        # Amend and release jointly declare the protected amendment guard in the
        # current families.  Other operations must remain fixed.
        standing.pop("amend", None)
        standing.pop("release", None)

    amendment = material.get("amendment_rule")
    if isinstance(amendment, dict):
        for key in (
            "amendment_actors",
            "required_events",
            "required_roles",
            "effective_interval",
        ):
            amendment.pop(key, None)

    transition = material.get("purported_transition")
    if isinstance(transition, dict):
        for key in ("guard_evaluation", "valid", "reason"):
            transition.pop(key, None)

    licensed = material.get("licensed_action")
    if isinstance(licensed, dict):
        licensed.pop("main_value", None)
    return material


def reviewed_content_hash(base: dict[str, Any]) -> str:
    """Hash base content reviewed for reference alignment and privacy.

    Review records and mutable construction-eligibility flags are excluded so that
    recording a completed review does not change the reviewed object.
    """

    material = copy.deepcopy(base)
    material.pop("independent_reference_review", None)
    material.pop("privacy_review", None)
    conditions = material.get("conditions", [])
    if isinstance(conditions, list):
        for item in conditions:
            if isinstance(item, dict):
                item.pop("construction", None)
    encoded = json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def review_passed(review: Any, expected_hash: str) -> bool:
    return (
        isinstance(review, dict)
        and review.get("status") == "completed"
        and review.get("decision") == "pass"
        and review.get("content_hash") == expected_hash
    )


def invariant_errors(document: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    bases = document.get("base_scenarios")
    if not isinstance(bases, list):
        return errors

    gates = document.get("construction_gate_log", [])
    gate_stages = [row.get("stage") for row in gates if isinstance(row, dict)]
    if set(gate_stages) != EXPECTED_GATE_STAGES or len(gate_stages) != len(EXPECTED_GATE_STAGES):
        errors.append("construction_gate_log must contain each construction stage exactly once")
    for index, row in enumerate(gates if isinstance(gates, list) else []):
        if not isinstance(row, dict):
            continue
        entered = row.get("entered_count")
        passed = row.get("passed_count")
        excluded = row.get("excluded_count")
        if all(isinstance(value, int) for value in (entered, passed, excluded)):
            if passed + excluded > entered:
                errors.append(
                    f"construction_gate_log[{index}]: passed plus excluded exceeds entered"
                )

    base_ids: set[str] = set()
    item_ids: set[str] = set()
    families: set[str] = set()

    for base_index, base in enumerate(bases):
        if not isinstance(base, dict):
            continue
        prefix = f"base_scenarios[{base_index}]"
        base_id = base.get("base_id")
        if base_id in base_ids:
            errors.append(f"{prefix}: duplicate base_id {base_id!r}")
        if isinstance(base_id, str):
            base_ids.add(base_id)
        family = base.get("scenario_family")
        if isinstance(family, str):
            families.add(family)

        actor_rows = base.get("actors", [])
        actor_ids = [row.get("role_id") for row in actor_rows if isinstance(row, dict)]
        if len(actor_ids) != len(set(actor_ids)):
            errors.append(f"{prefix}: actor role_ids must be unique")
        actor_set = {value for value in actor_ids if isinstance(value, str)}

        fixed = base.get("fixed_elements", {})
        if not isinstance(fixed, dict):
            continue
        initial = fixed.get("initial_main_value")
        requested = fixed.get("requested_main_value")
        initial_control = fixed.get("initial_control_value")
        requested_control = fixed.get("requested_control_value")
        main_target = fixed.get("main_action_target")
        control_target = fixed.get("control_action_target")
        later_directive_id = fixed.get("later_directive_id")
        later_text = fixed.get("later_directive_text")
        event_fact = fixed.get("fixed_event_fact_text")
        if initial == requested:
            errors.append(f"{prefix}: initial and requested main values must differ")
        if initial_control == requested_control:
            errors.append(f"{prefix}: initial and requested control values must differ")
        if main_target == control_target:
            errors.append(f"{prefix}: main and control action targets must differ")

        founding = base.get("founding_validity", {})
        founding_source = founding.get("adoption_source_id") if isinstance(founding, dict) else None
        expected_hash = reviewed_content_hash(base)
        reference_review = base.get("independent_reference_review")
        privacy_review = base.get("privacy_review")
        for review_name, review in (
            ("independent_reference_review", reference_review),
            ("privacy_review", privacy_review),
        ):
            if isinstance(review, dict) and review.get("status") == "completed":
                if review.get("content_hash") != expected_hash:
                    errors.append(f"{prefix}.{review_name}: content_hash does not match reviewed base")

        conditions = base.get("conditions", [])
        if not isinstance(conditions, list):
            continue
        by_condition = {
            row.get("condition"): row
            for row in conditions
            if isinstance(row, dict) and isinstance(row.get("condition"), str)
        }
        if set(by_condition) != set(CONDITIONS):
            errors.append(
                f"{prefix}: condition set is {sorted(by_condition)!r}, expected {sorted(CONDITIONS)!r}"
            )

        transition_times: set[str] = set()
        prompt_by_condition: dict[str, str] = {}
        for item_index, item in enumerate(conditions):
            if not isinstance(item, dict):
                continue
            item_prefix = f"{prefix}.conditions[{item_index}]"
            item_id = item.get("item_id")
            condition = item.get("condition")
            if item_id in item_ids:
                errors.append(f"{item_prefix}: duplicate item_id {item_id!r}")
            if isinstance(item_id, str):
                item_ids.add(item_id)
            if condition not in CONDITIONS:
                continue

            suffix, context_variant, manipulation_kind, context_operative = CONDITIONS[condition]
            expected_id = f"{base_id}-{suffix}"
            if item_id != expected_id:
                errors.append(f"{item_prefix}: item_id must be {expected_id!r}")
            if item.get("context_variant_id") != context_variant:
                errors.append(f"{item_prefix}: context_variant_id does not match {condition}")
            if item.get("application_surface") != "structured_prompt":
                errors.append(f"{item_prefix}: current fixtures must use structured_prompt")

            manipulation = item.get("manipulation", {})
            if isinstance(manipulation, dict):
                if manipulation.get("kind") != manipulation_kind:
                    errors.append(f"{item_prefix}: manipulation kind does not match {condition}")
                if manipulation.get("context_operative") is not context_operative:
                    errors.append(f"{item_prefix}: context_operative does not match {condition}")

            prompt_rows = item.get("prompt_messages", [])
            prompt_text = "\n".join(
                row.get("text", "") for row in prompt_rows if isinstance(row, dict)
            )
            prompt_by_condition[condition] = prompt_text
            if isinstance(later_text, str) and prompt_text.count(later_text) != 1:
                errors.append(
                    f"{item_prefix}: fixed later directive text is not reproduced exactly once"
                )
            if isinstance(event_fact, str) and prompt_text.count(event_fact) != 1:
                errors.append(f"{item_prefix}: fixed event fact is not reproduced exactly once")
            if token_count(prompt_text, initial) < 1:
                errors.append(f"{item_prefix}: prompt omits the initial main value")
            if token_count(prompt_text, initial_control) < 1:
                errors.append(f"{item_prefix}: prompt omits the initial control value")

            prompt_tags = TAG_PATTERN.findall(prompt_text)
            spans = item.get("tagged_spans", [])
            span_ids = [row.get("span_id") for row in spans if isinstance(row, dict)]
            span_by_id = {
                row.get("span_id"): row
                for row in spans
                if isinstance(row, dict) and isinstance(row.get("span_id"), str)
            }
            if len(prompt_tags) != len(set(prompt_tags)):
                errors.append(f"{item_prefix}: prompt tags must be unique")
            if len(span_ids) != len(set(span_ids)):
                errors.append(f"{item_prefix}: tagged span ids must be unique")
            if set(prompt_tags) != set(span_ids) or len(prompt_tags) != len(span_ids):
                errors.append(f"{item_prefix}: tagged_spans must be a bijection with prompt tags")
            if set(span_ids) != EXPECTED_SPANS[condition]:
                errors.append(
                    f"{item_prefix}: tagged span ids do not match the {condition} span design"
                )
            for span_id, span in span_by_id.items():
                expected_semantics = SPAN_SEMANTICS.get(span_id)
                if expected_semantics is None:
                    continue
                observed_semantics = (
                    span.get("pragmatic_status"),
                    span.get("operative"),
                    span.get("content_type"),
                )
                if observed_semantics != expected_semantics:
                    errors.append(
                        f"{item_prefix}: [{span_id}] status, operativity, and content_type "
                        "must match its declared span semantics"
                    )
                if span_id in NARRATOR_SPANS and span.get("source_role") != "benchmark_narrator":
                    errors.append(
                        f"{item_prefix}: [{span_id}] source_role must be benchmark_narrator"
                    )

            record = item.get("authorization_record", {})
            if not isinstance(record, dict):
                continue
            if set(record.get("actor_roles", [])) != actor_set:
                errors.append(f"{item_prefix}: authorization actor_roles differ from base actors")

            sources = record.get("governing_sources", [])
            source_id_list = [
                source.get("source_span_id")
                for source in sources
                if isinstance(source, dict) and isinstance(source.get("source_span_id"), str)
            ]
            source_ids = set(source_id_list)
            if len(source_id_list) != len(source_ids):
                errors.append(f"{item_prefix}: governing source_span_ids must be unique")
            if founding_source not in source_ids:
                errors.append(f"{item_prefix}: founding adoption source is not a governing source")
            expected_governing_sources = {founding_source, later_directive_id}
            if source_ids != expected_governing_sources:
                errors.append(
                    f"{item_prefix}: governing sources must be exactly the founding mandate "
                    "and later directive"
                )
            for source_span in source_ids:
                if f"[{source_span}]" not in prompt_text:
                    errors.append(
                        f"{item_prefix}: governing source [{source_span}] is absent from the prompt"
                    )
                if source_span in NON_GOVERNING_SPANS:
                    errors.append(
                        f"{item_prefix}: [{source_span}] cannot be a governing source"
                    )
            for source in sources if isinstance(sources, list) else []:
                if not isinstance(source, dict):
                    continue
                source_span = source.get("source_span_id")
                span = span_by_id.get(source_span)
                if not isinstance(span, dict):
                    errors.append(
                        f"{item_prefix}: governing source {source_span!r} lacks tagged-span metadata"
                    )
                    continue
                expected_kind = SOURCE_KIND_BY_CONTENT_TYPE.get(span.get("content_type"))
                if source.get("source_kind") != expected_kind:
                    errors.append(
                        f"{item_prefix}: governing source [{source_span}] kind conflicts with "
                        "tagged-span content_type"
                    )
                if source.get("operative") is not True or span.get("operative") is not True:
                    errors.append(
                        f"{item_prefix}: governing source [{source_span}] must be operative in "
                        "both registries"
                    )

            standing = record.get("operation_standing", {})
            if isinstance(standing, dict):
                for operation, entry in standing.items():
                    if not isinstance(entry, dict):
                        continue
                    unknown = set(entry.get("holders", [])) - actor_set
                    if unknown:
                        errors.append(
                            f"{item_prefix}: {operation} standing names unknown actors {sorted(unknown)!r}"
                        )
                issue = standing.get("issue", {})
                mandate_span = span_by_id.get(founding_source)
                if isinstance(issue, dict) and isinstance(mandate_span, dict):
                    if mandate_span.get("source_role") not in issue.get("holders", []):
                        errors.append(
                            f"{item_prefix}: founding mandate source_role lacks issue standing"
                        )

            amendment = record.get("amendment_rule", {})
            transition = record.get("purported_transition", {})
            if not isinstance(amendment, dict) or not isinstance(transition, dict):
                continue
            transition_times.add(str(transition.get("event_time")))
            amendment_actors = set(amendment.get("amendment_actors", []))
            required_roles = set(amendment.get("required_roles", []))
            if amendment_actors - actor_set:
                errors.append(f"{item_prefix}: amendment rule names unknown amendment actors")
            if required_roles - actor_set:
                errors.append(f"{item_prefix}: amendment rule names unknown required roles")

            amend_standing = standing.get("amend", {}) if isinstance(standing, dict) else {}
            amend_holders = set(amend_standing.get("holders", [])) if isinstance(amend_standing, dict) else set()
            if amendment_actors != amend_holders:
                errors.append(
                    f"{item_prefix}: amendment actors differ from structured amend standing"
                )
            if amend_standing.get("target") != main_target:
                errors.append(f"{item_prefix}: amend standing target must equal the main target")
            if amendment.get("target") != main_target:
                errors.append(f"{item_prefix}: amendment rule target must equal the main target")
            if transition.get("target") != main_target:
                errors.append(f"{item_prefix}: amendment transition target must equal the main target")

            guard = transition.get("guard_evaluation", {})
            required_events = set(guard.get("required_events", [])) if isinstance(guard, dict) else set()
            observed_events = set(guard.get("observed_events", [])) if isinstance(guard, dict) else set()
            if required_events != set(amendment.get("required_events", [])):
                errors.append(
                    f"{item_prefix}: transition guard requirements differ from the amendment rule"
                )
            issuer = transition.get("issuer_role")
            issuer_has_standing = issuer in amendment_actors and issuer in amend_holders
            guards_satisfied = required_events.issubset(observed_events)
            roles_are_typed = guard_roles_are_typed(
                set(amendment.get("required_events", [])),
                required_roles,
                amend_standing.get("guard") if isinstance(amend_standing, dict) else None,
                actor_set,
            )
            if not roles_are_typed:
                errors.append(
                    f"{item_prefix}: amendment required_roles are not bound to typed guard events"
                )
            derived_valid = issuer_has_standing and guards_satisfied and roles_are_typed
            if transition.get("valid") is not derived_valid:
                errors.append(f"{item_prefix}: stored transition validity differs from derived validity")

            design_valid = condition != "C1_control_change"
            if derived_valid is not design_valid:
                errors.append(
                    f"{item_prefix}: derived validity violates the frozen condition design"
                )
            if condition == "C1_control_change":
                if not issuer_has_standing:
                    errors.append(
                        f"{item_prefix}: C1 issuer must retain amendment standing"
                    )
                if not required_roles:
                    errors.append(
                        f"{item_prefix}: C1 guard must declare a typed required role"
                    )
                if not required_events or guards_satisfied:
                    errors.append(
                        f"{item_prefix}: C1 invalidity must be caused by a declared unsatisfied guard"
                    )
            if transition.get("requested_value") != requested:
                errors.append(
                    f"{item_prefix}: transition requested value differs from the fixed directive"
                )

            directive_span = span_by_id.get(later_directive_id)
            if isinstance(directive_span, dict) and directive_span.get("source_role") != issuer:
                errors.append(
                    f"{item_prefix}: later-directive source_role must match the transition issuer"
                )

            event_time = transition.get("event_time")
            interval_rows = (
                ("founding", founding.get("effective_interval") if isinstance(founding, dict) else None),
                ("authorization-record", record.get("effective_interval")),
                ("amendment-rule", amendment.get("effective_interval")),
            )
            for interval_name, interval in interval_rows:
                if interval_contains(event_time, interval) is False:
                    errors.append(
                        f"{item_prefix}: transition time lies outside the {interval_name} "
                        "effective interval"
                    )

            direct = standing.get("direct", {}) if isinstance(standing, dict) else {}
            if isinstance(direct, dict):
                if issuer not in direct.get("holders", []):
                    errors.append(
                        f"{item_prefix}: directive issuer lacks the unrelated control standing"
                    )
                if direct.get("target") != control_target:
                    errors.append(f"{item_prefix}: direct standing must target the control action")

            licensed = record.get("licensed_action")
            expected_action = item.get("expected_action")
            if licensed != expected_action:
                errors.append(f"{item_prefix}: expected_action differs from the authorization record")
            if isinstance(expected_action, dict):
                expected_main = requested if derived_valid else initial
                expected_pairs = {
                    "main_target": main_target,
                    "main_value": expected_main,
                    "control_target": control_target,
                    "control_value": requested_control,
                }
                for key, value in expected_pairs.items():
                    if expected_action.get(key) != value:
                        errors.append(f"{item_prefix}: expected_action.{key} must be {value!r}")

            construction = item.get("construction", {})
            if isinstance(construction, dict):
                inspected = construction.get("output_inspected_during_construction")
                production = construction.get("production_eligible")
                if inspected is True and production is True:
                    errors.append(
                        f"{item_prefix}: output-inspected development items cannot be production eligible"
                    )
                if production is True:
                    if not review_passed(reference_review, expected_hash):
                        errors.append(
                            f"{item_prefix}: production eligibility requires a completed passing independent reference review bound to this base"
                        )
                    if not review_passed(privacy_review, expected_hash):
                        errors.append(
                            f"{item_prefix}: production eligibility requires a completed passing privacy review bound to this base"
                        )
                    if document.get("status") == "development_only_no_collection_authorized":
                        errors.append(
                            f"{item_prefix}: top-level development status does not authorize production eligibility"
                        )

        if len(transition_times) > 1:
            errors.append(f"{prefix}: purported transition time is not held fixed across conditions")
        if set(CONDITIONS).issubset(by_condition):
            c0 = by_condition["C0_baseline"].get("authorization_record", {})
            c1 = by_condition["C1_control_change"].get("authorization_record", {})
            n0 = by_condition["N0_inert_load"].get("authorization_record", {})
            n1 = by_condition["N1_matched_placebo"].get("authorization_record", {})
            baseline_regime = c0.get("regime_id") if isinstance(c0, dict) else None
            if any(
                not isinstance(record, dict) or record.get("regime_id") != baseline_regime
                for record in (n0, n1)
            ):
                errors.append(f"{prefix}: C0, N0, and N1 must share one regime_id")
            normalized_controls = [
                normalized_control_record(record) for record in (c0, n0, n1)
            ]
            if not all(record == normalized_controls[0] for record in normalized_controls[1:]):
                errors.append(
                    f"{prefix}: normalized C0, N0, and N1 authorization records must match"
                )
            if stable_c1_projection(c1) != stable_c1_projection(c0):
                errors.append(
                    f"{prefix}: C1 differs from C0 outside the declared guard-failure package"
                )
            c0_rule = c0.get("amendment_rule") if isinstance(c0, dict) else None
            c1_rule = c1.get("amendment_rule") if isinstance(c1, dict) else None
            c0_transition = c0.get("purported_transition", {}) if isinstance(c0, dict) else {}
            c1_transition = c1.get("purported_transition", {}) if isinstance(c1, dict) else {}
            c0_standing = c0.get("operation_standing", {}) if isinstance(c0, dict) else {}
            c1_standing = c1.get("operation_standing", {}) if isinstance(c1, dict) else {}
            if isinstance(c0_transition, dict) and isinstance(c1_transition, dict):
                if (
                    c1_transition.get("issuer_role") != c0_transition.get("issuer_role")
                    or c1_transition.get("target") != c0_transition.get("target")
                ):
                    errors.append(
                        f"{prefix}: C1 must retain the C0 transition issuer and target"
                    )
            if isinstance(c0_rule, dict) and isinstance(c1_rule, dict):
                c0_actors = set(c0_rule.get("amendment_actors", []))
                c1_actors = set(c1_rule.get("amendment_actors", []))
                issuer = c1_transition.get("issuer_role") if isinstance(c1_transition, dict) else None
                if not c1_actors or not c1_actors.issubset(c0_actors) or issuer not in c1_actors:
                    errors.append(
                        f"{prefix}: C1 amendment actors must be a nonempty C0 subset containing "
                        "the fixed issuer"
                    )
            if isinstance(c0_standing, dict) and isinstance(c1_standing, dict):
                c0_amend = c0_standing.get("amend", {})
                c1_amend = c1_standing.get("amend", {})
                if isinstance(c0_amend, dict) and isinstance(c1_amend, dict):
                    c0_holders = set(c0_amend.get("holders", []))
                    c1_holders = set(c1_amend.get("holders", []))
                    issuer = (
                        c1_transition.get("issuer_role")
                        if isinstance(c1_transition, dict)
                        else None
                    )
                    if (
                        not c1_holders
                        or not c1_holders.issubset(c0_holders)
                        or issuer not in c1_holders
                    ):
                        errors.append(
                            f"{prefix}: C1 amend-standing holders must be a nonempty C0 subset "
                            "containing the fixed issuer"
                        )
            if c0_rule == c1_rule:
                errors.append(f"{prefix}: C1 must change the operative amendment rule")

            baseline_prompt = prompt_by_condition.get("C0_baseline", "")
            n0_prompt = prompt_by_condition.get("N0_inert_load", "")
            for token in (initial, requested, initial_control, requested_control):
                if token_count(n0_prompt, token) != token_count(baseline_prompt, token):
                    errors.append(
                        f"{prefix}: N0 changes answer-token vocabulary for {token!r}"
                    )

    if families != EXPECTED_FAMILIES:
        errors.append(
            f"scenario families are {sorted(families)!r}, expected {sorted(EXPECTED_FAMILIES)!r}"
        )

    # This is marker triage only; a clean result is not a privacy determination.
    for path, value in iter_strings(document):
        match = PRIVATE_MARKERS.search(value)
        if match:
            errors.append(f"{path}: possible private-source marker {match.group(0)!r}")

    return errors


def validate_document(document: Any, schema: Any) -> list[str]:
    errors = schema_errors(document, schema)
    if isinstance(document, dict):
        errors.extend(invariant_errors(document))
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("items", nargs="?", type=Path, default=DEFAULT_ITEMS)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        document = load_json(args.items)
        schema = load_json(args.schema)
    except (OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    errors = validate_document(document, schema)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    base_count = len(document["base_scenarios"])
    item_count = sum(len(base["conditions"]) for base in document["base_scenarios"])
    print(
        f"ok: structural checks only; semantic and privacy reviews remain external "
        f"({base_count} bases, {item_count} items)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
