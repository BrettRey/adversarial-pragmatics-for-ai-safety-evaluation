# UCON and XACML: source-grounded extraction for the JCS retarget

Prepared for the AI-agent-action-authorization manuscript. Every claim below carries a page
or section locator and, where load-bearing, a verbatim quote. Negative findings state the
search that produced them.

---

## 0. Citation and pagination caveats (read first)

### 0.1 The UCON copy on disk is the author camera-ready, not the published TISSEC pages

`/Users/brettreynolds/projects/LLM-CLI-projects/literature/park2004ucon.pdf` is 47 PDF pages,
internally numbered **1–47**. Its running footer reads:

> "ACM Transactions on Information and System Security, Vol. 0, No. 0, 02 2004, Pages 1–0??."
> (p. 1, footer)

and its copyright line reads:

> "© 2004 ACM 1084-4309/2004/0400-0001 $5.00" (p. 1)

**The published volume, issue, and page range do not appear anywhere in this file.** The
`7(1):128–174` given in the task brief is therefore not verifiable from this copy. It is
*arithmetically consistent* with it (174 − 128 + 1 = 47 pages), which makes the mapping
`published page = internal page + 127` a reasonable inference, but it is an inference and I
have not confirmed it against a source. **All page numbers below are the internal 1–47
numbering of this PDF.** Before submission, either verify the mapping against the ACM DL
version or cite by section number.

Also note the PDF metadata: `Title: ABC8.dvi`, `Producer: AFPL Ghostscript 7.03`,
`CreationDate: Fri Jan 16 15:05:01 2004`. This is a pre-print artefact.

Correct citation as far as this document supports it:

> Park, Jaehong, and Ravi Sandhu. 2004. "The UCON_ABC Usage Control Model." *ACM Transactions
> on Information and System Security*. [Volume/issue/pages not stated in this copy; commonly
> cited as 7(1): 128–174.]
> Author affiliations per p. 1: Park, George Mason University; Sandhu, NSD Security and
> George Mason University. Address: "Laboratory for Information Security Technology (LIST),
> ISE Department, George Mason University, Mail Stop 4A4, Fairfax, VA 22030" (p. 1).
> Acknowledgement on p. 1: "This research was partially supported by the National Science
> Foundation." Prior version: "Portion of this paper appeared in preliminary form under the
> title 'Towards Usage Control Models: Beyond Traditional Access Control' in Proceedings of
> 7th ACM Symposium on Access Control Models and Technologies, Monterey, CA, USA, 2002." (p. 1)

### 0.2 XACML pagination is exact

`oasis2013xacml.pdf` PDF page *N* = document "Page *N* of 154". No offset. The document
prescribes its own citation format on p. 2:

> "[XACML-V3.0] eXtensible Access Control Markup Language (XACML) Version 3.0. 22 January 2013.
> OASIS Standard. http://docs.oasis-open.org/xacml/3.0/xacml-3.0-core-spec-os-en.html."

Front matter (p. 1): OASIS Standard, 22 January 2013. Technical Committee: OASIS eXtensible
Access Control Markup Language (XACML) TC. Chairs: Bill Parducci (Individual), Hal Lockhart
(Oracle). Editor: Erik Rissanen (Axiomatics AB). Declared namespace
`urn:oasis:names:tc:xacml:3.0:core:schema:wd-17`. It "replaces or supersedes" XACML v2.0
(1 February 2005). p. 1 warns: "Check the 'Latest version' location noted above for possible
later revisions of this document" — so do not assert this is the current text without
checking; I have not checked.

---

# PART I — Park & Sandhu, UCON_ABC

## Précis (250 words)

UCON_ABC is a *model-layer* generalisation of access control that deliberately excludes
architecture, mechanism, administration, and delegation. Its unit of analysis is a single
usage: a consumer subject *s* exercising a right *r* on an object *o*. Eight components:
subjects, objects, rights, subject attributes, object attributes, and three decision
predicates — Authorizations (evaluated over subject and object attributes), oBligations
(actions a subject must perform), and Conditions (subject- and object-independent
environmental facts). Two axes cross-cut these. **Continuity**: each predicate has a *pre*
form, evaluated before the right is exercised, and an *ongoing* form, evaluated repeatedly
while it is exercised, whose failure triggers `stopped(s,o,r)`, i.e. mid-usage revocation.
**Mutability**: subject and object attributes may be updated as a consequence of access, at
three times — `preUpdate`, `onUpdate`, `postUpdate`. Crossing three predicates × two
continuities × four mutability settings, and striking the combinations the authors judge
useless, yields exactly 16 basic models (Figure 4, p. 14).

The paper then shows MAC, DAC, RBAC, trust management, DRM, and healthcare policies as
instances, using 29 worked examples in formal notation. Its distinctive claim is that
mutability lets a *later, otherwise-identical request be denied because of an earlier
permitted access*, which is how it captures consumable rights, metered payment, usage
counts, high-watermark clearance, and (by assertion) Chinese Wall.

It is explicitly a first step. Administration, delegation, static constraints, duties,
global obligations, trusted attribute sourcing, and the expressive power of *combined*
models are all named and deferred.

## Numbered claims

**U1. Mutability is the paper's own headline innovation, and it is defined as attribute
change caused by access.**
p. 7 (§3, opening) / abstract p. 1.
> "A significant innovation in U CON_ABC is that subject and object attributes can be
> mutable. Mutable attributes are changed as a consequence of access, whereas immutable
> attributes can be changed only by administrative action." (p. 7)

