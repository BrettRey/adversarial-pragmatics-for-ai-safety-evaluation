#!/usr/bin/env python3
"""Focused fail-closed tests for the naturalistic-corpus v2 validator."""

from __future__ import annotations

import base64
import csv
import hashlib
import hmac
import importlib.util
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_naturalistic_pragmatic_corpus.py"
PRIVATE = ROOT / "private"
KEY = b"0123456789abcdef0123456789abcdef"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("naturalistic_v2_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load v2 validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR_MODULE = load_validator_module()


def keyed_ref(prefix: str, domain: str, value: str, length: int) -> str:
    digest = hmac.new(KEY, f"{domain}\0{value}".encode("utf-8"), hashlib.sha256)
    return f"{prefix}-{digest.hexdigest()[:length].upper()}"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o600)


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    write_text(path, "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    path.chmod(0o600)


def make_dirs_private(root: Path) -> None:
    for current, directories, _files in os.walk(root):
        Path(current).chmod(0o700)
        for directory in directories:
            (Path(current) / directory).chmod(0o700)


def inventory(root: Path, *, exclude: set[str] | None = None) -> list[dict[str, object]]:
    excluded = exclude or set()
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative in excluded or not path.is_file():
            continue
        rows.append(
            {
                "relative_path": relative,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "byte_size": path.stat().st_size,
                "mode": f"{path.stat().st_mode & 0o777:04o}",
            }
        )
    return rows


class V2ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        token = secrets.token_hex(6)
        self.corpus = PRIVATE / "discovery" / f"validator-v2-test-{token}"
        self.restricted = PRIVATE / "restricted" / f"validator-v2-test-{token}"
        self.corpus.mkdir(parents=True, mode=0o700)
        self.restricted.mkdir(parents=True, mode=0o700)
        self.source = ROOT / "data" / "fixtures" / "naturalistic-corpus" / "codex" / "root-session.jsonl"
        self.assertTrue(self.source.is_file())
        session_id = "raw-session-one"
        trigger_node_id = "node-trigger-one"
        feedback_node_id = "node-feedback-one"
        session_value = f"codex|{session_id}"
        session_ref = keyed_ref("SES2", "session", session_value, 20)
        candidate_id = keyed_ref(
            "NPE2",
            "candidate",
            f"{session_value}|{trigger_node_id}|{feedback_node_id}|likely_pragmatic_failure",
            24,
        )
        source_ref = keyed_ref("SRC2", "source", f"codex|{self.source}", 20)
        candidate = {
            "candidate_id": candidate_id,
            "session_ref": session_ref,
            "source": "codex",
            "session_mode": "cli",
            "month": "2026-07",
            "candidate_class": "likely_pragmatic_failure",
            "candidate_score": 3,
            "evidence_strength": "moderate",
            "primary_phenomenon": "negative_constraint_persistence",
            "evidence_signals": [{"signal": "instruction_repetition", "weight": 3}],
            "pragmatic_load_signals": [],
            "alternative_explanations": [
                "insufficient_evidence",
                "reasonable_competing_reading",
            ],
            "compaction_before": False,
            "tool_event_count": 1,
            "tool_action_classes": ["artifact_read"],
            "content_withheld_fields": [],
            "redaction_counts": {"local_path": 1},
            "privacy_disposition": "internal_review_only",
            "reconstruction_status": "automatic_minimization",
            "review_selected": True,
        }
        review = {key: value for key, value in candidate.items() if key != "review_selected"}
        review.update(
            {
                "preceding_context": [],
                "triggering_request": "please return the requested token.",
                "model_visible_response": "the response omitted it.",
                "user_followup": "that missed the requested token.",
                "immediate_model_response": "fixed: output blue.",
            }
        )
        review["text_char_count"] = sum(
            len(review[field])
            for field in (
                "triggering_request",
                "model_visible_response",
                "user_followup",
                "immediate_model_response",
            )
        )
        self.candidate = candidate
        self.review = review
        write_text(
            self.corpus / "README.md",
            "# Privacy-Minimized Naturalistic Pragmatic Extremes Corpus\n\n"
            "This corpus is pseudonymized, not anonymized or public-safe.\n",
        )
        write_jsonl(self.corpus / "candidate-index.jsonl", [candidate])
        write_jsonl(self.corpus / "review-corpus.jsonl", [review])
        write_json(
            self.corpus / "corpus-manifest.json",
            {
                "schema_version": 2,
                "kind": "privacy_minimized_naturalistic_pragmatic_extremes_corpus",
                "privacy_model_version": 1,
                "restricted_linkage_separate": True,
                "session_count": 1,
                "candidate_count": 1,
                "review_corpus_count": 1,
            },
        )
        write_json(
            self.corpus / "reports" / "retrieval-audit.json",
            {"external_api_calls": False, "parse_errors": [], "retrieved": 1},
        )
        write_text(self.corpus / "reports" / "corpus-profile.md", "# Aggregate profile\n\nOne row.\n")
        write_json(
            self.corpus / "reports" / "privatization-audit.json",
            {
                "kind": "naturalistic_corpus_privatization_audit",
                "before": {"derivatives": 4},
                "after": {"derivatives": 3},
            },
        )
        residual_audit = {
            "kind": "naturalistic_corpus_residual_risk_audit",
            "residual_identifier_counts": {
                name: {"matches": 0, "records": 0, "fields": {}}
                for name in (
                    "absolute_or_home_path",
                    "email",
                    "phone",
                    "url",
                    "handle",
                    "credential_context",
                    "private_key",
                    "active_markup",
                    "network_code",
                    "correspondence_header",
                    "code_fence",
                    "honorific_name",
                    "organization_pattern",
                    "proper_name_pattern",
                )
            },
        }
        write_json(self.corpus / "reports" / "residual-risk-audit.json", residual_audit)
        payload = base64.b64encode(
            json.dumps([review], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).decode("ascii")
        script_nonce = "MDEyMzQ1Njc4OUFCQ0RFRjAxMjM0"
        style_nonce = "RkVEQ0JBOTg3NjU0MzIxMEZFRENC"
        html = f"""<!doctype html>
<html><head><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'nonce-{script_nonce}'; style-src 'nonce-{style_nonce}'; connect-src 'none'; img-src 'none'; object-src 'none'; frame-src 'none'; child-src 'none'; form-action 'none'; base-uri 'none'; font-src 'none'; media-src 'none'; worker-src 'none'; manifest-src 'none'">
<style nonce="{style_nonce}">body{{font-family:sans-serif}}</style></head>
<body><template id="candidate-data" data-encoding="base64">{payload}</template><main id="app"></main>
<script nonce="{script_nonce}">const node=document.getElementById('candidate-data');const rows=JSON.parse(atob(node.textContent));node.remove();document.getElementById('app').textContent=String(rows.length);</script>
</body></html>"""
        write_text(self.corpus / "review" / "index.html", html)
        write_text(
            self.corpus / "review" / "README.md",
            "# Private Pragmatic-Extremes Review\n\n"
            "This private review is not anonymized. Decisions remain in memory only.\n",
        )

        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        (self.restricted / "id-key.bin").write_bytes(KEY)
        (self.restricted / "id-key.bin").chmod(0o600)
        write_csv(
            self.restricted / "source-linkage.csv",
            [
                "candidate_id",
                "session_ref",
                "source",
                "source_ref",
                "raw_path",
                "session_id",
                "trigger_turn_index",
                "feedback_turn_index",
                "trigger_node_id",
                "feedback_node_id",
                "start_line",
                "end_line",
            ],
            [
                {
                    "candidate_id": candidate["candidate_id"],
                    "session_ref": candidate["session_ref"],
                    "source": "codex",
                    "source_ref": source_ref,
                    "raw_path": str(self.source),
                    "session_id": session_id,
                    "trigger_turn_index": 1,
                    "feedback_turn_index": 2,
                    "trigger_node_id": trigger_node_id,
                    "feedback_node_id": feedback_node_id,
                    "start_line": 1,
                    "end_line": 2,
                }
            ],
        )
        write_csv(
            self.restricted / "source-fingerprints.csv",
            ["source_ref", "source", "raw_path", "source_sha256", "byte_size"],
            [
                {
                    "source_ref": source_ref,
                    "source": "codex",
                    "raw_path": str(self.source),
                    "source_sha256": digest,
                    "byte_size": self.source.stat().st_size,
                }
            ],
        )
        make_dirs_private(self.corpus)
        make_dirs_private(self.restricted)
        privatization_path = self.corpus / "reports" / "privatization-audit.json"
        privatization = json.loads(privatization_path.read_text(encoding="utf-8"))
        privatization["transformations"] = {
            "keyed_hmac_candidate_ids": 1,
            "keyed_hmac_session_ids": 1,
            "raw_episode_derivatives_retained": 0,
            "direct_provenance_rows_moved_to_restricted_vault": 1,
            "manual_controlled_reconstruction_rows": 0,
        }
        corpus_inventory = inventory(
            self.corpus, exclude={"reports/privatization-audit.json"}
        )
        restricted_inventory = inventory(self.restricted)
        privatization["after"] = {
            "corpus_file_inventory": corpus_inventory,
            "restricted_file_inventory": restricted_inventory,
            "duplicate_groups": [],
            "residual_identifier_counts": residual_audit["residual_identifier_counts"],
            "reviewer_finalized": True,
            "aggregate_privacy_scan": {
                "kind": "aggregate_naturalistic_corpus_privacy_audit",
                "audit_policy": {
                    "input_paths_or_unrecognized_filenames_in_report": False,
                    "matched_values_or_excerpts_in_report": False,
                    "symlinks_followed": False,
                },
                "aggregate_findings": {
                    "direct_identifiers": {
                        "match_count": 0,
                        "affected_value_count": 0,
                    },
                    "high_confidence_secrets": {
                        "match_count": 0,
                        "affected_value_count": 0,
                    },
                    "active_markup_network_primitives": {
                        "match_count": 0,
                        "affected_value_count": 0,
                    },
                },
                "inventory": {
                    "regular_file_count": len(corpus_inventory) + len(restricted_inventory),
                    "owner_only_file_count": len(corpus_inventory) + len(restricted_inventory),
                    "non_owner_only_file_count": 0,
                    "wrong_owner_file_count": 0,
                    "symlink_count": 0,
                    "restricted_key_file_count": 1,
                    "restricted_32_byte_key_file_count": 1,
                },
                "duplication": {
                    "byte_identical_group_count": 0,
                    "hardlink_group_count": 0,
                },
                "renderer_structural_totals": {
                    "candidate_data_template_count": 1,
                    "csp_authorized_script_count": 1,
                    "csp_meta_count": 1,
                    "decoded_payload_count": 1,
                    "decoded_record_count": 1,
                    "encoded_payload_count": 1,
                    "event_handler_attribute_count": 0,
                    "external_resource_attribute_count": 0,
                    "payload_decode_error_count": 0,
                    "script_closing_sequence_count": 1,
                    "script_element_count": 1,
                    "script_nonce_attribute_count": 1,
                    "style_element_count": 1,
                    "style_nonce_attribute_count": 1,
                },
            },
        }
        write_json(privatization_path, privatization)

    def tearDown(self) -> None:
        shutil.rmtree(self.corpus, ignore_errors=True)
        shutil.rmtree(self.restricted, ignore_errors=True)

    def refresh_finalized_inventory(self) -> None:
        path = self.corpus / "reports" / "privatization-audit.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        corpus_inventory = inventory(
            self.corpus, exclude={"reports/privatization-audit.json"}
        )
        restricted_inventory = inventory(self.restricted)
        after = value["after"]
        after["corpus_file_inventory"] = corpus_inventory
        after["restricted_file_inventory"] = restricted_inventory
        scan_inventory = after["aggregate_privacy_scan"]["inventory"]
        regular_file_count = len(corpus_inventory) + len(restricted_inventory)
        scan_inventory["regular_file_count"] = regular_file_count
        scan_inventory["owner_only_file_count"] = regular_file_count
        write_json(path, value)

    def contextual_audit(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "kind": "naturalistic_corpus_contextual_privacy_audit",
            "generated_at": "2026-07-16T12:00:00Z",
            "corpus_version": 2,
            "sample_size": 1,
            "sampling_method": {"seed_domain": "privacy-context-v2"},
            "disposition_counts": {},
            "manual_pattern_review": {},
            "overlapping_row_counts": {},
            "interpretation_codes": ["internal_only"],
        }

    def run_validator(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--corpus-dir",
                str(self.corpus),
                "--restricted-dir",
                str(self.restricted),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_valid_minimized_package_passes(self) -> None:
        completed = self.run_validator()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_source_integrity_reader_is_strict(self) -> None:
        with tempfile.TemporaryDirectory(dir=PRIVATE) as temporary:
            root = Path(temporary)
            malformed = root / "malformed.jsonl"
            malformed.write_text('{"valid": true}\nnot-json\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid JSON"):
                VALIDATOR_MODULE.strict_jsonl_object_count(malformed)

            invalid_utf8 = root / "invalid-utf8.jsonl"
            invalid_utf8.write_bytes(b'{"valid": true}\n\xff\n')
            with self.assertRaises(UnicodeDecodeError):
                VALIDATOR_MODULE.strict_jsonl_object_count(invalid_utf8)

    def test_direct_identifier_fails_closed(self) -> None:
        row = dict(self.review)
        row["user_followup"] = "contact person@example.invalid"
        row["text_char_count"] = sum(
            len(row[field])
            for field in (
                "triggering_request",
                "model_visible_response",
                "user_followup",
                "immediate_model_response",
            )
        )
        write_jsonl(self.corpus / "review-corpus.jsonl", [row])
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("prohibited content: email", completed.stdout)

    def test_extra_script_fails_closed(self) -> None:
        path = self.corpus / "review" / "index.html"
        html = path.read_text(encoding="utf-8").replace(
            "</body>", "<script nonce='MDEyMzQ1Njc4OUFCQ0RFRjAxMjM0'></script></body>"
        )
        write_text(path, html)
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("exactly one script", completed.stdout)

    def test_network_primitive_fails_closed(self) -> None:
        path = self.corpus / "review" / "index.html"
        html = path.read_text(encoding="utf-8").replace(
            "const node=", "fetch('/local');const node="
        )
        write_text(path, html)
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("network/persistence/eval primitive", completed.stdout)

    def test_relaxed_permission_fails_closed(self) -> None:
        (self.corpus / "candidate-index.jsonl").chmod(0o644)
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("file mode must be 0600", completed.stdout)

    def test_duplicate_derivative_fails_closed(self) -> None:
        duplicate = self.corpus / "reports" / "duplicate.json"
        shutil.copyfile(self.corpus / "corpus-manifest.json", duplicate)
        duplicate.chmod(0o600)
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("byte-identical file group", completed.stdout)

    def test_unexpected_corpus_file_fails_after_inventory_refresh(self) -> None:
        write_json(
            self.corpus / "reports" / "unexpected-audit.json",
            {"kind": "apparently_private_aggregate", "count": 1},
        )
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unexpected file", completed.stdout)

    def test_unexpected_restricted_file_fails_after_inventory_refresh(self) -> None:
        write_text(self.restricted / "extra-linkage.txt", "opaque extra\n")
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("restricted tree contains 1 unexpected file", completed.stdout)

    def test_full_name_alternative_metadata_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["alternative_explanations"] = ["Brett Reynolds"]
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("fixed canonical vocabulary", completed.stdout)

    def test_arbitrary_primary_phenomenon_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["primary_phenomenon"] = "brett_reynolds"
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid primary phenomenon", completed.stdout)

    def test_arbitrary_signal_name_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["evidence_signals"] = [{"signal": "brett_reynolds", "weight": 3}]
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("outside the fixed vocabulary", completed.stdout)

    def test_arbitrary_tool_action_class_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["tool_action_classes"] = ["brett_reynolds"]
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("tool_action_classes contains a non-canonical value", completed.stdout)

    def test_arbitrary_redaction_key_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["redaction_counts"] = {"brett_reynolds": 1}
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("invalid redaction counts", completed.stdout)

    def test_canonical_optional_audit_passes(self) -> None:
        write_json(
            self.corpus / "reports" / "contextual-privacy-audit.json",
            self.contextual_audit(),
        )
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_optional_audit_wrong_kind_fails_closed(self) -> None:
        audit = self.contextual_audit()
        audit["kind"] = "wrong_kind"
        write_json(
            self.corpus / "reports" / "contextual-privacy-audit.json",
            audit,
        )
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("kind is wrong", completed.stdout)

    def test_optional_audit_narrative_fails_closed(self) -> None:
        audit = self.contextual_audit()
        audit["interpretation_codes"] = ["this is arbitrary narrative prose"]
        write_json(
            self.corpus / "reports" / "contextual-privacy-audit.json",
            audit,
        )
        self.refresh_finalized_inventory()
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("arbitrary narrative string", completed.stdout)

    def test_provenance_field_fails_closed(self) -> None:
        row = dict(self.candidate)
        row["raw_path"] = "/private/example"
        write_jsonl(self.corpus / "candidate-index.jsonl", [row])
        completed = self.run_validator()
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("prohibited fields: raw_path", completed.stdout)


if __name__ == "__main__":
    unittest.main()
