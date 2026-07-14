# Data

- `seed/`: hand-authored seed material and item-generation notes.
- `processed/`: generated datasets and derived analysis files.
- `fixtures/`: deterministic synthetic fixtures used to test local workflows;
  never empirical data.
- `provisional/`: public-safe frozen snapshot and manifest for the original
  author's pilot labels before independent re-adjudication.

Keep raw model outputs and API logs out of git by default.

Keep raw interaction histories, candidate repair episodes, evaluator responses,
identity mappings, and private provenance under ignored `private/` paths rather
than anywhere in `data/`.
