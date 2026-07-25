# Corpus follow-ups from the 2026-07-25 interjections session
<!-- SUMMARY: two open items on the naturalistic-pragmatic-extremes-v2 corpus: a detection blind spot for unopposed scope expansion, and no model/effort field on any entry · status: deferred, not started · updated: 2026-07-25 -->

Both surfaced on 2026-07-25 while Brett was working on a different project. Neither is started. Full analysis of the first is in `private/discovery/naturalistic-pragmatic-extremes-v2/reports/proposed-detector-unopposed-scope-expansion.md`.

## 1. Detection blind spot: unopposed scope expansion

`scope_and_authorization` exists as a phenomenon (n=33), but all 33 are found through **resistance signals** the user emits: `scope_or_file_correction` (10), `explicit_not_requested` (2), `instruction_repetition` (1), `completion_or_status_challenge` (1), plus generics. The entire `evidence_signals` vocabulary has that shape.

So the corpus can only find scope violations the user pushed back on. Cases where the user accommodated the expansion instead are structurally invisible, and there is no way from inside the corpus to estimate how many there are.

**The task for another time:** run an assistant-first-mention pass over the 155 sessions already held. For each task-object (file path, project directory, document name, citation key), record which side introduced it, then flag those the assistant introduced that went on to attract durable actions (`artifact_change`) and were taken up in the user's later turns. The number of unopposed cases the resistance-gated method missed is the result worth having, and the material for it is already on disk.

Seed specimen (assistant = Claude Opus 5, session 2026-07-25): a book-chapter pagination fix expanded into a full multi-commit citation rewrite of an unrelated paper, across seven turns, with no user objection at any point, the frame surfacing only when Brett asked "when did we start looking at the metaphor paper?" No existing signal fires anywhere in it.

Also needs a third `candidate_class`. The current pair is `likely_pragmatic_failure` / `surprising_success_candidate`, and this episode is neither: an output-oriented scorer codes it a success, because the work was completed, verified and accepted. Something like `accepted_output_exceeded_mandate`.

## 2. No model or effort recorded on any entry

Checked 2026-07-25 across both files. Neither `candidate-index.jsonl` (477 rows) nor `review-corpus.jsonl` (300 rows) carries a model or effort field. The only model-ish keys are `model_visible_response` and `immediate_model_response`, which hold response text. Provenance granularity is:

- `source`: `codex` 438 / `claude` 39
- `session_mode`: `cli` / `interactive`, perfectly correlated with `source`, so it carries no independent information
- `month`

**Why this bites.** "claude" spans Opus 4.x through Opus 5 over the Jan--Jul 2026 window, and the workspace deliberately downshifts models per skill (`/validate-bib` and `/check-style` to haiku, `/ship` to sonnet), with effort dropping to low or medium alongside. A single session can therefore contain several models at several effort levels, and a candidate drawn from a downshifted skill is currently indistinguishable from one drawn from the session's headline model. A haiku-at-low-effort artifact and an Opus-at-xhigh artifact are both filed as "claude".

That blocks the questions most worth asking of this data: whether pragmatic failures track capability, whether they are diminishing across model generations, and whether reasoning effort mitigates them. Without those fields the corpus supports "this happens with LLM assistants" and not much more. The adapter already records a run-condition variable of exactly this kind in `compaction_before`, so the concept is present; model and effort belong in the same family.

**Recoverable, but decaying.** Session transcripts record the model per request, and the manifest says exact source linkage is kept separately under the restricted boundary. So model and effort can be back-filled by adding the fields and re-running the adapter, provided the linkage table and the original logs survive. This gets harder as logs age out, which argues for doing it before the next corpus build rather than after.
