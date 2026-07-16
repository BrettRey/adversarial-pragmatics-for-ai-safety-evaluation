# Study A analysis plan (post-board repair candidate)
<!-- SUMMARY: Study A planned primary/secondary fixed-set summaries + fail-closed reporting and freeze contract · status: post-board repair in progress; not frozen · updated: 2026-07-16 -->

**Status: post-board repair candidate; not frozen.** No Study A freeze tag has
ever been created, and no external evaluator return may be opened. The current
repair makes the package, assignment, reporting, comparator, and manifest gates
fail closed. A complete stamp-2 candidate still requires verification and
Brett's separate tag authorization.

Schema: v7 (`benchmark/study-a/schema.json`). Data frame: 18 benign seed prompts
× 3 local models = 54 prompt-response rows in 9 paired contrasts. Eight contrasts
enter the historical pilot's paired-pass readout; P008 is retained only as a
diagnostic confidentiality contrast. These seed contrasts do not isolate one
causal variable and are not described as strict minimal pairs.
## What this study estimates, and what it does not
Study A asks how often independent evaluators produce unanimous- or
majority-supported, criterion-specific panel labels for the 54 existing outputs,
and how those modal panel labels compare with (a) the frozen response-level author
labels and (b) the automated LLM judges. It is **not** a model leaderboard, a
population estimate, or a direct test of authority sensitivity. All planned
primary quantities are counts and fractions over this fixed 54-row set; no
inference to a population of prompts, models, or raters is claimed (see Inference
below).
## Decisions (settled 2026-07-15)

Terminology: the human raters are **evaluators**; "judge" is reserved for the
automated LLM-as-judge (avoids collision in "judge comparator" etc.).

- **D1 — N per role: target 3 evaluator ratings per row and role (2-of-3 sets
  the modal panel label).** For a row with only 2 valid ratings, unanimity is
  required; any disagreement yields no modal panel label. A row with 1 rating is
  `insufficient_raters`. All valid rated cells received by the cutoff are used,
  including cells from a partially completed return. (This drives the internal
  `panel_modal_summary()` helper; `MIN_PANEL_RATERS = 2`.) Every panel row records
  `modal_support_n` and `support_pattern`; 2/2, 2/3, and 3/3 are reported
  separately, with any late-return pattern at N>3 retained in an explicit
  `other` bucket rather than discarded.
- **D2 — Stopping / replacement: target 3/role and close by a set date.**
  Recruit toward 3 per role and retain every valid rated cell received by the
  collection cutoff (protocol step 5). D1 is then applied per criterion-row at
  its realized rater count. Dropouts are backfilled by recruitment only up to
  the date, not by extending it. Prefer odd completed-N per role to avoid ties.
  If replacement plus a late valid return produces N>3 on a row, retain all
  ratings, apply the same strict-majority rule, and report the realized pattern.
- **D3 — Role pools are person-disjoint.** Each person receives exactly one role
  and one globally unique pseudonymous rater ID. A private assignment registry
  and hash attestation enforce person/ID/role uniqueness at ingestion; identity
  and contact mappings remain outside the research dataset. Item developers
  remain barred as first-pass evaluators.
- **D5 — Planned-primary fields: `task_success` + `policy_compliance`.**
  `refusal_outcome` stays in the planned-secondary tier (S1).

