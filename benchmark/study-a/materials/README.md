# Study A Materials

Operational status is controlled by the stamp-2 manifest and operational
config, not by historical `-draft` filename suffixes. At the current stage,
every document in this directory is a preparation draft; none represents ethics
approval, recruitment, a funded study, or a result. To pass the collection
gate, the nine designated operational materials
must be finalized, free of draft or placeholder status language, complete under
their required sections and local dependency closure, and hash-bound to stamp
2. Internal planning notes, outreach drafts, and the self-pilot runbook remain
non-operational. Do not send an outreach draft or circulate an evaluator form
until Brett has reviewed the materials, tested the interface, obtained a
written Humber scope determination, and selected the information/agreement path
that determination permits.
Even then, distribution is barred until the verified stamp-2 candidate has
been committed, an explicitly authorized annotated freeze tag points at
`HEAD`, and the separate collection-ready gate passes.

Current planning posture: Study A is an unfunded project led by Brett Reynolds,
a Humber Polytechnic employee. HREB scope and review status remain pending.
Recruitment and collection are paused pending HREB's written response and
compliance with any conditions it imposes.

## Contents

- `study-protocol-draft.md`: protocol suitable for methodological review and
  the pending institutional scope determination.
- `private-discovery-corpus-statement-draft.md`: limits on private histories as
  a discovery corpus.
- `privacy-and-release-boundary-draft.md`: storage and release rules.
- `evaluator-information-and-consent-draft.md`: evaluator information and
  agreement draft, explicitly not a live participant-consent form.
- `evaluator-quick-start-draft.md`: plain-language orientation for evaluators;
  the generated forms link to a separate optional practice set.
- `withdrawal-procedure-draft.md` and `withdrawal-log-template.csv`: draft-only
  pre-analysis deletion workflow; any populated log remains local and ignored.
- `data-return-instructions-draft.md`: channel-neutral return procedure; it
  remains incomplete until the written determination/data plan permits a
  specific access-controlled channel and Brett sets the cutoff.
- `self-pilot-runbook.md`: local-only six-block usability and burden test; it
  explicitly excludes self-pilot labels from independent Study A analysis.

The current Study A response schema is version 7. The linguistic/task form
rates whole-prompt source-role relations with a multi-select field and records
clarity separately. It treats top-level, unattributed prompt wording as the
task giver's contribution and keeps task success separate from policy
compliance, asking the identification questions first and task success last.
The policy/safety form rates stated security-boundary status and type rather
than deployment-level severity, with policy compliance asked last; see
`../schema.md`, `notes/study-a-visible-boundary-revision.md`, and
`notes/study-a-schema-v7-form-review.md`.
- `independent-adjudication-one-page.md`: a shareable study overview.
- `recruitment-notice-draft.md`: a bounded call for evaluators.
- `outreach/`: tailored drafts; no contact is made by this repository.
- `minimum-integrity-requirements-outline.md`: a later policy-brief structure,
  with no fabricated results.

The actual blind package, private row map, evaluator responses, and any identity
mapping remain local and ignored under `private/` or `benchmark/study-a/_runs/`.
Production distribution artifacts are separate role-isolated ZIPs. A private
assignment registry binds internal person and rater keys to one role and
package ID. Its attestation proves byte integrity and identifier coherence only;
a separate investigator review of the identity-side roster establishes unique
eligible real people and person-disjoint role pools.
