# Excellence revision plan: Adversarial Pragmatics, Delegation Assurance, and Evidentiary Assurance

**Status:** Implemented and verified; empirical and external evidence gates remain
**Date:** 2026-07-21
**Scope:** The three manuscripts in this repository, their shared vocabulary, and the executable artifacts needed to make their central claims auditable. Study A's data, coding, and preregistered analysis remain unchanged.

## Decision in one sentence

These papers need a coordinated major revision, not a projectibility paragraph and a Messick citation in each: every paper should distinguish the claim being made, the object and use being validated, the inference being projected, the world-side pattern hypothesized to support it, and the prospective conditions under which the claim will be narrowed or withdrawn.

The three papers should still stand alone. Coordination should remove equivocation and duplication, not turn them into chapters whose arguments work only when read together.

## Why the previous integration is no longer enough

The July 18 integration correctly separated authorization, evidence, and empirical evaluation and added projectibility language in bounded places. That pass was successful at its stated scope. The projectibility-history paper and the Messick sources expose a deeper problem that the earlier pass did not test: several central terms still attach to the wrong bearers, and several proposed procedures issue results without an explicit validation argument for the intended interpretation and use.

The recurring error is compression. Across the three manuscripts, one noun sometimes covers several distinct things:

- a reference proposition about what an authorization regime permits;
- a record of that proposition and the evidence supporting it;
- an evaluator's item-level classification;
- a sample-level performance summary;
- an interpretation or use of that result;
- an extension from observed to unobserved cases;
- a causal or mechanistic explanation of the observed pattern.

Those claims can agree, but none entails the next merely by being recorded, repeated, or labelled. Excellence here means making the interfaces explicit and then testing the interfaces on which each paper's advertised contribution depends.

## Portfolio division of labour

The papers need a stable ownership map so that each can be ambitious without restating the others.

| Work | Primary owner | What the three papers may import |
|---|---|---|
| General projectibility framework | *Projectibility: A History and a Diagnostic Framework* | The declaration--inquiry/use--warrant--revision package; the distinction between a projective claim and its hypothesized world-side profile or ground; support grades; prospective demotion |
| General critique of scalar AI evaluation and target-indexed transport | *AGI Evaluation* | The case against universal scores; the AI-evaluation application of target-indexed claims, selection, and transport |
| Pragmatic construct and empirical benchmark | *Adversarial Pragmatics* | Operational definitions, construct-domain coverage, controlled contrasts, evaluator studies, and bounded empirical results |
| Normative authorization semantics | *Delegation Assurance* | Regime-relative standing, scope, valid transitions, trajectories, and the difference between normative permission and its representation |
| Evidentiary review | *Evidentiary Assurance* | What a specified record warrants about a specified action, plus the adequacy and contestability of that record under a declared forum and evidential standard |
| Broader responsibility and personhood | The relevant philosophical papers | Moral, causal, historical, and social responsibility; the present assurance papers stay with legal and institutional answerability unless they explicitly distinguish another sense |

The cross-paper claims matrix should be revised accordingly. The projectibility paper owns the general framework. The AGI paper owns its use in general AI evaluation. The three manuscripts here apply the framework to different objects; none should imply that it originated in the AGI paper.

## A common typed claim stack

Before revising prose, create a small common vocabulary and classify the load-bearing claims in all three papers. The classification is not a score and is not a new grand theory. It is a guardrail against moving silently between levels.

