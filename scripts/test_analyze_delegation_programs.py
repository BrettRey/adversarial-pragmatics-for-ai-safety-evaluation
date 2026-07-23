"""Estimator and integrity tests for the Delegation Assurance programmes."""

from __future__ import annotations

import unittest

from scipy import stats

from scripts.analyze_delegation_programs import (
    AnalysisError,
    analyze_input,
    canonical_sha256,
)


FEATURE_ALLOWLIST = [
    "case_id",
    "trace_schema_version",
    "regime_id",
    "regime_version",
    "action_class",
    "trace_length",
    "capability",
    "permissions",
    "causal_attribution",
    "context_controls",
    "typed_representation",
]


def manifest(manifest_id: str, content: dict) -> dict:
    value = {
        "manifest_id": manifest_id,
        "manifest_version": "1.0.0",
        "frozen_at": "2026-07-21T09:00:00Z",
        "content": content,
    }
    value["sha256"] = canonical_sha256(value)
    return value


def rehash(binding: dict) -> None:
    unsigned = {key: value for key, value in binding.items() if key != "sha256"}
    binding["sha256"] = canonical_sha256(unsigned)


def local_input(with_observations: bool = True) -> dict:
    families = [
        "indirect_injection",
        "confused_deputy",
        "persistence",
        "temporal_authority",
    ]
    family_effects = dict(zip(families, (0.10, 0.15, 0.20, 0.40)))
    observations = []
    held_out = []
    if with_observations:
        for family in families:
            for index in range(30):
                base_id = f"{family}_base_{index}"
                held_out.append(base_id)
                baseline = 0.10
                nuisance = (
                    0.02 + 0.005 * (index % 3),
                    0.05 + 0.005 * (index % 4),
                    0.08 + 0.005 * (index % 5),
                )
                common_nuisance = sum(nuisance) / 3.0
                pair_noise = 0.04 * ((index % 5) - 2)
                authority = baseline + family_effects[family] + common_nuisance + pair_noise
                observations.append(
                    {
                        "observation_id": f"{family}_observation_{index}",
                        "family": family,
                        "base_item_id": base_id,
                        "reference_direction": 1,
                        "baseline_endpoint": baseline,
                        "authority_endpoint": authority,
                        "placebo_endpoint": baseline + nuisance[0],
                        "order_reversal_endpoint": authority - nuisance[1],
                        "shortcut_endpoint": baseline + nuisance[2],
                        "control_correct": True,
                        "reset_confirmed": True,
                        "evaluator_view": {
                            "case_id": base_id,
                            "standing_representation": "assigned",
                        },
                        "response_locked_at": "2026-07-21T10:00:00Z",
                        "reference_joined_at": "2026-07-21T10:01:00Z",
                    }
                )
    arms = ["baseline", "authority", "placebo", "order_reversal", "shortcut"]
    assignments = []
    for index, observation in enumerate(observations):
        offset = index % len(arms)
        order = arms[offset:] + arms[:offset]
        assignments.append(
            {
                "observation_id": observation["observation_id"],
                "presentation_order": order,
                "presentation_ids": {
                    arm: f"{observation['observation_id']}_{arm}_presentation"
                    for arm in arms
                },
            }
        )
    design = {
        "frozen_before_responses": True,
        "assignment_randomized": True,
        "reset_policy": "reset_before_each_presentation",
        "carryover_detected": False,
        "development_base_item_ids": ["development_base"],
        "held_out_base_item_ids": held_out,
    }
    return {
        "schema_version": "1.0.0",
        "input_id": "synthetic_local",
        "program_id": "local_discrimination",
        "specification_id": "DA_LOCAL_001_SPEC",
        "specification_version": "1.0.0",
        "created_at": "2026-07-21T11:00:00Z",
        "design": design,
        "design_object_bindings": {
            "assignment_manifest": manifest(
                "local_assignment_manifest",
                {
                    "randomization_unit": "package_presentation",
                    "randomization_method": "frozen_external_randomization",
                    "reset_policy": "reset_before_each_presentation",
                    "carryover_detected": False,
                    "assignments": assignments,
                },
            ),
            "split_manifest": manifest(
                "local_split_manifest",
                {
                    "split_unit": "base_item",
                    "development_base_item_ids": design[
                        "development_base_item_ids"
                    ],
                    "held_out_base_item_ids": design["held_out_base_item_ids"],
                },
            ),
        },
        "observations": observations,
    }


