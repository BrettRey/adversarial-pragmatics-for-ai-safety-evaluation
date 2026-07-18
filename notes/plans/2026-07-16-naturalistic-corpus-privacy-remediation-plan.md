# Naturalistic Corpus Privacy Remediation Plan

**Status:** completed on 2026-07-16. See
`notes/naturalistic-corpus-privatization-record.md` for the exact before/after
counts, transformation rules, hashes, contextual audit, and deletion record.

## Decision
Replace the current raw-episode derivative with a two-layer design:

1. a **privacy-minimized corpus** containing pseudonymous candidate metadata and aggressively minimized review excerpts; and

2. a **separate restricted linkage vault** containing only the local information needed to trace a candidate back to Brett's original history.


The result will be described as _privacy-minimized and pseudonymized_, not anonymized or public-safe. Public examples must still be newly written controlled reconstructions.

The current `review/index.html` is unsafe and must not be opened. It will be removed only after its before-state hash and structural defect have been recorded and a replacement has passed adversarial tests.
## Strongest Inversion
Putting raw transcript derivatives under an ignored `private/` directory does not privatize them. It only access-restricts them. A successful remediation must reduce what is retained, separate identity linkage from review data, make rendering inert, and fail closed when deterministic sanitization is inadequate.
## Load-Bearing Assumptions
| Assumption | Falsification condition | Design response |
| --- | --- | --- |
| Pragmatic candidate retrieval can be preserved without full tool output. | Removing stdout/file contents makes candidate class, evidence signals, or tool consequences uninterpretable. | Retain tool kind, generalized action class, success state, and event count; mark the item for controlled reconstruction rather than restoring raw output. |
| Deterministic redaction can create a useful internal review layer. | A post-build scanner or manual sample finds a direct identifier, correspondence fragment, active markup, or confidential project detail. | Withhold the affected text fields entirely and keep only structured candidate metadata pending manual reconstruction. |
| Exact source linkage can be separated from candidate data. | A candidate cannot be traced after raw paths and session IDs are removed from the corpus. | Keep an owner-only linkage map outside the corpus, keyed by HMAC pseudonyms and source-file hashes. |
| A static reviewer can be safe. | Hostile fixture text creates more than the intended script element, an external resource, an event handler, or a network-capable content path. | Encode corpus data as inert base64, use a strict CSP and nonce, avoid persistent browser storage, and validate the generated DOM structure before use. |
| Exact reporting need not expose private values. | The privatization record requires a name, path, address, email, URL, or excerpt to make a transformation reproducible. | Report algorithms, rule versions, counts, hashes, and field-level actions only; never report matched values. |
## Before-State Record
Before deletion or replacement, write a private machine-readable audit and a tracked aggregate record containing:

- sampling window, source/session/candidate/review counts;

- SHA-256 hashes, sizes, modes, and inode-duplication status for every derivative file;

- counts of direct-identifier and risk-pattern hits by field class;

- contextual audit design and aggregate disposition counts;

- the unsafe-reviewer mechanism and structural counts;

- the count of matches to the scanner's configured high-confidence secret patterns, without
  treating pattern absence as a credential-liveness test;

- the exact code version or source-file hashes used for the audit.


No raw match, identifier, path, domain, URL, token, or episode text will enter the tracked record.
## Target Data Architecture
```text
private/discovery/naturalistic-pragmatic-extremes-v2/
  corpus-manifest.json
  candidate-index.jsonl              # no conversation or tool text
  review-corpus.jsonl                # minimized, pseudonymized internal excerpts
  review/
    index.html                       # inert encoded data; no external resources
    README.md
  reports/
    corpus-profile.md                # aggregate only
    retrieval-audit.json
    privatization-audit.json         # before/after counts and hashes
    residual-risk-audit.json

private/restricted/naturalistic-pragmatic-extremes-v2/
  id-key.bin                         # owner-only HMAC key
  source-linkage.csv                 # HMAC IDs -> raw path/session/line linkage
  source-fingerprints.csv            # source hashes for reproducibility
```

The restricted vault is not part of the privatized corpus and must never be loaded by the reviewer. Original Codex and Claude histories remain the only raw source; no full normalized history or raw episode copy will be retained.
## Candidate-Index Minimization
Retain only:

- keyed candidate and session pseudonyms;

- source class and interactive mode;

- coarsened month, not exact timestamp;

- candidate class, score, strength, phenomenon, evidence signals, pragmatic-load signals, and alternative explanations;

- no model identifier: candidate retrieval and privacy review do not require it, and even a
  family label can combine with month and episode details to narrow the source session;

- counts and booleans for compaction, tool actions, and withheld content;

- privacy disposition and reconstruction status.


Remove exact timestamps, project hashes, software versions, branches, permission strings,
prompt provenance, raw paths, session IDs, node IDs, and all conversation/tool text from the
candidate index. Software versions and prompt provenance are not needed after restricting the
source set to interactive human sessions, and they add session-fingerprinting detail. The
candidate index is therefore text-free; selected conversation excerpts live only in the more
restricted review corpus described below. Raw tool arguments and outputs are never retained
because they routinely reproduce paths, source text, correspondence, and access context.

