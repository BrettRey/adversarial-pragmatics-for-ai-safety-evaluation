#!/usr/bin/env python3
"""Analyze genuine evidentiary-assurance calibration responses after unblinding."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
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


# A tolerance on an error rate is a claim about a rate the reviewer would produce
# in general, estimated from a handful of observations. Comparing a point estimate
# to a fixed threshold turns a noisy proportion into a hard pass/fail cliff: 0/12
# "passes" a 0.05 ceiling although 0/12 is consistent with a true rate near 0.2.
# We instead carry a posterior interval and require it to clear the threshold,
# following Gelman's objection to dichotomising an estimate without its uncertainty.
MEETS = "MEETS_TOLERANCE"
EXCEEDS = "EXCEEDS_TOLERANCE"
INDETERMINATE = "INDETERMINATE"

# Metric-level decisions roll up to the existing use-level vocabulary honestly:
# a use is demonstrated met only when every metric is met, demonstrated exceeded
# when any metric is exceeded, and otherwise not yet demonstrated.
DECISION_TO_STATUS = {
    MEETS: "PASS",
    EXCEEDS: "FAIL",
    INDETERMINATE: NOT_ESTIMATED,
    NOT_ESTIMATED: NOT_ESTIMATED,
}

# Rates are proportions estimated from data; a zero tolerance is a bright-line
# policy on a count; the review-minutes ceiling is a bound on a median; and the
# breach count is a bright-line policy on an event count.
RATE_METRICS = {
    "false_support_rate",
    "false_defeat_rate",
    "gap_defeat_confusion_rate",
    "gap_insufficiency_confusion_rate",
    "entity_conjunction_error_rate",
    "required_node_omission_rate",
}


def _betacf(a: float, b: float, x: float) -> float:
    """Continued fraction for the incomplete beta, via the modified Lentz method."""
    tiny = 1e-30
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return h


def regularized_incomplete_beta(a: float, b: float, x: float) -> float:
    """I_x(a,b): the CDF of a Beta(a,b) distribution at x."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(a * math.log(x) + b * math.log1p(-x) + lbeta)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def beta_quantile(p: float, a: float, b: float) -> float:
    """Inverse Beta CDF by bisection; deterministic and dependency-free."""
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if regularized_incomplete_beta(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def jeffreys_interval(k: int, n: int, mass: float = 0.95) -> tuple[float, float]:
    """Equal-tailed Jeffreys credible interval for a proportion: Beta(k+.5, n-k+.5)."""
    tail = (1.0 - mass) / 2.0
    a, b = k + 0.5, n - k + 0.5
    return beta_quantile(tail, a, b), beta_quantile(1.0 - tail, a, b)


def rate_record(numerator: int, denominator: int) -> dict[str, Any]:
    """A rate reported with its Jeffreys posterior mean and 95% credible interval."""
    if denominator == 0:
        return {
            "numerator": 0, "denominator": 0, "value": None,
            "posterior_mean": None, "ci_lower": None, "ci_upper": None,
        }
    lo, hi = jeffreys_interval(numerator, denominator)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator,
        "posterior_mean": (numerator + 0.5) / (denominator + 1.0),
        "ci_lower": lo,
        "ci_upper": hi,
    }


def median_ci(values: list[float], mass: float = 0.95) -> tuple[float | None, float | None]:
    """Distribution-free confidence interval for a median from order statistics.

    Returns the full observed range when the sample is too small to bound the
    median at the requested confidence, so a small sample yields a wide interval
    rather than a false claim of precision.
    """
    n = len(values)
    if n == 0:
        return None, None
    xs = sorted(values)
    tail = (1.0 - mass) / 2.0
    probs = [math.comb(n, i) * 0.5 ** n for i in range(n + 1)]
    lower_rank = 0  # 1-indexed; largest l with P(X <= l-1) <= tail
    l = 1
    while l <= n and sum(probs[:l]) <= tail:
        lower_rank = l
        l += 1
    if lower_rank < 1:
        return xs[0], xs[-1]
    upper_rank = n + 1 - lower_rank
    return xs[lower_rank - 1], xs[upper_rank - 1]


