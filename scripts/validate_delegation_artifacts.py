#!/usr/bin/env python3
"""Validate and execute Delegation Assurance's stipulated-regime fixtures.

The trace files contain only recorded material.  Separate oracle files contain
closed-world reference labels.  This validator derives grant validity,
transition effects, authorization verdicts, trajectory conditions, and record
adequacy from the versioned stipulated regime, then compares those results with
the hidden oracles.  It also builds reference-free reviewer and predictor views.

Passing these checks establishes consistency with the synthetic regime only. It
does not establish that an institutional regime is operative or that any
assessment interpretation transports beyond the declared fixtures.
"""

from __future__ import annotations

import argparse
import copy
import json
import operator
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "assurance" / "delegation"
REGIME_SCHEMA_NAME = "regime.schema.json"
TRACE_SCHEMA_NAME = "authorization-trace.schema.json"
ORACLE_SCHEMA_NAME = "oracle.schema.json"
REGIME_FIXTURE_NAME = "procurement-stipulated-regime-v2.json"
VIEW_POLICY_NAME = "view-policy.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: cannot load JSON: {exc}") from exc


def schema_errors(instance: Any, schema: Any, path: Path) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for issue in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
        errors.append(f"{path.name}:{location}: {issue.message}")
    return errors


def iso(value: str, label: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label}: invalid ISO timestamp {value!r}") from exc


def in_interval(timestamp: datetime, interval: dict[str, Any]) -> bool:
    start = iso(interval["starts_at"], "interval.starts_at")
    end_value = interval.get("ends_at")
    end = iso(end_value, "interval.ends_at") if end_value else None
    return timestamp >= start and (end is None or timestamp <= end)


def interval_ordered(interval: dict[str, Any]) -> bool:
    start = iso(interval["starts_at"], "interval.starts_at")
    end_value = interval.get("ends_at")
    end = iso(end_value, "interval.ends_at") if end_value else None
    return end is None or start <= end


def interval_within(child: dict[str, Any], parent: dict[str, Any]) -> bool:
    child_start = iso(child["starts_at"], "child.starts_at")
    parent_start = iso(parent["starts_at"], "parent.starts_at")
    child_end_value = child.get("ends_at")
    parent_end_value = parent.get("ends_at")
    child_end = iso(child_end_value, "child.ends_at") if child_end_value else None
    parent_end = iso(parent_end_value, "parent.ends_at") if parent_end_value else None
    if child_start < parent_start:
        return False
    if parent_end is None:
        return True
    return child_end is not None and child_end <= parent_end


def unique_ids(
    values: Iterable[dict[str, Any]], key: str, label: str, errors: list[str]
) -> set[str]:
    ids: list[str] = []
    for index, value in enumerate(values):
        identifier = value.get(key)
        if not isinstance(identifier, str):
            errors.append(f"{label}[{index}] lacks {key}")
        else:
            ids.append(identifier)
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        errors.append(f"{label}: duplicate {key} values: {', '.join(duplicates)}")
    return set(ids)


def compare(value: Any, op_name: str, threshold: Any) -> bool:
    operations = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
    }
    try:
        return bool(operations[op_name](value, threshold))
    except TypeError:
        return False


def source_set_satisfies(
    supplied: Iterable[str], permitted: Iterable[str], source_operator: str
) -> bool:
    supplied_set = set(supplied)
    permitted_set = set(permitted)
    if not supplied_set or not supplied_set <= permitted_set:
        return False
    if source_operator == "all_of":
        return supplied_set == permitted_set
    return bool(supplied_set & permitted_set)


def guard_status(
    regime: dict[str, Any], guard_ids: Iterable[str], evidence: dict[str, bool]
) -> bool | None:
    guards = {guard["guard_id"]: guard for guard in regime["guards"]}
    for guard_id in guard_ids:
        guard = guards.get(guard_id)
        if guard is None:
            return None
        values: list[bool] = []
        for requirement in guard["requirements"]:
            if requirement not in evidence:
                return None
            values.append(bool(evidence[requirement]))
        passed = all(values) if guard["operator"] == "all_of" else any(values)
        if not passed:
            return False
    return True


def standing_status(
    regime: dict[str, Any],
    source_ids: Iterable[str],
    operation: str,
    authority_object: str,
    timestamp: datetime,
    evidence: dict[str, bool],
) -> bool | None:
    saw_missing = False
    for rule in regime["standing_rules"]:
        if operation not in rule["operations"] or authority_object not in rule["authority_objects"]:
            continue
        if not in_interval(timestamp, rule["effective_interval"]):
            continue
        if not source_set_satisfies(source_ids, rule["source_ids"], rule["source_operator"]):
            continue
        guards = guard_status(regime, rule["guard_ids"], evidence)
        if guards is True:
            return True
        if guards is None:
            saw_missing = True
    return None if saw_missing else False


def constraint_contains(parent: Any, child: Any) -> bool:
    if isinstance(parent, list):
        child_values = child if isinstance(child, list) else [child]
        return set(child_values) <= set(parent)
    if isinstance(parent, dict):
        if set(parent) == {"max"}:
            child_max = child.get("max") if isinstance(child, dict) else child
            return isinstance(child_max, (int, float)) and child_max <= parent["max"]
        if set(parent) == {"min"}:
            child_min = child.get("min") if isinstance(child, dict) else child
            return isinstance(child_min, (int, float)) and child_min >= parent["min"]
        if not isinstance(child, dict):
            return False
        return all(key in child and constraint_contains(value, child[key]) for key, value in parent.items())
    return child == parent


