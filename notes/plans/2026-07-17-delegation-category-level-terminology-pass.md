# Category, level, and terminology pass: Delegation Assurance
## Objective
Revise the Delegation Assurance manuscript so that every predicate applies to the right kind of object and every key term has one stable job. The pass should sharpen the existing argument rather than add a new theoretical layer.

The governing discipline is:

> Authority regimes determine authorization; records represent that determination; deployments propose, gate, and execute operations; traces supply evidence; reviewers assess claims; projective conclusions require a declared target.
## Assumptions tested
1. **The target is Delegation Assurance only.** No changes will be made to Study A, the benchmark, AGI Evaluation, or Evidentiary Assurance.

2. **This is an editing pass, not a report-only audit.** The manuscript will be revised after this checkpoint.

3. **The central triad remains useful but needs a fourth distinction.** Contextual status, source standing, conflict priority, and licensing should be separated. Priority applies only after an occurrence has the relevant status and its source has standing; provenance channel or document type is not itself a priority rank.

4. **The existing projectibility-first safeguards are directionally right.** The defect is that action-specific, item-level component, protocol-validation, and projective performance claims still share one claim tree in places.

5. **The strongest inversion is constitutive.** A perfectly propagated authorization record can misstate the governing regime, while a valid grant can exist without an adequate record. The manuscript must be able to describe both cases without contradiction.

6. **Permission doesn't imply obligation.** Refusing permitted work may defeat task success or mandate compliance; it defeats action authorization only when the regime separately requires action and the omission is the assessed action.

## Level model
| Level | Proper objects | Proper predicates |
| --- | --- | --- |
| Normative | authority regime, grant, standing, constraints, proposed or executed operation | confers, applies, permits, prohibits, requires, authorizes |
| Representational | recorded status classification, recorded authorization state, scope field, constraint field | records, represents, propagates, omits, mismatches |
| Behavioural | model output, call proposal, gate decision, delivered output, executed operation | generates, proposes, permits/blocks at gate, delivers, executes |
| Evidentiary | record, trace, evidence item, claim, subclaim, reviewer verdict | preserves, reconstructs, supports, defeats, leaves unevaluable |
| Inferential | action-specific claim, item-level component finding, protocol-validation claim, projective target | applies to, estimates, validates for, projects to, requires revalidation |
## Terminology policy
- **Status**: independently adjudicated contextual role of a string occurrence.

- **Classification**: the system's recorded assignment of status.

- **Observable use/action selection**: how the occurrence affected a proposal or decision.

- **Standing**: a person's, role's, or instrument's competence under the authority regime to confer or alter authority.

- **Priority**: the conflict rule among directive occurrences whose status and source standing have already been established.

- **Grant**: the bounded authority-conferring act or instrument.

- **Authority regime (R)**: the applicable standing rules, grants, constraints, policies, and approval conditions.

- **Authorization**: the action-specific verdict under (R).

- **Licensing**: the manuscript's named analytic link from status, standing, and priority to authorization of a consequence; it will not be used as a loose synonym for every permission.

- **Permission**: an allowed operation, disclosure, or state change. **Approval** is an event satisfying a declared authorization condition. **Requirement** or **obligation** is distinct from both.

- **Proposal → gate decision → execution/delivery**: separate behavioural stages.

- **Record**: a stored artifact. **Trace**: linked or ordered records of events. **Evidence**: the role an admissible record or observation plays in supporting a claim.

- **Automated evaluator**: generic system category. **LLM judge**: automated subtype. **Expert adjudicator**: source of human reference judgments. **Assurance reviewer**: assessor of the claim and evidence.

- **Evaluation bearer (S)**: the entity whose performance is measured. **Executing deployment (D)**: the configured system through which an output is delivered or operation occurs. **Component (C)**: a model, classifier, gate, tool, or logger contributing to the event. **Potentially answerable actors**: people and organizations occupying named roles; the term doesn't prejudge legal liability.

## Planned repairs
### 1. Separate action, record, and governance properties
Replace the claim that an action is simultaneously authorized, scoped, attributable, contestable, remediable, and auditable with a compound assurance case:

- the proposed or executed operation was authorized and within scope;

- the trace supports operational and institutional attribution and audit;

- the governing process supplies contestation and operational remediation.


The action-specific authorization claim remains central; the other properties belong to linked claim trees.
### 2. Separate claim trees and verdict levels
Rewrite the safety-case pattern around three non-fungible outputs:

1. **Action-authorization claim** for identified operation (a), executing deployment (D), and authority regime (R).

2. **Item-level component findings** for the same trace: status-classification fit, standing/priority application, proposal, gate decision, execution, logging, and evaluator-label use.

3. **Projective performance claim** for declared target (T), including bearer/configuration, task and context population, regime/policy snapshot, environment, horizon, decision use or loss, support/shift conditions, and revalidation triggers.


