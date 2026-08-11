# Prior-art audit: does anything the manuscript already cites supply authorization semantics for the interpretation step?

Date: 2026-08-08. Scope: the ten works cited in `sections-delegation/02-existing-work.tex`, plus two uncited
works that turned up as higher-risk than anything in the assigned set.

**Headline.** No work in the assigned set occupies the ground. But the claim as currently worded is
refuted on its *necessity* half by two works, one of which the manuscript does not cite. The
contribution survives, and needs a specific narrowing, given in the last section.

---

## Method and a correction worth recording

Local full text existed for all ten (`lit resolve <key>` resolved nine to `literature/<key>.md`;
`kuehlewind2026audit.txt` sits in the same folder and `lit` misses it because it has no bib-key sidecar).

**A false-negative trap I hit and fixed.** `literature/zverev2025separate.md` and
`literature/he2026attriguard.md` are classified by `file(1)` as `data`, not text. Plain `grep` therefore
suppresses all output on them and exits 1, which reads exactly like "no hits". My first battery over
those two returned clean zeroes that were entirely artefactual. **Every search reported below on those
two files was re-run with `grep -a`.** Any future search over `literature/` should use `-a` by default;
I did not audit how many other files in that folder are binary-detected.

---

## Per-source verdicts

### 1. `south2025authenticated` — Authenticated Delegation and Authorized AI Agents (arXiv 2501.09674) — **ADJACENT**

The flagged highest risk. It is not one, and the reason is precise.

**Q1 (authorization semantics?) No, by design: it borrows.** Its own summary of the contribution is
"demonstrating how established internet-scale authentication (e.g., OpenID Connect and W3C VCs) and
access management protocols (e.g., XACML) can be adapted to address the unique challenges of AI agent
delegation" (§6, l.233). The authorization semantics are XACML's and OAuth's. The paper contributes
token structures (user ID-token, Agent-ID token, Delegation Token), not conditions under which an
operation counts as authorized.

**The natural-language-to-permission mechanism, read properly.** §4.4 (l.175–179):

> 1. A user writes: "Allow the agent to read and write to the directories about `projectAlpha`, but do
> not grant it access to the folders with financial folders;" 2. The LLM translates this requirement
> into a policy definition, either in a universal permission language (e.g., XACML) or in the specific
> permission language used by the resource... 3. The user reviews, corrects if necessary, and finalizes
> the policy.

This is **offline policy authoring from a trusted delegator's own utterance**, reviewed and approved by a
human before it ever governs anything. It is not classification of a string occurrence arriving at
runtime in the agent's input stream. The input's status ("this is my policy") and its source's standing
("I am the delegator") are both given by the workflow, not determined by the system. The manuscript's
step is upstream of everything South does.

South is explicit that the NL layer must not bear weight. §4.4: "We argue that the most broadly
applicable strategy is to enforce resource scoping with structured permissions. The brittleness of
natural language mechanisms makes them unsuitable for production-level usage of AI agents." §4.3: "while
natural language instructions can serve as a convenient mechanism..., they are not reliable enough to be
used as standalone policy mechanisms."

**Q2 (recognition failure in both directions?) No, and it says so is future work.** Two near-misses:

- §4.2, on dynamic authentication flows: "determining when a request requires explicit authorization can
  be non-trivial, and misclassifications can lead to either excessive prompting or critical operations
  slipping through unnoticed." Two-directional, but the classification is *risk level of a request*, not
  the role of a string occurrence or the standing of its source.
- §5.2, "New threat vectors for LLM attacks": "Prompt injection and jailbreak attacks can coerce a large
  language model into generating or accepting policies that exceed the original user's intent... While
  separating resource or task-scoping instructions from normal chat sessions or interactions reduces the
  likelihood of an attack, it still presents a new differentiated attack surface that needs to be
  guarded." This is South naming the manuscript's problem inside his own pipeline and leaving it open.
  §4.4 closes: "the evaluation of robustness of LLM translation into structured languages, we leave these
  specifics to future work."

**Q3 (bibliography).** Searched the full reference list for
`Lampson|Abadi|Burrows|Wobber|SPKI|SDSI|Ellison|Rivest|Delegation Logic|Grosof|Ninghui Li|SecPAL|Becker|UCON|Sandhu|Park, J|Jajodia|XACML|RBAC|Bertino|Ferraiolo|speaks.?for|calculus for access`.
Hits: XACML (OASIS, ref 59), ODRL (W3C, ref 83), OBAC (Brewster et al., ref 16), ROWLBAC (Finin, Joshi,
Kagal, Niu, **Sandhu**, Winsborough, Thuraisingham, ref 31), MultiOrBAC (Abou El Kalam & Deswarte, ref 2),
KaOS. No ABLP/Lampson, no SPKI/SDSI, no Delegation Logic, no SecPAL, no UCON. The only Sandhu is ROWLBAC
(RBAC in OWL), not UCON. So South joins to **policy-language syntax**, never to the delegation-logic
lineage that has the "who may say what on whose behalf" semantics.

