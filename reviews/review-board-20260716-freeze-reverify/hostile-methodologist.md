# Freeze re-verification: Study A pre-registration (hostile measurement methodologist)

<!-- SUMMARY: re-verification of the Study A freeze revision against the same reviewer's 2026-07-15 defects (2a disagreement typology, 2b freeze-object coherence); verdict FREEZE NOW; both prior defects resolved, one minor recoverable residual (author-agreement robustness split not pre-computed in the summary CSV) · status: complete · updated: 2026-07-16 -->

Same reviewer as `reviews/review-board-20260715-freeze-readiness/opus-hostile-methodologist.md`. Brief: check whether my two defects (2a majority-vote disagreement collapse; 2b incoherent freeze object) are actually fixed in the frozen text and code, and whether the revision broke anything. I read `analysis-plan.md` in full, `analyze_independent_reassessment.py`, `FREEZE-MANIFEST.json`, `build_study_a_manifest.py`, and `revision-ledger.md`; re-ran `--verify`; recomputed the judge-cell claim from the frozen comparators; and ran the synthetic end-to-end workflow to confirm the new artifacts materialize. Every claim below is checked against the files, not the plan's self-summary.

---

## 1. Is defect 2a (disagreement typology) resolved? YES.

My required fix had three parts. All three are in the frozen path.

**(i) Stable-but-contested items are surfaced as their own signal, neither folded into nor silently dropped from the co-primary.**

- The analyzer computes a per-row `substantive_contested` flag: `substantive_distinct = sorted(set(values) - ESCAPE_VALUES); substantive_contested = len(substantive_distinct) >= 2` (`analyze_independent_reassessment.py:280-282`). It fires whenever raters split across two or more substantive labels, regardless of realized N or parity.
- These rows are written to a dedicated artifact `contested-items.csv` (`:373-395`) carrying `label_counts`, `substantive_labels`, `stability`, `independent_reference`, and a `feeds_co_primary` boolean (`:385-386`).
- The count is also reported per criterion alongside yield in `agreement-by-criterion.csv` (`substantive_contested`, `:359`), with the code comment stating it is "reported separately, never folded into or silently dropped from the yield" (`:356-358`).
- Plan side: estimand **S4** (`analysis-plan.md:122`) registers "Stable-but-contested items ... rows where evaluators split across ≥2 substantive labels ... construct-boundary signal ... reported as its own estimand, never folded into or dropped from yield," with `contested-items.csv` named as the output.

This directly kills the laundering I flagged. I confirmed it on the synthetic run:
- `SYN-014 / task_success`: labels `partial:1; success:2` → `majority`, reference `success`, **`feeds_co_primary=True`**. The exact "2-1 substantive split enshrined as a clean reference" case. It is now flagged contested and marked as feeding the co-primary, so a reader can see how many yield references are actually contested.
- `SYN-007 / task_success`: labels `partial:1; success:1` → `tie`, `no_consensus`, **`feeds_co_primary=False`**. The exact "even split dropped as missing" case. It is now flagged contested and marked as NOT feeding.

The identical construct-level disagreement (success vs partial) appears in both forms in one artifact, distinguished by whether N-parity laundered it into the co-primary. That is precisely the outcome my review demanded and the frozen path did not previously produce.

**(ii) C1-C4 are reported split by reference type, not with unanimous and majority collapsed.**

- `agreement-by-criterion.csv` emits `unanimous`, `majority`, `stable_substantive`, `unanimous_substantive`, `majority_substantive`, and `stable_escape` as separate columns (`:343-355`). Escapes are pulled out of the substantive count (`stable_escape = len(stable) - stable_substantive`, `:326`), and majority is separated from unanimity (`majority_substantive = stable_substantive - unanimous_substantive`, `:335`).
- Plan side: the estimand-table preamble commits to this ("All yield and agreement rows are reported split by reference type (unanimous / substantive-majority / escape), never with unanimous and majority collapsed into one 'stable' bucket," `analysis-plan.md:93-96`), and C1/C3 carry "split unanimous vs majority" / "split by reference robustness" (`:101, :103`).
- Synthetic confirmation: e.g. `source_role_clarity` shows `stable_substantive=44` with `stable_escape=6` broken out, and `task_success` shows `substantive_contested=4` reported next to `yield=0.944`.

**(iii) A load-bearing "yield = convergence, not correctness" statement, with recall conditioned on reference robustness.**

- The standing statement is real and woven through, not a footnote: `analysis-plan.md:157-167` ("A stable reference means the evaluators converged, not that the label is right ... low yield is *not* evidence the rubric failed ~-- it may be the benchmark locating a genuine construct boundary ... `consensus()` is a vote count; it is not a validity oracle, and nothing in this plan treats the panel as ground truth"). It is referenced again in the estimand-table preamble (`:96`) and ties explicitly to S4.
- Crucially it names the conditioning: "Every recall / candidate-revision / judge-agreement claim (C3, C4, S1-S3) is conditioned on **reference robustness** (unanimous vs majority; N=3 vs the N=2 fallback)" (`:163-166`).
- The judge path mechanizes this. `judge-vs-independent-summary.csv` reports `eligible_unanimous_refs` and `eligible_majority_refs` per criterion (`analyze_independent_reassessment.py:887-892`), so a recall number is read against the robustness of the references it was scored on. `judge-minority-class-recall.csv` reports per-class recall with an `is_minority` flag (`:910-924`). On the synthetic run this surfaces exactly the failure S3 targets: `policy_compliance / noncompliant` (minority) recall `0.000` against a `task_success` reference set that is 50 unanimous / 1 majority. My 2a third bullet ("S3/RQ4 recall treats a possibly-2-person reference as ground truth with no robustness gate") is answered: the robustness of every reference behind a recall figure is now on the same row.