def scope_contains(parent_scope: dict[str, Any], child_scope: dict[str, Any]) -> bool:
    return all(
        key in child_scope and constraint_contains(value, child_scope[key])
        for key, value in parent_scope.items()
    )


def action_in_scope(scope: dict[str, Any], parameters: dict[str, Any]) -> bool:
    return all(
        key in parameters and constraint_contains(constraint, parameters[key])
        for key, constraint in scope.items()
    )


def validate_regime_semantics(regime: dict[str, Any], errors: list[str]) -> None:
    sources = unique_ids(regime["sources"], "source_id", "regime.sources", errors)
    guards = unique_ids(regime["guards"], "guard_id", "regime.guards", errors)
    unique_ids(regime["standing_rules"], "standing_rule_id", "regime.standing_rules", errors)
    unique_ids(regime["transition_rules"], "transition_rule_id", "regime.transition_rules", errors)
    unique_ids(regime["action_rules"], "action_rule_id", "regime.action_rules", errors)
    unique_ids(regime["trajectory_conditions"], "condition_id", "regime.trajectory_conditions", errors)
    unique_ids(regime["applicability_maps"], "applicability_id", "regime.applicability_maps", errors)

    action_classes = [rule["action_class"] for rule in regime["action_rules"]]
    if len(action_classes) != len(set(action_classes)):
        errors.append("regime.action_rules: action_class values must be unique")
    transition_keys = [
        (rule["operation"], rule["authority_object"])
        for rule in regime["transition_rules"]
    ]
    if len(transition_keys) != len(set(transition_keys)):
        errors.append(
            "regime.transition_rules: operation and authority_object pairs must be unique"
        )
    start = iso(regime["effective_interval"]["starts_at"], "regime.starts_at")
    end = iso(regime["effective_interval"]["ends_at"], "regime.ends_at")
    if start >= end:
        errors.append("regime.effective_interval: starts_at must precede ends_at")

    for collection, source_key, guard_key in (
        (regime["standing_rules"], "source_ids", "guard_ids"),
        (regime["transition_rules"], "eligible_source_ids", "guard_ids"),
    ):
        for rule in collection:
            unknown_sources = set(rule[source_key]) - sources
            unknown_guards = set(rule[guard_key]) - guards
            if unknown_sources:
                errors.append(f"{rule}: unknown sources {sorted(unknown_sources)}")
            if unknown_guards:
                errors.append(f"{rule}: unknown guards {sorted(unknown_guards)}")
    for rule in regime["standing_rules"]:
        if not interval_ordered(rule["effective_interval"]):
            errors.append(
                f"{rule['standing_rule_id']}: effective interval is not ordered"
            )
        elif not interval_within(
            rule["effective_interval"], regime["effective_interval"]
        ):
            errors.append(
                f"{rule['standing_rule_id']}: effective interval exceeds the regime interval"
            )
    for rule in regime["action_rules"]:
        unknown_guards = set(rule["guard_ids"]) - guards
        if unknown_guards:
            errors.append(f"{rule['action_rule_id']}: unknown guards {sorted(unknown_guards)}")


def derive_grant_validity(
    regime: dict[str, Any], trace: dict[str, Any], errors: list[str]
) -> dict[str, bool]:
    grants = {grant["grant_id"]: grant for grant in trace["grants"]}
    validity: dict[str, bool] = {}
    visiting: set[str] = set()

    def valid(grant_id: str) -> bool:
        if grant_id in validity:
            return validity[grant_id]
        if grant_id in visiting:
            errors.append(f"{trace['trace_id']}.{grant_id}: cyclic parent grants")
            validity[grant_id] = False
            return False
        visiting.add(grant_id)
        grant = grants[grant_id]
        issued_at = iso(grant["issued_at"], f"{trace['trace_id']}.{grant_id}.issued_at")
        end_value = grant["effective_interval"].get("ends_at")
        grant_end = iso(end_value, f"{trace['trace_id']}.{grant_id}.ends_at") if end_value else None
        interval_valid = interval_ordered(grant["effective_interval"]) and interval_within(
            grant["effective_interval"], regime["effective_interval"]
        )
        if (
            not in_interval(issued_at, regime["effective_interval"])
            or not interval_valid
            or (grant_end is not None and issued_at > grant_end)
        ):
            result = False
        elif grant["parent_grant_ids"]:
            result = True
            for parent_id in grant["parent_grant_ids"]:
                parent = grants.get(parent_id)
                if parent is None or not valid(parent_id):
                    result = False
                    continue
                if grant["grantor_ids"] != [parent["grantee_id"]]:
                    result = False
                if not parent["subdelegation_allowed"]:
                    result = False
                if not set(grant["action_classes"]) <= set(parent["action_classes"]):
                    result = False
                if not scope_contains(parent["scope"], grant["scope"]):
                    result = False
                if not interval_within(grant["effective_interval"], parent["effective_interval"]):
                    result = False
        else:
            standing = standing_status(
                regime,
                grant["grantor_ids"],
                "issue",
                grant["authority_object"],
                issued_at,
                grant["guard_evidence"],
            )
            if standing is None:
                errors.append(f"{trace['trace_id']}.{grant_id}: missing evidence for grant standing")
            result = standing is True
        visiting.remove(grant_id)
        validity[grant_id] = result
        return result

    for identifier in grants:
        valid(identifier)
    return validity


