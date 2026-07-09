# Review Triage: Three-Paper Set
## Decision
Keep the three-paper project for now, but stop letting papers 2 and 3 do the same work.

The adversarial-pragmatics paper remains the empirical anchor. The delegation-assurance paper should become the AI-security paper about status / priority / licensing and accountability asymmetry. The evidentiary-assurance paper should become the law/governance paper about burden allocation, validity of delegation, evidentiary sufficiency, and defeaters.

Do not merge papers 2 and 3 yet. A merge may be right later, but the next best move is cheaper: make the split real and test whether each paper has an independent job.
## Immediate Fixes
1. Adversarial pragmatics:

  - Surface the judge-validation result more strongly: under favourable conditions, the judge misses the safety-relevant minority classes.

  - Add the row-016 tension as a main-paper point: mention/use can be safe pragmatically while still violating an information-flow boundary.

  - Clarify the denominator switch for capability-failure recovery.

  - Qualify kappa reporting at small cell counts and note row non-independence.

  - Add gold-label and single-adjudicator limitations more explicitly.

  - Add validator checks for pair integrity, especially P008.

2. Delegation assurance:

  - Move accountability asymmetry closer to the abstract/introduction.

  - Make status / priority / licensing the central contribution.

  - Add one sentence distinguishing system-behaviour claims from evidentiary claims in assurance cases.

  - Cut the SOX passage or leave only a cross-reference to paper 3.

  - Treat Opus 4.8 as an example of a current-generation frontier system card, not a fixed named anchor.

3. Evidentiary assurance:

  - Add a validity row: whether the principal could validly confer the authority.

  - State the Robodebt lesson precisely: better records would not have made the scheme lawful; they would have made the unlawfulness reconstructable earlier.

  - Develop the burden-shifting account from the Canada Evidence Act analogy.

  - Align the abstract and evidence-primitives table.

  - Fix the source-family count in section 3.

  - Keep SOX here, not in delegation assurance.

## Defer
1. Do not merge papers 2 and 3 in this pass.

2. Do not remove Klee, Coase, Hayek, Mises, Klein, Jensen, or Miller globally yet; first cut them where they are only ornamental.

3. Do not claim the development-pass result before running it.

4. Do not rewrite the supplement until the main-paper fixes settle. Then add the judge prompt, row-level adjudications, repository URL, commit hash, licence, and validator checks.

## Proposed First Patch
Make the low-risk correctness and positioning fixes:

1. Paper 3: validity row, burden-shifting paragraph, Robodebt precision, abstract/table alignment, source-family wording.

2. Paper 2: cut SOX from the audit paragraph and replace with a cross-reference to paper 3; strengthen status / priority / licensing in the intro.

3. Paper 1: add the row-016 information-flow tension, kappa caution, denominator clarification, and stronger judge-result language.


This patch should not merge papers or alter dataset labels. It should make the present drafts less vulnerable while preserving the current project structure.
## Second Review Triage
The second external review confirms the three-paper structure, but asks for sharper division of labour and a few concrete artifacts.
### Keep the Stack
The three papers should remain separate for now:

1. **Adversarial Pragmatics**: measurement of language-mediated control.

2. **Delegation Assurance**: security/assurance standard for authorized action.

3. **Evidentiary Assurance**: evidence bundle for later review, contestation, and accountability.


Each abstract and introduction should state this division explicitly enough that cross-citations look intentional rather than repetitive.
### Immediate Second Patch
1. **Adversarial Pragmatics**

  - Make the first empirical paragraph say directly that the pilot is calibration and judge-validation, not evidence of model-level safety differences.

  - Make P008 repair non-optional: mark it out of strict-pair scoring in the current artifact and identify the repair path.

  - Strengthen judge metrics language so minority recall and per-class performance are primary, with kappa secondary.

  - Add a sanitized row-level adjudication artifact if the current summaries contain enough material; otherwise add a precise release requirement.

2. **Delegation Assurance**

  - Move status / priority / licensing even closer to the first-page contribution claim.

  - Add a filled-in delegation matrix for the procurement assistant.

  - Sharpen the gap against authenticated-delegation and IETF audit-protocol work: those provide infrastructure, but not language-status interpretation, refusal calibration, evaluator licensing, or evidence adequacy for the justified-action claim.

  - Consider softening the subtitle later, but do not rename the paper in this patch unless the title machinery is already easy.

3. **Evidentiary Assurance**

  - Distinguish admissibility, weight, and sufficiency in the legal framing.

  - Reframe "rebuttable presumption" as a rebuttable audit inference unless a legal rule is being defended.

  - Add privacy/minimization to the minimum evidence bundle and technical architecture.

  - Keep administrative-law analogy generic unless a jurisdiction-specific pass is done later.

### Defer
1. Do not run a development-pass experiment in this patch.

2. Do not globally rename "justified machine action" yet; first see whether added definitions and artifacts reduce the risk.

3. Do not perform a full legal doctrine pass now.

4. Do not commit until the current accumulated review-triage edits are verified together.
