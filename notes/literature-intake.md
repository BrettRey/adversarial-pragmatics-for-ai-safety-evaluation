# Literature Intake

Date: 2026-06-26

Scope: first-pass intake for the adversarial-pragmatics benchmark. I checked the shared literature folder at `/Users/brettreynolds/Documents/LLM-CLI-projects/literature`, Mendeley Desktop holdings, and current online primary sources. The project-local repository does not currently have its own `literature/` directory.

## Working Map

| Cluster | Core sources | Core claim | Methodological role for this project | Status |
|---|---|---|---|---|
| Instruction authority and prompt injection | Wallace et al. (2024); Greshake et al. (2023); Debenedetti et al. (2024); Toyer et al. (2023) | LLMs are vulnerable when they treat trusted instructions, user text, third-party data, and tool outputs as if they had the same control status. | Provides the authority/source hierarchy part of the taxonomy and motivates untrusted-context minimal pairs. | verified from online primary sources; Greshake PDF also local |
| Safety refusal and jailbreak robustness | Mazeika et al. (2024); Chao et al. (2024); Röttger et al. (2023); Wang et al. (2023); Arditi et al. (2024) | Refusal behavior must be evaluated separately from general task ability because unsafe compliance, correct refusal, and exaggerated refusal are distinct outcomes. | Supports separate scoring axes for task success, policy compliance, safety risk, and over-refusal. | verified from online and local sources |
| LLM-as-judge and instruction-following evaluation | Zheng et al. (2023); Liu et al. (2023); Zeng et al. (2024); Zhou et al. (2023); Hu and Levy (2023) | LLM judging can scale evaluation, but judges are sensitive to prompts, domains, deceptive fluency, and the precise measurability of the instruction. | Supports algorithmic checks where possible and a separate validation protocol for LLM-as-judge behavior. | verified from online and local sources |
| Quotation, demonstration, and use/mention | Davidson (1979); Clark and Gerrig (1990); Recanati (2001); Maier (2014) | Quotation is not a single simple device for mentioning words: displayed linguistic material can be a demonstration, a closed singular term, an open quotation, mixed quotation, scare quote, or incorporated quotation. | Gives the construct basis for quoted-command, embedded-command, demonstrated-string, and use/mention minimal pairs. | downloaded and moved to shared literature |
| Disagreement and annotation validity | Artstein and Poesio (2008); Davani et al. (2022); Pavlick and Kwiatkowski (2019); Messick (1995); Moss (1994) | Some disagreement reflects unreliable annotation; some persists under more labels or more context and should be modeled as construct signal. | Supports confidence labels, criterion-conflict notes, adjudication notes, and disagreement-as-data rather than majority vote only. | ACL sources verified online; Messick/Moss local in Mendeley |

## Source-by-Source Notes

| Source | Intake claim | What to use | Confidence |
|---|---|---|---|
| Wallace et al. (2024), "The Instruction Hierarchy" | Prompt injection and jailbreak vulnerability partly arise because models fail to prioritize privileged instructions over lower-priority text. | Cite for explicit hierarchy among system/developer/user/tool or third-party content. | from paper abstract/page |
| Greshake et al. (2023), "Not What You've Signed Up For" | Indirect prompt injection exploits the blurred line between retrieved data and instructions in LLM-integrated applications. | Cite for untrusted retrieved text and tool-mediated instruction attacks. | from arXiv page and local PDF |
| Debenedetti et al. (2024), "AgentDojo" | Agent evaluation needs dynamic tasks, tools, untrusted data, attacks, and defenses rather than static prompt-only tests. | Cite for agentic/tool-output benchmark context. | from arXiv page |
| Toyer et al. (2023), "Tensor Trust" | Human-generated prompt-injection attacks show interpretable strategies for prompt extraction and prompt hijacking. | Cite as evidence that adversarial instruction forms are learnable and classifiable. | from arXiv page |
| Mazeika et al. (2024), "HarmBench" | Automated red-teaming evaluation needs standardized behaviors, scoring, attacks, targets, and defenses. | Cite for benchmark-standardization precedent. | from arXiv page |
| Chao et al. (2024), "JailbreakBench" | Jailbreak evaluation needs reproducible prompts, threat models, templates, scoring, and leaderboards. | Cite for reproducibility and attack-evaluation practice. | from arXiv page |
| Röttger et al. (2023), "XSTest" | Over-refusal on safe prompts is a measurable safety failure, not just harmless caution. | Cite for exaggerated safety behavior and safe/unsafe contrast sets. | from arXiv page |
| Wang et al. (2023), "Do-Not-Answer" | Safeguard evaluation can focus on instructions responsible models should not follow. | Cite for refusal-targeted safety datasets; do not copy unsafe examples into benchmark. | from arXiv page |
| Arditi et al. (2024), "Refusal in Language Models Is Mediated by a Single Direction" | Refusal can be manipulated separately from harmfulness/compliance, so refusal is not itself a sufficient safety measure. | Cite for separating refusal behavior from safety-risk scoring. | from local source |
| Zheng et al. (2023), "Judging LLM-as-a-Judge" | Strong LLMs can approximate human preferences in some settings, but this is an empirical claim that needs validation. | Cite as positive baseline for LLM judges. | from arXiv page |
| Liu et al. (2023), "G-Eval" | Form-based LLM evaluation can improve alignment with human NLG judgments but remains task- and prompt-dependent. | Cite as one LLM-evaluation method, not as blanket validation. | from ACL page |
| Zeng et al. (2024), "LLMBar" | LLM evaluators can be misled by outputs that look attractive while violating instructions. | Cite for adversarial meta-evaluation of judges. | from arXiv page |
| Zhou et al. (2023), "IFEval" | Verifiable instruction-following items enable objective and reproducible checks. | Cite for algorithmic-verification strategy. | from arXiv page |
| Hu and Levy (2023), "Prompting is not a substitute for probability measurements" | Elicited metalinguistic judgments are not interchangeable with model probabilities. | Cite as caution against assuming prompted judgments reveal underlying competence. | from local source |
| Davidson (1979), "Quotation" | Quotation should be analyzed partly through demonstration/pointing to displayed tokens, and mixed use/mention cases defeat a simple quoted-vs-used split. | Cite for use/mention and demonstrative theory. | from local PDF/Markdown |
| Clark and Gerrig (1990), "Quotations as Demonstrations" | Quotations are demonstrations: nonserious, selective depictions that can be component or concurrent with ordinary language use. | Cite for displayed-string and demonstrated-command distinctions. | from local PDF/Markdown |
| Recanati (2001), "Open Quotation" | Open quotation is pragmatically central and cannot be collapsed into closed quotation or mere scare quotes. | Cite for open/closed and mixed-quotation distinctions. | from local PDF/Markdown |
| Maier (2014), "Pure Quotation" | Formal theories of pure quotation trade off compositionality, productivity, opacity, and recursivity. | Cite for formal taxonomy of pure quotation accounts. | from local PDF/Markdown |
| Artstein and Poesio (2008), "Inter-Coder Agreement for Computational Linguistics" | Agreement measures encode assumptions about coders, categories, and chance correction. | Cite for annotation reliability methods. | from ACL page |
| Davani et al. (2022), "Looking Beyond the Majority Vote" | Majority vote can hide systematic annotator differences in subjective tasks. | Cite for modeling disagreement instead of suppressing it. | from ACL page |
| Pavlick and Kwiatkowski (2019), "Inherent Disagreements in Human Textual Inferences" | Some NLI disagreements persist with more ratings and more context and should be captured by evaluation. | Cite for disagreement-as-construct-signal. | from ACL page |

