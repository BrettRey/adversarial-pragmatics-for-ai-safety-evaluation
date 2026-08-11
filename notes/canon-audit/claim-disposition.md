# Canon audit: what survives, what must be conceded, what must be added
<!-- SUMMARY: Claim disposition for Delegation Assurance against the authorization canon AND the 2024-26 literature; core claim (status classification as authorization input) is OPEN with a strong evidenced negative, but the reframing, trajectory-first, compositional delegation and the presupposition argument were all taken in the last six months, and three programmes argue in print that classification is the wrong move; claim (A) is weak against 1993 and strong against 2026, which is the paper · status: complete, awaiting Brett's direction call · updated: 2026-08-08 -->

Working note for prerequisite 1 of the JCS retarget
(`submission/venue-decision-2026-08-08.md`). Consolidates the four per-source
audits in this directory into a disposition for each of the paper's claims.

**Complete: all six canon works read** (ABLP 1993, Lampson et al. 1992, SPKI
RFC 2693, Delegation Logic, SecPAL, UCON, plus OASIS XACML 3.0).

The three results, as §1 now states them:

- **(A)** A complete and internally consistent trace of a machine action is compatible with that action being unauthorized.
- **(B)** A valid authorization can leave no trace at all.
- **(C)** Per-action authorization doesn't compose into authorization of the sequence, because individually permitted steps can **(i)** breach a cumulative limit, **(ii)** jointly disclose a protected value, or **(iii)** reach a prohibited terminal state.

---

## Headline

**The three advertised results are substantially eroded. What survives is the
thing the paper currently treats as setup: the interpretation step.** Every one
of the six works presupposes that the authorization engine is handed correctly
identified principals and correctly classified requests. None models the failure
of that step.

**Scope that survival claim carefully. It is established against the
authorization canon only.** The canon audit shows the six formalisms don't cover
the interpretation step. It does not show that *nobody* does. Two things could
still take the ground, and both are under test as of 2026-08-08:

1. **The security works the paper already cites.** If Greshake, Wallace, Zverev, or especially South et al. 2025 (authenticated delegation, whose natural-language permission translation is the danger) already supply authorization *semantics* for the interpretation step rather than attacks, benchmarks, or defences, the contribution collapses.
2. **Anyone who has connected the canon to LLM agents since 2023.** The highest-yield check is who cites SecPAL, UCON, Delegation Logic, and ABLP in 2023–2026, because anyone doing this would cite them.

Until both return, this note establishes *what the canon leaves open*, which is
not the same as *what is unclaimed*. Treating the former as the latter is the
unevidenced-negative failure the portfolio rule exists to prevent, and it is
exactly the error this audit caught in clause (C-ii) below.

**Both checks returned 2026-08-08. Verdict: the core claim is OPEN, but the
ground around it was substantially taken in the last six months.** Reports:
`prior-art-audit.md` (cited set) and `priority-sweep.md` (outward, 31 rated hits).
See "Priority verdict" immediately below before reading anything else here.

## Priority verdict (2026-08-08)

Five categories were tested. **Two open, three taken.**

| # | Criterion | Status |
|---|---|---|
| 1 | Authorization semantics making **classification of the NL string** an input to the decision | **OPEN.** Nothing treats use/mention, quotation-vs-command, or speech-act status as an authorization input. |
| 2 | Extension of ABLP/SPKI/DL/SecPAL/UCON/XACML/RT to LLM agents | **TAKEN.** Ibrahim & Li (arXiv:2606.03518); Kagal et al. (arXiv:2606.19464). |
| 3 | Argument that AC formalisms presuppose authenticated principals and pre-classified requests | **TAKEN.** Lin, Chen & Sun, SACMAT 2026 Blue Sky (10.1145/3750555.3811883): the tradition "binds identity to operation but not to runtime-negotiated operands." |
| 4 | Formal trajectory-/sequence-scoped authorization | **TAKEN, firmly.** Reddi (SIGOPS OSR); Siu et al. (ICML 2026); **MATE (USENIX Security 2026)**, a working trajectory auditor over natural-language policies with a 140K-trajectory benchmark released. |
| 5 | Adjudicated status vs **assigned** status, failing in both directions | **OPEN as a framework**, partly measured by Klisura et al. (EACL 2026). Nobody has a typed status space or a status/standing separation. |

