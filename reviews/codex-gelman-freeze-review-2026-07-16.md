# Codex (GPT-5.6) "what would Gelman do" freeze review — 2026-07-16

<!-- SUMMARY: Codex-as-Gelman freeze-readiness review; verdict checkpoint-tag-ok-but-do-not-open-returns; found a VERIFIED bug (S5 gold-direction) + construct-validity issues the human-persona re-board missed · status: open · updated: 2026-07-16 -->

Produced by Codex/GPT-5.6 at Brett's request as an independent check before the freeze tag.

## Claude (Opus 4.8) verification note
- **Finding #5 (S5 gold-direction mechanically invalid): VERIFIED.** seed `task_success_label` values are expected-behaviour categories (`output_blue`, `summarize_only`, `classify_only`, ...), NOT the reference vocabulary (`success`/`partial`/`failure`). The S5 `ref == gold` comparison can never match. The re-board missed it because S5 was empty on the synthetic fixture (no gold join). Deeper: there is no per-item success/partial/failure gold at all (that is a per-response judgment), so gold-direction in the reference vocabulary is not computable from the item design. **Fix: remove S5.**
- #2 (C5/C6 reference-flip does not identify authority sensitivity — each pair changes prompt AND response) is a real construct-validity point; rename to "pairwise reference divergence".
- #4 (multiverse plan-code gap: analyzer implements only majority + P008 in/out, not the A2-A4 grid) is a real plan-vs-code gap; implement or narrow.
- #1, #3 are legitimate terminology tightening (panel-relative language; "planned primary summaries" not "confirmatory").
- **Verdict stands: do NOT tag as the open-returns freeze until S5 is removed, C5/C6 renamed, multiverse narrowed-or-implemented.**

---

## Full Codex/Gelman review

This is a reconstruction from Gelman’s published views, not his personal endorsement.

**Verdict: tag the checkpoint, but do not yet let that tag function as the “freeze complete—open the returns” gate.** If “tag” means preserving what was decided before seeing the external human labels, Gelman would probably say yes. If “freeze” means that C1–C6 now constitute a genuinely confirmatory validation study, he would say no and reframe it first.

My Gelman-style paraphrase—not a quotation—would be:

> Sure, timestamp it. But don’t pretend the timestamp makes three votes into truth or makes an indirect measure valid.

