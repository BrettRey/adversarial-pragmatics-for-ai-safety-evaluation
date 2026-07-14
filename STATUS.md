# Adversarial Pragmatics for AI Safety Evaluation

Status: active research artifact. Scaffold created 2026-06-26; public arXiv identifier assigned 2026-07-01.

Title: *Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity*.

Public arXiv identifier: `arXiv:2607.01153`. Submission-system identifier: `submit/7776593`.

## Canonical Local State

The current repository state supersedes arXiv v1 for project and job-market use.

Current artifact:

- 18 hand-authored seed items.
- Eight eligible strict contrast pairs plus one diagnostic confidentiality contrast.
- 54 item--model rows from a local Ollama pilot over `qwen3:8b`, `gemma3:12b`, and `glm-4.7-flash:q4_K_M`.
- Adjudicated pilot totals: 36 full task successes, 11 partial successes, 7 failures, 46 policy-compliant outputs.
- Strict-pair readout: 12/24 eligible pair--model cells. P008 is excluded from strict-pair scoring because its two rows differ in phenomenon family and both require non-disclosure.
- Sanitized row-level and aggregate summaries under `benchmark/results/summaries/`.
- LLM-judge validation showing that a rubric-aided judge missed the safety-relevant minority classes under favourable conditions.

Current paper stack in this repository:

- `main.tex`: empirical adversarial-pragmatics seed benchmark and pilot.
- `supplement.tex`: schema, item inventory, protocol, reproducibility notes, and sanitized pilot summaries.
- `delegation-assurance.tex`: framework paper on status, priority, licensing, and evidence standards for delegated machine action.
- `evidentiary-assurance.tex`: governance/legal assurance paper on action-level evidence bundles and review.

## Public-Version Gap

arXiv v1 currently reports the earlier nine-pair / 13/27 strict-pair readout. The repaired local version reports eight eligible strict pairs plus one diagnostic contrast and 12/24 eligible strict-pair passes.

Before circulating the project as a polished public artifact:

- submit an arXiv revision matching the canonical local manuscript;
- push the corresponding repository state;
- tag a numbered GitHub release from the same commit;
- archive that release with a DOI if external citation is expected.

## Build And Checks

Use XeLaTeX.

```bash
make
make all-papers
make test
python3 .house-style/check-style.py main.tex delegation-assurance.tex evidentiary-assurance.tex supplement.tex
```

Build the arXiv source package with:

```bash
bash scripts/build_arxiv_bundle.sh
```

The generated source archive is ignored by git:

```text
submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz
```

## Next Research Actions

- Complete Study A before expanding the item set: use the prepared blind,
  role-separated re-adjudication of the existing 54 outputs.
- Continue the self-pilot on the rebuilt schema-v6 forms through the optional
  practice set and remaining Study A blocks. Preserve the completed schema-v5
  linguistic/task block as diagnostic interface evidence, use retained block
  timing to document realistic evaluator burden, settle data-transfer details,
  then decide whether to approach external evaluators.
- Use the fixture-only repair miner privately after that decision; do not import
  real histories or derive naturalistic items until Study A has informed the
  rubric and analysis path.
- Split P008 into two clean contrast pairs for the development set.
- Add a disjoint judge model, no-rubric condition, alternate judge prompts, repeated items, and balanced minority classes.
- After Study A closes, consider adding explicit system-assigned-status and recognitional-fit labels to the benchmark rubric (the field-one adjudication machinery already exists in the two-stage protocol). The Study A instrument is frozen mid-pilot; this is a revision candidate, not a change to live forms.
- Build an executable delegation-assurance harness for typed authority traces and reviewer reconstruction. The trace schema separates four fields per item: independently adjudicated authority status (genuine ambiguity admissible as a value), system-assigned status, recognitional fit or misfit, and the action produced through that recognition.
- Keep source verification current in `notes/source-verification.md`.

### 2026-07-10 Session Notes

- Reframed the portfolio stack: *Adversarial Pragmatics* is the flagship empirical/evaluation artifact; *Delegation Assurance* supplies the security-and-assurance framework; *Evidentiary Assurance* supplies the governance/legal review layer.
- Verified that public arXiv v1 still carries the stale nine-pair / 13/27 strict-pair readout, while the local manuscript has the repaired eight-eligible-pair / P008-diagnostic / 12/24 readout.
- Updated repository-facing surfaces (`README.md`, `STATUS.md`, benchmark READMEs, arXiv metadata/abstract) to make the local canonical state explicit before job-market use.
- Rebuilt `submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz`; the generated source now contains the repaired P008 and 12/24 text.
- Added `sections-delegation/07-compositional-delegation.tex`, framing the forward-looking extension as compositional delegation assurance over typed authority-graph nodes with monotonic authority.
- Decided not to start an authority-accounting / AI-2040-scale fourth paper yet; preserve it as a candidate macro-governance extension after public cleanup and executable delegation-assurance work.
- Checks passed: `make test`, `git diff --check`, house-style checker on all four TeX top-level files, and `make all-papers`.

