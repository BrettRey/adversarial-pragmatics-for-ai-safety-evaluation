# Adversarial Pragmatics for AI Safety Evaluation

Status: active research artifact. Scaffold created 2026-06-26; public arXiv identifier assigned 2026-07-01.

Title: *Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity*.

Public arXiv identifier: `arXiv:2607.01153`. Submission-system identifier: `submit/7776593`.

## Canonical Local State

The current repository state supersedes arXiv v1 for project and job-market use.

Current artifact:

- 18 hand-authored seed items.
- Eight eligible paired contrasts plus one diagnostic confidentiality contrast.
- 54 item--model rows from a local Ollama pilot over `qwen3:8b`, `gemma3:12b`, and `glm-4.7-flash:q4_K_M`.
- Adjudicated pilot totals: 36 full task successes, 11 partial successes, 7 failures, 46 policy-compliant outputs.
- Paired-contrast readout: 12/24 eligible pair--model cells. P008 is excluded
  because its two rows differ in phenomenon family and both require
  non-disclosure. The seed pairs are controlled development contrasts, not
  uniformly strict minimal pairs.
- Sanitized row-level and aggregate summaries under `benchmark/results/summaries/`.
- LLM-judge validation showing that a rubric-aided judge missed the safety-relevant minority classes under favourable conditions.

Current paper stack in this repository:

- `main.tex`: empirical adversarial-pragmatics seed benchmark and pilot.
- `supplement.tex`: schema, item inventory, protocol, reproducibility notes, and sanitized pilot summaries.
- `delegation-assurance.tex`: framework paper on status, priority, licensing, and evidence standards for delegated machine action.
- `evidentiary-assurance.tex`: governance/legal assurance paper on action-level evidence bundles and review.

## Public-Version Gap

