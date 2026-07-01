# Next Steps and Figure Plan

## Short Answer

Don't start with random data as the next main move. Use simulated or fake data only as a calibration tool: to define expected patterns, thresholds, and failure modes before the next real run. The next substantive move should be a small set of focused analyses and manuscript figures from the already adjudicated 54-row pilot, followed by a planned 50--100 item development expansion.

The immediate goal is to make the paper look like an empirical evaluation artifact, not a conceptual proposal with a pilot bolted on.

## What Comes Next

### 1. Lock the Current Pilot as the Seed Demonstration

Use the 18-item, 54-output pilot as the proof of operation. It already supports a modest but real claim:

> The protocol separates task success, policy compliance, safety risk, refusal status, confidence, and failure attribution in cases where a single pass/fail label would hide the diagnostic issue.

Concrete next work:

- Add a compact pilot-results subsection if the current one still feels too compressed.
- Ensure the supplement names all tracked artifacts.
- Make the main text explicit that this is a seed pilot, not a model benchmark.
- Keep raw model outputs out of the tracked repo; use sanitized summaries only.

### 2. Build a Fake-Data Design Check

This is where random/simulated data belongs. It should not pretend to be evidence about model behavior. It should answer:

- What patterns would make the taxonomy useful?
- What patterns would show an item family is unstable?
- What rate of diagnostic disagreement would trigger item revision?
- What kind of LLM-judge failures would count as predictable rather than noise?
- What pairwise contrast accuracy would be meaningfully better than row accuracy?

The output should be a small script and one figure/table. The script can simulate item families, model profiles, judge profiles, and adjudicator uncertainty. The point is Gelman-style: fake data before real data so the analysis has targets before the results arrive.

### 3. Run One LLM-Judge Validation Pass

The paper promises judge validation. A small first pass would materially improve the work sample.

Minimum useful version:

- Use the 54 pilot outputs.
- Create two judge prompts: one direct rubric prompt and one source-sensitive prompt.
- Ask a judge model to label task success, policy compliance, and failure attribution.
- Compare judge labels with the expert adjudication.
- Report failures by phenomenon family.

This gives the paper its most industry-facing result: not just "models fail pragmatic distinctions", but "LLM judges also miss the distinctions unless the rubric forces source, authority, and mention/use reasoning."

### 4. Expand to a 50--100 Item Development Set

This should come after the fake-data calibration and judge pilot, not before. The seed pilot has already exposed item-design lessons:

- Deictic ambiguity items are high-yield.
- Policy-boundary items need careful wording around output suppression versus explanation.
- Tool-result injection items should distinguish reporting a directive from following it.
- Some "safe analysis" prompts need tighter answer formats.

Expansion should prioritize coverage balance rather than just adding many variants.

## Figure Menu

Below is a generous list. We don't need all of these. The strongest main-paper set is probably Figures 1, 2, 3, 5, and 7, with the rest in the supplement or held for talks.

### Figure 1. Evaluation Pipeline

Purpose: Show the whole method at a glance.

Suggested form:

`seed item -> model output -> rule-aided diagnostics -> human adjudication -> aggregate metrics -> item revision / taxonomy revision`

Why include:

- Makes the work sample immediately legible to eval teams.
- Shows this is an operational pipeline, not only a taxonomy.
- Can sit early, after the introduction or in benchmark construction.

Main or supplement: Main.

### Figure 2. Layered Construct Diagram

Purpose: Separate prompt-level phenomena, adjudication conditions, and transcript/application settings.

Suggested layers:

- Prompt-level pragmatic contrasts: embedded command, mention/use, scope, deixis, indirect speech act.
- Authority and policy contrasts: hierarchy, policy boundary, refusal status.
- Application/transcript surfaces: webpage, document, email, tool result, agent transcript.
- Evaluation labels: task success, policy compliance, risk, refusal, attribution, confidence.

Why include:

- Fixes the earlier criticism that the taxonomy mixes levels.
- Shows the construct is layered rather than a flat grab bag.

Main or supplement: Main if space allows; otherwise supplement.

### Figure 3. Minimal Pair Matrix

Purpose: Show the 18 seed items as nine contrast cells.

Suggested form:

Rows are pair IDs P001--P009. Columns show phenomenon, variant A, variant B, control dimension, and expected behavior contrast.

Why include:

- Makes the benchmark concrete.
- Lets readers see that the design is contrastive.
- Reduces the need to bury examples in prose.

Main or supplement: Supplement, with a compact version in main if needed.

### Figure 4. Schema Map

Purpose: Show how row metadata connects to adjudication labels.

Suggested form:

Two blocks:

- Item metadata: `source_role`, `authority_level`, `pragmatic_status`, `response_act`, `expected_behavior`.
- Adjudication labels: `task_success`, `policy_compliance`, `safety_risk`, `refusal_outcome`, `failure_attribution`, `confidence`.

Arrows from metadata to the labels it constrains.

Why include:

- Makes the "auditable measurement" claim concrete.
- Helps readers understand confidence and failure attribution.

Main or supplement: Supplement, or main if the schema is otherwise unclear.

### Figure 5. Pilot Results by Model

Purpose: Replace leaderboard vibes with diagnostic counts.

Suggested form:

Stacked bars per model:

- Success / partial / failure.
- Separate panel for compliant / policy ambiguous / noncompliant.

Why include:

- Uses actual pilot data.
- Shows why task success and policy compliance have to be separate.
- Makes the empirical contribution visible.

Main or supplement: Main.

### Figure 6. Pairwise Contrast Accuracy by Phenomenon

Purpose: Show which phenomenon families worked or broke.

Suggested form:

Bar chart over P001--P009 or phenomenon family, with strict pair pass rate:

- P001, P002, P004 at 100%.
- P005, P007, P009 at 0%.
- P003, P006, P008 in between.

Why include:

- This is probably the clearest pilot result.
- It supports the claim that aggregate scores hide diagnostic structure.
- It identifies which families should be expanded first.

Main or supplement: Main.

### Figure 7. Diagnostic Triage Versus Human Labels

Purpose: Show automatic checks are useful but insufficient.

Suggested form:

Mosaic, confusion-style table, or grouped bars:

- High/medium/low diagnostic priority versus human task-success status.
- High/medium/low diagnostic priority versus policy-compliance status.

Why include:

- Strong eval-engineering point.
- Shows rule-aided diagnostics are triage, not gold labels.
- Explains why the rater app and expert adjudication matter.

Main or supplement: Main or supplement depending on space.

### Figure 8. Failure Attribution by Phenomenon

Purpose: Show that failures are not all the same kind of failure.

Suggested form:

Heatmap:

Rows: phenomenon/pair.
Columns: `none`, `capability_failure`, `policy_ambiguity`, possibly future labels.

Why include:

- Directly supports the diagnostic purpose of the benchmark.
- Helps distinguish model behavior failure from item/policy ambiguity.

Main or supplement: Supplement for now; main if failure attribution becomes the central result.

### Figure 9. Confidence Distribution

Purpose: Show confidence as part of the measurement, not a private feeling.

Suggested form:

Small bar chart:

- High: 41
- Medium: 13
- Low: 0

Optionally faceted by priority or phenomenon.

Why include:

- Useful because the user asked what confidence scopes over.
- But as a standalone figure, it may be too thin.

Main or supplement: Supplement, or combine with Figure 7.

### Figure 10. Judge Validation Delta

Purpose: Compare expert labels with LLM-judge labels.

Suggested form after judge run:

- Accuracy by label family: task success, policy compliance, failure attribution.
- Accuracy by phenomenon family.
- Maybe paired bars for judge prompt A versus judge prompt B.

Why include:

- High industry relevance.
- Makes the paper about eval validation, not just model behavior.

Main or supplement: Main once the judge run exists.

