# Benchmark

This directory holds the adversarial-pragmatics benchmark materials.

The seed file uses benign payloads such as colors, protected dummy tokens, and dummy secrets. It is meant to validate the schema, taxonomy, minimal-pair logic, refusal matrix, and application-surface wrappers before realistic policy-safe examples are added.

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

For a quick two-item check:

```bash
make pilot-smoke
```

The runner writes a timestamped result bundle under `benchmark/results/`.
It defaults to `think:false` for Ollama calls so Qwen3 and GLM responses are
captured in the API `response` field rather than the `thinking` field.

## Human Adjudication

After a local pilot run, prepare review materials with:

```bash
make pilot-diagnose
make pilot-review-app
```

`pilot-review-app` builds an offline browser app inside the ignored result
bundle, because the app contains raw model outputs. Open the generated
`review_app/adjudication_review.html` file directly in a browser.

Before coding, read `rubrics/rater-training.md`. Code the first 12 triage rows
as a calibration pass, then continue through all 54 rows. Download the JSON
response file, move it into that run's `review_app/responses/` directory, and
merge judgments with:

```bash
make pilot-ingest-adjudication
```

Then generate aggregate adjudication summaries and a manuscript-facing readout
with:

```bash
make pilot-adjudication-report
```

This writes raw-output-derived files inside the ignored run bundle and sanitized
aggregate copies under `benchmark/results/summaries/`. Treat browser downloads
as temporary imports only; the project should not rely on files in `~/Downloads`.

Use `RUN_DIR=/path/to/run` with any of these targets to operate on a specific
pilot bundle rather than the latest local run.

## Rule

Commit only sanitized benchmark items and aggregate/summarized results unless Brett explicitly approves storing raw model logs.