**U2. The paper names cumulative limits, in those words, as the paradigm application of
mutability.** This is the single most damaging sentence for the manuscript's claim (C).
pp. 7–8 (the sentence begins on the last line of p. 7, with "requir-/ing" broken across the
page, and completes on p. 8; the two following sentences are wholly on p. 8).
> "Policies requiring limits on the number of accesses by a subject or reduction of account
> balance based on access can be easily specified using mutable attributes. More generally,
> various kinds of consumable authorizations can be modelled in this manner. High watermark
> policies on subject clearance and Chinese Walls can also be enforced in this way."
> (pp. 7–8)

**U3. Continuity of decision is defined as pre vs. ongoing enforcement, with ongoing
enforcement semantically required to hold throughout the access.**
p. 11 (§3.4) and p. 19 (§4.2).
> "Authorizations can be either pre-authorizations (preA) or ongoing-authorizations (onA).
> preA is performed before a requested right is exercised and onA is performed while the
> right is exercised. onA may be performed continuously or periodically during the time span
> of access." (p. 11)
> "Semantically these requirements have to be true all the time while the right is exercised.
> Technically, these checking processes are likely to be performed periodically based on time
> or event. In the U CON_ABC model, we do not specify these technical and implementation
> details." (p. 19)

**U4. Revocation mid-usage is formalised as `stopped`.**
p. 19, Definition 4 (U CON_onA0).
> "—allowed(s, o, r) ⇒ true; —stopped(s, o, r) ⇐ ¬onA(AT T (s), AT T (o), r)." (p. 19)
> "We write 'stopped(s, o, r)' to indicate rights r of subject s to object o is revoked." (p. 19)

**U5. The re-evaluation trigger is left unspecified on purpose; the model is transaction-based.**
p. 12 (§3.5).
> "One of the basic assumptions in the U CON_ABC model is that its decision-making process is
> transaction-based. This means that decision predicates are evaluated upon each usage request
> and the decision influences usages of that request. A pre decision predicate decides approval
> or denial of the request. An ongoing predicate may revoke or continue to allow current
> exercise of the requested usage." (p. 12)

**U6. The three update times are `preUpdate`, `onUpdate`, `postUpdate`, and they are optional
procedures attached to the base models.**
pp. 16 (Defs 2–3), 19 (Defs 5–7), 22 (Defs 9–10), 25 (Defs 12–14).
> "preU pdate(AT T (s)), preU pdate(AT T (o)), an optional procedure to perform update
> operations on AT T (s) and AT T (o), respectively. Note that preU pdate can include
> non-deterministic operations." (p. 16, Definition 2)

**U7. The 16-model space is generated by decision factor × continuity × mutability, and the
paper's own rationale for the excluded cells is about the influence of updates on *future*
requests.**
pp. 13–14, Figure 4.
> "Our classification is based on the following three criteria: decision factors that consist
> of authorizations, obligations, and conditions, continuity of decision being either pre or
> ongoing with respect to the access in question, and mutability that can allow updates on
> subject or object attributes at different times." (p. 13)
> "Without ongoing decision, ongoing-update can only influence decisions on future requests
> and therefore the updates can be done after the usage is ended." (p. 14)

**U8. WORKED CUMULATIVE-LIMIT MECHANISM #1 — pre-paid credit consumed by access
(U CON_preA1).** An access lowers `credit(s)`; when `credit(s) < value(o,r)` the identical
request is denied. This is exactly "an attribute changes because of an access such that a
later otherwise-identical request is denied."
p. 17, Example 3 (repeated verbatim as Example 22, p. 33).
> "allowed(s, o, r) ⇒ credit(s) ≥ value(o, r)
>  preU pdate(credit(s)) : credit(s) = credit(s) − value(o, r)" (p. 17, Example 3)
> "In Example 3, if the credit of a subject s is not less than the value of the requested
> usage, the request is allowed. Once the request is allowed, the subject's credit is reduced
> by the value of the usage." (p. 18)

**U9. WORKED CUMULATIVE-LIMIT MECHANISM #2 — an explicit k-times usage counter with a guard.**
This is the cleanest "limited number of uses" instance in the paper.
p. 32, Example 20 (DAC using Capability List with usage count, U CON_preA1).
> "CL : S → 2^G×R×K , s is authorized to do r to g for k times
>  ...
>  allowed(s, o, r) ⇒ GR ≠ φ,
>      GR = {(g, r) | g ∈ groupId(o)} ∩ {(g′, r) | (g′, r, k) ∈ CL(s), k ≥ 1}
>  ...
>  preU pdate(CL(s)) : k = k − 1, (λ(GR), r, k) ∈ CL(s)" (p. 32)

**U10. WORKED CUMULATIVE-LIMIT MECHANISM #3 — metered usage accumulated post hoc
(U CON_preA3).**
p. 17, Example 4.
> "postU pdate(expense(s)) : expense(s) = expense(s) + (value(o, r) × usageT (s))" (p. 17)
> "a total expense has to be updated at the end of each usage by using current usage time and
> value of the usage so it can be paid periodically." (p. 18)

**U11. WORKED CUMULATIVE-LIMIT MECHANISM #4 — a concurrency cap enforced by a counter that
revokes an *already-granted* access when the 11th arrives.** Three variants (earliest start,
longest idle, greatest total usage time), Examples 5–7.
pp. 19–21, Example 5 (U CON_onA13).
> "stopped(s, o, r) ⇐ (usageN um(o) > 10) ∧ (id(s), t) ∈ startT (o) where t = min{t′|∃s′,
> (id(s′), t′) ∈ startT (o)}
>  preU pdate(usageN um(o)) : usageN um(o) = usageN um(o) + 1
>  postU pdate(usageN um(o)) : usageN um(o) = usageN um(o) − 1" (p. 20)
> "In Example 5, suppose only 10 users can access an object o1 simultaneously. If a 11th user
> requests access, the user with the earliest time is terminated." (p. 21)

