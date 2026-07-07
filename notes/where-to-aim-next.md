# Where To Aim Next

## Recommendation

Aim at the highest-value idea, not at preserving a forced connection between papers.

The best target is:

> **Delegation assurance for AI systems: an evidence framework for justified machine action.**

This should be a broader paper than adversarial pragmatics, but not a generic agent-security paper. The contribution should be a safety-case/evaluation framework that says what evidence is needed before an AI system's action can be treated as authorized, scoped, attributable, contestable, remediable, and auditable.

The adversarial-pragmatics benchmark remains relevant only if it helps this larger argument. It should appear as one evidence layer, not as the reason the new paper exists.

## Ranked Directions

| Rank | Direction | Why It Is Strong | Main Risk | Verdict |
|---|---|---|---|---|
| 1 | **Delegation assurance / justified machine action** | Bridges agent security, safety cases, evaluation design, auditability, and language-mediated authority. Produces a reusable framework rather than another benchmark. | Can become too broad unless it has boundary conditions and evidence requirements. | Aim here. |
| 2 | **Language-mediated authority as a security object** | Most distinctive relative to existing agent-security work; directly uses Brett's comparative advantage. | May be too narrow if detached from tools, access, and audit. | Use as the central wedge inside #1. |
| 3 | **Adversarial pragmatics as secure-delegation evidence** | Cleanest connection to the existing paper. | Too derivative; risks sounding like a framing essay for the benchmark. | Use as a section, not the whole paper. |
| 4 | **Agent-security taxonomy / secure delegation threat model** | Timely and legible. | Crowded by OWASP, NIST/CAISI, AgentDojo, instruction hierarchy, IAM/protocol work, and surveys. | Avoid as primary aim. |
| 5 | **Levels-of-game essay** | Memorable strategic frame; useful for talks and introductions. | Too aphoristic for a paper unless grounded in evidence standards. | Use as positioning logic only. |

## What The New Paper Should Be

The strongest version is a bridge paper between four literatures:

1. agent security and prompt injection;
2. access control, delegated identity, and audit protocols;
3. AI safety cases and assurance cases;
4. evaluation methodology for language-mediated control.

The paper's central claim:

> Current agent-security work identifies threats and controls. Secure delegation adds the evidentiary question: what would justify the claim that a machine action stayed within delegated authority?

This is not primarily a paper about prompts. It is a paper about action justification.

But the language layer is the wedge:

> In AI systems, authority is often carried, modified, spoofed, or lost through language. That makes instruction status, quotation, provenance, scope, policy examples, tool outputs, and evaluator labels part of the security surface.

That wedge is where the existing paper can contribute without owning the whole new project.

## Are The Levels-Of-Game Ideas Still Useful?

Yes, but not as the paper's explicit structure.

They are useful as the strategic diagnosis:

| Lower game | Higher game | Use in new paper |
|---|---|---|
| Block bad prompts | Preserve instruction-control integrity | Shows why prompt security is not enough. |
| Detect attacks | Specify evidence for authorized action | Motivates the assurance turn. |
| Build agent threat taxonomies | Build delegation safety cases | Distinguishes the paper from crowded survey work. |
| Trust model outputs | Audit delegated action | Moves from answer quality to action justification. |
| Validate benchmark scores | Validate evidence licenses | Connects evaluation methodology to safety cases. |

The levels-of-game idea should appear in the introduction as a paragraph or small table, not as the main theory.

Candidate formulation:

> AI security has often optimized the lower-level game of detecting bad prompts or blocking bad outputs. Tool-using systems force a higher-level game: specifying what evidence would show that a delegated action remained authorized, scoped, attributable, and auditable.

## Relation To The Existing Paper

No forced dependence.

The existing paper is still useful because it supplies one worked example of a delegation-assurance evidence layer. It measures whether systems and evaluators preserve distinctions among instructions, quotations, embedded commands, policy examples, source authority, refusal, task success, risk, and failure attribution.

But the new paper should not be written as "the theory behind the benchmark." That is too small.

Write it as:

> The benchmark paper is one example of the evidence this broader framework says assurance cases will need.

That preserves the connection without subordinating the new idea to the existing project.

## Boundary Conditions

The new paper should not claim every AI-security issue is a delegation issue.

Core delegation failures involve at least one of:

- delegated action;
- delegated access;
- delegated disclosure;
- delegated persistence;
- delegated judgment;
- delegated evaluation;
- delegated accountability.

Non-core cases include ordinary hallucination in no-tool chat, model extraction, benchmark contamination, infrastructure compromise, training-data leakage, and capability shortfall without action rights. These can affect delegation, but they are not delegation failures unless they alter authorized action or auditability.

## Best Title Direction

Avoid titles that sound like a generic agent-security rebrand.

Weak:

> Secure Delegation for AI Agents

Better:

> **Delegation Assurance for AI Systems**

Also viable:

- **Justified Machine Action**
- **Evidence Standards for Delegated AI Action**
- **From Prompt Security to Delegation Assurance**

Best current title:

> **Delegation Assurance for AI Systems**

Subtitle:

> **Evidence Standards for Justified Machine Action**

## Minimum Paper Shape

1. Introduction: the security game has moved from prompt defense to action justification.
2. Crowded-field positioning: agent-security threats and IAM/audit protocols are necessary but do not settle the evidentiary question.
3. Definition: delegated AI action and delegation assurance.
4. Claims/arguments/evidence pattern for delegated authority.
5. Boundary conditions: what is not primarily a delegation failure.
6. Failure-to-evidence table: common security failures mapped to what evidence would catch them.
7. Language-mediated authority as the distinctive hard case.
8. Adversarial pragmatics as one evidence layer.
9. Implications for system cards, red-team reports, safety cases, and external audits.

## Next Move

Do not draft a full paper yet.

Draft a 700--900 word introduction with this thesis:

> The next step above prompt security is not another agent threat taxonomy. It is delegation assurance: specifying the evidence required to justify machine actions performed on behalf of humans and institutions. Because AI systems receive, transform, and execute authority through language, this evidence has to include language-mediated authority, not only permissions, logs, and access controls.

If that introduction works, the paper is worth building.
