"""Tests for evidentiary stamping and projective-claim anchoring.

The stamper rewrites the hashes that bind the applicability map, fixtures, and
hidden reference key together. That is legitimate only while the set is still
pre-review, so write mode must refuse once a genuine reviewer response exists,
once an unblinding record exists, or once the Git-anchored boundary has passed.
Read-only check mode must remain available forever.

Every case here runs against a temporary directory. Nothing writes a reviewer
response into the repository, because a file claiming to be a genuine response
would contradict the artifact's own standing claim that none exist.
"""

from __future__ import annotations

import copy
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import stamp_evidentiary_artifacts as stamper
from scripts import validate_claim_register as claim_validator


def iso(moment: datetime) -> str:
    return moment.isoformat().replace("+00:00", "Z")


class FreezeGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.matched = root / "matched-cases"
        self.responses = self.matched / "responses"
        self.matched.mkdir(parents=True)
        self.boundary = datetime.now(timezone.utc) + timedelta(days=30)
        self.anchored_boundary = self.boundary
        self.write_package(self.boundary)
        patches = {
            "MATCHED": self.matched,
            "RESPONSES": self.responses,
        }
        for name, value in patches.items():
            patcher = mock.patch.object(stamper, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        anchor_patcher = mock.patch.object(
            stamper,
            "anchored_unblinding_boundary",
            side_effect=lambda: self.anchored_boundary,
        )
        anchor_patcher.start()
        self.addCleanup(anchor_patcher.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_package(self, boundary: datetime) -> None:
        (self.matched / "reviewer-package.json").write_text(
            json.dumps({"reference_key_unblinding_not_before": iso(boundary)}),
            encoding="utf-8",
        )

    def write_response(self, source: str, relative: str = "r1.json") -> None:
        path = self.responses / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"response_source": source}), encoding="utf-8"
        )

    def test_allows_stamping_before_any_review(self) -> None:
        stamper.guard_pre_review(stamper.Tree())

    def test_allows_stamping_when_response_dir_is_empty(self) -> None:
        self.responses.mkdir(parents=True)
        stamper.guard_pre_review(stamper.Tree())

    def test_refuses_once_a_genuine_response_exists(self) -> None:
        self.write_response("genuine_reviewer")
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("genuine reviewer response", str(caught.exception))

    def test_nested_genuine_response_blocks_write_mode(self) -> None:
        self.write_response("genuine_reviewer", "nested/genuine.json")
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("genuine reviewer response", str(caught.exception))

    def test_ignores_responses_not_marked_genuine(self) -> None:
        # Only genuine responses close the set; other payloads are not evidence
        # that a reviewer acted on the material.
        self.write_response("in_memory_self_test_only")
        stamper.guard_pre_review(stamper.Tree())

    def test_refuses_once_an_unblinding_record_exists(self) -> None:
        hidden = self.matched / "hidden"
        hidden.mkdir(parents=True)
        (hidden / "unblinding-record.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("unblinding record", str(caught.exception))

    def test_refuses_once_the_boundary_has_passed(self) -> None:
        past = datetime.now(timezone.utc) - timedelta(seconds=1)
        self.write_package(past)
        self.anchored_boundary = past
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("has passed", str(caught.exception))

    def test_local_boundary_edit_cannot_reopen_the_git_anchor(self) -> None:
        self.write_package(datetime.now(timezone.utc) + timedelta(days=3650))
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("differs from the earliest Git-anchored boundary", str(caught.exception))

    def test_repository_tree_is_never_touched(self) -> None:
        # The guard reads only the patched paths, so a real responses directory
        # is neither created nor consulted during these tests.
        self.assertFalse((stamper.ROOT / "assurance" / "evidentiary" / "matched-cases" / "responses").exists())


class StampModeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ea = self.root / "assurance" / "evidentiary"
        shutil.copytree(stamper.EA, self.ea)
        self.matched = self.ea / "matched-cases"
        self.responses = self.matched / "responses"
        package = json.loads((self.matched / "reviewer-package.json").read_text())
        self.boundary = datetime.fromisoformat(
            package["reference_key_unblinding_not_before"].replace("Z", "+00:00")
        )
        patches = {
            "ROOT": self.root,
            "EA": self.ea,
            "MATCHED": self.matched,
            "RESPONSES": self.responses,
        }
        for name, value in patches.items():
            patcher = mock.patch.object(stamper, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        anchor_patcher = mock.patch.object(
            stamper, "anchored_unblinding_boundary", return_value=self.boundary
        )
        anchor_patcher.start()
        self.addCleanup(anchor_patcher.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_package_boundary(self, boundary: datetime) -> None:
        path = self.matched / "reviewer-package.json"
        package = json.loads(path.read_text(encoding="utf-8"))
        package["reference_key_unblinding_not_before"] = iso(boundary)
        path.write_bytes(stamper.canonical_bytes(package))

    def snapshot(self) -> dict[str, bytes]:
        return {
            str(path.relative_to(self.root)): path.read_bytes()
            for path in self.root.rglob("*")
            if path.is_file()
        }

    def test_check_mode_remains_available_after_freeze_and_is_read_only(self) -> None:
        self.write_package_boundary(datetime.now(timezone.utc) - timedelta(days=1))
        nested = self.responses / "nested" / "self-test.json"
        nested.parent.mkdir(parents=True)
        nested.write_bytes(b'{"response_source":"in_memory_self_test_only"}')
        before = self.snapshot()
        with redirect_stdout(io.StringIO()):
            result = stamper.stamp(check_only=True)
        self.assertEqual(result, 0)
        self.assertEqual(self.snapshot(), before)

    def test_stamper_never_rewrites_response_data(self) -> None:
        nested = self.responses / "nested" / "self-test.json"
        nested.parent.mkdir(parents=True)
        response_bytes = b'{"response_source": "in_memory_self_test_only"}'
        nested.write_bytes(response_bytes)
        with redirect_stdout(io.StringIO()):
            result = stamper.stamp(check_only=False)
        self.assertEqual(result, 0)
        self.assertEqual(nested.read_bytes(), response_bytes)
        self.assertNotIn(nested, stamper.artifact_json_paths())


class ClaimAnchoringRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = claim_validator.load_json(claim_validator.DEFAULT_SCHEMA)

    def test_explicit_outcome_selected_population_is_not_claimed_as_prospective(self) -> None:
        fixture = claim_validator.load_json(
            claim_validator.ROOT
            / "reviews/code-review-20260729/raw/posthoc-claim-bypass.json"
        )
        issues = claim_validator.validate_payload(fixture, self.schema)
        self.assertTrue(issues)
        self.assertTrue(any("target_selection" in issue for issue in issues))
        self.assertTrue(any("repository_anchor" in issue for issue in issues))

    def test_mutated_proposal_cannot_borrow_a_committed_fixture_timing(self) -> None:
        payload = copy.deepcopy(claim_validator.load_json(claim_validator.DEFAULT_VALID))
        payload["claim_id"] = "POSTHOC_BYPASS_001"
        payload["declaration"]["population"] = (
            "Cases selected after outcome inspection for agreement with the desired direction"
        )
        payload["declaration"]["conditions"] = [
            "Discordant target cases are excluded once their outcomes are known"
        ]
        payload["declaration"]["projected_outcome"] = (
            "The retained subset exhibits the desired effect"
        )
        payload["provenance"]["declared_by"] = "analyst after target inspection"
        issues = claim_validator.validate_payload(payload, self.schema)
        self.assertTrue(any("unchanged proposed claim anchored" in issue for issue in issues))

    def test_structured_target_selection_is_executable(self) -> None:
        selection = {
            "records_pointer": "/items",
            "item_id_path": ["item_id"],
            "include_all": [
                {"field_path": ["eligible"], "operator": "equals", "value": True}
            ],
            "exclude_any": [
                {"field_path": ["outcome_known"], "operator": "equals", "value": True}
            ],
        }
        inventory = {
            "items": [
                {"item_id": "predeclared-a", "eligible": True, "outcome_known": False},
                {"item_id": "posthoc-b", "eligible": True, "outcome_known": True},
                {"item_id": "ineligible-c", "eligible": False, "outcome_known": False},
            ]
        }
        selected = claim_validator.evaluate_selection(
            selection, json.dumps(inventory).encode("utf-8")
        )
        self.assertEqual(selected, ["predeclared-a"])

    def test_frozen_claim_requires_the_exact_pre_freeze_git_digest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory_path = root / "targets.json"
            inventory_path.write_text(
                json.dumps(
                    {
                        "items": [
                            {"item_id": "target-a", "eligible": True},
                            {"item_id": "target-b", "eligible": False},
                        ]
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            claim = copy.deepcopy(claim_validator.load_json(claim_validator.DEFAULT_VALID))
            claim["claim_id"] = "ANCHORED_TEST_001"
            claim["declaration"]["target_selection"] = {
                "rule_language": "projective-selection-v1",
                "inventory_path": "targets.json",
                "inventory_sha256": claim_validator.sha256_bytes(
                    inventory_path.read_bytes()
                ),
                "records_pointer": "/items",
                "item_id_path": ["item_id"],
                "include_all": [
                    {"field_path": ["eligible"], "operator": "equals", "value": True}
                ],
                "exclude_any": [],
                "selected_item_ids": ["target-a"],
            }
            claim["provenance"]["source_files"] = ["claims.json"]
            claim_path = root / "claims.json"
            claim_path.write_text(json.dumps(claim, indent=2) + "\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(
                ["git", "config", "user.email", "regression@example.invalid"],
                cwd=root,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Regression Test"], cwd=root, check=True
            )
            subprocess.run(["git", "add", "claims.json", "targets.json"], cwd=root, check=True)
            subprocess.run(
                ["git", "commit", "-q", "-m", "anchor proposed claim"],
                cwd=root,
                check=True,
            )
            commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=root,
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

            claim["status"] = "frozen"
            claim["provenance"]["declaration_timing"] = (
                "repository_anchored_target_chronology_not_established"
            )
            claim["provenance"]["repository_anchor"] = {
                "repository": "git",
                "commit": commit,
                "claim_path": "claims.json",
                "claim_sha256": claim_validator.anchored_claim_digest(claim),
            }
            with mock.patch.object(claim_validator, "ROOT", root):
                issues = claim_validator.validate_payload(claim, self.schema)
                self.assertEqual(issues, [])
                claim["declaration"]["target_selection"]["selected_item_ids"] = [
                    "target-b"
                ]
                issues = claim_validator.validate_payload(claim, self.schema)
            self.assertTrue(any("current claim does not match" in issue for issue in issues))
            self.assertTrue(any("executable selection result" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
