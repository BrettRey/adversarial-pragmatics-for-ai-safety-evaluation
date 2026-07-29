# Adversarial code review: AI-assurance artifact package

**Package:** `code-review-package-2026-07-29.zip`  
**Repository state stated by the package:** commit `812d407`  
**Review date:** 2026-07-29  
**Primary review criterion:** whether an analyzer, validator, or stamper can emit a positive integrity or substantive result on input that should be refused.

## Executive judgment

The repository is well organized, unusually explicit about its failure criterion, and substantially better defended against ordinary structural mistakes than most research artifacts. The supplied checks all remain green: 91 unit tests pass, the evidentiary analyzer’s 19 in-memory checks pass, all artifact validators pass, and the no-data paths correctly return `NOT_ESTIMATED`.

It nevertheless isn’t ready to be tagged and cited as an assurance artifact. I reproduced seven distinct attack families, including a direct false authorization, a procurement calibration `PASS` with 96.6% of node verdicts wrong, leakage accepted by all three delegation empirical analyzers, an explicitly outcome-selected claim accepted as prospective, a sparse Study B design accepted as satisfying crossed scope, and post-freeze re-stamping after a genuine response. The production-binding code also reports `VERIFIED_MANIFEST_BOUND` without ever binding or opening the target item contents.

The most important point isn’t that malformed input can crash a script. The scripts continue normally and emit the very positive statuses the package identifies as dangerous: `authorized`, `PASS`, `ESTIMATED` with integrity diagnostics marked `PASS`, `in_scope_and_evaluable = true`, and `VERIFIED_MANIFEST_BOUND`.

No empirical result has been corrupted, because there are no target results. The theoretical projects also don’t stand or fall with these implementations. But the executable claims currently overstate what the code establishes. The delegation semantics, evidentiary calibration decision rule, and Study B scope/estimator need repair before an immutable release.

## What I ran

I ran every command in the package README, including all test suites and the smoke design analysis. The unit-test counts were:

- evidentiary stamper: 7;
- delegation empirical analyzer: 17;
- delegation semantic validator: 5;
- delegation design analysis: 5;
- Study B validator: 28;
- Study B excellence validator: 10;
- Study B analyzer: 19.

That is 91 passing unit tests. I then attacked the implementations independently of those tests. The accompanying reproduction script runs seven attacks without altering the supplied package; the stamper attack operates on a temporary copy.

## Severity summary

| Severity | Finding | Positive result obtained |
|---|---|---|
| Critical | A grant revoked at 14:01 can issue a valid child grant at 14:02 | proposal at 14:04 is `authorized` |
| Critical | Five-status calibration can collapse almost everything to `not_established` | procurement use is `PASS` with 2,712/2,808 node verdicts wrong |
| High | Hidden references can be placed under neutral keys in all three empirical views | all three analyses are `ESTIMATED`; leakage/oracle checks are `PASS` |
| High | Explicit outcome-selected narrowing evades the claim validator | no validation issues |
| High | Three sparse family–surface cells satisfy a nominal 3 × 2 scope | `scope_gate = PASS`; `in_scope_and_evaluable = true` |
| High | Stamper closure can be reopened and nested genuine responses are missed | write mode returns 0 and rewrites files after the response exists |
| High | Study B’s target-item contract binds digest strings, not item bytes | `production_eligibility = VERIFIED_MANIFEST_BOUND` |
| High | Study B code doesn’t implement the manuscript’s stated multilevel estimand | six cells are reported as `n_families = 6` in a two-stage meta-analysis |
| Medium–high | “Frozen before outcomes” is self-attested inside the analyzed input | coordinated rewrite, rehash, and backdating remains internally valid |
| Medium | Local assignment and predictive-ablation objects aren’t bound to execution | a schedule and feature list can exist without governing the observed endpoints |
| Medium | Several event streams are sorted as timestamp strings | RFC 3339 offsets can produce nonchronological state updates |
| Medium | Response discovery is top-level only | nested responses are ignored by validation, analysis, and the write guard |

## Detailed findings

### 1. Critical: a revoked parent grant can create a valid subgrant

**Code:** `scripts/validate_delegation_artifacts.py:267–330`, especially `295–311`; active-state logic at `391–434`.