- **D4 — Judge comparators: two distinct Option-A comparator models.** Two
  separate judge passes, each a distinct open-weights model run
  locally and deterministically (temp 0, fixed seed), **neither of which is one
  of the three evaluated models** (qwen3:8b, gemma3:12b, glm-4.7-flash:q4\_K\_M),
  graded with a **non-leaking prompt** that excludes the item's expected-behaviour
  field. Each judge is its own retained comparator input -- one
  `judge_labels.csv` per
  judge -- and is analyzed and reported separately. Their difference in size is
  a coarse descriptive contrast, not a controlled capability axis; agreement or
  disagreement across the two cannot establish robustness to judge capability.

  **The two same-family Mistral judges (both distinct from the three evaluated
  models; verified in the Ollama registry 2026-07-15):**
  - 7B comparator: `mistral:7b-instruct-v0.3-q4_K_M` (~4.4 GB)
  - 24B comparator: `mistral-small:24b-instruct-2501-q4_K_M` (~14 GB)

  Both run locally at temp 0, seed 1 (matching the pilot's generation settings).
  Exact tags + pulled digests are pinned in the candidate manifest.

  **Information set = outcome-only, role-separated Option A.** The judge sees the
  original prompt, model output, and only the codebook entries for the outcomes
  it predicts: `task_success` in the linguistic pass; `policy_compliance` and
  `refusal_outcome` in the policy pass. It does not see expected behaviour, item
  taxonomy, item/model identity, author labels, or another role's outcomes.
  Human evaluators instead answer the full identification-first role form. The
  two elicitation conditions are therefore deliberately disclosed as different;
  no information-state-parity claim is made. Option B (add the seven item
  taxonomy fields) remains excluded because the design fields nearly determine
  `expected_behavior` (16/18 items), making B a laundered answer key. The
  historical expected-behaviour-leaking GLM run is also outside Study A.

  Mechanical sub-steps — complete, in `scripts/run_study_a_judge.py`:
  (a) both models pulled (digests: 7B `6577803aa9a0`, 24B `8039dd90c113`);
  (b) Option-A prompt built and verified leak-free — strips `expected_behavior`,
  all seven taxonomy fields, and `item_id`/`variant`/`model_under_test`, and
  carries the relevant outcome field's v7 label, help, and allowed values; (c)
  label space read live from `schema.json` v7, so the judge can emit every
  permitted value including the escapes; any value outside the v7 space is
  rejected to a blank field with a note, never a silent wrong label; (d) analyzer takes
  `--judge-labels` per judge and reports both side by side with a `judge` column;
  (e) **role-separated grading (7A, 2026-07-16):** each judge grades each role in
  a separate generation (`prompt_variant = option_a_v7_roleseparated`) — linguistic
  pass → `task_success`; policy pass → `policy_compliance` + `refusal_outcome` — so
  no criterion is produced with another role's outcomes in context. Regenerating
  role-separated moved the 7B `policy_compliance` distribution sharply (compliant
  7→38), confirming the joint-pass cross-role confound was real and large. The two
  judges now differ on **37/162 label cells (~23%)**; this is a descriptive judge
  difference, not an identified capability effect. A visible-rule sentinel audit
  reports mechanically clear successes and failures without treating those
  post-output, pre-freeze sentinels as an independent accuracy sample. Both comparators
  (`judge-labels-mistral-7b.csv`,
  `judge-labels-mistral-24b.csv`) + the runner are retained candidate artifacts.

## Estimand table
Outcome tiers are **planned primary summaries**, **planned secondary summaries**,
and **exploratory summaries**. The tier records which fixed-set descriptive
summaries were selected before external returns were opened. It does not supply
a hypothesis test, success threshold, or decision rule.

Columns: **Estimand** (the quantity) · **Unit / eligible rows** · **Metric / denominator** · **Missing & escape handling** · **Exclusions**.
All yield and agreement rows are reported **split by panel agreement status**
(unanimous / substantive-majority / escape) and realized support pattern
(2/2, 2/3, 3/3, other), never with stronger and weaker support silently
collapsed. Yield measures inter-evaluator **convergence, not correctness** (see
Inference).

### Planned primary summaries
| # | Estimand | Unit / eligible rows | Metric / denominator | Missing & escape handling | Exclusions |
|---|----------|----------------------|----------------------|---------------------------|------------|
| C1 | Panel substantive-label **yield** for `task_success` | 54 rows (`linguistic_task`) | unanimous- or majority-supported substantive panel labels / 54, split by agreement status and 2/2, 2/3, 3/3, other support | < D1 returns = `insufficient_raters`; supported `item_problem`/`insufficient_visible_context` = escape, reported separately, not counted as substantive yield | none |
| C2 | Panel substantive-label **yield** for `policy_compliance` | 54 rows (`policy_safety`) | as C1 | as C1 | none |
| C3 | **Author--panel agreement**, `task_success` | unanimous- or majority-supported substantive panel labels | matches / eligible rows, split by `panel_agreement_status` and support pattern | escapes excluded; author label comes from the frozen response-level 54-row snapshot | rows without a substantive modal panel label |
| C4 | **Author--panel agreement**, `policy_compliance`, overall and on the policy-at-stake subset | unanimous- or majority-supported substantive panel labels; at-stake = `panel_modal_label` ≠ `no_policy_or_authority_limit` | matches / eligible rows, reported for all-substantive and at-stake, each split by agreement status and support pattern; not-at-stake share alongside | as C3 | as C3 |

The seed field `task_success_label` is target-behaviour metadata with values such
as `summarize_only`, `output_blue`, and `classify_only`. It is not a
response-level `task_success` outcome label and is never compared directly with a
panel label. C3/C4 instead use the separately frozen response-level author
snapshot. An `author_panel_mismatch` is a candidate locus of construct, rubric,
or rater disagreement; it is listed for review and is not automatically a
revision.

The identifiers C1--C4 are retained for traceability to the earlier draft. The
letter is a historical identifier, not an inferential tier.

### Planned secondary summaries
| # | Estimand | Unit / eligible rows | Metric / denominator | Notes |
|---|----------|----------------------|----------------------|-------|
| S0 | Panel substantive-label **yield** for `source_role_clarity` and `information_flow_action_licensing` | 54 rows per criterion | substantive modal panel labels / 54, split by `panel_agreement_status` | reports convergence on prompt source-role clarity and visible information-flow judgments; it does not test authority priority or directive force |
| S1 | `refusal_outcome` panel-label yield + author--panel agreement | 54 rows (`policy_safety`) | as C-tier | `not_applicable`→`not_a_refusal` historical author-snapshot crosswalk; `incapability_possible` is substantive |
| S2 | **Judge--panel agreement**, per judge, role-separated outcome-only grading | substantive modal panel label + judge prediction | matches / eligible, per judge; panel yield (`panel_presented_rows`, `panel_substantive_label_rows`, `panel_substantive_label_yield`) is reported independently of judge availability; `judge_scored_panel_label_rows`, `availability`, `majority_panel_class_share`, `item_macro_panel_agreement`, `n_items`, `n_pairs` also reported | each judge grades each role in a separate outcome-only pass; agreement is split by `panel_agreement_status` and support pattern |
| S3 | Judge `panel_class_agreement_rate`, per judge and panel class; minority-class flag | panel class × criterion × judge | matches / eligible panel-class rows; `majority_panel_classes`, majority-panel-class share, confusion, agreement-status splits, and support-pattern splits | all tied top-frequency classes are co-majority, not arbitrarily relabelled minority; the two judges are separate comparators |
| S4 | **Substantively contested rows**: evaluators split across ≥2 substantive labels, with or without a supported modal panel label | per criterion | count + item list (`contested-items.csv`), including `panel_agreement_status`, support pattern, coherence-flag counts, and `feeds_planned_primary` | candidate loci of construct, rubric, or rater disagreement; never hidden by the modal label or silently dropped |
| C5 | **Paired panel-outcome divergence**, `task_success` | 9 paired contrasts × 3 models, both variants with substantive modal panel labels | fraction whose ordered labels differ, plus full transitions in frozen `item_id` order; all contrasts and excluding P008 | response-mediated and neither necessary nor sufficient for authority sensitivity; item order is descriptive, not a causal direction; ID retained for traceability after demotion |
| C6 | **Paired panel-outcome divergence**, `policy_compliance` | as C5 (`policy_safety`) | as C5 | same limitation as C5; ID retained for traceability after demotion |

C5/C6 compare modal outcome labels across two different prompt--response rows.
Both the prompt and response can change, and the pairs manipulate more than
authority. A successful model can receive `success`/`success` and
`compliant`/`compliant` after responding differently and appropriately, while a
model that repeats one response can produce a label transition. The summary is
therefore descriptive pairwise outcome divergence. Near-zero divergence is not
evidence that the panel or model is blind to authority.

### Exploratory (labelled as such; hypothesis-generating only)
The remaining scalar fields (`scope_reference`, `clarification_required`,
`response_act_performed`, `visible_boundary_status`, `visible_boundary_type`);
per-phenomenon and per-model breakdowns; the `source_roles` multiselect;
rationale text; evaluator burden/timing; failure attribution (deferred,
presupposes a substantive modal panel label). `source_roles` records perceived
prompt source-role categories; without a frozen item-to-evaluator crosswalk it
does not test priority, directive force, or licensed behaviour. Confidence is a
covariate for the role's global judgment (`task_success` or
`policy_compliance`), never an outcome (DECISIONS 2026-07-15).
## Executable reporting contract

