# Adversarial Pragmatics for AI Safety Evaluation

This repository contains Brett Reynolds's empirical evaluation paper project:

**Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity**

## Project Frame

This is an empirical AI-evaluation paper, not another primarily conceptual AI-and-language paper.

Core signal:

> Turn messy language-mediated judgment into reliable, auditable AI evaluation.

The paper should produce a hiring-legible artifact: taxonomy, benchmark, annotation protocol, scoring metrics, and a concise policy/eval memo. The philosophy and linguistics are infrastructure for the evaluation design, not the advertised endpoint.

## Central Thesis

A large class of AI safety evaluation failures are failures in language-mediated control. Models and evaluators must decide what counts as an instruction, whose instruction has authority, whether a string is quoted or commanded, whether a request is literal or indirect, whether refusal is appropriate, and whether an agent transcript shows capability failure, safety refusal, scaffold failure, goal drift, or misreporting.

## Required Project Shape

- Build a small, auditable benchmark before expanding the theory.
- Prefer minimal pairs over one-off prompts.
- Keep examples non-operational: use harmless payloads such as colors, tokens, or dummy secrets unless a verified policy-safe item requires more.
- Separate task success, policy compliance, safety risk, evaluator confidence, and failure attribution.
- Treat disagreement as data: identify when disagreement is a property of the construct rather than rater noise.
- Validate LLM-as-judge behavior rather than assuming it.

## Repository Layout

```text
benchmark/
  items/              # seed and later gold-set items
  rubrics/            # taxonomy, annotation protocol, codebook
  results/            # generated evaluation results, not raw API logs by default
data/
  seed/               # hand-authored seed material
  processed/          # generated derived datasets
notes/                # project brief, source verification, pressure tests
scripts/              # validation/evaluation helpers
sections/             # LaTeX section files
submission/           # future submission materials
reviews/              # review-board or external review notes
```

## Source Discipline

- Do not cite the setup prompt as if it verifies its linked claims.
- Before adding a citation or factual claim about an organization, job posting, safety report, or research agenda, verify the source and record it in `notes/source-verification.md`.
- New bibliographic entries belong in `references-local.bib` unless Brett explicitly asks for a central-bib update.
- Keep `references.bib` as the symlink to the central bibliography.

## Build and Checks

Use XeLaTeX, not pdfLaTeX or LuaLaTeX.

```bash
make quick
make
python3 scripts/validate_items.py benchmark/items/seed-items.csv
```

Before any submission or public preprint:

- Run the central style checker on `main.tex`.
- Run the benchmark validator.
- Verify all sources in `notes/source-verification.md`.
- Ensure raw model outputs, API logs, and any sensitive examples are not committed unless intentionally sanitized.

## Writing Priorities

- Start from the evaluation bottleneck, not from disciplinary positioning.
- Use linguistics where it sharpens operational distinctions.
- Avoid "what linguistics can contribute to AI safety" framing.
- Avoid AGI ontology as the lead. This project is the practical evaluation layer below that abstraction.
- Make the method reusable for model-policy teams, frontier-risk evaluators, red-teamers, system-card authors, and external assurance teams.

## Key Terms

- Use `\term{}` for analytic terms and constructs.
- Use `\mention{}` for strings and prompt text.
- Use `\enquote{}` for quoted natural-language content.
- Keep `pdfkeywords` and the visible keyword line synchronized.
