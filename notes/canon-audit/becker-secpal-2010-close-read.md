# SecPAL (Becker, Fournet & Gordon) — close read for the JCS retarget

**Source read:** `/Users/brettreynolds/projects/LLM-CLI-projects/literature/becker2010secpal.pdf`
(59 pp., MiKTeX-produced author preprint; extracted with `pdftotext -layout`, cross-checked
against raw `pdftotext` for the rule displays).

## PAGE-NUMBER WARNING — READ THIS FIRST

**Every page number below is a page of the 59-page preprint PDF, not of the published
article.** The archived file is the authors' typescript: page 1 is the title/abstract page and
page 59 is the last reference page. It carries **no journal header, no volume/issue, and no
619–665 pagination anywhere in the document.** The JCS version is 47 pages (619–665), so the
mapping is not linear and I will not guess it. Before any of these page numbers goes into the
manuscript, they must be re-checked against the published version (DOI 10.3233/JCS-2009-0364).
Quotes are stable; page numbers are not.

Quotes are verbatim from the extracted text. I have silently repaired only unambiguous
`pdftotext` artifacts: `/0` → ∅, `TPω` → T_P^ω, and subscript/superscript positioning in
`can say0` / `can say∞` / `saysD`. No words changed.

---

## 1. Précis (250 words)

SecPAL is a declarative authorization language for decentralized systems. Its object of study
is the *assertion*: `A says fact if fact1, ..., factn, c`, where A is a principal who issues and
vouches for the claim, the conditional facts are further SecPAL facts, and `c` is a constraint
drawn from an open, user-extensible constraint domain. A policy is a set of such assertions (an
"assertion context"); an access request is mapped, via a policy-authored *authorization query
table*, to a logical query built from atomic queries, conjunction, disjunction, negation,
constraints, and existential quantification. Access is granted if the query succeeds.

The design goal is a three-way balance: syntax close to English, a semantics of exactly three
deduction rules, and polynomial-time evaluation. Delegation is expressed by the verb phrase
`can say`, carrying a boolean depth flag (0 = no re-delegation, ∞ = arbitrary re-delegation);
principal aliasing and role hierarchies by `can act as`. Purely syntactic *safety conditions*
guarantee that constraints are ground when evaluated, which is what lets SecPAL admit
expressive constraint classes (paths, regular expressions, arithmetic) that prior languages
excluded for tractability.

The formal core is a translation into Datalog with Constraints, proved sound and complete
(Thm 7.4), plus a tabled resolution algorithm proved sound, complete and terminating (Thm 8.4,
8.5) with polynomial data complexity (Thm 8.6). Section 6 works twelve policy idioms. Section 9
describes a signed-XML prototype deployed in a grid project and independently evaluated on
GridFTP. Twelve appendix pages carry all proofs.

---

## 2. Twenty-five numbered claims, each with page and verbatim quote

(Unnumbered bold lead-ins inside an item are supporting detail for that item, not separate claims.)

### The assertion form and its semantics (item 1)

**1. The assertion form is `A says fact if fact1, ..., factn, c`, with the issuer named.**
p. 7: "An authorization policy is specified as a set AC of assertions (called assertion
context) of the form / A says fact if fact1 , ..., factn , c / where the facts are sentences that
state properties on principals, defined below. In the assertion, A is the issuer;
fact1 , . . . , factn are the conditional facts; and c is the constraint."

**Assertions differ from Horn clauses in exactly three respects, the first being that the
issuer vouches for the claim.**
p. 8: "Assertions are similar to Horn clauses, with the difference that (1) they are qualified
by some principal A who issues and vouches for the asserted claim; (2) facts can be nested,
using the verb phrase can say, by means of which delegation rights are specified; and (3)
variables in the assertion are constrained by c".

**2. Every fact has the shape `e verbphrase`; verb phrases are predicates, `can say^D fact`, or
`can act as e`.**
p. 8 (grammar): "verbphrase ::= pred e1 ... en for n = Arity(pred) | can say^D fact
(delegation) | can act as e (principal aliasing) / fact ::= e verbphrase". And p. 7: "Every fact
in SecPAL takes the form e verbphrase, where e is the subject of the fact, and verbphrase is the
remainder."