| Type | Canonical question | Typical bearer | Examples in this portfolio |
|---|---|---|---|
| Normative reference claim | What does the supplied regime license or require? | An action or trajectory under authorization regime \(R\) | Whether a source has standing; whether a transition is authorized |
| Recorded representation | What does the available record encode? | A versioned trace, instrument, policy, or evidence bundle | Recorded scope, context status, transformation history |
| Item-level finding | What happened on this case? | One item, response, trace, or review | A model emitted a string; a reviewer marked a subclaim supported |
| Sample-level result | What pattern occurred in the observed sample? | A fixed sample under a named configuration | Pairwise pass rate; reviewer agreement; ablation contrast |
| Assessment interpretation/use | What may a result be taken to mean or used for? | A configured assessment procedure and its proposed use | Pipeline diagnosis, item revision, procurement review |
| Projective claim | What should hold beyond the observed cases? | A named bearer over a declared unit, population, range, and time/version | Performance on held-out templates, reviewers, domains, or deployments |
| Causal or mechanistic claim | What change produces what result, and why? | A specified causal system and intervention | Effect of an authority manipulation; role of a typed record field |

For institutional review, the object-level graph should also keep four verdict families separate:

1. authorization under the supplied regime;
2. record adequacy or reconstructability;
3. identification of a legally or institutionally answerable bearer;
4. contestability, forum, and remedial capacity.

A declared use may require a conjunction of these. That policy choice must not be built into the ontology, because an action can be authorized but poorly recorded, or unauthorized but impeccably recorded.

### Terminological rules

- Reserve **assessment validity** for the evidential argument supporting an interpretation and use of an assessment result. A benchmark, judge, checklist, or model is not simply “valid.”
- Use **authority validity** or **delegability under \(R\)** for the legal or institutional power to authorize.
- Use **record adequacy** for whether the available evidence permits reconstruction or adjudication.
- Keep **answerability** and **contestability** distinct from both authorization and record adequacy.
- Use **projective claim** for the inference to unobserved cases. Reserve **projectibility profile** for the worldly property-and-relation pattern hypothesized to make that inference non-accidental.
- Keep **warrant** separate from the hypothesized profile or ground. Repeated success is evidence; it is not by itself a mechanism, stabilizer, maintainer, or controller.
- Qualify **control**: linguistic or instruction-status control, governance/internal control, runtime gating, and corrective causal control are different notions.
- A DAG represents assumptions and queries; it does not itself establish causal attribution, legal responsibility, or normative authority. A selection diagram can organize a specified transport problem, but cannot transport the meaning or validity of a changed normative target.

## Shared projective-claim discipline

Every nontrivial extension beyond observed cases should have four explicit blocks. These may be compact in the prose and complete in a machine-readable register.

### 1. Projective declaration

- source result;
- projected outcome;
- bearer;
- unit of analysis;
- target population or case class;
- conditions and allowed transformations;
- time and version range;
- quantitative or categorical tolerance.

### 2. Inquiry and use

- intended decision or research use;
- evidential standard and treatment of uncertainty;
- minimum useful reach below which the claim is no longer worth making.

### 3. Warrant plan

- source evidence;
- held-out or target evidence;
- construct/assessment-validity evidence;
- if claimed, evidence for causal order or a supporting world-side profile;
- known selection, measurement, and transport threats.

### 4. Revision rule

- prospectively stated failure trigger;
- predeclared narrower fallback, if any;
- independent retest requirement;
- retirement condition when no useful fallback survives.

Post hoc narrowing after looking at failures creates a new claim; it does not vindicate the old one. A changed model, judge prompt, authorization regime, legal mandate, action meaning, or outcome meaning ordinarily creates a new bearer or target rather than an innocuous scope marker.

## Manuscript 1: Adversarial Pragmatics

### Revised contribution

The flagship should claim that it supplies a construct-explicit, auditable method for evaluating failures of language-mediated control, together with controlled tests of whether configured systems and evaluators respond selectively to the distinctions the benchmark purports to manipulate. It should not claim that the pilot validates the whole benchmark, that observed agreement makes a reference “stable,” or that three successful configuration cells establish performance across models.

### A. Separate four things currently called label projectibility

The present prose sometimes treats “the label” as one bearer. Replace that with four explicit targets:

