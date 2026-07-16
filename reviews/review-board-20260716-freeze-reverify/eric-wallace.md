# Freeze re-verify — Study A analysis plan (simulated Eric Wallace)
<!-- SUMMARY: re-review after the team revised in response to the 2026-07-15 authority-buried-in-exploratory defect; core defect resolved (authority sensitivity now confirmatory C5/C6, source-role + info-flow yields promoted to secondary S0), but the confirmatory operationalization is reference-flip not gold-direction, and the gold-direction validity test is named yet left un-tiered · verdict: FIX-FIRST (narrow, one tier line) · status: open · updated: 2026-07-16 -->

Reviewer lens: instruction hierarchy, prompt injection, privileged-instruction conflict. Persona simulated for stress-testing. I re-read `benchmark/study-a/analysis-plan.md`, the authority-sensitivity block of `scripts/analyze_independent_reassessment.py` (lines 402-447), the at-stake block (lines 758-802), `benchmark/study-a/FREEZE-MANIFEST.json`, `benchmark/study-a/schema.json` v7, and `benchmark/items/seed-items.csv`. Where I cite a number I checked it against the file. Not re-flagging the plan's DRAFT text or the stamp number per the standing note.

---

## 1. Is the authority-buried-in-exploratory defect resolved?

**The core of it, yes. The last increment, not quite.** Credit first, because the team did more than the floor I asked for:

- **Authority sensitivity is now confirmatory, not absent.** New rows C5/C6 (plan lines 105-106) put per-pair authority sensitivity for `task_success` and `policy_compliance` in the co-primary tier. I asked for "one confirmatory or secondary estimand"; they made it confirmatory. The plan states the point in the benchmark's own terms (lines 108-110): "A panel blind to authority produces near-zero flip." That is the estimand I said was missing from every tier.
- **The operationalization is real and the code matches the prose.** `analyze_independent_reassessment.py` lines 411-447 build `(pair_id, model)` cells, keep only cells where both variants have a stable substantive reference, and count the fraction whose two references differ, reported `all_pairs` and `excl_P008`, with `eligible_pair_cells` printed alongside `flip_rate` so the denominator is visible. That last part matters: on a small set the flip rate is only readable next to its N, and the script exposes it.
- **Source-role yield promoted, and info-flow with it.** S0 (line 118) promotes `source_role_clarity` **and** `information_flow_action_licensing` yield to secondary. Both are genuine scalar fields in schema v7 (lines 33, 200), so these yields already fall out of the existing agreement-by-criterion loop; S0 is an honest tier re-label of numbers the analyzer already computes, not vaporware. This covers my asks (1) and (3) together.

So the specific failure I raised, a "successful" Study A consistent with the panel being blind to authority, no longer holds on the falsification side: near-zero flip now disturbs a headline row.

**Where it is still short: confirmatory C5/C6 is reference-flip (any difference), not gold-direction match, and the gold-direction test is named but assigned to no tier.**

The plan is candid about this (line 111): "Reference-flip, not gold-direction match; gold-direction is a stricter refinement once the item gold is joined." I want to be exact about what that costs, because it is the same reliability-vs-validity seam my first review was about, reappearing one level down.

Reference-flip is a good **falsifier** and a poor **confirmer**. A panel blind to authority gives both variants the same reference (the clean-pair variants differ only in the authority framing), so near-zero flip kills the thesis. That downside teeth is real and I credit it. But a *high* flip rate is necessary, not sufficient, for "the panel reads authority": a panel that distinguishes the variants in the wrong direction, or for a reason incidental to authority, scores an identical flip. `len(set(refs.values())) >= 2` (line 432) counts any difference, including a backwards one. So "C5 succeeded" confirms the panel *distinguishes* the pair, not that it distinguishes it *correctly*. That is discrimination, not validity, and validity is the whole claim of an instruction-hierarchy paper.

The gold-direction match is the sufficient test, and the plan's stated precondition for it, "once the item gold is joined," is **already met**: `seed-items.csv` is now in the freeze manifest (see below), so `expected_behavior` / `task_success_label` are frozen and joinable today. There is no data reason to defer it. Yet gold-direction sits in no tier: not confirmatory, not secondary (S0-S4), not exploratory (lines 124-130), not a multiverse axis (A1-A5). It exists only as a sentence in the C5/C6 note.

That un-tiered status is the residue of the exact degree-of-freedom a pre-registration removes. By my own rule from the first review, promoting a construct across tiers after the first return is open is the freedom the freeze exists to close, and it "has to be done before the tag, or not at all." An estimand named in the frozen text but bound to no tier can be reported post-hoc as headline or footnote depending on how the number lands. The fix is a single line and needs no new data: **give gold-direction authority-sensitivity a tier before the tag.** Secondary is the honest home (it depends on the author gold, exactly like C3/C4, so it belongs beside them, not in the author-gold-independent confirmatory row). If Brett judges reference-flip's caveat sufficient and would rather bind gold-direction to *exploratory only* in writing, that also closes the freedom; what it cannot stay is un-tiered.

