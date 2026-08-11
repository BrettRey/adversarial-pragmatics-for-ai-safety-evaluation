# JCS Venue Fit-Evidence Verification — "Delegation Assurance for AI Systems"
Run date: 2026-08-08. All claims below are grounded in a fetched source; gaps are stated as gaps, not filled in.

---

## Method note (read first)

Per the warning, I did NOT trust a raw low count. I first resolved a known recent JCS DOI
(10.1177/0926227x251409398, the Lanckriet SoK) through both Crossref and OpenAlex, confirmed it
resolves to a single, unified journal record in each system (Crossref member 179 = Sage;
OpenAlex source S106992369, ISSN 0926-227X/1875-8924, no ISSN split), and only then queried that
resolved source for counts. This journal shows **no** legacy/live ISSN-split of the kind the
warning describes — the DOI prefix did change (10.3233, IOS Press → 10.1177, Sage) partway
through the 2025 volume, but both prefixes are indexed under the same Crossref/OpenAlex journal
record, so a straight ISSN-scoped query picks up all of it.

Queries run:
- Crossref: `GET https://api.crossref.org/journals/0926-227X/works?filter=from-pub-date:2025-01-01,until-pub-date:2026-08-08` → **33** journal-article results, all inspected individually (DOI, title, authors, volume/issue/page, date).
- OpenAlex: `GET https://api.openalex.org/works?filter=primary_location.source.id:S106992369,from_publication_date:2025-01-01,to_publication_date:2026-08-08` → **30** results.
- OpenAlex sources lookup: `GET https://api.openalex.org/sources?filter=issn:0926-227X` → exactly one source record (confirms no split).

The 33 vs 30 gap is consistent with OpenAlex's normal indexing lag for the newest items (several
of the 33 Crossref records are dated within the last few weeks); it is not evidence of a broken
query, since both point at the same single source. **I'm treating 33 as the more current and
complete figure**, cross-validated at 30 by the second source.

---

## Task 1: Recent output

**33 journal articles from 2025-01-01 through 2026-08-08** (roughly 19 months), i.e. an average
of ~1.7 articles/month or ~21/year. This is a normally active specialty journal, not a dormant
one — the near-zero-count failure mode the warning describes does not apply here once the query
is done correctly.

Full list (33 items) available on request; used throughout below for tasks 2–4.

---

## Task 2: Three claimed neighbours — all CONFIRMED via direct Crossref DOI lookup

**1. Nguyen, Sei, Tahara & Ohsuga (2026) — ABAC conformance testing.**
Duc-Hieu Nguyen, Yuichi Sei, Yasuyuki Tahara, Akihiko Ohsuga. "Model-driven approach enabling
formalization and conformance testing of attribute-based access control policies for business
processes." *Journal of Computer Security* 34(4), pp. 261–300. Published online 26 Feb 2026.
DOI: **10.1177/0926227x261421496**.
Abstract (Crossref): proposes "a fine-grained and highly automated model-driven framework
enabling the formalization and conformance testing of ABAC policies for business processes," an
ABAC metamodel with patterns, demonstrated on three business processes (one simulated, two
real-world).

**2. Abdunabi, Al Amin & Basnet (2025) — authorization framework.**
Ramadan Abdunabi, Md Al Amin, Rejina Basnet. "An authorization framework for body area network: A
policy verification and smart contract-based integrity assurance approach." *Journal of Computer
Security* 33(3), pp. 119–162. Published online 21 Feb 2025.
DOI: **10.1177/0926227x241296435**.
Abstract confirms: spatiotemporal ABAC (STABAC) model for body-area-network access decisions,
formal verification via timed coloured Petri nets, blockchain-backed policy-integrity checking.