**Strong evidenced negative behind category 1:** complete DBLP title listings for
19 venue streams (5,198 records), full SACMAT/CODASPY/AsiaCCS Crossref
proceedings, and the CSF/SaTML/USENIX/NDSS accepted-paper pages show **no
2024–2026 paper at any of those venues extending ABLP speaks-for, SPKI/SDSI,
Delegation Logic, SecPAL, RT, UCON or XACML to LLM agents.** CSF has zero
LLM-agent papers across three years. Ren, Acay & Myers (ESORICS 2025) is the
cleanest citation for "the tradition is alive and has not turned this way."

### The three things that hurt

1. **The reframing now has a better-placed owner.** Siu, He, Montgomery, Wang, Wang & Song, "Position: Agent Security Needs Redefinition through a Holistic Framework," ICML 2026 (arXiv:2607.22024, companion formalization arXiv:2603.19469), from Dawn Song's group, makes this paper's *motivating* move ~-- agent security is an authorization problem, not a content problem ~-- with "Source Authorization," trajectory-continuous evaluation, and **indirect prompt injection recast as Hardy's confused deputy.** That is the page-one move made on 2026-08-08. **The differentiator is real and must be stated in §1: Siu et al. reduce standing to authentication; this paper separates them and adds contextual status.**
2. **Two programmes argue in print, at top venues, that classification is the wrong move.** AttriGuard (USENIX Security 2026, already cited but not this sentence): "Most existing defenses treat IPI as an input-level semantic discrimination problem, which often fails to generalize to unseen payloads." LLMbda (Garby, Gordon & Sands, arXiv:2602.20064) "abandons content inspection in favour of provenance." CaMeL makes the same bet architecturally. **This is not a gap; it is a live opposing position held by good people with proofs and benchmarks.** The paper needs an argument for why status classification is necessary *despite* their results. The strongest line, and it is well evidenced: they exclude the class of cases rather than solve it, and each says so in its own assumptions.
3. **Trajectory-first is the weakest of the three results now**, and the seed benchmark has a large competitor in MATEBench.

### The thing that helps, and it reverses part of the canon audit

Against **Ibrahim & Li**, the closest formal competitor, the differentiator is
precisely claim (A), which the canon audit had downgraded. They have **one
graph**, so the recorded relation *is* the authorization. This paper keeps
`A_R(t)` and `Â(s_t)` apart and makes record-soundness `Â(s_t) ⊆ A_R(t)` a claim
needing separate evidence, **which is what lets it say a perfect trace can
represent an invalid grant. Their single relational graph cannot express that.**
They also have no guarded hyperedge for joint grants (all delegation types are
unary-source), and zero occurrences of "natural language," "classification,"
"trajectory," or "sequence."

**So (A) is weak against 1993 and strong against 2026.** That is the paper.

Also supporting: **Edwards & Morisset (SACMAT 2026, 10.1145/3750555.3811905)**
put an LLM in the PDP slot with natural-language policies and find it degrades
specifically on ambiguity. **FAVA** (arXiv:2607.27267) and
**draft-klrc-aiagent-auth-03** both knowingly exclude the language-classification
step from their guarantees ~-- the paper's best support, not its threat.

### Two loose ends

- **"A Vision for Access Control in LLM Agent Systems," ICECCS 2025** (10.1007/978-3-032-00828-2_25). No abstract in Crossref or Semantic Scholar; nobody has read it; the title is on the nose. Acquire before submission.
- CCS/ESORICS/ACSAC/PLDI/OOPSLA 2026 are not indexed anywhere because those conferences have not happened.

### Method warning worth keeping

**OpenAlex author disambiguation returned the wrong person for three of nineteen
names**, including "Na Li" for Ninghui Li. Trusting it would have inverted the
author-sweep conclusion. **DBLP `pid` records are the only reliable route for
author-level checks.**