`derive_grant_validity()` treats a child grant as valid when its parent is statically valid, allows subdelegation, contains the child’s action classes, scope, and interval, and names the parent grantee as grantor. It never asks whether the parent was active when the child was issued. Revocations are applied later by `normative_state_at()`, after the child’s validity has already been established.

I modified the valid revocation fixture as follows:

- parent grant issued at 13:00;
- parent effectively revoked at 14:01;
- child grant issued by the former grantee at 14:02;
- proposal made by the child grantee at 14:04.

The mutated trace passes the JSON schema and produces no semantic errors. The child is derived as valid and the proposal is `authorized`.

This is a direct false authorization, not merely a provenance weakness. A former authority-holder can mint new authority after revocation.

**Repair.** Separate static grant admissibility from temporal authority. Process grants and transitions in one parsed, chronological event stream. At a child-grant issuance event, every parent must be active immediately before issuance, and the child’s grantor must hold the relevant delegable authority then. Define a deterministic policy for equal timestamps. Add at least these regressions:

- child issued after parent revocation;
- child issued after parent expiry;
- child issued before parent issuance;
- child issued while a conditionally activated parent is inactive;
- the chosen policy for whether later parent revocation cascades to existing descendants.

The current architecture makes the first check impossible in `derive_grant_validity()` because transition effects haven’t yet been incorporated. This needs a state-machine change, not another local Boolean condition.

### 2. Critical: 96.6% wrong node verdicts can earn an evidentiary `PASS`

**Code:** `scripts/analyze_evidentiary_calibration.py:350–398` and `719–729`.  
**Manuscript conflict:** `sections-evidentiary/05-sufficiency-test.tex:136`; `sections-evidentiary/05-research-program.tex:16–21, 84–92`.

The analyzer doesn’t measure selective five-status classification. Its principal error rates are directional:

- false support counts only an observed `support` when support wasn’t expected;
- false defeat counts only an observed `substantive_defeat` when defeat wasn’t expected;
- one confusion metric covers only gap versus defeat;
- another covers only gap versus not established.

Consequently:

- expected `support` → observed `not_established` incurs no error;
- expected `substantive_defeat` → observed `not_established` incurs no error;
- expected `conflict` → observed `not_established` incurs no error.

I generated 252 complete responses: 12 reviewers on all 21 matched cases. Reviewers preserved true `record_gap` verdicts and labelled every other expected status `not_established`. Conjunction resolutions were left correct, every required node was present, all substantive coverage requirements were met, and review burden and privacy fields were clean.

The procurement result was:

- 2,712 wrong node verdicts out of 2,808: **96.5812% wrong**;
- every aggregate metric marked `PASS`;
- 48 node-level metrics marked `NOT_ESTIMATED`;
- use-level result: **`PASS`**.

The second defect compounds the first. At `719–729`, a node metric blocks the class only when it is `FAIL`; node-level `NOT_ESTIMATED` is ignored. The manuscript expressly rejects the result this code accepts: a positive finding cannot be earned by returning `not established` everywhere support is required.

**Repair.** Keep false-support and false-defeat rates as safety diagnostics, but add a complete multiclass decision structure. At minimum:

- exact-status concordance overall and by node;
- status-specific sensitivity/recall for `support`, `substantive_defeat`, `not_established`, `record_gap`, and `conflict`;
- a full confusion matrix, including defeat → not established and support → not established;
- prospectively declared minimum information for every required status/node combination;
- any required node metric that is `NOT_ESTIMATED` must block a use-level `PASS`.

A loss matrix would be better than raw accuracy if some confusions are more consequential, but the loss weights must be prospective and noncompensatory where the manuscript says they are. The adversarial blanket-`not_established` population should become a permanent regression test.

### 3. High: all three delegation empirical leakage checks are semantically blind

**Code:** `scripts/analyze_delegation_programs.py:283–295`, `363–384`, `547–553`, `763–773`, and `947–955`.  
**Schemas:** the three `*input.schema.json` files type `evaluator_view`, `predictor_view`, and `reviewer_view` only as generic objects.

`banned_key_paths()` examines key names. It never examines what values mean. The predictive analyzer also restricts top-level keys to an allowlist, but an allowlisted field can contain an arbitrary nested object.

These views were accepted:

```json
{"case_id": {"x": 1}}
{"case_id": {"x": 0}}
{"case_id": {"x": "supported"}}
```

