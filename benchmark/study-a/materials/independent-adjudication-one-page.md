# Independent Adjudication Study: One-Page Description

**Draft for methodological discussion. Not an active recruitment notice.**

## The Question

The current adversarial-pragmatics pilot contains 18 benign prompts and 54
model outputs. Its original labels were authored by the same person who wrote
the items and specified expected behaviour. Study A tests that limitation
directly: can independent evaluators converge on criterion-specific judgments
when they do not see those labels, expected behaviours, model identities, or
diagnostic metadata, and how often are those judgments unanimous or
majority-supported?

## Design

Each evaluator sees only an opaque row ID, prompt, response, and one of two
role-specific rubrics. The intended assignment covers all 54 rows in three
18-row blocks rather than one 54-row sitting; blocks can be completed in
separate sittings.

Linguistic/task evaluators judge task success, source-role relations across the
prompt as a whole, source-role clarity, scope/reference, clarification need,
and response-act performance. The source-role question is multi-select;
multiple clear roles are not treated as ambiguity. Top-level, unattributed
prompt wording is treated as the task giver's contribution, whether it is a
request or a question. Task success records how fully the response carries out
the user-facing request and its task-defining conditions; it does not
incorporate policy compliance. Policy/safety evaluators judge compliance, risk, refusal
calibration, and information-flow or action-licensing concerns. In the revised
policy/safety form, "risk" is operationalized as visible security-boundary
status and type, not a prediction about deployment harm or model architecture.

The roles are not pooled into an overall score. A response can accomplish the
visible request while violating a stated policy, or comply with policy without
accomplishing the request. Failure attribution is deferred until there is a
supported first-pass panel record to reason from.

## What the Study Can Establish

The study can quantify observed within-panel agreement, compare historical
author and automated-judge labels with modal panel labels, and show where
linguistic and policy reasoning diverge. Those comparisons are panel-relative;
they do not make the modal label ground truth or establish stability to a new
panel or occasion.

It cannot establish population prevalence, benchmark coverage, model rankings,
or a general claim about all evaluators. It does not treat volunteers as a
representative sample.

## Data Boundary and Current Status

Real ratings and row maps stay local. The project uses pseudonymous rater IDs,
preserves every first-pass rating, and releases only aggregate or reviewed
sanitized material. A separate private workflow may mine the investigator's own
interaction histories for discovery, but those histories are not study data or
public benchmark material.

Study A is currently a personal independent project. It does not claim an
institutional sponsor, affiliation, or ethics approval. If an institution,
funder, or host later conditions access to the work, the project will request
the applicable scope determination before proceeding under that arrangement.
Independent evaluation is an unpaid, bounded volunteer contribution; the
project does not offer honoraria, authorship, employment benefit, or other
material consideration for ratings.

The workflow has been tested only with deterministic synthetic data. The
evaluator-role scope, information/agreement note, recruitment, evaluator
burden, and data-transfer details remain to be settled before anyone is invited
to contribute.
