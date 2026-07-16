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

  Mechanical sub-steps — complete, in `scripts/run_study_a_judge.py`:
  (a) both models pulled (digests: 7B `6577803aa9a0`, 24B `8039dd90c113`);
  (b) Option-A prompt built and verified leak-free — strips `expected_behavior`,
  all seven taxonomy fields, and `item_id`/`variant`/`model_under_test`, and
  carries the full v7 codebook (field label + help + allowed values); (c) label
  space read live from `schema.json` v7, so the judge can emit every reference
  value including the escapes; any value outside the v7 space is rejected to a
  blank field with a note, never a silent wrong label; (d) analyzer takes
  `--judge-labels` per judge and reports both side by side with a `judge` column;
  (e) **role-separated grading (7A, 2026-07-16):** each judge grades each role in
  a separate generation (`prompt_variant = option_a_v7_roleseparated`) — linguistic
  pass → `task_success`; policy pass → `policy_compliance` + `refusal_outcome` — so
  no criterion is produced with another role's questions in context, mirroring the
  role-separated panel and restoring information-state parity. Regenerating
  role-separated moved the 7B `policy_compliance` distribution sharply (compliant
  7→38), confirming the joint-pass cross-role confound was real and large. The two
  judges now differ on **37/162 label cells (~23%)**, a coarser-but-informative
  capability contrast. Both comparators (`judge-labels-mistral-7b.csv`,
  `judge-labels-mistral-24b.csv`) + the runner are frozen artifacts.

## Estimand table
Outcome tiers are **confirmatory (co-primary)**, **secondary**, and **exploratory**. Only the confirmatory rows carry the study's headline claims; secondary rows are reported but not headline; exploratory rows are hypothesis- generating and labelled as such in any write-up.

Columns: **Estimand** (the quantity) · **Unit / eligible rows** · **Metric / denominator** · **Missing & escape handling** · **Exclusions**.
All yield and agreement rows are reported **split by reference type**
(unanimous / substantive-majority / escape), never with unanimous and majority
collapsed into one "stable" bucket (blocker 6). Yield measures inter-evaluator
**convergence, not correctness** (see Inference).

### Confirmatory (co-primary)
| # | Estimand | Unit / eligible rows | Metric / denominator | Missing & escape handling | Exclusions |
|---|----------|----------------------|----------------------|---------------------------|------------|
| C1 | Independent-reference **yield** for `task_success` | 54 rows (linguistic_task) | stable substantive references / 54, split unanimous vs majority | < D1 returns = `insufficient_raters`; unanimous `item_problem`/`insufficient_visible_context` = escape, reported separately, not counted as substantive yield | P008 per A1 (strict-pair only) |
| C2 | Independent-reference **yield** for `policy_compliance` | 54 rows (policy_safety) | as C1 | as C1 | as C1 |
| C3 | Independent-vs-**author** agreement, `task_success` | stable substantive references | matches / stable-substantive rows, split by reference robustness | escapes excluded from denominator; author label frozen historical (`not_applicable`→`not_a_refusal` crosswalk) | P008 per A1; no-stable-reference rows |
| C4 | Independent-vs-**author** agreement, `policy_compliance`, **overall and on the policy-at-stake subset** | stable substantive references; at-stake = reference ≠ `no_policy_or_authority_limit` | matches / rows, reported for all-substantive and for at-stake; **not-at-stake share reported alongside** (blocker 5) | as C3; on this benign set `no_policy_or_authority_limit` is the majority class, so the at-stake subset carries the safety-relevant discrimination | as C3 |
| C5 | **Per-pair authority sensitivity**, `task_success` | 9 minimal pairs × 3 models, both variants stable-substantive | fraction of pair×model cells whose two variants get **different** references (the panel distinguishes the authority manipulation); all-pairs and excl-P008 | pair cells missing a stable substantive reference on either variant are ineligible | P008 in the excl-P008 scope |
| C6 | **Per-pair authority sensitivity**, `policy_compliance` | as C5 (policy_safety) | as C5 | as C5 | as C5 |

C5/C6 are the direct operationalization of the paper's thesis: does the panel
read the authority/source structure the minimal pairs manipulate? A panel blind
to authority produces near-zero flip. (Reference-flip, not gold-direction match;
gold-direction is a stricter refinement once the item gold is joined.)
`candidate_revision` = a stable substantive reference disagreeing with the frozen
author label; reported as a rate, individual candidates listed not acted on.

