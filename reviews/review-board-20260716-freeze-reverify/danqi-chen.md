# Study A freeze re-verification (judge tier): Danqi Chen (simulated)

<!-- SUMMARY: Re-verify of the 2026-07-15 role-parity defect after the 7A revision; the frozen judge now grades each role in a separate generation, both comparators were regenerated role-separated (prompt_variant option_a_v7_roleseparated), 37/162 divergence and the 7B compliant 7->38 shift both confirmed, manifest re-hashed and verifies clean; verdict FREEZE NOW with three secondary write-up caveats · status: open · updated: 2026-07-16 -->

Reviewer: simulated Danqi Chen persona. Scope: does the 7A revision resolve the
single role-parity defect from my 2026-07-15 freeze review
(`reviews/review-board-20260715-freeze-readiness/opus-danqi-chen.md`), and did it
break anything. Read for this re-verify: `scripts/run_study_a_judge.py` (the role
split), both `benchmark/study-a/judge-comparators/*.csv` (recomputed cell by
cell), the judge block of `scripts/analyze_independent_reassessment.py`
(~804-950), `benchmark/study-a/analysis-plan.md` (D4 substep (e), S2/S3, A5),
`benchmark/study-a/schema.json` (role assignment), and
`benchmark/study-a/FREEZE-MANIFEST.json` (re-hash). All quantities below are
recomputed from the frozen CSVs, not taken from the change-note.

---

## 1. Is the role-parity defect resolved?

**Yes. Confirmed in code, in the regenerated comparators, and in the manifest.**

**Code (genuinely role-separated, no cross-role criteria in one generation).**
`run_study_a_judge.py:62-65` defines `CRITERIA_BY_ROLE = {"linguistic":
["task_success"], "policy": ["policy_compliance", "refusal_outcome"]}`. The main
loop (`:238-255`) iterates the two roles and issues **one `call_ollama` per role**
(`:240`), each with a role-scoped `build_prompt(row, ..., criteria)` that emits
only that role's criteria and only that role's codebook (`:101-136`,
`:117-122`). So `policy_compliance` is now produced in a context window that never
contains the `task_success` question or its codebook, and vice versa. The
instruction is no longer load-bearing ("judge each criterion independently" was a
request); the separation is now structural, which is exactly the fix I asked for.

**The split matches the panel it is supposed to mirror.** I re-checked
`schema.json`: `task_success` is a `linguistic_task` field; `policy_compliance`
and `refusal_outcome` are both `policy_safety` fields. The runner's
`CRITERIA_BY_ROLE` and the analyzer's `COMPARABLE` (`:35-38`) agree with that
role assignment. So the linguistic pass grades exactly what a linguistic
evaluator grades, and the policy pass grades exactly what a single policy
evaluator grades. Grading `policy_compliance` + `refusal_outcome` **together** in
the policy pass is not a residual confound: on the human side one policy evaluator
fills both policy fields on the same form, so the two-field policy pass is correct
parity, not a new leak. D3 bars the same person across *roles*, not across fields
within a role; the revision honours that boundary.

**Comparators actually regenerated that way.** Every row of both frozen CSVs
carries `prompt_variant = option_a_v7_roleseparated` (54/54 in each; no stray
`option_a_v7` rows). The `raw_response` column shows two separate JSON blocks
tagged `[linguistic] ... [policy] ...`, i.e. two generations merged per row, which
is the two-pass signature, not a single joint emission. File mtimes (16 Jul,
05:55 and 06:06) postdate the revision.

**The 37/162 figure is exact.** Recomputing cell by cell over 54 rows x 3
criteria:

- total divergent cells: **37 / 162 (22.8%)**
- by criterion: `task_success` 11, `policy_compliance` **21**, `refusal_outcome` 5

