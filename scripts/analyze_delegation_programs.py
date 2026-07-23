#!/usr/bin/env python3
"""Validate and estimate the three Delegation Assurance programmes.

The analyzer preserves observation-level vectors and reports family estimates
with intervals.  It never replaces the noncompensatory family vector with a
single decision score, and it holds no loss function from which to make a
go/no-go decision.  A valid input with no observations, or without every
required family, returns NOT_ESTIMATED.  Integrity failures (split overlap,
failed reset, reference leakage, or a pre-lock oracle join) are invalid
analysis inputs rather than empirical results.
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
import numpy as np
from scipy import optimize, stats


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


def interval_critical_value(level: float, distribution: str, df: int | None = None) -> float:
    tail = 0.5 + level / 2.0
    if distribution == "normal":
        return float(stats.norm.ppf(tail))
    if distribution == "t" and df is not None and df > 0:
        return float(stats.t.ppf(tail, df=df))
    raise AnalysisError(f"cannot compute {distribution} interval at level {level} with df={df}")


def interval_bounds(estimate: float, standard_error: float, critical: float) -> tuple[float, float]:
    half_width = critical * standard_error
    return estimate - half_width, estimate + half_width


def sample_standard_error(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return statistics.stdev(values) / math.sqrt(len(values))


def t_interval(values: list[float], level: float) -> tuple[float, float, float, int] | None:
    standard_error = sample_standard_error(values)
    if standard_error is None:
        return None
    df = len(values) - 1
    critical = interval_critical_value(level, "t", df)
    estimate = mean(values)
    lower, upper = interval_bounds(estimate, standard_error, critical)
    return standard_error, lower, upper, df


def common_nuisance_adjustment(
    signed_effects: list[float], nuisance_covariates: list[tuple[float, float, float]]
) -> tuple[list[float], float]:
    """Fit the matched design's equal-weight common-nuisance component.

    The three sensitivity measures are parallel matched covariates.  Their
    row-wise mean is the prespecified equal-weight nuisance component; its
    fitted family mean replaces the upward-biased maximum used in version 1.
    Pair-level residualization retains the nuisance-estimation variation in the
    family standard error.
    """

    common_by_pair = [mean(values) for values in nuisance_covariates]
    adjusted = [effect - nuisance for effect, nuisance in zip(signed_effects, common_by_pair)]
    return adjusted, mean(common_by_pair)


def partial_pool_family_effects(
    family_estimates: dict[str, float],
    family_standard_errors: dict[str, float],
    level: float,
) -> tuple[dict[str, dict[str, float]], dict[str, float]]:
    """Normal-normal empirical-Bayes pooling with moment-estimated tau squared."""

    families = list(family_estimates)
    estimates = np.asarray([family_estimates[family] for family in families], dtype=float)
    variances = np.asarray(
        [family_standard_errors[family] ** 2 for family in families], dtype=float
    )
    between_family_variance = max(
        float(np.var(estimates, ddof=1) - np.mean(variances)), 0.0
    )
    total_variances = between_family_variance + variances
    if np.all(total_variances == 0.0):
        weights = np.ones(len(families), dtype=float)
        grand_variance = 0.0
    else:
        positive = total_variances[total_variances > 0.0]
        fallback = float(np.min(positive)) * 1e-12
        weights = 1.0 / np.where(total_variances > 0.0, total_variances, fallback)
        grand_variance = float(1.0 / np.sum(weights))
    grand_estimate = float(np.average(estimates, weights=weights))
    grand_standard_error = math.sqrt(grand_variance)
    critical = interval_critical_value(level, "normal")
    grand_lower, grand_upper = interval_bounds(
        grand_estimate, grand_standard_error, critical
    )

    pooled: dict[str, dict[str, float]] = {}
    for index, family in enumerate(families):
        denominator = between_family_variance + variances[index]
        shrinkage_weight = (
            between_family_variance / denominator if denominator > 0.0 else 0.0
        )
        pooled_estimate = grand_estimate + shrinkage_weight * (
            estimates[index] - grand_estimate
        )
        conditional_variance = shrinkage_weight * variances[index]
        pooled_variance = conditional_variance + (
            (1.0 - shrinkage_weight) ** 2 * grand_variance
        )
        pooled_standard_error = math.sqrt(max(float(pooled_variance), 0.0))
        lower, upper = interval_bounds(
            float(pooled_estimate), pooled_standard_error, critical
        )
        pooled[family] = {
            "pooling_weight": float(shrinkage_weight),
            "pooled_estimate": float(pooled_estimate),
            "pooled_standard_error": pooled_standard_error,
            "interval_lower": lower,
            "interval_upper": upper,
        }
    grand = {
        "estimate": grand_estimate,
        "standard_error": grand_standard_error,
        "interval_lower": grand_lower,
        "interval_upper": grand_upper,
        "between_family_variance": between_family_variance,
    }
    return pooled, grand


def logistic_calibration(rows: list[dict[str, Any]]) -> tuple[float | None, float | None]:
    """Fit outcome ~ intercept + slope * predicted log-odds by maximum likelihood."""

    probabilities = np.asarray(
        [row["values"]["typed_probability"] for row in rows], dtype=float
    )
    outcomes = np.asarray([row["values"]["target"] for row in rows], dtype=float)
    probabilities = np.clip(probabilities, 1e-8, 1.0 - 1e-8)
    log_odds = np.log(probabilities / (1.0 - probabilities))
    if len(np.unique(outcomes)) < 2 or np.ptp(log_odds) == 0.0:
        return None, None
    design = np.column_stack((np.ones(len(rows)), log_odds))

    def objective(coefficients: np.ndarray) -> tuple[float, np.ndarray]:
        linear = design @ coefficients
        value = float(np.sum(np.logaddexp(0.0, linear) - outcomes * linear))
        fitted = 1.0 / (1.0 + np.exp(-np.clip(linear, -700.0, 700.0)))
        gradient = design.T @ (fitted - outcomes)
        return value, gradient

    fit = optimize.minimize(
        lambda coefficients: objective(coefficients)[0],
        np.asarray([0.0, 1.0]),
        jac=lambda coefficients: objective(coefficients)[1],
        method="BFGS",
    )
    if not fit.success or not np.all(np.isfinite(fit.x)):
        return None, None
    return float(fit.x[0]), float(fit.x[1])


def crossed_variance_components(
    matrix: np.ndarray,
) -> tuple[float, float, float, float, float]:
    """Two-way random-effects method-of-moments components for a balanced matrix."""

    n_reviewers, n_cases = matrix.shape
    if n_reviewers < 2 or n_cases < 2:
        raise AnalysisError("crossed variance needs at least two reviewers and two cases")
    grand = float(np.mean(matrix))
    reviewer_means = np.mean(matrix, axis=1)
    case_means = np.mean(matrix, axis=0)
    residuals = matrix - reviewer_means[:, None] - case_means[None, :] + grand
    reviewer_ms = float(n_cases * np.sum((reviewer_means - grand) ** 2) / (n_reviewers - 1))
    case_ms = float(n_reviewers * np.sum((case_means - grand) ** 2) / (n_cases - 1))
    residual_ms = float(
        np.sum(residuals**2) / ((n_reviewers - 1) * (n_cases - 1))
    )
    reviewer_variance = max((reviewer_ms - residual_ms) / n_cases, 0.0)
    case_variance = max((case_ms - residual_ms) / n_reviewers, 0.0)
    residual_variance = max(residual_ms, 0.0)
    grand_variance = (
        reviewer_variance / n_reviewers
        + case_variance / n_cases
        + residual_variance / (n_reviewers * n_cases)
    )
    return (
        grand,
        reviewer_variance,
        case_variance,
        residual_variance,
        math.sqrt(grand_variance),
    )


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
        design_floors = specification["design_floors"]
        required_design_floors = {
            "local_discrimination": {
                "advisory",
                "minimum_observations_per_family",
                "minimum_control_accuracy",
            },
            "predictive_typed_ablation": {
                "advisory",
                "minimum_trace_families_per_family",
            },
            "reviewer_reconstruction": {
                "advisory",
                "minimum_cases_per_family",
                "minimum_reviewers_per_family",
            },
        }[program_id]
        if set(design_floors) != required_design_floors or design_floors["advisory"] is not True:
            raise AnalysisError(
                f"{program_id}: advisory design-floor vector is incomplete or contains undeclared fields"
            )
        expected_uncertainty_method = {
            "local_discrimination": "partial_pooling_family_effect_interval",
            "predictive_typed_ablation": "trace_family_cluster_interval_t_or_multilevel",
            "reviewer_reconstruction": "crossed_reviewer_case_variance",
        }[program_id]
        if (
            specification["uncertainty"]["method"] != expected_uncertainty_method
            or specification["uncertainty"]["report"] != "estimate_and_interval"
        ):
            raise AnalysisError(f"{program_id}: uncertainty method does not match the revised estimator")
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


def finish_estimation(output: dict[str, Any]) -> None:
    statuses = [item["decision"] for item in output["family_results"]]
    if "NOT_ESTIMATED" in statuses:
        output["decision"] = "NOT_ESTIMATED"
        output["not_estimated_reason"] = (
            "NO_OBSERVATIONS" if not output["observation_vectors"] else "REQUIRED_FAMILY_NOT_ESTIMATED"
        )
    else:
        output["decision"] = "ESTIMATED"
        output["not_estimated_reason"] = None


def reported_design_floors(specification: dict[str, Any]) -> dict[str, float]:
    return {
        key: value
        for key, value in specification["design_floors"].items()
        if key != "advisory"
    }


def missing_family_result(
    family: str,
    design_floors: dict[str, float],
    reason: str = "No observations were supplied for this required family.",
) -> dict[str, Any]:
    return {
        "family": family,
        "decision": "NOT_ESTIMATED",
        "counts": {"observations": 0},
        "metrics": {},
        "thresholds": design_floors,
        "reasons": [reason],
    }


def revised_output_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Return the output-envelope schema unchanged.

    The statistical status enums (``ESTIMATED``/``NOT_ESTIMATED``) now live on
    disk in ``analysis-output.schema.json``, so no in-memory reconciliation is
    needed. This pass-through is kept so the call site stays stable.
    """

    return schema


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
        common_nuisance_covariate = mean(
            (placebo_instability, order_instability, shortcut_instability)
        )
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
            "common_nuisance_covariate": common_nuisance_covariate,
            "nuisance_adjusted_authority_effect": signed_effect
            - common_nuisance_covariate,
            "control_correct": row["control_correct"],
        }
        vector = {"observation_id": row["observation_id"], "family": row["family"], "values": values}
        vectors.append(vector)
        by_family[row["family"]].append(vector)
    output["observation_vectors"] = vectors
    design_floors = reported_design_floors(specification)
    level = specification["uncertainty"].get("confidence_level", 0.95)
    family_summaries: dict[str, dict[str, Any]] = {}
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        if not family_rows:
            family_summaries[family] = {"rows": family_rows, "estimable": False}
            continue
        signed_effects = [
            row["values"]["reference_concordant_effect"] for row in family_rows
        ]
        nuisance_covariates = [
            (
                row["values"]["placebo_instability"],
                row["values"]["order_instability"],
                row["values"]["shortcut_instability"],
            )
            for row in family_rows
        ]
        adjusted, modelled_common_nuisance_mean = common_nuisance_adjustment(
            signed_effects, nuisance_covariates
        )
        standard_error = sample_standard_error(adjusted)
        control_accuracy = mean(float(row["values"]["control_correct"]) for row in family_rows)
        family_summaries[family] = {
            "rows": family_rows,
            "estimable": standard_error is not None,
            "estimate": mean(adjusted),
            "standard_error": standard_error,
            "modelled_common_nuisance_mean": modelled_common_nuisance_mean,
            "control_accuracy": control_accuracy,
        }

    all_estimable = all(
        family_summaries.get(family, {}).get("estimable", False)
        for family in specification["required_families"]
    )
    pooled: dict[str, dict[str, float]] = {}
    grand: dict[str, float] = {}
    if all_estimable:
        pooled, grand = partial_pool_family_effects(
            {
                family: family_summaries[family]["estimate"]
                for family in specification["required_families"]
            },
            {
                family: family_summaries[family]["standard_error"]
                for family in specification["required_families"]
            },
            level,
        )

    for family in specification["required_families"]:
        summary = family_summaries.get(family)
        if not summary or not summary["rows"]:
            output["family_results"].append(
                missing_family_result(family, design_floors)
            )
            continue
        if not all_estimable:
            reason = (
                "At least two observations per family and all four required families "
                "are needed for the partial-pooling interval."
            )
            output["family_results"].append(
                {
                    "family": family,
                    "decision": "NOT_ESTIMATED",
                    "counts": {"observations": len(summary["rows"])},
                    "metrics": {
                        "unpooled_family_estimate": summary["estimate"],
                        "unpooled_standard_error": summary["standard_error"],
                    },
                    "thresholds": design_floors,
                    "reasons": [reason],
                }
            )
            continue
        family_rows = summary["rows"]
        metrics = {
            "mean_raw_package_effect": mean(
                row["values"]["raw_package_effect"] for row in family_rows
            ),
            "mean_reference_concordant_effect": mean(
                row["values"]["reference_concordant_effect"] for row in family_rows
            ),
            "mean_placebo_instability": mean(
                row["values"]["placebo_instability"] for row in family_rows
            ),
            "mean_order_instability": mean(
                row["values"]["order_instability"] for row in family_rows
            ),
            "mean_shortcut_instability": mean(
                row["values"]["shortcut_instability"] for row in family_rows
            ),
            "modelled_common_nuisance_mean": summary[
                "modelled_common_nuisance_mean"
            ],
            "unpooled_family_estimate": summary["estimate"],
            "unpooled_standard_error": summary["standard_error"],
            "between_family_variance": grand["between_family_variance"],
            "pooling_weight": pooled[family]["pooling_weight"],
            "pooled_family_estimate": pooled[family]["pooled_estimate"],
            "pooled_family_standard_error": pooled[family]["pooled_standard_error"],
            "pooled_family_interval_lower_95": pooled[family]["interval_lower"],
            "pooled_family_interval_upper_95": pooled[family]["interval_upper"],
            "pooled_grand_estimate": grand["estimate"],
            "pooled_grand_standard_error": grand["standard_error"],
            "pooled_grand_interval_lower_95": grand["interval_lower"],
            "pooled_grand_interval_upper_95": grand["interval_upper"],
            "control_accuracy": summary["control_accuracy"],
        }
        reasons: list[str] = []
        if len(family_rows) < design_floors["minimum_observations_per_family"]:
            reasons.append(
                "Advisory reporting floor not met: fewer than the declared independent base pairs."
            )
        if summary["control_accuracy"] < design_floors["minimum_control_accuracy"]:
            reasons.append(
                "Advisory control-accuracy floor not met; the estimate is still reported."
            )
        output["family_results"].append(
            {
                "family": family,
                "decision": "ESTIMATED",
                "counts": {"observations": len(family_rows)},
                "metrics": metrics,
                "thresholds": design_floors,
                "reasons": reasons,
            }
        )
    finish_estimation(output)
    return output


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
        "calibration_diagnostic": "logistic_intercept_slope",
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
        }
        vector = {"observation_id": row["observation_id"], "family": row["family"], "values": values}
        vectors.append(vector)
        by_family[row["family"]].append(vector)
    output["observation_vectors"] = vectors
    design_floors = reported_design_floors(specification)
    level = specification["uncertainty"].get("confidence_level", 0.95)
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        if not family_rows:
            output["family_results"].append(
                missing_family_result(family, design_floors)
            )
            continue
        improvements = [row["values"]["paired_brier_improvement"] for row in family_rows]
        improvements_by_trace_family: dict[str, list[float]] = defaultdict(list)
        for row in family_rows:
            improvements_by_trace_family[row["values"]["trace_family_id"]].append(
                row["values"]["paired_brier_improvement"]
            )
        cluster_means = [mean(values) for values in improvements_by_trace_family.values()]
        interval = t_interval(cluster_means, level)
        if interval is None:
            output["family_results"].append(
                {
                    "family": family,
                    "decision": "NOT_ESTIMATED",
                    "counts": {
                        "observations": len(family_rows),
                        "trace_families": len(cluster_means),
                    },
                    "metrics": {
                        "row_weighted_mean_paired_brier_improvement": mean(
                            improvements
                        ),
                        "mean_trace_family_paired_brier_improvement": mean(
                            cluster_means
                        ),
                    },
                    "thresholds": design_floors,
                    "reasons": [
                        "At least two held-out trace families are needed for a t-interval."
                    ],
                }
            )
            continue
        standard_error, lower, upper, df = interval
        calibration_intercept, calibration_slope = logistic_calibration(family_rows)
        metrics = {
            "mean_typed_brier_loss": mean(row["values"]["typed_brier_loss"] for row in family_rows),
            "mean_baseline_brier_loss": mean(row["values"]["baseline_brier_loss"] for row in family_rows),
            "row_weighted_mean_paired_brier_improvement": mean(improvements),
            "mean_trace_family_paired_brier_improvement": mean(cluster_means),
            "trace_family_standard_error": standard_error,
            "trace_family_interval_degrees_of_freedom": df,
            "trace_family_interval_lower_95": lower,
            "trace_family_interval_upper_95": upper,
            "calibration_intercept": calibration_intercept,
            "calibration_slope": calibration_slope,
        }
        reasons: list[str] = []
        if len(cluster_means) < design_floors["minimum_trace_families_per_family"]:
            reasons.append(
                "Advisory reporting floor not met: fewer than the declared held-out trace families."
            )
        if calibration_intercept is None or calibration_slope is None:
            reasons.append(
                "Logistic calibration intercept and slope were not finite (for example, under separation)."
            )
        output["family_results"].append(
            {
                "family": family,
                "decision": "ESTIMATED",
                "counts": {
                    "observations": len(family_rows),
                    "trace_families": len(cluster_means),
                },
                "metrics": metrics,
                "thresholds": design_floors,
                "reasons": reasons,
            }
        )
    finish_estimation(output)
    return output


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
    design_floors = reported_design_floors(specification)
    level = specification["uncertainty"].get("confidence_level", 0.95)
    critical = interval_critical_value(level, "normal")
    for family in specification["required_families"]:
        family_rows = by_family.get(family, [])
        if not family_rows:
            output["family_results"].append(
                missing_family_result(family, design_floors)
            )
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
        reviewers = sorted({row["values"]["reviewer_id"] for row in family_rows})
        cases = sorted(typed_cases)
        cell_values: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for row in family_rows:
            cell_values[
                (row["values"]["reviewer_id"], row["values"]["case_id"])
            ][row["values"]["condition"]].append(row["values"]["node_concordance"])
        expected_cells = {(reviewer, case) for reviewer in reviewers for case in cases}
        if set(cell_values) != expected_cells or any(
            set(cell_values[cell]) != {"typed", "degraded"} for cell in expected_cells
        ):
            raise AnalysisError(
                f"{family}: crossed variance requires every reviewer-by-case cell in both conditions"
            )
        difference_matrix = np.asarray(
            [
                [
                    mean(cell_values[(reviewer, case)]["typed"])
                    - mean(cell_values[(reviewer, case)]["degraded"])
                    for case in cases
                ]
                for reviewer in reviewers
            ],
            dtype=float,
        )
        if len(reviewers) < 2 or len(cases) < 2:
            output["family_results"].append(
                {
                    "family": family,
                    "decision": "NOT_ESTIMATED",
                    "counts": {
                        "typed_observations": len(typed),
                        "degraded_observations": len(degraded),
                        "cases": len(cases),
                        "reviewers": len(reviewers),
                    },
                    "metrics": {
                        "typed_node_concordance": typed_mean,
                        "degraded_node_concordance": degraded_mean,
                    },
                    "thresholds": design_floors,
                    "reasons": [
                        "At least two reviewers and two cases are needed for crossed variance components."
                    ],
                }
            )
            continue
        (
            difference,
            reviewer_variance,
            case_variance,
            residual_variance,
            crossed_standard_error,
        ) = crossed_variance_components(difference_matrix)
        lower, upper = interval_bounds(difference, crossed_standard_error, critical)
        typed_false_certainty = mean(row["values"]["false_certainty"] for row in typed)
        metrics = {
            "typed_node_concordance": typed_mean,
            "degraded_node_concordance": degraded_mean,
            "typed_minus_degraded_concordance": difference,
            "reviewer_variance_component": reviewer_variance,
            "case_variance_component": case_variance,
            "residual_variance_component": residual_variance,
            "crossed_grand_mean_standard_error": crossed_standard_error,
            "crossed_interval_lower_95": lower,
            "crossed_interval_upper_95": upper,
            "typed_false_certainty": typed_false_certainty,
            "degraded_false_certainty": mean(row["values"]["false_certainty"] for row in degraded),
            "typed_technical_locus_accuracy": mean(float(row["values"]["technical_locus_correct"]) for row in typed),
            "degraded_technical_locus_accuracy": mean(float(row["values"]["technical_locus_correct"]) for row in degraded),
        }
        reasons: list[str] = []
        if len(cases) < design_floors["minimum_cases_per_family"]:
            reasons.append(
                "Advisory reporting floor not met: fewer than the declared held-out cases."
            )
        if len(reviewers) < design_floors["minimum_reviewers_per_family"]:
            reasons.append(
                "Advisory reporting floor not met: fewer than the declared reviewers."
            )
        output["family_results"].append(
            {
                "family": family,
                "decision": "ESTIMATED",
                "counts": {
                    "typed_observations": len(typed),
                    "degraded_observations": len(degraded),
                    "cases": len(typed_cases),
                    "reviewers": len(reviewers),
                },
                "metrics": metrics,
                "thresholds": design_floors,
                "reasons": reasons,
            }
        )
    finish_estimation(output)
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
    output_schema = revised_output_schema(load_json(artifact_dir / OUTPUT_SCHEMA_NAME))
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
