# Benchmark

This directory holds the adversarial-pragmatics benchmark materials.

The seed file uses benign payloads such as colors, protected dummy tokens, and
dummy secrets. It is meant to validate the schema, taxonomy, paired-contrast
logic, refusal matrix, and application-surface wrappers before realistic
policy-safe examples are added. The current seed set has 18 items: eight
eligible controlled contrasts plus one diagnostic confidentiality contrast.
These development pairs do not uniformly meet a strict minimal-pair standard.

## Files

- `items/seed-items.csv`: hand-authored seed rows with source-role, authority, pragmatic-status, risk-type, refusal-outcome, and judge-validation metadata.
- `rubrics/taxonomy.md`: phenomenon families and inclusion criteria.
- `rubrics/annotation-protocol.md`: expert-evaluation protocol, refusal matrix, limited evaluator metadata, and adjudication rules.
- `results/README.md`: placeholder for generated outputs and summaries.

## Local Pilot

The seed benchmark can be run against local Ollama models with:

```bash
make pilot-local
```

The default local model set is:

- `qwen3:8b`
- `gemma3:12b`
- `glm-4.7-flash:q4_K_M`

## Study B: Design Only

`study-b/` contains the separate selective-sensitivity design, projection
register, typed authorization schema, and commitment-protected development
fixtures. These files are not part of the historical pilot or Study A, contain
no results, and authorize no collection. Validate the current development
package with:

```bash
make validate-study-b
```

The checked fixtures use a structured prompt harness. Document, email,
tool-result, and transcript wrappers remain target conditions for later direct
validation; the current metadata does not establish application-surface
transfer.

### Exploratory API candidates

The following model is a candidate for a future, separately versioned API
cohort. It is **not** part of the frozen 54-row local pilot or Study A, and the
current pilot runner supports Ollama rather than OpenAI-compatible endpoints.

- `thinkingmachines/inkling` via NVIDIA NIM
  - API base: `https://integrate.api.nvidia.com/v1`
  - Authentication: `NVIDIA_API_KEY`
  - Access: free NVIDIA-hosted endpoint for prototyping, research, development,
    testing, and evaluation through the free NVIDIA Developer Program
  - Status: experimental, non-production, and subject to provider limits or
    withdrawal
  - Data boundary: public benign benchmark items only; do not send private
    Study A returns, confidential material, or sensitive data
  - Integration needed: a separate OpenAI-compatible runner that records
    provider and endpoint provenance

Access and model ID were verified on 2026-07-16 against the
[NVIDIA Inkling endpoint](https://build.nvidia.com/thinkingmachines/inkling)
and [NIM access documentation](https://docs.api.nvidia.com/nim/docs/product).

For a quick two-item check:

```bash
make pilot-smoke
```

The runner writes a timestamped result bundle under `benchmark/results/`.
It defaults to `think:false` for Ollama calls so Qwen3 and GLM responses are
captured in the API `response` field rather than the `thinking` field.

## Human Adjudication

The workflow below documents the original author-pilot adjudication path. It
is intentionally unblinded and remains historical evidence, not the package
for independent external evaluation.

After a local pilot run, prepare review materials with:

```bash
make pilot-diagnose
make pilot-review-app
```

`pilot-review-app` builds an offline browser app inside the ignored result
bundle, because the app contains raw model outputs. Open the generated
`review_app/adjudication_review.html` file directly in a browser.

Before coding, read `rubrics/rater-training.md`. Code a small initial slice as a
calibration pass, then continue through all 54 rows. Download the JSON response
file, move it into that run's `review_app/responses/` directory, and merge
judgments with:

```bash
make pilot-ingest-adjudication
```

Then generate aggregate adjudication summaries and a manuscript-facing readout
with:

```bash
make pilot-adjudication-report
```

This writes raw-output-derived files inside the ignored run bundle and sanitized
row-level and aggregate copies under `benchmark/results/summaries/`. Treat
browser downloads as temporary imports only; the project should not rely on
files in `~/Downloads`.

Use `RUN_DIR=/path/to/run` with any of these targets to operate on a specific
pilot bundle rather than the latest local run.

## Study A: Blind Independent Re-adjudication

`study-a/` contains the preparation workflow for independent, role-separated
re-adjudication of the existing 54 rows. It preserves the author labels as
historical data and gives external evaluators opaque row IDs, prompt text,
response text, and their role-specific rubric only.

The Study A workflow has been tested with deterministic synthetic fixtures:

```bash
make phase1-check
make study-a-synthetic
```

The synthetic run produces three 18-row offline blocks for each of the two
roles. Real packages, response files, row maps, and rater identity mappings
must stay under ignored `private/` paths. See `study-a/README.md` and its
draft-only `materials/` directory before any recruitment decision.

## Rule

Commit only sanitized benchmark items and aggregate/summarized results unless Brett explicitly approves storing raw model logs.
