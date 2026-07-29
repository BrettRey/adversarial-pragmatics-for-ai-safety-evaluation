#!/usr/bin/env python3
"""Adversarial regressions for the evidentiary five-status calibration rule.

The analyser's in-memory self-tests run on synthetic vectors. These tests run
the same attacks against the committed fixture set, its real applicability map,
and its real declared uses, because the defect the external review found was a
property of the decision rule as configured, not of a toy population.

Nothing here writes a reviewer response into the repository. The synthetic
responses exist only in memory and carry the self-test response source, so the
artifact's standing claim that no genuine response exists is untouched.

Run: python3 -m unittest scripts.test_analyze_evidentiary_calibration
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import analyze_evidentiary_calibration as analyzer  # noqa: E402
import validate_evidentiary_artifacts as validation  # noqa: E402


PROCUREMENT_USE = "ea-node-calibration-procurement-v1"
PROCUREMENT_CLASS = "procurement_external_contact"


def load_fixture_configuration() -> dict[str, Any]:
    """The committed map, classifier, fixtures, and hidden key, as analysed."""
    _responses, applicability, classes, bundles, keys, manifest = (
        analyzer.load_validated_artifacts(analyzer.MATCHED / "responses")
    )
    return {
        "declared_uses": applicability["declared_uses"],
        "references": {
            case["case_id"]: validation.flat_expected(case) for case in keys["cases"]
        },
        "resolutions": {
            case["case_id"]: case["expected_conjunction_resolution"] for case in keys["cases"]
        },
        "case_classes": {
            case_id: bundle[0]["target_binding"]["asserted_action_class"]
            for case_id, bundle in bundles.items()
        },
        "case_metadata": {
            case["case_id"]: {
                "coverage_tags": case["coverage_tags"],
                "pair_id": case.get("pair_id"),
                "exposure": case.get("exposure", "blinded"),
            }
            for case in manifest["cases"]
        },
        "required_nodes": {
            action_class: set(item["required_nodes"])
            for action_class, item in classes.items()
        },
    }


class FiveStatusCalibrationTests(unittest.TestCase):
    """The external review's calibration attack, kept as a permanent regression."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_fixture_configuration()
        cls.reviewers = [f"R{index:02d}" for index in range(12)]

    def responses_from(self, transform) -> list[dict[str, Any]]:
        """Twelve reviewers on every matched case, answering by `transform`."""
        responses: list[dict[str, Any]] = []
        references = self.config["references"]
        for order, (case_id, expected) in enumerate(sorted(references.items()), start=1):
            observed = transform(expected)
            for reviewer in self.reviewers:
                responses.append(
                    analyzer.synthetic_response(
                        reviewer,
                        case_id,
                        observed,
                        presentation_order=order,
                        resolution=self.config["resolutions"][case_id],
                    )
                )
        return responses

    def analyze(self, responses: list[dict[str, Any]]) -> dict[str, Any]:
        return analyzer.analyze(
            responses,
            self.config["references"],
            self.config["case_classes"],
            self.config["required_nodes"],
            self.config["declared_uses"],
            self.config["case_metadata"],
            self.config["resolutions"],
        )

    def wrong_share(self, result: dict[str, Any], action_class: str) -> float:
        vectors = [
            vector for vector in result["node_vectors"]
            if vector["action_class"] == action_class
        ]
        wrong = sum(vector["expected"] != vector["observed"] for vector in vectors)
        return wrong / len(vectors)

    def test_blanket_not_established_cannot_pass_five_status_calibration(self) -> None:
        """Keep genuine record gaps, abstain everywhere else: this must not pass.

        This is the reviewed attack. Twelve reviewers answer all twenty-one
        matched cases, preserving every expected record gap and returning
        `not_established` for every expected support, substantive defeat, and
        conflict. Conjunction resolutions are correct, no required verdict is
        omitted, and burden and privacy fields are clean, so every directional
        error rate stays at zero. Over 96% of procurement node verdicts are
        nonetheless wrong, and the use must say so.
        """
        result = self.analyze(self.responses_from(
            lambda expected: {
                address: (status if status == "record_gap" else "not_established")
                for address, status in expected.items()
            }
        ))
        use = result["uses"][PROCUREMENT_USE]
        self.assertGreater(self.wrong_share(result, PROCUREMENT_CLASS), 0.95)
        self.assertNotEqual(use["status"], "PASS")
        self.assertEqual(use["status"], "FAIL")

        metrics = use["class_results"][PROCUREMENT_CLASS]["metrics"]
        # The directional rates are blind to this attack; that is why they were
        # never sufficient on their own.
        self.assertEqual(metrics["false_support_rate"]["decision"], analyzer.MEETS)
        self.assertEqual(metrics["false_defeat_rate"]["decision"], analyzer.MEETS)
        # The status-specific rates are what catch it.
        self.assertEqual(metrics["support_miss_rate"]["decision"], analyzer.EXCEEDS)
        self.assertEqual(metrics["substantive_defeat_miss_rate"]["decision"], analyzer.EXCEEDS)
        self.assertEqual(metrics["exact_status_discordance_rate"]["decision"], analyzer.EXCEEDS)

    def test_genuine_record_gaps_remain_correct_answers(self) -> None:
        """Abstention is penalized where evidence was available, not everywhere.

        The same population's record-gap recall is perfect, so the metric set
        does not simply punish every `record_gap` or every `not_established`.
        """
        result = self.analyze(self.responses_from(
            lambda expected: {
                address: (status if status == "record_gap" else "not_established")
                for address, status in expected.items()
            }
        ))
        metrics = result["uses"][PROCUREMENT_USE]["class_results"][PROCUREMENT_CLASS]["metrics"]
        self.assertEqual(metrics["record_gap_miss_rate"]["value"], 0.0)
        self.assertEqual(metrics["record_gap_miss_rate"]["recall"], 1.0)
        self.assertNotEqual(metrics["record_gap_miss_rate"]["decision"], analyzer.EXCEEDS)
        # And the reverse error is still caught: calling a genuine gap
        # not_established is a gap/insufficiency confusion.
        confused = self.analyze(self.responses_from(
            lambda expected: {address: "not_established" for address in expected}
        ))
        confused_metrics = confused["uses"][PROCUREMENT_USE]["class_results"][PROCUREMENT_CLASS]["metrics"]
        self.assertEqual(confused_metrics["record_gap_miss_rate"]["value"], 1.0)

    def test_perfect_agreement_is_not_refuted_by_the_new_metrics(self) -> None:
        """Reviewers who match the hidden key exactly trip no error metric.

        The fixture set is too small to demonstrate a five-percent ceiling, so
        this use is still NOT_ESTIMATED rather than PASS. The point is the
        weaker one that matters here: nothing in the strengthened rule
        manufactures a failure out of correct work.
        """
        result = self.analyze(self.responses_from(dict))
        use = result["uses"][PROCUREMENT_USE]
        self.assertEqual(use["status"], analyzer.NOT_ESTIMATED)
        metrics = use["class_results"][PROCUREMENT_CLASS]["metrics"]
        self.assertNotIn(
            "FAIL", [metric["status"] for metric in metrics.values()]
        )
        for name, metric in metrics.items():
            if name in analyzer.STATUS_MISS_METRICS.values() or name == analyzer.DISCORDANCE_METRIC:
                self.assertIn(metric["value"], (0.0, None), name)

    def test_required_node_not_estimated_blocks_use_pass(self) -> None:
        """An undecided required-node metric blocks a pass instead of sitting out.

        Under perfect agreement every decided metric meets its tolerance, so the
        only thing standing between this population and a use-level PASS is the
        set of required-node metrics the sample cannot decide. Each blocking
        entry names its node, its metric, and why.
        """
        result = self.analyze(self.responses_from(dict))
        class_result = result["uses"][PROCUREMENT_USE]["class_results"][PROCUREMENT_CLASS]
        gate = class_result["required_node_gate"]
        self.assertEqual(gate["status"], analyzer.NOT_ESTIMATED)
        self.assertGreater(gate["unmet_count"], 0)
        self.assertEqual(
            set(gate["required_nodes"]), self.config["required_nodes"][PROCUREMENT_CLASS]
        )
        self.assertNotIn("exceeds_tolerance", gate["unmet_reason_counts"])
        self.assertIn(
            "never_exercised_at_this_node", gate["unmet_reason_counts"]
        )
        for item in gate["unmet"]:
            self.assertIn(item["node_id"], self.config["required_nodes"][PROCUREMENT_CLASS])
            self.assertNotEqual(item["status"], "PASS")
        self.assertEqual(class_result["status"], analyzer.NOT_ESTIMATED)

    def test_node_metric_failure_still_fails_the_class(self) -> None:
        """A demonstrated node-level breach is a FAIL, not an abstention."""
        result = self.analyze(self.responses_from(
            lambda expected: {address: "support" for address in expected}
        ))
        use = result["uses"][PROCUREMENT_USE]
        self.assertEqual(use["status"], "FAIL")
        gate = use["class_results"][PROCUREMENT_CLASS]["required_node_gate"]
        self.assertEqual(gate["status"], "FAIL")
        self.assertIn("exceeds_tolerance", gate["unmet_reason_counts"])

    def test_confusion_matrix_covers_the_declared_statuses(self) -> None:
        """The full table is reported, including cells the sample never fills."""
        result = self.analyze(self.responses_from(dict))
        matrix = result["uses"][PROCUREMENT_USE]["class_results"][PROCUREMENT_CLASS]["status_confusion_matrix"]
        self.assertEqual(set(matrix), set(analyzer.STATUSES))
        for expected, row in matrix.items():
            self.assertEqual(set(row) - {expected}, set(), f"{expected} row: {row}")
        nodes = result["uses"][PROCUREMENT_USE]["class_results"][PROCUREMENT_CLASS]["node_status_confusion"]
        self.assertTrue(
            self.config["required_nodes"][PROCUREMENT_CLASS] <= set(nodes)
        )

    def test_every_declared_use_reports_the_same_rule(self) -> None:
        """No declared use can quietly run a weaker decision rule."""
        result = self.analyze(self.responses_from(dict))
        for use_id, use in result["uses"].items():
            self.assertIn("required node", use["rule"], use_id)
            self.assertIsNone(use["scalar_score"], use_id)
            for class_result in use["class_results"].values():
                self.assertIsNone(class_result["scalar_score"], use_id)


