# MATE vs. Adversarial Pragmatics: competitor assessment

Prepared 2026-08-08 for the JAIR submission of *Adversarial Pragmatics for AI Safety
Evaluation* (arXiv:2607.01153 v3).

---

## VERDICT

**On MATE specifically: NEEDS A ROW. Not damaging.**

MATE does not overlap the manuscript's construct. It is policy-violation detection over
mobile-GUI action sequences; the manuscript is about pragmatic interpretation of
language. Not one of the manuscript's claims is falsified by it, and the manuscript
makes no "first" or "no existing benchmark" claim anywhere that MATE could contradict
(grep for `first|no existing|novel|nobody|no benchmark|not been|to (my|our) knowledge`
across the main file, `sections/*.tex` and `supplement.tex` returns two innocuous hits,
"the first question" and "the first three"). Every novelty statement is explicitly
scoped to the six named comparators. MATEBench scores N or P on all seven columns, so
the row strengthens the paper and costs two word changes elsewhere.

**On what looking for MATE turned up: DAMAGING.**

MATE is the least of it. A citation-graph sweep of AgentDojo, IHEval and SEP (265 citing
records) found that the comparator set is a 2023–2025 sample being submitted in August
2026, and that **the two gaps §02 honestly declares as its own are exactly where the
field moved in 2026**:

- Column (e), nuisance/placebo transformations, declared as future work: at least four
  2026 papers do it, one of them (Same Payload / SAS, arXiv:2606.00566) using
  matched payload pairs that hold the malicious string identical and vary only the
  delivery channel, published two months before v1.
- Column (d), "only one measures its own grader's error": true of the six chosen, and
  indefensible as a field claim. Six 2025–26 papers do a version of it.
- Column (g), items may stay unresolved: contested by MP-Bench (arXiv:2603.25001),
  which calls itself "the first benchmark designed for multi-perspective failure
  attribution" and explicitly accounts for attribution ambiguity.
- The comparator table is now a crowded genre. AgentAtlas (arXiv:2605.20530) ran a
  coverage audit over fifteen agent benchmarks in May 2026; another review covers 210.

**Column (b), pragmatic status annotated alongside source role, survives, and it is the
paper's real asset.** Across three citation graphs and two targeted searches, nothing
found varies whether a string is used or mentioned. The revision should lead with (b)
and demote (d) to supporting. Full detail and the evidenced-negative queries in §6.

The single most damaging fact is in §5 and is about the manuscript, not any rival: its
own column (c) is N, so on the one dimension where it claims advantage over synthesized
sets it currently scores the same as they do.

---

## Source verification

