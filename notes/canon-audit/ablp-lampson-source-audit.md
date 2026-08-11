# ABLP 1993 and Lampson et al. 1992: source-grounded audit

Prepared for a manuscript on authorization of AI-agent actions, targeting
*Journal of Computer Security*. Adversarial brief: find where the canon already
does what the manuscript treats as missing.

Read in full: both PDFs, cover to cover, via `pdftotext -layout` (per-page
extraction, so every page number below is the page the text physically sits on
in the supplied file). Nothing here comes from memory.

---

## READ THIS FIRST: two pagination warnings

**1. The ABLP file is not the ACM Digital Library typesetting, and its own
footer contradicts the citation in the task brief.**

The supplied `abadi1993calculus.pdf` is internally paginated **1--29**. Its
running footer, on every page, reads:

> "ACM Transactions on Programming Languages and Systems, Vol. 15, No. 3, September 1993." (p. 1 and every subsequent page)

The task brief gives *15(4):706--334* (the second number is presumably a typo
for 734). **The document itself says No. 3, not No. 4, and gives no page
range.** 29 pages does map cleanly onto 706--734, so the offset "journal page =
PDF page + 705" is arithmetically consistent, but **I cannot verify it from this
document, and the volume/issue in the file disagrees with the brief.** Before any
page-specific ABLP citation goes into a JCS submission, check the ACM DL
version. A wrong page cite to Jajodia is worse than none.

All ABLP citations below are given as **"p. N"** meaning **page N of the
supplied 29-page PDF**, with the conditional journal equivalent in brackets
where useful.

**2. The Lampson et al. file is a preprint-style typesetting, paginated
1--47.** Its footer on every page is "Lampson et al, Authentication in
Distributed Systems N". Journal pagination is 265--310 (46 pages), so **the
internal page numbers do not map to journal pages by any offset I can verify.**
All LABW citations below are **"p. N of the supplied 47-page PDF."** These will
need re-mapping against the ACM DL version before submission.

**3. Glyph note.** `pdftotext` renders the turnstile as `”` (LABW) or a
backtick (ABLP), and drops primes (`A´` survives in LABW; ABLP renders `A′` as
`A0` and `R′` as `R0`). In the quotes below I have restored `⊢` and `′` and
noted nothing else. Everything else is verbatim, including hyphenation artifacts
where they occur mid-word.

---

# PAPER 1: Abadi, Burrows, Lampson and Plotkin (1993)

## Précis (150 words)

ABLP builds an algebra of principals and a modal logic over it, then uses both
to explain access-control decisions in distributed systems. Principals are
users, machines, cryptographic channels, groups, roles and delegations alike.
Two operators are primitive: conjunction `∧` (co-signature) and quoting `|`
(`B|A says s` iff `B says A says s`). `A ⇒ B` ("A speaks for B") abbreviates
`A = A ∧ B`. Roles are encoded `A as R = A|R`; delegation is encoded
`B for A = (B ∧ D)|A`, where `D` is a fictional, deliberately unimplemented
delegation server. `A controls s` abbreviates `(A says s) ⊃ s` and is what an
ACL entry means. The paper then treats the decision problem: the general case is
undecidable, a restricted case is exponential-time, and a further-restricted
grammar of ACL entries admits an algorithm proved sound and complete for
binary-relation models. Sections 7 sketches intersection, subtraction and
variables as extensions.

## Numbered claims

**A1. The paper's declared scope excludes security policies and mandatory
access control.** (p. 3)
> "we do not examine particular security policies nor matters connected with manda-tory access control."

**A2. `A ⇒ B` is defined algebraically, not epistemically: it abbreviates an
equation in the semilattice of principals.** (p. 4)
> "A ⇒ B stands for A = A ∧ B and means that A is at least as powerful as B; we pronounce this "A implies B" or "A speaks for B.""

**A3. Quoting is primitive and explicitly carries no delegation content.** (p. 4)
> "B|A: the principal obtained when B speaks on behalf of A, not necessarily with a proof that A has delegated authority to B; by definition, B|A says s if B says that A says s"

**A4. `for` is quoting plus a delegation, and is the stronger relation.** (p. 4)
> "B for A: the principal obtained when B speaks on behalf of A, with appropriate delegation certificates" ... "Since for is stronger than |, we tend to use | only for encoding for and as."

