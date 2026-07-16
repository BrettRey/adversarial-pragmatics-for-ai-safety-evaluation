# Study A analysis-plan review (pre-freeze): 2026-07-15

<!-- SUMMARY: GPT-5.6 pre-freeze review of the Study A analysis plan; verdict not-ready-to-freeze; blocker 3 confirmed+fixed, blockers 1-2 confirmed (1 with wording correction); blockers 4-8 unverified · status: open · updated: 2026-07-15 -->

Reviewer: GPT-5.6 (codex `gpt-5.6-sol`, ultra reasoning, ~197k tokens),
read-only pass over the frozen-plan artifacts. Purpose: decide whether the
Study A analysis path is ready to freeze as a pre-registration **before** any
external evaluator's re-adjudication data is opened. The reviewer was told not
to open `private/study-a/self-pilot/` outcomes, so its read of the plan is not
anchored on results.

Full transcript: `scratchpad/study-a-plan-review-gpt56.md` (1.2 MB, includes all
file reads). Extracted final answer: `scratchpad/study-a-review-final.md`.

**Reviewer verdict: not ready to freeze.** Eight blockers.

## Verification status

I (Claude, Opus 4.8) independently verified three blockers so far:
**blocker 3** (judge-column mismatch) — CONFIRMED and fixed; **blocker 2**
(no confirmatory-analysis contract) — CONFIRMED, no code fix, needs the estimand
table; **blocker 1** (N-dependent stable reference) — CONFIRMED in substance,
with the reviewer's "N unset" wording corrected (a ≥2/role floor exists). The
remaining five (4–8) are the reviewer's claims, code-anchored but not yet
independently verified by me. They are recorded below as claims to
check, not as established facts. This matters because the plan-freeze decision
should rest on verified findings, not on a single model's say-so (LLM critique
is a sparring aid, not evidence).

Pivot context: the project moved from "freeze one blessed analysis path" to a
**multiverse** design (report the result across the defensible analytic choices
and judge robustness across them; Steegen, Tuerlinckx, Gelman & Vanpaemel 2016).
Several blockers below (4, 5, 6) are therefore not "pick one path" problems but
the **axes of the multiverse grid** plus the small-N inference caveats.

---

## Blocker 3 — CONFIRMED and FIXED (2026-07-15)

**Producer↔analyzer column-format mismatch: the judge-validity comparator
scores zero rows on real producer output while reporting "available".**

Corrected description (my first framing said "eligible is always empty"; that
overstated it — it is empty only on the real producer's format, and the
synthetic fixture masks the bug by using the other format):

- The **real judge producer** `scripts/run_llm_judge_validation.py:127` writes
  `judge_labels.csv` with **`judge_`-prefixed** columns (`judge_task_success`,
  `judge_policy_compliance`, `judge_refusal_outcome`, plus `human_*`/`match_*`).
  Verified against a real header
  (`benchmark/results/local-pilot-20260630-185417/judge_validation/judge-validation-glm-compact-20260701/judge_labels.csv`).
- The **analyzer** `analyze_independent_reassessment.py` read the **bare** name
  (`task_success` etc., from the `comparable` dict). On the real producer's
  file `.get("task_success", "")` returns `""` for every row → `eligible`
  empty → `matched = 0`, `accuracy = ""`, yet `availability` was
  `"available" if judge_rows else "not_available"` (keyed off the file being
  non-empty), so the output read as "judge validation ran" over nothing.
