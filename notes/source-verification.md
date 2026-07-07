# Source Verification Queue

Do not cite these claims until the linked source has been read and the claim below has been checked. The setup prompt supplied the links and summaries; this file records what to verify.

| ID | Source | Claim to verify | Status |
|----|--------|-----------------|--------|
| S01 | https://doi.org/10.48550/arXiv.2510.15236 | Brett's AGI evaluation paper argues against snapshot scores and proposes centrality/stability-based evaluation profiles. | queued |
| S02 | https://brettreynolds.ca/publications.html | Public profile includes work on expert grammaticality judges, stable diagnostic ambiguity, CGELBank/CGEL annotation, LLM boundary phenomena, truth-tracking profiles, and category/kind theory. | queued |
| S03 | https://www.aisi.gov.uk/research-agenda | AISI research agenda emphasizes Science of Evaluations and rigorous methods for measuring frontier AI capabilities; autonomous systems and human influence are risk areas. | queued |
| S04 | https://openai.com/careers/model-policy-san-francisco/ | OpenAI Model Policy role mentions policy taxonomies, evaluation criteria, grading guidance, gold-set construction, labeling calibration, over-refusals, under-refusals, and ambiguous edge cases. | queued |
| S05 | https://openai.com/careers/researcher-trustworthy-ai-san-francisco/ | OpenAI Trustworthy AI role frames work as turning nebulous policy problems into tractable measurable ones. | queued |
| S06 | https://job-boards.greenhouse.io/scaleai/jobs/4677657005 | Scale Frontier Risk Evaluations role asks for evaluation measures, harnesses, datasets, and technical reports for policymakers. | queued |
| S07 | https://www.anthropic.com/careers/jobs/4949336008 | Anthropic safeguards role mentions multi-exchange harms, influence operations, agentic products, prompt injection, automated red-teaming, and adversarial robustness. | queued |
| S08 | https://www.aisi.gov.uk/blog/transcript-analysis-for-ai-agent-evaluations | AISI argues that aggregate pass rates flatten transcript-level failure distinctions such as refusal, tool-use problems, scaffold noncompliance, misreporting, omitted information, or failure to elicit capabilities. | queued |
| S09 | https://www.aisi.gov.uk/blog/llm-judges-on-trial-a-new-statistical-framework-to-assess-autograders | AISI highlights the need to evaluate LLM autograders and systematic biases in LLM judges. | queued |
| S10 | https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026 | 2026 International AI Safety Report says AI agents create heightened reliability risks because autonomous actions leave fewer intervention opportunities. | queued |
| S11 | https://job-boards.greenhouse.io/anthropic/jobs/5208278008 | Anthropic external-artifacts role includes catching terminology drift, contradictions among risk claims, and gaps between findings and public documents. | queued |
| S12 | https://philarchive.org/rec/REYLAB | Brett's LLM boundary phenomena paper argues that LLMs expose ambiguities in cluster concepts like language and cognition. | queued |

## Verified Literature Sources

Checked 2026-06-26 for use in the literature review, benchmark design, and citation queue.

