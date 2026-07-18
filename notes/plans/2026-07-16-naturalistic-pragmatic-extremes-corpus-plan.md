# Naturalistic Pragmatic Extremes Corpus: Build Plan

**Status:** superseded on 2026-07-16 by the privacy-minimized v2 design and the
completed record in `notes/naturalistic-corpus-privatization-record.md`. The v1
raw derivative described below was aggregate-audited and deleted.

## Decision
Build a private, provenance-preserving corpus from Brett's local Codex and Claude Code records with two candidate classes:

1. **likely pragmatic failures**: episodes containing strong evidence that the model misunderstood or failed to respect the operative request, authority, scope, reference, repair, or reporting obligation;

2. **surprising pragmatic successes**: episodes combining evidence of successful uptake with unusually high pragmatic load.


These are retrieval classes, not gold labels. The corpus will preserve ambiguity and competing explanations rather than converting user correction or praise directly into ground truth.
## What the Source Check Established
- Local records are available: roughly 3.2 GB of Codex sessions and 497 MB of Claude project records.

- Both formats preserve event structure beyond chat text. Codex includes developer/user/assistant messages, turn context, compaction summaries, tool calls, and tool outputs. Claude includes user/assistant messages, tool use and results, attachments, permission state, and file-history snapshots.

- The current project alone appears in 104 Codex session files and 38 Claude files including subagents. This is enough to test the adapters, but the corpus should sample across projects rather than make this paper's own development history the whole source.

- Explicit positive-assessment signals occur often enough to support a success retrieval channel. They will need contextual filtering because ordinary praise is not evidence of a difficult pragmatic success.

- The existing repair miner is suitable as a conceptual prototype, not as the production parser: it assumes a user--assistant--user sequence, drops system context, truncates aggressively, and does not reconstruct tool-mediated action.

## Load-Bearing Assumptions
| Assumption | Falsification condition | Design response |
| --- | --- | --- |
| Explicit repairs retrieve genuine pragmatic failures at useful precision. | Most sampled hits are changed requests, factual errors, or reasonable ambiguity. | Preserve those classes and expand retrieval to action reversal, repeated constraints, and repair non-uptake; do not report a failure rate. |
| Surprising successes are observable in the logs. | Positive language is mostly politeness, or successful episodes receive no explicit acknowledgment. | Require both success evidence and pragmatic-load evidence; retain evidence strength and audit a sample of high-load episodes without praise. |
| Full visible context can establish the operative instruction. | Required system state, UI action, hidden prompt, or external artifact is missing. | Label the episode `insufficient_visible_context`; never infer a violation from the chat fragment alone. |
| Codex and Claude episodes can share one event schema. | Important platform-specific state is lost in normalization. | Use a common core plus source-specific event payloads; preserve raw provenance and adapter version. |
| A private corpus can be constructed without creating a release hazard. | Candidate windows contain third-party text, secrets, proprietary code, identifying paths, or reconstructable context. | Keep all raw and normalized material under ignored `private/`; public derivatives must be newly written, benign controlled reconstructions. |

The strongest inversion is that a repair-rich corpus may primarily measure **Brett's detection and correction behaviour**, not model failure. The corpus therefore supports phenomenon discovery and controlled-item generation, not prevalence estimates or clean Codex--Claude comparisons.
## Sampling Frame
- Include primary Codex and Claude Code sessions dated **2026-01-01 through 2026-07-15**, across local projects.

- Exclude the current active session, synthetic fixtures, explicit test logs, and standalone subagent transcripts in the first pass. A parent episode may retain a subagent result when it was visible to the user and causally relevant.

- Preserve source, date, software/model version when recorded, project as an opaque hash, session as an opaque hash, and raw event offsets.

- Do not force equal source counts and do not interpret source differences as vendor performance differences.

- Retain every high-confidence candidate in the private retrieval queue. Build a review corpus capped at three episodes per session and stratified by source, polarity, phenomenon, and month so a few long sessions cannot dominate it.

## Episode Model
Each episode should reconstruct, when available:

```text
governing instructions and relevant state
    -> triggering request
    -> visible model interpretation, message, or action
    -> tool results and artifact effects
    -> user repair or uptake evidence
    -> immediate model response to that evidence
```

Do not extract hidden reasoning or encrypted reasoning fields. Store only visible interaction records and operational metadata needed to interpret them.
## Retrieval Class A: Likely Pragmatic Failure
Candidate evidence includes:

