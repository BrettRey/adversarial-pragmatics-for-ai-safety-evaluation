# Study A post-board repair plan

**Status:** implementation checkpoint
**Date:** 2026-07-16
**Scope:** repair the current Study A open-returns candidate; do not tag it or
open external returns in this stage

## Outcome sought

Produce a fail-closed stamp-2 candidate whose package, assignment, ingestion,
analysis, comparator, and claim contracts agree. A later explicit Brett
authorization would still be required to commit/tag the freeze and open
collection.

The existing review artifacts remain part of the record. No historical decision
or review is rewritten; corrections are append-only.

## Assumptions tested before planning

| Load-bearing assumption | Test | Result | Falsification condition / design response |
|---|---|---|---|
| The real 54-row source is available and intact | Compared the local source with the existing pilot freeze manifest and key grid | Pass: 54 unique item × model cells, 18 items, 3 models | If hash/key grid differs, production build aborts |
| The response-level author snapshot must still be created | Searched tracked provisional artifacts and compared keys | False: the 54-row snapshot already exists at `data/provisional/local-pilot-20260630-185417-provisional-author-labels.csv` and matches the source exactly | Add it and its pilot manifest to stamp 1 now |
| A random seeded shuffle satisfies the promised order | Replayed the frozen synthetic salt | False: four adjacent same-item pairs | Replace shuffle with a constructive balanced order and assertions |
| D3 can coexist with full 54-row assignments and overlapping people | Traced plan, package, and ingestion keys | False without row partitions; the default assignment gives every person every row | Make role pools person-disjoint and verify them through a private assignment registry |
| The current judge condition is information-state-parity matched | Compared the human form and judge prompt | False: humans answer the full identification-first role scaffold; judges see target outcomes only | Retain the current condition as a disclosed outcome-only comparator; remove parity claims |
| Current comparator errors imply the files should be replaced | Checked visible-rule cases and both comparator files | False: the errors are judge-behaviour evidence, not file corruption | Keep the current files, add predeclared sentinel readouts, and do not model-shop |
| Three support strata exhaust realized panels | Traced replacement/partial-return rules | False if a replacement and late return yield N>3 | Report 2/2, 2/3, 3/3, and an explicit `other` support-pattern bucket; never discard valid returns |
| Stamp-1 verification establishes freeze readiness | Inspected verifier semantics | False: it checks file hashes only and ignores manifest state and production invariants | Implement semantic stamp-2 and collection-ready gates |

## Decisions for this repair

### 1. Person-disjoint role pools

Replace D3 with a person-disjoint rule. Keep identity/contact information outside
the research dataset. Use an immutable ignored assignment registry containing a
stable investigator-side `person_key`, pseudonymous `rater_id`, assigned role,
and package ID. Record assignment, distribution, receipt, and withdrawal
timestamps in a separate private operations log so routine collection events do
not invalidate the registry attestation.

A new validator will:

- require one person, one globally unique rater ID, and one role;
- hash the registry into a private attestation;
- reject registry drift, unknown returned IDs, and role-mismatched payloads;
- retain no person key in ratings or analysis outputs.

This enforces the rule at data acceptance. It cannot detect deliberate false
identity information, so the protocol will state the investigator-side
attestation assumption explicitly.

### 2. Isolated role packages

The external artifact will no longer contain a two-role chooser. The builder will
produce two deterministic, self-contained ZIPs:

- one linguistic/task ZIP containing only that form and its practice set;
- one policy/safety ZIP containing only that form and its practice set.

The combined chooser remains only for the local self-pilot. Package audits will
fail if an opposite-role form, path, field inventory, or escaping link appears in
a distribution ZIP.

Every form and returned payload will carry an opaque `package_id` tied to the
frozen build. Ingestion will reject stale responses from another build.

### 3. Constructive presentation order

Fail closed unless the source is exactly the declared 18-item × 3-model grid.
Construct three 18-row blocks so that:

- each block contains one response per item;
- each block contains six responses per model;
- no same-item responses are adjacent, including block boundaries;
- the same source and private salt reproduce the same order.

Write and freeze `presentation-order.tsv` plus an order audit. All evaluators will
share this one order; the common-order limitation will be disclosed rather than
calling the design counterbalanced.

### 4. Preserve but flag incoherent ratings

Do not reject, normalize, or overwrite contradictory evaluator answers. Add a
production coherence flag for the schema-declared boundary dependency:

- `no_boundary_stated` must pair with boundary type `none`;
- a stated/violated boundary must pair with a non-`none` type.

Propagate flag counts into panel rows, contested-item outputs, and the readout.
Repair the synthetic baseline and inject one deliberate mismatch so the
end-to-end test proves that the raw answer survives and the flag appears.

### 5. Make realized support visible

Add `modal_support_n` and `support_pattern` to panel rows. Report 2/2, 2/3, 3/3,
and `other` counts/rates for:

- C1/C2 fixed-denominator yield;
- C3/C4 author–panel summaries, including policy-at-stake;
- S2 judge summaries;
- S3 class and confusion summaries.

Preserve unanimous/majority fields. Add the missing C4 policy-at-stake and S3
unanimous/majority splits.

### 6. Fail closed on comparison inputs

For non-synthetic analysis:

- require the tracked 54-row author snapshot with exact key coverage and valid
  target fields;
- require exactly two explicit judge files with distinct constant judge
  identities, 54 exact keys each, one condition each, required columns, and raw
  responses;
- allow an explicit parse failure to remain judge evidence, but never allow a
  missing row, duplicate condition, undeclared label, or silent file skip.

Synthetic metadata retains the deliberately smaller fixture path.

### 7. Keep the current judges; remove the false parity claim

Do not rerun or replace the two Mistral comparators. They are complete and
reproducible, and their visible errors are part of what Study A is meant to
measure. Reframe them as role-separated, outcome-only comparator conditions
whose elicitation differs from the human identification-first form.

Add:

- a structural prompt audit proving no answer-key/taxonomy/identity leak;
- a tracked visible-rule sentinel definition and per-judge readout;
- explicit language that sentinels were selected after viewing comparator output
  during the pre-freeze repair and are diagnostics, not an independent accuracy
  estimate;
- the corrected divergence statement: 21 policy cells differ, of which 17 are
  `compliant` ↔ `no_policy_or_authority_limit`.

### 8. Replace “strict minimal pair” claims for the seed pilot

Call the current materials paired or controlled contrasts. Retain minimal-pair
construction as the development benchmark's goal, but do not describe the seed
set or its pilot pass count as causal isolation. Align the plan, active paper
box, construction section, experiment captions/prose, and metric firewall.

### 9. Implement two gates

`freeze-ready` will:

- verify the tracked pilot/source fingerprints and author snapshot;
- build the real isolated packages in a new ignored production directory;
- require an empty responses directory;
- hash stamp-1 code/design/comparator artifacts and stamp-2 private
  package/order/map/metadata artifacts;
- validate manifest semantics, audits, model digests, commands, and absence of
  `not_yet_frozen` entries;
- write a complete-but-unsealed stamp-2 candidate.

`collection-ready` will additionally require:

- an annotated freeze tag pointing at the exact HEAD/manifest commit;
- no scoped drift;
- finalized collection cutoff, return address, retention/deletion wording, and
  current interface timing evidence.

This repair will implement both gates but will stop before the tag. Operational
placeholders that require Brett's real address/date choices will remain explicit
collection blockers rather than being guessed.

## Work sequence

1. Package and assignment layer:
   constrained order, package ID, isolated deterministic ZIPs, assignment
   validator, ingestion checks.
2. Measurement layer:
   coherence flags, support patterns, C4/S2/S3 splits, strict comparator inputs.
3. Comparator and claims:
   sentinel audit, non-parity framing, corrected counts, paired-contrast
   terminology.
4. Freeze layer:
   semantic manifest v2, freeze-ready and collection-ready commands, append-only
   decision/ledger correction.
5. Verification:
   negative tests first, then full synthetic workflow, package determinism,
   sentinel audit, manifest checks, item validator, Python compilation, XeLaTeX,
   house style, and diff checks.
6. Build the ignored local production package and stamp-2 candidate. Do not
   commit, tag, distribute, or open returns.

## Acceptance tests

The repair is complete only if all of these hold:

- duplicate person, duplicate rater ID, unknown rater, wrong-role payload, and
  changed registry all fail;
- each role ZIP contains only its own role and all internal links resolve;
- repeat builds with identical source/salt are byte-identical;
- every block is 18 unique items and six rows per model, with zero adjacent
  same-item rows;
- a changed/missing source-grid cell fails before files are written;
- stale `package_id` responses fail;
- deliberate boundary incoherence remains raw and is flagged;
- 2/2 + 3/3 equals unanimous supported rows, 2/3 equals majority for the current
  N≤3 fixture, and all additional patterns enter `other`;
- C4 policy-at-stake and S3 class/confusion outputs retain support strata;
- production analysis fails on missing/incomplete author data and on 0, 1, or 3
  judge files;
- sentinel mismatches are reported but do not invalidate the comparator file;
- the manifest verifier detects both artifact drift and metadata/gate drift;
- `collection-ready` fails before the annotated tag and unresolved operational
  fields;
- the end-to-end synthetic workflow and paper build pass;
- no existing external return is opened and no tag is created.

## Point of no return

The point of no return is distributing either role ZIP or opening a returned
file. This plan stops before both. Until the annotated tag and collection gate
exist, all generated production artifacts remain an unsealed local candidate and
may be rebuilt with the correction recorded.
