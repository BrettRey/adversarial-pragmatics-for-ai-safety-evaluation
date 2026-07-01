# Sanitized Result Summaries

This directory stores aggregate, manuscript-facing pilot summaries that can be
tracked without committing raw model outputs or browser-export files.

Generate these files with:

```bash
make pilot-adjudication-report
```

Full local pilot bundles remain ignored under `benchmark/results/local-pilot-*`.
Do not rely on files in `~/Downloads`; copy browser exports into the relevant
run bundle, ingest them, and regenerate these summaries.
