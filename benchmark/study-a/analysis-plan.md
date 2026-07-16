# Study A analysis plan (pre-freeze DRAFT)
<!-- SUMMARY: Study A confirmatory/exploratory estimand table + multiverse axes; DRAFT proposal, resolves review blocker 2, houses blockers 1 and 3; not frozen · status: draft · updated: 2026-07-15 -->

**Status: DRAFT proposal, not frozen, not authoritative.** This document is the deliverable that discharges blocker 2 of `reviews/study-a-plan-prefreeze-review-2026-07-15.md` (the plan had no confirmatory-analysis contract). It is written for Brett to edit and decide. The **OPEN DECISIONS** block near the top lists the calls only Brett can make; until those are settled and this document is frozen via a hashed manifest (blocker 8), no external evaluator return may be opened.

Schema: v7 (`benchmark/study-a/schema.json`). Data frame: 18 benign seed prompts × 3 local models = 54 prompt-response rows; 9 minimal pairs; P008 is a confidentiality contrast, not a clean minimal pair.
## What this study estimates, and what it does not
Study A asks whether independent evaluators produce **stable, criterion-specific reference labels** for the 54 existing outputs, and how those references compare to (a) the frozen original author labels and (b) the automated LLM judge. It is **not** a model leaderboard and **not** a population estimate. All primary quantities are counts and fractions over this fixed 54-row set; no inference to a population of prompts, models, or raters is claimed (see Inference below).
## Decisions (settled 2026-07-15)

Terminology: the human raters are **evaluators**; "judge" is reserved for the
automated LLM-as-judge (avoids collision in "judge comparator" etc.).

- **D1 — N per role: target 3 evaluators/role (2-of-3 majority sets the
  reference).** Fall back to 2 (unanimity required, any disagreement → no
  reference) only for a role where just 2 complete; a role with 1 is
  `insufficient_raters`. All valid returns received by the cutoff are used.
  (Drives `consensus()`; `MIN_REFERENCE_RATERS = 2`.)
- **D2 — Stopping / replacement: target 3/role, close by a set date, fall back
  to 2.** Recruit toward 3 per role; analyze whoever completed by the collection
  cutoff (protocol step 5). A role short of 3 uses the D1 fallback and is
  flagged; dropouts are backfilled by recruitment only up to the date, not by
  extending it. Prefer odd completed-N per role to avoid ties.
- **D3 — Role pools need not be disjoint people.** One refinement: the same
  person must not rate the *same row* under both roles (avoids within-person
  priming of the policy read by the linguistic read, and keeps the
  criterion-divergence analysis across independent people). Different people, or
  the same person on different rows, is fine. (Item-developers remain barred as
  first-pass evaluators.)
- **D5 — Co-primary set: `task_success` + `policy_compliance`.**
  `refusal_outcome` stays secondary (S1).