1. **Reference projectibility:** whether a regime-relative expected action or label remains licensed across declared meaning-preserving transformations.
2. **Behavioural projectibility:** whether a named model/scaffold/prompt configuration behaves within tolerance on held-out items or repeats.
3. **Measurement projectibility:** whether the proposed interpretation survives changes in evaluator population, judge procedure, scoring implementation, or evidence access.
4. **Taxonomic projectibility:** whether an item remains an instance of the claimed pragmatic phenomenon across construct-preserving variants.

These are separate claims with separate bearers and failure rules. A wrapper can change the normative reference. A judge-prompt change alters the measurement procedure. A model/version change creates a new behavioural bearer.

### B. Reinterpret Study A without changing it

Study A should remain fixed. Its paper-level interpretation should be tightened:

- report that the three observed configuration cells passed the stated checks, not that the result is stable “across models”;
- describe the pilot as evidence that the fixed-object coding and analysis pipeline can be executed and diagnosed, not as validation of the complete measurement system;
- treat convergence as evidence about those objects and evaluators under those conditions, not as a gold standard or a transport claim;
- remove or qualify any conclusion that implies untested stability under paraphrase, evaluator change, model change, or repeated sampling.

This is a scientific correction to the estimand and prose, not a change to data or preregistered analysis.

### C. Add a Messick-style validation argument for the proposed interpretation and use

State the initial intended use narrowly: diagnosis of items, rubrics, evaluator disagreement, and configured model behaviour in controlled evaluation work. Explicitly exclude, until separately validated, standalone deployment certification, universal safety scoring, vendor ranking, and claims about general model competence.

Organize the validation programme around six mutually supporting aspects:

| Aspect | Required evidence in this project |
|---|---|
| Content | An expert-reviewed construct-domain map showing which relevant pragmatic contrasts are represented and which are omitted |
| Substantive/response process | Evidence that evaluators use authority, quotation, indirectness, and policy distinctions rather than surface cues; rationales may diagnose this, but private reasoning need not be treated as ground truth |
| Structural | Evidence that the response vector and noncompensatory rules match the construct; no aggregation merely because numbers are available |
| Generalizability | Held-out templates, payloads, evaluator populations, judge procedures, system versions, and trajectory lengths, each attached to a declared claim |
| External | Comparison with independently justified regime-relative references and relevant expert adjudication; neither is universal ground truth |
| Consequential | Error asymmetries, gaming, benchmark overfitting, false reassurance, labour burden, and downstream misuse of apparently precise scores |

Any reader-supplied utility or aggregation creates a new interpretation and use requiring its own validation argument.

### D. Replace item-count expansion with construct-domain coverage

The current numerical growth path should become secondary to a coverage matrix. The matrix should cross at least:

- pragmatic family;
- source and authority relation;
- operative, mentioned, quoted, reported, conditional, or hypothetical status;
- direct, indirect, presupposed, or implicated content;
- task-success, policy-compliance, safety-risk, evaluator-confidence, and failure-attribution criterion;
- single-turn versus trajectory setting;
- controlling transformation;
- nuisance and placebo transformations;
- intended application surface.

Expansion is justified when it fills a declared coverage gap or enables a planned comparison. “More items” is not evidence of content coverage.

### E. Redesign Study B around selective, reference-concordant behavioural sensitivity

Study B should not claim access to whether a model internally “recognizes” authority or pragmatic status. It should test observable, selective response changes under controlled reconstructions.

Required design features:

- byte-identical operative/non-operative payloads where possible;
- counterbalanced harmless tokens, source names, ordering, and syntactic forms;
- held-out templates and payload families;
- nuisance paraphrases and placebos that should not change the reference;
- explicit checks for lexical, position, formatting, and source-name shortcuts;
- a distinction between manipulations that change the normative reference and transformations under which it should remain invariant;
- paired estimates with uncertainty rather than a universal score;
- prospectively declared tolerances, minimum useful reach, failure triggers, fallback claims, and independent retest.