None of the ten cited security works defines conditions under which an operation
counts as authorized *given a classification of a string occurrence's role and its
source's standing*. The three closest each mark the gap rather than fill it: South
leaves LLM policy-translation robustness to future work and names policy-channel
injection as a new unguarded attack surface; AttriGuard declares user-authorized
untrusted content an explicit non-goal; ScopeGate rules language out of the
authorization decision by construction. **And the Q3 result is uniform: none of
the ten cites ABLP, Lampson, SPKI/SDSI, Delegation Logic, SecPAL, or UCON.**

### But the claim as worded is false, and must be recast

"LLM deployments *must* classify a string occurrence before any authorization
engine can run" asserts a necessity, and there are two existence proofs against
it. **CaMeL** (Debenedetti et al., arXiv 2503.18813) makes provenance structural:
a privileged LLM emits a program from the trusted query alone, a quarantined LLM
parses untrusted data into typed values, and a custom interpreter propagates
capability tags, never interpreting a string's role. **ScopeGate** makes policy
exogenous, with "No LLM participates in the decision." Neither is a counterexample
to the *problem*; both are counterexamples to the *necessity*.

**Recast as a scope claim, which is stronger anyway.** There is a class of
deployments in which authority is conferred, altered, or invoked through language
reaching the system at runtime: the user's own natural-language mandate, an
amendment arriving mid-session, a retrieved document the user has authorized to
determine an action, a tool result carrying a directive that genuinely has
standing. In that class the classification and standing assignments are
unavoidable, and no authorization semantics covers them. **The structural defences
don't cover this class; they exclude it by assumption.** Four independent authors
carving out the same case is far better evidence than an unqualified "must":

- **CaMeL §3**, and this sentence is the paper's thesis restated as CaMeL's precondition: "We assume that the user prompt is trusted, that the user is not pasting a prompt from an untrusted source, and, if there is a memory in place, the memory has not been compromised by the adversary." §3.1 further concedes CaMeL "cannot defend against text-to-text attacks which have no consequences on the data flow."
- **ScopeGate §II.C**, out-of-band policy requirement.
- **AttriGuard**, "Pure Explicit Delegation to Untrusted Content" declared a non-goal.
- **South §5.2**, the unguarded policy-authoring channel.

### "Nobody has joined them" is both too strong and too weak

Too strong: the agent-security literature *has* joined one branch of the
access-control tradition. CaMeL joins DIFC and control-flow integrity (Denning
1976; Denning & Denning 1977; Myers & Liskov 1997; Sabelfeld & Myers 2003; Abadi
et al. 2009), ScopeGate joins complete mediation (Saltzer & Schroeder; Hardy),
South joins policy-language syntax (XACML, ODRL, ROWLBAC).

Too weak, because a sharper fully-evidenced claim is available: **the branch
nobody has joined is the authority-and-delegation lineage** ~-- ABLP, SPKI/SDSI,
Delegation Logic, SecPAL, UCON ~-- **which is the branch with semantics for who
may say what on whose behalf.** Across all ten cited works plus CaMeL, not one
citation to any of those five. That is checkable and it makes the point without
overreaching.

Note this also usefully connects CaMeL's DIFC bibliography to clause (C-ii)
below: Denning 1976 appears on both sides, which makes the information-flow
engagement cheaper than it looked.

### Three required citation additions

1. **CaMeL** (arXiv 2503.18813). Uncited anywhere in the repo (verified: no hits for `camel` or `debenedetti` beyond `debenedetti2024agentdojo`). Same first author as AgentDojo, which *is* cited; the best-known "provable" prompt-injection defence, reporting "77% of tasks with provable security" on AgentDojo. **Leaving it out is the single largest avoidable risk in the section**, and the obvious desk-reject question.
2. **MiniScope** (Zhu et al., arXiv 2512.11147), "A Least Privilege Framework for Authorizing Tool Calling Agents." Abstract read only.
3. Not yet checked, and worth ten minutes each before submission: **ETDI** ("OAuth-enhanced tool definitions and policy-based access control," AttriGuard ref. [51], the most plausible remaining occupier), **Wu, Cecchetti & Xiao 2024** (an IFC treatment of indirect prompt injection, cited by CaMeL), plus IPIGuard and Fides.

