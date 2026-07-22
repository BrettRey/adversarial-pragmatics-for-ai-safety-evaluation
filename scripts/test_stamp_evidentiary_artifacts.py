"""Tests for the freeze guard on the evidentiary binding stamper.

The stamper rewrites the hashes that bind the applicability map, fixtures, and
hidden reference key together. That is legitimate only while the set is still
pre-review, so the guard must refuse once a genuine reviewer response exists,
once an unblinding record exists, or once the declared boundary has passed.

Every case here runs against a temporary directory. Nothing writes a reviewer
response into the repository, because a file claiming to be a genuine response
would contradict the artifact's own standing claim that none exist.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts import stamp_evidentiary_artifacts as stamper


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
        self.write_package(self.boundary)
        patches = {
            "MATCHED": self.matched,
            "RESPONSES": self.responses,
        }
        for name, value in patches.items():
            patcher = mock.patch.object(stamper, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_package(self, boundary: datetime) -> None:
        (self.matched / "reviewer-package.json").write_text(
            json.dumps({"reference_key_unblinding_not_before": iso(boundary)}),
            encoding="utf-8",
        )

    def write_response(self, source: str) -> None:
        self.responses.mkdir(parents=True, exist_ok=True)
        (self.responses / "r1.json").write_text(
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
        self.write_package(datetime.now(timezone.utc) - timedelta(seconds=1))
        with self.assertRaises(stamper.StampError) as caught:
            stamper.guard_pre_review(stamper.Tree())
        self.assertIn("has passed", str(caught.exception))

    def test_repository_tree_is_never_touched(self) -> None:
        # The guard reads only the patched paths, so a real responses directory
        # is neither created nor consulted during these tests.
        self.assertFalse((stamper.ROOT / "assurance" / "evidentiary" / "matched-cases" / "responses").exists())


if __name__ == "__main__":
    unittest.main()
