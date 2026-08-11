# Source audit: RFC 2693 (SPKI) and Li, Grosof & Feigenbaum (Delegation Logic)

Prepared for a *Journal of Computer Security* submission on authorization of AI-agent
actions. Adversarial brief: find where these two works already do what the manuscript
treats as missing.

**Provenance and pagination**

| Item | Detail |
|---|---|
| SPKI file | `/Users/brettreynolds/projects/LLM-CLI-projects/literature/ellison1999spki.txt` (2,411 lines, plain-text RFC) |
| SPKI pagination | The RFC's own `[Page N]` markers; verified against the RFC's Table of Contents (§6.3.1→25, §6.3.2→27, §6.3.4→28, §7.5→35, §8→37 all match). Cite by **RFC section** first, page second. |
| DL file | `/Users/brettreynolds/projects/LLM-CLI-projects/literature/li2003delegationlogic.pdf` (42 pp.) |
| DL pagination | **This is the authors' preprint, folioed 1–42, not the journal offprint.** Page numbers below are this PDF's own printed folios, verified by re-extracting individual pages with `pdftotext -f N -l N`. The published article is said to run TISSEC 6(1):128–171 (44 pp.), so the journal folios are *not* simply 127+N, and I have not converted them. **Anyone citing a page must re-check against the ACM version.** |
| Journal metadata | The PDF front matter contains **no** journal name, volume, issue, or page range. The "ACM TISSEC 6(1):128–171, 2003" data came from the task brief, not from this file. Flagged, not adopted. |

---

# A. Ellison, Frantz, Lampson, Rivest, Thomas & Ylonen (1999), RFC 2693, *SPKI Certificate Theory*

## Précis (152 words)

RFC 2693 is the rationale document for SPKI: it gives the theory behind SPKI
certificates and ACLs "without going into technical detail about those structures or
their uses" (Abstract, p. 1). Its polemic is that a certificate's job is authorization,
not authentication, because the datum an application needs "is almost never the spelling
of a keyholder's name" (§3, p. 13). It reconstructs the history of name certification
(§2), argues globally unique names are politically and operationally unavailable, and
adopts SDSI local names, made global by anchoring each name space to a public key (§2.6,
§2.8). It then specifies delegation with a single boolean bit (§4), validity conditions
including timed CRLs, timed revalidations and one-time revalidations (§5), and a
5-tuple/4-tuple reduction calculus that folds a credential chain into one authorization
result (§6). Sections 7 and 8 cover key management and a two-point security argument for
`authorization→key` over `authorization→name` plus `name→key`.

## Claims

**A1. The document's own scope is theory, not mechanism.**
Abstract, p. 1.
> "This document gives the theory behind SPKI certificates and ACLs without going into technical detail about those structures or their uses."

**A2. The unit of decision is one authorization computation over one question.**
§6.6, p. 32.
> "Typically, one will reduce a chain of certificates to answer an authorization question in one of two forms: 1. Is this Subject, S, allowed to do A, under this ACL and with this set of certificates? 2. What is Subject S allowed to do…"

**A3. A 5-tuple is `<Issuer, Subject, Delegation, Authorization, Validity>`; delegation is a boolean.**
§6.1, pp. 23–24.
> "Delegation: a boolean. If TRUE, then the Subject is permitted by the Issuer to further propagate the authorization in this intermediate result."

**A4. The reduction rule. This is the core of the non-amplification question.**
§6.3, p. 24.
> "The two 5-tuples: `<I1,S1,D1,A1,V1> + <I2,S2,D2,A2,V2>` yield `<I1,S2,D2,AIntersect(A1,A2),VIntersect(V1,V2)>` provided the two intersections succeed, S1 = I2 and D1 = TRUE"

**A5. `AIntersect` is set intersection, and longer tag lists are stipulated to be narrower.**
§6.3.1, p. 25.
> "If one list is longer than the other but match at all elements where both lists have elements, then the longer list is the result of the intersection. This means that additional elements of a list must restrict the permission granted."

**A6. But that narrowing is an application-level convention, not an enforced invariant.**
§6.3.1, p. 25.
> "Although actual authorization string definitions are application dependent, AIntersect provides rules for automatic intersection of these strings… Special semantics would require special reduction software."