**A5. An ACL entry is a trust statement about a single formula, and interactions
between ACLs are explicitly not modelled.** (p. 5)
> "So far we have discussed ACLs for logical formulas, with the view that each formula corresponds to a separate assertion or command, and that it can have a separate ACL." ... "We do not model these combinations and dependencies."

**A6. Time is out of scope: no timestamps, no lifetimes, no replay.** (p. 5)
> "The logic does not consider the problems associated with timestamps and lifetimes, either. Therefore, we do not explain how principals come to believe that messages are recent and are not replays."

**A7. The three bridge axioms connecting the principal algebra to the modal
logic.** (p. 8)
> "⊢ (A ∧ B) says s ≡ (A says s) ∧ (B says s); ⊢ (B|A) says s ≡ B says A says s; ⊢ (A ⇒ B) ⊃ ((A says s) ⊃ (B says s))."

**A8. The axiomatisation is knowingly incomplete against the Kripke semantics.**
(p. 9)
> "Although useful for our application, the axioms are not complete."

**A9. Role adoption is free (no credential required) and irreversible for the
adopting principal.** (pp. 12, 13, 11)
> "Roles can be adopted freely, and any A can speak in the role G role" (p. 12); "We assume A ⇒ (A as R) for all A." (p. 13); "adoption is not reversible, in the sense that A as R cannot, on his own, recover the full powers of A" (p. 11)

**A10. Capability-style delegation is criticised precisely because a valid chain
does not make the delegate a sensible one.** (p. 13)
> "In all cases the provider of the service never checks that B is a reasonable delegate for A."

**A11. In delegation without certificates, the service provider has a complete
record of the utterance but no evidence of delegation, and the ACL alone
decides.** (pp. 14--15)
> "When C receives the request r, he has evidence that B has said that A requests r, but not that A has delegated to B" (p. 14); "Now C consults an ACL for r. If B|A appears in this ACL, that is, if B|A is trusted on r, then C believes r--access is granted." (p. 15)

**A12. The delegation server D is fictional and deliberately never implemented.**
(p. 17)
> "It is not actually necessary for D to be implemented, just as typical roles do not correspond to real users and machines." ... "In this formal derivation it is irrelevant whether D is a real server or not. (It is perhaps even better if D is not a real server, for then it cannot be attacked.)"

**A13. `B for A` is a total operation: it denotes even when no delegation has
occurred.** (p. 18)
> "B for A is always defined, even if A has not delegated to B."

**A14. Delegation does not compose associatively; one direction fails, and it
fails because the intermediate party checked nothing about the origin.** (p. 18)
> "The other direction of the implication is not valid." ... "Intuitively, this is because C's part in (C for B) for A need not involve checking evidence that B is a delegate for A, or even that A exists."

**A15. The decision problem takes exactly one request and treats its content as
an uninterpreted symbol.** (p. 20)
> "A statement s represents what is being requested or asserted; the statement is presented explicitly by the requester, and the service provider does not need to derive it logically from other statements. The precise nature of s is ignored--it is treated as an uninterpreted proposition symbol."

**A16. The implemented decision procedure deliberately ignores interaction
between ACL entries, and the authors show this is incomplete.** (p. 21)
> "In this simplification, ACL entries are considered one by one, and their possible interactions are ignored. ACL entries written by two different users cannot lead to results that neither of them could foresee. The simplification of the problem is both convenient and sound, but in some cases it is incomplete."

with the worked counterexample on the same page:
> "if R controls s and R′ controls s and both R and R′ are roles, then (R′|R) controls s; on the other hand, the requester (R′|R) is denied access when the entries R and R′ are considered separately."

**A17. Non-membership is in general unprovable in a distributed setting, so the
decision cannot depend on facts that hold but cannot be shown.** (p. 26)
> "in general it is possible to prove only membership in groups, but not nonmembership." ... "Therefore, the access control decision cannot depend on A ⇒ G and G ⇒ G″, and hence access should be granted in this case."

## Anticipations of the manuscript's claims (ABLP)

### Anticipates (A) -- complete consistent trace, unauthorized action: YES, substantially.

