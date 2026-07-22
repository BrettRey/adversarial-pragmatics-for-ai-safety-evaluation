# Source hook: optimizer's curse -> benchmark/eval paper (adversarial-pragmatics-for-ai-safety-evaluation.tex)
- Central note: `literature/smith-winkler-2006-optimizers-curse.notes.md`
- Cite: Smith & Winkler 2006 (`smith2006optimizersCurse`); optionally Gelman 2026 post (`gelman2026optimizersCurse`). Both in `references-local.bib`.

**Why this paper cares.** Any reported "best model / best prompt / best judge / best schema on our benchmark" is optimistically biased: selecting the max over noisy scores preferentially picks options whose noise ran high, so the winner disappoints in deployment. This is selection bias, not distribution shift.

**Sharpest bite: LLM-as-judge.** The project commits to validating the judge, not assuming it. If a judge/rubric is chosen because it maximises human agreement across candidates, its agreement is not an unbiased estimate of that judge's reliability. Same logic hits the study-a schema iteration (v7): the agreement of the selected schema is inflated.

**What to do.** Report shrunk estimates with credible intervals rather than naive maxima; use held-out or nested validation for the chosen judge/schema; frame the benchmark-to-deployment gap as partly the optimizer's curse. Natural home: `scripts/analyze_independent_reassessment.py`, `simulate_independent_reassessment.py`.

**Verify before citing:** Gelman's exact post wording (couldn't fetch, 403). Smith & Winkler DOI/pages are grounded.
