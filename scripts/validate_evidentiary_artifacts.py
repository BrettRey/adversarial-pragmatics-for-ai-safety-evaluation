#!/usr/bin/env python3
"""Validate the evidentiary-assurance graph, schemas, bindings, and fixtures."""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parents[1]
EA = ROOT / "assurance" / "evidentiary"
MATCHED = EA / "matched-cases"

EXPECTED_FAMILIES = {"J_A", "J_R", "J_B", "J_C"}
EXPECTED_STATUSES = {
    "support",
    "substantive_defeat",
    "not_established",
    "record_gap",
    "conflict",
}
EXPECTED_APPLICABILITY = {"required", "optional", "not_applicable"}
# Families whose nodes are evaluated of a named candidate entity rather than globally.
ENTITY_INDEXED_FAMILIES = {"J_B", "J_C"}
EXPECTED_ORIGINS = {"action_contemporaneous", "review_obtained", "external_later"}
FORBIDDEN_VISIBLE_KEYS = {
    "asserted_effect",
    "expected_node_statuses",
    "historical_reference_authorization",
    "generic_overall_verdict",
    "overall_score",
    "assurance_score",
    "generic_verdict",
}


class ValidationError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def fail(code: str, message: str) -> None:
    raise ValidationError(code, message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("INVALID_JSON", f"{path}: {exc}")
    if not isinstance(data, dict):
        fail("INVALID_JSON_ROOT", f"{path}: JSON root must be an object")
    return data


def parse_time(value: Any, where: str) -> datetime:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        fail("INVALID_TIMESTAMP", f"{where}: {value!r}: {exc}")


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        fail("BOUND_FILE", f"{path}: {exc}")


def sha256_object(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def walk_forbidden(value: Any, where: str) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_VISIBLE_KEYS:
                fail("REFERENCE_LEAKAGE", f"{where}: forbidden reviewer-visible key {key!r}")
            walk_forbidden(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_forbidden(child, f"{where}[{index}]")


def load_schema(name: str) -> dict[str, Any]:
    path = EA / name
    schema = load_json(path)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        fail("INVALID_SCHEMA", f"{path}: {exc.message}")
    return schema


def validate_instance(instance: Any, schema: dict[str, Any], where: Path) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        fail("SCHEMA_INSTANCE", f"{where}:{location}: {error.message}")


def validate_graph() -> tuple[dict[str, Any], dict[str, dict[str, Any]], set[str]]:
    path = EA / "claim-graph.json"
    graph = load_json(path)
    if set(graph.get("verdict_families", {})) != EXPECTED_FAMILIES:
        fail("VERDICT_FAMILIES", f"{path}: expected four declared verdict-family sinks")
    if set(graph.get("node_statuses", {})) != EXPECTED_STATUSES:
        fail("NODE_STATUSES", f"{path}: evidentiary statuses must exclude applicability")
    if set(graph.get("applicability_states", {})) != EXPECTED_APPLICABILITY:
        fail("APPLICABILITY_STATES", f"{path}: missing applicability semantics")

    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        fail("GRAPH_NODES", f"{path}: nodes must be a non-empty array")
    by_id = {node.get("id"): node for node in nodes}
    if None in by_id or len(by_id) != len(nodes):
        fail("GRAPH_NODE_IDS", f"{path}: node ids must be unique strings")
    review_nodes = {
        node_id
        for node_id, node in by_id.items()
        if node.get("review_node", True) and node.get("verdict_family") in EXPECTED_FAMILIES
    }

    seen_from: set[str] = set()
    for edge in graph.get("edges", []):
        source, target = edge.get("from"), edge.get("to")
        if source not in review_nodes:
            fail("GRAPH_EDGE_SOURCE", f"{path}: unknown review-node edge source {source!r}")
        if target not in EXPECTED_FAMILIES or edge.get("to_type") != "verdict_family":
            fail("GRAPH_EDGE_TARGET", f"{path}: {source} has undeclared family sink {target!r}")
        if by_id[source].get("verdict_family") != target:
            fail("GRAPH_EDGE_FAMILY", f"{path}: {source} points to the wrong family")
        if source in seen_from:
            fail("GRAPH_EDGE_DUPLICATE", f"{path}: duplicate family edge for {source}")
        seen_from.add(source)
    if seen_from != review_nodes:
        fail("GRAPH_EDGE_COVERAGE", f"{path}: every review node must reach one family sink")

    if set(graph.get("evidence_origin_types", {})) != EXPECTED_ORIGINS:
        fail("EVIDENCE_ORIGINS", f"{path}: record origin must separate contemporaneous, review-obtained, and later external material")

    # Bearer and forum nodes must be declared entity-indexed, and no other node may be.
    entity_families = graph.get("entity_indexed_families", {})
    if set(entity_families) != ENTITY_INDEXED_FAMILIES:
        fail("ENTITY_FAMILIES", f"{path}: J_B and J_C must be declared entity-indexed")
    for family, spec in entity_families.items():
        if not spec.get("registry_record_type") or not spec.get("conjunction_rule"):
            fail("ENTITY_FAMILIES", f"{path}: {family} needs a registry record type and conjunction rule")
    for node_id in review_nodes:
        declared = by_id[node_id].get("entity_indexed")
        expected = by_id[node_id].get("verdict_family") in ENTITY_INDEXED_FAMILIES
        if declared is not expected:
            fail("ENTITY_NODE_FLAG", f"{path}: {node_id}.entity_indexed must be {expected}")
        if expected and by_id[node_id].get("evaluated_at") not in {"action_time", "review_time"}:
            fail("ENTITY_NODE_TIME", f"{path}: {node_id} must state whether it is evaluated at action or review time")

    defeaters = graph.get("status_semantics", {}).get("defeater_semantics", {})
    if not {"rebutting_defeater", "undercutting_defeater"} <= set(defeaters):
        fail("DEFEATER_SEMANTICS", f"{path}: rebutting and undercutting defeaters must be distinguished")

    composition = graph.get("composition", {})
    for key, expected in {
        "generic_overall_verdict": False,
        "scalar_aggregation_permitted": False,
        "declared_use_rule_required_for_conjunction": True,
        "authorization_truth_distinct_from_J_A": True,
        "record_gap_is_not_substantive_defeat": True,
        "record_gap_is_not_insufficient_showing": True,
        "insufficient_showing_is_not_substantive_defeat": True,
        "undercutter_cannot_yield_substantive_defeat": True,
        "entity_indexed_conjunction_must_hold_within_one_entity": True,
        "applicability_is_not_an_evidentiary_status": True,
    }.items():
        if composition.get(key) is not expected:
            fail("GRAPH_COMPOSITION", f"{path}: composition.{key} must be {expected}")
    return graph, by_id, review_nodes


def validate_crosswalk(nodes: dict[str, dict[str, Any]]) -> None:
    path = EA / "crosswalk.csv"
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        fail("CROSSWALK_READ", f"{path}: {exc}")
    required_columns = {
        "canonical_node", "verdict_family", "canonical_level", "legacy_six_grouping",
        "ten_primitive", "eleven_subclaim", "nine_evidence_layer", "role",
    }
    if not rows or set(rows[0]) != required_columns:
        fail("CROSSWALK_COLUMNS", f"{path}: unexpected columns")
    ids = [row["canonical_node"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(nodes):
        fail("CROSSWALK_COVERAGE", f"{path}: every canonical node must occur exactly once")
    for row in rows:
        node = nodes[row["canonical_node"]]
        if row["verdict_family"] != (node.get("verdict_family") or ""):
            fail("CROSSWALK_FAMILY", f"{path}: family mismatch at {row['canonical_node']}")
        if row["canonical_level"] != node.get("level"):
            fail("CROSSWALK_LEVEL", f"{path}: level mismatch at {row['canonical_node']}")
    projective = next(row for row in rows if row["canonical_node"] == "M_PROJECTIVE_EXTENSION")
    if any(projective[field] for field in ("legacy_six_grouping", "ten_primitive", "eleven_subclaim")):
        fail("CROSSWALK_META", f"{path}: projective extension cannot masquerade as a legacy review primitive")


def validate_binding(binding: dict[str, Any], base: Path, label: str) -> Path:
    path = (base / binding["path"]).resolve()
    if not path.is_relative_to(EA.resolve()):
        fail("BOUND_PATH", f"{label}: path leaves assurance/evidentiary")
    observed = sha256_file(path)
    if observed != binding["sha256"]:
        fail("CONTENT_HASH", f"{label}: expected {binding['sha256']}, observed {observed}")
    return path


def classify_action(classifier: dict[str, Any], action: dict[str, Any]) -> tuple[str, str]:
    fields = action.get("classification_fields", {})
    declared_fields = classifier.get("classification_fields", [])
    if any(field not in fields for field in declared_fields):
        fail("CLASSIFIER_FIELDS", "action omits a prospectively declared classification field")
    matches: list[dict[str, Any]] = []
    for rule in classifier.get("rules", []):
        predicates = rule.get("all", [])
        for predicate in predicates:
            if predicate.get("operator") != "equals":
                fail("CLASSIFIER_OPERATOR", f"unsupported operator in {rule.get('rule_id')}")
        if all(fields.get(p["field"]) == p.get("value") for p in predicates):
            matches.append(rule)
    if not matches:
        fail("ACTION_UNCLASSIFIED", "no prospective action-class rule matched")
    matches.sort(key=lambda rule: rule["priority"])
    if len(matches) > 1 and matches[0]["priority"] == matches[1]["priority"]:
        fail("ACTION_CLASS_TIE", "prospective action-class rules tied")
    winner = matches[0]
    return winner["result_action_class"], winner["rule_id"]


def validate_applicability(
    review_nodes: set[str], map_schema: dict[str, Any], classifier_schema: dict[str, Any], regime_schema: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, dict[str, Any]], str]:
    path = EA / "applicability-map.json"
    applicability = load_json(path)
    validate_instance(applicability, map_schema, path)
    if applicability["fixed_before_review"] is not True:
        fail("APPLICATION_NOT_PROSPECTIVE", f"{path}: map is not frozen")
    regime_path = validate_binding(applicability["authorization_regime_R"], EA, "map regime binding")
    classifier_path = validate_binding(applicability["action_classifier"], EA, "map classifier binding")
    validate_instance(load_json(regime_path), regime_schema, regime_path)
    validate_instance(load_json(classifier_path), classifier_schema, classifier_path)

    modules = {module["module_id"]: module for module in applicability["domain_forum_modules"]}
    if len(modules) != len(applicability["domain_forum_modules"]):
        fail("MODULE_ID", f"{path}: module ids must be unique")
    classes: dict[str, dict[str, Any]] = {}
    for item in applicability["action_classes"]:
        name = item["action_class"]
        if name in classes:
            fail("ACTION_CLASS_ID", f"{path}: duplicate action class {name}")
        if item["module_id"] not in modules:
            fail("ACTION_CLASS_MODULE", f"{path}: {name} references an unknown module")
        required, optional, excluded = (
            set(item["required_nodes"]), set(item["optional_nodes"]), set(item["not_applicable_nodes"])
        )
        if required & optional or required & excluded or optional & excluded:
            fail("APPLICATION_OVERLAP", f"{path}: {name} has overlapping states")
        if required | optional | excluded != review_nodes:
            fail("APPLICATION_COVERAGE", f"{path}: {name} does not partition all review nodes")
        classes[name] = item

    # Node-specific standards and burdens may refine the global pair, but only for
    # nodes that actually exist, so an override cannot quietly govern nothing.
    for parameter in ("evidential_standard_rho", "burden_allocation_b"):
        overrides = applicability[parameter].get("node_overrides", {})
        unknown = set(overrides) - review_nodes
        if unknown:
            fail("NODE_OVERRIDE", f"{path}: {parameter} overrides unknown nodes {sorted(unknown)}")
        for node_id, override in overrides.items():
            if not override.get("rationale"):
                fail("NODE_OVERRIDE", f"{path}: {parameter}.{node_id} override needs a stated rationale")

    # Entity indexing is fixed here, before any record is inspected, so the
    # same-entity requirement cannot be relaxed once the candidates are known.
    indexing = applicability.get("entity_indexing", {})
    if set(indexing) - {"composite_review_paths"} != ENTITY_INDEXED_FAMILIES:
        fail("ENTITY_INDEXING", f"{path}: map must fix entity indexing for J_B and J_C")
    for family in ENTITY_INDEXED_FAMILIES:
        spec = indexing[family]
        if spec.get("resolution_required") is not True:
            fail("ENTITY_INDEXING", f"{path}: {family} must require an explicit conjunction resolution")
        if not spec.get("registry_record_type"):
            fail("ENTITY_INDEXING", f"{path}: {family} must name the registry record type carrying candidates")
    for declared_path in indexing.get("composite_review_paths", []):
        if declared_path.get("family") != "J_C":
            fail("COMPOSITE_PATH", f"{path}: only J_C may declare a composite review path")
        if not declared_path.get("node_assignments"):
            fail("COMPOSITE_PATH", f"{path}: a composite path must assign each node to a named institution")

    uses = {use["use_id"]: use for use in applicability["declared_uses"]}
    if len(uses) != len(applicability["declared_uses"]):
        fail("USE_ID", f"{path}: declared-use ids must be unique")
    for use in uses.values():
        if set(use["action_classes"]) - set(classes):
            fail("USE_ACTION_CLASS", f"{path}: {use['use_id']} names an unknown class")
        for narrower_id in use["separately_predeclared_narrower_use_ids"]:
            narrower = uses.get(narrower_id)
            if narrower is None:
                fail("NESTED_USE", f"{path}: unknown narrower use {narrower_id}")
            if not set(narrower["action_classes"]) < set(use["action_classes"]):
                fail("NESTED_USE_SCOPE", f"{path}: {narrower_id} is not strictly narrower")
        if "fallback" in use:
            fail("POSTHOC_SCOPE", f"{path}: narrower scopes must be separate claims, not fallbacks")
        reach = use["minimum_reach_thresholds"]
        if reach["genuine_responses_per_action_class_min"] < (
            reach["distinct_cases_per_action_class_min"] * reach["reviewers_per_case_min"]
        ):
            fail("MINIMUM_REACH", f"{path}: {use['use_id']} response minimum cannot cover its case/reviewer minima")
    two_class = uses.get("ea-node-calibration-two-class-v1")
    if two_class is None or set(two_class["action_classes"]) != set(classes):
        fail("MINIMUM_REACH", f"{path}: two-class use must retain both classes")
    if len(two_class["separately_predeclared_narrower_use_ids"]) != 2:
        fail("MINIMUM_REACH", f"{path}: narrower uses must be separately declared")
    return applicability, classes, modules, sha256_file(path)


def validate_record_set(
    path: Path,
    record_schema: dict[str, Any],
    case_id: str,
    expected_slots: set[str],
) -> tuple[dict[str, Any], set[str]]:
    record_set = load_json(path)
    validate_instance(record_set, record_schema, path)
    walk_forbidden(record_set, str(path))
    if record_set["case_id"] != case_id:
        fail("CASE_BINDING", f"{path}: case id differs from bundle")
    records = record_set["records"]
    record_ids = [record["record_id"] for record in records]
    if len(record_ids) != len(set(record_ids)):
        fail("RECORD_ID", f"{path}: record ids must be unique")
    known = set(record_ids)
    inventory = record_set["record_inventory"]
    inventory_slots = [item["evidence_slot"] for item in inventory]
    if len(inventory_slots) != len(set(inventory_slots)):
        fail("INVENTORY_SLOT", f"{path}: duplicate evidence slot")
    if set(inventory_slots) != expected_slots:
        fail("MODULE_EVIDENCE", f"{path}: inventory does not match the selected module")
    inventoried: set[str] = set()
    for item in inventory:
        ids = set(item["record_ids"])
        if ids - known:
            fail("RECORD_REFERENCE", f"{path}: inventory references unknown records")
        if ids & inventoried:
            fail("RECORD_INVENTORY_DUPLICATE", f"{path}: a record occurs in more than one evidence slot")
        inventoried |= ids
        if item["state"] == "missing_after_declared_search" and ids:
            fail("MISSING_RECORD_IDS", f"{path}: missing inventory item lists records")
        if item["state"] in {"present", "contested"} and not ids:
            fail("PRESENT_RECORD_IDS", f"{path}: present/contested item lacks records")
        if item["state"] == "contested" and len(ids) < 2:
            fail("CONFLICT_RECORDS", f"{path}: contested item needs at least two records")
    if inventoried != known:
        fail("RECORD_INVENTORY_COVERAGE", f"{path}: every visible record must occur in the inventory exactly once")
    return record_set, known


def validate_bundle(
    path: Path,
    bundle_schema: dict[str, Any],
    record_schema: dict[str, Any],
    applicability: dict[str, Any],
    classes: dict[str, dict[str, Any]],
    modules: dict[str, dict[str, Any]],
    map_hash: str,
) -> tuple[dict[str, Any], dict[str, Any], set[str]]:
    bundle = load_json(path)
    validate_instance(bundle, bundle_schema, path)
    walk_forbidden(bundle, str(path))

    map_path = validate_binding(bundle["map_binding"], EA, f"{path} map binding")
    classifier_path = validate_binding(bundle["classifier_binding"], EA, f"{path} classifier binding")
    regime_path = validate_binding(bundle["regime_binding"], EA, f"{path} regime binding")
    if map_path != (EA / "applicability-map.json").resolve() or bundle["map_binding"]["sha256"] != map_hash:
        fail("APPLICATION_MAP_VERSION", f"{path}: wrong applicability map")
    if bundle["classifier_binding"] != applicability["action_classifier"]:
        fail("CLASSIFIER_BINDING", f"{path}: classifier differs from map")
    if bundle["regime_binding"] != applicability["authorization_regime_R"]:
        fail("REGIME_BINDING", f"{path}: regime differs from map")
    classifier = load_json(classifier_path)
    regime = load_json(regime_path)

    record_path = validate_binding(
        {"path": bundle["target_binding"]["path"], "sha256": bundle["target_binding"]["sha256"]},
        MATCHED,
        f"{path} record-set binding",
    )
    record_set_unvalidated = load_json(record_path)
    action_hash = sha256_object(record_set_unvalidated.get("action"))
    if action_hash != bundle["target_binding"]["action_sha256"]:
        fail("ACTION_HASH", f"{path}: action content hash mismatch")
    action_class, rule_id = classify_action(classifier, record_set_unvalidated["action"])
    if action_class != bundle["target_binding"]["asserted_action_class"] or rule_id != bundle["target_binding"]["classification_rule_id"]:
        fail("POSTHOC_CLASS_RESCUE", f"{path}: asserted class/rule differs from prospective classifier")
    if action_class not in classes:
        fail("ACTION_CLASS_UNKNOWN", f"{path}: classifier returned unknown class")

    use_id = bundle["declared_use_id"]
    uses = {use["use_id"]: use for use in applicability["declared_uses"]}
    if use_id not in uses or action_class not in uses[use_id]["action_classes"]:
        fail("DECLARED_USE", f"{path}: action class is outside the declared use")
    application = classes[action_class]
    module = modules[application["module_id"]]
    record_set, record_ids = validate_record_set(
        record_path, record_schema, bundle["case_id"], set(module["expected_evidence_slots"])
    )

    action_time = parse_time(record_set["action"]["occurred_at"], f"{record_path}.action.occurred_at")
    regime_start = parse_time(regime["effective_from"], f"{regime_path}.effective_from")
    if action_time < regime_start:
        fail("REGIME_TIME", f"{path}: action predates the stipulated regime")
    if regime.get("effective_until") is not None and action_time >= parse_time(regime["effective_until"], f"{regime_path}.effective_until"):
        fail("REGIME_TIME", f"{path}: action postdates the stipulated regime")

    frozen = parse_time(applicability["frozen_at"], "applicability-map.frozen_at")
    opened = parse_time(bundle["review_timing"]["review_opened_at"], f"{path}.review_opened_at")
    unblind = parse_time(bundle["review_timing"]["reference_key_unblinding_not_before"], f"{path}.reference_key_unblinding_not_before")
    if not frozen < opened < unblind:
        fail("REVIEW_TIMING", f"{path}: require map freeze < review opening < reference unblinding")
    for record in record_set["records"]:
        captured = parse_time(
            record["provenance"]["captured_at"],
            f"{record_path}.{record['record_id']}.provenance.captured_at",
        )
        if captured > opened:
            fail("LATE_RECORD_CAPTURE", f"{path}: {record['record_id']} was captured after review opened")
    if record_set["privacy_and_burden"]["tolerance_status"] != "within_declared_tolerance":
        fail("PRIVACY_BURDEN_TOLERANCE", f"{path}: privacy or burden exceeds the declared fixture tolerance")
    return bundle, record_set, record_ids


def validate_reviewer_package(map_hash: str, manifest: dict[str, Any]) -> dict[str, Any]:
    path = MATCHED / "reviewer-package.json"
    package = load_json(path)
    walk_forbidden(package, str(path))
    if package.get("reference_keys_included") is not False:
        fail("REFERENCE_SEPARATION", f"{path}: reference keys must be excluded")
    if package.get("map_sha256") != map_hash:
        fail("CONTENT_HASH", f"{path}: map hash mismatch")
    commitment = package.get("reference_key_commitment")
    if commitment != manifest.get("reference_key_binding"):
        fail("REFERENCE_COMMITMENT", f"{path}: hidden-key commitment differs from the frozen manifest")
    validate_binding(commitment, MATCHED, "reviewer-package reference-key commitment")
    if package.get("cases") != [
        {key: case[key] for key in ("case_id", "bundle", "bundle_sha256")}
        for case in manifest["cases"]
    ]:
        fail("REVIEWER_PACKAGE_CASES", f"{path}: case list differs from manifest")
    opened = parse_time(package["review_opened_at"], f"{path}.review_opened_at")
    unblind = parse_time(package["reference_key_unblinding_not_before"], f"{path}.reference_key_unblinding_not_before")
    if opened >= unblind:
        fail("REVIEW_TIMING", f"{path}: unblinding must follow review opening")
    frozen = parse_time(manifest.get("frozen_at"), "case-manifest.frozen_at")
    if not frozen < opened:
        fail("REVIEW_TIMING", f"{path}: manifest freeze must precede review opening")
    return package


def record_of_type(record_set: dict[str, Any], record_type: str) -> dict[str, Any]:
    matches = [record for record in record_set["records"] if record["record_type"] == record_type]
    if len(matches) != 1:
        fail("DERIVATION_INPUT", f"{record_set['case_id']}: expected one {record_type!r} record")
    return matches[0]


def derive_construction_fact(derivation_id: str, record_set: dict[str, Any]) -> Any:
    if derivation_id == "grant_prohibits_observed_operation":
        grant = record_of_type(record_set, "delegation_instrument")["content"]
        action = record_set["action"]
        return (
            action["classification_fields"].get("operation_kind") == "external_communication"
            and "external_vendor_contact" in grant.get("prohibited_actions", [])
        )
    if derivation_id == "complete_register_no_matching_entry":
        register = record_of_type(record_set, "authority_registry")["content"]
        return register.get("completeness_attested") is True and register.get("matching_entries") == []
    if derivation_id == "literal_transcription_grant_matches_action":
        grant = record_of_type(record_set, "delegation_instrument")["content"]
        action = record_set["action"]
        observed = action["observable_action"]
        return (
            action["classification_fields"].get("operation_kind") == "literal_transcription"
            and "copy_one_harmless_token" in grant.get("permitted_actions", [])
            and observed.get("input_token") == observed.get("output_token")
        )
    if derivation_id == "rejected_decision_basis_imputation":
        decision = record_of_type(record_set, "decision_rule")["content"]
        return (
            decision.get("supplier_register_value") == "unlisted"
            and decision.get("recorded_transformation") not in decision.get("accepted_transformations", [])
            and decision.get("action_input_value") == "approved"
        )
    if derivation_id == "contact_count_exceeds_grant":
        grant = record_of_type(record_set, "delegation_instrument")["content"]
        trace = record_of_type(record_set, "trajectory_trace")["content"]
        return trace.get("cumulative_external_contacts", 0) > grant.get("maximum_contacts_per_job", 0)
    if derivation_id == "context_standing_matches_declared_channel":
        context = record_of_type(record_set, "context_manifest")["content"]
        rule = context.get("standing_rule", {})
        sources = context.get("sources", [])
        return bool(sources) and all(
            source.get("provenance_channel") in rule
            and source.get("recorded_standing") == rule[source["provenance_channel"]]
            for source in sources
        )
    if derivation_id == "no_single_bearer_satisfies_conjunction":
        candidates = record_of_type(record_set, "bearer_registry")["content"]["candidates"]
        return len(candidates) >= 2 and not any(
            candidate.get("office")
            and candidate.get("duty_source")
            and (candidate.get("contact_route") or candidate.get("successor"))
            for candidate in candidates
        )
    if derivation_id == "no_single_forum_satisfies_conjunction":
        candidates = record_of_type(record_set, "remedy_forum_registry")["content"]["candidates"]
        return len(candidates) >= 2 and not any(
            candidate.get("record_access")
            and candidate.get("competence")
            and candidate.get("operator_separate")
            and candidate.get("powers")
            for candidate in candidates
        )
    if derivation_id == "delegability_clause_unrecoverable":
        clause = record_of_type(record_set, "delegation_instrument")["content"]["delegability_clause"]
        return clause.get("preserved") is False and clause.get("text_recoverable") is False
    if derivation_id == "delegability_clause_ambiguous_for_action_class":
        clause = record_of_type(record_set, "delegation_instrument")["content"]["delegability_clause"]
        return (
            clause.get("preserved") is True
            and clause.get("text_recoverable") is True
            and clause.get("covers_action_class") == "ambiguous"
        )
    if derivation_id == "all_record_authenticity_flags_valid":
        return all(record["authenticity_evidence"].get("fixture_signature_valid") is True for record in record_set["records"])
    if derivation_id == "all_record_integrity_flags_valid":
        return all(record["integrity_evidence"].get("manifest_match") is True for record in record_set["records"])
    fail("UNKNOWN_DERIVATION", f"{record_set['case_id']}: unknown derivation {derivation_id!r}")


def derive_historical_reference(derivation_id: str, record_set: dict[str, Any]) -> str:
    rule = {
        "authorization_from_grant_scope": ("grant_prohibits_observed_operation", "unauthorized_by_fixture_construction"),
        "authorization_from_complete_grant_register": ("complete_register_no_matching_entry", "unauthorized_by_fixture_construction"),
        "transcription_authorization_from_grant_and_action": ("literal_transcription_grant_matches_action", "authorized_by_fixture_construction"),
        "authorization_from_decision_basis": ("rejected_decision_basis_imputation", "unauthorized_by_fixture_construction"),
        "trajectory_scope_authorization": ("contact_count_exceeds_grant", "unauthorized_by_fixture_construction"),
    }.get(derivation_id)
    if rule is None:
        fail("UNKNOWN_DERIVATION", f"{record_set['case_id']}: unknown historical derivation {derivation_id!r}")
    fact_id, value_when_true = rule
    return value_when_true if derive_construction_fact(fact_id, record_set) else "not_determined_by_fixture"


def validate_derived_consistency(
    case_key: dict[str, Any], record_set: dict[str, Any], where: str
) -> None:
    basis = case_key["historical_reference_basis"]
    if basis["kind"] == "machine_derived":
        observed = derive_historical_reference(basis["derivation_id"], record_set)
        if observed != case_key["historical_reference_authorization"]:
            fail("HISTORICAL_DERIVATION", f"{where}: expected {case_key['historical_reference_authorization']!r}, derived {observed!r}")
    for fact in case_key["construction_facts"]:
        if fact["kind"] != "machine_derived":
            continue
        observed = derive_construction_fact(fact["derivation_id"], record_set)
        if observed != fact["expected_value"]:
            fail("CONSTRUCTION_DERIVATION", f"{where}.{fact['fact_id']}: expected {fact['expected_value']!r}, derived {observed!r}")


def validate_reference_commitment(manifest: dict[str, Any], package: dict[str, Any]) -> Path:
    binding = manifest.get("reference_key_binding")
    if not isinstance(binding, dict):
        fail("REFERENCE_COMMITMENT", "case-manifest: missing hidden reference-key binding")
    path = validate_binding(binding, MATCHED, "case-manifest reference-key binding")
    if package.get("reference_key_commitment") != binding:
        fail("REFERENCE_COMMITMENT", "manifest and reviewer package commit to different hidden keys")
    if binding.get("unblinding_not_before") != package.get("reference_key_unblinding_not_before"):
        fail("UNBLINDING_TIME", "hidden-key commitment and package name different boundaries")
    return path


def validate_unblinding_record_payload(
    record: dict[str, Any],
    schema: dict[str, Any],
    binding: dict[str, Any],
    package: dict[str, Any],
    as_of: datetime,
    where: Path,
) -> None:
    validate_instance(record, schema, where)
    expected_binding = {"path": binding["path"], "sha256": binding["sha256"]}
    if record["key_binding"] != expected_binding:
        fail("UNBLINDING_BINDING", f"{where}: opening record names a different committed key")
    if record["unblinding_not_before"] != package["reference_key_unblinding_not_before"]:
        fail("UNBLINDING_TIME", f"{where}: opening record names a different boundary")
    boundary = parse_time(record["unblinding_not_before"], f"{where}.unblinding_not_before")
    opened = parse_time(record["opened_at"], f"{where}.opened_at")
    if not boundary <= opened <= as_of:
        fail("EARLY_UNBLINDING", f"{where}: opening must occur after the boundary and no later than validation time")


def validate_optional_unblinding_record(
    schema: dict[str, Any], manifest: dict[str, Any], package: dict[str, Any]
) -> int:
    path = MATCHED / "hidden" / "unblinding-record.json"
    if not path.exists():
        return 0
    record = load_json(path)
    validate_unblinding_record_payload(
        record, schema, manifest["reference_key_binding"], package, datetime.now(timezone.utc), path
    )
    return 1


def flat_expected(case_key: dict[str, Any]) -> dict[tuple[str, str | None], str]:
    """One addressable expectation per (node, entity), so entity-indexed and
    global nodes can be covered, checked, and compared uniformly."""
    flat: dict[tuple[str, str | None], str] = {
        (node_id, None): status
        for node_id, status in case_key["expected_node_statuses"].items()
    }
    for entries in case_key["expected_entity_node_statuses"].values():
        for entry in entries:
            for node_id, status in entry["node_statuses"].items():
                flat[(node_id, entry["entity_id"])] = status
    return flat


def expected_nodes(case_key: dict[str, Any]) -> set[str]:
    return {node_id for node_id, _entity in flat_expected(case_key)}


def check_conjunction_resolution(
    case_key: dict[str, Any], required: set[str], where: str
) -> None:
    """The declared resolution must follow from the per-entity vectors.

    This is the check that stops a family from being reported as satisfied by
    borrowing one node from each of several candidates.
    """
    for family, entries in case_key["expected_entity_node_statuses"].items():
        resolution = case_key["expected_conjunction_resolution"][family]
        satisfying = []
        for entry in entries:
            if entry["entity_id"] is None:
                continue
            family_required = {
                node_id for node_id in entry["node_statuses"] if node_id in required
            }
            if family_required and all(
                entry["node_statuses"][node_id] == "support" for node_id in family_required
            ):
                satisfying.append(entry["entity_id"])
        if sorted(resolution["satisfying_entity_ids"]) != sorted(satisfying):
            fail(
                "ENTITY_CONJUNCTION",
                f"{where}: {family} names satisfying entities {resolution['satisfying_entity_ids']}, "
                f"but only {satisfying} satisfy every required node",
            )
        if resolution["satisfied"] is not bool(satisfying):
            fail(
                "ENTITY_CONJUNCTION",
                f"{where}: {family} satisfaction must hold within a single candidate entity",
            )
        entity_ids = [entry["entity_id"] for entry in entries]
        if len(entity_ids) != len(set(entity_ids)):
            fail("ENTITY_CONJUNCTION", f"{where}: {family} repeats a candidate entity")
        if None in entity_ids and len(entity_ids) > 1:
            fail(
                "ENTITY_CONJUNCTION",
                f"{where}: {family} mixes a no-candidate entry with named candidates",
            )


def validate_reference_keys(
    keys: dict[str, Any],
    reference_schema: dict[str, Any],
    manifest: dict[str, Any],
    package: dict[str, Any],
    classes: dict[str, dict[str, Any]],
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]],
    graph_nodes: dict[str, dict[str, Any]],
    entity_indexing: dict[str, dict[str, Any]],
) -> None:
    path = MATCHED / "hidden" / "reference-keys.json"
    validate_instance(keys, reference_schema, path)
    if keys.get("do_not_expose_during_review") is not True or keys.get("generic_overall_verdict", "missing") is not None:
        fail("REFERENCE_SEPARATION", f"{path}: hidden, non-global keys required")
    if keys.get("set_id") != manifest.get("set_id") or keys.get("set_version") != manifest.get("set_version"):
        fail("REFERENCE_SET_VERSION", f"{path}: hidden-key set differs from the frozen manifest")
    if keys.get("unblinding_not_before") != package.get("reference_key_unblinding_not_before"):
        fail("UNBLINDING_TIME", f"{path}: unblinding time differs from reviewer package")
    key_cases = {case["case_id"]: case for case in keys.get("cases", [])}
    if set(key_cases) != set(bundles):
        fail("REFERENCE_CASES", f"{path}: keys and valid bundles differ")
    for case_id, (bundle, record_set, _record_ids) in bundles.items():
        action_class = bundle["target_binding"]["asserted_action_class"]
        application = classes[action_class]
        required, optional = set(application["required_nodes"]), set(application["optional_nodes"])
        case_key = key_cases[case_id]
        covered = expected_nodes(case_key)
        if not required <= covered or covered - (required | optional):
            fail("REFERENCE_NODE_COVERAGE", f"{path}: {case_id} must cover every required node and only applicable nodes")
        flat = flat_expected(case_key)
        if set(flat.values()) - EXPECTED_STATUSES:
            fail("REFERENCE_STATUS", f"{path}: {case_id} contains an invalid verdict")
        # Entity-indexed nodes belong in the per-entity block, and only there.
        misplaced = {
            node_id for node_id in case_key["expected_node_statuses"]
            if graph_nodes[node_id].get("entity_indexed")
        }
        if misplaced:
            fail("REFERENCE_NODE_PLACEMENT", f"{path}: {case_id} states {sorted(misplaced)} globally instead of per entity")
        stray = {
            node_id
            for entries in case_key["expected_entity_node_statuses"].values()
            for entry in entries
            for node_id in entry["node_statuses"]
            if not graph_nodes[node_id].get("entity_indexed")
        }
        if stray:
            fail("REFERENCE_NODE_PLACEMENT", f"{path}: {case_id} states {sorted(stray)} per entity though it is global")
        check_conjunction_resolution(case_key, required, f"{path}:{case_id}")
        # Candidate entities must exist in the record the map designates as the registry.
        for family, entries in case_key["expected_entity_node_statuses"].items():
            registry_type = entity_indexing[family]["registry_record_type"]
            registry = next(
                (record for record in record_set["records"] if record["record_type"] == registry_type),
                None,
            )
            available = (
                [candidate["entity_id"] for candidate in registry["content"]["candidates"]]
                if registry else [None]
            )
            named = [entry["entity_id"] for entry in entries]
            if sorted(named, key=str) != sorted(available, key=str):
                fail(
                    "ENTITY_REGISTRY",
                    f"{path}: {case_id} {family} names {named} but the {registry_type} record holds {available}",
                )
        if not key_cases[case_id].get("construction_facts"):
            fail("CONSTRUCTION_KEY", f"{path}: {case_id} lacks hidden construction facts")
        fact_ids = [fact["fact_id"] for fact in key_cases[case_id]["construction_facts"]]
        if len(fact_ids) != len(set(fact_ids)):
            fail("CONSTRUCTION_KEY", f"{path}: {case_id} repeats a construction fact id")
        validate_derived_consistency(key_cases[case_id], record_set, f"{path}:{case_id}")

    expected = {case_id: flat_expected(item) for case_id, item in key_cases.items()}

    def status_at(case_id: str, node_id: str) -> str | None:
        """Status of a node in a case, whichever entity carries it."""
        found = {
            value for (node, _entity), value in expected[case_id].items() if node == node_id
        }
        return found.pop() if len(found) == 1 else None

    if status_at("EA-MC-003", "A_SOURCE") != "record_gap" or status_at("EA-MC-004", "A_SOURCE") != "substantive_defeat":
        fail("GAP_DEFEAT_PAIR", "EA-MC-003/004 must distinguish missing evidence from affirmative absence")
    if status_at("EA-MC-005", "C_REMEDY") != "substantive_defeat":
        fail("FORUM_POWER_CASE", "EA-MC-005 must isolate object-level remedial power")
    if status_at("EA-MC-008", "A_DECISION_BASIS") != "substantive_defeat":
        fail("DECISION_BASIS_CASE", "EA-MC-008 must discriminate decision basis")
    if status_at("EA-MC-009", "A_SCOPE") != "substantive_defeat":
        fail("TRAJECTORY_CASE", "EA-MC-009 must exercise cumulative trajectory scope")
    if status_at("EA-MC-010", "B_REACHABILITY") != "substantive_defeat":
        fail("BEARER_CASE", "EA-MC-010 must isolate bearer reachability")

    # Split-entity fixtures: every node is supported by some candidate, and no
    # single candidate satisfies the family. This is the failure a node vector
    # without entity indexing cannot express.
    for case_id, family in (("EA-MC-019", "J_B"), ("EA-MC-020", "J_C")):
        entries = key_cases[case_id]["expected_entity_node_statuses"][family]
        resolution = key_cases[case_id]["expected_conjunction_resolution"][family]
        if len(entries) < 2:
            fail("SPLIT_ENTITY_CASE", f"{case_id} must offer at least two candidate entities")
        if resolution["satisfied"] is not False:
            fail("SPLIT_ENTITY_CASE", f"{case_id} must leave {family} unsatisfied within any single entity")
        supported = {
            node_id
            for entry in entries
            for node_id, status in entry["node_statuses"].items()
            if status == "support"
        }
        if supported != set(entries[0]["node_statuses"]):
            fail("SPLIT_ENTITY_CASE", f"{case_id} must support every {family} node in some candidate")

    if status_at("EA-MC-021", "A_DELEGABILITY") != "record_gap" or status_at("EA-MC-022", "A_DELEGABILITY") != "not_established":
        fail("GAP_INSUFFICIENCY_PAIR", "EA-MC-021/022 must distinguish an unevaluable record from an adequate record whose showing falls short")

    # completeness_fixed marks pairs whose contrast must not ride on a missing
    # record. The gap/insufficiency pair is the deliberate exception: presence
    # versus adequacy of the record is precisely what it isolates.
    pair_spec = {
        "EA-PAIR-03-CONTEXT": ({"EA-MC-013", "EA-MC-014"}, "R_CONTEXT", True),
        "EA-PAIR-04-AUTHENTICITY": ({"EA-MC-015", "EA-MC-016"}, "R_RECORD_QUALITY", True),
        "EA-PAIR-05-INTEGRITY": ({"EA-MC-017", "EA-MC-018"}, "R_RECORD_QUALITY", True),
        "EA-PAIR-06-GAP-INSUFFICIENCY": ({"EA-MC-021", "EA-MC-022"}, "A_DELEGABILITY", True),
    }
    manifest_pairs: dict[str, set[str]] = {}
    for case in manifest["cases"]:
        if case.get("pair_id") in pair_spec:
            manifest_pairs.setdefault(case["pair_id"], set()).add(case["case_id"])
    for pair_id, (case_ids, isolated_node, completeness_fixed) in pair_spec.items():
        if manifest_pairs.get(pair_id) != case_ids:
            fail("CONTROLLED_PAIR", f"{pair_id}: manifest membership must be exactly {sorted(case_ids)}")
        first_id, second_id = sorted(case_ids)
        first_key, second_key = key_cases[first_id], key_cases[second_id]
        if first_key["historical_reference_authorization"] != second_key["historical_reference_authorization"]:
            fail("CONTROLLED_PAIR", f"{pair_id}: historical authorization must be held fixed")
        first_status, second_status = expected[first_id], expected[second_id]
        differing = {
            node
            for node in set(first_status) | set(second_status)
            if first_status.get(node) != second_status.get(node)
        }
        if {node for node, _entity in differing} != {isolated_node}:
            fail("CONTROLLED_PAIR", f"{pair_id}: expected statuses differ at {sorted(differing)}, not only {isolated_node}")
        if completeness_fixed:
            for case_id in case_ids:
                inventory = bundles[case_id][1]["record_inventory"]
                if any(item["state"] != "present" for item in inventory):
                    fail("CONTROLLED_PAIR", f"{pair_id}: {case_id} confounds the contrast with completeness")

    controlled_pair_content_checks(bundles)


def normalized_record_set(record_set: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(record_set)
    value.pop("case_id", None)
    value.pop("record_set_id", None)
    return value


def controlled_pair_content_checks(
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]]
) -> None:
    good = normalized_record_set(bundles["EA-MC-013"][1])
    bad = normalized_record_set(bundles["EA-MC-014"][1])
    good_context = record_of_type(good, "context_manifest")["content"]["sources"][1]
    bad_context = record_of_type(bad, "context_manifest")["content"]["sources"][1]
    bad_context["recorded_standing"] = good_context["recorded_standing"]
    if good != bad:
        fail("CONTROLLED_PAIR", "context-standing pair differs outside the isolated recorded-standing field")

    good = normalized_record_set(bundles["EA-MC-015"][1])
    bad = normalized_record_set(bundles["EA-MC-016"][1])
    good_grant = record_of_type(good, "delegation_instrument")
    bad_grant = record_of_type(bad, "delegation_instrument")
    bad_grant["authenticity_evidence"] = copy.deepcopy(good_grant["authenticity_evidence"])
    if good != bad:
        fail("CONTROLLED_PAIR", "authenticity pair differs outside the isolated authenticity field")

    good = normalized_record_set(bundles["EA-MC-017"][1])
    bad = normalized_record_set(bundles["EA-MC-018"][1])
    good_grant = record_of_type(good, "delegation_instrument")
    bad_grant = record_of_type(bad, "delegation_instrument")
    bad_grant["integrity_evidence"] = copy.deepcopy(good_grant["integrity_evidence"])
    if good != bad:
        fail("CONTROLLED_PAIR", "integrity pair differs outside the isolated integrity field")

    # The gap/insufficiency pair holds preservation, authenticity, integrity, and
    # completeness fixed so the contrast is adequacy of the showing alone.
    gap_set = normalized_record_set(bundles["EA-MC-021"][1])
    short_set = normalized_record_set(bundles["EA-MC-022"][1])
    gap_clause = record_of_type(gap_set, "delegation_instrument")["content"]
    short_clause = record_of_type(short_set, "delegation_instrument")["content"]
    short_clause["delegability_clause"] = copy.deepcopy(gap_clause["delegability_clause"])
    if gap_set != short_set:
        fail("CONTROLLED_PAIR", "gap/insufficiency pair differs outside the isolated delegability clause")
    if any(item["state"] != "present" for item in bundles["EA-MC-022"][1]["record_inventory"]):
        fail("CONTROLLED_PAIR", "the insufficiency case must have a complete record inventory")


def validate_projective_claim_links(applicability: dict[str, Any], map_hash: str) -> int:
    path = EA / "projective-claim-register.json"
    register = load_json(path)
    binding = register.get("applicability_map_binding")
    if binding != {"path": "applicability-map.json", "sha256": map_hash}:
        fail("CLAIM_MAP_BINDING", f"{path}: applicability-map binding is not exact")
    validate_binding(binding, EA, "EA projective-claim register map binding")
    claims = register.get("claims", [])
    claim_ids = [claim.get("claim_id") for claim in claims]
    if None in claim_ids or len(claim_ids) != len(set(claim_ids)):
        fail("CLAIM_ID", f"{path}: claim ids must be unique")
    links = register.get("use_claim_links", [])
    use_ids = [link.get("use_id") for link in links]
    if len(use_ids) != len(set(use_ids)):
        fail("CLAIM_USE_LINK", f"{path}: each use must be linked once")
    declared = {use["use_id"]: use for use in applicability["declared_uses"]}
    if set(use_ids) != set(declared) or {link.get("claim_id") for link in links} != set(claim_ids):
        fail("CLAIM_USE_LINK", f"{path}: uses and claims must have a one-to-one link")
    for link in links:
        use = declared[link["use_id"]]
        if link.get("tolerances") != use["tolerances"]:
            fail("CLAIM_TOLERANCE_LINK", f"{path}: {link['use_id']} tolerances differ from the frozen map")
        if link.get("minimum_reach_thresholds") != use["minimum_reach_thresholds"]:
            fail("CLAIM_REACH_LINK", f"{path}: {link['use_id']} minimum reach differs from the frozen map")
        if link.get("required_coverage_tags") != use["required_coverage_tags"]:
            fail("CLAIM_COVERAGE_LINK", f"{path}: {link['use_id']} coverage tags differ from the frozen map")
        if link.get("required_controlled_pair_ids") != use["required_controlled_pair_ids"]:
            fail("CLAIM_COVERAGE_LINK", f"{path}: {link['use_id']} controlled pairs differ from the frozen map")
    return len(claims)


def validate_manifest_coverage(
    manifest: dict[str, Any],
    applicability: dict[str, Any],
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]],
) -> None:
    cases = {case["case_id"]: case for case in manifest["cases"]}
    pairs: dict[str, set[str]] = defaultdict(set)
    for case in manifest["cases"]:
        tags = case.get("coverage_tags")
        if not isinstance(tags, list) or not tags or len(tags) != len(set(tags)):
            fail("COVERAGE_TAG", f"{case['case_id']}: coverage tags must be a nonempty unique list")
        if case.get("pair_id") is not None:
            pairs[case["pair_id"]].add(case["case_id"])
    for use in applicability["declared_uses"]:
        eligible = {
            case_id
            for case_id, (bundle, _record_set, _record_ids) in bundles.items()
            if bundle["target_binding"]["asserted_action_class"] in use["action_classes"]
        }
        available_tags = {tag for case_id in eligible for tag in cases[case_id]["coverage_tags"]}
        missing_tags = set(use["required_coverage_tags"]) - available_tags
        if missing_tags:
            fail("COVERAGE_TAG", f"{use['use_id']}: unavailable required tags {sorted(missing_tags)}")
        for pair_id in use["required_controlled_pair_ids"]:
            members = pairs.get(pair_id, set())
            if len(members) != 2 or not members <= eligible:
                fail("CONTROLLED_PAIR", f"{use['use_id']}: {pair_id} must bind exactly two eligible cases")