**U12. WORKED HISTORY-DEPENDENT PROHIBITION — BLP high watermark: a permitted read raises
clearance, which then forbids a write that would previously have been permitted.**
p. 29, Example 14 (U CON_preA1). This is the one fully worked instance in the paper of
"individually permitted actions become impermissible in combination."
> "allowed(s, o, read) ⇒ maxClearance(s) ≥ classif ication(o)
>  preU pdate(clearance(s)) : clearance(s) = LU B(clearance(s), classif ication(o))" (p. 29)
> "a subject always start with the lowest possible clearance label. The clearance of the
> subject is raised to higher labels until it reaches its maximum label as the subject accesses
> higher objects." (p. 29)

**U13. RBAC high watermark, same pattern, with the authors noting it destroys least privilege.**
pp. 30–31, Examples 16 and 17.
> "Having an automated high watermark property in RBAC eliminates the least privilege
> principle that is supported in original models. It also causes a selection problem in case
> there are multiple roles available for a request." (p. 30)

**U14. Chinese Wall and dynamic separation of duty are named as covered — but only named.**
p. 38 (§6.1).
> "Mutability is a crucial property for history-based policies (e.g., dynamic SoD, Chinese
> Wall) and policies that require consumable attributes (e.g., most of commercial B2C DRM
> policies)." (p. 38)
> Also p. 8: "High watermark policies on subject clearance and Chinese Walls can also be
> enforced in this way."

**Search record for U14:** case-insensitive search of the full extracted text for `Chinese`
returns exactly **2** hits (p. 8, p. 38), both the assertions quoted above; `dynamic SoD`
returns **1** hit (p. 38, same sentence); `dynamic separation` returns **0**. **There is no
worked Chinese Wall example and no worked dynamic-SoD example anywhere in the paper.** The
only SoD treated at length is *static* SoD, and it is explicitly pushed out of the core model
(see U15).

**U15. Static SoD is explicitly excluded from the core model as an administrative matter, and
the model assumes such constraints are already enforced.**
pp. 37–38 (§6.1).
> "in U CON_ABC model, constraints that have to be applied to the assignments of immutable
> attributes are assumed to be already enforced." (p. 38)
> "Although we can make U CON_ABC model more complex to enforce static SoD by including
> 'Constraints' property within the model, since assignment of immutable attribute to subject
> or object is an administrative issue, and since U CON_ABC model is the first step in this
> arena, we consider only the core issues of usage control and keep the core model as simple
> as possible." (p. 38)

**U16. The model presupposes attribute values; it does not derive them, and says so twice.**
p. 8 and p. 9 footnote 1; reaffirmed p. 45.
> "Mutable attributes add further complication to the requirement for obtaining timely values
> of attributes from a trusted source, since now the attributes must also be modifiable in a
> trusted way." (p. 8)
> "Using attributes for access decisions requires a trusted source for the values and their
> timeliness. There are many challenges to achieving this. The details of how this would be
> accomplished is an important implementation and architectural issue. Nonetheless, in our
> view it is important to keep the model separate from these implementation concerns, however
> important they may be." (p. 9, footnote 1)
> "U CON_ABC leaves open the architecture and mechanisms for providing trusted attributes.
> This is one of the important challenges as we look ahead." (p. 45)

**U17. Delegation and administrative rights are explicitly out of scope; who may change a
policy is not modelled.**
p. 1 (abstract), p. 11 (§3.3), p. 45 (§8).
> "We call these core models because they address the essence of usage control, leaving
> administration, delegation and other important but second-order issues for later work." (p. 1)
> "In this paper we do not consider delegation rights and administrative rights." (p. 11)
> "Delegation of rights is among the crucial issues that should be covered within UCON
> framework. In addition, there should be a clear description of administration issues." (p. 45)

Where administration *is* discussed (§6.2, pp. 38–39), it is a sketch of a consumer /
provider / identifiee triangle with "serial" and "parallel" usage controls, and the section
opens by assuming the rules are given: "In this section we assume that usage rules such as
authorization, obligation, and condition rules are already provided." (p. 38)

**U18. Access review under mutability is characterised as a safety-analysis problem, not a
lookup.** This is UCON conceding that you cannot read off from the model what a sequence will
be permitted to do.
p. 11, footnote 2.
> "The U CON_ABC viewpoint has consequences for access review. Predicting which rights will be
> available when access is attempted becomes a problem more akin to safety analysis with
> respect to leakage of rights [Harrison et al 1976], than a simple lookup of relevant data
> structures." (p. 11, fn. 2)

**U19. The composition of UCON models is itself unanalysed, by the authors' admission.**
p. 45 (§8); see also p. 14.
> "We emphasize that we have only described the 'pure' models corresponding to individual
> points in these figures. In practice we would expect real systems to use composite models
> which combine several of these together. **Space does not permit us to explore the
> expressive power of combined models.**" (p. 45, emphasis added)
> "In this paper we are not trying to develop a logical expression language for the U CON_ABC
> model." (p. 14)

**U20. Obligations that affect only future requests ("global obligations") are excluded from
the core.**
p. 12 footnote 3; p. 28 (§4.7).
> "Such global obligations are outside the scope of U CON_ABC core models." (p. 12, fn. 3)
> "Since there is no influence on decision-making for current usages, this feature can't belong
> to U CON_B0, hence can't belong to U CON_B1, U CON_B2, or U CON_B3." (p. 28)
> And on the periodic-payment case: "Enforcement of periodic payment of accumulated expense is
> not considered as part of the core U CON_ABC model since it is not related to a request-based
> decision process but is part of larger workflow." (p. 18, fn. 6)

