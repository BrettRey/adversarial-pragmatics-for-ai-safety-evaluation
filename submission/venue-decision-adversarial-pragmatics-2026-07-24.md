# Venue Decision Record: Adversarial Pragmatics
<!-- SUMMARY: proposes JAIR primary and Language Resources and Evaluation second for the flagship, turning on an unresolvable Springer CC-BY preprint conflict - status: proposed, awaiting Brett - updated: 2026-07-24 -->

## Record

- [x] Project: `papers/development/adversarial-pragmatics-for-ai-safety-evaluation` (flagship)
- [x] Manuscript title: *Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control* (32 pp plus a 13 pp supplement, ~11,200 words)
- [x] Proposed venue: **JAIR** (Journal of Artificial Intelligence Research) primary; **Language Resources and Evaluation** (Springer) second
- [x] Article type / section: JAIR regular article; LRE would be a Project Note rather than a Full-Length Paper
- [x] Venue URL / author instructions checked: `jair.org`; `link.springer.com/journal/10579`; Springer Nature self-archiving policy `springernature.com/gp/new-content-item/23218974`; `info.arxiv.org/help/license`
- [x] Date checked: 2026-07-24
- [x] Decision owner: Brett
- [x] Assisting agent/model: Claude Opus 5 (1M context), with a four-agent parallel verification sweep over 16 journals
- [x] Recommendation status: **approved** (Brett, 2026-07-24: "JAIR")
- [x] Final decision: **submit to JAIR**, after arXiv v3. LRE is not pursued.

Standing constraint applied before the shortlist was built: **journals only, no
conferences or workshops** (Brett, 2026-07-24). This is severe for this paper.
Benchmark-and-protocol work of this kind lives mostly at ACL, EMNLP, NeurIPS
Datasets and Benchmarks, and FAccT, all of which are out. The task was to find
journals that own the same conversation.

## Journal-Reader Contract

Primary, JAIR:

> This manuscript changes the debate about **what an LLM-judge score licenses
> you to conclude** for readers of *JAIR* by showing that a rubric-aided judge
> can look strong in aggregate while never recovering the safety-relevant
> minority class, and that the apparent advantage survives neither item-clustered
> intervals nor partial pooling.

Second, LRE:

> This manuscript changes the debate about **annotation-protocol design for
> safety evaluation** for readers of *Language Resources and Evaluation* by
> showing that a protocol which fuses task success, policy compliance, risk,
> refusal, and attribution into one label cannot support the inferences
> evaluators draw from it, and by supplying a seed resource that separates them.

- [ ] The debate/problem is visible in the title, abstract, and first two pages.
      For JAIR, close. For LRE, no: the opening is in an AI-safety register and
      would need the resource-construction contribution foregrounded.
- [x] The contribution is journal-local at both.
- [ ] Reader's vocabulary decided. Provisional for JAIR: *benchmark, judge,
      annotation, inter-rater agreement, calibration* are free; *adversarial
      pragmatics, projectibility, bearer, inference license, deixis, indirect
      speech act, joint pair completion* are earned.

## Fit Evidence

**JAIR**, verified 2026-07-24 on `jair.org`:

- Diamond OA, **zero fee**.
- Disclosure-model AI policy: AI "cannot be credited as authors," with editing,
  idea-generation, and analysis assistance allowed if disclosed. Matches the
  house `\aidisclosure{}` practice.
- Preprints explicitly permitted: "Authors may submit their JAIR papers to arXiv
  and similar services."
- **No length cap**, and short articles are explicitly welcomed.
- JAIR publishes under CC BY itself, so there is **no license conflict**.
- Published by the AI Access Foundation. Its tie to AAAI/IJCAI is historical
  sponsorship and a joint prize, not a submission or presentation requirement,
  which matters given the no-conferences constraint.
- Three DOI-verified 2025-26 neighbours: WorldView-Bench
  (`10.1613/jair.1.19001`), ConSCompF (`10.1613/jair.1.17028`), "Agentic Large
  Language Models, a Survey" (`10.1613/jair.1.18675`).

**LRE**, verified 2026-07-24: the scope statement itself names annotation,
evaluation, and benchmarking, which is the closest topical match among all 16
journals checked. Hybrid, with a genuine free subscription route.

## The finding that decides the ranking