---

### 2. `mellafezuvic2026scopegate` — Capability Gates Are Not Authorization (arXiv 2606.28679) — **ADJACENT**

**Q1: it does supply a decision procedure, and deliberately keeps language out of it.** Algorithm 1
(`SCOPEGATE.DECIDE`) is a five-stage PDP/PEP: scope → argument allowlist → money ceiling → idempotency →
default deny, with `catch any error: return DENY`. That is a thin authorization semantics over tool calls.

But its founding move is the opposite of the manuscript's: **it refuses to let any interpretation of
language bear on authorization at all.** §V: "It receives a proposed tool, args, and trusted context; it
returns ALLOW or DENY. **No LLM participates in the decision.**" §II.C: "The policy used by SCOPEGATE is
not model output... loaded from a root of trust outside the model's context window, write path, and
influence... A design in which the LLM emits, expands, or discovers its own per-call scope would be
circular: the same injection that corrupts the call could corrupt the scope."

**Q2: no.** There is no independently-correct-vs-assigned classification anywhere. Policy membership is a
set-lookup against an operator-authored verified set. The principal is not derived from anything the
model read; it arrives in the session context Γ.

**This makes ScopeGate a seventh member of the audited canon, not a counterexample.** Its own framing of
per-call authorization — "whether this concrete call, with these argument values, **in this principal and
session context**, is allowed" (§I) — presupposes the principal exactly as ABLP/SPKI/SecPAL do.

**Q3.** Searched for the full tradition list. References are Saltzer & Schroeder 1975, Hardy 1988
(confused deputy), OWASP LLM Top 10, MITRE ATLAS, Greshake, AgentDojo, InjecAgent, ToolEmu, WASP,
MiniScope. No ABLP, SPKI, Delegation Logic, SecPAL, UCON, or XACML.

---

### 3. `he2026attriguard` — AttriGuard (arXiv 2603.10749) — **ADJACENT** (the closest of the assigned set on Q2)

**Q1: no. Causal attribution, not authorization.** Definition 1: "Action-level causal attribution assigns
c to one of two categories. We say c is **intent-supported** if it is justified by the user task Tu given
the execution history up to step t. We say c is **observation-driven** if producing c requires causal
influence from the untrusted observation stream O₁:ₜ₋₁ beyond what is warranted by Tu. Equivalently, the
paradigm defines an attribution mapping g(Hₜ,c) ∈ {intent-supported, observation-driven}."

That is a two-valued classification, but of a *tool call*, and the criterion is counterfactual survival
under control-attenuated observations (Defs 2–3: control effect as log-probability shift; control potency
as KL divergence). Nothing says under what conditions an operation is authorized.

**Q2: it identifies the standing question by name and declares it out of scope.** This is the most useful
finding for the manuscript. Threat model, "Explicit Non-goals":

> **Pure Explicit Delegation to Untrusted Content.** Scenarios in which the user explicitly *authorizes*
> attacker-modifiable content to fully determine a specific action or critical argument... We classify a
> case as a non-goal only when the observation itself is *authorized* to fully determine the specific
> action or critical argument.

And in the limitations (§ near l.370): "As the user increasingly authorizes external observations to
determine actions or critical arguments..., those observations need to exert less additional control
effect to drive the malicious action, making it more likely to be attributed as intent-supported...
**the issue is not incorrect attribution, but that causal attribution alone cannot verify the authenticity
or integrity of the heavily delegated content.**"

So the leading causal-attribution defence: (a) grants that untrusted content can be authorized to
determine an action; (b) has no way to tell an authorized from an unauthorized instance; (c) carves the
case out. That is the manuscript's gap, stated by a defender.

Incidental and useful: AttriGuard's attenuation operators are explicitly speech-act theoretic. Perspective
Rewriting T₃ₚ "rewrites both explicit and implicit second-person constructions into third-person
declaratives while preserving propositional content, which reduces the directive force of the text and
weakens these perlocutionary effects [4]" — ref [4] is **J. L. Austin, *How to do things with words***. A
frontier IPI defence is already doing crude illocutionary-force stripping and citing Austin for it. That
is a live hook for the adversarial-pragmatics paper.

