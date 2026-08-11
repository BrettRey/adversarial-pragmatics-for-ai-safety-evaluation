# Venue Decision Record: Delegation Assurance (retarget)
<!-- SUMMARY: Retarget of delegation-assurance.tex from Minds and Machines to Journal of Computer Security after M&M went to the AGI-evaluation paper; venue analysis stands but the paper itself is HELD pending Brett's direction call after the same-day canon audit and priority sweep · status: venue approved, PAPER HELD · updated: 2026-08-08 -->

**PAPER HELD, 2026-08-08, same day this record was written.** The venue analysis
below stands and JCS remains the right target *if the paper proceeds in
substantially its current form*. It may not. A canon audit and a priority sweep
run the same afternoon found the paper's core claim still open but the
surrounding ground taken within about six months, and three programmes arguing in
print that its central move is wrong. Brett's call is **hold and think**. Read
`notes/canon-audit/claim-disposition.md` before acting on anything in this record.
The prerequisites below are unchanged in substance but their scope depends on
which direction the paper takes.

Supersedes `venue-decision-2026-07-22.md`, whose Alternatives Considered, Fit
Evidence, and Risk Test sections remain valid and are the basis for this
decision rather than being redone. Only the target changes.

## Record

- Project: `papers/development/adversarial-pragmatics-for-ai-safety-evaluation/`
- Manuscript title: *Delegation Assurance for AI Systems: Typed Authorization Semantics and Comparative Evaluation*
- Extent: 39 pp., ~13,700 words excluding bibliography (up from 36 pp. / ~11,800 in July)
- Proposed venue: **Journal of Computer Security** (Sage, in partnership with IOS Press), research article
- ISSN: 0926-227X (print), 1875-8924 (online)
- Venue URLs checked: `journals.sagepub.com/home/jcu`, `journals.sagepub.com/author-instructions/JCU`
- Date checked: 2026-08-08
- Decision owner: Brett
- Assisting model: Claude Opus 5
- Recommendation status: **approved by Brett, 2026-08-08**
- Final decision: **submit to Journal of Computer Security, after the two prerequisites below**

### Why the venue changed

Not a fit failure. M&M was chosen on 2026-07-22 and the paper was reworked for
it. The change is a portfolio-sequencing outcome: three Reynolds papers pointed
at M&M (this one, Truth-Tracking Profiles, and the AGI-evaluation paper), and
`PORTFOLIO.md`'s venue-coordination flag recorded that they could not all be
under review there at once. Brett's call on 2026-08-08 gives the M&M slot to the
AGI-evaluation paper. Truth-Tracking Profiles is being retargeted separately.

JCS is not a new candidate. The July record already named it "primary target if
the literature section and formal core get built" and rated it "highest ceiling
of any venue found." What blocked it then was unstarted work, not fit. Brett has
now chosen to commit to that work rather than run a fresh sweep or cut the paper
down for a length-capped venue.

## Journal-Reader Contract

> Access-control research has formalized who may perform which operation, and
> agent-security research has catalogued how a language model can be induced to
> act outside its permissions. This manuscript shows readers of the *Journal of
> Computer Security* that neither line reaches the authorization question posed
> by language-mediated delegation: a complete and internally consistent trace of
> a machine action is compatible with that action being unauthorized, a valid
> authorization can leave no trace at all, and per-action authorization does not
> compose into authorization of the sequence.

The third clause is the load-bearing one for this venue. Non-composition of
step-local authorization into trajectory authorization is a claim about
authorization semantics, stated in terms a JCS reader owns, and it is the part
of the paper that the per-call enforcement mechanisms this readership builds do
not currently address.

- [ ] The debate is visible in the title, abstract, and first two pages. **FAILS NOW, and for the opposite reason it failed in July.** See the page-one finding below.
- [x] The contribution is journal-local, not only topically adjacent. Authorization semantics is JCS's own subject matter, and SecPAL was published in this journal.
- [ ] The expected reader can tell why the paper belongs here without a cover letter. Depends on the page-one rework.
- [ ] Reader's vocabulary split not yet decided. Run `.house-style/check-terms.py`. Provisional, and it inverts the M&M split: for JCS *delegation*, *authorization*, *principal*, *least privilege*, *policy decision point*, *confused deputy*, *usage control* are free; *projectibility*, *warrant*, *defeasible*, *standing*, *transition competence*, *bearer* are earned. The July record predicted this inversion and it holds.

