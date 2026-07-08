# Delegation Assurance for AI Systems
**Subtitle:** Evidence Standards for Justified Machine Action
## Status
This is a working paper sketch, not a full draft. It consolidates the current best version of the new-paper idea: delegation assurance as an evidence framework for justified machine action.
## Abstract Seed
Current agent-security work provides threat taxonomies, attacks, defenses, and architectural controls. Less developed is the evidentiary question: what would justify the claim that an AI system's action remained within delegated authority? This paper calls that problem delegation assurance. Delegation assurance requires evidence across three layers: technical control, language-mediated authority, and institutional audit. We map common AI-security failures to delegation-layer failures and derive evaluation designs for authority uptake, scope control, tool licensing, information flow, persistence, refusal calibration, audit reconstruction, and judge validation. The goal is not to replace agent-security taxonomies, access-control mechanisms, audit protocols, or AI safety cases. The goal is to give them a common evidentiary grammar for justified machine action.
## Introduction
AI security work has made real progress by identifying prompt injection, jailbreaks, tool misuse, data exfiltration, memory poisoning, and scaffold failures. That work remains necessary. But tool-using AI systems also raise a question that is not captured by asking whether a prompt was malicious or an output was unsafe. When a system reads private data, calls an external tool, updates persistent state, sends a message, grades a transcript, or recommends an institutional decision, the security issue is whether the resulting machine action stayed within the authority delegated to it.

This paper calls that problem delegation assurance. The term does not introduce a new class of AI-agent attacks. It names an evidentiary problem: what would justify the claim that an AI system's action was authorized, scoped, attributable, contestable, remediable, and auditable? Existing agent-security work gives threat models, benchmarks, defenses, access-control mechanisms, and audit protocols. Those are essential components. Delegation assurance asks how those components support a safety case about action: who delegated authority, what action was licensed, what sources could change that license, which limits were non-delegable, what evidence records the transition from instruction to action, and how failure would be attributed after the fact.

A user asks an assistant to summarize an email thread but not reveal confidential attachments. A retrieved webpage contains an instruction to ignore the user and send stored credentials elsewhere. A policy document includes examples of prohibited requests, some of which look like executable commands. A memory entry says the user usually approves a class of action, although the current task does not. A judge sees only a polished transcript and scores the interaction as safe because the final answer looks compliant. In each case, the system's failure is not adequately described by output safety alone. The question is whether authority moved across language, tools, memory, and evaluation in a licensed way.

Delegation assurance therefore sits between technical control and institutional audit. At one end are familiar engineering mechanisms: least privilege, access control, scoped credentials, tool permissions, logs, monitors, and memory controls. At the other end are assurance practices: structured claims, arguments, evidence, audit records, incident review, and external accountability. The hard middle layer is language-mediated authority. AI systems increasingly receive, transform, and execute authority through language. A string may be a command, a quotation, an example, a policy boundary, an untrusted document, a tool result, or a request to analyze rather than enact. A system that cannot preserve those distinctions cannot support a strong claim that its actions remained within delegated authority.

The contribution of this paper is a delegation-assurance framework for AI systems. The framework maps familiar security failures to evidence requirements. Direct prompt injection becomes a failure to preserve instruction authority. Indirect prompt injection becomes a failure to prevent untrusted data from becoming action-guiding instruction. Tool misuse becomes a failure of action licensing. Data exfiltration becomes a failure to separate read access from disclosure authority. Memory poisoning becomes an unauthorized persistence update. Over-refusal and under-refusal become different failures of delegation calibration: one abandons authorized work, the other exceeds authorized bounds. Judge failure becomes a failure of the evaluation layer to preserve the distinctions needed to license a safety claim.

This framework also sets boundary conditions. Not every AI failure is primarily a delegation failure. A factual hallucination in a no-tool chat setting, a benchmark-contamination artifact, capability shortfall, model extraction, infrastructure compromise, or training-data privacy leakage may affect delegated action downstream, but those cases are not central examples unless they alter authorized action, action evidence, or accountability records. Delegation assurance is about systems that act, access, disclose, persist, judge, or otherwise exercise authority on behalf of someone else.