class ToleranceResolutionTests(unittest.TestCase):
    """Where a status ceiling comes from when the map does not declare one."""

    def setUp(self) -> None:
        self.declared = {
            "false_support_rate_max": 0.05,
            "false_defeat_rate_max": 0.05,
            "gap_defeat_confusion_rate_max": 0.10,
            "gap_insufficiency_confusion_rate_max": 0.05,
        }

    def test_declared_status_ceiling_wins(self) -> None:
        tolerances = {**self.declared, "support_miss_rate_max": 0.02}
        self.assertEqual(
            analyzer.resolve_tolerance("support_miss_rate", tolerances),
            (0.02, "declared"),
        )

    def test_undeclared_status_ceiling_takes_the_strictest_declared_one(self) -> None:
        self.assertEqual(
            analyzer.resolve_tolerance("conflict_miss_rate", self.declared),
            (0.05, "derived_strictest_declared_judgement_error_ceiling"),
        )

    def test_no_declared_judgement_ceiling_leaves_the_metric_undecidable(self) -> None:
        self.assertIsNone(
            analyzer.resolve_tolerance("conflict_miss_rate", {"median_review_minutes_max": 25})
        )
        record = analyzer.decided_metric(
            "conflict_miss_rate",
            analyzer.rate_record(0, 40),
            {"median_review_minutes_max": 25},
        )
        self.assertEqual(record["status"], analyzer.NOT_ESTIMATED)
        self.assertEqual(record["tolerance_source"], "undeclared")


class SelfTestParityTests(unittest.TestCase):
    """The in-memory self-tests the Makefile runs must also pass here."""

    def test_self_tests_pass(self) -> None:
        checks = analyzer.run_self_tests()
        self.assertGreaterEqual(len(checks), 24)


if __name__ == "__main__":
    unittest.main()
