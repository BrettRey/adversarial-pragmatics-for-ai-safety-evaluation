# Study A freeze-readiness review (simulated Percy Liang)

<!-- SUMMARY: freeze-readiness sign-off on tagging benchmark/study-a/analysis-plan.md as a pre-registration; verdict FIX-FIRST on manifest git_commit provenance mismatch · status: review · updated: 2026-07-15 -->

*Simulated persona for stress-testing, not the real Percy Liang. Reviewer lens: LM evaluation, benchmark architecture, transparency, multi-metric evaluation, metric validity, reproducibility, and aggregate numbers that hide trade-offs.*

*Scope: this is a freeze-readiness review, not a paper review. The eight prior blockers (fixed-denominator yield, escape exclusion, judge majority-baseline plus minority recall, item-macro / effective-N, model-mixed blinding, hashed freeze manifest) are treated as closed and are not re-litigated except where a new defect sits inside one of them.*

---

## 1. Faithful restatement (what is being frozen, and what it commits you to)

You are about to git-tag `benchmark/study-a/analysis-plan.md` (plus a hashed manifest) as a **pre-registration**: the analysis path is locked *before* the first external evaluator return is opened. This is the right shape for the study. The outcome (the independent human reference labels) does not exist yet; you are committing to how you will analyze it before you can see it, which is the whole point of a pre-registration and the only way the confirmatory claims carry weight.

Concretely, freeze stamp 1 hashes eight artifacts into `FREEZE-MANIFEST.json`: the analysis plan, the v7 schema, the two frozen Mistral judge comparators (7B and 24B, Option-A information set), and four scripts (`run_study_a_judge.py`, `analyze_independent_reassessment.py`, `ingest_independent_reassessment.py`, `build_independent_reassessment.py`), plus the two Ollama model digests. It explicitly defers three artifacts to stamp 2 (`not_yet_frozen`: the real row map, the blind-package presentation order, the frozen author snapshot), to be added when the real packages are built.

The commitments I read as binding once the tag exists:

- **Estimands.** Co-primary is C1/C2 (independent-reference *yield* for `task_success` and `policy_compliance` over the fixed 54-row set), and C3/C4 (independent-vs-author agreement on the stable-substantive subset). `refusal_outcome` is secondary; judge-vs-reference (S2/S3) is secondary and reported per judge with a majority baseline and per-class recall. Seven scalar fields plus source-role structure are exploratory and labeled as such.
- **Reference rule.** `MIN_REFERENCE_RATERS = 2`; target 3/role, 2-of-3 majority sets the reference, fall back to 2-as-unanimity, no invented tie-break (`consensus()` returns `tie` / `no_majority` / `insufficient_raters` as non-stable). Escapes (`item_problem`, `insufficient_visible_context`) are stable-but-not-substantive and excluded from comparator accuracy, not scored as labels the judge/author had to match.
- **Inference discipline.** Primary results are fixed-set counts and fractions, no population interval; any interval must cluster by item or pair; row-micro accuracy and modal share are descriptive. The analyzer reports item-macro accuracy, `n_items`, `n_pairs`, and an availability flag alongside every judge number.
- **Multiverse.** Five pre-committed axes (A1 P008, A2 reference rule, A3 missingness, A4 escape handling, A5 judge capability plus information-set ladder), reported as a grid, with an explicit obligation to flag any cell that flips the qualitative conclusion.
- **Tamper-evidence.** `build_study_a_manifest.py --verify` detects drift; `revision-ledger.md` logs any post-freeze change with before/after hashes.

I checked the parts that are cheap to check and they hold up. All eight current file hashes match the manifest; `--verify` returns `OK: all 8 frozen artifacts match`. The judge prompt builder (`build_prompt`) passes only `prompt` and `response`, so the Option-A no-leak claim is real: `expected_behavior`, the taxonomy fields, and the identifiers never reach the judge. The plan's headline judge-divergence number ("26/162 label cells, ~16%") reproduces exactly from the two CSVs (26/162 = 16.0%; one blank cell in the 7B run from a `not_applicable` emission correctly rejected to blank rather than mislabeled). The small-N honesty is genuine, not decorative. This is a serious evaluation artifact, and most of it is ready.

That is the version of the design I would want its authors to endorse. Now the objection.

## 2. Sign-off verdict

**FIX-FIRST.** One integrity defect in the freeze object must be reconciled before the tag is cut. It is cheap now and expensive to walk back after the tag exists.

## 3. The single most important remaining defect

**`FREEZE-MANIFEST.json` records `git_commit: fd20944...`, but its hashed payload is the tree at `HEAD` = `1dee5cd`, not `fd20944`. The manifest's own recorded commit fails the manifest's own `--verify`.**

Evidence (run in-repo today):

- `build_study_a_manifest.py` sets `git_commit` via `git rev-parse HEAD` *at build time* (line 78-88), i.e. before the commit that will contain the manifest.
- The manifest and the two script fixes for "blockers 4-7" landed together in commit `1dee5cd`, whose parent is `fd20944`. So the manifest captured its parent, `fd20944`, while hashing the *edited* scripts that only exist at `1dee5cd`.
- At `fd20944`, two of the eight frozen artifacts have different content than the manifest records:
  - `analyze_independent_reassessment.py`: `fd20944` = `55be03a0...`, manifest/HEAD = `00a58897...`
  - `build_independent_reassessment.py`: `fd20944` = `2cce45fc...`, manifest/HEAD = `729d5145...`
