# Phase 1 Findings: Freeze and Readiness Check

## Frozen Historical Artifact

The current 18-item, 54-output pilot is reproducible from the local ignored
run bundle. Its public-safe provisional-label snapshot and freeze manifest are
under `data/provisional/`. The freeze records that these are author-provisional
labels before external re-adjudication; it does not promote them to gold.

## Resolved Preparation Gaps

1. The original browser app is deliberately unblinded. It shows expected
   behaviour, model identity, diagnostic metadata, and historical labels, so it
   cannot be used for external Study A evaluation. A separate blind package
   now exists.
2. Historical source labels lived only in the ignored local run bundle. A
   public-safe label-only snapshot now preserves comparison fields without
   coder identity, browser metadata, full rationales, or raw outputs.
3. The repository did not reserve a clear location for private histories,
   opaque provenance maps, or evaluator-identifying files. `private/` and the
   ignored Study A run path now provide that boundary, checked by
   `make privacy-check`.

## Conditions Still Relevant Before Outside Evaluation

- P008 remains a diagnostic confidentiality contrast, not an eligible strict
  minimal pair. It must stay excluded from strict-pair claims until it is split
  into clean development-set pairs.
- AP-SEED-007 and AP-SEED-008 are also flagged for later revision or exclusion.
  Their conditional prohibition permits an output without clearly requesting
  one, so the current pair does not support a stable task-success contrast.
  This interface revision does not alter the frozen prompts.
- Existing `annotation-protocol.md` and `rater-training.md` describe the
  original author-pilot path. Blind Study A evaluators must use only the new
  role-specific schema and form.
- A full local self-pilot tested the interface and burden without creating
  Study A outcomes. The policy/safety blocks had a median of about 28 minutes;
  linguistic elapsed times were unusable open-tab wall clock. Evaluator-facing
  materials therefore use a conservative administrative estimate of 30--40
  minutes per 18-row block and exclude timing from research claims.
- Practice pages use six separate synthetic examples (three per role), show
  immediate explanations, and are audited to ensure that they do not duplicate
  blind study rows. They are orientation only: no score, gate, or study data.
- Resolved in schema v6: the scope/reference help now italicizes the mentioned
  expressions _this_, _that_, _the previous one_, _only_, _except_, and _not_.
- The unlaunched policy/safety form has been revised to ask about visible
  security-boundary status and type rather than low/medium/high deployment
  risk. This responds to pre-recruitment usability feedback without changing
  the frozen historical pilot.
- Study A is designed as expert evaluation of outputs, not research about the
  evaluators. HREB was asked on 16 July 2026 whether it regards the proposed
  experts as human research participants. External recruitment, package
  distribution, and return opening remain closed pending its written response
  and the collection gate.
- The synthetic workflow validates data flow, not judge validity, item
  stability, evaluator reliability, or any model result.
- Real source exports, real evaluator files, and identity mappings have not
  been imported and must not be committed.
