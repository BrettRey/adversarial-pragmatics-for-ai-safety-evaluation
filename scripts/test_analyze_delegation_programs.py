"""Synthetic pass/fail tests for the frozen Delegation Assurance programmes."""

from __future__ import annotations

import copy
import unittest

from scripts.analyze_delegation_programs import AnalysisError, analyze_input, canonical_sha256


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


def local_input(with_observations: bool = True) -> dict:
    families = ["indirect_injection", "confused_deputy", "persistence", "temporal_authority"]
    observations = []
    held_out = []
    if with_observations:
        for family in families:
            for index in range(30):
                base_id = f"{family}_base_{index}"
                held_out.append(base_id)
                observations.append(
                    {
                        "observation_id": f"{family}_observation_{index}",
                        "family": family,
                        "base_item_id": base_id,
                        "reference_direction": 1,
                        "baseline_endpoint": 0.10,
                        "authority_endpoint": 0.90,
                        "placebo_endpoint": 0.10,
                        "order_reversal_endpoint": 0.90,
                        "shortcut_endpoint": 0.10,
                        "control_correct": True,
                        "reset_confirmed": True,
                        "evaluator_view": {"case_id": base_id, "standing_representation": "assigned"},
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
                    arm: f"{observation['observation_id']}_{arm}_presentation" for arm in arms
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
                    "development_base_item_ids": design["development_base_item_ids"],
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
                observations.append(
                    {
                        "observation_id": f"{family}_prediction_{index}",
                        "family": family,
                        "trace_family_id": f"heldout_trace_family_{index % 10}",
                        "target": target,
                        "typed_probability": 0.95 if target else 0.05,
                        "baseline_probability": 0.50,
                        "predictor_view": {"case_id": f"case_{family}_{index}", "trace_length": 3},
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
                    "calibration_bins": 10,
                },
            ),
            "held_out_manifest": manifest(
                "predictive_heldout_manifest",
                {
                    "split_unit": "trace_family",
                    "training_trace_family_ids": design["training_trace_family_ids"],
                    "held_out_trace_family_ids": design["held_out_trace_family_ids"],
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
        for family in families:
            for case_index in range(10):
                case_id = f"{family}_case_{case_index}"
                held_out.append(case_id)
                for condition in ("typed", "degraded"):
                    for repeat in range(3):
                        observations.append(
                            {
                                "judgment_id": f"{family}_{condition}_{case_index}_{repeat}",
                                "reviewer_id": f"reviewer_{(case_index + repeat) % 6}",
                                "case_id": case_id,
                                "family": family,
                                "condition": condition,
                                "reviewer_verdict": "supported" if condition == "typed" else "defeated",
                                "reference_label": "supported",
                                "justified_uncertainty": False,
                                "technical_locus_correct": condition == "typed",
                                "reviewer_view": {"case_id": case_id, "record_condition": condition},
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
    def test_synthetic_passes_preserve_vectors(self) -> None:
        for builder in (local_input, predictive_input, reviewer_input):
            input_data = builder()
            output = analyze_input(input_data)
            self.assertEqual(output["decision"], "PASS")
            self.assertFalse(output["scalar_aggregation_permitted"])
            self.assertEqual(len(output["observation_vectors"]), len(input_data["observations"]))
            self.assertTrue(all(result["decision"] == "PASS" for result in output["family_results"]))

    def test_no_data_is_not_estimated(self) -> None:
        for builder in (local_input, predictive_input, reviewer_input):
            output = analyze_input(builder(False))
            self.assertEqual(output["decision"], "NOT_ESTIMATED")
            self.assertEqual(output["not_estimated_reason"], "NO_OBSERVATIONS")
            self.assertTrue(
                all(result["decision"] == "NOT_ESTIMATED" for result in output["family_results"])
            )

    def test_failed_family_cannot_be_compensated_by_other_families(self) -> None:
        input_data = local_input()
        for observation in input_data["observations"]:
            if observation["family"] == "temporal_authority":
                observation["authority_endpoint"] = observation["baseline_endpoint"]
                observation["order_reversal_endpoint"] = observation["baseline_endpoint"]
        output = analyze_input(input_data)
        decisions = {row["family"]: row["decision"] for row in output["family_results"]}
        self.assertEqual(decisions["temporal_authority"], "FAIL")
        self.assertEqual(sum(value == "PASS" for value in decisions.values()), 3)
        self.assertEqual(output["decision"], "FAIL")

    def test_predictive_leakage_is_rejected(self) -> None:
        input_data = predictive_input()
        input_data["observations"][0]["predictor_view"]["oracle_verdict"] = "supported"
        with self.assertRaisesRegex(AnalysisError, "non-allowlisted|leaks"):
            analyze_input(input_data)

    def test_duplicate_rows_within_one_trace_family_do_not_fake_precision(self) -> None:
        input_data = predictive_input()
        for observation in input_data["observations"]:
            if observation["family"] == "trajectory_authorization":
                observation["trace_family_id"] = "heldout_trace_family_0"
        output = analyze_input(input_data)
        result = next(
            row for row in output["family_results"] if row["family"] == "trajectory_authorization"
        )
        self.assertEqual(result["counts"]["observations"], 30)
        self.assertEqual(result["counts"]["trace_families"], 1)
        self.assertIsNone(result["metrics"]["trace_family_cluster_paired_brier_improvement_lcb_95"])
        self.assertEqual(result["decision"], "FAIL")
        self.assertEqual(output["decision"], "FAIL")

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
        unsigned = {key: value for key, value in binding.items() if key != "sha256"}
        binding["sha256"] = canonical_sha256(unsigned)
        with self.assertRaisesRegex(AnalysisError, "allocate all five presentation arms"):
            analyze_input(input_data)

    def test_manifest_must_precede_first_locked_outcome(self) -> None:
        input_data = reviewer_input()
        binding = input_data["design_object_bindings"]["assignment_manifest"]
        binding["frozen_at"] = "2026-07-21T10:00:00Z"
        unsigned = {key: value for key, value in binding.items() if key != "sha256"}
        binding["sha256"] = canonical_sha256(unsigned)
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
        input_data["design"]["held_out_trace_family_ids"] = ["development_trace_family"]
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
