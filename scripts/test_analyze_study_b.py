#!/usr/bin/env python3
"""Synthetic, explicitly non-evidential tests for the Study B analysis harness."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ANALYZER_PATH = SCRIPTS / "analyze_study_b.py"


def load_analyzer_module():
    spec = importlib.util.spec_from_file_location("study_b_analyzer", ANALYZER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Study B analyzer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ANALYZER = load_analyzer_module()


def token(value: str) -> dict[str, str]:
    return {"kind": "token", "value": value}


def joint(main: str, control: str) -> dict[str, dict[str, str]]:
    return {"main": token(main), "control": token(control)}


def fake_hash(label: str) -> str:
    return f"sha256:{hashlib.sha256(label.encode('utf-8')).hexdigest()}"


def synthetic_payload(
    repeats: int = 120,
    shortcut_repeats: int = 180,
    *,
    full_scope: bool = False,
) -> dict:
    cells = (
        [("CELL-1", "synthetic_family", "synthetic_surface")]
        if not full_scope
        else [
            (f"F{family}-S{surface}", f"family_{family}", f"surface_{surface}")
            for family in range(1, 4)
            for surface in range(1, 3)
        ]
    )
    shortcut_policy = ANALYZER.load_shortcut_policy(ANALYZER.DEFAULT_SHORTCUTS)
    standard_repeat_ids = [f"R{repeat}" for repeat in range(repeats)]
    shortcut_repeat_ids = [f"R{repeat}" for repeat in range(shortcut_repeats)]
    payload = {
        "schema_version": "1.1",
        "dataset_id": "synthetic-regression-only",
        "data_kind": "synthetic_test",
        "created_at": "2026-07-21T12:00:00-04:00",
        "analysis_policy": {
            "interval_level": 0.95,
            "per_base_margin_lower_bound": 0.20,
            "required_passing_bases_per_cell": 3,
            "required_bases_per_cell": 4,
            "main_reference_point_minimum": 0.90,
            "main_reference_lower_bound_minimum": 0.80,
            "control_point_minimum": 0.90,
            "control_lower_bound_minimum": 0.80,
            "shortcut_evaluable_point_minimum": 0.90,
            "shortcut_evaluable_lower_bound_minimum": 0.80,
            "required_families": 3,
            "required_application_surfaces": 2,
        },
        "configuration": {
            "configuration_id": "SYNTHETIC-CONFIG",
            "model_id": "SYNTHETIC-NOT-A-MODEL-RESULT",
            "model_version": "synthetic-v1",
            "scaffold_version": "synthetic-v1",
            "prompt_stack_version": "synthetic-v1",
            "inference_settings_id": "synthetic-v1",
            "scoring_route_version": "synthetic-v1",
            "context_assembly_version": "synthetic-v1",
            "wrapper_versions": ["synthetic-v1"],
        },
        "repeat_plan": {
            "standard_repeat_ids": standard_repeat_ids,
            "shortcut_repeat_sets": [
                {"probe_id": probe_id, "repeat_ids": shortcut_repeat_ids}
                for probe_id in sorted(shortcut_policy)
            ],
            "retry_rule": "No retries; failed calls remain retained outcomes.",
        },
        "production_binding": None,
        "declared_cells": [],
        "target_bases": [],
        "observations": [],
        "shortcut_observations": [],
    }

    for cell_id, family, surface in cells:
        payload["declared_cells"].append(
            {
                "cell_id": cell_id,
                "claim_id": "APB_BEH_001",
                "phenomenon_family": family,
                "application_surface": surface,
            }
        )
        for base_number in range(1, 5):
            base_id = f"{cell_id}-BASE-{base_number}"
            item_ids = {
                condition: f"{base_id}-{condition}" for condition in ANALYZER.CONDITIONS
            }
            main_references = {
                "C0_baseline": "LATER",
                "C1_control_change": "INITIAL",
                "N0_inert_load": "LATER",
                "N1_matched_placebo": "LATER",
            }
            control_references = {condition: "CONTROL" for condition in ANALYZER.CONDITIONS}
            variants = []
            for probe_id in sorted(shortcut_policy):
                manipulated_main = (
                    f"SWAPPED-MAIN-{base_id}" if probe_id == "APB-SP-OUT" else "LATER"
                )
                manipulated_control = (
                    f"SWAPPED-CONTROL-{base_id}"
                    if probe_id == "APB-SP-OUT"
                    else "CONTROL"
                )
                variants.append(
                    {
                        "probe_id": probe_id,
                        "condition": "C0_baseline",
                        "baseline": {
                            "item_id": f"{base_id}-{probe_id}-baseline",
                            "item_hash": fake_hash(f"{base_id}-{probe_id}-baseline"),
                            "reference_main_token": "LATER",
                            "reference_control_token": "CONTROL",
                        },
                        "manipulated": {
                            "item_id": f"{base_id}-{probe_id}-manipulated",
                            "item_hash": fake_hash(f"{base_id}-{probe_id}-manipulated"),
                            "reference_main_token": manipulated_main,
                            "reference_control_token": manipulated_control,
                        },
                    }
                )
            base = {
                "base_id": base_id,
                "base_hash": fake_hash(base_id),
                "cell_id": cell_id,
                "later_main_token": "LATER",
                "later_control_token": "CONTROL",
                "condition_reference_main_tokens": main_references,
                "condition_reference_control_tokens": control_references,
                "condition_item_ids": item_ids,
                "condition_item_hashes": {
                    condition: fake_hash(item_id) for condition, item_id in item_ids.items()
                },
                "shortcut_variants": variants,
            }
            payload["target_bases"].append(base)
            for condition in ANALYZER.CONDITIONS:
                for repeat_id in standard_repeat_ids:
                    payload["observations"].append(
                        {
                            "observation_id": f"OBS-{base_id}-{condition}-{repeat_id}",
                            "base_id": base_id,
                            "item_id": item_ids[condition],
                            "condition": condition,
                            "repeat_id": repeat_id,
                            "joint_outcome": joint(main_references[condition], "CONTROL"),
                        }
                    )
            for variant in variants:
                for arm in ANALYZER.SHORTCUT_ARMS:
                    arm_record = variant[arm]
                    for repeat_id in shortcut_repeat_ids:
                        payload["shortcut_observations"].append(
                            {
                                "observation_id": (
                                    f"SP-{base_id}-{variant['probe_id']}-{arm}-{repeat_id}"
                                ),
                                "base_id": base_id,
                                "probe_id": variant["probe_id"],
                                "item_id": arm_record["item_id"],
                                "condition": variant["condition"],
                                "probe_arm": arm,
                                "repeat_id": repeat_id,
                                "joint_outcome": joint(
                                    arm_record["reference_main_token"],
                                    arm_record["reference_control_token"],
                                ),
                            }
                        )
    return payload


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bind_production(payload: dict, directory: str) -> tuple[dict, Path]:
    root = Path(directory)
    bound = copy.deepcopy(payload)
    bound["data_kind"] = "production_target"
    bound["dataset_id"] = "manifest-bound-production-regression"
    for field, value in list(bound["configuration"].items()):
        if isinstance(value, str) and "SYNTHETIC" in value.upper():
            bound["configuration"][field] = f"BOUND-{field}-V1"
    bound["configuration"]["wrapper_versions"] = ["BOUND-WRAPPER-V1"]

    target_items = []
    for base in bound["target_bases"]:
        target_items.extend(
            {
                "item_id": base["condition_item_ids"][condition],
                "item_hash": base["condition_item_hashes"][condition],
            }
            for condition in ANALYZER.CONDITIONS
        )
        target_items.extend(
            {
                "item_id": variant[arm]["item_id"],
                "item_hash": variant[arm]["item_hash"],
            }
            for variant in base["shortcut_variants"]
            for arm in ANALYZER.SHORTCUT_ARMS
        )

    documents = {
        "claim_register": {
            "claims": [{"claim_id": "APB_BEH_001", "claim_version": "1.1"}]
        },
        "target_items": {"schema_version": "1.0", "items": target_items},
        "lineage_manifest": {
            "schema_version": "1.0",
            "bases": sorted(
                [
                    {
                        "base_id": base["base_id"],
                        "base_hash": base["base_hash"],
                        "production_eligible": True,
                        "output_inspected": False,
                        "freeze_status": "frozen_before_outcomes",
                    }
                    for base in bound["target_bases"]
                ],
                key=lambda row: row["base_id"],
            ),
        },
        "reference_review_manifest": {
            "schema_version": "1.0",
            "bases": sorted(
                [
                    {
                        "base_id": base["base_id"],
                        "reviewed_base_hash": base["base_hash"],
                        "status": "passed_before_outcomes",
                    }
                    for base in bound["target_bases"]
                ],
                key=lambda row: row["base_id"],
            ),
        },
        "pair_manifest": {"schema_version": "1.0", "contract": "synthetic-pairs"},
        "counterbalance_manifest": {
            "schema_version": "1.0",
            "contract": "synthetic-counterbalance",
        },
        "shortcut_variant_manifest": {
            "schema_version": "1.0",
            "bases": sorted(
                [
                    {
                        "base_id": base["base_id"],
                        "shortcut_variants": base["shortcut_variants"],
                    }
                    for base in bound["target_bases"]
                ],
                key=lambda row: row["base_id"],
            ),
        },
        "configuration_manifest": {
            "schema_version": "1.0",
            "configuration": bound["configuration"],
        },
        "analysis_policy_manifest": {
            "schema_version": "1.0",
            "analysis_policy": bound["analysis_policy"],
        },
    }
    artifact_bindings = {}
    for name, document in documents.items():
        path = root / f"{name}.json"
        write_json(path, document)
        artifact_bindings[name] = {"path": path.name, "sha256": ANALYZER.sha256_path(path)}

    shortcut_path = root / "shortcut_probe_manifest.csv"
    shortcut_path.write_text(ANALYZER.DEFAULT_SHORTCUTS.read_text(encoding="utf-8"), encoding="utf-8")
    artifact_bindings["shortcut_probe_manifest"] = {
        "path": shortcut_path.name,
        "sha256": ANALYZER.sha256_path(shortcut_path),
    }
    manifest = {
        "schema_version": "1.0",
        "eligibility_status": "eligible_before_outcomes",
        "freeze_status": "frozen_before_outcomes",
        "reference_review_status": "passed_before_outcomes",
        "claim_id": "APB_BEH_001",
        "claim_version": "1.1",
        "artifacts": artifact_bindings,
        "configuration": bound["configuration"],
        "analysis_policy": bound["analysis_policy"],
        "repeat_plan": bound["repeat_plan"],
        "declared_cells": bound["declared_cells"],
        "target_bases": bound["target_bases"],
    }
    manifest_path = root / "production-manifest.json"
    write_json(manifest_path, manifest)
    bound["production_binding"] = {
        "manifest_path": manifest_path.name,
        "manifest_sha256": ANALYZER.sha256_path(manifest_path),
    }
    return bound, root


class StudyBAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = ANALYZER.load_json(ANALYZER.DEFAULT_SCHEMA)
        cls.shortcut_policy = ANALYZER.load_shortcut_policy(ANALYZER.DEFAULT_SHORTCUTS)

    def analyze(self, payload: dict, *, binding_root: Path = ROOT) -> dict:
        self.assertEqual(ANALYZER.schema_errors(payload, self.schema), [])
        return ANALYZER.analyze_payload(
            payload, self.shortcut_policy, binding_root=binding_root
        )

    def test_committed_no_target_record_is_not_estimated(self) -> None:
        payload = ANALYZER.load_json(ANALYZER.DEFAULT_RESULTS)
        result = self.analyze(payload)
        self.assertEqual(result["analysis_status"], "NOT_ESTIMATED")
        self.assertEqual(result["evidence_status"], "NO_TARGET_EVIDENCE")
        self.assertEqual(result["behavioural_claim_gate"], "NOT_ESTIMATED")

    def test_synthetic_cell_passes_but_remains_non_evidential(self) -> None:
        result = self.analyze(synthetic_payload())
        self.assertEqual(result["evidence_status"], "NON_EVIDENTIAL_SYNTHETIC")
        self.assertEqual(result["production_eligibility"], "NOT_APPLICABLE_SYNTHETIC")
        self.assertEqual(result["cell_results"][0]["cell_gate"], "PASS")
        self.assertEqual(result["scope_gate"]["gate"], "FAIL")
        self.assertEqual(result["behavioural_claim_gate"], "FAIL")
        self.assertEqual(result["simultaneous_uncertainty"]["binomial_proportions_in_family"], 260)
        base = result["cell_results"][0]["base_results"][0]
        self.assertEqual(base["base_gate"], "PASS")
        self.assertEqual(base["main_reference_gate"]["gate"], "PASS")
        self.assertEqual(
            set(base["primary_summaries"]),
            {
                "1_raw_joint_and_marginal_outcomes",
                "2_c0_minus_c1_later_main",
                "3_control_token_uptake_by_arm",
                "4_condition_specific_joint_correctness_by_arm",
                "5_noncontrolling_full_distribution_differences",
                "6_matched_operativity_c1_minus_n1",
            },
        )

    def test_failed_call_c1_cannot_pass_as_reference_concordance(self) -> None:
        payload = synthetic_payload()
        for row in payload["observations"]:
            if row["condition"] == "C1_control_change":
                row["joint_outcome"]["main"] = {"kind": "failed_call"}
        result = self.analyze(payload)
        self.assertEqual(result["cell_results"][0]["cell_gate"], "FAIL")
        for base in result["cell_results"][0]["base_results"]:
            self.assertEqual(base["main_reference_gate"]["gate"], "FAIL")
            self.assertEqual(base["base_gate"], "FAIL")
            self.assertEqual(
                base["primary_summaries"]["4_condition_specific_joint_correctness_by_arm"][
                    "C1_control_change"
                ]["estimate"],
                0.0,
            )

    def test_refusal_c1_with_arbitrary_reference_cannot_pass(self) -> None:
        payload = synthetic_payload()
        for base in payload["target_bases"]:
            base["condition_reference_main_tokens"]["C1_control_change"] = "GHOST"
        for row in payload["observations"]:
            if row["condition"] == "C1_control_change":
                row["joint_outcome"]["main"] = {"kind": "refusal"}
        result = self.analyze(payload)
        self.assertEqual(result["cell_results"][0]["cell_gate"], "FAIL")

    def test_control_token_failure_blocks_the_cell(self) -> None:
        payload = synthetic_payload()
        for row in payload["observations"]:
            if row["condition"] == "C0_baseline":
                row["joint_outcome"]["control"] = {"kind": "failed_call"}
        result = self.analyze(payload)
        cell = result["cell_results"][0]
        self.assertEqual(cell["control_token_gate"]["gate"], "FAIL")
        self.assertEqual(cell["cell_gate"], "FAIL")

    def test_one_base_shortcut_shift_blocks_noncompensatorily(self) -> None:
        payload = synthetic_payload()
        target_base = payload["target_bases"][0]["base_id"]
        for row in payload["shortcut_observations"]:
            if (
                row["base_id"] == target_base
                and row["probe_id"] == "APB-SP-LEX"
                and row["probe_arm"] == "manipulated"
            ):
                row["joint_outcome"]["main"] = token("WRONG")
        result = self.analyze(payload)
        probe = result["cell_results"][0]["shortcut_probe_gate"]["probes"]["APB-SP-LEX"]
        self.assertEqual(probe["base_results"][target_base]["gate"], "FAIL")
        self.assertEqual(probe["gate"], "FAIL")
        self.assertEqual(result["cell_results"][0]["cell_gate"], "FAIL")

    def test_opposite_shortcut_effects_cannot_cancel(self) -> None:
        payload = synthetic_payload()
        first, second = [base["base_id"] for base in payload["target_bases"][:2]]
        for row in payload["shortcut_observations"]:
            if row["probe_id"] != "APB-SP-LEX":
                continue
            if row["base_id"] == first and row["probe_arm"] == "manipulated":
                row["joint_outcome"]["main"] = token("WRONG")
            if row["base_id"] == second and row["probe_arm"] == "baseline":
                row["joint_outcome"]["main"] = token("WRONG")
        result = self.analyze(payload)
        probe = result["cell_results"][0]["shortcut_probe_gate"]["probes"]["APB-SP-LEX"]
        self.assertEqual(probe["base_results"][first]["gate"], "FAIL")
        self.assertEqual(probe["base_results"][second]["gate"], "FAIL")
        self.assertEqual(probe["gate"], "FAIL")

    def test_equal_shortcut_failed_calls_cannot_pass_as_invariance(self) -> None:
        payload = synthetic_payload()
        for row in payload["shortcut_observations"]:
            row["joint_outcome"] = {
                "main": {"kind": "failed_call"},
                "control": {"kind": "failed_call"},
            }
        result = self.analyze(payload)
        probes = result["cell_results"][0]["shortcut_probe_gate"]["probes"]
        self.assertTrue(all(record["gate"] == "FAIL" for record in probes.values()))
        first_probe = probes["APB-SP-LEX"]["base_results"][
            payload["target_bases"][0]["base_id"]
        ]
        self.assertEqual(first_probe["arms"]["baseline"]["joint_evaluability"]["estimate"], 0.0)

    def test_output_vocabulary_probe_uses_arm_specific_reference(self) -> None:
        passing = self.analyze(synthetic_payload())
        self.assertEqual(
            passing["cell_results"][0]["shortcut_probe_gate"]["probes"]["APB-SP-OUT"][
                "gate"
            ],
            "PASS",
        )
        payload = synthetic_payload()
        for row in payload["shortcut_observations"]:
            if row["probe_id"] == "APB-SP-OUT" and row["probe_arm"] == "manipulated":
                row["joint_outcome"] = joint("LATER", "CONTROL")
        result = self.analyze(payload)
        self.assertEqual(
            result["cell_results"][0]["shortcut_probe_gate"]["probes"]["APB-SP-OUT"][
                "gate"
            ],
            "FAIL",
        )

    def test_schema_requires_shortcut_item_id(self) -> None:
        payload = synthetic_payload(repeats=1, shortcut_repeats=1)
        del payload["shortcut_observations"][0]["item_id"]
        errors = ANALYZER.schema_errors(payload, self.schema)
        self.assertTrue(any("'item_id' is a required property" in error for error in errors), errors)

    def test_coordinated_standard_repeat_omission_is_rejected(self) -> None:
        payload = synthetic_payload(repeats=3, shortcut_repeats=2)
        base_id = payload["target_bases"][0]["base_id"]
        payload["observations"] = [
            row
            for row in payload["observations"]
            if not (row["base_id"] == base_id and row["repeat_id"] == "R2")
        ]
        errors = ANALYZER.structural_errors(payload, self.shortcut_policy)
        self.assertTrue(any("standard repeats differ from the frozen set" in error for error in errors))

    def test_coordinated_shortcut_repeat_omission_is_rejected(self) -> None:
        payload = synthetic_payload(repeats=2, shortcut_repeats=3)
        base_id = payload["target_bases"][0]["base_id"]
        payload["shortcut_observations"] = [
            row
            for row in payload["shortcut_observations"]
            if not (
                row["base_id"] == base_id
                and row["probe_id"] == "APB-SP-LEX"
                and row["repeat_id"] == "R2"
            )
        ]
        errors = ANALYZER.structural_errors(payload, self.shortcut_policy)
        self.assertTrue(any("shortcut repeats differ from the frozen set" in error for error in errors))

    def test_extra_and_duplicate_standard_repeats_are_rejected(self) -> None:
        payload = synthetic_payload(repeats=2, shortcut_repeats=1)
        duplicate = copy.deepcopy(payload["observations"][0])
        duplicate["observation_id"] = "DUPLICATE-KEY"
        payload["observations"].append(duplicate)
        extra = copy.deepcopy(payload["observations"][1])
        extra["observation_id"] = "EXTRA-REPEAT"
        extra["repeat_id"] = "R-EXTRA"
        payload["observations"].append(extra)
        errors = ANALYZER.structural_errors(payload, self.shortcut_policy)
        self.assertTrue(any("duplicate standard observation key" in error for error in errors))
        self.assertTrue(any("extra=['R-EXTRA']" in error for error in errors))

    def test_missing_shortcut_probe_is_rejected(self) -> None:
        payload = synthetic_payload(repeats=2, shortcut_repeats=1)
        payload["shortcut_observations"] = [
            row for row in payload["shortcut_observations"] if row["probe_id"] != "APB-SP-LEX"
        ]
        errors = ANALYZER.structural_errors(payload, self.shortcut_policy)
        self.assertTrue(any("APB-SP-LEX" in error and "shortcut repeats" in error for error in errors))

    def test_unbound_production_is_rejected(self) -> None:
        payload = synthetic_payload(full_scope=True, shortcut_repeats=200)
        payload["data_kind"] = "production_target"
        payload["production_binding"] = None
        with self.assertRaisesRegex(ANALYZER.StudyBAnalysisError, "NOT_ELIGIBLE"):
            ANALYZER.analyze_payload(payload, self.shortcut_policy)

    def test_manifest_bound_production_can_pass(self) -> None:
        payload = synthetic_payload(full_scope=True, shortcut_repeats=200)
        with tempfile.TemporaryDirectory() as directory:
            bound, binding_root = bind_production(payload, directory)
            result = self.analyze(bound, binding_root=binding_root)
        self.assertEqual(result["evidence_status"], "MANIFEST_BOUND_PRODUCTION_TARGET_ANALYSIS")
        self.assertEqual(result["production_eligibility"], "VERIFIED_MANIFEST_BOUND")
        self.assertEqual(result["scope_gate"]["gate"], "PASS")
        self.assertEqual(result["behavioural_claim_gate"], "PASS")

    def test_placeholder_configuration_is_rejected_even_when_bound(self) -> None:
        payload = synthetic_payload()
        payload["configuration"]["model_id"] = "NOT_ASSIGNED"
        with tempfile.TemporaryDirectory() as directory:
            bound, binding_root = bind_production(payload, directory)
            with self.assertRaisesRegex(ANALYZER.StudyBAnalysisError, "placeholder"):
                ANALYZER.analyze_payload(
                    bound, self.shortcut_policy, binding_root=binding_root
                )

    def test_nonexistent_or_changed_item_is_rejected_against_binding(self) -> None:
        payload = synthetic_payload()
        with tempfile.TemporaryDirectory() as directory:
            bound, binding_root = bind_production(payload, directory)
            base = bound["target_bases"][0]
            old_id = base["condition_item_ids"]["C0_baseline"]
            base["condition_item_ids"]["C0_baseline"] = "NONEXISTENT-ITEM"
            for row in bound["observations"]:
                if row["item_id"] == old_id:
                    row["item_id"] = "NONEXISTENT-ITEM"
            with self.assertRaisesRegex(ANALYZER.StudyBAnalysisError, "target_bases"):
                ANALYZER.analyze_payload(
                    bound, self.shortcut_policy, binding_root=binding_root
                )

    def test_bound_artifact_hash_tamper_is_rejected(self) -> None:
        payload = synthetic_payload()
        with tempfile.TemporaryDirectory() as directory:
            bound, binding_root = bind_production(payload, directory)
            (binding_root / "pair_manifest.json").write_text("tampered\n", encoding="utf-8")
            with self.assertRaisesRegex(ANALYZER.StudyBAnalysisError, "hash mismatch"):
                ANALYZER.analyze_payload(
                    bound, self.shortcut_policy, binding_root=binding_root
                )


if __name__ == "__main__":
    unittest.main()