The values were, respectively, the hidden local reference direction, predictive target, and reviewer reference label. All three analyzers returned `ESTIMATED`; all three reported `leakage = PASS`, `oracle_masking = PASS`, and `reference_join = PASS`.

A banned-token scan can catch accidental field naming. It cannot establish masking. Renaming an answer to `x`, encoding it, or placing it inside a nominal identifier defeats the check.

**Repair.** Make nonleakage true by construction rather than inferred from vocabulary:

1. Construct reviewer and predictor views inside the trusted pipeline from typed source records; don’t accept an arbitrary caller-supplied view as evidence of masking.
2. Give every view an exact recursive schema with `additionalProperties: false` and scalar types. `case_id`, for example, must be a string, not an arbitrary object.
3. Keep hidden labels physically separate and inaccessible to the view-construction process until a committed lock event.
4. Commit the exact bytes shown to the reviewer or predictor, then join the reference later by stable ID.
5. Reserve `PASS` for a verified construction. A key-name scan should be reported as `NO_BANNED_FIELD_NAMES_FOUND`, not as oracle masking.

The three neutral-key attacks should be regressions, but tests alone can’t prove semantic nonleakage if the input format still permits arbitrary values.

### 4. High: the prospective-claim validator accepts explicit post-hoc selection

**Code:** `scripts/validate_claim_register.py:44–97`; schema provenance at `assurance/shared/projective-claim.schema.json:185–193`.

The validator rejects post-hoc rescue only when it sees the exact phrases `only successful` or `failures removed`. The temporal fact is represented by the self-asserted constant `declaration_timing: before_target_outcomes`.

The following content passes with no issues:

- population: “Cases selected after outcome inspection for agreement with the desired direction”;
- condition: “Discordant target cases are excluded once their outcomes are known”;
- declared by: “analyst after target inspection”;
- `declaration_timing`: `before_target_outcomes`.

This isn’t an edge paraphrase. It states the forbidden selection directly. Natural-language semantic integrity can’t be secured by two substring checks.

**Repair.** Narrow the validator’s claim. It can verify schema structure and internal consistency; it can’t verify prospectivity from prose. Prospectivity requires an external chronology:

- hash or sign the frozen claim before the first target outcome exists;
- anchor that digest in a protected tag, release, registry, or append-only log;
- bind target collection to trusted timestamps and a stable target-item inventory;
- represent inclusion/exclusion rules structurally and bind the selection code;
- require a new claim ID/version when the frozen scope changes.

Lexical heuristics can remain as warnings. They mustn’t be presented as a post-hoc-narrowing validator. The register validator should also reject duplicate claim ID/version pairs and enforce version-history rules.

### 5. High: Study B’s scope gate checks margins, not the promised cross

**Code:** `scripts/analyze_study_b.py:1089–1095` and `1130–1147`.  
**Design:** `benchmark/study-b/design.md:259, 263–267`.

The design describes inference crossed by phenomenon family and application surface and requires four bases in each family-by-surface cell. The analyzer instead asks only whether the set contains at least three distinct family labels and two distinct surface labels.

I retained only three cells:

- family 1 × surface 1;
- family 2 × surface 1;
- family 3 × surface 2.

All omitted cells and their bases/observations were removed cleanly. The payload had no schema or structural errors. It contains three families and two surfaces but only three of the six Cartesian cells, confounding family with surface. The analyzer returned:

- `scope_gate = PASS`;
- `scope_in_range = true`;
- `all_cells_evaluable = true`;
- `in_scope_and_evaluable = true`.

**Repair.** Freeze either an explicit set of required cell IDs or the required family and surface sets and their Cartesian product. Require every expected pair exactly once and the declared number of independent bases in every required cell. If sparse crossing is actually intended, the manuscript and output labels need to say so, and no separate family/surface reach claim should be made from a confounded sparse design.

### 6. High: the stamper’s freeze guard both blocks verification and permits mutation

**Code:** `scripts/stamp_evidentiary_artifacts.py:88–116` and `204–223`.

There are three linked problems.

First, `guard_pre_review()` runs in both write and `--check` modes. Once the unblinding boundary passes, `--check` exits 2 before checking whether bindings are current. This contradicts the stated CI-guard role at lines 19–20 and prevents post-freeze integrity verification precisely when it matters most.