### Page-one finding (new, and the most actionable item here)

The July decision's first prerequisite was "rewrite page one for a philosophy
readership," and it was completed on 2026-07-22 in commit `8da2df6`, "Target
Minds and Machines and reaim Delegation Assurance's opening." That commit
removed a security-framed opening and replaced it with the current one.

The removed opening (recoverable at `git show 777aea0:sections-delegation/01-introduction.tex`)
begins:

> "AI security work has made real progress by identifying prompt injection,
> jailbreaks, tool misuse, data exfiltration, memory poisoning, and scaffold
> failures. That work remains necessary. But tool-using AI systems also raise a
> question that isn't captured by asking whether a prompt was malicious or an
> output was unsafe."

That is close to the page one JCS wants. The current opening leads with Rashid
(2026), an article in *Minds and Machines*, and spends four paragraphs
contrasting meaningful human control, effective oversight, and accountability.
A JCS desk editor reading that will not see a security paper.

**This is not a revert.** The work done between `777aea0` and now is good and
stays: the `typed` definition in §1, the two withdrawn overclaims, and §2.3's
engagement with Santoni de Sio & van den Hoven, Sterz et al., Novelli et al.,
and Nguyen et al. The change is positional. The AI-governance material moves
from page-one framing to a related-work subsection where it belongs for this
readership, and the security framing returns to the front. Expect the reverse of
July's edit, not an undo of it.

## Fit Evidence

Verified 2026-08-08 against the current author instructions:

- Scope (verbatim): "presents research and development results of lasting significance in the theory, design, implementation, analysis, and application of secure computer systems," and it "additionally serves as a forum for ideas about the meaning and implications of security and privacy, particularly those with important consequences for the technical community." That second clause is the one written for this paper.
- Article types: research articles; review articles. Special-issue proposals are tied to major conferences (ESORICS, DBSEC, CSF, SCN); individual article topic proposals are rejected. **Not relevant to us**: we submit a research article directly.
- **No stated word or page limit.** Confirmed on both the homepage and the author instructions. At 39 pp. and growing, this is the single most important structural fact about the venue.
- **No submission or publication fees.** Optional OA via Sage Choice or an institutional agreement; the subscription route is free.
- Peer review: **single-anonymized** (reviewer concealed from author, not the reverse). This is a change from M&M's double-blind and *reduces* packaging work: no author-anonymization pass is needed.
- Preprints: explicitly permitted. Enter the preprint DOI at submission, do not update the preprint during review, and link from preprint to published version on acceptance. Compatible with the held `delegation-assurance-r1` tag plan.
- LaTeX accepted, templates on the Sage Journal Author Gateway. Word is "preferred" but LaTeX is accepted.
- **Reference style: Sage Vancouver.** A numeric style, and a genuine cost: the house setup is biblatex/APA. This is a mechanical conversion, but it is not free and it touches every citation in a 39-page paper. Flagged for the submission gate, not for now.
- AI policy: disclosure model, and **the July quote is confirmed verbatim against the current live page**, `www.sagepub.com/generative-AI-tools-policy-msg` (fetched 2026-08-08 by curl; WebFetch is Cloudflare-blocked on Sage). Exact text: "While submissions will not be rejected solely because of the disclosed use of GenAI tools, if the editor becomes aware that GenAI was inappropriately used in the preparation of a submission without disclosure, the editor reserves the right to reject the submission at any time during the publishing process." The word *solely* is present. Compatible with the house `\aidisclosure{}` macro on page 1, and the disclosure must be made at submission.
  - Sage's nine prohibited uses include "fabricated references or falsified claims," "generation of incorrect text or content," and "plagiarism or inappropriate attribution to prior sources." **Directly relevant to prerequisite 1:** the engagement section will make comparative claims about six formalisms none of which anyone here has read yet. Under this policy an unread-source citation error is not merely a scholarly lapse but a disclosed-AI-use integrity issue at a venue that reserves rejection at any stage. The archive is marked do-not-cite until read for exactly this reason (`notes/source-verification.md`).
  - Caution recorded: Sage maintains at least two regionally-branded policy pages that are not word-for-word identical. A Wayback snapshot of `uk.sagepub.com/en-gb/asi/artificial-intelligence-policy` (2026-01-17) drops "solely" and lists only three prohibited uses. The `www.sagepub.com` page above is the fuller and more current text and is the one relied on.

