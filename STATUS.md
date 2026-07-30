---
slug: adversarial-pragmatics-for-ai-safety-evaluation
kind: paper
title: 'Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for
  Language-Mediated Control'
stage: complete
external: preprint
blocked_on: []
updated: 2026-07-30
source:
- STATUS.md
- PORTFOLIO.md
venue: JAIR
preprints:
- arXiv:2607.01153
next_action: 'JAIR submission (STATUS.md: "the next available piece of work")'
notes: 'Classified on the flagship Adversarial Pragmatics (AP) paper, matching the directory/manifest
  title. This repository holds three stand-alone papers (AP itself; delegation-assurance.tex; evidentiary-assurance.tex)
  plus a shared supplement. ADJUDICATION 2026-07-30: DA and EA now have their own registry entries in
  batch-10.yaml, with `path` pointing at this directory, per the v2 rule that the registry unit is the
  manuscript rather than the directory. This block covers AP only. STATUS.md/SUMMARY: arXiv v3 is public
  (2607.01153, retitled, 2026-07-29 timestamp); "Not held: Adversarial Pragmatics, whose benchmark, pilot,
  and judge results run through none of this [external-review] code, and whose JAIR submission is the
  next available piece of work" -- i.e. AP has never been submitted to a venue (external: preprint, blocked_on:
  none), unlike DA/EA whose release tags are explicitly "held" pending Brett''s call on "frozen" language.
  AP carries a known but STATUS.md-described-as-non-critical v3 defect (supplement.tex:361 estimator misdescription,
  deferred to v4; "No computed result is affected"), not treated as blocking stage: complete.

  '
---

# Adversarial Pragmatics for AI Safety Evaluation
<!-- SUMMARY: empirical adversarial-pragmatics benchmark; arXiv v3 PUBLIC 2026-07-29 (retitle live, sibling citations now resolve); external code review 2026-07-29 found 7 false-pass bugs, all closed, but DA claim register migrated, assurance-check green again; assurance tags still held pending Brett's call on 'frozen' language in DA; EA taken through two external-review rounds to minor revision + interval-decision analyzer; all three papers shipped to public main 2026-07-24; HREB partially answered Study A scope inquiry 2026-07-28 (participant-status cleared, jurisdiction question still open); EA release tag/DOI and venue record still pending; v3 ships a known supplement estimator misdescription, deferred to v4 · status: active · updated: 2026-07-30 -->

Status: active research artifact. Scaffold created 2026-06-26; public arXiv identifier assigned 2026-07-01; v2 replacement public 2026-07-16; **v3 replacement public, announced in the 2026-07-30 mailing** (arXiv version timestamp 2026-07-29 15:40:42 UTC, 942 KB).

## Deferred: two corpus follow-ups (2026-07-25)

The naturalistic-pragmatic-extremes-v2 corpus has (1) a detection blind spot for scope expansion the user never objected to, since all 33 `scope_and_authorization` cases are found via user-resistance signals, and (2) **no model or effort field on any of its 777 entries**, so Opus-at-xhigh and haiku-at-low are both filed as "claude". Details and the proposed assistant-first-mention pass: `notes/2026-07-25-corpus-followups.md`. Neither started.

Title: *Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control*.

Public arXiv identifier: `arXiv:2607.01153` (v3 public, announced 2026-07-30; the identifier is unchanged across versions). Submission-system identifiers: `submit/7776593` (v1), `submit/7830880` (v2 replacement), `submit/7884568` (v3 replacement). Paper password recorded in `private/arxiv-credentials.md` (gitignored; unchanged by the v3 replacement, verified 2026-07-30).

**v3 carries a known defect, deliberately not corrected by an emergency v4.** `supplement.tex:361` describes Study B's family-level estimator as "a single multilevel model with partial pooling across families and bases", while `scripts/analyze_study_b.py:650` implements DerSimonian--Laird two-stage random-effects pooling. This text is new since v2 and was already in flight when the discrepancy was found on 2026-07-29 (see DECISIONS.md). No computed result is affected: Study B's record is NOT_ESTIMATED and no target data exists, so this misdescribes a planned estimator rather than reporting a wrong number. Queue it with the font-bundle change that DECISIONS.md already defers to v4.

## Canonical Local State

The repository state remains canonical for project and job-market use. arXiv v2 was built from the repository manuscript as of 2026-07-15; where they have since diverged, the repository governs.

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

