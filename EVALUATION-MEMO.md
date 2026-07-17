# Evaluation Brief: Adversarial Pragmatics for AI Safety Evaluation

**Status:** pre-collection portfolio brief, July 2026
**Audience:** model-policy teams, safety evaluators, red teams, system-card authors, and assurance reviewers

## Decision problem

AI evaluations often compress several questions into one pass/fail judgment.
A response can complete the requested task while violating a stated policy,
refuse safely while failing the task, follow an instruction embedded in
untrusted content, or repeat protected information while explaining a refusal.
An aggregate score hides which control failed and whether the label itself is
stable enough to support a safety claim.

This project turns those distinctions into an auditable evaluation workflow.
Its target is **language-mediated control**: deciding which text counts as an
instruction, what authority it has, what action it licenses, which policy
boundary applies, and what the visible record supports about failure.

## What the artifact contains

- An 18-item benign seed benchmark covering embedded commands, mention/use,
  authority hierarchy, scope and negation, reference hijacking, indirect
  speech acts, policy-boundary ambiguity, and agent-transcript interpretation.
  Three local models produced 54 prompt-response objects.
- Validator-enforced item metadata and separate label spaces for task success,
  policy compliance, visible safety boundaries, refusal, and failure
  attribution.
- A frozen, sanitized local-pilot evidence layer with row-level and aggregate
  summaries.
- Rule-aided diagnostic checks and an LLM-judge validation workflow.
- A role-separated expert-evaluation design with blind offline packages,
  deterministic presentation order, private return ingestion, object-level
  analysis, and explicit privacy and release boundaries.
- Executable freeze and collection gates that bind the item set, code,
  comparators, package bytes, assignments, materials, and institutional-scope
  evidence before external returns can be opened.
- Synthetic end-to-end regression tests that exercise the same build, ingest,
  and analysis path without creating empirical findings.

## Evidence available now

The completed local seed pilot is a pipeline-calibration result, not a model
leaderboard. A single author-adjudicator labelled 54 outputs from
`qwen3:8b`, `gemma3:12b`, and `glm-4.7-flash:q4_K_M`:

- 36 outputs were full task successes, 11 partial successes, and 7 failures;
- 46 were policy-compliant;
- 12 of 24 eligible pair-model cells passed the joint task-success and
  policy-compliance rule;
- the rule-aided diagnostic pass flagged all 7 noncompliant rows.

The first LLM-judge pass produced valid structured output for every row but
mostly tracked skewed majority labels. It recovered none of the 11 partial task
successes, 3 of 7 noncompliant outputs, and none of the 11 risk-labelled rows.
Those figures are deliberately reported as a negative validation result. The
judge graded its own outputs, saw expected-behaviour information, and was
compared with labels from the item author, so the pass does not establish a
deployable automated grader.

## Operational recommendations

1. **Keep criteria separate.** Report task success, policy compliance, visible
   boundary status, refusal calibration, and failure attribution separately.
   A safe refusal should not become a capability success, and successful task
   completion should not erase a policy violation.
2. **Represent source and embedding.** Preserve whether relevant text came from
   the user, a quotation, a document, a tool result, or a stated policy. Test
   whether models process untrusted text as data rather than as authority.
3. **Validate judges by class, not aggregate agreement.** Compare judge
   performance with majority-class baselines and report safety-relevant
   minority labels. Preserve the judge prompt, rubric access, model version,
   and information state.
4. **Treat unresolved labels as evidence.** Agreement can support an object
   label, but it does not turn a panel judgment into ground truth. Preserve
   contested cells and distinguish item ambiguity, missing context, criterion
   conflict, and taxonomy failure.
5. **Freeze the measurement path before returns.** Bind the item set, role
   packages, comparators, analysis code, and decision rules to a reviewable
   checkpoint. Keep identity-side records and raw returns private.
6. **Match claims to the evidence.** A result about a fixed prompt-response set
   does not by itself license claims about deployment robustness, evaluator
   populations, or model rankings.
7. **Expose offsetting transitions.** Pair aggregate scores with item- or
   family-level transition and harmful-tail reports when the design includes
   repeated paired conditions. Context-induced improvements and degradations
   can cancel in the mean, making aggregate stability a poor proxy for
   action-level reliability.

## External expert validation

Study A is the planned external validation layer. It targets three evaluators
per role, applying prescriptive, role-specific codebooks to the fixed 54
objects: one role evaluates linguistic/task criteria and the other evaluates
policy/safety criteria. Every planned result is indexed to an object, criterion
cell, paired contrast, or object-label comparison. The design does not estimate
evaluator traits or populations.

No external ratings have been collected. HREB was asked on 16 July 2026 whether
it regards the proposed experts as human research participants. Recruitment,
package distribution, and return opening remain closed pending its written
response and the executable collection gate.

## What the current repository state supports

The pre-collection repository state supports inspection of an evaluation stack
through fail-closed pre-collection gating: construct definition, benign item
design, schema validation, model execution, diagnostic triage, judge auditing,
and synthetic exercises of blind expert-package generation, private ingestion,
and object-level analysis. It also supplies a concrete negative result showing
why structured judge output and high aggregate agreement are insufficient
validation.

It does not yet support external human-panel findings, population estimates,
deployment-level safety claims, or a model leaderboard. Those limits are part
of the artifact rather than qualifications hidden after the results.

## Check the public artifact

```bash
make public-check
make study-a-synthetic
make
```

`make public-check` verifies the tracked benchmark and pilot artifacts from a
fresh clone. The historical raw pilot bundle and the Study A production build
are intentionally ignored; maintainer-local checks for those artifacts are
`make phase1-check` and `make study-a-freeze-ready`.

Start with the [repository overview](README.md), the
[Study A analysis plan](benchmark/study-a/analysis-plan.md), the
[expert-evaluation protocol](benchmark/study-a/materials/study-protocol-draft.md),
the sanitized pilot
[adjudication readout](benchmark/results/summaries/local-pilot-20260630-185417-adjudication-readout.md),
and the [LLM-judge validation readout](benchmark/results/summaries/local-pilot-20260630-185417-judge-validation-readout.md).