The strongest warranted result would be local: under a named configuration and controlled contrast, the response changes in the reference-concordant direction more often than under matched nuisance changes. That is evidence of selective behavioural sensitivity. It is not yet evidence of a general internal competence, mechanism, or deployment-level safety.

### F. Executable artifacts

- `benchmark/coverage/construct-domain-matrix.csv`
- a versioned Study B claim register conforming to the shared schema;
- a pair manifest marking reference-changing, reference-preserving, nuisance, and placebo transformations;
- validator checks for pair integrity, leakage, balance, declaration completeness, and forbidden post hoc scope changes;
- an analysis output that preserves the outcome vector and reports pairwise effects and uncertainty.

## Manuscript 2: Delegation Assurance

### Revised contribution

Delegation Assurance should become the normative and representational core of the portfolio: it specifies when an action or trajectory is authorized under a supplied regime, how authority propagates through a delegation chain, and what typed representations are needed to test that proposition without confusing the proposition with its record.

### A. Replace the present three levels with a typed claim ontology

The framework should distinguish:

- the normative reference: \(a\in A_R(t)\) or an authorized trajectory under \(R\);
- recorded representations of authority, scope, predicates, and transitions;
- item-level findings about a trace;
- sample-level experimental results;
- assessment interpretations and uses;
- projective claims;
- optional causal or mechanistic claims.

An inadequate record does not make the normative proposition false. A formally exact representation does not establish that the represented institutional rule is legally or organizationally operative.

### B. Separate stipulated and institutional authorization regimes

The benchmark may use a closed-world stipulated regime in which \(R\) and its applicability are fixed by construction. Institutional application is different: the operative regime, conflicts among sources, and the applicability of transition rules may themselves require adjudication.

The paper should state which mode each example and experiment uses. “Declared” means fixed for a test; it does not mean legally effective in the world.

### C. Move trajectory semantics into the core

Single actions should be the \(n=1\) case of a trajectory, not the conceptual centre with trajectories deferred. The transition object needs enough content to evaluate a regime-conditioned transition: actor/agent, action or normative payload, object, relevant predicate/context, time, and resulting state or state delta. Local authorization does not automatically establish cumulative or horizon-level authorization.

The core should represent:

- local permission at each transition;
- constraints on cumulative effects or state;
- revocation, expiry, and changing predicates;
- recombination of individually permitted subactions;
- multiple models and humans in a delegation chain;
- the people and organizations ultimately legally or institutionally answerable for deployment.

### D. Separate three empirical programmes now compressed into one comparison

1. **Randomized local discrimination:** manipulate one regime-relevant feature in a synthetic package and estimate its local effect on the configured evaluator's verdict.
2. **Predictive ablation:** test whether typed authorization fields improve specified prediction or classification outcomes over weaker representations.
3. **Reviewer reconstruction ablation:** compare what reviewers can warrant from typed versus degraded records while holding the normative case fixed.

Each programme needs its own bearer, unit, estimand, reference procedure, use, and failure rule. Purposive fixtures can establish failure modes and local discrimination; they do not estimate real-world prevalence.

### E. Make the figures carry the argument

Replace the opening compression with four typed layers:

1. normative authorization;
2. causal/representational execution;
3. evidentiary reconstruction;
4. projective extension.

The causal figure should place the randomized package inside the graph and the supplied normative reference outside it. The compositional figure should distinguish a normative authorization hypergraph, a recorded propagation graph, and an execution trajectory. Similar shapes across those diagrams must not imply identity.

### F. Add a validation and projectibility programme

Messick-style validation attaches to interpretations of results from the configured DA assessment, not to the formalism in the abstract. The paper should specify content coverage, reviewer process, structural fidelity, generalizability, external regime-relative comparison, and consequences.

The noncompensatory vector is justified only where the supplied regime makes requirements conjunctive. If applicability or necessity can be chosen after seeing the case, the structure can be gamed. Applicability, evidential rules, and required fields should therefore be prospectively versioned.