Noncompensation applies within each declared claim tree. The paper will report the three outputs as a vector rather than allowing one to stand in for another. At the subclaim level, use **supported**, **defeated**, or **unevaluable**. At the top level, use **supported**, **not supported**, or **indeterminate**. **Not applicable** remains an applicability ruling, not a verdict.
### 3. Separate reconstruction from validation of a reconstruction protocol
For one action, ask whether admissible evidence and warrants support reconstruction. Across cases, separately test whether a specified matrix/trace protocol improves reference-aligned reviewer judgments over a declared target. A holdout supports projection only to the extent that its relationship to (T) is stated and defended.
### 4. Repair permission/obligation errors
- Reclassify over-refusal as task-fulfilment or mandate-compliance failure unless (R) imposes a duty to act.

- Make refusal-calibration rows score authorization, task success, and any requirement to act separately.

- Replace claims that abandoning merely authorized work defeats action authorization.

### 5. Separate normative authorization from its record
In the compositional section, define:

- (A_R(n)): actions permitted at node (n) under governing regime (R);

- (\widehat{A}(s_n)): actions that recorded state (s_n) represents as permitted.


Normative non-amplification constrains (A_R). Record-level propagation constrains (\widehat{A}). Assurance also requires evidence of fit between them. A record omission defeats a component or audit subclaim; only an executed operation outside (A_R) defeats the action-authorization claim.
### 6. Repair bearer and action-stage drift
- Reserve **model** for generated output, classification, or proposal unless the model itself is the declared evaluation bearer for a performance claim.

- Attribute delivered outputs and executed operations to the configured deployment/runtime.

- Rewrite the action-specific claim as an operation executed through (D), not an action “by (S)” when (S) may be a base model.

- Distinguish proposed, gate-authorized, blocked, delivered, and executed calls in audit and red-team passages.

- Replace **accountable bearer** with **potentially answerable actors** and keep legal liability separate.

### 7. Repair status/standing/priority terminology
- Split the existing authority-priority subclaim into source standing and conflict priority.

- Replace lists that treat system, developer, user, tool, retrieval, memory, and policy as parallel sources. Record issuer/role and standing separately from technical channel, storage location, and content type.

- Replace “authority status of the directive and its source” with contextual status of the occurrence and standing of its source.

- Treat status → standing → priority → licensing as a logical dependency, not a mandatory temporal architecture.

### 8. Repair evidence and diagnostic categories
- Rename the evidence-table header from **Delegation subclaim** to **Evidence or diagnostic dimension**; each row supports an explicitly declared claim rather than automatically becoming a required subclaim.

- Replace “the trace fails delegation assurance” with the appropriate claim verdict or evidence-adequacy judgment.

- Separate technical locus, normative-boundary adjudication, and evaluative uncertainty in failure attribution.

- Call an isolated error an item-level finding or a reliability hypothesis, not a reliability failure.

### 9. Repair the comparative test and figures
- Describe causal attribution and authorization as cross-classifying different questions, not as opposite verdicts.

- In Figure 2, make the principal-to-record task link an ordinary record/input edge; reserve the dashed relation for source standing.

- Rename visible “authority edge” language to **standing relation**.

- Split predictive and reconstructive demotion rules: failure on one doesn't demote the other.

- In Figure 1, use **assurance reviewer** rather than conflating an operational evaluator with an independent reviewer.

### 10. Make local logical and lexical repairs
- Fix the persistence contrast so the same proposed update is paired with two different grants.

- Replace generic **authority effect/family/status** with the specific manipulated or adjudicated object: authorization contrast, standing contrast, contextual status, source standing, or authorization verdict.

- Prefer **authorized action** and **permitted operation**; reserve **Licensing** for the named analytic dimension.

- Use **automated evaluator**, **LLM judge**, **expert adjudicator**, and **assurance reviewer** consistently.

## Out of scope
- No new citations or literature section unless a terminology change unexpectedly requires one.

- No title change in this pass; _justified_ remains explicitly stipulated as security-and-assurance justification. A title change would be a separate framing decision.

- No changes to empirical data, Study A, benchmark items, codebooks, or analysis scripts.

## Verification
1. Search for residual overloaded phrases: _authority status/effect/family_, _accountable bearer_, _trace fails_, _model executes_, _preserves priority among system/developer/user/tool/retrieved/memory/policy_, and generic _tool call_ where stage matters.

2. Verify every use of **supported/not supported/indeterminate** and **supported/defeated/unevaluable** occurs at the declared level.

3. Run the strict house-style checker and `git diff --check`.

4. Build with XeLaTeX/Biber and inspect warning logs.

5. Visually inspect the revised first figure, claim-pattern section, two dense evidence tables, comparative-test figure, and compositional section.