I can live with reference-flip **as** the confirmatory row: keeping the co-primary independent of the author answer key is defensible, and parallels the Option-A logic. The objection is not that reference-flip is wrong. It is that the validity version, the one I named by phrase in the first review ("flip in the gold direction... the number that says the benchmark measures what it claims"), is computable, frozen-data-ready, and tier-less.

---

## 2. Lower-priority notes

- **L1 (seed-items freeze): resolved.** `benchmark/items/seed-items.csv` is now a hashed manifest artifact (FREEZE-MANIFEST.json lines 20-23), sha256 `96e1ef4b...`, 7928 bytes, and I verified the hash matches the working file. The 16/18 leak argument and the C3/C4 author comparator now rest on a frozen object. Done.
- **L2 (two taxonomies, no crosswalk): not addressed, but softened by L1.** The plan still names `source_role, authority_level, pragmatic_status, response_act` (lines 64-65) with no paragraph mapping them to schema v7's `source_roles / source_role_clarity / response_act_performed`. `grep` finds no "crosswalk" for the item-authoring/evaluator split. It is milder now only because those columns live in a frozen file a reader can open. Still worth a three-line crosswalk; not a freeze blocker.
- **L4 (no system/developer tier): not addressed, not recorded as deferred.** No mention of a system/developer privilege level or of "instruction hierarchy" here being a two-to-three-tier slice (user vs embedded-content vs stated-policy). `authority_level` in the items still tops out at `trusted_user`/`policy_constraint`. This was always "the paper should say so plainly," so the analysis plan is a defensible place to skip it, but nothing anywhere marks it deferred. One sentence of scope would prevent a reviewer expecting system-prompt conflicts.
- **L5 (policy_compliance gold zero variance): substantially addressed via 5B.** C4 now reports agreement "overall and on the policy-at-stake subset" with the not-at-stake share (lines 104, 140), and the analyzer computes `at_stake_rows`, `not_at_stake_share`, and `at_stake_candidate_revision_rate` (lines 773-792). That surfaces the effective substantive denominator I asked for, as a reported quantity rather than a guessed pre-number. Note the cut is on the reference side (`independent_reference != no_policy_or_authority_limit`), which addresses the trivial-majority-class worry; the all-`compliant` author gold I flagged is handled downstream by the at-stake candidate-revision rate. Good enough; the concern is now visible in the outputs.

---

## 3. Did the revision introduce anything new or wrong?

No correctness bug in the new code. Three things a freeze reviewer should have on the record:

1. **Role-separated judge grading (7A) is a new, material change, not part of my defect.** The judges now grade each role in a separate pass (`option_a_v7_roleseparated`), and the plan reports the 7B `policy_compliance` distribution moved sharply (compliant 7→38) and judge disagreement rose from 26/162 to **37/162** (lines 80-87). It is well-motivated (information-state parity with the role-separated panel) and the judge CSVs were regenerated and re-hashed. I did not re-diff the 37/162 (outside my defect), but I confirmed all nine manifest hashes match the working files, including both judge comparators and the analyzer, so the freeze object is internally coherent, not a half-rebuilt state. Flagging it only because a same-day methodology change to the frozen comparators is exactly the kind of thing that should be seen, not buried; here it is documented.
2. **The code emits a superset of what C5/C6 and 5B name; harmless.** `COMPARABLE` includes `refusal_outcome`, so the authority-sensitivity CSV gets a third `refusal_outcome` flip row not named in C5/C6, and the at-stake columns are written for `task_success` too (where `no_policy_or_authority_limit` never matches, so at-stake trivially equals overall and not-at-stake share is 0). Neither miscounts anything. Tidy the plan text or filter the emitted rows so the CSV and the estimand table say the same thing.
3. **The flip metric leans on `pair_id` and `variant` arriving clean from the row map.** The exclusion `pair_id in {"P008"}` (line 26) matches the seed-items `pair_id` column literally, and I confirmed P008 = AP-SEED-015/016 is genuinely not a clean minimal pair (different phenomena, different gold), so excl-P008 is the right scope. But the analyzer reads `pair_id`/`variant` from the private `row_map`, deferred to stamp 2. If the real row map renames pairs or collapses variant labels, cells silently become ineligible (the `len(refs) == 2` guard drops rather than miscounts, so it fails safe, but a silently empty flip table would read as "no eligible cells," not as an error). Worth a one-line assertion that the row map's pair_id set equals the seed-items pair_id set when stamp 2 is built.

One structural point in the team's favor: adding C5/C6 does not inflate any error budget, because the plan runs fixed-set counts with no population intervals and no p-values (inference section, lines 154-167). There is no alpha to spend across six confirmatory rows, so promoting authority sensitivity was cheap and safe. That is the small-N discipline paying off.

---

## 4. Sign-off

**FIX-FIRST** — one tier line: assign gold-direction authority-sensitivity to a tier (secondary, beside C3/C4) before the tag; the gold is already frozen, so leaving the validity test un-tiered is the one remaining post-freeze degree-of-freedom. Everything else (C5/C6, S0, L1, 5B) is done and I'd freeze it.

— Eric Wallace (simulated), 2026-07-16
