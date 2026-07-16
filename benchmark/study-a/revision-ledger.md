# Study A revision ledger

<!-- SUMMARY: Study A design-revision and future post-freeze deviation log · status: pre-freeze, no tag created · updated: 2026-07-16 -->

**Correction (2026-07-16): Study A has never been frozen.** Earlier uses of
“freeze stamp 1,” “frozen,” and “post-freeze” below describe mutable checkpoint
artifacts or proposed states, not an annotated Git freeze tag. They remain
visible as design history. A candidate manifest must pass
`python3 scripts/build_study_a_manifest.py --verify`; even successful
verification does not freeze the design or authorize collection.

Before a tag, this ledger records design changes and self-pilot observations.
After an explicitly authorized annotated freeze tag exists at `HEAD`, it will
also record every scoped artifact change. At that point a silent edit to a
frozen artifact is a protocol violation; a logged edit is a disclosed
deviation and must pass the collection gate again.

Log a row whenever a frozen artifact changes after the freeze, or whenever a
self-pilot / exploratory observation motivates a design change (per DECISIONS
2026-07-15, self-pilot findings may become design rationale, never paper
evidence, and must be provenance-logged here).

| date_first_viewed | observation_source | affected_artifact_or_field | before_sha256 | after_sha256 | rationale | analysis_consequence |
|-------------------|--------------------|----------------------------|---------------|--------------|-----------|----------------------|
| _(none yet — no annotated freeze tag has been created)_ | | | | | | |
