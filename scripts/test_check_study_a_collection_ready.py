#!/usr/bin/env python3
"""Focused tests for Study A's private collection-readiness records."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_study_a_collection_ready as gate


NOW = datetime(2026, 7, 16, 16, 0, tzinfo=timezone.utc)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class InstitutionalScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config_path = self.root / "operational-config.json"
        self.evidence_directory = self.root / gate.EVIDENCE_DIRECTORY
        self.evidence_directory.mkdir()
        self.sent_request = self.evidence_directory / "sent-request.eml"
        self.sent_request.write_bytes(b"Sent scope inquiry\n" + b"q" * 600)
        self.humber_response = self.evidence_directory / "humber-response.eml"
        self.humber_response.write_bytes(b"Humber written response\n" + b"r" * 200)
        self.manifest: dict[str, object] = {"public_artifacts": {}}
        public = self.manifest["public_artifacts"]
        assert isinstance(public, dict)
        for artifact_path in gate.SCOPE_BASIS_ARTIFACTS.values():
            path = self.root / artifact_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"scope basis: {artifact_path}\n", encoding="utf-8")
            public[artifact_path] = {"sha256": digest(path), "bytes": path.stat().st_size}

    def basis_records(self) -> dict[str, object]:
        return {
            key: {"path": artifact_path, "sha256": digest(self.root / artifact_path)}
            for key, artifact_path in gate.SCOPE_BASIS_ARTIFACTS.items()
        }

    def scope_record(self, **changes: object) -> dict[str, object]:
        record: dict[str, object] = {
            "status": "no_reb_review_required",
            "authority": gate.HUMBER_SCOPE_AUTHORITY,
            "request_sent_at": "2026-07-14T12:00:00-04:00",
            "response_received_at": "2026-07-15T13:00:00-04:00",
            "determined_at": "2026-07-15T12:00:00-04:00",
            "reference_id": "Humber REB scope response 2026-07-15",
            "sent_request": {
                "path": "evidence/sent-request.eml",
                "sha256": digest(self.sent_request),
            },
            "humber_response": {
                "path": "evidence/humber-response.eml",
                "sha256": digest(self.humber_response),
            },
            "scope_basis_artifacts": self.basis_records(),
            "scope_basis_accurately_represented_in_sent_request": True,
            "humber_response_provenance_manually_verified": True,
            "scope_meaning_manually_reviewed": True,
            "participant_role_question_addressed_or_inapplicable": True,
            "humber_jurisdiction_question_addressed_or_inapplicable": True,
            "scope_conditions_implemented": True,
            "approval_expires_at": None,
        }
        record.update(changes)
        return record

    def validate(
        self,
        record: object,
        *,
        active_through: datetime | None = None,
    ) -> list[str]:
        errors: list[str] = []
        with (
            mock.patch.object(gate.freeze_manifest, "ROOT", self.root),
            mock.patch.object(
                gate.freeze_manifest,
                "has_symlink_component",
                side_effect=lambda path, root=self.root: False,
            ),
        ):
            gate.validate_institutional_scope(
                record,
                self.config_path,
                now=NOW,
                manifest_payload=self.manifest,
                required_active_through=active_through,
                errors=errors,
            )
        return errors

    def test_accepts_dual_evidence_no_review_record(self) -> None:
        self.assertEqual(self.validate(self.scope_record()), [])

    def test_rejects_response_changed_after_hashing(self) -> None:
        record = self.scope_record()
        self.humber_response.write_bytes(b"changed" * 30)
        self.assertTrue(any("hash does not match" in error for error in self.validate(record)))

    def test_rejects_identical_request_and_response_files(self) -> None:
        self.humber_response.write_bytes(self.sent_request.read_bytes())
        record = self.scope_record()
        self.assertTrue(any("identical bytes" in error for error in self.validate(record)))

    def test_rejects_implausibly_small_response(self) -> None:
        self.humber_response.write_bytes(b"yes")
        record = self.scope_record()
        self.assertTrue(any("implausibly small" in error for error in self.validate(record)))

    def test_rejects_evidence_path_escape(self) -> None:
        record = self.scope_record(
            humber_response={"path": "../response.eml", "sha256": "0" * 64}
        )
        self.assertTrue(any("confined" in error for error in self.validate(record)))

    def test_request_must_precede_response_and_determination(self) -> None:
        record = self.scope_record(request_sent_at="2026-07-15T14:00:00-04:00")
        errors = self.validate(record)
        self.assertTrue(any("response_received_at must follow" in error for error in errors))
        self.assertTrue(any("determined_at must follow" in error for error in errors))

    def test_manual_question_confirmations_are_exact_true(self) -> None:
        record = self.scope_record(
            participant_role_question_addressed_or_inapplicable=1,
            humber_jurisdiction_question_addressed_or_inapplicable=False,
        )
        errors = self.validate(record)
        self.assertEqual(sum("must be explicitly true" in error for error in errors), 2)
        self.assertTrue(all("hashes prove byte integrity only" in error for error in errors))

    def test_sent_request_must_be_manually_bound_to_scope_basis(self) -> None:
        record = self.scope_record(
            scope_basis_accurately_represented_in_sent_request=False
        )
        errors = self.validate(record)
        self.assertTrue(
            any(
                "scope_basis_accurately_represented_in_sent_request" in error
                for error in errors
            )
        )

    def test_scope_basis_must_match_manifest_and_current_bytes(self) -> None:
        record = self.scope_record()
        basis = record["scope_basis_artifacts"]
        assert isinstance(basis, dict)
        plan = basis["analysis_plan"]
        assert isinstance(plan, dict)
        plan["sha256"] = "0" * 64
        errors = self.validate(record)
        self.assertTrue(any("stamp-2 manifest" in error for error in errors))
        self.assertTrue(any("current artifact bytes" in error for error in errors))

    def test_reb_approval_must_cover_analysis_start(self) -> None:
        record = self.scope_record(
            status="reb_approved",
            approval_expires_at="2026-08-01T12:00:00-04:00",
        )
        errors = self.validate(
            record,
            active_through=datetime(2026, 9, 1, 16, 0, tzinfo=timezone.utc),
        )
        self.assertTrue(any("analysis_start_at" in error for error in errors))

    def test_no_review_record_forbids_approval_expiry(self) -> None:
        record = self.scope_record(approval_expires_at="2027-07-16T12:00:00-04:00")
        self.assertTrue(any("must be null" in error for error in self.validate(record)))

    def test_nested_non_objects_report_errors_without_crashing(self) -> None:
        record = self.scope_record(
            sent_request=[],
            humber_response="response",
            scope_basis_artifacts=[],
        )
        errors = self.validate(record)
        self.assertGreaterEqual(sum("must be an object" in error for error in errors), 3)


class RosterReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.config_path = self.root / "operational-config.json"
        self.registry = self.root / "private" / gate.ASSIGNMENT_REGISTRY_NAME
        self.registry.parent.mkdir()
        self.registry.write_text("person_key,rater_id,role,package_id\n", encoding="utf-8")
        self.evidence = self.root / gate.PRIVATE_EVIDENCE_DIRECTORY
        self.evidence.mkdir()
        self.review = self.evidence / gate.INVESTIGATOR_ROSTER_REVIEW_NAME
        self.payload = {
            "review_schema_version": gate.INVESTIGATOR_ROSTER_REVIEW_SCHEMA_VERSION,
            "study": "A",
            "reviewed_at": "2026-07-16T10:00:00-04:00",
            "reviewer": "Principal investigator manual roster review",
            "assignment_registry_sha256": digest(self.registry),
            "checks": {
                "unique_real_people_confirmed": True,
                "role_eligibility_confirmed": True,
                "cross_role_disjointness_confirmed": True,
            },
        }
        self.write_review()

    def write_review(self) -> None:
        self.review.write_text(json.dumps(self.payload, indent=2) + "\n", encoding="utf-8")

    def reference(self) -> dict[str, str]:
        return {
            "path": "private/evidence/investigator-roster-review.json",
            "sha256": digest(self.review),
        }

    def validate(self, reference: object | None = None) -> list[str]:
        errors: list[str] = []
        gate.validate_investigator_roster_review(
            self.reference() if reference is None else reference,
            self.config_path,
            self.registry,
            attestation_validated_at=datetime(
                2026, 7, 16, 9, 0, tzinfo=timezone.utc
            ),
            now=NOW,
            errors=errors,
        )
        return errors

    def test_accepts_hash_bound_manual_roster_review(self) -> None:
        self.assertEqual(self.validate(), [])

    def test_registry_digest_must_match_current_registry(self) -> None:
        self.registry.write_text("changed registry bytes\n", encoding="utf-8")
        self.assertTrue(any("current assignment registry" in error for error in self.validate()))

    def test_each_real_world_check_must_be_exact_true(self) -> None:
        checks = self.payload["checks"]
        assert isinstance(checks, dict)
        checks["cross_role_disjointness_confirmed"] = 1
        self.write_review()
        errors = self.validate()
        self.assertTrue(any("cross_role_disjointness_confirmed" in error for error in errors))

    def test_roster_review_must_be_json_object(self) -> None:
        self.review.write_text("[1, 2, 3]" + " " * 220, encoding="utf-8")
        errors = self.validate()
        self.assertTrue(any("must be a JSON object" in error for error in errors))


class OperationalRecordTests(unittest.TestCase):
    def test_accepts_exact_non_evidentiary_workload_estimate(self) -> None:
        errors: list[str] = []
        gate.validate_workload_estimate(
            {"minimum": 30, "maximum": 40, "basis": "planning_estimate_only"},
            errors,
        )
        self.assertEqual(errors, [])

    def test_return_channel_requires_all_security_assertions(self) -> None:
        valid = {
            "description": "Encrypted institutional file drop",
            "access_control": "Named investigator account with multifactor authentication",
            "investigator_access_only": True,
            "public_link": False,
            "not_long_term_store": True,
        }
        errors: list[str] = []
        gate.validate_return_channel(valid, errors)
        self.assertEqual(errors, [])
        invalid = dict(valid, investigator_access_only=1, public_link=0, not_long_term_store=False)
        errors = []
        gate.validate_return_channel(invalid, errors)
        self.assertEqual(sum("explicitly" in error for error in errors), 3)

    def test_config_must_be_confined_and_parent_chain_must_not_be_symlinked(self) -> None:
        with tempfile.TemporaryDirectory(dir=gate.freeze_manifest.ROOT) as temporary:
            base = Path(temporary)
            production = base / "production"
            production.mkdir()
            config = production / "operational-config.json"
            config.write_text("{}\n", encoding="utf-8")
            self.assertEqual(gate.validate_config_location(config, production), [])
            outside = base / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            self.assertTrue(any("confined" in error for error in gate.validate_config_location(outside, production)))
            real_parent = base / "real-parent"
            real_parent.mkdir()
            linked_parent = production / "linked"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            linked_config = linked_parent / "operational-config.json"
            linked_config.write_text("{}\n", encoding="utf-8")
            self.assertTrue(any("symlink" in error for error in gate.validate_config_location(linked_config, production)))

    def test_missing_and_symlinked_local_dependencies_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir=gate.freeze_manifest.ROOT) as temporary:
            directory = Path(temporary)
            source = directory / "source.md"
            source.write_text("[missing](missing.md)\n", encoding="utf-8")
            _, errors = gate.local_material_dependencies(source, source.read_text())
            self.assertTrue(any("missing local dependency" in error for error in errors))
            target = directory / "target.md"
            target.write_text("target\n", encoding="utf-8")
            linked = directory / "linked.md"
            linked.symlink_to(target)
            source.write_text("[linked](linked.md)\n", encoding="utf-8")
            _, errors = gate.local_material_dependencies(source, source.read_text())
            self.assertTrue(any("symlinked local dependency" in error for error in errors))


class TagTimingTests(unittest.TestCase):
    @staticmethod
    def result(stdout: bytes = b"", returncode: int = 0) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess([], returncode, stdout, b"")

    def git_results(self, tagger_at: str) -> list[subprocess.CompletedProcess[bytes]]:
        return [
            self.result(),
            self.result(b"abc\n"),
            self.result(b"abc\n"),
            self.result(b"tag\n"),
            self.result(b"study-a-freeze|tag\n"),
            self.result((tagger_at + "\n").encode()),
        ]

    def test_annotated_tag_must_postdate_scope_determination(self) -> None:
        determined = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
        with mock.patch.object(
            gate, "git", side_effect=self.git_results("2026-07-15T11:00:00-04:00")
        ):
            errors = gate.check_annotated_tag_at_head(
                "study-a-freeze", after_scope_recorded_at=determined
            )
        self.assertTrue(any("created after" in error for error in errors))

    def test_later_annotated_tag_passes_timing_check(self) -> None:
        determined = datetime(2026, 7, 15, 16, 0, tzinfo=timezone.utc)
        with mock.patch.object(
            gate, "git", side_effect=self.git_results("2026-07-15T13:00:00-04:00")
        ):
            errors = gate.check_annotated_tag_at_head(
                "study-a-freeze", after_scope_recorded_at=determined
            )
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