Second, the boundary is loaded from the mutable `reviewer-package.json`. Moving that timestamp into the future reopens write mode. Nothing outside the tree anchors the earlier closure.

Third, the genuine-response scan uses `RESPONSES.glob("*.json")`, while the later canonicalization uses `EA.rglob("*.json")`. A genuine response in `responses/nested/genuine.json` is invisible to the guard but is loaded and rewritten by the stamper.

On a temporary copy, I:

1. moved the boundary into the past and confirmed that `--check` was refused;
2. moved the same local field to 2099;
3. created a nested genuine response;
4. made a formatting-only change to a bound bundle;
5. ran write mode.

The stamper returned 0 and rewrote both the bundle and the genuine response.

**Repair.**

- `--check` must remain available after closure and must never invoke the write guard.
- Write mode must consult an externally anchored closure state, not a field it can itself rewrite.
- Response discovery must be recursive or, better, the exact response inventory and permitted layout must be committed and unexpected nested files rejected.
- The stamper should never load and flush response data. Limit its write set to the explicit binding artifacts it owns.
- After first response or closure, use a new artifact-set version rather than mutating the old one.

A protected Git tag can help anchor a released state, but only if the tool verifies against an expected commit/digest that isn’t supplied by the same mutable tree.

### 7. High: Study B binds target hash labels, not target item contents

**Code:** `scripts/analyze_study_b.py:175–217` and `302–377`.  
**Manuscript claim:** `supplement.tex:386–394`.

The production manifest binds a `target_items` JSON file. That file’s contract contains only rows of:

```json
{"item_id": "…", "item_hash": "…"}
```

The analyzer checks that the rows match the digest strings repeated in the result payload. It never resolves a target-item path, loads item content, or recomputes an item hash from the item bytes. The production regression builder consequently obtains `VERIFIED_MANIFEST_BOUND` with 480 synthetic digest strings and no item payloads in the target-item contract.

This verifies consistency among claims about hashes, not that any hash belongs to the prompt or item actually run.

**Repair.** Each target-item entry should either contain the complete canonical item object or bind a relative path to it. The analyzer must resolve the path safely and compute the digest itself. The exact bytes passed to the model should also be committed after context assembly; binding an abstract item record alone won’t catch wrapper or prompt-stack substitution.

### 8. High: Study B doesn’t implement the estimator the paper describes

**Code:** `scripts/analyze_study_b.py:629–688` and `1096–1100`.  
**Manuscript:** `supplement.tex:359–365`.

The supplement promises “a single multilevel model with partial pooling across families and bases” and cluster-robust uncertainty. The implementation instead:

1. computes a mean base effect and a between-base t interval separately for each family–surface cell;
2. passes every cell estimate to a DerSimonian–Laird random-effects meta-analysis;
3. labels the number of cells `n_families`.

In the nominal 3-family × 2-surface synthetic design, the output reports `n_families = 6`. Family, surface, their interaction, and shared family membership aren’t represented. Cell estimates aren’t partially pooled toward family means. The pooled normal interval also treats the cell estimates as the meta-analytic units, while their variances come only from dispersion among four base point estimates and don’t propagate the finite-repeat binomial uncertainty used elsewhere in the analyzer.

This is not a cosmetic naming error. It changes the estimand and uncertainty model.

**Repair.** Either implement the stated joint model or rewrite the paper to describe the two-stage cell meta-analysis and defend its assumptions. A faithful joint analysis would operate at the repeat/base level, propagate outcome uncertainty, and model family, surface, and family × surface structure explicitly. With only three families and four bases per cell, regularization and a full prior/sensitivity analysis are preferable to pretending the variance components are well determined. Report cell-level estimates regardless; don’t let a pooled estimate substitute for them.

### 9. Medium–high: the freeze and manifest checks establish self-consistency, not chronology

**Code:** `scripts/analyze_delegation_programs.py:387–417`; analogous Study B logic at `scripts/analyze_study_b.py:302–377`.

For the delegation programmes, each manifest contains its own content, SHA-256, and `frozen_at`. The analyzer recomputes the digest from the supplied object and compares the self-reported time with the first self-reported lock time in the same input. A coordinated edit can change the manifest, rehash it, and backdate it. The result still reports design-object SHA-256s as verified.