**Q3.** No hits for any of ABLP/SPKI/SecPAL/UCON/XACML/Sandhu/Grosof/Ellison (`grep -a`). It cites CaMeL,
IPIGuard, SecAlign, ETDI, and the confused-deputy framing via Greshake.

---

### 4. `zverev2025separate` — Can LLMs Separate Instructions From Data? (ICLR 2025) — **ADJACENT**

**Q1: no, and the word does not appear.** `grep -a -c -i "authoriz"` → **0**. `"access control"` → 0.
`"capabilit"` → 0. `"semantics"` → 0. This is a measurement paper end to end.

**Q2: two-directional at the behavioural level, but the ground truth is stipulated by channel.**
Definitions 1–4 give a separation score comparing `g(s, x+d)` (probe in the data argument) with
`g(s+x, d)` (probe in the instruction argument), and pair it with a utility score, so failure to execute
a legitimate instruction and execution of a data-borne one are both scored. But what makes a probe
"meant to be executed" is *which argument slot the harness put it in*. l.77: "out of all cases in which
the model outputs the witness when the probe is **meant to be executed**, how often does it also do so
when the probe is **meant to be processed** instead."

There is no notion of a string that sits in the data slot and genuinely does carry authority, nor of a
string in the instruction slot that is merely mentioned. The correct classification is defined to be the
channel. That is precisely the assumption the manuscript attacks, and Zverev et al. formalize it rather
than question it.

**Q3.** No tradition citations. Nearest neighbours are OS/SQL-injection analogies and ConfusedPilot
(RoyChowdhury et al. 2024).

---

### 5. `wallace2024instruction` — The Instruction Hierarchy (arXiv 2404.13208) — **CLEAR**

**Q1: no.** `grep -a -c -i "authoriz"` → 1 (a passing use). `"access control"` → 0. No decision
procedure; the contribution is synthetic data generation plus SFT/RLHF and eval results.

