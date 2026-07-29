# Venue Decision Record: Evidentiary Assurance
<!-- SUMMARY: proposes Computer Law & Security Review for Evidentiary Assurance, with a stop condition on engaging the reviewability literature CLOSED 2026-07-29; abstract still opens on a requirements landscape - status: approved, package work may begin - updated: 2026-07-29 -->

## Record

- [x] Project: `papers/development/adversarial-pragmatics-for-ai-safety-evaluation` (Evidentiary Assurance)
- [x] Manuscript title: *Evidentiary Assurance* (`evidentiary-assurance.tex`, 34 pp, ~14,780 body words excluding references)
- [x] Proposed venue: **Computer Law & Security Review** (Elsevier)
- [x] Article type / section: feature article
- [x] Venue URL / author instructions checked: `sciencedirect.com/journal/computer-law-and-security-review` guide for authors (via search snapshot; ScienceDirect returns 403 to direct fetching)
- [x] Date checked: 2026-07-24
- [x] Decision owner: Brett
- [x] Assisting agent/model: Claude Opus 5 (1M context)
- [x] Recommendation status: **approved** (Brett, 2026-07-24, pending the CLSR article check, which passed 2026-07-24)
- [x] Final decision: **submit to CLSR.** Both stop-condition requirements closed 2026-07-29; package work may begin.

Prior state: EA had no venue record at all. It has been through two external
review rounds against an unstated "AI-governance journal" target, and its §5
artifact statement already promises a DOI at publication. The revision has
therefore been shaped by a venue that was never chosen.

## Journal-Reader Contract

> This manuscript changes the **reviewability** debate for readers of *Computer
> Law & Security Review* by showing that record-keeping requirements settle what
> evidence exists without settling what that evidence warrants about whether an
> action was authorized, and by supplying a review procedure that keeps the
> historical question and the evidentiary one apart.

- [x] The debate/problem is visible in the first two pages **as of 2026-07-29**:
      the reviewability engagement now sits on the first page of body text and
      names Cobbe & Singh's position before departing from it. **The abstract
      still opens on a requirements landscape rather than a debate**, so this is
      closed for the body and open for the abstract. Worth a pass before
      submission.
- [x] The contribution is journal-local: it continues the reviewability
      programme at the point its authors leave open, rather than arriving from
      outside it.
- [x] The expected reader can tell why the paper belongs here without relying on
      a cover letter: achievable, because reviewability is a CLSR-native frame.
- [ ] Reader's vocabulary decided (free/earned). Provisional split for a
      law-and-technology readership:
  - **Free** (this reader owns them): accountability, auditability, oversight,
    provenance, recourse, impact assessment, audit evidence, rule of law,
    reviewability.
  - **Earned** (must be glossed at first use): projective claim, typed claim,
    bearer, verdict vector, `not_established`, applicability map, undercutting
    vs rebutting defeater, noncompensatory use, `J_B(z)` / `J_C(f)`.
  - The earned list is long. That length is itself the risk this record turns
    on.

## Fit Evidence

- [x] Current aims/scope checked 2026-07-24.
- [x] Length: submissions "normally between 6,000-15,000 words", longer "subject
      to negotiation with the Editor". EA is ~14,780 body words before
      references, so it sits at the top of the band and probably over it once
      references count. Negotiable, not disqualifying.
- [x] AI-use policy: **disclosure model.** Authors "must declare the use of
      generative AI in the manuscript preparation process upon submission."
      This matches the house `\aidisclosure{}` practice exactly. Not a
      prohibition-model venue.
- [x] Publishing route: both gold OA and subscription are offered, so there's no
      mandatory fee. Gold OA APC is reported at USD 3,760; the subscription
      route costs nothing and permits self-archiving after embargo.
- [x] At least three recent venue articles make the match concrete.

**The genre fit, confirmed against primary texts (2026-07-24).** Four recent
CLSR articles were retrieved and read in full (open-access self-archived copies;
ScienceDirect blocks automated retrieval even for hybrid-OA articles). CLSR
publishes across a spectrum, not one doctrinal mode:

- pure doctrinal with no apparatus (Sargeant 2026; Metikoš et al. 2026);
- law-plus-CS joint apparatus grounded in named real systems (Cabay, Vandamme &
  Debeir 2025, which imports an ML-auditing typology from outside law in
  precisely the way EA imports assurance-case and evidence-law vocabulary);
- CS-majority comparative apparatus with coded matrices and heatmaps
  (Rintamäki et al. 2026).