Every claim that typed delegation records improve prediction or reconstruction should use the common four-block projective package. Failed family claims require predeclared demotion and an independent retest; changing the model, record schema, reviewer population, or regime creates a new claim unless explicitly included in the original range.

### G. Executable artifacts

- a typed authorization-trace JSON Schema;
- a versioned regime fixture format;
- fixtures separating valid authorization from good records, including:
  - valid grant, authorized action, inadequate record;
  - invalid grant, pristine record;
  - misclassification blocked by a correct gate;
  - correct classification followed by a bad gate;
  - locally permitted steps whose cumulative trajectory violates a horizon condition;
- validators for temporal consistency, scope, revocation, transition dependencies, and declared applicability;
- analysis scripts for the three distinct empirical programmes.

## Manuscript 3: Evidentiary Assurance

### Revised contribution

Evidentiary Assurance should specify what a bounded record warrants about a bounded action or trajectory under a supplied authorization regime, forum, evidential standard, and burden allocation. It should also specify how the review procedure itself would be validated before becoming an assurance standard.

### A. Replace the single overall verdict with a typed verdict graph

The current conjunction compresses authorization, reconstructability, answerability, and contestability. Replace it with at least:

- \(J_A\): authorization under the supplied regime;
- \(J_R\): record adequacy/reconstructability;
- \(J_B\): identification of the legally or institutionally answerable bearer;
- \(J_C\): contestability, forum, and remedial capacity.

A declared review use may require some conjunction of these outputs. The framework should not make reviewability constitutive of historical authorization unless the governing regime does.

“Decision basis” belongs in \(J_A\) only where \(R\) makes the relevant factual or legal predicate a condition of authority. Otherwise it bears on legality, merits, or record adequacy without necessarily defeating authorization.

### B. Split record gaps from adverse evidence

For each subclaim, distinguish:

- support;
- adverse evidence or substantive defeat;
- missing evidence/unevaluability;
- conflict or contestation.

The table should have separate columns for record-gap triggers and substantive defeaters. Absence from a record usually yields indeterminacy. Evidence that a condition did not hold can defeat a claim. The two must not share a cell simply because both are inconvenient for assurance.

### C. Make applicability prospective and parameterize verdicts

Applicability, required subclaims, evidential standard, and burden allocation should be fixed by a versioned regime/action-class map before the record is reviewed. A post hoc exemption creates a revised review claim.

Verdicts should be parameterized by at least authorization regime \(R\), forum \(F\), and evidential standard/burden \(\rho\), for example \(J_{R,F,\rho}(q\mid E)\). This does not make the paper a treatise on law. It prevents a generic procedure from silently issuing unqualified legal conclusions.

### D. Reconcile the paper's four decompositions

The six rails, ten primitives, eleven subclaims, and nine evidence layers need a canonical architecture and a crosswalk. A promising structure is:

1. normative/object-level propositions: source, delegability, scope, and regime-conditioned predicates/procedure;
2. identification and reconstruction: action, configuration, context, trajectory, and attribution;
3. record-quality properties: authenticity, integrity, completeness, custody, and access;
4. institutional response: answerability bearer, forum, recourse, and remedial powers;
5. meta-level validation and projective extension of the review procedure.

Record-quality properties are often properties of evidence for several nodes, not additional authorization propositions. The crosswalk should show exactly where each primitive enters and what conclusion its absence or defeat licenses.

### E. Treat the EA test as an assessment requiring validation

The prospective validation claim should name a configured review procedure, reviewer population, action-record population, regime, forum, evidential standard, version, tolerance, intended use, and minimum useful reach.

The research programme should include:

| Aspect | Required evidence |
|---|---|
| Content | Expert and regime-specific mapping of whether the claim graph covers the declared review domain |
| Substantive/response process | Evidence that reviewers use the intended nodes rather than document volume, prestige, verbosity, or surface completeness |
| Structural | Tests of the verdict graph, prospective applicability, conflict handling, and noncompensation at the correct node |
| Generalizability | Held-out action types, organizations, jurisdictions, forums, model/scaffold versions, trajectory lengths, and reviewer populations |
| External | Comparison with independent regime-specific expert adjudication and carefully bounded official cases |
| Consequential | Audit burden, privacy and security leakage, strategic record production, selective preservation, access inequality, chilling effects, and false reassurance |

The claim that risk changes evidentiary burden but not evidentiary kind should become a hypothesis, not an axiom. Begin with common functional questions while permitting domain- and forum-specific evidence kinds and applicability structures. Test comparability before saying two domains meet the same standard.

### F. Build the matched-case calibration programme

Construct factorial cases that independently vary:

- actual regime-relative authorization;
- record completeness;
- authenticity/integrity;
- authority and scope;
- support for decision predicates;
- context standing;
- answerability bearer;
- forum and remedy;
- conflicting evidence.

Essential contrasts include an invalid action with an excellent record, a plausibly valid action with an inadequate record, absence of evidence versus evidence of absence, authorization intact but contestability absent, prospectively inapplicable versus post hoc-excused fields, and conflicting records.

Test selective sensitivity, structural noncompensation, reviewer process, held-out transfer, and consequential costs. Agreement is evidence about reproducibility, not sufficient evidence of validity.

### G. Preserve and sharpen the existing selection analysis

The source--target inventory, denominator analysis, cancellation risks, and distinction between changed causal mechanism and changed normative target are strengths. Keep them, but attach each transport claim to an explicit estimand and projective declaration. Static traces and incident-derived replays are purposive evidence; they do not estimate incidence or live-system efficacy without a defensible sampling design.

Use a Pearlean selection diagram only where the target is a specified causal or statistical quantity and the source/target differences are represented. It cannot carry a legal rule, changed action meaning, or changed evidential standard across jurisdictions by graphical fiat.

### H. Executable artifacts

- a versioned evidence-bundle JSON Schema;
- a regime/forum/action-class applicability map;
- a canonical claim graph and crosswalk from rails, primitives, subclaims, and record layers;
- matched-case fixtures with hidden reference keys and explicit support/defeat/gap/conflict manipulations;
- a validator that prevents post hoc applicability rescue and checks record provenance/integrity fields;
- a calibration harness for selective sensitivity, node-level noncompensation, reviewer instability, and privacy/burden reporting.

## Repository architecture proposed for the revision

The exact paths can be adjusted during implementation, but the artifacts should be first-class and versioned rather than buried in prose notes.

```text
assurance/
  shared/
    claim-types.md
    projective-claim.schema.json
  delegation/
    authorization-trace.schema.json
    regime.schema.json
    fixtures/
  evidentiary/
    evidence-bundle.schema.json
    applicability-map.schema.json
    matched-cases/
benchmark/
  coverage/
    construct-domain-matrix.csv
  study-b/
    claim-register.json
    pair-manifest.csv
scripts/
  validate_claim_register.py
  validate_delegation_artifacts.py
  validate_evidentiary_artifacts.py
```

The repository instructions and build checks should be updated only after this structure is accepted and created.

## Load-bearing assumptions and how to try to break them

