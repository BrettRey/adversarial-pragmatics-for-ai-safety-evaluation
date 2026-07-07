# Adversarial Pragmatics as Secure Delegation Evaluation

## Core Move

Use secure delegation as the strategic frame for the paper, while keeping the benchmark as the central artifact.

The paper should not become a theory of machine agency. The sharper claim is:

> Secure delegation requires reliable evaluation of language-mediated control failures. Adversarial pragmatics isolates one neglected layer of that problem: whether an AI system and its evaluators can tell which language has authority, what action it licenses, and how failures should be attributed.

This lets the project speak directly to AI security without reducing it to prompt-injection detection or refusal-rate benchmarking.

## Dominant-Game Ladder

| Weak Game | Stronger Game | Higher Game | Benchmark Construct |
| --- | --- | --- | --- |
| Block bad prompts | Preserve instruction-control integrity | Govern which intentions become actions | Instruction-status classification |
| Detect malicious strings | Track authority, provenance, and execution rights | Control the delegation graph of agency | Authority/source/scope labels |
| Maximize refusals | Separate refusal, task success, compliance, and risk | Make security tradeoffs auditable and learnable | Multi-axis outcome scoring |
| Patch known attacks | Test minimal pairs across pragmatic contrasts | Map the system's security invariants | Pairwise robustness by phenomenon |
| Benchmark prompt safety | Benchmark agentic security under adversarial pragmatics | Build a science of AI control failure | Failure-attribution protocol |

The top-level formulation:

> The dominant game in AI security is not preventing every bad output. It is controlling the conditions under which agency can be delegated to machines.

## Existing Paper or New Paper?

Both, but not at the same weight.

For the existing paper, secure delegation should be a light strategic frame. It should sharpen the opening motivation, contribution statement, and implications section, but it should not change the paper's center of gravity. The current paper is still the benchmark paper: taxonomy, items, annotation protocol, metrics, pilot evidence, and judge validation.

As a separate future paper or policy memo, secure delegation could become the primary object. That piece would ask what institutional, technical, and evaluative conditions make machine delegation trustworthy. The current benchmark would then appear as one measurement component inside a broader secure-delegation program.

The practical decision is:

> Use secure delegation to make the existing paper legible to AI-security readers, while saving the larger theory of delegated machine agency for a later article or memo.

## How It Changes the Existing Paper

### Introduction

Open from the security bottleneck, not from linguistics.

Current frame:

> Frontier-model safety evaluation increasingly evaluates language-mediated control.

Possible sharpened frame:

> AI security is increasingly a problem of secure delegation: systems act through natural-language instructions, tool outputs, retrieved documents, policy text, and agent transcripts. A safety evaluation is therefore incomplete if it only asks whether the final output was acceptable. It also has to ask whether the system preserved control over which language counted as an instruction, whose authority it carried, what action it licensed, and how any failure should be attributed.

### Contribution Statement

Position the benchmark as an evaluation layer for secure delegation:

> This paper contributes a small, auditable benchmark for evaluating language-mediated control failures in delegated AI systems. The benchmark uses minimal pairs to test whether models and evaluators preserve distinctions among instruction, quotation, policy analysis, untrusted content, scoped permission, refusal, inability, and unsafe enactment.

### Implications Section

Make the payoff explicit for AI-security audiences:

> The benchmark does not claim to solve secure delegation. It supplies one measurement layer that secure-delegation regimes need: evidence about whether instruction status, authority, scope, and failure attribution remain stable under adversarial language conditions.

## What Not To Claim
- Do not claim that adversarial pragmatics is the whole of AI security.

- Do not claim that secure delegation is solved by better prompt evaluation.

- Do not make "machine agency" the paper's object of theory.

- Do not replace the empirical contribution with a conceptual ladder.

- Do not let the frame obscure the current artifacts: seed items, labels, validator, pilot summaries, judge validation, and adjudication workflow.

## What To Claim

- AI-security failures often involve language-mediated control failures.

- Prompt injection, jailbreaks, policy ambiguity, agent transcript review, and LLM-judge grading share a common measurement problem: evaluators have to determine what language counted as an instruction, from whom, under what scope, and with what authorized action.

- The benchmark operationalizes this measurement problem through minimal pairs and separate labels for task success, policy compliance, safety risk, confidence, and failure attribution.

- Disagreement is part of the target when it reveals unstable constructs rather than mere rater noise.

- LLM-as-judge behavior must be validated on these distinctions rather than assumed.

## Immediate Use

1. Add one secure-delegation paragraph to the introduction.

2. Add a compact dominant-game table to a note, appendix, or policy memo rather than the main paper unless space allows.

3. Revise the implications section so AI-security readers see why the benchmark matters beyond prompt-injection examples.

4. Keep the abstract empirical: benchmark, taxonomy, protocol, metrics, pilot, and judge validation.

5. Use "secure delegation" sparingly as the umbrella, not as a new terminological burden.

## Candidate One-Sentence Pitch

Adversarial pragmatics is the measurement layer that asks whether delegated AI systems preserve control over what language they treat as authoritative instruction.
