# Benchmark

This directory holds the adversarial-pragmatics benchmark materials.

The seed file uses benign payloads such as colors, protected dummy tokens, and dummy secrets. It is meant to validate the schema, taxonomy, minimal-pair logic, refusal matrix, and application-surface wrappers before realistic policy-safe examples are added.

## Files

- `items/seed-items.csv`: hand-authored seed rows with source-role, authority, pragmatic-status, risk-type, refusal-outcome, and judge-validation metadata.
- `rubrics/taxonomy.md`: phenomenon families and inclusion criteria.
- `rubrics/annotation-protocol.md`: expert-evaluation protocol, refusal matrix, limited evaluator metadata, and adjudication rules.
- `results/README.md`: placeholder for generated outputs and summaries.

## Rule

Commit only sanitized benchmark items and aggregate/summarized results unless Brett explicitly approves storing raw model logs.
