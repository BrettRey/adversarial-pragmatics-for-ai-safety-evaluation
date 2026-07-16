# Study A freeze-readiness review (judge tier): Danqi Chen (simulated)

<!-- SUMMARY: Freeze-readiness review of the Study A pre-registration, judge tier; verdict FIX-FIRST; the frozen judge grades all three criteria in one joint pass while the reference panel is role-separated and person-disjoint across roles, so the plan's information-state-parity claim is false on the role axis and the two frozen comparators embed a role-collapse confound · status: open · updated: 2026-07-15 -->

Reviewer: simulated Danqi Chen persona (instruction-following eval, LLM-as-judge
meta-evaluation, adversarial evaluation of evaluators). Scope: freeze-readiness of
the Study A analysis path as a pre-registration, with the judge tier as the focus.
Read for this review: `benchmark/study-a/analysis-plan.md` (full),
`scripts/run_study_a_judge.py`, both `benchmark/study-a/judge-comparators/*.csv`,
the judge-validity block of `scripts/analyze_independent_reassessment.py`,
`benchmark/study-a/schema.json`, `benchmark/study-a/FREEZE-MANIFEST.json`,
`scripts/build_study_a_manifest.py`, the pre-freeze review
(`reviews/study-a-plan-prefreeze-review-2026-07-15.md`), and the four D4 info-set
board reviews. I did not open any external evaluator return (none exists yet).

---

## 1. Faithful restatement of what is being frozen (Rapoport's Rules)

Study A re-adjudicates 54 existing outputs (18 benign seed prompts times three
local models: `qwen3:8b`, `gemma3:12b`, `glm-4.7-flash:q4_K_M`) under schema v7.
A blind, role-separated human panel produces criterion-specific reference labels:
`linguistic_task` evaluators judge `task_success` (and other linguistic fields);
`policy_safety` evaluators judge `policy_compliance` and `refusal_outcome` (and
other policy fields). A stable reference needs a 2-of-3 majority, falling back to
unanimity at N=2 (D1). The confirmatory co-primary outcomes are reference *yield*
and independent-vs-author agreement for `task_success` and `policy_compliance`
(C1 to C4). The judge tier is explicitly secondary (S2, S3): two same-family
Mistral judges (`mistral:7b`, `mistral-small:24b`), run locally, deterministic
(temp 0, seed 1), pinned by digest, under an Option-A information set (prompt +
response + full v7 codebook, no taxonomy fields, no `expected_behavior`, no
identifiers). Each judge is a separate frozen `judge_labels.csv`; the analyzer
reads them side by side, reports per-judge availability, majority baseline,
item-macro accuracy, effective cluster counts, and per-class recall with an
`is_minority` flag. Freezing means tagging a hashed manifest (stamp 1) over the
plan, schema, both comparators, and the four analysis scripts.

What the team gets right, and I want this on the record before I attack:

- The eight prior blockers are genuinely discharged in code, not just in prose. I
  re-verified the manifest (`build_study_a_manifest.py --verify` returns "OK: all
  8 frozen artifacts match"), and the drift detector works. This is real
  reproducibility hygiene, not a git tag pretending to be a pre-registration.
- The plan's quantitative self-description is honest. It claims the two judges
  "differ on 26/162 label cells (~16%)"; I recomputed from the frozen CSVs and got
  exactly 26/162 (task_success 12, policy_compliance 9, refusal_outcome 5). Numbers
  in a pre-registration that match the artifacts are rarer than they should be.
- Separating reference *yield* from reference *agreement* before scoring any judge
  is the right spine, and the escape-value handling (`item_problem`,
  `insufficient_visible_context` excluded from comparator accuracy) closes the
  usual "the judge matched an escape" leak.
- The judge is already demoted to a caveated secondary finding with a mandatory
  small-N reporting caveat, and Option B was correctly rejected as a laundered
  answer key. The D4 board's central instinct (parity with the reference is the
  whole ballgame for a substitutability claim) is exactly the right frame. My
  attack is that the board applied that frame to only one of the two axes on which
  parity can break, and froze the design before checking the other.

The removal of the old self-judging confound is also real and I confirmed it. The
"18 self-judged rows" (blocker 5) came from an earlier design in which the judge
was one of the three evaluated models, so 18/54 rows had a model grading its own
output. The frozen comparators use Mistral judges that are disjoint from all three
generators (I checked the model column in both CSVs and in the pilot `outputs.csv`:
generators are exactly qwen/gemma/glm, 18 each; judges are Mistral). Zero
self-judged rows remain. That sub-check passes.