- **p. 4**, the definition of `|` exists *for this purpose*. A record of the form
  "B said A said s" is well-formed, internally consistent, and by construction
  carries no delegation: "not necessarily with a proof that A has delegated
  authority to B."
- **p. 14**, the delegation-without-certificates protocol is a worked instance:
  C has a cryptographically sound, complete trace and still cannot conclude the
  action is authorized. Whether it is authorized is settled by a *separate*
  object, the ACL.
- **p. 18** is the sharpest: a syntactically well-formed nested delegation
  `(C for B) for A` can be derived where "C's part ... need not involve checking
  evidence that B is a delegate for A, or even that A exists." A complete chain,
  a nonexistent principal at the root.
- **p. 13** on capability systems is ABLP criticising exactly the failure the
  manuscript names: transferable credentials produce well-formed chains that the
  service provider cannot evaluate.

**Consequence for the manuscript:** (A) as stated, "a complete and internally
consistent trace of a machine action is compatible with that action being
unauthorized," is not new. ABLP built the `|` operator around it in 1991. What
may survive is the *action-level* reading: see below.

### Anticipates (B) -- valid authorization leaving no trace: YES, and this is the strongest overlap in either paper.

- **p. 17.** Every `for`-authorization in the entire system is half-constituted by
  a principal that produces no artifact ever, because it does not exist. "It is
  not actually necessary for D to be implemented" ... "it is irrelevant whether D
  is a real server or not." The authorization is valid; the delegation server
  contributes zero evidence.
- **p. 18.** "when A makes a statement himself, there is no need to find a
  corresponding statement by the delegation server."
- **pp. 12--13.** Role adoption requires no credential and generates none:
  "Roles can be adopted freely, and any A can speak in the role G role"; "We
  assume A ⇒ (A as R) for all A." A real, consequential narrowing of authority
  with no evidentiary artifact.
- **p. 21.** The converse gap, also present: an authorization that holds in the
  model and that the procedure will never find. `(R′|R) controls s` is true and
  access is denied.
- **p. 26.** Facts that hold but cannot be proved are systematically excluded
  from the decision: "the access control decision cannot depend on A ⇒ G and
  G ⇒ G″."

**Consequence for the manuscript:** (B) is anticipated at the level of principle.
Do not present "authorization can hold without leaving evidence" as a discovery.
ABLP's fictional `D` is the canonical example and a reviewer will name it.

### Anticipates (C) -- non-composition across a sequence: PARTIALLY, and in a way that must be distinguished carefully.

What ABLP *does* have:

- **A non-composition theorem, p. 18.** `C for (B for A) ⇒ (C for B) for A` holds
  and the converse fails. Delegation is not associative. This is a genuine
  non-composition result in the canon, but it composes *principals* (who is
  asking, through what chain of hops), not *actions*.
- **A composition-safety design decision, p. 21.** The decision procedure
  deliberately prevents independently written authorizations from combining into
  an unforeseen grant: "ACL entries written by two different users cannot lead to
  results that neither of them could foresee." They saw a composition worry, and
  answered it by refusing to reason across entries, at a stated cost in
  completeness.
- **History carried inside the principal expression, p. 11.** "adoption is not
  reversible, in the sense that A as R cannot, on his own, recover the full
  powers of A." What a principal may do at step *n* depends on roles adopted at
  steps 1..*n*−1. That history is encoded in the principal term, so the calculus
  is not wholly memoryless. But this is monotone privilege *reduction* on the
  requester, not a budget consumed by actions.
- **An explicit disclaimer of the nearest thing, p. 5.** "the ACLs that pertain
  to reading and writing a file might be related, and an ACL that controls
  modifications to another ACL might also control modifications to itself. We do
  not model these combinations and dependencies."

What ABLP does **not** have (evidenced negative, searches stated below):

No occurrence anywhere in the 29 pages of: *revocation*, *revoke*, *history*,
*cumulative*, *accumulate*, *aggregate*, *audit*, *information flow*, *quota*,
*budget*, *threshold*, *transaction*, *workflow*, *invariant*, *terminal state*,
*trace*. Searches run (case-insensitive, over per-page extracted text):
`revok`, `revoc`, `history`, `cumulat`, `aggregat`, `audit`, `information flow`,
`quota`, `budget`, `threshold`, `accumul`, `transaction`, `batch`, `workflow`,
`successive`, `series`, `over time`, `multiple requests`, `per request`,
`each request`, `invariant`, `safety property`, `trace`, `nonmonotonic`,
`already granted`. Only hits: `quota` inside the word "quotation" (p. 8),
`transaction` inside the journal footer, `combin`/`interact`/`depend` in the
senses quoted at A5 and A16.