def predictive_input(with_observations: bool = True) -> dict:
    families = [
        "proposal_authorization",
        "gate_fidelity",
        "execution_authorization",
        "trajectory_authorization",
    ]
    observations = []
    if with_observations:
        for family in families:
            for index in range(30):
                target = index % 2
                predicted_positive = bool(target)
                if index % 5 == 0:
                    predicted_positive = not predicted_positive
                observations.append(
                    {
                        "observation_id": f"{family}_prediction_{index}",
                        "family": family,
                        "trace_family_id": f"heldout_trace_family_{index % 10}",
                        "target": target,
                        "typed_probability": 0.75 if predicted_positive else 0.25,
                        "baseline_probability": 0.50,
                        "predictor_view": {
                            "case_id": f"case_{family}_{index}",
                            "trace_length": 3,
                        },
                        "prediction_locked_at": "2026-07-21T10:00:00Z",
                        "reference_joined_at": "2026-07-21T10:01:00Z",
                    }
                )
    held_out_trace_families = [f"heldout_trace_family_{index}" for index in range(10)]
    design = {
        "split_frozen_before_outcomes": True,
        "training_trace_family_ids": ["development_trace_family"],
        "held_out_trace_family_ids": held_out_trace_families,
        "feature_allowlist": FEATURE_ALLOWLIST,
        "prediction_procedure_id": "synthetic_brier_predictors",
        "software_version": "1.0.0",
        "prediction_view_built_before_reference_join": True,
    }
    return {
        "schema_version": "1.0.0",
        "input_id": "synthetic_predictive",
        "program_id": "predictive_typed_ablation",
        "specification_id": "DA_PRED_001_SPEC",
        "specification_version": "1.0.0",
        "created_at": "2026-07-21T11:00:00Z",
        "design": design,
        "design_object_bindings": {
            "feature_manifest": manifest(
                "predictive_feature_manifest",
                {
                    "feature_allowlist": FEATURE_ALLOWLIST,
                    "typed_feature_keys": FEATURE_ALLOWLIST,
                    "baseline_feature_keys": [
                        key for key in FEATURE_ALLOWLIST if key != "typed_representation"
                    ],
                    "prediction_procedure_id": "synthetic_brier_predictors",
                    "software_version": "1.0.0",
                    "loss": "brier",
                    "calibration_diagnostic": "logistic_intercept_slope",
                },
            ),
            "held_out_manifest": manifest(
                "predictive_heldout_manifest",
                {
                    "split_unit": "trace_family",
                    "training_trace_family_ids": design["training_trace_family_ids"],
                    "held_out_trace_family_ids": design[
                        "held_out_trace_family_ids"
                    ],
                },
            ),
        },
        "observations": observations,
    }


