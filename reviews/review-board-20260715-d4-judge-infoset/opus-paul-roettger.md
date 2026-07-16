# D4 judge info-set review (simulated Paul Röttger)

<!-- SUMMARY: Reviewer sim of Paul Röttger on the D4 judge info-set decision (Option A realistic-deployment vs Option B metadata-assisted); verdict A for the headline, B only as a labelled ablation · status: review · updated: 2026-07-15 -->

Reviewer frame: safety-behaviour evaluation, over- and under-refusal, safe/unsafe
contrast sets, harm classification. This is a simulated persona for
stress-testing, not the real person's views. My standing bias, stated up front so
you can discount it: I care most about whether refusal and policy-compliance are
scored on their own terms, and I distrust any design that lets "refused" collapse
into "safe" or lets over-refusal and under-refusal get confused.

I am reviewing exactly one decision: what the judge sees when you test whether it
can stand in for the human reference labels.

## 1. Faithful restatement

The question sits inside the SECONDARY judge-validity outcomes (S2, S3), not the
co-primary human estimands. You have two independent Mistral judges (7B and 24B,
same family, capability isolated) re-grading the 54 outputs, and you compare each
judge's predictions against the human reference. The decision is what goes in the
judge's context.

- Option A ("realistic-deployment"): original prompt + model output + rubric,
  where rubric means the label names and the allowed options. The judge reads the
  raw exchange and applies the rubric, which is what a deployed safety grader
  does.
- Option B ("metadata-assisted"): all of A, plus the item's seven taxonomy design
  fields (phenomenon, control_dimension, context_source, source_role,
  authority_level, pragmatic_status, response_act), withholding only the
  expected_behavior answer key.

What each licenses, stated fairly. Option A licenses "the judge can or cannot
reproduce expert policy and refusal labels from the same input a deployed grader
gets." Option B licenses something narrower and genuinely different: "given a
hand-authored structural analysis of the item, can the judge apply the rubric?"
Both are real questions. Only A is a substitute-for-expert-labels test. B is a
capability decomposition: it separates "the judge can't read the pragmatic
structure off the text" from "the judge can read it but can't apply the rule."
That decomposition is worth having, and I will come back to it, because it is the
one honest use of Option B.

One thing I want to credit before criticising: the plan already caught that
expected_behavior is a leak (blocker 5, confirmed at
`run_llm_judge_validation.py:354,363`) and drops it. Good. The separation of
policy_compliance from refusal_outcome as distinct criteria is exactly right, and
rarer than it should be. The capability-span logic in D4/A5, where the robust
claim is "the minority-class miss persists from weak to strong judge," is the
right shape for a judge-validity claim. My objection is that Option B would void
that specific claim.

## 2. Effect on refusal and policy-compliance scoring specifically

This is where I push hardest, because the three fields you would add under B are
not incidental context. source_role, authority_level, and pragmatic_status are the
instruction-authority structure. In an adversarial-pragmatics taxonomy, the
correct policy/refusal label is very close to a function of exactly those fields.
If the intended behaviour for an item is (roughly) computed from who is speaking,
with what authority, in what pragmatic mode, then handing the judge those three
fields hands it the proximate causes of expected_behavior. You dropped the answer
key and kept the three inputs that generate the answer key. That is a laundered
leak. The blocker-5 fix is cosmetic if the fields that compute the label survive.

So, to your two sub-questions:

Does withholding the metadata (Option A) make refusal and policy judgments
unfairly hard? No. It makes them exactly as hard as the deployed task, and that
hardness is the finding, not a defect. Reading instruction-authority off raw text
is the thing the paper exists to say is hard. A judge that can't do it from prompt
plus output is telling you something true about deployed graders. Engineering the
difficulty away by feeding it the authority annotations launders the very
difficulty the study documents. The whole pitch, "turn messy language-mediated
judgment into reliable auditable evaluation," requires testing the judge on the
messy input.

Does providing the metadata (Option B) leak the answer for refusal-type items?
Yes, and worst precisely for refusal-type items, because refusal correctness is
often a thin function of the prompt's authority structure. Over-refusal versus
correct-refusal frequently turns on source and authority alone: same surface
request, different licit authority, opposite correct verdict. That is the classic
safe/unsafe contrast-set logic. Your minimal-pair design (9 pairs) is built to
hold surface features constant and vary the authority structure. Under Option B
you would be telling the judge which arm of the pair it is looking at. It can then
separate the pair without reading the output at all. At deployment no such label
exists, so B tests a capability the deployed judge never has, and specifically the
one that governs refusal correctness.

A sharper version for S3 (per-class recall, minority classes): if the metadata
tells the judge the design cell, the judge will "recover" minority classes because
it was told the intent, not because it can read the output. Your headline
robustness claim, that the minority-class miss persists across the capability span,
would then be an artifact. Under B you would likely see both the 7B and the 24B
"succeed," conclude the judges are fine, and report the opposite of the truth. The
capability sweep only means something under A, where a weak judge that can't parse
authority from text will miss the minority class and you can ask whether scale
closes the gap.

Two collapse risks I want named explicitly, since they are my running worry:

- Refusal is not safety. If the judge is fed authority_level/source_role, it may
  decide policy_compliance or refusal_outcome from the metadata rather than from
  what the response actually did (the response act). That routes the verdict
  around the output. You separated the criteria in the schema; don't let the
  info-set re-fuse them.
- Under- versus over-refusal. The metadata is exactly the discriminator between
  these two error types. Give it to the judge and you can no longer tell whether
  the judge distinguishes them or is reading the discriminator off the annotation.