## Where the manuscript's claims survive (ABLP)

1. **The action dimension is entirely absent.** ABLP's judgment form is
   `P controls s` for a single, uninterpreted `s` (p. 20). Because "the precise
   nature of s is ignored," the calculus is structurally incapable of expressing
   a constraint whose satisfaction depends on the *content* of `s` or on
   previously granted `s`s. The manuscript's (C) is safe here, provided it is
   stated as a claim about *action* composition and not *principal* composition,
   and provided the p. 18 associativity failure is cited so the reviewer sees you
   know the difference.

2. **No temporal or state dimension.** p. 5 is a flat disclaimer: no timestamps,
   no lifetimes, no recency. A cumulative limit needs a notion of "so far," and
   the logic has none.

3. **No aggregation or disclosure reasoning.** Mandatory access control is
   scoped out at p. 3. See the far more serious version of this warning under
   LABW below.

4. **The (A)/(B) pair is not *thematised*.** ABLP exhibit both gaps at many
   points but never pose the question the manuscript poses: they never ask what
   the relation is between an authorization holding and its being recorded, nor
   treat the divergence as a property to be managed. The gaps are consequences of
   the design, not objects of study. That is a thin but real opening, and it is
   the only honest way to keep (A) and (B) as contributions: not "nobody noticed
   this," but "the canon exhibits this without naming it, and an agent setting
   makes it load-bearing."

## Correct citation, from the document's own front matter

Byline (p. 1): MARTÍN ABADI, MICHAEL BURROWS, and BUTLER LAMPSON (Digital
Equipment Corporation) and GORDON PLOTKIN (University of Edinburgh).
Provenance note (p. 1): "This is an extended version of a paper presented at the
Crypto '91 conference, August 1991."
Dates (p. 29): "Received August 1991; revised September 1992; accepted November
1992."
Running footer: "ACM Transactions on Programming Languages and Systems, Vol. 15,
No. 3, September 1993."

```bibtex
@article{abadi1993calculus,
  author  = {Abadi, Mart{\'i}n and Burrows, Michael and Lampson, Butler and Plotkin, Gordon},
  title   = {A Calculus for Access Control in Distributed Systems},
  journal = {ACM Transactions on Programming Languages and Systems},
  year    = {1993},
  volume  = {15},
  number  = {4},
  pages   = {706--734},
  month   = sep,
  doi     = {10.1145/155183.155225}
}
```

**Flagged, not verified:** number, pages and DOI are NOT in the supplied
document. The document's own footer says **No. 3**. I have written `number = {4}`
and `706--734` because that is what the task brief supplied and it is
arithmetically consistent with a 29-page article, but **this must be confirmed
against the ACM DL record before submission.** The DOI above is likewise not in
the document and is unverified; delete it or check it.

---

# PAPER 2: Lampson, Abadi, Burrows and Wobber (1992)

## Précis (150 words)

LABW present the same theory in a systems register, plus a running
implementation. The core is the "speaks for" relation `A ⇒ B`, defined by
`(A ⇒ B) ≡ (A = A ∧ B)` (P7), together with `∧`, quoting `|`, and the handoff
axiom `(A says (B ⇒ A)) ⊃ (B ⇒ A)` (P10), from which the handoff rule (P11) and
a joint-authority rule (P12) follow. Roles are `A as R = A|R` (R1) with `A ⇒ A as
R` (R2); delegation is `B for A = B|A ∧ D|A` (D5) with `A ⇒ D|A` (D6). The paper
then works through channels and encryption, certification authorities and path
names, groups, secure program loading and booting, delegation and login,
authenticated interprocess communication with a per-node authentication agent,
and finally an access-checking algorithm over a restricted ACL grammar. Section
9.1 observes that the theory yields a formal proof per decision, which can be
written to an audit trail. An appendix lists every axiom.

