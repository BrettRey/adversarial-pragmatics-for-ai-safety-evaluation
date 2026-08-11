# Rival benchmarks 2025–26: comparator-table audit

For `adversarial-pragmatics-for-ai-safety-evaluation` (arXiv:2607.01153, v1 submitted 2026-07-01, now at v3).
Compiled 2026-08-08.

## Verification status (read this first)

- Every entry below carries an arXiv ID and an abstract retrieved from a live API or page. **Nothing here is from memory.**
- Sources actually fetched: `api.semanticscholar.org/graph/v1/paper/...` (citations endpoint and `/batch` POST endpoint), and `https://arxiv.org/abs/<id>` fetched directly with curl for the seven top candidates plus three others, with the abstract extracted from the page's `<blockquote class="abstract">` block.
- **Caveat, and it matters for the table:** I read *abstracts*, not full papers. The manuscript's Table 1 caption promises "entries are read from each paper." My column scores below are **provisional readings from abstracts** and must be re-derived from full text before any of them goes into the table. I have flagged each score as provisional.
- The failed fetch: `http://export.arxiv.org/api/query?id_list=2510.03485` returned zero bytes (blocked or refused in this sandbox). I substituted the `arxiv.org/abs/` page and the Semantic Scholar record, which agree.
- One discrepancy worth noting: Semantic Scholar's title for arXiv:2510.03485 is **"Learning Efficient Guardrails for Compliance"**, while arXiv's own page and every other source give **"Towards Policy-Compliant Agents: Learning Efficient Guardrails For Policy Violation Detection"**. Use the arXiv title.

## The seven columns, restated

From `sections/02-pass-fail.tex`, Table `tab:comparators`:
(a) task success scored apart from policy/safety compliance; (b) source role and pragmatic status both annotated; (c) expected behaviour adjudicated independently of the item author; (d) grader/judge error itself measured; (e) nuisance or placebo transformations; (f) transcript-level failure attribution; (g) an item may stay unresolved.

Manuscript scores itself: `Y Y N Y N P Y`.

**None of the candidates below is currently cited.** I grepped `references.bib`, `references-local.bib`, `sections/`, and the top-level `.tex` files for all twenty candidate names. The only hit was a substring false positive on "WIRE"; a word-boundary grep returns nothing.

---

# TIER 1 — must be in the table or the revision fails review

## 1. AgentAtlas (arXiv:2605.20530) — the most dangerous omission

<https://arxiv.org/abs/2605.20530> · Parsa Mazaheri, Kasra Mazaheri · 2026-05-19 · preprint

> "Large language model agents now act on codebases, browsers, operating systems, calendars, files, and tool ecosystems, but their evaluations often collapse behavior into final task success. AgentAtlas reframes agent evaluation as a diagnostic vocabulary and audit protocol for separating outcome success from control-decision quality and trajectory quality. The paper contributes: (i) a six-state control-decision taxonomy (Act / Ask / Refuse / Stop / Confirm / Recover); (ii) a trajectory-failure vocabulary with primary error source and downstream impact; (iii) a 0/1/2 benchmark-coverage audit over fifteen agent benchmarks; and (iv) an illustrative protocol study on a synthetic 1,342-item set evaluated with eight models under taxonomy-aware and taxonomy-blind prompt formats. The synthetic demonstration is not a public benchmark release and should not be read as a definitive model comparison. Instead, it illustrates two measurement risks: mapped label agreement can change substantially when the explicit label menu is removed, and axis choice can change apparent rankings. AgentAtlas is intended to help benchmark designers state what behavior they cover, and to help evaluators diagnose failures that outcome-only leaderboards hide."

**Construct:** pragmatic-adjacent and structurally identical in purpose. Refusal is one of six control states, so refusal appropriateness is native. The trajectory-failure vocabulary with "primary error source and downstream impact" is failure attribution. The taxonomy-aware/taxonomy-blind contrast is a measurement of the annotation protocol's own instability, i.e. a version of column (d).

**Threat:** severe, and to the *table itself*, not to a cell. AgentAtlas performs a 0/1/2 coverage audit over fifteen agent benchmarks. The manuscript performs a Y/P/N coverage audit over six. A reviewer will ask why the paper built a coverage audit without citing the coverage audit that ran three months earlier over 2.5× the benchmarks, and whether the manuscript's six are a subset of AgentAtlas's fifteen.

