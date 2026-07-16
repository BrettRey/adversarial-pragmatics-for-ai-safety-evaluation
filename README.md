# Adversarial Pragmatics for AI Safety Evaluation

Title: **Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity**.

This is an empirical AI-safety-evaluation paper and executable evaluation
artifact. It turns difficult judgments about instruction status, source
authority, policy scope, refusal, and failure attribution into a benchmark,
annotation protocol, judge audit, and fail-closed expert-evaluation workflow.

## Portfolio Walkthrough

For the shortest path through the project:

1. Read the [evaluation brief](EVALUATION-MEMO.md) for the decision problem,
   current evidence, operational recommendations, and explicit limits.
2. Inspect the [18-item benchmark](benchmark/items/seed-items.csv),
   [taxonomy](benchmark/rubrics/taxonomy.md), and
   [annotation protocol](benchmark/rubrics/annotation-protocol.md).
3. Review the sanitized 54-row pilot
   [adjudication readout](benchmark/results/summaries/local-pilot-20260630-185417-adjudication-readout.md)
   and negative [LLM-judge validation readout](benchmark/results/summaries/local-pilot-20260630-185417-judge-validation-readout.md).
4. Run `make public-check` and `make study-a-synthetic` to verify tracked pilot
   artifacts and exercise the blind build-to-analysis path without external
   data.

Core deliverables:

- a taxonomy of safety-relevant pragmatic failure modes;
- a seed benchmark of paired, controlled contrasts;
- annotation and expert-evaluation protocols separating task success, policy
  compliance, visible safety boundaries, refusal, and failure attribution;
- metrics for diagnostic ambiguity and taxonomy drift;
- a local pilot and LLM-judge validation pass;
- supplementary documentation for model-policy, red-team, system-card, and external-assurance audiences.

## Current State

The canonical repository state contains:

- an 18-item seed benchmark with eight eligible paired contrasts plus one diagnostic confidentiality contrast;
- a 54-row local pilot over three Ollama models;
- sanitized row-level and aggregate pilot summaries under `benchmark/results/summaries/`;
- a judge-validation pass showing that a rubric-aided LLM judge missed the safety-relevant minority classes under favourable conditions;
- a semantically verified Study A stamp-2 candidate with role-isolated expert
  packages, object-level analysis, synthetic regression tests, and a separate
  fail-closed collection gate;
- LaTeX source for the main paper, supplement, and two related framework papers.

No external Study A ratings have been collected. HREB was asked on 16 July
2026 whether it regards the proposed expert evaluators as human research
participants. Recruitment, package distribution, and return opening remain
closed pending its written response and the collection gate. The completed
local pilot and judge audit remain available for inspection and job-market use.

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

Verify tracked artifacts and exercise the synthetic preparation workflows with:

```bash
make public-check
make study-a-synthetic
make discovery-synthetic
```

The Study A and discovery commands use deterministic synthetic fixtures only.
They do not run an external study or import private interaction history.

Maintainers with the ignored local-pilot and Study A production artifacts can
also run `make phase1-check` and `make study-a-freeze-ready`. Freeze readiness
verifies the pre-collection artifact; it does not create a tag or authorize
external returns.

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