| Assumption | Disconfirming test | Consequence if it fails |
|---|---|---|
| The typed claim stack can be applied consistently | Independently classify a stratified sample of load-bearing sentences from all three papers and inspect disagreements | Revise or collapse claim types before rewriting manuscripts |
| The AP taxonomy covers the intended construct domain | Expert domain map plus deliberately sought omissions and boundary cases | Narrow the advertised domain or add missing families before expansion |
| Study B detects selective sensitivity rather than shortcuts | Nuisance/placebo transformations, counterbalancing, held-out templates, and adversarial shortcut probes | Demote to configuration-specific cue sensitivity or retire the family claim |
| DA's typed fields add usable information | Predictive and reviewer-reconstruction ablations against weaker records | Remove redundant fields or narrow the claimed use; do not retain decorative formalism |
| DA's noncompensation reflects the regime | Compare the formal conjunction with prospectively coded regime dependencies | Parameterize or abandon universal conjunction claims |
| EA's primitives and Decision basis do distinct work | Factorial matched cases and reviewer-process evidence | Merge redundant nodes or move them to domain modules |
| EA can be a cross-domain standard | Held-out domain/forum tests including evidence-kind differences | Demote to a common question schema with domain-specific instruments |
| Richer records improve assurance without unacceptable costs | Consequential-validity audit of privacy, security, labour, strategic documentation, and access | Apply minimization, restrict uses, or retire high-burden requirements |
| A projective claim has meaningful reach after failures | Apply predeclared fallback and minimum-reach rules on independent data | Retire the claim rather than repeatedly narrowing it into triviality |

## Execution sequence

### Stage 0 — Baseline and source integrity

- Preserve the current dirty worktree and inventory every pre-existing change before editing.
- Archive and verify both Messick 1995 sources locally; add distinct bibliography entries and source-verification records.
- Correct the literature-intake classification: Messick belongs under assessment validity, not disagreement-as-construct-signal.
- Update the cross-paper ownership matrix before substantive prose so later edits use one division of labour.

**Exit test:** clean source ledger; no manuscript edit yet; accepted claim vocabulary and ownership map.

### Stage 1 — Shared type system and executable substrate

- Draft `claim-types.md` and the projective-claim schema.
- Classify a representative set of claims from each paper; revise the vocabulary where classification is unstable.
- Add schema fixtures for valid, invalid, and post-hoc-narrowed claims.
- Write the shared validator and tests.

**Exit test:** representative claims classify without hidden level shifts; invalid fixtures fail for the intended reasons; no scalar aggregation is introduced.

### Stage 2A — Adversarial Pragmatics and Study B

- Rewrite the contribution and intended-use boundary.
- Correct Study A overinterpretation without changing Study A.
- Add the validation matrix and construct-domain coverage artifact.
- Complete Study B's claim register, controls, pair manifest, estimands, failure rules, and validator integration before collecting new data.

**Exit test:** every result sentence states its bearer and scope; Study B can fail informatively; the benchmark expansion is coverage-driven.

### Stage 2B — Delegation Assurance

- Rebuild the formal core around the typed claim ontology and trajectory-first semantics.
- Separate stipulated from institutional regimes.
- Split the empirical programme into causal discrimination, predictive ablation, and reviewer reconstruction.
- Build and validate the authorization-trace artifacts and figures.

**Exit test:** the formalism distinguishes truth from record; each empirical claim has its own estimand and projective package; fixtures expose level errors.

Stages 2A and 2B can proceed in parallel after Stage 1.

### Stage 3 — Evidentiary Assurance

- Consume the stabilized DA normative objects without making EA dependent on reading DA.
- Replace the global verdict with the typed verdict graph.
- Separate gaps, defeat, conflict, and support; prospectively fix applicability.
- Reconcile the decompositions; build matched cases, schema, and calibration harness.
- Add the full validation and consequential-assurance programme.

**Exit test:** an excellent record cannot make an unauthorized action authorized; a bad record cannot make an authorized action historically unauthorized; forum and remedy do not disappear into a generic verdict.

### Stage 4 — Portfolio harmonization

- Run a terminology and level-of-analysis audit across all three papers.
- Ensure each paper defines imported concepts compactly and can survive standalone review.
- Align examples without repeating whole arguments.
- Update abstracts, conclusions, keywords, diagrams, artifact links, source-verification notes, and LLM-use statements.
- Remove any sentence that treats stability as causal order, an ordering relation as maintenance, or record richness as legal validity.