Hashes are doing real work here: they catch accidental or uncoordinated mismatch. They don’t establish that the object existed before outcomes, who authored it, or that an earlier version wasn’t replaced.

**Repair.** Distinguish statuses such as `INTERNALLY_HASH_CONSISTENT` from `PROSPECTIVELY_FROZEN`. The latter requires an expected digest or signed event anchored outside the analyzed payload. Lock times should come from the collection system or an append-only record, not from the outcome rows whose integrity is under review.

### 10. Medium: local randomization and predictive ablation aren’t bound to what was executed

#### Local discrimination

**Code:** `scripts/analyze_delegation_programs.py:473–533`.

The assignment manifest contains five presentation IDs and an order for every observation. Observation rows contain only aggregate arm endpoints and no presentation IDs or observed order. The analyzer proves that a complete schedule exists and that its observation IDs match. It doesn’t prove that the endpoints came from those presentations in that order.

Bind a raw collection log carrying presentation ID, order position, reset/session ID, response hash, and endpoint derivation. Derive the aggregate observation from that log rather than accepting it independently.

#### Predictive typed ablation

**Code:** `scripts/analyze_delegation_programs.py:719–788`.

The feature manifest states which keys belong to the typed and baseline predictors, but the analyzer accepts the two probabilities directly. It doesn’t run or bind a predictor, verify that the typed representation was present only in the typed input, or connect the probability to a committed input/model artifact. `predictor_view` may even be empty under the schema.

A valid ablation needs separately bound typed and baseline views, a frozen executable scoring procedure or signed prediction log, and a reference join after those exact predictions are committed. Otherwise the code analyzes claimed probabilities rather than an ablation.

### 11. Medium: temporal ordering uses raw timestamp strings

**Code:** `scripts/validate_delegation_artifacts.py:353, 408, 490, 507, 803`.

The schema accepts RFC 3339 date-times with offsets, but event streams are sorted by the original strings. Lexical order isn’t chronological order when offsets differ. State transitions, executions, cumulative conditions, and continuity can therefore be applied in the wrong order while each timestamp parses and lies inside the boundary.

Parse once, normalize to UTC, and sort by the resulting aware `datetime` plus an explicit tie-break rule. Add a regression in which lexical and chronological order differ.

### 12. Medium: nested responses are silently outside the evidentiary sample

**Code:** `scripts/validate_evidentiary_artifacts.py:1010–1015`; `scripts/analyze_evidentiary_calibration.py:769–770`; stamper at `88–100`.

Validation, analysis, and the freeze guard all use top-level `glob("*.json")`. A response under a subdirectory is ignored. This can cause selective omission as well as the write-guard bypass above.

Either use recursive discovery with an exact committed file inventory or reject all unexpected directory structure. Silent omission is the unsafe option.

## Additional design assumption to settle

`scope_contains()` and `action_in_scope()` at `scripts/validate_delegation_artifacts.py:183–211` require all constrained parent keys but permit extra child-scope and action-parameter keys. That is safe only if additional parameters are semantically irrelevant or are fully captured by the action class. In tool APIs, an extra parameter can change destination, visibility, persistence, or side effects. Decide explicitly whether scope is open-world or closed-world. If it is closed-world, reject undeclared keys or give each action class an exact parameter schema.

The same clarity is needed for descendant revocation: the current state engine deactivates the named parent grant but has no general cascade rule for already-issued subgrants. That may be an intentional regime choice, but it shouldn’t remain implicit.

## What held up well

Several parts resisted the attacks I tried:

- Ordinary content-hash mismatches are rejected.
- Study B’s bound-path resolution blocks absolute paths and root escape.
- Exact repeat sets, duplicate identifiers, unknown links, and several cross-file inventories are checked carefully.
- Delegation proposal–execution divergence is rejected, and execution is evaluated separately from proposal authorization.
- Missing required delegation families produce `NOT_ESTIMATED` rather than compensatory aggregation.
- No-data paths are honest: the committed empirical records don’t manufacture results.
- The artifacts preserve detailed observation/node vectors instead of hiding everything in one scalar.
- The papers themselves state many of the right distinctions: structural validation versus substantive validity, record gap versus defeat, and internal hash consistency versus trusted provenance. The principal failures arise where the code’s positive status is stronger than those distinctions warrant.