## Numbered claims

**L1. The reference monitor is per-request by construction.** (p. 2)
> "A reference monitor: a guard for each object that examines each request for the object and decides whether to grant it."

**L2. Information flow, and therefore nondisclosure, is explicitly out of
scope.** (p. 2, footnote 1)
> "The access control model is less useful for availability, which is not considered in this paper. Information flow [8] is an alternative model which is also not considered, so we have nothing to say about mandatory security policies that can enforce nondisclosure of secrets."

(Reference [8] is Denning, "A lattice model of secure information flow," CACM
19(5), 1976; see p. 46.)

**L3. Informal definition of "speaks for."** (p. 5)
> "A speaks for B if the fact that principal A says something means we can believe that principal B says the same thing."

**L4. Fail-secure: the system may withhold access it should have granted.** (p. 6)
> "the system should be 'fail-secure': if an untrusted component fails, the system may deny access it should have granted, but it won't grant access it should have denied."

**L5. Secrecy and timeliness are absent from the theory.** (p. 7)
> "secrecy and timeliness are fundamental there; neither appears in our theory."

**L6. `A says s` does not entail that A uttered s, or was even present.** (p. 8)
> "The intuitive meaning of ⊢ A says s is not quite that A has uttered the statement s, since in fact A may not be present and may never have seen s. Rather it means that we can proceed as though A has uttered s."

**L7. Quoting records an attribution that may be false.** (p. 8)
> "A | B says something if A quotes B as saying it. This does not mean B actually said it: A could be mistaken or lying."

**L8. The formal definition of speaks-for and its consequence.** (p. 8)
> "⊢ (A ⇒ B) ≡ (A = A ∧ B)" (P7); "⊢ (A ⇒ B) ⊃ ( (A says s) ⊃ (B says s) )" (P8)

**L9. The handoff axiom, and the authors' own warning that it is too strong.**
(p. 9, and footnote 5)
> "⊢ ( A says (B ⇒ A) ) ⊃ (B ⇒ A)" (P10); "In other words, A has the right to allow any other principal B to speak for it."
> footnote 5: "it is preferable to assume only some instances of (P10)--the general axiom is too powerful, for example when A represents a group."

**L10. Joint authority (P12) is the basis of revocation and of ending a login
session.** (p. 9)
> "⊢ ( (A′ ∧ B ⇒ A) ∧ (B ⇒ A′) ) ⊃ (B ⇒ A)" (P12); "(P12) is the basis for revoking authentication certificates (Section 5) and ending a login session (Section 7)."

**L11. Lifetimes exist, but outside the formalism.** (p. 10)
> "Each premise has a lifetime, and the lifetime of the conclusion, and therefore of the credentials, is the lifetime of the shortest-lived premise. We could add lifetimes to our formalism ... but here we content ourselves with an informal treatment."

**L12. Revocation is achieved by short lifetimes plus a countersigning online
agent; the revocation TCB is named.** (p. 20)
> "the TCB for granting access is just CA, because O acting on its own can't do anything, but CA speaks for A; the TCB for revocation is CA and O, since either one can prevent access from being revoked."

**L13. Group non-membership is unprovable by construction.** (p. 26)
> "This representation makes it impossible to prove that P is not a member of G."

**L14. Role axioms.** (p. 27; repeated in the appendix, p. 45)
> "⊢ A as R = A | R for all R ∈ Roles" (R1); "⊢ A ⇒ A as R for all R ∈ Roles" (R2); "⊢ as is commutative and idempotent on roles" (R3)

**L15. Role assumption by a person is outside the formalism.** (p. 27)
> "If the principal is a person, it can just decide to do so; in this case we can't give any formal rule for when the principal should be willing to assume the role."

**L16. Secure program loading deliberately keeps no record.** (p. 29)
> "There's no need for A to record the credentials, since no one else needs to see them; if you trust A to run P, you have to trust A not to lie to you when it says it is running P."

**L17. Delegation axioms and the two-sided protocol; both parties must
consent.** (p. 31)
> "⊢ A ∧ B|A ⇒ B for A." (D1); "A says B|A ⇒ B for A." (1); "B|A says B|A ⇒ B for A." (2); "To put it another way, for equals delegation (1) plus quoting (2). We need this explicit action by B because when B for A says something, the intended meaning is that both A and B contribute, and hence both must consent."