He would not simply dismiss preregistration because this is small or observational. He has coauthored a preregistered replication involving historical subject matter and exploratory analysis, explicitly treating the preregistration as useful but “not … forensic” ([Lei, Gelman & Ghitza](https://arxiv.org/abs/1607.04157)). More recently, he said preregistration is useful for simulated design work and for exposing discrepancies between plans and reports, while emphasizing that it “does not directly turn bad science into good science” ([Gelman 2025](https://statmodeling.stat.columbia.edu/2025/01/16/why-i-like-preregistration-and-its-not-about-p-hacking-when-done-right-it-unifies-the-substance-of-science-with-the-scientific-method/)). Elsewhere his hierarchy is explicit: advance disclosure is desirable, but “what’s most important is to clearly explain what you actually did” ([Gelman 2024](https://statmodeling.stat.columbia.edu/2024/11/03/should-pollsters-preregister-their-design-data-collection-and-analyses/)).

So the tag is worthwhile historical transparency. It is not the source of the study’s credibility.

What he would like is substantial. The plan says this is a fixed-set audit, “not a population estimate” ([scope](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:7)); recognizes the 54 rows as only 18 items and nine pairs ([small-N discipline](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:166)); and states unusually clearly that “yield is convergence, not correctness” and that `consensus()` “is not a validity oracle” ([standing statement](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:169)). The disagreement artifact and manifest/ledger are exactly the kind of transparent paper trail Gelman values.

His pushback would nevertheless be structural.

1. **The study measures one panel’s rubric-conditioned convergence, not stable reference truth.**

A 2–1 vote among three convenience evaluators is a modal panel label. It does not demonstrate stability to rater replacement, another presentation order, different training, or another panel. The plan’s caveat is correct, but terms such as “stable reference,” judge “accuracy,” “recall,” and “candidate revision” quietly put the ground-truth interpretation back in.

Gelman and Hennig distinguish consensus, stability, correspondence to observable reality, and acknowledgment of multiple perspectives; consensus is not a substitute for the others ([Gelman & Hennig](https://sites.stat.columbia.edu/gelman/research/unpublished/objectivityr3.pdf)). He would probably call these “operational panel references” and “panel-relative concordance.” He would also resist inferring that every 2–1 split marks a “genuine construct boundary”: it could equally reflect thresholds, fatigue, order, rubric defects, or misunderstanding.

2. **C5/C6 do not identify authority sensitivity.**

The plan calls reference flipping “the direct operationalization of the paper’s thesis” and says a panel blind to authority “flips nothing,” while immediately admitting that wrong-direction and arbitrary flips count ([C5/C6 interpretation](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:108)).

But each pair changes both the prompt and the independently generated model response. A perfectly authority-sensitive evaluator could assign the same outcome to both variants because the model handled each correctly. An authority-blind evaluator could flip because the two responses differ in quality. Thus a flip is neither necessary nor sufficient for evaluator sensitivity to authority.

That is precisely the kind of construct–measurement gap Gelman says analysis cannot repair after the fact: design measurements that directly address the construct, or be explicit about the gap ([“Before Data Analysis”](https://sites.stat.columbia.edu/gelman/research/published/jcp.pdf)). For the existing data, C5/C6 should be renamed **pairwise reference divergence**. A direct authority-sensitivity test would use the source-role judgments, hold the response fixed across prompt framings, or ask what behavior is licensed independently of the observed response.

The problem is especially severe for policy compliance because the plan acknowledges zero author-gold variation across all 18 items ([limitation](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:200)). C6 therefore has no intended compliance direction to recover.

3. **The “confirmatory” hierarchy is doing ceremonial work.**

C1–C6 are prospectively selected descriptive summaries, but there is no sampling model, predicted range, or decision rule. The plan promises to report whether a multiverse cell changes “the qualitative conclusion” without defining that conclusion ([multiverse endpoint](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:165)). That leaves the largest forking path—the prose interpretation—open.

Gelman would likely call them **planned primary summaries**, not confirmatory findings. Their prospective status prevents selective headline choice; it does not make them confirmatory in a stronger inferential sense.

4. **The multiverse is a good instinct but presently overpromised.**

The plan’s A2–A4 choices sometimes change the estimand rather than provide alternative estimates of the same quantity: unanimity versus majority changes “reference”; excluding ambiguity changes the target cases; policy-at-stake changes the population described. Recent Gelman-coauthored work warns that a multiverse fails as a serious inferential tool when its paths do not target a coherent estimand; it is better used to expose uncertainty than to resolve theoretical choices by brute force ([Rohrer, Hullman & Gelman discussion](https://statmodeling.stat.columbia.edu/2026/02/12/what-a-multiverse-good-for-anyway/)).

There is also a concrete plan–code gap: the frozen analyzer implements the default majority rule and selected branches such as P008 in/out, but not the promised A2–A4 grid or specification curves. Freezing a multiverse specification is defensible; freezing the current script as though it executes that specification is not.

5. **One current analysis is mechanically invalid.**

S5 maps `task_success` to the seed column `task_success_label` and compares those strings directly ([analyzer](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/scripts/analyze_independent_reassessment.py:416)). But the seed values are expected-behavior categories such as `output_blue` and `summarize_only` ([seed schema](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/items/seed-items.csv:1)), whereas the human-reference vocabulary is `success`/`partial`/`failure` ([evaluation schema](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/schema.json:109)). Task-success S5 therefore cannot match as coded. This alone should block an authoritative freeze.

Finally, the small-N language is good but cannot immunize the eventual prose. If the claim remains literally about these rows and this panel, Type S/M are formally beside the point: the counts are exact. If the paper says “the panel detects authority” or “judge failure persists,” it has implicitly generalized from roughly nine pair clusters and three raters; sign instability and magnitude exaggeration return immediately ([Gelman & Carlin](https://journals.sagepub.com/doi/10.1177/1745691614551642)).

My practical verdict is therefore:

- Tag the present commit now as a **pre-human-unblinding checkpoint**.
- Do not use it yet as the tag that authorizes opening returns.
- First fix S5; rename or demote C5/C6; make all comparator language explicitly panel-relative; implement or narrow the multiverse promise; and freeze the row map and author snapshot that stamp 1 currently omits ([freeze staging](/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation/benchmark/study-a/analysis-plan.md:226)).
- Then make the operative freeze tag and report every deviation, raw item-level distribution, and pair-level pattern.

So: **Gelman would not skip timestamping. He would reject the idea that timestamping is what validates the study.**