So "CLSR only wants doctrinal legal analysis" is wrong: two of four carry real
formal apparatus. **Length is also not the binding constraint** the earlier
draft of this record assumed. Two of the four run well past the stated
6,000-15,000 ceiling, so EA's ~14,780 words is unremarkable.

**Correction to an earlier claim in this record.** A previous version called the
Cobbe & Singh CLSR paper ("Reviewable Automated Decision-Making," 2020,
`10.1016/j.clsr.2020.105475`) the "decisive fit fact." That was too strong. It
establishes that CLSR has hosted this framework; it does not establish that
CLSR's current cohort is building on it. None of the four sampled 2025-26
papers cites either Cobbe & Singh 2020 or Cobbe, Lee & Singh 2021. Four papers
is a small, theme-selected sample, so this is a caution rather than a refutation,
but the fit case now rests on genre match, not on a citation chain.

Archived copies (central literature archive, SHA-256 in
`/tmp/claude-agent-output/clsr-profile.md`):
`cabay_vandamme_debeir_2025_looking-through-the-crack-clsr.pdf`,
`sargeant_2026_mind-the-gap-clsr.pdf`,
`rintamaki_etal_2026_impact-assessment-gdpr-vs-aiact-preprint.pdf`,
`metikos_2026_enabling-contestation-dissertation.pdf`.

Recent comparable venue articles or signals (CLSR 2025-2026; 221 works published
since 2025-01-01, of which 40 hit accountability, audit, evidence, oversight, or
automated-decision themes):

1. "Looking through the crack in the black box: A comparative case law benchmark
   for auditing AI-powered [systems]" (2025). Case-law-facing auditing, which is
   EA's contested-case setting.
2. "My AI, my code, my secret: Trade secrecy, informational transparency and
   meaningful litigant participation" (2025). What a record lets a party show in
   a dispute, which is EA's question in a different doctrinal register.
3. "Mind the gap: Securing algorithmic explainability for credit decisions
   beyond the UK GDPR" (2025).
4. "Impact assessment requirements in the GDPR vs the AI Act: Overlaps,
   divergence, and implications" (2026).

Method note, because a prior sweep in this portfolio produced a false negative:
Crossref's journal record for ISSN 0267-3649 indexes almost nothing after 2008,
and OpenAlex splits the journal into a legacy "Computer Law & Security Report"
source and the live journal under ISSNs 2212-473X / 2212-4748. Both the naive
Crossref query and the naive OpenAlex query returned **zero** 2025+ articles.
The 221 figure comes from OpenAlex source `S4394735566`, located by resolving a
known CLSR DOI rather than by searching the title. Any future sweep of this
journal that reports a thin recent record has probably hit the same artifact.

Editorial/reviewer fit:

- Likely desk screen: a law-and-technology editor asking whether this is legal
  analysis. CLSR wants "good quality legal analysis and new lines of legal
  thought or policy development that go beyond mere description."
- Plausible reviewer pool: the Cambridge Compliant and Accountable Systems
  group and its citers; EU AI Act and GDPR accountability scholars; algorithmic
  audit researchers.
- Reviewer pool mismatch risk: **real.** EA's formal core (verdict lattice,
  typed claims, executable fixtures) is not doctrinal legal analysis. A CLSR
  reviewer may read the apparatus as machinery imported from elsewhere rather
  than as a contribution to legal thought.

## Alternatives Considered

Rows marked (inherited) reuse verification done for the Delegation Assurance
record on 2026-07-22 and were not re-checked today.

