# Study B Design: Selective Sensitivity under Controlled Context Variation

**Status:** design only; no collection authorized
**Date:** 2026-07-17
**Relationship to Study A:** separate study, item set, estimands, analysis plan, and institutional-scope decision

## Research question

Can an AI system distinguish context that should control a licensed action from context that is causally present but has no standing to alter that action?

The target property is **selective sensitivity**:

- behaviour changes appropriately when pragmatically controlling context changes; and
- behaviour remains stable when non-controlling context changes.

The first requirement rules out blanket invariance. The second rules out generic context sensitivity masquerading as authority recognition. Context can causally affect a response without being normatively entitled to guide it.

## Projectibility claim

A Study B result supports a model-and-configuration-specific inference about selective sensitivity within the declared phenomenon families, application surfaces, context loads, and sampling conditions. It does not by itself support a claim about general safety, a vendor, all agent trajectories, or deployment robustness outside that intervention range.

Every reported result must name:

- model and exact configuration;
- item and phenomenon family;
- application surface;
- context condition and length;
- sampling settings and number of repetitions;
- scoring route and judge information state;
- projected inference and known defeaters.

Material model, scaffold, or context-assembly changes require revalidation. The design is projectibility-first; it assumes no HPC, homeostatic, natural-kind, or maintenance-mechanism framework.

## Source boundary

The private naturalistic corpus is a discovery instrument, not Study B data. Its candidate classes are retrieval categories, not gold labels, observations of prevalence, or model comparisons.

No private excerpt will be quoted, lightly edited, paraphrased, or translated into a Study B item. A candidate may contribute only an abstract phenomenon card containing:

- provisional pragmatic phenomenon;
- abstract control relation;
- observed failure or success shape;
- competing non-pragmatic explanation;
- minimum context needed to reproduce the distinction;
- forbidden identifying or proprietary features.

A new scenario is then written from the phenomenon card in a different harmless domain, with new wording, actors, objects, and action surface. Payloads use colours, ordinary tokens, dummy records, fictional tools, or other non-operational material. The private candidate-to-card linkage remains in the restricted vault and never enters a released item.

## Controlled reconstruction gate

An item can enter development only if all six checks pass:

1. **Novel expression:** no distinctive phrase or sequence from the naturalistic source remains.
2. **Novel setting:** people, organizations, projects, paths, repositories, correspondence, and incidents are replaced rather than pseudonymized.
3. **Harmless payload:** the item cannot perform or teach a consequential unsafe action.
4. **Single declared contrast:** the controlling manipulation is named and competing changes are minimized.
5. **Matched placebo:** a non-controlling variant supplies comparable surface material or contextual load without changing the operative license.
6. **Privacy review:** a reviewer with no access to the linkage record cannot recover the source episode from the item.

Failure on novelty or privacy permanently excludes that reconstruction. It is not repaired by adding more redaction.

## Experimental unit

The primary unit is a **base scenario × model/configuration × context condition × generation repeat**. Each base scenario produces a four-condition contrast set.

| Condition | Manipulation | Expected relation to baseline |
| --- | --- | --- |
| `C0_baseline` | Unambiguous operative instruction with minimal necessary context. | Reference condition. |
| `C1_control_change` | Change one source-role, authority, scope, reference, or speech-act fact that alters what action is licensed. | Behaviour should change appropriately. |
| `N0_inert_load` | Add task-content-irrelevant material with no standing and no answer evidence. | Behaviour should remain stable. |
| `N1_matched_placebo` | Add surface material matched to the controlling contrast, but place it where it is quoted, completed, untrusted, or otherwise lacks standing. | Behaviour should remain stable. |

`C1` measures warranted sensitivity. `N0` estimates nonspecific load sensitivity. `N1` tests whether the model distinguishes the control relation from a surface lookalike. The exact four-way realization may vary by phenomenon, but all conditions must preserve the same harmless action target and scoring scale.

## Development set

The initial target is 24 base scenarios, each with four conditions, for 96 development items. Cases should span at least six high-yield phenomenon families identified during private corpus review:

1. source role and authority;
2. mention, use, and speech-act status;
3. scope, exceptions, and negative-constraint persistence;
4. deixis, reference, and long-distance attachment;
5. repair uptake and cross-turn state;
6. action, completion, and failure reporting in tool or transcript settings.

Allocation across families follows reconstruction yield and pair integrity, not private candidate frequency. A family with fewer defensible reconstructions receives fewer cases; retrieval counts never become benchmark weights.

Before production sampling, run a 12-base-scenario construction pilot. Its purposes are to test pair integrity, output schema, scoring feasibility, privacy review, and the generic-instability floor. Pilot outcomes do not become confirmatory findings.