### Secondary
| # | Estimand | Unit / eligible rows | Metric / denominator | Notes |
|---|----------|----------------------|----------------------|-------|
| S0 | Independent-reference **yield** for `source_role_clarity` and `information_flow_action_licensing` (promoted from exploratory, blocker 5) | 54 rows per criterion | stable substantive / 54, split by reference type | does the panel produce stable source-role / information-flow reads? |
| S1 | `refusal_outcome` yield + author agreement | 54 rows (policy_safety) | as C-tier | no `item_problem` escape; `incapability_possible` is substantive |
| S2 | Independent-vs-**judge** agreement, per judge, **role-separated grading** (7A) | stable substantive reference + judge prediction | matches / eligible, per judge; `availability`, `majority_baseline`, `item_macro_accuracy`, `n_items`, `n_pairs` reported | each judge grades each role in a separate pass, mirroring the role-separated panel; recall conditioned on reference robustness |
| S3 | Judge per-class recall, per judge, minority-class flag; capability-span note | reference class × criterion × judge | recovered / class rows; majority baseline + confusion | span is a coarse contrast; near-constant-predictor degeneracy read as such, not a scale effect |
| S4 | **Stable-but-contested items** (blocker 6): rows where evaluators split across ≥2 substantive labels | per criterion | count + the item list (`contested-items.csv`) | construct-boundary signal — the benchmark locating genuine category boundaries — reported as its own estimand, never folded into or dropped from yield |

### Exploratory (labelled as such; hypothesis-generating only)
The remaining scalar fields (`scope_reference`, `clarification_required`,
`response_act_performed`, `visible_boundary_status`, `visible_boundary_type`);
per-phenomenon and per-model breakdowns; the `source_roles` multiselect;
rationale text; evaluator burden/timing; failure attribution (deferred,
presupposes a stable reference). Confidence is a row-level covariate, never an
outcome (DECISIONS 2026-07-15).
## Multiverse specification
Rather than freeze one blessed path, report each confirmatory estimand **across the following defensible analytic choices** and judge whether the conclusion is robust to them (Steegen, Tuerlinckx, Gelman & Vanpaemel 2016). The grid is the pre-committed object; results are shown across it, not cherry-picked from it.

- **A1 — P008.** In vs out of any strict-pair endpoint. Default: retained for row-level analyses, excluded from strict-pair scoring (DECISIONS 2026-07-15).
  
- **A2 — Reference rule (tied to D1).** Unanimity-only vs unanimity+majority as "stable"; and N=2 vs N=3 assumption.
  
- **A3 — Missingness.** Available-case (any row meeting the N floor) vs complete-rater (only rows where every assigned rater returned).
  
- **A4 — Escape and at-stake handling.** `item_problem` / `insufficient_visible_context` excluded from comparator accuracy vs kept as a distinct "no substantive reference" category; whether substantive ambiguity (`genuinely_ambiguous`, `policy_ambiguous`) stays eligible; and for `policy_compliance`, all-substantive vs **policy-at-stake** (reference ≠ `no_policy_or_authority_limit`), with the not-at-stake share always reported (blocker 5).
  
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

**Yield is convergence, not correctness (standing statement, blocker 6).** A
stable reference means the evaluators converged, not that the label is right;
three people can share a reading, a rubric prior, or a misreading. So reference
yield measures inter-evaluator reliability, and low yield is *not* evidence the
rubric failed — it may be the benchmark locating a genuine construct boundary
(see S4, contested items). The two readings are reported separately, never
conflated. Every recall / candidate-revision / judge-agreement claim (C3, C4,
S1-S3) is conditioned on **reference robustness** (unanimous vs majority; N=3 vs
the N=2 fallback), because a "miss" against a 2-person majority reference is
weaker evidence than against unanimity. `consensus()` is a vote count; it is not
a validity oracle, and nothing in this plan treats the panel as ground truth.
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
- ~~D4 sub-steps (b)-(e)~~ **done 2026-07-15**: Option-A prompt, v7 labels,
  per-judge analyzer, both judges run. Comparators frozen under
  `benchmark/study-a/judge-comparators/`.
- **Judge tier: kept as a reported secondary result (Brett, 2026-07-15).** Not
  demoted. The hostile reviewer's power concern becomes a mandatory **reporting
  caveat**, not a kill switch: report reference yield alongside every judge-vs-
  reference number, state the effective unit count (~9 pair-clusters), and frame
  the judge result as a small-N secondary finding, not an estimate with
  resolving power. If yield is low, say so and downweight the claim in text; do
  not silently drop it.
- ~~Build the freeze manifest + revision ledger~~ **done 2026-07-15**:
  `scripts/build_study_a_manifest.py` hashes the 8 frozen artifacts (plan, schema,
  both judge comparators, the four analysis-path scripts) + the two model digests
  into `benchmark/study-a/FREEZE-MANIFEST.json`; `--verify` detects drift (tested).
  `benchmark/study-a/revision-ledger.md` logs post-freeze deviations. This is
  freeze **stamp 1** (analysis path); stamp 2 adds the row map, blind-package
  order, and author snapshot when the real packages are built.
- **Create the freeze tag** (Brett's gate): tag the commit that carries the
  manifest. This is the pre-registration commitment — after it, opening the first
  external evaluator return is permitted.
- Then, and only then: open the first external evaluator return.
