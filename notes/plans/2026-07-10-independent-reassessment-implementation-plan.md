# Independent Re-adjudication and Private Discovery: Implementation Plan

**Historical status:** the fixture-only stopping rule in Phase 4 was superseded
on 16 July 2026 for an explicitly authorized, ignored private Codex/Claude
candidate-corpus build. The prohibitions on treating retrieval candidates as
gold labels, publishing raw histories, estimating prevalence, or deriving
public benchmark items without further review remain active.

## Decision
Treat the current 18-item, 54-output pilot as a frozen historical artefact. Its author labels remain available for comparison, but Study A will collect independent, blind, criterion-specific ratings without overwriting or exposing them.

The immediate goal is a small, reproducible workflow that can be run with synthetic data now and real external ratings later. It is not a scaled benchmark expansion or a recruitment campaign.
## What Already Exists
- A validated 18-item seed set and a 54-output local-pilot bundle.
  
- Author adjudications, diagnostics, a browser review app, ingestion, reporting, and judge-validation scripts.
  
- Synthetic calibration tooling, but not a blind role-separated study workflow.
  
- Git ignores generated result bundles, but no explicit protected local-only area for private histories or evaluator-identifying material.
  
## Load-Bearing Assumptions To Test
| Assumption | Fast test / safeguard | What changes if it fails |
| --- | --- | --- |
| The historic pilot can be reproduced without changing labels. | Freeze checksums and regenerate reports in a temporary copy. | Repair or document the inconsistency before external review. |
| A blind package can support task and policy judgments without expected-behaviour fields. | Generate role-specific synthetic packages and inspect their payloads for prohibited fields. | Narrow or clarify the first-pass criteria; do not leak author expectations. |
| Separate roles produce data that can be rejoined without evaluator identity disclosure. | Use opaque row IDs, pseudonymous rater IDs, and local-only response folders in the synthetic run. | Revise the response schema and storage boundary. |
| Repair turns can retrieve useful candidates without becoming labels. | Run fixture corpus through local-only miner and inspect ranked episodes. | Change retrieval signals or review categories, not the substantive taxonomy. |
## Phase 1: Freeze the Current Pilot
1. Add a versioned freeze manifest for the seed file, outputs, author responses, and existing readout.
  
2. Add a check that verifies row counts, item/model coverage, complete author labels, and the manifest digests.
  
3. Regenerate reports in a temporary copy and compare the resulting public summaries with the tracked canonical summaries.
  
4. Add an explicit local-only `private/` boundary and a privacy check that rejects tracked private-history or evaluator-response paths.
  
5. Record any pre-existing exposure or inconsistency without changing reported pilot results.
  

Checkpoint: do not alter source labels, the published pilot readout, or the current manuscript statistics.
## Phase 2: Blind Independent Re-adjudication (Synthetic First)
1. Add a Study A schema with separate `linguistic_task` and `policy_safety` forms.
  
2. Build an offline blind-package generator that takes an output bundle and emits role-specific HTML/TSV materials with opaque `row_id` values. It must omit model identity, expected behaviour, author labels/rationales, automated-judge labels, and outcome-derived diagnostic fields.
  
3. Use a first-pass design that defers `failure_attribution`: attribution depends on stable task/policy reference labels and should be a later, separately recorded adjudication stage rather than an imposed first-pass judgment.
  
4. Add response ingestion and analysis that preserve every first-pass rating, distinguish roles, rejoin only through a local mapping, and report agreement, author-label revision, class-specific judge performance, cross-role conflicts, instability, and phenomenon-level results.
  
5. Add a complete synthetic fixture generator and a one-command smoke workflow that builds packages, simulates ratings, runs analysis, and checks for blind-field leakage.

6. Include optional, role-specific practice pages with separate synthetic examples, plain-language labels, immediate explanatory feedback, no pass threshold, and no study-data collection. Retain only coarse block timing in real response payloads so evaluator burden can be tested before recruitment.
  

Checkpoint: synthetic outputs are explicitly labelled synthetic. No real evaluator result, author-label revision, or empirical claim is created by this phase.
## Phase 3: Draft-Only Scope, Evaluator-Agreement, and Outreach Materials
Create clearly marked drafts for:

- Study protocol and evaluator burden.
  
- Private-discovery-corpus description and privacy/release boundary.
  
- Evaluator information and agreement text.
  
- One-page independent-adjudication description and short recruitment notice.
  
- Tailored outreach drafts for Humber/U of T, Trajectory Labs, AIGS Canada, SPAR, and post-validation Encode.
  
- A skeleton two-page policy brief, `Minimum Integrity Requirements for AI Safety Evaluation`.
  

No messages are sent, no institutional determination is claimed, and no study is represented as launched.
## Phase 4: Private Naturalistic Discovery (Fixture-Only)
1. Define a simple local JSONL normalization format for ChatGPT, Codex, and Claude Code exports.
  
2. Build a local-only repair miner that identifies correction-like turns, retains a bounded preceding-context/target/model/repair window, assigns opaque local provenance, and emits privacy/third-party-content flags.
  
3. Build an offline review page that lets Brett retain, reject, or classify candidate episodes without uploading them.
  
4. Include only a synthetic conversation fixture in the repository; real exports and outputs live under ignored `private/` paths.
  
5. Support the planned distinctions: clear misinterpretation, clarification required, reasonable competing readings, lost context, changed request, non-pragmatic error, and insufficient evidence; plus conversational versus action-scope failures.
  

Checkpoint: stop after the synthetic fixture workflow. Do not import any real history, build corpus statistics, or derive benchmark items.
## Phase 5--8: Scaffold Only
- Phase 5: add a controlled-derivative record template, not real derivatives.
  
- Phase 6: gate naturalistic-item review on completion of Study A.
  
- Phase 7: add placeholder reporting slots that require real external ratings.
  
- Phase 8: draft only the policy-brief structure, without results.
  
## Intended File Shape
```text
benchmark/study-a/
  README.md
  schema.md
  training-items.json         # separate practice-only synthetic examples
  materials/                 # draft, public-safe study documents
  fixtures/                  # synthetic rows and synthetic ratings only
  controlled-derivative-template.csv
private/
  README.md                  # tracked boundary notice; all other contents ignored
data/fixtures/
  synthetic-repair-history.jsonl
scripts/
  freeze_pilot_artifact.py
  check_pilot_integrity.py
  build_independent_reassessment.py
  ingest_independent_reassessment.py
  analyze_independent_reassessment.py
  simulate_independent_reassessment.py
  mine_repair_episodes.py
  build_repair_episode_review.py
  check_private_boundaries.py
```
## Completion Criteria For This Pass
- `make phase1-check` verifies the frozen 54-row pilot without modifying it.
  
- `make study-a-synthetic` runs an end-to-end synthetic blinded Study A workflow.

- The synthetic package includes and audits two separate practice pages, and
  synthetic ingestion/analysis retains block-burden timing.
  
- `make discovery-synthetic` creates and reviews a synthetic local-only repair-corpus run.
  
- Draft scope/recruitment/policy materials contain no claim of approval, recruitment, or result.
  
- Git and privacy checks confirm that no raw private history or evaluator-identifying response can enter the tracked artefact by default.
  
## Decisions Deferred To Brett
- Whether the blinded package can be shared as-is with external evaluators after the synthetic test and any needed scope determination.
  
- Which real ChatGPT, Codex, and Claude Code exports, if any, enter the private discovery workflow.
  
- The final evaluator count, data-return/withdrawal terms, and recruitment sequence.
  
- Whether any independently re-adjudicated item becomes revised, retained, ambiguous, or withdrawn after real ratings arrive.