- **D4 — Judge comparator: Path A, two independent judges spanning a capability
  range.** Two fresh judge passes, each a distinct open-weights model run
  locally and deterministically (temp 0, fixed seed), **neither of which is one
  of the three evaluated models** (qwen3:8b, gemma3:12b, glm-4.7-flash:q4\_K\_M),
  spanning weak-local → strong-local, graded with a **non-leaking prompt** (must
  not include the item's expected-behaviour field). The judge-validity claim is
  then *robustness across the capability span*: does the miss-the-minority-class
  failure persist from the weaker to the stronger judge? Each judge is its own
  frozen comparator — one `judge_labels.csv` per judge (the blocker-3 dup-guard
  forbids mixing conditions in one file), analyzed separately and reported side
  by side. A frontier API model was rejected as a frozen comparator: most
  capable but least reproducible (non-deterministic, paid, stale). "Most
  capable" was rejected as the target; capability is a dimension to sweep, not to
  maximize.

  **The two judges (same-family Mistral span, capability isolated, family held
  constant; both distinct from the three evaluated models; verified in the
  Ollama registry 2026-07-15):**
  - weak: `mistral:7b-instruct-v0.3-q4_K_M` (~4.4 GB)
  - strong: `mistral-small:24b-instruct-2501-q4_K_M` (~14 GB)

  Both run locally at temp 0, seed 1 (matching the pilot's generation settings).
  Exact tags + pulled digests are pinned in the freeze manifest.

  **Information set = Option A (realistic-deployment), per the 2026-07-15 review
  board (unanimous 4/4; `reviews/review-board-20260715-d4-judge-infoset/`).**
  The judge sees only the original prompt, the model output, and the full
  evaluator codebook (definitions, not just label names). This matches what the
  human evaluators see (`study-protocol-draft.md:30`: prompt + response + rubric,
  everything else hidden), preserving information-state parity with the panel
  that defines the reference. Option B (add the seven taxonomy fields) was
  rejected: verified empirically that `(source_role, authority_level,
  pragmatic_status, response_act)` nearly determines `expected_behavior` (16/18
  items), so B is a laundered answer key. B is retained only as a pre-registered,
  labelled ceiling (see A5).

  Mechanical sub-steps (design + models fixed): (a) pull both models [done];
  (b) build a genuinely non-leaking prompt — strip `expected_behavior`, **all
  seven taxonomy fields, and the `item_id`/`variant`/`model_under_test`
  identifiers** (both prompt variants currently emit the full facts list, so
  dropping only `expected_behavior` would still be Option B), and include the
  full codebook definitions; (c) **migrate the judge label space to v7** — the
  producer cannot currently emit `insufficient_visible_context`, `item_problem`,
  `no_policy_or_authority_limit`, or `not_a_refusal`, so judge-vs-reference
  disagreement would be partly schema mismatch; apply the
  `not_applicable`→`not_a_refusal` crosswalk; (d) extend the runner/analyzer to a
  named judge file per judge; (e) run each judge to its own `judge_labels.csv`.

## Estimand table
Outcome tiers are **confirmatory (co-primary)**, **secondary**, and **exploratory**. Only the confirmatory rows carry the study's headline claims; secondary rows are reported but not headline; exploratory rows are hypothesis- generating and labelled as such in any write-up.

Columns: **Estimand** (the quantity) · **Unit / eligible rows** · **Metric / denominator** · **Missing & escape handling** · **Exclusions**.
### Confirmatory (co-primary)
| # | Estimand | Unit / eligible rows | Metric / denominator | Missing & escape handling | Exclusions |
|---|----------|----------------------|----------------------|---------------------------|------------|
| C1 | Independent-reference **yield** for `task_success` | 54 rows (linguistic_task) | Count and fraction of rows with a stable reference / 54 | Rows with < D1 returns = `insufficient_raters` (no reference); unanimous `item_problem` or `insufficient_visible_context` = "no substantive reference", reported separately, not counted as yield | P008 per A1 |
| C2 | Independent-reference **yield** for `policy_compliance` | 54 rows (policy_safety) | Count and fraction with stable reference / 54 | as C1 (escape values `item_problem`, `insufficient_visible_context`) | P008 per A1 |
| C3 | Independent-vs-**author** agreement, `task_success` | rows with a stable substantive reference | matches / stable-substantive-reference rows | escape references excluded from the denominator; author label is frozen historical (`not_applicable`→`not_a_refusal` crosswalk applied before compare) | P008 per A1; rows with no stable reference |
| C4 | Independent-vs-**author** agreement, `policy_compliance` | as C3 | matches / stable-substantive-reference rows | as C3 | as C3 |

`candidate_revision` = a stable substantive reference that disagrees with the frozen author label. Reported as a rate; individual candidates are listed, not acted on inside this study.
### Secondary
| # | Estimand | Unit / eligible rows | Metric / denominator | Missing & escape handling | Exclusions |
|---|----------|----------------------|----------------------|---------------------------|------------|
| S1 | Independent-reference yield + author agreement, `refusal_outcome` | 54 rows (policy_safety) | as C-tier | `refusal_outcome` has no `item_problem` escape but has `incapability_possible`; treat as substantive | P008 per A1 |
| S2 | Independent-vs-**judge** agreement, `task_success` / `policy_compliance` / `refusal_outcome`, **for each of the two judges** | rows with stable substantive reference **and** a judge prediction | matches / eligible; report `availability` (available / no_predictions / not_available) per judge | judge missing-prediction rows excluded from denominator, counted in coverage | P008 per A1 |
| S3 | Judge per-class recall on the reference classes, **per judge**, plus whether the minority-class failure **persists across the capability span** | per reference class, per criterion, per judge | recovered / reference-class rows; report majority baseline and full confusion counts | zero-support classes reported as such | as S2 |
### Exploratory (labelled as such; hypothesis-generating only)
The other seven scalar fields (`source_role_clarity`, `scope_reference`, `clarification_required`, `response_act_performed`, `visible_boundary_status`, `visible_boundary_type`, `information_flow_action_licensing`); per-phenomenon and per-model breakdowns; the `source_roles` multiselect; rationale text; evaluator burden/timing; failure attribution (deferred entirely, presupposes a stable reference). Confidence is a row-level covariate, never an outcome (DECISIONS 2026-07-15).
## Multiverse specification
Rather than freeze one blessed path, report each confirmatory estimand **across the following defensible analytic choices** and judge whether the conclusion is robust to them (Steegen, Tuerlinckx, Gelman & Vanpaemel 2016). The grid is the pre-committed object; results are shown across it, not cherry-picked from it.

- **A1 — P008.** In vs out of any strict-pair endpoint. Default: retained for row-level analyses, excluded from strict-pair scoring (DECISIONS 2026-07-15).
  
- **A2 — Reference rule (tied to D1).** Unanimity-only vs unanimity+majority as "stable"; and N=2 vs N=3 assumption.
  
- **A3 — Missingness.** Available-case (any row meeting the N floor) vs complete-rater (only rows where every assigned rater returned).
  
- **A4 — Escape handling.** `item_problem` / `insufficient_visible_context` excluded from comparator accuracy vs kept as a distinct "no substantive reference" category; and whether substantive ambiguity (`genuinely_ambiguous`, `policy_ambiguous`) stays eligible.
  
- **A5 — Judge capability contrast + information-set ladder (tied to D4).** Two
  same-family q4 judges (7B, 24B) as a *coarse capability contrast, not a
  controlled span* (review board caution: two convenience-quantized models are
  not a real capability axis). Report judge-validity for each; "the failure
  persists from 7B to 24B" is a weak-robustness note, not a general claim.
  Information-set ladder, pre-registered: A (realistic) is the comparator; B
  (taxonomy-assisted ceiling) and the old glm full-leak run are reported only as
  labelled severity checks on a negative finding, never as the substitutability
  number.
  

Report a compact multiverse table or specification-curve per confirmatory estimand; state explicitly if any cell flips the qualitative conclusion.
## Inference and small-N discipline (blocker 6)
Primary results are **fixed-set counts and fractions**; no population interval is attached to them. There are 54 rows but only 18 prompts, 9 pairs, and 3 outputs/prompt, with repeated ratings from the same evaluators, so rows are not independent. Any interval or bootstrap offered as sensitivity **must cluster by item or pair** (or use leave-one-pair-out); chance-corrected agreement (κ/α) is secondary and reported as fragile under sparse, skewed classes. Row-micro accuracy and mean modal share are descriptive summaries, not estimates.
## Freeze object (blocker 8, not yet done)
A git tag alone does not freeze the private row map, package/presentation order, comparator snapshots, or judge prompts. Freezing means tagging a **manifest that hashes**: this analysis plan, `schema.json`, the training/practice set, the exact blind-package build + presentation order, the row map, the frozen author snapshot, the frozen judge snapshot + comparator condition, the analysis scripts, and the build command. A dated **revision ledger** records any later change (observation source, date first viewed, affected item/field, before/after hashes, rationale, analysis consequence). Until that manifest exists and D1–D5 are settled, the plan is not frozen and no external return may be opened.
## Verified dependencies from the pre-freeze review
- Blocker 2 (no confirmatory contract): resolved by the estimand table above;
  co-primary set fixed (D5 = task_success + policy_compliance).
- Blocker 3 (judge-column mismatch): fixed in `analyze_independent_reassessment.py`;
  the analyzer now rejects a multi-condition `judge_labels.csv`, so **D4 must
  name one comparator condition** (still open).
- Blocker 1 (N-dependent reference): settled by D1–D3 (target 3/role, 2-of-3
  majority, fallback to 2-as-unanimity).

## Remaining before freeze
- **D4 sub-steps (b)-(e):** non-leaking Option-A prompt (strip taxonomy +
  identifiers, add codebook), **migrate judge label space to v7 + crosswalk**,
  per-judge file, run both judges.
- **Judge tier: kept as a reported secondary result (Brett, 2026-07-15).** Not
  demoted. The hostile reviewer's power concern becomes a mandatory **reporting
  caveat**, not a kill switch: report reference yield alongside every judge-vs-
  reference number, state the effective unit count (~9 pair-clusters), and frame
  the judge result as a small-N secondary finding, not an estimate with
  resolving power. If yield is low, say so and downweight the claim in text; do
  not silently drop it.
- **Build the freeze manifest + revision ledger** (blocker 8): hash the artifacts
  listed under "Freeze object" (including both frozen judge snapshots + the
  migrated label space) and tag the manifest, not just the commit.
- Then, and only then: open the first external evaluator return.