**The flat/nested distinction is grammatical: a fact is nested iff it contains a `can say`.**
p. 8: "We say that a fact is nested when it includes a can say, and is flat otherwise. For
example, the fact Bob can read f is flat, but Charlie can say0 Bob can read f is nested."

**3. The semantics is given directly by three deduction rules, deliberately not by translation.**
p. 11: "We now describe a formal semantics consisting of only three deduction rules that
directly reflect the intuition suggested by the syntax. This proof-theoretic approach enhances
simplicity and clarity, far more than if we had instead taken the translation to Datalog with
Constraints in Section 7 as the language specification."

**The judgment carries a delegation flag; D = 0 forbids any use of the (can say) rule
anywhere in the derivation.**
p. 11–12: "Each deduction rule consists of a set of premises and a single consequence of the
form AC , D |= A says fact where vars(fact) = ∅ and the delegation flag D is 0 or ∞." … "if
D = 0, no instance of the rule (can say) can occur in the derivation."

**The three rules, verbatim (p. 12).**

```
            (A says fact if fact1 , ..., factk , c) ∈ AC
            AC , D |= A says facti θ for all i ∈ {1..k}
                |= cθ        vars(factθ) = ∅
(cond)  ------------------------------------------------
                 AC , D |= A says factθ

            AC , ∞ |= A says B can say^D fact
                  AC , D |= B says fact
(can say) --------------------------------------
                  AC , ∞ |= A says fact

            AC , D |= A says B can act as C
            AC , D |= A says C verbphrase
(can act as) ------------------------------------
            AC , D |= A says B verbphrase
```

**4. "Says" is not a modality with an independent semantics; it is the issuer slot of an
assertion, and the deduction relation is what gives it content.** SecPAL declines to state a
formal connection to the modal literature.
p. 37: "SecPAL's delegation operators can say∞ and can act as resemble the 'controls' and
'speaks for' operators, respectively, of ABLP, but we have not established precise
connections."

### `can say`, delegation depth, non-amplification (item 2)

**5. Delegation depth is boolean, 0 or ∞, and that is claimed sufficient.**
p. 12: "In Section 6, we show that the boolean delegation flag D ∈ {0, ∞} is sufficient for
expressing a wide range of complex delegation policies, including depth-restricted delegation."
p. 26: "The verb phrase can say0 fact allows no further delegation of fact, while can say∞ fact
allows arbitrary further delegation."

**Any fixed integer depth is encoded by nesting `can say0`.**
p. 26: "SecPAL can express any fixed integer delegation depth by nesting can say0." Worked with
assertions (29) `Alice says Bob can say0 x is a friend` and (30) `Alice says Bob can say0 x can
say0 y is a friend`.

**6. Proposition 3.6 is a proved non-amplification property: a zero-depth delegation confines
the derivation to the delegate's own assertions.**
p. 13: "Proposition 3.6. Let AC_A be the set of all assertions in AC whose issuer is A. We have
AC , 0 |= A says fact iff AC_A , 0 |= A says fact." And immediately after: "Proposition 3.6
implies that if A says fact is deduced from a zero-depth delegation assertion A says B can say0
fact then the delegation chain is guaranteed to depend only on assertions issued by B."

**7. SecPAL claims this property is what XrML and Delegation Logic lack: their depth bounds are
defeatable by predicate laundering.**
p. 26: "In XrML and DL, Charlie can then re-delegate to Doris via is a friend2, thereby
circumventing the depth specification. The SecPAL semantics prevents this by threading the depth
restriction through the entire branch of the proof; this is a corollary of Proposition 3.6."

**8. Width-bounded delegation (every link in the chain must satisfy a predicate) is
expressible, and is claimed unavailable in SPKI/SDSI, DL, or XrML.**
p. 27: "If these are the only assertions by Alice that mention the predicate is a friend or is a
delegator, then any derivation of Alice says x is a friend can only depend on Bob or principals
with a matching email address. As with depth-bounded delegation, this property cannot be
enforced in SPKI/SDSI, DL or XrML."

