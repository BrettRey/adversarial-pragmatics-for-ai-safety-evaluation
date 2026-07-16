# Freeze re-verify board synthesis (2026-07-16)

<!-- SUMMARY: focused 3-reviewer re-board after the estimand revision; 2 FREEZE-NOW (Chen, hostile) + 1 narrow FIX-FIRST (Wallace); all narrow fixes now applied; freeze-ready pending fixes 3-4 + tag · status: fixes-applied · updated: 2026-07-16 -->

Three reviewers who raised the deepest 2026-07-15 defects re-checked whether their
defect is resolved and whether the revision broke anything, source-grounded.

## Verdicts
- **Chen — FREEZE NOW.** Role-parity resolved (verified role-separated grading;
  recomputed 37/162; confirmed 7B compliant 7→38). Residuals: secondary write-up
  caveats only.
- **Hostile methodologist — FREEZE NOW.** Disagreement typology (2a) and freeze-
  object coherence (2b) both resolved; ran the synthetic workflow to confirm.
  One recoverable residual: author-summary robustness split not emitted.
- **Wallace — FIX-FIRST (narrow).** Authority sensitivity now confirmatory
  (C5/C6) and source-role/info-flow promoted; but C5/C6 are reference-flip (weak
  confirmer) while the gold-direction validity test he asked for by name was
  data-ready yet un-tiered — a post-freeze degree of freedom.

## Fixes applied (2026-07-16, after the re-board)
1. **Gold-direction match estimand (S5)** implemented in the analyzer (joins the
   frozen `seed-items.csv` gold; reference matches gold on both variants of a
   gold-differing pair) and pre-registered in the plan. Computable for
   task_success (9/9 pairs have a gold flip); disclosed as degenerate for
   policy_compliance (all-compliant gold, Wallace L5). [Wallace blocker]
2. **Author-summary robustness split** (`unanimous_comparable`,
   `majority_comparable`, `unanimous_candidate_revision`) now emitted, matching
   the plan's C3/C4 commitment. [hostile residual]
3. **Deferred-limitations block** added to the plan: prompt-robustness caveat
   (Chen L4), the compliant↔no_policy_or_authority_limit label-boundary reading of
   37/162 (Chen), taxonomy crosswalk (Wallace L2), no system tier (Wallace L4),
   zero-variance policy gold (Wallace L5).

## Status
All re-board asks addressed. Remaining before the tag are the two freeze-time
mechanical steps only: strip the plan's DRAFT text (fix 3) and re-stamp at the
tagged commit (fix 4). No open scientific defect.