**Mitigation available:** AgentAtlas is a two-author preprint with a synthetic item set and explicitly disclaims being a benchmark release. It is a vocabulary paper, not a measurement instrument. The manuscript can cite it as independent convergence on the diagnosis while claiming the executed artifact. But it must be cited.

Provisional scores: (a) Y, (b) P, (c) N, (d) P, (e) N, (f) Y, (g) P.

## 2. IH-Benchmark (arXiv:2607.25987) — the IHEval successor

<https://arxiv.org/abs/2607.25987> · Conor McCauley, Zeliang Kan, Jason Martin · 2026-07-28

> "…We present IH-Benchmark, a conflict-centered benchmark for instruction-hierarchy robustness across direct system-user conflicts (S>U) and tool-mediated user-tool (U>T) conflicts. IH-Benchmark is built from a human-authored taxonomy of 44 constraint families across generic, health, finance, retail, and coding settings, and evaluates scenarios with a uniform binary pass/fail protocol combining a predicate DSL with category-scoped LLM judges. Across 37 evaluated models, hierarchy compliance ranges from 98.2% to 20.5%. We find that strong S>U compliance is not a reliable proxy for U>T robustness… These results suggest that instruction-hierarchy robustness is not a single capability, but a set of behaviors that must be evaluated across conflict surfaces, constraint types, and attack presentations."

**Construct:** instruction conflict and source authority, directly. Not use-mention.

**Threat:** the table cites IHEval (2025). This is the 2026 IHEval successor, larger on every axis, and its closing sentence ("not a single capability, but a set of behaviors") is a compressed version of the manuscript's own multidimensionality thesis. Leaving it out while claiming the IHEval row is the single most predictable "missing citation" note.

**But it is also a gift.** It is explicitly "a uniform binary pass/fail protocol," which is column (g) = N, and its expected behaviours come from its own authors' taxonomy, which is (c) = N. It is a comparator that makes the manuscript's point.

Provisional scores: (a) P, (b) P, (c) P, (d) N, (e) N, (f) N, (g) N.

## 3. Same Payload, Different Channel / Safety Asymmetry Score (arXiv:2606.00566) — the methodological rival

<https://arxiv.org/abs/2606.00566> · Mohammed Sameer Syed, Rozhin Yasaei · 2026-05-30

> "…We introduce the Safety Asymmetry Score (SAS), which measures how much a model's susceptibility to adversarial content shifts depending on whether that content arrives in the user message, tool metadata, or tool output, **using matched payload pairs that keep the malicious text identical and vary only the context of delivery.** Evaluated across 6 production LLMs and three attack families, we find a consistent and informative asymmetry: agent-native models are substantially more vulnerable when adversarial content arrives via tool descriptions than via user messages, while general-purpose models show the reverse. This asymmetry further inverts when the same content is delivered through tool outputs rather than descriptions, suggesting models implicitly treat tool metadata as trusted instructions and tool results as ordinary data…"

(emphasis mine)

**Construct:** source authority, measured by minimal pairs. This is the manuscript's "instruction-source sensitivity" metric under a different name, with a published metric attached to it.

**Threat: the worst of the three on a per-column basis.** The manuscript scores itself **N on (e)** and says in §02 that nuisance and placebo transformations are one of "the two gaps Study A and Study B exist to close." Matched payload pairs that hold the string constant and vary only delivery channel *are* the controlled-transformation design. A reviewer can say the manuscript's declared future work already exists, published two months before v1, and comes with a scalar score. It also lands squarely on (b)'s source-role half.

What it does **not** do: pragmatic status. Nothing here is about use vs mention, or quoted vs commanded. The payload is malicious in every condition; only the channel moves. That is the manuscript's opening.

Provisional scores: (a) N, (b) P, (c) N, (d) N, (e) Y, (f) N, (g) N.

## 4. PolicyGuardBench / PolicyGuard (arXiv:2510.03485) — the one you asked about

<https://arxiv.org/abs/2510.03485> · Xiaofei Wen, Wenjie Jacky Mo, Yanan Xie, Peng Qi, Muhao Chen · v1 2025-10-03, v2 2026-05-18 · **accepted ICML 2026** (comments field: "16 pages, 5 figures. Accepted by ICML 2026")

Full title: *Towards Policy-Compliant Agents: Learning Efficient Guardrails For Policy Violation Detection*. Model card: <https://huggingface.co/Rakancorle1/PolicyGuard-4B>. OpenReview: <https://openreview.net/forum?id=7zuhQWJIqX>.