Springer Nature's group-wide self-archiving policy states: **"Preprints must not
be archived/deposited under a Creative Commons licence, such as a CC BY
licence."** This manuscript's arXiv posting (2607.01153) **is** licensed CC BY
4.0, verified on the arXiv abstract page.

The sweep proposed curing this by giving v3 a different license. That is only a
partial cure, and the difference matters. arXiv states that "different versions
of the work can have different licenses," so v3 *can* drop CC BY, but it also
states that "the license chosen for each version is irrevocable." **v1 and v2
therefore remain publicly available under CC BY 4.0 permanently.** Anyone
applying the Springer sentence literally would still find a CC BY deposit of
this work.

Assessment: the textual conflict is real; its practical force is unknown, since
Springer journals routinely publish papers with CC BY preprints, and the clause
may be aimed at accepted-manuscript deposits rather than pre-submission
preprints. But it cannot be fully resolved by anything Brett does now. That is
why the ranking puts JAIR, which has no such clause, ahead of the better
topical match.

This clause silently affects four candidates a topic-organized sweep would not
have connected: LRE, Machine Learning, Behavior Research Methods, and AI and
Ethics.

## Alternatives Considered

| Venue | Why plausible | Why not chosen now | Fallback status |
|---|---|---|---|
| **Language Resources and Evaluation** (Springer) | Scope literally names annotation, evaluation, benchmarking. Best topical fit of 16 checked. Free subscription route | Springer CC-BY preprint clause, unresolvable per above. Also, an LRE desk editor used to larger validated resources may read the paper's honest non-validation stance as not-submission-ready; Project Note is the safer article type | **Strong second.** Query the editorial office about the CC-BY clause before any package work |
| **ACM JDIQ** | Arguably the best conceptual match: the paper's central claim is about the quality and reliability of an evaluation instrument. ACM policy is disclosure-model, arXiv permitted, no CC-BY restriction found | `dl.acm.org` was Cloudflare-blocked to every fetch method tried, so its scope and length facts rest on secondary sourcing, not a directly read page. Length also runs over its ~25pp norm | Third, pending a manual browser check |
| **Natural Language Processing** (Cambridge; renamed from *Natural Language Engineering* in 2024) | Near-exact length fit | Gold-OA-only at roughly USD 3,655 | Fourth |
| **Computational Linguistics** (MIT Press) | Zero fee, strong fit | Its normal length band runs *longer* than this manuscript, the reverse of the usual problem | Fifth |
| **TACL** | Obvious candidate; presentation was the suspected blocker | Presentation is **optional**, confirmed by two independent primary sources, so the suspected blocker was a false alarm. It fails instead on a 10-page ACL-format cap that the manuscript exceeds by roughly 40% | Out on length |
| **AI and Ethics** (Springer) | Topically adjacent | Categorical scope gate excluding work that is "primarily a technical contribution... with no substantive ethical analysis," which matches this paper's own stated shape almost word for word. Plus the CC-BY clause | Out |
| **Patterns**; **Journal of Responsible Technology** | Both genuinely strong topical matches | Both fail on specific quoted word caps | Out on length |
| **AI Magazine** | Cleanest preprint and AI policy of any candidate, zero fee | 6,000-9,000 words of "expository text without complex equations or formulas," which excludes the kappa, bootstrap, and hierarchical-model apparatus as written. Structural retargeting, not a trim | Out |
| **Machine Learning** (Springer) | Strong topical fit, free subscription route | CC-BY clause, plus a separately branded "Journal Track @ ECML PKDD" that *does* require conference presentation and must be actively avoided | Out |
| **Artificial Intelligence** (Elsevier) | Qualifies on all hard constraints | Guide for Authors Cloudflare-blocked (a disclosed access gap, not a clean finding); recent content skews to classical and formal AI | Out |
| **Behavior Research Methods** (Springer) | Real practice-level fit if reframed to "LLMs as research instruments" | Needs a reframing pass, not just placement. Plus the CC-BY clause | Out |
| **ACM TIST** | Close DOI neighbours including LLM-as-judge alignment work | Recent output skews to papers with a validated technical system or benchmark result, making the non-validation stance a bigger liability than at JDIQ | Out |
| Any conference or workshop | Where this conversation mostly happens | Standing constraint: journals only | Out |

## Risk Test