- explicit correction of interpretation, reference, file, scope, or requested action;

- `stop`, `undo`, `revert`, or equivalent immediately after an agent action;

- repetition of a previously stated negative constraint after apparent non-compliance;

- correction that the agent reviewed when asked to edit, edited when asked to diagnose, or acted when asked only to answer;

- challenge to a completion, causation, permission, or status claim;

- failure to incorporate a user repair on the next turn;

- artifact evidence that the action exceeded or missed the requested scope.


Each candidate receives an evidence-strength score and one provisional alternative explanation: `reasonable_competing_reading`, `clarification_needed`, `user_changed_request`, `lost_or_hidden_context`, `non_pragmatic_error`, or `insufficient_evidence`.
## Retrieval Class B: Surprising Pragmatic Success
A success candidate requires both:

1. **uptake evidence**, such as explicit positive evaluation, confirmation of the interpretation, verified artifact/test success followed by acceptance, or a dependent next instruction that presupposes correct completion without intervening repair; and

2. **pragmatic-load evidence**, such as long-distance reference, multiple instruction sources, an override or negative constraint, a diagnose/edit boundary, action authorization, recovery after compaction, correction of an earlier misunderstanding, or a multi-stage stop condition.


`No complaint followed` is never sufficient on its own. The corpus should call these `surprising_success_candidate` rather than `unlikely_success` until review.
## Provisional Phenomenon Families
- reference and ellipsis resolution;

- speech-act or task-type recognition;

- scope and authorization;

- instruction source, priority, and authority;

- negative-constraint persistence;

- repair uptake;

- cross-turn state and compaction recovery;

- completion, causation, and status reporting;

- tool/action consequence alignment;

- non-pragmatic or insufficient-evidence control.

## Private Outputs
```text
private/discovery/naturalistic-pragmatic-extremes-v1/
  corpus-manifest.json
  source-index.jsonl
  normalized-events/
  all-candidates.jsonl
  review-corpus.jsonl
  provenance-index.csv
  review/
    index.html
  reports/
    retrieval-audit.json
    corpus-profile.md
```

`review-corpus.jsonl` will contain bounded raw context and therefore remains private. The profile may summarize retrieval mechanics and candidate counts locally, but those counts are not paper results.
## Implementation Sequence
1. Specify and test a common event schema with synthetic Codex and Claude fixtures covering messages, tool calls/results, compaction, permissions, and file effects.

2. Implement streaming, read-only adapters for primary Codex and Claude session records. Hash identifying provenance in corpus rows while retaining a separate private linkage index.

3. Implement deterministic failure, uptake, pragmatic-load, privacy, and alternative-explanation signals. Keep every individual signal inspectable.

4. Run a small adapter and retrieval audit on a mechanically selected set of sessions. Inspect false positives and missed obvious cases before the full build.

5. Stream the fixed sampling frame, create the full candidate queue, and build the stratified review corpus.

6. Extend the existing offline review interface for polarity, evidence strength, phenomenon family, competing explanation, and privacy disposition.

7. Audit a random sample of retrieval misses so the report can distinguish signal precision from unknown recall.

## Checkpoints and Stop Conditions
- **Adapter checkpoint:** stop if visible governing context or action outcomes cannot be reconstructed reliably from either source.

- **Retrieval checkpoint:** continue to the full build only if each polarity yields at least 15 plausible cases in the small audit and the success channel is more than generic praise.

- **Privacy checkpoint:** stop public-derivative work if manual review cannot remove source-specific identity or proprietary context without destroying the phenomenon.

- **Scientific checkpoint:** the corpus remains discovery material unless a later protocol supplies independent review and controlled reproduction.

## Evidential and Scope Boundary
This pass creates a private candidate corpus. It does not add observations to the fixed 54-object Study A, estimate failure prevalence, compare vendors, or authorize verbatim publication. The HREB inquiry sent on 16 July describes only the six-expert evaluation of the fixed objects and should not be represented as covering this retrospective corpus. Any claim-bearing self-study, systematic corpus analysis, external annotation, or publication of naturalistic excerpts requires its own scope decision.
## Immediate Deliverable
The useful first outcome is not another paper. It is a private, reviewable contrast corpus that can support:

- controlled benchmark-item generation for a later version of this project;

- a small public casebook made only from benign synthetic derivatives;

- a later Study B on naturalistic-to-controlled coding-agent pragmatic evaluation, if the retrieval audit shows sufficient yield.
