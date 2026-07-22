# Delegation-assurance referee triage, 2026-07-22
<!-- SUMMARY: Triage of a major-revision referee review of delegation-assurance.tex; review verified accurate, one item promoted above the reviewer's own ordering, four decisions pending · status: awaiting decisions · updated: 2026-07-22 -->

**Verdict on the review: accurate and worth acting on.** Every factual claim I could
check held up, including one bibliographic error I confirmed against the source. The
review's own priority ordering is close to right, with one item I would promote.

## Verification

| Review claim | Status |
|---|---|
| No foundational authorization literature | **Confirmed, and total.** Zero hits for Abadi/Lampson/ABLP, SPKI/SDSI, Delegation Logic, SecPAL, UCON, XACML, trust management, or usage control across `sections-delegation/`, `references-local.bib`, and `references.bib` |
| Artifact not inspectable from the paper | **Confirmed.** §3 says "the repository" and `\path{assurance/delegation/}` but never names it. No URL, DOI, or commit anywhere in the source |
| Formalism is schematic, not a semantics | **Confirmed.** `τ_R` never defined; `G_R` "collects the... conditions" uninterpreted; `H_R(t)` gets one descriptive sentence; no syntax, typing judgments, propositions, or correspondence results |
| Alloula et al. author order reversed | **Confirmed against arXiv:2606.07874.** Source order is Alloula, Licini, **Batchkala, Goldfarb-Tarrant**; `references-local.bib` has Goldfarb-Tarrant before Batchkala |
| Tables 5 and 6 too dense | **Confirmed.** Both `\scriptsize`, three text columns, full-page `[p]` floats, pp. 22 and 24 |
| Statistical thresholds stipulated | **Confirmed.** All three frozen specs in §3.6 |
| Ten-bin ECE at n=30 | **Confirmed.** Three observations per bin at the stated minimum |
| Genealogy thin | **Confirmed.** Dams Safety NSW Board Meeting No. 5, item 14, plus a Canadian Heritage audit. The paper is already honest about this |
| Cornell Wex (LII) as legal sources | **Confirmed.** Three entries: agency, actual authority, principal |
| Initialisms unprotected in bib titles | **Partly.** Only three entries, all Brett's own self-citations |

**Inward-before-outward check:** nothing in the authorization literature appears anywhere
in the portfolio. Searched all `*.bbl` and `*.bib` for Abadi, Lampson, SPKI, SDSI, SecPAL,
XACML, usage control, trust management, delegation logic, Bertino, Sandhu. Zero hits. This
is a genuine outward search, not a rediscovery.

**Not verified:** the review's claim that these literatures "directly overlap standing,
joint grants, transition powers, temporal state, non-amplification, applicability,
priority, and licensing." That's plausible and is the reason the gap matters, but it
rests on the reviewer's characterisation, not on sources read here. Confirm it while
doing the reading, not before.

## Promote above the reviewer's ordering

**Link the artifact first.** The reviewer puts this third. It should be first because it
costs minutes and currently makes several central claims uncheckable. The repository is
already public (`github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation`,
HTTP 200) and the seven fixtures really are there, `01-valid-authorized-inadequate-record`
through `07-ineffective-override-valid-release`, alongside the three schemas, the view
policy, and the claim register. Nothing needs building. The paper just never says where to
look.

## Two additions the review missed

**The formal overclaim is internally inconsistent, not only external.** §3.5 already says
"the paper's formal contribution lies at the normative and representational layers," which
concedes most of what the reviewer argues. That sits against a title promising *typed
authorization semantics* and against §2's claim that existing work fails to "supply typed
semantics for whether a concrete operation or trajectory was authorized." The paper is
arguing with itself, which makes the rename the cheaper resolution.

**The record-soundness inconsistency is also internal.** The reviewer notes that
`Â(s_t) ⊆ A_R(t)` is point-in-time while authorization is history-dependent. Stronger than
that: §3.3 defines local authorization as `L_R(u_i | h_{i-1})`, explicitly conditioned on
prior history. So the paper's own semantics contradicts the static form of its soundness
subclaim. This is a defect to fix, not a modelling preference to weigh.

## Cheap and unambiguous

1. Artifact URL, release tag or commit hash, licence, and a construct-to-code map.
2. Alloula author order.
3. Brace `{AI}` in the three self-citation titles.
4. Split or landscape Tables 5 and 6; add a notation table.
5. Title: *Comparative Evaluation* to *Comparative Evaluation Designs*. The paper reports
   designs and analyzers and says plainly it has no target-study outcomes.
6. Fix `Â(s_t) ⊆ A_R(t)` to a history-indexed comparison.
7. Stray leading tab in the Table 6 "Automated-evaluator assessment" row.

## Real work

**The literature section.** This is the item that produces a reject rather than a revise at
any security or formal-methods venue, and it's the largest genuine task. Source-grounding
risk is high here: these are exactly the sources a model will confabulate confidently.
Every entry needs the primary text read and recorded in `notes/source-verification.md`
before it's cited. The reviewer's proposed narrower novelty claim is better than the
current one and should be adopted once the reading is done, not before.

**The statistical specifications.** The ECE threshold is the weakest link and should go
regardless. Calibration intercept and slope, proper scores as primary, bootstrap intervals
clustered by trace family. The reviewer-cluster analysis needs a crossed estimator or a
cross-classified model rather than the larger of two one-way standard errors, and the
design has to say whether reviewers are crossed with condition. The margins and minimum
counts need power simulations or explicit demotion to provisional.

## Decisions needed

**A. Meta-model or full semantics.** Renaming costs minutes and resolves the internal
inconsistency above. Building the formal core (grammar, typing judgments, denotational
preorder for non-amplification, correspondence and non-amplification-preservation
propositions) is weeks and changes what venue the paper is for. Recommend renaming now and
treating the formal core as a separate paper.

**B. Venue.** The reviewer's judgment is that the paper is close for a workshop or
interdisciplinary conceptual venue and would likely be rejected at a security or
formal-methods venue. `PORTFOLIO.md`'s venue-decision gate requires a completed record
before target-specific work, and this review is the strongest available input to it. The
literature gap matters much more at a security venue than at a conceptual one, so B
partly determines how much of the literature work is mandatory.

**C. Content interpretation as a fifth field.** The status/standing/priority/licensing
decomposition doesn't cover determining what operation, object, recipient, interval, and
conditions an occurrence expresses. The paper currently distributes this across `p_i`,
scope fields, and the adversarial-pragmatics companion. Either add the field or state
explicitly that the four presuppose a separately represented interpretation step. Adding
it is the more honest option and touches §1, §2, §3, and Table 6.

**D. Institutional worked case.** The reviewer wants a case with conflicting sources, a
disputed amendment, reviewer disagreement over ineffective versus voidable, a complete
trace, and an unresolved conclusion. The framework already names those states in §3;
what's missing is an instance. Fixture 07 (ineffective override, valid release) is the
closest existing material and could seed it.

## Deferred

- Reducing the manuscript by 15--20%. Real, but do it after A and the literature section
  settle, since both change what's in the paper.
- *Transition competence* as the primary term over *authorization standing*: reasonable,
  but §1 already introduces both and explicitly distinguishes standing from locus standi.
- *Oracle-free evaluator view* for *reference-free trace*: the reviewer is right that the
  current term is misleading, but the schema filename would need renaming with it.
