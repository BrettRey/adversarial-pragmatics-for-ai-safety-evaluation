# D4 judge information-set review (simulated Percy Liang)

<!-- SUMMARY: Simulated-Percy-Liang review of the D4 judge-visibility decision (Option A realistic-deployment vs Option B metadata-assisted); verdict A, with B allowed only as a clearly-labeled oracle ceiling · status: open · updated: 2026-07-15 -->

Reviewer persona: simulated Percy Liang (LM evaluation, benchmark architecture,
transparency, multi-metric evaluation). Stress-test only, not the real person's
views. Scope: one methodological decision (D4, what the LLM judge sees), not the
whole plan.

Files read: `benchmark/study-a/analysis-plan.md` (D4 + estimand table),
`benchmark/study-a/schema.json` (the seven taxonomy fields and both role
intros), `reviews/study-a-plan-prefreeze-review-2026-07-15.md` (blocker
context), `scripts/run_llm_judge_validation.py:332-383` (the current judge
prompt builder). Where I cite a number I did not compute, I flag it.

---

## 1. Faithful restatement

The question is narrow: when you validate whether an automated LLM-as-judge can
stand in for the independent human panel on these 54 rows, what goes into the
judge's context window?

- **Option A ("realistic-deployment"):** original prompt + model output +
  rubric (the label names and allowed options). Nothing about how the item was
  designed.
- **Option B ("metadata-assisted"):** all of A, plus the item's seven taxonomy
  design fields (`phenomenon`, `control_dimension`, `context_source`,
  `source_role`, `authority_level`, `pragmatic_status`, `response_act`). Only
  the `expected_behavior` answer key is withheld.

What each licenses:

- **A** licenses a deployment claim: "given the same visible record a shipped
  judge would see, and the same information the human panel had, the judge does
  or does not reproduce the expert reference labels, and the minority-class miss
  does or does not persist across the weak→strong Mistral span." That is exactly
  the S2/S3/A5 claim the plan advertises, and it is the claim a hiring-legible
  eval artifact needs.
- **B** licenses only a ceiling claim: "when additionally told the design
  category of the item, the judge does or does not reproduce the labels." It
  bounds how much of any judge failure is failure-to-identify-the-phenomenon
  versus failure-to-apply-the-rubric-once-told. That is a real and useful
  quantity, but it is not a deployment claim and must never be reported as
  "judge validity" unqualified.

I want to be fair to B before I criticize it. The instinct behind B is sound:
you do not want to hand the judge the answer key (`expected_behavior`), and the
taxonomy fields are not literally the answer, so dropping only the answer key
feels like a principled middle. The decomposition B enables (identification vs
application) is genuinely informative and I would want it reported. My
disagreement is about which condition is the headline, not about whether B has
any value.

One more thing the plan gets right and I will not relitigate: rejecting a
frontier API model as the frozen comparator (non-deterministic, paid, stale) and
treating capability as an axis to sweep rather than maximize. Both are correct
calls and both help reproducibility.

## 2. Metric / construct validity

This is where the decision is actually made, and it is not close.

**The reference labels are produced taxonomy-blind.** Both role intros in
`schema.json` instruct the human evaluators to "judge only from the visible
record (the prompt and response as shown); do not infer a hidden policy or
intended answer." The panel never sees `pragmatic_status`, `source_role`,
`authority_level`, or the rest. So the reference standard that S2/S3 score the
judge against was generated under visible-record-only. If the judge gets the
taxonomy (Option B), the judge is in a strictly richer information state than
the humans whose labels define ground truth. You are then no longer measuring
"can the judge reproduce the human reference under the human's conditions." You
are measuring "can a taxonomy-advantaged judge match taxonomy-blind humans,"
which is a different and less interpretable quantity. Information-state parity
with the reference is the whole ballgame for a substitutability claim, and only
A has it.