### A cross-project find

AttriGuard's attenuation operators cite **Austin, *How to do things with words***
for stripping directive force from untrusted text. That is a direct hook for the
Adversarial Pragmatics flagship, not for this paper.

## Disposition

| Claim | Verdict | Action |
|---|---|---|
| (A) | **Substantially anticipated** in XACML §9, ABLP's `A\|B`, SPKI §4.1.1/§7.5. Survives only as a reframing. | Cite; restate against SecPAL's soundness theorem. |
| (B) | **Near-trivial across all six.** A *design property* of SPKI and DL, structural in UCON, conceded by Lampson et al. | Demote. Fuse with (A) as two directions of one gap. |
| (C-i) cumulative limits | **DOES NOT SURVIVE.** UCON owns it outright. | Concede, cite, pivot to the five narrower points. |
| (C-ii) joint disclosure | **Survives against these six, but is a POSITIONING LIABILITY.** | Not a gap. Engage the information-flow / inference-aggregation literature. Highest risk. |
| (C-iii) terminal states | **Survives in generality and vocabulary**; the pattern doesn't. | Distinguish forbidden end state from forbidden next step. |
| Grant-relative non-amplification | **DIRECTLY ANTICIPATED** by SPKI tuple reduction and DL's step-9 rule. | Concede and cite. Three usable qualifications remain. |
| **The interpretation / classification step** | **Survives across all six** ~-- but priority against the security literature is UNDER TEST, see Headline. | **Promote if it clears.** |

---

## What survives the canon: the interpretation step

*Priority against the security literature is under test; see Headline.*

SecPAL is the sharpest case because it is the closest neighbour. Its principals
*are* public keys; authentication happens before SecPAL runs. Zero hits for
`classif`, `recogni`, `spoof`, `forge`, `injection` across the whole paper. The
same holds across the set: ABLP and Lampson et al. reduce every decision to
proving `A ⇒ B`; UCON presupposes attribute values and explicitly declines to
model where they come from; XACML's PIP hands the PDP attributes it does not
question.

The canon assumes the hard part away. An LLM deployment cannot, because it has to
decide whether a string occurrence is a command in use, a mentioned quotation, a
policy example, a tool result, or retrieved content, and whether its source has
standing, before any authorization engine can run. Both assignments can fail in
either direction.

**This is the paper's strongest position and it is currently framed as setup for
the three results.** Consider inverting that.

---

## (C-i) cumulative limits: concede

Not a gap UCON leaves. It's what UCON was built to close, in the paper's own terms:

> "Policies requiring limits on the number of accesses by a subject or reduction
> of account balance based on access can be easily specified using mutable
> attributes … various kinds of consumable authorizations can be modelled in this
> manner. High watermark policies … and Chinese Walls can also be enforced in
> this way." (Park & Sandhu, §2)

Four worked mechanisms back it: credit decrement with a guard (Ex. 3), an explicit
`k = k − 1` counter with guard `k ≥ 1` (Ex. 20), post-hoc metered accumulation
(Ex. 4), and a concurrency cap that revokes a live access when exceeded (Ex. 5–7).

**Five narrower things survive, and they are the pivot:**

1. **UCON encodes, it doesn't detect.** The author must already know which constraint exists and hand-write the update. Nothing identifies which constraints a deployment needs or checks that per-action policies are jointly adequate to a sequence-level goal. UCON declines to build that: no logical expression language (§4), and "Space does not permit us to explore the expressive power of combined models" (§9).
2. **Park and Sandhu concede sequence-level prediction is hard**, placing access review under mutability in the class of HRU safety analysis, "a problem more akin to safety analysis with respect to leakage of rights" (§3 n.2). **A friendly citation** the paper can cite *for* its claim.
3. **The unit of analysis contains no sequence.** `workflow` appears once, pushing accumulated-payment enforcement *out* of the core. No plan, trace, goal, or terminal state.
4. **Attribute derivation is presupposed**, which is where joint-disclosure reasoning would live.
5. **Standing to change policy is out of scope.** UCON models what a policy permits, never who may alter it.