def reviewer_input(with_observations: bool = True) -> dict:
    families = ["single_action", "gate_failure", "transition", "cumulative_trajectory"]
    observations = []
    held_out = []
    if with_observations:
        for family_index, family in enumerate(families):
            for case_index in range(10):
                case_id = f"{family}_case_{case_index}"
                held_out.append(case_id)
                for reviewer_index in range(6):
                    for condition in ("typed", "degraded"):
                        if condition == "typed":
                            concordant = (
                                reviewer_index + case_index + family_index
                            ) % 5 != 0
                        else:
                            concordant = (
                                2 * reviewer_index + case_index + family_index
                            ) % 3 == 0
                        observations.append(
                            {
                                "judgment_id": (
                                    f"{family}_{condition}_{case_index}_{reviewer_index}"
                                ),
                                "reviewer_id": f"reviewer_{reviewer_index}",
                                "case_id": case_id,
                                "family": family,
                                "condition": condition,
                                "reviewer_verdict": (
                                    "supported" if concordant else "defeated"
                                ),
                                "reference_label": "supported",
                                "justified_uncertainty": False,
                                "technical_locus_correct": condition == "typed",
                                "reviewer_view": {
                                    "case_id": case_id,
                                    "record_condition": condition,
                                },
                                "oracle_visible_to_reviewer": False,
                                "review_locked_at": "2026-07-21T10:00:00Z",
                                "reference_joined_at": "2026-07-21T10:01:00Z",
                            }
                        )
    assignments = [
        {
            "judgment_id": observation["judgment_id"],
            "reviewer_id": observation["reviewer_id"],
            "case_id": observation["case_id"],
            "condition": observation["condition"],
        }
        for observation in observations
    ]
    design = {
        "assignment_frozen_before_reviews": True,
        "condition_randomized": True,
        "reset_policy": "independent_randomized_presentation",
        "held_out_case_ids": held_out,
        "oracle_masking_confirmed": True,
    }
    return {
        "schema_version": "1.0.0",
        "input_id": "synthetic_reviewer",
        "program_id": "reviewer_reconstruction",
        "specification_id": "DA_RECON_001_SPEC",
        "specification_version": "1.0.0",
        "created_at": "2026-07-21T11:00:00Z",
        "design": design,
        "design_object_bindings": {
            "assignment_manifest": manifest(
                "reviewer_assignment_manifest",
                {
                    "assignment_unit": "reviewer_case_presentation",
                    "randomization_method": "frozen_external_randomization",
                    "reset_policy": "independent_randomized_presentation",
                    "assignments": assignments,
                },
            ),
            "held_out_manifest": manifest(
                "reviewer_heldout_manifest",
                {
                    "split_unit": "case",
                    "held_out_case_ids": held_out,
                    "matched_case_coverage_required": True,
                },
            ),
        },
        "observations": observations,
    }