> "Autonomous web agents are increasingly deployed for long-horizon tasks, yet their ability to adhere to real-world policies remains critically underexplored compared to standard safety objectives. To address this gap, we introduce PolicyGuardBench, a benchmark of 60k policy-trajectory pairs designed to evaluate compliance through both full-trajectory and novel prefix-based violation detection tasks. Using this dataset, we train PolicyGuard, a lightweight guardrail model that achieves strong detection accuracy while maintaining high inference efficiency. Notably, our model demonstrates robust generalization capabilities, preserving high performance even on unseen domains. These contributions establish a comprehensive framework for studying policy compliance, showing that accurate and generalizable guardrails are feasible at small scales."

**Verdict on the construct: this is policy-violation-detection work, not pragmatics.** No instruction conflict, no use-mention, no source authority, no over-refusal, no judge-error measurement, no unresolved category. It is a labelled corpus for training and scoring a *classifier* that reads a trajectory (or a prefix of one) and emits a violation label.

**It strengthens the manuscript, and I'd argue for a table row precisely because of that.** It is 60k items, ICML 2026, and by my provisional reading it scores N on every one of the seven columns. That is the concrete form of §02's argument that "the advantage claimed here isn't scale." Right now the largest comparator in the table is Tensor Trust, which scores relatively well; adding the largest and newest one, which scores all-N, makes the diagnostic-resolution claim considerably harder to dismiss as special pleading.

Provisional scores: (a) N, (b) N, (c) N, (d) N, (e) N, (f) N, (g) N. **Verify against the full paper before publishing an all-N row** — an all-N row is a strong claim and an easy thing to be wrong about.

## 5. Failure attribution: Who&When Pro (arXiv:2607.09996) and MP-Bench (arXiv:2603.25001)

The manuscript scores itself **P on (f)** and treats transcript-level failure attribution as thinly covered. Since early 2025 this has become a named subfield with at least six benchmarks. Claiming (f) without engaging it will not survive an agents reviewer.

**Who&When Pro** <https://arxiv.org/abs/2607.09996> · Jiale Liu, Huajun Xi, Shaokun Zhang, Yifan Zeng, Tianwei Yue, Chi Wang, Jian Kang, Qingyun Wu, Huazheng Wang · 2026-07-10

> "Automated failure attribution uses LLMs to identify where and why agentic systems fail. As agents become more capable, their failures become subtler, making automated attribution increasingly important. We introduce Who&When Pro, a large-scale benchmark for automated failure attribution in agentic systems. Using a strictly controlled pipeline that injects a failure only after exactly replaying a successful prefix, we construct 12,326 failed trajectories with golden labels across 3 modalities and 26 benchmarks covering various scenarios…"

The predecessor, Who&When (*Which Agent Causes Task Failures and When?*), was an **ICML 2025 spotlight** — <https://github.com/ag2ai/Agents_Failure_Attribution>, <https://openreview.net/forum?id=GazlTYxZss>. Best method reported 53.5% agent-identification accuracy and 14.2% step-identification accuracy.

**MP-Bench** <https://arxiv.org/abs/2603.25001> — *Rethinking Failure Attribution in Multi-Agent Systems: A Multi-Perspective Benchmark and Evaluation*, 2026

> "…existing benchmarks and methods largely assume a single deterministic root cause for each failure. In practice, MAS failures often admit multiple plausible attributions due to complex inter-agent dependencies and ambiguous execution trajectories. We revisit MAS failure attribution from a multi-perspective standpoint and propose multi-perspective failure attribution, a practical paradigm that explicitly accounts for attribution ambiguity. To support this setting, we introduce MP-Bench, the first benchmark designed for multi-perspective failure attribution in MAS… we find that prior conclusions suggesting LLMs struggle with failure attribution are largely driven by limitations in existing benchmark designs."

**MP-Bench is the threat to column (g), not just (f).** "Explicitly accounts for attribution ambiguity" is the manuscript's "an item may stay unresolved" applied to attribution, and it is called "the first benchmark designed for" it. If the manuscript claims (g) as near-unique, this contests it directly. Its closing claim — that earlier negative findings were benchmark artifacts — is also the kind of sentence a reviewer will quote back.

