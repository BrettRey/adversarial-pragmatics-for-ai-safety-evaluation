# The formal core: what to build, and why the earlier advice changed twice
<!-- SUMMARY: Decision memo on DA's formal contribution for JCS; recommends one proposition plus a comparative idiom table, both small, on the SecPAL precedent; supersedes two earlier recommendations · status: awaiting Brett · updated: 2026-08-08 -->

Task #4 asks what "strengthening the formal core" means for a JCS submission.
It is a design decision, so this is a memo, not an edit. Nothing in the
manuscript has been changed on this point.

## Why the advice moved twice in one day

**First recommendation (from the venue corpus): demonstration, not
formalization.** Grounded in Nguyen et al. (2026) and Abdunabi et al. (2025),
both JCS papers that present a framework validated by a worked case rather than a
theorem. Both are real precedents and both are cited in
`submission/venue-decision-2026-08-08.md`.

**Second (after reading the board): still demonstration, more firmly.** The
editorial board is heavily formal-methods, so a half-built formalization put in
front of Millen, Koutsos, Zhang, or Bichhawat would be worse than an honest
meta-model.

**Third, and current (after reading SecPAL): both, small.** The two applied
framework papers are the wrong comparison class. SecPAL is the right one: same
venue, same subject, and the paper this manuscript's title invites comparison
with. Its bar was four body theorems, seventeen appendix lemmas with all proofs,
twelve comparative idiom subsections, and a described prototype ~-- with **no
experiments whatsoever** ("Although system implementation is not the subject of
this paper").

So the venue supports a paper with no experiments. It does not support one with
no formal results, and §3.5's disclaimer that the contribution is "a meta-model
at the normative and representational layers, not a complete authorization
language" will be read directly against the paper that *is* the complete
authorization language.

## Recommendation: two pieces, neither large

### 1. One proposition, in SecPAL's own shape

SecPAL's core structural results (Prop. 3.3–3.6) are short statements about a
three-rule system; 3.6 is a single line doing heavy work. A meta-model can hit
that target.

**The proposition to prove is the one the priority sweep identified as the
differentiator against the closest current competitor.** Ibrahim & Li
(arXiv:2606.03518) have already published a compositional delegation operator
with soundness proofs, so the manuscript cannot claim that ground. What it can
claim is that their formalism, having a single relational graph, cannot express
the separation this paper is built on: the recorded relation simply *is* the
authorization for them, whereas here \(A_R(t)\) and \(\widehat A(s_t)\) are
distinct types and record-soundness \(\widehat A(s_t) \subseteq A_R(t)\) is a
claim requiring separate evidence.

A separation result of roughly this shape:

> No formalism representing authorization by a single relation over recorded
> state can distinguish (i) an action authorized under \(R\) whose record
> misstates its basis, from (ii) an action unauthorized under \(R\) whose record
> is complete and internally consistent. Distinguishing them requires two
> relations and a soundness condition between them.

That is the paper's claim (A) turned into a statement with a proof obligation.
It is provable at the scale of one page, it is exactly what the fixtures already
demonstrate operationally, and it converts the weakest-looking claim into the
formal core. **Claim (A) is weak against 1993 and strong against 2026, and this
proposition is where that inversion pays.**

### 2. A comparative idiom table, from fixtures that already exist

SecPAL §6 is twelve named idiom subsections, each set against named competitors,
with a specific claim about which prior language cannot express it. That is this
venue's recognized substitute for an evaluation section and it costs no
experiments.

The seven existing fixtures already encode level separations. Reorganizing them
into that form is presentation work, not new research, and it answers the
"synthetic fixtures" objection by changing what the fixtures are *for*: not
evidence about a population, but demonstrations of expressiveness, which is
precisely how SecPAL uses its idioms.

Candidate rows, each with a named formalism that cannot express it:

| Idiom | Cannot be expressed by |
|---|---|
| Valid grant, misstating record | Ibrahim & Li (single graph) |
| Complete record, invalid grant | Ibrahim & Li; XACML (no record requirement) |
| Status held without recognition | SecPAL (principals are keys); ABLP (uninterpreted request) |
| Recognition without status | as above |
| Regime overrides a user-conferred grant | XACML combining algorithms (no standing layer) |
| Non-delegable limit with principal-only override | SPKI (delegation bit is binary) |
| Cumulative condition over a trajectory | SecPAL (stateless by explicit assumption); ABLP; Delegation Logic |

The last row is honest only if it credits usage control, which *can* express
cumulative conditions. That is a virtue: a table that concedes a row is more
credible than one that wins them all.

## What NOT to do

- **Do not build a grammar with typing judgments and correspondence results.** It is months of work, it invites direct comparison with SecPAL on SecPAL's own ground, and the board contains people who will see immediately what a partial version is missing.
- **Do not retitle to something vaguer to escape the problem.** The title question is the same decision as this one, and vagueness costs more than it saves at a venue whose readers are precise about these words. Either the paper carries a formal result and keeps *Typed Authorization Semantics*, or it drops that phrase and presents as an applied assurance framework measured against Nguyen and Abdunabi instead.
- **Do not add a real-world case study *instead* of the proposition.** It answers a question this venue is not primarily asking. SecPAL had no experiments and was fine.

## The coupling to state plainly

Title and formal core are one decision:

- **Keep *Typed Authorization Semantics*** → the SecPAL comparison class → one proposition is required, and the idiom table is the demonstration.
- **Drop it for an applied-framework title** → the Nguyen/Abdunabi class → a worked real case is required, and the proposition becomes optional.

The first is recommended. It is less total work, it uses material that already
exists, and it is the only one of the two that answers the §3.5 disclaimer
instead of conceding it.

## Status

Not started. Requires Brett's call, and that call is downstream of the larger
direction question recorded in `claim-disposition.md`, on which the paper is
currently held.
