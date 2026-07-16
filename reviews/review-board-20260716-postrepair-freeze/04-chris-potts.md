# Chris Potts profile: pragmatic construct-validity review

*Simulated reviewer profile. This is a stress test, not a statement by Chris
Potts or evidence of field consensus.*

## One-sentence summary

Study A is a disciplined fixed-set panel-convergence study—not an authority
experiment or gold-label oracle—and its core analysis preserves criterion and
disagreement distinctions, but assignment independence and cross-field validity
are not yet executable freeze constraints.

## Strengths

- The inferential target is unusually clear: fixed-set counts, no population
  inference, and panel convergence explicitly not correctness
  (`benchmark/study-a/analysis-plan.md:10-19,182-194`). The analyzer implements
  the 54-row denominator, separates unanimous from majority support, and
  preserves contested rows
  (`scripts/analyze_independent_reassessment.py:395-489`).
- The quotation/source-role codebook cleanly distinguishes task-giver
  contribution, directive wording under discussion, embedded directives, other
  reported content, tool/data output, and policy; it also correctly says
  quotation marks delimiting external content do not create a mention/use
  classification (`benchmark/study-a/schema.json:10-28`;
  `benchmark/study-a/schema.md:66-88`). P001/P002 instantiate the intended
  content/command and mention/use contrasts
  (`benchmark/items/seed-items.csv:2-5`).
- Task success and policy compliance remain genuinely separate, including in
  role-specific instructions and analysis, with no composite score
  (`benchmark/study-a/schema.md:90-97`;
  `benchmark/study-a/materials/study-protocol-draft.md:55-73`;
  `scripts/analyze_independent_reassessment.py:1363-1385`).
- Read-only checks passed: seed-item validation, the full synthetic workflow, and
  all ten manifest SHA-256/byte-count checks.

## Weaknesses and defects

### Freeze blockers

- D3 is incompatible with the package design as written. D3 permits the same
  person in both role pools but forbids that person from rating the same row
  twice (`analysis-plan.md:36-41`); meanwhile every evaluator is targeted for all
  54 rows under an assigned role (`study-protocol-draft.md:35-42,81-85`).
  Ingestion keys duplicates and coverage separately by role, so it cannot detect
  cross-role reuse (`ingest_independent_reassessment.py:201-205,260-290`).
  Freeze must either require disjoint people or freeze a non-overlapping
  cross-role assignment/audit mechanism.
- Cross-field boundary semantics are not enforced or even flagged. The schema
  says `none` corresponds to `no_boundary_stated`
  (`schema.json:175-197`; `schema.md:124-130`), but the simulator assigns
  `boundary_stated_no_visible_violation` together with
  `visible_boundary_type=none`
  (`simulate_independent_reassessment.py:150-160`). Ingestion validates fields
  independently (`ingest_independent_reassessment.py:206-228`), and the passing
  synthetic run silently accepted 70 such contradictory ratings. Repair the
  fixture and define prevention or contradiction-flagging before collection.
- The current manifest is a verified stamp-1 object, not an unblinding freeze: it
  explicitly omits the row map, presentation order, and author snapshot
  (`FREEZE-MANIFEST.json:53-57`), all of which the plan itself says the freeze
  must hash (`analysis-plan.md:224-225`). This is acknowledged, but remains a
  hard gate.

### Limitation and reporting scope

- “Eight strict minimal pairs” overstates the materials
  (`analysis-plan.md:10`): P001, for example, changes context, source role,
  pragmatic status, response act, and requested task
  (`seed-items.csv:2-3`). The plan's later characterization of C5/C6 as
  descriptive, response-mediated divergence correctly neutralizes the causal
  problem (`analysis-plan.md:138-144`); reporting should therefore call these
  controlled contrasts, not strict minimal pairs.

## Key question

Will any individual serve in both roles? If yes, what frozen assignment and
identity-side audit guarantees that person never rates the same row twice while
the protocol still targets full 54-row coverage?

## Verdict

**FIX-FIRST** — the estimands and analysis logic are credible, but D3 is
presently unenforceable, contradictory schema combinations pass the regression
gate, and stamp 2 is still required before unblinding.

## Scope note

The absence of a direct authority test is not a defect because the plan
explicitly removes that claim (`analysis-plan.md:15-19,214-217`). The cited
“unanimous 4/4” simulated board is decision provenance, not evidence of field
consensus (`analysis-plan.md:63-73`). No outside findings were invoked.
