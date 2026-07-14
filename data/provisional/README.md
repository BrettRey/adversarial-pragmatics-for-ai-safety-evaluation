# Provisional Historical Labels

This directory preserves a public-safe snapshot of the original author's
54-row pilot labels before independent re-adjudication. The snapshot is not a
gold standard and must not be overwritten when later Study A ratings arrive.

`local-pilot-20260630-185417-freeze-manifest.json` records the frozen public
artefact and, when available locally, fingerprints the ignored raw source
bundle. `local-pilot-20260630-185417-provisional-author-labels.csv` contains
only the label fields needed for later comparison; it excludes coder identity,
browser-response metadata, full rationales, and raw model outputs.

Run `make phase1-check` before preparing external review materials. A deliberate
change to this historical snapshot requires `scripts/freeze_pilot_artifact.py
--write --reason "..."`; it should also be documented in the study record.
