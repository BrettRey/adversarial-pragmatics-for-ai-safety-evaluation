# Local Pilot Infrastructure Plan

## Goal

Make the 18-item seed benchmark runnable as a repeatable local pilot against Ollama models, with enough saved metadata and summaries to support a small results section without turning the repo into an API-log dump.

## Proposed Additions

1. Add `scripts/run_local_pilot.py`.
   - Read `benchmark/items/seed-items.csv`.
   - Validate it with the existing schema before running.
   - Call Ollama's local HTTP API for each item/model pair.
   - Default models: `qwen3:8b`, `gemma3:12b`, `glm-4.7-flash:q4_K_M`.
   - Default to `think:false`, because Qwen3 and GLM otherwise emit reasoning into `thinking` and can leave `response` empty.
   - Use deterministic settings by default: `temperature=0`, bounded `num_predict`.
   - Support `--limit`, `--models`, `--out-dir`, `--run-id`, `--resume`, and Ollama URL overrides.

2. Save a timestamped result bundle under `benchmark/results/local-pilot-<timestamp>/`.
   - `outputs.jsonl`: one sanitized record per item/model.
   - `outputs.csv`: compact review table for spreadsheet/manual adjudication.
   - `summary.json`: run-level counts and settings.
   - `pairwise_summary.csv`: pair/model completion table by `pair_id`.
   - `run_metadata.json`: system, Ollama, model list, timing, and script settings.
   - `README.md`: generated note explaining exactly how the run was produced.

3. Add a lightweight scoring layer.
   - Do not pretend to fully grade semantic correctness automatically.
   - Provide rule-aided diagnostic checks only:
     - whether `BLUE`, `GREEN`, protected tokens, or dummy secrets appear;
     - whether the output looks like a refusal;
     - whether output is empty;
     - whether Ollama returned a `thinking` field;
     - whether generation stopped normally or hit the token cap.
   - Preserve expected labels from the CSV so human adjudication can compare output to intended behavior.

4. Update docs and Make targets.
   - Add `make pilot-local` for the default local run.
   - Add `make pilot-smoke` for a small `--limit` run.
   - Update `benchmark/results/README.md` with the result-bundle contract.
   - Update `benchmark/README.md` with the local pilot command.

## Non-Goals

- No cloud API calls.
- No new Python dependencies.
- No LLM-as-judge yet.
- No claim that heuristic checks are gold labels.
- No changes to the seed items unless the runner exposes a schema issue.

## Verification

After implementation:

1. Run `python3 scripts/validate_items.py benchmark/items/seed-items.csv`.
2. Run `python3 scripts/run_local_pilot.py --limit 2 --run-id smoke --out-dir benchmark/results/_scratch`.
3. Inspect generated files.
4. Run a full local pilot unless the smoke run exposes a problem.
5. Run `make test`.

## Open Decision

Generated full pilot outputs are harmless for this seed set, but they are still raw model outputs. I will write them under `benchmark/results/` because that is the project-designated location, and I will keep the generated bundle separate from code changes so it can be reviewed before committing.
