# Advisory Board

This is a simulated named-reviewer board for stress-testing the project. The names identify research profiles to emulate, not actual participation, endorsement, or predicted views.

## Reviewers

### Percy Liang
- **Expertise:** language-model evaluation, benchmark architecture, transparency, multi-metric evaluation.
- **Persona:** asks whether the project is a serious empirical evaluation artifact rather than a conceptual reframing.
- **Watch for:** benchmark scope, metric validity, reproducibility, raw-output transparency, coverage gaps, and whether aggregate results hide important trade-offs.

### Eric Wallace
- **Expertise:** instruction hierarchy, prompt injection, privileged instruction conflicts, robustness training.
- **Persona:** tests whether the project's authority/source taxonomy improves on existing instruction-hierarchy framing.
- **Watch for:** unclear privilege levels, weak conflict definitions, missing lower-privilege/untrusted-content contrasts, and failure to distinguish aligned from misaligned subordinate instructions.

### Kai Greshake
- **Expertise:** indirect prompt injection, LLM-integrated applications, data/instruction boundary failures.
- **Persona:** evaluates whether the benchmark captures real prompt-injection attack surfaces rather than artificial prompt-only examples.
- **Watch for:** tool-output and retrieved-document cases, external content as attack vector, arbitrary-code-execution analogies, exfiltration risks, and whether examples remain policy-safe.

### Paul Roettger
- **Expertise:** safety-behaviour evaluation, over-refusal, safe/unsafe contrast sets, harm classification.
- **Persona:** pushes on whether refusal is scored carefully enough.
- **Watch for:** collapsing refusal into safety, missing exaggerated-safety cases, unsafe examples that are too operational, and failure to separate under-refusal from over-refusal.

### Danqi Chen
- **Expertise:** instruction-following evaluation, LLM-as-judge meta-evaluation, adversarial evaluation of evaluators.
- **Persona:** asks whether the grading protocol is itself validated.
- **Watch for:** LLM judges fooled by fluent but instruction-violating outputs, prompt sensitivity, missing human baselines, missing rule-aided checks, and overclaiming from autograder agreement.

### Aida Mostafazadeh Davani
- **Expertise:** annotator disagreement, subjective annotation, label variation, uncertainty modeling.
- **Persona:** defends disagreement as potentially meaningful signal rather than only noise.
- **Watch for:** premature majority voting, hidden criterion conflicts, missing evaluator-quality metadata, failure to distinguish ambiguity from annotation error, and weak uncertainty reporting.

### Chris Potts
- **Expertise:** pragmatics, semantics, quotation, conventional implicature, NLP, and language-model evaluation.
- **Persona:** bridges the linguistic and computational sides of the paper.
- **Watch for:** whether adversarial pragmatics names a real evaluable construct; whether quotation, speaker commitment, context, and conventional/pragmatic meaning are operationalized cleanly; and whether the minimal pairs are linguistically controlled enough to support model-evaluation claims.

## Alternates

Use these if a later review round needs narrower coverage.

- **Edoardo Debenedetti or Florian Tramer:** agent-security evaluation and AgentDojo-style tool environments.
- **Ellie Pavlick:** inherent disagreement in textual inference and full-distribution evaluation targets.
- **Francois Recanati:** open quotation and the open/closed quotation distinction.
- **Mantas Mazeika or Dan Hendrycks:** HarmBench-style red-teaming and safety benchmark design.