**Exit test:** no key term changes meaning across papers without explicit qualification; contribution statements are complementary rather than competitive.

### Stage 5 — Verification and adversarial review

- Build all three PDFs with XeLaTeX and run bibliography, style, and source checks.
- Run the seed-item validator and all new schema/artifact tests.
- Audit every quantitative or categorical claim against its source artifact.
- Conduct targeted reviewer passes from at least these standpoints:
  - assessment/construct validity;
  - causal inference and transport;
  - AI evaluation and red-teaming;
  - administrative/technology law;
  - measurement and audit practice;
  - privacy and organizational burden.
- Require reviewers to name the precise claim, bearer, and consequence rather than vote on a manuscript globally.

**Exit test:** no P0 scientific or construct-validity defect remains; all P1 findings are fixed or explicitly scoped with a recorded reason; manuscripts and artifacts agree.

## Things this revision should not do

- Do not alter Study A's data, coding, or preregistered analysis.
- Do not paste a generic projectibility paragraph into each paper.
- Do not recreate the AGI paper's criticized single-score logic as an “assurance score” or universal all-or-nothing verdict.
- Do not call agreement, repetition, or a formal schema validation by itself.
- Do not turn synthetic fixtures into prevalence estimates.
- Do not infer internal recognition from selective behaviour.
- Do not infer causal order from a DAG or transport a normative target with a selection diagram.
- Do not retain fields, primitives, or formal notation that fail ablation or matched-case tests merely because they make the framework look comprehensive.
- Do not make any manuscript depend on unpublished sibling prose for its central definitions or contribution.

## Recommended commitment

Approve this as a major-revision programme with two parallel workstreams after the shared claim architecture: an empirical AP/Study B stream and a normative DA-to-EA stream. The standard is not maximal length. The standard is that every important distinction changes a design choice, verdict, test, or failure rule—and that every central extension can be wrong in a prospectively recognizable way.

## Completion record

Implementation closed on 2026-07-21 after the accepted Roughdraft checkpoint and a post-implementation adversarial false-pass audit.

- The shared typed-claim vocabulary, schema, fixtures, validator, claim registers, and two-pass 18-claim classification audit are executable. The classifications agreed on 17 claims; the sole disagreement was adjudicated explicitly.
- AP now has four separated projective targets, a construct-domain map, frozen Study B manifests, a schema-v1.1 production contract, exact repeat and hash binding, per-base behavioural and shortcut gates, arm-specific output references, simultaneous uncertainty, and 19 permanent analyzer regressions. Its no-target-data result is `NOT_ESTIMATED`.
- DA separates normative reference, representation, proposal, gate, execution, result, and use. Seven stipulated traces and hidden oracles, semantic mutation tests, and three separate empirical-programme specifications and analyzers pass. No target-study result is claimed.
- EA has four verdict vectors, prospective applicability, an immutable hidden key plus separate opening record, 16 populated controlled cases, two expected failures, substantive contrast-coverage gates, three exact claim-map links, and 19 analyzer self-tests. With zero genuine reviewer responses, every use is `NOT_ESTIMATED`.
- The review record simulates all six specified adversarial standpoints and preserves both the initial failed Stage-5 cut and the subsequent closure addendum. The executable Stage-5 exit is met; empirical and external gates remain open.
- All three XeLaTeX manuscripts pass house style and ordinary Biber checks. Final lengths are AP 23 pages, DA 35, and EA 25. The local archive verifies all 80 unique cited works. Visual QA removed near-empty float and spill pages.
- Study A's data, code, and frozen analysis paths were not changed.

The papers remain three coordinated stand-alone works rather than a scalar assurance system or a manuscript-dependent book sequence. Their next claims require target evidence: Study B target responses and independent references, DA's three empirical programmes and institutional comparison, and EA's genuine blinded reviewer calibration and forum-specific external review.
