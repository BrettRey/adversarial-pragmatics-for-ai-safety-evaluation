#!/usr/bin/env python3
"""Analyze genuine evidentiary-assurance calibration responses after unblinding."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import validate_evidentiary_artifacts as validation


ROOT = Path(__file__).resolve().parents[1]
EA = ROOT / "assurance" / "evidentiary"
MATCHED = EA / "matched-cases"
NOT_ESTIMATED = "NOT_ESTIMATED"

METRIC_TOLERANCES = {
    "false_support_rate": "false_support_rate_max",
    "false_defeat_rate": "false_defeat_rate_max",
    "gap_defeat_confusion_rate": "gap_defeat_confusion_rate_max",
    # A gap says the recording failed; not established says the showing fell
    # short on an adequate record. Confusing them misdirects the remedy.
    "gap_insufficiency_confusion_rate": "gap_insufficiency_confusion_rate_max",
    # Reporting an answerability chain or review path that no single entity
    # occupies. Tracked separately because it is a logical error, not a judgement call.
    "entity_conjunction_error_rate": "entity_conjunction_error_rate_max",
    "required_node_omission_rate": "required_node_omission_rate_max",
    "median_review_minutes": "median_review_minutes_max",
    "privacy_or_security_breach_count": "privacy_or_security_breach_count_max",
}


class AnalysisError(ValueError):
    pass


def parse_time(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AnalysisError(f"invalid ISO timestamp {value!r}: {exc}") from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AnalysisError(f"{path}: JSON root must be an object")
    return value


def enforce_unblinding(
    as_of: datetime,
    package: dict[str, Any],
    opening_record: dict[str, Any],
) -> None:
    boundary = parse_time(package["reference_key_unblinding_not_before"])
    if as_of < boundary:
        raise AnalysisError(
            f"reference-key comparison is blocked until {package['reference_key_unblinding_not_before']}"
        )
    commitment = package["reference_key_commitment"]
    expected_binding = {"path": commitment["path"], "sha256": commitment["sha256"]}
    if opening_record.get("key_binding") != expected_binding:
        raise AnalysisError("unblinding record names a different committed key")
    if opening_record.get("unblinding_not_before") != package.get("reference_key_unblinding_not_before"):
        raise AnalysisError("unblinding record and reviewer package declare different boundaries")
    opened = parse_time(opening_record["opened_at"])
    if opened < boundary or opened > as_of:
        raise AnalysisError("unblinding record lies outside the permitted interval")


def rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def pairwise_disagreement(values: list[str]) -> tuple[int, int]:
    disagree = total = 0
    for index, left in enumerate(values):
        for right in values[index + 1 :]:
            total += 1
            disagree += left != right
    return disagree, total


def address(item: dict[str, Any]) -> tuple[str, str | None]:
    """Verdicts are addressed by node and, for bearer and forum families, entity."""
    return (item["node_id"], item.get("entity_id"))


def response_index(response: dict[str, Any]) -> dict[tuple[str, str | None], dict[str, Any]]:
    return {address(verdict): verdict for verdict in response.get("node_verdicts", [])}


def raw_metrics(
    responses: list[dict[str, Any]],
    references: dict[str, dict[tuple[str, str | None], str]],
    case_classes: dict[str, str],
    required_nodes: dict[str, set[str]],
    case_resolutions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    case_resolutions = case_resolutions or {}
    false_support_n = false_support_d = 0
    false_defeat_n = false_defeat_d = 0
    confusion_n = confusion_d = 0
    insufficiency_n = insufficiency_d = 0
    conjunction_n = conjunction_d = 0
    omission_n = omission_d = 0
    minutes: list[float] = []
    breach_count = 0
    vectors: list[dict[str, Any]] = []
    node_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {
            "false_support_n": 0, "false_support_d": 0,
            "false_defeat_n": 0, "false_defeat_d": 0,
            "confusion_n": 0, "confusion_d": 0,
            "insufficiency_n": 0, "insufficiency_d": 0,
            "omission_n": 0, "omission_d": 0,
        }
    )

    for response in responses:
        case_id = response["case_id"]
        action_class = case_classes[case_id]
        expected_vector = references[case_id]
        observed_vector = response_index(response)
        required = required_nodes[action_class]
        # An expectation exists per (node, entity); omission is judged against that
        # same address set, so a missing candidate counts as a missing verdict.
        required_addresses = {
            addr for addr in expected_vector if addr[0] in required
        }
        omission_d += len(required_addresses)
        omission_n += len(required_addresses - set(observed_vector))
        for node_id, entity_id in required_addresses:
            node_counts[node_id]["omission_d"] += 1
            node_counts[node_id]["omission_n"] += (node_id, entity_id) not in observed_vector
        expected_resolution = case_resolutions.get(case_id, {})
        for family, expected_family in expected_resolution.items():
            observed_family = response.get("conjunction_resolution", {}).get(family)
            if observed_family is None:
                continue
            conjunction_d += 1
            wrong = (
                observed_family.get("satisfied") is not expected_family["satisfied"]
                or sorted(observed_family.get("satisfying_entity_ids", []))
                != sorted(expected_family["satisfying_entity_ids"])
            )
            conjunction_n += wrong
        minutes.append(float(response["burden"]["active_review_minutes"]))
        breach_count += sum(
            incident.get("confirmed_breach") is True
            for incident in response.get("privacy_security_incidents", [])
        )
        for (node_id, entity_id), expected in expected_vector.items():
            verdict = observed_vector.get((node_id, entity_id))
            observed = verdict.get("verdict") if verdict else None
            vectors.append(
                {
                    "pseudonymous_reviewer_id": response["pseudonymous_reviewer_id"],
                    "presentation_id": response["presentation"]["presentation_id"],
                    "presentation_order": response["presentation"]["presentation_order"],
                    "blinded_replicate_group_id": response["presentation"]["blinded_replicate_group_id"],
                    "case_id": case_id,
                    "action_class": action_class,
                    "node_id": node_id,
                    "entity_id": entity_id,
                    "expected": expected,
                    "observed": observed,
                    "cited_record_ids": verdict.get("cited_record_ids", []) if verdict else [],
                    "confidence": verdict.get("confidence") if verdict else None,
                }
            )
            if expected != "support":
                false_support_d += 1
                false_support_n += observed == "support"
                node_counts[node_id]["false_support_d"] += 1
                node_counts[node_id]["false_support_n"] += observed == "support"
            if expected != "substantive_defeat":
                false_defeat_d += 1
                false_defeat_n += observed == "substantive_defeat"
                node_counts[node_id]["false_defeat_d"] += 1
                node_counts[node_id]["false_defeat_n"] += observed == "substantive_defeat"
            if expected in {"record_gap", "substantive_defeat"}:
                confusion_d += 1
                confusion_n += (
                    (expected == "record_gap" and observed == "substantive_defeat")
                    or (expected == "substantive_defeat" and observed == "record_gap")
                )
                node_counts[node_id]["confusion_d"] += 1
                node_counts[node_id]["confusion_n"] += (
                    (expected == "record_gap" and observed == "substantive_defeat")
                    or (expected == "substantive_defeat" and observed == "record_gap")
                )
            if expected in {"record_gap", "not_established"}:
                insufficiency_d += 1
                confused = (
                    (expected == "record_gap" and observed == "not_established")
                    or (expected == "not_established" and observed == "record_gap")
                )
                insufficiency_n += confused
                node_counts[node_id]["insufficiency_d"] += 1
                node_counts[node_id]["insufficiency_n"] += confused

    node_error_metrics: dict[str, Any] = {}
    for node_id, counts in sorted(node_counts.items()):
        node_error_metrics[node_id] = {
            "false_support_rate": {"numerator": counts["false_support_n"], "denominator": counts["false_support_d"], "value": rate(counts["false_support_n"], counts["false_support_d"])},
            "false_defeat_rate": {"numerator": counts["false_defeat_n"], "denominator": counts["false_defeat_d"], "value": rate(counts["false_defeat_n"], counts["false_defeat_d"])},
            "gap_defeat_confusion_rate": {"numerator": counts["confusion_n"], "denominator": counts["confusion_d"], "value": rate(counts["confusion_n"], counts["confusion_d"])},
            "gap_insufficiency_confusion_rate": {"numerator": counts["insufficiency_n"], "denominator": counts["insufficiency_d"], "value": rate(counts["insufficiency_n"], counts["insufficiency_d"])},
            "required_node_omission_rate": {"numerator": counts["omission_n"], "denominator": counts["omission_d"], "value": rate(counts["omission_n"], counts["omission_d"])},
        }

    return {
        "response_count": len(responses),
        "false_support_rate": {"numerator": false_support_n, "denominator": false_support_d, "value": rate(false_support_n, false_support_d)},
        "false_defeat_rate": {"numerator": false_defeat_n, "denominator": false_defeat_d, "value": rate(false_defeat_n, false_defeat_d)},
        "gap_defeat_confusion_rate": {"numerator": confusion_n, "denominator": confusion_d, "value": rate(confusion_n, confusion_d)},
        "gap_insufficiency_confusion_rate": {"numerator": insufficiency_n, "denominator": insufficiency_d, "value": rate(insufficiency_n, insufficiency_d)},
        "entity_conjunction_error_rate": {"numerator": conjunction_n, "denominator": conjunction_d, "value": rate(conjunction_n, conjunction_d)},
        "required_node_omission_rate": {"numerator": omission_n, "denominator": omission_d, "value": rate(omission_n, omission_d)},
        "median_review_minutes": {"value": statistics.median(minutes) if minutes else None, "response_count": len(minutes)},
        "privacy_or_security_breach_count": {"value": breach_count, "response_count": len(responses)},
        "node_error_metrics": node_error_metrics,
        "node_vectors": vectors,
    }


def threshold_metrics(raw: dict[str, Any], tolerances: dict[str, float | int]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for metric, tolerance_name in METRIC_TOLERANCES.items():
        observed = raw[metric]["value"]
        threshold = tolerances[tolerance_name]
        status = NOT_ESTIMATED if observed is None else ("PASS" if observed <= threshold else "FAIL")
        results[metric] = {**raw[metric], "threshold_max": threshold, "status": status}
    return results


def threshold_node_metrics(
    raw: dict[str, dict[str, Any]], tolerances: dict[str, float | int]
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for node_id, metrics in sorted(raw.items()):
        node_result: dict[str, Any] = {}
        for metric, observed_record in metrics.items():
            tolerance_name = METRIC_TOLERANCES[metric]
            if tolerance_name not in tolerances:
                continue
            observed = observed_record["value"]
            threshold = tolerances[tolerance_name]
            status = NOT_ESTIMATED if observed is None else ("PASS" if observed <= threshold else "FAIL")
            node_result[metric] = {**observed_record, "threshold_max": threshold, "status": status}
        results[node_id] = node_result
    return results


def minimum_reach_result(
    responses: list[dict[str, Any]], thresholds: dict[str, int]
) -> dict[str, Any]:
    cases = {response["case_id"] for response in responses}
    reviewers = {response["pseudonymous_reviewer_id"] for response in responses}
    reviewers_by_case: dict[str, set[str]] = defaultdict(set)
    for response in responses:
        reviewers_by_case[response["case_id"]].add(response["pseudonymous_reviewer_id"])
    minimum_case_reviewers = min((len(value) for value in reviewers_by_case.values()), default=0)
    observed = {
        "distinct_cases_per_action_class": len(cases),
        "genuine_responses_per_action_class": len(responses),
        "distinct_reviewers_per_action_class": len(reviewers),
        "minimum_reviewers_on_any_observed_case": minimum_case_reviewers,
    }
    criteria = {
        "distinct_cases_per_action_class": observed["distinct_cases_per_action_class"] >= thresholds["distinct_cases_per_action_class_min"],
        "genuine_responses_per_action_class": observed["genuine_responses_per_action_class"] >= thresholds["genuine_responses_per_action_class_min"],
        "distinct_reviewers_per_action_class": observed["distinct_reviewers_per_action_class"] >= thresholds["distinct_reviewers_per_action_class_min"],
        "reviewers_per_case": bool(cases) and minimum_case_reviewers >= thresholds["reviewers_per_case_min"],
    }
    return {
        "status": "PASS" if all(criteria.values()) else NOT_ESTIMATED,
        "observed": observed,
        "thresholds": thresholds,
        "criteria_pass": criteria,
    }


def coverage_reach_result(
    responses: list[dict[str, Any]],
    use: dict[str, Any],
    case_metadata: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    # Responses on an exposed demonstration fixture cannot evidence a blinded
    # use; they are dropped before coverage and reach are computed.
    observed_case_ids = {
        response["case_id"] for response in responses
        if case_metadata.get(response["case_id"], {}).get("exposure") != "exposed_demonstration"
    }
    observed_tags = {
        tag
        for case_id in observed_case_ids
        for tag in case_metadata.get(case_id, {}).get("coverage_tags", [])
    }
    required_tags = set(use.get("required_coverage_tags", []))
    missing_tags = sorted(required_tags - observed_tags)
    reviewers_by_case: dict[str, set[str]] = defaultdict(set)
    for response in responses:
        if case_metadata.get(response["case_id"], {}).get("exposure") == "exposed_demonstration":
            continue
        reviewers_by_case[response["case_id"]].add(response["pseudonymous_reviewer_id"])
    reviewer_minimum = use["minimum_reach_thresholds"]["reviewers_per_case_min"]
    pair_results: dict[str, Any] = {}
    for pair_id in use.get("required_controlled_pair_ids", []):
        members = sorted(
            case_id for case_id, metadata in case_metadata.items() if metadata.get("pair_id") == pair_id
        )
        member_reviewers = {case_id: len(reviewers_by_case.get(case_id, set())) for case_id in members}
        pair_results[pair_id] = {
            "expected_members": members,
            "member_distinct_reviewer_counts": member_reviewers,
            "status": "PASS" if len(members) == 2 and all(count >= reviewer_minimum for count in member_reviewers.values()) else NOT_ESTIMATED,
        }
    status = "PASS" if not missing_tags and all(item["status"] == "PASS" for item in pair_results.values()) else NOT_ESTIMATED
    return {
        "status": status,
        "required_coverage_tags": sorted(required_tags),
        "observed_coverage_tags": sorted(observed_tags),
        "missing_coverage_tags": missing_tags,
        "required_controlled_pairs": pair_results,
    }


def conjunctive_status(metric_sets: Iterable[dict[str, Any]]) -> str:
    statuses = [metric["status"] for metrics in metric_sets for metric in metrics.values()]
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if not statuses or any(status == NOT_ESTIMATED for status in statuses):
        return NOT_ESTIMATED
    return "PASS"


def disagreement_report(vectors: list[dict[str, Any]]) -> dict[str, Any]:
    first_by_reviewer_case_node: dict[tuple[str, str, str], dict[str, Any]] = {}
    for vector in vectors:
        if vector["observed"] is None:
            continue
        key = (vector["pseudonymous_reviewer_id"], vector["case_id"], vector["node_id"])
        prior = first_by_reviewer_case_node.get(key)
        if prior is None or vector["presentation_order"] < prior["presentation_order"]:
            first_by_reviewer_case_node[key] = vector
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    by_class: dict[str, list[tuple[int, int]]] = defaultdict(list)
    by_case: dict[str, list[tuple[int, int]]] = defaultdict(list)
    for vector in first_by_reviewer_case_node.values():
        grouped[(vector["case_id"], vector["node_id"])].append(vector["observed"])
    total_n = total_d = 0
    for (case_id, _node_id), values in grouped.items():
        numerator, denominator = pairwise_disagreement(values)
        total_n += numerator
        total_d += denominator
        action_class = next(v["action_class"] for v in vectors if v["case_id"] == case_id)
        by_class[action_class].append((numerator, denominator))
        by_case[case_id].append((numerator, denominator))

    def summarize(parts: list[tuple[int, int]]) -> dict[str, Any]:
        numerator = sum(item[0] for item in parts)
        denominator = sum(item[1] for item in parts)
        return {"numerator": numerator, "denominator": denominator, "value": rate(numerator, denominator), "status": "ESTIMATED" if denominator else NOT_ESTIMATED}

    return {
        "definition": "Unordered-pair verdict disagreement among distinct reviewers judging the same case and node, using each reviewer's lowest-order presentation so blinded repeats do not inflate agreement or disagreement.",
        "overall": summarize([(total_n, total_d)]),
        "by_action_class": {key: summarize(value) for key, value in sorted(by_class.items())},
        "by_case": {key: summarize(value) for key, value in sorted(by_case.items())},
    }


def conditional_variation_report(vectors: list[dict[str, Any]]) -> dict[str, Any]:
    first_by_reviewer_case_node: dict[tuple[str, str, str], dict[str, Any]] = {}
    for vector in vectors:
        if vector["observed"] is None:
            continue
        key = (vector["pseudonymous_reviewer_id"], vector["case_id"], vector["node_id"])
        prior = first_by_reviewer_case_node.get(key)
        if prior is None or vector["presentation_order"] < prior["presentation_order"]:
            first_by_reviewer_case_node[key] = vector
    grouped: dict[tuple[str, str, str, str], list[str]] = defaultdict(list)
    for vector in first_by_reviewer_case_node.values():
        if vector["observed"] is not None:
            grouped[(
                vector["pseudonymous_reviewer_id"],
                vector["action_class"],
                vector["node_id"],
                vector["expected"],
            )].append(vector["observed"])
    by_reviewer: dict[str, list[tuple[int, int]]] = defaultdict(list)
    total_n = total_d = 0
    for (reviewer, _action_class, _node, _expected), values in grouped.items():
        numerator, denominator = pairwise_disagreement(values)
        total_n += numerator
        total_d += denominator
        by_reviewer[reviewer].append((numerator, denominator))

    def summarize(parts: list[tuple[int, int]]) -> dict[str, Any]:
        numerator = sum(item[0] for item in parts)
        denominator = sum(item[1] for item in parts)
        return {"numerator": numerator, "denominator": denominator, "value": rate(numerator, denominator), "status": "ESTIMATED" if denominator else NOT_ESTIMATED}

    return {
        "definition": "Descriptive within-reviewer verdict variation across different cases sharing action class, node, and hidden expected status; case differences prevent a test-retest interpretation.",
        "overall": summarize([(total_n, total_d)]),
        "by_reviewer": {key: summarize(value) for key, value in sorted(by_reviewer.items())},
    }


def test_retest_instability_report(vectors: list[dict[str, Any]]) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for vector in vectors:
        group_id = vector.get("blinded_replicate_group_id")
        if group_id is not None and vector["observed"] is not None:
            grouped[(vector["pseudonymous_reviewer_id"], group_id, vector["node_id"])].append(vector["observed"])
    by_reviewer: dict[str, list[tuple[int, int]]] = defaultdict(list)
    by_group: dict[str, list[tuple[int, int]]] = defaultdict(list)
    total_n = total_d = 0
    for (reviewer, group_id, _node_id), values in grouped.items():
        numerator, denominator = pairwise_disagreement(values)
        total_n += numerator
        total_d += denominator
        by_reviewer[reviewer].append((numerator, denominator))
        by_group[group_id].append((numerator, denominator))

    def summarize(parts: list[tuple[int, int]]) -> dict[str, Any]:
        numerator = sum(item[0] for item in parts)
        denominator = sum(item[1] for item in parts)
        return {"numerator": numerator, "denominator": denominator, "value": rate(numerator, denominator), "status": "ESTIMATED" if denominator else NOT_ESTIMATED}

    return {
        "definition": "Within-reviewer test-retest disagreement only across presentations in the same predeclared blinded replicate group and at the same node.",
        "overall": summarize([(total_n, total_d)]),
        "by_reviewer": {key: summarize(value) for key, value in sorted(by_reviewer.items())},
        "by_blinded_replicate_group": {key: summarize(value) for key, value in sorted(by_group.items())},
    }


def analyze(
    responses: list[dict[str, Any]],
    references: dict[str, dict[str, str]],
    case_classes: dict[str, str],
    required_nodes: dict[str, set[str]],
    declared_uses: list[dict[str, Any]],
    case_metadata: dict[str, dict[str, Any]] | None = None,
    case_resolutions: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    case_metadata = case_metadata or {}
    case_resolutions = case_resolutions or {}
    if not responses:
        return {
            "analysis_status": NOT_ESTIMATED,
            "reason": "zero genuine reviewer responses",
            "genuine_response_count": 0,
            "node_vectors": [],
            "uses": {use["use_id"]: {"status": NOT_ESTIMATED, "reason": "zero genuine reviewer responses", "minimum_reach_thresholds": use["minimum_reach_thresholds"], "required_coverage_tags": use.get("required_coverage_tags", []), "required_controlled_pair_ids": use.get("required_controlled_pair_ids", []), "scalar_score": None} for use in declared_uses},
            "reviewer_disagreement": {"status": NOT_ESTIMATED},
            "reviewer_instability": {"status": NOT_ESTIMATED},
            "across_case_conditional_variation": {"status": NOT_ESTIMATED},
        }

    all_raw = raw_metrics(responses, references, case_classes, required_nodes, case_resolutions)
    vectors = all_raw.pop("node_vectors")
    by_class: dict[str, Any] = {}
    for action_class in sorted(set(case_classes.values())):
        subset = [response for response in responses if case_classes[response["case_id"]] == action_class]
        raw = raw_metrics(subset, references, case_classes, required_nodes, case_resolutions)
        raw.pop("node_vectors")
        by_class[action_class] = raw

    def grouped_metrics(key: str) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for response in responses:
            groups[str(response[key])].append(response)
        result: dict[str, Any] = {}
        for group_id, items in sorted(groups.items()):
            metrics = raw_metrics(items, references, case_classes, required_nodes, case_resolutions)
            metrics.pop("node_vectors")
            result[group_id] = metrics
        return result

    uses: dict[str, Any] = {}
    for use in declared_uses:
        class_results: dict[str, Any] = {}
        for action_class in use["action_classes"]:
            subset = [response for response in responses if case_classes[response["case_id"]] == action_class]
            raw = by_class.get(action_class)
            if raw is None:
                raw = raw_metrics([], references, case_classes, required_nodes)
                raw.pop("node_vectors")
            aggregate_metrics = threshold_metrics(raw, use["tolerances"])
            node_metrics = threshold_node_metrics(raw["node_error_metrics"], use["tolerances"])
            reach = minimum_reach_result(subset, use["minimum_reach_thresholds"])
            aggregate_status = conjunctive_status([aggregate_metrics])
            node_failure = any(
                metric["status"] == "FAIL"
                for metrics in node_metrics.values()
                for metric in metrics.values()
            )
            class_status = (
                "FAIL" if aggregate_status == "FAIL" or node_failure
                else NOT_ESTIMATED if aggregate_status == NOT_ESTIMATED or reach["status"] != "PASS"
                else "PASS"
            )
            class_results[action_class] = {
                "status": class_status,
                "metrics": aggregate_metrics,
                "node_error_metrics": node_metrics,
                "minimum_reach": reach,
                "scalar_score": None,
            }
        relevant_responses = [
            response for response in responses
            if case_classes[response["case_id"]] in use["action_classes"]
        ]
        coverage = coverage_reach_result(relevant_responses, use, case_metadata)
        class_statuses = [item["status"] for item in class_results.values()]
        status = "FAIL" if "FAIL" in class_statuses else (
            NOT_ESTIMATED if NOT_ESTIMATED in class_statuses or coverage["status"] != "PASS" else "PASS"
        )
        uses[use["use_id"]] = {
            "status": status,
            "rule": "Every metric must pass in every declared action class; no metric or class compensates for another.",
            "class_results": class_results,
            "substantive_coverage": coverage,
            "scalar_score": None,
        }

    return {
        "analysis_status": "ESTIMATED",
        "genuine_response_count": len(responses),
        "node_vectors": vectors,
        "metrics_overall": all_raw,
        "metrics_by_action_class": by_class,
        "metrics_by_case": grouped_metrics("case_id"),
        "metrics_by_reviewer": grouped_metrics("pseudonymous_reviewer_id"),
        "reviewer_disagreement": disagreement_report(vectors),
        "reviewer_instability": test_retest_instability_report(vectors),
        "across_case_conditional_variation": conditional_variation_report(vectors),
        "uses": uses,
    }


def genuine_paths(response_dir: Path) -> list[Path]:
    return sorted(response_dir.glob("*.json")) if response_dir.exists() else []


def load_validated_artifacts(response_dir: Path) -> tuple[
    list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]
]:
    schemas = {
        name: validation.load_schema(name)
        for name in (
            "evidence-bundle.schema.json", "applicability-map.schema.json", "record-set.schema.json",
            "reviewer-response.schema.json", "action-classifier.schema.json", "authorization-regime.schema.json",
            "reference-key.schema.json",
        )
    }
    _graph, graph_nodes, review_nodes = validation.validate_graph()
    applicability, classes, modules, map_hash = validation.validate_applicability(
        review_nodes, schemas["applicability-map.schema.json"], schemas["action-classifier.schema.json"], schemas["authorization-regime.schema.json"]
    )
    bundles, _negative_count, package, keys, manifest, _mutations = validation.validate_matched_cases(
        schemas["evidence-bundle.schema.json"], schemas["record-set.schema.json"], schemas["reference-key.schema.json"],
        applicability, classes, modules, map_hash, graph_nodes,
    )
    validation.validate_responses(
        response_dir, schemas["reviewer-response.schema.json"], package, map_hash, classes, bundles,
        graph_nodes, applicability["entity_indexing"],
    )
    responses = [load_json(path) for path in genuine_paths(response_dir)]
    return responses, applicability, classes, bundles, keys, manifest


def verdict(node_id: str, value: str, entity_id: str | None = None) -> dict[str, Any]:
    item = {"node_id": node_id, "verdict": value, "cited_record_ids": [], "confidence": "high"}
    if entity_id is not None:
        item["entity_id"] = entity_id
    return item


def synthetic_response(
    reviewer: str,
    case_id: str,
    expected: dict[Any, str],
    minutes: float = 10,
    presentation_order: int = 1,
    replicate_group: str | None = None,
    resolution: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "response_source": "in_memory_self_test_only",
        "pseudonymous_reviewer_id": reviewer,
        "case_id": case_id,
        "presentation": {
            "presentation_id": f"{reviewer}-{case_id}-{presentation_order}",
            "presentation_order": presentation_order,
            "blinded_replicate_group_id": replicate_group,
        },
        "burden": {"active_review_minutes": minutes, "protected_material_accessed": False, "material_access_events": 0},
        "privacy_security_incidents": [],
        "node_verdicts": [
            verdict(key[0], value, key[1]) if isinstance(key, tuple) else verdict(key, value)
            for key, value in expected.items()
        ],
        **({"conjunction_resolution": resolution} if resolution else {}),
    }


def run_self_tests() -> list[str]:
    # Verdicts are addressed by (node, entity). N1--N3 are global; B1 is a
    # stand-in entity-indexed node carried by two candidate entities.
    base_vector = {
        ("N1", None): "substantive_defeat",
        ("N2", None): "record_gap",
        ("N3", None): "support",
        ("N4", None): "not_established",
        ("B1", "E1"): "support",
        ("B1", "E2"): "record_gap",
    }
    references = {case: dict(base_vector) for case in ("P1", "P2", "T1", "T2")}
    resolutions = {
        case: {"J_B": {"satisfied": True, "satisfying_entity_ids": ["E1"]}}
        for case in references
    }
    case_classes = {"P1": "procurement", "P2": "procurement", "T1": "transcription", "T2": "transcription"}
    required = {
        "procurement": {"N1", "N2", "N3", "N4", "B1"},
        "transcription": {"N1", "N2", "N3", "N4", "B1"},
    }
    tolerance = {
        "false_support_rate_max": 0.05,
        "false_defeat_rate_max": 0.05,
        "gap_defeat_confusion_rate_max": 0.05,
        "gap_insufficiency_confusion_rate_max": 0.05,
        "entity_conjunction_error_rate_max": 0.0,
        "required_node_omission_rate_max": 0.0,
        "median_review_minutes_max": 25,
        "privacy_or_security_breach_count_max": 0,
    }
    reach = {"distinct_cases_per_action_class_min": 2, "genuine_responses_per_action_class_min": 4, "distinct_reviewers_per_action_class_min": 2, "reviewers_per_case_min": 2}
    uses = [
        {"use_id": "both", "action_classes": ["procurement", "transcription"], "tolerances": tolerance, "minimum_reach_thresholds": reach, "required_coverage_tags": [], "required_controlled_pair_ids": []},
        {"use_id": "proc", "action_classes": ["procurement"], "tolerances": tolerance, "minimum_reach_thresholds": reach, "required_coverage_tags": [], "required_controlled_pair_ids": []},
        {"use_id": "trans", "action_classes": ["transcription"], "tolerances": tolerance, "minimum_reach_thresholds": reach, "required_coverage_tags": [], "required_controlled_pair_ids": []},
    ]
    baseline = [
        synthetic_response(
            reviewer, case_id, expected, presentation_order=order,
            resolution=resolutions[case_id],
        )
        for reviewer in ("R1", "R2")
        for order, (case_id, expected) in enumerate(references.items(), start=1)
    ]
    checks: list[str] = []

    perfect = analyze(baseline, references, case_classes, required, uses, None, resolutions)
    assert perfect["uses"]["both"]["status"] == "PASS"
    checks.append("all-metric pass")

    mutations = {
        "false-support": ("P1", "N1", "support", "false_support_rate"),
        "false-defeat": ("P1", "N3", "substantive_defeat", "false_defeat_rate"),
        "gap-defeat-confusion": ("P1", "N2", "substantive_defeat", "gap_defeat_confusion_rate"),
        # Reporting an unevaluable record as a showing that merely fell short,
        # and the reverse: each misdirects the institutional response.
        "gap-reported-as-insufficiency": ("P1", "N2", "not_established", "gap_insufficiency_confusion_rate"),
        "insufficiency-reported-as-gap": ("P1", "N4", "record_gap", "gap_insufficiency_confusion_rate"),
    }
    for label, (case_id, node_id, value, metric) in mutations.items():
        sample = copy.deepcopy(baseline)
        # Mutate the node in every response for the case, so the detected rate
        # does not depend on how many other nodes share the denominator.
        for response in (item for item in sample if item["case_id"] == case_id):
            next(item for item in response["node_verdicts"] if item["node_id"] == node_id)["verdict"] = value
        result = analyze(sample, references, case_classes, required, uses, None, resolutions)
        assert result["uses"]["proc"]["class_results"]["procurement"]["metrics"][metric]["status"] == "FAIL"
        checks.append(label)

    sample = copy.deepcopy(baseline)
    response = next(item for item in sample if item["case_id"] == "P1")
    response["node_verdicts"] = [item for item in response["node_verdicts"] if item["node_id"] != "N3"]
    assert analyze(sample, references, case_classes, required, uses, None, resolutions)["uses"]["proc"]["class_results"]["procurement"]["metrics"]["required_node_omission_rate"]["status"] == "FAIL"
    checks.append("required-node omission")

    # Dropping one candidate's verdict is an omission, not a silent pass: without
    # entity addressing the remaining candidate's verdict would have covered the node.
    sample = copy.deepcopy(baseline)
    response = next(item for item in sample if item["case_id"] == "P1")
    response["node_verdicts"] = [
        item for item in response["node_verdicts"]
        if not (item["node_id"] == "B1" and item.get("entity_id") == "E2")
    ]
    assert analyze(sample, references, case_classes, required, uses, None, resolutions)["uses"]["proc"]["class_results"]["procurement"]["metrics"]["required_node_omission_rate"]["status"] == "FAIL"
    checks.append("per-candidate omission detected")

    # The split-entity failure: every node supported by someone, no single
    # candidate carrying the conjunction, reported as satisfied anyway.
    split_references = {case: dict(vector) for case, vector in references.items()}
    split_resolutions = {case: dict(item) for case, item in resolutions.items()}
    for case in split_references:
        split_references[case][("B1", "E1")] = "record_gap"
        split_references[case][("B1", "E2")] = "support"
        split_resolutions[case] = {
            "J_B": {"satisfied": False, "satisfying_entity_ids": []}
        }
    sample = [
        synthetic_response(
            reviewer, case_id, expected, presentation_order=order,
            # claims a satisfied bearer chain assembled from two candidates
            resolution={"J_B": {"satisfied": True, "satisfying_entity_ids": ["E1"]}},
        )
        for reviewer in ("R1", "R2")
        for order, (case_id, expected) in enumerate(split_references.items(), start=1)
    ]
    result = analyze(sample, split_references, case_classes, required, uses, None, split_resolutions)
    assert result["uses"]["proc"]["class_results"]["procurement"]["metrics"]["entity_conjunction_error_rate"]["status"] == "FAIL"
    checks.append("split-entity conjunction rejected")

    # And the honest reading of the same split passes.
    honest = [
        synthetic_response(
            reviewer, case_id, expected, presentation_order=order,
            resolution={"J_B": {"satisfied": False, "satisfying_entity_ids": []}},
        )
        for reviewer in ("R1", "R2")
        for order, (case_id, expected) in enumerate(split_references.items(), start=1)
    ]
    result = analyze(honest, split_references, case_classes, required, uses, None, split_resolutions)
    assert result["uses"]["proc"]["class_results"]["procurement"]["metrics"]["entity_conjunction_error_rate"]["status"] == "PASS"
    checks.append("honest split-entity report accepted")

    sample = copy.deepcopy(baseline)
    for response in sample:
        if case_classes[response["case_id"]] == "procurement":
            response["burden"]["active_review_minutes"] = 26
    assert analyze(sample, references, case_classes, required, uses, None, resolutions)["uses"]["proc"]["class_results"]["procurement"]["metrics"]["median_review_minutes"]["status"] == "FAIL"
    checks.append("review-time")

    sample = copy.deepcopy(baseline)
    sample[0]["privacy_security_incidents"] = [{"confirmed_breach": True}]
    assert analyze(sample, references, case_classes, required, uses, None, resolutions)["uses"]["proc"]["class_results"]["procurement"]["metrics"]["privacy_or_security_breach_count"]["status"] == "FAIL"
    checks.append("privacy-security breach")

    sample = copy.deepcopy(baseline)
    response = next(item for item in sample if item["case_id"] == "P1" and item["pseudonymous_reviewer_id"] == "R2")
    next(item for item in response["node_verdicts"] if item["node_id"] == "N3")["verdict"] = "record_gap"
    result = analyze(sample, references, case_classes, required, uses, None, resolutions)
    assert result["reviewer_disagreement"]["overall"]["value"] > 0
    checks.append("reviewer disagreement")

    sample = copy.deepcopy(baseline)
    original = next(item for item in sample if item["case_id"] == "P1" and item["pseudonymous_reviewer_id"] == "R1")
    original["presentation"]["blinded_replicate_group_id"] = "BLIND-P1-R1"
    extra = synthetic_response("R1", "P1", references["P1"], presentation_order=5, replicate_group="BLIND-P1-R1")
    next(item for item in extra["node_verdicts"] if item["node_id"] == "N3")["verdict"] = "record_gap"
    sample.append(extra)
    result = analyze(sample, references, case_classes, required, uses, None, resolutions)
    assert result["reviewer_instability"]["overall"]["value"] > 0
    checks.append("blinded-replicate test-retest instability")

    sample = copy.deepcopy(baseline)
    response = next(item for item in sample if item["case_id"] == "P2" and item["pseudonymous_reviewer_id"] == "R1")
    next(item for item in response["node_verdicts"] if item["node_id"] == "N3")["verdict"] = "substantive_defeat"
    result = analyze(sample, references, case_classes, required, uses, None, resolutions)
    assert result["reviewer_instability"]["overall"]["status"] == NOT_ESTIMATED
    assert result["across_case_conditional_variation"]["overall"]["value"] > 0
    assert result["uses"]["trans"]["status"] == "PASS" and result["uses"]["both"]["status"] == "FAIL"
    checks.extend(["across-case variation not mislabeled instability", "noncompensatory class failure"])

    one_response = analyze([baseline[0]], references, case_classes, required, uses)
    assert all(item["status"] == NOT_ESTIMATED for item in one_response["uses"].values())
    checks.append("minimum reach blocks one-response pass")

    dilution_specs = {
        "nodewise false-support": ("record_gap", "support", "false_support_rate"),
        "nodewise false-defeat": ("support", "substantive_defeat", "false_defeat_rate"),
        "nodewise gap-confusion": ("record_gap", "substantive_defeat", "gap_defeat_confusion_rate"),
        "nodewise omission": ("support", None, "required_node_omission_rate"),
    }
    for label, (expected_extra, observed_mutation, metric) in dilution_specs.items():
        diluted_references = {
            case_id: {
                **references[case_id],
                **{(f"D{index:02d}", None): expected_extra for index in range(25)},
            }
            for case_id in ("P1", "P2")
        }
        diluted_classes = {"P1": "procurement", "P2": "procurement"}
        diluted_required = {
            "procurement": {node_id for node_id, _entity in next(iter(diluted_references.values()))}
        }
        diluted_tolerance = {**tolerance, "required_node_omission_rate_max": 0.05}
        diluted_use = [{"use_id": "proc", "action_classes": ["procurement"], "tolerances": diluted_tolerance, "minimum_reach_thresholds": reach, "required_coverage_tags": [], "required_controlled_pair_ids": []}]
        diluted_responses = [
            synthetic_response(reviewer, case_id, expected, presentation_order=order)
            for reviewer in ("R1", "R2")
            for order, (case_id, expected) in enumerate(diluted_references.items(), start=1)
        ]
        target = next(item for item in diluted_responses if item["case_id"] == "P1" and item["pseudonymous_reviewer_id"] == "R1")
        if observed_mutation is None:
            target["node_verdicts"] = [item for item in target["node_verdicts"] if item["node_id"] != "D00"]
        else:
            next(item for item in target["node_verdicts"] if item["node_id"] == "D00")["verdict"] = observed_mutation
        diluted = analyze(diluted_responses, diluted_references, diluted_classes, diluted_required, diluted_use)
        class_result = diluted["uses"]["proc"]["class_results"]["procurement"]
        assert class_result["metrics"][metric]["status"] == "PASS"
        assert class_result["node_error_metrics"]["D00"][metric]["status"] == "FAIL"
        assert diluted["uses"]["proc"]["status"] == "FAIL"
        checks.append(label)

    coverage_references = {
        case_id: {"N1": "support"}
        for case_id in ("P1", "P2", "P3", "P4")
    }
    coverage_classes = {case_id: "procurement" for case_id in coverage_references}
    coverage_required = {"procurement": {"N1"}}
    coverage_responses = [
        synthetic_response(reviewer, case_id, coverage_references[case_id], presentation_order=order)
        for reviewer in ("R1", "R2")
        for order, case_id in enumerate(("P1", "P2"), start=1)
    ]
    coverage_use = [{
        "use_id": "proc-contrast",
        "action_classes": ["procurement"],
        "tolerances": tolerance,
        "minimum_reach_thresholds": reach,
        "required_coverage_tags": ["required_contrast"],
        "required_controlled_pair_ids": ["PAIR-X"],
    }]
    coverage_metadata = {
        "P1": {"coverage_tags": ["ordinary"], "pair_id": None},
        "P2": {"coverage_tags": ["ordinary"], "pair_id": None},
        "P3": {"coverage_tags": ["required_contrast"], "pair_id": "PAIR-X"},
        "P4": {"coverage_tags": ["required_contrast"], "pair_id": "PAIR-X"},
    }
    coverage_result = analyze(
        coverage_responses,
        coverage_references,
        coverage_classes,
        coverage_required,
        coverage_use,
        coverage_metadata,
    )
    coverage_class = coverage_result["uses"]["proc-contrast"]["class_results"]["procurement"]
    coverage_gate = coverage_result["uses"]["proc-contrast"]["substantive_coverage"]
    assert coverage_class["minimum_reach"]["status"] == "PASS"
    assert coverage_gate["status"] == NOT_ESTIMATED
    assert coverage_gate["missing_coverage_tags"] == ["required_contrast"]
    assert coverage_result["uses"]["proc-contrast"]["status"] == NOT_ESTIMATED
    checks.append("substantive contrast coverage blocks numeric-reach false pass")

    empty = analyze([], references, case_classes, required, uses, None, resolutions)
    assert empty["analysis_status"] == NOT_ESTIMATED and all(item["status"] == NOT_ESTIMATED for item in empty["uses"].values())
    checks.append("zero-response NOT_ESTIMATED")

    immutable_key = b'{"hidden":"reference values"}'
    key_hash = hashlib.sha256(immutable_key).hexdigest()
    package = {
        "reference_key_unblinding_not_before": "2026-08-15T00:00:00Z",
        "reference_key_commitment": {"path": "hidden/reference-keys.json", "sha256": key_hash},
    }
    opening_record = {
        "key_binding": {"path": "hidden/reference-keys.json", "sha256": key_hash},
        "unblinding_not_before": "2026-08-15T00:00:00Z",
        "opened_at": "2026-08-15T00:00:01Z",
    }
    try:
        enforce_unblinding(parse_time("2026-08-14T23:59:59Z"), package, opening_record)
    except AnalysisError:
        pass
    else:
        raise AssertionError("pre-boundary unblinding was accepted")
    enforce_unblinding(parse_time("2026-08-15T00:00:02Z"), package, opening_record)
    assert hashlib.sha256(immutable_key).hexdigest() == key_hash
    assert hashlib.sha256(immutable_key + b"mutation").hexdigest() != key_hash
    checks.append("separate opening record preserves immutable key commitment")
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, default=MATCHED / "responses", help="Directory containing genuine reviewer-response JSON files")
    parser.add_argument("--unblinding-record", type=Path, default=MATCHED / "hidden" / "unblinding-record.json", help="Post-boundary opening record bound to the immutable hidden-key hash")
    parser.add_argument("--as-of", help="ISO timestamp for the comparison boundary; defaults to current UTC time")
    parser.add_argument("--output", type=Path, help="Optional JSON output path")
    parser.add_argument("--self-test", action="store_true", help="Run synthetic in-memory metric and boundary tests")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        try:
            checks = run_self_tests()
        except (AssertionError, AnalysisError, validation.ValidationError) as exc:
            print(f"FAIL analyzer self-test: {exc}", file=sys.stderr)
            return 1
        print(f"PASS analyzer self-tests: {len(checks)} in-memory checks ({', '.join(checks)}); no genuine response files created.")
        if not args.output and args.responses == MATCHED / "responses":
            return 0

    paths = genuine_paths(args.responses)
    if not paths:
        applicability = load_json(EA / "applicability-map.json")
        result = analyze([], {}, {}, {}, applicability["declared_uses"])
    else:
        package = load_json(MATCHED / "reviewer-package.json")
        now = datetime.now(timezone.utc)
        as_of = parse_time(args.as_of) if args.as_of else now
        if as_of > now:
            print("ERROR --as-of cannot be later than the current system time", file=sys.stderr)
            return 1
        boundary = parse_time(package["reference_key_unblinding_not_before"])
        if as_of < boundary:
            print(f"ERROR reference-key comparison blocked until {package['reference_key_unblinding_not_before']}", file=sys.stderr)
            return 1
        try:
            responses, applicability, classes, bundles, keys, manifest = load_validated_artifacts(args.responses)
            if not args.unblinding_record.exists():
                raise AnalysisError(f"missing post-boundary unblinding record: {args.unblinding_record}")
            opening_record = load_json(args.unblinding_record)
            opening_schema = validation.load_schema("unblinding-record.schema.json")
            validation.validate_instance(opening_record, opening_schema, args.unblinding_record)
            enforce_unblinding(as_of, package, opening_record)
            references = {
                case["case_id"]: validation.flat_expected(case) for case in keys["cases"]
            }
            case_resolutions = {
                case["case_id"]: case["expected_conjunction_resolution"] for case in keys["cases"]
            }
            case_classes = {case_id: bundle[0]["target_binding"]["asserted_action_class"] for case_id, bundle in bundles.items()}
            case_metadata = {
                case["case_id"]: {
                    "coverage_tags": case["coverage_tags"],
                    "pair_id": case.get("pair_id"),
                    "exposure": case.get("exposure", "blinded"),
                }
                for case in manifest["cases"]
            }
            required_nodes = {action_class: set(item["required_nodes"]) for action_class, item in classes.items()}
            result = analyze(
                responses,
                references,
                case_classes,
                required_nodes,
                applicability["declared_uses"],
                case_metadata,
                case_resolutions,
            )
        except (AnalysisError, validation.ValidationError) as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 1

    result["generated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result["response_directory"] = str(args.responses)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
