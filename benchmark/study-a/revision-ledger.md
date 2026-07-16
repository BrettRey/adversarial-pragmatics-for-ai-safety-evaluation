# Study A revision ledger

<!-- SUMMARY: post-freeze deviation log for the Study A pre-registration; every change to a frozen artifact after the freeze is recorded here · status: active · updated: 2026-07-15 -->

This ledger records **every change to a frozen artifact after the freeze**, so the
pre-registration stays tamper-evident. The freeze is the manifest
`benchmark/study-a/FREEZE-MANIFEST.json` (verify with
`python3 scripts/build_study_a_manifest.py --verify`). A silent edit to a frozen
artifact is a protocol violation; a logged edit is a disclosed deviation.

Log a row whenever a frozen artifact changes after the freeze, or whenever a
self-pilot / exploratory observation motivates a design change (per DECISIONS
2026-07-15, self-pilot findings may become design rationale, never paper
evidence, and must be provenance-logged here).

| date_first_viewed | observation_source | affected_artifact_or_field | before_sha256 | after_sha256 | rationale | analysis_consequence |
|-------------------|--------------------|----------------------------|---------------|--------------|-----------|----------------------|
| _(none yet — freeze stamp 1 created 2026-07-15)_ | | | | | | |