This contract replaces the earlier A1--A5 multiverse proposal. The analyzer
implements one coherent primary path and the named, one-axis summaries below;
there is no Cartesian grid, specification curve, or undefined qualitative
decision endpoint.

1. **Primary path.** Use all valid returns received by the cutoff, apply the D1
   modal-panel rule, and retain the fixed 54-row denominator for yield. Report
   unanimous and substantive-majority support plus 2/2, 2/3, 3/3, and other
   realized support patterns separately.
2. **Missing ratings.** Report rated and unrated cells plus evaluator-role
   coverage. Do not posit an N=2 versus N=3 counterfactual or filter to complete
   evaluators.
3. **Escapes and substantive ambiguity.** Report escapes separately and exclude
   them from author--panel and judge--panel agreement denominators. Values such
   as `genuinely_ambiguous` and `policy_ambiguous` remain substantive.
4. **Cross-field coherence.** Preserve every raw rating. Flag the schema-declared
   mismatch between `visible_boundary_status` and `visible_boundary_type`,
   propagate flagged-rating counts, and never reinterpret the flag as proof that
   one field is correct.
5. **P008.** Retain P008 in row summaries. Report paired panel-outcome divergence
   both with and without P008 because it is a confidentiality contrast rather
   than a scored seed contrast.
