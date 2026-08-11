# Source hook: Bulut 2026 inter-rater reliability -> AP judge validation
<!-- SUMMARY: independent replication of AP's own judge finding in an unrelated domain — minority class missed, raw agreement high, κ at chance across five labellers incl. Fable 5 and GPT-5.5 · status: uncited, unrefereed source · updated: 2026-08-06 -->

- **Central note:** `literature/bulut_2026_inter_rater_reliability_llm_annotation.notes.md`
- **Companion hook:** the Alloula et al. 2026 note (`literature/2606.07874v1.notes.md`) routed here 2026-07-14 on judge rigidity; this is the reliability-side counterpart.
- **Source:** Levent Bulut, "Inter-Rater Reliability of LLM and Rule-Based Annotation for Inferential Narrative Features," v1.0, August 2026. Self-published, no DOI or venue.

**Why it matters here: it is the same finding, from outside.** AP's own LLM-judge validation showed a rubric-aided judge missing the safety-relevant minority classes under favourable conditions. Bulut, working on Turkish narrative annotation with no connection to safety evaluation, finds the identical structure: the minority class is missed, raw agreement stays high (74.7–84.5%), and κ sits at chance (0.004, 0.015, 0.000, 0.019, 0.027 across five labellers). One rule, five machines, positive counts of 0, 1, 40, 72, 78 against a human 9.

That independence is the value. AP currently supports its judge claim with its own pilot in its own domain, where a reader can say the rubric or the safety framing did it. A second instance in computational narratology makes the better claim available: this is a property of judge-based measurement under class imbalance, not an artefact of safety rubrics.

**The quotable line, for the pass-fail argument.** Bulut §5: "Any reader — or benchmark leaderboard — that ranks these systems by raw agreement will rank them by their willingness to say absent." That is AP's evaluator-side limit stated as a scoring-design fact, and it generalises to any benchmark reporting a single agreement or accuracy figure over a skewed class. Note ChatGPT 5.5 posts the *best* overall raw agreement in his data (84.5%) alongside a chance-level κ on the target rule — a leaderboard would rank it first.

**Where it could go.**
- Flagship §2 (pass-fail) and §7a (planned judge-validation experiment): as the independent-domain corroboration, and as a reason the planned experiment should report class distributions, not just agreement.
- Delegation Assurance §2.5 (judge reliability): Bulut's positive control matters here — *simile*, a feature reducing to a short list of function words, scored κ = 1.00. The pipeline agrees perfectly when the feature is a string and collapses when it is inferential. That is a cleaner statement of where judge delegation is safe than a blanket reliability caveat, and it is a licence boundary, not a performance number.
- Evidentiary Assurance: his three-conflict declaration on page 1 (he designed the rules, was sole rater in Study 1, had Claude assist the analysis while Claude was a scored system, and the corpus is his own) is a compact worked example of a declaration that names dependence rather than asserting independence. Possible illustration if EA's declaration section wants a real one.

**Caveats before citation.** Self-published v1.0, unrefereed, no DOI, inside the author's own framework ("Bulut Doctrine"). Two of his own figure sets are derived rather than raw: Gemini and Grok confusion counts were recovered arithmetically after the per-scene labels were lost, and the detector's Study 2 labels are a reconstruction. He flags both (§7.3). Cite for the measurement pattern, not as an authority, and check for a later version first.