**9. Safety conditions are purely syntactic and are the enabling device for the whole
expressiveness claim.**
p. 10, Definition 3.1: "The assertion A says fact if fact1 , ..., factn , c is safe iff the
following conditions hold: • all conditional facts are flat;" (p. 11) "• all variables in c also
occur somewhere else in the assertion; • if fact is flat, all variables in fact also occur in a
conditional fact." Rationale, p. 10: "rather than restricting constraints, SecPAL's safety
conditions (Definition 3.1) only ensure that constraints will be ground at runtime, once all
conditional facts have been satisfied."

### Queries, conflict, priority

**10. Negation is confined to queries and excluded from assertions, by design.**
p. 13: "Our solution is based on the observation that negated conditions can be effectively
separated from recursion by allowing negation only in authorization queries. Collecting
negations at the level of authorization queries also makes for clearer policies whose
consequences are easier to foresee."

**11. Conflict resolution and priority are not language primitives; they are encoded in the
query.**
p. 17: "It also illustrates how a time-dependent prohibition policy with a Deny-Override
conflict resolution rule can be written in SecPAL. More elaborate conflict resolution rules such
as assertions with different priorities can also be encoded on the level of authorization
queries."

**12. The request-to-query mapping is a table of parameterized requests, authored as part of the
policy.**
p. 16: "An authorization query table is a finite set of mappings r 7→ q from parameterized
access requests r to authorization queries q. / Upon a request, the reference monitor issues an
instantiated request lookup (instead of issuing a query directly) that gets mapped by the table
to the corresponding authorization query".

### Safety, decidability, tractability (item 3)

**13. Theorem 7.4 (soundness and completeness of the Datalog translation).**
p. 31: "Theorem 7.4 (Soundness and completeness). Let P be the Datalog translation of a safe
assertion context AC . We have A says^D fact ∈ T_P^ω(∅) iff AC , D |= A says fact."

**14. Theorem 8.4 (soundness, completeness, termination of the tabling algorithm).**
p. 34: "Theorem 8.4. (soundness, completeness, termination) Let Ans be a sound and complete
answer table, P an IN/OUT-safe program and P an IN/OUT-safe query. Then Answers_P(P, Ans) is
defined, finite and equal to {θ : Pθ ∈ T_P^ω(∅), dom(θ) ⊆ vars(P)}."

