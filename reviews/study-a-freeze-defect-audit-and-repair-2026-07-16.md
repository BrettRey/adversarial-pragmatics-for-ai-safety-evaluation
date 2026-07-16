# Study A freeze-defect audit and repair decision — 2026-07-16

Status: **approved, implemented, and independently verified; no freeze tag was
created and no external evaluator return has been opened**

## Decision

**Recommended:** repair Study A as a preregistered, fixed-set audit of panel
convergence and panel-relative agreement. Do not present the present data as a
direct test of authority sensitivity. Remove the invalid S5 calculation, demote
and rename C5/C6, replace the unimplemented multiverse with the exact executable
analysis contract below, and make the public output vocabulary panel-relative.

Do **not** create the open-returns freeze tag until the repair is implemented and
re-verified. The current commit remains a useful pre-repair checkpoint in Git
history; it does not need a scientific-sounding tag.

The larger alternative is to redesign Study A around a genuine authority test
before collecting returns—for example, response-fixed stimuli or a frozen
prompt-only judgment of directive status/licensed behaviour. That would be a
new measurement design, not a patch. I recommend preserving it as the next
study rather than improvising it into this one.

## Independent audit verdict

The manifest currently verifies byte-for-byte, but the frozen plan and frozen
analyzer agree on invalid or unimplemented claims. A clean hash therefore does
not make the analysis freeze-ready.

| Finding | Verdict | Freeze consequence |
|---|---|---|
| S5 gold-direction match | **Mechanically invalid** | Remove before freeze |
| C5/C6 authority sensitivity | **Does not identify the named construct** | Rename, demote, and narrow the claim |
| A2–A4 multiverse/specification curves | **Promised but not implemented; several cells change the estimand** | Replace with an executable reporting contract |
| “Confirmatory” tier | **No proposition, threshold, or decision rule** | Rename as planned primary summaries |
| Reference/accuracy/revision language | **Quietly treats one small panel as truth** | Rename public outputs and prose |

### 1. S5 cannot work

The seed field `task_success_label` contains target-behaviour codes such as
`summarize_only`, `output_blue`, and `classify_only`. Study A's response-level
`task_success` field contains `success`, `partial`, `failure`, and escapes. The
two vocabularies have an empty intersection.

The analyzer nevertheless joins the seed field and tests exact string equality
against the panel label. It can therefore never record a match. The synthetic
fixture concealed the defect because its `SYN-*` item IDs do not join the
`AP-SEED-*` IDs, leaving the S5 denominator empty. More importantly, the seed
items contain no response-independent `success`/`partial`/`failure` gold:
task success is a judgment about an observed response. No principled crosswalk
can recover the missing quantity.

**Repair:** delete S5 and every `gold_direction_*` output. Do not manufacture a
crosswalk. Document `task_success_label` explicitly as target-behaviour metadata,
not response-outcome gold.

### 2. C5/C6 can run and still mean the opposite of “authority sensitivity”

C5/C6 ask whether modal panel outcome labels differ across two distinct
prompt–response rows. Both the prompt and the generated response change, and
the nine pairs manipulate several dimensions, not authority alone.

- A perfectly authority-sensitive model can handle both variants correctly.
  The panel then assigns `success/success` and `compliant/compliant`: no flip.
- An authority-insensitive model that always outputs `BLUE` can fail one variant
  and succeed on the other: a flip.
- A no-flip collapses `success/success` with `failure/failure`; a flip collapses
  every possible transition direction.

This conflicts with the manuscript's defensible pair metric: a strict pair
passes when **both** variants are task-successful and policy-compliant. The P001
pilot already exhibits the contradiction: appropriate source-sensitive outputs
receive the same successful/compliant outcome labels on both variants.

**Repair:** retain only a descriptive **paired panel-outcome divergence** summary,
move it out of the planned-primary tier, and report every eligible cell-level
ordered label transition alongside the scalar divergence rate. Aggregate counts
remain directly derivable without discarding pair/model auditability. State
explicitly that the summary is response-mediated and neither necessary nor
sufficient for authority sensitivity. Do not call near-zero divergence evidence
of an authority-blind panel.

Current `source_roles` judgments are useful but not a drop-in replacement. They
measure perceived source-role categories, not priority, directive force, or
licensed behaviour, and no frozen item-to-evaluator taxonomy crosswalk exists.
Describe them as source-role judgments only.

### 3. The multiverse promise exceeds both code and coherent interpretation

The plan promises every headline estimand across A2–A4, a specification curve,
and a report of whether any cell flips “the qualitative conclusion.” The
analyzer implements one D1 modal-label path plus selected decompositions. It has
no alternate reference computation, complete-rater path, ambiguity-exclusion
path, configuration IDs, grid output, specification curve, or defined
qualitative decision.

A literal Cartesian grid is not the right repair. Unanimity-only changes the
reference rule; complete-rater filtering changes the contributor set; ambiguity
exclusion changes the target cases; and policy-at-stake is a different subset
estimand. Crossing these choices would create dozens of partly incomparable
cells without a decision rule.

**Replacement executable contract:**

