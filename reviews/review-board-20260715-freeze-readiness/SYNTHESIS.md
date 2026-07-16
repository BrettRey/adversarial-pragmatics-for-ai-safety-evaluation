# Freeze-readiness board synthesis (2026-07-15)

<!-- SUMMARY: 6-reviewer Opus board on whether to git-tag the Study A pre-registration; UNANIMOUS not-ready (5 FIX-FIRST, 1 CONDITIONAL); do NOT tag; verified before-tag fix list below · status: NO-GO · updated: 2026-07-15 -->

Six independent Opus reviewers (named advisory board: Liang, Chen, Röttger,
Wallace, Greshake; plus a hostile methodologist with the target-heterogeneity
check), each blind to the others, each answering one question: sign off on
freezing this pre-registration now, or is there a defect that must be fixed
first? Individual reviews in this directory.

## Verdict: NO-GO. Do not tag. Unanimous.

5 × FIX-FIRST (Liang, Chen, Röttger, Wallace, hostile), 1 × CONDITIONAL
(Greshake). No reviewer signed off. This reverses my earlier "GO" — the board
found real, file-verified, before-tag defects that I and the D4 board missed.

**Board self-check.** This is not smoothing to a centroid. Each reviewer found a
*different* primary defect through their own lens, and most are verified against
the actual files (manifest hashes, 26/162, all-`compliant` gold,
`no_policy_or_authority_limit` at 33/54 & 42/54, `seed-items.csv` absent). The
one genuine *cluster* — four reviewers hitting co-primary construct validity from
different angles — is strong signal that the estimand tier really has a problem,
not reviewers echoing a role. Caveat: six simulated agents agreeing is not proof
the field would; treat this as a stress test.

---

## A. Mechanical / integrity defects (cheap, I can fix, must precede any tag)

1. **Manifest `git_commit` mismatch** (Liang + hostile, both verified). The
   manifest records `git_commit: fd20944`, but its frozen script hashes match
   HEAD `1dee5cd`, not `fd20944`. `git checkout fd20944 && build_study_a_manifest.py
   --verify` prints DRIFT. `--verify` passes at HEAD only because it never checks
   the `git_commit` field. The pre-registration's own named commit fails its own
   verify. Fix: drop the field (the tag is the authoritative commit pointer) and
   re-hash at the tagged commit.
2. **`seed-items.csv` not in the manifest** (Wallace, verified). The item set —
   the 18 items, the `expected_behavior` gold, the per-item author labels, and
   the item-authoring taxonomy that grounds the "Option B is a laundered answer
   key" argument — is unfrozen. The leak argument and C3/C4 author comparator
   are anchored to an unhashed file. Fix: hash it into stamp 1.
3. **Plan text still declares itself unfrozen** (Liang + hostile). The document
   being hashed opens "pre-freeze DRAFT," says "not frozen, not authoritative,"
   and references an "OPEN DECISIONS" section that was renamed. Fix: strip the
   self-negating language.
4. **Empty revision ledger / rolling re-baseline** (hostile). Frozen scripts were
   edited after the manifest was first built and the manifest was re-hashed to
   absorb it, with no ledger entry. Defensible pre-tag (no tag exists yet), but
   stamp 1 should be declared void and re-stamped cleanly at the tagged commit,
   not carried forward. Fix: re-stamp at tag.

## B. Scientific / estimand defects (the real blocks; need Brett's design calls)