### Recent output: the venue is active

**33 journal articles from 2025-01-01 to 2026-08-08** (~19 months, ~21/year).
Verified against the standing "a quiet journal is usually a broken query"
lesson, and it does not apply here. Method, recorded so the covered space is
inspectable: a known recent JCS DOI (`10.1177/0926227x251409398`) was resolved
first through both Crossref and OpenAlex to confirm which source record it
lands in, and only then were counts queried against that record.

- Crossref: `api.crossref.org/journals/0926-227X/works?filter=from-pub-date:2025-01-01,until-pub-date:2026-08-08` → 33, each inspected individually.
- OpenAlex: `api.openalex.org/works?filter=primary_location.source.id:S106992369,from_publication_date:2025-01-01,to_publication_date:2026-08-08` → 30.
- `api.openalex.org/sources?filter=issn:0926-227X` → exactly one source record, so no ISSN split.

The 33/30 gap is OpenAlex indexing lag on the newest items, not a split. Worth
knowing: **the DOI prefix changed mid-2025 from `10.3233` (IOS Press) to
`10.1177` (Sage)**, but both prefixes sit under the same journal record, so an
ISSN-scoped query picks up all of it. A prefix-scoped query would not.

### Recent comparable venue articles

All three neighbours claimed in the July record were re-verified today by direct
Crossref DOI lookup. All three confirmed:

1. **Nguyen, Sei, Tahara & Ohsuga (2026)**, "Model-driven approach enabling formalization and conformance testing of attribute-based access control policies for business processes," *JCS* 34(4):261–300, DOI 10.1177/0926227x261421496. An ABAC metamodel with patterns, demonstrated on three business processes.
2. **Abdunabi, Al Amin & Basnet (2025)**, "An authorization framework for body area network: A policy verification and smart contract-based integrity assurance approach," *JCS* 33(3):119–162, DOI 10.1177/0926227x241296435. Spatiotemporal ABAC with timed-coloured-Petri-net verification.
3. **Lanckriet, Piessens & Devriese (2026)**, "SoK: Robust properties, robust abstractions and back-translations," *JCS* 34(3):230–257, DOI 10.1177/0926227x251409398. An explicit systematization paper.

Two further genuine neighbours found:

4. **Soni, Nanda, Priyadarshini & Panda (2025)**, "A comprehensive review and comparative analysis of zero trust architecture," *JCS* 34(2):85–110, DOI 10.1177/0926227x251409922. Zero trust is the continuously-reverified authorization question at systems-architecture level, and this is a pure review with no new formal or empirical content.
5. **Abdulla, Oligeri & Bakiras (2026)**, "Location-based access control system for mobile devices using bluetooth low energy technology," *JCS* 34(4):301–319, DOI 10.1177/0926227x261428667. Access-control policy enforcement.

Topically adjacent but *not* a real neighbour, recorded so it isn't oversold
later: Sun et al. (2026), "Fully adaptive MA-ABE supporting multi-fan-in
circuits," *JCS* 34(3):211–229, DOI 10.1177/0926227x261418208. Access control is
the application of a crypto primitive there; the contribution is a scheme with a
security proof. A reviewer drawn from that paper is a crypto-construction person.

