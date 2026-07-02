# Decisions

2026-06-26 — Treat the project as an empirical evaluation paper rather than a conceptual AI-and-language essay. Reason: the strategic value is a reusable safety-evaluation artifact: taxonomy, benchmark, annotation protocol, scoring metrics, and policy/eval memo.

2026-06-26 — Use the short durable project folder `adversarial-pragmatics-for-ai-safety-evaluation` and put the full technical title in the manuscript. Reason: folder names should stay scannable while the paper title can carry the benchmark subtitle.

2026-06-26 — Keep all provided external links in a source-verification queue rather than citing their claims immediately. Reason: organizational agendas, job postings, and safety reports are time-sensitive and must be checked before becoming paper claims.

2026-06-26 — Start the benchmark with harmless payloads and minimal pairs. Reason: the paper needs safety-relevant language-mediated structure without committing operationally harmful content or raw red-team material on day one.

2026-07-01 — Submit the arXiv version as a TeX source archive, not as a generated PDF. Reason: arXiv requires source for TeX-generated work, and the main paper plus supplement can be represented as two ordered top-level TeX files.

2026-07-01 — Make the arXiv source package self-contained with explicit top-level bibliography declarations and bundled open fonts. Reason: arXiv's scanner missed bibliography declarations hidden in the shared preamble, local `.bbl` files were incompatible with TeX Live 2025, and arXiv's workers did not provide the local font names used by the house-style preamble.

2026-07-01 — Use CC BY with primary category `cs.AI`, secondary `cs.CL`, and third category `cs.SE` for the arXiv submission. Reason: the paper is an AI safety/evaluation artifact grounded in computation-and-language methods, with a reusable software/eval infrastructure component.
2026-07-01 — Re-reported judge validation and disclosed pilot circularities after the second review board (reviews/review-board-2026-07-01.md). Added majority-class base rates, Cohen's kappa, and minority-class recall to the judge tables (main §6, supplement); recomputed all values from the artifact confusion matrix, not from reviewer arithmetic. Rewrote §1 box, §6 prose, and supplement conclusion: raw agreement tracks skewed base rates; triage on this pilot belongs to the rule-aided pass; the judge pass is a negative result motivating the validation protocol. Disclosed in §6/§7a/supplement: judge is one of the three evaluated models (18/54 self-judged rows), judge prompt contained the gold expected-behaviour field, and the single adjudicator is the item author. Fixed nested \citep in §1. Reason: seven of eight board reviewers found the raw-agreement reporting misleading against the paper's own cited methodology (Artstein & Poesio); fixing before arXiv announcement avoids v1 carrying the overclaim. Deeper fixes (second adjudicator, item repairs, projection statements) deferred to the development pass / v2.
2026-07-01 — arXiv assigned the permanent identifier `2607.01153` to submission `submit/7776593`. Reason: the paper is now a public preprint, so downstream surfaces should cite `arXiv:2607.01153` and reserve the submission-system id for archive/reference only.
