# Venue Decision Record: Delegation Assurance
<!-- SUMMARY: Venue analysis for delegation-assurance.tex; M&M proposed primary, JCS the target if the authorization-literature work happens; awaiting Brett's approval · status: proposed · updated: 2026-07-22 -->

## Record

- Project: `papers/development/adversarial-pragmatics-for-ai-safety-evaluation/`
- Manuscript title: *Delegation Assurance for AI Systems: Typed Authorization Semantics and Comparative Evaluation*
- Extent: 36 pp., ~11,800 words excluding bibliography
- Proposed venue: **Minds and Machines** (Springer), research article
- Contingent alternative: **Journal of Computer Security** (SAGE) if the authorization-literature work is done
- Venue URLs checked: `link.springer.com/journal/11023/aims-and-scope`, `.../submission-guidelines`, `.../how-to-publish-with-us`; `journals.sagepub.com/home/jcu`, `journals.sagepub.com/author-instructions/JCU`
- Date checked: 2026-07-22
- Decision owner: Brett
- Assisting model: Claude Opus 4.8, two background sweeps of 28 journals
- Recommendation status: **approved by Brett, 2026-07-22**
- Final decision: **submit to Minds and Machines, after the three prerequisites below**

Brett's reasoning, recorded because it corrects the agent's initial lean toward JCS: the
paper has no threat model, no attacks, no defences, and no security evaluation, so it is
not a security paper. JCS hosts formal access-control modelling with proofs; joining that
venue topically while missing its methodological norm would repeat the
topic-match-over-reader-match error the outcomes ledger documents five times.

Constraint fixed by Brett on 2026-07-22: **journals only, no conferences** (no conference funding). This removes SaTML, AIES, FAccT, NeurIPS D&B, CCS, S&P, and USENIX from consideration entirely.

## Journal-Reader Contract

Revised 2026-07-22 after reading the recent M&M corpus. Positioned against Rashid (2026):

> Rashid has shown when a model's output crosses from information into executable intervention,
> and asks what authorization that executable authority then requires. This manuscript answers
> that question for readers of *Minds and Machines*: authorization is regime-relative and
> trajectory-scoped, so a complete and internally consistent trace of a machine action is
> compatible with that action being unauthorized, a valid authorization can leave no trace at
> all, and per-action authorization does not compose into authorization of the sequence.

Three things this gains over the earlier draft contract. It names a specific interlocutor in the
venue rather than a general debate. It states the paper's answer as an answer to a question the
venue has already published as open. And the third clause is the trajectory result, which is the
part no one in this M&M conversation currently has.