def transition_rule(
    regime: dict[str, Any], transition: dict[str, Any]
) -> dict[str, Any] | None:
    matches = [
        rule
        for rule in regime["transition_rules"]
        if rule["operation"] == transition["operation"]
        and rule["authority_object"] == transition["authority_object"]
    ]
    return matches[0] if len(matches) == 1 else None


def derive_transition_effects(
    regime: dict[str, Any],
    trace: dict[str, Any],
    valid_grants: dict[str, bool],
    errors: list[str],
) -> dict[str, str]:
    grant_ids = set(valid_grants)
    effects: dict[str, str] = {}
    for transition in sorted(trace["transitions"], key=lambda item: item["timestamp"]):
        prefix = f"{trace['trace_id']}.{transition['transition_id']}"
        timestamp = iso(transition["timestamp"], prefix)
        rule = transition_rule(regime, transition)
        if rule is None:
            errors.append(f"{prefix}: no unique transition rule for operation and authority object")
            effects[transition["transition_id"]] = "ineffective"
            continue
        sources_ok = source_set_satisfies(
            transition["issuer_ids"], rule["eligible_source_ids"], rule["source_operator"]
        )
        standing = standing_status(
            regime,
            transition["issuer_ids"],
            transition["operation"],
            transition["authority_object"],
            timestamp,
            transition["guard_evidence"],
        )
        guards = guard_status(regime, rule["guard_ids"], transition["guard_evidence"])
        if standing is None or guards is None:
            errors.append(f"{prefix}: transition guard or standing evidence is missing")
            effects[transition["transition_id"]] = "unevaluable"
            continue
        payload = transition["normative_payload"]
        payload_ok = True
        if rule["effect_kind"] in {"activate_grant", "deactivate_grant"}:
            payload_ok = payload.get("grant_id") in grant_ids
        elif rule["effect_kind"] == "set_object_state":
            payload_ok = "state" in payload
        unknown_basis = set(transition["basis_grant_ids"]) - grant_ids
        if unknown_basis:
            errors.append(f"{prefix}: unknown basis grants {sorted(unknown_basis)}")
        effective = sources_ok and standing is True and guards is True and payload_ok and not unknown_basis
        effects[transition["transition_id"]] = "effective" if effective else "ineffective"
    return effects


def normative_state_at(
    regime: dict[str, Any],
    trace: dict[str, Any],
    valid_grants: dict[str, bool],
    transition_effects: dict[str, str],
    timestamp: datetime,
) -> dict[str, Any]:
    grants = {grant["grant_id"]: grant for grant in trace["grants"]}
    active = {
        grant_id
        for grant_id, grant in grants.items()
        if valid_grants[grant_id]
        and grant["activation_transition_id"] is None
        and iso(grant["issued_at"], f"{grant_id}.issued_at") <= timestamp
        and in_interval(timestamp, grant["effective_interval"])
    }
    object_states = copy.deepcopy(regime["initial_normative_state"]["authority_object_states"])
    for transition in sorted(trace["transitions"], key=lambda item: item["timestamp"]):
        transition_time = iso(transition["timestamp"], transition["transition_id"])
        if transition_time > timestamp or transition_effects[transition["transition_id"]] != "effective":
            continue
        rule = transition_rule(regime, transition)
        assert rule is not None
        payload = transition["normative_payload"]
        if rule["effect_kind"] == "activate_grant":
            active.add(payload["grant_id"])
        elif rule["effect_kind"] == "deactivate_grant":
            active.discard(payload["grant_id"])
        elif rule["effect_kind"] == "set_object_state":
            object_states[transition["authority_object"]] = payload["state"]
        for grant_id, grant in grants.items():
            if grant["activation_transition_id"] == transition["transition_id"] and valid_grants[grant_id]:
                active.add(grant_id)
    active = {
        grant_id
        for grant_id in active
        if valid_grants[grant_id]
        and iso(grants[grant_id]["issued_at"], f"{grant_id}.issued_at") <= timestamp
        and in_interval(timestamp, grants[grant_id]["effective_interval"])
    }
    return {
        "active_grant_ids": sorted(active),
        "authority_object_states": object_states,
    }


def action_rule(regime: dict[str, Any], action_class: str) -> dict[str, Any] | None:
    matches = [rule for rule in regime["action_rules"] if rule["action_class"] == action_class]
    return matches[0] if len(matches) == 1 else None


def derive_action_authorization(
    regime: dict[str, Any],
    trace: dict[str, Any],
    action: dict[str, Any],
    subject_id: str,
    timestamp: datetime,
    evidence: dict[str, bool],
    valid_grants: dict[str, bool],
    transition_effects: dict[str, str],
) -> str:
    rule = action_rule(regime, action["action_class"])
    if rule is None:
        return "unevaluable"
    if rule["effect"] == "prohibit":
        return "prohibited"
    guards = guard_status(regime, rule["guard_ids"], evidence)
    if guards is None:
        return "unevaluable"
    if guards is False:
        return "prohibited"
    state = normative_state_at(regime, trace, valid_grants, transition_effects, timestamp)
    grants = {grant["grant_id"]: grant for grant in trace["grants"]}
    matching = [
        grants[grant_id]
        for grant_id in state["active_grant_ids"]
        if grants[grant_id]["grantee_id"] == subject_id
        and action["action_class"] in grants[grant_id]["action_classes"]
        and action_in_scope(grants[grant_id]["scope"], action["parameters"])
    ]
    if rule["valid_grant_required"] and not matching:
        return "prohibited"
    if rule["effect"] == "discretionary":
        if "discretionary_authorized" not in evidence:
            return "unevaluable"
        return "authorized" if evidence["discretionary_authorized"] else "prohibited"
    return "authorized"


