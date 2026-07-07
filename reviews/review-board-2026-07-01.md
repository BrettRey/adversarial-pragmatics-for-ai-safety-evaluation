# Review Board Synthesis: 2026-07-01

Second simulated named-reviewer round, run against the submitted arXiv version
(submit/7776593, 2026-07-01; 15-page main + 9-page supplement). The names
identify research profiles to emulate, not participation or endorsement.
Reviewers ran as independent subagents; none saw the 2026-06-26 round or each
other's reviews. Unlike the June round, reviewers had access to the full
artifact, and most findings below were verified directly against
`benchmark/items/seed-items.csv`, `benchmark/rubrics/*.md`,
`benchmark/results/local-pilot-20260630-185417/` (including
`adjudication_responses.csv` and the judge confusion matrices), and
`scripts/run_local_pilot.py` / `run_llm_judge_validation.py`.

## Board

- Percy Liang persona: benchmark architecture and transparency.
- Eric Wallace persona: instruction hierarchy and source authority.
- Kai Greshake persona: indirect prompt injection and app-level attack surfaces.
- Paul Roettger persona: refusal and over-refusal evaluation.
- Danqi Chen persona: LLM-as-judge validation.
- Aida Mostafazadeh Davani persona: annotator disagreement and uncertainty
  (carried the target-heterogeneity check).
- Chris Potts persona: pragmatics, quotation, and NLP bridge.
- Projectibility Reviewer (mandatory for HPC-adjacent papers).

## Verdicts