- `adversarial-pragmatics-for-ai-safety-evaluation.tex`: empirical adversarial-pragmatics seed benchmark and pilot.
- `supplement.tex`: schema, item inventory, protocol, reproducibility notes, and sanitized pilot summaries.
- `delegation-assurance.tex`: framework paper on status, priority, licensing, and evidence standards for delegated machine action.
- `evidentiary-assurance.tex`: governance/legal assurance paper on action-level evidence bundles and review.

On 2026-07-20, the official Hinkle automated-vehicle testimony and introduced H.R. 7390 were integrated as a targeted case in Delegation Assurance and Evidentiary Assurance. Study B now records a fictional controlled-reconstruction hook for institutional force. Study A is unchanged, and this work supplies no collection authorization. Both primary sources are archived in the central literature directory.

On 2026-07-22, Evidentiary Assurance was revised against an external major-revision review, targeting an AI-governance journal. Now 32pp. The substantive change is that bearer and forum verdicts are indexed to a named candidate (`J_B(z)`, `J_C(f)`) and a family counts as satisfied only if one candidate carries the whole required conjunction; the previous flat node vector let a review report an answerability chain no party occupied, and that defect was live in the schema, not only the prose. A fifth node status, `not_established`, separates an unevaluable record from an adequate record whose showing falls short, and undercutting defeaters are barred from yielding substantive defeat. The artifact carries 20 fixtures (up from 16), 24 analyzer self-tests (up from 19), a new binding stamper with a pre-review freeze guard and its own tests, and node-specific evidential standards. Assurance-case, audit-evidence, and accountability literatures added (ISO/IEC/IEEE 15026-2, PCAOB AS 1105, Porter et al., Bovens), all archived centrally with hashes; RFC 6962 replaced by RFC 9162 in both assurance papers. The reviewer's proposal to split the projectibility material into a companion paper was rejected. Study A and the flagship are untouched.

On 2026-07-21, OpenAI's first-party report on long-horizon model safety was integrated as a bounded construct-design case. The flagship now separates source uptake, contiguous occurrence, declared recoverability, reconstruction/use, and downstream effect; Delegation Assurance separates authorization paths from bounded execution trajectories and repairs non-amplification to be grant-relative; Evidentiary Assurance adds trajectory, monitor-intervention, incident-lineage, and selected-replay records. Study B records a harmless static recoverability hook and a static-to-live projection threat, but its current schema and fixtures remain unchanged. Study A remains untouched. The complete cited page and a readable derivative are archived centrally; the source doesn't support prevalence or safeguard-efficacy claims.

## Public-Version Gap

Closed on the arXiv side: v2 (replacement `submit/7830880`, submitted
2026-07-15 UTC, announced public 2026-07-16) was built from the repaired
repository manuscript ~-- eight eligible paired contrasts plus one diagnostic
contrast, 12/24 eligible paired-contrast passes, no uniform
strict-minimal-pair claim ~-- and fixed the v1 font-load failure by bundling
fonts at the package top level (see `submission/arxiv/README.md`).

Still outstanding for a numbered archival release:

- tag a numbered GitHub release from the same commit;
- archive that release with a DOI if external citation is expected.

## Build And Checks

Use XeLaTeX.