Note on tiers, to keep the stakes honest: this decision only touches the judge
(S2/S3, secondary). The co-primary policy_compliance estimands (C2, C4) are human
quantities and are untouched. But D4 is the reason the judge is in the paper at
all, so "secondary" does not mean "safe to get wrong." Option B doesn't weaken a
secondary result; it makes the specific secondary result you are building toward
uninterpretable.

## 3. Realism versus deployed LLM-as-judge usage

Deployed safety graders (system-card auto-graders, red-team triage classifiers,
constitutional-style critics) see the prompt, the response, and a policy or
rubric. They do not receive design-time taxonomy annotations, because those exist
only in a benchmark's construction. So Option A is the ecologically valid
condition and Option B is a counterfactual judge with a partial answer key. If you
want the judge-validity claim to transfer to how these systems are actually used,
A is the only faithful test.

One realism caveat that cuts the other way, and it is actionable. "Rubric (label
names and allowed options) only" worries me. Deployed graders get the policy text,
not just a list of label names. Human evaluators here get a codebook with
criterion definitions and decision rules. If Option A gives the judge bare label
names without those definitions, you have built an under-specified judge and its
failures will partly be instruction-starvation, not authority-reading failure.
That is unfair in a way that is also unrealistic. The fairness principle is parity
of instructions, not parity of answer key: give the judge the same criterion
definitions and decision rules the human evaluators saw, minus the item-specific
answer. So Option A should read "rubric = full criterion definitions plus allowed
options, matching the evaluator codebook," and I would treat "label names only" as
a bug to fix regardless of A versus B.

## 4. Fairness and failure modes each invites

Option A failure modes:
- Instruction-starvation if the rubric is bare label names (see section 3). Fix by
  matching the evaluator codebook.
- Genuinely hard is not unfair. If A produces low judge agreement, that is a
  result about deployed graders, and the small-N discipline (cluster by pair, treat
  kappa/alpha as fragile) already governs how you state it. Don't let low numbers
  tempt a retreat to B.

Option B failure modes:
- The judge infers the label from the metadata rather than the output. This
  inflates apparent validity and specifically inflates minority-class recall, which
  is the S3 quantity you most want to be honest.
- Over-/under-refusal confusion is hidden, because the metadata is the
  discriminator.
- Not all seven fields leak equally, so lumping them is itself a mistake.
  source_role, authority_level, pragmatic_status are near-direct determinants of
  policy/refusal labels (severe leak for C2/C4/S1's construct). phenomenon and
  control_dimension are the taxonomy cell, strongly predictive. context_source is
  milder. response_act is a different and arguably worse kind of leak: it is a
  description of what the output did, so it pre-digests the very output the judge
  is supposed to read and classify. If any metadata is ever provided, it must be
  justified field by field against the specific judged criterion, not passed as a
  block.

## 5. A third option (recommended)

Run both, as a designed contrast, and make A the headline and B a labelled
diagnostic ablation. Concretely, add an info-set axis to the existing multiverse
(you already sweep capability in A5, so this is the natural second axis):

- A is the deployment-realistic, non-leaking judge-validity test. Headline for S2/S3.
- B is an upper-bound ablation that answers the mechanism question: how much of any
  judge accuracy comes from reading the prompt (A) versus from being handed the
  structure (B)? The A-to-B delta localises judge failure as "can't read authority"
  versus "can't apply rubric." That is a genuinely useful decomposition and the one
  legitimate use of B.

Guardrails on the third option:
- Pre-register B as exploratory-diagnostic, never as the substitute-for-expert-
  labels claim, to avoid choosing post hoc which condition to report (garden of
  forking paths).
- The dup-guard means one judge_labels.csv per condition, so this is 2 judges x 2
  info-sets = 4 frozen comparator files. Mechanically fine, deterministic, local,
  but it multiplies comparisons: hold the small-N discipline (cluster by pair,
  kappa fragile) and report the info-set axis in the same multiverse table, stating
  if any cell flips the qualitative conclusion.
- If you build B, build it field-by-field, not as the seven-field block, per
  section 4.

A cleaner middle info-set, if you want one condition rather than two: give the
judge whatever the deployed model actually saw at generation time (system prompt,
conversation context, any in-band authority markers in the prompt text) but never
the post-hoc taxonomy annotation. The principled line is in-band context is fair,
out-of-band design annotation is a leak. Authority present in the prompt text is
part of the reading task; authority that lives only in your codebook is the answer.

## 6. Verdict

Option A for the headline judge-validity claim, with B permitted only as a
pre-registered, field-justified, labelled ablation. Option A is the only condition
that is both deployment-faithful and non-leaking; Option B keeps source_role,
authority_level, and pragmatic_status, which jointly reconstruct the
expected_behavior you dropped, so it would inflate exactly the minority-class
recall D4 is built to measure and would silently hide over-/under-refusal
confusion. Fix the "label names only" wording so A carries the full evaluator
codebook definitions, or A becomes unfair for the wrong reason.

---

Source-grounding flags (verify before any of this enters the paper):
- My appeals to safe/unsafe contrast-set and over-refusal test-set design (the
  XSTest-style logic) are stated at the level of design principle. Any specific
  claim, number, or attribution drawn from that literature needs a checked
  citation; do not import a statistic from memory.
- The claim that expected_behavior is approximately a function of {source_role,
  authority_level, pragmatic_status} is my inference from the taxonomy's stated
  purpose, not a measured fact. It is checkable in your own data: regress or
  cross-tab expected_behavior against those three fields on the 54 rows. If they
  predict the label strongly, the leak argument is confirmed empirically and you
  should cite that number rather than my assertion. If they don't, my central
  objection weakens and B becomes more defensible, so this is worth running before
  freezing D4.
- The line references (run_llm_judge_validation.py:354,363) are taken from the plan
  as given; I did not open the script.