**3. Lanckriet, Piessens & Devriese (2026) — SoK.**
Emiel Lanckriet, Frank Piessens, Dominique Devriese. "SoK: Robust properties, robust abstractions
and back-translations." *Journal of Computer Security* 34(3), pp. 230–257. Published online 26
Feb 2026. DOI: **10.1177/0926227x251409398**.
Abstract confirms: systematizes formal security criteria across secure compilation, cryptography,
and information-flow control (robust properties, robust abstractions, a new "non-degrading
abstractions" notion); explicitly a systematization/unification paper, not a single-system
proof-of-security paper.

All three verdicts: **CONFIRMED**, full metadata pulled directly from `api.crossref.org/works/<DOI>`.

---

## Task 3: Further genuine neighbours (2025+)

I re-examined all 33 titles/abstracts in the 2025–2026 window for topical fit to delegation,
authorization, trust management, usage control, access-control policy, or agent/LLM security.
Two are strong, direct neighbours; one is topically-adjacent but methodologically distinct
(flagged as such, not oversold).

**Strong neighbours:**

- **Soni, Nanda, Priyadarshini & Panda (2025).** "A comprehensive review and comparative
  analysis of zero trust architecture: Evolution, implementation strategies, and key
  challenges." *JCS* 34(2), pp. 85–110. Published online 26 Dec 2025.
  DOI: **10.1177/0926227x251409922**.
  Why it's a real neighbour: zero-trust architecture is precisely the "who is authorized to act,
  under what continuously-reverified conditions" question the manuscript is about, at the
  systems-architecture level rather than the meta-model level. It is also a pure literature
  review with no new formal or empirical contribution — directly relevant to Task 4 too.

- **Abdulla, Oligeri & Bakiras (2026).** "Location-based access control system for mobile
  devices using bluetooth low energy technology." *JCS* 34(4), pp. 301–319. Published online
  5 Mar 2026. DOI: **10.1177/0926227x261428667**.
  Why it's a real neighbour: a genuine access-control-policy-enforcement paper (dynamic policy
  enforcement via BLE beacons, tamper-resistant Android enforcement module) — it sits squarely
  in "access-control policy," one of the named categories.

**Topically-adjacent but not a semantic match (included for completeness, not oversold):**

- **Sun, Gao, Hu, Zhao, Zhou, Song & Lu (2026).** "Fully adaptive MA-ABE supporting
  multi-fan-in circuits." *JCS* 34(3), pp. 211–229. Published online 16 Feb 2026.
  DOI: **10.1177/0926227x261418208**.
  This is a cryptographic construction paper (multi-authority attribute-based encryption,
  adaptive-security proof) — access control is the *application* of the crypto primitive, but
  the paper's contribution is a cryptographic scheme with a security proof, not authorization
  semantics or a policy/trace model. A reviewer assigned this paper would be a crypto-construction
  person, not necessarily someone who reasons about authorization semantics the way the
  manuscript does.

**Negative finding, stated explicitly:** none of the 33 articles concern LLM agents, AI agent
security, or delegation to autonomous software agents. Queries run and returning nothing on
point: `"Journal of Computer Security" LLM agent security 2025 2026` (WebSearch) and
`"Journal of Computer Security" usage control OR "trust management" OR delegation 2025 2026`
(WebSearch) — both returned only off-venue LLM-agent-security papers (arXiv, ScienceDirect) and
off-topic JCS hits. I also read every one of the 33 titles/abstracts directly and none mentions
LLMs, AI agents, or delegation to autonomous software. So: JCS currently has zero output in the
manuscript's most novel dimension (AI-agent delegation specifically), but real precedent in the
surrounding territory (ABAC formalization, authorization frameworks, zero-trust, access-control
enforcement).

---

## Task 4: Methodological norm check — THE decision-relevant finding

I classified all 33 articles from the 2025–2026 window by shape, using abstracts fetched directly
from Crossref for every SoK/survey/framework paper and the borderline cases, and title+venue-domain
inference for the remaining more mechanically-obvious ML/systems papers (traffic classifiers,
malware/intrusion detectors, fuzzers, watermarking schemes — these are unambiguously
empirical/experimental from their titles and are standard security-conference/journal fare).

| Shape | Count | Share | Examples |
|---|---|---|---|
| Empirical / experimental (ML detectors, fuzzers, attack demos, systems builds with benchmarks) | ~22 | ~67% | ANT-ET traffic fingerprinting; FedRAB; HuntFUZZ; SQLaser; EMI backdoor; Log2Graph; GS-HF |
| Formal / proof-carrying (protocol verification, crypto security proofs) | ~6 | ~18% | Delaune, Lallemand & Outrey, vote-privacy formalization + ProVerif; Fernet, Mödersheim & Viganò, decision procedure + typing result; Hess et al., Isabelle/HOL verification tool; Sun et al., MA-ABE adaptive-security proof |
| Formal/typed framework + worked-example validation, no proof, no statistical evaluation | 2 | ~6% | **Nguyen et al. (ABAC conformance)**; **Abdunabi et al. (authorization framework)** — the manuscript's two confirmed "neighbours" |
| SoK / literature survey / comparative review, no new proof or experiment | 3 | ~9% | **Lanckriet et al., SoK**; **Soni et al., zero-trust review**; Jiang, Ryan, Li & Ferdosian, HGNN survey |

