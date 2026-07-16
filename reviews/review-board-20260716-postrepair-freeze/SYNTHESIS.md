# Study A post-repair freeze-readiness review board

**Date:** 2026-07-16
**Target:** commit `c82577c` (`Repair Study A freeze analysis contract`)
**Gate reviewed:** the actual tag that would authorize opening external evaluator returns
**Board verdict:** **FIX-FIRST**

## Scope and method

This board reviewed the repaired Study A design as a pre-unblinding measurement
and reproducibility object. Five reviewers worked independently and were told not
to read prior reviews:

1. Percy Liang profile — benchmark design and reproducibility
2. Danqi Chen profile — judge validity and comparison design
3. Aida Mostafazadeh Davani profile — disagreement and rater heterogeneity
4. Chris Potts profile — pragmatic construct validity
5. Eric Wallace profile — instruction hierarchy and prompt-injection evaluation

These are simulated expert profiles, not statements by the named researchers and
not evidence of field consensus. The board's job was to stress-test the current
artifact, not to vote on whether the project is worth pursuing.

The chair separately verified the current repository state. All ten stamp-1
hashes match the manifest. There is no git tag. The manifest still lists the real
row map, presentation order, and response-level author snapshot as not frozen.
No scientific source file was changed during this review.

## Outcome

Do **not** use the current commit as the open-returns freeze.

The scientific core is viable and substantially better than the previous
candidate. The repaired plan correctly defines Study A as a fixed-set
panel-convergence study, not a model leaderboard, population estimate,
authority-sensitivity experiment, or gold-label oracle. The remaining problems
are mostly executable-contract defects: the written safeguards are not yet
guaranteed by the production path.

All five profiles returned FIX-FIRST. That agreement should not be mistaken for
five independent empirical votes: the gate question was narrow and several
defects are directly observable in the same files. The more informative result
is the non-overlapping catches—the ordering guarantee, judge-scaffold mismatch,
realized-N collapse, and fail-open comparison inputs.

## Consensus strengths

- **Bounded estimand.** The plan limits primary claims to exact counts and
  fractions over 54 existing rows and explicitly disclaims population and
  leaderboard inference (`benchmark/study-a/analysis-plan.md:10-19`).
- **Convergence is not correctness.** Modal labels are treated as vote summaries,
  with uncertainty, escapes, and substantive contestation preserved rather than
  converted into truth (`analysis-plan.md:103-106,185-194`;
  `scripts/analyze_independent_reassessment.py:352-489`).
- **Criterion separation.** Task success and policy compliance remain distinct;
  no composite score erases task-successful/noncompliant or
  task-failing/compliant cases (`benchmark/study-a/schema.md:90-97`).
- **Good missingness discipline.** Yield uses the fixed 54-row denominator,
  partial blocks are retained, and unrated cells remain visible
  (`analysis-plan.md:25-35,163-168`;
  `scripts/analyze_independent_reassessment.py:395-463`).
- **Auditable comparator artifacts.** Both judge files preserve raw responses,
  contain 54 unique keys, and have no parse errors; all ten stamp-1 hashes verify.
- **Repair of the prior scientific defect.** Seed target-behaviour codes are now
  explicitly separated from response-outcome labels, and C5/C6 are framed as
  descriptive, response-mediated pairwise divergence rather than authority
  identification (`analysis-plan.md:116-144`).

## Freeze blockers

### 1. The open-returns gate is not executable

The plan says the tagged freeze must hash the exact package/order, row map,
response-level author snapshot, comparator conditions, analysis scripts, and
build command (`analysis-plan.md:224-225`). The current manifest explicitly
omits three of those objects (`benchmark/study-a/FREEZE-MANIFEST.json:53-56`),
contains only a judge-run command, and the manifest builder implements stamp 1
only (`scripts/build_study_a_manifest.py:12-16,33-52,92-105`).

The state language is also inconsistent: the plan says “not frozen,” there is no
tag, while the revision ledger calls itself post-freeze and says stamp 1 was
created (`benchmark/study-a/revision-ledger.md:1-18`).

The production analysis also fails open: a missing author snapshot becomes
`author_label_not_available`, missing judge files are silently skipped, and the
CLI defaults to one judge file (`scripts/analyze_independent_reassessment.py:855-876,1040-1053`).

**Required:** implement one fail-closed production command that builds the real
packages, records the source-output snapshot and exact presentation order,
requires the complete 54-row author snapshot and exactly two named 54-row judge
snapshots, records build/ingest/analyze invocations, creates and verifies stamp 2,
and only then permits the open-returns tag. Align the plan, manifest, and ledger
on whether stamp 1 is a checkpoint or a freeze.

### 2. D3 cannot be satisfied by the default assignment

D3 allows the same person in both role pools only if that person never rates the
same row under both roles (`analysis-plan.md:36-41`). The protocol assigns each
evaluator all 54 rows in one role (`study-protocol-draft.md:35-42,81-85`), the
builder exposes the same blocks for both roles
(`scripts/build_independent_reassessment.py:567-588`), and ingestion's duplicate
key includes role (`scripts/ingest_independent_reassessment.py:201-205`).

**Required:** the simplest defensible repair is person-disjoint role pools. If
cross-role participation is retained, freeze a person × role × row assignment
map and a private identity-side overlap audit. Pseudonymous IDs alone cannot
establish person-level independence.

### 3. The promised ordering constraint is false

The builder comments promise that same-item responses will not be adjacent, but
the implementation performs only an unconstrained seeded shuffle
(`scripts/build_independent_reassessment.py:97-108`). Replaying the frozen
synthetic salt produced four adjacent same-item pairs. This can reveal the
repeated-item structure and induce comparative rather than independent ratings.