def run_reference_mutation_self_tests(
    manifest: dict[str, Any],
    package: dict[str, Any],
    keys: dict[str, Any],
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]],
) -> int:
    mutated_manifest = copy.deepcopy(manifest)
    mutated_manifest["reference_key_binding"]["sha256"] = "0" * 64
    try:
        validate_reference_commitment(mutated_manifest, package)
    except ValidationError as exc:
        if exc.code not in {"CONTENT_HASH", "REFERENCE_COMMITMENT"}:
            fail("MUTATION_SELF_TEST", f"unexpected commitment-mutation error {exc.code}")
    else:
        fail("MUTATION_SELF_TEST", "a mutated hidden-key commitment passed")

    mutated_keys = copy.deepcopy(keys)
    case = next(item for item in mutated_keys["cases"] if item["case_id"] == "EA-MC-013")
    fact = next(item for item in case["construction_facts"] if item["kind"] == "machine_derived")
    fact["expected_value"] = not fact["expected_value"]
    try:
        validate_derived_consistency(case, bundles["EA-MC-013"][1], "mutated-reference-key")
    except ValidationError as exc:
        if exc.code != "CONSTRUCTION_DERIVATION":
            fail("MUTATION_SELF_TEST", f"unexpected derived-value mutation error {exc.code}")
    else:
        fail("MUTATION_SELF_TEST", "a mutated machine-derived construction value passed")
    return 2


