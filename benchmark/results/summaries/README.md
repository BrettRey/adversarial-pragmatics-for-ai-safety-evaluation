# Sanitized Result Summaries

This directory stores sanitized row-level and aggregate, manuscript-facing pilot
summaries that can be tracked without committing raw model outputs or
browser-export files.

Generate these files with:

```bash
make pilot-adjudication-report
```

LLM-judge validation summaries are generated with:

```bash
make pilot-judge-validation
```

Fake development-pass calibration summaries are generated with:

```bash
make fake-dev-calibration
```

The fake calibration files are design checks only. They should not be described
as empirical pilot results.

Full local pilot bundles remain ignored under `benchmark/results/local-pilot-*`.
Do not rely on files in `~/Downloads`; copy browser exports into the relevant
run bundle, ingest them, and regenerate these summaries.