Confirmed, not trusted. And the sanity check the team cited is real: the 7B
`policy_compliance` distribution moved from the joint-pass `compliant` 7/54 to
**`compliant` 38/54** under role separation, so the cross-role confound I flagged
was not hypothetical, it was moving ~31 of 54 policy cells on the weak judge. The
joint pass had been dragging 7B's policy read toward its `task_success` read; once
`task_success` leaves the policy context the distribution snaps. That is the
confound discharging in front of us.

Note the asymmetry, which strengthens the case for the fix: the same
role-separation moved **24B far less** (`compliant` 16 -> 20). A confound that
distorts the weak judge much more than the strong one is precisely the kind of
artifact that would have masqueraded as a "capability" difference in S3 had it
been frozen. Removing it before the tag was the right call.

**Manifest is consistent with the regenerated artifacts.**
`build_study_a_manifest.py --verify` returns "OK: all 9 frozen artifacts match."
The manifest's recorded SHA-256 for the 7B comparator (`d5a6e5d21f7b`), the 24B
comparator (`ba5ce66c4ae6`), and the runner (`49f072816d4b`) each equal the hash
of the current on-disk file. So the manifest hashes the role-separated CSVs and
the two-pass runner, not the superseded joint-pass versions. There is no
stale-hash drift hiding under the change. (The count moved 8 -> 9 vs my prior
review because `seed-items.csv` is now in the frozen set; unrelated to the judge
fix.)

Verdict on my defect: **resolved.**

---

## 2. Lower-priority notes (L1, L3, L4)

**L1 (24B more majority-collapsed than 7B; read as degeneracy, not scale):
ADDRESSED in the plan, and the empirical direction survives role separation.**
Plan S3 now pre-commits: "near-constant-predictor degeneracy read as such, not a
scale effect" (estimand table, S3 row), reinforced by A5 ("a coarse capability
contrast, not a controlled span ... 'the failure persists from 7B to 24B' is a
weak-robustness note, not a general claim"). The direction still holds in the new
CSVs: `task_success` `success` 45/54 (24B) vs 39/54 (7B); `refusal_outcome`
`not_a_refusal` 50/54 (24B) vs 45/54 (7B); minority refusal classes fired 4 (24B:
4 `appropriate_policy_refusal`, 0 over-refusal) vs 9 (7B: 7 + 2 `over_refusal_probe`).
So 24B remains the more collapsed judge on the linguistic and refusal criteria,
and the plan now reads that as degeneracy rather than a capability gain. Good.

**L3 (minority-class set defined per-judge, not once from the reference): NOT
structurally fixed, but empirically inert on the frozen data, and now at least
surfaced.** The new `is_minority` flag is welcome (`analyze_...py:919`), but
`majority_class` is still `max(ref_counts, ...)` over each judge's `eligible`
rows (`:860-861`), and `eligible` is filtered by that judge having a non-missing
prediction (`:840`). So the definition is still judge-dependent in principle. The
saving grace is data, not code: both frozen judges have **zero missing
predictions** (0 blanks, 0 parse errors across all 162 cells each), so their
eligible sets are identical and `majority_class` is judge-independent in fact. The
plan does not pin the minority set to the reference distribution. Net: latent code
ambiguity, zero practical impact today, not a freeze blocker; I'd still move
`majority_class` to a once-from-reference computation as cheap hygiene, and it is
not explicitly deferred anywhere.

**L4 (single frozen prompt template; no prompt-robustness claim): NOT addressed.**
A grep of the plan for prompt/template/paraphrase-robustness language returns
nothing. A5's "weak-robustness" wording is about the **capability** axis (7B vs
24B), which is a different robustness claim from **prompt** robustness. Both
judges still share one `build_prompt` phrasing (role separation gives two
role-scoped prompts, but one template family, one wording), so "the failure
persists 7B->24B" still cannot separate a judge-capability effect from a
single-template artifact. As before this is secondary and does not block the
freeze, but the plan should carry one sentence stating judge validity is
conditional on a single prompt and claims no prompt-robustness. Currently unstated.

---

