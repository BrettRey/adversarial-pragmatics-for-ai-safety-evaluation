# Source hook: Ashokkumar et al. 2026 (Nature) — LLMs predict social-science experiment results

**Source:** Ashokkumar, Hewitt, Ghezae & Willer, *Nature* 2026, doi:10.1038/s41586-026-10742-x. Central note: `literature/ashokkumar_etal_2026_llms_predict_social_science_experiments.notes.md`.

**Why this project cares:** a clean, high-profile worked case of the project's own line that validity is a property of an interpretation-and-use, not intrinsic. GPT-4-derived effect predictions are valid for *discrimination* (r ≈ 0.85–0.90) but *invalid for absolute magnitude* — they overestimate ~2× and need recalibration. Same result, two validities.

**Reusable methods:**
- Published-vs-unpublished-by-training-cutoff coding as a **training-data-contamination control** for out-of-distribution claims.
- Correlation (discrimination) vs regression slope / r.m.s.e. (calibration) reported separately — a template for keeping ranking and magnitude claims typed apart, which matches this project's typed-claims discipline.

**Caveat before citing:** their domain is attitude/survey experiments, not language-mediated-control eval; use as an analogy for the validity/calibration distinction, not as evidence about pragmatic-control benchmarks.
