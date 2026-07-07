# Secure Delegation New-Paper Plan

## Recommendation

Use the waiting period for the second judge to start a separate secure-delegation paper, but make the first artifact a short position paper or policy memo rather than a full empirical article.

The existing paper answers:

> How can we evaluate language-mediated control failures in AI safety evaluation?

The new paper should answer:

> What is the higher-level security problem that prompt injection, jailbreaks, tool misuse, agent failure, policy ambiguity, and judge failure all instantiate?

The proposed answer:

> AI security is becoming the problem of secure delegation: deciding when, how, and under what evidence humans and institutions can delegate agency to AI systems.

## Crowded-Field Check

The broad question is crowded. It is not original to say that agentic AI needs a new security lens, that prompt injection affects tool-using agents, or that autonomous agents need threat models. That territory is already occupied by indirect-prompt-injection work, instruction-hierarchy work, AgentDojo, OWASP Agentic AI guidance, NIST/CAISI agent-security work, OAuth/OpenID-style authenticated-delegation proposals, IETF audit-architecture work, and recent agentic-security surveys.

The viable original wedge is narrower:

> Secure delegation is not another agent-security taxonomy. It is an evidence standard for justified machine action: what has to be tracked, tested, and auditable before an AI system can safely act on someone else's behalf.

That means the paper should not compete with surveys or threat taxonomies on breadth. It should make a more specific claim:

> Existing agent-security work identifies attack surfaces and defenses; secure delegation asks what evidence would show that authority, scope, action rights, and failure attribution remained under control across those surfaces.

The paper's distinctive contribution should be the bridge from security failures to evaluation requirements. The question is less "What are the threats?" and more "What would a safety case need to prove about delegation before the system acts?"

Sources checked for this scoping judgment on 2026-07-07:

- [Greshake et al. 2023, indirect prompt injection](https://arxiv.org/abs/2302.12173): LLM-integrated applications blur data and instruction, and retrieved prompts can manipulate application behavior and API calls.
- [Wallace et al. 2024, instruction hierarchy](https://arxiv.org/abs/2404.13208): privileged-instruction ordering is already a central technical response to prompt injection and jailbreaks.
- [AgentDojo 2024](https://arxiv.org/abs/2406.13352): tool-using agents over untrusted data already have a dedicated evaluation environment.
- [OWASP Agentic AI threats and mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/): agentic AI security guidance is already organized as threat-model-based practical mitigation.
- [NIST/CAISI 2026 RFI](https://www.nist.gov/news-events/news/2026/01/caisi-issues-request-information-about-securing-ai-agent-systems): federal standards work is explicitly focused on AI agent systems, autonomous action, adversarial data, access constraints, monitoring, and measurement.
- [The Attack and Defense Landscape of Agentic AI, 2026](https://arxiv.org/html/2603.11088v1): the survey space is explicitly systematizing agentic AI security across design dimensions, attacks, and defenses.
- [Authenticated Delegation and Authorized AI Agents](https://arxiv.org/html/2501.09674v1): term-level delegation work already exists around OAuth/OpenID-style agent credentials, scoped permissions, accountability, and natural-language permission translation.
- [IETF AI-agent audit architecture draft](https://datatracker.ietf.org/doc/draft-kuehlewind-audit-architecture/): protocol work already targets delegation audit records, delegated principal identity, authorization-transition records, append-only audit records, and trace reconstruction.
- [ICO assurance-case guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/explaining-decisions-made-with-artificial-intelligence/annexe-5-argument-based-assurance-cases/) and [AI safety-case construction work](https://arxiv.org/html/2601.22773v2): the right home for the new paper may be an assurance-case pattern rather than a standalone security taxonomy.

## Best First Form

Start with a 2,500--4,000 word position paper or policy memo.

This form fits the current evidence base. The benchmark paper can supply one concrete measurement layer, but the secure-delegation argument should not depend on the current pilot being settled. It should be a framework paper with a research agenda and evaluation architecture, not a new results paper.

## Working Titles

- **Secure Delegation: AI Security as Control of Machine Agency**
- **From Prompt Security to Secure Delegation**
- **Secure Delegation and the Evaluation of AI Control Failures**
- **The Delegation Problem in AI Security**

Best current title:

> **From Prompt Security to Secure Delegation**

It is broad enough for security readers and specific enough to avoid sounding like general AI governance.

## Core Thesis

Current AI-security language often treats failures as bad prompts, bad outputs, bad refusals, or bad agents. Those are surface descriptions. The common structure is delegated agency under uncertain control.

Secure delegation asks four questions:

1. Who or what is authorized to act through the system?
2. Which language, data, tools, or policies can change the system's authorized action?
3. What evidence shows that control was preserved or lost?
4. Who can audit, contest, or revise the delegation after the fact?

Adversarial pragmatics is one measurement layer inside this broader project: it tests whether delegated AI systems preserve control over what language they treat as authoritative instruction.

Formal claim:

> A delegated AI action is justified only if there is reviewable evidence of principal, delegate, action, authority source, scope, constraints, provenance, information-flow rights, persistence rights, tool-use license, non-delegable limits, and failure attribution.

## Contribution

The new paper should contribute a framework, not another benchmark.

Minimum contribution stack:

1. **Delegation frame:** AI-security failures are often failures of delegated agency, not only failures of content filtering or model obedience.
2. **Delegation stack:** user intent, system policy, instruction hierarchy, tool authority, data provenance, action rights, logging, adjudication, and institutional accountability.
3. **Failure taxonomy:** prompt injection, jailbreaks, over-refusal, under-refusal, tool misuse, scaffold failure, goal drift, policy ambiguity, and judge failure as control failures at different layers.
4. **Evidence standard:** secure delegation requires evidence about instruction status, authority, scope, action licensing, failure attribution, and auditability.
5. **Evaluation agenda:** benchmarks should test invariants across paraphrase, source movement, authority changes, tool surfaces, and evaluator prompts.
6. **Safety-case pattern:** a reusable claim/argument/evidence structure for showing that a task family in an environment remained within delegated authority.

## What This Paper Is Not

- Not a replacement for the benchmark paper.
- Not a theory of consciousness, understanding, or AI personhood.
- Not a general AGI governance essay.
- Not a prompt-injection survey.
- Not a claim that all AI security reduces to language.
- Not a claim that secure delegation is solved by adversarial pragmatics.
- Not a replacement for least privilege, access control, audit logging, or assurance cases.
- Not a frame broad enough to absorb every AI failure.

## Boundary Conditions

Not every AI-security failure is primarily a delegation failure. Clear non-core cases include ordinary factual hallucination in a no-tool chat setting, model capability shortfall without action rights, benchmark contamination, model extraction, infrastructure compromise, training-data privacy leakage, and generic availability failures.

These failures may affect delegated action downstream, but they become secure-delegation failures only when they alter authorized action, action evidence, or post-hoc accountability.

## Relationship To The Benchmark Paper

The benchmark paper becomes the concrete case study.

Use it like this:

> If secure delegation is the larger security problem, adversarial pragmatics supplies one measurement layer: the evaluation of language-mediated control under adversarial or ambiguous instruction conditions.

Do not use the benchmark paper like this:

> The pilot proves the secure-delegation framework.

The pilot does not have to bear that weight. The new paper can cite the benchmark as an artifact and use its taxonomy as an example of what a secure-delegation evaluation layer looks like.

## Load-Bearing Assumptions

| Assumption | What would make it false? | Design response |
| --- | --- | --- |
| "Secure delegation" is a useful higher-level frame. | It collapses into existing terms such as agent security, prompt injection, alignment, or access control without adding distinctions. | Define the added value narrowly: it links technical control, instruction authority, tool/action rights, and post-hoc audit. |
| The paper can be useful without new empirical results. | Reviewers/readers expect empirical validation and treat the framework as a slogan. | Publish first as a position paper, policy memo, or workshop paper with explicit research agenda and case mapping. |
| The benchmark paper can support the argument without overburdening it. | The current pilot weaknesses distract from the secure-delegation thesis. | Use the benchmark as an example of a measurement layer, not as proof of the framework. |
| AI-security readers will recognize the problem. | The framing sounds like philosophy or governance rather than security engineering. | Start from concrete security failures: prompt injection, tool misuse, authority spoofing, policy ambiguity, judge failure, and audit failure. |
| The framework has a distinctive action payoff. | It only renames familiar concerns. | Include a checklist of evaluation requirements that changes how a team designs tests, logs, policies, and adjudication. |

## Strongest Anti-Thesis

Secure delegation may be too broad to do technical work. It could become an umbrella phrase that makes prompt injection, agent security, access control, evaluation, and governance sound unified without yielding sharper tests or decisions.

The paper survives this objection only if it produces concrete discriminations:

- which control layer failed;
- what evidence would have detected the failure;
- which evaluation design would expose it;
- what audit trail would make responsibility assignable;
- what remains outside the secure-delegation frame.

## Proposed Outline

1. **The security problem has moved up a level**
   - Bad prompts and bad outputs are symptoms.
   - The harder problem is controlled delegation of action.
2. **What delegation adds**
   - Delegation is not just tool use.
   - It combines intention, authority, scope, action rights, evidence, and accountability.
3. **The delegation stack**
   - Principal or requester.
   - System and policy authority.
   - Model inference.
   - Tools and external services.
   - Data sources and retrieved content.
   - Persistent state and logs.
   - Evaluators and adjudicators.
4. **Delegation claims, arguments, and evidence**
   - Top-level claim: for task family T in environment E, system S acts only within delegated authority.
   - Subclaims for instruction status, authority priority, action scope, information flow, persistence, audit evidence, and evaluator validity.
5. **Failure modes**
   - Instruction capture.
   - Authority spoofing.
   - Scope drift.
   - Tool/action overreach.
   - Refusal/task conflation.
   - Scaffold failure.
   - Misreporting and audit failure.
   - Judge failure.
6. **Evidence for secure delegation**
   - Authority tracking.
   - Source provenance.
   - Action licensing.
   - Minimal-pair invariance.
   - Multi-axis outcomes.
   - Failure attribution.
   - Disagreement and adjudication.
7. **Adversarial pragmatics as one measurement layer**
   - Connect to the current benchmark paper.
   - Keep the claim modest.
8. **Research and policy agenda**
   - What benchmark designers should measure.
   - What system-card authors should report.
   - What red-teamers should separate.
   - What external assurance teams should ask for.

## Minimum Viable Draft

The first draft should be short and useful:

- 3,000 words;
- one delegation-stack figure;
- one table mapping common AI-security failures to delegation-layer failures;
- one table mapping delegation evidence to evaluation designs;
- one safety-case claim/subclaim box;
- one boundary-conditions box;
- one paragraph connecting to the adversarial-pragmatics benchmark;
- no new empirical claims beyond already published artifact facts.

## Near-Term Work While Waiting On The Judge

1. Draft the one-page thesis memo.
2. Build the two core tables.
3. Create a source-verification queue for secure-delegation background sources.
4. Decide target format: policy memo, workshop position paper, or full academic article.
5. Draft the delegation-stack figure.

## Decision Point

After the second judge returns, decide whether the next two weeks prioritize:

- **Benchmark v2 first:** use the judge feedback to repair the empirical paper, then write secure delegation from a stronger evidence base.
- **Secure-delegation memo first:** ship a short framework memo while the empirical paper moves more slowly.

Current recommendation:

> Draft the secure-delegation memo now, but do not submit or post it until the second-judge feedback shows whether the benchmark paper needs a major reframing.