**Q2: partly, but on the wrong axis.** Privilege is fixed by message channel — System > User > Model
Output > Tool Output (§2, l.41) — and is never in question. What varies is whether a lower-privileged
instruction is "aligned" or "misaligned" *in content* with the higher-privileged one (§3.1): aligned
instructions "have the same constraints, rules, or goals as higher-level instructions." That is content
consistency, not source standing. Over-refusal is acknowledged as the other error direction (§1: "we do
observe some regressions in 'over-refusals'"), so both directions exist behaviourally, but for
instruction-following, not for status or standing.

**Q3.** No tradition citations. The access-control analogy is to OS kernel mode (Corbató & Vyssotsky 1965;
Ritchie & Thompson 1974) and SQL injection (Su & Wassermann 2006), i.e. gestural, not formal.

---

### 6. `greshake2023not` — Indirect prompt injection (arXiv 2302.12173) — **CLEAR**

`grep -a -c -i`: `authoriz` → 1 (one passing mention of privilege escalation, l.111); `access control` → 0;
`semantics` → 0; `quotation|quoted` → 0; `Lampson|Abadi|SPKI|SDSI|SecPAL|UCON|XACML|Sandhu|Grosof|Ellison` → 0.
The four `standing` hits are all inside "understanding" / "outstanding". The taxonomy is
injection-method × threat (passive / active / user-driven / hidden × information gathering, fraud,
intrusion, malware, manipulated content, availability). Attack demonstration and threat taxonomy only.

---

### 7. `debenedetti2024agentdojo` — AgentDojo (arXiv 2406.13352) — **CLEAR**

`grep -a -c -i "authoriz"` → 0. Its security notion is purely outcome-based: "Utility Under Attack: the
fraction of security cases... where the agent solves the user task correctly, without any adversarial
side effects" and "Targeted Attack Success Rate (ASR): the fraction of security cases where the
attacker's goal is met." Ω is enumerated per-case by the benchmark authors. No policy language, no
classification model.

---

### 8. `kuehlewind2026audit` — IETF draft-kuehlewind-audit-architecture-00 — **CLEAR**

**Q1: no. It records authorization; it does not decide it.** §5: "Authorization Transition Records:
capture changes in permission state over time: initial grants, step-up approvals, scope narrowing on
exchange, revocation, and expiry. Authorization is considered as a time-evolving state. The ordered
sequence of Authorization Transition Records of a run reconstructs the authorization in force at any
point within it." WI-8 asks for "a canonical Authorization Transition Record **format** carrying previous
state, new state, triggering event, and responsible actor." A format, not a semantics. Authorization
itself is OAuth's: §4.1, "Agents operate within the authorization they were issued."

**Q2: no, and the vocabulary is absent.** Searched
`inject|untrusted|classif|provenance|retriev|memory|quot|mention|status|standing|misinterpret|intent`.
Zero hits for `inject`, `untrusted`, `classif`, `quot`, `mention`, `standing`. `intent` appears only as
"user intent" to be linked to actions, never as something whose recognition can fail.

**Q3.** OAuth/RFC lineage (RFC 6749, RFC 8693, RFC 9334 RATS, SCITT, WIMSE, SPIFFE). None of the
formalization tradition.

Worth noting positively for the manuscript: §4.1's requirement that boundary records "reflect the
canonical request as observed at the boundary, **not as reported by the Agent**" is a structural cousin of
the manuscript's insistence that the system's assigned classification be recorded separately.

---

### 9. `owasp2025agentic` — OWASP Agentic AI: Threats and Mitigations — **CLEAR**

64 occurrences of `authoriz`, all threat description or mitigation checklist. The closest passage
(l.398–409) states the manuscript's problem and immediately hands it to conventional access control:

> a Confused Deputy vulnerability arises when an AI agent... **cannot distinguish between legitimate user
> requests with proper authorizations and adversarial injected instructions**... To mitigate this, it is
> essential to properly scope agent entitlements by applying the principle of least privileges... and
> validate whether users submitting the prompts have proper authorization to perform the requested
> actions.

The mitigation presupposes the requester is correctly identified, which is the presupposition under
audit. Closing recommendation is "strict RBAC and a zero-trust model" (l.431). Zero hits for
`use-mention`, `quotation|quoted`, `semantics`, or any tradition author.

---

### 10. `nistCaisi2026agents` — NIST/CAISI RFI announcement — **CLEAR**

A 12 January 2026 news item announcing a Request for Information, ~450 words of body text. It poses
questions ("Promise of and possible gaps in existing cybersecurity approaches when applied to AI agent
systems"; "Interventions in deployment environments... including methods to constrain and monitor the
extent of agent access"). It asserts nothing and defines nothing. Note for the manuscript: it is cited in
§2.1 as work that "asks how to measure, constrain, and monitor agent access in deployment environments" —
accurate, but a reader who follows the link finds an RFI notice, not a study. Consider softening
"Work by NIST and CAISI asks..." to make its genre explicit.

---

## Two uncited works that are more dangerous than anything in the assigned set

### CaMeL — Debenedetti et al., "Defeating Prompt Injections by Design" (arXiv 2503.18813) — **must cite; refutes the necessity claim as worded**

Not in `references-local.bib` or `references.bib`; not cited anywhere in `sections/`, `sections-delegation/`,
or `sections-evidentiary/` (searched `camel|beurer|IPIGuard|MiniScope|fides|SecAlign|debenedetti`). Same
first author as AgentDojo, which the manuscript does cite. Fetched from arXiv for this audit
(`/private/tmp/.../scratchpad/camel.pdf`, `camel.txt`).

CaMeL **does** supply an authorization semantics for LLM agent actions: a privileged LLM emits a program
from the trusted query alone, a quarantined LLM parses untrusted data into typed values, a custom Python
interpreter propagates capability tags recording each value's `sources` and `readers`, and security
policies are checked before every tool call (Fig. 4: `if policies.check(tool, args, mem) = ⊥ then return
Trace`). It reports "77% of tasks with provable security" on AgentDojo.

**Why it does not occupy the ground, and why it still forces a narrowing.** CaMeL never classifies a
string occurrence's role. Capabilities are assigned *mechanically by data flow* inside the interpreter,
never by interpreting the string. It removes the manuscript's step rather than solving it — and it buys
that by assuming the step away, in as many words (§3):

> **We assume that the user prompt is trusted, that the user is not pasting a prompt from an untrusted
> source, and, if there is a memory in place, the memory has not been compromised by the adversary.**

That single sentence is the manuscript's thesis restated as CaMeL's precondition, and it belongs in the
paper. §3.1 further concedes CaMeL "cannot defend against text-to-text attacks which have no consequences
on the data flow," including injection-induced phishing.

Bibliography: joins to **DIFC and control-flow integrity** — Denning 1976, Denning & Denning 1977, Myers &
Liskov 1997, Sabelfeld & Myers 2003, Abadi et al. 2009 (CFI), Anderson 2010 ch. 6 — and to CHERI. No
ABLP/Lampson, SPKI, Delegation Logic, SecPAL, UCON, XACML.

### MiniScope — Zhu et al. (arXiv 2512.11147) — **should cite; ADJACENT**

"A Least Privilege Framework for Authorizing Tool Calling Agents." Reconstructs permission hierarchies
from relationships among tool calls and combines them with a mobile-style permission model. Abstract only
(not fetched in full). Permissions derive from tool-call structure and user grants, not from string-role
classification; it presupposes the requester. ScopeGate names it as its nearest neighbour and explicitly
declines to claim priority over it. Given that the manuscript positions against ScopeGate, a reviewer
will expect MiniScope in the frame.

---

## Overall verdict

**On the assigned set: the contribution survives, cleanly.** Not one of the ten defines conditions under
which an operation counts as authorized *given a classification of a string occurrence's role and its
source's standing*. The three that come closest each mark the gap rather than fill it: South leaves LLM
policy-translation robustness "to future work" and names policy-channel injection as an unguarded new
attack surface; AttriGuard declares user-authorized untrusted content an explicit non-goal and concedes
causal attribution cannot settle it; ScopeGate rules language out of the authorization decision by
construction. The IETF draft standardizes a record format for authorization transitions and never touches
interpretation (zero hits for `inject`, `untrusted`, `classif`). And the Q3 result is uniform: **none of
the ten cites ABLP/Lampson, SPKI/SDSI, Delegation Logic, SecPAL, or UCON.**

**But the claim as worded is false in one respect, and a hostile reviewer with CaMeL in hand will say so.**
The sentence "LLM deployments must *classify* a string occurrence... and assign its source standing before
any authorization engine can run" asserts a necessity. CaMeL and ScopeGate are two existence proofs
against it: both run authorization engines over agent actions without ever classifying a string's role.
CaMeL makes provenance structural; ScopeGate makes policy exogenous and enumerable. Neither is a
counterexample to the *problem*; both are counterexamples to the *necessity*.

### The narrowing, precisely

Three edits, in order of importance.

1. **Replace the necessity claim with a scope claim.** Not "deployments must classify," but: *there is a
   class of deployments in which authority is conferred, altered, or invoked through language reaching
   the system at runtime — the user's own natural-language mandate, an amendment arriving mid-session, a
   retrieved document the user has authorized to determine an action, a tool result carrying a directive
   that genuinely has standing. In that class the classification and standing assignments are
   unavoidable, and no authorization semantics covers them.* The structural defences do not cover this
   class; they exclude it. Say so, and cite the exclusions: CaMeL §3's trusted-prompt assumption,
   ScopeGate §II.C's out-of-band-policy requirement, AttriGuard's explicit-delegation non-goal, South
   §5.2's unguarded policy-authoring channel. Four independent authors carving out the same case is far
   stronger evidence for the manuscript than an unqualified "must."

2. **Reword the "nobody has joined them" clause, which is both too strong and too weak.** Too strong:
   the agent-security literature *has* joined one branch of the access-control tradition — CaMeL to DIFC
   (Denning; Myers & Liskov; Sabelfeld & Myers) and control-flow integrity, ScopeGate to complete
   mediation (Saltzer & Schroeder; Hardy), South to policy-language syntax (XACML, ODRL, ROWLBAC). Too
   weak, because the sharper and fully evidenced claim is available: *the branch nobody has joined to is
   the authority-and-delegation lineage — ABLP, SPKI/SDSI, Delegation Logic, SecPAL, UCON — which is the
   branch that has semantics for who may say what on whose behalf.* Across all ten cited works plus CaMeL,
   there is not one citation to any of those five. That is a checkable, evidenced negative, and it makes
   the same point without overreaching.

3. **Cite CaMeL and MiniScope.** CaMeL is by AgentDojo's first author, is the best-known "provable"
   prompt-injection defence, and is the obvious desk-reject question. Leaving it out is the single largest
   avoidable risk in the section.

### Residual risk I did not close

I audited the assigned ten plus CaMeL (full text) and MiniScope (abstract). Not checked: **ETDI**
("OAuth-enhanced tool definitions and policy-based access control," cited by AttriGuard as ref [51] —
the OAuth-plus-policy framing makes it the most plausible remaining occupier), **IPIGuard**, **Fides**,
and **Wu, Cecchetti & Xiao 2024** (cited by CaMeL as an information-flow-control treatment of indirect
prompt injection). ETDI and Wu et al. are worth ten minutes each before submission.