The full paper is **not yet public**. USENIX Security '26 runs 12–14 August 2026 and
the proceedings PDF field on the presentation page is present but carries no href as of
2026-08-08. Everything below is from the **abstract and author block**, fetched and
archived, and is labelled as such. Two claims circulating in search summaries
("158 Chinese and English mobile applications"; ">90% on two external agent-security
benchmarks") are **not** in the fetched abstract and I could not verify them; do not
cite them.

**Verified from <https://www.usenix.org/conference/usenixsecurity26/presentation/jiang-changyue>
(fetched 2026-08-08; also cross-checked against the technical-sessions listing):**

- **Title:** MATE: Policy-Aware Security Auditing for Mobile Agents via Synthesis-Driven
  Trajectory Learning
- **Authors:** Changyue Jiang, Fudan University and Shanghai Innovation Institute;
  Jiayi Wang, Xin Wen, Jiarun Dai, and Geng Hong, Fudan University; Xudong Pan, Fudan
  University and Shanghai Innovation Institute
- **Venue:** 35th USENIX Security Symposium, Baltimore MD, 12–14 August 2026.
  **Category: Short Presentation.** Not listed on the Cycle 1 accepted-papers page, so
  it is a Cycle 2 acceptance (consistent with the Fudan SecSys announcement of
  2026-07-20, which I could not fetch directly: the host returns 504 and it is not in
  the Wayback Machine).
- **Local archive:** `notes/sources/usenix-sec26-mate-jiang-2026-08-08.html`
  SHA-256 `171d08bcd0174000fa4447202ea370ce2842ee279a5a0e4005e674bcc738f49a`

**Abstract, verbatim:**

> Mobile agents powered by foundation models now automate complex, multi-step workflows
> on real devices, but their trajectories can violate app-specific security policies.
> Existing trajectory-level defenses rely on LLM prompting or rigid rules, and thus fail
> to support fine-grained, natural-language policies that generalize across apps and
> tasks. In this work, we introduce MATE, a lightweight, policy-conditioned auditor that
> encodes both agent trajectories and natural-language security policies to determine
> whether a trajectory violates a given policy and to explain why. Treating policies as
> editable text rather than fixed model parameters allows MATE to handle user-defined
> and evolving requirements without retraining. To construct MATE, we build a knowledge
> base by extracting app descriptions, workflows, and policies from hundreds of popular
> mobile apps worldwide, and synthesizing over 140K semantically realistic,
> policy-conditioned trajectories with a multi-stage pipeline. We further release
> MATEBench, a trajectory-level auditing benchmark with two synthetic subsets and one
> real-world subset of manually collected trajectories. Models trained with our
> synthesis-driven trajectory learning achieve over 95% accuracy on MATEBench, retain
> strong performance on external safety benchmarks, and audit trajectories from Zhipu's
> AutoGLM and Alibaba's Mobile-Agent on real devices with over 95% accuracy,
> outperforming prior methods by over 20%. MATE shows that practical, fine-grained
> security auditing for heterogeneous mobile agents is both feasible and effective.

---

## 1. What MATEBench is a benchmark OF

**Unit: the (trajectory, policy) pair.** A trajectory is a multi-step sequence of
actions a foundation-model mobile agent takes on a real device inside an app. The
auditing task is a function of two inputs, not one: given a trajectory *and* a
natural-language policy, output a binary violation judgment plus a natural-language
explanation. Not a turn, not an item.

**Policies: app-specific operational security rules.** Extracted from "app descriptions,
workflows, and policies from hundreds of popular mobile apps worldwide." These govern
what an agent may *do* inside an application. They are not about authorization standing
among competing linguistic sources, and they are not safety policies in the
harmful-content sense; they sit closest to task-compliance-plus-information-flow
constraints. Critically, MATE's framing presupposes that policy application is
**decidable**: a trajectory either violates a given policy or it does not, and the model
can say why. There is no provision for a policy whose application to a case is
genuinely contested.

**How the 140K were generated: fully synthetic, from a knowledge base.** A knowledge
base is built by extraction from app documentation, then "a multi-stage pipeline"
synthesizes "over 140K semantically realistic, policy-conditioned trajectories." No
seeding from real traces is mentioned for the training corpus.

**Correction to the framing in the task brief:** the 140K figure is MATE's **training
corpus**, not MATEBench. The abstract does not state MATEBench's size at all. MATEBench
is a separate, smaller artifact: two synthetic subsets plus one real-world subset of
manually collected trajectories. Any comparison of "18 items vs 140K" compares a
benchmark to a training set and should not be made in those terms.

**What that does to validity.** Two of MATEBench's three subsets are synthetic, and the
synthesis pipeline that produced them is the same pipeline family that produced the
auditor's 140K training trajectories. The labels on those subsets are assigned by
construction: the pipeline that writes the item also writes the answer. A >95% accuracy
figure on such a subset measures pipeline-internal consistency, not policy-violation
detection. This is the manuscript's column (c) failure in an acute form, and it is
exactly what `haimes2024benchmarkInflation` is cited for at
`sections/02-pass-fail.tex:13`.

The genuinely load-bearing evidence is the real-world subset and the live AutoGLM /
Mobile-Agent device runs. Two observations there, both from the abstract alone:

- The abstract reports **the same ">95%"** for MATEBench and for the real-device
  transfer. Synthetic-to-real transfer normally costs accuracy. That either indicates
  the real subset is easy, that it is small, or that it shares structure with the
  synthetic ones. The abstract gives no n, so the question is unresolvable until the
  PDF is out.
- The explanations ("explain why") appear nowhere in the reported metrics. A single
  accuracy number cannot be scoring a free-text explanation, so the explanation
  component is very likely **unevaluated**. That is worth a sentence in the manuscript,
  because it is the closest thing in the neighbouring literature to the manuscript's
  attribution ambition, and it ships unvalidated.

---

## 2. Construct overlap: near-disjoint, but adjacent on one surface

**MATE touches none of the pragmatic phenomena.** Checked item by item:

| Manuscript phenomenon | In MATE? |
|---|---|
| Instruction conflict (competing directives) | No. One authoritative policy text; nothing competes with it. |
| Embedded commands / indirect injection | No. The threat model is a trajectory that drifts outside policy, not untrusted text acquiring directive force. |
| Use vs. mention, quoted vs. commanded | No. Trajectories are action sequences; there is no quotation phenomenon and no string whose directive status is in question. |
| Source authority / authorization standing | No. Policies are given, not contested; no source-role dimension. |
| Refusal appropriateness (over- and under-) | No. The auditor judges completed trajectories post hoc. There is no refusal dimension and no exaggerated-safety analogue. |
| Failure attribution (capability / safety refusal / scaffold / drift / misreport) | No. Output is violation + which policy clause, not why the agent failed. |
| Policy-boundary ambiguity | **Inverted.** MATE assumes decidability; the manuscript's family is the residue where decidability fails. |

**The one real adjacency: trajectory-level judgment.** MATE occupies the surface the
manuscript names as its eighth family and then defers. `sections/03-taxonomy.tex:82`:
"In the seed set this family is instantiated only by a single-turn tool-result injection
(pair P007); multi-turn transcript items are deferred to Study~B." MATE ships a trained
auditor and a released benchmark on that surface now.

**Net:** the constructs are disjoint; the *evaluation surfaces* touch at one edge. MATE
is a defence-plus-benchmark for policy compliance over action sequences. The manuscript
is a diagnostic framework for interpretation of language. A reviewer who reads both will
not think the manuscript has been scooped. A reviewer who reads only MATE's abstract and
the manuscript's abstract might, which is the reason to cite it and draw the line
explicitly rather than leave it to inference.

---

## 3. Draft comparator row

Table format from `sections/02-pass-fail.tex:26–39`, seven columns:
(a) task success scored apart from policy/safety compliance; (b) source role and
pragmatic status both annotated; (c) expected behaviour adjudicated independently of the
item author; (d) grader or judge error itself measured; (e) nuisance or placebo
transformations; (f) transcript-level failure attribution; (g) an item may stay
unresolved.

```latex
MATEBench \citep{jiang2026mate} & N & N & N & P & N & P & N \\
```

Insert after the `InjecAgent` line and before `Tensor Trust`, or at the end of the
neighbour block; ordering in the existing table is not chronological, so either is fine.

**Coding rationale (abstract-only; re-check every cell when the PDF posts 12 Aug):**

- **(a) N.** Only policy violation is scored. No task-success dimension is reported at
  all; whether the agent completed the user's workflow is not part of the label.
- **(b) N.** Single policy source, no source-role annotation; no pragmatic status.
- **(c) N.** Synthetic subsets are labelled by the generating pipeline. "Manually
  collected" describes collection of the real-world trajectories, not independent
  adjudication of their labels; the abstract does not say who labelled them. Could
  become P if the PDF shows independent annotation of the real subset.
- **(d) P.** This is the only close call. Auditor accuracy is measured against MATEBench
  and, more usefully, against live third-party AutoGLM and Mobile-Agent traces, which is
  real external validation of a scoring model. But the reference labels' own error is
  not estimated, the synthetic subsets share a generator with the training corpus, and
  the explanation output appears unscored. **P, not Y** — and this matters, because Y
  would break the sentence "only one measures its own grader's error."
- **(e) N.** No nuisance or placebo conditions in the abstract. Provisional.
- **(f) P.** The strongest cell and the reason the row belongs. MATE localizes a
  violation within a trajectory and explains it — genuine transcript-level attribution,
  but attribution to a *policy clause*, not to a failure *cause*. It cannot distinguish
  capability failure from safety refusal from scaffold failure from goal drift from
  misreporting.
- **(g) N.** Binary violation judgment reported as a single accuracy percentage, which
  requires forced choice.

**Consequential text edits, both trivial** (`sections/02-pass-fail.tex:19`):

- "against six neighbouring benchmarks" → "against seven neighbouring benchmarks"
- "Only two of the six score task success apart from policy compliance" → "Only two of
  the seven..." (Y count is unchanged: AgentDojo and Tensor Trust.)
- "none annotates pragmatic status alongside source role" — **unchanged**, MATEBench is N on (b).
- "only one measures its own grader's error" — **unchanged**, given P on (d).

**Also add a paragraph to the supplement evidence map** (`supplement.tex`, after the
Tensor Trust paragraph at line 330–338), matching the house pattern:

> \textbf{MATEBench} \citep{jiang2026mate}. (a) N: only policy violation is scored;
> completion of the user's workflow isn't labelled. (b) N: a single policy text supplies
> the norm, so there is no source-role contrast, and pragmatic status isn't annotated.
> (c) N: two of three subsets are synthesized by the pipeline that also produced the
> auditor's training trajectories, so the item author and the label author are one
> process; the third subset is described as manually collected, without a stated
> adjudication procedure. (d) P: auditor accuracy is reported against the benchmark and
> against live third-party device traces, but the reference labels' own error isn't
> estimated and the free-text explanations aren't scored. (e) N: no nuisance or placebo
> condition is reported. (f) P: a violation is localized within a trajectory and
> explained, but attribution is to a policy clause rather than to a failure cause.
> (g) N: the judgment is binary and reported as a single accuracy figure. Coded from the
> abstract; the proceedings version was not public at the time of coding.

**Bib entry for `references-local.bib`** (append; do not overwrite):

```bibtex
@inproceedings{jiang2026mate,
  author    = {Jiang, Changyue and Wang, Jiayi and Wen, Xin and Dai, Jiarun and Hong, Geng and Pan, Xudong},
  title     = {{MATE}: Policy-Aware Security Auditing for Mobile Agents via Synthesis-Driven Trajectory Learning},
  booktitle = {Proceedings of the 35th {USENIX} Security Symposium},
  publisher = {{USENIX} Association},
  address   = {Baltimore, MD},
  year      = {2026},
  url       = {https://www.usenix.org/conference/usenixsecurity26/presentation/jiang-changyue},
  urldate   = {2026-08-08},
  note      = {To appear. Coded from the published abstract; proceedings {PDF} not public as of 2026-08-08}
}
```

---

## 4. Manuscript claims at risk

**No claim is falsified.** The manuscript is unusually well insulated, because every
comparative statement is scoped to the named set rather than to the field. Three
passages nevertheless take on exposure.

### 4a. The comparator set's vintage (the real one)

> "Table~\ref{tab:comparators} sets those separations against six neighbouring
> benchmarks. The advantage claimed here isn't scale... Only two of the six score task
> success apart from policy compliance, none annotates pragmatic status alongside source
> role, and only one measures its own grader's error."
> — `sections/02-pass-fail.tex:19`

Literally true and correctly hedged. But the six are from 2023–2025, and this goes to
JAIR in August 2026. The sentence does rhetorical work as an implicit claim about the
field, and a reviewer who knows the 2026 literature will read the set as under-sampled.
MATE is the exhibit that makes the point, not the substance of it: see §6, where the
sweep it prompted found five further candidates and showed that the clause "only one
measures its own grader's error" carries an implicature about the field that six
2025–26 papers falsify. Adding the MATE row is not the fix; refreshing the set and
scoping that clause is.

### 4b. The trajectory promissory note

> "it's built to extend to transcript-level attribution, which the seed pilot and
> current static fixtures don't yet exercise"
> — `sections/09-conclusion.tex:5`

> "It's designed to extend to multi-turn agent transcripts, which the seed set
> represents only by a single-turn tool-result contrast."
> — abstract, `adversarial-pragmatics-for-ai-safety-evaluation.tex:27`

Still true, but the ground is now occupied by a shipped artifact. The roadmap at
`sections/07a-limitations-next-steps.tex:34` ("A later trajectory harness would have to
vary and record sequence length, opportunities to retry, child-session and tool
affordances, cumulative state, monitor visibility and intervention, and pause,
operational-continuation, normative-release, restart, and stopping rules") reads
differently once a reviewer knows a 2026 USENIX paper released a trajectory auditing
benchmark. **The fix is one sentence, and it is a strengthening move**, because the
distinction is real and the manuscript already has the argument: MATE audits trajectories
against policies it treats as determinately applicable, so it cannot represent the
policy-boundary cases, and its attribution is to a policy clause rather than to a
failure cause. Suggested placement is `sections/03-taxonomy.tex` in the agent-transcript
subsection, right after the P007 sentence at line 82.

### 4c. The unstated answer to the obvious question

A hostile reviewer will ask: MATE produces natural-language explanations of policy
violations at >95% accuracy over 140K-trained trajectories; what does an 18-item
taxonomy add? The manuscript has the answer distributed across §3 (policy-boundary
ambiguity), §4 (validation architecture) and §7a, but never assembles it, because MATE
is not cited. Assembling it in two sentences is worth more than the table row.

### 4d. Claims MATE *helps*

- `sections/03-taxonomy.tex:76–82`, agent transcript interpretation: MATE is positive
  evidence that trajectory auditing is being deployed *without* failure attribution.
  Cite it as a live instance of the gap the family names.
- `sections/02-pass-fail.tex:13`, benchmark inflation: MATE is a 2026 worked example of
  synthetic-reference construction, currently supported only by 2021–2024 citations.

---

## 5. Scale asymmetry: a differentiator, and MATE's construction supports the manuscript

**The comparison as framed does not hold.** 140K is the training corpus. MATEBench's
size is unstated. There is no "18 vs 140K" fact to defend against.

**On the substance, MATE is an argument for the manuscript's position, not against it.**
Its references are generated by the pipeline that generates its training data. The
manuscript's position — that construct validity comes from adjudicated references and
controlled contrasts rather than from n — predicts exactly the pattern MATE's abstract
shows: a very high number on pipeline-internal data, an unstated-n real-world holdout,
and an explanation output that the reported metrics do not appear to score. That is a
free, current, high-profile illustration.

**But here is the finding that hurts, and it is not about MATE.**

Small-and-adjudicated beats large-and-synthesized only if the adjudication has happened.
It has not:

> "It uses 18 hand-authored seed items, three local models, harmless toy payloads, and
> one expert adjudicator, the author, labelling items he wrote from expected-behaviour
> fields he also wrote. The judge pass shares this circularity: the judge model was
> drawn from the evaluated set and saw each item's expected-behaviour field."
> — `sections/07a-limitations-next-steps.tex:4`

The manuscript's own comparator row is **(c) N**, the same as MATEBench's. On the single
dimension where it claims the advantage over synthesized sets, it currently scores the
same as the thing it is being compared to. The manuscript says so plainly, twice
(`sections/02-pass-fail.tex:19`: "Its references are author-written rather than
independently adjudicated"), and that candour is its defence. But candour about a gap is
not closure of it, and a JAIR reviewer can put it starkly: 18 self-authored,
self-labelled, self-adjudicated items plus a prospective Study A/B, against a released
benchmark with a real-device holdout and validation on two third-party production agents.

The manuscript wins that exchange on construct argument and loses it on delivered
evidence. Nothing in this assessment changes that, and adding MATE to the table makes
the asymmetry slightly more visible rather than less. **If anything in the paper should
move before submission, it is Study A's independent adjudication of even a handful of
the 18 items — turning (c) from N to P.** That is worth more to the submission than
every edit proposed above combined.

---

## 6. Other 2025–26 benchmarks the table now misses

From a parallel sweep of the Semantic Scholar citation graphs of AgentDojo
(2406.13352), IHEval (2502.08745) and SEP (2403.06833) — 265 citing records scanned —
plus targeted searches. **None of the following is currently cited** (grepped both bibs
and all `.tex`). Full detail, with a fetched URL and verbatim abstract for every entry:
`/tmp/claude-agent-output/rival-benchmarks-2025-26.md`.

**Standing caveat:** these were read at abstract level, not full text. The table caption
promises "entries are read from each paper," so every provisional column score below has
to be re-derived from the full paper before it goes in.

### The five that most need a row

| Candidate | Why | Provisional (a)–(g) |
|---|---|---|
| **AgentAtlas** arXiv:2605.20530 (2026-05) | The dangerous one. A six-state control-decision taxonomy (Act/Ask/Refuse/Stop/Confirm/Recover), a trajectory-failure vocabulary with "primary error source and downstream impact," and **a 0/1/2 coverage audit over fifteen agent benchmarks**. A reviewer will ask why a six-row coverage audit does not cite the fifteen-benchmark coverage audit from three months earlier. Mitigation: it is a two-author preprint with a synthetic item set that disclaims being a benchmark release, so the manuscript can claim the executed artifact — but it must be cited. | Y P N P N Y P |
| **IH-Benchmark** arXiv:2607.25987 (2026-07-28) | The IHEval successor: 44 constraint families, 37 models, S>U and U>T conflict surfaces. Its conclusion ("instruction-hierarchy robustness is not a single capability, but a set of behaviors") is a compressed form of the manuscript's own thesis. Cheapest fix, most predictable complaint. Also a gift: "a uniform binary pass/fail protocol" is (g) = N. | P P P N N N N |
| **Same Payload, Different Channel / SAS** arXiv:2606.00566 (2026-05-30) | Worst on a per-column basis. "Matched payload pairs that keep the malicious text identical and vary only the context of delivery" **is** the controlled-transformation design the manuscript declares as a Study-B gap, published before v1, with a scalar metric attached. Does not touch use vs mention: the payload is malicious in every condition, only the channel moves. That is the opening. | N P N N **Y** N N |
| **PolicyGuardBench** arXiv:2510.03485, **ICML 2026** | The one to include *because* it is large and separates nothing: 60k policy-trajectory pairs, provisionally all-N. Converts §02's scale argument from assertion to demonstration. Note the title discrepancy: use arXiv's *Towards Policy-Compliant Agents: Learning Efficient Guardrails For Policy Violation Detection*, not Semantic Scholar's shorter form. Verify the all-N row against full text — an all-N row is a strong claim and an easy thing to get wrong. | N N N N N N N |
| **Who&When Pro** arXiv:2607.09996 (12,326 failed trajectories, 26 benchmarks) **or MP-Bench** arXiv:2603.25001 | Pick one for column (f). Failure attribution has been a named subfield since the Who&When ICML 2025 spotlight; claiming (f) without engaging it will not survive an agents reviewer. MP-Bench if the (g) claim matters more, Who&When Pro if scale and lineage do. | — |

Also in the attribution cluster: TraceElephant (2604.22708, ACL 2026), TELBench+DRIFT
(2606.02060, span-level, distinguishes "harmful error spans" from "normal exploration…
and harmless noise"), AgenTracer (2509.03312), StepFinder (2606.03467, KDD 2026).

### The most important citation that is not a table row

**Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks**
(arXiv:2607.28685, 2026-07-30). It executes the manuscript's validity thesis
quantitatively **on two of the manuscript's own comparators** (InjecAgent, AgentDojo),
shows an "always positive" policy attaining F1 = 0.690 on R-Judge, above five of 21
models that actually discriminate, and closes: "Naming the benchmark, metric, target
behavior, and model panel is the minimum a safety claim needs." It appeared 29 days
after v1. It costs the manuscript no novelty and substantially upgrades §02, which
currently leans on 2021 and 2024 citations. Cite it in the BetterBench/retro-holdout
paragraph at `sections/02-pass-fail.tex:13`.

### Highest-value remaining citations

- **Prompt Injection as Role Confusion** (2603.12277, Ye/Cui/**Hadfield-Menell**):
  "models perceive the source of text from how it sounds, not its labeled role… To the
  model, sounding like a role is indistinguishable from being one." The manuscript's
  central pragmatic claim in one sentence, with representational evidence behind it.
  Strongest corroboration available and the most quotable rival framing; MIT authorship
  makes omission conspicuous. §03.
- **Discourse-Role Labels as Presentation-Time Variables** (2606.04109): same misleading
  assertion under `Reference:` / `Evidence:` / `Instruction:` / `Note:` / `Example:`
  over 500 items; adoption shifts 56–84 points and "`Example:` consistently suppresses
  it." **That is a use-mention effect measured without being named as one** — the best
  available external support for column (b).
- **Control Illusion** (2502.15851, AAAI 2025): "societal hierarchy framings (e.g.,
  authority, expertise, consensus) show stronger influence on model behavior than
  system/user roles." A pragmatics result inside an instruction-hierarchy paper; its
  absence is conspicuous for a paper about language-mediated authority.
- **The Illusion of Role Separation** (2505.00626, ICML 2025): fine-tuned models
  identify roles via "task type exploitation" and "proximity to begin-of-text."
  **A construct-validity threat to the manuscript's own source-role contrasts** — if
  models track position and task type rather than role, P001/P003 may be measuring the
  proxy. Belongs in limitations, not related work.
- **AgentProp-Bench** (2604.16706): "Substring-based judging agrees with human
  annotation at kappa=0.049 (chance-level); a three-LLM ensemble reaches kappa=0.432."
  Column (d) on agent traces, quantified.
- **Judge Reliability Harness** (2603.05399, RAND): judge perturbations including
  "formatting changes, paraphrasing, changes in verbosity, and flipping the ground truth
  label" — column (e) applied to the judge, the manuscript's declared gap.
- **FalseReject** (2505.08054): 16k queries, 44 categories, human-annotated test set.
  The XSTest replacement; the manuscript currently cites only `rottger2024xstest` (250
  hand-written 2024 prompts, saturated) for the whole over-refusal mode.
- **TAB** (2605.12233): "suppressing distractor execution also suppresses the cues
  required for task completion" — the over/under-refusal tradeoff demonstrated inside
  the injection setting.
- **PhantomPolicy** (2604.12177): 600 traces manually reviewed, "Manual review changes
  32 labels (5.3%)… confirming the need for trace-level human review." A directly
  quotable warrant for the manuscript's (c) argument.
- Then: WIRE (2605.27784, non-binary four-cell outcome space plus explicit claim-typing
  discipline — a methodological ally, cite as precedent), ManyIH-Bench (2604.09443),
  ConInstruct (2511.14342), DACSI (2606.09005), PasswordEval (2508.19980), OctoBench
  (2601.10343, treats the scaffold as an instruction source), Refusal–Compliance
  Tradeoff (2605.05427), Talk is (Not) Cheap (2605.15118), How should AI Safety
  Benchmarks Benchmark Safety? (2601.23112, reviews 210 benchmarks).

### Use-mention: the evidenced negative that holds

The sweep could not find a 2025–26 benchmark targeting the use-mention distinction as
such. Covered space, so the claim is inspectable:

1. WebSearch `use-mention distinction large language models benchmark quoted vs commanded 2026` — no benchmark returned.
2. WebSearch `arXiv 2026 benchmark LLM distinguishing quoted instruction from issued instruction metalinguistic mention pragmatics evaluation` — **top substantive hit was arXiv:2607.01153, the manuscript itself.**
3. Semantic Scholar citations on SEP (2403.06833), AgentDojo (2406.13352, both pages), IHEval (2502.08745) — 265 records scanned; no title containing *use*, *mention*, *quotation*, *quoted*, *metalinguistic*, or *autonymy* in the relevant sense.

What this licenses in print is "not found in the AgentDojo/IHEval/SEP citation graphs or
in two targeted web searches," with the queries stated — not "does not exist." Under the
portfolio's negative-claims rule that is the only assertable form, and it is enough.

---

## 7. What to do before the JAIR submission, in order

1. **Get independent adjudication onto even a handful of the 18 items.** Turning column
   (c) from N to P is worth more than every other item on this list combined. It is the
   only one that changes what the paper has, rather than what it cites.
2. **Scope or drop the (d) implicature.** "Only one measures its own grader's error" is
   safe about the six and false about the field. One clause.
3. **Refresh the comparator set.** Add MATEBench plus the five in §6. The added rows
   mostly score worse than the manuscript, so this strengthens the table; the cost is
   reading five papers properly, because the caption promises entries are read.
4. **Lead with column (b).** It is the surviving unique claim and it is currently the
   third item in a list. Demote (d) to supporting.
5. **Cite arXiv:2607.28685** in §02 and **arXiv:2603.12277** in §03. Two citations, high
   return.
6. **One sentence distinguishing the trajectory roadmap from MATEBench and
   PolicyGuardBench**, in `sections/03-taxonomy.tex` after the P007 sentence at line 82.
7. **Add arXiv:2505.00626 to limitations** — it threatens the manuscript's own
   source-role contrasts and is better raised by the author than by a reviewer.
8. Re-check the MATE row against the proceedings PDF once it posts on **12 August 2026**.

---

## Appendix: search record

Negative and positive findings both rest on these queries, run 2026-08-08.

- `arXiv API: all:MATEBench` → no results. **MATE is not on arXiv.**
- `arXiv API: abs:"policy-conditioned" AND abs:"mobile agent"` → one unrelated result.
- `https://secsys.fudan.edu.cn/news/content/2026-07-20-007/` → HTTP 504 on four attempts
  (curl direct, curl with UA, WebFetch ×2, r.jina.ai proxy). Not in the Wayback Machine.
- `https://www.usenix.org/conference/usenixsecurity26/accepted-papers` → 404.
- `https://www.usenix.org/conference/usenixsecurity26/cycle1-accepted-papers` → 580 KB,
  **0 matches** for `MATE|Changyue`. Basis for the Cycle 2 inference.
- `https://www.usenix.org/conference/usenixsecurity26/technical-sessions` → 1.3 MB,
  **10 matches**. Source of the abstract.
- `https://www.usenix.org/conference/usenixsecurity26/presentation/jiang-changyue` →
  full entry; PDF field present, **no href**. Archived locally.
- dblp API and Semantic Scholar API both rate-limited (429 / connection reset); no data
  obtained from either.