### 2026-07-10 Independent Re-adjudication Preparation

- Froze the original 54-row pilot as provisional historical data with a
  public-safe label snapshot and checksum manifest; the source author labels
  remain unchanged in the ignored local pilot bundle.
- Added `make phase1-check` to verify item/output/label coverage, frozen
  digests, summary reproduction in a temporary copy, and the private-data
  boundary.
- Added a separate blind Study A workflow with opaque IDs, two role-specific
  forms, 18-row blocks, local rejoin maps, synthetic rater simulation, and
  criterion-specific analysis. Failure attribution is deferred beyond the first
  pass.
- Added separate, practice-only evaluator orientation pages with six synthetic
  examples, immediate explanations, no pass threshold, plain-language form
  labels, field help, and block-level burden timing. Practice material is
  audited against the blind study rows and never exposes pilot labels or
  expected behaviour.
- Added draft-only evaluator-scope, recruitment, outreach, and policy-translation
  materials. No evaluator or organization has been contacted and no institutional
  determination is claimed.
- Selected the independent personal-project posture for Study A. Draft materials
  now state that the work is not institutionally sponsored, hosted, funded, or
  affiliated while that remains true; outreach and recruitment remain unlaunched.
- Selected full 54-row coverage per evaluator, split across three 18-row
  sittings. The workflow retains completed partial returns with an explicit
  coverage flag, but requires at least two ratings before a stable independent
  reference is created.
- Selected an unpaid, bounded volunteer contribution model. Draft materials now
  make clear that no honorarium, authorship, employment benefit, or other
  material consideration is offered or implied.
- Added `make study-a-self-pilot`, which builds a local-only, non-ingestible
  package from the frozen 54-row output bundle for interface and burden testing.
- Selected a full six-block self-pilot. Added a timing-only report command and
  runbook; self-pilot labels remain private and are technically excluded from
  independent Study A ingestion.
- Selected retention of returned blocks with a pre-analysis deletion window.
  Draft materials now require an exact collection-close and analysis-start
  cutoff, a private withdrawal log, deletion of requested source files before
  the cutoff, and regenerated derived outputs.
- Selected a dedicated Study A email address as the proportionate return channel.
  Draft instructions require MFA, pseudonymous JSON-only attachments, separate
  identity/contact records, and prompt transfer into the local private store.
- Revised the unlaunched policy/safety form after pre-recruitment usability
  feedback: schema version 3 replaces deployment-severity `safety_risk` and
  `risk_type` judgments with visible security-boundary status and type. The
  historical pilot remains frozen and no external Study A result is claimed.
- Added a fixture-only local repair-episode miner and review page. Real ChatGPT,
  Codex, and Claude Code histories remain unimported and must stay under
  ignored `private/` paths.

### 2026-07-14 Study A interface and paper-stack review

- Compared Brett's completed schema-v5 linguistic/task block with the frozen
  historical author labels. The six task-success differences are diagnostic,
  not independent inter-rater disagreement; AP-SEED-007 and AP-SEED-008 remain
  flagged for later item repair, and the frozen prompts and prior ratings were
  not rewritten.
- Rebuilt the linguistic/task instrument as schema v6. Source roles are judged
  across the prompt as a whole with a multi-select field; task-giver provenance
  is separated from directive force; source-role clarity separates competing
  analyses from missing information; task success is separate from policy
  compliance; scope/reference includes an explicit not-applicable response;
  requested-act labels are expanded; and rationales are optional.
- Retained the desktop sticky source panel, mobile single-column layout,
  top-and-focus reset on navigation, safe italic emphasis in help text,
  collapsed source-role examples, and schema/block-specific saved state. The
  v5 self-pilot JSON remains unchanged as a pre-revision record.
- Cross-read *Effective without warrant*, *Delegation Assurance*, and
  *Evidentiary Assurance*. The full three-pattern differential test belongs in
  *Delegation Assurance* against a strong capability, per-call authorization,
  provenance, and causal-attribution baseline. *Evidentiary Assurance* needs
  only the record-side corollary; the Synthese manuscript remains frozen.
- Terminology guardrail: use “efficacy outruns authorization” for the security
  cases. Moral warrant is a separate assessment and does not follow merely
  from authorization failure.
- Verification passed: `make phase1-check` and `make study-a-synthetic`; seed
  validation, private-data boundaries, frozen-pilot integrity, categorical
  ingestion, partial-return retention, and the complete synthetic workflow are
  clean under schema v6.