Also in this cluster, all verified via S2 `/batch`:
- **TraceElephant** (arXiv:2604.22708, ACL 2026): full-execution-trace observability; "full traces improve attribution accuracy by up to 76% over a partial-observation counterpart."
- **TELBench + DRIFT** (arXiv:2606.02060): span-level error localisation over 2,790 real deep-research trajectories; annotation distinguishes "harmful error spans" from "normal exploration, failed searches, tentative hypotheses, and harmless noise" — a nuisance-vs-signal distinction the manuscript would recognise.
- **AgenTracer / AgenTracer-8B** (arXiv:2509.03312): "counterfactual replay and programmed fault injection."
- **StepFinder** (arXiv:2606.03467, KDD 2026).

---

# TIER 1.5 — not a table row, but the single most important citation to add

## Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks (arXiv:2607.28685)

<https://arxiv.org/abs/2607.28685> · Youting Wang, Xiao Han, Dingyan Shang, Yuan Tang, Bowen Liu · 2026-07-30

> "Agent-safety benchmarks measure different behaviors, and their scores get quoted interchangeably as an agent's safety. We treat four of them (R-Judge, InjecAgent, AgentHarm, AgentDojo) as measurements to be validated, running each under its official implementation and author-provided scorer on up to 22 models, with MMLU and GPQA measured by us under one protocol as a capability composite. The metric is the first problem. On any binary trace-judgment benchmark scored by $F_1$, an ``always positive'' policy attains $F_1 = 2\pi/(1+\pi)$; on R-Judge that is $0.690$, above five of the 21 models that actually discriminate. The three broad-coverage benchmarks then rank the same 18 models differently… Capability predicts task success ($\rho{=}{+}0.60$) but correlates negatively with misalignment safety ($\rho{=}{-}0.44$, $n{=}21$)… Naming the benchmark, metric, target behavior, and model panel is the minimum a safety claim needs."

**Why this is the one.** The manuscript's governing commitment (per `CLAUDE.md` and §02) is that validity is a property of an assessment-result interpretation and use, not of a benchmark. This paper executes that thesis quantitatively, on **two of the manuscript's own six comparators** (InjecAgent, AgentDojo), and lands on the same prescription in its last sentence. It appeared 29 days after v1.

**Threat:** it is where a JAIR reviewer drawn from this area will most plausibly be sourced, and its absence is the kind of gap that reads as "the author isn't tracking the field." It is not a rival benchmark, so it costs the manuscript no novelty — but it substantially upgrades §02's empirical warrant, which currently leans on `haimes2024benchmarkInflation` and `dehghani2021benchmarkLottery` from 2024 and 2021. Cite it in §02 alongside the BetterBench/retro-holdout paragraph.

Adjacent, same genre, all verified:
- **How should AI Safety Benchmarks Benchmark Safety?** (arXiv:2601.23112): "a review of 210 safety benchmarks," arguing for "efficiently deploying measurement theory to connect benchmarking objectives with the world." Direct support for the validity framing; also a competing statement of it.
- **Talk is (Not) Cheap** (arXiv:2605.15118): a 4×6 STRIDE-grounded Target × Technique matrix from a 507-leaf taxonomy over 932 arXiv security studies; applied to six public benchmarks it finds "HarmBench, InjecAgent, AgentDojo occupy non-overlapping cells covering at most 25% of the matrix." A competing coverage-audit method with released extensible artifacts, over an overlapping benchmark set.
- **Who Tests the Testers? / SafeAudit** (arXiv:2603.18245): meta-audit finding ">20% residual unsafe behaviors that existing benchmarks fail to expose."
- **Chasing Shadows: Pitfalls in LLM Security Research** (arXiv:2512.09549, NDSS): nine pitfalls across 72 peer-reviewed security papers; "every paper contains at least one pitfall… only 15.7% of the present pitfalls were explicitly discussed."

---

# TIER 2 — cite, don't tabulate

## Instruction hierarchy / privilege conflict