```bash
make
make all-papers
make test
python3 .house-style/check-style.py adversarial-pragmatics-for-ai-safety-evaluation.tex delegation-assurance.tex evidentiary-assurance.tex supplement.tex
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
- **2026-07-28: HREB replied (REB Coordinator Suzan Abdelkarim, 17:42:18 UTC).**
  Determination: the six experts are not human research participants under
  TCPS 2 Article 2.1, because the design does not require them to provide
  their own data or respond to interventions from the researcher — they
  evaluate fixed AI-output objects. This answers only the participant-status
  question; the jurisdiction/auspices question was not asked in the sent
  version and HREB's reply does not address it. Per the inquiry record's own
  criterion, that leaves the collection gate not yet formally passed on the
  HREB dimension — a follow-up asking the jurisdiction question directly, or a
  deliberate decision to treat the current reply as sufficient, is Brett's
  call to make, not to be inferred. Full record:
  `notes/study-a-hreb-determination-record-2026-07-28.md`. Evidence preserved
  at `private/study-a/production/evidence/hreb-scope-determination-received-2026-07-28.eml`
  (ignored, mode 0600, SHA-256 `f5b3b04a17150763185c09e27ef946cc77b3f926c4740ef9fd16476855de1837`).
  **Brett's decision (same day):** no jurisdiction follow-up will be sent — as
  a Humber employee he is never "off duty" for ethics purposes, matching his
  own 2026-07-16 annotation on this exact question, so the omission from the
  sent email doesn't reflect real doubt on his side. This resolves the
  HREB/ethics dimension of the collection gate. It does **not** make Study A
  collection-ready by itself: `study-a-collection-launch-decisions-2026-07-16.md`
  §8's remaining steps (finalize evaluator materials, operational config,
  timing runs, assignment registry + attestation, verified freeze stamp,
  explicit tag authorization, then tag + `make study-a-collection-ready`) are
  unaffected and still outstanding. No recruitment, package distribution, or
  external collection authorized yet.
- A fresh local stamp-2 production candidate was rebuilt and semantically
  verified on 2026-07-16 after the object-only and gate-v3 repairs. Freeze
  readiness passes. This public-project commit is not the Study A freeze tag;
  collection readiness still fails closed because there is no authorized tag,
  operational config, Humber evidence, real assignment registry/attestation,
  or identity-side roster review. Rebuild and re-stamp after implementing any
  Humber conditions; no tag or external opening has been authorized.
- The real-history pragmatic-extremes derivative has been rebuilt as a
  privacy-minimized v2 corpus plus a separate owner-only linkage vault. The raw
  v1 derivative and a second older derivative were aggregate-audited and
  deleted. V2 contains 477 pseudonymized retrieval candidates and 300 minimized
  internal-review rows; deterministic validation and a 60-row contextual audit
  found no retained direct identifier or credential-pattern match in review
  text, but contextual reidentification risk remains. It is internal-only, not
  anonymous or public safe. Any public case requires a new controlled reconstruction and a separate
  scope decision. Exact record:
  `notes/naturalistic-corpus-privatization-record.md`.
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
- If the trajectory/recoverability hook advances beyond design, first specify a new schema and independently review the harmless four-arm reconstruction. Keep the static recognition query separate from any live, horizon-indexed tool harness; freeze the trajectory boundary, observer and transform, opportunity count, child-session and tool affordances, monitor intervention, and pause, operational-continuation, normative-release, restart, and stopping rules before collection.
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
- Added a fixture-only local repair-episode miner and review page. This was the
  active boundary on 2026-07-10; it was superseded on 2026-07-16 for a private,
  authorized Codex/Claude candidate-corpus build. Raw records, bounded episodes,
  provenance, and review decisions remain under ignored `private/` paths.

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

## 2026-07-21 Projectibility and validity excellence revision

- Completed the coordinated major revision of *Adversarial Pragmatics*, *Delegation Assurance*, and *Evidentiary Assurance* under a projectibility-first, Messick-informed validity framework. The three papers remain stand-alone: AP owns the pragmatic measurement layer, DA the normative authorization layer, and EA the evidentiary review layer.
- Added a shared typed-claim vocabulary, projective-claim schema and validator, prospective claim registers, a two-pass load-bearing-claim audit, and a dated six-standpoint adversarial stress-test record.
- Closed the Study B false-pass routes with manifest-bound production eligibility, exact repeat inventories, per-base main-reference gates, per-arm shortcut references and evaluability gates, and 19 permanent analyzer regressions. The committed result remains `NOT_ESTIMATED`; no target outputs were created.
- Made DA's distinction among normative reference, representation, proposal, gate, execution, result, and assessment use executable. Seven stipulated traces and hidden oracles, five semantic mutations, and three separate empirical-programme analyzers pass; no target-study outcome is claimed.
- Made EA's four verdict vectors, prospective applicability, immutable-key opening boundary, 16 controlled cases, substantive contrast-coverage requirement, and three noncompensatory use claims executable. Nineteen analyzer self-tests pass; with zero genuine reviewer responses, every use remains `NOT_ESTIMATED`.
- Verified all 80 unique cited sources locally and cleaned bibliography metadata. Final builds are AP 23 pages, DA 35, and EA 25; ordinary Biber and house-style checks pass, and visual QA removed three near-empty pagination artifacts.
- Study A's data, code, and frozen analysis paths were unchanged. The executable Stage-5 exit is met, but external gates remain: independent Study B references and target runs; DA's three target programmes and institutional comparison; and EA's genuine blinded reviewer study and forum-specific review.
- No commit, tag, push, recruitment, collection, unblinding, or target-data generation was performed in this revision.

## 2026-07-22 Filename and outreach-preparation session

- The projectibility-first assurance revision described above was subsequently committed and pushed as `95e927b`.
- Renamed the Adversarial Pragmatics entry point and generated artifact family from generic `main.*` names to `adversarial-pragmatics-for-ai-safety-evaluation.*`. Delegation Assurance and Evidentiary Assurance already had useful filenames and remain unchanged; the supplement remains `supplement.*`.
- Updated the Makefile, validators, cited-source scanner, project instructions, status and workflow references, source hook, arXiv bundler, and submission metadata. The regenerated arXiv package uses `adversarial-pragmatics-for-ai-safety-evaluation.tex` as its first top-level source. Historical records and one external project's genuine `main.tex` path remain unchanged.
- Forced fresh XeLaTeX/Biber builds produced AP 23 pages, DA 35 pages, EA 25 pages, and the supplement 10 pages. House style, `make assurance-check`, final-log scans, an independent filename audit, and clean-extraction arXiv builds all pass. The rebuilt DA and EA hashes were refreshed in the cited-source archive.
- Drafted `correspondence/2026-07-22-trustai-founder-outreach.md`: a product-specific false-green stress-test proposal leading, if there is interest, to a bounded paid two-week pilot on one harmless shadow ERP/MCP workflow. No outreach was sent in this session.
- The filename rename, its reviewed plan, the TrustAI draft, and other pre-existing untracked working files remain uncommitted. No tag, release, recruitment, collection, unblinding, or target-data generation occurred.

### 2026-07-24 Session Notes
One long session (2026-07-22 to 07-24), all on Adversarial Pragmatics (AP); Delegation/Evidentiary Assurance touched only as siblings.

- **Pairwise cross-section audit** of all three papers via 8 read-only subagents (full within-paper pairwise + selective cross-paper); findings applied. Added an `omitted_information` failure-attribution label across the codebook, validator, review app, rater-training, and AP §2/§3.
- **Two external-review rounds (major → minor revision).** Verified every reviewer claim against source; the sharpest was refuted: on AP-SEED-009 the models split BLUE/BLUE/GREEN rather than converging (stronger evidence of referential underdetermination than the reviewer's mechanism; reference NOT revised, routed to Study A output-blind). Found from the CSV that **all nine seed pairs change the response act**; renamed the statistic **joint pair completion**; added an 18-item inventory table; added a six-benchmark comparator table (IHEval + InjecAgent added to `references-local.bib`, verified against arXiv + ACL Anthology; Tensor Trust already present).
- **Statistics made Gelman-clean.** Item-clustered bootstrap intervals (four of six kappa CIs include zero). A **3×2 judge experiment** (glm + mistral-7b + mistral-24b × expected-behaviour visible/withheld; new `compact_no_rubric` prompt variant) overturned an earlier claim (the disjoint 24b is the strongest cell). **Eight-schools partial pooling** shrinks the one eye-catching rubric effect from +16.7 to +9.7 [−1.8, 25.7], interval through zero, robust to prior scale (`scripts/rubric_effect_partial_pooling.py`).
- **Retitled** to "…A Diagnostic Framework and Seed Benchmark for Language-Mediated Control" across 12 files incl. the `reynolds2026adversarialPragmatics` bib key the siblings cite. arXiv v2 still carries the old title → **v3 needed** before sibling cites resolve.
- **Released** raw model outputs, run metadata, all six judge runs' per-row labels, and the interval/pooling scripts; adjudication exports stay excluded.
- **Study B gates re-derived** from threshold gates to a pooled estimand (mean-nuisance subtraction, no lower-bound gate, DerSimonian–Laird cross-family pooling; correctness kept as evaluability screens). `analyze_study_b.py`, `claim-register.json`, tests, and the excellence validator updated; `make validate-study-b` green; committed no-target record still `NOT_ESTIMATED`.
- **Claude Code security docs** read and mapped to all three papers (`notes/claude-code-security-mapping.md`, gap-setup framing); AP intro tightened against the "old hat" exposure (lead with linguistic + four-bearer typing, not provenance-binding). **Integral vs non-integral citation pass**: three OpenAI-as-subject cites → `\textcite`.
- **Build:** AP 32 pp, supplement 13 pp, both clean, 0 undefined.
- **Commit state:** shipped through `e8e5c8d` (Gelman/partial-pooling pass). **Uncommitted:** Study B analyzer re-derivation, security-docs mapping + two `@online` bib entries, intro tightening, integral-citation pass, this STATUS/DECISIONS update.
- **Blockers/outstanding (Brett's calls):** frozen release tag / commit hash / archival DOI; arXiv v3 (retitle); `\citep` (8) vs `\parencite` (33) normalization choice; placement of the drafted DA/EA security-docs insertions (not placed — the other session edits those). `make assurance-check` fails only on a stale `delegation-assurance.pdf` hash from the concurrent session's DA revisions, not AP work.

## 2026-07-24 Evidentiary Assurance review rounds, interval analyzer, bib fix, ship

- Took Evidentiary Assurance through two external-review rounds (major → minor revision), AI-governance-journal target. Entity-indexed J_B(z)/J_C(f) with single-entity conjunction (fixing a defect that was live in the schema, not just prose); added `not_established` as a fifth status with a precedence rule; typed S_action/E_action/E_external; repaired the illustrative use rule and the worked-case action ontology; designated EA-MC-019 an exposed demonstration fixture and added blinded twin EA-MC-023; added assurance-case, audit-evidence, and accountability literatures; renamed J_C object-forum capacity; RFC 6962→9162. Tag `evidentiary-assurance-r2`.
- Replaced the calibration analyzer's PASS/FAIL cliff with a Jeffreys posterior-interval decision (MEETS / EXCEEDS / INDETERMINATE), following Gelman & Stern 2006 and Brown, Cai & DasGupta 2001. Design-analysis number now stated in the paper: ~49 clean observations to demonstrate a 0.05 error ceiling, so the illustrative reach of 12 is a coverage floor only.
- Bibliography: diagnosed that /push-bib moves entries to the central house bib without refreshing the repo's vendored references.bib, which broke all builds; refreshed references.bib as a full mirror of central (2162 entries), slimmed references-local.bib to un-pushed entries, added `make vendor-bib`. Collapsed a duplicate Gelman-Carlin key in the delegation paper; made three OpenAI/Hinkle citations integral; archived and verified eleven statistics/accountability sources against their first pages.
- Shipped all three papers to public origin/main on 2026-07-24. `/ship` also committed the flagship's uncommitted Study B work as b2819fb (coordination note left for that agent). Final builds clean: AP 32pp, DA 39pp, EA 34pp, supplement 13pp; `make assurance-check` green.
- Still open for EA: no venue decision record; artifact statement promises a DOI-at-publication that does not yet exist.

## 2026-07-24 Delegation Assurance: venue decision, Gelman pass, analyzer coherence, polish

Focused session on `delegation-assurance.tex` (targeting *Minds and Machines*), responding to two external review rounds.

- **Venue: Minds and Machines**, approved by Brett; journals only, no conferences. Record in `submission/venue-decision-2026-07-22.md` with alternatives (JCS, JRT, AI Magazine, AI&Law, AI&Ethics), disqualifications, and risk analysis. Chosen over Journal of Computer Security because the paper has no threat model/attacks/defences, so a security venue would be a topic-not-reader match. The sweep's "no M&M agent-authorization conversation" claim was a query artifact; the journal's real 2025+ output (86 articles) is a dense conversation, and Rashid 2026 (M&M 36:30) poses this paper's question and leaves it open.
- **Page one reaimed** at the M&M readership: opens on Rashid's threshold and the persons-vs-authority contrast (MHC/oversight/accountability specify conditions on people, none on authority), trajectory non-entailment promoted to p.1, security opening and Dams Safety NSW genealogy demoted. New §2.3 engages Santoni de Sio & van den Hoven, Sterz et al., Novelli et al., Nguyen et al. (all read, archived centrally).
- **Round-2 fixes**: withdrew two overclaims I'd introduced (the persons/authority sentence asserted the gap over a literature that fills it; the per-call negative was unevidenced); located the artifact (§8, commit `95e927b`); defined "typed" (reviewer's option over a retitle); fixed Alloula author order.
- **Gelman-facing statistical revision of §3.6**: built and ran a design analysis by simulation (`scripts/design_analysis.py` + tests + Makefile `design-analysis`), reporting Type S/M and coverage. Retired every LCB-gate, the ten-bin ECE screen, and max-of-two-SEs; replaced with partial-pooling / t-or-multilevel / crossed-variance estimands, decisions tied to declared losses. Four Gelman citations verified.
- **Analyzer coherence**: reimplemented the 838-line `analyze_delegation_programs.py` to compute estimate-and-interval (dispatched to gpt-5.6-sol via codex, verified independently); closed the PASS/FAIL output-schema residue; synced prose. 17 analyzer + 5 design-analysis tests pass; `make validate-delegation` green.
- **Polish**: removed editorial scar tissue (changelog framing) from §3.6/§8; fixed three integral-vs-non-integral citation doublings (South, Kühlewind & Birkholz, Hinkle).

State at session end: delegation-assurance builds clean, 39 pp, 0 undefined citations. **Open for Brett**: whether to normalize `\parencite`/`\citep` across the three-paper suite; the M&M portfolio conflict (Truth-Tracking Profiles and the AGI-evaluation paper also point at M&M); and the round-1 items still deferred (non-amplification as a history-sensitive relation, institutional-mode worked case, content-interpretation fifth field). Heavy concurrent multi-session activity in this repo this session (one references-local.bib clobber-and-recover); verify before assuming any single file's state.

## 2026-07-29 External adversarial code review, and the seven repairs

An external reviewer was given the executable artifacts with one brief: can you make any
analyzer or validator emit a false pass? Seven attack families, all reproduced, and I
reproduced all seven independently before accepting the report. The reviewer's diagnosis
of the set: several checks established internal consistency while their output labels
implied stronger semantic, temporal, or procedural assurance. Verdict was to keep
developing the papers but hold the immutable software release.

All seven are now closed and the reviewer's own unmodified script returns 0/7 (its
SHA-256 was checked against the filed copy, so the suite was not gamed). Test count went
from 91 to 127 across eight suites, each attack having become a standing regression.
Repairs, in the reviewer's order: chronological authority-state evaluation so a revoked
parent can no longer confer child authority; a calibration rule under which near-total
abstention cannot pass and required-node NOT_ESTIMATED blocks a use-level pass; evaluator
views constructed from recursive typed contracts with the presented bytes digested,
replacing banned-key-name scanning; externally anchored prospective claims; Study B
validating required Cartesian cells and recomputing digests from item bytes; and the
stamper separating permanently available read-only checks from closed writes.

Study B's estimator was ported to the multilevel model the supplement already described,
resolving that paper/code discrepancy in the paper's favour on Brett's call: DerSimonian
-Laird estimates tau-squared by method of moments and then treats it as known, which
understates uncertainty badly at four families. It follows the eight-schools
implementation already in the repo, extended to two-dimensional quadrature so pooling runs
across families and bases as the paper says.

**Resolved same day.** DA's three claims were migrated to `status: proposed` with
`declaration_timing: repository_anchored_target_chronology_not_established`, and
`assurance-check` is green. That enum value is the honest one: the claims are anchored in
the repository's Git history, but no target inventory has been fixed, so prospectivity is
not established. The stronger values require a digested target inventory checked at both
HEAD and the anchor commit, which DA cannot supply because the items each programme will
run on have never been enumerated. Building those inventories is real design work and
would make the claims genuinely prospective; until then this is what is true.

**Open for Brett: the word "frozen" now carries two senses.** `sections-delegation/07-conclusion.tex`
says the specifications are "frozen before any target outcome", which is true and
Git-verifiable of the specifications. The claim register's `frozen` status now means
something stronger, anchored plus a fixed target inventory, which those claims do not
meet. Two senses of one word across paper and artifact is exactly the label problem the
review was about, and it wants either a different word in the paper or a sentence
distinguishing them.

Superseded note, kept for the record: **`make assurance-check` was red, and correctly so.** The hardened projective-claim schema
rejects `assurance/delegation/projective-claim-register.json`, whose three claims
self-attest `declaration_timing: before_target_outcomes` and carry no `repository_anchor`
or structured `target_selection`. That self-attestation was the vulnerability, so the
failure is the repair working. Migrating those three claims needs genuine anchors and
honest inclusion rules, not a schema shuffle, and it is the next task. The evidentiary and
Study B registers already pass.

Held until that closes: the `delegation-assurance-r1` and `evidentiary-assurance-r3` tags,
and therefore the two assurance preprints, whose artifact statements name them. Not held:
Adversarial Pragmatics, whose benchmark, pilot, and judge results run through none of this
code, and whose JAIR submission is the next available piece of work.

Review, reproduction script, results, bypass fixture, and the exact reviewed package are
preserved with hashes under `reviews/code-review-20260729/`.
