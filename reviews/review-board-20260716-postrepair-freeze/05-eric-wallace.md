# Eric Wallace profile: instruction-hierarchy and prompt-injection review

*Simulated reviewer profile. This is a stress test, not a statement by Eric
Wallace or evidence of field consensus.*

## One-sentence summary

Study A is a blind, role-separated, fixed-set re-adjudication of 54 benign
prompt–response rows, intended to measure panel convergence and panel-relative
agreement without claiming model ranking, population inference, or direct
authority-sensitivity identification
(`benchmark/study-a/analysis-plan.md:10-19`).

## Strengths

- The revised estimand is appropriately bounded. C5/C6 are now explicitly
  descriptive, response-mediated divergences and are neither necessary nor
  sufficient for authority sensitivity (`analysis-plan.md:135-144`).
- Source-role judgments are carefully separated from source priority, directive
  force, and licensed behaviour (`benchmark/study-a/schema.md:66-79`). The lack
  of a system/developer authority tier is disclosed rather than hidden
  (`analysis-plan.md:206-217`).
- Task success and policy compliance are genuinely separated, allowing
  task-successful/noncompliant and task-failing/compliant outcomes
  (`schema.md:90-97`; `study-protocol-draft.md:55-73`).
- The blindness boundary is strong in principle: packages expose only opaque row
  ID, prompt, and response, while withholding model, item, expected-behaviour,
  author, and judge metadata
  (`scripts/build_independent_reassessment.py:1-8`;
  `study-protocol-draft.md:32-33`).
- The plan repeatedly states that modal labels measure convergence rather than
  correctness and do not become ground truth (`analysis-plan.md:185-194`). That
  is the right epistemic posture.

## Weaknesses and defects

### Freeze blockers

- The open-returns freeze gate is not yet operationally complete. The plan says
  the tagged manifest must hash the exact package/order, row map, author
  snapshot, and build command (`analysis-plan.md:224-225`), but the current
  manifest explicitly leaves the first three unfrozen
  (`FREEZE-MANIFEST.json:53-56`) and contains no package-build command. The
  manifest builder only implements stamp 1 and says stamp 2 requires manually
  extending its frozen-artifact list
  (`scripts/build_study_a_manifest.py:12-16,33-52,92-105`). Yet the plan also
  says the next tag permits opening returns (`analysis-plan.md:253-256`). A
  stamp-1 checkpoint tag is defensible; it is not yet the stated open-returns
  gate.
- D3 is not operationalized by the assignment workflow. The plan permits the
  same person across roles only on different rows (`analysis-plan.md:36-41`),
  while the default protocol assigns every evaluator all 54 rows in one role
  (`study-protocol-draft.md:32-42,81-85`). The package exposes both role paths
  over the same blocks (`build_independent_reassessment.py:311-334,567-588`),
  and ingestion permits the same `rater_id`/row under both roles because role is
  part of the duplicate key
  (`scripts/ingest_independent_reassessment.py:201-205`). Either use
  person-disjoint role pools or implement and validate a person × role × row
  allocation.
- The claimed presentation-order protection is false. The builder says its
  permutation ensures no same-item responses are adjacent, but it merely calls
  `shuffle()` without enforcing that constraint
  (`build_independent_reassessment.py:97-108`). Running the current 54-row source
  through the frozen synthetic salt used by the regression workflow
  (`scripts/simulate_independent_reassessment.py:1028-1030`) produced four
  adjacent same-item pairs. Adjacent repeated prompts invite comparative rather
  than independent judgment and partially reveal the repeated-item structure.
  Use a constrained permutation plus an assertion.
- Judge–panel “information-state parity” is overstated. Humans see all
  role-specific questions in identification-first order
  (`schema.md:54-64,113-122`), whereas the judge sees only `task_success` for the
  linguistic pass and only `policy_compliance` plus `refusal_outcome` for the
  policy pass (`scripts/run_study_a_judge.py:54-65,101-123`). This conflicts with
  the plan's “full evaluator codebook” and parity claims
  (`analysis-plan.md:63-69,84-90`). Either rerun with the full role-specific
  rubric/order or describe the judges honestly as different elicitation
  conditions.
- Cross-field policy labels can be internally incoherent without detection. The
  schema says boundary type `none` must match status `no_boundary_stated`
  (`schema.md:124-130`), but validation checks fields independently
  (`ingest_independent_reassessment.py:69-94`). The synthetic fixture itself
  emits `boundary_stated_no_visible_violation` with type `none`
  (`simulate_independent_reassessment.py:150-160`). At minimum, freeze a
  coherence flag and handling rule; ideally repair the fixture and add a
  regression test.

### Limitations rather than freeze blockers

- All evaluators share one presentation order. Even after adjacency is fixed,
  order effects remain common across the panel; this should be disclosed unless
  orders are counterbalanced.
- The active manuscript still defines “instruction-source sensitivity” as
  pairwise contrast accuracy (`sections/07-metrics.tex:11-13`) and describes the
  seed set as strict controlled contrasts
  (`sections/01-evaluation-problem.tex:22-23`). Study A's C5/C6 cannot populate
  that stronger metric. An explicit reporting firewall is needed when Study A
  enters the paper, although the current analysis plan itself is correctly
  scoped.
- The toy, single-turn set cannot support deployed prompt-injection or
  system/developer hierarchy claims; the manuscript mostly acknowledges this
  (`sections/04-benchmark-construction.tex:7-9`).

## Key question

Is the next tag intended to be merely a stamp-1, pre-data checkpoint, or the
actual open-returns gate? If it is the latter, which exact stamp-2 package files,
presentation order, row map, author snapshot, and reproducible build invocation
will the tagged manifest hash?

## Verdict

**FIX-FIRST.** The scientific core is viable and substantially improved, but the
current artifact should not serve as the open-returns freeze until the gate,
role allocation, ordering constraint, and judge-parity claim are repaired.