**A7. `VIntersect` narrows the validity window, and folds online-test windows into it.**
§6.3.2, p. 27.
> "Vmin = max( Xmin, Ymin ) Vmax = min( Xmax, Ymax ) and if Vmin > Vmax, then the intersection failed."
And: "Each such test carries with it a validity interval, in terms of dates. That validity interval is intersected with any present in the certificate, to yield a new, current validity interval."

**A8. Boolean depth control was chosen over integer depth, and the authors say why.**
§4.1.4, p. 16.
> "The integer control option was the original design and has appeal, but was defeated by the inability to predict the proper depth of delegation."
And, on what depth control does *not* buy you: "As for controlling the proliferation of permissions, there is no control on the width of the delegation tree, so control on its depth is not a tight control on proliferation."

**A9. The authors concede that withholding the delegation bit is not enforceable.**
§4.1.1, p. 15.
> "if a keyholder is given permission to do something but not the permission to delegate it, then it is possible for that keyholder to loan out the empowered private key or to set up a proxy service, signing challenges or requests for the intended delegate."

**A10. And they concede a second, structural bypass: grant to a *name* and the keyholder can re-delegate at will.**
§7.5, p. 35.
> "If one delegates some authorization to (name (hash sha1 |…|) carl) and a different authorization to (hash sha1 |…|) directly, both without granting the permission to delegate, that key can delegate at will through <name,key> certificates in the former case and not delegate at all in the latter case."

**A11. Restricting who may *exercise* a permission was considered and abandoned.**
§4.2, p. 17.
> "We decided that a delegator is free to create a new key pair, also controlled by it, and delegate the rights to that key to exercise the delegated permission. Therefore, there was no benefit from attempting to restrict the exercise of a permission by someone permitted to delegate it."

**A12. The root of authority is an unsigned, uncommunicated, local object.**
§1.1 Glossary, p. 4, and §3.4, p. 15.
> "An ACL entry has potentially the same content as a certificate body, but has no Issuer (and is not signed)."
> "In SPKI, an ACL entry is free to be implemented in any way the developer chooses, since it is never communicated and therefore does not need to be standardized."

**A13. Every authorization computation is required to be deterministic; wandering CRLs are banned for exactly that reason.**
§5.1, p. 19.
> "SPKI has ruled out the use of wandering anti-matter CRLs for its certificates. Every authorization computation is deterministic, under SPKI rules."

**A14. One-time revalidation is scoped to a single computation, and expires with it.**
§5.5, pp. 20–21.
> "This form of revalidation has no lifetime beyond the current authorization computation… This protocol takes the place of a validity date range and represents a validity interval of zero, starting and ending at the time the authorization computation completes."

**A15. The validity interval is a risk-management parameter, framed as tolerance for acting on a known-false statement.**
§5.4, p. 20.
> "To set this validity interval, one must answer the question: 'How long are you willing to let the world believe and act on a statement you know to be false?'"

**A16. Authorization-not-identity, with the security argument stated.**
§8, p. 37.
> "Each certificate has an issuer. If that issuer is subverted, then the attacker can gain access. In the former case, there is only one issuer to trust. In the latter case, there are two."
And §3, p. 13: "the application needs to know if the keyholder is authorized for some access. This is the primary job of a certificate, according to the members of the SPKI WG".

**A17. Local names, made global by keying the name space; SPKI does not enforce one key per name.**
§2.8, p. 11, and §2.10, p. 12.
> "It is SDSI 1.0 convention, preserved in SPKI, that if a (local) SDSI name occurs within a certificate, then the public key of the issuer is the identifier of the name space in which that name is defined."
> "SPKI/SDSI does not claim to enforce one key per name. Therefore, a named group can be defined by issuing multiple (name,key) certificates with the same name -- one for each group member."

**A18. Path discovery is pushed onto the prover; the verifier just replays a supplied order.**
§6.3.4, p. 28.
> "All reduction operations are in the order provided by the prover. That simplifies the job of the verifier, but leaves the job of finding the correct list of reductions to the prover."

**A19. Rivest's objection, recorded and left unresolved: the verifier, not the issuer, bears the risk.**
§5.7.2, pp. 21–22.
> "in the commercial space, it is the verifier and not the issuer who is taking a risk by accepting a certificate. It should therefore be the verifier who decides what level of assurance he needs before accepting a credential… This line of thought deserves further consideration, but is not reflected in the SPKI structure definition."

---

# B. Li, Grosof & Feigenbaum, *Delegation Logic: A Logic-based Approach to Distributed Authorization*

## Précis (149 words)