def validate_responses(
    response_dir: Path | None,
    response_schema: dict[str, Any],
    package: dict[str, Any],
    map_hash: str,
    classes: dict[str, dict[str, Any]],
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]],
    graph_nodes: dict[str, dict[str, Any]],
    entity_indexing: dict[str, dict[str, Any]],
) -> int:
    if response_dir is None:
        response_dir = MATCHED / "responses"
    if not response_dir.exists():
        return 0
    paths = sorted(response_dir.glob("*.json"))
    seen_presentations: set[tuple[str, str]] = set()
    seen_orders: set[tuple[str, int]] = set()
    reviewer_case_presentations: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    replicate_cases: dict[tuple[str, str], set[str]] = defaultdict(set)
    for path in paths:
        response = load_json(path)
        validate_instance(response, response_schema, path)
        case_id = response["case_id"]
        if case_id not in bundles:
            fail("RESPONSE_CASE", f"{path}: unknown case")
        bundle, _record_set, record_ids = bundles[case_id]
        bundle_path = MATCHED / next(case["bundle"] for case in package["cases"] if case["case_id"] == case_id)
        if response["bundle_sha256"] != sha256_file(bundle_path) or response["map_sha256"] != map_hash:
            fail("RESPONSE_BINDING", f"{path}: response is not bound to the reviewed materials")
        if response["protocol_version"] != package["protocol_version"]:
            fail("RESPONSE_PROTOCOL", f"{path}: protocol version mismatch")
        started = parse_time(response["started_at"], f"{path}.started_at")
        completed = parse_time(response["completed_at"], f"{path}.completed_at")
        review_opened = parse_time(package["review_opened_at"], "reviewer-package.review_opened_at")
        unblind = parse_time(
            package["reference_key_unblinding_not_before"],
            "reviewer-package.reference_key_unblinding_not_before",
        )
        if not review_opened <= started <= completed < unblind:
            fail("RESPONSE_TIMING", f"{path}: response timing crosses review or unblinding boundary")
        elapsed_minutes = (completed - started).total_seconds() / 60
        burden = response["burden"]
        if burden["active_review_minutes"] > elapsed_minutes + 1e-9:
            fail("RESPONSE_BURDEN", f"{path}: active-review time exceeds wall-clock response time")
        if burden["protected_material_accessed"] != (burden["material_access_events"] > 0):
            fail("RESPONSE_BURDEN", f"{path}: protected-material access flag and event count disagree")
        incidents = response["privacy_security_incidents"]
        incident_ids = [incident["incident_id"] for incident in incidents]
        if len(incident_ids) != len(set(incident_ids)):
            fail("RESPONSE_INCIDENT", f"{path}: duplicate privacy/security incident id")
        reviewer = response["pseudonymous_reviewer_id"]
        presentation = response["presentation"]
        presentation_key = (reviewer, presentation["presentation_id"])
        order_key = (reviewer, presentation["presentation_order"])
        if presentation_key in seen_presentations or order_key in seen_orders:
            fail("RESPONSE_PRESENTATION", f"{path}: duplicate reviewer presentation id or order")
        seen_presentations.add(presentation_key)
        seen_orders.add(order_key)
        reviewer_case_presentations[(reviewer, case_id)].append(presentation)
        group_id = presentation["blinded_replicate_group_id"]
        if group_id is not None:
            replicate_cases[(reviewer, group_id)].add(case_id)
        verdicts = response["node_verdicts"]
        addresses = [(item["node_id"], item.get("entity_id")) for item in verdicts]
        if len(addresses) != len(set(addresses)):
            fail("RESPONSE_NODE", f"{path}: duplicate node verdict")
        node_ids = {item["node_id"] for item in verdicts}
        application = classes[bundle["target_binding"]["asserted_action_class"]]
        required, optional = set(application["required_nodes"]), set(application["optional_nodes"])
        if not required <= node_ids or node_ids - (required | optional):
            fail("RESPONSE_NODE_COVERAGE", f"{path}: missing required or included inapplicable node")

        # Entity-indexed nodes must name the candidate they are about, and every
        # candidate in the record must be judged on every required node of its family.
        candidates: dict[str, list[str | None]] = {}
        for family, spec in entity_indexing.items():
            registry = next(
                (item for item in _record_set["records"] if item["record_type"] == spec["registry_record_type"]),
                None,
            )
            candidates[family] = (
                [item["entity_id"] for item in registry["content"]["candidates"]] if registry else [None]
            )
        for verdict in verdicts:
            node = graph_nodes[verdict["node_id"]]
            family = node.get("verdict_family")
            if node.get("entity_indexed"):
                if "entity_id" not in verdict:
                    fail("RESPONSE_ENTITY", f"{path}: {verdict['node_id']} must name the candidate it is about")
                if verdict["entity_id"] not in candidates[family]:
                    fail("RESPONSE_ENTITY", f"{path}: {verdict['node_id']} names a candidate absent from the record")
            elif "entity_id" in verdict:
                fail("RESPONSE_ENTITY", f"{path}: {verdict['node_id']} is global and must not name a candidate")
            if set(verdict["cited_record_ids"]) - record_ids:
                fail("RESPONSE_CITATION", f"{path}: cites an unknown record")
        for family, entity_ids in candidates.items():
            family_required = {
                node_id for node_id in required if graph_nodes[node_id].get("verdict_family") == family
            }
            for entity_id in entity_ids:
                missing = family_required - {
                    item["node_id"] for item in verdicts if item.get("entity_id") == entity_id
                }
                if missing:
                    fail(
                        "RESPONSE_ENTITY_COVERAGE",
                        f"{path}: candidate {entity_id!r} lacks verdicts for {sorted(missing)}",
                    )

        # A family may be reported satisfied only if one candidate carries the
        # whole required conjunction. This is the split-entity check.
        for family, resolution in response["conjunction_resolution"].items():
            family_required = {
                node_id for node_id in required if graph_nodes[node_id].get("verdict_family") == family
            }
            supported = [
                entity_id
                for entity_id in candidates[family]
                if entity_id is not None
                and family_required
                and all(
                    item["verdict"] == "support"
                    for item in verdicts
                    if item.get("entity_id") == entity_id and item["node_id"] in family_required
                )
            ]
            if sorted(resolution["satisfying_entity_ids"]) != sorted(supported):
                fail(
                    "RESPONSE_CONJUNCTION",
                    f"{path}: {family} claims satisfying entities {resolution['satisfying_entity_ids']}, "
                    f"but the node verdicts support {supported}",
                )
            if resolution["satisfied"] is not bool(supported):
                fail("RESPONSE_CONJUNCTION", f"{path}: {family} satisfaction must hold within one candidate")
    for (reviewer, case_id), presentations in reviewer_case_presentations.items():
        if len(presentations) <= 1:
            continue
        groups = {item["blinded_replicate_group_id"] for item in presentations}
        if None in groups or len(groups) != 1:
            fail("RESPONSE_DUPLICATE", f"{reviewer}/{case_id}: repeated judgments require one blinded replicate group")
    for (reviewer, group_id), case_ids in replicate_cases.items():
        if len(case_ids) != 1:
            fail("REPLICATE_GROUP", f"{reviewer}/{group_id}: a replicate group must bind one underlying case")
    return len(paths)


