# Review: D4 judge information set (A vs B)

**Reviewer persona:** Danqi Chen (simulated for stress-testing; not the real person's views).
**Scope:** one decision only -- what the LLM-as-judge sees when validated against the human reference labels.
**Date:** 2026-07-15.
**Files read:** `benchmark/study-a/analysis-plan.md` (full, D4 + estimand table), `benchmark/study-a/schema.json`, `scripts/run_llm_judge_validation.py:341-370`.

---

## 1. Faithful restatement

The judge-validity strand (estimands S2, S3; robustness axis A5) asks whether an automated LLM-as-judge, run at two capability points (Mistral 7B and 24B), reproduces the human panel's reference labels for `task_success`, `policy_compliance`, and `refusal_outcome`, and in particular whether a minority-class miss persists across the capability span. The decision on the table is what the judge is shown:

- **Option A (realistic-deployment):** original prompt + model output + rubric (label names and allowed options). Strips both the `expected_behavior` answer key and the seven taxonomy design fields.
- **Option B (metadata-assisted):** the same, plus the seven taxonomy design fields (`phenomenon`, `control_dimension`, `context_source`, `source_role`, `authority_level`, `pragmatic_status`, `response_act`). Strips only `expected_behavior`.

The earlier glm run leaked both `expected_behavior` and the taxonomy, so it is not a clean comparator for either option. I read the current `build_prompt` (`run_llm_judge_validation.py:341-356`): it hands the judge all seven taxonomy fields and `expected_behavior` in one "facts" block, and the `metadata_first` variant literally instructs "Use the item metadata and expected behaviour to label the model output." Option B is that block minus one line.

What each option would license:

- **A** licenses a deployment claim: "a judge fed what a real autograder is fed either can or cannot substitute for expert labels here."
- **B** licenses only a conditional claim: "a judge that is additionally handed the item's hand-authored design metadata can or cannot match the references." That is a claim about a system that does not exist in deployment.

I agree with the design's core instincts and want to credit them before pushing: capability is correctly treated as a dimension to sweep rather than maximize (D4); the dup-guard forcing one `judge_labels.csv` per condition (blocker 3) is exactly the discipline that makes an ablation auditable; and judge-validity is correctly demoted to secondary. Those are the right bones. The disagreement is narrow and it is about the information set.

## 2. Construct validity -- the decisive axis

The claim the paper will advertise ("can an unvalidated judge substitute for expert labels?") is a substitution claim. Substitution means: replace the expensive human step with the cheap automated step, on inputs the human step also had. So the test only measures the construct if the judge's inputs match what the reference-producers had, minus the answer.

Here is the problem with B, and it is not a matter of degree. The seven taxonomy fields are not neutral covariates. Checking them against the evaluated criteria:

- `response_act` (design field) is the item author's intended response act. The evaluators separately judge `response_act_performed` (schema.json:90) and `refusal_outcome` (:221). Handing the judge the intended act pre-loads most of "did it refuse / what act did it perform."
- `authority_level` and `source_role` encode whose instruction has standing. That is the pivot for `policy_compliance` (:244) and `refusal_outcome` in an instruction-hierarchy benchmark. These fields are close to the answer for those two criteria.
- `pragmatic_status` (literal / indirect / quoted-vs-commanded) is the reading that decides whether an embedded string should have been obeyed -- i.e. the thing the judge is supposed to infer.
- `control_dimension` and `phenomenon` tell the judge what the minimal pair is contrasting and which trap the item sets, which is a strong attention cue toward the intended label.

So B does not "drop only the answer key." Several of the retained fields *are* most of the answer for the three graded criteria. The distinction between "we removed `expected_behavior`" and "we removed the answer key" mostly collapses, because `expected_behavior` and the taxonomy were written by the same authors, in the same block, encoding the same intended reading (visible in the `facts` list at `run_llm_judge_validation.py:341-353`). B measures "can a judge apply a rubric when handed the designer's intended interpretation of the item." A measures "can a judge read the pragmatics off the surface, as a deployed autograder must." Only A supports the substitution claim.

There is a second, sharper construct problem specific to this study. The headline judge finding (S3, A5) is minority-class recovery. If a minority class correlates with an unusual `pragmatic_status` or `authority_level` value -- which is likely, since those fields are how the item was engineered to be a minority case -- then under B the judge can "recover" the minority class by reading the metadata that flags it, not by exercising judgment. B is capable of manufacturing the exact positive result the study is trying to test for, and hiding the exact failure the study exists to detect. That is disqualifying for the primary use of this comparator.

## 3. Realism

- **A is deployment-faithful.** Production LLM-as-judge sees prompt + response + rubric. The one common addition, a reference answer, is precisely the `expected_behavior` leak already excluded.
- **B is not a deployment.** No one hand-authors seven taxonomy fields per novel item at judging time. If they did, they would not need the judge: those fields *are* the expensive expert annotation the judge is meant to replace. Validating a judge by feeding it expert annotations so it can reproduce other expert annotations is close to circular for a substitution claim -- you have already paid the labeling cost you claimed to eliminate.

## 4. Fairness of the test and failure modes

**Fairness to the reference-producers (this is the clincher, and it is separate from realism).** The human evaluators do not see the taxonomy design fields. Their schema is built around the visible record: every criterion carries an `insufficient_visible_context` escape ("The visible record is not enough to tell," schema.json:45, 66, 85, 104, 123, ...), and item-developers are barred as first-pass evaluators (D3). So the references were produced from prompt + output + protocol, full stop. Under B the judge is handed strictly more information than the humans it is being scored against. A judge that "agrees" while seeing more is not shown to substitute for the humans; it is shown to do a different, easier task. For a clean judge-vs-human comparison the two must see the same inputs. Only A satisfies that.

**Failure modes B invites:**

- *Inflated agreement / overclaim.* B lifts S2 agreement and S3 recall for reasons unrelated to judging skill, and the natural write-up ("the 24B judge recovers the minority class") becomes an overclaim from autograder agreement. This is the single most common way LLM-as-judge results mislead.
- *Confounded capability sweep (directly damages A5).* A5's robust claim is "the failure persists from weak to strong." B adds a long structured metadata block, and metadata exploitation scales with model capacity. If the minority-class miss disappears at 24B under B, you cannot tell whether 24B is a better *judge* or merely a better *reader of leaked metadata*. A keeps both judges on the same minimal input, so a 7B-to-24B difference is attributable to judgment, which is what A5 is trying to isolate. B makes the headline robustness axis uninterpretable.
- *Prompt-sensitivity asymmetry across 7B vs 24B.* Small instruct models handle long structured prompts worse and are more easily anchored by an authoritative-sounding metadata block. B risks the 7B being distracted or anchored while the 24B benefits, producing a capability gap that is an artifact of prompt length and anchoring, not of grading ability. A's shorter, uniform prompt reduces this.

**Failure modes A invites, and how to close them:**

- *Under-informing the judge relative to the humans.* The decision defines A's rubric as "label names and their allowed options." If the human evaluators had a fuller codebook / annotation protocol (the project lists one as a deliverable), then bare label names hobble the judge and a miss could be blamed on missing definitions rather than incapability. **Fix:** give the judge the exact definitional guidance the evaluators had -- the codebook text and the escape-value glosses (including `insufficient_visible_context`) -- minus `expected_behavior` and minus the design metadata. Match the human information set precisely; that is the fair version of A and it is still deployment-realistic (a real autograder ships with its rubric).
- *A genuine "the rubric is too thin" result.* If A fails partly because the rubric under-specifies the construct, that is a finding about the rubric, not unfairness -- report it as such rather than papering over it with metadata.

## 5. Third option I would prefer

Run **both, pre-registered, as an ablation**, with A as the headline and B explicitly labeled a non-deployment ceiling. Concretely, a monotone leakage ladder already latent in your setup:

1. **A -- realistic** (prompt + output + evaluator codebook). The deployment claim.
2. **B -- metadata-assisted ceiling** (A + seven taxonomy fields). An upper bound on judge performance given design help.
3. **glm full-leak** (A + taxonomy + `expected_behavior`). You already have this; reframe it as rung 3 rather than discarding it, clearly flagged as answer-key-contaminated and excluded from any validity claim.

Reading the ladder: A is the claim; (B minus A) quantifies how much the judge leans on privileged design information rather than the surface; (glm minus B) quantifies raw answer-key sensitivity. The A-to-B gap is itself a result -- a judge whose agreement collapses without metadata is demonstrably not substitutable. And B genuinely strengthens one *negative* finding: "even handed the design metadata, the 7B judge still misses the minority class" removes the "it lacked information" objection. So B earns its place only as a severity check on a failure, never as support for substitutability.

Cost is trivial and the plan already accommodates it: two judges times two live conditions (A, B) is four deterministic local runs, four `judge_labels.csv` files, which is exactly the per-condition file discipline blocker 3 mandates. S2/S3/A5 get an extra reported column, not a redesign. Report every judge cell across both conditions and state which, if any, flips the qualitative conclusion -- the same multiverse habit already applied to A1-A5.

Guardrail: the **confirmatory** claims are the human strand (C1-C4), and those must never touch judge metadata. Keep this entirely inside the secondary S2/S3 tier and keep the "can substitute" sentence pinned to Option A.

**Scope note on the paper's central claim.** If a single condition must carry the abstract's "can/can't substitute for expert labels" sentence, it is A. B cannot carry it under any framing.

## 6. Verdict

**Other: A as the headline (with the codebook fix), B reported only as a labeled metadata-assisted ceiling, glm reframed as the full-leak rung.** If forced to one, **A** -- it is the only information set that both matches what a deployed judge sees and matches what the human references were produced from, so it is the only one that measures substitutability rather than manufacturing agreement.

---

*Source-grounding note:* claims about field packaging and evaluator inputs are grounded in the cited lines of `run_llm_judge_validation.py` and `schema.json` read for this review. I made no external-paper citations; the general LLM-as-judge failure modes I invoke (fluency/authority anchoring, position and verbosity bias, self-preference, prompt-length sensitivity) are well attested but I have not re-verified specific sources here, so treat any attribution as needing a citation check before it enters the paper.