| ID | Name | Why it matters | Table risk |
|---|---|---|---|
| [2604.09443](https://arxiv.org/abs/2604.09443) | **ManyIH-Bench** (Zhang, Li, Jurayj, Zhan, Van Durme, Khashabi) | "up to 12 levels of conflicting instructions," 853 agentic tasks, 46 real-world agents; frontier models ~40%. Explicitly attacks IH's "fixed, small set of privilege levels (typically fewer than five)." | Extends authority far past the manuscript's source contrasts. Cite in §03. |
| [2502.15851](https://arxiv.org/abs/2502.15851) | **Control Illusion** (AAAI 2025) | "societal hierarchy framings (e.g., authority, expertise, consensus) show stronger influence on model behavior than system/user roles, suggesting that pretraining-derived social structures function as latent behavioral priors." | **This is a pragmatics result inside an IH paper, from 2025.** Its absence is conspicuous for a paper about language-mediated authority. |
| [2511.14342](https://arxiv.org/abs/2511.14342) | **ConInstruct** (AAAI 2026) | Conflict detection *and* resolution within one instruction. Key finding: "Despite their strong conflict detection abilities, LLMs rarely explicitly notify users about the conflicts or request clarification." | Directly relevant to the unresolved/ask-for-clarification behaviour the manuscript's (g) column implies. |
| [2606.07808](https://arxiv.org/abs/2606.07808) | **Where Instruction Hierarchy Breaks** | Decomposes IH non-compliance into "instruction identification, conflict resolution, and response realization" — a failure-attribution taxonomy *for the IH construct specifically*. | Closest thing to the manuscript's attribution categories applied to instruction conflict. |
| [2605.27784](https://arxiv.org/abs/2605.27784) | **WIRE** (Yan, Chen, Zhang) | Four-cell resolution profile (both / earlier only / later only / neither) over 13,335 trials; "only 35.4% satisfy both governed rules." And: "WIRE is not a proof of natural-language contradiction, a deployment-frequency estimator, or a root-cause diagnosis." | A **methodological ally**: non-binary outcome space plus explicit claim-typing discipline, which is the manuscript's own house rule. Cite as precedent, not rival. |
| [2607.23545](https://arxiv.org/abs/2607.23545) | **XIH-Bench** | Multilingual IH; "Language Boundary Effect" — cross-language conflicts yield higher compliance than same-language. | A nuisance-variable result the manuscript's design does not control for. |
| [2603.15527](https://arxiv.org/abs/2603.15527) | **Priority Graph** | Models conflict resolution as a context-dependent priority graph; names "priority hacking." | Conceptual, not a benchmark. |
| [2511.04694](https://arxiv.org/abs/2511.04694) | **VerIH** (ACL 2025) | IH resolution as a reasoning task; training data. | Method paper. Low threat. |

## Prompt injection with agent trajectories / source authority

| ID | Name | Why it matters |
|---|---|---|
| [2603.12277](https://arxiv.org/abs/2603.12277) | **Prompt Injection as Role Confusion** (Ye, Cui, **Hadfield-Menell**) | "models perceive the source of text from how it sounds, not its labeled role… To the model, sounding like a role is indistinguishable from being one." **This is the manuscript's central pragmatic claim, stated in one sentence, with representational evidence and a 60%-ASR attack (CoT Forgery) behind it.** Strongest conceptual corroboration available; also the most quotable rival framing. MIT authorship makes omission conspicuous. Cite prominently in §03. |
| [2606.09005](https://arxiv.org/abs/2606.09005) | **DACSI** | "document-authored labels are data, not policy." A "non-imperative, metadata-like payload subclass" where retrieved text impersonates "metadata, provenance, authority, or disclosure-policy signals." Includes "a source-authority attribution probe." This is authorization standing as an attack class. |
| [2606.04109](https://arxiv.org/abs/2606.04109) | **Discourse-Role Labels as Presentation-Time Variables** | Paired fixed-content probe over 500 MMLU-Pro items: same misleading assertion under `Reference:` / `Evidence:` / `Instruction:` / `Note:` / `Example:`. Adoption shifts **56–84 percentage points**; "`Example:` consistently suppresses it." That last result is a use-mention effect measured empirically without being named as one. Small paper, easy cite, strong support for (b). |
| [2508.19980](https://arxiv.org/abs/2508.19980) | **PasswordEval** | "whether language models can correctly determine when a user request is authorized (i.e., with a correct password)." Authorization standing, measured directly. Plus: "reasoning traces frequently leak confidential information." |
| [2605.12233](https://arxiv.org/abs/2605.12233) | **TAB** (Task Alignment Benchmark) | 89 terminal tasks with a necessary environmental cue plus a plausible distractor. "Evaluating six prompt-injection defenses further shows that **suppressing distractor execution also suppresses the cues required for task completion**." That is the over/under-refusal tradeoff inside the injection setting — the manuscript's refusal-appropriateness point, demonstrated on agents. |
| [2508.15815](https://arxiv.org/abs/2508.15815) | **UserAssist** (ACL 2025) | Role-tag-induced bias across 52 frontier models; "human-preference alignment amplifies user bias, while reasoning fine-tuning reduces it." Source authority as a training artifact. |
| [2505.00626](https://arxiv.org/abs/2505.00626) | **The Illusion of Role Separation** (ICML 2025) | Fine-tuned models identify roles via "task type exploitation" and "proximity to begin-of-text." **A threat to construct validity for any source-role minimal-pair design, including the manuscript's** — if models track position and task type rather than role, source contrasts may be measuring the proxy. |
| [2606.27567](https://arxiv.org/abs/2606.27567) | **On the Inseparability of Instructions and Data** | Impossibility proof for SEP's construct in shared-embedding architectures. The manuscript leans on SEP as the formalisation of one central problem; this argues the problem is not solvable in-pipeline. Useful for the limitations section. |
| [2604.12177](https://arxiv.org/abs/2604.12177) | **PhantomPolicy** | 600 traces manually reviewed; "Manual review changes 32 labels (5.3%) relative to the original case-level annotations, confirming the need for trace-level human review." A **directly quotable warrant** for the manuscript's argument, and a (c)/(d) exemplar. |
| [2604.08499](https://arxiv.org/abs/2604.08499) | **PIArena** | Unified prompt-injection evaluation platform; finds "fundamental challenges when an injected task aligns with the target task." |

## Over-refusal / exaggerated safety (successors to XSTest)

The manuscript cites only `rottger2024xstest` for this whole failure mode. XSTest is 250 hand-written prompts from 2024 and is saturated on current models. Three successors, verified:

- **FalseReject** (arXiv:2505.08054): "16k seemingly toxic queries… across 44 safety-related categories," with "a human-annotated benchmark test set," benchmarked on 29 SOTA LLMs. The natural XSTest replacement citation.
- **The Refusal–Compliance Tradeoff** (arXiv:2605.05427): audits both directions jointly across 21 open-weight models on OR-Bench, XSTest, ToxiGen, BOLD, "using a composition adjustment to isolate model sensitivity from dataset toxicity confounds." Opens with "Refusal rates are a poor proxy for LLM safety" and closes calling for "joint, demographically-aware, and multi-judge safety evaluation." That is the manuscript's §02 argument, empirically instantiated.
- **HopRefusalBench** (arXiv:2608.01358, 2026-08-02, six days ago): 889 unanswerable multi-hop questions with "a final-outcome taxonomy spanning target-aware refusal, pseudo-refusal, hallucinated completion, and search-budget exhaustion." **A refusal-attribution taxonomy** — the same move the manuscript makes, in the search-agent setting.
- Also: **InjecGuard / NotInject** (arXiv:2410.22770), 339 benign samples with injection trigger words, measuring guardrail over-defense. Older (2024) but it is over-refusal measured on the *guard model* rather than the assistant, which is the manuscript's grader-error angle.

## LLM-judge meta-evaluation and judge-error measurement

The manuscript claims **(d)** as a near-unique Y ("only one measures its own grader's error"). True of the six chosen comparators; false as a field claim by 2026. Reword the surrounding prose or the sentence will be challenged.

- **AgentProp-Bench** (arXiv:2604.16706) — the sharpest. 2,000 tasks, 2,300 traces, "a 100-label human-validated subset." Result: "Substring-based judging agrees with human annotation at kappa=0.049 (chance-level); a three-LLM ensemble reaches kappa=0.432 (moderate) with a conservative bias." Column (d), on agent traces, quantified.
- **Judge Reliability Harness** (arXiv:2603.05399, **RAND Corporation**) — an open-source library generating reliability tests, evaluated on "four benchmarks spanning safety, persuasion, misuse, and agentic behavior." Perturbations include "simple text formatting changes, paraphrasing, changes in verbosity, and flipping the ground truth label." **That is column (e) applied to the judge**, which is the manuscript's declared gap. "No judge that we evaluated is uniformly reliable across benchmarks using our harness."
- **RubricEval** (arXiv:2603.25133): rubric-level (not response-level) judge meta-evaluation, 3,486 instances; "even GPT-4o… achieves only 55.97% on Hard subset."
- **When the Judge Changes, So Does the Measurement** (arXiv:2607.08535): "We treat this evaluator-replacement ambiguity as a measurement-validity problem… LLM-as-judge reports should include dataset slices, bias probes, error-dependence estimates, and protocol audit trails." Measurement-validity framing, same as the manuscript's.
- **Sage** (arXiv:2512.16041): judge assessment without human ground truth, via local self-consistency and global transitivity. Notable for the manuscript's rater-role section: "We also find substantial inconsistency in human judgments, which indicates that human annotation may not be a reliable gold standard."
- **LongJudgeBench** (arXiv:2606.01629).
- **OS-Harm** (arXiv:2506.14866, NeurIPS 2025): already does column (d) at a basic level — "an automated judge… that achieves high agreement with human annotations (0.76 and 0.79 F1 score)."

## Task success separated from compliance (column (a))

- **OctoBench** (arXiv:2601.10343, ACL 2026): "To disentangle solving the task from following the rules, we provide an automated observation-and-scoring toolkit that captures full trajectories and performs fine-grained checks." 34 environments, 217 tasks, 7,098 checklist items, three scaffold types. **The scaffold-awareness angle also maps onto the manuscript's "scaffold failure" attribution category** — the only paper I found that treats the scaffold as an instruction source in its own right.
- **MOSAIC** (arXiv:2601.18554, EACL 2026): "existing benchmarks often fail to reflect real-world use or isolate compliance from task success"; finds "compliance is not a monolithic capability."
- **COPAL** (arXiv:2606.04394): composed-policy violations in chatbots; 33.1% error rate across 9 served models.
- **Instruction Stacking Collapse** (arXiv:2608.02639): follow rate falls "from ~96% to as low as 20%" as 24 verifier-checked instructions stack; "A single 'output JSON' constraint… is jointly unsatisfiable with nine others." Instruction conflict as an emergent property of stacking, not of adversarial design.

## Other, lower priority

- **Prompt Governance?** (arXiv:2606.07539, FAccT 2026): whether system-level instructions "operate reliably, consistently, and predictably enough across contexts and adversarial settings to support such governance frameworks"; analyses EO 14319 and the EU GPAI Code of Practice. The policy-memo audience the project targets.
- **Security Considerations for AI Agents** (arXiv:2603.12230): Perplexity's NIST/CAISI RFI response. Names "code-data separation, authority boundaries," "confused-deputy behavior," and asks for "policy models for delegation and privilege control." Useful evidence that the practitioner side wants exactly this.
- **ROME/ARISE** (arXiv:2605.03242): rewrites unsafe trajectories into deceptive variants "while preserving their underlying risk labels" — a controlled-transformation design for column (e).
- **Dynamic Boundary Evaluation** (arXiv:2605.06213): item-bank/IRT-style difficulty calibration covering "harmful request refusal and over-refusal." Measurement-theoretic, relevant to the manuscript's threshold-justification argument in §02 sentence 1.
- **Adaptive Evaluation of Out-of-Band Defenses** (arXiv:2606.26479): warns that CaMeL/FIDES/Progent/RTBAS/FORGE are "validated only on static benchmarks… the same methodology that made in-band defenses look strong until adaptive, defense-aware attacks broke twelve of them at over 90% success."
- **Who Controls the Conversation?** (arXiv:2603.00089, CHI 2026): user perceptions of system prompts.

---

# Use-mention: the evidenced negative

**I could not find a 2025–26 benchmark that targets the use-mention distinction as such.** This is the manuscript's most defensible novelty claim. Here is the covered space, so the claim is inspectable:

Searches run:
1. WebSearch: `use-mention distinction large language models benchmark quoted vs commanded 2026` — no benchmark returned; results were generic LLM-benchmark listicles.
2. WebSearch: `arXiv 2026 benchmark LLM distinguishing quoted instruction from issued instruction metalinguistic mention pragmatics evaluation` — **top substantive hit was arXiv:2607.01153, the manuscript itself.**
3. Semantic Scholar citations endpoint on arXiv:2403.06833 (SEP), arXiv:2406.13352 (AgentDojo, both pages), arXiv:2502.08745 (IHEval) — **265 citing records scanned**; no title containing *use*, *mention*, *quotation*, *quoted*, *metalinguistic*, or *autonymy* in the relevant sense.

Nearest neighbours, neither of which names the distinction:
- **Discourse-Role Labels** (2606.04109) finds `Example:` suppresses adoption relative to `Instruction:`/`Reference:`. That is a use-mention effect discovered as a labelling effect.
- **Prompt Injection as Role Confusion** (2603.12277) is about *who is speaking*, which is source authority, not use vs mention.
- **DACSI** (2606.09005) explicitly separates "command-style injection" from a "non-imperative… metadata/provenance/policy surface" — the closest anyone comes to grammatical mood as an evaluation variable.

**Caveat on the negative:** three searches plus three citation graphs is not the whole literature. The claim I can defend is "not found in the AgentDojo/IHEval/SEP citation graphs or in two targeted web searches," not "does not exist." If the manuscript wants to assert it in print, the queries need to be stated.

---

# Ranked verdict

## Put in the comparator table (5)

1. **AgentAtlas** (2605.20530) — competing coverage audit over 15 benchmarks + control-decision taxonomy. The omission a methods reviewer will find.
2. **IH-Benchmark** (2607.25987) — the IHEval successor. Cheapest fix, most predictable complaint.
3. **Same Payload / SAS** (2606.00566) — matched-payload source-role minimal pairs. Occupies the manuscript's declared Study-B gap (e).
4. **PolicyGuardBench** (2510.03485, ICML 2026) — 60k items, provisionally all-N. Include it *because* it is large and separates nothing; it converts the scale argument from assertion to demonstration.
5. **Who&When Pro** (2607.09996) **or MP-Bench** (2603.25001) — pick one for column (f). MP-Bench if the (g) claim matters more; Who&When Pro if scale and the ICML-spotlight lineage matter more.

## Add as citations, no row (highest value first)

**Safety, or Just Capability?** (2607.28685) · **Prompt Injection as Role Confusion** (2603.12277) · **Discourse-Role Labels** (2606.04109) · **AgentProp-Bench** (2604.16706) · **Judge Reliability Harness** (2603.05399) · **TAB** (2605.12233) · **FalseReject** (2505.08054) · **Control Illusion** (2502.15851) · **WIRE** (2605.27784) · **PhantomPolicy** (2604.12177) · **ManyIH-Bench** (2604.09443) · **OctoBench** (2601.10343) · **How should AI Safety Benchmarks Benchmark Safety?** (2601.23112) · **The Illusion of Role Separation** (2505.00626) · **Refusal–Compliance Tradeoff** (2605.05427) · **ConInstruct** (2511.14342) · **DACSI** (2606.09005) · **PasswordEval** (2508.19980) · **Talk is (Not) Cheap** (2605.15118)

## The bad news, stated plainly

**The manuscript's two honest self-declared gaps are exactly where 2026 moved.** §02 says: "Its references are author-written rather than independently adjudicated, and the seed set carries no nuisance or placebo transformations. Those are the two gaps Study A and Study B exist to close."

- Column (e), nuisance/placebo: **Same Payload** (matched payloads, channel-only variation), **Judge Reliability Harness** (formatting/paraphrase/verbosity/label-flip perturbations), **Discourse-Role Labels** (paired fixed-content probe), **ROME** (rewrites preserving risk labels). Four papers, all 2026, all before or around v1.
- Column (c), independent adjudication: **PhantomPolicy** (600 traces human-reviewed, 5.3% label change), **AgentProp-Bench** (100-label human-validated subset), **TraceElephant**, **IH-Benchmark** (human-authored taxonomy + predicate DSL).

**Column (d) is no longer scarce.** The sentence "only one measures its own grader's error" is defensible about the six chosen comparators and indefensible as a claim about the field. AgentProp-Bench, OS-Harm, PhantomPolicy, RubricEval, the RAND harness, and AgentAtlas's taxonomy-blind contrast all do a version of it. Either scope the sentence explicitly to the six, or drop the implicature.

**Column (g) is contested.** MP-Bench claims to be "the first benchmark designed for" attribution ambiguity; WIRE's four-cell profile is a non-binary outcome space with 13,335 trials behind it.

**Column (b) survives, and it is the paper's real asset.** No 2025–26 benchmark I found annotates pragmatic status (use vs mention, quoted vs commanded, mood) *alongside* source role. Same Payload varies channel; Discourse-Role Labels varies the wrapper label; Role Confusion measures perceived speaker. None of them varies whether the string is being used or mentioned. **The revision should lead with (b) and treat (d) as supporting rather than distinguishing.**

One structural risk beyond the table: the comparator table itself is now a crowded genre. AgentAtlas (15 benchmarks), Talk is (Not) Cheap (6 benchmarks, 507-leaf taxonomy, released artifacts), SafeAudit (3 benchmarks, 12 environments), and the 210-benchmark review all audit benchmark coverage. A reviewer may ask why a six-row hand-read table is the right instrument when extensible released matrices exist. The answer is presumably that none of them has a pragmatic-status axis — but the paper has to say so.
