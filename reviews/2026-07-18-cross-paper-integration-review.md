# Cross-paper integration review: commitment, causation, selection, and evidence

**Date:** 2026-07-18
**Scope:** *Adversarial Pragmatics*, Study B, *Delegation Assurance*, and *Evidentiary Assurance*
**Status:** implementation accepted; production Study B collection remains closed
**Hard boundary:** Study A was not changed

## Review method

Three independent review roles examined the implementation: causal identification and selection, delegation/governance/legal semantics, and empirical pragmatics/security evaluation. Their role labels describe the questions put to simulated reviewers; they don't imply participation or endorsement by named scholars, and convergence among them isn't field consensus.

The first pass returned **REVISE**. The causal reviewer then received the repaired validator without seeing or editing the implementation and replayed the original counterexamples. The post-repair verdict was **PASS** for the bounded implementation. Passing the implementation review doesn't authorize production collection.

## Findings and disposition

| Initial finding | Repair | Disposition |
| --- | --- | --- |
| `C0`--`C1` was at risk of being read as a standing-specific effect even though the prompt packages co-vary. | The primary object is now the arm-specific joint main/control-token distribution. `C0`--`C1` is explicitly a total assigned prompt-package effect. | Closed. |
| Cross-arm correctness could conceal the intended behavioural transition because the reference changes with condition. | The reference is treatment-dependent, `Y*(A)`, and correctness is condition-specific rather than the authority-effect estimand. | Closed. |
| `C1`--`N1` could be interpreted before protection content and load were independently matched. | The operativity contrast is unavailable until an independent matching review passes. | Closed as an implementation claim; matching remains a production gate. |
| The validator could accept C1 invalidity caused by lost issuer standing rather than an unsatisfied guard. | C1 now requires the fixed issuer to retain amendment standing and invalidity to arise from a nonempty, unsatisfied declared guard. No new C1 amendment actor or holder may appear. | Closed. |
| `N0` or `N1` could alter structured authority content while retaining the baseline regime ID. | Full authorization records for `C0`, `N0`, and `N1` now have to match after removal of condition-specific explanatory prose. | Closed. |
| A transition could fall outside the founding, authorization-record, or amendment-rule interval. | The validator parses the frozen `Tn` time vocabulary and requires the transition time to lie within all three intervals. | Closed. |
| Inert or placebo spans could be marked operative or governing. | Span IDs now constrain status, operativity, content type, source role, source kind, and governing-source membership. | Closed. |
| Required roles were unused annotations in the validity path. | The finite fixture validator binds role, event, and guard identifiers and rejects role or issuer substitutions. | Closed for the four fixtures. Expanded families need explicit event-to-role/evidence objects. |
| Study B's apparent target could drift from a finite, frozen test set to a model, vendor, wrapper, or deployment claim. | The design names the model/configuration, item family, `structured_prompt` surface, scoring route, and sampling conditions; wrappers and later versions require direct revalidation. | Closed. |
| A selection diagram could be treated as proof of transportability. | The register freezes a causal query and labels its diagram a selection-node threat map. P3 is measurement validation, and a changed normative target creates a new claim rather than another `S` node. | Closed. |
| Delegation assurance blurred authorization semantics, evidence sufficiency, answerability, remedy, and liability. | *Delegation Assurance* now owns temporal, operation-specific authorization semantics; *Evidentiary Assurance* owns record adequacy and evidentiary verdict. Answerability bearers and review/remedy forums are separate, and neither determines liability. | Closed. |
| A responsive principal--agent picture misclassified protected discretion or credible commitment as drift. | The paper distinguishes responsive, protected-discretion, and commitment-protected modes; tests the operative mandate rather than the latest preference; and treats commitment protection as contingent rather than inherently desirable. | Closed. |
| Evidentiary assurance risked treating record presence as a positive verdict. | Record adequacy is now distinct from whether the evidence supports, defeats, or leaves the action-level claim indeterminate. The Robodebt analysis separates decision-basis, adverse-signal, and observation-selection failures. | Closed. |
| Aggregate summaries could hide oppositely signed item effects. | All three papers retain item/action transitions and relevant tails; none uses a universal delegation, assurance, or selective-sensitivity score. | Closed. |

## Post-repair adversarial replay

The causal reviewer verified the current 4-base, 16-item fixture and all 28 regression/mutation tests. The replay rejected:

- all four original counterexamples;
- four additional interval and required-role probes;
- all ten incorrect required-role substitutions; and
- all ten C1 actor/issuer substitutions.

The reviewer returned **PASS** and treated the remaining reference, privacy, matching, prompt-diff, held-out-construction, and wrapper work as declared pre-production gates rather than current implementation defects.

## Projectibility-first audit

The Study B design was also audited against the projectibility and securing-claim checks. The audit is read-only and doesn't import an HPC or natural-kind framework.

| Check | Status | Evidence |
| --- | --- | --- |
| Projection target | GREEN | The design declares an item-, model/configuration-, surface-, and scoring-specific inference; the projection register states the experiment-specific causal query. |
| Diagnostic independence | GREEN | No category earns projection from its own membership test. Claims beyond an observed cell require target data or direct revalidation. |
| Securing-ladder separability | GREEN / not invoked | The design claims no stable-profile, network-order, maintenance, or corrective-control tier. |
| Stabilizer versus controller | GREEN / not invoked | `Control` denotes which context is licensed to guide action, not a homeostatic or corrective mechanism. |
| Level and mereology | GREEN | The authorization record defines the stipulated reference; it is explicitly not a behavioural causal mechanism. Actor, model response, and scoring route remain separate bearers. |
| Scope and field-relativity | GREEN | The current surface is exactly `structured_prompt`; family summaries describe the finite frozen constructed set; provider, model, scaffold, and wrapper changes require revalidation. |
| Failure modes and demotion | GREEN | The design lists contrast-integrity, ambiguity, scoring, instability, privacy, comparability, tail, and judge failures and requires narrowing, splitting, or demotion. |
| Positioning and conclusion | GREEN | The payoff is the bounded inference the experiment licenses, with no mechanism-first or universal-score claim. |

Projectibility is structural rather than decorative: it fixes the target, unit, estimands, selection boundaries, revalidation rule, and demotion conditions. The design makes no securing-tier claim beyond the observed, finite, model-and-configuration-specific response profile.

## Remaining gates

No production generation, external annotation, or claim-bearing Study B collection is authorized until the following are frozen and passed:

- content-bound independent reference-alignment and privacy reviews;
- normalized prompt-diff whitelists and independent minimal-pair review;
- C1--N1 matching review;
- explicit event-to-role/evidence objects for any family beyond the four frozen fixtures;
- untouched held-out production items or a fresh set frozen before production outputs are viewed;
- real wrapper construction and target-specific validation for any surface claim;
- model/configuration list, inference settings, sampling count, retry rule, codebooks, scoring routes, exclusions, and tail rule; and
- the release boundary and separate institutional-scope evidence for any external human evaluation.

The AGI Evaluation worktree remained untouched. Its live agent owns the coordinated checks on `S`-node meaning, normative-target changes, dashboard-before-aggregation, and current projectibility-first title/version metadata.

## Verification record

- Study B validator: 4 bases and 16 items; 28 tests passed; Python compilation passed.
- Manuscripts: *Adversarial Pragmatics* 20 pages, *Delegation Assurance* 27 pages, *Evidentiary Assurance* 16 pages.
- House style: no violations in the three top-level manuscripts.
- LaTeX: no undefined citations or references. Delegation and Evidentiary have no overfull boxes; the flagship retains three visually harmless 1.28--2.40 pt warnings.
- Bibliography: 31, 41, and 34 citekeys respectively; 75-key union; no missing or duplicate entries.
- Local source archive: 75 of 75 cited sources present with matching SHA-256 hashes. No relevant Rajagopalan, Zhang, Pearl/Bareinboim, Robodebt, or Miller files remain in Downloads.
- Study A no-touch proof reproduced: tracked-diff SHA-256 `03cd54e19edc21fc26f2ab19309c1abae6485dc07a2e7db4a95d2503fde20f0b`; complete file-manifest SHA-256 `76f2b1bcd3a28ad064d660451a6efaea2966f89e0596970af39f92ebc901c40a`; pre-existing modified-file SHA-256 `e0fd7021704f3e0d9b68117ab63a2e29e74c1126d653f33934d56c86791d7f3b`.
- `git diff --check` passed in this repository and in the four note-only philosophical-hook repositories whose stale Downloads paths were corrected.

No commit, tag, external invitation, return opening, or collection action was performed.