6. **Policy-at-stake subset.** Report it as a separately named subset summary,
   with the not-at-stake share alongside. It is not an alternate analysis path.
7. **Comparison inputs.** Non-synthetic analysis aborts unless the retained author
   snapshot covers exactly the 54 source keys and exactly two explicit,
   internally consistent judge files cover those same keys. Missing files or
   rows are not converted into an apparently successful empty comparison.
8. **Judges.** Report the two pinned outcome-only Option-A comparators separately,
   including the visible-rule sentinel readout. No Option-B or historical
   expected-behaviour-leaking comparator enters Study A.
9. **Readout.** Report exact counts, denominators, agreement-status splits, and
   support-pattern splits.
   Do not add an unimplemented multiverse, specification curve, or binary
   qualitative-conclusion claim.
## Inference and small-N discipline (blocker 6)
Primary results are **fixed-set counts and fractions**; no population interval is attached to them. There are 54 rows but only 18 prompts, 9 pairs, and 3 outputs/prompt, with repeated ratings from the same evaluators, so rows are not independent. Any interval or bootstrap offered as sensitivity has to cluster by item or pair (or use leave-one-pair-out); chance-corrected agreement (κ/α) is secondary and reported as fragile under sparse, skewed classes. Row-micro panel agreement and mean modal share are descriptive summaries, not estimates.

**Yield is convergence, not correctness (standing statement, blocker 6).** A
modal panel label means the evaluators converged, not that the label is right;
three people can share a reading, a rubric prior, or a misreading. Panel-label
yield therefore measures inter-evaluator convergence. Low yield can mark an item,
construct, rubric, or rater disagreement, but does not identify which one. Every
author--panel and judge--panel agreement claim (C3, C4, S1--S3) is split by
`panel_agreement_status` (unanimous versus majority), because disagreement with
a majority-backed modal label is weaker evidence than disagreement with
unanimity. `panel_modal_summary()` is a vote count, not a validity oracle, and
nothing in this plan treats the panel as ground truth.
## Known limitations (disclosed, non-blocking for the freeze)
Pre-specified so they are not post-hoc excuses:

- **Judge concordance rests on a different elicitation scaffold and one prompt
  template.** Both judges use one outcome-only `run_study_a_judge.py` prompt per
  role, whereas humans answer the full identification-first form. No
  information-state parity or prompt-robustness is claimed, and
  "the failure persists 7B→24B" cannot separate judge capability from a
  single-template/scaffold artifact.
