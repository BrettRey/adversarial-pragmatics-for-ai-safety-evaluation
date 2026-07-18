# Study B Projection Register

**Status:** declaration template and selection-node threat map; no transportability result
**Date:** 2026-07-18
**Applies to:** Study B only; development fixtures authorize no collection

## Rule

Projectibility is the umbrella question: what inference, if any, may extend beyond an observed Study B cell? A causal-transport claim requires a fixed causal query, declared source and target domains, target data, and a causal model whose suspected source--target differences are marked. An annotated diagram does not establish transportability by inspection.

Where target access is feasible, direct revalidation is preferred. If the target changes the authority regime, licensed action, outcome meaning, or scoring construct, register a new target claim or estimand instead of treating the change as an `S` node.

## Experiment-specific causal query template

For each model/configuration and base scenario, the default causal question is:

> Under the frozen structured-prompt assembly protocol, how does assignment to each controlled context condition change the joint distribution over concrete main-token and control-token outputs?

This is an intervention contrast over assigned prompt packages, not a claim about an internal reasoning pathway. Base item, model/checkpoint, system and developer configuration, inference settings, and scoring route are conditioned on or frozen for each contrast. The typed authorization record supplies a treatment-dependent reference `Y*(A)`; condition-specific correctness compares `Y` with `Y*(A)` but is not itself the authority effect.

The frozen estimand vector is:

1. the arm-specific joint distribution over all concrete main/control outputs, including invalid-format, refusal, and off-vocabulary outcomes (primary);
2. `P(later-main | C0) - P(later-main | C1)`, interpreted as the total effect of the assigned prompt packages, not a standing-specific effect;
3. `P(later-control | A = a)` for every condition;
4. `P(Y = Y*(a) | A = a)` for condition-specific correctness, with no causal interpretation attached to cross-arm correctness differences;
5. full-distribution stability for `C0`--`N0` and `C0`--`N1`; and
6. `C1`--`N1` as the operativity contrast only after independent matching review.

Family summaries remain descriptive of the finite frozen constructed item set unless a target item population and generative or sampling frame are separately preregistered.

## Source--target declarations

| ID | Source domain | Target domain | Causal query | Required target data | Suspected changed mechanisms or marginals | Normative target preserved? | Decision rule | Current status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | Frozen `structured_prompt` Study B harness, one named model/configuration, one provider version and date | Same item and model/configuration in a separately built document, email, tool-result, or transcript wrapper | Effect of assigned condition on the raw main/control distribution, including `C1`--`N1` after matching | Direct target repeats under the frozen target wrapper; assembly and truncation logs | Context assembly, truncation, scaffold, application surface, tool serialization | Must be checked item by item | No surface transfer from current fixtures; build and rerun the target wrapper, then narrow if effects or placebo floors change materially | Real wrappers unbuilt; threat map only |
| P2 | Frozen Study B run at provider/model version and retrieval date `v0` | Later provider/model version or materially changed local checkpoint `v1` | Same condition effect on the same licensed action | Fresh repeats in every target condition; exact version and configuration record | Model weights, provider routing, system prompt, inference defaults, moderation layer | Yes only if item and authorization record are unchanged | No automatic carry-over; revalidate directly and report versions separately | Direct revalidation required |
| P3 | Frozen rule-aided scoring of harmless tokens | Expert or LLM-judge scoring of the same common response set | Agreement and error of a changed measurement route under unchanged label semantics | Every route scores the same frozen responses; blinded route comparison, agreement, calibration, and information-state audit | Judge/rubric, source-order presentation, expected-answer visibility | Yes only if the response set and label meaning are unchanged | Treat disagreement as measurement-validation evidence; do not describe this as Pearlean transport | Measurement validation only, not a causal transport claim |
| P4 | One stipulated fictional authority regime | A regime with different amendment, release, or outcome rules | Not the same query when the licensed action changes | A new authorization record and newly specified expected action | Normative target or construct meaning | No | Define a new target claim or estimand; do not add an `S` node to P1--P3 | Transport prohibited as currently stated |

## Selection-node threat map

When a row becomes a formal source--target analysis, mark only variables for which a mechanism or marginal difference is substantively suspected:

```text
                                            treatment-dependent reference Y*(A)
                                           ^                                  |
S_assembly -> realized context <- assigned condition A                        v
              |             +----> response Y ------------------------> comparison/score
              +------------------------------------------------------> ^
S_model    -----------------------> response Y                          |
S_surface  -----------------------> response Y                          |
S_judge    -------------------------------------------------------------+
S_time     -> provider/model realization
```

The `S` labels are source--target difference markers. They are not authority markers, sample-inclusion variables, or proof that the query can be transported. Sample selection into construction, pilot survival, or observed complaint requires a separate selection account.

## Demotion rules

Demote or narrow the projected claim when any of the following occurs:

- the target regime changes the licensed action or outcome meaning;
- target assembly, truncation, scaffold, or tool behavior is unobserved;
- the `N0` or `N1` instability floor approaches the `C1` control contrast;
- the action-specific audit control fails, suggesting blanket earlier-text preference or general task failure;
- model or provider changes cannot be versioned or reproduced;
- a scoring route changes the label meaning or sees a different information set;
- target data contradict the projected relation; or
- the source and target do not support the same item-level causal query.

Production projection is also blocked while independent reference-alignment and privacy reviews are pending. The marker regex and structural validator do not establish prompt meaning, privacy, or minimal-pair integrity; normalized prompt-diff whitelisting and independent pair review remain production-freeze work.

The response is direct revalidation where feasible; otherwise report the narrower source-domain result, split the target, or mark the projection unresolved. No single selective-sensitivity score may override these item-, family-, configuration-, and target-specific decisions.