- Consequence: the natural auditor move, `git checkout fd20944 && python3 scripts/build_study_a_manifest.py --verify`, prints **FREEZE DRIFT DETECTED** on those two files. Verify passes only at `HEAD`, which the manifest does not name.

Why this must be fixed *before* the tag, not after. A pre-registration's entire value is that an outside party can point at one immutable commit and reproduce the frozen path. This manifest names a commit where that reproduction fails, and the field is labeled `git_commit`, which invites exactly the checkout-and-verify an auditor performs. For a paper whose thesis is "reliable, auditable evaluation," shipping an auditability artifact that fails its own recorded-commit audit is the precise embarrassment to avoid, and it surfaces *later*, when someone reproduces, not now. Once you tag, the wrong pointer is baked into the tag; correcting it means moving an annotated tag (defeating the immutability claim) plus a revision-ledger entry. Before the tag it is a rebuild.

The underlying bug is structural, not a typo: `git_commit()` captures `HEAD` before the manifest's own commit, so whenever a frozen artifact is edited in the same commit that rebuilds the manifest (which is what happened), the recorded commit is guaranteed to be a tree where verify fails. Acceptable fixes, any one:

1. Drop `git_commit` from the manifest and let the **git tag** be the sole commit binding (the content hashes are the real freeze; a redundant pointer that can go stale is worse than none), or
2. Keep the field but set it, by amend or a one-line follow-up, to the commit that actually contains the manifest, and confirm `--verify` passes at that commit, or
3. Relabel it `built_against_parent_commit` *and* guarantee no frozen artifact differs between that commit and the manifest commit (not currently true, so this needs a clean rebuild anyway).

Whichever you choose, the acceptance test is one line: check out the commit the manifest names (or the tag), run `--verify`, see `OK`. Until that passes, do not cut the tag.

## 4. Lower-priority notes

- **(Near-blocker, cheap) The frozen plan text still calls itself a draft.** The object you are about to hash begins "Study A analysis plan (**pre-freeze DRAFT**)"; line 4 reads "Status: DRAFT proposal, not frozen, not authoritative," points at an "**OPEN DECISIONS** block near the top" that no longer exists in the document, and line 130 heads a section "Freeze object (**blocker 8, not yet done**)" although the manifest is done. Freezing a document whose own header disclaims its authority and describes its own freeze as incomplete is self-contradictory on its face. This is a text pass, so I did not lead with it, but clean it in the same pre-tag edit as the `git_commit` fix (and rebuild the manifest so the hash tracks the cleaned text). The SUMMARY line (`status: draft ... not frozen`) needs the same update.

- **Confirmatory denominator is stated two ways.** Line 8 commits to "counts and fractions over this fixed 54-row set" (P008 in), but the C1/C2 rows list "P008 per A1" under *Exclusions*, and the analyzer computes yield over `len(map_by_row)`, not a hardcoded 54. A1's default retains P008 for row-level analyses (yield is row-level) and only drops it from strict-pair scoring, so the intended denominator is 54-with-P008, but the C1/C2 Exclusions cell says the opposite. A pre-registered confirmatory denominator should not be readable as either 54 or 51. State it once, unambiguously, before the tag. The real row map is stamp-2, so also assert there that `len(map_by_row) == 54` or the yield denominator silently shifts.

- **The verifier is not self-frozen.** `build_study_a_manifest.py` is not in `FROZEN_ARTIFACTS`, so the tool that certifies the freeze can be edited without tripping its own drift check. Add it to the frozen set (or record its hash), so the integrity check is not itself mutable.

- **The plan's freeze-object list over-claims what stamp 1 covers.** Line 131 says freezing hashes "this analysis plan, schema.json, **the training/practice set**, ... the build command." The training/practice set is neither in `artifacts` nor in `not_yet_frozen`; it is simply absent. Either freeze it in stamp 1 or move it explicitly into `not_yet_frozen` so the plan text and the manifest agree on what stamp 1 actually pins.

- **`study-protocol-draft.md` is load-bearing but unfrozen.** The Option-A judge information set is justified by information-state parity with what evaluators see (`study-protocol-draft.md:30`). If that protocol file changes, the parity justification for the frozen judge silently shifts. Consider hashing it in stamp 1, or note in the manifest that the parity claim is pinned to a specific revision.

- **Judge determinism is a claim, not a dependency (fine as is, worth a sentence).** The judge CSVs are frozen artifacts, so bit-level reproducibility of the Ollama runs is not required for the freeze. Good. But the plan presents "temp 0, seed 1" as if it guarantees reproducibility; local llama.cpp/Ollama runs are not bit-reproducible across runtime versions or hardware. One sentence stating that the frozen CSV *is* the comparator (and the digests plus command are provenance, not a reproduction guarantee) would prevent a reviewer reading determinism as a promise you cannot keep.

None of the note-level items block on their own. The `git_commit` reconciliation does. Fix it, rebuild, confirm `--verify` passes at the tagged commit, then tag.
