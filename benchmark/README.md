# Benchmark

This directory holds the adversarial-pragmatics benchmark materials.

The seed file uses benign payloads such as colors and dummy tokens. It is meant to validate the schema, taxonomy, and minimal-pair logic before realistic policy-safe examples are added.

## Files

- `items/seed-items.csv`: first hand-authored seed rows.
- `rubrics/taxonomy.md`: phenomenon families.
- `rubrics/annotation-protocol.md`: rater protocol and label definitions.
- `results/README.md`: placeholder for generated outputs and summaries.

## Rule

Commit only sanitized benchmark items and aggregate/summarized results unless Brett explicitly approves storing raw model logs.
