"""Direct mutation tests for proposal/gate/execution closure."""

from __future__ import annotations

import copy
import unittest

from scripts.validate_delegation_artifacts import (
    DEFAULT_ARTIFACT_DIR,
    REGIME_FIXTURE_NAME,
    TRACE_SCHEMA_NAME,
    derive_trace_results,
    load_json,
    schema_errors,
)


class DelegationExecutionClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_dir = DEFAULT_ARTIFACT_DIR / "fixtures"
        cls.regime = load_json(fixture_dir / REGIME_FIXTURE_NAME)
        cls.trace = load_json(fixture_dir / "05-local-steps-cumulative-violation.json")
        cls.oracle = load_json(
            fixture_dir / "oracles" / "05-local-steps-cumulative-violation.oracle.json"
        )
        cls.trace_schema = load_json(DEFAULT_ARTIFACT_DIR / TRACE_SCHEMA_NAME)

    def test_execution_requires_actual_action(self) -> None:
        mutant = copy.deepcopy(self.trace)
        mutant["records"]["executions"][0].pop("action")
        errors = schema_errors(mutant, self.trace_schema, DEFAULT_ARTIFACT_DIR / "mutant.json")
        self.assertTrue(any("action" in error and "required property" in error for error in errors))

    def test_post_gate_action_divergence_is_prohibited(self) -> None:
        mutant = copy.deepcopy(self.trace)
        execution = mutant["records"]["executions"][0]
        execution["action"]["parameters"]["channel"] = "external"
        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertTrue(any("post-gate execution divergence" in error for error in errors))
        self.assertEqual(derived["execution_authorizations"][execution["execution_id"]], "prohibited")

    def test_post_gate_actor_divergence_is_prohibited(self) -> None:
        mutant = copy.deepcopy(self.trace)
        execution = mutant["records"]["executions"][0]
        execution["executor_id"] = "human_approver"
        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertTrue(any("post-gate execution divergence" in error for error in errors))
        self.assertEqual(derived["execution_authorizations"][execution["execution_id"]], "prohibited")

    def test_execution_before_allow_gate_is_prohibited(self) -> None:
        mutant = copy.deepcopy(self.trace)
        execution = mutant["records"]["executions"][0]
        execution["timestamp"] = "2026-07-19T14:01:30Z"
        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertTrue(any("execution precedes its gate decision" in error for error in errors))
        self.assertEqual(derived["execution_authorizations"][execution["execution_id"]], "prohibited")

    def test_execution_linked_to_block_gate_is_prohibited(self) -> None:
        mutant = copy.deepcopy(self.trace)
        execution = mutant["records"]["executions"][0]
        gate = next(
            item
            for item in mutant["records"]["gate_decisions"]
            if item["gate_decision_id"] == execution["gate_decision_id"]
        )
        gate["decision"] = "block"
        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(derived["execution_authorizations"][execution["execution_id"]], "prohibited")


if __name__ == "__main__":
    unittest.main()