Delegation Logic recasts distributed authorization as a knowledge-representation
problem. The paper presents D1LP, the monotonic fragment, which extends Datalog definite
ordinary logic programs by attaching an issuer to every atom and adding three statement
forms: `X says ba`, `X delegates ba^d to PE`, and `Y represents X on ba` (§3.1, pp. 10–12).
Delegation carries an explicit depth, an integer or `*`, and delegatees may be complex
principal structures built from conjunction, disjunction, and static unweighted, static
weighted, and dynamic thresholds (§3.1, p. 12). Semantics is given by compiling D1LP into
an ordinary logic program with two predicates, `holds/3` and `delegates/5`, whose extra
`len` field counts depth-consuming steps (§4.1, pp. 21–22). The paper's formal results are
about cost, not safety: Lemmas 1–4 bound transformation growth, and Theorems 5–7 give
`O(N⁴D²)` transform size and time and `O(N^{v+4}D²)` inferencing (§5, pp. 33–35). An XSB
implementation, XD1LP, is reported (§7.1, p. 38).

## Claims

**B1. Authorization is defined as proof-of-compliance for one request.**
Abstract, p. 1.
> "we adopt the trust-management approach, in which 'authorization' is viewed as a 'proof-of-compliance' problem: Does a set of credentials prove that a request complies with a policy?"

**B2. Delegation means transferability of support for a base atom, at a stated depth.**
§3.1, p. 12.
> "In a delegation statement (8) 'X delegates ba^d to PE ,' X is called the issuer of this statement; d is called the delegation depth (9) of this delegation ('∗' means unlimited depth)"
And: "In DL, the basic meaning of a delegation is transferability of support."

**B3. Depth is a re-delegation counter, consumed one step at a time.**
§3.3, pp. 14–15.
> "depth 1 means that no re-delegation is allowed, depth 2 means that one further step is allowed, depth 3 means that two further steps are allowed, and depth ∗ means that unlimited re-delegation is allowed."
> "Bob can delegate this permission to another entity say, Carl, but one step of depth is consumed in this re-delegation step. Carl cannot effectively delegate this permission further."

**B4. Depth is downward-closed: a stronger delegation entails all weaker ones.**
§3.3, p. 15.
> "A depth-d delegation from A to B about a base atom ba implies all delegations of depth smaller than d from A to B about ba. In particular, a depth-∗ delegation implies all integer-depth delegations."

**B5. The authors argue directly against SPKI's §4.1.4 reasoning, quoting it.**
§3.3, p. 15.
> "We disagree with these arguments for the following three reasons. First, whether delegation depths can be properly predicted depends on the application using the system."
And, on the laptop-key case: "In the boolean approach, one has no choice but to allow infinite delegation. In DL, one can use delegation depth 2."

**B6. Depth control is justified by non-transitivity of trust.**
§3.3, p. 15.
> "A more philosophical reason for limiting delegation with respect to depth is that trust is not transitive"
> "even if Bob trusts Carl about goodCredit(?X), and Carl trusts David about goodCredit(?X), Bob does not necessarily trust David about goodCredit(?X)."

**B7. The chaining rule enforces non-amplification of depth, with the rationale stated in one clause.**
§4.1, step 9, "Delegation chaining meta-rule," pp. 24–25.
> "delegates(A, ba, min(d ⊖ len, dep), C, len ⊕ ll) if delegates(A, ba, d, B, ll), PExpand(BE , delegates(ba, dep, C, len))."
> "The depth of this newly derived delegation is bounded by the depth dep, because A should not trust C more than BE trusts C. It is also bounded by the depth d minus the number of delegation steps that have already been used to derive the delegation from BE to C."

*Glyph note.* `pdftotext` drops the ⊖ operator (it renders as whitespace, giving
"min(d len, dep)"). I confirmed the glyph is a circled minus by rendering p. 25 at 200 dpi
and reading it. Its definition, immediately below the rule on p. 25, is
"d1 ⊖ d2 = d1 − d2 / ∗ ⊖ d1 = ∗ / ∗ ⊖ ∗ = ∗". The companion operator ⊕ is defined on p. 21:
"d1 ⊕ d2 = ∗ if d1 = ∗, or d2 = ∗, or d1 + d2 > D; d1 + d2 otherwise". Anyone quoting this
rule from a text extraction will silently lose the operator.