class DelegationProgrammeTests(unittest.TestCase):
    def test_synthetic_estimates_preserve_vectors(self) -> None:
        for builder in (local_input, predictive_input, reviewer_input):
            input_data = builder()
            output = analyze_input(input_data)
            self.assertEqual(output["decision"], "ESTIMATED")
            self.assertFalse(output["scalar_aggregation_permitted"])
            self.assertEqual(
                len(output["observation_vectors"]), len(input_data["observations"])
            )
            self.assertTrue(
                all(
                    result["decision"] == "ESTIMATED"
                    for result in output["family_results"]
                )
            )

    def test_no_data_is_not_estimated(self) -> None:
        for builder in (local_input, predictive_input, reviewer_input):
            output = analyze_input(builder(False))
            self.assertEqual(output["decision"], "NOT_ESTIMATED")
            self.assertEqual(output["not_estimated_reason"], "NO_OBSERVATIONS")
            self.assertTrue(
                all(
                    result["decision"] == "NOT_ESTIMATED"
                    for result in output["family_results"]
                )
            )

    def test_missing_required_family_is_not_estimated(self) -> None:
        input_data = predictive_input()
        input_data["observations"] = [
            row
            for row in input_data["observations"]
            if row["family"] != "trajectory_authorization"
        ]
        output = analyze_input(input_data)
        self.assertEqual(output["decision"], "NOT_ESTIMATED")
        self.assertEqual(
            output["not_estimated_reason"], "REQUIRED_FAMILY_NOT_ESTIMATED"
        )
        observed = {row["family"]: row["decision"] for row in output["family_results"]}
        self.assertEqual(observed["trajectory_authorization"], "NOT_ESTIMATED")
        self.assertEqual(sum(value == "ESTIMATED" for value in observed.values()), 3)

    def test_local_uses_common_nuisance_mean_not_maximum(self) -> None:
        output = analyze_input(local_input())
        vector = output["observation_vectors"][0]["values"]
        expected_common = (
            vector["placebo_instability"]
            + vector["order_instability"]
            + vector["shortcut_instability"]
        ) / 3.0
        self.assertAlmostEqual(vector["common_nuisance_covariate"], expected_common)
        self.assertAlmostEqual(
            vector["nuisance_adjusted_authority_effect"],
            vector["reference_concordant_effect"] - expected_common,
        )
        self.assertNotIn("matched_nuisance_floor", vector)
        self.assertNotIn("selective_margin", vector)

    def test_local_partial_pooling_reports_family_and_grand_intervals(self) -> None:
        output = analyze_input(local_input())
        results = {row["family"]: row for row in output["family_results"]}
        high = results["temporal_authority"]["metrics"]
        self.assertLess(high["pooled_grand_estimate"], high["pooled_family_estimate"])
        self.assertLess(high["pooled_family_estimate"], high["unpooled_family_estimate"])
        self.assertGreaterEqual(high["pooling_weight"], 0.0)
        self.assertLessEqual(high["pooling_weight"], 1.0)
        self.assertLess(
            high["pooled_family_interval_lower_95"],
            high["pooled_family_interval_upper_95"],
        )
        grand_estimates = {
            row["metrics"]["pooled_grand_estimate"]
            for row in output["family_results"]
        }
        self.assertEqual(len(grand_estimates), 1)

    def test_predictive_t_interval_matches_trace_family_means(self) -> None:
        output = analyze_input(predictive_input())
        result = output["family_results"][0]
        metrics = result["metrics"]
        family = result["family"]
        by_trace: dict[str, list[float]] = {}
        for vector in output["observation_vectors"]:
            if vector["family"] != family:
                continue
            by_trace.setdefault(vector["values"]["trace_family_id"], []).append(
                vector["values"]["paired_brier_improvement"]
            )
        cluster_means = [sum(values) / len(values) for values in by_trace.values()]
        estimate = sum(cluster_means) / len(cluster_means)
        standard_error = stats.sem(cluster_means)
        half_width = stats.t.ppf(0.975, df=len(cluster_means) - 1) * standard_error
        self.assertAlmostEqual(
            metrics["mean_trace_family_paired_brier_improvement"], estimate
        )
        self.assertAlmostEqual(metrics["trace_family_standard_error"], standard_error)
        self.assertAlmostEqual(metrics["trace_family_interval_lower_95"], estimate - half_width)
        self.assertAlmostEqual(metrics["trace_family_interval_upper_95"], estimate + half_width)
        self.assertIn("calibration_intercept", metrics)
        self.assertIn("calibration_slope", metrics)
        self.assertFalse(any("ece" in key.lower() or "lcb" in key.lower() for key in metrics))

    def test_design_floor_is_advisory_not_an_effect_gate(self) -> None:
        input_data = predictive_input()
        input_data["observations"] = [
            row
            for row in input_data["observations"]
            if row["trace_family_id"]
            in {"heldout_trace_family_0", "heldout_trace_family_1"}
        ]
        output = analyze_input(input_data)
        self.assertEqual(output["decision"], "ESTIMATED")
        self.assertTrue(
            all(row["counts"]["trace_families"] == 2 for row in output["family_results"])
        )
        self.assertTrue(
            all(any("Advisory" in reason for reason in row["reasons"]) for row in output["family_results"])
        )

    def test_one_trace_family_cannot_supply_a_t_interval(self) -> None:
        input_data = predictive_input()
        for observation in input_data["observations"]:
            if observation["family"] == "trajectory_authorization":
                observation["trace_family_id"] = "heldout_trace_family_0"
        output = analyze_input(input_data)
        result = next(
            row
            for row in output["family_results"]
            if row["family"] == "trajectory_authorization"
        )
        self.assertEqual(result["counts"]["observations"], 30)
        self.assertEqual(result["counts"]["trace_families"], 1)
        self.assertEqual(result["decision"], "NOT_ESTIMATED")
        self.assertEqual(output["decision"], "NOT_ESTIMATED")

    def test_reviewer_uses_crossed_variance_components(self) -> None:
        output = analyze_input(reviewer_input())
        for result in output["family_results"]:
            metrics = result["metrics"]
            expected_variance = (
                metrics["reviewer_variance_component"] / result["counts"]["reviewers"]
                + metrics["case_variance_component"] / result["counts"]["cases"]
                + metrics["residual_variance_component"]
                / (result["counts"]["reviewers"] * result["counts"]["cases"])
            )
            self.assertAlmostEqual(
                metrics["crossed_grand_mean_standard_error"] ** 2,
                expected_variance,
            )
            self.assertGreaterEqual(metrics["reviewer_variance_component"], 0.0)
            self.assertGreaterEqual(metrics["case_variance_component"], 0.0)
            self.assertGreaterEqual(metrics["residual_variance_component"], 0.0)
            self.assertNotIn("case_cluster_standard_error", metrics)
            self.assertNotIn("reviewer_cluster_standard_error", metrics)
            self.assertNotIn("conservative_cluster_lcb_95", metrics)

    def test_incomplete_crossed_reviewer_case_design_is_rejected(self) -> None:
        input_data = reviewer_input()
        removed = input_data["observations"].pop()
        binding = input_data["design_object_bindings"]["assignment_manifest"]
        binding["content"]["assignments"] = [
            assignment
            for assignment in binding["content"]["assignments"]
            if assignment["judgment_id"] != removed["judgment_id"]
        ]
        rehash(binding)
        with self.assertRaisesRegex(AnalysisError, "every reviewer-by-case cell"):
            analyze_input(input_data)

    def test_predictive_leakage_is_rejected(self) -> None:
        input_data = predictive_input()
        input_data["observations"][0]["predictor_view"]["oracle_verdict"] = "supported"
        with self.assertRaisesRegex(AnalysisError, "non-allowlisted|leaks"):
            analyze_input(input_data)

    def test_manifest_hash_mismatch_is_rejected(self) -> None:
        input_data = local_input(False)
        input_data["design_object_bindings"]["assignment_manifest"]["content"][
            "reset_policy"
        ] = "not_the_frozen_policy"
        with self.assertRaisesRegex(AnalysisError, "SHA-256 does not match"):
            analyze_input(input_data)

    def test_hashed_assignment_must_allocate_every_presentation_arm(self) -> None:
        input_data = local_input()
        binding = input_data["design_object_bindings"]["assignment_manifest"]
        binding["content"]["assignments"][0]["presentation_order"].pop()
        rehash(binding)
        with self.assertRaisesRegex(AnalysisError, "allocate all five presentation arms"):
            analyze_input(input_data)

    def test_manifest_must_precede_first_locked_outcome(self) -> None:
        input_data = reviewer_input()
        binding = input_data["design_object_bindings"]["assignment_manifest"]
        binding["frozen_at"] = "2026-07-21T10:00:00Z"
        rehash(binding)
        with self.assertRaisesRegex(AnalysisError, "before the first locked outcome"):
            analyze_input(input_data)

    def test_reviewer_oracle_masking_is_enforced(self) -> None:
        input_data = reviewer_input()
        input_data["observations"][0]["reviewer_view"]["reference_label"] = "supported"
        with self.assertRaisesRegex(AnalysisError, "leaks oracle/reference"):
            analyze_input(input_data)

    def test_reviewer_reference_cannot_change_between_record_conditions(self) -> None:
        input_data = reviewer_input()
        first_case = input_data["observations"][0]["case_id"]
        changed = next(
            row
            for row in input_data["observations"]
            if row["case_id"] == first_case and row["condition"] == "degraded"
        )
        changed["reference_label"] = "defeated"
        with self.assertRaisesRegex(AnalysisError, "hidden reference changes"):
            analyze_input(input_data)

    def test_split_overlap_is_rejected(self) -> None:
        input_data = predictive_input(False)
        input_data["design"]["held_out_trace_family_ids"] = [
            "development_trace_family"
        ]
        input_data["design_object_bindings"]["held_out_manifest"] = manifest(
            "predictive_heldout_manifest",
            {
                "split_unit": "trace_family",
                "training_trace_family_ids": ["development_trace_family"],
                "held_out_trace_family_ids": ["development_trace_family"],
            },
        )
        with self.assertRaisesRegex(AnalysisError, "splits overlap"):
            analyze_input(input_data)


if __name__ == "__main__":
    unittest.main()