def validate_matched_cases(
    bundle_schema: dict[str, Any],
    record_schema: dict[str, Any],
    reference_schema: dict[str, Any],
    applicability: dict[str, Any],
    classes: dict[str, dict[str, Any]],
    modules: dict[str, dict[str, Any]],
    map_hash: str,
    graph_nodes: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]],
    int,
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    int,
]:
    manifest_path = MATCHED / "case-manifest.json"
    manifest = load_json(manifest_path)
    case_ids = [case["case_id"] for case in manifest.get("cases", [])]
    if len(case_ids) != len(set(case_ids)):
        fail("CASE_ID", f"{manifest_path}: duplicate case id")
    bundles: dict[str, tuple[dict[str, Any], dict[str, Any], set[str]]] = {}
    for case in manifest["cases"]:
        bundle_path = MATCHED / case["bundle"]
        if sha256_file(bundle_path) != case["bundle_sha256"]:
            fail("CONTENT_HASH", f"{bundle_path}: manifest hash mismatch")
        validated = validate_bundle(bundle_path, bundle_schema, record_schema, applicability, classes, modules, map_hash)
        if validated[0]["case_id"] != case["case_id"]:
            fail("CASE_BINDING", f"{bundle_path}: manifest case mismatch")
        bundles[case["case_id"]] = validated

    validate_manifest_coverage(manifest, applicability, bundles)

    negative_count = 0
    for negative in manifest.get("negative_fixtures", []):
        negative_count += 1
        bundle_path = MATCHED / negative["bundle"]
        try:
            validate_bundle(bundle_path, bundle_schema, record_schema, applicability, classes, modules, map_hash)
        except ValidationError as exc:
            if exc.code != negative["expected_error_code"]:
                fail("NEGATIVE_FIXTURE", f"{bundle_path}: expected {negative['expected_error_code']}, got {exc.code}")
        else:
            fail("NEGATIVE_FIXTURE", f"{bundle_path}: invalid fixture unexpectedly passed")
    package = validate_reviewer_package(map_hash, manifest)
    key_path = validate_reference_commitment(manifest, package)
    keys = load_json(key_path)
    validate_reference_keys(
        keys, reference_schema, manifest, package, classes, bundles,
        graph_nodes, applicability["entity_indexing"],
    )
    mutation_count = run_reference_mutation_self_tests(manifest, package, keys, bundles)
    return bundles, negative_count, package, keys, manifest, mutation_count


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--responses",
        type=Path,
        default=None,
        help="Optional directory of genuine reviewer-response JSON files. No simulated responses are bundled.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        schemas = {
            name: load_schema(name)
            for name in (
                "evidence-bundle.schema.json",
                "applicability-map.schema.json",
                "record-set.schema.json",
                "reviewer-response.schema.json",
                "action-classifier.schema.json",
                "authorization-regime.schema.json",
                "reference-key.schema.json",
                "unblinding-record.schema.json",
            )
        }
        _graph, nodes, review_nodes = validate_graph()
        validate_crosswalk(nodes)
        applicability, classes, modules, map_hash = validate_applicability(
            review_nodes,
            schemas["applicability-map.schema.json"],
            schemas["action-classifier.schema.json"],
            schemas["authorization-regime.schema.json"],
        )
        bundles, negative_count, package, _keys, manifest, mutation_count = validate_matched_cases(
            schemas["evidence-bundle.schema.json"],
            schemas["record-set.schema.json"],
            schemas["reference-key.schema.json"],
            applicability,
            classes,
            modules,
            map_hash,
            nodes,
        )
        unblinding_record_count = validate_optional_unblinding_record(
            schemas["unblinding-record.schema.json"], manifest, package
        )
        claim_count = validate_projective_claim_links(applicability, map_hash)
        response_count = validate_responses(
            args.responses,
            schemas["reviewer-response.schema.json"],
            package,
            map_hash,
            classes,
            bundles,
            nodes,
            applicability["entity_indexing"],
        )
    except ValidationError as exc:
        print(f"ERROR [{exc.code}] {exc}", file=sys.stderr)
        return 1

    print(
        "Evidentiary artifact validation passed: "
        f"{len(review_nodes)} review nodes, 4 verdict families, "
        f"{len(bundles)} populated-record calibration fixtures, "
        f"{negative_count} expected-failure fixtures, "
        f"{claim_count} exactly linked projective claims, "
        f"{mutation_count} mutation-rejection self-tests, "
        f"{unblinding_record_count} post-boundary opening records, "
        f"{response_count} genuine reviewer responses."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