**U21. Conditions are intrinsically immutable, so the C-models contribute nothing to
history-dependence.**
p. 12 (§3.6), p. 14, p. 26 (§4.5).
> "Unlike authorizations or obligations, condition variables cannot be mutable since conditions
> are not under direct control of individual subjects. Evaluation of conditions cannot update
> any subject or object attributes." (p. 12)

**U22. UCON treats logs and payment records as first-class *derivative objects* under usage
control, and explicitly contemplates the subject having rights to redact them.** Bears
directly on manuscript claim (A).
pp. 10, 42–43 (§6.4, "Reverse UCON").
> "In UCON, however, the derivative object is an object that is created in consequence of
> obtaining or exercising rights on an original object. For example, playing MP3 music file can
> create usage log information. This log data file is called a derivative object in UCON." (p. 10)
> "Now Alice becomes both a provider subject (PS) and an identifiee subject (IS) of the
> log/payment information and may hold certain rights (PR and IR) on them such as the right
> that she can delete her ID from log information." (p. 42)
> "—To provide ability to refuse creation of derivative objects (the consumer may have to give
> up or reduce exercising original rights).
>  —To provide ability to restrict reverse usage by blocking certain part of derivative objects
> (i.e., identity) or by allowing only aggregated information of individual objects." (p. 43)

**U23. UCON's own verdict on XACML 1.0 (2002): it fails on mutability and on ongoing
decisions.** Useful, but date-check it: this is about the 2002 spec, not the 2013 one.
pp. 44–45 (§7).
> "Similar shortcomings can be found also in OASIS eXtensible Access Control Markup Language
> (XACML) [Godik and Moses 2002]. Although authorization in XACML is based on transaction or
> request, it fails to cover mutable cases and ongoing cases." (p. 45)
> On XrML, the parallel diagnosis: "XACML can express 'student can play a MP3 file 5 times' but
> assumes usage history of 'play' rights is supported by applications. Hence, it fails to
> resolve mutable cases such as 'after being played 2 times, now the MP3 file can be played only
> 3 more times'." (p. 44, of XrML; the XACML sentence follows immediately)

---

## HOW MUCH OF CLAIM (C) DOES UCON ALREADY COVER?

Claim (C): *per-action authorization does not compose into authorization of the sequence:
individually permitted steps can (i) breach a cumulative limit, (ii) jointly disclose a
protected value, or (iii) reach a prohibited terminal state.*

### Verdict: **SUBSTANTIALLY covered, and on conjunct (i) fully covered.**

Taking the conjuncts separately, because they come apart sharply.

**(i) Cumulative limits — FULLY COVERED. Do not claim this.**

This is not a gap UCON leaves; it is the thing UCON was built to close. The paper states the
problem in the manuscript's own terms on pp. 7–8 ("Policies requiring limits on the number of
accesses by a subject … can be easily specified using mutable attributes … various kinds of
consumable authorizations can be modelled in this manner", U2), and then delivers four
independent worked mechanisms: credit decrement with a guard (Example 3, p. 17, U8), an
explicit `k = k − 1` counter with guard `k ≥ 1` (Example 20, p. 32, U9), post-hoc metered
accumulation (Example 4, p. 17, U10), and a concurrency cap that revokes a live access when
the cap is exceeded (Examples 5–7, pp. 19–21, U11). In every case an attribute changes
*because of* an access such that a later otherwise-identical request is denied — the exact
mechanism the brief asked me to look for.

A JCS reviewer of Jajodia's background will read an unqualified "individually permitted steps
can breach a cumulative limit, and per-action authorization cannot see this" as a restatement
of UCON's motivating premise, twenty-two years late. The manuscript must cite Park & Sandhu
here and say what it adds, not present the observation as a finding.

**(ii) Joint disclosure of a protected value — NOT COVERED. This survives.**

Search record: `inference` → **0** hits in the full text. `aggregation` → **0**.
`aggregat` → **1** hit, p. 43, and it runs the *other* way (a privacy safeguard that would
release "only aggregated information of individual objects"). Nothing in the model reasons
about what a *set* of separately released objects jointly reveals.

The nearest thing is the mutable-attribute encoding: p. 9 offers "usage log (eg., already read
portion cannot be read again)" as an example of a mutable subject attribute, so a policy author
*could* hand-encode a disclosure constraint as an attribute predicate. But that is UCON
supplying a register, not an analysis. UCON never asks which combinations disclose, and by U16
it explicitly declines to model where attribute values come from. Chinese Wall (U14) is the
conflict-of-interest case, not the aggregation case, and in any event is asserted, not worked.

**(iii) Prohibited terminal states — PARTIALLY covered, and the part that is covered is
covered by assertion plus one worked analogue, not by a general treatment.**

Search record: `terminal` → **0** hits in the whole document. `terminal state` → 0. UCON has
no notion of a state a system must not reach; its objects of evaluation are a request and a
live usage, never a trajectory.

But the *pattern* — an earlier permitted act making a later act impermissible via a policy
predicate rather than a budget — is instantiated once, cleanly, in BLP high watermark
(Example 14, p. 29, U12): a permitted read at a higher classification raises `clearance(s)`,
after which a write that was previously permitted by the star property is forbidden. RBAC high
watermark (Examples 16–17, pp. 30–31) is the same shape. And Chinese Wall and dynamic SoD, the
canonical members of this family, are claimed as enforceable at p. 8 and p. 38 without being
formalised (U14).

So on (iii) the honest position is: UCON provides the mechanism and asserts the coverage; it
does not provide the analysis, the vocabulary, or a worked case of a *forbidden end state* as
distinct from a *forbidden next step*.

### What remains for the manuscript to claim

Five things survive, all of them narrower than a bare (C):