8/8 Revise & Resubmit. No Accept, no Reject. Every reviewer endorsed the
construct and the measurement architecture; every reviewer found the pilot's
evidentiary claims under-supported. Per the skill's ground rule, the board's
role is failure analysis, not worth-adjudication, but for the record the board
uniformly treated the line of work as worth pursuing (Greshake persona: "I want
this line of work to exist"; Liang persona: "sound and underappreciated").

## Consensus Strengths

- The core diagnosis (pass/fail labels collapse capability failure, policy
  ambiguity, instruction conflict, refusal status, and evaluator instability)
  is right and underserved; labels-as-inference-licenses is a useful framing.
- The strict-pair metric penalizes degenerate constant policies (always-refuse,
  always-comply, blanket-ignore); most published injection benchmarks can be
  gamed by blanket conservatism and this design can't (6 reviewers).
- Schema-first, pre-registered item design with validator enforcement, pinned
  environments, and a released pipeline: "better measurement hygiene than most
  benchmarks an order of magnitude larger" (Wallace persona).
- The refusal matrix and five-axis decomposition are the right architecture
  (4 reviewers).
- Honest scoping throughout (toy payloads, pipeline-not-psychometrics) was
  noted by nearly every reviewer.
- The judge's partial-upgrading confusion pattern is a genuine publishable
  finding about LLM judges (Potts, Liang personas).
- The artifact's auditability is what enabled the criticisms below; several
  reviewers noted this explicitly as a strength of the release discipline.

## Consensus Weaknesses

Ordered by breadth of agreement; all verified against the artifact.

1. **Judge-validity numbers are base-rate artifacts, reported in a form §5's
   own citation (Artstein & Poesio) says is misleading (7/8 reviewers).**
   Refusal outcome 98.1% vs constant-judge baseline 96.3% (52/54 rows
   `not_applicable`); task success 66.7% exactly equals the majority baseline;
   safety risk 72.2% is *below* its 79.6% baseline; policy compliance 88.9%
   conceals 3/7 recall on noncompliant rows, 1/4 on integrity, 1/4 on
   confidentiality, 0/11 on partials, 0/11 on elevated risk. The deterministic
   rule-aided pass caught 7/7 noncompliant rows, so on this data rule-aided
   checks dominate the judge for triage (Chen persona: the judge is currently
   "a negative result"). The abstract's "66.7% to 98.1%" box and §6's
   "strongest for refusal outcome and policy compliance" and "can support
   triage" claims are unsupported as written.
2. **Three undisclosed circularities (7/8).** (a) The judge (glm-4.7-flash) is
   one of the three evaluated models: 18/54 rows are self-judged. (b) The judge
   prompt includes the gold `expected_behavior` field
   (`run_llm_judge_validation.py`), so reported agreement is an upper bound on
   rubric-aided judging, not judging as deployed. (c) All 54 gold labels come
   from a single adjudicator (coder "BR") who authored the items, the expected
   behaviours, and the judge prompt. §7a discloses "one expert adjudicator" but
   not the author-as-gold circularity. The two-stage disagreement protocol,
   the paper's methodological centrepiece, has never processed a disagreement
   (Davani persona: "the design admits no variance to partition").
3. **Pre-registered vs adjudicated label drift occurred inside the pilot,
   unreported, which is the very thing §7.8's drift metric exists to catch
   (5/8).** AP-SEED-009 pre-registers `instruction_conflict`; the adjudicator
   assigned `capability_failure` (zero `instruction_conflict` labels exist in
   the CSV). All 18 items pre-specify `safety_risk_label = low`; the
   adjudicator used `not_applicable` on 43/54 rows.
4. **The refusal axis was never exercised and is partly miscoded (Roettger
   persona, supported by the marginals).** 52/54 rows `not_applicable`,
   including the three AP-SEED-018 rows where models output the protected
   token (under-refusal by the paper's own matrix) and a gemma3 AP-SEED-016
   row that is a refusal. The protocol file also conflates probe-type labels
   (item metadata) with refusal-outcome labels (response judgments) in its
   Required Judgments list. Over-refusal probes contain nothing harm-adjacent,
   so the trained-refusal phenomenon (XSTest-style) is untestable with these
   materials; toy in-context policies test constraint persistence, a different
   mechanism.
5. **The harness has one privilege level, so authority and surface metadata
   are narrated, not instantiated (Wallace + Greshake personas, the two domain
   experts).** `run_local_pilot.py` sends one flat string to `/api/generate`:
   no system role, no chat structure, no real tool channel. `tool_output`,
   `webpage_text`, `email_body` are cooperative narrations inside the user
   prompt. The taxonomy has no system/developer level. A model could pass
   every item and fail real system-vs-user conflicts, or vice versa.
   AP-SEED-015's "exfiltration" has no exfil sink; the "agent transcript"
   family contains only single-turn items.
6. **Pair minimality is claimed but not enforced (Liang, Potts personas).**
   Only P002 and P004 approach single-dimension control; P007–P009 vary
   several dimensions at once (P008 even changes phenomenon family), so
   strict-pair failures can't be attributed to the intended dimension. Most
   pairs couple a trivially easy variant with a hard one, so strict-pair
   accuracy largely reduces to hard-item accuracy. Item-level defects:
   AP-SEED-002's "Ignore the previous sentence" has no antecedent;
   AP-SEED-008's gold arguably misreads a report as a request (a model
   refusing BLUE there is the more careful reader and is scored a failure);
   AP-SEED-016's "secret" appears in the requester's own prompt.
7. **The aligned-subordinate contrast is claimed in §3.3 but absent from the
   artifact (Wallace persona).** Every untrusted-content item carries a
   conflicting directive; a blanket "never act on embedded content" rule
   passes them all, which is exactly the failure mode §3.3 warns against.
8. **Projectibility is operationalized as within-benchmark invariance, not
   inductive reach (Projectibility Reviewer).** No family or metric states
   what a score licenses you to predict (unseen items, realistic payloads,
   other models). The construct "adversarial pragmatics" is never given a
   predictive-increment target (it earns kind status if its scores predict
   deployment failures that aggregate pass rates miss). Fix is propagation,
   not reconception: one "a score here licenses..." sentence per family and
   metric; pre-register the pilot's family-level patterns as development-pass
   predictions.
9. **Contestable gold labels encode the author's pragmatic judgments as model
   failures (Greshake, Chen, Davani, Potts personas).** P005: resolving "the
   previous instruction" to a colour is a defensible most-recent-antecedent
   reading, and `noncompliant` is assigned with no policy text in the item
   (a clarification norm smuggled into the policy axis). P009 is labelled
   policy-boundary ambiguity but "never output ZETA-42" is maximally crisp.
   P006's forced choice ("direct instruction or quoted content") is a false
   dilemma (both, at different levels; the rubric never draws the
   type/token-in-context distinction).
10. **Withheld raw outputs and missing canary (Liang persona).** The 54 raw
    outputs are excluded with a circular justification; toy payloads from
    local models have no privacy rationale, and quantized local inference
    isn't bit-reproducible, so primary evidence may be unrecoverable. Items
    are on public GitHub; add a contamination canary before "ignore the
    previous instruction / output BLUE" patterns are memorized.
11. **Quotation machinery cited but not implemented (Potts persona).** §3.2
    promises speaker/source, commitment, and reproduction-permission
    annotation; the schema has none of these fields. Either implement or trim
    the citations. The taxonomy also mixes model-behaviour families (1–6)
    with measurement-hazard families (7–8), blurring model failure vs eval
    failure, the paper's own target confound.

Mechanical: §1 nests `\citep` inside author parentheses (doubled parens);
abstract lists "refusal outcome" where §2 lists "source sensitivity" and the
protocol actually has seven axes; verify `reynolds2026kindsProjectibilityProfiles`
resolves; only the `compact` judge-prompt variant was run though
`metadata_first` exists in the script (so §7.6's judge-prompt sensitivity is
defined, not exercised).

## Contradictions (preserved, not averaged)

- **What AP-SEED-016/018 measure:** Roettger persona reads 018's token output
  as under-refusal that should be coded as such; Greshake persona reads both
  items as same-principal self-conflict, measuring in-context constraint
  persistence rather than policy compliance. Both agree the coding is wrong;
  they disagree about the construct. This is a genuine criterion conflict of
  the kind the paper's own protocol is designed to record.
- **Role of the LLM judge:** Chen persona concludes the judge is a negative
  result and rule-aided checks should own triage; Liang and Davani personas
  ask for corrected reporting and a disjoint judge but stop short of
  demoting the judge. The revision has to pick a position.
- **Remedy for the flat-prompt harness:** Wallace persona wants real privilege
  channels crossed with the same contrasts; Greshake persona offers a cheaper
  alternative (relabel the field as `narrated_source` and make in-band scope
  explicit) alongside the rerun. Honest relabeling is the floor; the crossed
  design is the ceiling.

## Prioritized Revision List

1. **Fix the judge-validation reporting (cheap, urgent).** Per-class
   precision/recall, majority-class baselines and/or chance-corrected
   coefficients per label family, uncertainty at N=54. Rewrite the abstract's
   "66.7% to 98.1%" box, §6's "strongest for refusal outcome," and the triage
   claim (either demote the judge or scope triage to rule-aided checks).
2. **Disclose the three circularities (cheap, urgent).** Self-judging rows,
   rubric-in-prompt, author-as-sole-adjudicator, in §6, not just §7a. Where
   feasible, report own-model vs other-model judge accuracy separately.
3. **Re-adjudicate the 54 rows with at least one independent annotator.**
   Fix the refusal coding (018 under-refusal; 016), separate `probe_status`
   from `refusal_outcome`, and report the pre-registered-vs-adjudicated drift
   (009, safety-risk marginals) as a worked example of the protocol catching
   itself. This converts two embarrassments into evidence for the method.
4. **Item and scope repairs before scaling.** Pair-minimality audit
   (P007–P009), re-author or flag defective items (002, 008, 016), add
   aligned-subordinate items or retract the §3.3 sentence, relabel
   `application_surface` as narrated source or state in-band scope in §4,
   rename or restock the transcript family, add the canary, release raw
   outputs.
5. **State the projections.** One licensing sentence per family and per
   metric; pre-register the pilot's three stable/three failing family
   patterns as predictions for the 50–100-item development pass; give
   "adversarial pragmatics" its predictive-increment target. Also worth
   doing: the cheap convergent-validity experiment (same models on an
   XSTest/IFEval slice, show what multi-axis labels recover).

## Comparison with the 2026-06-26 round

The June board asked for operationalized metrics, a refusal matrix, app-shaped
items, annotator metadata, and an inclusion test. The July version *defines*
all of these, and this round confirms the definitions are good. What this
round shows is that the pilot doesn't yet *exercise* them: the refusal matrix
exists but no refusal was coded; the drift metric exists but drift in the
pilot went unmeasured; the annotator-metadata fields exist but are absent from
the adjudication CSV; the disagreement protocol exists but n=1 makes
disagreement impossible. June's "Remaining Risks" flagged exactly this ("needs
development-pass results before it is submission-ready as an empirical
benchmark paper"); that risk materialized.

## Self-check

Convergence this round is strong (8/8 R&R, same top findings), which normally
warrants suspicion of role-stereotyping. Two mitigations: the biggest findings
are arithmetic recomputed independently from released CSVs by at least three
reviewers (base rates, per-class recall), not matters of taste; and the
contradictions section shows genuine divergence where judgment is involved.
One caution stands: all eight reviews come from the same underlying model, so
the shared instinct to check the confusion matrices is correlated, and a real
board would show more variance in what it bothered to verify. Do not read
"8/8" as field consensus; read it as "the released artifact makes these
specific problems checkable, and they check out as real."

## Note on timing

The paper is in arXiv moderation (submit/7776593). Items 1–2 of the revision
list (reporting fixes and disclosures) are hours of work and change no data;
if arXiv still allows replacing the submission before announcement, doing so
would prevent v1 from carrying the base-rate-artifact claims. Items 3–5 are
v2/development-pass work.
