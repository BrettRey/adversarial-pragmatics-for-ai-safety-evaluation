# Adversarial Pragmatics for AI Safety Evaluation

Working title: **Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity**.

This is an empirical AI-safety-evaluation paper. The project turns Brett's work on linguistic judgment, unstable categories, annotation, grammaticality, and evaluation kinds into a concrete benchmark and protocol for language-mediated safety cases.

Core deliverable:

- a taxonomy of safety-relevant pragmatic failure modes;
- a minimal-pair benchmark;
- an annotation protocol separating task success, policy compliance, safety risk, evaluator confidence, and failure attribution;
- metrics for diagnostic ambiguity and taxonomy drift;
- a short policy/eval memo for model-policy, red-team, system-card, and external-assurance audiences.

## Current State

The project contains a working LaTeX draft, an 18-item seed benchmark, expert-evaluation rubrics, source-verification notes, and a validator for benchmark metadata. No source claims in the setup prompt should be treated as verified until checked in `notes/source-verification.md`.

## Build

```bash
make quick
make
make test
```

## Layout

```text
benchmark/items/seed-items.csv       # first safe, benign minimal-pair seed set
benchmark/rubrics/taxonomy.md        # failure-mode taxonomy
benchmark/rubrics/annotation-protocol.md
notes/project-brief.md
notes/source-verification.md
notes/12-pressure-test.md
scripts/validate_items.py
```

## Bibliography

`references.bib` is a vendored snapshot of the central bibliography so this public repository builds independently. Add project-only verified entries to `references-local.bib`.

## License

Unless otherwise noted, manuscript text, benchmark items, rubrics, notes, documentation, and data are licensed under the Creative Commons Attribution 4.0 International License (`CC-BY-4.0`). Source code, scripts, and build files are licensed under the MIT License. See `LICENSE.md` and `LICENSES/`.
