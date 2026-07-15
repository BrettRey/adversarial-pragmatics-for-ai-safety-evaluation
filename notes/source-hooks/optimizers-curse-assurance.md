# Source hook: optimizer's curse -> assurance strand (delegation- & evidentiary-assurance)
- Central note: `literature/smith-winkler-2006-optimizers-curse.notes.md`
- Cite: Smith & Winkler 2006 (`smith2006optimizersCurse`); optionally Gelman 2026 post (`gelman2026optimizersCurse`). Both in `references-local.bib`.

**Why these papers care.** Defender-side optimizer's curse: picking the configuration that *looks safest* on a finite eval systematically overstates deployed safety, for the same selection-on-max reason. That gives the assurance framing a named, citable statistical reason to demand skeptical discounting before certifying a system. "Disciplined skepticism" is Smith & Winkler's own phrase for the Bayesian fix.

**Where it plugs in.**
- `evidentiary-assurance.tex` (sufficiency test, evidence primitives): a pass selected as the best-looking option is weaker evidence than its face value; a sufficiency test should account for selection over configurations/evals.
- `delegation-assurance.tex` (framework, implications): certifying on the max-looking pass rate is exactly the failure mode; the remedy is shrinkage / hold-out before the assurance claim.

**Verify before citing:** Gelman's exact post wording (couldn't fetch, 403). Smith & Winkler DOI/pages are grounded.