| ID | Source | Verified claim | Status |
|----|--------|----------------|--------|
| L01 | https://arxiv.org/abs/2404.13208 | Wallace et al. introduce an instruction hierarchy for conflicts among privileged and lower-priority instructions, with data generation to train selective ignoring of lower-privileged instructions. | verified 2026-06-26; paper/background |
| L02 | https://arxiv.org/abs/2302.12173 and https://doi.org/10.1145/3605764.3623985 | Greshake et al. define indirect prompt injection as attacks through data retrieved or processed by LLM-integrated applications; the ACM DOI is `10.1145/3605764.3623985`, and a local PDF exists at `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/greshake2023not.pdf`. | verified 2026-06-26; paper/background |
| L03 | https://arxiv.org/abs/2406.13352 | AgentDojo evaluates LLM agents executing tools over untrusted data, with realistic tasks, security test cases, attacks, and defenses. | verified 2026-06-26; paper/background |
| L04 | https://arxiv.org/abs/2311.01011 | Tensor Trust provides a large human-generated dataset of prompt-injection attacks and defenses, including prompt extraction and prompt hijacking. | verified 2026-06-26; paper/background |
| L05 | https://arxiv.org/abs/2402.04249 | HarmBench is a standardized framework for automated red-teaming and robust refusal, comparing attacks, target models, and defenses. | verified 2026-06-26; paper/background |
| L06 | https://arxiv.org/abs/2404.01318 | JailbreakBench provides an open benchmark with jailbreak artifacts, behaviors, threat model, system prompts, templates, scoring functions, and a leaderboard. | verified 2026-06-26; paper/background |
| L07 | https://arxiv.org/abs/2308.01263 | XSTest targets exaggerated safety behavior by contrasting safe prompts that should not be refused with unsafe prompts that should be refused. | verified 2026-06-26; paper/background |
| L08 | https://arxiv.org/abs/2308.13387 | Do-Not-Answer is an open dataset of instructions that responsible models should not follow, with response annotation and safety-evaluation classifiers. | verified 2026-06-26; paper/background |
| L09 | https://arxiv.org/abs/2306.05685 | Zheng et al. present MT-Bench and Chatbot Arena, arguing that LLM-as-judge can approximate human preferences in model evaluation settings while providing public benchmark data. | verified 2026-06-26; paper/background |
| L10 | https://aclanthology.org/2023.emnlp-main.153/ | G-Eval uses GPT-4 with chain-of-thought and form filling to evaluate NLG quality and reports better human alignment than prior reference-free LLM evaluators in tested settings. | verified 2026-06-26; paper/background |
| L11 | https://arxiv.org/abs/2310.07641 | LLMBar is a meta-evaluation benchmark for LLM evaluators on instruction-following outputs, including deceptively attractive but instruction-violating responses. | verified 2026-06-26; paper/background |
| L12 | https://arxiv.org/abs/2311.07911 | IFEval uses objectively verifiable instruction types to make instruction-following evaluation reproducible and less dependent on human or LLM judgment. | verified 2026-06-26; paper/background |
| L13 | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/BF00126690.pdf` | Davidson's "Quotation" argues against proper-name and spelling accounts of quotation and develops a demonstrative account in which quotation marks point to displayed tokens. DOI: `10.1007/BF00126690`. | verified 2026-06-26; paper |
| L14 | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Clark-QuotationsDemonstrations-1990.pdf` | Clark and Gerrig argue that quotations are demonstrations: selective, nonserious depictions that can be embedded in or concurrent with ordinary language use. DOI: `10.2307/414729`. | verified 2026-06-26; paper |
| L15 | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Recanati-OpenQuotation-2001.pdf` | Recanati distinguishes open from closed quotation and argues that ignoring open quotation confuses syntactico-semantic status with the pragmatic point of the demonstration. DOI: `10.1093/mind/110.439.637`. | verified 2026-06-26; paper |
| L16 | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Philosophy Compass - 2014 - Maier - Pure Quotation.pdf` | Maier compares proper-name, description, demonstrative, and disquotational theories of pure quotation against compositionality, productivity, recursivity, and opacity. DOI: `10.1111/phc3.12149`. | verified 2026-06-26; paper |
| L17 | https://aclanthology.org/J08-4004/ | Artstein and Poesio survey inter-coder agreement methods for computational linguistics and list DOI `10.1162/coli.07-034-R2`. | verified 2026-06-26; paper/method |
| L18 | https://aclanthology.org/2022.tacl-1.6/ | Davani, Díaz, and Prabhakaran argue that majority vote can suppress systematic annotator differences in subjective annotation tasks. | verified 2026-06-26; paper/method |
| L19 | https://aclanthology.org/Q19-1043/ | Pavlick and Kwiatkowski show that some human NLI disagreements persist with more ratings and context; DOI `10.1162/tacl_a_00293`. | verified 2026-06-26; paper/method |
| L20 | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/arditi2024refusal.md` | Arditi et al. report that a one-dimensional refusal direction can be ablated to reduce refusal on harmful instructions or added to elicit refusal on harmless instructions, supporting separate scoring of refusal behaviour and request safety. | verified 2026-06-26; paper/background |
| L21 | `/Users/brettreynolds/Documents/LLM-CLI-projects/papers/preprints/kinds-as-projectibility-profiles/main.tex`; https://philarchive.org/rec/REYKAP-2 | Reynolds frames kinds as projectibility profiles and gives support grades and demotion rules for categories whose projected inferences fail. | verified 2026-06-26; paper/method |
| L22 | https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ | OWASP's Agentic AI threat guide frames agentic AI security as threat-model-based guidance for autonomous systems whose LLM integration expands scale, capability, and risk. | verified 2026-07-07; secure-delegation background |
| L23 | https://www.nist.gov/news-events/news/2026/01/caisi-issues-request-information-about-securing-ai-agent-systems | NIST/CAISI's 2026 RFI focuses on security risks of AI agent systems that plan and act in real-world environments, including adversarial data, model outputs combined with software functionality, access constraints, monitoring, and measuring agent security. | verified 2026-07-07; secure-delegation background |
| L24 | https://arxiv.org/abs/2504.19956 | Narajala and Narayan argue that GenAI agents need threat modeling tailored to autonomy, memory, reasoning, and tool integration, organized across agent-specific threat domains and mitigation frameworks. | verified 2026-07-07; secure-delegation background |
| L25 | https://arxiv.org/html/2603.11088v1 | "The Attack and Defense Landscape of Agentic AI" surveys agentic AI security from a systems perspective, mapping design dimensions, attack categories, defenses, and open challenges; this confirms the general agent-security survey space is already crowded. | verified 2026-07-07; secure-delegation background |
| L26 | https://arxiv.org/html/2501.09674v1 | South et al. propose authenticated, authorized, and auditable delegation for AI agents by extending OAuth/OpenID-style identity and access-management infrastructure with agent-specific credentials, scoped permissions, accountability chains, and natural-language permission translation. | verified 2026-07-07; secure-delegation background |
| L27 | https://datatracker.ietf.org/doc/draft-kuehlewind-audit-architecture/ | The IETF draft proposes architecture for auditing AI-agent delegation and interactions, including AI-agent delegation audit records, delegated principal identity, authorization transition records, append-only audit records, and trace reconstruction. | verified 2026-07-07; secure-delegation background |
| L28 | https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/explaining-decisions-made-with-artificial-intelligence/annexe-5-argument-based-assurance-cases/ | ICO's guidance presents argument-based assurance cases as structured claims, arguments, and evidence for showing that a system has a property in a given context. | verified 2026-07-07; secure-delegation assurance background |
| L29 | https://arxiv.org/html/2601.22773v2 | "A Structured Approach to Safety Case Construction for AI Systems" frames AI safety cases around claim/argument/evidence structures, evidence taxonomies, reusable templates, operational context, and evolving model behavior. | verified 2026-07-07; secure-delegation assurance background |
| L30 | https://arxiv.org/abs/2411.15594 | Gu et al.'s LLM-as-a-Judge survey treats judge reliability as an open problem requiring attention to consistency, bias mitigation, domain adaptation, and reliability-evaluation methods. | verified 2026-07-07; secure-delegation judge-validation background |
| L31 | https://aclanthology.org/2024.emnlp-main.474/ | Chen et al. show that human and LLM judges are vulnerable to judgment biases and that those biases can be exploited in attacks, supporting the secure-delegation paper's treatment of evaluator failure as part of the assurance problem. | verified 2026-07-07; secure-delegation judge-validation background |
| L32 | https://www.nist.gov/artificial-intelligence/ai-agent-standards-initiative | NIST's AI Agent Standards Initiative frames AI agents as autonomous task-performing systems and emphasizes risks around access, measurement, monitoring, and standards for agent security. | verified 2026-07-07; secure-delegation background |

## Verification Rule

When a source is checked, add:

- date checked;
- exact page or section if available;
- one-sentence verified claim;
- whether it belongs in the paper, project memo, or strategic positioning notes only.