---

## 2. Sign-off verdict

**FIX-FIRST.** The confirmatory spine (C1 to C4, human yield and author agreement)
is freeze-ready and I would tag it today. The judge tier is not. The two frozen
judge comparators embed a design confound that the freeze would enshrine, and it
directly contradicts the plan's own stated justification for the Option-A
comparator. The fix is cheap and belongs before the tag, not in the revision
ledger after it.

---

## 3. Single most important remaining defect

**The frozen judge grades all three criteria in one joint pass, while the
reference panel is role-separated and person-disjoint across roles. The plan's
"information-state parity with the panel" claim is therefore false on the
role-separation axis, and the two frozen comparators measure a confounded
quantity.**

Where it lives:
- `scripts/run_study_a_judge.py:56`, `:102`, `:225`: `CRITERIA = ["task_success",
  "policy_compliance", "refusal_outcome"]`, and `build_prompt` emits all three
  criteria and all three codebook entries into a single prompt, scored in a single
  generation. The instruction "Judge each criterion independently" (`:97`) is a
  request, not a structural guarantee; the judge's `policy_compliance` label is
  produced in a context window that also contains the `task_success` question and
  its codebook, and vice versa.
- `benchmark/study-a/schema.json`: `task_success` is a `linguistic_task` field;
  `policy_compliance` and `refusal_outcome` are `policy_safety` fields. The two
  roles are separate forms.
- `benchmark/study-a/analysis-plan.md:24-25` (D3): "the same person must not rate
  the same row under both roles (avoids within-person priming of the policy read
  by the linguistic read)." The human design spends its independence machinery
  precisely to prevent cross-role priming.
- `benchmark/study-a/analysis-plan.md:61-63`: Option A "matches what the human
  evaluators see ... preserving information-state parity with the panel that
  defines the reference."

The contradiction is direct. The reference `policy_compliance` label is produced
by an evaluator who never saw `task_success` as a question; the judge's
`policy_compliance` label is produced with `task_success` and its codebook in the
same context. So the judge sits in a strictly richer information state than any
single human evaluator, exactly the failure that Percy Liang's D4 review named as
disqualifying, only on a different axis than the one he checked. Liang killed
Option B because a taxonomy-advantaged judge scored against taxonomy-blind humans
measures "a different and less interpretable quantity." A role-collapsed judge
scored against role-separated humans has the same defect: when the judge disagrees
with the reference, you cannot tell whether it is judge incapability or the
joint-vs-separated grading structure. By the board's own principle ("parity is the
whole ballgame"), Option A as implemented does not have parity.

Why this must be fixed before the freeze rather than logged after it:
- A pre-registration exists to lock a *clean* comparator. If you report a
  judge-vs-reference number at all, even a caveated secondary one, it has to
  measure judge-vs-reference, not judge-under-joint-grading vs
  reference-under-separated-grading. Freezing a knowingly confounded comparator and
  then reporting it invites the precise critique this paper is built to defeat:
  your autograder validation is itself unvalidated.
- The plan currently presents the asymmetry as a virtue. Lines 61-63 advertise
  parity as the reason Option A beats Option B, and the D4 board endorsed that
  4/4. Tagging the manifest pre-registers an inaccurate justification, not just a
  suboptimal one.
- The fix is an afternoon. Run the judge in two role-separated passes: a
  linguistic-only prompt that emits `task_success`, and a policy-only prompt that
  emits `policy_compliance` + `refusal_outcome`, each carrying only its own role's
  codebook, mirroring the two human forms. Regenerate the two comparators,
  re-hash, then tag. After the tag this becomes a logged deviation requiring a
  re-freeze, which is strictly worse.

If Brett decides to keep single-pass grading (for instance, to model a deployment
autograder that sees everything at once), that is defensible, but then two things
are mandatory before the tag, not optional: (a) strike the "information-state
parity" language at lines 61-63 and downgrade it to "instruction parity, minus
the answer key, single joint pass," and (b) pre-register the joint-grading
structure as a named confound in A5 and in the S2/S3 caveat, so the secondary
number is read as "joint-pass judge vs separated-panel reference," never as a
substitutability estimate. My recommendation is (regenerate role-separated); it
removes the confound instead of documenting it.

