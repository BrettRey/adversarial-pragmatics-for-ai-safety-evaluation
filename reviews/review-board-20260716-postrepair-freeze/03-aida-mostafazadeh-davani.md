# Aida Mostafazadeh Davani profile: disagreement and heterogeneity review

*Simulated reviewer profile. This is an expert-perspective stress test, not
evidence of Aida Mostafazadeh Davani's views or of field consensus.*

## One-sentence summary

Study A is a carefully bounded fixed-set re-adjudication that preserves
first-pass label variation and explicitly separates convergence from
correctness, but its freeze contract still cannot reliably separate meaningful
disagreement from inconsistent, exposure-dependent, or uneven-N ratings.

## Strengths

- The plan is commendably explicit that modal labels are vote summaries, not
  truth: yield means convergence, low yield may reflect item, construct, rubric,
  or rater disagreement, and majority-backed comparisons remain separate from
  unanimity (`benchmark/study-a/analysis-plan.md:103-106,185-194`). The analyzer
  preserves counts, modal share, rater IDs, and contested labels rather than
  outputting only the winner
  (`scripts/analyze_independent_reassessment.py:352-383,465-489`).
- Ambiguity is not collapsed into missingness or error. The schema separates
  `genuinely_ambiguous`, `insufficient_visible_context`, and `item_problem`,
  while `policy_ambiguous` remains substantive
  (`benchmark/study-a/schema.json:33-47,244-262`;
  `benchmark/study-a/analysis-plan.md:169-171`).
- Partial returns and unrated cells are handled transparently: coverage is
  retained, yield uses the fixed 54-row denominator, and available-case inflation
  is avoided (`benchmark/study-a/analysis-plan.md:25-35,163-168`;
  `scripts/ingest_independent_reassessment.py:259-297`;
  `scripts/analyze_independent_reassessment.py:395-463`).
- The multiselect treatment is particularly good: exact source-role sets and
  per-role binary selections remain separate, with no synthetic “Frankenstein”
  set assembled from componentwise majorities
  (`benchmark/study-a/materials/study-protocol-draft.md:106-114`;
  `scripts/analyze_independent_reassessment.py:604-663`).

## Weaknesses and defects

- **BLOCKER — internally contradictory ratings are neither rejected nor
  flagged.** The schema says boundary type `none` matches
  `no_boundary_stated` (`benchmark/study-a/schema.md:124-130`), but ingestion
  validates fields independently without cross-field coherence rules
  (`scripts/ingest_independent_reassessment.py:69-94`). Worse, the regression
  fixture itself emits `boundary_stated_no_visible_violation` together with
  boundary type `none` for compliant boundary cases
  (`scripts/simulate_independent_reassessment.py:150-160`). Add a frozen
  coherence audit that preserves raw answers but flags incompatible combinations
  before treating variation as substantive disagreement.
- **BLOCKER — realized panel size is hidden inside the primary support
  categories.** D1 deliberately uses different rules at N=2 and N=3
  (`benchmark/study-a/analysis-plan.md:25-35`), yet the aggregate output combines
  2/2 and 3/3 as “unanimous” and reports no yield stratum by `rater_n`
  (`scripts/analyze_independent_reassessment.py:407-445`). With blockwise partial
  returns, this confounds convergence with coverage. Freeze support-count/N
  strata—at minimum 2/2, 2/3, and 3/3—for C1–C4 and comparator summaries.
- **BLOCKER — D3 is not operationally realizable as written.** The plan permits
  people in both pools provided they never rate the same row across roles
  (`benchmark/study-a/analysis-plan.md:36-41`), while the protocol assigns every
  evaluator all 54 rows (`benchmark/study-a/materials/study-protocol-draft.md:35-42`)
  and the builder supplies every block under both roles
  (`scripts/build_independent_reassessment.py:567-588`). Ingestion's duplicate
  key includes role, so even the same pseudonymous ID on the same row across
  roles passes (`scripts/ingest_independent_reassessment.py:201-205`). Either
  require person-disjoint pools or freeze and enforce a person-by-role row
  allocation map.
- **LIMIT — the method preserves raw first-pass label heterogeneity, not stable
  disagreement.** S4 is only a split-across-substantive-labels flag
  (`benchmark/study-a/analysis-plan.md:134`;
  `scripts/analyze_independent_reassessment.py:358-363`). It has no frozen means
  to distinguish context-sensitive answers, terminological drift, item–rubric
  mismatch, ambiguity, fatigue/training effects, or plain confusion. Confidence
  is promised as a covariate (`benchmark/study-a/analysis-plan.md:153-155`) but
  explicitly excluded from analysis and never summarized
  (`scripts/analyze_independent_reassessment.py:230-239`); optional practice use
  and qualification route are also unrecorded. This is acceptable only if claims
  remain about raw convergence, not stable interpretive populations. Also treat
  the “unanimous 4/4” simulated board
  (`benchmark/study-a/analysis-plan.md:63-64`) as decision provenance, not field
  consensus.

## Key question

What heterogeneity is Study A intended to preserve—raw criterion-level
first-pass variation or stable, reproducible interpretive disagreement—and, if
the latter, what frozen evidence distinguishes it from context sensitivity,
internal contradiction, terminology drift, item–rubric mismatch, ambiguity,
practice/fatigue effects, and confusion?

## Verdict

**FIX-FIRST** — freeze after adding cross-field coherence flags, realized-N
reporting, and an enforceable cross-role independence rule; otherwise the
primary disagreement readout conflates construct variation with preventable
measurement variation.
