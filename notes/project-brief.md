# Project Brief

## Core Signal

Brett Reynolds turns messy language-mediated judgment into reliable, auditable AI evaluation.

This project should read as a concrete evaluation artifact, not as a disciplinary positioning essay. It connects linguistic judgment methodology, category/kind theory, grammaticality work, CGEL-style annotation, LLM ontology/epistemology, and AGI evaluation by building a benchmark and protocol that safety teams can use.

## Working Title

**Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control**

Alternate strategic title:

**From Ambiguous Policy to Reliable Evals: Adversarial Pragmatics and Taxonomy Drift in AI Safety Evaluation**

## Contribution Stack

1. Taxonomy: safety-relevant instruction conflicts and ambiguity types.
2. Benchmark: controlled minimal pairs for embedded commands, quotation, hierarchy, scope, deixis, indirect speech acts, policy ambiguity, and agent transcripts.
3. Expert-evaluation protocol: evaluator roles, gold labels, confidence, disagreement, and adjudication.
4. Scoring framework: diagnostic ambiguity, taxonomy drift, source sensitivity, mention/use robustness, scope robustness, and adjudication stability.
5. Policy/eval memo: practical recommendations for gold-set construction, prompt-injection testing, LLM-judge validation, system cards, and safety cases.

## Non-Goals

- Do not write a generic "linguistics and AI safety" paper.
- Do not lead with whether LLMs really understand, refer, or have language.
- Do not lead with AGI ontology.
- Do not build a leaderboard paper whose main output is model ranking.

## First Milestone

Create a 50--100 item development benchmark from the seed schema, run a small expert-evaluation calibration pass, and use the item-level disagreement profile to revise the taxonomy before scaling toward 300--800 items. Do not collect ordinary-user labels or report evaluator responses as data about evaluator populations. Before running models, simulate fake data over item, model, application surface, rubric criterion, and judge prompt so the revision thresholds are explicit.