arXiv v1 currently reports the earlier nine-pair / 13/27 strict-pair readout.
The repaired local version reports eight eligible paired contrasts plus one
diagnostic contrast and 12/24 eligible paired-contrast passes; the new wording
does not claim that the seed pairs are uniformly strict minimal pairs.

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
- Self-pilot collection closed 2026-07-15. Five schema-v6 blocks returned
  (linguistic 02--03, policy/safety 01--03); the preserved schema-v5 sitting
  stands in for linguistic block 01 (Brett's call, 2026-07-15), so the v6
  timing report stays at 5/6 by design. Returns under
  `private/study-a/self-pilot/responses/` (v5 in `schema-v5-preserved/`),
  timing readout in `private/study-a/self-pilot/report/`. These are historical
  usability records, not Study A outcomes: policy/safety median was ~28 min per
  18-row block, while linguistic elapsed times are unusable open-tab wall
  clock. Evaluator-facing materials now use a conservative administrative
  estimate of 30--40 minutes per block and exclude timing from research claims.
- Exploratory self-pilot label diagnostics exist under
  `private/study-a/self-pilot/label-diagnostics/`
  (`scripts/analyze_self_pilot_labels.py`; DECISIONS 2026-07-15 narrowed the
  exclusion to no-ingestion/exploratory-only). Findings stay private; any
  design change they motivate goes through DECISIONS with provenance noted.
- Project policy bars evaluator invitations until a written Humber scope
  determination permits them. The executable gate cannot detect prior contact
  or distribution; before distributing a package or opening any external Study
  A return, retain separate hash-bound copies of the sent request and response,
  bind the current plan and protocol as the scope basis, complete the
  identity-side roster review, implement any required review or agreement path,
  finalize operational config v3, semantically verify stamp 2, commit it,
  create an annotated tag after response receipt only with Brett's explicit
  authorization, and pass the collection-ready gate. Verification or a commit
  without the written determination and tag does not authorize collection. The
  sanitized inquiry record is
  `notes/study-a-hreb-inquiry-record-2026-07-16.md`; the design rationale is
  `notes/study-a-evaluator-role-justification-2026-07-16.md`.
- Brett sent the shortened inquiry to HREB from his Humber account on
  2026-07-16 at 19:10:41 UTC. The byte-exact `.eml` is preserved, mode 0600 and
  Git-ignored, at
  `private/study-a/production/evidence/hreb-scope-inquiry-sent-2026-07-16.eml`
  (SHA-256 `b61f8f59c237b1cc3bac3a83fb8ee853fe69f93d1bfd5b99c21554ae7b767589`).
  The message describes the unfunded fixed-object study and asks whether HREB
  regards the experts as human research participants. It does not describe the
  project as independent and does not separately ask a jurisdiction/auspices
  question. Any HREB reply must either settle that second issue as inapplicable
  or prompt a follow-up before the current collection gate can pass. Proposed
  paper-affiliation wording remains a later manuscript decision. Humber's
  published calendar delays formal applications until HREB activity resumes in
  September; it does not say whether a narrow scope inquiry will be answered
  during the closure. External collection remains paused, but non-collection
  development can continue.
- A fresh local stamp-2 production candidate was rebuilt and semantically
  verified on 2026-07-16 after the object-only and gate-v3 repairs. Freeze
  readiness passes. Collection readiness fails closed as intended because the
  corrected files are not committed/tagged and no operational config, Humber
  evidence, real assignment registry/attestation, or identity-side roster
  review exists. Rebuild and re-stamp after implementing any Humber conditions;
  no tag or external opening has been authorized.
- Use the fixture-only repair miner privately after that decision; do not import
  real histories or derive naturalistic items until Study A has informed the
  rubric and analysis path.
- Split P008 into two clean contrast pairs for the development set.
- Add a disjoint judge model, no-rubric condition, alternate judge prompts, repeated items, and balanced minority classes.
- After Study A closes, consider adding explicit system-assigned-status and
  recognitional-fit labels to the benchmark rubric (the field-one adjudication
  machinery already exists in the two-stage protocol). Schema v5/v6 self-pilot
  forms remain preserved usability evidence; v7 is the current candidate
  instrument and has not been collection-frozen.
- Schema v7 built 2026-07-15 from the full form review
  (`notes/study-a-schema-v7-form-review.md`, changelog at end). Brett's call:
  identification questions first, global judgment last, on both forms.
  Standard escape pair on every scalar field, substantive first-slot keys for
  none-findings, stated/visible wording split, harmonized labels. Simulator,
  analyzer, builder, schema.md, and Study A READMEs updated; synthetic
  workflow, item validator, phase1-check, and privacy boundary all pass.
  Recruitment packages will be built from v7; self-pilot v5/v6 returns stay
  local usability evidence, not field-comparable to v7.
- Build an executable delegation-assurance harness for typed authority traces and reviewer reconstruction. The trace schema separates four fields per item: independently adjudicated authority status (genuine ambiguity admissible as a value), system-assigned status, recognitional fit or misfit, and the action produced through that recognition.
- Keep source verification current in `notes/source-verification.md`.

### 2026-07-13--15 Session Notes

- Delegation Assurance grew its missing empirical centre: a §3 comparative
  test (three authority minimal-pair families against a capabilities /
  per-call-authorization / causal-attribution baseline: Hardy 1988, ScopeGate
  arXiv:2606.28679, AttriGuard arXiv:2603.10749), a recognition-gap
  motivation in §1 citing *Effective without warrant* (PhilArchive REYEWW),
  a four-field trace schema (adjudicated status with admissible ambiguity,
  assigned status, fit, action), two TikZ figures (authority minimal pair;
  compositional path pair), and a conclusion that stakes the framework on the
  test instead of conceding "bounded translation".
- Flagship: judge-steerability paragraph in §2 and a rubric-departure judge
  condition in §7a (Alloula et al., arXiv:2606.07874, routed via central
  literature note); §5 adjudication sentence aligned with targeted
  confidence. Evidentiary: assigned-status record-adequacy sentence in the
  sufficiency test. Sources L71--L75 verified.
- Shipped `878f8dc` (2026-07-14). Work since is uncommitted: schema v7 and
  script/doc sync, the v7 form-review note, label diagnostics, confidence
  scoping, tracking updates.
- Study A self-pilot closed: six blocks returned, v5 sitting stands in for
  linguistic block 01; timing report says policy/safety median ~28 min per
  18-row block (linguistic elapsed is wall-clock, unusable).
- Schema v7 built from the full form review
  (`notes/study-a-schema-v7-form-review.md`): identification-first order with
  the global judgment last, uniform escape pair, substantive first-slot
  none-findings, harmonized wording; confidence targeted to the global
  judgment. Synthetic workflow, item validator, phase1-check, privacy
  boundary all pass.
- Exploratory self-pilot label diagnostics ran under the narrowed exclusion
  (no ingestion, exploratory-only): findings private under
  `private/study-a/self-pilot/label-diagnostics/`; item review candidates
  noted there.

### 2026-07-10 Session Notes

- Reframed the portfolio stack: *Adversarial Pragmatics* is the flagship empirical/evaluation artifact; *Delegation Assurance* supplies the security-and-assurance framework; *Evidentiary Assurance* supplies the governance/legal review layer.
- Verified that public arXiv v1 still carries the stale nine-pair / 13/27
  strict-pair readout, while the local manuscript has the repaired
  eight-eligible-paired-contrast / P008-diagnostic / 12/24 readout.
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
- **Superseded 2026-07-16:** selected the independent personal-project posture
  for Study A. The current description is an unfunded project led by a Humber
  Polytechnic employee; HREB has been asked for a written participant-status
  determination, and external recruitment remains closed.
- Selected full 54-row coverage per evaluator, split across three 18-row
  sittings. The workflow retains completed partial returns with an explicit
  coverage flag, but requires at least two ratings and a unique strict majority
  before a supported modal panel label is created.
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
  **Superseded 2026-07-16:** neither a dedicated address nor MFA is a hard
  requirement. Operational config v3 accepts any investigator-only, non-public,
  access-controlled transfer channel that is not used as long-term storage.
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

## Related reading — Cognition 2026 intake (2026-07-14)
Sources routed from a *Cognition* 2026 batch. Central index: `literature/cognition-2026-intake.md`. Verify claims/citations before use.
- **Selective deliberation, not blanket effort** [weak] — `notes/lit-cognition-2026-analytic-thinking-styles.md`
- **Future instructions relax present cognitive control** [medium] — `notes/lit-cognition-2026-prospective-relaxation.md`
- **Self-similar synthetic voices can amplify illusory truth** [medium] — `notes/lit-cognition-2026-self-voice-illusory-truth.md`
- (cross-ref) minimal-group-partisanship — `notes/source-hooks/cognition-2026-minimal-group-partisanship.md`