def decide_rate(numerator: int, denominator: int, threshold: float) -> str:
    """Meet the tolerance only when the whole credible interval clears it.

    A zero threshold is a bright line on the count, not a rate to estimate: no
    continuous posterior can put its upper bound at zero, so demanding a Bayesian
    interval there would make the tolerance unmeetable.
    """
    if denominator == 0:
        return NOT_ESTIMATED
    if threshold <= 0.0:
        return MEETS if numerator == 0 else EXCEEDS
    lo, hi = jeffreys_interval(numerator, denominator)
    if hi <= threshold:
        return MEETS
    if lo > threshold:
        return EXCEEDS
    return INDETERMINATE


def decide_count(count: int, observations: int, maximum: int) -> str:
    if observations == 0:
        return NOT_ESTIMATED
    return MEETS if count <= maximum else EXCEEDS


def decide_median(record: dict[str, Any], maximum: float) -> str:
    """Meet the burden ceiling only when the median's confidence interval clears it."""
    if record.get("value") is None:
        return NOT_ESTIMATED
    lo, hi = record.get("ci_lower"), record.get("ci_upper")
    if hi is not None and hi <= maximum:
        return MEETS
    if lo is not None and lo > maximum:
        return EXCEEDS
    return INDETERMINATE


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
            "false_support_rate": rate_record(counts["false_support_n"], counts["false_support_d"]),
            "false_defeat_rate": rate_record(counts["false_defeat_n"], counts["false_defeat_d"]),
            "gap_defeat_confusion_rate": rate_record(counts["confusion_n"], counts["confusion_d"]),
            "gap_insufficiency_confusion_rate": rate_record(counts["insufficiency_n"], counts["insufficiency_d"]),
            "required_node_omission_rate": rate_record(counts["omission_n"], counts["omission_d"]),
        }

    median_lo, median_hi = median_ci(minutes)
    return {
        "response_count": len(responses),
        "false_support_rate": rate_record(false_support_n, false_support_d),
        "false_defeat_rate": rate_record(false_defeat_n, false_defeat_d),
        "gap_defeat_confusion_rate": rate_record(confusion_n, confusion_d),
        "gap_insufficiency_confusion_rate": rate_record(insufficiency_n, insufficiency_d),
        "entity_conjunction_error_rate": rate_record(conjunction_n, conjunction_d),
        "required_node_omission_rate": rate_record(omission_n, omission_d),
        "median_review_minutes": {
            "value": statistics.median(minutes) if minutes else None,
            "ci_lower": median_lo,
            "ci_upper": median_hi,
            "response_count": len(minutes),
        },
        "privacy_or_security_breach_count": {"value": breach_count, "response_count": len(responses)},
        "node_error_metrics": node_error_metrics,
        "node_vectors": vectors,
    }


def decide_metric(metric: str, record: dict[str, Any], threshold: float | int) -> str:
    """Interval-aware decision for one metric against its tolerance."""
    if metric in RATE_METRICS:
        return decide_rate(record["numerator"], record["denominator"], float(threshold))
    if metric == "privacy_or_security_breach_count":
        return decide_count(record["value"], record["response_count"], int(threshold))
    if metric == "median_review_minutes":
        return decide_median(record, float(threshold))
    raise AnalysisError(f"unknown metric {metric!r}")