This isn’t a repository of superficial checks. The problem is narrower and more consequential: the tests exercise the intended implementation but not enough hostile alternative implementations of the same input contract.

## Cross-cutting diagnosis

Four patterns recur.

1. **Semantic properties are inferred from tokens.** Leakage is inferred from key names; post-hoc selection is inferred from two phrases. These checks can find accidental disclosure but can’t establish the property named by their `PASS` status.

2. **Provenance is self-attested.** A digest supplied beside the object it hashes establishes internal consistency. A timestamp supplied beside an outcome doesn’t establish chronology. “Frozen” needs an external anchor.

3. **Marginal coverage substitutes for joint coverage.** Study B counts families and surfaces without checking their cross. The evidentiary analyzer counts selected directional errors without ensuring five-status discrimination.

4. **Tests mirror the implementation’s decomposition.** The supplied negative tests are useful but ask whether the code rejects the mistakes its authors already represented. The successful attacks change the representation: answer values under neutral keys, a wrong verdict outside the enumerated confusion pairs, a post-hoc claim without the two trigger phrases, and missing cross-cells with intact margins.

## Repair order

### P0: before either assurance paper is tagged

1. Replace static subgrant derivation with chronological authority-state evaluation.
2. Replace the evidentiary decision rule with complete five-status calibration and make required node-level `NOT_ESTIMATED` blocking.
3. Rebuild reviewer/predictor masking by construction with exact typed views and committed presentation/prediction bytes.
4. Split read-only verification from write authorization in the stamper and anchor closure outside the mutable artifact tree.

### P1: before Study B produces target results

5. Enforce the frozen family × surface cell set and base count per cell.
6. Implement the stated joint estimator, or revise the paper and output names to the estimator actually run.
7. Recompute target-item hashes from actual item content and bind the assembled model input.
8. Bind randomization, ablation inputs, and predictions to raw execution logs.

### P2: hardening

9. Normalize and sort parsed timestamps.
10. Commit an exact response inventory or recursively reject/validate all response files.
11. Make open- versus closed-world scope semantics explicit.
12. Replace positive labels such as `PASS`, `VERIFIED`, and `FROZEN` with narrower labels wherever only internal consistency has been established.

## Regression tests to add

The following test names capture the missing properties rather than just the current implementation:

- `test_subgrant_issued_after_parent_revocation_is_invalid`
- `test_subgrant_issued_before_parent_authority_is_invalid`
- `test_blanket_not_established_cannot_pass_five_status_calibration`
- `test_required_node_not_estimated_blocks_use_pass`
- `test_neutral_nested_value_cannot_carry_local_reference`
- `test_allowlisted_field_cannot_carry_predictive_target`
- `test_neutral_nested_value_cannot_carry_reviewer_reference`
- `test_explicit_outcome_selected_population_is_not_claimed_as_prospective`
- `test_sparse_family_surface_cross_is_out_of_scope`
- `test_check_mode_remains_available_after_freeze`
- `test_nested_genuine_response_blocks_write_mode`
- `test_stamper_never_rewrites_response_data`
- `test_target_item_digest_is_recomputed_from_item_bytes`
- `test_manifest_freeze_requires_external_expected_digest`
- `test_assignment_log_matches_presentation_ids_and_order`
- `test_typed_and_baseline_predictions_recompute_from_bound_inputs`
- `test_offset_timestamps_are_applied_chronologically`

The accompanying script already supplies executable versions of seven of these attack families and can be converted directly into unit tests.

## Publication recommendation

I wouldn’t publish an immutable artifact tag in its present form. The code currently falsifies several concrete executable claims made by the manuscripts:

- the delegation engine can derive an authorization from authority that had already been revoked;
- the evidentiary analyzer can issue the blanket-`not_established` pass the paper explicitly says must be impossible;
- the delegation empirical integrity statuses don’t establish leakage prevention;
- Study B’s scope and estimator aren’t the scope and estimator described in the design and supplement;
- the stamper doesn’t reliably enforce or verify closure.

The papers can survive these findings. No target result needs withdrawal or reinterpretation. But either the code should be repaired before release, or the manuscript claims should be narrowed to describe structural prototypes that don’t yet establish masking, prospectivity, temporal authorization, full five-status calibration, or production binding. For the two assurance papers, repair is preferable: the defects strike the executable centre of the contribution, and the required adversarial tests are now concrete.