## Contradiction and Tension Map

| Tension | Source side A | Source side B | Project decision |
|---|---|---|---|
| Authority failure vs pragmatic ambiguity | Instruction-hierarchy and prompt-injection papers frame the problem as conflict among privileged and untrusted instructions. | Quotation/pragmatics papers show that the same string can be displayed, demonstrated, incorporated, reported, or commanded. | Benchmark items should cross source authority with string status: trusted command, untrusted command, quoted command, demonstrated string, and mixed quotation. |
| Refusal as success vs refusal as failure | HarmBench, JailbreakBench, and Do-Not-Answer emphasize correct refusal for harmful requests. | XSTest and Arditi et al. show over-refusal and refusal-direction manipulation as distinct phenomena. | Scoring must not collapse "refused" into "safe"; code separate outcome fields. |
| Scalable judge vs validated judge | MT-Bench and G-Eval show practical value for LLM-as-judge workflows. | LLMBar and Hu/Levy show that prompted judgments can fail on instruction-following and metalinguistic distinctions. | Use LLM judges only as measured systems; include judge-validation items in the benchmark. |
| Majority-vote gold labels vs disagreement as data | Artstein and Poesio support principled agreement measurement. | Davani et al. and Pavlick/Kwiatkowski show systematic/persistent disagreement. | Annotation protocol should record confidence, evaluation criterion, and disagreement type before adjudication. |

## Benchmark Implications

1. Build minimal pairs that vary only one control dimension at a time: authority source, quotation status, embeddedness, policy category, or transcript attribution.
2. Use harmless payloads for conflict tests: colors, tokens, dummy secrets, formatting constraints, and fictional tool calls.
3. Keep at least five independent score fields: task success, instruction-source compliance, policy compliance, safety risk, and evaluator confidence.
4. Add explicit item tags for `quoted`, `demonstrated`, `incorporated`, `indirect`, `untrusted-context`, `policy-ambiguous`, `over-refusal-risk`, and `judge-validation`.
5. Treat disagreement as an observation. Use majority labels only after recording whether the disagreement came from ambiguity, policy uncertainty, criterion conflict, or annotation error.

## Remaining Access Needs

No urgent library-access PDFs remain from this pass.

The previous quotation access gap is closed; these files are now in the shared literature folder:

| Source | DOI | Local file |
|---|---|---|
| Davidson (1979), "Quotation" | `10.1007/BF00126690` | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/BF00126690.pdf` |
| Clark and Gerrig (1990), "Quotations as Demonstrations" | `10.2307/414729` | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Clark-QuotationsDemonstrations-1990.pdf` |
| Recanati (2001), "Open Quotation" | `10.1093/mind/110.439.637` | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Recanati-OpenQuotation-2001.pdf` |
| Maier (2014), "Pure Quotation" | `10.1111/phc3.12149` | `/Users/brettreynolds/Documents/LLM-CLI-projects/literature/Philosophy Compass - 2014 - Maier - Pure Quotation.pdf` |

Likely next downloads, if we want local PDFs rather than online copies, are the ACL/arXiv sources for annotation disagreement, instruction hierarchy, AgentDojo, Tensor Trust, LLMBar, IFEval, HarmBench, JailbreakBench, XSTest, and Do-Not-Answer. They do not require library access based on the checked source pages.