def apply_delta(before: dict[str, Any], delta: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(before)
    for key, value in delta.items():
        result[key] = value
    return result


def state_continuity(trace: dict[str, Any], errors: list[str]) -> bool:
    current = copy.deepcopy(trace["boundary"]["initial_execution_state"])
    continuous = True
    for execution in sorted(trace["records"]["executions"], key=lambda item: item["timestamp"]):
        prefix = f"{trace['trace_id']}.{execution['execution_id']}"
        state = execution["state"]
        if state["before"] != current:
            errors.append(f"{prefix}: state.before does not equal the preceding state")
            continuous = False
        expected_after = apply_delta(state["before"], state["delta"])
        if state["after"] != expected_after:
            errors.append(f"{prefix}: state.delta does not produce state.after")
            continuous = False
        current = copy.deepcopy(state["after"])
    return continuous


def evaluate_conditions(
    regime: dict[str, Any], trace: dict[str, Any], errors: list[str]
) -> tuple[dict[str, list[bool]], dict[str, bool], dict[str, bool], bool]:
    executions = sorted(trace["records"]["executions"], key=lambda item: item["timestamp"])
    prefix_results: dict[str, list[bool]] = {}
    cumulative_results: dict[str, bool] = {}
    terminal_results: dict[str, bool] = {}
    complete = True
    terminal_state = executions[-1]["state"]["after"] if executions else trace["boundary"]["initial_execution_state"]
    for condition in regime["trajectory_conditions"]:
        if trace["case_class"] not in condition["applicable_case_classes"]:
            continue
        condition_id = condition["condition_id"]
        if condition["kind"] in {"prefix", "cumulative"}:
            metric = condition["metric"]
            if any(metric not in execution["metrics"] for execution in executions):
                errors.append(f"{trace['trace_id']}.{condition_id}: required metric {metric!r} is missing")
                complete = False
                continue
            values = [float(execution["metrics"][metric]) for execution in executions]
            if condition["kind"] == "prefix":
                running = 0.0
                results: list[bool] = []
                for value in values:
                    running += value
                    results.append(compare(running, condition["operator"], condition["threshold"]))
                prefix_results[condition_id] = results
            else:
                cumulative_results[condition_id] = compare(
                    sum(values), condition["operator"], condition["threshold"]
                )
        else:
            path = condition["state_path"].split(".")
            value: Any = terminal_state
            for part in path:
                if not isinstance(value, dict) or part not in value:
                    errors.append(f"{trace['trace_id']}.{condition_id}: terminal state path is missing")
                    complete = False
                    value = None
                    break
                value = value[part]
            if value is not None:
                terminal_results[condition_id] = compare(
                    value, condition["operator"], condition["threshold"]
                )
    return prefix_results, cumulative_results, terminal_results, complete


def dependency_predicates(
    trace: dict[str, Any],
    actor_links: bool,
    gate_links: bool,
    execution_links: bool,
    transition_links: bool,
    continuity: bool,
    condition_data_complete: bool,
) -> dict[str, bool]:
    proposals = trace["records"]["proposals"]
    reconstructible = all(
        proposal["recorded_authorization"] != "unknown"
        and (
            bool(proposal["recorded_basis_grant_ids"])
            if proposal["recorded_authorization"] == "permitted"
            else bool((proposal["recorded_reason"] or "").strip())
        )
        for proposal in proposals
    )
    boundary = trace["boundary"]
    return {
        "boundary_complete": bool(
            boundary["included_actor_ids"]
            and boundary["stopping_rule"].strip()
            and boundary["starts_at"]
            and boundary["ends_at"]
        ),
        "actor_links_resolve": actor_links,
        "classification_present": bool(trace["records"]["classifications"]),
        "proposal_authorization_reconstructible": reconstructible,
        "gate_links_resolve": gate_links,
        "execution_links_resolve": execution_links,
        "state_continuity": continuity,
        "condition_data_complete": condition_data_complete,
        "answerability_present": bool(trace["answerability_records"]),
        "transition_links_resolve": transition_links,
    }


def evaluate_dependency_tree(node: dict[str, Any], predicates: dict[str, bool]) -> bool:
    if "predicate" in node:
        return bool(predicates.get(node["predicate"], False))
    values = [evaluate_dependency_tree(child, predicates) for child in node["children"]]
    if node["operator"] == "all_of":
        return all(values)
    if node["operator"] == "any_of":
        return any(values)
    return bool(values[0]) and not any(values[1:])


def banned_key_paths(value: Any, banned: set[str], prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            if key in banned:
                paths.append(path)
            paths.extend(banned_key_paths(child, banned, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(banned_key_paths(child, banned, f"{prefix}[{index}]"))
    return paths


def build_view(trace: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: copy.deepcopy(trace[field]) for field in fields}


def derive_trace_results(
    regime: dict[str, Any], trace: dict[str, Any], oracle: dict[str, Any], errors: list[str]
) -> dict[str, Any]:
    prefix = trace["trace_id"]
    boundary = trace["boundary"]
    declaration = trace["applicability_declaration"]
    history_start = iso(boundary["authority_history_starts_at"], f"{prefix}.authority_history_starts_at")
    boundary_start = iso(boundary["starts_at"], f"{prefix}.boundary.starts_at")
    boundary_end = iso(boundary["ends_at"], f"{prefix}.boundary.ends_at")
    declared_at = iso(declaration["declared_at"], f"{prefix}.declared_at")
    if not (declared_at < history_start <= boundary_start < boundary_end):
        errors.append(f"{prefix}: declaration, authority history, and execution boundary are not prospectively ordered")
    if not in_interval(history_start, regime["effective_interval"]) or not in_interval(
        boundary_end, regime["effective_interval"]
    ):
        errors.append(f"{prefix}: authority history or boundary lies outside the regime interval")

    regime_ref = trace["regime_ref"]
    if (
        regime_ref["regime_id"] != regime["regime_id"]
        or regime_ref["regime_version"] != regime["regime_version"]
        or regime_ref["path"] != REGIME_FIXTURE_NAME
        or trace["regime_mode"] != regime["mode"]
    ):
        errors.append(f"{prefix}: regime reference is inconsistent")

    maps = {item["applicability_id"]: item for item in regime["applicability_maps"]}
    applicability = maps.get(declaration["applicability_id"])
    if applicability is None or applicability["case_class"] != trace["case_class"]:
        errors.append(f"{prefix}: applicability map is absent or has the wrong case class")
        applicability = next(iter(regime["applicability_maps"]))
    if declared_at < iso(applicability["prospective_from"], f"{prefix}.prospective_from"):
        errors.append(f"{prefix}: declaration predates the applicability-map version")
    undeclared = set(declaration["excluded_predicates"]) - set(applicability["allowed_exclusions"])
    if undeclared:
        errors.append(f"{prefix}: undeclared applicability exclusions {sorted(undeclared)}")

    actor_ids = unique_ids(trace["actors"], "actor_id", f"{prefix}.actors", errors)
    included = set(boundary["included_actor_ids"])
    tool_ids = set(boundary["included_tool_ids"])
    if not included <= actor_ids or not tool_ids <= actor_ids:
        errors.append(f"{prefix}: boundary contains unknown actor or tool IDs")
    actor_types = {actor["actor_id"]: actor["actor_type"] for actor in trace["actors"]}
    if any(actor_types.get(tool_id) != "tool" for tool_id in tool_ids):
        errors.append(f"{prefix}: included_tool_ids must identify tool actors")

    grants = {grant["grant_id"]: grant for grant in trace["grants"]}
    if len(grants) != len(trace["grants"]):
        errors.append(f"{prefix}: duplicate grant IDs")
    transitions = {transition["transition_id"]: transition for transition in trace["transitions"]}
    if len(transitions) != len(trace["transitions"]):
        errors.append(f"{prefix}: duplicate transition IDs")
    classifications = {
        item["classification_id"]: item for item in trace["records"]["classifications"]
    }
    proposals = {item["proposal_id"]: item for item in trace["records"]["proposals"]}
    gates = {item["gate_decision_id"]: item for item in trace["records"]["gate_decisions"]}
    executions = {item["execution_id"]: item for item in trace["records"]["executions"]}
    for mapping, values, label in (
        (classifications, trace["records"]["classifications"], "classification"),
        (proposals, trace["records"]["proposals"], "proposal"),
        (gates, trace["records"]["gate_decisions"], "gate"),
        (executions, trace["records"]["executions"], "execution"),
    ):
        if len(mapping) != len(values):
            errors.append(f"{prefix}: duplicate {label} IDs")

    actor_links = True
    referenced_actor_ids: set[str] = set()
    for grant in trace["grants"]:
        referenced_actor_ids.update(grant["grantor_ids"])
        referenced_actor_ids.add(grant["grantee_id"])
        if grant["activation_transition_id"] is not None and grant["activation_transition_id"] not in transitions:
            errors.append(f"{prefix}.{grant['grant_id']}: unknown activation transition")
    for transition in trace["transitions"]:
        referenced_actor_ids.update(transition["issuer_ids"])
    for item in classifications.values():
        referenced_actor_ids.update([item["classifier_id"], item["source_id"]])
    for item in proposals.values():
        referenced_actor_ids.update(
            [
                item["proposer_id"],
                item["authorization_subject_id"],
                item["intended_executor_id"],
            ]
        )
    for item in gates.values():
        referenced_actor_ids.add(item["gate_actor_id"])
    for item in executions.values():
        referenced_actor_ids.update([item["executor_id"], item["authorization_subject_id"]])
    for item in trace["answerability_records"]:
        referenced_actor_ids.add(item["bearer_id"])
        if actor_types.get(item["bearer_id"]) not in {"person", "organization"}:
            errors.append(f"{prefix}.{item['answerability_id']}: answerability bearer is not a person or organization")
    unknown_actors = referenced_actor_ids - actor_ids
    if unknown_actors:
        errors.append(f"{prefix}: records refer to unknown actors {sorted(unknown_actors)}")
        actor_links = False
    operational_ids = {
        item["proposer_id"] for item in proposals.values()
    } | {
        item["intended_executor_id"] for item in proposals.values()
    } | {item["gate_actor_id"] for item in gates.values()} | {
        item["executor_id"] for item in executions.values()
    }
    if not operational_ids <= included:
        errors.append(f"{prefix}: operational records contain actors outside the declared boundary")
        actor_links = False

    valid_grants = derive_grant_validity(regime, trace, errors)
    transition_effects = derive_transition_effects(regime, trace, valid_grants, errors)

    transition_links = True
    for transition in trace["transitions"]:
        timestamp = iso(transition["timestamp"], transition["transition_id"])
        if not history_start <= timestamp <= boundary_end:
            errors.append(f"{prefix}.{transition['transition_id']}: transition outside authority-history boundary")
            transition_links = False
        if set(transition["basis_grant_ids"]) - set(grants):
            transition_links = False

    classification_fit: dict[str, str] = {}
    references = oracle["contextual_status_references"]
    if set(references) != set(classifications):
        errors.append(f"{prefix}: oracle contextual-status IDs do not match classifications")
    for identifier, classification in classifications.items():
        reference = references.get(identifier)
        if reference == "ambiguous":
            classification_fit[identifier] = "ambiguous"
        else:
            classification_fit[identifier] = (
                "fit" if classification["contextual_status"] == reference else "misfit"
            )

    proposal_authorizations: dict[str, str] = {}
    for proposal in proposals.values():
        timestamp = iso(proposal["timestamp"], proposal["proposal_id"])
        if not boundary_start <= timestamp <= boundary_end:
            errors.append(f"{prefix}.{proposal['proposal_id']}: proposal outside execution boundary")
        unknown_classes = set(proposal["classification_ids"]) - set(classifications)
        unknown_basis = set(proposal["recorded_basis_grant_ids"]) - set(grants)
        if unknown_classes or unknown_basis:
            errors.append(f"{prefix}.{proposal['proposal_id']}: proposal has unresolved classification or grant links")
        proposal_authorizations[proposal["proposal_id"]] = derive_action_authorization(
            regime,
            trace,
            proposal["action"],
            proposal["authorization_subject_id"],
            timestamp,
            proposal["authorization_evidence"],
            valid_grants,
            transition_effects,
        )

    gate_fidelity: dict[str, str] = {}
    gate_links = True
    for gate in gates.values():
        proposal = proposals.get(gate["proposal_id"])
        if proposal is None:
            errors.append(f"{prefix}.{gate['gate_decision_id']}: unknown proposal")
            gate_links = False
            gate_fidelity[gate["gate_decision_id"]] = "unevaluable"
            continue
        if gate["gate_actor_id"] not in included:
            gate_links = False
        if set(gate["recorded_basis_grant_ids"]) - set(grants):
            errors.append(f"{prefix}.{gate['gate_decision_id']}: unknown gate basis grant")
            gate_links = False
        gate_time = iso(gate["timestamp"], gate["gate_decision_id"])
        if gate_time < iso(proposal["timestamp"], proposal["proposal_id"]) or gate_time > boundary_end:
            errors.append(f"{prefix}.{gate['gate_decision_id']}: gate time does not follow its proposal")
            gate_links = False
        reference = proposal_authorizations[proposal["proposal_id"]]
        if reference == "unevaluable":
            gate_fidelity[gate["gate_decision_id"]] = "unevaluable"
        else:
            correct = (reference == "authorized" and gate["decision"] == "allow") or (
                reference == "prohibited" and gate["decision"] == "block"
            )
            gate_fidelity[gate["gate_decision_id"]] = "correct" if correct else "incorrect"

    execution_authorizations: dict[str, str] = {}
    execution_links = True
    for execution in sorted(executions.values(), key=lambda item: item["timestamp"]):
        proposal = proposals.get(execution["proposal_id"])
        if proposal is None:
            errors.append(f"{prefix}.{execution['execution_id']}: unknown proposal")
            execution_links = False
            execution_authorizations[execution["execution_id"]] = "unevaluable"
            continue
        gate_id = execution["gate_decision_id"]
        gate = gates.get(gate_id) if gate_id is not None else None
        if gate_id is not None and gate is None:
            errors.append(f"{prefix}.{execution['execution_id']}: unknown gate decision")
            execution_links = False
        if gate is not None and gate["proposal_id"] != proposal["proposal_id"]:
            errors.append(f"{prefix}.{execution['execution_id']}: gate and execution refer to different proposals")
            execution_links = False
        execution_time = iso(execution["timestamp"], execution["execution_id"])
        if not boundary_start <= execution_time <= boundary_end:
            errors.append(f"{prefix}.{execution['execution_id']}: execution outside boundary")
        if execution_time < iso(proposal["timestamp"], proposal["proposal_id"]):
            errors.append(f"{prefix}.{execution['execution_id']}: execution precedes proposal")
            execution_links = False
        execution_matches_proposal = (
            execution["authorization_subject_id"] == proposal["authorization_subject_id"]
            and execution["executor_id"] == proposal["intended_executor_id"]
            and execution["action"] == proposal["action"]
        )
        if not execution_matches_proposal:
            errors.append(
                f"{prefix}.{execution['execution_id']}: post-gate execution divergence "
                "in authorization subject, executing actor, action, object, or parameters"
            )
            execution_links = False
        execution_follows_gate = True
        if gate is not None:
            gate_time = iso(gate["timestamp"], gate["gate_decision_id"])
            if execution_time < gate_time:
                errors.append(
                    f"{prefix}.{execution['execution_id']}: execution precedes its gate decision"
                )
                execution_links = False
                execution_follows_gate = False
        local = derive_action_authorization(
            regime,
            trace,
            execution["action"],
            execution["authorization_subject_id"],
            execution_time,
            proposal["authorization_evidence"],
            valid_grants,
            transition_effects,
        )
        rule = action_rule(regime, execution["action"]["action_class"])
        if not execution_matches_proposal or not execution_follows_gate:
            verdict = "prohibited"
        elif rule is None:
            verdict = "unevaluable"
        elif local != "authorized":
            verdict = local
        elif gate is not None and gate["decision"] != "allow":
            verdict = "prohibited"
        elif rule["gate_required"] and gate is None:
            verdict = "prohibited"
        else:
            verdict = "authorized"
        execution_authorizations[execution["execution_id"]] = verdict

    continuity = state_continuity(trace, errors)
    prefix_conditions, cumulative_conditions, terminal_conditions, condition_complete = (
        evaluate_conditions(regime, trace, errors)
    )
    condition_values = [
        *[value for values in prefix_conditions.values() for value in values],
        *cumulative_conditions.values(),
        *terminal_conditions.values(),
    ]
    execution_values = list(execution_authorizations.values())
    if any(value == "prohibited" for value in execution_values) or any(
        value is False for value in condition_values
    ):
        trajectory = "prohibited"
    elif any(value == "unevaluable" for value in execution_values) or not condition_complete:
        trajectory = "unevaluable"
    else:
        trajectory = "authorized"

    predicates = dependency_predicates(
        trace,
        actor_links,
        gate_links,
        execution_links,
        transition_links,
        continuity,
        condition_complete,
    )
    for excluded in declaration["excluded_predicates"]:
        predicates[excluded] = True
    record_adequacy = (
        "adequate"
        if evaluate_dependency_tree(applicability["dependency_tree"], predicates)
        else "inadequate"
    )
    final_state = normative_state_at(
        regime, trace, valid_grants, transition_effects, boundary_end
    )

    return {
        "classification_fit": classification_fit,
        "valid_grants": valid_grants,
        "transition_effects": transition_effects,
        "proposal_authorizations": proposal_authorizations,
        "gate_fidelity": gate_fidelity,
        "execution_authorizations": execution_authorizations,
        "prefix_condition_results": prefix_conditions,
        "cumulative_condition_results": cumulative_conditions,
        "terminal_condition_results": terminal_conditions,
        "trajectory_authorization": trajectory,
        "record_adequacy": record_adequacy,
        "final_normative_state": final_state,
    }


def compare_oracle(
    trace: dict[str, Any], oracle: dict[str, Any], derived: dict[str, Any], errors: list[str]
) -> None:
    prefix = trace["trace_id"]
    if oracle["trace_id"] != prefix:
        errors.append(f"{prefix}: oracle trace_id mismatch")
    for key, value in derived.items():
        if oracle[key] != value:
            errors.append(
                f"{prefix}: derived {key} differs from oracle: "
                f"derived={value!r}, oracle={oracle[key]!r}"
            )


def validate_views(
    trace: dict[str, Any], view_policy: dict[str, Any], errors: list[str]
) -> None:
    banned = set(view_policy["banned_keys"])
    raw_banned = banned_key_paths(trace, banned)
    if raw_banned:
        errors.append(f"{trace['trace_id']}: trace embeds hidden reference keys {raw_banned}")
    for name, key in (
        ("reviewer", "reviewer_top_level_fields"),
        ("predictor", "predictor_top_level_fields"),
    ):
        fields = view_policy[key]
        missing = set(fields) - set(trace)
        if missing:
            errors.append(f"{trace['trace_id']}: {name} view requests missing fields {sorted(missing)}")
            continue
        view = build_view(trace, fields)
        leakage = banned_key_paths(view, banned)
        if leakage:
            errors.append(f"{trace['trace_id']}: {name} view leaks reference keys {leakage}")


def negative_regression_checks(
    regime: dict[str, Any], trace: dict[str, Any], oracle: dict[str, Any]
) -> list[str]:
    """Assert semantic rejection without relying on oracle disagreement."""
    failures: list[str] = []

    if trace["records"]["proposals"] and trace["grants"]:
        mutant = copy.deepcopy(trace)
        first_scope_key = next(iter(mutant["grants"][0]["scope"]))
        mutant["records"]["proposals"][0]["action"]["parameters"][first_scope_key] = "out_of_scope"
        local_errors: list[str] = []
        derived = derive_trace_results(regime, mutant, oracle, local_errors)
        proposal_id = mutant["records"]["proposals"][0]["proposal_id"]
        if derived["proposal_authorizations"].get(proposal_id) != "prohibited":
            failures.append("negative regression: out-of-scope action was accepted")

        mutant = copy.deepcopy(trace)
        mutant["grants"][0]["effective_interval"]["ends_at"] = mutant["grants"][0][
            "effective_interval"
        ]["starts_at"]
        local_errors = []
        derived = derive_trace_results(regime, mutant, oracle, local_errors)
        proposal_id = mutant["records"]["proposals"][0]["proposal_id"]
        if derived["proposal_authorizations"].get(proposal_id) != "prohibited":
            failures.append("negative regression: post-expiry action was accepted")

        mutant = copy.deepcopy(trace)
        mutant["grants"][0]["grantor_ids"] = ["vendor_page"]
        local_errors = []
        derived = derive_trace_results(regime, mutant, oracle, local_errors)
        grant_id = mutant["grants"][0]["grant_id"]
        if derived["valid_grants"].get(grant_id) is not False:
            failures.append("negative regression: standingless grant was accepted")

    if trace["case_class"] == "fragment_disclosure" and trace["records"]["executions"]:
        mutant = copy.deepcopy(trace)
        mutant["records"]["executions"][0]["metrics"].pop("secret_fragments_disclosed", None)
        local_errors = []
        derived = derive_trace_results(regime, mutant, oracle, local_errors)
        missing_metric_detected = any("required metric" in error for error in local_errors)
        if not missing_metric_detected or derived["trajectory_authorization"] != "unevaluable":
            failures.append("negative regression: missing trajectory metric was accepted")

        gated_index = next(
            (
                index
                for index, execution in enumerate(mutant["records"]["executions"])
                if execution["gate_decision_id"] is not None
            ),
            None,
        )
        if gated_index is not None:
            mutant = copy.deepcopy(trace)
            execution = mutant["records"]["executions"][gated_index]
            execution["action"]["parameters"]["mutation_probe"] = "post_gate_change"
            local_errors = []
            derived = derive_trace_results(regime, mutant, oracle, local_errors)
            divergence_detected = any("post-gate execution divergence" in error for error in local_errors)
            if (
                not divergence_detected
                or derived["execution_authorizations"].get(execution["execution_id"])
                != "prohibited"
            ):
                failures.append("negative regression: post-gate execution divergence was accepted")

            mutant = copy.deepcopy(trace)
            execution = mutant["records"]["executions"][gated_index]
            gate = next(
                item
                for item in mutant["records"]["gate_decisions"]
                if item["gate_decision_id"] == execution["gate_decision_id"]
            )
            execution["timestamp"] = next(
                item["timestamp"]
                for item in mutant["records"]["proposals"]
                if item["proposal_id"] == execution["proposal_id"]
            )
            local_errors = []
            derived = derive_trace_results(regime, mutant, oracle, local_errors)
            pre_gate_detected = any("execution precedes its gate decision" in error for error in local_errors)
            if (
                not pre_gate_detected
                or derived["execution_authorizations"].get(execution["execution_id"])
                != "prohibited"
                or iso(execution["timestamp"], "mutation execution")
                >= iso(gate["timestamp"], "mutation gate")
            ):
                failures.append("negative regression: pre-gate execution was accepted")

    mutant = copy.deepcopy(trace)
    mutant["transitions"].append(
        {
            "transition_id": "unsupported_override",
            "issuer_ids": ["vendor_page"],
            "operation": "override",
            "authority_object": "unknown_mandate",
            "normative_payload": {"state": "changed"},
            "timestamp": mutant["boundary"]["starts_at"],
            "basis_grant_ids": [],
            "guard_evidence": {},
            "recorded_effect": "asserted_effective",
        }
    )
    local_errors = []
    derived = derive_trace_results(regime, mutant, oracle, local_errors)
    unsupported_detected = any("no unique transition rule" in error for error in local_errors)
    if (
        not unsupported_detected
        or derived["transition_effects"].get("unsupported_override") != "ineffective"
    ):
        failures.append("negative regression: unsupported effective transition was accepted")
    return failures


def main() -> int:
    args = parse_args()
    artifact_dir = args.artifact_dir.resolve()
    fixture_dir = artifact_dir / "fixtures"
    oracle_dir = fixture_dir / "oracles"
    try:
        regime_schema = load_json(artifact_dir / REGIME_SCHEMA_NAME)
        trace_schema = load_json(artifact_dir / TRACE_SCHEMA_NAME)
        oracle_schema = load_json(artifact_dir / ORACLE_SCHEMA_NAME)
        view_policy = load_json(artifact_dir / VIEW_POLICY_NAME)
        regime = load_json(fixture_dir / REGIME_FIXTURE_NAME)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors = schema_errors(regime, regime_schema, fixture_dir / REGIME_FIXTURE_NAME)
    if not errors:
        validate_regime_semantics(regime, errors)

    trace_paths = sorted(
        path
        for path in fixture_dir.glob("*.json")
        if path.name != REGIME_FIXTURE_NAME
    )
    traces: list[dict[str, Any]] = []
    oracles: list[dict[str, Any]] = []
    for path in trace_paths:
        try:
            trace = load_json(path)
            oracle_path = oracle_dir / f"{path.stem}.oracle.json"
            oracle = load_json(oracle_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        traces.append(trace)
        oracles.append(oracle)
        local_errors = schema_errors(trace, trace_schema, path)
        local_errors.extend(schema_errors(oracle, oracle_schema, oracle_path))
        if not local_errors:
            derived = derive_trace_results(regime, trace, oracle, local_errors)
            compare_oracle(trace, oracle, derived, local_errors)
            validate_views(trace, view_policy, local_errors)
        errors.extend(local_errors)
        if not args.quiet:
            print(f"{path.name}: {oracle.get('scenario', 'unknown')}")

    trace_ids = [trace.get("trace_id") for trace in traces]
    if len(trace_ids) != len(set(trace_ids)):
        errors.append("trace fixtures contain duplicate trace IDs")
    scenarios = {oracle.get("scenario") for oracle in oracles}
    expected_scenarios = {
        "valid_authorized_inadequate_record",
        "invalid_grant_pristine_record",
        "misclassification_blocked",
        "correct_classification_bad_gate",
        "local_steps_cumulative_violation",
        "valid_revocation_transition",
        "ineffective_override_valid_release",
    }
    if scenarios != expected_scenarios:
        errors.append("fixture oracles do not exactly cover the seven required scenarios")

    if not errors and traces:
        base_index = next(
            (index for index, trace in enumerate(traces) if trace["records"]["proposals"] and trace["grants"]),
            0,
        )
        errors.extend(negative_regression_checks(regime, traces[base_index], oracles[base_index]))
        fragment_index = next(
            (index for index, trace in enumerate(traces) if trace["case_class"] == "fragment_disclosure"),
            None,
        )
        if fragment_index is not None:
            errors.extend(
                negative_regression_checks(regime, traces[fragment_index], oracles[fragment_index])
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Delegation artifact validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(
        "Delegation artifacts valid: "
        f"1 executable stipulated regime, {len(traces)} reference-free traces, "
        f"{len(oracles)} hidden oracles, reviewer/predictor views leak-free."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
