# Results

Generated summaries can be stored here once model runs begin. The default
local pilot command is:

```bash
make pilot-local
```

For a quick smoke test:

```bash
make pilot-smoke
```

To prepare human adjudication materials for the latest local run:

```bash
make pilot-diagnose
make pilot-review-app
```

The review app is generated inside the result bundle:

```text
benchmark/results/local-pilot-<timestamp>/review_app/adjudication_review.html
```

Open that file directly in a browser. Downloaded JSON response files should be
placed in the same bundle under `review_app/responses/`. Merge them with:

```bash
make pilot-ingest-adjudication
```

After ingesting responses, generate aggregate adjudication summaries with:

```bash
make pilot-adjudication-report
```

The full run bundle remains ignored because it contains raw model outputs. The
report target also writes sanitized aggregate copies under
`benchmark/results/summaries/`, which is the durable project-local location for
manuscript-facing pilot evidence. Browser downloads are temporary imports only.

`benchmark/results/*` is ignored by Git except for this README, so generated
run bundles can be inspected before any deliberate release decision.

## Result Bundle Contract

`scripts/run_local_pilot.py` creates one directory per run:

```text
benchmark/results/local-pilot-<timestamp>/
  outputs.jsonl
  outputs.csv
  pairwise_summary.csv
  summary.json
  run_metadata.json
  diagnostic-readout.md
  adjudication-template.csv
  adjudication_responses.csv
  adjudication_summary.csv
  adjudication_model_summary.csv
  adjudication_pair_summary.csv
  adjudication_priority_summary.csv
  adjudication-readout.md
  diagnostic_matrix.csv
  review_app/
  README.md
```

Tracked aggregate summaries use this naming pattern:

```text
benchmark/results/summaries/
  local-pilot-<timestamp>-adjudication-readout.md
  local-pilot-<timestamp>-model-summary.csv
  local-pilot-<timestamp>-pair-summary.csv
  local-pilot-<timestamp>-priority-summary.csv
```

- `outputs.jsonl`: one structured record per item/model.
- `outputs.csv`: compact table for spreadsheet review and manual adjudication.
- `pairwise_summary.csv`: pair/model diagnostic counts.
- `summary.json`: aggregate diagnostic counts.
- `run_metadata.json`: command, environment, Git state, Ollama state, and settings.
- `diagnostic-readout.md`: triage readout for human adjudication.
- `adjudication-template.csv`: spreadsheet-ready manual labeling file.
- `adjudication_responses.csv`: flattened human adjudication labels.
- `adjudication_summary.csv`: per-review-row label counts across response files.
- `adjudication_model_summary.csv`: model-level adjudicated label counts.
- `adjudication_pair_summary.csv`: pair-level adjudicated label counts.
- `adjudication_priority_summary.csv`: diagnostic-priority performance summary.
- `adjudication-readout.md`: manuscript-facing summary of adjudicated pilot results.
- `diagnostic_matrix.csv`: compact item/model diagnostic matrix.
- `review_app/`: generated offline browser app and downloaded adjudication JSON.
- `README.md`: generated run note.

The diagnostic fields are rule-aided checks only. They are useful for triage,
but they are not gold task-success or policy-compliance labels.

Do not commit raw API logs, transcripts with sensitive content, or provider-specific metadata unless they have been reviewed and intentionally sanitized.