---

## (C-ii) joint disclosure: the highest-risk item

**The readers disagreed, and reconciling them is the finding.** The UCON/XACML
reader found this "survives cleanly" (`inference` and `aggregation`: zero hits in
UCON; `inference` zero in XACML). True of those documents. The ABLP reader found
the opposite and is right about what it means. Lampson et al. scope the problem
out **by name, pointing at the field that owns it**:

> "Information flow [8] is an alternative model which is also not considered, so
> we have nothing to say about mandatory security policies that can enforce
> nondisclosure of secrets." (Lampson et al., §1 n.1; ref. [8] is Denning 1976)

ABLP likewise scopes out mandatory access control (§1).

**The zero hits are a boundary marker, not absence of coverage.** Reading them as
"nobody has done this" is precisely the unevidenced negative over an unsearched
space the portfolio rule prohibits.

**Worst possible place to get this wrong: Sushil Jajodia is on the JCS editorial
board and inference and aggregation in multilevel secure databases is his own
research area.** He is also cited twice in Delegation Logic (refs [22], [23]),
positioned as centralized prior work that "did not address the delegation
aspect," so his work is already inside this literature's bibliography.

**Required, and it is new work beyond the six-work list:** engage the
information-flow and inference/aggregation line (Denning 1976 onward, and the
multilevel-database inference literature), then say what an LLM-agent setting
adds. Until then, clause (ii) should not appear on page one as a result.

---

## (C-iii) terminal states: survives narrowly

`terminal` returns zero hits in UCON; its objects are a request and a live usage,
never a trajectory. But the *pattern* is worked once as BLP high watermark
(Ex. 14): a permitted read raises `clearance(s)`, after which a previously
permitted write is forbidden by the star property. Chinese Wall and dynamic
separation of duty are claimed as enforceable without being formalized.

Honest position: UCON provides the mechanism and asserts the coverage; it supplies
neither the analysis, the vocabulary, nor a worked case of a forbidden *end state*
as distinct from a forbidden *next step*.

---

## Grant-relative non-amplification: concede this too

A direct anticipation, and the paper currently presents it as its own repair.

- **SPKI §6.3** reduces `<I1,S1,D1,A1,V1> + <I2,S2,D2,A2,V2>` to `<I1,S2,D2,AIntersect(A1,A2),VIntersect(V1,V2)>`, requiring `D1 = TRUE`, narrowing authority, validity, and the delegation bit at once.
- **Delegation Logic's step-9 chaining rule** bounds derived depth by `min(d ⊖ len, dep)` "because A should not trust C more than BE trusts C." (Note: `pdftotext` silently drops the `⊖` glyph; it was confirmed by rendering the page at 200 dpi.)