| Venue | Why plausible | Why not chosen now | Fallback status |
|---|---|---|---|
| **ACM FAccT** | The actual home of the reviewability conversation EA extends; Cobbe, Lee & Singh 2021 is the paper EA is closest to | **Out on a standing constraint, settled by Brett 2026-07-24: journals only, no conferences, portfolio-wide.** No conference funding, and he won't present online. This is why the CLSR route matters: it's where the same authors published the same framework | Out |
| **Big Data & Society** (SAGE) | Broad accountability and governance readership, OA, no obvious length bar | Not verified today. Its readership skews social-scientific and empirical; EA is formal and normative | Unverified second |
| **Ethics and Information Technology** (Springer) | Long-standing home for normative analysis of computing | Not verified today. EA's normativity is deontic (authorization) rather than moral, the same mismatch that ruled out AI and Ethics | Unverified third |
| **Artificial Intelligence and Law** (Springer) | Scope names "evaluation and auditing techniques for legal AI systems"; no length limit (inherited) | EA doesn't model legal reasoning; it uses evidence law as a source of distinctions. Six-day median to first decision reads as a high desk-reject rate (inherited) | Weak |
| **AI and Ethics** (Springer) | Densest near-neighbour cluster in the governance sweep (inherited) | Hard in-scope gate: "Does my paper make a claim about what is right, fair, harmful, or just... and defend it?" EA is deontic, not moral (inherited) | Rejected on scope gate |
| **Journal of Responsible Technology** | Pittman & Schaefer (2025), "Toward a responsible and ethical authorization to operate," is a direct neighbour (inherited) | 5,000-10,000 words *including* references against EA's ~14,780 before references (inherited) | Rejected on length |
| **Minds and Machines** | Sibling paper's approved target | Taken by Delegation Assurance. Two Reynolds submissions from the same repo at one journal, on adjacent apparatus, invites the "what's distinct?" question the DA record already flags | Out |
| **AI & Society** | Broad scope (inherited) | 10,000-word ceiling; LLM use "strongly discouraged" beyond grammar and translation (inherited) | Out |
| **Internet Policy Review** | Diamond OA (inherited) | "The use of generative AI to author articles is not permitted." Prohibition model (inherited) | Out |

## Risk Test

- **Strongest desk-rejection risk:** "This is not legal analysis." EA supplies a
  formal review procedure and an executable artifact; CLSR publishes legal
  thought and policy development. The abstract currently leads with a
  requirements inventory and an executable artifact, neither of which reads as
  a legal contribution.
- **Strongest reviewer-rejection risk:** the ledger's recurring finding, that
  the apparatus substitutes terminology for analysis. The Journal of Social
  Ontology referees said exactly this about a sibling paper ("the paper
  substitutes terminology for analysis"). EA's earned-vocabulary list above is
  long, and every one of those terms has to visibly do work a plainer
  description couldn't.
- **Strongest "not motivated / no live problem" risk:** **This is the binding
  one.** EA cites Cobbe, Lee & Singh exactly once, in
  `sections-evidentiary/01-introduction.tex:11`, as background. Its nearest
  neighbour, in its own target venue, appears once in passing. More broadly, of
  47 cited sources only 11 are journal articles, spread roughly one per journal
  across psychometrics, statistics, management science, public administration,
  law, and AI ethics; the citation base is standards documents, statutes, and
  reports. A paper can be excellent and still read as joining no conversation.
- **Strongest "opinion piece / no evidence" risk:** moderate and honestly
  handled. EA states in its own abstract that "no reviewer has yet answered
  them, the procedure remains a research hypothesis rather than a validated
  instrument." That's the right disclosure, and a reviewer may still ask what
  the paper establishes.
- **Strongest "wrong literature / wrong methodology" risk:** high, and it's the
  same finding as the motivation risk.

Resolution:

- [ ] Risks resolved in manuscript before package work.
- [ ] Risks accepted explicitly by Brett.
- [x] **Both stop-condition requirements closed 2026-07-29.** Remaining risks are the ones no revision removes: the apparatus reading as terminology, and the paper's own disclosed non-validation.

### Stop condition

Two requirements, the second confirmed against primary texts on 2026-07-24 and
now the more important of the pair.

**1. Join a conversation. CLOSED 2026-07-29.** Page one should say that reviewability tells an
institution which records to keep and in what form, and that this leaves open
what a kept record warrants about whether the action was authorized, which is
what a contested case turns on. EA already contains that point; it isn't on
page one and isn't attached to anyone's position. EA cites Cobbe, Lee & Singh
once, in `sections-evidentiary/01-introduction.tex:11`, as background.

**2. Run the apparatus against one sustained, named, real case. CLOSED 2026-07-26** (Robodebt promoted to spine). This is the
sharper gap. In every apparatus-bearing paper in the CLSR sample, the typology
or matrix is cashed out against fully concrete, named, real systems or statutes
*from opening to conclusion*: EUIPO and BOIP's actual trademark search engines
against actual case law; the UK's actual DUAA reform against actual CJEU cases;
30 real jurisdictions' actual DPA guidance. None invents standalone symbolic
notation the way EA's Figure 1 does (`R`, `F_review`, ρ, `b`, `c`, `u`, `J_A`,
`J_B`, `J_C` are new coinages), and none leans on a hypothetical for its central
illustration. EA's throughline is a hypothetical procurement-assistant vignette,
with Robodebt and the Hinkle testimony appearing as passing illustrations.

