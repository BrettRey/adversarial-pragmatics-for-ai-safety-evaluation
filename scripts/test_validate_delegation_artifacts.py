"""Direct mutation tests for temporal authority and execution closure."""

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


class DelegationChronologicalAuthorityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_dir = DEFAULT_ARTIFACT_DIR / "fixtures"
        cls.regime = load_json(fixture_dir / REGIME_FIXTURE_NAME)
        cls.trace = load_json(fixture_dir / "06-valid-revocation-transition.json")
        cls.oracle = load_json(
            fixture_dir / "oracles" / "06-valid-revocation-transition.oracle.json"
        )
        cls.conditionally_activated_trace = load_json(
            fixture_dir / "07-ineffective-override-valid-release.json"
        )
        cls.conditionally_activated_oracle = load_json(
            fixture_dir
            / "oracles"
            / "07-ineffective-override-valid-release.oracle.json"
        )
        cls.trace_schema = load_json(DEFAULT_ARTIFACT_DIR / TRACE_SCHEMA_NAME)

    def add_child_grant(
        self,
        trace: dict,
        issued_at: str,
        proposal_at: str | None = None,
    ) -> tuple[dict, dict, dict | None]:
        parent = trace["grants"][0]
        parent["subdelegation_allowed"] = True
        child = {
            "grant_id": "chronological_subgrant",
            "authority_object": parent["authority_object"],
            "grantor_ids": [parent["grantee_id"]],
            "grantee_id": "document_service",
            "action_classes": list(parent["action_classes"]),
            "scope": copy.deepcopy(parent["scope"]),
            "issued_at": issued_at,
            "effective_interval": {
                "starts_at": issued_at,
                "ends_at": parent["effective_interval"]["ends_at"],
            },
            "subdelegation_allowed": False,
            "parent_grant_ids": [parent["grant_id"]],
            "guard_evidence": {},
            "activation_transition_id": None,
            "record_status": "asserted_valid",
        }
        trace["grants"].append(child)
        proposal = None
        if proposal_at is not None:
            proposal = trace["records"]["proposals"][0]
            proposal["proposal_id"] = "chronological_child_proposal"
            proposal["authorization_subject_id"] = "document_service"
            proposal["timestamp"] = proposal_at
            proposal["recorded_authorization"] = "permitted"
            proposal["recorded_basis_grant_ids"] = [child["grant_id"]]
            proposal["recorded_reason"] = "Purported authority under the child grant."
        return parent, child, proposal

    def test_subgrant_issued_after_parent_revocation_is_invalid(self) -> None:
        """Permanent regression for the external review's reproduced fixture."""

        mutant = copy.deepcopy(self.trace)
        _, child, proposal = self.add_child_grant(
            mutant,
            "2026-07-20T14:02:00Z",
            "2026-07-20T14:04:00Z",
        )
        self.assertIsNotNone(proposal)
        schema_issues = schema_errors(
            mutant,
            self.trace_schema,
            DEFAULT_ARTIFACT_DIR / "adversarial-post-revocation.json",
        )
        self.assertEqual(schema_issues, [])

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])
        self.assertEqual(
            derived["proposal_authorizations"][proposal["proposal_id"]],
            "prohibited",
        )

    def test_offset_timestamp_ordering_uses_absolute_instants(self) -> None:
        mutant = copy.deepcopy(self.trace)
        mutant["transitions"][0]["timestamp"] = "2026-07-20T15:01:00+01:00"
        _, child, _ = self.add_child_grant(mutant, "2026-07-20T14:02:00Z")

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])

    def test_subgrant_issued_before_parent_authority_is_invalid(self) -> None:
        mutant = copy.deepcopy(self.trace)
        mutant["transitions"] = []
        parent, child, _ = self.add_child_grant(mutant, "2026-07-20T14:02:00Z")
        parent["issued_at"] = "2026-07-20T14:03:00Z"

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])

    def test_subgrant_issued_after_parent_expiry_is_invalid(self) -> None:
        mutant = copy.deepcopy(self.trace)
        mutant["transitions"] = []
        parent, child, _ = self.add_child_grant(mutant, "2026-07-20T14:02:00Z")
        parent["effective_interval"]["ends_at"] = "2026-07-20T14:01:00Z"
        child["effective_interval"] = {
            "starts_at": "2026-07-20T14:00:00Z",
            "ends_at": "2026-07-20T14:01:00Z",
        }

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])

    def test_inactive_conditionally_activated_parent_cannot_subdelegate(self) -> None:
        mutant = copy.deepcopy(self.conditionally_activated_trace)
        _, child, _ = self.add_child_grant(mutant, "2026-07-21T14:02:00Z")

        errors: list[str] = []
        derived = derive_trace_results(
            self.regime, mutant, self.conditionally_activated_oracle, errors
        )
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])

    def test_equal_instant_revocation_precedes_subgrant_issuance(self) -> None:
        mutant = copy.deepcopy(self.trace)
        _, child, _ = self.add_child_grant(mutant, "2026-07-20T14:01:00Z")

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertFalse(derived["valid_grants"][child["grant_id"]])

    def test_parent_revocation_does_not_implicitly_cascade(self) -> None:
        mutant = copy.deepcopy(self.trace)
        _, child, proposal = self.add_child_grant(
            mutant,
            "2026-07-20T14:00:00Z",
            "2026-07-20T14:04:00Z",
        )
        self.assertIsNotNone(proposal)

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertTrue(derived["valid_grants"][child["grant_id"]])
        self.assertEqual(
            derived["proposal_authorizations"][proposal["proposal_id"]],
            "authorized",
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

    def test_offset_execution_ordering_uses_absolute_instants(self) -> None:
        mutant = copy.deepcopy(self.trace)
        mutant["records"]["executions"][0][
            "timestamp"
        ] = "2026-07-19T15:03:00+01:00"

        errors: list[str] = []
        derived = derive_trace_results(self.regime, mutant, self.oracle, errors)
        self.assertEqual(errors, [])
        self.assertEqual(
            derived["prefix_condition_results"],
            self.oracle["prefix_condition_results"],
        )


if __name__ == "__main__":
    unittest.main()