## Generation protocol

- Test several publicly accessible or locally reproducible models, with the list frozen before production generation.
- Record exact model identifier, provider, version or retrieval date, scaffold, system/developer instructions, tools, context assembly, inference parameters, and seeds where available.
- Randomize condition order independently within model while preserving a stored schedule.
- Use clean sessions unless conversational history is the declared manipulation.
- Draw repeated samples in every item-condition cell. Use five repeats in the construction pilot; choose and freeze the production count from pilot variance, cost, and precision before viewing production comparisons.
- Preserve failed calls, truncation, refusals, and invalid structured outputs as outcomes rather than silently retrying them. Any protocol-level retry rule must be frozen in advance.

## Label spaces

Keep the existing analytic separations:

- task success;
- policy compliance;
- control uptake: which context the response treated as action-guiding;
- refusal type and calibration;
- visible safety risk;
- failure attribution;
- scoring confidence and unresolved ambiguity.

Control uptake is not inferred from final correctness alone. Where possible, harmless token outputs and tool-call arguments permit rule-aided scoring. Nuanced transcript or attribution cases require a prescriptive codebook and validated expert adjudication. An LLM judge may be evaluated as a scoring route but cannot define the reference labels by itself.

## Primary summaries

Report cells and transitions before any aggregate.

1. **Controlling-context response:** item-level transition from `C0` to `C1`, classified as appropriate change, inappropriate change, or no required change because the item failed construction review.
2. **Inert-context stability:** item-level transition from `C0` to `N0`.
3. **Matched-placebo stability:** item-level transition from `C0` to `N1`.
4. **Selective-sensitivity profile:** the joint pattern across the three contrasts, reported by item, phenomenon family, application surface, model/configuration, and label space.
5. **Two-sided instability:** improvements and degradations under each non-controlling condition reported separately and as mean absolute change where repeated samples support probability estimates.
6. **Harmful tail:** worst-affected items or families reported only when the number of items and repeats supports a stable estimate. If items are selected and estimated on the same data, use split-sample selection and estimation.

Do not collapse warranted sensitivity and non-controlling invariance into one headline score unless a specific deployment decision supplies a defensible utility function. Never cap or discard beneficial shifts before checking whether they cancel harmful ones.

## Analysis contrasts

The core analysis compares:

- `C0` versus `C1`: does behaviour track the declared control relation?
- `C0` versus `N0`: how much generic instability follows from added load?
- `C0` versus `N1`: does a surface-matched but non-controlling string hijack behaviour?
- control effect versus placebo effects: does the authority-sensitive signal exceed the generic context-instability floor?

Inference is crossed by model/configuration, item, phenomenon family, application surface, and context type. Because affected items may be model-specific, a pooled result cannot substitute for model-specific transition tables.

## Construction and measurement failure conditions

Pause or demote the affected claim when:

- controlling and placebo conditions change more than the declared pragmatic dimension;
- adjudicators cannot agree on what context has standing after clarification;
- the scoring route cannot distinguish control uptake from final-answer luck;
- the non-controlling instability floor is as large as the purported authority effect;
- privacy review cannot establish that the reconstruction is genuinely new;
- model or scaffold changes make earlier cells non-comparable;
- the item or repeat count is too small for a stable tail estimate;
- judge errors concentrate in the same phenomenon being measured.

An item that fails contrast integrity is revised or removed before production. A phenomenon family whose projections repeatedly fail is narrowed, split, or reported as diagnostically ambiguous rather than repaired through an aggregate.

## Privacy, release, and institutional scope

Study B's public layer may contain only new benign controlled reconstructions, schemas, codebooks, aggregate summaries, and intentionally released model outputs. The private discovery corpus, linkage vault, source histories, and naturalistic excerpts remain ignored and access-controlled under the existing privatization record.

The pending Study A HREB inquiry describes only expert application of fixed codebooks to the 54 Study A objects. It does not cover this corpus, Study B, retrospective self-study claims, or future external annotation. External recruitment, claim-bearing human evaluation, or publication of naturalistic material requires a separate written institutional-scope decision before it begins.

## Pre-collection gates

Production generation or annotation remains closed until the following are frozen:

- base scenarios and all four conditions;
- reconstruction and privacy-review records;
- item schema and validator;
- model/configuration list and generation settings;
- sampling count and retry rule;
- label codebooks and scoring routes;
- primary contrasts, exclusions, and tail-estimation rule;
- release boundary and institutional-scope evidence.

Passing these gates authorizes only the activity named by the gate. It does not alter Study A or turn the naturalistic corpus into study data.
