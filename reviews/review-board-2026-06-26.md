# Review Board Synthesis: 2026-06-26

This was a simulated named-reviewer stress test. The names identify research profiles to emulate, not participation or endorsement.

## Board

- Percy Liang: benchmark architecture and transparency.
- Eric Wallace: instruction hierarchy and source authority.
- Kai Greshake: indirect prompt injection and app-level attack surfaces.
- Paul Roettger: refusal and over-refusal evaluation.
- Danqi Chen: LLM-as-judge validation.
- Aida Mostafazadeh Davani: annotator disagreement and uncertainty.
- Chris Potts: pragmatics, quotation, and NLP bridge.

## Consensus Strengths

- The core framing is strong: pass/fail safety labels collapse capability failure, refusal, policy ambiguity, source confusion, and evaluator instability.
- Minimal pairs are the right method for isolating source role, quotation, authority, scope, and pragmatic status.
- The criterion-conflict distinction is valuable, especially the decision to treat some disagreement as construct signal rather than annotation noise.

## Consensus Weaknesses

- The draft read too much like a benchmark proposal rather than an empirical artifact.
- Metrics were named but not operationalized with denominators, contrast scoring, refusal calibration, or judge-validation design.
- The seed examples risked looking prompt-only and toy-like without app-shaped wrappers.
- Refusal needed its own matrix rather than being folded into safety.
- Annotation needed annotator-level metadata and clearer adjudication criteria.
- The construct boundary needed an inclusion test and a clearer relation to instruction hierarchy.

## Reviewer-Specific Pressure

- Liang: release artifacts, raw-output transparency, schema excerpts, operational metrics.
- Wallace: distinguish hierarchy failures from pre-hierarchy source/status parsing and policy-boundary failures.
- Greshake: add webpage/email/tool-result/dummy-secret surfaces and explicit risk types.
- Roettger: add over-refusal, under-refusal, safe redirection, and policy-ambiguous refusal.
- Chen: validate LLM judges with prompt perturbations and fluent but wrong outputs.
- Davani: preserve annotator identity, role, confidence, repeated-item stability, and disagreement source.
- Potts: add an inclusion test and operational fields for quotation, speaker/source, commitment, and requested act.

## Actioned Changes

- Expanded `benchmark/items/seed-items.csv` from 12 to 18 items.
- Added schema fields for control dimension, source role, authority level, pragmatic status, response act, risk type, refusal outcome, and judge-validation flag.
- Added app-shaped seed cases for tool-output injection, dummy-secret exfiltration, and safe policy-analysis over-refusal.
- Updated `scripts/validate_items.py` to enforce the expanded schema and label inventories.
- Expanded `benchmark/rubrics/taxonomy.md` with an inclusion test and required control fields.
- Expanded `benchmark/rubrics/annotation-protocol.md` with annotator metadata, refusal matrix, and adjudication decision rules.
- Revised sections 3--7 to define the construct boundary, operational schema, development-pass design, judge-validation experiment, and metric denominators.

## Remaining Risks

- The paper still needs development-pass results before it is submission-ready as an empirical benchmark paper.
- Some seed pairs remain deliberately schematic; the next benchmark pass should add more tightly controlled app-level minimal pairs where the same payload and response space are held constant.
- The simulated board converged strongly on operationalization. Treat that convergence as a useful stress-test result, not as evidence of real reviewer consensus.
