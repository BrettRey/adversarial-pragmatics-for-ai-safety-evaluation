# Review-board synthesis: D4 judge information-set decision (2026-07-15)

<!-- SUMMARY: 4-reviewer Opus board on Study A D4 (what the LLM judge sees); unanimous Option A; two reviewer claims verified against code+data; open split on keep-vs-demote the judge sub-study · status: decided (A) · updated: 2026-07-15 -->

Board: four independent Opus reviewers (simulated personas Danqi Chen, Percy
Liang, Paul Röttger, + a hostile measurement methodologist), each blind to the
others, each given `benchmark/study-a/analysis-plan.md` and the A-vs-B framing.
Individual reviews in this directory.

**Decision: Option A (realistic-deployment) — the judge sees the prompt + the
model output + the full evaluator codebook, nothing else.** Unanimous (4/4),
and, unusually, backed by facts I verified against the code and data rather than
by reviewer taste alone.

## The decision
- **Option A** — judge sees: original prompt, model output, rubric.
- **Option B** — same, plus the seven item taxonomy fields, dropping only the
  `expected_behavior` answer key.

## Consensus (all four)
- **Option A for the headline "can an LLM judge substitute for expert labels?"
  claim.** Option B is not a "metadata-assisted" condition; it is a **laundered
  answer key**.
- **Option B only as a pre-registered, explicitly labelled ceiling / ablation**,
  never as the substitutability comparator.
- **Upgrade Option A's rubric to the full evaluator codebook definitions**, not
  just label names. Parity of *instructions* with the humans, not parity of
  *answers*. (Fixes a real ambiguity in my original wording.)

## Verified against source (not taken on the reviewers' word)
1. **Parity — humans are taxonomy-blind (Liang).** Protocol
   (`study-protocol-draft.md:30`): evaluators see "only opaque row IDs, the
   prompt, the response, and a role-specific rubric"; the package "hides ... item
   and phenomenon identifiers, expected behaviour, author labels ...". So the
   humans who define the reference never see the taxonomy. Option B would put the
   judge in a **richer** information state than the reference-setters, making the
   S2/S3 comparison uninterpretable. **Confirmed.**
2. **The leak is real and large (Röttger, Chen, hostile).** Across the 18 items,
   `(source_role, authority_level, pragmatic_status, response_act)` forms 14
   distinct tuples; only 2 collide. So those four design fields nearly
   **determine** `expected_behavior` — ~16/18 items uniquely. Option B hands the
   judge the answer for ~89% of items. **Confirmed empirically.**
3. **My plan's D4 sub-step (b) was wrong (Liang).** Both judge prompt variants
   join the identical full `facts` list (`run_llm_judge_validation.py:343-373`),
   so "drop `expected_behavior`" leaves **Option B**. True Option A must also
   strip the seven taxonomy fields **and** the `item_id`/`variant`/
   `model_under_test` identifiers (`variant` reveals minimal-pair membership).
   **Confirmed.**
4. **Judge label space is pre-v7 (hostile) — a separate, blocking bug.** The
   judge emits a label space that cannot match the v7 reference: it can never
   produce `insufficient_visible_context` or `item_problem` (task + policy) or
   `no_policy_or_authority_limit` (policy), and it says `not_applicable` where
   v7 says `not_a_refusal`. So judge-vs-reference disagreement is partly a schema
   mismatch **no information set can fix**. **Confirmed.** Must migrate the judge
   label space to v7 (+ the `not_applicable`→`not_a_refusal` crosswalk) before
   any comparison.

## The real disagreement (preserved, not smoothed)
- **Keep-with-ablation** (Chen, Liang, Röttger): run the judge tier, headline on
  A, add B as a labelled ceiling. Chen wants a full **leakage ladder** (A
  realistic / B metadata-ceiling / old glm full-leak) as a severity check on a
  negative finding.
- **Demote / restructure** (hostile): at ~9 effective pair-clusters the
  secondary judge estimate is unresolvable, so the A-vs-B choice can't move it;
  gate the judge tier on **reference yield first** (if too few rows get a stable
  human reference, there is nothing to validate the judge against), and **drop
  the "capability span" framing** — two same-family q4 models is a convenience
  pair, not a real capability axis.

This split is the decision left for Brett: **A is settled; whether the judge
tier is a reported secondary result or a demoted/gated appendix is not.**

## Board self-check
4/4 convergence on A is suspiciously clean, and a synthetic panel can smooth
toward a centroid. Here the convergence is warranted rather than smoothed: it
rests on two verified structural facts (parity + the measured leak), not on
shared reviewer taste. The genuine heterogeneity — keep vs demote the sub-study,
and how seriously to take the capability-span claim — is preserved above and not
resolved by vote.

## Actions
1. **D4 info set = Option A**, corrected: strip `expected_behavior`, the seven
   taxonomy fields, and `item_id`/`variant`/`model_under_test`; upgrade the
   rubric to full codebook definitions. (Fix analysis-plan sub-step (b).)
2. **Migrate the judge label space to v7** (+ crosswalk) before any judge run —
   blocking, independent of A/B.
3. **Soften the "capability span" claim** to "two same-family q4 judges (7B, 24B)
   as a coarse capability contrast, not a controlled span."
4. **Gate the judge tier on reference yield**; if yield is low, the judge tier is
   an appendix, not a secondary result. (Brett's call.)
5. Optional (Chen): pre-register the A / B-ceiling / glm-full-leak leakage ladder.