**L18. The delegation server D is defined so as never to be built.** (p. 31,
footnote 24)
> "⊢ B for A = B|A ∧ D|A" (D5); "⊢ A ⇒ D|A" (D6); "We don't want to implement D; if we did, it might be compromised. So A has to be able to do D's job; in other words, A ⇒ D|A."

**L19. Delegations are revoked by expiry and must be continuously refreshed.**
(p. 31)
> "We use timeouts to revoke delegations. A gives (1) a fairly short lifetime, say 30 minutes, and B must ask A to refresh it whenever it's about to expire."

**L20. Long-running delegated computation is an admitted open problem.** (p. 32)
> "We would still like some control over the duration of the delegated authority, and some way to revoke it on demand. ... We have not worked out the details of this scheme; it is a tricky exercise in balancing the demands of convenience, availability, and security."

**L21. The access-check algorithm is a proof search over one requester against
one ACL, restricted to make it complete and fast.** (pp. 41--42)
> "the reference monitor needs an algorithm that will generate a proof of A ⇒ B (then it grants access), or determine that no such proof exists (then it denies access)." (p. 41); "Now there is an efficient algorithm to test A ⇒ B:" (p. 42)

**L22. Denial is skeptical about positive premises and credulous about negative
ones.** (p. 43)
> "Certificates are stored insecurely, so we can't securely determine that a principal is not in a group because we can't count on finding the membership certificate if it is in the group." ... "it views positive premises like A ⇒ B skeptically, negative ones like "deny Jim access" trustingly."

**L23. Every decision yields a proof, and the proof is the audit record.** (p. 43)
> "Our theory yields a formal proof for every access control decision. ... The proof can be written into the audit trail, and it gives a complete account of what access was granted and why. The theory thus provides a formal basis for auditing."

## Anticipations of the manuscript's claims (LABW)

### Anticipates (A): YES.

- **p. 8, (P2) gloss.** "This does not mean B actually said it: A could be
  mistaken or lying." A well-formed, complete record of `A|B says s` is by
  explicit design compatible with B having authorized nothing.
- **p. 43.** The system's response to the gap is a policy stance, not a proof:
  "it views positive premises like A ⇒ B skeptically, negative ones like 'deny
  Jim access' trustingly." That is an acknowledgement that provable and
  entitled diverge, resolved by choosing which way to err.
- **p. 6, fail-secure.** The chosen error direction is stated as a design
  invariant.

### Anticipates (B): YES, and p. 8 is the passage the manuscript most needs to reckon with.

- **p. 8.** "in fact A may not be present and may never have seen s. Rather it
  means that we can proceed as though A has uttered s." This is (B) in one
  sentence, from 1992, in the abstract of the theory rather than in a corner
  case. Authorization-bearing attributions hold of principals who left no trace
  of any kind.
- **Axiom (S4), pp. 7 and 44.** "If ⊢ s then ⊢ A says s for every principal A."
  Every principal says every theorem, having done nothing.
- **p. 31, footnote 24.** "We don't want to implement D; if we did, it might be
  compromised." The delegation server that constitutes half of every `for` is
  chosen to be untraceable because being traceable would make it attackable.
  This is not an oversight: it is an argued security benefit of leaving no trace.
- **p. 29.** Secure loading deliberately discards the evidence: "There's no need
  for A to record the credentials, since no one else needs to see them."
- **p. 27, (R2).** `A ⇒ A as R` licenses free role adoption with no artifact.
- **The converse gap, pp. 6, 26, 43.** Valid entitlements that cannot be shown:
  non-membership is unprovable (p. 26), missing certificates cause denial
  (p. 43), and the system is designed to "deny access it should have granted"
  (p. 6).

### Anticipates (C): PARTIALLY, and one clause of (C) is in serious trouble.

