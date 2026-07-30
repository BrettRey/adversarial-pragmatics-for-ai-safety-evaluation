# What needs you
<!-- SUMMARY: the only open items that require Brett rather than an agent, ordered by dependency, each pre-drafted to a decision or a paste - status: live - updated: 2026-07-29 -->

Six items. Two are one-word decisions, three are short checks, one is real work
I can do once you've answered item 1. Everything else in this project is either
done or is mine to get on with.

---

## 1. Pick a word. Two minutes. Unblocks the tags and both preprints.

`sections-delegation/07-conclusion.tex` says the three programme specifications
are **"frozen before any target outcome."** That is true of the specifications
and checkable in Git history.

But the claim register's `frozen` status now means something stronger after the
code review: anchored *plus* a fixed target inventory. DA's claims don't meet
that, so they now sit at `proposed`. One word, two senses, spanning paper and
artifact. That is the exact defect the external review was about, so it should
not survive into a posted preprint.

**Pick one:**

- **(a) Change the paper's word.** Replace "frozen" with "committed" or
  "pre-registered" in that sentence, leaving the register's `frozen` to mean the
  strong thing. Cheapest, no new claim.
- **(b) Keep "frozen", add one clause** distinguishing the senses, e.g. "frozen
  in the sense that the specifications predate any target outcome; the claim
  register reserves its own `frozen` status for claims whose target inventory is
  also fixed."
- **(c) Earn the strong sense.** Enumerate the target items for each of the three
  programmes, so the claims become genuinely prospective and can be `frozen` in
  both senses. Real design work, and worth doing before the programmes run
  rather than after, but it is not a prerequisite for posting.

I'd take (a). It costs one word and removes the ambiguity outright.

**Reply with just "a", "b", or "c"** and I'll do the rest of this item.

---

## 2. Two small checks, five minutes total, both browser-only.

**2a. SSRN's generative-AI policy.** Their support page 404s and I could not
verify it. You disclose AI assistance on page 1, so this needs a human look
before Evidentiary Assurance is posted there. If they run a prohibition model
rather than a disclosure model, we move EA's preprint elsewhere.

**2b. Is CLSR on U of T's covered list?** Open <https://search.scifree.se/utoronto>
and search "Computer Law" or ISSN 2212-473X. If it's listed as a covered Elsevier
hybrid title, gold OA is free rather than USD 3,760. Their agreement runs to
31 December 2026 and usually attaches at acceptance, not submission, so the
timing matters.

---

## 3. Cut and push two tags. One command, after item 1.

Both manuscripts already name these tags. Neither exists yet, which is the last
thing standing between the papers and their preprint servers.

```
git tag -a delegation-assurance-r1 -m "Delegation Assurance: artifact as described in the manuscript" HEAD
git tag -a evidentiary-assurance-r3 -m "Evidentiary Assurance: artifact as described in the manuscript" HEAD
git push origin --tags
```

Do this *after* item 1, so the tagged state matches the final wording.

---

## 4. Post the two preprints. Twenty minutes, after item 3.

**Delegation Assurance to arXiv.** Categories cs.CY primary, cs.AI cross-list.

> **Licence: choose "arXiv.org perpetual, non-exclusive license 1.0", NOT CC BY.**
> Minds and Machines is Springer, and Springer's policy bars preprints deposited
> under a Creative Commons licence. arXiv licences are irrevocable per version,
> so this cannot be corrected later. This is the single most consequential click
> in the whole list.

**Evidentiary Assurance to SSRN**, subject to item 2a.

Tell me when both are live and I'll update the nine mutual citations from
`@unpublished` to real identifiers, rebuild, and re-verify. That's the step that
makes the three-paper structure legible to a reader for the first time.

---

## 5. Decide whether to run DA's two computational programmes. Your call on compute.

Now unblocked: the leakage hole that would have contaminated them was closed
this morning, and the analyzer is repaired and regression-tested.

- `local_discrimination`: 30 observations across each of 4 families, 120 runs.
- `predictive_typed_ablation`: 10 trace families per family.

Neither needs people or approvals. Same footing as the AP pilot. Running them
turns Delegation Assurance from a framework with frozen specifications into one
reporting two of three programmes, which is a substantial strengthening for
Minds and Machines. The third needs six reviewers per family and stays behind a
human-participants determination.

Say the word and I'll run them.

---

## 6. JAIR submission for Adversarial Pragmatics. The real work, and mostly mine.

Unblocked and independent of everything above. **One thing you should know before
I start: JAIR requires its own LaTeX template at submission and auto-rejects
other formats.** So this is a genuine reformatting pass off the house style, not
a cover letter and upload. Template is at
<https://www.overleaf.com/read/hycbzkdksrzz#8106d4> or the Author Kit on jair.org.

What JAIR wants, verified 2026-07-29:

- PDF only, under 15 MB, in their template.
- **Not blind.** No anonymisation work.
- Three mandatory survey answers, 150 words each. Missing or unclear answers are
  a desk rejection. I've drafted all three below; they need your eye, not your
  labour.
- A reproducibility checklist appended to their template.
- Account registration at jair.org, then the submission wizard.

### Draft survey answers, for you to approve or redline

**Q1. Why this matters to AI researchers.**

> Safety evaluations increasingly rest on judgments about ambiguous language:
> whether a model followed an instruction, refused appropriately, or misreported
> progress. Those judgments are made by LLM judges at scale, and this paper shows
> a rubric-aided judge can look strong in aggregate while never recovering the
> safety-relevant minority class. Across six judge conditions no cell recovered
> more than two of eleven partial successes, and the strongest cell earned its
> aggregate lead partly by never emitting that label. The paper supplies a
> linguistically controlled taxonomy, an 18-item seed benchmark with
> validator-enforced metadata, and an annotation protocol that separates task
> success, policy compliance, risk, refusal, and attribution rather than fusing
> them. The methodological claim is that a single label conceals four distinct
> inference targets, and that evaluation practice should keep them apart.

**Q2. Closest JAIR publications, and how this differs.**

> The closest recent JAIR work is WorldView-Bench (10.1613/jair.1.19001), which
> benchmarks cultural perspectives in LLMs; ConSCompF (10.1613/jair.1.17028), a
> similarity-comparison framework for generative models; and the agentic LLM
> survey (10.1613/jair.1.18675). Each builds an evaluation instrument and reports
> what it measures. This paper differs in asking what such an instrument's scores
> license: it treats labels as inference licenses and tests whether
> safety-relevant categories project across paraphrase, wrapper, model, and judge
> condition. Its central results are negative and about the evaluator rather than
> the evaluated. It also reports item-clustered rather than row-level intervals,
> under which four of six chance-corrected agreement statistics cannot be
> distinguished from a constant labeller, and applies hierarchical partial
> pooling that shrinks the one eye-catching effect to an interval through zero.

**Q3. Prior publication status.**

> The paper is available as a preprint at arXiv:2607.01153 (cs.CL primary, cs.AI
> and cs.SE cross-listed), first posted 1 July 2026, with a v3 replacement
> submitted 29 July 2026 carrying the current title and abstract. It has not been
> published or submitted elsewhere, and no part has appeared in conference
> proceedings. The benchmark items, rubrics, raw model outputs, run metadata,
> per-row judge labels for all six conditions, and the interval and pooling
> scripts are publicly released in the project repository. Two studies described
> in the paper as future work, an independent expert re-adjudication and a
> controlled contrast study, have not been run; the paper reports no results from
> either and says so.

**Reply "yes" to the drafts** and I'll do the template port, the reproducibility
checklist, and the full submission gate, then hand you a finished PDF and a
paste sheet for the wizard.
