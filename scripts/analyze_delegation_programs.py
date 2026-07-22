#!/usr/bin/env python3
"""Validate and analyze the three frozen Delegation Assurance programmes.

The analyzer preserves observation-level vectors and applies familywise,
noncompensatory decision rules.  It never replaces the family vector with a
single score.  A valid input with no observations returns NOT_ESTIMATED.
Integrity failures (split overlap, failed reset, reference leakage, or a
pre-lock oracle join) are invalid analysis inputs rather than empirical
failures.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT_DIR = ROOT / "assurance" / "delegation" / "empirical"
SPECIFICATIONS_NAME = "program-specifications.json"
SPECIFICATIONS_SCHEMA_NAME = "program-specifications.schema.json"
OUTPUT_SCHEMA_NAME = "analysis-output.schema.json"
LOCAL_PRESENTATION_ARMS = {
    "baseline",
    "authority",
    "placebo",
    "order_reversal",
    "shortcut",
}


class AnalysisError(ValueError):
    """A schema, design-integrity, or analysis-contract failure."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--validate-specs", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisError(f"{path}: cannot load JSON: {exc}") from exc


def schema_issues(instance: Any, schema: Any, label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    issues: list[str] = []
    for issue in validator.iter_errors(instance):
        location = ".".join(str(part) for part in issue.absolute_path) or "<root>"
        issues.append(f"{label}:{location}: {issue.message}")
    return sorted(issues)


def require_schema(instance: Any, schema: Any, label: str) -> None:
    issues = schema_issues(instance, schema, label)
    if issues:
        raise AnalysisError("\n".join(issues))


def iso(value: str, label: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise AnalysisError(f"{label}: invalid ISO timestamp {value!r}") from exc


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def mean(values: Iterable[float]) -> float:
    data = list(values)
    return statistics.fmean(data)


def normal_lcb(values: list[float], critical: float) -> float | None:
    if len(values) < 2:
        return None
    return mean(values) - critical * statistics.stdev(values) / math.sqrt(len(values))


def unique_ids(rows: list[dict[str, Any]], key: str, label: str) -> None:
    values = [row[key] for row in rows]
    duplicates = sorted({value for value in values if values.count(value) > 1})
    if duplicates:
        raise AnalysisError(f"{label}: duplicate {key} values {duplicates}")


def banned_key_paths(value: Any, banned_tokens: set[str], prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else key
            normalized = key.lower().replace("-", "_")
            if any(token in normalized for token in banned_tokens):
                paths.append(path)
            paths.extend(banned_key_paths(item, banned_tokens, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(banned_key_paths(item, banned_tokens, f"{prefix}[{index}]"))
    return paths


def validate_specifications(artifact_dir: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    specifications = load_json(artifact_dir / SPECIFICATIONS_NAME)
    schema = load_json(artifact_dir / SPECIFICATIONS_SCHEMA_NAME)
    require_schema(specifications, schema, SPECIFICATIONS_NAME)
    by_program = {item["program_id"]: item for item in specifications["specifications"]}
    expected = {
        "local_discrimination": ("DA_LOCAL_001_SPEC", "DA_LOCAL_001"),
        "predictive_typed_ablation": ("DA_PRED_001_SPEC", "DA_PRED_001"),
        "reviewer_reconstruction": ("DA_RECON_001_SPEC", "DA_RECON_001"),
    }
    if set(by_program) != set(expected) or len(by_program) != 3:
        raise AnalysisError("program specifications do not exactly cover the three declared programmes")
    for program_id, (specification_id, claim_id) in expected.items():
        specification = by_program[program_id]
        if (
            specification["specification_id"] != specification_id
            or specification["claim_id"] != claim_id
        ):
            raise AnalysisError(f"{program_id}: specification-to-claim binding is inconsistent")
        schema_path = artifact_dir / specification["input_schema"]
        input_schema = load_json(schema_path)
        Draft202012Validator.check_schema(input_schema)
        thresholds = specification["thresholds"]
        required_thresholds = {
            "local_discrimination": {
                "minimum_observations_per_family",
                "minimum_selective_margin",
                "selective_margin_lcb_strictly_above",
                "minimum_control_accuracy",
            },
            "predictive_typed_ablation": {
                "minimum_observations_per_family",
                "minimum_trace_families_per_family",
                "minimum_mean_brier_improvement",
                "brier_improvement_lcb_strictly_above",
                "maximum_typed_brier_loss",
                "maximum_typed_ece",
            },
            "reviewer_reconstruction": {
                "minimum_observations_per_arm_per_family",
                "minimum_cases_per_family",
                "minimum_reviewers_per_arm_per_family",
                "minimum_typed_minus_degraded_concordance",
                "concordance_difference_lcb_strictly_above",
                "maximum_typed_false_certainty",
            },
        }[program_id]
        if set(thresholds) != required_thresholds:
            raise AnalysisError(f"{program_id}: threshold vector is incomplete or contains undeclared fields")
        expected_bindings = {
            "local_discrimination": {"assignment_manifest", "split_manifest"},
            "predictive_typed_ablation": {"feature_manifest", "held_out_manifest"},
            "reviewer_reconstruction": {"assignment_manifest", "held_out_manifest"},
        }[program_id]
        if set(specification["integrity_rules"]["required_design_object_bindings"]) != expected_bindings:
            raise AnalysisError(f"{program_id}: frozen design-object binding vector is inconsistent")
    output_schema = load_json(artifact_dir / OUTPUT_SCHEMA_NAME)
    Draft202012Validator.check_schema(output_schema)
    return specifications, by_program


def make_output(input_data: dict[str, Any], specification: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "program_id": input_data["program_id"],
        "specification_id": specification["specification_id"],
        "specification_version": specification["specification_version"],
        "specification_sha256": canonical_sha256(specification),
        "input_id": input_data["input_id"],
        "decision": "NOT_ESTIMATED",
        "not_estimated_reason": None,
        "scalar_aggregation_permitted": False,
        "integrity_diagnostics": {
            "split": "NOT_APPLICABLE",
            "reset": "NOT_APPLICABLE",
            "leakage": "PASS",
            "oracle_masking": "PASS",
            "reference_join": "PASS",
            "design_object_sha256s": {},
        },
        "family_results": [],
        "observation_vectors": [],
    }


def verify_design_object_bindings(
    input_data: dict[str, Any], expected_names: set[str]
) -> dict[str, str]:
    bindings = input_data["design_object_bindings"]
    if set(bindings) != expected_names:
        raise AnalysisError(
            f"{input_data['program_id']}: design-object bindings do not match {sorted(expected_names)}"
        )
    input_created = iso(input_data["created_at"], input_data["input_id"])
    lock_key = {
        "local_discrimination": "response_locked_at",
        "predictive_typed_ablation": "prediction_locked_at",
        "reviewer_reconstruction": "review_locked_at",
    }[input_data["program_id"]]
    first_lock = (
        min(iso(row[lock_key], f"{input_data['program_id']}.{lock_key}") for row in input_data["observations"])
        if input_data["observations"]
        else input_created
    )
    verified: dict[str, str] = {}
    for name, manifest in bindings.items():
        unsigned = {key: value for key, value in manifest.items() if key != "sha256"}
        derived = canonical_sha256(unsigned)
        if derived != manifest["sha256"]:
            raise AnalysisError(f"{input_data['program_id']}.{name}: SHA-256 does not match manifest content")
        if iso(manifest["frozen_at"], f"{name}.frozen_at") >= first_lock:
            raise AnalysisError(
                f"{input_data['program_id']}.{name}: manifest was not frozen before the first locked outcome"
            )
        verified[name] = derived
    return verified


def finish_decision(output: dict[str, Any]) -> None:
    decisions = [item["decision"] for item in output["family_results"]]
    if "FAIL" in decisions:
        output["decision"] = "FAIL"
        output["not_estimated_reason"] = None
    elif "NOT_ESTIMATED" in decisions:
        output["decision"] = "NOT_ESTIMATED"
        output["not_estimated_reason"] = (
            "NO_OBSERVATIONS" if not output["observation_vectors"] else "REQUIRED_FAMILY_NOT_ESTIMATED"
        )
    else:
        output["decision"] = "PASS"
        output["not_estimated_reason"] = None


def missing_family_result(family: str, thresholds: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": family,
        "decision": "NOT_ESTIMATED",
        "counts": {"observations": 0},
        "metrics": {},
        "thresholds": thresholds,
        "reasons": ["No observations were supplied for this required family."],
    }


def analyze_local(input_data: dict[str, Any], specification: dict[str, Any]) -> dict[str, Any]:
    output = make_output(input_data, specification)
    output["integrity_diagnostics"].update({"split": "PASS", "reset": "PASS"})
    design = input_data["design"]
    output["integrity_diagnostics"]["design_object_sha256s"] = verify_design_object_bindings(
        input_data, set(specification["integrity_rules"]["required_design_object_bindings"])
    )
    assignment_content = input_data["design_object_bindings"]["assignment_manifest"]["content"]
    if set(assignment_content) != {
        "randomization_unit",
        "randomization_method",
        "reset_policy",
        "carryover_detected",
        "assignments",
    }:
        raise AnalysisError("local discrimination: assignment manifest has the wrong fields")
    if (
        assignment_content["randomization_unit"] != "package_presentation"
        or assignment_content["randomization_method"] != "frozen_external_randomization"
        or assignment_content["reset_policy"] != design["reset_policy"]
        or assignment_content["carryover_detected"] != design["carryover_detected"]
    ):
        raise AnalysisError("local discrimination: assignment manifest does not encode the declared design")
    scheduled = assignment_content["assignments"]
    if not isinstance(scheduled, list):
        raise AnalysisError("local discrimination: assignment manifest assignments must be a list")
    scheduled_by_observation: dict[str, dict[str, Any]] = {}
    for assignment in scheduled:
        if not isinstance(assignment, dict) or set(assignment) != {
            "observation_id",
            "presentation_order",
            "presentation_ids",
        }:
            raise AnalysisError("local discrimination: malformed package-presentation assignment")
        observation_id = assignment["observation_id"]
        if observation_id in scheduled_by_observation:
            raise AnalysisError("local discrimination: duplicate observation in assignment manifest")
        order = assignment["presentation_order"]
        presentation_ids = assignment["presentation_ids"]
        if (
            not isinstance(order, list)
            or len(order) != len(LOCAL_PRESENTATION_ARMS)
            or set(order) != LOCAL_PRESENTATION_ARMS
            or not isinstance(presentation_ids, dict)
            or set(presentation_ids) != LOCAL_PRESENTATION_ARMS
            or len(set(presentation_ids.values())) != len(LOCAL_PRESENTATION_ARMS)
            or not all(isinstance(value, str) and value for value in presentation_ids.values())
        ):
            raise AnalysisError("local discrimination: assignment doesn't allocate all five presentation arms")
        scheduled_by_observation[observation_id] = assignment
    split_content = input_data["design_object_bindings"]["split_manifest"]["content"]
    expected_split = {
        "split_unit": "base_item",
        "development_base_item_ids": design["development_base_item_ids"],
        "held_out_base_item_ids": design["held_out_base_item_ids"],
    }
    if split_content != expected_split:
        raise AnalysisError("local discrimination: split manifest does not match the declared item split")
    development = set(design["development_base_item_ids"])
    held_out = set(design["held_out_base_item_ids"])
    if development & held_out:
        raise AnalysisError("local discrimination: development and held-out base-item splits overlap")
    rows = input_data["observations"]
    unique_ids(rows, "observation_id", "local discrimination")
    if set(scheduled_by_observation) != {row["observation_id"] for row in rows}:
        raise AnalysisError(
            "local discrimination: assignment manifest doesn't exactly cover observation IDs"
        )
    seen_pairs: set[tuple[str, str]] = set()
    banned = set(specification["integrity_rules"]["banned_view_key_tokens"])
    vectors: list[dict[str, Any]] = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["base_item_id"] not in held_out:
            raise AnalysisError(f"{row['observation_id']}: base item is not in the frozen held-out split")
        pair = (row["family"], row["base_item_id"])
        if pair in seen_pairs:
            raise AnalysisError(f"{row['observation_id']}: duplicate independent family/base pair")
        seen_pairs.add(pair)
        if not row["reset_confirmed"]:
            raise AnalysisError(f"{row['observation_id']}: evaluator reset was not confirmed")
        leaked = banned_key_paths(row["evaluator_view"], banned)
        if leaked:
            raise AnalysisError(f"{row['observation_id']}: evaluator view leaks reference keys {leaked}")
        if iso(row["reference_joined_at"], row["observation_id"]) <= iso(
            row["response_locked_at"], row["observation_id"]
        ):
            raise AnalysisError(f"{row['observation_id']}: reference was not joined after response lock")
        raw_effect = row["authority_endpoint"] - row["baseline_endpoint"]
        signed_effect = row["reference_direction"] * raw_effect
        placebo_instability = abs(row["placebo_endpoint"] - row["baseline_endpoint"])
        order_instability = abs(row["order_reversal_endpoint"] - row["authority_endpoint"])
        shortcut_instability = abs(row["shortcut_endpoint"] - row["baseline_endpoint"])
        nuisance_floor = max(placebo_instability, order_instability, shortcut_instability)
        values = {
            "base_item_id": row["base_item_id"],
            "reference_direction": row["reference_direction"],
            "baseline_endpoint": row["baseline_endpoint"],
            "authority_endpoint": row["authority_endpoint"],
            "placebo_endpoint": row["placebo_endpoint"],
            "order_reversal_endpoint": row["order_reversal_endpoint"],
            "shortcut_endpoint": row["shortcut_endpoint"],
            "raw_package_effect": raw_effect,
            "reference_concordant_effect": signed_effect,
            "placebo_instability": placebo_instability,
            "order_instability": order_instability,
            "shortcut_instability": shortcut_instability,
            "matched_nuisance_floor": nuisance_floor,
            "selective_margin": signed_effect - nuisance_floor,
            "control_correct": row["control_correct"],
        }
        vector = {"observation_id": row["observation_id"], "family": row["family"], "values": values}
        vectors.append(vector)
        by_family[row["family"]].append(vector)
    output["observation_vectors"] = vectors
    thresholds = specification["thresholds"]
    critical = specification["uncertainty"]["critical_value"]
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        reported_thresholds = {
            "minimum_observations": thresholds["minimum_observations_per_family"],
            "minimum_selective_margin": thresholds["minimum_selective_margin"],
            "selective_margin_lcb_strictly_above": thresholds["selective_margin_lcb_strictly_above"],
            "minimum_control_accuracy": thresholds["minimum_control_accuracy"],
        }
        if not family_rows:
            output["family_results"].append(missing_family_result(family, reported_thresholds))
            continue
        margins = [row["values"]["selective_margin"] for row in family_rows]
        control_accuracy = mean(float(row["values"]["control_correct"]) for row in family_rows)
        lcb = normal_lcb(margins, critical)
        metrics = {
            "mean_raw_package_effect": mean(row["values"]["raw_package_effect"] for row in family_rows),
            "mean_reference_concordant_effect": mean(row["values"]["reference_concordant_effect"] for row in family_rows),
            "mean_placebo_instability": mean(row["values"]["placebo_instability"] for row in family_rows),
            "mean_order_instability": mean(row["values"]["order_instability"] for row in family_rows),
            "mean_shortcut_instability": mean(row["values"]["shortcut_instability"] for row in family_rows),
            "mean_matched_nuisance_floor": mean(row["values"]["matched_nuisance_floor"] for row in family_rows),
            "mean_selective_margin": mean(margins),
            "selective_margin_lcb_95": lcb,
            "control_accuracy": control_accuracy,
        }
        reasons: list[str] = []
        if len(family_rows) < thresholds["minimum_observations_per_family"]:
            reasons.append("Family has fewer than the frozen minimum independent base pairs.")
        if metrics["mean_selective_margin"] < thresholds["minimum_selective_margin"]:
            reasons.append("Mean selective margin is below the frozen practical threshold.")
        if lcb is None or lcb <= thresholds["selective_margin_lcb_strictly_above"]:
            reasons.append("The 95% lower confidence bound does not exceed zero.")
        if control_accuracy < thresholds["minimum_control_accuracy"]:
            reasons.append("Control accuracy is below the frozen threshold.")
        output["family_results"].append(
            {
                "family": family,
                "decision": "FAIL" if reasons else "PASS",
                "counts": {"observations": len(family_rows)},
                "metrics": metrics,
                "thresholds": reported_thresholds,
                "reasons": reasons,
            }
        )
    finish_decision(output)
    return output


def expected_calibration_error(rows: list[dict[str, Any]], bins: int = 10) -> float:
    total = len(rows)
    error = 0.0
    for bin_index in range(bins):
        members = [row for row in rows if row["values"]["calibration_bin"] == bin_index]
        if not members:
            continue
        predicted = mean(row["values"]["typed_probability"] for row in members)
        observed = mean(row["values"]["target"] for row in members)
        error += len(members) / total * abs(predicted - observed)
    return error


def analyze_predictive(input_data: dict[str, Any], specification: dict[str, Any]) -> dict[str, Any]:
    output = make_output(input_data, specification)
    output["integrity_diagnostics"].update({"split": "PASS", "reset": "NOT_APPLICABLE"})
    design = input_data["design"]
    output["integrity_diagnostics"]["design_object_sha256s"] = verify_design_object_bindings(
        input_data, set(specification["integrity_rules"]["required_design_object_bindings"])
    )
    feature_content = input_data["design_object_bindings"]["feature_manifest"]["content"]
    expected_feature_content = {
        "feature_allowlist": design["feature_allowlist"],
        "typed_feature_keys": design["feature_allowlist"],
        "baseline_feature_keys": [
            key for key in design["feature_allowlist"] if key != "typed_representation"
        ],
        "prediction_procedure_id": design["prediction_procedure_id"],
        "software_version": design["software_version"],
        "loss": "brier",
        "calibration_bins": 10,
    }
    if feature_content != expected_feature_content:
        raise AnalysisError("predictive ablation: feature manifest does not match the frozen feature design")
    held_out_content = input_data["design_object_bindings"]["held_out_manifest"]["content"]
    expected_held_out_content = {
        "split_unit": "trace_family",
        "training_trace_family_ids": design["training_trace_family_ids"],
        "held_out_trace_family_ids": design["held_out_trace_family_ids"],
    }
    if held_out_content != expected_held_out_content:
        raise AnalysisError("predictive ablation: held-out manifest does not match the declared split")
    training = set(design["training_trace_family_ids"])
    held_out = set(design["held_out_trace_family_ids"])
    if training & held_out:
        raise AnalysisError("predictive ablation: training and held-out trace-family splits overlap")
    expected_allowlist = set(specification["integrity_rules"]["feature_allowlist"])
    if set(design["feature_allowlist"]) != expected_allowlist:
        raise AnalysisError("predictive ablation: feature allowlist differs from the frozen specification")
    banned = set(specification["integrity_rules"]["banned_view_key_tokens"])
    rows = input_data["observations"]
    unique_ids(rows, "observation_id", "predictive ablation")
    vectors: list[dict[str, Any]] = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["trace_family_id"] not in held_out:
            raise AnalysisError(f"{row['observation_id']}: trace family is not in the held-out split")
        view_keys = set(row["predictor_view"])
        disallowed = view_keys - expected_allowlist
        if disallowed:
            raise AnalysisError(f"{row['observation_id']}: predictor view contains non-allowlisted fields {sorted(disallowed)}")
        leaked = banned_key_paths(row["predictor_view"], banned)
        if leaked:
            raise AnalysisError(f"{row['observation_id']}: predictor view leaks oracle/reference fields {leaked}")
        if iso(row["reference_joined_at"], row["observation_id"]) <= iso(
            row["prediction_locked_at"], row["observation_id"]
        ):
            raise AnalysisError(f"{row['observation_id']}: reference was not joined after prediction lock")
        target = row["target"]
        typed_loss = (row["typed_probability"] - target) ** 2
        baseline_loss = (row["baseline_probability"] - target) ** 2
        values = {
            "trace_family_id": row["trace_family_id"],
            "target": target,
            "typed_probability": row["typed_probability"],
            "baseline_probability": row["baseline_probability"],
            "typed_brier_loss": typed_loss,
            "baseline_brier_loss": baseline_loss,
            "paired_brier_improvement": baseline_loss - typed_loss,
            "calibration_bin": min(int(row["typed_probability"] * 10), 9),
        }
        vector = {"observation_id": row["observation_id"], "family": row["family"], "values": values}
        vectors.append(vector)
        by_family[row["family"]].append(vector)
    output["observation_vectors"] = vectors
    thresholds = specification["thresholds"]
    critical = specification["uncertainty"]["critical_value"]
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        reported_thresholds = {
            "minimum_observations": thresholds["minimum_observations_per_family"],
            "minimum_trace_families": thresholds["minimum_trace_families_per_family"],
            "minimum_mean_brier_improvement": thresholds["minimum_mean_brier_improvement"],
            "brier_improvement_lcb_strictly_above": thresholds["brier_improvement_lcb_strictly_above"],
            "maximum_typed_brier_loss": thresholds["maximum_typed_brier_loss"],
            "maximum_typed_ece": thresholds["maximum_typed_ece"],
        }
        if not family_rows:
            output["family_results"].append(missing_family_result(family, reported_thresholds))
            continue
        improvements = [row["values"]["paired_brier_improvement"] for row in family_rows]
        improvements_by_trace_family: dict[str, list[float]] = defaultdict(list)
        for row in family_rows:
            improvements_by_trace_family[row["values"]["trace_family_id"]].append(
                row["values"]["paired_brier_improvement"]
            )
        cluster_means = [mean(values) for values in improvements_by_trace_family.values()]
        lcb = normal_lcb(cluster_means, critical)
        metrics = {
            "mean_typed_brier_loss": mean(row["values"]["typed_brier_loss"] for row in family_rows),
            "mean_baseline_brier_loss": mean(row["values"]["baseline_brier_loss"] for row in family_rows),
            "row_weighted_mean_paired_brier_improvement": mean(improvements),
            "mean_trace_family_paired_brier_improvement": mean(cluster_means),
            "trace_family_cluster_paired_brier_improvement_lcb_95": lcb,
            "typed_ece_10_bin": expected_calibration_error(family_rows),
        }
        reasons: list[str] = []
        if len(family_rows) < thresholds["minimum_observations_per_family"]:
            reasons.append("Family has fewer than the frozen minimum held-out cases.")
        if len(cluster_means) < thresholds["minimum_trace_families_per_family"]:
            reasons.append("Family has fewer than the frozen minimum held-out trace families.")
        if (
            metrics["mean_trace_family_paired_brier_improvement"]
            < thresholds["minimum_mean_brier_improvement"]
        ):
            reasons.append("Mean paired Brier improvement is below the practical threshold.")
        if lcb is None or lcb <= thresholds["brier_improvement_lcb_strictly_above"]:
            reasons.append("The 95% lower confidence bound does not exclude no improvement.")
        if metrics["mean_typed_brier_loss"] > thresholds["maximum_typed_brier_loss"]:
            reasons.append("Typed Brier loss exceeds the frozen maximum.")
        if metrics["typed_ece_10_bin"] > thresholds["maximum_typed_ece"]:
            reasons.append("Typed ten-bin calibration error exceeds the frozen maximum.")
        output["family_results"].append(
            {
                "family": family,
                "decision": "FAIL" if reasons else "PASS",
                "counts": {
                    "observations": len(family_rows),
                    "trace_families": len(cluster_means),
                },
                "metrics": metrics,
                "thresholds": reported_thresholds,
                "reasons": reasons,
            }
        )
    finish_decision(output)
    return output


def cluster_standard_error(
    rows: list[dict[str, Any]], outcome_key: str, cluster_key: str
) -> float | None:
    typed = [row for row in rows if row["values"]["condition"] == "typed"]
    degraded = [row for row in rows if row["values"]["condition"] == "degraded"]
    typed_mean = mean(row["values"][outcome_key] for row in typed)
    degraded_mean = mean(row["values"][outcome_key] for row in degraded)
    scores: dict[str, float] = defaultdict(float)
    for row in typed:
        scores[str(row["values"][cluster_key])] += (
            row["values"][outcome_key] - typed_mean
        ) / len(typed)
    for row in degraded:
        scores[str(row["values"][cluster_key])] -= (
            row["values"][outcome_key] - degraded_mean
        ) / len(degraded)
    clusters = len(scores)
    if clusters < 2:
        return None
    variance = clusters / (clusters - 1) * sum(score**2 for score in scores.values())
    return math.sqrt(max(variance, 0.0))


def analyze_reviewer(input_data: dict[str, Any], specification: dict[str, Any]) -> dict[str, Any]:
    output = make_output(input_data, specification)
    output["integrity_diagnostics"].update({"split": "PASS", "reset": "PASS"})
    output["integrity_diagnostics"]["design_object_sha256s"] = verify_design_object_bindings(
        input_data, set(specification["integrity_rules"]["required_design_object_bindings"])
    )
    assignment_content = input_data["design_object_bindings"]["assignment_manifest"]["content"]
    if set(assignment_content) != {
        "assignment_unit",
        "randomization_method",
        "reset_policy",
        "assignments",
    }:
        raise AnalysisError("reviewer reconstruction: assignment manifest has the wrong fields")
    if (
        assignment_content["assignment_unit"] != "reviewer_case_presentation"
        or assignment_content["randomization_method"] != "frozen_external_randomization"
        or assignment_content["reset_policy"] != input_data["design"]["reset_policy"]
    ):
        raise AnalysisError("reviewer reconstruction: assignment manifest does not encode the declared design")
    scheduled = assignment_content["assignments"]
    if not isinstance(scheduled, list):
        raise AnalysisError("reviewer reconstruction: assignment manifest assignments must be a list")
    scheduled_by_judgment: dict[str, dict[str, Any]] = {}
    for assignment in scheduled:
        if not isinstance(assignment, dict) or set(assignment) != {
            "judgment_id",
            "reviewer_id",
            "case_id",
            "condition",
        }:
            raise AnalysisError("reviewer reconstruction: malformed randomized assignment")
        judgment_id = assignment["judgment_id"]
        if judgment_id in scheduled_by_judgment:
            raise AnalysisError("reviewer reconstruction: duplicate judgment in assignment manifest")
        scheduled_by_judgment[judgment_id] = assignment
    held_out_content = input_data["design_object_bindings"]["held_out_manifest"]["content"]
    expected_held_out = {
        "split_unit": "case",
        "held_out_case_ids": input_data["design"]["held_out_case_ids"],
        "matched_case_coverage_required": True,
    }
    if held_out_content != expected_held_out:
        raise AnalysisError("reviewer reconstruction: held-out manifest does not match the declared cases")
    held_out = set(input_data["design"]["held_out_case_ids"])
    rows = input_data["observations"]
    unique_ids(rows, "judgment_id", "reviewer reconstruction")
    expected_assignments = {
        row["judgment_id"]: {
            "judgment_id": row["judgment_id"],
            "reviewer_id": row["reviewer_id"],
            "case_id": row["case_id"],
            "condition": row["condition"],
        }
        for row in rows
    }
    if scheduled_by_judgment != expected_assignments:
        raise AnalysisError(
            "reviewer reconstruction: assignment manifest doesn't exactly match judgment allocation"
        )
    case_families: dict[str, str] = {}
    case_references: dict[str, str] = {}
    banned = set(specification["integrity_rules"]["banned_view_key_tokens"])
    vectors: list[dict[str, Any]] = []
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["case_id"] not in held_out:
            raise AnalysisError(f"{row['judgment_id']}: case is not in the frozen held-out set")
        prior_family = case_families.setdefault(row["case_id"], row["family"])
        if prior_family != row["family"]:
            raise AnalysisError(f"{row['judgment_id']}: one held-out case is assigned to multiple families")
        prior_reference = case_references.setdefault(row["case_id"], row["reference_label"])
        if prior_reference != row["reference_label"]:
            raise AnalysisError(
                f"{row['judgment_id']}: the hidden reference changes across record conditions"
            )
        if row["oracle_visible_to_reviewer"]:
            raise AnalysisError(f"{row['judgment_id']}: oracle visibility violates masking")
        leaked = banned_key_paths(row["reviewer_view"], banned)
        if leaked:
            raise AnalysisError(f"{row['judgment_id']}: reviewer view leaks oracle/reference fields {leaked}")
        if iso(row["reference_joined_at"], row["judgment_id"]) <= iso(
            row["review_locked_at"], row["judgment_id"]
        ):
            raise AnalysisError(f"{row['judgment_id']}: reference was not joined after review lock")
        concordant = int(row["reviewer_verdict"] == row["reference_label"])
        false_certainty = int(not concordant and not row["justified_uncertainty"])
        values = {
            "reviewer_id": row["reviewer_id"],
            "case_id": row["case_id"],
            "condition": row["condition"],
            "reviewer_verdict": row["reviewer_verdict"],
            "reference_label": row["reference_label"],
            "node_concordance": concordant,
            "justified_uncertainty": row["justified_uncertainty"],
            "false_certainty": false_certainty,
            "technical_locus_correct": row["technical_locus_correct"],
        }
        vector = {"observation_id": row["judgment_id"], "family": row["family"], "values": values}
        vectors.append(vector)
        by_family[row["family"]].append(vector)
    output["observation_vectors"] = vectors
    thresholds = specification["thresholds"]
    critical = specification["uncertainty"]["critical_value"]
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        reported_thresholds = {
            "minimum_observations_per_arm": thresholds["minimum_observations_per_arm_per_family"],
            "minimum_cases": thresholds["minimum_cases_per_family"],
            "minimum_reviewers_per_arm": thresholds["minimum_reviewers_per_arm_per_family"],
            "minimum_typed_minus_degraded_concordance": thresholds["minimum_typed_minus_degraded_concordance"],
            "concordance_difference_lcb_strictly_above": thresholds["concordance_difference_lcb_strictly_above"],
            "maximum_typed_false_certainty": thresholds["maximum_typed_false_certainty"],
        }
        if not family_rows:
            output["family_results"].append(missing_family_result(family, reported_thresholds))
            continue
        typed = [row for row in family_rows if row["values"]["condition"] == "typed"]
        degraded = [row for row in family_rows if row["values"]["condition"] == "degraded"]
        typed_cases = {row["values"]["case_id"] for row in typed}
        degraded_cases = {row["values"]["case_id"] for row in degraded}
        if typed_cases != degraded_cases:
            raise AnalysisError(f"{family}: typed and degraded arms do not cover the same held-out cases")
        if not typed or not degraded:
            raise AnalysisError(f"{family}: both randomized record conditions are required")
        typed_mean = mean(row["values"]["node_concordance"] for row in typed)
        degraded_mean = mean(row["values"]["node_concordance"] for row in degraded)
        difference = typed_mean - degraded_mean
        case_se = cluster_standard_error(family_rows, "node_concordance", "case_id")
        reviewer_se = cluster_standard_error(family_rows, "node_concordance", "reviewer_id")
        conservative_se = (
            max(case_se, reviewer_se)
            if case_se is not None and reviewer_se is not None
            else None
        )
        lcb = difference - critical * conservative_se if conservative_se is not None else None
        typed_false_certainty = mean(row["values"]["false_certainty"] for row in typed)
        metrics = {
            "typed_node_concordance": typed_mean,
            "degraded_node_concordance": degraded_mean,
            "typed_minus_degraded_concordance": difference,
            "case_cluster_standard_error": case_se,
            "reviewer_cluster_standard_error": reviewer_se,
            "conservative_cluster_lcb_95": lcb,
            "typed_false_certainty": typed_false_certainty,
            "degraded_false_certainty": mean(row["values"]["false_certainty"] for row in degraded),
            "typed_technical_locus_accuracy": mean(float(row["values"]["technical_locus_correct"]) for row in typed),
            "degraded_technical_locus_accuracy": mean(float(row["values"]["technical_locus_correct"]) for row in degraded),
        }
        typed_reviewers = {row["values"]["reviewer_id"] for row in typed}
        degraded_reviewers = {row["values"]["reviewer_id"] for row in degraded}
        reasons: list[str] = []
        if min(len(typed), len(degraded)) < thresholds["minimum_observations_per_arm_per_family"]:
            reasons.append("An arm has fewer than the frozen minimum judgments.")
        if len(typed_cases) < thresholds["minimum_cases_per_family"]:
            reasons.append("Family has fewer than the frozen minimum held-out cases.")
        if min(len(typed_reviewers), len(degraded_reviewers)) < thresholds["minimum_reviewers_per_arm_per_family"]:
            reasons.append("An arm has fewer than the frozen minimum reviewers.")
        if difference < thresholds["minimum_typed_minus_degraded_concordance"]:
            reasons.append("Typed-minus-degraded concordance is below the practical threshold.")
        if lcb is None or lcb <= thresholds["concordance_difference_lcb_strictly_above"]:
            reasons.append("The conservative 95% lower confidence bound does not exclude no improvement.")
        if typed_false_certainty > thresholds["maximum_typed_false_certainty"]:
            reasons.append("Typed-condition false certainty exceeds the frozen maximum.")
        output["family_results"].append(
            {
                "family": family,
                "decision": "FAIL" if reasons else "PASS",
                "counts": {
                    "typed_observations": len(typed),
                    "degraded_observations": len(degraded),
                    "cases": len(typed_cases),
                    "typed_reviewers": len(typed_reviewers),
                    "degraded_reviewers": len(degraded_reviewers),
                },
                "metrics": metrics,
                "thresholds": reported_thresholds,
                "reasons": reasons,
            }
        )
    finish_decision(output)
    return output


ANALYZERS = {
    "local_discrimination": analyze_local,
    "predictive_typed_ablation": analyze_predictive,
    "reviewer_reconstruction": analyze_reviewer,
}


def analyze_input(input_data: dict[str, Any], artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    _, by_program = validate_specifications(artifact_dir)
    program_id = input_data.get("program_id")
    if program_id not in by_program:
        raise AnalysisError(f"unknown program_id {program_id!r}")
    specification = by_program[program_id]
    input_schema = load_json(artifact_dir / specification["input_schema"])
    require_schema(input_data, input_schema, f"{program_id} input")
    if (
        input_data["specification_id"] != specification["specification_id"]
        or input_data["specification_version"] != specification["specification_version"]
    ):
        raise AnalysisError(f"{program_id}: input does not bind to the frozen specification")
    output = ANALYZERS[program_id](input_data, specification)
    output_schema = load_json(artifact_dir / OUTPUT_SCHEMA_NAME)
    require_schema(output, output_schema, f"{program_id} output")
    return output


def main() -> int:
    args = parse_args()
    artifact_dir = args.artifact_dir.resolve()
    try:
        validate_specifications(artifact_dir)
        if args.validate_specs and args.input is None:
            print("Delegation empirical specifications valid: 3 frozen programmes and 4 schemas.")
            return 0
        if args.input is None:
            raise AnalysisError("--input is required unless --validate-specs is used alone")
        input_data = load_json(args.input)
        output = analyze_input(input_data, artifact_dir)
        rendered = json.dumps(output, indent=2, sort_keys=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