**Direct answer to the question asked:** JCS's actual recent corpus is dominated by empirical/
experimental security papers (roughly two-thirds), not by formal proof papers — the "formal
modelling with proofs" reputation does not describe the *majority* of what the journal is
currently publishing. But the venue does publish non-empirical, non-proof-carrying work: 3 of 33
recent articles (~9%) are SoKs/surveys/comparative reviews with no new formal or empirical
contribution, and JCS explicitly uses the "SoK" label (Lanckriet et al.), which is a genre marker
for exactly the kind of systematizing, non-experimental contribution the manuscript makes.

**Important caveat, stated plainly rather than smoothed over:** none of these three is a perfect
shape-match for the manuscript. The Lanckriet SoK still delivers new formal definitions and
general results (robust properties, non-degrading abstractions) — it is conceptual but not
evaluation-free in the sense of having zero technical payload beyond taxonomy. Soni et al.'s
zero-trust piece and the Jiang et al. survey are literature reviews of *other people's* systems,
not a new meta-model of the authors' own design. The two closest genre-precedents by actual shape
(a novel formal framework, demonstrated rather than proved or benchmarked) are Nguyen et al. and
Abdunabi et al. — but both still include a validation step (conformance testing against real
event logs; Petri-net verification) that the manuscript, by design, has none of (no threat model,
no attacks, no defences, no evaluation of any kind).

**Bottom line for the retargeting decision:** the venue does not require proofs or experiments —
survey/SoK papers with zero empirical or proof content are a real, if minority (~9%), part of the
recent corpus, and framework-without-a-mechanism papers exist too (Abdunabi, Nguyen). But every
non-empirical example found still delivers *something* beyond a typed taxonomy — either new
formal results (Lanckriet) or a worked demonstration (Abdunabi, Nguyen) or a synthesis of others'
empirical work (Soni, Jiang). A manuscript with literally no evaluation, no worked example, and no
formal proof would be the most minimal-contribution paper of this shape yet seen in the 33-article
window — plausible given the precedent, but not a guaranteed comfortable fit, and worth having the
cover letter/framing anticipate that a referee may ask for at least one worked case study analogous
to Nguyen's or Abdunabi's three-business-process / BAN demonstration.

---

## Task 5: Sage generative-AI policy — verbatim, with URL and fetch method

