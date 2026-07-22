#!/usr/bin/env python3
"""Mutation tests for the cross-file Study B excellence validator."""

from __future__ import annotations

import copy
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VALIDATOR_PATH = SCRIPTS / "validate_study_b_excellence.py"


def load_validator_module():
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(
            "study_b_excellence_validator", VALIDATOR_PATH
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("could not load Study B excellence validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


VALIDATOR = load_validator_module()


class StudyBExcellenceValidatorTests(unittest.TestCase):
    def write_csv(
        self,
        directory: str,
        name: str,
        fields: list[str],
        rows: list[dict[str, str]],
    ) -> Path:
        path = Path(directory) / name
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def target_schedule_rows(self) -> tuple[list[str], list[dict[str, str]]]:
        fields, rows = VALIDATOR.load_csv(VALIDATOR.DEFAULT_COUNTERBALANCE)
        rows = copy.deepcopy(rows)
        position_cycle = ["mandate_first", "directive_first"]
        marker_cycle = ["implicit_operativity", "neutral_status_header"]
        for index, row in enumerate(rows):
            row["split"] = "untouched_target"
            row["balance_block"] = "TARGET-A"
            row["freeze_status"] = "frozen_before_outputs"
            row["critical_clause_position"] = position_cycle[index % 2]
            row["marker_variant"] = marker_cycle[(index // 2) % 2]
            row["generation_order_slot"] = str((index % 4) + 1)
        return fields, rows

    def test_committed_artifacts_pass(self) -> None:
        errors = []
        errors.extend(VALIDATOR.coverage_errors(VALIDATOR.DEFAULT_COVERAGE))
        errors.extend(
            VALIDATOR.pair_errors(VALIDATOR.DEFAULT_PAIRS, VALIDATOR.DEFAULT_ITEMS)
        )
        errors.extend(
            VALIDATOR.claim_errors(
                VALIDATOR.DEFAULT_CLAIMS, VALIDATOR.DEFAULT_CLAIM_SCHEMA
            )
        )
        lineage_errors, production_open = VALIDATOR.lineage_errors(
            VALIDATOR.DEFAULT_LINEAGE, VALIDATOR.DEFAULT_ITEMS
        )
        errors.extend(lineage_errors)
        errors.extend(
            VALIDATOR.counterbalance_errors(
                VALIDATOR.DEFAULT_COUNTERBALANCE,
                VALIDATOR.DEFAULT_ITEMS,
                production_open,
            )
        )
        errors.extend(
            VALIDATOR.shortcut_errors(VALIDATOR.DEFAULT_SHORTCUTS, production_open)
        )
        self.assertEqual(errors, [])

    def test_pooled_behavioural_gate_is_rejected(self) -> None:
        payload = VALIDATOR.load_json(VALIDATOR.DEFAULT_CLAIMS)
        behavioural = next(
            claim for claim in payload["claims"] if claim["claim_id"] == "APB_BEH_001"
        )
        behavioural["declaration"]["tolerance"]["success_threshold"] = (
            "The shift wins on 75% of untouched target bases."
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "claims.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            errors = VALIDATOR.claim_errors(path, VALIDATOR.DEFAULT_CLAIM_SCHEMA)
        self.assertTrue(any("pooled compensatory base gate" in error for error in errors), errors)

    def test_uncertainty_cannot_be_primary_coverage(self) -> None:
        fields, rows = VALIDATOR.load_csv(VALIDATOR.DEFAULT_COVERAGE)
        rows = copy.deepcopy(rows)
        rows[0]["criterion_uncertainty_role"] = "primary"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "coverage.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            errors = VALIDATOR.coverage_errors(path)
        self.assertTrue(any("cannot be a primary estimand" in error for error in errors), errors)

    def test_content_hash_detects_fixture_change(self) -> None:
        document = VALIDATOR.load_json(VALIDATOR.DEFAULT_ITEMS)
        document["base_scenarios"][0]["conditions"][0]["prompt_messages"][1]["text"] += (
            " Changed."
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "items.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            errors, _ = VALIDATOR.lineage_errors(VALIDATOR.DEFAULT_LINEAGE, path)
        self.assertTrue(any("content_hash does not bind" in error for error in errors), errors)

    def test_overt_markers_cannot_enter_target_schedule(self) -> None:
        fields, rows = VALIDATOR.load_csv(VALIDATOR.DEFAULT_COUNTERBALANCE)
        rows = copy.deepcopy(rows)
        rows[0]["split"] = "untouched_target"
        rows[0]["freeze_status"] = "frozen_before_outputs"
        rows[0]["generation_order_slot"] = "1"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "counterbalance.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            errors = VALIDATOR.counterbalance_errors(
                path, VALIDATOR.DEFAULT_ITEMS, production_open=False
            )
        self.assertTrue(any("overt-marker items cannot enter" in error for error in errors), errors)

    def test_planned_shortcut_probe_blocks_production(self) -> None:
        errors = VALIDATOR.shortcut_errors(
            VALIDATOR.DEFAULT_SHORTCUTS, production_open=True
        )
        self.assertTrue(any("production is open before" in error for error in errors), errors)

    def test_target_balance_dimension_cannot_collapse_within_block(self) -> None:
        fields, rows = self.target_schedule_rows()
        for row in rows:
            row["source_name_variant"] = "collapsed_source_variant"
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "counterbalance.csv", fields, rows)
            errors = VALIDATOR.counterbalance_errors(
                path, VALIDATOR.DEFAULT_ITEMS, production_open=False
            )
        self.assertTrue(
            any("source_name_variant" in error and "collapses" in error for error in errors),
            errors,
        )

    def test_target_balance_block_requires_equal_condition_counts(self) -> None:
        fields, rows = self.target_schedule_rows()
        rows.pop()
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "counterbalance.csv", fields, rows)
            errors = VALIDATOR.counterbalance_errors(
                path, VALIDATOR.DEFAULT_ITEMS, production_open=False
            )
        self.assertTrue(any("equal counts" in error for error in errors), errors)

    def test_pair_manifest_rejects_duplicate_comparison_class(self) -> None:
        fields, rows = VALIDATOR.load_csv(VALIDATOR.DEFAULT_PAIRS)
        rows = copy.deepcopy(rows)
        duplicate = copy.deepcopy(rows[0])
        duplicate["pair_id"] = "APB-CP01-C0-C1-DUPLICATE"
        rows.append(duplicate)
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "pairs.csv", fields, rows)
            errors = VALIDATOR.pair_errors(path, VALIDATOR.DEFAULT_ITEMS)
        self.assertTrue(
            any("exactly one" in error and "found 2" in error for error in errors),
            errors,
        )

    def test_pair_manifest_rejects_missing_comparison_class(self) -> None:
        fields, rows = VALIDATOR.load_csv(VALIDATOR.DEFAULT_PAIRS)
        rows = [row for row in rows if row["pair_id"] != "APB-CP01-C0-N0"]
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_csv(directory, "pairs.csv", fields, rows)
            errors = VALIDATOR.pair_errors(path, VALIDATOR.DEFAULT_ITEMS)
        self.assertTrue(
            any("exactly one" in error and "found 0" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