**Required:** use a constrained deterministic permutation and assert the
declared invariants. Freeze the realized order. Either counterbalance orders or
disclose that all evaluators share one order and therefore share any order
effect.

### 4. Contradictory policy ratings pass silently

The schema says boundary type `none` corresponds to
`no_boundary_stated` (`benchmark/study-a/schema.md:124-130`), but ingestion
validates fields independently (`scripts/ingest_independent_reassessment.py:69-94`).
The passing synthetic fixture itself combines
`boundary_stated_no_visible_violation` with `none`
(`scripts/simulate_independent_reassessment.py:150-160`).

**Required:** preserve raw evaluator answers, but add a frozen cross-field
coherence flag and handling rule before interpreting variation as substantive
disagreement. Repair the fixture and add regression coverage. Do not silently
coerce or discard an evaluator's contradictory record.

### 5. The judge condition and reporting contract still disagree with the plan

The plan claims full-codebook information-state parity
(`analysis-plan.md:63-69,84-90`). Humans answer all role-specific questions in
identification-first order (`benchmark/study-a/schema.md:54-64,113-122`), while
the judge receives only `task_success` in the linguistic pass and only
`policy_compliance` plus `refusal_outcome` in the policy pass
(`scripts/run_study_a_judge.py:54-65,79-123`). These are different grading
scaffolds.

Two remaining plan–code gaps also matter:

- C4's policy-at-stake result is not split by unanimous versus majority support
  (`scripts/analyze_independent_reassessment.py:954-1028`).
- S3 class and confusion outputs merge supported rows across those support levels
  (`scripts/analyze_independent_reassessment.py:1066-1080,1186-1238`).

The plan's numeric description is wrong as well: 17, not “~21,” of the 37
cross-judge label divergences are
`compliant` ↔ `no_policy_or_authority_limit`. There are 21 policy-compliance
divergences in total.

**Required:** either rerun the judges with the full role-specific scaffold or
describe the current files as minimal-rubric, non-parity comparators. Do not
replace them merely because they contain errors: those errors are legitimate
judge-failure evidence. Predefine visible-rule sentinel checks, keep current
development runs auditable if new comparators are generated, correct the 17/37
count, and implement the promised support-status splits.

## Additional required tightening

- **Realized N.** `unanimous` currently combines 2/2 and 3/3, while 2/3 is
  `majority`. Because partial blocks are retained, report support-count/N strata
  (at least 2/2, 2/3, and 3/3) for C1–C4 and comparator summaries. This is a
  descriptive coverage readout, not an N=2-versus-N=3 counterfactual.
- **Pair terminology.** “Eight strict minimal pairs” overstates the materials.
  P001, for example, changes context, source role, pragmatic status, response act,
  and requested task. Use “paired contrasts” or “controlled contrasts” in the
  Study A plan. Preserve the stronger instruction-source-sensitivity metric in
  the manuscript only for future materials that actually isolate that construct.
- **Meaning of disagreement.** S4 preserves raw first-pass heterogeneity; it
  cannot identify stable interpretive populations or distinguish ambiguity from
  fatigue, practice effects, terminology drift, item–rubric mismatch, or
  confusion. Keep claims at the level of observed first-pass convergence.

## Contradictions preserved

- **Are the sentinel failures themselves blockers?** The Chen-profile review
  treats the lack of a matched validity anchor as a blocker. The chair's narrower
  resolution is that obvious judge errors are expected evidence in a validation
  study; the design defect is calling a different scaffold “parity” and treating
  parse success or aggregate concordance as semantic validation.
- **Must internally inconsistent ratings be rejected?** No. Rejection would hide
  measurement variation. Preserve them and flag them; prevention in the form may
  be added only where the dependency is logically definitional.
- **Is counterbalancing mandatory?** Only the false no-adjacency guarantee is a
  demonstrated code defect. Counterbalancing is preferable, but a single frozen
  order can remain if the common-order limitation is explicit.
- **Is the minimal-pair label a freeze blocker?** It does not invalidate the
  bounded convergence estimand, because C5/C6 are already demoted and
  non-causal. It should still be corrected before tagging because the freeze
  document should not misdescribe its materials.

## Top five revisions before an open-returns tag

1. **Implement and verify stamp 2 as a fail-closed production gate**, including
   real source snapshot, package/order, row map, author snapshot, two comparator
   snapshots, exact commands, consistent state language, and the tag.
2. **Make role pools person-disjoint** or implement a frozen non-overlap
   assignment and private identity-side audit.
3. **Replace the unconstrained shuffle with a constrained, asserted order** and
   freeze the realized presentation order.
4. **Add measurement-integrity diagnostics:** cross-field coherence flags, a
   corrected fixture, regression tests, and 2/2–2/3–3/3 reporting.
5. **Reconcile the comparator and claim contracts:** remove or earn parity,
   predefine sentinels, require complete comparison inputs, add C4/S3
   support-status splits, correct the judge-divergence count, and call the seed
   materials paired contrasts rather than strict minimal pairs.

## Board self-check

The profiles converged on FIX-FIRST, but not on a single theory of failure. Three
findings recurred broadly: incomplete stamp 2, impossible D3, and unflagged
cross-field contradiction. The strongest single-reviewer catch was the false
presentation-order guarantee, which the chair reproduced directly. The board
did not consult external literature and makes no claim that these profiles
represent the named scholars' actual views. The board's conclusion rests on
repository evidence, not the apparent authority or unanimity of the names.
