# From Prompt Security to Secure Delegation
## Thesis
AI security is moving from a prompt-security problem to a secure-delegation problem.

Prompt injection, jailbreaks, tool misuse, policy ambiguity, agent scaffold failure, and LLM-judge failure are usually treated as separate failure classes. They are separate at the attack-surface level, but they share a deeper structure: an AI system is being allowed to act on someone else's behalf, and the evaluator has to know whether authority, scope, action rights, and failure attribution remained under control.

The new paper should not claim that "agentic AI needs a new security lens." That field is already crowded. Indirect-prompt-injection work, instruction-hierarchy work, AgentDojo, OWASP Agentic AI guidance, NIST/CAISI agent-security work, and recent agent-security surveys already establish that tool-using and agentic systems create new attack surfaces.

The sharper claim is:

> Secure delegation is an evidence standard for justified machine action.

The paper asks what has to be tracked, tested, and auditable before an AI system can safely act on a user's, organization's, or institution's behalf.

The compact contribution statement:

> This paper does not introduce a new class of AI-agent attacks. It introduces a delegation-assurance framework: a way to specify, test, and audit whether an AI system's actions remained within the authority delegated to it. The contribution is the mapping from agent-security failures to evidence requirements, with particular attention to language-mediated authority: the system's ability to preserve distinctions among instructions, quotations, untrusted data, policy examples, tool outputs, and authorized user intent.
## The Wedge
Existing agent-security work largely asks:

> What are the threats, attacks, defenses, and architectural weak points of AI agents?

The secure-delegation paper should ask:

> What evidence would show that delegated machine action remained authorized, scoped, attributable, contestable, remediable, and auditable?

That is a different contribution. It does not compete with threat taxonomies on breadth. It converts security concerns into evaluation requirements and safety-case requirements.

The paper's distinctive move is to connect three layers that are usually treated separately:

1. **Technical control:** tools, permissions, memory, retrieval, policies, logs, and runtime monitors.

2. **Language-mediated authority:** which strings count as instructions, quotations, policy examples, untrusted data, or authorized user intent.

3. **Institutional audit:** who can explain, contest, correct, or take responsibility for a delegated action after it happens.

## Core Definition
Secure delegation is the condition in which an AI system acts on behalf of a principal only within authorized scope, under evidence that makes the action's authority, source, goal, constraints, and failure mode auditable.

The definition deliberately avoids saying that the model "understands" the principal's intent. The security question is operational:

> Can the system and its evaluators show why this action was authorized, what it was authorized to do, what it was not authorized to do, and where control failed if the action went wrong?

A delegated AI action is justified only if there is reviewable evidence of:

- principal;

- delegate;

- action;

- authority source;

- scope;

- constraints;

- provenance;

- information-flow rights;

- persistence rights;

- tool-use license;

- non-delegable limits;

- failure attribution.


This should be organized as a claims-arguments-evidence structure:

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
The frame needs clear exclusions. Not every AI-security failure is primarily a delegation failure.

Cases outside the primary secure-delegation target include:

- ordinary factual hallucination in a no-tool chat setting;

- model capability shortfall without action rights;

- benchmark contamination;

- model extraction;

- infrastructure compromise;

- training-data privacy leakage;

- generic availability failures.


These failures can affect secure delegation, but they are not delegation failures in the primary sense unless they alter authorized action, action evidence, or post-hoc accountability.
## Evidence Quality
The paper should distinguish reported evidence from verifiable evidence.

A model's own transcript is weak audit evidence when the model or scaffold can misreport what happened. Stronger evidence includes independent logs, append-only traces, authorization-transition records, delegated-principal identity, tool-call records, and trace reconstruction that does not depend only on the model's self-report.

This distinction connects the paper to protocol and assurance-case work rather than leaving "auditability" as a slogan.
## Table 1: AI-Security Failures as Delegation-Layer Failures
| Surface failure | Delegation-layer failure | Security question |
| --- | --- | --- |
| Direct prompt injection | Instruction authority is overwritten by an attacker-controlled string. | Which instruction source had authority, and did the system preserve that priority? |
| Indirect prompt injection | Untrusted data is promoted into an action-guiding instruction. | Did the system preserve the distinction between content to process and instruction to obey? |
| Jailbreak | Safety constraints are treated as negotiable within the user dialogue. | Which constraints are non-delegable, and did the system maintain them under pressure? |
| Tool misuse | The model invokes a legitimate tool for an unauthorized action. | Was the tool call licensed by the principal's goal and the system's policy scope? |
| Data exfiltration | Access to information is delegated without corresponding release authority. | Did the system distinguish permission to read from permission to disclose? |
| Memory poisoning | Persistent state is modified by content without authority to shape future action. | Who is allowed to update durable context, and how is that update audited? |
| Goal drift | The system pursues a nearby or inferred objective beyond the delegated task. | What objective was delegated, and what evidence shows the system stayed within it? |
| Over-refusal | The system declines safe work because refusal is treated as the dominant safety action. | Did the system confuse risk control with task abandonment? |
| Under-refusal | The system completes a request that violates policy or authority constraints. | Which boundary should have blocked action, and why did it fail? |
| Scaffold failure | The model's surrounding workflow loses, hides, or misapplies constraints. | Did the system preserve authority and scope across components, not just inside the model turn? |
| Agent transcript misreporting | The system's report does not match what happened during delegated action. | Can auditors reconstruct the action, evidence, and failure attribution from the trace? |
| LLM-judge failure | The evaluator collapses task success, compliance, risk, and failure attribution. | Is the evaluation itself authorized to license safety claims? |
## Table 2: Delegation Evidence and Evaluation Designs
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
## Relation To Adversarial Pragmatics
Adversarial pragmatics becomes one measurement layer inside secure delegation.