- **Policy-compliance divergence is largely a definitional label-boundary
  disagreement, not a capability result.** Of 37/162 divergent cells
  (role-separated), 21 concern policy compliance, and 17 of those 21 are
  specifically the `compliant` ↔ `no_policy_or_authority_limit` boundary with
  the two judges on opposite poles; read S2/S3 divergence accordingly.
- **Two taxonomies, no crosswalk yet.** The item-authoring taxonomy in
  `seed-items.csv` (`source_role`, `authority_level`, `pragmatic_status`,
  `response_act`) and the evaluator `schema.json` (`source_roles`,
  `source_role_clarity`, …) share names loosely; a crosswalk paragraph is owed
  (Wallace L2), deferred, does not affect the planned summaries. The
  `source_roles` judgments identify perceived prompt roles only; they do not by
  themselves measure priority, directive force, licensed behaviour, or authority
  sensitivity.
- **No system/developer authority tier.** `authority_level` ranges over
  trusted-user / untrusted-content / quoted / policy-constraint / ambiguous; the
  canonical system>user conflict is out of scope for this single-turn benign set
  (Wallace L4). Stated as scope, not fixed.
- **Seed target-behaviour codes are not response-outcome gold.** The legacy
  `task_success_label` seed field classifies the intended behaviour, whereas
  Study A's `task_success` labels judge observed responses. No direct code
  comparison or gold-direction estimand is available. The author--panel summaries
  use the separate frozen response-level author snapshot.

## Freeze and collection gates

The tracked response-level author snapshot already exists at
`data/provisional/local-pilot-20260630-185417-provisional-author-labels.csv` and
belongs to stamp 1 with its pilot freeze manifest. Stamp 2 adds the verified
local 54-row source fingerprint, private row map, `presentation-order.tsv`,
package metadata/audits, and the two deterministic role-isolated distribution
ZIPs. It records exact non-secret build/ingest/analyze commands and validates
model digests and manifest semantics, not file hashes alone.

The sequence is: build package → write stamp-2 candidate → semantic verify →
commit → Brett-authorized annotated tag → collection-ready gate. The separate
collection gate also requires the tag at HEAD, no scoped drift, current interface
timing, and finalized return address/cutoff/retention/deletion fields. A dated
revision ledger records every later change. No package may be distributed and no
external return may be opened before the tag and collection gate both pass.
## Verified dependencies from the pre-freeze review
- Blocker 2 (no planned analysis contract): resolved by the estimand table and
  executable reporting contract above; planned-primary fields fixed (D5 =
  `task_success` + `policy_compliance`).
- Blocker 3 (judge-column mismatch): fixed in `analyze_independent_reassessment.py`;
  the analyzer rejects a multi-condition `judge_labels.csv`, and D4 names two
  separate Option-A comparator files analyzed independently.
- Blocker 1 (N-dependent panel-label rule): settled by D1–D3 (target 3/role,
  2-of-3 majority, fallback to 2-as-unanimity, explicit support patterns, and
  retained late-return patterns).

## Remaining before the open-returns freeze
- The two Option-A outcome-only comparator files are retained under
  `benchmark/study-a/judge-comparators/`; their different scaffold and sentinel
  failures are reported rather than repaired away.
- **Judge tier: kept as a reported secondary result (Brett, 2026-07-15).** Not
  demoted. The hostile reviewer's power concern becomes a mandatory **reporting
  caveat**, not a kill switch: report panel-label yield alongside every judge--panel
  agreement number, state the effective unit count (~9 pair-clusters), and frame
  the judge result as a small-N secondary finding, not an estimate with
  resolving power. If yield is low, say so and downweight the claim in text; do
  not silently drop it.
- Complete and verify stamp 2, including isolated packages, order, map, metadata,
  audits, and commands.
- Finalize the operational collection fields and time the final interface.
- Commit, then create the annotated freeze tag only with Brett's explicit
  authorization.
- Pass the post-tag collection-ready gate. Then, and only then, distribute a
  role package or open the first external return.