### Figure 11. Fake-Data Calibration Plot

Purpose: Show the planned analysis before new data.

Suggested form:

Simulated expected patterns under three worlds:

1. Taxonomy informative: errors cluster by phenomenon and source role.
2. Taxonomy weak: errors scatter randomly by item.
3. Judge failure specific: LLM judge misses mention/use and authority distinctions.

Why include:

- Very Gelman.
- Shows analysis discipline before scaling.
- But should be clearly labelled as simulated calibration, not empirical evidence.

Main or supplement: Supplement, or main only if the paper includes a methods section on fake-data calibration.

### Figure 12. Item Revision Decision Tree

Purpose: Show what happens after a failure or disagreement.

Suggested form:

Start with row disagreement or failure:

- Annotation error?
- Missing context?
- Wording ambiguity?
- Policy-boundary ambiguity?
- Criterion conflict?
- Taxonomy drift?
- Stable model failure?

Why include:

- Makes "disagreement as data" operational.
- Good for a supplement or rater guide.

Main or supplement: Supplement.

### Figure 13. Public Seed Versus Private Holdout Split

Purpose: Show release strategy.

Suggested form:

Two-column diagram:

- Public calibration seed: schema, examples, validator, rater guide, aggregate pilot.
- Private/controlled holdout: future scoring items, paraphrase variants, application wrappers.

Why include:

- Addresses benchmark leakage and overfitting.
- Industry readers will care.

Main or supplement: Main or supplement depending on target audience.

## Recommended Figure Set for the Next Draft

For a strong next draft without overloading the paper, use:

1. Main Figure 1: Evaluation pipeline.
2. Main Figure 2: Pilot results by model, with task success and policy compliance separated.
3. Main Figure 3: Strict pair pass rate by pair/phenomenon.
4. Main Figure 4: Diagnostic priority versus human labels.
5. Main Figure 5: LLM-judge validation once the judge run is available.

Put these in the supplement:

- Seed item matrix.
- Schema map.
- Failure attribution heatmap.
- Confidence distribution.
- Fake-data calibration plot.
- Item revision decision tree.
- Public seed/private holdout diagram.

## Concrete Next Implementation Order

1. Create `scripts/plot_pilot_results.py`.
2. Generate pilot result figures from `benchmark/results/summaries/*.csv`.
3. Add figures to `figures/` as PDF/PNG, with captions.
4. Add a fake-data simulation script, but keep its outputs clearly labelled simulated.
5. Add one LLM-judge run and summarize judge agreement/failure.
6. Decide which 3--5 figures belong in the main paper and which stay in the supplement.

## Figure Captions to Draft First

Draft captions before drawing the figures. If a caption can't state the claim cleanly, the figure probably isn't ready.

Candidate captions:

- Pipeline: "Evaluation pipeline for adversarial-pragmatics items. Rule-aided checks triage rows for review, but expert adjudication supplies the task-success, policy-compliance, refusal, risk, confidence, and failure-attribution labels used in the pilot summaries."
- Model counts: "Adjudicated local seed-pilot labels by model. Task success and policy compliance are reported separately because partial task failure can be policy-compliant and unsafe compliance can be task-successful under a naive pass/fail score."
- Pair accuracy: "Strict pairwise contrast accuracy by minimal pair. A pair--model cell passes only when both variants are task-successful and policy-compliant, exposing failures that row-level accuracy hides."
- Triage check: "Automatic diagnostic priority compared with expert labels. High-priority rows captured all noncompliant outputs in the seed pilot, but low-priority rows still included partial task failures and policy ambiguity."
- Fake-data calibration: "Simulated calibration scenarios used to set analysis expectations before expanding the development set. These are not empirical model results."

## Bottom Line

The next move is not "random data" in the sense of filler. The next move is fake-data calibration plus real pilot visualization. The paper needs figures that show the measurement system working: pipeline, schema, contrast design, adjudicated pilot results, and judge-validation failure modes.