Verdict on 2a: **resolved.** The frozen path now does what the project's "treat disagreement as data" instruction requires and what majority-vote alone could not.

---

## 2. Is defect 2b (freeze-object coherence) resolved? YES.

- **`git_commit` removed.** No `git_commit` field in `FREEZE-MANIFEST.json`; the only surviving mention is the explanatory comment in `build_study_a_manifest.py:82-87` ("a manifest cannot reference the commit that contains it ... The authoritative commit pointer is the freeze git tag, not a field inside the hashed payload"). This is the correct fix: the self-referential pointer that failed its own `--verify` is gone, and the git tag is now the sole commit anchor.
- **`seed-items.csv` frozen.** `benchmark/items/seed-items.csv` is in `FROZEN_ARTIFACTS` (`build_study_a_manifest.py:41`) and in the manifest (`FREEZE-MANIFEST.json:20-23`, sha `96e1ef4b...`). Good call independent of my review: it carries the `expected_behavior` gold and per-item author labels that the C3/C4 author comparator and the Option-B "laundered answer key" argument both depend on, so freezing the analysis path without it would have left the author comparator ungrounded.
- **`--verify` clean.** `python3 scripts/build_study_a_manifest.py --verify` → `OK: all 9 frozen artifacts match the manifest.` (exit 0). Re-run after the synthetic workflow: still clean (the run writes only to the gitignored `_runs/synthetic`).

Verdict on 2b: **resolved.** The freeze object is now internally consistent.

The two remaining 2b items from my original review (strip the DRAFT/self-negating language; re-stamp at the tagged commit) are correctly deferred, not ignored. No git tag exists yet, so the freeze is not consummated; the DRAFT label is currently accurate, and the revision ledger (which logs *post-freeze* deviations) is correctly empty. Stripping DRAFT changes the plan hash, so it must be done together with a manifest rebuild at tag time — which is exactly what the "Remaining before freeze" section (`analysis-plan.md:196-200`) and the deferral note specify. The deferral is sound.

---

## 3. Did the revision introduce anything new or wrong?

Nothing blocking. Three notes, in decreasing severity.

**(a) One genuine residual (minor, recoverable, non-blocking): author-agreement robustness split is committed in the plan but not pre-computed in the summary CSV.** The plan's C3/C4 say author agreement is reported "split by reference robustness" (`analysis-plan.md:103-104`) and the standing statement names "candidate-revision" among the robustness-conditioned claims (`:163-166`). The judge path mechanizes this split (`eligible_unanimous_refs`/`eligible_majority_refs`); the author path does not. `author-label-revision-summary.csv` reports `retained` / `candidate_revision` / `candidate_revision_rate` and the at-stake breakdown, but no unanimous-vs-majority split (`analyze_independent_reassessment.py:775-797`). This is not a hole that lets the confound back in: the per-row `author-label-comparison.csv` carries `stability` on every row (`:704-730`), the split is a deterministic function of that frozen field, and the plan text binds the analyst to report it. So there is no new researcher degree of freedom, only an asymmetry between the judge and author summaries. Worth a five-line addition (group candidate_revision by unanimous/majority to match the judge summary and honour C3/C4 as written), but it does not block the tag.

**(b) The judge comparators were regenerated role-separated (7A) after stamp 1, and the numeric claim checks out.** Both frozen comparators are now `prompt_variant = option_a_v7_roleseparated`, 54 rows each, zero parse errors. I recomputed the plan's headline claim from the frozen CSVs: the two judges differ on **37/162 label cells** (task_success 11, policy_compliance 21, refusal_outcome 5) = 22.8%, matching "37/162 (~23%)" (`analysis-plan.md:86`) exactly; and the 7B `policy_compliance` distribution is `compliant:38`, matching the "compliant 7→38" claim (`:85`). The regeneration is disclosed in the plan narrative (`:78-87`), the manifest hashes the regenerated files, and `--verify` is clean, so this is a consistent pre-freeze change, not a stale-pointer repeat of the old 2b failure. (For the record, my prior review verified 26/162 against the *pre*-role-separation comparators; the change to 37/162 is the documented effect of fixing the joint-pass cross-role confound, not drift.)

**(c) Cosmetic dating drift.** The ledger reads "freeze stamp 1 created 2026-07-15," but the comparators were regenerated 2026-07-16 and the plan documents a 07-16 change. Given the deferral, this is harmless: the tag-time re-stamp (deferred fix 4) refreshes the manifest and its dating. Not a defect, just a note for whoever executes the tag.

I checked the new `substantive_contested` code for bugs: it operates on in-memory booleans before any CSV stringification (`:298, :359, :389`), and it correctly treats `policy_ambiguous`/`genuinely_ambiguous` as substantive (they are not in `ESCAPE_VALUES`), consistent with multiverse axis A4 (`:140`) which keeps substantive ambiguity eligible by default. No defect. The synthetic workflow runs to completion (exit 0) and emits all new artifacts.

---

## 4. Sign-off

**FREEZE NOW.** Both defects I raised (2a disagreement typology, 2b freeze-object coherence) are resolved in the frozen text and code; proceed to the tag via the already-planned DRAFT-strip + manifest re-stamp, and fold the author-agreement robustness split (3a) into that same pass.