**B8. The two weakening meta-rules run only one way, downward.**
§4.1, steps 11 and 13, p. 25.
> "delegates(A, ba, dep, C, len) if delegates(A, ba, dep ⊕ 1, C, len). This meta-rule states that a smaller-depth delegation may be derived if a corresponding larger-depth delegation is derived."

**B9. Representation statements are an explicit, deliberate exception to depth-based non-amplification, and only the trust root may make them.**
§3.5, pp. 17–18.
> "The representation statement is strictly stronger than the delegation statement. If 'Y represents X on ba,' then Y has all the power that X has with respect to ba, even if X is not allowed to re-delegate this power. In other words, conclusions drawn from a representation statement don't consume any delegation depth."
> "As one can see, a representation statement essentially circumvents the delegation-depth restriction. Therefore, a rule with a representation statement in its head always has the principal Local, i.e., the trust root, as its issuer. A principal B can issue a statement saying that B delegates to C. But B cannot say that C represents B."

**B10. Width can be controlled too, by conjunctive delegatees, with a throwaway key as the fence.**
§3.6, Example 4, p. 20.
> "Alice delegates access(docZ)^∗ to (Bob,tmpKey). tmpKey delegates access(docZ)^1 to threshold(1, ?X, Carl says member(?X,orgA))."
> "Bob can delegate freely. But tmpKey only delegates to those principals certified by Carl to be members of orgA, and tmpKey does not allow re-delegation."

**B11. Delegation strength is a partial order, and disjunctive/conjunctive delegatees have a stated entailment direction.**
§6.1, pp. 35–36.
> "'A delegates to (B;C)' is logically equivalent to the conjunction of 'A delegates to B' and 'A delegates to C.' By contrast, 'A delegates to (B,C)' is weaker than either 'A delegates to B' or 'A delegates to C'"
And §6.2, p. 37: "'A delegates to P S1' is stronger than 'A delegates to P S2' if and only if P S2 ⇒ P S1 is a tautology."

**B12. There is exactly one viewpoint per decision: the authorizer's.**
§3.4, p. 17.
> "In DL, there is always a single, distinguished viewpoint: the viewpoint of the principal who is doing reasoning and making authorization decisions, i.e., the current trust root, referred to as 'Local.'"

**B13. Locally stored policy is unsigned, and the trust root may bypass the engine entirely.**
§3.4, p. 16, and §3.5, p. 18.
> "Policies that are securely stored locally do not need to be signed."
> "Also note that the trust root has no incentive to cheat on depth, because it can choose to authorize a request without consulting the trust-management engine."