It does not solve tool security, access control, memory integrity, or governance. It tests a necessary condition for all of them: whether the system preserves control over language-mediated authority under adversarial or ambiguous conditions.

The benchmark paper can be cited as a concrete example:

> A secure-delegation safety case needs evidence that instruction status, source authority, quotation, scope, task success, policy compliance, risk, and failure attribution remain stable under controlled perturbation. The adversarial-pragmatics benchmark operationalizes that evidence layer with minimal pairs and multi-axis adjudication.
## Candidate Opening
AI security is often described as a problem of bad prompts, unsafe outputs, overbroad refusals, vulnerable tools, or unreliable agents. Those descriptions identify important symptoms, but they miss the common control problem. AI systems are increasingly authorized to act on behalf of users and institutions: reading messages, calling tools, modifying files, querying systems, summarizing policy, judging transcripts, and recommending decisions. The security question is therefore not only whether a model produced an acceptable answer. It is whether delegated machine action remained authorized, scoped, attributable, and auditable as language, tools, data, policies, and evaluators interacted.

This paper calls that problem secure delegation. The term does not name a new attack class. It names an evidence standard. Before an AI system can safely act for someone else, developers and evaluators need evidence about who delegated authority, what action was licensed, which sources could change that license, what constraints were non-delegable, and how failure would be attributed after the fact.
## Venue-Facing Abstract Seed
Current agent-security work provides threat taxonomies, attacks, defenses, and architectural controls. Less developed is the evidentiary question: what would justify the claim that an AI system's action remained within delegated authority? This paper calls that problem secure delegation. Secure delegation requires evidence across three layers: technical control, language-mediated authority, and institutional audit. We map common AI-security failures to delegation-layer failures and derive evaluation designs for instruction status, authority priority, scope, provenance, action licensing, information flow, persistence, refusal calibration, failure attribution, audit reconstruction, and judge validation.
## Claims To Make
- Agentic AI security is already a crowded field; secure delegation is a narrower evidence-and-evaluation frame.

- Prompt injection matters because it can corrupt delegation, not because prompts are the only security boundary.

- Tool security and access control are necessary but incomplete without evidence about language-mediated authority and scope.

- Refusal quality, task success, policy compliance, and safety risk have to be separated because each supports a different delegation claim.

- Auditability is part of security, not a post-hoc documentation layer.

- Adversarial pragmatics supplies one reusable measurement layer for secure delegation.

- The paper is a bridge between agent security, evaluation design, pragmatics, and AI assurance.

- Least privilege, access control, audit logging, and assurance cases are inputs to the framework, not things the framework replaces.

## Claims To Avoid
- Do not say secure delegation is the whole of AI security.

- Do not say all agent failures are linguistic failures.

- Do not imply the current pilot proves the secure-delegation thesis.

- Do not compete with OWASP, NIST/CAISI, AgentDojo, or agent-security surveys as a broader taxonomy.

- Do not lead with machine agency as metaphysics. Lead with authorized action as security engineering.

- Avoid unqualified use of "corrigibility"; use contestability, reversibility, remediability, and accountable correction unless engaging alignment literature directly.

- Do not let "delegation" become so broad that every model failure becomes a delegation failure.

## Immediate Next Drafting Tasks
1. Turn the candidate opening into a 700-word introduction.

2. Convert Table 1 into the paper's main diagnostic table.

3. Convert Table 2 into a checklist for evaluators and system-card authors.

4. Sketch one figure: the delegation stack from principal to system policy, model, tools, data sources, persistent state, logs, and evaluators.

5. Write a short "what this adds beyond agent-security taxonomies" subsection using the verified source queue.

6. Draft the safety-case subsection around the top-level claim and seven subclaims above.