Superseded draft, retained for the record: "…changes the debate about what an AI audit record
establishes… by supplying the typed vocabulary that keeps auditability and authorization apart."
Still true, and it remains the referee's own view of the paper's best contribution ("not a new
access-control mechanism… a discipline for keeping unlike claims apart"), but it names no
interlocutor and so reads as thread-opening.

- [ ] The debate is visible in the title, abstract, and first two pages. **FAILS NOW.** §1 opens on prompt injection, jailbreaks, tool misuse, and memory poisoning, which states the security field's problem in the security field's terms, then detours into the Dams Safety NSW genealogy. Page one must be rewritten before submission.
- [x] The contribution is journal-local, not only topically adjacent. Philosophy of computer science; M&M's editorial focus list names "Philosophy of Computer Science," "Knowledge and Its Representation," and "Ethics and Governance of Artificial Intelligence."
- [ ] The expected reader can tell why the paper belongs here without a cover letter. Depends on the page-one rewrite.
- [ ] Reader's vocabulary split not yet decided. Run `.house-style/check-terms.py`. Provisional: for M&M, *normative*, *warrant*, *defeasible*, *validity* are free; *standing*, *transition competence*, *licensing*, *projectibility*, *trajectory authorization* are earned. For JCS the split inverts on several of these.

## Fit Evidence

Minds and Machines:

- Scope (verbatim): "a philosophy journal that aims to provide a forum to publish innovative, well-reasoned, scientifically grounded articles that provide conceptual analyses on topics at the intersection between cognitive philosophy, logic, epistemology, ethics and computer and data science."
- Article types: "Research and review articles; Topical collections; Critical responses; Commentaries (up to 4000)." Double-blind.
- **No length limit** for research articles. The only stated cap is the 4,000-word commentary limit. This matters: the referee wants a literature section *added*.
- "Manuscripts with mathematical content can also be submitted in LaTeX."
- AI policy: Springer Nature disclosure model, verified verbatim. Compatible, provided disclosure sits in the manuscript body and not only in a thanks-note. The current `\thanks{}` disclosure needs moving or duplicating into the body.
- APC £2490 / $3390 / €2790, **subscription route free**.
- Median first decision: 45 days.

### Corrected fit evidence, 2026-07-22

Eight open-access M&M papers downloaded to the central literature archive
(`literature/*_MM.pdf`). Two read directly; the rest have verified abstracts.

**Rashid (2026), "From Recommender to Actor: The Normative Boundary When RAG Tools Become
Tool-Calling Agents," 10.1007/s11023-026-09782-z, M&M 36:30, 36 pp.** The ideal neighbour.
Rashid poses this paper's question and leaves it open (p. 3):

> "Once a model output can alter records, modify permissions, transmit messages, initiate
> transactions, or otherwise change external states, the question is no longer only whether the
> system is reliable or explainable. It is also whether the system has been granted a form of
> executable authority, and what kind of authorization, oversight, and answerability that
> authority requires."

His threshold account (causal efficacy, autonomy, irreversibility, moral salience) says *when*
an output becomes an intervention. Delegation Assurance says *under what conditions that
intervention was authorized*. His three governance heuristics (epistemic traceability,
operational reversibility, normative containment) and "bounded delegation structures" are
precisely what this paper supplies typed machinery for.

**Nguyen et al. (2026), "On Controllability in Agentic AI: A Survey," 10.1007/s11023-026-09783-y,
55 pp.** Already draws this paper's causal/normative distinction at survey level: "the technical
infrastructure of intervention (what we call causal controllability) and the normative conditions
under which intervention constitutes genuine oversight (normative controllability)", via Santoni
de Sio & van den Hoven (2018). §3.6 of the manuscript draws the same distinction independently,
through AttriGuard versus authorization, citing none of it.

Also relevant, abstracts verified: Fischli 2026 on autonomy interpretations (…09786-9); Pozzi
2026 on Meaningful Human Control as reason-responsiveness (…09762-3); Schmidt 2026 on
computational reliabilism and warrant from computational results (…09759-y); Bjerring 2025 on
algorithmic robustness via Nozick counterfactuals (…09734-z), which bears on the paper's
perturbation and placebo material; Buijsman 2026 on why accuracy alone is insufficient in a
socio-technical system (…09768-x); Ferrario 2025 on reliance and trust (…09754-9).

**Length confirmed empirically, not just from the absence of a stated cap:** Rashid runs 36 pp.
and Nguyen 55 pp. in this journal.

**The literature gap that matters at M&M is a different one from the referee's.** The referee
named ABLP, SPKI/SDSI, SecPAL, UCON, XACML. An M&M reviewer will instead expect Meaningful
Human Control (Santoni de Sio & van den Hoven 2018), effective human oversight (Sterz et al.
2024), accountability (Novelli et al. 2024), and Responsible AI (Dignum 2019). The manuscript
engages none of these. This reading list is far shorter and more tractable than the security
canon, and it is the one this venue requires.

Formalism precedent: Jia, Floridi, Tohmé & Messina (2026), 10.1007/s11023-026-09791-y, a
proof-carrying paper.

Editorial/reviewer fit:

- Plausible reviewer pool: philosophers of computer science and AI governance scholars. They will not know the ABLP/SPKI/SecPAL canon, which is why the missing-literature defect costs less here than anywhere else.
- Reviewer pool mismatch risk: the same reviewers will not be able to check the formalism against the authorization literature either, so a favourable decision here does not retire that defect.

## Alternatives Considered

| Venue | Why plausible | Why not chosen now | Fallback status |
|---|---|---|---|
| **Journal of Computer Security** (SAGE) | Scope clause is written for this paper: "also provides a forum for ideas about the meaning and implications of security and privacy." Publishes SoK and proof-only formal papers with no experiments. No page ceiling, no fees. SAGE AI policy is the most forgiving found: submissions "will not be rejected solely because of the disclosed use of GenAI tools." Real authorization neighbours (Nguyen et al. 2026 ABAC conformance; Abdunabi et al. 2025 authorization framework; Lanckriet et al. 2026 SoK, all Crossref-verified) | This is precisely the readership that owns ABLP, SPKI/SDSI, SecPAL, UCON, and XACML. Submitting before that reading is done invites the rejection the referee predicted | **Primary target if the literature section and formal core get built.** Highest ceiling of any venue found |
| **AI Magazine** (AAAI/Wiley) | Article type is literally "conceptual analyses." Fully OA at zero cost. Live 2025–26 agentic-AI conversation to join: Navaie on privacy engineering for agentic AI (10.1002/aaai.70036), Mitchell on evaluating cognitive capabilities (10.1002/aaai.70061), both verified | 6,000–9,000 words against 11,800, and "expository text without complex equations or formulas." That guts the formalism. It would be a different, shorter paper | Viable only as a deliberate short conceptual spin-off |
| **Journal of Responsible Technology** (Elsevier) | Best single neighbour in either sweep: Pittman & Schaefer (2025), "Toward a responsible and ethical authorization to operate," 10.1016/j.jrt.2025.100130, verified | Full-length cap 5,000–10,000 words *including* references, against 11,800 before the referee's additions. Gold OA USD 1,850 | Rejected on length |
| **Artificial Intelligence and Law** (Springer) | Scope names deontic notions, normative modalities, normative systems, automated intelligent legal agents, and "evaluation and auditing techniques for legal AI systems." No length limit | Six-day median to first decision reads as a high desk-reject rate. The paper is not legal AI: it uses agency law as analogy and H.R. 7390 as a case, but does not model legal reasoning. Crossref returns zero 2025+ delegation/authority articles | Weak third |
| **AI and Ethics** (Springer) | Densest cluster of near neighbours in the governance sweep | Hard in-scope gate: "Does my paper make a claim about what is right, fair, harmful, or just… and defend it?" This paper is normative in the deontic sense, not the moral sense. Likely desk reject without a dedicated ethics section | Rejected on scope gate |
| **Computers & Security** (Elsevier) | Obvious topical home | **Disqualified by written policy**: "items directed to the security of AI/ML systems themselves… are out of scope of the journal" | Out |
| **ACM TOPS / TIST / IEEE S&P mag** | Topically adjacent | TOPS bans surveys/tutorials and demands practical-significance argument; TIST's only non-empirical track is invitation-only; IEEE S&P "is not a research journal" and rejects papers "that lack results of experimental validation" | Out |
| **Internet Policy Review** | Diamond OA | **Disqualified**: "The use of generative AI to author articles is not permitted." Prohibition model, not disclosure | Out |
| **AI & Society** | Broad scope | LLM use "strongly discouraged" beyond grammar and translation; 10,000-word ceiling | Out |

## Risk Test

- **Strongest desk-rejection risk:** page one addresses a security readership at a philosophy journal. The editor reads three paragraphs about prompt injection and public-sector dam-safety audit plans and cannot see the philosophical question. Fixable, and must be fixed before submission.
- **Strongest reviewer-rejection risk:** the title promises *typed authorization semantics* and the paper supplies a schema. §3.5 already concedes this ("the paper's formal contribution lies at the normative and representational layers"), so the paper contradicts its own title. Renaming resolves it more cheaply than building the formal core.
- **~~Strongest "not motivated / no live problem" risk~~ — WITHDRAWN 2026-07-22 on evidence.** The sweep reported no 2025+ M&M article on agent authorization or delegation. That was a query artifact: its Crossref string bundled eight terms with `query.bibliographic`, which behaves as a relevance ranker and returned two items. Re-pulling the journal's full 2025+ output (86 articles, `filter=from-pub-date:2025-01-01,type:journal-article`, rows=200) shows a dense current conversation. The paper joins a thread rather than opening one. **This removes what I had called the strongest predictor of rejection.** See Fit Evidence, corrected.
- **Strongest "opinion piece / no evidence" risk:** genuinely no empirical results. Three programme designs, seven fixtures, two analyzers, and no target study. The artifact link is the answer to this and is currently absent from the paper.
- **Strongest "wrong literature / wrong methodology" risk:** the total absence of ABLP, SPKI/SDSI, Delegation Logic, SecPAL, UCON, and XACML. Low cost at M&M, fatal at JCS.

Resolution:

- [ ] Risks resolved in manuscript before package work. **Three prerequisites, none yet done.**
- [x] Risks accepted explicitly by Brett: the missing authorization literature is accepted as a
      lower-cost risk at M&M than at a security venue, on the ground that M&M reviewers do not
      own that canon. It is **not** retired by an M&M acceptance and remains a defect.
- [ ] Risks unresolved: proceed once the three prerequisites clear.

**Prerequisites before package work:**

1. ~~**Page one rewritten for a philosophy readership.**~~ **DONE 2026-07-22.** The security
   opening and the Dams Safety NSW detour are gone; the genealogy is now a footnote. §1 opens on
   Rashid's threshold, quotes his open question directly (p. 3), states that this paper answers
   it, then shows that meaningful human control, effective oversight, and accountability all
   specify conditions on *persons* and none on *authority*. The trajectory non-entailment result
   is now on page one rather than buried in §3.2. A new §2.3, "Human Control, Oversight, and
   Accountability," does the fuller engagement, and §2's title and framing paragraph were widened
   from agent security to the two literatures. Build clean, no undefined citations, style checker
   clean, 36 pp. to 37 pp.

   *Deviation from plan:* I did not bring H.R. 7390 forward. Leading with Rashid is the stronger
   move for this venue, because it names an interlocutor the journal has already published rather
   than a legislative case the readership has no stake in. H.R. 7390 stays where it is.
2. **Rename resolved.** The title promises *typed authorization semantics*; §3.5 already
   concedes the formal contribution is at the normative and representational layers. The paper
   contradicts its own title, and an M&M reviewer will not need the security canon to see it.
3. **Artifact linked.** The repository is public and the seven fixtures are in it; the paper
   never names it. This is also the answer to the "no empirical results" objection.

## Evidence And Motivation Test

- [ ] Problem shown live, not merely imaginable. Partly. The procurement case is constructed; H.R. 7390 and the OpenAI long-horizon report are real, and both sit too late in the paper.
- [x] Conceptual paper names its evidential standard. §3.6 does this in detail, arguably in too much detail.
- [ ] Engages current recommended practice in the relevant field. **Fails** for authorization; passes for validity theory (Messick).
- [x] Documents a practical decision point. H.R. 7390 manufacturer safety cases.
- [ ] States which readership owns the main payoff. **Undecided, and this is the whole question.**

## Forecast (Prediction Ledger)

Base rate from `score.py`, 2026-07-22: 17 resolved events, no AI/CS venue class yet exists, so this would be the first. Nearest comparators: philosophy n=1 (desk survived, not accepted, 47 d); overall acceptance across resolved events is low (linguistics 2/10; corpus 0/3; cogsci 0/2). Standing pattern in the ledger: Brett's forecasts run well above Claude's on every pending event.

- Base rate for this venue class: none; new class `ai-cs`.
- P(survives desk / reaches external review): Brett ____ ; Claude 0.45 at M&M *after* the page-one rewrite, 0.2 without it.
- P(eventually accepted at this venue): Brett ____ ; Claude 0.2.
- Expected first decision by: submission date + 45 days (M&M median).

## Package Authorization

- [ ] Venue decision approved before target-specific package work begins. **NOT APPROVED.**
- [ ] Brett has approved the target or explicitly delegated the decision.
- [ ] Unresolved risks copied into the pre-submission checklist.
- [ ] Record linked from `DECISIONS.md` and `STATUS.md` if submission proceeds.

## Open portfolio conflict

*Minds and Machines* is already the stated target for two other Reynolds papers: Truth-Tracking Profiles (`papers/retarget/truth-tracking-profiles/`) and the AGI evaluation paper, whose `STATUS.md` lists venue choice as its next action and says M&M "remains a strong conceptual fit." Delegation Assurance and the AGI paper share the Messick/Kane validity apparatus and the projectibility vocabulary closely enough that a reviewer meeting both would fairly ask what is distinct.

**Now live, given the 2026-07-22 decision.** Delegation Assurance takes the M&M slot, so the
AGI evaluation paper and Truth-Tracking Profiles need their venue decisions made against that
fact rather than in isolation. The AGI paper's own referee review (triaged the same day at
`papers/retarget/agi-evaluation/reviews/referee-review-triage-2026-07-22.md`) raises the same
centre-of-gravity question from a different direction, so its venue call is not yet settled
either. Whoever picks that up should know M&M is spoken for by this paper.

This is Brett's to sequence. The ledger meta-lesson below argues against reflexively moving a
paper off its best-fit venue purely to avoid concurrency; it does not argue for putting three
overlapping papers in front of one editor.

Ledger meta-lesson (2026-07-12, Corpora/IJCL): choosing a weaker-fit venue to avoid a second concurrent submission at the best-fit venue cost a full submission cycle. Weigh the concurrency explicitly; do not default to avoidance.