def threshold_metrics(raw: dict[str, Any], tolerances: dict[str, float | int]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for metric, tolerance_name in METRIC_TOLERANCES.items():
        threshold = tolerances[tolerance_name]
        decision = decide_metric(metric, raw[metric], threshold)
        results[metric] = {
            **raw[metric],
            "threshold_max": threshold,
            "decision": decision,
            "status": DECISION_TO_STATUS[decision],
        }
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
            threshold = tolerances[tolerance_name]
            decision = decide_metric(metric, observed_record, threshold)
            node_result[metric] = {
                **observed_record,
                "threshold_max": threshold,
                "decision": decision,
                "status": DECISION_TO_STATUS[decision],
            }
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
    checks: list[str] = []

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

    def make_use(overrides: dict[str, float] | None = None) -> list[dict[str, Any]]:
        merged = dict(tolerance)
        if overrides:
            merged.update(overrides)
        return [{
            "use_id": "u", "action_classes": ["c"], "tolerances": merged,
            "minimum_reach_thresholds": reach, "required_coverage_tags": [],
            "required_controlled_pair_ids": [],
        }]

    def population(
        vector: dict[tuple[str, str | None], str],
        n_responses: int,
        error_node: tuple[str, str | None] | None = None,
        error_value: str | None = None,
        errors: int = 0,
        drop_node: tuple[str, str | None] | None = None,
        drops: int = 0,
        minutes_of: Any = None,
        resolution_of: Any = None,
    ):
        """Build n responses over enough cases/reviewers to satisfy reach.

        The first `errors` responses carry `error_value` at `error_node`; the
        first `drops` omit `drop_node`. Everything else matches `vector`.
        """
        reviewers = ("RA", "RB", "RC")
        refs: dict[str, dict[tuple[str, str | None], str]] = {}
        responses: list[dict[str, Any]] = []
        made = 0
        case_index = 0
        while made < n_responses:
            case_id = f"C{case_index}"
            refs[case_id] = dict(vector)
            for reviewer in reviewers:
                if made >= n_responses:
                    break
                observed = dict(vector)
                if error_node is not None and made < errors:
                    observed[error_node] = error_value
                if drop_node is not None and made < drops:
                    observed.pop(drop_node, None)
                minutes = minutes_of(made) if callable(minutes_of) else (minutes_of if minutes_of is not None else 10)
                responses.append(synthetic_response(
                    reviewer, case_id, observed, minutes=minutes,
                    presentation_order=case_index + 1,
                    resolution=resolution_of(made) if callable(resolution_of) else resolution_of,
                ))
                made += 1
            case_index += 1
        classes = {case_id: "c" for case_id in refs}
        required = {"c": {node for node, _entity in vector}}
        return responses, refs, classes, required

    def decision_of(result: dict[str, Any], metric: str) -> str:
        return result["uses"]["u"]["class_results"]["c"]["metrics"][metric]["decision"]

    # --- The core objection: a clean but small sample cannot demonstrate a low
    #     error ceiling, and must not be reported as if it had. ---
    gap_only = {("X", None): "record_gap"}
    small_clean, refs, classes, required = population(gap_only, 12)
    result = analyze(small_clean, refs, classes, required, make_use())
    assert decision_of(result, "false_support_rate") == INDETERMINATE
    assert result["uses"]["u"]["status"] == NOT_ESTIMATED
    checks.append("small clean sample is indeterminate, not a pass")

    # Enough clean observations to put the whole credible interval under 0.05.
    large_clean, refs, classes, required = population(gap_only, 60)
    result = analyze(large_clean, refs, classes, required, make_use())
    metric = result["uses"]["u"]["class_results"]["c"]["metrics"]["false_support_rate"]
    assert metric["decision"] == MEETS and metric["numerator"] == 0
    assert metric["ci_upper"] <= 0.05
    checks.append("large clean sample meets tolerance")

    # A rate well above tolerance is demonstrably exceeded once the lower bound clears it.
    dirty, refs, classes, required = population(
        gap_only, 60, error_node=("X", None), error_value="support", errors=20)
    result = analyze(dirty, refs, classes, required, make_use())
    metric = result["uses"]["u"]["class_results"]["c"]["metrics"]["false_support_rate"]
    assert metric["decision"] == EXCEEDS and metric["ci_lower"] > 0.05
    checks.append("clearly-high rate exceeds tolerance")

    # A rate near the threshold with moderate data stays indeterminate: the
    # interval straddles the line, so neither claim is earned.
    borderline, refs, classes, required = population(
        gap_only, 60, error_node=("X", None), error_value="support", errors=2)
    assert decision_of(analyze(borderline, refs, classes, required, make_use()), "false_support_rate") == INDETERMINATE
    checks.append("near-threshold rate stays indeterminate")

    # A zero tolerance is a bright line on the count, not a rate to estimate: a
    # single error exceeds it even at small n, and none meets it.
    omit_vec = {("X", None): "record_gap", ("Y", None): "support"}
    dropped, refs, classes, required = population(omit_vec, 12, drop_node=("X", None), drops=1)
    assert decision_of(analyze(dropped, refs, classes, required, make_use()), "required_node_omission_rate") == EXCEEDS
    clean, refs, classes, required = population(omit_vec, 12)
    assert decision_of(analyze(clean, refs, classes, required, make_use()), "required_node_omission_rate") == MEETS
    checks.append("zero-tolerance omission is a bright line")

    # The same bright line for the entity-conjunction error, reported per response.
    split_vec = {("B1", "E1"): "record_gap", ("B1", "E2"): "support"}
    honest_res = {"J_B": {"satisfied": False, "satisfying_entity_ids": []}}
    dishonest_res = {"J_B": {"satisfied": True, "satisfying_entity_ids": ["E1"]}}
    resolutions_true = {f"C{i}": honest_res for i in range(40)}
    honest, refs, classes, required = population(split_vec, 12, resolution_of=lambda _i: honest_res)
    assert decision_of(analyze(honest, refs, classes, required, make_use(), None, resolutions_true), "entity_conjunction_error_rate") == MEETS
    dishonest, refs, classes, required = population(split_vec, 12, resolution_of=lambda _i: dishonest_res)
    assert decision_of(analyze(dishonest, refs, classes, required, make_use(), None, resolutions_true), "entity_conjunction_error_rate") == EXCEEDS
    checks.append("entity-conjunction split rejected, honest split accepted")

    # Median burden: a distribution-free interval must clear the ceiling.
    fast, refs, classes, required = population(gap_only, 30, minutes_of=10)
    assert decision_of(analyze(fast, refs, classes, required, make_use()), "median_review_minutes") == MEETS
    slow, refs, classes, required = population(gap_only, 30, minutes_of=40)
    assert decision_of(analyze(slow, refs, classes, required, make_use()), "median_review_minutes") == EXCEEDS
    spread, refs, classes, required = population(gap_only, 6, minutes_of=lambda i: 5 if i < 3 else 40)
    assert decision_of(analyze(spread, refs, classes, required, make_use()), "median_review_minutes") == INDETERMINATE
    checks.append("median burden decided by its interval")

    # A confirmed breach is a bright line regardless of sample size.
    breached, refs, classes, required = population(gap_only, 12)
    breached[0]["privacy_security_incidents"] = [{"incident_id": "I1", "confirmed_breach": True}]
    assert decision_of(analyze(breached, refs, classes, required, make_use()), "privacy_or_security_breach_count") == EXCEEDS
    checks.append("confirmed breach exceeds")

    # Posterior interval sanity: contains the mean and tightens with more data.
    lo12, hi12 = jeffreys_interval(0, 12)
    lo120, hi120 = jeffreys_interval(0, 120)
    assert 0.0 <= lo12 <= (0.5 / 13) <= hi12 <= 1.0
    assert hi120 < hi12
    checks.append("posterior interval contains mean and tightens with n")

    # A fully clean, richly exercised sample can reach a use-level pass, so the
    # framework is not merely capable of withholding judgement.
    rich_vec = {
        ("FS", None): "record_gap",
        ("FD", None): "support",
        ("SD", None): "substantive_defeat",
        ("NE", None): "not_established",
        ("BB", "E1"): "support",
    }
    rich_res = {f"C{i}": {"J_B": {"satisfied": True, "satisfying_entity_ids": ["E1"]}} for i in range(40)}
    rich, refs, classes, required = population(
        rich_vec, 60, resolution_of=lambda _i: {"J_B": {"satisfied": True, "satisfying_entity_ids": ["E1"]}})
    result = analyze(rich, refs, classes, required, make_use(), None, rich_res)
    assert result["uses"]["u"]["status"] == "PASS"
    checks.append("rich clean sample reaches a use-level pass")

    # --- Structural checks that do not depend on the threshold semantics. ---
    struct_vec = {("N1", None): "substantive_defeat", ("N3", None): "support"}
    struct, refs, classes, required = population(struct_vec, 12)
    # reviewer disagreement: two reviewers differ on one case/node
    disagree = copy.deepcopy(struct)
    target = next(r for r in disagree if r["case_id"] == "C0" and r["pseudonymous_reviewer_id"] == "RB")
    next(v for v in target["node_verdicts"] if v["node_id"] == "N3")["verdict"] = "record_gap"
    dresult = analyze(disagree, refs, classes, required, make_use())
    assert dresult["reviewer_disagreement"]["overall"]["value"] > 0
    checks.append("reviewer disagreement")

    # blinded-replicate instability: a reviewer changes a verdict within a group
    inst = copy.deepcopy(struct)
    original = next(r for r in inst if r["case_id"] == "C0" and r["pseudonymous_reviewer_id"] == "RA")
    original["presentation"]["blinded_replicate_group_id"] = "BLIND-C0-RA"
    extra = synthetic_response("RA", "C0", refs["C0"], presentation_order=99, replicate_group="BLIND-C0-RA")
    next(v for v in extra["node_verdicts"] if v["node_id"] == "N3")["verdict"] = "record_gap"
    inst.append(extra)
    iresult = analyze(inst, refs, classes, required, make_use())
    assert iresult["reviewer_instability"]["overall"]["value"] > 0
    checks.append("blinded-replicate test-retest instability")

    # across-case variation is descriptive, not test-retest instability
    assert iresult["across_case_conditional_variation"]["overall"]["status"] in {"ESTIMATED", NOT_ESTIMATED}
    checks.append("across-case variation reported separately from instability")

    # minimum reach blocks a one-response pass
    one = analyze([struct[0]], refs, classes, required, make_use())
    assert all(item["status"] == NOT_ESTIMATED for item in one["uses"].values())
    checks.append("minimum reach blocks one-response pass")

    # exposed demonstration fixtures are dropped before coverage and reach
    exposure_meta = {case_id: {"coverage_tags": ["t"], "pair_id": None, "exposure": "exposed_demonstration"} for case_id in refs}
    exposed_use = [{
        "use_id": "u", "action_classes": ["c"], "tolerances": tolerance,
        "minimum_reach_thresholds": reach, "required_coverage_tags": ["t"],
        "required_controlled_pair_ids": [],
    }]
    exposed = analyze(struct, refs, classes, required, exposed_use, exposure_meta)
    assert exposed["uses"]["u"]["substantive_coverage"]["missing_coverage_tags"] == ["t"]
    checks.append("exposed fixtures excluded from coverage")

    # substantive contrast coverage blocks a numeric-reach false pass
    coverage_meta = {case_id: {"coverage_tags": ["ordinary"], "pair_id": None} for case_id in refs}
    contrast_use = [{
        "use_id": "u", "action_classes": ["c"], "tolerances": tolerance,
        "minimum_reach_thresholds": reach, "required_coverage_tags": ["required_contrast"],
        "required_controlled_pair_ids": [],
    }]
    contrast = analyze(struct, refs, classes, required, contrast_use, coverage_meta)
    assert contrast["uses"]["u"]["substantive_coverage"]["missing_coverage_tags"] == ["required_contrast"]
    assert contrast["uses"]["u"]["status"] == NOT_ESTIMATED
    checks.append("substantive contrast coverage blocks numeric-reach false pass")

    # zero responses
    empty = analyze([], refs, classes, required, make_use())
    assert empty["analysis_status"] == NOT_ESTIMATED and all(item["status"] == NOT_ESTIMATED for item in empty["uses"].values())
    checks.append("zero-response NOT_ESTIMATED")

    # per-candidate omission: dropping one candidate's verdict is caught
    per_candidate, refs, classes, required = population(split_vec, 12, drop_node=("B1", "E2"), drops=1, resolution_of=lambda _i: honest_res)
    assert decision_of(analyze(per_candidate, refs, classes, required, make_use(), None, resolutions_true), "required_node_omission_rate") == EXCEEDS
    checks.append("per-candidate omission detected")

    # separate opening record preserves the immutable key commitment
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