5. **The co-primary tier measures trivial / no-stakes agreement, not the
   safety-relevant discrimination the benchmark is about.** Four reviewers,
   four angles, all verified:
   - **Röttger:** co-primary `policy_compliance` treats `no_policy_or_authority_limit`
     (nothing-at-stake) as a substantive reference, and it is the majority class
     (24B 33/54 = 61%, 7B 42/54 = 78%). C4 agreement is dominated by trivial
     "no policy in play"; the compliant-vs-noncompliant discrimination lives in
     ~12-21 rows and is never pre-registered. A4 omits this value.
   - **Wallace:** the authority/source-role constructs the benchmark is built to
     manipulate (`source_role_clarity`, `information_flow_action_licensing`,
     per-pair authority-sensitivity) are all *exploratory*, while the co-primary
     that depends on them is confirmatory. A "successful" Study A is consistent
     with the panel being blind to authority: yield measures reliability, not
     validity, and two evaluators sharing a wrong authority read agree.
   - **Greshake:** the co-primary labels don't bear on embedded-command / injection
     adjudication; on AP-SEED-013 a response that followed the injection can score
     `task_success = success`, `policy_compliance = no_policy_or_authority_limit`.
   - **Röttger L5 / Wallace L5:** `policy_compliance` author gold is `compliant`
     for all 18 items (zero design variance).
   Convergent fix menu: pre-register a **policy-at-stake conditional** co-primary
   and report the not-at-stake share; add a **per-pair authority-sensitivity**
   estimand (fraction of the 9 pairs whose reference flips in the gold direction);
   promote **`source_role_clarity` yield** and/or **`information_flow_action_licensing`**
   to (secondary-)confirmatory; state expected substantive denominators.
6. **`consensus()` cannot separate construct contestedness from rater noise**
   (hostile; the deepest defect). "Stable" = majority vote only. A 2-1 substantive
   split becomes a clean reference (feeds C1-C4); the same boundary item at 2-2 is
   dropped as "no substantive reference." Parity of N, not the construct, decides
   whether contestedness is signal or noise — violating the project's own "treat
   disagreement as data" mandate. Co-primary yield then confounds "rubric
   unreliable" with "benchmark contains genuine boundary items" (arguably the most
   interesting finding), and S3/RQ4 recall treats a possibly-2-person reference as
   ground truth. Fix: pre-register a disagreement typology (stable-but-contested
   as its own estimand); report C1-C4 split by reference type (unanimous /
   substantive-majority / escape), not collapsed; condition every recall /
   candidate-revision claim on reference robustness; add a standing statement that
   yield = convergence, not correctness.
7. **The judge breaks information-state parity on the role axis** (Chen; verified).
   The frozen judge grades all three criteria in one joint pass, while the human
   panel is role-separated (D3 bars one person doing both roles, precisely to
   avoid cross-role priming). So the judge's `policy_compliance` is produced with
   `task_success` in context; the human's is not. Same defect that killed Option B,
   different axis — the Option-A "information-state parity" justification is false
   as implemented. Fix: run the judge in two role-separated passes (linguistic-only
   → task_success; policy-only → policy_compliance + refusal_outcome), regenerate
   both comparators, re-hash. (Or, if keeping single-pass, strike the parity claim
   and pre-register joint-grading as a named confound — Chen prefers regenerate.)

## Lower-priority (documented, not blocking)
- Chen L1: the 24B is *more* majority-collapsed than the 7B on task_success /
  refusal, so S3's "does failure persist weak→strong" is near-guaranteed "yes,
  worse" as a near-constant-predictor artifact, not a scale effect — pre-commit
  to reading it that way.
- Chen L3: minority-class set defined per-judge; freeze it once from the reference.
- Chen L4 / general: judge validity rests on one prompt template; state no
  prompt-robustness is claimed.
- Wallace L2-L4: two taxonomies (item-authoring vs evaluator schema) share names
  with no crosswalk; `untrusted_embedded_directive` conflates provenance with
  trust; no system/developer authority tier (scope limit to state).
- Hostile 2c: "prefer odd N" next to "analyze whoever completed" invites
  post-cutoff rater-dropping; one sentence forbidding it closes the forking path.

## Disposition
Do not tag. The mechanical fixes (A1-A4) are mine to do. The estimand fixes
(B5-B7) are design decisions for Brett: which authority/at-stake estimands to
promote, whether to add the disagreement typology, whether to re-run the judge
role-separated. This is a real revision, not a patch.