**Theorem 8.5 (finiteness, soundness, completeness of full query evaluation).**
p. 35: "Theorem 8.5 (Finiteness, soundness, and completeness of query evaluation). For all safe
assertion contexts AC and safe authorization queries q, / 1. AuthAns_AC(q) is defined and finite,
and / 2. AC , θ ` q iff θ ∈ AuthAns_AC(q)."

**15. Theorem 8.6 (polynomial data complexity), with the two parameters named.**
p. 36: "Theorem 8.6. Let M be the number of flat atomic assertions (i.e., those without
conditional facts) in a safe assertion context AC and let N be the maximum length of constants
occurring in these assertions. The time complexity of computing AuthAns_AC is polynomial in M
and N." Note the qualification on p. 36: data complexity is "a measure of the computation time
for evaluating a fixed query with fixed intensional database (IDB) but variable extensional
database (EDB)."

**16. The underlying bound is exponential in the number of variables and polynomial only in the
fact count.** Read this before describing SecPAL as simply "tractable."
p. 50, Lemma A.16: "All transition paths starting from an initial state are of finite length,
and the path lengths are polynomial in the number of facts (i.e., clauses with empty body) in
P ." Proof, p. 50: "It follows that the length of any path is bounded by 4C^(M+V) N," where M
and V are the maximum numbers of distinct variables in clause heads and bodies respectively, and
C is the number of constants.

### Proof, evidence, audit (item 5)

**17. Authorization holds if and only if a proof graph exists. SecPAL states this biconditional
in both directions, for Datalog and for SecPAL itself.**
p. 36: "A ground atom P occurs in T_P^ω(∅) if and only if there is a proof graph for P with P as
a root node." And: "Similarly, we can define a notion of proof graph for SecPAL such that there
is a derivation of AC , ∞ |= A says fact according to the three deduction rules of Section 3 if
and only if there is a SecPAL proof graph with AC , ∞ |= A says fact as a root node."

**Proof graphs are motivated as a debugging aid, not as an accountability record.**
p. 36: "When testing and troubleshooting policies, it is useful to be able to see a
justification of an authorization decision." The evaluator does not emit them by default; the
answer table merely "contains enough information to reconstruct the complete proof graph for
each answer" (p. 34).

**18. Auditing in the prototype is explicitly partial.**
p. 37: "Partial auditing of access decisions is performed according to an XML audit policy. An
audit log tool allows security administrators to view the details of past access decisions and
visualize answers to queries as SecPAL proof graphs."

### State, history, sequences (item 4)

**19. A single query evaluation is atomic with respect to system state. This is an assumption,
stated as such.**
p. 9: "The denotation of a function f(~r) is defined if ~r is ground, and is also a constant, but
may depend on the system state as well as [[~r]]. For example, [[CurrentTime()]] returns a
different constant when called at different times. However, we assume that a single
authorization query evaluation is atomic with respect to system state. That is, even though an
expression may be evaluated multiple times, we require that its denotation not vary during a
single evaluation."

**The reference monitor is defined per request.**
p. 13: "A reference monitor is a component, typically software, that given a request to access a
sensitive resource, decides whether or not to grant access. A reference monitor based on SecPAL
generates a suitable authorization query, and evaluates the query against the current assertion
context".

**20. The separation-of-duties idiom depends on a cross-request effect that SecPAL explicitly
declines to specify.** This is the single most important passage for the manuscript's claim (C).
p. 21: "If this is successful, the reference monitor adds Bank says U has initiated P to the
local assertion context." p. 22: "Note that the requirement that a successful execution of an
initPay request should add a new fact to the assertion context is not specified here. However,
SecPAL's authorization query table can be extended in such a way that requests are mapped not
just to queries, but also to a sequence of fact insertions and deletions that is executed when
the query is successful."

**21. History-dependent authorization is named, placed outside SecPAL, and declared an easy
extension with an existing semantics.**
p. 40: "Dynamic updates to the authorization environment occur in history-dependent
authorization policies such as dynamic separation of duties and RBAC-style role activation and
deactivation. Becker and Nanz [10] have shown how Datalog-based authorization languages can be
extended to support such policies and be given a semantics based on transaction logic. SecPAL
could be easily extended according to that scheme: authorization query tables would map requests
not only to queries, but also to a sequence of insertions (and retractions) of basic assertions
into (and from) the assertion context."
Reference [10], p. 54: "M. Y. Becker and S. Nanz. A logic for state-modifying authorization
policies. In 12th European Symposium on Research in Computer Security (ESORICS), pages 203–218,
2007."

**22. Revocation is a pre-evaluation filter over a snapshot, not an ongoing enforcement
mechanism, and its own dependence on message availability is conceded and deferred.**
p. 19: "Given an assertion context AC and a set of revocation assertions AC_rev where AC ∩
AC_rev = ∅, we remove all assertions revoked by AC_rev in AC before evaluating authorization
queries." And: "as with certificate revocation lists, revocation in SecPAL depends on the
availability of revocation assertions. Depending on the application, the distribution of
revocation assertions can be managed by pull or push schemes. This and other revocation-related
issues, which are orthogonal to the specification mechanisms, are beyond the scope of this
paper."

**Revocation assertions cannot themselves be revoked, and the reason given is
comprehensibility, not expressiveness.**
p. 19: "The condition that AC and AC_rev must be disjoint means that revocation assertions
cannot be revoked (at least not within the language). Allowing revocation assertions to be
revoked by each other causes the same problems and semantic ambiguities as negated body
predicates in logic programming."

### The interpretation problem (item 6)

**23. Principals *are* public keys. Identity resolution is stipulated, not modelled.**
p. 5: "We identify principals by names Alice, Cluster, FileServer, . . . ; these names stand for
public signature-verification keys in the SecPAL implementation." p. 28: "indeed, we assume here
that principals are uniquely identified by their public keys."

**Authentication and token validation happen before SecPAL is invoked.**
p. 6: "Before processing the request, the cluster authenticates Alice as the requester, validates
her tokens, and runs the query Cluster says Alice can execute dbgrep against the set of
assertions formed by its local policy plus these tokens." p. 5: "Every assertion is XML-encoded
and signed by its issuer."

**24. SecPAL has no notion of an utterance being addressed to anyone; anything said can be
picked up by anyone, and the paper concedes this as a limitation relative to DKAL.**
p. 40: "In SecPAL, if A says fact, then there is nothing to prevent B from importing this
statement using B says A can say∞ fact. Importing knowledge can be controlled more finely in
DKAL, where the says operator is parameterized by the intended target of the communication: only
if A says fact to B can it be deduced that B knows A said fact."

### Stated limitations and future work (item 7)

**25. Implementation is disclaimed as the paper's subject.**
p. 4: "Although system implementation is not the subject of this paper, SecPAL has been
implemented and deployed as the core authorization mechanism of a large system-development
project, initially targeted at grid applications [29]."

**The conclusion's future work is tooling, not theory.**
p. 41: "Future work includes tools for policy authoring, deployment, and formal analysis."
p. 40: "If authorization queries are extended by an aggregation operator (which can be easily
done without modifying the assertion semantics and without sacrificing polynomial data
complexity), SecPAL can (safely) express the entire benchmark policy described in [6] and [7],
one of the largest and most complex examples of a formal authorization policy to date."

**Prohibition is discouraged in the paper's own voice.**
p. 17: "Just as with negative conditions, prohibition makes policies less comprehensible and
should be used sparingly, if at all [32, 27]."

---

## 3. Anticipations of the manuscript's claims

### (A) A complete, internally consistent trace is compatible with the action being unauthorized

**Partial anticipation of the mechanism; no anticipation of the claim.**

Inside the model, SecPAL asserts the opposite. Soundness (Lemma A.7, p. 43; Lemma A.13, p. 48;
Theorem 7.4, p. 31) means every derivable atom really is in the least fixed point of the
assertion context, and p. 36 states the biconditional between holding and having a proof graph.
So a well-formed SecPAL derivation cannot accompany an unauthorized action *relative to the
assertion context it was evaluated against*.

The whole of (A) therefore turns on the context, and SecPAL twice puts the context beyond its
own guarantees:

- **Revocation availability.** p. 19: "revocation in SecPAL depends on the availability of
  revocation assertions… beyond the scope of this paper." The filtered context (p. 19) is only as
  good as the revocation messages that arrived. A sound, complete, internally consistent
  derivation over a stale context licenses an action the issuer had revoked. This is (A) in a
  narrow, concrete form, and it is in the text. It is not named, generalized, or drawn as a
  conclusion about what a trace establishes; it is filed under distribution engineering.
- **The query-selection gap.** The reference monitor maps a request to a query by table lookup
  (p. 16). A sound proof of the *queried* proposition says nothing about whether that was the
  right query for the action actually taken. SecPAL never raises this; the table is authored by
  the policy author and its correctness is assumed.

**Bearing on the manuscript:** (A) survives as a claim, but it must be stated *against* SecPAL's
soundness result, not in ignorance of it. A JCS reader will read (A) as an assertion that the
soundness theorem does not do the work people think it does, and will expect the manuscript to
locate the failure precisely where SecPAL itself locates the boundary of its guarantee: at the
assembly of the assertion context, not inside the deduction. Cite p. 19 explicitly.

### (B) A valid authorization can leave no trace at all

**Consistent with SecPAL, never claimed by it, and at serious risk of reading as trivial to this
readership.**

- Proof graphs are motivated for "testing and troubleshooting policies" (p. 36), a debugging
  purpose.
- Emission is optional: the answer table "contains enough information to reconstruct the
  complete proof graph for each answer" (p. 34), a capability, not an obligation. `AuthAns`
  (Figure 2, p. 35) returns substitutions, not proofs.
- The prototype does **partial** auditing by explicit design: "Partial auditing of access
  decisions is performed according to an XML audit policy" (p. 37).

Nothing in the paper asserts that authorization requires a record. Case-insensitive full-text
searches: "audit" 2 hits, both p. 37; "evidence" 0; "accountab" 0; "logging" 0; "log entry" 0;
"audit trail" 0. Every other `log`-initial token in the document is "logic", "logical",
"Datalog" or "login" — the bare noun "log" occurs once, in "audit log tool" (p. 37).

**Bearing on the manuscript, adversarially:** to a SecPAL reader, (B) is close to definitional —
a derivation is a proof object, a log is an I/O side-effect, and nobody ever claimed they
coincide. If (B) is doing real work in the manuscript it has to be doing more than "logging is
optional," and the manuscript should say what, up front. The strongest available version is not
"traces can be absent" but "the artifact that makes an authorization valid (a derivation over a
context) and the artifact an auditor later inspects (a log) have no guaranteed relation in
either direction," with (A) and (B) as the two directions. Framed that way, p. 34, p. 36 and
p. 37 together are supporting evidence rather than a precedent that scoops it.

### (C) Per-action authorization does not compose into authorization of the sequence

**No anticipation as a claim or a result. But SecPAL states the gap in its own voice, twice, and
declares the fix easy.** This is the most consequential finding in this read.

- p. 22: the separation-of-duties idiom is precisely a cumulative constraint across two requests,
  and it works only because "the reference monitor adds Bank says U has initiated P to the local
  assertion context" (p. 21) — an effect the paper says "is not specified here" (p. 22).
- p. 22 and p. 40 both propose the same extension: query tables mapping requests to "a sequence
  of fact insertions and deletions."
- p. 40: "Becker and Nanz [10] have shown how Datalog-based authorization languages can be
  extended to support such policies and be given a semantics based on transaction logic. SecPAL
  could be easily extended according to that scheme."

Case-insensitive full-text searches: "cumulat" 0 hits; "budget" 0; "obligation" 0; "mutable" 0;
"ongoing" 0; "continuous enforcement" 0 (the sole "continuous" is the topological property of
the T_P operator, p. 29); "aggregat" 2 hits, p. 13 and p. 40, both about a query-level
aggregation operator within a single evaluation, not across requests; "sequence" (excluding
"consequence") exactly 2 hits, p. 22 and p. 40, both the same deferred extension; "session" 1
hit, p. 22, in that same sentence; "histor" 2 hits, p. 18 ("Historically", about X.509 CRLs) and
p. 40 ("history-dependent authorization policies"), the latter being the relevant one.

**Bearing on the manuscript:** claim (C) is true *of SecPAL*, and SecPAL says so. What the
manuscript cannot say is that the canon overlooked sequence-level authorization. It was seen,
named ("history-dependent authorization policies"), given a semantics elsewhere, and dismissed
as an easy extension. The manuscript therefore has to engage **Becker & Nanz 2007, "A logic for
state-modifying authorization policies," ESORICS, pp. 203–218** ([10] at p. 54), and probably
UCON alongside it, and then say why "easily extended" is wrong or insufficient. Two lines of
attack are available from this text and both are defensible: the extension is a *reference
monitor* discipline, not a language guarantee, so nothing in the semantics prevents a policy
author from writing a table whose insertions fail to capture the cumulative limit; and SecPAL's
own atomicity assumption (p. 9) makes each evaluation blind to the state changes of concurrent
evaluations, which is exactly where a cumulative-limit breach lives.

### Bonus: the four-field analysis against SecPAL

- **Standing** — fully covered, and better than the manuscript's scope-inclusion story. `can say`
  with a depth flag plus Proposition 3.6 (p. 13) gives a *proved* non-amplification property, and
  the paper uses it to attack XrML and DL for lacking it (p. 26). The manuscript's
  non-amplification idea will be measured against Prop. 3.6. If the manuscript's version is scope
  inclusion rather than a history-sensitive relation (which the July referee already flagged as
  an open item), a JCS reader will see the weaker of the two.
- **Priority** — partially covered: encoded at query level, Deny-Override worked as Example 4.4
  (p. 17), and "assertions with different priorities can also be encoded on the level of
  authorization queries" (p. 17). Not a primitive, and the paper prefers it that way.
- **Licensing** — this is exactly the deduction relation `AC, D |= A says fact`.
- **Status** — **not covered, and this is where the manuscript's novelty concentrates.** But note
  a partial precedent worth acknowledging rather than being caught by: the flat/nested
  distinction (p. 8) grammatically separates asserting a fact from delegating authority over it,
  so `A says B can say0 C can read f` mentions the inner fact without asserting it. That is a
  use/mention distinction, built into the grammar. And the DKAL passage (p. 40) is a status
  problem in all but name: an utterance with no addressee can be imported by anyone. Cite both;
  the manuscript's point is that these distinctions are *stipulated by well-formed syntax* rather
  than *recovered from an ambiguous string*, which is a real difference and a defensible one.

---

## 4. Where the manuscript's claims survive

**The interpretation problem is untouched, and the evidence is unusually clean.**

Case-insensitive full-text searches returning **zero hits**: "classif", "recogni",
"misinterpret", "ambiguous input", "parse", "spoof", "forge", "impersonat", "injection". The
only occurrence of "interpret" outside a reference title (Bell & LaPadula, "Multics
interpretation", p. 55) is a graph-theoretic use on p. 34: "is interpreted to have edges
pointing to each of its child nodes". "ambigu" has 6 hits, all about *other languages'*
specifications (pp. 3–4) or about negation semantics (pp. 13, 19), never about recovering what a
string means. "natural language" has 3 hits (p. 1 abstract, p. 3, p. 40), all describing SecPAL's
own concrete syntax as resembling English — never natural language as input to be interpreted.

Everything SecPAL evaluates arrives pre-classified, by three separate stipulations:

1. **Who said it** is settled cryptographically outside the language: "these names stand for
   public signature-verification keys" (p. 5); "Every assertion is XML-encoded and signed by its
   issuer" (p. 5); "we assume here that principals are uniquely identified by their public keys"
   (p. 28).
2. **That it is an assertion at all** is settled by the wire format: signed XML objects against a
   schema (p. 37), with a typing discipline for constants, functions and variables noted and set
   aside as semantically inert (p. 7).
3. **What was requested** is settled by the query table before evaluation: the monitor "issues an
   instantiated request lookup" (p. 16) over "parameterized access requests" (p. 16), and
   authentication and token validation are completed first (p. 6).

Read together, SecPAL's contribution begins at the point where the manuscript's problem is
already solved. That is a clean, quotable boundary and it is the strongest ground the manuscript
has at this venue. It also gives the cover letter its joining move: SecPAL fixed the semantics of
decentralized authorization on the assumption of an authenticated, schema-typed channel; an
LLM agent's channel is neither, and the four-field analysis is what that assumption costs.

**Secondary survivals, both with textual support:**

- The atomicity assumption (p. 9) is stated as an assumption, and it is exactly the assumption
  a long-running agent trajectory violates.
- Revocation as pre-evaluation filtering over a snapshot (p. 19), with distribution declared out
  of scope, leaves continuous/ongoing enforcement entirely unaddressed. No hits for "continuous
  enforcement", "ongoing", "mutable attribute", "obligation".

---

## 5. The evidentiary bar this paper set in JCS

What a 2010 JCS reader saw a decentralized-authorization paper deliver:

**Formal apparatus (the bulk of it).** Three deduction rules constituting the semantics
(p. 12). Five numbered definitions fixing safety and well-formedness (3.1 assertion safety
p. 10; 4.1 query safety p. 15; 4.5 query-table safety p. 17; 8.1 IN/OUT safety p. 34; 8.3
sound/complete answer tables p. 34), plus Lemma 8.2 connecting the two safety notions (p. 34;
note the paper restates it in the appendix as "Restatement of Theorem 8.2", p. 46, an internal
numbering slip worth not reproducing). One corollary and four propositions about the deduction
relation (3.2–3.6, pp. 12–13). Four numbered
theorems in the body: 7.4 soundness+completeness of the Datalog translation (p. 31); 8.4
soundness+completeness+termination (p. 34); 8.5 finiteness+soundness+completeness of query
evaluation (p. 35); 8.6 polynomial data complexity (p. 36). A twelve-page appendix (pp. 42–53)
with seventeen further numbered lemmas/definitions/theorems and **all** proofs, including a
labelled transition system (p. 46) introduced solely because "it is easier to prove properties
for it than for the pseudocode in Figure 1" (p. 45), and an explicit complexity bound
(4C^(M+V)N, p. 50).

**Algorithm.** Full pseudocode for a tabled resolution algorithm (Figure 1, p. 31) and the
evaluation function for compound queries (Figure 2, p. 35).

**Worked coverage rather than experiments.** Section 6 (pp. 20–28) has twelve named idiom
subsections, each set against named competitors: Discretionary Access Control, Mandatory Access
Control (Bell-LaPadula), role hierarchies, parameterized attributes, separation of duties,
threshold policies and compound principals, hierarchical resources, attribute-based delegation,
constrained delegation, depth-bounded delegation, width-bounded delegation, local namespaces.
Each is accompanied by a specific claim about which prior language cannot express it (XACML and Lithium
p. 20; RT_C p. 24; SPKI/SDSI, DL, XrML pp. 26–27). This is the paper's substitute for an
evaluation section, and it is comparative, not illustrative.

**Implementation, described but disclaimed.** A signed-XML prototype with an XML schema, a
text/.NET object model, a policy-editing tool, C# query invocation, an audit-log viewer, and
translators from Kerberos, X.509 and Active Directory tokens (p. 37). Deployed in a named
Microsoft grid project [29]. Independently evaluated by a third party on GridFTP (Humphrey et
al. [40], p. 37).

**What is absent, and this matters for the manuscript.** No performance numbers, no benchmark
timings, no scalability graphs, no user study, no attacks or defences, no threat model, and no
security evaluation in the empirical sense. The paper says so: "Although system implementation
is not the subject of this paper" (p. 4). Its expressiveness claim against a real large policy
is asserted by reference to earlier work, not demonstrated here (p. 40).

**Calibration.** SecPAL's precedent supports a JCS submission that is design + semantics +
worked comparative idioms + a described artifact, with *no* experiments. It does not support one
with no formal results. The theorems are not decoration here; they are the paper's answer to its
own critique of XrML, SPKI/SDSI and XACML for having ambiguous or non-terminating semantics
(pp. 3–4). A framework paper arriving in this venue with neither theorems nor experiments is
outside the shape this precedent set, and the "meta-model at the normative and representational
layers, not a complete authorization language" disclaimer will be read against exactly this
paper, which *is* the complete authorization language. Two mitigations are visible from the text:
(i) SecPAL's own core result is a small number of clean structural propositions (3.3–3.6) about a
three-rule system, which is an achievable target for a meta-model — Prop. 3.6 in particular is a
one-line statement doing heavy work, and a manuscript proposition of that shape about
non-composition would substantially change how the paper reads here; (ii) the comparative idiom
table (§6) is a legitimate in-venue form of demonstration that costs no experiments, and the
manuscript's fixtures could be reorganized to occupy it.

---

## 6. Citation

**From the document's own front matter (p. 1), which is all it carries:**

> SecPAL: Design and Semantics of a Decentralized Authorization Language.
> Moritz Y. Becker, Cédric Fournet, Andrew D. Gordon.
> Microsoft Research, 7 JJ Thomson Avenue, Cambridge, CB3 0FB, United Kingdom.
> Keywords: authorization language, access control, policy, trust management.
> Corresponding author: Moritz Y. Becker, moritzb@microsoft.com.

**The archived PDF carries no journal name, volume, issue, year, or page range.** It is the
authors' typescript (PDF creation date 2009-01-16). The journal metadata below is *not* from this
document; it matches what is already recorded in the project's own
`notes/source-verification.md` line 165 and `notes/sources/authorization-formalization-sources-20260808.md`:

```bibtex
@article{becker2010secpal,
  author  = {Becker, Moritz Y. and Fournet, C{\'e}dric and Gordon, Andrew D.},
  title   = {{SecPAL}: Design and Semantics of a Decentralized Authorization Language},
  journal = {Journal of Computer Security},
  volume  = {18},
  number  = {4},
  pages   = {619--665},
  year    = {2010},
  doi     = {10.3233/JCS-2009-0364}
}
```

**Prior versions the paper names itself** (p. 5: "Earlier versions of this paper are published as
a technical report [8] and, abridged, in a conference proceedings [9]"):
- [8] Microsoft Research technical report, 2006 (p. 54).
- [9] IEEE Computer Security Foundations Symposium, 2007, pp. 3–15, under the shorter title
  "Design and semantics of a decentralized authorization language" (p. 54). This is the
  near-identical-title item the earlier source sweep flagged and discarded; the note is correct
  to prefer the journal version.

**One reference to acquire before drafting**, cited above as the pivot for claim (C):
Becker, M. Y. & Nanz, S. (2007). A logic for state-modifying authorization policies. *12th
European Symposium on Research in Computer Security (ESORICS)*, pp. 203–218. (SecPAL's [10],
p. 54.)