**The taxonomy is not neutral metadata; it is the answer to the hard part of
the task.** The construct this benchmark probes is language-mediated control:
whose instruction has authority, whether a directive is quoted or commanded,
whether a request is literal or indirect. Those are precisely
`source_role`, `authority_level`, `pragmatic_status`, and `response_act`.
Handing the judge those fields pre-resolves the exact ambiguities the item was
built to pose. B does not merely flatter the judge; it dissolves the construct.
It is a softer sibling of the `expected_behavior` leak, not a clean condition.

**B inflates the metric in the direction that hides the finding the study
exists to surface.** S3 asks whether the judge misses the minority class
(the rare noncompliant / failure / probe cases) and whether that miss persists
from the 7B to the 24B judge (A5). The taxonomy flags which items are the
adversarial ones. Feeding it lets even the weak judge locate the minority class
by reading the label rather than by doing the pragmatic work, which raises
minority-class recall and collapses the capability contrast. So the one number
the plan most wants (does the failure persist across the span?) is the number B
is most likely to erase. Aggregate accuracy would look better while concealing
the deployment-relevant trade-off. That is the exact pathology to guard against.

**Reproducibility.** Both options run locally at temp 0, seed 1, so both yield
deterministic numbers. But a reproducible number is not a valid one: B
reproducibly answers a question no reader asked. A also has a hygiene edge. Its
input surface is smaller (prompt + output + rubric), so the freeze manifest has
fewer per-item strings to hash and fewer opportunities for drift than B, which
must freeze the taxonomy text for all 18 items as judge input.

**Code-grounded caveat, verified directly.** Neither option is implemented yet.
In `run_llm_judge_validation.py`, the shared `facts` list (lines 343-357)
carries `expected_behavior` and all seven taxonomy fields, and *both* prompt
variants emit the full list (the `metadata_first` branch at line 360 and the
`else` branch at line 373 build `ordering` from the same `facts`). The only
difference between the two current variants is the instruction sentence. So the
existing "realistic" variant is not realistic; it leaks the answer key
identically. D4 sub-step (b) as written ("drop the `expected_behavior` field")
implements **Option B**, not A. To get A you must also strip the seven taxonomy
fields *and* the bare identifiers `item_id` / `variant` / `model_under_test`
from the prompt text, because `item_id` + `variant` reveal minimal-pair
membership and let the judge infer the contrast structure. Flag this explicitly
in the sub-step or you will silently ship B while believing you chose A.

## 3. Realism vs actual LLM-as-judge deployment

Real judge deployments (eval harnesses, reward/critique models, system-card
grading, autoraters) get a prompt or transcript, the model's response, and a
rubric or principle. They do not get a hand-authored per-item design taxonomy,
because that taxonomy is the human labor the automated judge is meant to
replace. B describes a world where a human has already annotated
`pragmatic_status`, `source_role`, and `authority_level` for every item, at
which point the judge is being asked to do the easy residual and the expensive
part has already been paid by hand. That inverts the value proposition. A is the
condition that maps to a deployment anyone would actually run.

One realism refinement that strengthens A rather than B: the human panel gets
rich per-field rubric guidance (the schema `help` text and the task-giver
convention), while A as literally worded gives the judge only "label names and
allowed options." That asymmetry is on the *rubric* dimension, not the item
dimension, and it is legitimate to close. Give the judge the same field-level
rubric help the humans get. That matches the human information state on the
rubric while keeping the judge taxonomy-blind on the item. It is the cleanest
parity: same rubric guidance, same visible-record-only, no design leakage. Do
not confuse this with B; rubric help is the label space, the taxonomy is
per-item design intent.

## 4. Fairness and hidden trade-offs at N = 54

The plan is admirably disciplined about small N (blocker 6, the inference
section): fixed-set counts and fractions, cluster by item or pair, 18 items and
9 pairs, non-independent rows. That discipline makes the information-set choice
*more* consequential, not less.

