# Percy Liang profile: benchmark and reproducibility review

*Simulated reviewer profile. This is a stress test, not a statement by Percy
Liang or evidence of field consensus.*

## One-sentence summary

Study A estimates fixed-set evaluator convergence on criterion-specific labels
for 54 existing prompt–response rows, then compares supported panel labels with
frozen author labels and two role-separated automated judges; it is a
measurement-validation study, not a model leaderboard or population estimate.

## Strengths

- The estimand is unusually disciplined: the plan explicitly limits claims to
  counts and fractions over the fixed 54-row set and disclaims population,
  leaderboard, and direct authority-sensitivity interpretations
  (`benchmark/study-a/analysis-plan.md:10-19`). It also correctly states that
  panel yield measures convergence, not correctness (`analysis-plan.md:185-194`).
- The multi-metric design is substantive rather than cosmetic. Task success
  excludes policy compliance (`benchmark/study-a/schema.md:90-97`), no composite
  is calculated (`benchmark/study-a/materials/study-protocol-draft.md:70-73`),
  and the analyzer preserves row-level task/policy divergence
  (`scripts/analyze_independent_reassessment.py:1241-1273`).
- The executable reporting path preserves ambiguity and denominators: yield uses
  all 54 presented rows, not available cases
  (`analyze_independent_reassessment.py:395-463`), while substantively contested
  rows remain separately auditable (`analyze_independent_reassessment.py:465-489`).
- Reproducibility is materially better than a typical pilot. The manifest pins
  ten artifacts and both judge digests
  (`benchmark/study-a/FREEZE-MANIFEST.json:6-51`), and read-only verification
  passed. Both frozen comparator CSVs contain `raw_response`; a direct audit
  found 54 unique rows each, one run/template/model each, zero parse errors, and
  no missing labels or raw responses.

## Weaknesses and defects

- **Freeze-blocking — the freeze object is explicitly incomplete.** The plan
  defines freezing as hashing the real row map, presentation order, author
  snapshot, and build command (`analysis-plan.md:224-225`), while the current
  manifest declares all three real-run artifacts “not yet frozen”
  (`FREEZE-MANIFEST.json:53-56`) and records only the judge-run command
  (`FREEZE-MANIFEST.json:10`). Build the real packages, add stamp 2 with the
  source-output snapshot, ordered package artifacts, row map, author snapshot,
  and exact build/ingest/analyze commands, verify, then tag. Tagging `c82577c`
  itself would not close the stated pre-unblinding object.
- **Freeze-blocking — the comparison layer fails open and still misses one
  planned split.** C3/C4 depend on a frozen 54-row author snapshot and D4 requires
  two comparators (`analysis-plan.md:45-53,113-120`), but missing author data
  merely becomes `author_label_not_available`
  (`analyze_independent_reassessment.py:855-876`), while the analyzer defaults to
  one judge file and silently skips missing or empty files
  (`analyze_independent_reassessment.py:1040-1053`). Separately, the plan requires
  every agreement result to be split by unanimous versus majority support
  (`analysis-plan.md:103-106,190-193`), yet C4's policy-at-stake result is
  aggregate-only (`analyze_independent_reassessment.py:957-1009`); only the
  overall result receives the split
  (`analyze_independent_reassessment.py:1011-1028`). Make the frozen author
  snapshot and exactly two named, internally consistent 54-row judge files
  mandatory; add unanimous/majority policy-at-stake denominators and regression
  tests.
- **Freeze-blocking — the cross-role independence rule is not operationalized.**
  D3 allows a person in both role pools only if they never rate the same row
  (`analysis-plan.md:36-41`), but the protocol targets all 54 rows per evaluator
  (`study-protocol-draft.md:35-42`) and the builder emits the same blocks for both
  roles (`build_independent_reassessment.py:567-588`). Thus any full-coverage
  dual-role evaluator necessarily violates D3. Require disjoint people across
  roles, or implement assignment-specific row partitions plus a private
  person × role × row overlap audit.
- **Limitation/reporting improvement — “eight strict minimal pairs” overstates
  the benchmark architecture.** The plan calls them strict minimal pairs
  (`analysis-plan.md:10`) but later correctly concedes that prompts, responses,
  and more than authority change (`analysis-plan.md:138-144`); P001 alone changes
  a webpage-summary task into direct token output
  (`benchmark/items/seed-items.csv:2-3`). Call these paired contrasts throughout.
  This does not invalidate the fixed-set convergence study, but it precludes
  presenting Study A as a clean minimal-pair test of authority sensitivity.

## Key question

What exact tag and fail-closed command will guarantee that the real row order,
author snapshot, cross-role assignment independence, and both complete
comparator snapshots are fixed—and that analysis aborts rather than quietly
degrading if any one is absent?

## Verdict

**FIX-FIRST** — the empirical design is serious and largely executable, but the
current commit is a verified stamp-1 candidate, not a complete pre-unblinding
freeze, and several stated safeguards are not yet enforced.
