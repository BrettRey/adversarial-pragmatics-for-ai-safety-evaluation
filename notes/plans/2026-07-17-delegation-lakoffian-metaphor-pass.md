# Lakoffian metaphor pass: Delegation Assurance
## Objective
Revise the manuscript's conceptual-metaphor system without trying to purge metaphor from technical prose. The pass should keep established legal and security vocabulary, assign each spatial or structural metaphor a fixed job, and remove wording whose entailments conflict with the paper's evidentiary restraint.

The governing distinction will be:

> Authority is granted and exercised; authorization data is recorded and propagated; evidence supports or defeats claims.
## Assumptions tested
1. **This is a conceptual audit, not a request to add Lakoffian theory to the paper.** The project is an empirical/evaluative paper, so the revision should not add a metaphor-theory section or new Lakoff citations.

2. **Conventional legal and security metaphors are useful when disciplined.** _Grant_, _scope_, _within delegated authority_, _information flow_, _policy-enforcement point_, _trace_, and _chain of delegation_ do real analytic work and should remain.

3. **The problem is category slippage, not figurative language itself.** The current draft sometimes treats normative authority, its technical representation, and the evidence about it as one travelling substance.

4. **Graph and stack language is safe only when explicitly representational.** A recorded edge or tag can show what information was available to a gate; it cannot by itself create authority, establish internal representation, prove enforcement, or determine legal liability.


The strongest inversion is this: a technically propagated authorization tag can be perfectly recorded while the supposed grant is normatively invalid, and a valid grant can exist while the record is incomplete. The revision must keep those possibilities apart.
## Governing metaphor policy
| Target | Retain | Avoid or qualify |
| --- | --- | --- |
| Normative authority | principal, grant, standing to direct action, scope, condition, limit, revocation, exercise, exceed, within | authority as cargo, fluid, contamination, or a scalar quantity |
| Technical representation | authorization state, recorded classification, constraint field, typed graph, propagation, policy-enforcement point | saying a record, matrix, document, or model output itself grants authority |
| Evidence and assurance | claim, subclaim, support, defeat, indeterminate, trace, reconstruction | treating a trace as proof of internal representation, enforcement, or legal validity |
| System behaviour | recorded classification, observable uptake decision, proposed action, executed action | personifying an automated evaluator as an institutionally authorized policy-maker |
| Structure | layer/stack for evidence types; chain for serial delegation; graph for branching systems; path for one route through the graph | switching among these as though they described one literal universal pipeline |
## Planned revisions
### 1. Remove authority-as-payload language
- Replace claims that authority “arrives,” “moves,” “survives,” or is “executed” through language with claims about grants and constraints being communicated, recorded, re-expressed, classified, or misclassified.

- Rewrite the introductory core question as whether each classification, tool call, memory update, and evaluation claim was licensed under the relevant authority regime.

- Rewrite the language-mediated-authority opening so that transitions can alter the recorded basis for authorization without changing who actually had standing.

### 2. Separate normative force from technical records
- State that the delegation matrix represents the governing authority regime; it does not license or block actions by itself.

- In the compositional figure, change “constraint shown to hold” to “constraint recorded at gate” and “constraint not reconstructible” to “constraint absent at gate.”

- Revise the figure caption to say what the trace establishes and what it does not establish.

- Change delegation edges from things that “carry authority” to edges that represent recorded grants and constraints.

### 3. Replace scalar authority entailments
- Replace `monotonic authority` with a non-amplification formulation defined over a partial order of specified permissions and constraints.

- State that downstream components may introduce no permission unsupported by the current grants and may omit no still-applicable constraint.

- Replace “smaller authority” with narrower or better-delimited permitted action sets and localized governing constraints.

### 4. Separate causal influence from standing
- In the failure table, say that hostile content displaces a governing instruction in recorded classification or action selection, or is treated _as though_ it authorized action.

- Say that documents, policies, contracts, and memories can state constraints, provide evidence, or induce misclassification; merely entering context does not give them authority.

- Replace “trusted source” with “source with standing” where authorization, rather than technical trust, is the issue.

### 5. Remove institutional personification of automated judges
- Attribute operational force to the human or organizational decision rule that uses the label.

- Record who authorized that use, the evaluator's assigned scope, and the rule giving its output operational effect.

### 6. Discipline the structural diagrams
- Describe the introductory figure as an evidentiary-dependency schematic, not a universal linear execution pipeline.

- Rename its central stage from “Language-mediated authority” to “Language classification / authority record.”

- Define `tool gate` once as shorthand for a tool/action policy-enforcement point.

- Keep graph/path language in the compositional section because the representation is explicit, but use “propagate recorded fields” rather than “authority tags travel.”

### 7. Make smaller consistency repairs
- Prefer permissions over rights where no moral or legal right is intended.

- Replace “whose string wins” with “which instruction source controls.”

- Replace “external governance shell” with “external enforcement framework.”

- Replace “assurance burden” with “cost and complexity of assurance” unless an evidentiary burden is specifically meant.

- In the conclusion, replace collapsed boundaries and crossed gates with the relevant distinctions and recorded gate decisions.

## Out of scope
- No changes to Study A, the benchmark, empirical results, the AGI paper, or Evidentiary Assurance.

- No attempt to eliminate ordinary agentive shorthand such as a model proposing an action where the behaviour is observable.

- No new empirical or legal claims and no new citations unless a proposed terminology change unexpectedly requires one.

## Verification
1. Search for the risky collocations after editing: authority + _move/arrive/survive/contaminate/smaller/carry/travel_; matrix + _license/block_; judge + _own authority/policy_.

2. Run the strict house-style audit and `git diff --check`.

3. Build `delegation-assurance.pdf` with XeLaTeX/Biber and check citation/reference logs.

4. Inspect the revised introduction, failure table, comparative-test figure, implications, and compositional figure in the rendered PDF.

---
comments:
  c1:
    body: this all looks good. On top of this, notice that, in model output, there's
      a potential use vs mention issue. Not a metaphor issue, but possibly
      relevant
    by: user
    at: 2026-07-18T01:25:45.484Z