**Three qualifications the paper can legitimately keep:** SPKI's version is an
application-level convention, not a guarantee ("Special semantics would require
special reduction software", §6.3.1); DL exempts representation statements, which
"don't consume any delegation depth"; and **neither work proves it** — DL's only
theorems (5–7) are complexity bounds.

---

## (A) and (B): fuse them

**(A)** is anticipated three ways in XACML §9, all framed as implementation
hazards rather than a general property:

> "A failure to match will result in 'NotApplicable' and be treated as 'Permit'.
> So an unintended failure to match may allow unintended access." (XACML p. 90)

ABLP's quoting operator marks the same gap: `A|B` means A claims B said it, and
"This does not mean B actually said it: A could be mistaken or lying." SPKI
§4.1.1 documents key-loaning and signing-oracle proxying, and §7.5 a structural
bypass via name grants, without drawing the epistemic conclusion.

**(A) must be restated against SecPAL's soundness theorem**, which proves
holding-iff-provable. So (A) has to locate its failure exactly where SecPAL locates
its own boundary: revocation availability (conceded and declared out of scope) and
the untested request→query table mapping.

**(B) is the weakest of the three.** It is a *design property* of SPKI (an ACL
entry "has no Issuer (and is not signed)" and "is never communicated") and of DL
(local policy "need not be signed"; the trust root "can choose to authorize a
request without consulting the trust-management engine"); structural in UCON,
whose `0`-mutability class is defined as authorization that changes nothing and
holds MAC, DAC, RBAC and most trust management; and conceded flatly by Lampson et
al., where `A says s` holds though "A may not be present and may never have seen
s," with delegation built on a server `D` deliberately never implemented.

A JCS reader will find "logging is optional" unremarkable. **Recommendation:
demote (B) from a headline result and present (A) and (B) as the two directions of
a single gap between authorization and record.**

---

## A distinction the paper must draw explicitly

**ABLP already proves delegation doesn't compose associatively.** An unqualified
"authorization doesn't compose" collides with a known result about a different
axis. The paper's claim is about the **action** sequence; ABLP's is about the
**principal** chain. Say which, in the sentence making the claim.

Clean quotable targets on the action axis, which the canon genuinely leaves open:

- ABLP treats the request as "an uninterpreted proposition symbol" (§7).
- Lampson et al. reduce every access decision to proving `A ⇒ B` (§8), and define auditing as recording the per-decision proof, "a complete account of what access was granted and why" (§9.1) — exactly the per-action framing the paper disputes.
- Lampson et al. concede long-running delegated computation is unsolved: "We have not worked out the details of this scheme" (§6).
- SecPAL is stateless per query **by explicit assumption**: "we assume that a single authorization query evaluation is atomic with respect to system state." Its separation-of-duties idiom works only because an external reference monitor writes a fact into the context, an effect "not specified here."
- Delegation Logic: the string `valid` occurs **zero times** in the entire paper. D1LP is monotonic Datalog: no negation, no arithmetic aggregation, no clock, no state.
- SPKI's temporal machinery constrains credential currency only; one-time revalidation has "no lifetime beyond the current authorization computation" (§5.5).

**But one caution that changes the framing.** SecPAL *names* this gap in its own
voice and calls the fix easy: "SecPAL could be easily extended according to that
scheme," citing **Becker & Nanz 2007** (ESORICS) on state-modifying authorization.
So the paper cannot claim the canon overlooked sequences. **It must engage Becker
& Nanz 2007 and argue why "easily extended" is wrong.** That is a required new
source.

---

## The evidentiary bar SecPAL set in this venue, and why it reverses earlier advice

**This supersedes the earlier recommendation to take the demonstration route over
the formalization route.** That advice came from Nguyen (2026) and Abdunabi
(2025), applied framework papers. SecPAL is the closer precedent: same venue, same
topic, and the paper DA's title invites comparison with.

What a 2010 JCS reader saw a decentralized-authorization paper deliver: three
deduction rules constituting the semantics; five numbered safety/well-formedness
definitions; one corollary and four propositions; **four numbered theorems in the
body**; a twelve-page appendix with seventeen further lemmas and **all** proofs;
full pseudocode; twelve comparative idiom subsections each set against named
competitors; and a described prototype.

What it did **not** have: no performance numbers, no benchmarks, no scalability
graphs, no user study, no attacks, no threat model, no security evaluation. The
paper says so: "Although system implementation is not the subject of this paper."

**Calibration: this venue supports a paper with no experiments. It does not
support one with no formal results.** And DA's disclaimer that its contribution is
"a meta-model at the normative and representational layers, not a complete
authorization language" will be read directly against SecPAL, which *is* the
complete authorization language.

**Two mitigations, both visible in SecPAL's own text and both cheap:**

1. **One clean proposition.** SecPAL's core structural results (Prop. 3.3–3.6) are a small number of short statements about a three-rule system; Prop. 3.6 in particular is one line doing heavy work. A single proposition of that shape about non-composition on the action axis is an achievable target for a meta-model and "would substantially change how the paper reads here."
2. **The comparative idiom table.** SecPAL's §6, twelve idioms each against named competitors, is this venue's recognized substitute for an evaluation section, and it costs no experiments. **DA's seven existing fixtures could be reorganized to occupy exactly that form** — they already encode level separations, which is the same move.

Revised recommendation for the open formalization question: **not one route or the
other, but both, small.** One proposition plus a fixture-to-idiom-table
reorganization. Neither requires new empirical work, both are in-venue recognized
forms, and together they close the gap the meta-model disclaimer opens.

This also couples to the title question. **"Typed Authorization Semantics" invites
the SecPAL comparison and its theorem bar; an applied-framework title invites the
Nguyen/Abdunabi comparison and its worked-case bar.** The title decision and the
formalization decision are the same decision.

---

## Citation hazards: page mapping is unsafe for four of seven sources

**Cite by section, definition, and example number, not page, wherever the local
copy is an author version.** Those identifiers are stable across paginations. This
note does that throughout.

| Source | Local copy | Hazard |
|---|---|---|
| ABLP 1993 | Author copy, paginated 1–29 | Footer reads "Vol. 15, No. 3"; Crossref gives **15(4):706–734, Sept 1993** (re-verified live 2026-08-08 against `10.1145/155183.155225`). Crossref is authoritative and the footer is a pre-final artifact, but **no page-specific cite maps from this copy.** |
| Lampson et al. 1992 | Preprint, paginated 1–47 | No verifiable offset to 265–310. The citation itself is source-grounded from ABLP's reference list (ref. 17): TOCS 10(4), Nov. 1992, 265–310. |
| Delegation Logic | Authors' preprint, folioed 1–42 | Does not map to 128–171 by any fixed offset; the PDF carries **no journal metadata at all**. |
| SecPAL | Author typescript, 59 pp. | No journal pagination. Every page cite must be remapped to 619–665 before it enters the manuscript. |
| Park & Sandhu 2004 | Author camera-ready, 1–47 | Footer reads "Vol. 0, No. 0, 02 2004, Pages 1–0??". Published **7(1):128–174** unverifiable from the file; the +127 offset is arithmetic inference only. |
| SPKI RFC 2693 | Canonical RFC text | Safe. Cite by RFC section. |
| OASIS XACML 3.0 | Official OASIS PDF | **Pagination exact.** Page cites safe. |

**Do not reuse the two Delegation Logic bibliography DOIs** produced during the
read: they were flagged as unverified against any source actually fetched. Resolve
them against Crossref before they go into `references-local.bib`.

Three further accuracy traps:

- **XACML delegation is not in the core specification.** It is the separate *Administration and Delegation Profile* v1.0, and that document is a **Committee Draft (CD 03, 11 March 2010), not an OASIS Standard.** The core spec reaches it only via `<PolicyIssuer>` and `MaxDelegationDepth`.
- **Park and Sandhu's dismissal of XACML** ("fails to cover mutable cases and ongoing cases") targets Godik & Moses 2002, i.e. **XACML 1.0**, not the 3.0 read here.
- **SecPAL's appendix restates its own Lemma 8.2 as "Restatement of Theorem 8.2"**, an internal numbering slip. Don't reproduce it.

---

## Two questions a JCS reviewer will ask

1. **"Doesn't UCON already do continuous authorization of long-running actions?"** Yes, definitionally: `onA`/`onB`/`onC` with `stopped(s,o,r)` on predicate failure. **If the contribution is framed as "authorization should be continuous, not one-shot," there is no contribution.** The re-evaluation *trigger* is explicitly unspecified ("we do not specify these technical and implementation details"), and that is a real opening.
2. **"Is XACML really stateless, or are you just not counting obligations?"** Obligations are the only write path and XACML defines no semantics for them ("There are no standard definitions for these actions in version 3.0 of XACML"). A deployment can get cross-decision state by having the PEP discharge an obligation updating a PIP-visible attribute, but that is outside the standard, which forbids mutation within a decision and fixes time to a snapshot. Say it that way or the reviewer will.

## New sources now required

Beyond the six-work canon list, the audit surfaced two the paper must engage:

1. **Becker & Nanz 2007** (ESORICS), on state-modifying authorization — because SecPAL names it as the easy fix for exactly the gap DA claims.
2. **The information-flow / inference-aggregation literature**, Denning 1976 onward plus the multilevel-database inference line — because that is where clause (C-ii) actually lives, and because Jajodia is on the board.

Neither is acquired yet.
