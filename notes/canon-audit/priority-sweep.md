# Prior-art sweep: has anyone connected the formal access-control / authorization tradition to the LLM-agent interpretation problem?

Run 2026-08-08. Target manuscript: `delegation-assurance.tex` (+ `adversarial-pragmatics`), Brett Reynolds.

---

## BOTTOM LINE

**The ground is PARTLY TAKEN, and it was taken in the last six months.** Nothing occupies the
specific claim, but the scaffolding around it has been built out very fast and three of the five
hit-categories the brief listed are now occupied by other people.

Category by category:

| # | Criterion | Status |
|---|---|---|
| 1 | Formal authorization language/semantics for LLM agents that makes **classification of the NL string** part of the authorization decision | **OPEN.** Nothing does use/mention, quotation-vs-command, or speech-act status as an authorization input. OpenAlex full-text `"speech act" AND "agent security"` returns 7 works, one of which is Brett's own paper; `"contextual status" AND "authorization" AND "agent"` returns 3, none relevant (§1.2b). |
| 2 | Explicit extension of ABLP / SPKI-SDSI / Delegation Logic / SecPAL / UCON / XACML / RT / trust management to LLM agents | **TAKEN** (Ibrahim & Li, arXiv:2606.03518; also Kagal et al. arXiv:2606.19464 for the Rei deontic tradition). |
| 3 | Argument that access-control formalisms presuppose authenticated principals and pre-classified requests, and that language-mediated agents break that | **TAKEN, in a Blue Sky paper at SACMAT 2026** (Lin, Chen & Sun, DOI 10.1145/3750555.3811883): the tradition "binds identity to operation but not to runtime-negotiated operands." Elsewhere it appears only as a disclaimer: FAVA carves the NL step out of its own guarantee; two IETF drafts declare it out of scope; a third states it as a problem. |
| 4 | Formal **trajectory-/sequence-scoped** authorization (vs per-call) | **TAKEN, and more firmly than a position paper.** Reddi (SIGOPS OSR) makes the trajectory the unit over which *authority and evidence* are stated; Siu et al. (ICML 2026) require the four properties be evaluated "continuously across the agent's trajectory"; and **MATE (USENIX Security 2026)** is a working trajectory-scoped auditor over natural-language policies with a 140K-trajectory released benchmark. What is left is that all three are learned or architectural, not a formal semantics. |
| 5 | Independently-adjudicated status/authority vs the system's **assigned** status, failing in **both** directions | **OPEN as a framework; partly measured.** Klisura et al. (EACL 2026) evaluate LLM adherence to RBAC in both directions (refusal precision *and* false permits) with policy and role stipulated. And one grey-literature deposit (H7b) measures exactly one status misclassification — preference language read as permission — and names it "a non-adversarial authority-classification failure distinct from prompt injection." Nobody has a typed status space or a status/standing separation. |

**The single most dangerous finding** is not a formal-methods paper. It is
**Siu, He, Montgomery, Wang, Wang & Song, "Position: Agent Security Needs Redefinition through a
Holistic Framework," ICML 2026 (arXiv:2607.22024)**, with its companion formalization
(arXiv:2603.19469). It makes the manuscript's *motivating* move — agent security is an
authorization problem, not a content problem — as an ICML position paper from Dawn Song's group,
with "Source Authorization," trajectory-continuous evaluation, and indirect prompt injection
recast as Hardy's confused deputy. If the manuscript's contribution is *the reframing*, that
reframing now has a better-placed owner. What survives is the finer machinery: Siu et al. reduce
standing to **authentication**, which the manuscript already argues is the wrong reduction.

**What is still open, precisely.** Nobody has written an authorization semantics in which the
*contextual status of a string occurrence* (command in use / quotation / policy example / tool
result / retrieved content / memory) is a typed input to the authorization decision, separately
from the *standing* of its source, with both able to fail in either direction against an
independent adjudication. Every system found either (a) classifies by **provenance only** and
explicitly refuses to inspect content (LLMbda, CaMeL-lineage, PACT, AuthGraph), or (b) translates
the **user's task** into a policy and then treats the resulting policy as ground truth (FAVA,
PAuth, ASTRA, autoformalization-to-Cedar), or (c) treats the question as authentication (Siu et al.
and most of the rest).

One system does read content to decide authorization, and it is worth knowing about because it is
the exception that shows the shape of the gap: the FLAIRS 2026 BDI system (A19b) extracts
authorization context from document text *and* visual features like institutional logos and
security badges. But what it reads off are policy **attributes of a document** — this poster is
from institution X, so clearance Y applies — never the illocutionary status of an occurrence or the
standing of a source to direct an action.

**Positioning cost.** The manuscript's `02-existing-work.tex` currently cites South et al. 2025,
Kühlewind 2026, ScopeGate and AttriGuard for the "delegation protocols and access control"
subsection. That subsection is now materially incomplete and, as written, its gap claim
("the remaining gap lies in joining delegation infrastructure to language-status classification")
is *still true* but will read as uninformed unless it engages Siu et al., Ibrahim & Li, and Reddi
by name. Similarly `07-compositional-delegation.tex` needs to position against Ibrahim & Li, who
have already published a compositional delegation operator with soundness proofs.

**Reassurance withheld, twice over.**