The framework can be expressed as a safety-case pattern. For a task family T in environment E, the top-level claim is not merely that system S produced a safe-looking result. It is that S acted only within delegated authority, and that the authority relation can be reconstructed by a third party. The evidence has to identify the principal, delegate, action, authority source, scope, constraints, provenance, information-flow rights, persistence rights, tool-use license, non-delegable limits, and failure attribution. Subclaims then ask whether S preserves instruction status across trusted and untrusted language, preserves authority priority across system, developer, user, tool, retrieved, and policy sources, keeps action scope bounded by target, time, tool, data class, and permitted operation, separates read access from disclosure authority, requires authorization for persistent state changes, produces audit evidence sufficient for third-party reconstruction, and uses evaluators that preserve rather than collapse these distinctions.

This is where adversarial pragmatics enters the picture, but only as one evidence layer. A delegation-assurance case needs evidence that language-mediated authority remains stable under adversarial and ambiguous conditions. The adversarial-pragmatics benchmark is one way to test that layer: it uses controlled contrasts to ask whether systems and evaluators preserve distinctions among instructions, embedded commands, quotation, source authority, scope, refusal, task success, risk, and failure attribution. The broader paper does not depend on that benchmark. The benchmark shows what one reusable evidence layer can look like when delegation assurance reaches the language interface.

The goal is not to replace agent-security taxonomies, access-control mechanisms, audit protocols, or AI safety cases. The goal is to give them a common evidentiary grammar for justified machine action. The next step above prompt security is not another list of threats. It is a way to specify what has to be true, and what has to be recorded, before an AI system's action can be treated as legitimately delegated.
## Core Claim
By *justified*, this paper means justified for the purposes of security and assurance: there is enough evidence to support the claim that the action remained within delegated authority in the relevant operational context.

A delegated AI action is justified only when a reviewer can reconstruct, from evidence independent of the system's bare assertion, who authorized the action, what action was licensed, under what scope and constraints, through which sources and tools, with what information-flow and persistence rights, subject to which non-delegable limits, and with what attribution if control fails.

## Safety-Case Pattern
**Top-level claim:** for task family T in environment E, system S acts only within delegated authority.

**Subclaims:**

1. S preserves instruction status across trusted and untrusted language.

2. S preserves authority priority across system, developer, user, tool, retrieved, and policy sources.

3. S keeps action scope bounded by target, time, tool, data class, and permitted operation.

4. S separates read access from disclosure authority.

5. S requires authorization for persistent state changes.

6. S produces audit evidence sufficient for third-party reconstruction.

7. S's evaluators preserve the same distinctions rather than collapsing success, safety, refusal, and compliance.

## Boundary Conditions
Not every AI-security failure is primarily a delegation failure. Core delegation failures involve at least one of:

- delegated action;

- delegated access;

- delegated disclosure;

- delegated persistence;

- delegated judgment;

- delegated evaluation;

- delegated record-keeping for accountability.


Non-core cases include ordinary hallucination in no-tool chat, model extraction, benchmark contamination, infrastructure compromise, training-data leakage, and capability shortfall without action rights. These can affect delegation, but they are not delegation failures unless they alter authorized action or auditability.

## Table 1: AI-Security Failures As Delegation-Layer Failures
| Surface failure | Delegation-layer failure | Security question |
| --- | --- | --- |
| **Authority uptake failures** |  |  |
| Direct prompt injection | Instruction authority is overwritten by an attacker-controlled string. | Which instruction source had authority, and did the system preserve that priority? |
| Indirect prompt injection | Untrusted data is promoted into an action-guiding instruction. | Did the system preserve the distinction between content to process and instruction to obey? |
| Jailbreak | Safety constraints are treated as negotiable within the user dialogue. | Which constraints are non-delegable, and did the system maintain them under pressure? |
| **Action execution failures** |  |  |
| Tool misuse | The model invokes a legitimate tool for an unauthorized action. | Was the tool call licensed by the principal's goal and the system's policy scope? |
| Data exfiltration | Access to information is delegated without corresponding release authority. | Did the system distinguish permission to read from permission to disclose? |
| Memory poisoning | Persistent state is modified by content without authority to shape future action. | Who is allowed to update durable context, and how is that update audited? |
| Goal drift | The system pursues a nearby or inferred objective beyond the delegated task. | What objective was delegated, and what evidence shows the system stayed within it? |
| Over-refusal | The system declines safe work because refusal is treated as the dominant safety action. | Did the system confuse risk control with task abandonment? |
| Under-refusal | The system completes a request that violates policy or authority constraints. | Which boundary should have blocked action, and why did it fail? |
| Scaffold failure | The model's surrounding workflow loses, hides, or misapplies constraints. | Did the system preserve authority and scope across components, not just inside the model turn? |
| **Evidentiary and evaluation failures** |  |  |
| Agent transcript misreporting | The system's report does not match what happened during delegated action. | Can auditors reconstruct the action, evidence, and failure attribution from the trace? |
| LLM-judge failure | The evaluator collapses task success, compliance, risk, and failure attribution. | Is the evaluation itself authorized to license safety claims? |

