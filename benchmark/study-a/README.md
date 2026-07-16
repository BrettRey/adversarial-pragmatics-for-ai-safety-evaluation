# Study A: Independent Re-adjudication

Study A is a blind, role-separated re-adjudication of the existing 54 pilot
outputs. It does not replace the original author labels; it creates an
independent evidence layer against which those provisional labels and the
automated judge can later be compared.

The first pass has two separate forms:

- `linguistic_task`: task success, whole-prompt source-role relations,
  source-role clarity, scope/reference, clarification need, and response-act
  performance.
- `policy_safety`: visible policy compliance, visible security-boundary status
  and type, refusal calibration, and information-flow/action-licensing
  concerns.

`failure_attribution` is intentionally deferred. Assigning a cause requires a
supported modal panel label on both task and policy criteria and should occur,
if needed, in a later documented adjudication stage rather than being forced
into every first-pass rating.

Each evaluator's intended assignment is full coverage of the 54 rows in their
one role, divided into three 18-row blocks. The workflow retains any completed
partial blocks and marks the rater-role coverage as partial. A modal panel label
requires at least two ratings for the relevant criterion, and two ratings must
agree.

## Evaluator Orientation

Generated packages include an optional practice page for each role. Each page
uses three separate synthetic examples, gives immediate explanations, records
no study data, and has no pass threshold. The actual forms use plain-language
option labels and short field help, while retaining the corresponding
machine-readable values in downloaded JSON. They also retain coarse
block-level timing solely to estimate evaluator burden.

The source-role question is multi-select and applies to the prompt as a whole.
Several clear roles may be selected without marking the prompt ambiguous;
clarity is recorded in a separate field. Top-level, unattributed prompt wording
is treated as the task giver's contribution, whether it is a request or a
question. Quotation marks that merely delimit supplied content do not make the
content wording under discussion.

Task success measures how fully the response performs the user-facing request
and its task-defining conditions. It does not incorporate compliance with a
stated policy, which the policy/safety role evaluates separately. The current
response schema is version 7 (identification-first question order, the global
judgment last, uniform escape options; see `../../notes/study-a-schema-v7-form-review.md`);
version 5 and 6 self-pilot files remain unchanged as pre-revision usability
evidence.

The practice material is defined in `training-items.json` and audited against
the blind rows at package-build time. It must never use real pilot rows,
withheld expected behaviour, author labels, or automated-judge labels.

The policy/safety form does not ask evaluators to rate deployment-level
severity, firewall quality, or real-world harm. It asks only what the visible
prompt-response record establishes about stated boundaries. The old pilot's
severity and risk-type labels remain historical and are not directly compared
to the revised first-pass fields.

## Blindness Boundary

External evaluators receive opaque row IDs, prompt text, model response text,
their role-specific rubric, and no other row metadata. They do not see model
identity, item/pair identity, phenomenon family, expected behaviour, original
author labels or rationales, automated-judge labels, or outcome-derived
diagnostic fields.

Real packages, row maps, responses, and any rater identity mapping live under
ignored paths in `private/`. `benchmark/study-a/_runs/` is also ignored so the
synthetic workflow can exercise the same file shape without adding responses
to the repository.

## Current State

The repository currently supports only a synthetic end-to-end run:

```bash
make study-a-synthetic
```

This generates synthetic source rows and ratings, builds both blind offline
forms, joins pseudonymous synthetic responses locally, and writes analysis
tables. It does not constitute an empirical study result.

To inspect and time the actual 54-row interface without creating an
independent-rating submission, run:

```bash
make study-a-self-pilot
```

This writes a local-only package under `private/study-a/self-pilot/` with a
distinct study ID that the independent-rating ingestion script rejects. It is
for usability and burden testing only, not author re-adjudication or evidence.

After the six local blocks are complete, place the downloaded self-pilot JSON
files under `private/study-a/self-pilot/responses/` and run:

```bash
make study-a-self-pilot-report
```

This report reads only timing and completion metadata; self-pilot labels remain
local and excluded from independent Study A analysis.

The private discovery fixture workflow can be tested separately with:

```bash
make discovery-synthetic
```

It mines synthetic repair turns, builds the offline review page, simulates
private decisions, and exercises the retained-candidate queue. It does not
import any real interaction history.

See `schema.md` for the study criteria and `materials/` for draft-only scope,
recruitment, and policy-translation documents.