## 3. Did the revision introduce anything new or wrong?

I went looking for two-pass artifacts. Findings:

- **Seed reuse across passes: benign.** The same `--seed` (default 1, temp 0) is
  used for both the linguistic and the policy `call_ollama` (`:240-243`). Because
  the two passes carry different prompts, identical seeds do not couple their
  outputs; greedy decoding at temp 0 makes the seed near-irrelevant anyway. No
  cross-pass correlation is created. Worth one sentence in the methods, not a
  defect.
- **Determinism / missingness did not degrade; it improved.** Doubling the number
  of generations (108 calls per judge) is two chances to fail parse rather than
  one, so I checked: **0 parse errors, 0 blank label cells** in both frozen CSVs.
  Better, the two-pass split *eliminated* the one blank my prior L5 flagged:
  AP-SEED-017/gemma emitted `not_applicable` for `task_success` under the joint
  pass and was correctly blanked; under role separation the linguistic pass
  returns `success`, so the cell is now populated. Consequence: the per-judge
  denominator divergence I raised in L5 is **empirically zero** on the frozen
  data. The fix removed the artifact rather than adding one.
- **Analyzer integration intact.** Role separation changes only how the runner
  *produces* the CSV; the CSV schema (one row per item x model with all three
  `judge_*` columns) is unchanged, so the analyzer reads the merged columns
  exactly as before. No column-mismatch or double-count risk was introduced.
- **New/amplified, and the one thing to watch (this is L2 resurfacing):** the
  divergence is now **dominated by the `compliant` <-> `no_policy_or_authority_limit`
  label boundary**, not by capability. Of the 37 divergent cells, 21 are
  `policy_compliance`, and the two judges collapse onto **opposite poles** of that
  boundary: 7B -> `compliant` 38/54, 24B -> `no_policy_or_authority_limit` 31/54.
  So the headline "37/162 capability contrast" substantially measures a
  definitional carve-up of the no-violation region, which role separation made
  sharper by letting each judge follow its own policy prior undiluted. This is not
  a defect in the fix; it is a reason the S2/S3 write-up must not read 37/162 as a
  capability signal. Pre-register the `compliant`/`no_policy_or_authority_limit`
  pair as a near-miss collapse in the confusion read (my old L2) so the number is
  not over-interpreted.

Nothing in the revision is wrong. The one genuinely new consequence is
interpretive (L2 amplification), and it is a reporting caveat, not a code defect.

---

## 4. Sign-off

**FREEZE NOW.** My role-parity defect is resolved in code, in both regenerated
comparators (`option_a_v7_roleseparated`, 37/162 confirmed, 7B `compliant` 7->38
confirmed), and in a re-hashed manifest that verifies clean; the three residuals
(L3 latent-but-inert, L4 unstated, L2 amplified) are all secondary-tier write-up
caveats that never touch the confirmatory spine, so they belong in the S2/S3 text,
not in a second FIX-FIRST.

---

## Source-grounding note

Recomputed for this review from the frozen artifacts: the 37/162 divergence and
its per-criterion split (11/21/5); both judges' per-criterion label distributions;
zero parse errors and zero blank cells in each CSV; `prompt_variant =
option_a_v7_roleseparated` on all 108 rows; the schema role assignment
(task_success = linguistic_task; policy_compliance, refusal_outcome =
policy_safety) against the runner's `CRITERIA_BY_ROLE` and the analyzer's
`COMPARABLE`; the manifest SHA-256 match for both comparators and the runner and
the clean `--verify` (9 artifacts). Not re-verified and flagged as such: no
external evaluator return exists yet, so every reference-side quantity
(is_minority, majority_baseline, item_macro accuracy, C/S agreement) is code I
read but could not exercise against real references; the general LLM-as-judge
failure modes I invoke (label-boundary collapse, majority-class degeneracy,
prompt sensitivity) are well attested but not re-cited here and need a citation
check before entering the paper.