**Negative finding, with the search stated.** None of the 33 articles concerns
LLM agents, AI-agent security, or delegation to autonomous software agents. All
33 titles and abstracts were read directly; two WebSearch queries
(`"Journal of Computer Security" LLM agent security 2025 2026` and
`"Journal of Computer Security" usage control OR "trust management" OR delegation 2025 2026`)
returned only off-venue LLM work and off-topic JCS hits. **The paper would be
this venue's first on AI-agent delegation specifically.** That cuts both ways: no
thread to join, but no incumbent to displace, and real precedent in the
surrounding territory.

### Methodological-norm check: the decision-relevant finding

The question was whether a paper with neither proofs nor experiments is a shape
JCS publishes at all. Classification of all 33 recent articles:

| Shape | Count | Share |
|---|---|---|
| Empirical / experimental (ML detectors, fuzzers, attack demos, systems builds with benchmarks) | ~22 | ~67% |
| Formal / proof-carrying (protocol verification, crypto security proofs) | ~6 | ~18% |
| Formal/typed framework + worked-example validation, no proof, no statistical evaluation | 2 | ~6% |
| SoK / survey / comparative review, no new proof or experiment | 3 | ~9% |

**JCS's "formal modelling with proofs" reputation does not describe the majority
of what it currently publishes** — two-thirds is empirical security work, and
proof-carrying papers are a smaller minority than the reputation implies. More
to the point, roughly 15% of the recent corpus is neither: SoKs and surveys with
no new formal or empirical content, plus framework-with-worked-example papers.
JCS also uses the "SoK" label explicitly, which is a genre marker for
systematizing non-experimental work.

**Correction to the sweep's own verdict, and it matters.** The sweep concluded
the paper would be "the most minimal-contribution paper of this shape yet seen
in the 33-article window," on the premise that it has "no worked examples and no
formal proof." That premise came from my brief, which carried forward Brett's
July phrase "no threat model, no attacks, no defences, and no security
evaluation." That phrase is about the paper not being a security-*evaluation*
paper. It is not true that the paper lacks a demonstration. Verified in the
repository today:

- §3.4 is a worked running example (procurement assistant) with a stipulated regime fixture.
- Seven fixtures encode the level separations of the typed-claim-stack section, plus a hidden-oracle set authored against the regime fixtures rather than generated from engine output.
- Two analyzers: a semantic engine deriving standing, guards, payload–scope fit, grant and subgrant validity, transition effects, local authorization, state continuity, prefix/cumulative/terminal conditions; and an empirical analyzer emitting observation vectors and noncompensatory family verdicts.
- A design analysis by simulation (`scripts/design_analysis.py`) reporting Type S/M error and interval coverage.
- 17 analyzer tests plus 5 design-analysis tests, all passing today (`make validate-delegation` green).