Note this does not touch the confirmatory tier. C1 to C4 are human-only; the
defect is confined to S2/S3 and to the Option-A justification text. A clean
alternative to a full FIX-FIRST is to freeze stamp 1 without the two judge
comparators, and add them to the manifest once regenerated role-separated. Either
route keeps the judge artifacts out of a tag until they measure the right thing.

---

## 4. Lower-priority notes (all judge tier, all source-grounded against the frozen CSVs)

**L1. The capability span is not just coarse, it is partly inverted on the
safety-relevant criterion.** From the frozen comparators: the "strong" 24B judge
is *more* collapsed onto the majority class than the 7B for `task_success`
(`success` 48/54 vs 40/54) and `refusal_outcome` (`not_a_refusal` 49/54 vs 44/54),
and it fires fewer minority refusal classes (24B: 5 `appropriate_policy_refusal`,
0 over/under-refusal probes; 7B: 7 appropriate + 1 under + 2 over = 10). So S3's
pre-registered question "does the minority-class failure persist from weaker to
stronger?" is nearly guaranteed to answer "yes, and it worsens with scale," but
that is an artifact of both judges being near-constant, not a capability finding.
A5 concedes "coarse"; it does not concede *directionally inverted for refusal*.
Before freezing, S3's write-up should pre-commit to reading "worse recall at 24B"
as degeneracy of a near-constant predictor, not as a scale effect.

**L2. A systematic label-boundary split between the two judges will masquerade as
accuracy.** `policy_compliance`: 7B assigns `no_policy_or_authority_limit` 42/54
and `compliant` only 7/54; 24B assigns `no_policy_or_authority_limit` 33/54 and
`compliant` 16/54. The judges carve the "no violation" region differently between
"no limit stated" and "compliant." Whichever the human reference picks, one judge
is systematically penalized on a distinction that is definitional, not capability.
Pre-register the `no_policy_or_authority_limit` <-> `compliant` pair as a
near-miss collapse in the confusion read so S2 accuracy is not misread.

**L3. The minority-class set is defined per-judge, not once from the reference.**
In `analyze_independent_reassessment.py` (~731-733, ~781), `majority_class` is
`max(ref_counts, ...)` over each judge's *eligible* rows, and eligibility requires
a non-missing prediction for that judge. With differential missingness the
"minority" set can differ across judges, so "persists across the span" would
compare recall over non-identical class definitions. Freeze the minority-class set
once from the reference distribution (judge-independent). Practical impact is small
today (see L5), but a pre-registration should not carry the ambiguity.

**L4. Judge validity rests on a single frozen prompt template with no paraphrase
robustness.** Both judges use the identical `build_prompt` output. "The failure
persists 7B to 24B" cannot separate a judge-capability effect from a
single-template artifact. Given secondary status this need not block the freeze,
but the plan should state that judge validity is conditional on one prompt and
claims no prompt-robustness. This is the standard prompt-sensitivity caveat for
any LLM-as-judge claim and it is currently unstated.

**L5. Missing-prediction handling is correct but creates a per-judge denominator
divergence worth one sentence.** AP-SEED-017/gemma (7B) emitted `not_applicable`
for `task_success` (a real intuition: task success is moot for a refusal); the
runner correctly blanks it to a missing prediction rather than a silent wrong
label (`run_study_a_judge.py:227-234`). Good. Consequence: that row drops from the
7B `task_success` denominator but not the 24B one, so the two judges are scored on
slightly different eligible sets (1 cell here). The analyzer reports availability
per judge, which is the right instinct; just make the denominator divergence
explicit in the S2 write-up so the two judges' accuracies are not read as computed
over identical rows.

---

## Source-grounding note

Verified against artifacts for this review: the 26/162 (16.0%) judge-difference
count, the per-criterion label distributions in L1/L2, the generator/judge model
disjointness (zero self-judged rows), the single-prompt joint-criterion structure,
the manifest integrity (`--verify` clean), and that no D4 board review raised the
role-separation axis (they debated only taxonomy-blindness parity). Not verified
and flagged as such: the general LLM-as-judge failure modes I invoke (joint-grading
halo effects, prompt-sensitivity, majority-class collapse) are well attested in the
autograder literature but I did not re-verify specific sources here; treat any
attribution as needing a citation check before it enters the paper. No external
evaluator return was opened; all reference-side quantities remain hypothetical.