**The clause "jointly disclose a protected value" is directly and explicitly
scoped out, with the right literature named.** p. 2, footnote 1: "Information
flow [8] is an alternative model which is also not considered, so we have
nothing to say about mandatory security policies that can enforce nondisclosure
of secrets." Reference [8] is Denning 1976. Lampson et al. knew that the
aggregate-disclosure problem exists, knew which framework addresses it, and
declared it out of scope. **A JCS reviewer, and Jajodia in particular given his
work on inference and aggregation in multilevel databases, will read a claim of
novelty on joint disclosure as a failure to know the field.** Treat this clause
as a positioning liability, not an asset. The honest move is to cite the
exclusion, cite the information-flow and inference/aggregation line it points
at, and then say what an agent setting adds that those frameworks do not cover.

Other partial anticipations:

- **Ongoing rather than one-shot authorization.** p. 31: delegations carry
  30-minute lifetimes and must be refreshed. p. 32 (login): the workstation
  forgets the login session key at logout so it "can no longer act for the user
  after the 30-minute lifetime of the delegation has expired." Authority is
  maintained across a session, not granted once. That is a temporal dimension,
  though not a cumulative one.
- **An implementation that does hold state.** Table IV, "The State of an Agent"
  (p. 39), and the `Self / Discard / And / As / Handoff / Claim / For / Accept`
  interface (Table V, p. 39). The agent tracks which processes may speak for
  which authorities, and a process can relinquish one via `Discard(a)`. This is
  state about *who currently holds what standing*, not about *what has already
  been done*.
- **Order matters within a delegation chain.** p. 42: "Our theory of
  authentication is compatible with other theories of access control, for
  example, one in which the order of delegation hops (operands of for) is less
  important." Their own theory is order-sensitive along the delegation
  dimension.
- **An admitted open problem in the right neighbourhood.** p. 32: long-running
  computations that outlive the user's session, needing duration control and
  on-demand revocation, "We have not worked out the details of this scheme."
  This is the closest either paper comes to the manuscript's setting, and it is
  offered as unfinished.

**Evidenced negative for the rest of (C).** Searches over the per-page extracted
text of all 47 pages, case-insensitive: `cumulat` (0 hits), `aggregat` (0),
`history` (0), `quota` (0), `budget` (0), `threshold` (0), `accumul` (0),
`transaction` (0), `workflow` (0), `invariant` (0), `terminal state` (0),
`multiple requests` (0), `per request` (0), `series` (0), `over time` (0),
`nonmonotonic` (0), `already granted` (0). `batch` returns exactly one hit, the
open problem at p. 32. `trace` returns exactly one hit, "retrace its steps" in a
name-lookup discussion (p. 22), unrelated. `audit` returns four hits, all in
§9.1 (p. 43).

## Where the manuscript's claims survive (LABW)

1. **Auditing is defined as recording the authorization proof, not the action.**
   p. 43: "Our theory yields a formal proof for every access control decision. ...
   The proof can be written into the audit trail, and it gives a complete
   account of what access was granted and why." The audit trail is a log of
   *decisions and their justifications*, per decision. There is no notion of a
   trace of what the granted operations then did, no reconciliation of
   authorization records against effects, and nothing that would let an auditor
   discover that a sequence of individually justified grants produced a
   disallowed outcome. This is the single best point of purchase for the
   manuscript: LABW claim their theory "provides a formal basis for auditing,"
   and the basis they provide is exactly the per-decision one the manuscript
   argues is insufficient. Quote them and show the gap.

2. **The decision problem is `A ⇒ B` and nothing else.** p. 41: the monitor must
   "generate a proof of A ⇒ B ... or determine that no such proof exists." The
   entire question is whether the requester's principal expression implies an
   ACL entry. The operation and the object are inputs to `CheckAccess`
   (p. 39, Table V) but no part of the logic reasons about them. Nothing in the
   formalism can express a constraint over a set of operations.

3. **No formal account of time.** p. 10 offers `s until t` as an explicit
   might-have-done and declines it: "here we content ourselves with an informal
   treatment." Lifetimes live in the implementation, not the logic. A cumulative
   constraint needs a formal "so far," and there is none.

4. **The one adjacent open problem is left open.** p. 32 concedes that
   long-running delegated computation needs duration control and on-demand
   revocation and that they have not solved it. That is a citable invitation.

5. **The gaps are never thematised, here either.** LABW exhibit (A) and (B)
   repeatedly, and never treat the divergence between holding and being
   recorded as an object of theory. The manuscript's contribution has to be
   pitched at that level, and the framing has to be "this is latent in the
   canon and becomes load-bearing under agentic delegation," not "this has been
   overlooked."