*First:* the trajectory-first result (the manuscript's "third result") is the weakest of the three
novelty claims now. Reddi states it in SIGOPS OSR, Siu et al. state it in the ICML abstract, and
**MATE** (USENIX Security 2026) implements trajectory-scoped policy auditing over natural-language
policies with a 140K-trajectory benchmark released. The manuscript still has the *formal* version,
but "taking bounded trajectories rather than single actions as the primary object" can no longer be
presented as an observation the field has missed, and the seed benchmark now has a large competitor.

*Second, and more serious:* **two independent programmes now argue in print, at top venues, that
the manuscript's central move is the wrong one.** AttriGuard (USENIX Security 2026): *"Most existing
defenses treat IPI as an input-level semantic discrimination problem, which often fails to
generalize to unseen payloads."* LLMbda (Gordon & Sands): the principled line *"abandons content
inspection in favour of provenance."* CaMeL (SaTML 2026) makes the same bet architecturally. That is
not a gap in the literature; it is a position against the manuscript's, held by good people with
proofs and benchmarks. The paper needs an argument for why status classification is necessary
*despite* their results, not merely a claim that nobody has done it. The strongest available line is
the one the earlier same-day audit identified: these systems do not solve the classification
problem, they **exclude the class of cases where it arises**, and each says so in its own
assumptions (CaMeL §3's trusted-prompt assumption is the cleanest example).

---

## 1. FULL QUERY LOG

Every query below was actually executed. Where a call failed, that is recorded as a failure, not
as a zero result.

### 1.1 Semantic Scholar citation graph — recent (2023+) citers of the classics

Endpoint: `https://api.semanticscholar.org/graph/v1/paper/{id}/citations?fields=title,year,externalIds,venue,abstract,authors&limit=100&offset=N`

| Seed | Resolved title (verified) | Citers pulled | 2023+ |
|---|---|---|---|
| `DOI:10.3233/JCS-2009-0364` | SecPAL: Design and semantics of a decentralized authorization language | 346 | 14 |
| `DOI:10.1145/984334.984339` | The UCON_ABC usage control model | 1000 (cap) | 80 |
| `DOI:10.1145/605434.605438` | Delegation logic | 28 | 11 |
| `DOI:10.1145/155183.155225` | A calculus for access control in distributed systems (ABLP) | 739 | 13 |
| `DOI:10.1145/54289.871709` | The Confused Deputy | 431 | **84** |
| `DOI:10.1145/138873.138874` | Authentication in distributed systems (Lampson et al., speaks-for) | 734 | 13 |
| `DOI:10.17487/RFC2693` | SPKI Certificate Theory | 742 | 10 |
| `DOI:10.1109/SECPRI.1996.502679` | Decentralized trust management (Blaze/Feigenbaum/Lacy) | 800 (cap) | 47 |
| `DOI:10.1109/LICS.2003.1210062` | Logic in access control (Abadi) | 178 | 8 |
| `DOI:10.1109/SECPRI.2002.1004366` | Design of a role-based trust-management framework (RT) | 156 | 16 |
| `DOI:10.1109/2.485845` | Role-based access control models (RBAC96) | 304 (2023+) | 304 |

**Two seed DOIs initially resolved to the wrong paper and were corrected**: `10.1145/54289.871709`
replaced a bogus CorpusID for Hardy (which had resolved to a 2016 brain-cell-culture paper), and
`10.1109/SECPRI.2002.1004366` replaced `10.1109/SECPRI.2002.1004374`, which is Park/Chan/Song on
multicast packet authentication, not RT. Both corrections were verified by title before use.
This is the exact failure mode the brief warned about; it happened twice and was caught.

The confused-deputy list (84 items) is the highest-yield single artifact of the whole run and is
saved in full at `/tmp/claude-agent-output/apsearch/s2_citers3.json`.

### 1.2 OpenAlex — independent cross-check of the same citation graph

Endpoint: `https://api.openalex.org/works?filter=cites:{W-id},from_publication_date:2023-01-01&search={term}`
run for terms `agent`, `large language model`, `LLM`, `prompt injection`, against
SecPAL (W2167122335), UCON (W2068189899), Delegation Logic (W2020992910), ABLP (W1987339920),
Confused Deputy (W2056073317), SPKI RFC2693 (W2105470748).

Result: OpenAlex reproduced the Semantic Scholar picture and added four items S2 had missed
(Reddi SIGOPS OSR; two SSRN preprints; the CHI EA landscape paper). SPKI returned **zero**
agent/LLM citers on OpenAlex against ten on S2 — a real coverage difference, so neither index
alone is sufficient.

### 1.2b OpenAlex full-text search — the sharpest evidenced negatives in this report

Endpoint: `https://api.openalex.org/works?filter=fulltext.search:{q},from_publication_date:2023-01-01`.
This searches indexed **full text**, not titles/abstracts, so it bounds the space far more tightly
than the arXiv `all:` queries.

| Query | Count | What is in it |
|---|---|---|
| `"speech act" AND "agent security"` | **7** | **One of the seven is Brett's own arXiv:2607.01153.** The others are Chinese national-security discourse, an Electronic Imaging paper on protocol translation, ClawSafety, AttriGuard, a Web-of-Agents survey, and a multi-agent architecture paper. **Nobody else combines speech-act theory with agent security.** |
| `"contextual status" AND "authorization" AND "agent"` | **3** | Digital-twin 6G networks, an XR robotics middleware paper, and a Ukrainian media-semiotics thesis. Zero relevant. |
| `"instruction status" AND "authorization" AND "agent"` | **1** | A KIT privacy-DFD paper. Zero relevant. |
| `"language-mediated" AND "authorization"` | 59 | Almost entirely medical sociology, ritual semiotics, and education. Two AI items (an agent-OS paper; "The Agentic Trust Fabric" TechRxiv systematization), neither on point. |
| `"authorization" AND "use-mention"` | 50 | Forensic genetics, ethnobotany, dermatology. Zero relevant — the two terms simply never co-occur in this literature. |
| `"quotation" AND "prompt injection"` | 137 | Prompt-hacking competitions (Tensor Trust, HackAPrompt), firewalls, RAG reviews. No use/mention treatment; "quotation" is incidental. |
| `"authorization logic" AND "large language model"` | 65 | Secure-code-generation, ABAC explainability, MCP manifest signing, serverless least privilege. Two worth naming: **"BDI Agent-Based Access Control Reasoning for Multimodal Retrieval-Augmented Generation," FLAIRS 2026, DOI 10.32473/flairs.39.1.141759** (belief-desire-intention agents doing access-control reasoning over RAG — the only BDI-tradition item found), and **"Give Them an Inch and They Will Take a Mile: Understanding and Measuring Caller Identity Confusion in MCP-Based AI Systems"** (arXiv, id not captured; caller-identity confusion is the standing question at the protocol layer). Neither classifies string status. |

**These six rows are the load-bearing negative of the whole report.** They are full-text, indexed,
reproducible, and they show the manuscript's core vocabulary pairing (status/use-mention/speech act
× authorization/agent security) is essentially unoccupied.

### 1.3 arXiv API — 69 full-text queries across four sweeps

Endpoint: `http://export.arxiv.org/api/query?search_query={q}&max_results=8..40&sortBy=submittedDate`

Sweep 1 (30 queries):
`all:"authorization logic" AND all:"LLM"` ·
`all:"authorization logic" AND all:"agent" AND all:"language model"` ·
`all:"access control" AND all:"large language model" AND all:"formal semantics"` ·
`all:"delegation logic" AND all:"AI agent"` ·
`all:"SecPAL"` ·
`all:"usage control" AND all:"LLM"` ·
`all:"trust management" AND all:"language model"` ·
`all:"prompt injection" AND all:"access control" AND all:"formal"` ·
`all:"instruction hierarchy" AND all:"authorization"` ·
`all:"capability security" AND all:"LLM agent"` ·
`all:"confused deputy" AND all:"LLM"` ·
`all:"confused deputy" AND all:"agent"` ·
`all:"speaks for" AND all:"authorization" AND all:"agent"` ·
`all:"principal" AND all:"authorization" AND all:"LLM agent"` ·
`all:"trajectory" AND all:"authorization" AND all:"agent"` ·
`all:"sequence-level" AND all:"authorization"` ·
`all:"XACML" AND all:"LLM"` ·
`all:"SPKI" AND all:"agent" AND all:"LLM"` ·
`all:"authorization semantics" AND all:"agent"` ·
`all:"use-mention" AND all:"LLM"` ·
`all:"speech act" AND all:"prompt injection"` ·
`all:"directive" AND all:"classification" AND all:"authorization" AND all:"agent"` ·
`all:"authority" AND all:"utterance" AND all:"agent" AND all:"security"` ·
`all:"pragmatics" AND all:"AI safety" AND all:"evaluation"` ·
`all:"authorization" AND all:"natural language" AND all:"agent" AND all:"policy"` ·
`all:"information flow control" AND all:"LLM agent"` ·
`all:"reference monitor" AND all:"LLM agent"` ·
`all:"authenticated delegation" AND all:"AI agent"` ·
`all:"agent authorization" AND all:"OAuth"` ·
`all:"formal" AND all:"delegation" AND all:"agentic AI"`

Sweep 3 (8 queries, targeting category 5 — recognition failure in both directions):
`all:"over-refusal" AND all:"authorization"` (5) ·
`all:"false refusal" AND all:"agent" AND all:"authority"` (**0**) ·
`all:"ground truth" AND all:"authorization" AND all:"adjudicat"` (**0**) ·
`all:"both directions" AND all:"recognition" AND all:"authority"` (3, all irrelevant) ·
`all:"legitimate instruction" AND all:"rejected" AND all:"agent security"` (**0**) ·
`all:"authorized but refused" OR all:"unauthorized but executed"` (5) ·
`all:"inter-rater" AND all:"agent security"` (**0**) ·
`all:"annotation" AND all:"authorization" AND all:"agent" AND all:"agreement"` (3, all irrelevant).
This sweep is what surfaced H7 and H8, both of which the earlier sweeps had missed — a reminder
that the negative was softer than it looked before it was run.

Sweep 4 (6 queries, closing the earlier audit's residual list): `all:"ETDI" AND all:"tool
definition"` · `ti:"IPIGuard"` · `all:"Fides" AND all:"information flow" AND all:"agent"` ·
`au:"Cecchetti" AND all:"prompt injection"` · `ti:"MiniScope"` · `all:"least privilege" AND
all:"tool calling agents"`.

Sweep 2 (25 queries):
`all:"authorization" AND all:"quotation" AND all:"agent"` ·
`all:"mentioned" AND all:"used" AND all:"instruction" AND all:"agent security"` ·
`all:"deontic" AND all:"LLM agent"` ·
`all:"normative" AND all:"authorization" AND all:"LLM"` ·
`all:"authority" AND all:"delegation" AND all:"trace" AND all:"audit" AND all:"LLM"` ·
`all:"policy language" AND all:"LLM agent"` ·
`all:"Datalog" AND all:"LLM agent" AND all:"policy"` ·
`all:"formal semantics" AND all:"agentic"` ·
`all:"authorization" AND all:"speech" AND all:"classification" AND all:"LLM"` ·
`all:"cumulative" AND all:"authorization" AND all:"agent" AND all:"trajectory"` ·
`all:"multi-step" AND all:"authorization" AND all:"LLM agent"` ·
`all:"session-scoped" OR all:"task-scoped" AND all:"authorization" AND all:"agent"` ·
`all:"Zanzibar" AND all:"agent"` ·
`all:"Cedar" AND all:"agent" AND all:"LLM"` ·
`all:"OPA" AND all:"Rego" AND all:"LLM agent"` ·
`all:"authorization" AND all:"provenance" AND all:"LLM agent"` ·
`all:"assurance case" AND all:"AI agent" AND all:"authorization"` ·
`all:"safety case" AND all:"agent" AND all:"delegated authority"` ·
`abs:"authorization" AND abs:"language-mediated"` ·
`all:"instruction-data separation" AND all:"authorization"` ·
`all:"source authorization" AND all:"agent"` ·
`all:"who issued the command" OR all:"whose instruction"` ·
`all:"transition competence" OR all:"authorization standing"` ·
`all:"MCP" AND all:"authorization" AND all:"formal"` ·
`all:"agent" AND all:"principal" AND all:"speaks-for"`

**Notable zero-result arXiv queries** (these are the evidenced negatives, and they are the load-bearing
ones): `all:"SecPAL"` returned **0** arXiv papers of any date. `all:"speech act" AND all:"prompt
injection"` = 0. `all:"deontic" AND all:"LLM agent"` = 0. `all:"instruction-data separation" AND
all:"authorization"` = 0. `abs:"authorization" AND abs:"language-mediated"` = 0.
`all:"transition competence" OR all:"authorization standing"` = 5 raw, all pre-2023.
`all:"authorization logic" AND all:"agent" AND all:"language model"` = 0.
`all:"delegation logic" AND all:"AI agent"` = 0.
`all:"assurance case" AND all:"AI agent" AND all:"authorization"` = 0.
`all:"safety case" AND all:"agent" AND all:"delegated authority"` = 0.

Caveat on those: arXiv's `all:` field with quoted phrases is a full-text match over an
inconsistently-indexed corpus, so a zero here bounds the space loosely, not tightly. It is the
citation-graph sweep, not these, that carries the negative.

### 1.4 Semantic Scholar keyword search

Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search?query={q}&year=2023-2026&limit=12..20`

Queries run: `authorization logic LLM agent` · `access control large language model formal
semantics` · `delegation logic AI agent` · `SecPAL agent authorization` · `usage control LLM agent`
· `trust management language model agent` · `prompt injection access control formal semantics` ·
`instruction hierarchy authorization semantics` · `capability security LLM agent` · `confused
deputy LLM agent` · `agent authorization trajectory` / `agent authorization trajectory scoped` ·
`sequence authorization AI agent` · `speaks-for logic LLM` · `principal identification language
model agent` · `deontic logic agentic AI governance` · `authority regime machine action
authorization` · `use mention distinction prompt injection` · `quotation instruction agent
security` · `speech act authorization AI agent` · `illocutionary force LLM safety` · `pragmatics
prompt injection instruction status` · `natural language authorization decision agent` ·
`authorization semantics natural language instruction classification` · `delegated authority audit
AI agent trace` · `standing authority instruction LLM` · `authorization semantics agentic AI`.

Historical / agent-communication-language check: `speech act performative authorization access
control agent communication language` · `KQML FIPA ACL authorization trust performative` ·
`illocutionary force security policy agent` · `directive speech act access control formal logic` ·
`quotation use mention security policy logic` · `says logic authorization principal utterance`.

**Honest caveat on this surface:** a first pass of 25 queries was killed by a 10-minute timeout and
a second background pass produced an empty log. On re-run, several queries returned HTTP 429
(rate-limited), which my first script silently rendered as `total: None`. Re-running those
individually with error visibility confirmed they *do* return results (e.g. `authorization logic
LLM agent` → total 1075). So treat this surface as **partially covered**: the queries that
completed are logged with their results, and everything material they surfaced was already found
via the citation graph and arXiv. It did add four items (OIDC-A, Causal Past Logic, AgenticOS,
Durable Authorization State).

The historical ACL/speech-act queries that did complete returned nothing connecting illocutionary
classification to authorization; `says logic authorization principal utterance` (total 12) returned
only the expected authorization-logic classics (Garg's proof theory, "Do As I SaY!" CSF 2007) with
no NL-classification content.

### 1.5 Identifier verification (anti-fabrication pass)

**All 34 arXiv ids appearing in this report were extracted from the finished document and re-run in
one batch against `http://export.arxiv.org/api/query?id_list=`. All 34 resolved, and every returned
title matched the title claimed here. Zero not-found, zero mismatches.** All 11 DOIs were
round-tripped through `https://api.crossref.org/works/{doi}` and confirmed by title and date; zero
failures.

One cosmetic discrepancy, recorded rather than smoothed over: arXiv's metadata for 2607.22024 gives
the title as "Agent Security Needs Redefinition through a Holistic Framework"; the rendered paper
and its HTML `<title>` both prefix it "Position:". Either form is citable.

### 1.5b Crossref verification

Every DOI reported below was round-tripped through
`https://api.crossref.org/works/{doi}` and confirmed by title and date. Eleven DOIs verified;
zero failures. Every arXiv id below was round-tripped through
`http://export.arxiv.org/api/query?id_list=` and confirmed by title, authors and date.

### 1.6 Web search

`"Treacherous Envoy Problem" SACMAT 2026 Lin Chen Sun multi-agent workflows accountability` ·
`"confused deputy" LLM agent authorization logic "speaks for" OR SecPAL OR "delegation logic" 2026`.

Note: the second search's synthesis asserted several things I could **not** verify and am therefore
**not** reporting as findings — a "VIGIL framework by Lin et al." with a specific 22% number, a
"CoSAI Agentic Identity and Access Management Framework published April 17," a NIST agent-identity
concept paper, and a Berkeley Technology Law Journal blog post. Treat all four as unverified leads.
(An arXiv paper titled *VIGIL: Runtime Enforcement of Behavioral Specifications in AI Agent Skills*,
arXiv:2606.26524, does exist and was verified, but it is by Ying Li et al., not the Lin et al. the
search synthesis named, and I did not verify the 22% claim.)

### 1.7 ACM Digital Library

**Blocked.** `dl.acm.org/doi/...` returned HTTP 403 on every attempt (Cloudflare). Fallbacks used
instead: Crossref for metadata, Semantic Scholar's abstract field, and OpenAlex. This means the
two SACMAT 2026 papers and the SIGOPS OSR paper below are rated **from verified abstracts, not from
full text.** That is a real limitation and is flagged per-item.

### 1.8 IETF / standards (delegated, completed)

Full log at `/tmp/claude-agent-output/ietf-agent-auth-drafts.md`. Summarised in §4.

### 1.9 DBLP / security-venue sweep (delegated, then salvaged by hand)

**The delegated agent wrote only a section skeleton** — `venue-sweep-accesscontrol-llm.md` is 805
bytes of headings with "(filled in below)" under each. Its report is worthless. Its **raw dumps are
not**, and I parsed them myself rather than lose the surface:

- `sacmat.txt`, `asiaccs.txt`, `codaspy.txt` — Crossref container-title pulls, 2024–2026
- `venues/sec.txt`, `sec2.txt`, `sec3.txt` — DBLP venue streams for CCS, S&P, USENIX Security, NDSS,
  ESORICS, SACMAT, DSN, ICISS, ACSAC, EuroS&P
- `dblp/batch1.txt`, `batch1b.txt`, `batch2.txt` — DBLP publication search
  (`https://dblp.org/search/publ/api?q={q}&format=json&h=100`) on: `authorization agent LLM`
  (**parse error, no result**), `access control large language model`, `delegation LLM agent`,
  `authorization LLM agent`, `authorization logic agent` (**0**), `confused deputy LLM`,
  `agentic access control`, `agentic authorization`, `authorization agentic AI`,
  `access control agentic`
- `cr_batch1.txt` — Crossref bibliographic queries
- `oa_batch1.txt` — OpenAlex title-and-abstract queries

What that surface added beyond everything above:

**One publication-status correction that matters.** H7, Klisura et al. "Role-Conditioned Refusals,"
is **not** preprint-only: DBLP has it as **EACL 2026**, key `conf/eacl/KlisuraKKKR26`. It is a
peer-reviewed \*ACL paper, which raises its weight as a comparator considerably.

**A second SACMAT 2026 Blue Sky paper on the same theme**, which the citation graph missed because
it cites none of the classics: **Rubio-Medrano, N. & S. (2026), "Towards Agentic AI for Access
Control in Cyber-infrastructures: Exploring the Security and Human Factors [BlueSky Paper],"**
SACMAT 2026, DBLP `conf/sacmat/Rubio-MedranoNS26`. So SACMAT 2026 ran **two** blue-sky papers on
agentic access control. The venue is actively soliciting this.

**Peer-reviewed venue items not otherwise surfaced** (all resolved in a fetched API response):
"Access Controlled Website Interaction for Agentic AI with Delegated Critical Tasks," WWW 2026,
DOI 10.1145/3774904.3792864; "Permissioned LLMs: Enforcing Access Control in Large Language
Models," NeurIPS 2025 (`conf/nips/JayaramanMMSK25`, arXiv 2505.22860); "Prompt Injection Attack to
Tool Selection in LLM Agents," NDSS 2026 (`conf/ndss/ShiYTZGS26`); "Lineage: A UMA2.0 Protocol
Extension for Multi-Hop LLM Agent Delegation," IEEE Access 2026, DOI 10.1109/access.2026.3708618;
"MCP-Secure: A Runtime Access Control Layer for Privilege-Aware LLM Agent Tooling," IEEE OJ-CS
2026; "CapChain: A Capability-Token Access Control Architecture with Verifiable Provenance for
Multi-Agent LLM Systems," Applied Sciences 2026; "Consent collapse in agentic AI: moral
authorization beyond the boundaries of task delegation," *AI and Ethics* 2026,
DOI 10.1007/s43681-026-01287-w. Also a fourth Santos-Grueiro paper, "Temporary Authority, Permanent
Effects: Commit-Time Authorization for LLM Agents," arXiv 2607.10487.

**And a warning about the surface itself.** OpenAlex's `"authorization" AND ("LLM agent" OR
"agentic")` returns a 2026 cluster of Zenodo / SSRN / TechRxiv self-published items on exactly the
manuscript's vocabulary — "Authority versus Authorization: A Definitional Framework for AI
Governance" (10.5281/zenodo.21341907, Edward Meyman), "Authority Before Execution"
(10.5281/zenodo.18327665, Mark T. Menard), "Delegated Authority Without Accountability"
(10.5281/zenodo.21786828, Bjorn Bjornsvik), "Execution-Time Authorization for AI Agents: A Formal
Framework for Deterministic Governance Boundaries" (10.2139/ssrn.6300558), "Execution-Witness
Binding: Proof-Carrying Authorization for LLM Agent Runtimes" (10.2139/ssrn.6352164), and a dozen
more. **None is peer reviewed and several come in serial families from one author with duplicate
DOIs.** They do not threaten priority in any sense a journal would recognise, but they do mean the
manuscript's title vocabulary is crowded, and a naive search by a reviewer will surface them.

---

## 2. HIT LIST BY SEVERITY

### SUBSTANTIAL OVERLAP

**H1. Siu, He, Montgomery, Wang, Wang & Song (2026). "Position: Agent Security Needs Redefinition
through a Holistic Framework." ICML 2026 position paper.** arXiv:2607.22024v1, submitted
2026-07-24, cs.CR/cs.AI. Companion: **Siu, He, Montgomery, Wang, Gong, Wang & Song (2026), "A
Framework for Formalizing LLM Agent Security," arXiv:2603.19469v1, 2026-03-19** (UC Santa Cruz / UC
Berkeley / Duke).

*What it does.* Argues agent security is contextual, not content-based, and operationalises this
as four properties that must hold jointly and be "evaluated continuously across the agent's
trajectory": **Source Authorization** ("Who issued the command, and does that source have
authority?"), Task Alignment, Action Alignment, Data Isolation. Recasts indirect prompt injection
as a Source Authorization violation, verbatim: *"Indirect prompt injection is the confused deputy
problem (Hardy, 1988) in agent form, with the agent using its own authority to carry out a request
whose source has none."* Maps each property to a classical-security ancestor (Hardy 1988; Saltzer &
Schroeder 1975; Anderson 1972; Abadi et al. 2009 CFI; Denning 1976; Goguen & Meseguer 1982). States
*"Snapshot benchmarks that reset context between tasks cannot see these patterns by construction."*
The companion paper supplies oracle functions and a formal definition, and formalises confused
deputy as `(s_user, s_target) ∉ R ∧ (s_agent, s_target) ∈ R`.

*Why this is the most dangerous hit.* It makes the manuscript's motivating reframing, with better
institutional placement, four months earlier, in the venue that sets the agenda for this literature.

*What it does not do — verified by full-text keyword scan of both papers.* Neither paper contains
a single occurrence of SecPAL, speaks-for, SPKI, SDSI, Delegation Logic, UCON, XACML, trust
management, Lampson, Sandhu, RBAC, reference monitor (as a cited primitive in 2603.19469),
authorization logic, Datalog, or policy language. Neither contains "quotation," "use-mention,"
"speech act," or "pragmatic." "Standing" appears in 2603.19469 six times, all inside
"understanding." Its whole treatment of the manuscript's *status* and *standing* fields collapses
into one predicate: whether the source is **authenticated**. That is precisely the reduction
`02-existing-work.tex` already argues against ("message channel, storage location, and technical
trust bear on whether a source can confer or alter authority only insofar as the governing regime
recognizes them").

*Action.* Must be cited and engaged head-on, probably in the introduction, not buried in related
work. The manuscript's differentiator against it is the authentication/standing distinction and the
status classification, and both need to be stated explicitly against these two papers.

---

**H2. Ibrahim & Li (2026). "Overlaying Governance: A Compositional Authorization Framework for
Delegation and Scope in Agentic AI."** arXiv:2606.03518v1, submitted 2026-06-02, cs.AI/cs.CR.

*What it does.* The clean category-2 hit. Builds delegation types for agentic AI directly on the
decentralized-authorization and trust-management logics, citing **Li, Grosof & Feigenbaum 2003
(Delegation Logic)** and **Becker, Fournet & Gordon 2007 (SecPAL)** at §3.2, **Ellison et al. RFC
2693 (SPKI)** and **Appel et al. Nexus Authorization Logic (CSF 2014)** at §6, plus ReBAC/Zanzibar/
OpenFGA/Cedar/XACML. Defines four delegation types including *"Full delegation (unconditional
'speaks-for')"*, scoped delegation with attenuation, conditional delegation, and depth-bounded
delegation with bound K. Defines a compositional operator overlaying agentic semantics onto existing
relational policies via graph transformation, with **preservation and agent-authorization soundness
proofs** plus runtime benchmarks. Claims: *"To the best of our knowledge, no prior work defines a
contractual notion of delegation together with a compositional operator to operationalize AI
governance primitives."*

*Severity for the manuscript.* Directly threatens `07-compositional-delegation.tex`. Anyone
reviewing that section will ask why Ibrahim & Li is not there.

*What it does not do — verified by full-text scan.* Zero occurrences of "natural language,"
"classification," "utterance," "trajectory," or "sequence." Prompt injection appears six times,
purely as motivation; the response is privilege constraint, never language classification. It
assumes requests arrive attributable to graph-resident principals. So it takes category 2 and
leaves categories 1, 4 and 5 alone.

---

**H3. Reddi (2026). "Architecting the Agentic AI Systems Stack: What Should Infrastructure Manage
When the Unit of Work Is a Trajectory?"** ACM SIGOPS Operating Systems Review, 2026-07-13.
DOI 10.1145/3830422.3830429 (Crossref-verified). Single author: Vijay Janapa Reddi.
**Rated from verified abstract only — ACM DL 403.**

*What it does.* Argues the agentic trajectory should be a system-visible managed unit. The load-
bearing sentence: *"The trajectory is the smallest unit over which budget, **authority**, recovery,
**evidence**, and physical cost can be stated without hiding essential state in application
convention."* Develops a "managed trajectory" contract covering identity, goals, budgets, memory,
authority, effects, evidence, and recovery.

*Severity.* This states the manuscript's third result — trajectory rather than single action as the
primary object for authority *and* evidence — as a design premise, in a systems venue, one month
before this sweep. The manuscript still has the formal version (cumulative limits, joint
disclosure, prohibited terminal states, TrajAuth_R), and Reddi is an architecture agenda paper
rather than a semantics. But "many current agent mechanisms operate per call" can no longer be
framed as an unnoticed gap.

---

**H4. Garby, Gordon & Sands (2026). "The LLMbda Calculus: AI Agents, Conversations, and Information
Flow."** arXiv:2602.20064v2, submitted 2026-02-23, revised 2026-07-10, cs.PL/cs.AI/cs.CR.
(Edinburgh / Chalmers–Gothenburg.)

*Why it matters institutionally.* **Andrew D. Gordon is a SecPAL co-author.** If anyone was going
to connect the authorization-logic tradition to LLM agents, this was the most likely author. He did
not. Full-text scan of the 30k-word PDF: SecPAL 0, speaks-for 0, SPKI 0, Delegation Logic 0,
authorization logic 0, UCON 0, XACML 0, trust management 0, confused deputy 0. The tradition it
plugs into instead is information-flow control: Arden/Liu/Myers flow-limited authorization,
Askarov/Myers declassification, nonmalleable information flow.

*What it does.* An untyped call-by-value lambda calculus with first-class prompt-response
conversations (fork/clear), code generation, and dynamic IFC in which every value carries a label
propagated by every reduction. Central result: termination-insensitive probabilistic
noninterference over the whole calculus, plus an insulated variant, all machine-checked in Lean, with
the verified interpreter serving as the actual agent harness. Evaluated on AgentDojo banking.

*Why it is a genuine competitor and also useful ammunition.* It is the strongest formal-semantics
work in the space, and it makes **the opposite methodological bet** to the manuscript, explicitly:
*"The most principled defences replace content inspection with provenance — classifying data by
source"* and *"A more principled line of work has emerged that abandons content inspection in favour
of provenance."* That is a stated, defended, proof-backed position that classification of the
occurrence is the wrong place to intervene. The manuscript should engage it as the live opposing
view, not ignore it.

---

**H5. Mishra & Sharad (2026). "Observability for Delegated Execution in Agentic AI Systems."**
arXiv:2606.09692v1, 2026-06-08, cs.CR/cs.AI.

*What it does.* Opens with: *"Delegation-scoped execution is not identifiable from standard
observables: audit logs and execution traces can be identical under multiple incompatible
delegation assignments."* Argues delegation-scoped reconstruction from causal structure alone is
"structurally underdetermined" for LLM agents, and proposes a gateway plus common information model
that binds delegation context at execution time.

*Severity.* This is adjacent to the manuscript's **first result** (a complete, internally consistent
trace is compatible with the action being unauthorized) and to the evidentiary-assurance companion.
It is an identifiability claim rather than a normative-vs-representational separation, so it is not
the same result — but a reviewer will read them as neighbours and the manuscript should say why
they differ.

---

**H6. Lin, Chen & Sun (2026). "The Treacherous Envoy Problem: Trust, Collusion, and Accountability
in Multi-Agent Workflows [Blue Sky Paper]."** SACMAT 2026 (31st ACM Symposium on Access Control
Models and Technologies), Waterloo ON, 2026-07-08. DOI 10.1145/3750555.3811883
(Crossref-verified). Zhiqiang Lin (Ohio State), Shuo Chen (Microsoft Research), Huan Sun (Ohio
State). NSF 2112471 + Schmidt Sciences Safety Science award. **Full text obtained from the author's
page (`zhiqlin.github.io/file/SACMAT26.pdf`) after ACM DL 403 — read, not rated from abstract.**

*Upgraded from ADJACENT after reading.* This is the closest published statement of the brief's
**category 3**, and it is in the access-control venue, citing the right lineage. Its related-work
paragraph is the sentence the manuscript is trying to write:

> *"Classical access control (RBAC/ABAC), authorization logics and trust management [ABLP 1993;
> SecPAL 2010], policy languages (XACML), relationship or tuple-based authorization (Zanzibar),
> attenuated credentials (macaroons), OAuth, usage control (UCON), and graph-based frameworks (NGAC)
> **bind identity to operation but not to runtime-negotiated operands**; TEP binds such operands and
> couples conformance with bounded disclosure under [collusion]."*

*What it does.* Formulates detection as one decision problem over a **natural-language delegation
N**, public tool-side effects, and released artifacts: can a principal decide whether an envoy acted
treacherously in time to abort, or otherwise with evidence sufficient for adjudication and
accountability, when agents may collude and there is no trusted mediator? Argues structural hardness
via a trilemma of expressive NL negotiation, verifiable conformance of effects to intent, and
bounded disclosure, with formal (information-theoretic, Fano-based) evidence for two coupling edges.
It even has a **formal result about language interpretation inside the authorization problem**:
*"under any natural-language metric that treats hedged and unhedged phrasings as close, maximal
soundness forces a strict change in the extracted constraint. Robustness therefore cannot be
obtained for free; it must be traded against either specificity or soundness."*

*What it does not do — verified by full-text scan.* Zero occurrences of speaks-for, SPKI, Delegation
Logic, use-mention, quotation, mention, speech act, pragmatic, directive, **status**, **standing**,
or **trajectory**. Its gap is *runtime-negotiated operands* — the values in a deal — not the
*contextual status of an occurrence* or the *standing of its source*. It also never treats
recognition failure in both directions. And it is a Blue Sky paper: it names a problem and lists
research directions rather than supplying a semantics.

*Net effect on the manuscript.* Category 3 is no longer virgin ground, and the manuscript can no
longer be the first to say that the access-control tradition presupposes something language-mediated
agents break. But TEP is an **invitation** in exactly the direction the manuscript goes, from
authors with access-control-community standing, and citing it converts a bare gap claim into a
claim someone else independently identified from inside SACMAT. Use it that way.

**H7. Klisura, Khoury, Kundu, Krishnan & Rios (2025). "Role-Conditioned Refusals: Evaluating Access
Control Reasoning in Large Language Models."** arXiv:2510.07642v1, 2025-10-09, cs.CL. (UT San
Antonio / Cisco. **Ram Krishnan is at UTSA's Institute for Cyber Security — Sandhu's group**, i.e.
this is the RBAC community itself building an LLM evaluation.)

*Why this is here and not under ADJACENT.* It is the closest existing thing to the **benchmark**
half of the project, and it is the only work found that measures recognition failure in **both
directions**. It studies "the LLM's ability to adhere to access control policies by answering when
authorized and refusing when not," on a purpose-built dataset extending Spider and BIRD with
realistic PostgreSQL role-based policies at table and column level, comparing prompting, a
two-step generator–verifier, and LoRA fine-tuning. It reports both **refusal precision** and
**false permits**, and finds that "longer and more complex policies consistently reduce the
reliability of all systems." Datasets and code released.

*What it does not do.* The authorization side is stipulated RBAC over database roles: the policy is
given, the requester's role is given, and the only question is whether the model's SQL respects it.
There is no status classification (nothing about whether a string is a command, a quotation, or
data), no standing question (the role is authenticated by construction), and no adversarial or
pragmatic manipulation of instruction status. It is the RBAC-reasoning benchmark, not the
language-status benchmark.

*Action.* The adversarial-pragmatics seed benchmark must cite this and say what it measures that
this does not. A reviewer from the access-control community will know it.

**H7b. de Angel Garcia (2026). "When Preference Sounds Like Permission: Role-to-Consent Confusion in
Tool-Using LLM Agents."** Zenodo, deposited 2026-06-29, DOI 10.5281/zenodo.21023615, resource type
**Software** (a "defensive security-research lab"). Verified directly against the Zenodo API.

*This is the closest single item in the entire sweep to the manuscript's core claim.* Its own
description: tool-using LLM agents "can misclassify low-authority **preference language** as
**authorization** (role-to-consent confusion), **a non-adversarial authority-classification failure
distinct from prompt injection**." It ships a pre-registered confirmatory benchmark on GPT-4.1 and
Claude Sonnet 4.5, a measured prompt-versus-gateway mitigation comparison, and an exploratory
mechanistic probe on Qwen2.5-7B.

Preference versus permission is a speech-act-force distinction, and treating its misclassification
as an authority-classification failure separate from injection is exactly the manuscript's move,
measured. This is the one thing found that would make a reviewer ask "hasn't this been done?"

*Why it does not settle the question, stated carefully rather than dismissively.* It is a Zenodo
software deposit, not a peer-reviewed paper, and it sits inside a large 2026 cluster of
self-published grey literature on the same vocabulary (§1.9), some of it in serial families with
duplicate DOIs. It covers **one** contrast (preference vs permission) rather than a typed status
space, and there is no authorization semantics, no standing/status separation, and no connection to
the access-control tradition. On the evidence available — a metadata record, since the deposit is a
code artifact rather than a paper — it is a measurement of one instance of the phenomenon, not a
framework for it. **But it is the one item Brett should look at personally before deciding how to
word the benchmark's novelty claim.**

**H8. Li, Liu, He, Zhao, Li & Xu (2026). "Chain-of-Authorization: Embedding authorization into large
language models."** arXiv:2603.22869v2, 2026-03-24, revised 2026-04-03, cs.AI. Fine-tunes on
synthesized data with "complex permission topologies" so the model must emit a **structured
authorization trajectory** as a causal prerequisite for any substantive response or action, on the
argument that "existing defense mechanisms are fundamentally decoupled from internal reasoning."
Relevant because it puts the authorization decision *inside* the model rather than at a gate, which
is a live alternative the manuscript's gate-based framing should acknowledge. Its "authorization
trajectory" is a reasoning chain, not a bounded execution trajectory, so it does not take category 4.

### ADJACENT

*(A1 was the Treacherous Envoy paper; it was promoted to H6 once the full text was obtained.
Numbering left as-is so the two ratings stay traceable.)*

**A2. Sharma, Jiang, Lin & Chen (2026). "PAuth — Precise Task-Scoped Authorization For Agents."**
arXiv:2603.17170v1, 2026-03-17, cs.CR/cs.AI/cs.PL. Same group as A1. Proposes that "submitting an
NL task implicitly authorizes only the concrete operations required for its faithful execution,"
enforced via "NL slices" (symbolic specifications derived from the task) and "envelopes" binding
each operand's value to its symbolic provenance. Prototyped in AgentDojo. This is the closest work
to category 1 — but it derives authorization from the *user's* NL task, and never classifies the
status of an occurring string.

**A3. Fan, Li, Tian, Wang, Li & Wang (2026). "The Granularity Mismatch in Agent Security:
Argument-Level Provenance Solves Enforcement and Isolates the LLM Reasoning Bottleneck" (PACT).**
arXiv:2605.11039v1, 2026-05-11. *"Indirect prompt injection becomes dangerous not when untrusted
content appears in context, but when it determines an authority-bearing argument."* Assigns
semantic roles to tool arguments and checks role-specific trust contracts. Explicitly "reframes
agent security as authority binding." Provenance-only; no status classification.

**A4. Zhang, Zhao, Liu, Lou, Cheng & Liu (2026). "FAVA: Formal Authorization for Verified Agents
with Evidence-Backed Permission Graphs."** arXiv:2607.27267v1, 2026-07-29. LLM-guided Permission IR
translating NL tasks into structured constraints, deterministic lowering to a permission graph, SMT
authorizer, runtime gateway. **The quotable sentence for the manuscript:** *"FAVA does not provide
an end-to-end proof that an agent is safe from natural language alone; its formal guarantee begins
once available evidence has been lowered into the permission graph."* That is the presupposition of
category 3, stated by an author who then declines to address it.

**A5. Joshi, Finin, Joshi & Kagal (2026). "Deontic Policies for Runtime Governance of Agentic AI
Systems" (AgenticRei).** arXiv:2606.19464v1, 2026-06-17. To appear, IEEE Symposium on Agentic
Services (ICWS 2026). Applies the **Rei** deontic policy language (OWL, external logic engine) to
agentic AI, adding obligations, dispensations, **meta-policy conflict resolution**, and ontological
reasoning, on the argument that "XACML, Rego, and Cedar address only the permit/prohibit subset."
Conflict resolution is the manuscript's *priority* field. A second category-2 occupancy, from the
semantic-web policy tradition.

**A6. Yamazaki (2026). "Who Decides the Trade-off? Resolution Policy as Delegation Governance in
Autonomous Agents."** CAIS (ACM Conference on AI and Society) 2026, 2026-05-26.
DOI 10.1145/3786335.3813179 (Crossref-verified, CC-BY). Cites **all four** of SecPAL, UCON,
Delegation Logic and ABLP — the single most tradition-connected paper in the recent citer set.
Formalises "Resolution Policy" via a Deterministic Delegation Model for what to do when delegated
constraints conflict, with 2,248 experimental probes. Its own positioning sentence is telling:
*"Concurrent work has advanced authorization enforcement; the complementary question — what to do
when authorized actions conflict, and by whose authority — is the problem Resolution Policy
resolves."*

**A7. Zhang & Zhang (2026). "Are You Still the Agent I Authorized? Earned Authority under a Fixed
Ceiling for Evolving Agents."** arXiv:2607.23586v1, 2026-07-26. Formulates "authorization
continuity" with a transition envelope and immutable effect ceiling fixed at grant time; proves
mutation cannot amplify protected effects beyond the user-issued ceiling under complete mediation,
sound effect abstraction, attenuating delegation and monitor integrity. Distinguishes requested from
realized effects. Temporal/operation-specific authorization standing, without the language layer.

**A8. Gallo (2026). "Proof-of-Continuity: A Temporal Model for Authority Propagation in Distributed
Systems and AI Agents."** arXiv:2607.08906v1, 2026-07-09. Argues possession of tokens/capabilities is
insufficient because it does not preserve the causal relation between request origin and later
authority; each step may propagate only a non-expansive subset. Claims that under Proof-of-Continuity
"the confused deputy condition cannot be satisfied as valid model behavior."

**A9. Mellafe Zuvic (2026). "Capability Gates Are Not Authorization: Confused-Deputy Failures in LLM
Agent Frameworks" (ScopeGate).** arXiv:2606.28679v1, 2026-06-27. **Already cited by the manuscript**
as `mellafezuvic2026scopegate`. Audits LangChain/LangGraph, LlamaIndex and the Stripe Agent Toolkit;
none re-authorizes per call with concrete argument values by default.

**A10. Santos-Grueiro (2026), two papers.** "Lingering Authority: Revocable Resource-and-Effect
Capabilities for Coding Agents" (PORTICO), arXiv:2606.22504v1, 2026-06-19; and "Context-to-Execution
Integrity for LLM Agents" (CXI), arXiv:2607.06000v1, 2026-07-07. CXI's decomposition — field
authority, exact-effect authorization, invocation authority, all binding to one action manifest — is
structurally close to the manuscript's licensing field, at the enforcement layer rather than the
semantics layer.

**A11. Wang, Li & Tian (2026). "Aligning Provenance with Authorization: A Dual-Graph Defense for LLM
Agents" (AuthGraph).** arXiv:2605.26497v1, 2026-05-26. Builds an authorization graph from user intent
in an isolated clean context and structurally compares it against the execution provenance graph.
Claims to be "the first agent security defense to structurally compare authorization specifications
against execution provenance at the parameter-source level."

**A12. Shi, Du, Wang, Liang, Liu, Bian & Guan (2025/26). "SoK: Trust-Authorization Mismatch in LLM
Agent Interactions."** arXiv:2512.06914v2, 2025-12-07, revised 2026-02-09. Surveys 200+ papers;
proposes a Belief–Intention–Permission framework and diagnoses "desynchronization between dynamic
trust states and static authorization boundaries" as the common root cause.

**A13. Munirathinam (2026). "Will the Agent Recuse, and Will It Stop? Measuring LLM-Agent Compliance
with In-Band Governance Signals at the Access Door and Mid-Flight."** arXiv:2606.06460v4, 2026-06-04,
revised 2026-08-01. An in-band "Recuse Signal" over SSH banners, PostgreSQL NOTICEs and Kubernetes
admission warnings; measures whether agents honour a language-carried governance directive. Findings
directly relevant to the adversarial-pragmatics benchmark: *"an authorization framing flips GPT-4o to
proceed."* This is language-mediated authority measured empirically — the closest empirical neighbour
to the benchmark, though it studies compliance, not classification.

**A14. Palumbo, Choudhary, Choi, Amir, Chalasani & Jha (2026). "Formal Policy Enforcement for
Real-World Agentic Systems" (FORGE).** arXiv:2602.16708v3, 2026-02-18. Datalog policies over abstract
predicates, observability service under an assume/guarantee contract, reference monitor at every
action. Explicitly motivated by the inadequacy of natural-language policies in system prompts.

**A15. Li, Zhang, Polley & Ma (2026). "Security Considerations for Artificial Intelligence Agents."**
arXiv:2603.12230v2, 2026-03-12. Adapted from Perplexity's response to NIST/CAISI RFI 2025-0035.
**Ninghui Li is a co-author of both Delegation Logic and the RT framework.** Discusses agent
architectures changing "core assumptions around code-data separation, authority boundaries," names
indirect prompt injection and confused-deputy behavior, and lists "policy models for delegation and
privilege control" as a research gap. Notable as evidence that the tradition's own authors see the
gap and have not filled it.

**A16. Standards-adjacent.** South, Marro, Hardjono, Mahari, Whitney, et al. (2025), "Authenticated
Delegation and Authorized AI Agents," arXiv:2501.09674 — **already cited**. Madhira (2026), "Digital
Identity for Agentic Systems: Toward a Portable Authorization Standard for Autonomous Agents,"
arXiv:2605.11487. Huang et al. (2025), "OpenID Connect for Agents (OIDC-A) 1.0," arXiv:2509.25974.
El Helou, Troiani, Ryder, Diaconu, Muyal & Yannuzzi (2025), "Delegated Authorization for Agents
Constrained to Semantic Task-to-Scope Matching" (ASTRA, Cisco), arXiv:2510.26702 — semantic matching
of an NL task to OAuth scopes, with a dataset; the closest thing to a *benchmark* for NL-to-authorization.

**A17. Zhang & Wang (2026). "Towards Human-Centered Agent Authorization: A Landscape Analysis of
Commercial AI Agents."** CHI Extended Abstracts 2026, 2026-04-13. DOI 10.1145/3772363.3798851
(Crossref-verified). Walkthroughs of 18 commercial web agents; finds a "two-layer architecture where
agents demand broad system permissions masked by interface guardrails, shifting security reliance
from deterministic protocols to probabilistic model compliance."

**A18. Mondl, Maisel & Brock (2026). "Autoformalization of Agent Instructions into Policy-as-Code."**
arXiv:2606.26649v1, 2026-06-25. Accepted at AIWILD workshop, ICML 2026. LLM generator–critic loop
translating prompts, MCP tool descriptions and NL policy documents into Cedar. The reverse direction:
NL → policy, not NL-status → authorization.

**A19b. Yesil, Tezel & Challenger (2026). "BDI Agent-Based Access Control Reasoning for Multimodal
Retrieval-Augmented Generation."** The International FLAIRS Conference Proceedings, 2026-05-06.
DOI 10.32473/flairs.39.1.141759 (Crossref-verified). The only item found from the BDI /
agent-oriented-programming tradition. Uses Jason on JADE to "enforce multimodal access control by
separating authorization logic from generative computation," with LLMs used strictly as
computational services via MCP. Notable because it is the one system found that **reads content to
determine authorization**: parallel semantic extraction pipelines derive "authorization contexts"
from text *and* visual features such as institutional logos and security badges, tested on research
posters from six Belgian institutions. But what it extracts are policy *attributes* of a document,
not the illocutionary status of an occurrence, and no source-standing question arises.

**A19. Alglave & Cousot (2026). "Ceci n'est pas une pipe: AI systems as semantic abstractions."**
arXiv:2607.09489. Cites SecPAL. Proposes a semantic framework distinguishing what accepted domain
knowledge justifies, what reference sources say, and what the system can currently use, giving
precise definitions to extrapolation, unsupported assertion, added hypotheses, "unsupported use."
Framed around outputs and tool calls that "must be justified by reliable claims and **explicit
authority** rather than apparent fluency." Patrick Cousot (abstract interpretation) taking an
interest here is worth noting; the Magritte title signals a representation/reality distinction
close in spirit to the manuscript's normative/representational separation, though it is about
epistemic warrant for assertions, not authorization for action.

### NOT RELEVANT (checked and dismissed)

The UCON 2023+ citer set (80 papers) is almost entirely IoT, data spaces, zero-trust architecture,
blockchain and digital twins with no LLM-agent content. The RT and RBAC96 citer sets are similar.
LLM-adjacent items in that set run the *reverse* direction — using LLMs to generate access-control
policy (e.g. "On-device derivation of IoT usage control policies: Automating U-XACML policy
generation from natural language with LLMs," DOI 10.1016/j.future.2025.108067; LLMPEx, ABAC policy
extraction, DOI 10.1109/SMC58881.2025.11343181; AutoCedar, arXiv:2607.03656). These are
NL → policy synthesis, not NL-status → authorization, and pose no threat.

Also dismissed: hardware/TEE confused-deputy work (BreakFAST, Speed Kills, compartmentalization
SoKs), MCP registry/provenance infrastructure, and the large 2026 arXiv cluster of single-author
agent-security preprints with no formal or classificatory content.

---

## 2b. LATE ADDITIONS FROM THE VENUE SWEEP (agent completed after first write-up)

The delegated venue agent's report was empty when I first read it; it finished afterwards at 642
lines and is good. Its findings are at `/tmp/claude-agent-output/venue-sweep-accesscontrol-llm.md`.
**I re-verified every identifier below myself** — six DOIs through Crossref, two arXiv ids through
the arXiv API, and the two USENIX abstracts fetched directly with a browser user-agent after
WebFetch got 403. Everything quoted below is verbatim from a page I retrieved.

Three of these change the picture.

**H9. Jiang, Wang, Wen, Dai, Hong & Pan (2026). "MATE: Policy-Aware Security Auditing for Mobile
Agents via Synthesis-Driven Trajectory Learning." USENIX Security 2026** (Fudan University and
Shanghai Innovation Institute). Verified at
`usenix.org/conference/usenixsecurity26/presentation/jiang-changyue`. Not yet in DBLP.
**SUBSTANTIAL OVERLAP — the strongest category-4 hit, and a benchmark comparator too.**
Verbatim: *"Existing trajectory-level defenses rely on LLM prompting or rigid rules, and thus fail
to support fine-grained, natural-language policies that generalize across apps and tasks. In this
work, we introduce MATE, a lightweight, policy-conditioned auditor that encodes both agent
trajectories and natural-language security policies to determine whether a trajectory violates a
given policy and to explain why. Treating policies as editable text rather than fixed model
parameters allows MATE to handle user-defined and evolving requirements without retraining."*
Over 140K synthesized policy-conditioned trajectories; MATEBench released.
This is trajectory-scoped policy compliance over natural-language policy, at a top-four security
venue, with a released benchmark. It is **learned auditing, not a formal semantics**, and it audits
compliance with a stipulated policy rather than deciding authorization from status and standing —
that is the remaining opening. But "nobody evaluates policy compliance over whole trajectories"
is now false, and the seed benchmark has a large, released competitor in MATEBench.

**H10. He, Zhu, Li, Shao, Yao, Liu & Qin (2026). "AttriGuard: Defeating Indirect Prompt Injection in
LLM Agents via Causal Attribution of Tool Invocations." USENIX Security 2026** (Zhejiang / NTU /
City University of Hong Kong). arXiv:2603.10749. **The manuscript already cites this as
`he2026attriguard`, but not the sentence that matters.** Verbatim from the USENIX page:
*"Most existing defenses treat IPI as an input-level semantic discrimination problem, which often
fails to generalize to unseen payloads. We propose a new paradigm, action-level causal attribution,
which secures agents by asking why a particular tool call is produced. The central goal is to
distinguish tool calls supported by the user's intent from those causally driven by untrusted
observations."*
That first sentence is a **top-venue argument against the manuscript's thesis**, and it is the
second one found (LLMbda is the first, from the PL side; this is the security side). Two
independent research programmes now argue in print that treating directive-recognition as a
classification problem is the wrong move. The manuscript cannot cite AttriGuard as background and
leave that unanswered.

**H11. Edwards & Morisset (2026). "LLMs as PDPs Within a Smart-Home Environment: Accuracy,
Ambiguity, and Latency [Work in Progress Paper]." SACMAT 2026, 217–222.
DOI 10.1145/3750555.3811905** (Crossref-verified). Puts an LLM in the Policy Decision Point slot:
natural-language access policies plus a structured request in, decision out. Macro-F1 up to 0.998
in a small well-specified environment, but performance degrades under ambiguous queries with
"non-deterministic 'repair' behaviour and conservative use of Unknown." This is a published,
citable measurement of an LLM doing the natural-language half of an authorization decision and
**failing specifically on ambiguity** — good support for the manuscript, and a third SACMAT 2026
paper at the AI/access-control intersection.

Also newly confirmed, at ADJACENT:

- **Shapira, Gandhi, Habler & Shabtai (2026). "Mind the Web: The Security of Web Use Agents."**
  AsiaCCS 2026, DOI 10.1145/3779208.3805968; arXiv 2506.07153. Introduces the **task-aligned
  injection attack**, which frames malicious content as helpful task guidance rather than as an
  overt attack, ">80% ASR across five commercial agents." A clean empirical case of recognition
  failure driven by **pragmatic framing** rather than an imperative — the adversarial-pragmatics
  paper's phenomenon, demonstrated at a security venue.
- **Ştefănescu & Aciobăniţei (2026). "Lineage: A UMA2.0 Protocol Extension for Multi-Hop LLM Agent
  Delegation."** IEEE Access, DOI 10.1109/ACCESS.2026.3708618 (Crossref-verified). Signed
  delegation-ancestry records validated at the resource server, scope monotonicity and bounded
  delegation depth by construction. Category 2 on the OAuth/UMA side.
- **Singh & Madisetti (2026). "MCP-Secure."** IEEE OJ-CS, DOI 10.1109/OJCS.2026.3664314
  (Crossref-verified). Session-level state machine for permissions across multi-step workflows.
- **Choong, Hsieh & Leu (2026). "CapChain."** Applied Sciences 16(15), DOI 10.3390/app16157776
  (Crossref-verified). Capability tokens over a shared LangGraph state store.
- **Zouari (2025). "Toward Agentic IAM."** BDCAT 2025, DOI 10.1145/3773276.3776564
  (Crossref-verified). States the presupposition failure in IAM terms: RBAC, ABAC, OAuth 2.0 and
  OpenID Connect "were designed for static or user-initiated interactions."
- **Rubio-Medrano, Nath, Soneji, Mondragon, Baek & Ahn (2026).** SACMAT 2026 Blue Sky,
  DOI 10.1145/3750555.3811881 (Crossref-verified). *AI for access control* — the mirror problem.
- **Zhang, Kaiyuan; Su; Chen; Bertino; Zhang, Xiangyu & Li, Ninghui (2025). "LLM Agents Should
  Employ Security Principles."** arXiv:2505.24019v1 (verified). **Ninghui Li again**, with Elisa
  Bertino. Confirms the RT/Delegation-Logic author is writing on agent security in position-paper
  form without bringing his own formalism across.
- **Santos-Grueiro (2026), a fourth paper: "Temporary Authority, Permanent Effects: Commit-Time
  Authorization for LLM Agents,"** arXiv:2607.10487v1 (verified).
- **Ren, Acay & Myers (2025). "An Algebraic Approach to Asymmetric Delegation and Polymorphic Label
  Inference."** ESORICS 2025, 334–353, DOI 10.1007/978-3-032-07901-5_17. **Andrew Myers is still
  publishing delegation formalism in 2025 with no AI content whatsoever.** This is the cleanest
  single citation for "the tradition is alive and has not turned this way."
- **Baldo, Di Gianantonio, Paier & Miculan (2026). "Strobilus: Enriching Cedar with Stateful
  Policies."** SACMAT 2026, DOI 10.1145/3750555.3811892. No LLM content, but it is the formal
  machinery for state-scoped authorization a trajectory account would need. Pair with **Cutler et
  al. (2024), "Cedar: A New Language for Expressive, Fast, Safe, and Analyzable Authorization,"
  OOPSLA, DOI 10.1145/3649835** — which is where the modern authorization-language tradition
  actually lives in PL venues, and which the manuscript does not cite.
- **CaMeL's venue is now known: SaTML 2026**, Munich, 23–25 March 2026
  (satml.org/2026/accepted-papers). The earlier same-day audit had it as arXiv-only.

**One item nobody has read:** Huang, Li, Cai, Li, Xu, Tang, Zhang & Liu (2025), **"A Vision for
Access Control in LLM Agent Systems," ICECCS 2025, LNCS 467–472, DOI 10.1007/978-3-032-00828-2_25**.
Six-page vision paper; neither Crossref nor Semantic Scholar carries an abstract and neither the
venue agent nor I obtained the full text. Given the title, **acquire it before submission.**

**Two strong evidenced negatives from that sweep**, method stated: complete DBLP title listings for
19 venue streams (5,198 records) plus complete SACMAT/CODASPY/AsiaCCS proceedings from Crossref and
the CSF/SaTML/USENIX/NDSS accepted-paper pages, grepped. (1) No paper at CCS, S&P, USENIX Security,
NDSS, ESORICS, CSF, SaTML, SACMAT, CODASPY, AsiaCCS, ACSAC, EuroS&P, DSN, DBSec, POST, ICISS, PLDI,
POPL or OOPSLA, 2024–2026, extends ABLP speaks-for, SPKI/SDSI, Delegation Logic, SecPAL, RT, UCON or
XACML to LLM agents. (2) **CSF has zero LLM-agent papers across all three years.** The extension
work that exists is all on the OAuth/UMA/capability-token side.

**And a methodological warning worth carrying forward:** that agent reports OpenAlex author
disambiguation returned the **wrong person for three of nineteen** names, including giving "Na Li"
for Ninghui Li. Had it trusted OpenAlex, its author-sweep conclusion would have been exactly
inverted. DBLP `pid` records are the only reliable route for author-level checks.

---

## 3. ONE FINDING WORTH SEPARATE ATTENTION

**"Pragmatic Failure in Agentic LLM Systems: An Analysis Through Gricean Maxims and Speech Act
Theory."** *Global Spectrum of Research and Humanities*, 2026. DOI 10.69760/gsrh.0260302009
(surfaced via Semantic Scholar; **not independently verified against the publisher, and the venue
looks low-quality**). This is the only item in the entire sweep that applies speech-act theory to
agentic LLM systems. It bears on the adversarial-pragmatics paper rather than the authorization
claim, and its existence does not threaten either, but the manuscript should not be caught claiming
that nobody has applied speech-act theory to agentic systems.

---

## 4. THE IETF PICTURE (delegated agent, completed)

Full log: `/tmp/claude-agent-output/ietf-agent-auth-drafts.md`.

This is the strongest *supporting* evidence found for the manuscript's gap claim, because the
standards bodies have named the step and pushed it out of scope rather than ignored it:

- `draft-kuehlewind-audit-architecture-00`, "An Architecture for Auditing AI Agent Delegation and
  Interactions," Kühlewind (Ericsson) + Birkholz (Fraunhofer SIT), 2026-05-18, rev 00, Active,
  individual submission. This is the draft the manuscript already cites; confirmed.
- Its BOF request, `bofreq-kuhlewind-agent-use-of-delegation-and-interaction-traceability-audit-02`
  (proposers Kühlewind, Birkholz, Dingle/Microsoft, 2026-07-06), is in state **Declined**.
- `draft-klrc-aiagent-auth-03` (Okta/OpenAI/Ping/AWS/Zscaler/Defakto) states the mission "is
  typically expressed in natural language" and that "the process through which the mission is
  translated into authorization requriements is **out of scope**."
- `draft-liu-agent-operation-authorization-02` (Alibaba/Cisco) designs around *excluding* the NL
  instruction, retaining only a hash.
- `draft-pelov-bounded-agent-capabilities-00` states the consequence: where the interface carries no
  enforceable structure, "an authorization decision requires a model to interpret the call, making
  the decision probabilistic and non-reproducible: two independent policy enforcement points can
  legitimately reach different conclusions about the same call."

That last one is an independent, citable statement of the manuscript's inter-rater-reliability
problem, from a standards draft. It should be in the paper.

Also flagged by that sweep: `draft-han-bmwg-agent-security-benchmark-00` (China Mobile, 55 metrics,
jailbreak and indirect-injection defence tests) is a direct comparator for the seed benchmark that
does *not* separate task success, policy compliance, safety risk, evaluator confidence and failure
attribution — i.e. it fails on exactly the axis the benchmark is built around.

Caveat carried from that agent: the I-D corpus is flooded (259 name-matches, many apparently
machine-drafted), so an Internet-Draft signals nothing about consensus. Zero AI-agent-specific
drafts have been adopted by the OAuth WG or WIMSE. No working group exists.

---

## 5. COVERAGE GAPS — what this sweep did NOT cover well

State these honestly; they bound the negative.

1. **ACM DL full text was inaccessible** (403 on every attempt). Worked around for the Treacherous
   Envoy paper via the author's own PDF, which was read in full. **Still abstract-only: Reddi
   (SIGOPS OSR, H3), Yamazaki (CAIS, A6), and Zhang & Wang (CHI EA, A17).** Reddi is the one that
   matters — if the trajectory framing is load-bearing for the manuscript, get that PDF.
2. **The Semantic Scholar keyword surface was only partially covered** (rate-limit failures, §1.4).
   The citation graph and arXiv carry the negative; S2 keyword search does not.
3. **The DBLP / security-venue sweep initially returned an empty skeleton; it completed later and
   is now integrated (§2b).** Between the two, that surface is well covered: complete DBLP title
   listings for 19 venue streams (5,198 records), full SACMAT/CODASPY/AsiaCCS proceedings from
   Crossref, and the CSF/SaTML/USENIX/NDSS accepted-paper pages. Its author-page walk did complete
   and found the two pivots that matter (Gordon → LLMbda; Ninghui Li → two position papers).
   Residual: **CCS 2026, ESORICS 2026, ACSAC 2026, PLDI 2026 and OOPSLA 2026 are not indexed
   anywhere and those conferences have not happened**, so nothing here speaks for them.
4. **No Google Scholar.** Not accessible from this environment without browser escalation.
5. **Non-English work not searched.**
6. **Anything published in the last three weeks may not be indexed yet.** The newest confirmed items
   are from 2026-08-05. Given that the four most threatening items all appeared between March and
   July 2026, this space is moving fast enough that a re-check immediately before submission is
   warranted, not optional.

---

## 6. WHAT THE MANUSCRIPT MUST NOW POSITION AGAINST

In priority order. Before any of them, two things to do personally: **read H7b** (the
preference-vs-permission deposit, 20 minutes, bears on how the benchmark's novelty is worded), and
**acquire "A Vision for Access Control in LLM Agent Systems," ICECCS 2025, DOI
10.1007/978-3-032-00828-2_25** — nobody in this sweep has read it and the title is on the nose.

**0. The two published counter-positions, before anything else.** AttriGuard (USENIX Sec 2026,
already cited in the manuscript) and LLMbda / CaMeL both argue against classification-based
defence. Answer them by showing they exclude the class of cases rather than solve it.

1. **Siu et al. (ICML 2026, arXiv:2607.22024 + arXiv:2603.19469)** — the reframing competitor.
   Differentiator: they equate standing with authentication; the manuscript separates them, and
   adds contextual status. State this in the introduction.
2. **Ibrahim & Li (arXiv:2606.03518)** — the compositional-delegation competitor.
   `07-compositional-delegation.tex` must engage it, and the overlap is specific: their **resource
   scope attenuation** and depth-bounded delegation cover the same territory as the manuscript's
   grant-relative non-amplification
   (`Scope(g_down) ⊆ Conferrable_R(x, g_up, t)`), and they prove preservation and
   agent-authorization soundness for it.
   The manuscript's differentiator here is real and should be stated in one sentence: Ibrahim & Li
   have **one** graph, so the recorded relation *is* the authorization; the manuscript keeps
   `A_R(t)` and `Â(s_t)` apart and makes record-soundness `Â(s_t) ⊆ A_R(t)` a claim needing separate
   evidence, which is what lets it say a perfect trace can represent an invalid grant. Their single
   relational graph cannot express that, and it also has no guarded hyperedge for joint grants
   (their delegation types are all unary-source). Plus, as verified: zero occurrences of "natural
   language," "classification," "trajectory" or "sequence" in their paper.
3. **Reddi (SIGOPS OSR, DOI 10.1145/3830422.3830429)** — the trajectory competitor. The trajectory-
   first framing needs recalibrating from "unnoticed" to "recently proposed as an architecture
   agenda; here formalised."
4. **Garby, Gordon & Sands (arXiv:2602.20064)** — the opposing formal position. Engage as a live
   alternative: provenance-only, proof-backed, and explicitly against content inspection.
5. **FAVA (arXiv:2607.27267)** and **draft-klrc-aiagent-auth-03** — quote both as evidence that the
   language-classification step is *knowingly* excluded from current guarantees. These are the
   manuscript's best support, not its threat.
6. **Lin, Chen & Sun (SACMAT 2026, DOI 10.1145/3750555.3811883)** and **PAuth (arXiv:2603.17170)** —
   same group, access-control venue, natural-language delegation. TEP's related-work sentence
   ("bind identity to operation but not to runtime-negotiated operands") is the field's own
   statement of the gap and should be quoted, with the manuscript's difference stated: TEP's gap is
   the *operands*, the manuscript's is the *status of the occurrence and the standing of its
   source*.

---

## 7. RELATION TO THE EARLIER SAME-DAY AUDIT — AND ONE CORRECTION TO IT

A parallel session produced `/tmp/claude-agent-output/delegation-prior-art-audit-20260808.md`
earlier today (12:26). It audits the ten works **already cited** in `02-existing-work.tex` plus
CaMeL and MiniScope; this sweep looks **outward** for work the manuscript does not cite. The two are
complementary and their headline verdicts agree: nothing occupies the classification-plus-standing
ground.

**But that audit's headline evidenced negative is now partly refuted by this sweep, and Brett needs
to know before it goes into the paper.** It recommends (its narrowing, item 2) replacing the
"nobody has joined them" clause with the sharper claim:

> *the branch nobody has joined to is the authority-and-delegation lineage — ABLP, SPKI/SDSI,
> Delegation Logic, SecPAL, UCON ... Across all ten cited works plus CaMeL, there is not one
> citation to any of those five.*

The first half of that is **false as a general claim about the field**, though the second half
(about the ten cited works) is true and was correctly established. Three 2026 papers cite that exact
lineage in an LLM-agent context:

- **Ibrahim & Li, arXiv:2606.03518** — cites Delegation Logic and SecPAL at §3.2, SPKI and Nexus
  Authorization Logic at §6, and defines an "unconditional speaks-for" delegation type.
- **Yamazaki, DOI 10.1145/3786335.3813179 (CAIS 2026)** — cites SecPAL, UCON, Delegation Logic *and*
  ABLP.
- **Lin, Chen & Sun, DOI 10.1145/3750555.3811883 (SACMAT 2026)** — cites SecPAL, UCON and ABLP.

So the sentence must be scoped to what is actually true: *the lineage has been joined to agentic
authorization (delegation chains, scope attenuation, conflict resolution), but not to the
interpretation step; no work in that lineage, extended or classical, makes the contextual status of
a string occurrence an input to the authorization decision.* That version is still strong, still
evidenced, and survives contact with Ibrahim & Li.

**Residual items that audit left open, now closed.** All four verified via the arXiv API; none is a
category-1 hit, all are mechanism-level:

- **ETDI** — Bhatt, Narajala & Habler (2025), "ETDI: Mitigating Tool Squatting and Rug Pull Attacks
  in Model Context Protocol (MCP) by using OAuth-Enhanced Tool Definitions and Policy-Based Access
  Control," arXiv:2506.01333v1, 2025-06-02. Tool-definition integrity and OAuth scoping; nothing on
  string status.
- **IPIGuard** — An, Zhang, Du, Zhou, Li & Li (2025), arXiv:2508.15310v1, 2025-08-21. Tool-dependency-
  graph defence.
- **Fides** — Costa, Köpf, Kolluri, Paverd, Russinovich et al. (2025), "Securing AI Agents with
  Information-Flow Control," arXiv:2505.23643v2, 2025-05-29. IFC; same provenance-not-content bet as
  LLMbda and CaMeL.
- **Wu, Cecchetti & Xiao (2024)** — "System-Level Defense against Indirect Prompt Injection Attacks:
  An Information Flow Control Perspective," arXiv:2409.19091v2, 2024-09-27.
- **MiniScope** — Zhu, Tseng, Vernik, Huang, Patil et al. (2025), "MiniScope: A Least Privilege
  Framework for Authorizing Tool Calling Agents," arXiv:2512.11147v1, 2025-12-11. Confirmed; least
  privilege from tool-call structure, not string role.

That closes the earlier audit's stated residual risk. The new residual risk is the one in §5 of this
report: the remaining ACM-DL-only full texts, chiefly Reddi.

I also spot-checked the three identifiers that audit supplies for works this report relies on, and
all three resolve correctly: **arXiv:2503.18813v2** = Debenedetti, Shumailov, Fan, Hayes, Carlini,
Fabian, Kern, Shi, Terzis & Tramèr, "Defeating Prompt Injections by Design" (CaMeL);
**arXiv:2603.10749v2** = He, Zhu, Li, Shao, Yao, Liu & Qin, "AttriGuard: Defeating Indirect Prompt
Injection in LLM Agents via Causal Attribution of Tool Invocations"; **arXiv:2512.11147v1** = Zhu,
Tseng, Vernik, Huang, Patil, Fang & Popa, "MiniScope."

---

## 8. ARTIFACTS

- `/tmp/claude-agent-output/apsearch/s2_citers.json` — SecPAL, UCON, Delegation Logic, ABLP citers
- `/tmp/claude-agent-output/apsearch/s2_citers2.json` — Lampson, SPKI, trust management, Abadi citers
- `/tmp/claude-agent-output/apsearch/s2_citers3.json` — **confused deputy (84 2023+ citers)**, RT, RBAC96
- `/tmp/claude-agent-output/apsearch/arxiv_search.json` — sweep-1 arXiv results
- `/tmp/claude-agent-output/apsearch/*.txt` — extracted full texts of 2607.22024, 2606.03518,
  2607.27267, 2603.19469, and 2602.20064 (LLMbda PDF)
- `/tmp/claude-agent-output/ietf-agent-auth-drafts.md` — IETF/standards log
- `/tmp/claude-agent-output/venue-sweep-accesscontrol-llm.md` — DBLP/venue log