- Why it wasn't caught: the **synthetic fixture** (`benchmark/study-a/_runs/
  synthetic/private/judge_labels.csv`, produced by the `simulate_*` path) uses
  **bare** columns, so the analyzer worked on it. The two halves of the real
  pipeline (LLM-judge producer → `build_independent_reassessment.py:610`, which
  copies the judge file **verbatim** into `private_dir`) were never wired
  together and no test exercised the analyzer on real producer output.
- Secondary, confirmed: the lookup keyed only on `(item_id, model)`; the file
  carries a `prompt_variant` column, so multiple variants/runs silently
  overwrote (last row wins).

**Fix applied** (`analyze_independent_reassessment.py`, +51/−6): added
`judge_value(row, criterion)` (reads `judge_<criterion>`, falls back to bare
`<criterion>`, so real producer output and synthetic fixtures both work);
`build_judge_lookup()` raises on duplicate `(item_id, model)` keys instead of
overwriting; availability is now `available` / `no_predictions` / `not_available`
so a missing judge column reads as `no_predictions`, not `available`.
Verified: synthetic (bare) output unchanged (task 0.961, policy 0.824, refusal
1.000); a prefixed-column copy of the same data now scores **identically**
instead of "available / 0 rows"; dup-key guard raises; missing column →
`no_predictions`; full output-file set unchanged; module compiles.

**Deferred to the estimand work (not in this fix):** a versioned
producer/analyzer input schema + semantic crosswalk (e.g. the historical-v7
`not_applicable`→`not_a_refusal` remap), retaining raw + normalized values, and
the frozen choice of *which* comparator condition/prompt_variant is canonical.

---

## Blocker 2 — CONFIRMED (verified 2026-07-15; no code fix — needs the estimand table)

**The plan has no confirmatory-analysis contract.**

- `primary_criteria()` (`analyze_independent_reassessment.py:142`) is misnamed:
  it returns **all 10 scalar single-select fields** (5 per role — linguistic:
  source_role_clarity, scope_reference, clarification_required,
  response_act_performed, task_success; policy: visible_boundary_status,
  visible_boundary_type, information_flow_action_licensing, refusal_outcome,
  policy_compliance), i.e. everything except confidence/rationale/source_roles
  and multiselects. No field is designated over any other; "primary" is asserted
  by the name, not established by the logic.
- A **second, undeclared** narrowing makes it worse: the author- and
  judge-comparison stages use a different hardcoded set of only 3
  (`task_success`, `policy_compliance`, `refusal_outcome`, the `comparable`
  dict). So one script carries two implicit "primary" sets (10 for
  agreement/reference, 3 for comparison) that disagree, neither declared.
- **No plan document** pre-specifies outcomes: grep across `schema.md`,
  `annotation-protocol.md`, and the notes for primary/confirmatory/co-primary/
  success-criterion/estimand returns nothing for Study A. The only "exploratory"
  hits are the self-pilot diagnostics (a different thing); the figures note
  (`next-steps-and-figures-plan.md`) is an explicit *menu* of candidate figures
  ("Figure 10 … suggested form after judge run"), not a pre-specification.

Not a code bug; a spec gap. **Resolution = the estimand table** (outcome, unit,
eligible rows, metric, denominator, missing/escape handling, exclusions per
row), with a declared hierarchy: task-success and policy-compliance
agreement/reference-yield co-primary; author and locked-judge comparisons
secondary; the other seven fields, phenomena, model summaries, rationales, and
burden exploratory. This is the spine the multiverse is written onto; without it
there is nothing coherent to freeze. Load-bearing blocker.

## Blocker 1 — CONFIRMED IN SUBSTANCE, reviewer wording corrected (verified 2026-07-15)

**The stable-reference machinery is sharply N-dependent and N is only
floored, not pinned.**

- Verified analyzer mechanics (`consensus()`, `analyze_...py:88`;
  `MIN_REFERENCE_RATERS = 2`): <2 ratings → `insufficient_raters` (no stable
  reference); **exactly 2 → any disagreement is a `tie`, so a stable reference
  requires unanimity**; 3 → a 2-1 `majority` counts. So the co-primary
  "reference yield" outcome degrades discontinuously at N=2.
- Correction to the reviewer: "target N ... remains unset" is **imprecise**. The
  protocol draft sets a floor — "at least two" evaluators per role
  (`study-protocol-draft.md:69`), full 54-row coverage each (line 33), "a stable
  independent reference requires at [least two]" (line 102).
- Genuinely unset: whether the analysis **assumes 2 or 3+** per role (which
  changes unanimity-vs-majority), any **maximum / N-based stopping rule** (only a
  time-based collection cutoff exists, procedure step 5), a **dropout-replacement
  rule**, and whether the two role pools must be **person-disjoint** (the
  independence section bars item-developers as first-pass raters but does not say
  a linguistic rater can't also be a policy rater).
- *Fix:* in the estimand table, state the assumed N per role and how "stable
  reference" is defined at that N (at N=2, unanimity-or-nothing); add max /
  stopping / replacement rules and role-pool disjointness. **(Structural design
  gap, interacts with the co-primary definition; not a multiverse axis.)**

## Blockers 4–8 — reviewer claims, not yet independently verified

4. **Missingness / escapes / disagreement / P008 eligibility open.** Zero-rated
   rows disappear; partial returns enter available-case analysis silently;
   unanimous `item_problem` / `insufficient_visible_context` becomes a stable
   "reference" and enters accuracy; 2–1 dissent labeled stable and omitted from
   the instability queue; P008 enters every row-level analysis with no strict-
   pair rule. `ingest_independent_reassessment.py:259`, `analyzer:202`,
   `DECISIONS.md:21`. *Fix / multiverse axes:* build the full role×54-row grid;
   freeze available-case vs complete-rater rules; distinguish unanimous /
   disputed-majority / tied / insufficient references; exclude
   item-problem/context escapes from comparator accuracy; state whether
   substantive ambiguity stays eligible. Retain P008 for row-level analyses,
   exclude only from any strict-pair endpoint.

5. **Judge validity & "minority recall" not pre-specified.** Accuracy silently
   conditions on both stable references and non-missing judge labels; the
   minority-recall file reports every observed class with no frozen minority
   definition, zero-support classes, baseline, or uncertainty; the script cannot
   implement the two planned prompt conditions and substitutes refusal outcome
   for the deferred failure-attribution analysis. `analyzer:607`,
   `notes/next-steps-and-figures-plan.md:232`. *Fix:* freeze exact judge
   run/model/prompt, missing-prediction rule, comparator classes, treatment of
   the 18 self-judged rows; rename per-class recall unless safety-critical
   classes are fixed beforehand; report coverage, confusion counts, majority
   baseline, macro/per-class recall; keep failure attribution deferred.
   (Interacts with confirmed blocker 3.)

6. **Metrics ignore dependence / small effective N.** 54 rows but 18 prompts,
   9 pairs, 3 outputs/prompt, repeated ratings from the same evaluators. Mean
   modal share and row-micro judge accuracy are descriptive, not
   independent-sample estimates; the one-page acknowledges limited
   generalizability, the analyzer does not. *Fix:* state primary results are
   fixed-set counts/fractions without population inference; add item-macro or
   leave-one-pair-out sensitivity; any interval/bootstrap must cluster by item
   or pair; κ/α secondary and explicitly fragile under sparse, skewed classes.
   **(The Gelman small-N caveat; belongs in the multiverse write-up.)**

7. **Operational blinding / role separation incomplete** (direct label blinding
   is fine). Builder preserves model-major source order → one model per 18-row
   block, same prompt sequence repeated across blocks; the root package exposes
   both roles; ingestion does not enforce assigned roles; the policy form
   receives linguistic/task-specific support text.
   `build_independent_reassessment.py:68,178,291`. *Fix:* deterministic,
   counterbalanced, rater-specific orders balanced across models; role-only
   packages; validate `rater_id→role→order`; role-specific support text; review
   the optional practice set for near-isomorphic target cases.

8. **Self-pilot provenance + freeze object insufficient.** "Exploratory-only;
   provenance-logged" names no allowable revision triggers, ledger, or item-
   disposition rule. **A git tag would not freeze private row maps, package
   order, comparator snapshots, or judge prompts.**
   `benchmark/study-a/materials/self-pilot-runbook.md:48`, `DECISIONS.md:73`.
   *Fix:* freeze a revision **ledger** (observation source, date first viewed,
   affected item/field, before/after hashes, rationale, analysis consequence);
   prompts cannot change while retaining old outputs; **tag a manifest that
   hashes** schema, training set, exact package/order, row map, source rows,
   author/judge snapshots, crosswalk, scripts, build command, and analysis
   spec; all later changes are dated deviations. **(This reshapes the freeze
   itself: tag a hashed manifest, not just the commit.)**

## Reviewer says already sound
- No-tie-break rule; per-role source-role separation; no composite score;
  historical risk fields excluded from comparison.

## Disposition
- Do **not** create the freeze tag yet.
- Blocker 3: FIXED 2026-07-15 (analyzer +51/-6, verified).
- Blocker 2: RESOLVED IN DRAFT by benchmark/study-a/analysis-plan.md (estimand
  table + multiverse axes); pending Brett's OPEN DECISIONS D1-D5 and freeze.
- Blocker 8: manifest/revision-ledger spec written into analysis-plan.md; not
  yet built.
- Blockers 4, 5, 6: fold the analytic choices into the multiverse grid; fix the
  silent-handling bugs in ingest/analyzer as they are implemented.
- Blockers 1, 7: structural design decisions (evaluator N + stopping rule;
  counterbalanced blinded packages) — settle before recruiting evaluators.
- Blockers 1, 2, 4–8 still need independent verification before being treated as
  established; only blocker 3 is confirmed.

---

## Blockers 4-7 — VERIFIED 2026-07-15 (before the freeze tag)

Verified against the code. The headline: **blockers 4, 5, 6 are one coherent
plan-vs-code gap** — the frozen analysis plan specifies estimands and handling
the analyzer does not yet implement — and **blocker 7 is a real blinding/ordering
gap in the package builder.**

- **B4 — CONFIRMED (plan↔code gap).** `analyze_independent_reassessment.py:242-244`
  builds references only from non-empty ratings (available-case), and reports
  "reference rows: len(reference_rows)" (line ~841), never yield over a fixed
  54-row denominator. Escape-valued references (`item_problem`,
  `insufficient_visible_context`) are NOT excluded from author/judge comparator
  accuracy. No strict-pair endpoint / explicit P008 rule exists. The estimand
  table (C1-C4, A1, A4) specifies all of these; none is implemented.
- **B5 — CONFIRMED (plan↔code gap).** `judge-minority-class-recall.csv` reports
  per-class recall but has no majority-baseline column and no frozen
  minority-class definition; plan S3 requires baseline + confusion (confusion
  exists, baseline does not).
- **B6 — PARTIAL.** The analyzer emits fractions with no false confidence
  intervals (good — no overclaim), but implements none of the item/pair-clustered
  or leave-one-pair-out sensitivity the plan's inference section requires. A
  missing sensitivity analysis, not a wrong one.
- **B7 — CONFIRMED (builder blinding gap).** Verified: pilot `outputs.csv` is
  model-major (first 18 rows all `qwen3:8b`); `build_independent_reassessment.py:554`
  slices consecutive 18-row blocks with no per-rater shuffle, so each 18-row
  block is exactly one model — a rater rates one model, and the three blocks map
  to the three models. `supportPanel()` is a single hardcoded task/source-role
  string rendered for all roles, so the policy form carries task-flavoured
  support text.

**Freeze implication.** The PLAN is design-complete and correct (board-verified),
but the analyzer and the package builder do not yet implement it. Freezing the
plan now = freezing a spec ahead of its implementation; the "pre-registered
analysis" cannot be run as written until the analyzer (yield/54, escape
exclusion, baseline, clustered sensitivity) and builder (counterbalanced
per-rater order, role-specific support text) are brought to spec and re-verified.
Only blockers 1-3 are both verified and implemented; 4-7 are verified as real and
outstanding.

### Blockers 4-7 — FIXED 2026-07-15 (implementation brought to spec)

- **B4:** `analyze_independent_reassessment.py` now reports reference yield over
  the fixed presented-row denominator (agreement-by-criterion: presented_rows,
  rated_rows, unrated_rows, stable_substantive, stable_escape,
  yield_substantive_over_presented) and excludes escape-valued references
  (`ESCAPE_VALUES`) from both author (`escape_reference_excluded`) and judge
  accuracy.
- **B5:** judge summary adds `majority_baseline` + `majority_class`; minority-class
  recall adds `is_minority`.
- **B6:** judge summary adds `item_macro_accuracy`, `n_items`, `n_pairs`; row-micro
  accuracy kept but no longer the only figure.
- **B7:** `build_independent_reassessment.py` applies a deterministic
  salt-seeded permutation so 18-row blocks mix models (verified: no model-major
  blocks; same salt reproduces the order) and `supportPanel()` is role-specific
  (linguistic vs policy). Residual (documented, not blocking): a single shared
  shuffle, not per-rater counterbalanced orders.
- All verified on the synthetic fixture; the analyzer changes are backward-
  compatible (backward path and two-judge path both clean).
