# Rajagopalan–Zhang Integration and Study B Plan
**Status:** Roughdraft checkpoint before implementation
**Date:** 2026-07-17
## Decision
Use the two papers to strengthen the evaluation and assurance programme without reopening Study A or altering manuscripts already under review. The shared organizing problem is false assurance at the wrong granularity: legal personality doesn't itself provide enforceability, while aggregate accuracy doesn't establish action-level contextual reliability.

All new framing is projectibility-first. It asks which declared inferences an evaluation or assurance record supports, for which systems, items, interventions, and deployment conditions. It doesn't revive HPC, homeostasis, natural-kind membership, or an inferred maintenance-mechanism requirement.
## Tested assumptions and failure conditions
| Assumption | What would make it false | Design response |
| --- | --- | --- |
| Zhang et al. can strengthen Adversarial Pragmatics without changing Study A. | Their measures require data already represented in the fixed 54 objects. | They do not: INS and tail measures require paired context conditions and repeated generations. Add methodological grounding and one scope limitation only; touch no `benchmark/study-a/` file. |
| “Task-irrelevant context” is the right description for Zhang et al.'s intervention. | Added context changes discourse structure or source interpretation even though it supplies no answer evidence. | Call it **task-content-irrelevant** or **non-evidential** context and state that causal influence is not the same as normative authority. |
| Rajagopalan supports the claim that personhood is unnecessary. | Personhood serves moral, recognitional, claimant-side, or expressive purposes beyond enforcement. | Use only her narrower result: bare legal personality is neither necessary nor sufficient for identification, recovery, deterrence, or cessation. Explicitly reject extension to personhood's whole purpose. |
| Runtime identity is adequately represented by an agent or model identifier. | Context assembly, ordering, truncation, retrieval, configuration, or version changes behaviour. | Extend the evidentiary record to bind those runtime conditions and require revalidation after material changes. |
| Private corpus cases can seed a public Study B safely. | A reconstruction preserves recognizable wording, actors, projects, paths, secrets, or proprietary content. | Derive only an abstract phenomenon specification, then write a new benign scenario with harmless payloads. No private excerpt enters Study B. |
| Revision hooks won't disturb submitted manuscripts. | A hook changes manuscript, submission, bibliography, or public metadata. | Create note-only hooks in each project; don't edit manuscript sources, PDFs, submission packages, status surfaces, or bibliographies. |

The strongest inversion is that a context effect may reveal generic instability rather than a failure of pragmatic authority recognition. Study B must therefore include matched non-controlling placebo contexts. An authority account earns its keep only when authority-sensitive behaviour exceeds that generic instability floor.
## Implementation map
### 1. Adversarial Pragmatics
- Add a compact paragraph to `sections/07-metrics.tex` distinguishing two aggregate failures:

  - normative compression through utility weights and base rates; and

  - statistical cancellation of item-level improvements and degradations.

- State the scope boundary: Zhang et al. manipulate context irrelevant to answer evidence, not necessarily context pragmatically inert in an interaction.

- Add one operational recommendation to `EVALUATION-MEMO.md`: pair aggregate scores with item/family transition and harmful-tail reporting.

- Add verified bibliography entries and source-verification rows for both papers, although Rajagopalan won't be cited in the flagship empirical manuscript.

- Do not modify Study A data, materials, protocol, analysis plan, code, or estimands.

### 2. Delegation Assurance
- Replace categorical claims that an LLM “can't bear responsibility” with the narrower claim that executing an action doesn't make the model an independently reachable and answerable legal or institutional actor.

- Define the external governance shell: identifiable accountable bearer, review, redress, financial recovery where applicable, and cessation.

- In the comparative test, add task-content-irrelevant placebo perturbations. An apparent authority effect must exceed generic context instability.

- Distinguish a lost authority edge from nonspecific destabilization caused by accumulated context in compositional delegation.

- Replace promises to reconstruct why an action happened with reconstruction of recorded authority, operating conditions, execution, and review path.

- Require per-item and harmful-tail contextual-reliability reporting alongside mean pass rates.

### 3. Evidentiary Assurance
- Add Rajagopalan's six-layer enforcement stack to the governance comparison while stating the remaining gap: enforceability doesn't prove that a particular action was authorized.

- Extend runtime/context provenance to include role ordering, context length, truncation, retrieval selection, conversation history, inference settings, exact model/configuration version, and material change history.

- Explain that apparently irrelevant material may be causally material. Use hashes, manifests, protected references, and tiered retention where full open retention would violate privacy constraints.

- Distinguish favorable selection from cancellation: optimizer's curse and context instability are separate aggregate-inference failures.

- Promise reconstructable conditions and authority paths, not complete internal causal explanation or deterministic replay.

### 4. Study B: selective sensitivity
Create `benchmark/study-b/design.md` as a design-only protocol, separate from Study A and from the pending Study A HREB inquiry.

Each newly written benign base scenario will support two contrast families:

1. **Control-relevant variation:** change source role, authority, scope, reference, or speech-act status. Appropriate behaviour should change.

2. **Non-controlling variation:** add irrelevant logs, completed prior turns, unrelated tool output, or filler while preserving the operative instruction. Appropriate behaviour should remain invariant.


The target property is selective sensitivity: response to context that controls the licensed action and invariance to context that does not. The design will require repeated samples, separate task-success/policy-compliance/control-uptake labels, item-level transitions, two-sided instability, and harmful-tail reporting. Retrieval yields from the private corpus remain discovery counts, not prevalence or accuracy estimates.

No naturalistic text will be paraphrased into the public set. Reconstruction will proceed from a phenomenon card stripped of wording and identity, followed by a new harmless scenario and privacy review. External annotation or claim-bearing collection remains gated on a separate institutional-scope decision.
### 5. Philosophical-paper revision hooks
Create note-only hooks, without editing live or submitted manuscripts:

- `llms-as-boundary-phenomena/notes/source-hooks/`: Zhang on aggregate capacity versus item-level contextual projectibility; Rajagopalan only as a bounded enforcement-projection example. Mark the next revision as projectibility-first rather than HPC-based.

- `vector-grounding-problem-response/docs/groundwork/`: Zhang as a measurement caution, not evidence of grounding; Rajagopalan has no material role.

- `effective-without-warrant/notes/`: Rajagopalan as an application of the separation among legal status, social efficacy, enforceability, and moral warrant.

- `personhood-and-proforms/notes/`: Rajagopalan's slippage among legal personality, moral personhood, personification, and discourse-level PERSONAL, saved for an R&R clarification only.

## Verification
1. Verify bibliographic metadata and exact claims against the supplied local papers; record both in `notes/source-verification.md`.

2. Build all three LaTeX papers with XeLaTeX through their Makefile targets.

3. Run the central style checker on edited `.tex` sources and validate citation keys.

4. Confirm `git diff --name-only` contains no path under `benchmark/study-a/`.

5. Confirm philosophical repositories contain note-only changes.

6. Review diffs for the prohibited inferences: task-content irrelevance → pragmatic irrelevance; causal influence → authority; enforceability → the whole purpose of personhood; black-box stability → mechanism.

## Deliverables
- Revised flagship metrics section and evaluation memo.

- Revised Delegation Assurance paper.

- Revised Evidentiary Assurance paper.

- Verified local bibliography and source record.

- A standalone, implementation-ready Study B design.

- Four note-only philosophical revision hooks.