**B14. The formal results are complexity results; there is no safety or soundness-of-authority theorem.**
Lemmas 1–4 sit in §4.1 (p. 27), §4.3 (pp. 30–31) and §4.4 (pp. 31–32) and bound `PExpand`
growth factors; §5.1, p. 33 gathers them ("From Lemmas 1, 2, 3, and 4 in Sections 4.1, 4.3,
and 4.4"). Theorems 5 and 6 are on p. 33, Theorem 7 on p. 35, and they are the only
theorems in the paper:
> "Theorem 5 (Tractable Transform Size). Given a D1LP P, the size of O = Trans(P) is O(N⁴D²)"
> "Theorem 7 (Tractable D1LP Inferencing). Given a D1LP P that is VB(v), computing the minimal D1LP model of P has time complexity O(N^{v+4}D²)"
Searched the whole file for `Theorem|Lemma|Proposition|Definition` at line start: the seven results above are the complete set. No non-amplification, safety, or authority-containment theorem is stated or proved.

**B15. Tractability forces a syntactic restriction on what can be asked.**
§3.1, p. 13, and §6, p. 36.
> "A delegation statement appearing in a query or a rule-body… must have a delegatee that is a principal, a principal variable, or a conjunction of principals. That is, such a delegatee is not permitted to contain a disjunction or a threshold structure… This restriction is called the conjunctive-delegatee-queries restriction."
> "In order to keep D1LP's semantics tractable, we impose the limitation that D1LP only generates delegation to a single principal as conclusions."

**B16. Their reading of SPKI: boolean re-delegation control, and tag intersection is under-specified.**
§2.2.3, p. 9.
> "The second difference is that SPKI 2.0 has boolean re-delegation control, while KeyNote has no re-delegation control. Otherwise, SPKI 2.0 has the same limitations as KeyNote."
> "only an incomplete prose description and several examples of tag intersections are given in [15]… Howell pointed out that intersection between some kinds of tags may not be finitely representable using tags; he gave a precise specification for tag intersection, in which intersections in potentially problematic cases are artificially defined to be empty."

**B17. Declared out of scope / future work: credential discovery, predicate agreement, wire formats.**
§7.2, pp. 38–39.
> "There are several additional infrastructural issues, beyond what we discussed here, that are practically important for developing real-world systems based on DL, and which are the subject of current and future work. For example, how can different entities agree on meanings of predicates? Which data structures and communication protocols should one use for exchanging DL rules…?"
> "Another unresolved infrastructural question is how an authorizer obtains all the credentials needed to make the decision."

**B18. Declared out of scope: nonmonotonic policy, with an admitted obstruction.**
§7.3, p. 39.
> "D2LP as defined in [29] prohibits delegation statements from appearing in queries or rule-bodies. Also note that, when using nonmonotonic policies, one often needs complete information about certain things in order to derive correct conclusions, and complete information is inherently hard to obtain in distributed environments. These difficulties need to be resolved before one can use nonmonotonic policies in trust management."

**B19. Also set aside: typing for DL, and dynamic weighted thresholds.**
§4.2, p. 28, and §4.4, p. 32.
> "Although we think that adding types to DL is potentially very useful, we do not pursue this topic further in this paper, because it is not our main topic."
> "We also considered incorporating dynamic weighted threshold structures [31] into DL; however, they pose difficulties for ensuring tractability."

**B20. Sushil Jajodia is a cited author here, twice.**
References [22] and [23], p. 41.
> "[22] Sushil Jajodia, Pierangela Samarati, and V. S. Subrahmanian. A logical language for expressing authorizations. In Proceedings of the 1997 IEEE Symposium on Security and Privacy, pages 31–42."
> "[23] Sushil Jajodia, Pierangela Samarati, V. S. Subrahmanian, and Elisa Bertino. A unified framework for enforcing multiple access control policies. In Proceedings of ACM SIGMOD International Conference on Management of Data, pages 474–485, 1997."
Both are cited in §1 as prior logic-based work on security policy that "focused on centralized environments and did not address the delegation aspect of distributed authorization" (p. 5). A reviewer who is Jajodia will know exactly how DL positions his 1997 papers.

---

# Anticipations of the manuscript's claims

## Claim (B): a valid authorization can leave no trace at all. **Fully anticipated, in both works.**

This is the strongest anticipation, and it is not a near-miss. Both canonical systems put
the root of authority in an object that is by design unsigned, uncommunicated, and
invisible to any credential chain.

- SPKI §1.1, p. 4: an ACL entry "has no Issuer (and is not signed)". §3.4, p. 15: "it is
  never communicated and therefore does not need to be standardized." The ACL is
  simultaneously "the source of empowerment for certificates" (§1.1, p. 4). So the thing
  that authorizes everything is the one thing that produces no artifact.
- DL §3.4, p. 16: "Policies that are securely stored locally do not need to be signed."
- DL §3.5, p. 18 goes further and says the authorizer can skip the mechanism altogether:
  "the trust root has no incentive to cheat on depth, because it can choose to authorize a
  request without consulting the trust-management engine."

**Consequence for the manuscript.** Claim (B) as stated will read to a JCS reviewer as a
restatement of a 1999/2003 design property, not a finding. It needs either to be dropped
as a claim and retained as a premise with these two citations, or sharpened into something
the canon does *not* say. The available sharpening: the canon treats the traceless root as
benign because the root is the risk-bearer and is co-located with the resource. An
AI-agent setting breaks that co-location, and the manuscript could argue that
tracelessness stops being benign once the authorizing principal is not the party that
suffers the consequence. That is a different claim, and it is defensible.

## Claim (A): a complete, internally consistent trace is compatible with the action being unauthorized. **Partially anticipated in SPKI.**

RFC 2693 §4.1.1, p. 15 states the mechanism precisely: a keyholder can "loan out the
empowered private key or to set up a proxy service, signing challenges or requests for the
intended delegate." The verifier then sees a chain that reduces cleanly, with a valid
signature by an authorized key, while the acting party is someone else. §7.5, p. 35 gives
a second, purely structural version: an authorization granted to a *name* rather than a
key lets the name-space owner "delegate at will through <name,key> certificates" even
though the delegation bit was withheld. §4.2, p. 17 records that they gave up on
separating delegation from exercise for the same reason.

**Where this falls short of the manuscript's (A).** SPKI describes these as reasons *not
to try* to enforce a restriction; it does not draw the epistemic conclusion that a valid
trace under-determines authorization status, and it has no notion of "trace" at all
(zero occurrences of `audit`, `accountab`, `trace` in the authorization sense; see search
log). The manuscript's (A) is therefore not anticipated as a *claim*, but the underlying
phenomenon is documented in the canon and must be cited. Do not present the loaned-key or
signing-oracle case as new.

## Grant-relative non-amplification. **Anticipated in both, with important differences.**

This is the item the brief flagged as a likely direct anticipation, and it is one.

**SPKI enforces it structurally, on all three carried fields.** §6.3, p. 24: the reduction
of `<I1,S1,D1,A1,V1> + <I2,S2,D2,A2,V2>` yields `<I1,S2,D2,AIntersect(A1,A2),VIntersect(V1,V2)>`
subject to `D1 = TRUE`. Authority is intersected (§6.3.1, p. 25), validity is intersected
(§6.3.2, p. 27), and the delegation bit cannot be raised because `D1 = TRUE` is a
precondition, so `D2 ≤ D1` always. The resulting tuple is issued by `I1`, the original
grantor. That is grant-relative non-amplification in three dimensions, specified in 1999.

**DL enforces it on depth, arithmetically, with the rationale spelled out.** §4.1 step 9,
pp. 24–25: derived depth is `min(d ⊖ len, dep)`, "because A should not trust C more than
BE trusts C." Steps 11 and 13 weaken only downward. §3.3, p. 15 makes depth downward
closed. And DL is non-amplifying in the *permission* dimension for free, because
delegation is per base atom: rule 8's propagation requires the same `ba` on both sides, so
a delegatee cannot broaden the atom.

**Three qualifications the manuscript can use, and should not overlook.**

1. **SPKI's version is a convention imposed on the application, not an invariant of the
   system.** §6.3.1, p. 25: "actual authorization string definitions are application
   dependent… Special semantics would require special reduction software." The claim that
   "additional elements of a list must restrict the permission granted" is a stipulation
   about how applications should design tags. An application that violates it breaks
   non-amplification while every certificate remains valid. DL p. 9 reinforces this from
   outside: Howell showed tag intersection "may not be finitely representable using tags,"
   and had to define awkward cases "artificially… to be empty."
2. **DL carves out an explicit exception.** §3.5, p. 18: representation statements
   "essentially circumvent the delegation-depth restriction," and conclusions drawn
   through them "don't consume any delegation depth." The exception is fenced by making
   the trust root the only permitted issuer, which is a *governance* fix rather than a
   logical one.
3. **Neither work proves non-amplification.** SPKI's §6 is presented as illustrative:
   "The processing plan presented here is an example that may be followed, but its primary
   purpose is to clarify the semantics of an SPKI certificate" (§6, p. 22). DL's only
   theorems are Lemmas 1–4 and Theorems 5–7, all about size and time (see B14).

**Consequence for the manuscript.** If "grant-relative non-amplification" is presented as
a new principle, a reviewer who knows RFC 2693 §6.3 will reject it on sight. It must be
introduced as the canonical property, cited to §6.3/§6.3.1 and to DL step 9, and the
manuscript's contribution must be located elsewhere: either in extending it to a dimension
the canon does not carry (see below), or in the observation that both canonical
enforcements are grant-relative *per credential chain* and say nothing about a run of
chains.

## Claim (C): per-action authorization does not compose into authorization of the sequence. **Not anticipated. Nothing in either document addresses it.**

See the next section for the textual evidence and the search log.

---

# Where the manuscript's claims survive

## (C) survives, and the canon is unambiguous that authorization is per-request

**SPKI.** The decision unit is a single "authorization computation" answering a single
question (A2, §6.6, p. 32). The determinism requirement (§5.1, p. 19: "Every authorization
computation is deterministic, under SPKI rules") is a *within-computation* property; it is
about eliminating timing dependence on CRL propagation, not about relating one computation
to the next. One-time revalidation is explicitly bounded by the computation: "no lifetime
beyond the current authorization computation… a validity interval of zero, starting and
ending at the time the authorization computation completes" (§5.5, pp. 20–21).

Everything SPKI has that spans time is a *validity window on a credential*, never a
constraint on a run of actions:

- validity dates in the 5-tuple and 4-tuple (§6.1 p. 24, §6.2 p. 24)
- timed CRLs, whose date ranges must not intersect (§5.2, p. 19)
- timed revalidations (§5.3, p. 20), one-time revalidations (§5.5, p. 20), short-lived
  certificates (§5.6, p. 21)

The nearest thing to a quantitative limit anywhere in the RFC is the tag wildcard
`(* range <ordering> <lower-limit>? <upper-limit>?)` (§6.3.1, p. 25), which bounds a value
*within one request's tag*, not a total across requests.

**Delegation Logic.** Stronger still, and the evidence is unusually clean: **the string
`valid` does not occur anywhere in the paper** (`grep -c -i valid` returns 0). D1LP has no
validity periods, no revocation, no clock, no state. It is Datalog plus issuers: no
function symbols of nonzero arity (§5.2, p. 34), hence no arithmetic aggregation over a
history, and no negation (`"Definite" means without negation`, footnote 2, p. 5). It is
declared monotonic (Abstract, p. 1: "we describe D1LP, the monotonic version of DL"),
which forecloses the very shape of a cumulative prohibition: adding the fact that a
further step occurred can never retract a conclusion that a step is permitted.

The paper knows nonmonotonicity is where such policies would live, and defers it
(§7.3, p. 39, quoted at B18), noting that nonmonotonic policy "often needs complete
information about certain things," which "is inherently hard to obtain in distributed
environments." That sentence is the closest either work comes to acknowledging the
manuscript's problem, and it stops at the doorstep.

**The one place a reviewer might push, and the answer.** DL's requirement (6),
§1, p. 4, gives a spending example:

> "It is also useful to infer additional attributes based on these field values and to
> delegate attribute authority to a certain entity only for certain specific field values,
> e.g., only when spending level is below a certain limit."

This is a predicate on a field value carried by *this* request or credential. There is no
mechanism in D1LP to compute a running total, and given Datalog-without-arithmetic there
could not be one. Similarly, DL's weighted thresholds sum weights (§3.1, p. 12: "the sum
of the weights of all those principals that support the base atom"), but that aggregates
*support from principals for one base atom*, not effects across operations. Both are worth
naming pre-emptively in the manuscript, because a JCS reviewer will reach for them.

**Recommended framing.** Claim (C) is best stated as: the canonical decentralized
authorization calculi are, by construction, functions from (credential set, request) to a
verdict, with no argument place for what has already happened. SPKI's temporal machinery
constrains credential currency; DL has no temporal machinery at all. Neither can express
a cumulative limit, a joint-disclosure condition, or a prohibited terminal state, and DL's
monotonicity makes the first of these expressible only by leaving the monotonic fragment.
Cite §5–§6 of RFC 2693 and §5.2, §7.3, Abstract of DL. That is an evidenced negative,
narrow enough to hold.

## Two further openings the canon leaves

1. **Risk-bearer vs. decision-maker.** RFC 2693 §5.7.2, pp. 21–22 records Rivest's
   argument that "it is the verifier and not the issuer who is taking a risk," and then
   says flatly: "This line of thought deserves further consideration, but is not reflected
   in the SPKI structure definition." An unclosed question in the canon, and one that maps
   onto agent deployment, where the party bearing the consequence is neither the issuer
   nor the executing agent.
2. **Proliferation width.** SPKI §4.1.4, p. 16 concedes "there is no control on the width
   of the delegation tree." DL answers this for delegation (Example 4, p. 20) but not for
   *exercise*: nothing in either system bounds how many times a granted permission is
   used. That is the same gap as (C), approached from the canon's own admitted weakness,
   and citing it that way is much stronger than asserting a gap from outside.

---

# Search log for the negative findings

Required under the negative-claims rule. All searches case-insensitive, over the full
text of each document (`dl.txt` = `pdftotext -layout` of all 42 pages).

**RFC 2693 — zero occurrences:** `audit`, `accountab`, `non-goal`, `out of scope`,
`stateful`, `session`, `quota`, `amplif`, `attenuat`, `budget`, `spend`, `rate limit`,
`forbid`, `irrevers`, `workflow`, `separation of duty`, `chinese wall`, `composit`,
`compose` (in the authorization sense; the single hit, §7.2 p. 34, is "names would have to
be composed of parts").

**RFC 2693 — occurrences checked and found irrelevant:** `histor` (1: a TOC line);
`cumulat` (1: "accumulating tuples", §6.3.2 p. 27, deferred online tests within one
reduction); `sequence` (7: CRL sequence numbers, delta-CRL sequences, and certificate
chains — never action sequences); `trace` (2: "traced back to", and Chaum's "Untraceable
Payments" in the references); `log` (1: "for logging purposes", §3.3 p. 14, about mapping
a key to a name after the fact); `terminal` (1: Diffie–Hellman quotation, p. 5);
`prohibit` (1: privacy regulations, p. 9).

**Delegation Logic — zero occurrences:** `valid` (all forms), `revoke`, `revocation`,
`expir`, `temporal`, `history`, `cumulat`, `sequence`, `audit`, `accountab`, `trace`,
`amplif`, `attenuat`, `quota`, `aggregat`, `composit`, `compose`, `obligation`, `usage`,
`budget`, `rate limit`, `terminal`, `irrevers`, `workflow`, `separation of duty`,
`chinese wall`, `out of scope`, `beyond the scope`.

**Delegation Logic — occurrences checked:** `spend` (1: requirement (6), p. 4, discussed
above); `time` (all hits are complexity bounds or the phrase "for the first time" on p. 7);
`state` (all hits are "statement" or "policy statement"); `monoton` (Abstract p. 1, §7.3
p. 39, and §6.3 p. 37 on nonmonotonicity of dynamic-threshold delegation queries).

**Also searched and confirmed:** the complete set of formal results in DL is Lemmas 1–4
and Theorems 5–7 (`grep '^ *Theorem\|^ *Lemma\|^ *Proposition\|^ *Definition'`); all seven
concern transformation size or inferencing time.

---

# Bibliography entries

From the documents' own front matter.

**RFC 2693** — front matter gives surnames and affiliations (C. Ellison, Intel; B. Frantz,
Electric Communities; B. Lampson, Microsoft; R. Rivest, MIT Laboratory for Computer
Science; B. Thomas, Southwestern Bell; T. Ylonen, SSH), September 1999, Category:
Experimental. Full given names are from the Authors' Addresses section, pp. 41–42.

```bibtex
@techreport{Ellison1999SPKI,
  author      = {Ellison, Carl M. and Frantz, Bill and Lampson, Butler and
                 Rivest, Ron and Thomas, Brian and Ylonen, Tatu},
  title       = {{SPKI} Certificate Theory},
  type        = {Request for Comments},
  number      = {2693},
  institution = {Internet Engineering Task Force},
  series      = {RFC},
  month       = sep,
  year        = {1999},
  note        = {Category: Experimental},
  doi         = {10.17487/RFC2693}
}
```

Note on the DOI: `10.17487/RFC2693` is the RFC Editor's standard DOI pattern and is
**not printed in this 1999 text file** (DOIs postdate it). Verify before it goes into the
manuscript, or drop the field and give the RFC number alone.

**Delegation Logic** — front matter gives: NINGHUI LI, Stanford University; BENJAMIN N.
GROSOF, Massachusetts Institute of Technology; JOAN FEIGENBAUM, Yale University. Title as
above. **No journal, volume, issue, page range, or date appears anywhere in this PDF.**
The venue data below is from the task brief and must be confirmed against the ACM record
before submission.

```bibtex
@article{Li2003DelegationLogic,
  author  = {Li, Ninghui and Grosof, Benjamin N. and Feigenbaum, Joan},
  title   = {Delegation Logic: A Logic-based Approach to Distributed Authorization},
  journal = {ACM Transactions on Information and System Security},
  volume  = {6},
  number  = {1},
  pages   = {128--171},
  year    = {2003},
  doi     = {10.1145/605434.605438}
}
```

The DOI here is likewise **not in the PDF** and is unverified from any source I read.
Confirm or remove.

The PDF does record its own prior publication history, p. 1:

> "Parts of this paper were published in preliminary form in the following two papers: 'A Logic-Based Knowledge Representation for Authorization with Delegation (Extended Abstract)' in Proceedings of the 12th IEEE Computer Security Foundations Workshop, June 1999. 'A Practically Implementable and Tractable Delegation Logic' in Proceedings of the 2000 IEEE Symposium on Security and Privacy, May 2000."

and its funding, p. 40:

> "The first author is currently supported by DARPA through SPAWAR contracts N66001-00-C-8015 and by DoD MURI 'Semantics Consistency in Information Exchange' as ONR Grant N00014-97-1-0505."