So the paper belongs in the **6% row, alongside Nguyen and Abdunabi** — the two
confirmed neighbours — not in a category of its own below the table. The honest
residual gap against those two is narrower and more specific than "no
demonstration": Nguyen validates against three real business processes
(two real-world event logs), and Abdunabi does Petri-net verification, whereas
this paper's validation is **synthetic regression only**, which §8 states plainly
("No target-study outcomes exist. Every reported result is synthetic regression
or design-analysis output"). The gap is real-versus-synthetic demonstration, not
presence-versus-absence.

That is a much smaller gap and it points at a concrete, cheap reviewer-anticipation
move: expect a referee to ask for at least one worked case analogous to Nguyen's
three-business-process demonstration, and decide in advance whether to supply one
or to defend the synthetic-fixture design explicitly. Worth deciding before
submission rather than in a response letter.

### Editorial fit: resolved 2026-08-08, and it cuts both ways

Board read from `journals.sagepub.com/editorial-board/JCU` by Brett in a browser
after every automated route hit a Cloudflare challenge with no Wayback coverage.
The page also supplies metrics the July record lacked: **Impact Factor 1.3,
5-year 1.8**, and it still brands the journal "IOS Press" under Sage.

Roles are **not labelled on the page**, so the four names listed above the rest
(Calzavara, Liu, Jajodia, Millen) are positionally suggestive of editor and
honorary/founding roles but that is not asserted here. Independently confirmed:
**Peng Liu** (Penn State) is Editor-in-Chief, per his own faculty page.
**Stéphanie Delaune** is no longer on the board at all, which corroborates her
own CV's "co-editor-in-chief (2022–2025)" against the secondary sources that
still call her current. Stefano Calzavara is the plausible successor by position,
unverified.

Full board: Calzavara (Ca' Foscari Venezia), Liu (Penn State), Jajodia (George
Mason), Millen (MITRE), Bartoletti (Cagliari), Bichhawat (IIT), Boureanu
(Surrey), Carminati (Politecnico di Milano), Koutsos (INRIA), Lin (USTC),
Nicomette (INSA Toulouse), Oligeri (Hamad Bin Khalifa), Ren (Zhejiang),
Squarcina (TU Wien), Tang (Sydney), Haining Wang (Delaware), Shuai Wang (HKUST),
Ting Wang (Penn State), Danfeng Zhang (Duke).

**The good news, and it is substantial.** The paper now has named plausible
handlers, which it did not an hour ago:

- **Sushil Jajodia** (George Mason) is the single most relevant name on this board. Access-control policy and authorization are his field, and he is among the few people anywhere who own the whole canon prerequisite 1 has to engage. If he handles or reviews this, the canon engagement will be read closely ~-- which is an argument for doing it properly rather than defensively.
- **Danfeng Zhang** (Duke) and **Abhishek Bichhawat** (IIT) both work in language-based security and information-flow control, i.e. type systems used for security properties. That connects directly to the paper's `typed` framing, and both would be competent to judge whether §1's broad type-theoretic sense is doing real work or is a label.
- **Jonathan Millen** (MITRE) is classic formal security-protocol analysis.
- **Ting Wang** (Penn State), **Kui Ren** (Zhejiang), and **Shuai Wang** (HKUST) supply genuine ML/AI-security presence, so the AI side of the paper will not be wholly foreign to the board even though the venue has published nothing on agent delegation.
- Incidental: **Gabriele Oligeri** is both a board member and a co-author of the BLE access-control neighbour found above (Abdulla, Oligeri & Bakiras 2026).

**The complication, and it partly re-raises a risk the corpus check had
downgraded.** The board is heavily weighted toward formal methods and
language-based security: Calzavara, Millen, Bartoletti, Bichhawat, Boureanu,
Koutsos, Squarcina, and Zhang between them represent protocol verification,
process calculi, type systems, and information-flow proofs. The corpus check
found only ~18% of recent output proof-carrying, which suggested the "where is
the theorem?" norm was weaker than JCS's reputation implies. **Board composition
points the other way.** Corpus shape and reviewer pool are genuinely in tension
here, and the reviewer pool is what a submission actually meets.

Two consequences for the prerequisites:

1. The methodology risk should be treated as **moderate, not downgraded** ~-- somewhere between the reputation and the corpus. A referee drawn from the formal-methods half of this board is a real possibility, and §3.5's concession that the contribution is a meta-model rather than a complete authorization language is exactly the sentence such a referee will stop on.
2. This strengthens the case for the **demonstration** route over the formalization route in item 3 below, but for a different reason than cost. A half-built formalization put in front of Koutsos, Millen, or Zhang is worse than an honest meta-model plus a real worked case: they will see immediately what a grammar without correspondence results is missing, whereas a well-executed demonstration is not pretending to be a proof at all.

Full sweep with every query string: `notes/sources/jcs-venue-verification-2026-08-08.md`.

## Alternatives Considered

Carried forward from `venue-decision-2026-07-22.md`, re-screened today against
the paper's current extent. Nothing in the rejected set has changed in a way
that reopens it.

| Venue | Why plausible | Why not chosen now | Fallback status |
|---|---|---|---|
| **Minds and Machines** | Approved target until today; page one already written for it; Rashid 2026 poses the paper's question and leaves it open | **Given to the AGI-evaluation paper.** Not a fit judgment | Reopens only if the AGI paper leaves M&M |
| Journal of Responsible Technology | Best single neighbour found in either sweep (Pittman & Schaefer 2025, authorization to operate, 10.1016/j.jrt.2025.100130) | 5,000–10,000 words **including references** against ~13,700 excluding them. The gap widened since July | Rejected on length, more firmly than in July |
| AI Magazine | Article type is literally "conceptual analyses"; free OA | 6,000–9,000 words and "expository text without complex equations or formulas." Guts the formal apparatus, which is the thing we are now committing to strengthen | Only as a deliberate short spin-off |
| Artificial Intelligence and Law | Scope names deontic notions, normative systems, evaluation and auditing of legal AI. No length limit | Six-day median first decision reads as a high desk-reject rate; the paper uses agency law as analogy but does not model legal reasoning | Weak third |
| AI and Ethics | Densest cluster of near neighbours in the governance sweep | Fails its in-scope gate, which demands a defended claim about what is right, fair, harmful, or just. This paper is normative in the deontic sense, not the moral one | Rejected on scope gate |
| Computers & Security | Obvious topical home | Disqualified by written policy: "items directed to the security of AI/ML systems themselves… are out of scope" | Out |
| ACM TOPS / TIST / IEEE S&P mag | Topically adjacent | TOPS bans surveys/tutorials and demands a practical-significance argument; TIST's non-empirical track is invitation-only; IEEE S&P "is not a research journal" | Out |
| Internet Policy Review | Diamond OA | Disqualified: "The use of generative AI to author articles is not permitted." Prohibition model | Out |
| AI & Society | Broad scope | LLM use "strongly discouraged" beyond grammar and translation; 10,000-word ceiling | Out |

Conferences (SaTML, AIES, FAccT, NeurIPS D&B, CCS, S&P, USENIX) remain excluded
portfolio-wide per Brett's standing constraint: journals only, no conference
funding, and he will not present online.

## Risk Test

- **Strongest desk-rejection risk: page one addresses a philosophy readership at a security journal.** The exact mirror of July's risk, created by July's fix. Fixable, and must be fixed before submission. See the page-one finding above.
- **Strongest reviewer-rejection risk: the missing authorization canon, which at this venue is fatal rather than cheap.** The July record accepted this risk explicitly *on the ground that M&M reviewers do not own that canon*. That ground is now gone. JCS is precisely the readership that owns ABLP, SPKI/SDSI, Delegation Logic, SecPAL, UCON, and XACML, and the external referee said the gap is decisive "for a security, access-control, or formal-methods venue." **The risk is not accepted; it is a prerequisite.** Grep on 2026-08-08 reconfirms zero hits across `sections-delegation/`, `references-local.bib`, and `references.bib`.
- **Strongest "wrong methodology" risk: MODERATE.** Downgraded from the reputation, then partly re-raised by the board. The corpus says the proof norm is weaker than JCS's reputation implies (~18% proof-carrying against ~67% empirical and ~15% neither), and the paper's shape matches the framework-plus-worked-example row occupied by both confirmed neighbours. But the editorial board is heavily formal-methods and language-based-security (Calzavara, Millen, Bartoletti, Bichhawat, Boureanu, Koutsos, Squarcina, Zhang), and **the reviewer pool is what a submission actually meets, not the corpus average.** §3.5's concession that the contribution is a meta-model rather than a complete authorization language is the sentence a formal-methods referee will stop on. Residual gap against the two neighbours is narrower than "no demonstration": their validation runs against real event logs and Petri-net verification, this one's against synthetic fixtures. Expect a referee to ask for a real worked case.
- **Strongest "no thread to join" risk, new and specific to this venue:** JCS has published nothing on LLM agents, AI-agent security, or delegation to autonomous software agents in 33 articles since January 2025. The paper would be a first here. The surrounding territory is well populated (ABAC formalization, authorization frameworks, zero trust, access-control enforcement), so this is thread-opening within an active area rather than arriving in a vacuum, but the cover letter has to do the joining work that a citable in-venue predecessor would otherwise do. SecPAL, published in this journal in 2010, is the strongest available anchor.
- **Strongest "opinion piece / no evidence" risk: lower than July.** Three programme designs, seven fixtures, a hidden-oracle set, two analyzers, 22 passing tests, and a design analysis by simulation, with the artifact now linked in §8 (tag `delegation-assurance-r1`, held). All results are synthetic regression, and §8 says so plainly rather than letting it be discovered.
- **Strongest "not motivated / no live problem" risk:** low. Agent authorization is live in this venue's own subject matter, and the confused-deputy framing is native to it.
- **~~Unquantified risk: the editorial board could not be read~~ — RESOLVED 2026-08-08.** Brett read the board page in a browser. Named plausible handlers now exist, chiefly Sushil Jajodia for the authorization canon and Danfeng Zhang or Abhishek Bichhawat for the typed framing. The residual is not a gap in knowledge but the composition finding folded into the methodology risk above.

Resolution:

- [ ] Risks resolved in manuscript before package work. **Two prerequisites, neither started.**
- [x] Risks accepted explicitly by Brett: none this round. The July acceptance of the missing-canon risk is **withdrawn**, because it was conditional on an M&M readership.
- [ ] Risks unresolved: proceed once the two prerequisites clear.

**Prerequisites before package work:**

1. **Engage the authorization canon.** ABLP (Abadi, Burrows, Lampson & Plotkin), SPKI/SDSI, Delegation Logic (Li, Grosof & Feigenbaum), SecPAL (Becker, Fournet & Gordon), UCON (Park & Sandhu), XACML. Not a defensive citation list: the paper has to say what each formalism does, where its own claims stand relative to them, and specifically which can and cannot express trajectory-scoped authorization.

   **All six read 2026-08-08; the result is worse than "add a section" and is recorded in `notes/canon-audit/claim-disposition.md`.** Three of the paper's advertised results are substantially eroded: (C-i) cumulative limits does not survive at all, because it is what UCON was built to close and UCON states it in this paper's own terms with four worked mechanisms; grant-relative non-amplification is directly anticipated by SPKI's tuple reduction and Delegation Logic's step-9 rule; and (B) is near-trivial across all six, a *design property* of SPKI and Delegation Logic rather than an observation. (C-ii) joint disclosure is a positioning liability rather than a gap: Lampson et al. scope it out by name and point at Denning 1976, and **Jajodia's own field is inference and aggregation in multilevel databases**. **What survives cleanly is the interpretation step** ~-- every one of the six presupposes correctly identified principals and correctly classified requests, and SecPAL's principals simply *are* public keys. That is the paper's real contribution and it is currently framed as setup.
2. **Page one reaimed at a security readership.** Restore the security framing from `777aea0`, keeping the intervening improvements, and move the AI-governance material into related work. The non-composition result should be on page one for this venue as it was for M&M.

Sequenced after those two, not blocking the venue decision:

3. **Decide what "strengthening the formal core" means here. CORRECTED 2026-08-08 after reading SecPAL; my earlier recommendation in this slot was wrong.** That advice ("take the demonstration route, skip the formalization") was drawn from Nguyen and Abdunabi, which are applied framework papers. SecPAL is the closer precedent: same venue, same topic, and the paper this manuscript's title invites comparison with. Its bar was four body theorems, seventeen appendix lemmas with all proofs, twelve comparative idiom subsections, a described prototype ~-- and **no experiments at all** ("Although system implementation is not the subject of this paper"). **So JCS supports a paper with no experiments but not one with no formal results**, and the §3.5 disclaimer that this is "a meta-model … not a complete authorization language" will be read directly against the paper that *is* the complete authorization language. **Revised recommendation: both routes, small.** One clean proposition about non-composition on the action axis, in the shape of SecPAL's own Prop. 3.3–3.6 (short structural statements about a three-rule system, one of which is a single line doing heavy work); plus a reorganization of the seven existing fixtures into a comparative idiom table in SecPAL's §6 form, which is this venue's recognized substitute for an evaluation section and costs no new work. Brett's call, and note it is **the same decision as the title question**: *Typed Authorization Semantics* invites the SecPAL theorem bar, an applied-framework title invites the Nguyen/Abdunabi worked-case bar.
4. **Narrow the claims to what survives the canon.** The audit (`notes/canon-audit/claim-disposition.md`) found that (C-i) cumulative limits does not survive at all, grant-relative non-amplification is directly anticipated, (B) is near-trivial across all six works, and (C-ii) joint disclosure is a positioning liability rather than a gap. What survives clean is the interpretation step, which the paper currently treats as setup. This is prerequisite 1's real content and is larger than "add a literature section."
5. **Sage Vancouver reference-style conversion**, at submission-gate time.
6. ~~Read the editorial board page in a browser.~~ **Done 2026-08-08.**

## Evidence And Motivation Test

- [x] Problem shown live, not merely imaginable. Confused deputy, H.R. 7390, and the OpenAI long-horizon report are all real; the security readership will recognize the first immediately.
- [x] Conceptual paper names its evidential standard. §3.6, in detail.
- [ ] Engages current recommended practice in the relevant field. **Fails, and this is prerequisite 1.** For this venue the relevant field is authorization formalization, not validity theory.
- [x] Documents a practical decision point. H.R. 7390 manufacturer safety cases.
- [x] States which readership owns the main payoff. Now unambiguous: the security and access-control readership.

## Forecast (Prediction Ledger)

To be completed with Brett's numbers before submission. Base rate: run
`python3 Project-Management/prediction-ledger/score.py`. As of 2026-07-22 there
were 17 resolved events and no `ai-cs` venue class; the July record opened that
class. Standing pattern in the ledger: Brett's forecasts run above Claude's on
every pending event.

The methodological-norm question that was blocking this estimate is now
answered: JCS does publish non-proof, non-experimental framework papers, and the
manuscript's shape matches two confirmed in-venue neighbours.

- Base rate for this venue class: `ai-cs`, still n=0 resolved.
- P(survives desk / reaches external review): Brett ____ ; Claude 0.6 **after both prerequisites clear**, 0.25 without the page-one reaim. The desk risk is now mostly framing, not shape. Unchanged by the board finding, which bears on review rather than the desk.
- P(eventually accepted at this venue): Brett ____ ; Claude 0.2, revised down from 0.25 after reading the board. Three things the desk screen won't catch: the paper would be the venue's first on AI-agent delegation; its demonstrations are synthetic where both in-venue neighbours' are real; and the board leans formal-methods, so the referee likely to be assigned is likelier than the corpus average to want a theorem. Jajodia's presence pushes the other way for the canon engagement specifically, but only if that engagement is done properly.
- Expected first decision by: ____ . **JCS publishes no median-first-decision figure and none was found.** Do not guess one; record it if a Sage journal-metrics page or the submission system supplies it.

Log matching `event` and `forecast` records to
`Project-Management/prediction-ledger/ledger.jsonl` on submission, and a
`resolution` record the day the decision letter arrives.

## Package Authorization

- [x] Venue decision approved by Brett before target-specific package work begins (2026-08-08).
- [ ] Prerequisites 1 and 2 cleared.
- [ ] Unresolved risks copied into the pre-submission checklist.
- [x] Record linked from `DECISIONS.md`; `STATUS.md` and `PORTFOLIO.md` updated 2026-08-08.

## Portfolio note

This retarget resolves the three-way M&M collision recorded in `PORTFOLIO.md`.
After it: the AGI-evaluation paper keeps M&M, Delegation Assurance goes to JCS,
Evidentiary Assurance is already retargeted to *Computer Law & Security Review*,
and Truth-Tracking Profiles is being handled separately. No two of the four now
point at the same venue.

Ledger meta-lesson (2026-07-12, Corpora/IJCL): choosing a weaker-fit venue to
avoid a second concurrent submission at the best-fit venue cost a full
submission cycle. That lesson does not bite here. JCS was independently rated
the highest-ceiling venue found for this paper, so the sequencing constraint
moved it toward its best fit rather than away from it.