## Correct citation, from the documents' front matter

The supplied LABW PDF's own front matter gives title, byline, the ACM copyright
line "© 1992 ACM 0734--2071/92/1100-0000 $01.50", and the note that "A
preliminary version of this paper appeared in the Proceedings of the Thirteenth
ACM Symposium on Operating Systems Principles." **It gives no volume, issue or
page range.**

However, the volume/issue/pages *are* source-grounded: ABLP's own reference list
(p. 28, item 17) reads:

> "Lampson, B., Abadi, M., Burrows, M., and Wobber, E. Authentication in distributed systems: theory and practice. ACM Trans. Comput. Syst. 10, 4 (November 1992), 265--310."

```bibtex
@article{lampson1992authentication,
  author  = {Lampson, Butler and Abadi, Mart{\'i}n and Burrows, Michael and Wobber, Edward},
  title   = {Authentication in Distributed Systems: Theory and Practice},
  journal = {ACM Transactions on Computer Systems},
  year    = {1992},
  volume  = {10},
  number  = {4},
  pages   = {265--310},
  month   = nov
}
```

Volume, issue, month and pages here are grounded in ABLP p. 28 ref. 17, not in
the LABW file itself. No DOI appears in either document; do not invent one.

---

# Cross-cutting assessment

**Ranked by risk to the manuscript:**

1. **Highest risk: the joint-disclosure clause of (C).** LABW p. 2 n.1 names
   information flow and Denning 1976 and scopes them out; ABLP p. 3 scopes out
   mandatory access control. The problem is known, the tool is named, and the
   exclusion is deliberate. Any hint of novelty here is a desk-level error at
   JCS.

2. **High risk: (B) presented as new.** LABW p. 8 ("A may not be present and may
   never have seen s") and the fictional delegation server (ABLP p. 17, LABW
   p. 31 n.24) are canonical, prominently placed, and exactly on point.

3. **Moderate risk: (A) presented as new.** The `|` operator was introduced to
   mark this distinction (ABLP p. 4, LABW p. 8). ABLP p. 18 supplies a
   well-formed chain whose root principal may not exist.

4. **Moderate risk: (C) confused with delegation non-associativity.** ABLP p. 18
   already proves that delegation does not compose. If the manuscript says
   "authorization does not compose" without distinguishing the action dimension
   from the principal dimension, a reviewer will say it was done in 1993.

**Where the manuscript is genuinely clear:**

- The action dimension. `s` is uninterpreted (ABLP p. 20); the judgment is
  `A ⇒ B` (LABW p. 41). Neither calculus can state a constraint over a set of
  operations, and neither tries.
- Cumulative limits and prohibited terminal states. Zero vocabulary in either
  paper, per the searches listed above.
- Auditing as reconciliation. LABW p. 43 defines the audit trail as the
  justification per decision. That is the strongest quotable target.
- Long-running agentic computation. LABW p. 32 leaves it open in their own
  words.

**One suggested framing.** ABLP and LABW compose authorization along the
*principal* axis: who is asking, through which delegations, in which roles, over
what chain of hops. They are rich there and they know where that composition
breaks (ABLP p. 18, p. 21). They do not compose along the *action* axis at all,
and both say so in their scoping paragraphs. The manuscript's contribution is
best positioned as supplying the second axis, with the canon's own non-
composition results on the first axis cited as precedent for the shape of the
problem rather than as objections to it.

---

## Method note

- Full text of both PDFs read via `pdftotext -layout`, once flat and once page
  by page (`-f N -l N`) so that every page attribution is mechanically derived
  rather than estimated.
- Working files, retained: `/tmp/claude-agent-output/abadi1993.txt`,
  `/tmp/claude-agent-output/lampson1992.txt`,
  `/tmp/claude-agent-output/ABLP_paged.txt`,
  `/tmp/claude-agent-output/LABW_paged.txt`, and the lookup helper
  `/tmp/claude-agent-output/pg.py`.
- No web sources consulted. No claim above is from memory.
- Items I could not verify and have flagged rather than filled in: ABLP's
  journal issue number, page range and DOI; the mapping from either PDF's
  internal pagination to journal pagination.
