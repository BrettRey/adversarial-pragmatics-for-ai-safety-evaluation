# Adversarial Pragmatics for AI Safety Evaluation

Title: **Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity**.

This is an empirical AI-safety-evaluation paper. The project turns Brett's work on linguistic judgment, unstable categories, annotation, grammaticality, and evaluation kinds into a concrete benchmark and protocol for language-mediated safety cases.

Core deliverables:

- a taxonomy of safety-relevant pragmatic failure modes;
- a seed benchmark of paired, controlled contrasts;
- an annotation protocol separating task success, policy compliance, safety risk, evaluator confidence, and failure attribution;
- metrics for diagnostic ambiguity and taxonomy drift;
- a local pilot and LLM-judge validation pass;
- supplementary documentation for model-policy, red-team, system-card, and external-assurance audiences.

## Current State

The canonical repository state contains:

- an 18-item seed benchmark with eight eligible paired contrasts plus one diagnostic confidentiality contrast;
- a 54-row local pilot over three Ollama models;
- sanitized row-level and aggregate pilot summaries under `benchmark/results/summaries/`;
- a judge-validation pass showing that a rubric-aided LLM judge missed the safety-relevant minority classes under favourable conditions;
- LaTeX source for the main paper, supplement, and two related framework papers.

Public-version note: arXiv v1 (`2607.01153v1`) reflects an earlier version of
the pilot readout. The current repository state is the canonical source for the
repaired paired-contrast treatment: P008 is excluded, leaving 12/24 eligible
paired-contrast passes. The seed pairs are controlled development contrasts,
not uniformly strict minimal pairs.

No source claims in setup prompts or review notes should be treated as verified until checked in `notes/source-verification.md`.

## Build

```bash
make quick
make
make test
```

Verify the frozen pilot and exercise the new preparation workflows with:

```bash
make phase1-check
make study-a-synthetic
make discovery-synthetic
```

The latter two commands use deterministic synthetic fixtures only. They do not
run an external study or import private interaction history.

Build the main paper, supplement, and two related framework papers with:

```bash
make all-papers
```

## Layout

```text
benchmark/items/seed-items.csv       # first safe, benign paired-contrast seed set
benchmark/rubrics/taxonomy.md        # failure-mode taxonomy
benchmark/rubrics/annotation-protocol.md
notes/project-brief.md
notes/source-verification.md
notes/12-pressure-test.md
scripts/validate_items.py
```

## Release Checklist

Before using the project as a public job-market or citation artifact:

- build clean PDFs with `make all-papers`;
- rebuild the arXiv source bundle with `bash scripts/build_arxiv_bundle.sh`;
- submit an arXiv revision matching the repaired paired-contrast readout;
- tag a numbered GitHub release from the same commit;
- archive the release with a DOI if the artifact will be cited externally;
- keep raw model-output bundles ignored unless they are intentionally sanitized for release.

## Bibliography

`references.bib` is a vendored snapshot of the central bibliography so this public repository builds independently. Add project-only verified entries to `references-local.bib`.

## License

Unless otherwise noted, manuscript text, benchmark items, rubrics, notes, documentation, and data are licensed under the Creative Commons Attribution 4.0 International License (`CC-BY-4.0`). Source code, scripts, and build files are licensed under the MIT License. See `LICENSE.md` and `LICENSES/`.