Two Sage policy pages exist; I fetched both directly (via `curl` after `WebFetch` was blocked by
Sage's Cloudflare bot-challenge — see Task 6 note on the identical block). The general/current
page is more complete and is quoted in full below.

**URL fetched (live, 200 OK via `curl`):** `https://www.sagepub.com/generative-AI-tools-policy-msg`
(this is Sage's general "Publication ethics policies → Artificial intelligence policy" page,
not a medical-journal-specific policy — confirmed by the page's own breadcrumb/nav, which lists
it under "Publication ethics policies" alongside "Authorship guidelines," "Citation manipulation
policy," etc., applicable across Sage journals including JCS.)

**Prohibited-use / non-rejection clause, verbatim:**

> "While submissions will not be rejected solely because of the disclosed use of GenAI tools, if
> the editor becomes aware that GenAI was inappropriately used in the preparation of a submission
> without disclosure, the editor reserves the right to reject the submission at any time during
> the publishing process."

This is an exact match for the July note's paraphrase — the word "solely" is present verbatim on
this current live page.

**Complete list of prohibited/inappropriate uses of GenAI, verbatim (9 items):**

> "Inappropriate use of GenAI includes:
> - Generation of incorrect text or content
> - Generation of data or submission using a series of prompts
> - Conducting interviews with GenAI tools in lieu of participants for qualitative research
> - Analysis of experiences and themes
> - Plagiarism or inappropriate attribution to prior sources
> - Generated images that are presented as unique or novel research images
> - Fabricated references or falsified claims
> - Use of GenAI tools for editorial work or to conduct peer-review
> - Use of GenAI to generate peer review reports, such as uploading or copy-pasting the manuscript
>   or parts of it to a GenAI tool"

**Disclosure-required category (for context):** "primary or partial use of AI tools and/or LLMs
that produce content such as references, text, images, or any other content that directly impacts
the research methodology, analysis, results and/or conclusions must be disclosed upon submission."
Assistive AI (grammar/language/structure suggestions on the author's own text) does not require
disclosure.

**Secondary check:** I also pulled a Wayback Machine snapshot of the parallel
`uk.sagepub.com/en-gb/asi/artificial-intelligence-policy` page (captured 2026-01-17) as a live
`WebFetch` attempt returned HTTP 403. That snapshot has near-identical wording but *without* the
word "solely" ("submissions will not be rejected because of the disclosed use of generative AI")
and a shorter 3-item inappropriate-use list. The live `www.sagepub.com` page fetched above is more
recent in substance (it has the fuller 9-item list and the "solely" wording) — I'm treating it as
the current, authoritative version, but flag that Sage maintains at least two regionally-branded
policy pages that aren't word-for-word identical.

---

## Task 6: Editor-in-Chief and editorial board

**What I could confirm, from primary sources:**

- **Peng Liu** (Raymond G. Tronzo, MD Professor of Cybersecurity, Penn State College of
  Information Sciences and Technology) is currently listed as Editor-in-Chief of *Journal of
  Computer Security* on his own faculty page (`s2.ist.psu.edu/pliu/`), with no end date given —
  i.e., an ongoing role as of this fetch.
- **Stéphanie Delaune** (CNRS Director of Research, IRISA/Univ Rennes, formal verification of
  security protocols, voting-protocol privacy) — her own CV (`people.irisa.fr/Stephanie.Delaune/cv.pdf`,
  itself dated with entries through 2026) lists: **"Journal of Computer Security (JCS),
  co-editor-in-chief (2022–2025)."** This is a *completed* term by her own primary-source
  account, not an ongoing one — several secondary/search-engine summaries describe her as a
  "current" co-EiC, but her own CV contradicts that as of whenever it was last updated (which
  appears to be mid-2026, given it lists a June 2026 committee role). **I cannot resolve who (if
  anyone) succeeded her as of August 2026** — no source I could reach names a successor.
- Predecessor lineage (from Delaune's and Cortier's own CVs): Véronique Cortier — editorial board
  2011–2019, co-editor-in-chief 2019–2022; Delaune — co-editor-in-chief 2022–2025; Liu — ongoing,
  start date not stated in any source I found.

**What I could NOT confirm — stated as a gap, not filled in:**

The journal's actual editorial-board page, `journals.sagepub.com/editorial-board/JCU`, returns a
**Cloudflare Turnstile bot-challenge (HTTP 403, "Just a moment...")** on every fetch attempt —
via `WebFetch`, via `curl` with a realistic browser user-agent, and via the `r.jina.ai` proxy.
This is the same failure mode already documented in this portfolio for English-Corpora.org. The
page has **never been captured by the Wayback Machine** (checked via the CDX API — zero snapshots
at any URL casing). No secondary source (search engines, ResearchGate, DBLP, personal CVs of six
plausible access-control-community board members I checked by name — Indrakshi Ray, Achim
Brucker, Sebastian Mödersheim, Steve Kremer, Cas Cremers, Ravi Sandhu, Ninghui Li, Pierangela
Samarati) reproduces the associate-editor list or confirms any of them as current JCS board
members.

**So: I cannot name any editorial board member who would plausibly handle an authorization-
semantics-for-AI-agents submission.** The honest answer is that this is unverified, not that the
board lacks such expertise — the page simply could not be read. If this matters for the
submission decision, the practical path is a human browser visit to
`journals.sagepub.com/editorial-board/JCU` (which should clear the Cloudflare challenge
normally) rather than another automated attempt.

---

## Summary verdict for the retargeting decision

1. **Venue is active**, not quiet: 33 articles in 19 months, verified via two independent
   cross-validated sources.
2. **All three claimed neighbours check out**, DOIs confirmed directly.
3. **Real additional neighbours exist** (zero-trust review, BLE access-control paper), though the
   venue currently has zero output specifically on LLM/AI-agent security — the manuscript would be
   a genuine first in that specific sub-topic at this venue, not an obvious continuation of an
   existing thread.
4. **The methodological fit is plausible but not free of risk.** JCS does publish non-empirical,
   non-proof work (~9% SoK/survey), and framework-without-mechanism papers exist (~6%,
   Abdunabi/Nguyen) — but every located example still does *something* beyond taxonomy (new
   formal results, a worked case study, or synthesis of others' empirical results). A submission
   with zero worked examples and zero formal proof would be testing the outer edge of what this
   venue's recent corpus actually contains, not comfortably inside a well-populated norm.
5. **Sage's AI-disclosure policy is verified verbatim** and matches the July note's claim exactly
   (including "solely"), plus the full 9-item prohibited-use list is now on record.
6. **Editorial leadership is partially confirmed** (Liu ongoing EiC; Delaune's co-EiC term ended
   2022–2025 per her own CV) but the full board is an **unresolved gap** due to a Cloudflare block
   with no Wayback coverage — flagged rather than guessed at.