The fix is available without new research: EA already has two real cases in
hand. Promote one, most plausibly Robodebt, from illustration to spine, and run
the four verdict vectors against it end to end. A reader then sees the apparatus
do work on a case they recognise, which is what the sampled papers all do.

This remains layer (a) in the ledger's diagnosis, presentation rather than
substance. The payoff exists and is buried in program frame.

## Evidence And Motivation Test

- [ ] The manuscript shows that the problem is live, not merely imaginable.
      Partly. Robodebt and the Hinkle testimony are real contested cases, but
      they arrive as illustrations rather than as the motivating problem.
- [x] If the paper is conceptual, the first two pages still name the evidential
      standard. EA does this well; node-specific evidential standards are
      explicit.
- [x] If the paper is methodological, it engages current recommended practice:
      NIST AI RMF, ISO/IEC/IEEE 15026-2, PCAOB AS 1105, EU AI Act.
- [x] If the paper is jurisdictional or institutional, it documents actual
      variation: Canada Evidence Act, PIPEDA, Robodebt (Australia), SOX §404 and
      PCAOB (US), EU AI Act. The comparative spread is a genuine strength and is
      currently undersold.
- [ ] If the paper is interdisciplinary, it states which readership owns the
      main payoff. Not yet stated.

## Forecast (Prediction Ledger)

- Base rate for this venue class: **none on file.** The ledger has classes for
  book, cogsci, corpus, linguistics, and philosophy. Law and technology is a new
  class, so there's no outside view specific to it. Portfolio-wide across 17
  resolved events: 6/17 (35%) desk survival, 2/17 (12%) eventual acceptance.
- P(survives desk / reaches external review): Brett to record. Claude Opus 5:
  **0.35** as the manuscript stands today, **0.55** if the stop condition is
  cleared first.
- P(eventually accepted at this venue): Brett to record. Claude Opus 5: **0.15**
  today, **0.3** after the stop condition.
- Expected first decision by: Brett to record once a submission date exists.

## Package Authorization

- [ ] Venue decision approved before target-specific package work begins.
- [ ] Brett has approved the target or explicitly delegated the decision.
- [ ] Unresolved risks copied into the pre-submission checklist.
- [ ] Record linked from `DECISIONS.md` and `STATUS.md` if submission proceeds.

Resolved 2026-07-24:

1. **Journals only, no conferences, portfolio-wide.** Brett's standing
   constraint, not a per-paper call: no conference funding, and he won't present
   online. FAccT is out, and so is every proceedings venue. Recorded in the
   `venue-selection` skill's standing lessons.
2. **CLSR approved in principle**, pending a read of recent CLSR articles to
   confirm the journal publishes work of this shape. That check is running.

Still open:

- Subscription route or gold OA at USD 3,760.
- The stop condition above, which is the real gate.

Decision summary for `DECISIONS.md`, to be added only if Brett approves:

```markdown
2026-07-24 - Venue decision: Computer Law & Security Review for Evidentiary Assurance. Owner: Brett, agent-assisted. Record: `submission/venue-decision-evidentiary-2026-07-24.md`. Reason: CLSR is the journal home of the reviewability framework EA extends (Cobbe & Singh 2020) and carries a live 2025-26 accountability conversation. Risks accepted: none; a stop condition on engaging that literature remains open.
```

## Stop condition closed, 2026-07-29

Acquired and read Cobbe & Singh's *CLSR* paper (green OA author copy, Cambridge
Apollo, archived with hash). Two things it supplies that the earlier draft of
this record only guessed at:

- Reviewability is derived from **administrative law**, where judicial review
  assesses the decision-making process as a whole rather than the decision
  alone. Robodebt is public-sector automated decision-making of exactly that
  kind, so EA's spine and the venue's own framework are about the same object.
  That was luck rather than design, and it makes the engagement much stronger.
- Cobbe & Singh state their own open problem: what record-keeping suits each
  step and what information is worth retaining. EA's question sits immediately
  after it, which lets EA position as continuing their programme rather than
  competing with it.

The rewrite also fixed a defect the stop condition hadn't named. EA argued
against explanation-focused approaches on its own account, then cited Cobbe &
Singh afterwards as background, when their section 2 is titled "Limits of
Explanations" and makes that argument. Re-deriving a cited author's argument and
then citing them for background is the signature of not engaging. The
explainability paragraph now takes their objection as read and states where EA
departs instead.

Placement: both the Robodebt opening and the reviewability engagement sit on the
first page of body text (PDF page 2; page 1 is title, abstract, keywords, and
the AI disclosure). EA builds clean at 34 pp with the new citation resolving.