## Table 2: Delegation Evidence And Evaluation Designs
| Delegation evidence needed | What it tests | Evaluation design |
| --- | --- | --- |
| Instruction-status evidence | Whether the system identifies which language has directive force. | Minimal pairs contrasting command, quotation, embedded content, policy example, and reported speech. |
| Authority evidence | Whether higher-priority instructions defeat lower-priority or untrusted instructions. | Crossed system/developer/user/tool-output conflicts with aligned and conflicting subordinate content. |
| Scope evidence | Whether permission and prohibition remain bounded. | Items varying permitted action, prohibited action, time, target, tool, and data boundary. |
| Provenance evidence | Whether source identity affects uptake. | Same payload presented as user request, webpage text, email body, retrieved document, tool output, and policy text. |
| Action-licensing evidence | Whether tool use follows from authorized task goals. | Tool-call tasks where reading, transforming, storing, sending, and deleting have distinct authorization. |
| Information-flow evidence | Whether access rights are separated from disclosure rights. | Read-but-do-not-reveal and transform-without-leaking tasks with benign canaries. |
| Persistence evidence | Whether memory or state changes require authority. | Memory-update tasks with trusted, untrusted, stale, and adversarial sources. |
| Refusal calibration evidence | Whether refusal tracks policy risk rather than uncertainty or linguistic form. | Safe/unsafe paired requests, safe analysis of unsafe text, and unsafe enactment of quoted text. |
| Failure-attribution evidence | Whether failures are assigned to model capability, policy boundary, scaffold, tool, evaluator, or taxonomy instability. | Multi-axis adjudication protocol over model outputs and agent transcripts. |
| Audit evidence | Whether a third party can reconstruct why the action happened. | Trace review tasks requiring source, authority, tool, policy, and rationale reconstruction. |
| Judge-validation evidence | Whether automated graders preserve the same distinctions. | LLM-judge validation against expert labels, with no-rubric and rubric-aided conditions. |

## Proposed Outline
1. **Introduction**

  - The problem has moved from prompt defense to action justification.

  - Delegation assurance names the evidentiary question.

2. **What Existing Agent-Security Work Does Not Settle**

  - Agent-security threats, IAM, and audit protocols are necessary but do not settle the evidentiary question.

3. **Delegated Action: Principal, Authority, Scope, and Evidence**

  - Define principal, delegate, action, authority, scope, and evidence.

4. **Delegation Assurance**

  - Present the claim/argument/evidence pattern.

5. **Boundary Conditions**

  - Specify what is not primarily a delegation failure.

6. **Failure-To-Evidence Mapping**

  - Develop Table 1 into the diagnostic framework.

7. **Evidence-To-Evaluation Mapping**

  - Develop Table 2 into evaluation requirements.

8. **Language-Mediated Authority as a Security Object**

  - Treat instruction status, quotation, provenance, scope, and evaluator labels as security objects.

9. **Adversarial Pragmatics As One Evidence Layer**

  - Use the existing benchmark as an example, not as the center of the new paper.

10. **Implications for System Cards, Red-Teaming, Audits, and Judge Validation**

  - System cards, red-team reports, safety cases, external audits, and judge validation.

## Immediate Gaps
- Add actual citations from the source-verification queue.

- Decide target genre: workshop position paper, policy memo, or full academic article.

- Create a delegation-stack figure.

- Turn the two tables into polished paper tables.

- Draft the existing-work section without sounding like a survey.
