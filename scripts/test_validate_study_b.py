#!/usr/bin/env python3
"""Regression and mutation tests for the Study B validator."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_study_b.py"
ITEMS_PATH = ROOT / "benchmark" / "study-b" / "commitment-protected-development-items.json"
SCHEMA_PATH = ROOT / "benchmark" / "study-b" / "schema.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("study_b_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Study B validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator_module()


class StudyBValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = VALIDATOR.load_json(ITEMS_PATH)
        cls.schema = VALIDATOR.load_json(SCHEMA_PATH)

    def validate(self, document):
        return VALIDATOR.validate_document(document, self.schema)

    def test_committed_fixture_passes(self) -> None:
        self.assertEqual(self.validate(copy.deepcopy(self.document)), [])

    def test_missing_condition_fails(self) -> None:
        document = copy.deepcopy(self.document)
        document["base_scenarios"][0]["conditions"].pop()
        errors = self.validate(document)
        self.assertTrue(any("condition set" in error for error in errors), errors)

    def test_stored_validity_must_equal_derived_validity(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][0]["conditions"][1]
        item["authorization_record"]["purported_transition"]["valid"] = True
        errors = self.validate(document)
        self.assertTrue(any("differs from derived validity" in error for error in errors), errors)

    def test_issuer_must_have_amendment_standing(self) -> None:
        document = copy.deepcopy(self.document)
        record = document["base_scenarios"][0]["conditions"][0]["authorization_record"]
        record["amendment_rule"]["amendment_actors"] = ["archive_board"]
        record["operation_standing"]["amend"]["holders"] = ["archive_board"]
        errors = self.validate(document)
        self.assertTrue(any("differs from derived validity" in error for error in errors), errors)

    def test_missing_required_guard_event_invalidates_transition(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][2]["conditions"][0][
            "authorization_record"
        ]["purported_transition"]
        transition["guard_evaluation"]["observed_events"] = []
        errors = self.validate(document)
        self.assertTrue(any("differs from derived validity" in error for error in errors), errors)

    def test_observed_protected_guard_event_changes_derived_validity(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][3]["conditions"][1][
            "authorization_record"
        ]["purported_transition"]
        transition["guard_evaluation"]["observed_events"] = ["review_council_approval"]
        errors = self.validate(document)
        self.assertTrue(any("differs from derived validity" in error for error in errors), errors)
        self.assertTrue(any("frozen condition design" in error for error in errors), errors)

    def test_c1_invalidity_must_be_guard_failure_not_lost_standing(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][0]["conditions"][1][
            "authorization_record"
        ]["purported_transition"]
        transition["issuer_role"] = "archive_review_officer"
        errors = self.validate(document)
        self.assertTrue(
            any("C1 issuer must retain amendment standing" in error for error in errors), errors
        )

    def test_c1_declared_guard_must_remain_unsatisfied(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][0]["conditions"][1][
            "authorization_record"
        ]["purported_transition"]
        transition["guard_evaluation"]["observed_events"] = ["board_vote"]
        errors = self.validate(document)
        self.assertTrue(
            any("C1 invalidity must be caused by a declared unsatisfied guard" in error for error in errors),
            errors,
        )

    def test_c1_cannot_gain_an_alternative_amendment_actor(self) -> None:
        document = copy.deepcopy(self.document)
        record = document["base_scenarios"][0]["conditions"][1]["authorization_record"]
        actors = ["archive_director", "archive_review_officer"]
        record["amendment_rule"]["amendment_actors"] = actors
        record["operation_standing"]["amend"]["holders"] = actors
        errors = self.validate(document)
        self.assertTrue(
            any("C1 amendment actors must be a nonempty C0 subset" in error for error in errors),
            errors,
        )
        self.assertTrue(
            any("C1 amend-standing holders must be a nonempty C0 subset" in error for error in errors),
            errors,
        )

    def test_guard_requirements_must_match_amendment_rule(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][1]["conditions"][1][
            "authorization_record"
        ]["purported_transition"]
        transition["guard_evaluation"]["required_events"] = []
        errors = self.validate(document)
        self.assertTrue(any("differ from the amendment rule" in error for error in errors), errors)

    def test_required_roles_must_bind_to_typed_guard_events(self) -> None:
        document = copy.deepcopy(self.document)
        amendment = document["base_scenarios"][0]["conditions"][1][
            "authorization_record"
        ]["amendment_rule"]
        amendment["required_roles"] = ["archive_review_officer"]
        errors = self.validate(document)
        self.assertTrue(
            any("required_roles are not bound to typed guard events" in error for error in errors),
            errors,
        )

        document = copy.deepcopy(self.document)
        amendment = document["base_scenarios"][0]["conditions"][1][
            "authorization_record"
        ]["amendment_rule"]
        amendment["required_roles"] = []
        errors = self.validate(document)
        self.assertTrue(
            any("C1 guard must declare a typed required role" in error for error in errors),
            errors,
        )

    def test_amendment_target_must_match_main_target(self) -> None:
        document = copy.deepcopy(self.document)
        transition = document["base_scenarios"][0]["conditions"][0][
            "authorization_record"
        ]["purported_transition"]
        transition["target"] = "audit_token"
        errors = self.validate(document)
        self.assertTrue(any("transition target must equal" in error for error in errors), errors)

    def test_reference_and_expected_action_must_match(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][1]["conditions"][0]
        item["expected_action"]["main_value"] = "MAPLE"
        errors = self.validate(document)
        self.assertTrue(any("differs from the authorization record" in error for error in errors), errors)

    def test_initial_control_must_differ_and_appear_in_prompt(self) -> None:
        document = copy.deepcopy(self.document)
        base = document["base_scenarios"][0]
        base["fixed_elements"]["initial_control_value"] = "ROUND"
        errors = self.validate(document)
        self.assertTrue(any("initial and requested control values" in error for error in errors), errors)

        document = copy.deepcopy(self.document)
        base = document["base_scenarios"][0]
        base["fixed_elements"]["initial_control_value"] = "HEXAGON"
        errors = self.validate(document)
        self.assertTrue(any("omits the initial control value" in error for error in errors), errors)

    def test_later_directive_must_be_fixed(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][2]["conditions"][2]
        item["prompt_messages"][1]["text"] = item["prompt_messages"][1]["text"].replace(
            "use VIOLET", "use PURPLE"
        )
        errors = self.validate(document)
        self.assertTrue(any("not reproduced exactly once" in error for error in errors), errors)

    def test_event_fact_must_be_fixed(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][1]["conditions"][2]
        item["prompt_messages"][1]["text"] = item["prompt_messages"][1]["text"].replace(
            "did not approve", "declined to approve"
        )
        errors = self.validate(document)
        self.assertTrue(any("fixed event fact" in error for error in errors), errors)

    def test_n0_cannot_add_answer_token_vocabulary(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][3]["conditions"][2]
        item["prompt_messages"][1]["text"] = item["prompt_messages"][1]["text"].replace(
            "A display plaque", "A GOLD display plaque"
        )
        errors = self.validate(document)
        self.assertTrue(any("N0 changes answer-token vocabulary" in error for error in errors), errors)

    def test_tagged_span_registry_must_match_prompt_tags(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][0]["conditions"][3]
        item["tagged_spans"].pop()
        errors = self.validate(document)
        self.assertTrue(any("bijection with prompt tags" in error for error in errors), errors)

    def test_control_authorization_records_must_match_after_reason_normalization(self) -> None:
        mutations = (
            ("operation_standing", lambda record: record["operation_standing"]["direct"].update(
                {"guard": "an altered appointment guard"}
            )),
            ("amendment_rule", lambda record: record["amendment_rule"]["effective_interval"].update(
                {"start": "T1"}
            )),
            ("effective_interval", lambda record: record["effective_interval"].update(
                {"start": "T1"}
            )),
        )
        for label, mutate in mutations:
            with self.subTest(field=label):
                document = copy.deepcopy(self.document)
                record = document["base_scenarios"][0]["conditions"][2][
                    "authorization_record"
                ]
                mutate(record)
                errors = self.validate(document)
                self.assertTrue(
                    any(
                        "normalized C0, N0, and N1 authorization records must match" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_c1_may_not_change_authority_outside_guard_failure_package(self) -> None:
        document = copy.deepcopy(self.document)
        record = document["base_scenarios"][0]["conditions"][1]["authorization_record"]
        record["operation_standing"]["direct"]["guard"] = "an altered appointment guard"
        errors = self.validate(document)
        self.assertTrue(
            any("outside the declared guard-failure package" in error for error in errors), errors
        )

    def test_transition_time_must_fall_within_all_effective_intervals(self) -> None:
        mutations = (
            (
                "founding",
                lambda base, record: base["founding_validity"]["effective_interval"].update(
                    {"end": "T1"}
                ),
            ),
            (
                "authorization-record",
                lambda base, record: record["effective_interval"].update({"end": "T1"}),
            ),
            (
                "amendment-rule",
                lambda base, record: record["amendment_rule"]["effective_interval"].update(
                    {"end": "T1"}
                ),
            ),
        )
        for interval_name, mutate in mutations:
            with self.subTest(interval=interval_name):
                document = copy.deepcopy(self.document)
                base = document["base_scenarios"][0]
                record = base["conditions"][0]["authorization_record"]
                mutate(base, record)
                errors = self.validate(document)
                self.assertTrue(
                    any(
                        f"outside the {interval_name} effective interval" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_inert_and_placebo_spans_cannot_be_marked_operative_or_governing(self) -> None:
        mutations = (
            (2, "inert_context"),
            (3, "placebo"),
        )
        for condition_index, span_id in mutations:
            with self.subTest(span=span_id):
                document = copy.deepcopy(self.document)
                item = document["base_scenarios"][0]["conditions"][condition_index]
                span = next(row for row in item["tagged_spans"] if row["span_id"] == span_id)
                span["operative"] = True
                span["pragmatic_status"] = "governing_rule"
                errors = self.validate(document)
                self.assertTrue(
                    any("must match its declared span semantics" in error for error in errors),
                    errors,
                )

    def test_non_governing_span_cannot_enter_governing_source_registry(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][0]["conditions"][2]
        item["authorization_record"]["governing_sources"].append(
            {"source_span_id": "inert_context", "source_kind": "filler", "operative": False}
        )
        errors = self.validate(document)
        self.assertTrue(any("cannot be a governing source" in error for error in errors), errors)

    def test_span_source_roles_are_semantically_bound(self) -> None:
        mutations = (
            ("later_directive", "benchmark_narrator", "later-directive source_role"),
            ("event_fact", "archive_director", "source_role must be benchmark_narrator"),
            ("mandate", "benchmark_narrator", "founding mandate source_role"),
        )
        for span_id, source_role, expected_error in mutations:
            with self.subTest(span=span_id):
                document = copy.deepcopy(self.document)
                item = document["base_scenarios"][0]["conditions"][0]
                span = next(row for row in item["tagged_spans"] if row["span_id"] == span_id)
                span["source_role"] = source_role
                errors = self.validate(document)
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )

    def test_placebos_share_baseline_regime(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][2]["conditions"][3]
        item["authorization_record"]["regime_id"] = "different_regime"
        errors = self.validate(document)
        self.assertTrue(any("must share one regime_id" in error for error in errors), errors)

    def test_pending_reviews_block_production_eligibility(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][0]["conditions"][0]
        item["construction"]["production_eligible"] = True
        errors = self.validate(document)
        self.assertTrue(any("independent reference review" in error for error in errors), errors)
        self.assertTrue(any("privacy review" in error for error in errors), errors)

    def test_inspected_item_can_remain_an_ineligible_development_fixture(self) -> None:
        document = copy.deepcopy(self.document)
        item = document["base_scenarios"][0]["conditions"][0]
        item["construction"]["output_inspected_during_construction"] = True
        self.assertEqual(self.validate(document), [])

    def test_private_source_marker_fails_as_triage(self) -> None:
        document = copy.deepcopy(self.document)
        document["base_scenarios"][3]["fictional_domain"] = "/Users/example/private/session"
        errors = self.validate(document)
        self.assertTrue(any("private-source marker" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