- **Strongest desk-rejection risk (JAIR):** whether a reviewer culture weighted
  toward algorithmic and formal AI reads a linguistically grounded diagnostic
  taxonomy over an 18-item benchmark as a core AI contribution or a scope
  stretch. An informal pre-submission query to the editor-in-chief is cheap
  insurance.
- **Strongest desk-rejection risk (LRE):** the paper's own honesty about scale
  and non-validation reading as an admission it isn't ready.
- **Strongest reviewer-rejection risk (both):** 18 items over three small local
  models, with HarmBench, XSTest, and AgentDojo cited but not benchmarked
  against, and Studies A and B not yet run. A skeptical reviewer can fairly ask
  why this shouldn't wait for Study A. This is the same objection the CJL
  referees raised on a different Reynolds paper (ledger, 2026-07-09): no clear
  evidential standard for the apparatus built on top.
- **Strongest "not motivated" risk:** lower here than for the siblings. The
  judge findings are concrete, negative, and surprising.

Resolution:

- [ ] Risks resolved before package work.
- [x] **Risks accepted explicitly by Brett**: he chose JAIR on 2026-07-24, which takes the Springer CC-BY preprint conflict off the table entirely rather than accepting it. The remaining risks are the JAIR scope-stretch question and the 18-item evidential-base objection, both live.
- [ ] Risks unresolved: pause.

## Evidence And Motivation Test

- [x] The problem is live, not merely imaginable: the six-cell judge experiment
      produces a real negative result on real outputs.
- [x] The evidential standard is named in the first two pages.
- [x] It engages current recommended practice: Messick and Kane on validity,
      Gelman and Carlin on Type-M and Type-S.
- [x] Interdisciplinary payoff ownership: needs stating explicitly, and the
      answer differs by venue (JAIR: evaluation methodology; LRE: resource and
      protocol construction).

## Forecast (Prediction Ledger)

- Base rate for this venue class: **none on file.** The ledger has book, cogsci,
  corpus, linguistics, and philosophy classes. AI and NLP is new. Portfolio-wide
  across 17 resolved events: 6/17 (35%) desk survival, 2/17 (12%) acceptance.
- P(survives desk / reaches external review): Brett to record. Claude Opus 5:
  **0.5** at JAIR, **0.45** at LRE.
- P(eventually accepted at this venue): Brett to record. Claude Opus 5: **0.25**
  at JAIR, **0.2** at LRE.
- Expected first decision by: Brett to record once a submission date exists.

## Required before submission, either venue

1. **Post arXiv v3.** The preprint carries the old title, a stale comments field
   (18 pp / 10 pp / 11 tables against a true 32 pp / 13 pp / 17 tables), and an
   abstract that claims multi-turn agent transcript coverage the seed set
   represents only by a single-turn tool-result contrast. A submission whose
   preprint carries a different title invites confusion at the desk. Draft
   abstract and checklist: `notes/arxiv-v3-abstract-draft.md`,
   `submission/arxiv/metadata.md`.
2. **Decide the article type** if LRE: Project Note, and say so in the cover
   letter rather than letting a desk editor decide.
3. **Foreground the venue-legible framing** in the first two pages. For LRE this
   means leading with annotation protocol and resource construction rather than
   the AI-safety register.
4. **Decide the arXiv v3 license** if LRE is chosen, understanding that v1 and
   v2 stay CC BY regardless.

## Package Authorization

- [x] Venue decision approved before target-specific package work begins.
- [x] Brett has approved the target (2026-07-24).
- [ ] Unresolved risks copied into the pre-submission checklist.
- [ ] Record linked from `DECISIONS.md` and `STATUS.md` if submission proceeds.

Decision summary for `DECISIONS.md`, to be added only if Brett approves:

```markdown
2026-07-24 - Venue decision: JAIR for Adversarial Pragmatics, with Language Resources and Evaluation as second. Owner: Brett, agent-assisted. Record: `submission/venue-decision-adversarial-pragmatics-2026-07-24.md`. Reason: JAIR is the only strong candidate with zero fee, no length cap, an explicit preprint permission, and no CC-BY conflict; LRE is the better topical match but carries a Springer preprint-license clause that cannot be fully cured because arXiv licenses are irrevocable per version. Risks accepted: none; arXiv v3 required before submission either way.
```