- **B, upward bias where it hurts.** The taxonomy fields correlate with the
  correct labels by construction. At N = 54 with skewed classes, a handful of
  items flipping moves the headline; leakage that helps most on the hard and
  minority items is leakage concentrated exactly where the study's claim lives.
  B's inflation is not uniform noise, it is targeted at the finding.
- **A, a real downward-bias risk to name honestly.** If some item genuinely
  requires context that lives only in the taxonomy and is truly absent from the
  visible prompt, A will make the judge look bad for a reason a fair judge
  should not be penalized for. But the same missing context would have defeated
  the human panel too (they were visible-record-only), so such an item should
  surface as a human `insufficient_visible_context` / `item_problem` escape and
  drop out of the comparator denominator under A4 before it can bias the judge
  score. The escape machinery is the correct fix, not feeding the judge the
  taxonomy. If an item only becomes answerable once you inject the taxonomy, that
  is a defective item, not a judge that needs help.
- **The leaked glm run is neither A nor B and must be quarantined.** The setup
  note says the earlier glm run leaked `expected_behavior` *and* all seven
  fields, so it is an answer-key-assisted "B-plus" condition. It cannot be
  pooled with the fresh Mistral runs or reported as judge validity. Any accuracy
  figure inherited from it is an oracle upper bound, full stop. Source-grounding
  flag: I did not see a real glm judge-validity table; the numbers that appear
  in the pre-freeze review (task 0.961, policy 0.824, refusal 1.000) are
  described there as **synthetic-fixture** output from the `simulate_*` path, not
  real judge performance. Do not cite any of these as judge results. Recompute on
  the fresh non-leaking Mistral runs and cite only those.
- **Two same-family Mistral judges is a good capability isolation** (family held
  constant, size varied), but note it buys robustness across capability, not
  across model family. State the judge-validity conclusion as span-specific to
  the Mistral family. That is a limitation of D4 generally, not of A versus B,
  but it interacts: under B the span contrast is likely to vanish for the wrong
  reason (leakage), so the family caveat and the info-set choice compound.

## 5. A third option

Yes, and it plugs straight into the multiverse the plan already commits to
(Steegen, Tuerlinckx, Gelman & Vanpaemel 2016), so it costs you little
architecturally.

Add an **information-set axis** to the grid alongside the existing capability
axis (A5):

1. **A (rubric-only, visible record).** Headline judge-validity condition.
2. **B (rubric + taxonomy).** Reported as a clearly-labeled *oracle-assisted
   ceiling*, never as "judge validity." Its job is the identification-versus-
   application decomposition: the A→B gap estimates how much of the judge's miss
   is failure to recognize the phenomenon.
3. **glm answer-key condition.** Not run fresh, not comparable, shown only as a
   historical upper bound if shown at all, and labeled as leaked.

Report A as primary; report the A→B delta as the ablation; keep every cell
descriptive-only per the plan's own small-N rule. Discipline caveat, in my own
voice: an information-set axis (3 levels) crossed with capability (2 judges)
crossed with two criteria is already a lot of researcher degrees of freedom on
54 non-independent rows. Pre-commit the grid in the freeze manifest, label every
cell descriptive, and do not let the specification curve become a garden of
forking paths where the flattering cell gets promoted to the abstract. A
specification curve here is a transparency device, not a license to fish.

If you only have appetite for one run: run A. The ablation is a nice-to-have;
the deployment condition is the requirement.

## 6. Verdict

**Option A**, with B permitted only as an explicitly labeled oracle ceiling in a
pre-committed information-set ablation. A is the sole condition that holds the
judge to the same visible-record-only information state as the reference-setting
human panel, corresponds to a real judge deployment, and preserves the pragmatic
ambiguities that are the construct; B inflates a secondary metric in exactly the
direction that would hide the minority-class failure the study exists to detect.
Fix D4 sub-step (b) so it strips the seven taxonomy fields and the identifiers,
not just `expected_behavior`, or you will implement B while thinking you chose A.