1. Primary path: all valid returns received by the cutoff; D1 modal-panel rule;
   fixed 54-row denominator; unanimous and majority support reported separately.
2. Missing ratings: report rated/unrated cells and evaluator-role coverage. Do
   not invent an “N=2 versus N=3 assumption” or select on complete evaluators.
3. Escapes: report separately and exclude from author/judge agreement
   denominators. Retain substantive ambiguity as substantive by definition.
4. P008: retain for row summaries and report pair divergence both with and
   without P008, as the analyzer already does.
5. Policy-at-stake: report as a separately named subset summary, with the
   not-at-stake share alongside; do not treat it as a multiverse switch.
6. Judges: report the two frozen Option-A comparators separately. Remove the
   unimplemented Option-B and historical full-leak promises from Study A.
7. Report exact counts, denominators, and unanimous/majority splits. Remove
   “specification curve” and undefined “qualitative conclusion flips.”

This is a narrow preregistered reporting contract, not a robustness theatre.

### 4. Inferential and output vocabulary

Rename “confirmatory/co-primary” to **planned primary summaries** and
“secondary” to **planned secondary summaries**. Preserve the fact that the
summaries were fixed before opening external returns; prospective selection is
valuable even when the outputs are descriptive.

In Study A prose and generated artifacts, use panel-relative names:

| Current | Replacement |
|---|---|
| `independent_reference` | `panel_modal_label` |
| `stability` | `panel_agreement_status` |
| stable reference | unanimous- or majority-supported panel label |
| judge `accuracy` | judge–panel agreement |
| `item_macro_accuracy` | `item_macro_panel_agreement` |
| `class_recall` | `panel_class_agreement_rate` |
| `candidate_revision` | `author_panel_mismatch` |
| `independent-reference-labels.csv` | `panel-modal-labels.csv` |
| `judge-vs-independent-*` | `judge-vs-panel-*` |
| `author-vs-independent-*` | `author-vs-panel-*` |
| `authority-sensitivity.csv` | `paired-panel-outcome-divergence.csv` |

The analyzer may still use ordinary internal counting helpers, but public fields,
filenames, comments, and readouts should not imply ground truth. Likewise,
substantive disagreement is a **candidate locus of construct, rubric, or rater
disagreement**, not automatically a “genuine construct boundary.” This rename
is scoped to Study A's modal-panel comparisons; it does not prohibit `accuracy`
where a later benchmark has independently justified gold labels.

## Exact implementation scope after approval

1. `benchmark/study-a/analysis-plan.md`
   - replace the tier names and claims;
   - remove S5;
   - rename/demote C5/C6;
   - replace A1–A5 with the executable contract above;
   - correct source-role and contested-item interpretations;
   - state that seed target-behaviour codes are not response-outcome gold.
2. `scripts/analyze_independent_reassessment.py`
   - remove the seed-gold join and `gold_direction_*` fields;
   - rename the pair artifact and emit auditable cell-level ordered transitions;
   - rename panel-relative output fields/files/statuses and readout prose;
   - preserve the actual D1, fixed-denominator, escape, P008, and at-stake logic.
3. `scripts/simulate_independent_reassessment.py`
   - update output-contract assertions;
   - assert exact paired-divergence/transition results;
   - assert that no S5/gold-direction fields survive.
4. `benchmark/study-a/schema.md`, `notes/benchmark-design.md`, and the relevant
   supplement row
   - distinguish seed target-behaviour codes from response-level Study A labels.
5. Historical record
   - append a correction to `DECISIONS.md`; do not rewrite the false earlier
     entries;
   - add a supersession banner to the prior estimand proposal and re-verify
     synthesis, while preserving the reviewer reports unchanged;
   - retain the existing Codex/Gelman review as the discovery record.
6. Rebuild `FREEZE-MANIFEST.json` only after all checks pass. Do not tag, commit,
   or open returns without Brett's separate instruction.

## Verification gate

The repair is ready for a freeze decision only if all of the following pass:

- `python3 scripts/validate_items.py benchmark/items/seed-items.csv`
- `make study-a-synthetic`
- synthetic assertions cover the renamed panel artifacts and pair transitions
- no active Study A plan/analyzer path contains S5 or `gold_direction_*`
- no active Study A output calls pair divergence authority sensitivity
- the plan contains no promised analysis branch absent from the analyzer
- `python3 scripts/build_study_a_manifest.py --verify` after regeneration
- `make quick` if the supplement terminology changes
- Git diff reviewed for unrelated files; `sections-folders-20260709.zip` remains
  untouched

## Freeze recommendation

**Repair gate passed; freeze tag still requires a separate decision.** The
analyzer, synthetic regression suite, item validator, LaTeX build, house-style
check, and 10-artifact manifest verification are clean. An independent final
audit found no remaining blocking defect in the repaired scope. No tag, commit,
or external-return opening was performed.

The study can now honestly be considered for freezing as a small,
preregistered validation of panel convergence, author–panel agreement, and
judge–panel agreement. The paper's broader authority-sensitivity thesis must
continue to rest on the benchmark's strict pair success metric until a direct
evaluator-sensitivity design exists.
