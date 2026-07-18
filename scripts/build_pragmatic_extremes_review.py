#!/usr/bin/env python3
"""Build a quarantined offline reviewer for a private pragmatic-extremes corpus."""

from __future__ import annotations

import argparse
import base64
import html
import importlib.util
import json
import os
import secrets
import stat
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVATE_ROOT = REPO_ROOT / "private"
DISCOVERY_ROOT = PRIVATE_ROOT / "discovery"
VALIDATOR_PATH = Path(__file__).resolve().with_name(
    "validate_naturalistic_pragmatic_corpus.py"
)
REVIEW_FILENAME = "review-corpus.jsonl"
REVIEW_DIRECTORY = "review"
REVIEW_OUTPUT_FILES = frozenset({"index.html", "README.md"})


def load_corpus_validator() -> Any:
    """Load the authoritative v2 schema validator from this scripts directory."""

    spec = importlib.util.spec_from_file_location(
        "_naturalistic_corpus_validator_for_reviewer", VALIDATOR_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load the naturalistic-corpus validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CORPUS_VALIDATOR = load_corpus_validator()


HTML_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive,nosnippet,noimageindex">
<meta http-equiv="Content-Security-Policy" content="__CSP__">
<title>Private pragmatic-extremes review</title>
<style nonce="__STYLE_NONCE__">
:root{--ink:#172026;--muted:#617080;--line:#cbd5df;--accent:#0f766e;--warn:#b45309;--fail:#991b1b;--success:#166534}*{box-sizing:border-box}body{margin:0;font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}main{max-width:1280px;margin:0 auto;padding:24px}h1,h2{margin:0 0 10px}h1{font-size:1.5rem}h2{font-size:1.03rem;margin-top:16px}.muted{color:var(--muted)}.notice{border-left:4px solid var(--warn);background:#fff7ed;padding:11px 13px;margin:14px 0}.flash{border-left-color:var(--accent);background:#ecfdf5}.grid{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:18px}.box{border:1px solid var(--line);border-radius:8px;padding:14px;margin-bottom:14px}.text{white-space:pre-wrap;overflow-wrap:anywhere;border:1px solid #dbe2ea;border-radius:6px;padding:10px;max-height:320px;overflow:auto;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#fbfdff}.context{max-height:220px}.trace{max-height:260px}.tag{display:inline-block;border:1px solid #cbd5df;border-radius:999px;padding:3px 7px;margin:2px;font-size:.84rem}.fail{color:var(--fail);background:#fef2f2;border-color:#fecaca}.success{color:var(--success);background:#f0fdf4;border-color:#bbf7d0}.warn{color:#7c2d12;background:#fff7ed;border-color:#fed7aa}label{display:grid;gap:6px;margin:13px 0;font-weight:650}select,textarea,button{font:inherit}select,textarea{width:100%;padding:9px 10px;border:1px solid var(--line);border-radius:6px}textarea{min-height:90px;resize:vertical}.actions{display:flex;gap:9px;flex-wrap:wrap;margin-top:14px}button{padding:9px 13px;border:1px solid var(--line);border-radius:7px;background:#fff;cursor:pointer}.primary{background:var(--accent);border-color:var(--accent);color:white}.danger{border-color:#fca5a5;color:var(--fail)}.meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;font-size:.9rem}@media(max-width:900px){main{padding:16px}.grid{display:block}}
</style>
</head>
<body>
<main id="app"></main>
<template id="candidate-data" data-encoding="base64">__CORPUS_B64__</template>
<script nonce="__SCRIPT_NONCE__">
"use strict";

const dataNode = document.getElementById("candidate-data");
if (!dataNode || dataNode.dataset.encoding !== "base64") {
  throw new Error("Private candidate data is missing or has an unexpected encoding.");
}
const encodedData = dataNode.content.textContent.trim();
const dataBytes = Uint8Array.from(atob(encodedData), character => character.charCodeAt(0));
const ITEMS = JSON.parse(new TextDecoder().decode(dataBytes));
dataNode.remove();

const OPTIONS = Object.freeze({
  decision: ["unreviewed", "retain", "reject", "needs_followup"],
  adjudicated_class: ["", "likely_pragmatic_failure", "surprising_pragmatic_success", "ambiguous_or_competing_readings", "neither"],
  evidence_strength: ["", "high", "moderate", "low", "insufficient"],
  phenomenon: ["", "reference_and_ellipsis", "task_type_recognition", "scope_and_authorization", "instruction_source_and_authority", "negative_constraint_persistence", "repair_uptake", "state_and_compaction", "completion_and_status_reporting", "tool_action_alignment", "non_pragmatic", "other"],
  alternative_explanation: ["", "none_apparent", "reasonable_competing_reading", "clarification_needed", "user_changed_request", "lost_or_hidden_context", "non_pragmatic_error", "insufficient_evidence"],
  privacy_disposition: ["not_reviewed", "internal_only", "manual_reconstruction_required", "do_not_derive"]
});
const app = document.getElementById("app");
let index = 0;
let decisions = Object.create(null);
let flashMessage = "";
let showDecisionView = false;

function display(value) {
  return value === null || value === undefined ? "" : String(value);
}

function element(tag, className, textValue) {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (textValue !== undefined) result.textContent = display(textValue);
  return result;
}

function append(parent, ...children) {
  for (const child of children) parent.appendChild(child);
  return parent;
}

function button(label, className, handler) {
  const result = element("button", className, label);
  result.type = "button";
  result.addEventListener("click", handler);
  return result;
}

function currentDecision(item) {
  const candidateId = display(item.candidate_id);
  return {
    candidate_id: candidateId,
    decision: "unreviewed",
    adjudicated_class: "",
    evidence_strength: "",
    phenomenon: OPTIONS.phenomenon.includes(item.primary_phenomenon) ? item.primary_phenomenon : "",
    alternative_explanation: "",
    privacy_disposition: "not_reviewed",
    notes: "",
    ...(decisions[candidateId] || {})
  };
}

function setDecision(item, name, value) {
  const candidateId = display(item.candidate_id);
  decisions[candidateId] = {
    ...currentDecision(item),
    [name]: value,
    updated_at: new Date().toISOString()
  };
  refreshDecisionView();
}

function decisionControl(item, name, value) {
  const label = element("label", "", name.replaceAll("_", " "));
  const select = document.createElement("select");
  select.dataset.name = name;
  for (const optionValue of OPTIONS[name]) {
    const option = element("option", "", optionValue);
    option.value = optionValue;
    option.selected = value === optionValue;
    select.appendChild(option);
  }
  select.addEventListener("change", () => setDecision(item, name, select.value));
  label.appendChild(select);
  return label;
}

function notesControl(item, value) {
  const label = element("label", "", "Notes");
  const textarea = document.createElement("textarea");
  textarea.dataset.name = "notes";
  textarea.value = value;
  textarea.addEventListener("input", () => setDecision(item, "notes", textarea.value));
  label.appendChild(textarea);
  return label;
}

function signalText(signal) {
  if (typeof signal === "string") return signal;
  if (signal && typeof signal === "object") return display(signal.signal);
  return display(signal);
}

function tagList(values, className) {
  const list = element("div");
  if (!Array.isArray(values) || values.length === 0) {
    list.textContent = "none";
    return list;
  }
  for (const value of values) list.appendChild(element("span", `tag ${className}`, signalText(value)));
  return list;
}

function labeledTags(parent, label, values, className) {
  const paragraph = document.createElement("p");
  paragraph.appendChild(element("b", "", label));
  paragraph.appendChild(document.createElement("br"));
  paragraph.appendChild(tagList(values, className));
  parent.appendChild(paragraph);
}

function textSection(parent, heading, value, extraClass) {
  parent.appendChild(element("h2", "", heading));
  parent.appendChild(element("div", `text${extraClass ? ` ${extraClass}` : ""}`, value));
}

function contextText(values) {
  if (!Array.isArray(values) || values.length === 0) return "(none retained)";
  return values.map(value => `user: ${display(value && value.user)}\nassistant: ${display(value && value.assistant)}`).join("\n\n---\n\n");
}

function metadata(parent, label, value, tagClass) {
  const row = document.createElement("div");
  row.appendChild(element("b", "", `${label}: `));
  row.appendChild(tagClass ? element("span", `tag ${tagClass}`, value) : document.createTextNode(display(value)));
  parent.appendChild(row);
}

function clearMemory() {
  if (!window.confirm("Clear every in-memory decision from this review session? This cannot be undone.")) return;
  decisions = Object.create(null);
  index = 0;
  showDecisionView = false;
  flashMessage = "All in-memory decisions were cleared.";
  render();
}

function decisionRecord(item) {
  const record = currentDecision(item);
  return {
    candidate_id: record.candidate_id,
    decision: record.decision,
    adjudicated_class: record.adjudicated_class,
    evidence_strength: record.evidence_strength,
    phenomenon: record.phenomenon,
    alternative_explanation: record.alternative_explanation,
    privacy_disposition: record.privacy_disposition,
    notes: record.notes,
    updated_at: record.updated_at || null
  };
}

function decisionPayloadText() {
  const records = ITEMS
    .filter(item => Object.prototype.hasOwnProperty.call(decisions, display(item.candidate_id)))
    .map(decisionRecord);
  const payload = {
    schema_version: 2,
    kind: "private_pragmatic_extremes_decisions",
    prepared_at: new Date().toISOString(),
    decisions: records
  };
  return JSON.stringify(payload, null, 2);
}

function refreshDecisionView() {
  const output = document.getElementById("decision-json");
  if (output) output.textContent = decisionPayloadText();
}

function decisionViewPanel() {
  const panel = element("div", "box");
  panel.id = "decision-json-panel";
  panel.appendChild(element("h2", "", "Decision JSON for manual private save"));
  panel.appendChild(element(
    "p",
    "muted",
    "This read-only view contains decision fields and reviewer notes only. Manually save it inside the restricted private boundary; do not place it in an ordinary, synced, or shared folder."
  ));
  const output = element("pre", "text trace", decisionPayloadText());
  output.id = "decision-json";
  output.tabIndex = 0;
  output.setAttribute("role", "textbox");
  output.setAttribute("aria-readonly", "true");
  panel.appendChild(output);
  return panel;
}

function showDecisionJson() {
  showDecisionView = true;
  render();
}

function privacyNotice() {
  return element(
    "div",
    "notice",
    "Private material: decisions are held only in memory and disappear when this tab closes or reloads. Prepare the decision JSON only when needed, then manually save it inside the restricted private boundary—never in an ordinary, synced, shared, or public destination."
  );
}

function renderEmpty() {
  app.replaceChildren(
    element("h1", "", "No candidates"),
    element("p", "", "The private review corpus is empty."),
    privacyNotice()
  );
}

function renderFinished() {
  const actions = element("div", "actions");
  append(
    actions,
    button("Return", "", () => { index = Math.max(0, ITEMS.length - 1); render(); }),
    button("Show decision JSON", "primary", showDecisionJson),
    button("Clear in-memory decisions", "danger", clearMemory)
  );
  const children = [
    element("h1", "", "Review complete"),
    element("p", "", `${Object.keys(decisions).length} candidate decisions are currently held in memory.`),
    privacyNotice(),
    actions
  ];
  if (showDecisionView) children.push(decisionViewPanel());
  app.replaceChildren(...children);
}

function render() {
  if (!Array.isArray(ITEMS) || ITEMS.length === 0) {
    renderEmpty();
    return;
  }
  if (index >= ITEMS.length) {
    renderFinished();
    return;
  }

  const item = ITEMS[index];
  const record = currentDecision(item);
  const candidateClass = display(item.candidate_class);
  const className = candidateClass === "likely_pragmatic_failure" ? "fail" : "success";
  const header = element("div");
  append(
    header,
    element("h1", "", "Private pragmatic-extremes review"),
    element("p", "muted", `Candidate ${index + 1} of ${ITEMS.length}; ${display(item.candidate_id)}`),
    privacyNotice()
  );
  if (flashMessage) {
    header.appendChild(element("div", "notice flash", flashMessage));
    flashMessage = "";
  }
  header.appendChild(element("div", "notice", "This is a retrieval candidate, not a gold label or publication-ready excerpt. Judge the visible episode, preserve ambiguity, and do not copy transcript material outside the private boundary."));

  const episodeBox = element("div", "box");
  const meta = element("div", "meta");
  metadata(meta, "Source", item.source);
  metadata(meta, "Class", candidateClass, className);
  metadata(meta, "Score", item.candidate_score);
  metadata(meta, "Phenomenon", item.primary_phenomenon);
  metadata(meta, "Session", item.session_ref);
  metadata(meta, "Month", item.month);
  metadata(meta, "Privacy", item.privacy_disposition);
  metadata(meta, "Reconstruction", item.reconstruction_status);
  episodeBox.appendChild(meta);
  labeledTags(episodeBox, "Evidence signals", item.evidence_signals, className);
  labeledTags(episodeBox, "Pragmatic-load signals", item.pragmatic_load_signals, "warn");
  labeledTags(episodeBox, "Content withheld", item.content_withheld_fields, "warn");
  labeledTags(episodeBox, "Redactions", Object.entries(item.redaction_counts || {}).map(([name, count]) => `${name}: ${count}`), "warn");
  labeledTags(episodeBox, `Tool/action classes (${display(item.tool_event_count || 0)} events)`, item.tool_action_classes, "warn");
  textSection(episodeBox, "Preceding context", contextText(item.preceding_context), "context");
  textSection(episodeBox, "Triggering request", display(item.triggering_request));
  textSection(episodeBox, "Model-visible response", display(item.model_visible_response));
  textSection(episodeBox, "User follow-up", display(item.user_followup));
  textSection(episodeBox, "Immediate model response", display(item.immediate_model_response) || "(none retained)");

  const controls = element("div", "box");
  for (const name of ["decision", "adjudicated_class", "evidence_strength", "phenomenon", "alternative_explanation", "privacy_disposition"]) {
    controls.appendChild(decisionControl(item, name, record[name]));
  }
  controls.appendChild(notesControl(item, record.notes));
  const actions = element("div", "actions");
  append(
    actions,
    button("Back", "", () => { index = Math.max(0, index - 1); render(); }),
    button(index + 1 === ITEMS.length ? "Finish" : "Next", "primary", () => { index += 1; render(); }),
    button("Show decision JSON", "", showDecisionJson),
    button("Clear in-memory decisions", "danger", clearMemory)
  );
  controls.appendChild(actions);
  if (showDecisionView) controls.appendChild(decisionViewPanel());

  const grid = element("div", "grid");
  const section = document.createElement("section");
  const aside = document.createElement("aside");
  section.appendChild(episodeBox);
  aside.appendChild(controls);
  append(grid, section, aside);
  app.replaceChildren(header, grid);
}

render();
</script>
</body>
</html>
"""


def lexical_absolute(path: Path) -> Path:
    """Return an absolute normalized path without resolving symlinks."""

    return Path(os.path.abspath(os.path.expanduser(os.fspath(path))))


def path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def check_no_symlink_components(
    path: Path, label: str, *, allow_missing_leaf: bool = False
) -> None:
    """Reject symlinks in every project-relative component of ``path``."""

    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError as exc:
        raise SystemExit(f"{label} must be inside the repository") from exc
    current = REPO_ROOT
    for position, component in enumerate(relative.parts):
        current /= component
        try:
            info = current.lstat()
        except FileNotFoundError as exc:
            is_leaf = position == len(relative.parts) - 1
            if allow_missing_leaf and is_leaf:
                return
            raise SystemExit(f"{label} has a missing path component") from exc
        if stat.S_ISLNK(info.st_mode):
            raise SystemExit(f"{label} contains a symlink path component")


def validate_cli_paths(candidates_arg: Path, output_arg: Path) -> tuple[Path, Path]:
    """Enforce the one permitted corpus-input and reviewer-output layout."""

    candidates = lexical_absolute(candidates_arg)
    output = lexical_absolute(output_arg)
    if (
        candidates.name != REVIEW_FILENAME
        or candidates.parent.parent != DISCOVERY_ROOT
    ):
        raise SystemExit(
            "--candidates must be the exact review-corpus.jsonl of a direct-child "
            "private/discovery corpus"
        )
    check_no_symlink_components(candidates, "--candidates")
    candidate_info = candidates.lstat()
    if not stat.S_ISREG(candidate_info.st_mode):
        raise SystemExit("--candidates must be a regular file")
    if candidate_info.st_nlink != 1:
        raise SystemExit("--candidates must not be hard-linked")

    expected_output = candidates.parent / REVIEW_DIRECTORY
    if output != expected_output:
        raise SystemExit("--out-dir must be the candidates file's sibling review directory")
    if (
        candidates == output
        or candidates in output.parents
        or output in candidates.parents
    ):
        raise SystemExit("candidate input and reviewer output must not overlap")
    check_no_symlink_components(output, "--out-dir", allow_missing_leaf=True)
    return candidates, output


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        handle = path.open(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise SystemExit("review corpus is unreadable") from exc
    with handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"review-corpus row {line_number} is invalid JSON")
                continue
            if not isinstance(value, dict):
                errors.append(f"review-corpus row {line_number} is not an object")
                continue
            rows.append(value)
    if errors:
        fail_validation(errors)
    return rows


def fail_validation(errors: list[str]) -> None:
    displayed = errors[:50]
    suffix = ""
    if len(errors) > len(displayed):
        suffix = f"\n- {len(errors) - len(displayed)} further errors suppressed"
    raise SystemExit(
        "review corpus failed v2 validation:\n"
        + "\n".join(f"- {error}" for error in displayed)
        + suffix
    )


def validate_review_rows(rows: list[dict[str, Any]]) -> None:
    """Apply the authoritative exact v2 schema, privacy, and cap rules."""

    errors: list[str] = []
    candidates_by_id: dict[str, dict[str, Any]] = {}
    exact_rows: list[tuple[int, dict[str, Any]]] = []
    for row_number, row in enumerate(rows, start=1):
        if set(row) != CORPUS_VALIDATOR.REVIEW_FIELDS:
            try:
                CORPUS_VALIDATOR.validate_review_row(
                    row, row_number, candidates_by_id, errors
                )
            except (KeyError, TypeError, ValueError):
                errors.append(f"review-corpus row {row_number} has invalid field types")
            continue
        candidate = {
            field: row[field]
            for field in CORPUS_VALIDATOR.CANDIDATE_FIELDS
            if field != "review_selected"
        }
        candidate["review_selected"] = True
        try:
            candidate_id, _session_ref = CORPUS_VALIDATOR.validate_candidate_row(
                candidate, row_number, errors
            )
        except (KeyError, TypeError, ValueError):
            errors.append(f"review-corpus row {row_number} has invalid field types")
            candidate_id = None
        if candidate_id is not None:
            if candidate_id in candidates_by_id:
                errors.append(f"review-corpus row {row_number} repeats a candidate ID")
            else:
                candidates_by_id[candidate_id] = candidate
        exact_rows.append((row_number, row))

    for row_number, row in exact_rows:
        try:
            CORPUS_VALIDATOR.validate_review_row(
                row, row_number, candidates_by_id, errors
            )
        except (KeyError, TypeError, ValueError):
            errors.append(f"review-corpus row {row_number} has invalid field types")
    if errors:
        fail_validation(errors)


def prepare_output_directory(output: Path, candidates: Path, overwrite: bool) -> None:
    """Create or clear only the exact review directory, without following links."""

    if not path_exists(output):
        try:
            os.mkdir(output, 0o700)
        except OSError as exc:
            raise SystemExit("could not create the exact review directory") from exc
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        directory_fd = os.open(output, flags)
    except OSError as exc:
        raise SystemExit("--out-dir must be a non-symlink directory") from exc
    try:
        output_info = os.fstat(directory_fd)
        if not stat.S_ISDIR(output_info.st_mode):
            raise SystemExit("--out-dir must be a directory")
        candidate_info = candidates.stat()
        names = os.listdir(directory_fd)
        for name in names:
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as exc:
                raise SystemExit("review directory contains an unreadable entry") from exc
            if stat.S_ISLNK(info.st_mode):
                raise SystemExit("review directory contains a symlink entry")
            if not stat.S_ISREG(info.st_mode):
                raise SystemExit("review directory contains a nonregular entry")
            if name not in REVIEW_OUTPUT_FILES:
                raise SystemExit("review directory contains an unexpected regular file")
            if info.st_nlink != 1:
                raise SystemExit("review directory contains a hard-linked entry")
            if (info.st_dev, info.st_ino) == (
                candidate_info.st_dev,
                candidate_info.st_ino,
            ):
                raise SystemExit("candidate input and reviewer output overlap")
        if names and not overwrite:
            raise SystemExit("review output exists; pass --overwrite")
        if overwrite:
            for name in names:
                os.unlink(name, dir_fd=directory_fd)
        os.fchmod(directory_fd, 0o700)
    finally:
        os.close(directory_fd)


def write_private_file(directory: Path, name: str, content: str) -> None:
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    directory_fd = os.open(directory, directory_flags)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        file_fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
        with os.fdopen(file_fd, "w", encoding="utf-8") as handle:
            handle.write(content)
    finally:
        os.close(directory_fd)


def nonce() -> str:
    """Return a fresh high-entropy CSP nonce in standard Base64 form."""

    return base64.b64encode(secrets.token_bytes(24)).decode("ascii")


def build_html(candidates: list[dict[str, Any]]) -> str:
    """Encode private records inertly and bind the sole script with a CSP nonce."""

    script_nonce = nonce()
    style_nonce = nonce()
    compact_json = json.dumps(candidates, ensure_ascii=False, separators=(",", ":"))
    corpus_b64 = base64.b64encode(compact_json.encode("utf-8")).decode("ascii")
    csp = "; ".join(
        [
            "default-src 'none'",
            f"script-src 'nonce-{script_nonce}'",
            f"style-src 'nonce-{style_nonce}'",
            "connect-src 'none'",
            "img-src 'none'",
            "object-src 'none'",
            "frame-src 'none'",
            "form-action 'none'",
            "base-uri 'none'",
            "font-src 'none'",
            "media-src 'none'",
            "worker-src 'none'",
            "child-src 'none'",
            "manifest-src 'none'",
        ]
    )
    return (
        HTML_TEMPLATE.replace("__CSP__", html.escape(csp, quote=True))
        .replace("__STYLE_NONCE__", html.escape(style_nonce, quote=True))
        .replace("__CORPUS_B64__", corpus_b64)
        .replace("__SCRIPT_NONCE__", html.escape(script_nonce, quote=True))
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    os.umask(0o077)
    args = parse_args()
    candidates_path, out_dir = validate_cli_paths(args.candidates, args.out_dir)
    candidates = read_jsonl(candidates_path)
    validate_review_rows(candidates)
    document = build_html(candidates)
    readme = (
        "# Private Pragmatic-Extremes Review\n\n"
        "Open `index.html` directly in a browser. Candidate data is Base64-encoded "
        "inside the page as inert local data; it is not anonymized and the page must "
        "remain inside the ignored private corpus directory.\n\n"
        "Review decisions exist only in memory and disappear when the tab closes or "
        "reloads. Use **Show decision JSON** when needed. The page displays a read-only "
        "decision-only JSON view and never creates a decision file. Manually save that "
        "text only inside the restricted private boundary, never in an ordinary, synced, "
        "shared, or public destination. The view contains only decision fields and "
        "reviewer-authored notes; it never automatically copies the embedded transcript. "
        "Treat notes as private because a reviewer can type or paste sensitive material "
        "into them.\n"
    )
    prepare_output_directory(out_dir, candidates_path, args.overwrite)
    write_private_file(out_dir, "index.html", document)
    write_private_file(out_dir, "README.md", readme)
    print(f"Built offline review page for {len(candidates)} candidates: {out_dir / 'index.html'}")


if __name__ == "__main__":
    main()