Use HMAC-SHA-256 with a random local key stored outside the corpus. Do not use unsalted path hashes.
## Review-Corpus Minimization
For each selected candidate:

- copy the minimized candidate-index fields;

- retain only the triggering request, visible response, user follow-up, and immediate repair response when they pass sanitization;

- retain at most two preceding turns, capped at 900 characters per role, only when a retrieval
  signal such as reference, ellipsis, repetition, or post-compaction recovery requires them;
  the cap limits contextual re-identification while preserving the smallest useful contrast;

- replace tool-call/output spans with generalized action classes and bounded event counts while
  omitting their arguments and returned text; omit governing instruction dumps, environment
  context, full compaction summaries, file contents, email bodies, quoted documents, code
  blocks, and attachment text;

- replace tool traces with generalized event metadata and bounded counts;

- impose both per-field and per-episode character caps;

- replace paths, emails, URLs, handles, phone/address patterns, long identifiers, dates, file names, and proper-name/organization patterns with typed episode-local placeholders;

- withhold the entire relevant text field when correspondence, pasted-document, credential, active-markup, or residual direct-identifier rules fire;

- label every row `internal_review_only`; never label an automatically minimized row public-safe.


If minimization destroys the pragmatic contrast, keep the structured index row and mark it `manual_controlled_reconstruction_required`.
## Reviewer Repair
The replacement reviewer will:

- never interpolate JSON directly into executable JavaScript;

- embed only base64-encoded minimized data;

- set a strict Content Security Policy denying connections, external resources, forms, frames, objects, and base URLs;

- authorize only the one generated script with a nonce;

- render candidate content through text nodes or escaping, never as trusted markup;

- keep decisions in memory rather than `localStorage`;

- display decision-only JSON as inert, read-only text, never corpus text;

- provide no automatic download, file-write, clipboard, or browser-storage path, and remind the
  reviewer that any deliberate manual save belongs only inside the restricted private boundary;

- offer a clear-memory action.


The hostile fixture must include closing-script text, script/image/iframe tags, event handlers, network calls, HTML entities, email headers, local paths, URLs with query values, and code blocks.
## Validator Changes
The validator must fail unless:

- output and restricted-vault paths are inside ignored private roots;

- all directories are `0700`, files are `0600`, and no symlink is present;

- the candidate index contains no prohibited text or direct-provenance fields;

- the review corpus contains no raw path, email, phone, URL, credential, active-markup, or forbidden proper-name pattern;

- field and episode caps hold, and no tool text is retained;

- source linkage exists only in the separate restricted vault;

- no derivative files are byte-identical duplicates;

- the reviewer has exactly the intended script, no external resources or handlers, a strict CSP, and inert data;

- aggregate reports contain no candidate text or direct identifiers;

- the before/after privacy audit is internally consistent.

## Implementation Sequence
1. Record the complete before-state audit without exposing matched values.

2. Add hostile synthetic fixtures and tests that reproduce the current reviewer injection and direct-identifier leakage.

3. Implement keyed pseudonyms, field minimization, aggressive redaction, withholding, total episode caps, and generalized tool metadata.

4. Split the privacy-minimized corpus from the restricted linkage vault; eliminate the byte-identical normalized copy and all raw episode derivatives.

5. Replace the static reviewer and remove browser persistence.

6. Extend the validator with placement, symlink, directory-mode, residual-identifier, minimization, duplication, and reviewer-structure checks.

7. Build v2 beside v1, validate it, and run a deterministic 60-row contextual residual-risk audit.

8. If any direct identifier or active content survives, tighten rules and rebuild; do not waive the failure.

9. After v2 passes, delete v1 and verify that no unsafe HTML, duplicate raw derivative, browser export, or review state remains.

10. Write `notes/naturalistic-corpus-privatization-record.md` with exact transformations, before/after counts, audit method, limitations, and file hashes.

11. Re-run synthetic workflow, corpus validator, privacy boundary checks, public checks, and `git diff --check`.

## Checkpoints and Stop Conditions
- **Before-state checkpoint:** no old file is removed until its hash, size, permissions, and risk counts are recorded.

- **Renderer checkpoint:** any extra parsed script/resource/handler or network-capable path blocks use of the reviewer.

- **Residual-identifier checkpoint:** any confirmed direct identifier in the minimized review corpus forces withholding or rebuild.

- **Interpretability checkpoint:** lost context leads to a reconstruction flag, never reintroduction of raw tool/document output.

- **Deletion checkpoint:** v1 is deleted only after v2 and its restricted linkage map independently validate.

- **Reporting checkpoint:** the tracked record must reproduce every aggregate claim from machine-readable audits without revealing a private value.

## Evidential Boundary
This remediation does not make the corpus representative, independently adjudicated, or covered by the pending Study A HREB inquiry. It does not authorize quotation or publication. It creates a safer internal discovery index and review workflow from which any public case must be reconstructed as a new benign controlled example.
