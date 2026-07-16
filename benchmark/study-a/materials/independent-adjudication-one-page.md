# Independent Adjudication Study: One-Page Description

**Draft for methodological discussion. Not an active recruitment notice.**

## The Question

The current adversarial-pragmatics pilot contains 18 benign prompts and 54
model outputs. Its original labels were authored by the same person who wrote
the items and specified expected behaviour. Study A asks for what fraction of
those fixed prompt-response objects a specified independent-evaluation
procedure yields criterion-specific, unanimous- or majority-supported
substantive panel labels when the assessors do not see the original labels,
expected behaviours, model identities, or diagnostic metadata.

## Design

Each evaluator sees only an opaque row ID, prompt, response, and one of two
role-specific rubrics. The intended assignment covers all 54 rows in three
18-row blocks rather than one 54-row sitting; blocks can be completed in
separate sittings. Role pools are person-disjoint, each evaluator receives only
the assigned role's ZIP, and a private registry binds each globally unique
rater ID to one person, one role, and one package version.

The assessors apply stated criteria to prompt-response objects. The objects,
rubrics, and evaluation procedure are the focus of inquiry; the study has no
person-level estimand. It does not analyze personal reactions, evaluator
populations, rater severity or drift, background or subgroup effects,
confidence calibration, reasoning styles, or individual speed or performance.
Qualification and network breadth are independence and conflict-of-interest
controls, not analysis variables.

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
Confidence is limited to item-level uncertainty metadata for the global
criterion judgment. An optional rationale may support adjudication of the
object or rubric. Neither field is used to characterize the evaluator.

The roles are not pooled into an overall score. A response can accomplish the
visible request while violating a stated policy, or comply with policy without
accomplishing the request. Failure attribution is deferred until there is a
supported first-pass panel record to reason from.

## What the Study Can Establish

The study can quantify observed within-panel agreement, compare historical
author labels and two role-separated outcome-only automated comparators with
modal panel labels, and show where distinct task and policy labels coexist on
the same output. Those combinations characterize the object under separate
criteria; they do not estimate a difference between linguistic and policy
evaluator groups. Agreement, disagreement, and yield qualify item labels and
diagnose the specified measurement procedure.
Those comparisons are panel-relative; they do not make the modal label ground
truth or establish stability to a new panel or occasion. The automated
comparators use a compact scaffold rather than the humans' full
identification-first forms, so no information-state or measurement parity is
claimed.

It cannot establish population prevalence, benchmark coverage, model rankings,
or a general claim about all evaluators. It does not treat assessors as a
representative sample or report individual, subgroup, timing, burden,
confidence-calibration, or rationale-pattern effects.

## Data Boundary and Current Status

Real ratings and row maps stay local. The project uses pseudonymous rater IDs,
preserves every first-pass rating privately, and releases only reviewed
object-level panel aggregates. Individual votes, confidence values, rationales,
and timing metadata are not release candidates. A separate private workflow may mine the investigator's own
interaction histories for discovery, but those histories are not study data or
public benchmark material.

Study A is an unfunded project led by Brett Reynolds, a Humber Polytechnic
employee. It claims neither HREB approval nor an exemption. Recruitment and
collection remain paused pending HREB's written response and compliance with
any conditions it imposes.
Independent evaluation is an unpaid, bounded volunteer contribution; the
project does not offer honoraria, authorship, employment benefit, or other
material consideration for ratings.

Evaluator-facing materials use a conservative administrative workload estimate
of **30--40 minutes per 18-row block** (**90--120 minutes total**). Timing is not
a research outcome; any timestamps needed for saving, return validation, or
administration are excluded from analysis and public reporting.

The end-to-end workflow has a deterministic synthetic regression, and the real
54-row source is available locally for a private package candidate. No
collection-ready freeze tag exists. The methodological role statement, written
institutional determination, information/agreement note, recruitment,
data-transfer details, retention/deletion terms, and post-tag gate remain to be
settled before anyone is invited to contribute.