1. **UCON encodes; it does not detect.** The policy author must already know which cumulative
   constraint exists and must hand-write the attribute update that enforces it. Nothing in
   UCON identifies which constraints a deployment needs, or checks that a set of per-action
   policies is jointly adequate to a sequence-level goal. The paper declines to build the
   apparatus that would allow such a check: no logical expression language (p. 14, U19), and
   the expressive power of *combined* models is unexplored for want of space (p. 45, U19).

2. **The authors themselves say sequence-level prediction is hard.** p. 11 fn. 2 (U18) puts
   access review under mutability in the class of HRU safety analysis. That is a quotable
   concession, and it is friendly: the manuscript can cite UCON *for* the claim that
   per-action policy does not let you read off what a sequence may do, rather than against it.

3. **The unit of analysis has no sequence in it.** UCON's objects are subject, object, right,
   attributes. Search record: `workflow` → **1** hit, and it is used to push accumulated-payment
   enforcement *out* of the core ("not related to a request-based decision process but is part
   of larger workflow", p. 18 fn. 6). `task` → 2 hits, both bibliographic gestures at TBAC
   (Thomas & Sandhu 1997, cited p. 4 and p. 47) which UCON notes but does not incorporate.
   There is no plan, no trace, no goal, no terminal state.

4. **Attribute derivation is presupposed** (U16), which is where joint-disclosure reasoning
   would have to live.

5. **Standing to change policy is out of scope** (U17). UCON models what a policy permits, never
   who may alter it. Its administration section assumes the rules are given (p. 38).

### What the manuscript must stop claiming

Any unqualified form of "per-action authorization does not compose, e.g. because of cumulative
limits" — as a diagnosis, a novelty, or an unattributed observation. Cite pp. 7–8 and Examples 3,
4, 5, 20 directly, concede the point, and pivot to (1)–(5) above.

---

## Anticipations of manuscript claims (A) and (B) in UCON

**(A) A complete and internally consistent trace is compatible with an unauthorized action.**

*No direct anticipation.* Search record: `trace` → **0** hits, `audit` → **0** hits in the full
text. UCON has no trace, log-as-evidence, or after-the-fact-verification concept.

*Two adjacent findings, both useful.*

- **The log is a controlled object, so its content is a policy output.** U22: usage logs are
  "derivative objects" (p. 10) subject to UCON in their own right, and Reverse UCON
  contemplates a consumer with "the right that she can delete her ID from log information"
  (p. 42) and mechanisms "To provide ability to restrict reverse usage by blocking certain part
  of derivative objects (i.e., identity)" (p. 43). A trace whose contents are themselves governed
  by usage policy is one that can be complete-as-permitted and yet not record what happened.
  This is a *supporting* citation for (A) from inside the canonical usage-control paper.
- **Access review is undecidable-hard** (U18, p. 11 fn. 2). Consistency of a trace with policy
  is not readable off the policy.

**(B) A valid authorization can leave no trace at all.**

*Anticipated structurally, though never framed as a claim.* The immutable models are defined
precisely as the case where authorization changes nothing:

> "If all attributes are immutable, no updates are possible as a consequence of the decision
> process. This case is denoted as '0'." (p. 13)

`U CON_preA0` (Definition 1, p. 15) is `allowed(s, o, r) ⇒ preA(AT T (s), AT T (o), r)` with no
update procedure of any kind, and the paper places MAC, DAC, RBAC, and most trust management in
it ("Traditional access controls such as MAC, DAC, and RBAC are likely to belong to
U CON_preA0", p. 16). The condition models are immutable by construction: "the U CON_onC0 model
is intrinsically immutable" (p. 27). So a large, explicitly-named class of valid UCON
authorizations leaves no residue whatever. UCON never *says* this is a problem; the manuscript
can note that the model licenses it.

---

# PART II — OASIS XACML 3.0

## Précis (150 words)

XACML 3.0 is an XML policy language plus an evaluation semantics for a single authorization
decision. Its architecture separates the PEP (guards the resource, asks, enforces), the PDP
(evaluates policy, returns a decision), the PAP (writes policies), the PIP (supplies attribute
values), and a context handler that normalises requests and responses into a canonical XACML
context. Policy is a three-level tree — Rule, Policy, PolicySet — where each level names a
*combining algorithm* that resolves the results of its children into one decision. Decisions
are Permit, Deny, Indeterminate, or NotApplicable. Policies may attach *obligations* (the PEP
must discharge them or refuse) and *advice* (the PEP may ignore). Attributes are pulled into
the request context and are immutable during evaluation; there is no write-back, no counter,
and no memory of prior decisions. Administration and delegation — including who may issue a
policy — are handled in a separate profile, not here.

## Numbered claims

**X1. PEP / PDP / PAP / PIP are defined in the glossary, with ISO and IETF lineage.**
pp. 10 (§1.1.1).
> "Policy administration point (PAP): The system entity that creates a policy or policy set"
> "Policy decision point (PDP): The system entity that evaluates applicable policy and renders
> an authorization decision. … This term corresponds to 'Access Decision Function' (ADF) in
> [ISO10181-3]."
> "Policy enforcement point (PEP): The system entity that performs access control, by making
> decision requests and enforcing authorization decisions. … This term corresponds to 'Access
> Enforcement Function' (AEF) in [ISO10181-3]."
> "Policy information point (PIP): The system entity that acts as a source of attribute values"
> (all p. 10)

**X2. The 14-step data-flow model.**
pp. 19–20 (§3.1, Figure 1).
> "1. PAPs write policies and policy sets and make them available to the PDP. … 2. The access
> requester sends a request for access to the PEP. 3. The PEP sends the request for access to
> the context handler in its native request format … 13. The PEP fulfills the obligations.
> 14. (Not shown) If access is permitted, then the PEP permits access to the resource;
> otherwise, it denies access." (pp. 19–20)

**X3. Combining algorithms are the conflict-resolution / priority mechanism, and there are
four headline families plus ordered variants and two "unless" forms.** This is directly the
manuscript's "priority" field.
p. 15 (§2.3) for the overview; pp. 133–134 (Appendix B.9) for identifiers; pp. 135–148
(Appendix C) for normative pseudo-code.
> "Deny-overrides (Ordered and Unordered), Permit-overrides (Ordered and Unordered),
> First-applicable and Only-one-applicable." (p. 15)
> "In the case of the Deny-overrides algorithm, if a single <Rule> or <Policy> element is
> encountered that evaluates to 'Deny', then, regardless of the evaluation result of the other
> <Rule> or <Policy> elements in the applicable policy, the combined result is 'Deny'." (p. 15)
> "The 'Only-one-applicable' policy-combining algorithm only applies to policies. … If no policy
> or policy set applies, then the result is 'NotApplicable', but if more than one policy or
> policy set is applicable, then the result is 'Indeterminate'." (pp. 15–16)
> Appendix C adds Deny-unless-permit (§C.6, p. 139), Permit-unless-deny (§C.7), and legacy
> variants (§C.10 ff.), plus: "Users of this specification may, if necessary, define their own
> combining algorithms." (p. 16)

**X4. The combining machinery is a *decision* calculus with a five-valued extended
Indeterminate, not a state machine.**
pp. 83 (§7.10), 135 (§C.1–C.2).
> "The final decision returned by a PDP cannot be an extended Indeterminate. Any such decision
> at the top level policy or policy set is returned as a plain Indeterminate in the response
> from the PDP." (p. 83)
> Deny-overrides, normative behaviour: "1. If any decision is 'Deny', the result is 'Deny'.
> 2. Otherwise, if any decision is 'Indeterminate{DP}', the result is 'Indeterminate{DP}'. …
> 7. Otherwise, the result is 'NotApplicable'." (p. 135)

**X5. Combining is order-independent for obligations, hence obligation sets are
non-deterministic unless an ordered algorithm is chosen.**
pp. 135, 85.
> "The children may be processed in any order, so the set of obligations or advice provided by
> this algorithm is not deterministic." (p. 135)
> "In situations where any lack of determinism is unacceptable, a deterministic combining
> algorithm, such as ordered-deny-overrides, should be used." (p. 85)

**X6. Obligations are mandatory-on-pain-of-refusal; advice is ignorable. Neither has standard
semantics in 3.0.**
p. 18 (§2.12–2.13); p. 9 and p. 10 (glossary); p. 43; p. 85 (§7.18).
> "There are no standard definitions for these actions in version 3.0 of XACML. Therefore,
> bilateral agreement between a PAP and the PEP that will enforce its policies is required for
> correct interpretation. PEPs that conform to v3.0 of XACML are required to deny access unless
> they understand and can discharge all of the <Obligations> elements associated with the
> applicable policy." (p. 18)
> "In some applications it is helpful to specify supplemental information about a decision.
> XACML provides facilities to specify supplemental information about a decision with the
> <Advice> element. Such advice may be safely ignored by the PEP." (p. 18)
> "Obligation identifier. The value of the obligation identifier SHALL be interpreted by the
> PEP." (p. 61, §5.34)

**X7. Obligations only survive up the tree if the level's decision matches their `FulfillOn`,
so a Permit at the top can silently drop obligations attached to branches that lost.**
p. 85 (§7.18).
> "As a consequence of this procedure, no obligations or advice SHALL be returned to the PEP if
> the rule, policies, or policy sets from which they are drawn are not evaluated, or if their
> evaluated result is 'Indeterminate' or 'NotApplicable', or if the decision resulting from
> evaluating the rule, policy, or policy set does not match the decision resulting from
> evaluating an enclosing policy set." (p. 85)

**X8. XACML has NO state, history, or memory across decisions.**
Search record over the full 154-page extraction, case-insensitive:
`mutable` → **1** hit and it asserts the *opposite* (p. 78, quoted below);
`cumulative` → 0; `increment` → 0; `persist` → 0; `across requests` → 0;
`previous decision` → 0; `prior decision` → 0; `history` → 2 hits, both the
"Appendix E. Revision History" heading (pp. 8, 149); `workflow` → 0;
`chinese` → 0; `separation of dut` → 0; `dynamic separation` → 0; `write-back` → 0.

The positive statement of immutability within an evaluation:
> "SHALL behave as if each bag of attribute values is fully populated in the context before it
> is first tested, and is thereafter immutable during evaluation. (That is, every subsequent
> test of that attribute shall use the same bag of values that was initially tested.)" (p. 78, §7.3.5)

And the snapshot semantics of time:
> "This identifier indicates the current time at the context handler. In practice it is the
> time at which the request context was created. For this reason, if these identifiers appear
> in multiple places within a <Policy> or <PolicySet>, then the same value SHALL be assigned to
> each occurrence in the evaluation procedure, regardless of how much time elapses between the
> processing of the occurrences." (p. 132, §B.7)

**X9. The one cross-decision hook, `access-permitted`, evaluates a *hypothetical* request in
isolation — it is not a record of past decisions.**
p. 127 (§A.3.16).
> "The function SHALL invoke a complete policy evaluation using the newly constructed context.
> This evaluation SHALL be completely isolated from the evaluation which invoked the function,
> but shall use all current policies and combining algorithms, including any per request
> policies." (p. 127)
> Its risk is flagged separately: "It is possible that the function is invoked during the
> recursive invocations of the PDP such that loops are formed." (p. 91, §9.1.8)

**X10. Delegation is NOT in this document. The core carries exactly two hooks into a separate
profile.**
p. 13 (normative references); pp. 43, 44, 45, 49, 50.
The referenced document, verbatim from the reference list:
> "[XACMLAdmin] OASIS Committee Draft 03, XACML v3.0 Administration and Delegation Profile
> Version 1.0. 11 March 2010. http://docs.oasis-open.org/xacml/3.0/xacml-3.0-administration-v1-
> spec-cd-03-en.doc" (p. 13)

Hook 1, `<PolicyIssuer>` — the element that says *who issued a policy*:
> "The <PolicyIssuer> element contains attributes describing the issuer of the policy or policy
> set. The use of the policy issuer element is defined in a separate administration profile
> [XACMLAdmin]. A PDP which does not implement the administration profile MUST report an error
> or return an Indeterminate result if it encounters this element." (p. 45, §5.3)
> Also pp. 43 and 49: "The interpretation of the <PolicyIssuer> element is explained in the
> separate administrative policy profile [XACMLAdmin]."

Hook 2, `MaxDelegationDepth`:
> "MaxDelegationDepth [Optional] If present, limits the depth of delegation which is authorized
> by this policy set. See the delegation profile [XACMLAdmin]." (p. 44, §5.1; identical wording
> for <Policy> at p. 50, §5.14)

**Be precise in the manuscript:** the profile is a *Committee Draft 03* dated 11 March 2010, not
an OASIS Standard, and it is not this document. Note also that XACML 3.0 core is a January 2013
OASIS Standard referencing a March 2010 committee draft — worth stating if the manuscript leans
on delegation.

Two other capabilities are likewise profiled out: hierarchical resources [Hier] and multiple
decisions [Multi] (p. 12 references; p. 85 §7.16; p. 65).

**X11. Attributes are pulled, not derived, and the PDP does not classify the request — the
context handler and PEP decide what the request *is*.**
pp. 20 (§3.2), 77 (§7.3), 79 (§7.3.6).
> "Implementations must convert between the attribute representations in the application
> environment (e.g., SAML, J2SE, CORBA, and so on) and the attribute representations in the
> XACML context. How this is achieved is outside the scope of the XACML specification." (p. 20)
> "Standard environment attributes are listed in Section B.7. If a value for one of these
> attributes is supplied in the decision request, then the context handler SHALL use that value.
> Otherwise, the context handler SHALL supply a value." (p. 79)

**X12. A NotApplicable that is treated as Permit is a documented, named hole, and the spec
attributes it to a matching failure.** Directly relevant to (A).
p. 90 (§9.1.6).
> "If 'NotApplicable' is to be treated as 'Permit', it is vital that the matching algorithms
> used by the policy to match elements in the decision request be closely aligned with the data
> syntax used by the applications that will be submitting the decision request. A failure to
> match will result in 'NotApplicable' and be treated as 'Permit'. So an unintended failure to
> match may allow unintended access." (p. 90)

**X13. The PEP's behaviour on Indeterminate and NotApplicable is undefined in the base case;
the "bias" is a deployment choice.**
pp. 76–77 (§7.2).
> "If the decision is 'Not Applicable', then the PEP's behavior is undefined. If the decision is
> 'Indeterminate', then the PEP's behavior is undefined." (p. 76, §7.2.1 Base PEP)
> Deny-biased: "All other decisions SHALL result in the denial of access." (p. 77)
> Permit-biased: "All other decisions SHALL result in the permission of access." (p. 77)
> And in both: "Note: other actions, e.g. consultation of additional PDPs,
> reformulation/resubmission of the decision request, etc., are not prohibited." (p. 77)

**X14. Negative rules are documented as a source of policy violation under attribute
suppression and base-group drift, with distributed administration named as an aggravator.**
pp. 90–91 (§9.1.7).
> "An example of suppressed attributes would be if we have a policy that access should be
> permitted, unless the subject is a credit risk. If it is possible that the attribute of being
> a credit risk may be unknown to the PDP for some reason, then unauthorized access may result."
> (p. 91)
> "Problems of this type are easy to avoid when one individual administers all policies, but
> when administration is distributed, as XACML allows, this type of situation must be explicitly
> guarded against." (p. 91)

**X15. The trust model makes correctness contingent on the PEP actually enforcing, and nothing
in the system checks that it did.** Directly relevant to (A).
p. 93 (§9.2.6).
> "None of the entities of the authorization system are dependent on the PEP. They may collect
> data from it, (for example authentication data) but are responsible for verifying it
> themselves."
> "The correct operation of the system depends on the ability of the PEP to actually enforce
> policy decisions."
> "The PEP depends on the PDP to correctly evaluate policies. This in turn implies that the PDP
> is supplied with the correct inputs. Other than that, the PDP does not depend on the PEP."
> (all p. 93)

**X16. The PDP must always return one of exactly four decisions, and Indeterminate is the
catch-all.**
p. 85 (§7.17).
> "The PDP MUST return a response context, with one <Decision> element of value 'Permit',
> 'Deny', 'Indeterminate' or 'NotApplicable'. If the PDP cannot make a decision, then an
> 'Indeterminate' <Decision> element SHALL be returned." (p. 85)
> Missing-attribute handling forces eventual termination: "Note, this requirement forces the PDP
> to eventually return an authorization decision of 'Permit', 'Deny', or 'Indeterminate' with
> some other status code, in response to successively-refined requests." (p. 86, §7.19.3)

---

## Anticipations of manuscript claims (A) and (B) in XACML

**(A) A complete and internally consistent trace is compatible with an unauthorized action.**

*Anticipated in substance, three ways, all quotable and all in the non-normative §9.*

1. **Decision ≠ enforcement.** X15, p. 93: "The correct operation of the system depends on the
   ability of the PEP to actually enforce policy decisions," combined with "None of the entities
   of the authorization system are dependent on the PEP." A PDP transcript can be perfectly
   well-formed while the enforcement step diverged, and nothing in the architecture detects it.
2. **A clean Permit can rest on a matching failure.** X12, p. 90: "A failure to match will
   result in 'NotApplicable' and be treated as 'Permit'. So an unintended failure to match may
   allow unintended access." The request was well-formed, the evaluation was correct, the
   decision was consistent, and access should not have been granted.
3. **A clean Permit can rest on an attribute that was suppressed.** X14, p. 91, the credit-risk
   example. Same shape: internally consistent, substantively wrong.

The manuscript should cite (2) and (3) as the security literature's own version of (A). They
narrow the novelty of (A) considerably in its *epistemic* form, though XACML frames them as
implementation hazards rather than as a general property of authorization records.

**(B) A valid authorization can leave no trace at all.**

*Not addressed; nothing requires logging.* Search record: `audit` → **1** hit in 154 pages,
p. 92, and it concerns *policy* transparency, not decision recording:
> "In other environments, policies may be made freely available for distribution, inspection,
> and audit." (p. 92, §9.2.3.1)
`trace` → **1** hit, p. 74, an XPath implementation-defined-output note, irrelevant.

The specification defines no audit record, no decision log, no retention requirement, and no
obligation to emit one. The nearest available hook is an obligation, and obligations have no
standard semantics in 3.0 (X6, p. 18) — so any logging is a bilateral PAP–PEP agreement outside
the standard. **A conforming XACML deployment can render and enforce a valid Permit with no
persistent record whatever.** That is (B), textually supported by absence plus the stated search.

---

## Where the manuscript's claims survive, with textual evidence

| Manuscript claim | Status against these two sources | Load-bearing evidence |
|---|---|---|
| (A) complete consistent trace compatible with unauthorized action | **Substantially anticipated in XACML §9**, as implementation hazards rather than as a general property. Survives only if reframed as a property of authorization *records* generally, with XACML cited. | X12 p. 90; X14 p. 91; X15 p. 93. UCON adds a different angle: the log is itself a governed object that the subject may hold redaction rights over (U22, pp. 10, 42–43). |
| (B) valid authorization can leave no trace | **Survives.** Neither document requires a record. UCON's `0`-mutability models change nothing by construction; XACML has no audit requirement. | UCON p. 13 ("no updates are possible as a consequence of the decision process"), Definition 1 p. 15, p. 27; XACML search record for `audit`/`trace` above. |
| (C-i) cumulative limits | **Does not survive.** UCON owns this. | UCON pp. 7–8 (U2); Examples 3 (p. 17), 4 (p. 17), 5–7 (pp. 19–21), 20 (p. 32), 22–24 (pp. 33–34). |
| (C-ii) joint disclosure | **Survives cleanly.** Neither document reasons about what a set of permitted releases jointly reveals. | UCON: `inference` 0 hits, `aggregation` 0 hits; the one `aggregat` hit (p. 43) is a privacy safeguard running the other way. XACML: `inference` 0 hits. |
| (C-iii) prohibited terminal state | **Survives in vocabulary and generality; the underlying pattern does not.** UCON asserts Chinese Wall / dynamic SoD coverage (p. 8, p. 38) without formalising either, and works the pattern once as BLP high watermark (p. 29). Neither document has a notion of a terminal state (`terminal` 0 hits in UCON). | UCON U12 p. 29, U14 p. 38 with search record; XACML X8 search record. |
| Composition of per-action policies is un-analysed | **Survives, and UCON concedes it.** | UCON p. 45: "Space does not permit us to explore the expressive power of combined models"; p. 14: "we are not trying to develop a logical expression language"; p. 11 fn. 2 (safety analysis). |
| Attribute *derivation* / classifying the incoming request | **Survives.** Both models presuppose attribute values from elsewhere. | UCON p. 9 fn. 1, p. 8, p. 45 (U16); XACML p. 20, p. 79 (X11). |
| Standing to change policy, as against what policy permits | **Survives in both core documents, but is exactly the subject of XACML's separate Administration and Delegation Profile.** Be careful: this is a live literature the manuscript must engage, not a gap. | UCON p. 1, p. 11, p. 45 (U17); XACML p. 45 §5.3, p. 13 reference, pp. 44/50 `MaxDelegationDepth` (X10). |
| "Priority" as a field in the manuscript's authorization record | **Prior art exists and is normative.** Not a gap; the manuscript should map its field onto XACML's combining algorithms and say what differs. | XACML p. 15, pp. 133–134, Appendix C pp. 135–148 (X3); non-determinism caveat p. 135, p. 85 (X5). |

---

## Two things a JCS reviewer will check, and what the sources say

1. **"Doesn't UCON already do continuous authorization of long-running actions?"** Yes, and it
   is definitional: `onA`/`onB`/`onC` with `stopped(s,o,r)` on predicate failure (U3, U4;
   pp. 11, 19, 25, 27). If the manuscript's contribution is framed as "authorization should be
   continuous, not one-shot," it has no contribution. The re-evaluation *trigger*, however, is
   explicitly unspecified — "we do not specify these technical and implementation details"
   (p. 19) — and that is a real opening.

2. **"Is XACML really stateless, or are you just not counting obligations?"** Obligations are
   the only write-path, and XACML defines no semantics for them ("There are no standard
   definitions for these actions in version 3.0 of XACML", p. 18). So a deployment can achieve
   cross-decision state by having the PEP discharge an obligation that updates a PIP-visible
   attribute — but that is outside the standard, and the standard's own evaluation model forbids
   mutation within a decision (p. 78) and fixes time to a snapshot (p. 132). Say it that way, or
   the reviewer will.
