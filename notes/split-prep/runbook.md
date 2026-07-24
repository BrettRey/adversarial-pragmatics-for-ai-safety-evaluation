# Repo Split Runbook: Delegation Assurance + Evidentiary Assurance -> New Repo
<!-- SUMMARY: exact step-by-step procedure to split DA+EA into a new public repo while AP stays put; drafted, not executed - status: draft - updated: 2026-07-24 -->

This runbook operationalizes a decision already made and not open for relitigation here:
the repository splits into two. Repo 1 (this one) keeps *Adversarial Pragmatics* (AP),
the supplement, `benchmark/`, all Study A/B machinery, the private-data boundary, and all
existing history, unchanged at its current path and GitHub URL. Repo 2 is a new public
repo holding *Delegation Assurance* (DA) and *Evidentiary Assurance* (EA) together, with
fresh history (no `git filter-repo`).

I drafted this by reading the actual file tree and the DA/EA source files, not from
assumptions. Nobody has executed any step in it. Four sibling agents are concurrently
editing `Makefile`, `scripts/`, `submission/`, `notes/arxiv-v3-abstract-draft.md`,
`notes/cited-source-local-archive.md`, and `assurance/shared/` in this repo right now;
`git status --short` at the time of drafting also showed `CLAUDE.md` modified. Re-run the
discovery commands in Section 1 before executing anything here -- the file lists below are
a snapshot, not a promise about the tree at execution time.

## 0. One interpretive call this runbook makes, flagged for Brett to confirm

The brief says Repo 1 keeps AP + supplement + benchmark + Study A/B + the private-data
boundary + all existing history, and separately that Repo 2 holds DA + EA. It does not
say in so many words whether DA/EA content is *removed* from Repo 1's working tree going
forward, or left in place as a duplicate. I read "the repository splits into two" as
requiring removal (Phase C below): otherwise there are two canonical homes for DA/EA and
every future edit has to be made twice or the copies drift. "All existing history" is kept
by *not* rewriting Repo 1's git history (no filter-repo, no `git rm` of old commits) --
only a new, forward-looking removal commit is added. **Confirm this reading with Brett
before running Phase C.** If he wants Repo 1 to keep a duplicate copy of DA/EA instead,
skip Phase C and Phase F entirely; everything else in this runbook (building Repo 2) is
unaffected either way.

## 1. Preconditions (re-run before executing)

```bash
cd /Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation
git status --short                       # must be clean, or every dirty path accounted for below
git log --oneline -5                      # confirm HEAD is what you think it is
git log --oneline -1 95e927b              # confirm this commit (DA §8's current pin) still resolves
find . -not -path './.git/*' -type f | wc -l   # sanity check against the 814 counted at drafting time
```

Do not proceed past Phase A while any of `Makefile`, `scripts/*`, `submission/*`,
`notes/arxiv-v3-abstract-draft.md`, `notes/cited-source-local-archive.md`, or
`assurance/shared/*` show as modified/untracked by another live session -- Phase C and the
Makefile split (owned by a sibling agent) will conflict with each other's edits.

Pick the new repo's name and folder path before Phase A (see `open-questions.md`, item 1).
This runbook uses the placeholder `REPO2_NAME` and a sibling directory
`../REPO2_NAME` for illustration; substitute the real values throughout.

## 2. File classification

Four buckets. "Stays" and "Moves" are mutually exclusive; "Copy to both" and "Copy as
historical context" create a second copy in Repo 2 without touching Repo 1.

### 2a. Moves to Repo 2 (removed from Repo 1 in Phase C)

```text
delegation-assurance.tex
evidentiary-assurance.tex
sections-delegation/                      # all 9 files
sections-evidentiary/                     # all 7 files
assurance/delegation/                     # entire tree
assurance/evidentiary/                    # entire tree
figure-plan.md                            # DA's figure menu; AP has no figures/ dependency here
submission/venue-decision-2026-07-22.md   # DA's venue-decision record; lives directly under
                                           # submission/, NOT submission/arxiv/ -- easy to miss
notes/delegation-assurance-introduction-draft.md
notes/delegation-assurance-paper-sketch.md
notes/secure-delegation-new-paper-plan.md
notes/secure-delegation-positioning.md
notes/secure-delegation-thesis-memo.md
notes/plans/2026-07-17-delegation-category-level-terminology-pass.md
notes/plans/2026-07-17-delegation-lakoffian-metaphor-pass.md
notes/plans/2026-07-17-delegation-projectibility-harmonization.md
reviews/delegation-assurance-referee-triage-2026-07-22.md
scripts/validate_delegation_artifacts.py
scripts/analyze_delegation_programs.py
scripts/design_analysis.py
scripts/test_validate_delegation_artifacts.py
scripts/test_analyze_delegation_programs.py
scripts/test_design_analysis.py
scripts/validate_evidentiary_artifacts.py
scripts/analyze_evidentiary_calibration.py
scripts/stamp_evidentiary_artifacts.py
scripts/build_evidentiary_new_fixtures.py
scripts/test_stamp_evidentiary_artifacts.py
```

Build artifacts (`delegation-assurance.{aux,bbl,bcf,blg,log,out,run.xml,pdf}`,
`evidentiary-assurance.{...}`) are untracked in git already (`git ls-files` confirms only
the `.tex` sources are tracked) -- nothing to move, Repo 2 rebuilds them with `make`.
`scripts/__pycache__/*.pyc` matching the moved scripts should be deleted, not copied; they
are compiled bytecode, not source, and appear to be accidentally tracked in Repo 1 (worth a
separate cleanup note to Brett, out of scope here).

### 2b. Copy to both repos (Repo 1 keeps it unchanged; Repo 2 gets a duplicate)

```text
assurance/shared/                         # entire tree: claim-types.md, fixtures/,
                                           # load-bearing-claim-audit.csv,
                                           # projective-claim.schema.json
scripts/validate_claim_register.py
```

Reason: `make validate-claims` runs this validator three times in Repo 1 today, once
against `benchmark/study-b/claim-register.json` (AP, stays), once against
`assurance/delegation/projective-claim-register.json` (moves), once against
`assurance/evidentiary/projective-claim-register.json` (moves). AP's own Study B claim
register needs the shared schema and fixtures after the split just as much as DA/EA do, so
this is a genuine duplication, not a move. Keep both copies byte-identical after the split;
if `assurance/shared/` semantics ever change, change both repos or note the divergence.

### 2c. Copy as historical context into Repo 2 only (new subfolder; Repo 1 untouched)

Place under a new `notes/pre-split-history/` folder in Repo 2 so it reads as inherited
context, not Repo 2's own working notes:

```text
notes/cross-paper-claims-matrix-2026-07-18.md
notes/claude-code-security-mapping.md
notes/pairwise-section-audit-2026-07-22.md
notes/advisory-board.md
notes/plans/2026-07-18-implementation-baseline.md
notes/plans/2026-07-18-commitment-causation-selection-integration-plan.md
notes/plans/2026-07-21-projectibility-validity-excellence-revision-plan.md
notes/plans/2026-07-22-paper-filename-renames.md
reviews/2026-07-18-cross-paper-integration-review.md
reviews/2026-07-21-projectibility-validity-executable-stress-test.md
```

These documents discuss AP, DA, and EA together (cross-paper vocabulary decisions, the
pairwise section audit, the projectibility/validity stress test). They stay live and
unchanged in Repo 1 too -- both repos benefit from the record, and neither repo's copy is
authoritative over the other after this point; they are frozen history, not synced state.

### 2d. Fresh copies Repo 2 needs but does not inherit verbatim

```text
.house-style/            -> copy the current snapshot (version 2.1.2 per .house-style-version)
.house-style-version      -> copy as-is
LICENSE, LICENSE.md       -> copy as-is (same terms: CC-BY-4.0 content, MIT code)
LICENSES/                 -> copy as-is (CC-BY-4.0.txt, MIT.txt)
references.bib            -> regenerate via `make vendor-bib` against the portfolio
                              central bib, same mechanism Repo 1 uses (do not hand-filter
                              to "only DA/EA's cited keys" -- Repo 1's own convention is to
                              vendor the full central bib for a self-contained build, and
                              DA+EA together already cite widely enough that filtering
                              saves little and risks missing an entry)
references-local.bib      -> start from an empty template (header comment only). The two
                              Claude-Code-security entries currently sitting in this repo's
                              references-local.bib are NOT yet cited in DA or EA body text
                              (verified: zero hits for either key in delegation-assurance.tex,
                              evidentiary-assurance.tex, or either sections- tree) -- confirm
                              with whoever lands notes/claude-code-security-mapping.md's
                              "not placed" insertions before deciding whether they belong here
.gitignore                -> write a new, smaller one (LaTeX build artifacts + __pycache__ +
                              .DS_Store); do not copy Repo 1's verbatim, since most of its
                              rules are about benchmark/results, private/, and Study A/B
                              paths that don't exist in Repo 2
.agent/workflows/         -> do not hand-copy Repo 1's; regenerate via the portfolio's
                              `paper-project-setup` skill / `.house-style/templates/agents/
                              create-paper.sh`, so Repo 2 gets correctly-templated
                              workflow docs instead of AP-specific boilerplate
CITATION.cff, README.md, CLAUDE.md, AGENTS.md, GEMINI.md, Makefile
                          -> drafted fresh in notes/split-prep/ (this task); AGENTS.md and
                              GEMINI.md do not have their own drafts here, but in this repo
                              they are byte-identical to CLAUDE.md's content (verified by
                              reading all three) -- when executing, copy repo2-CLAUDE.md's
                              final text into AGENTS.md and GEMINI.md as well, or symlink
                              them, rather than leaving them absent or stale
```

Repo 2 does **not** need a `figures/` directory: both DA and EA figures are pure TikZ
(verified: zero `\includegraphics` calls in either paper's `.tex` or section files). The
inherited `\graphicspath{{figures/}}` line in the house-style preamble is harmless with no
`figures/` directory present, since nothing calls it.

### 2e. Stays in Repo 1 only (everything not listed above)

This is the residual bucket: `adversarial-pragmatics-for-ai-safety-evaluation.tex`,
`supplement.tex`, `sections/*.tex`, `benchmark/` (entire tree), `data/`, `private/`,
`figures/`, `EVALUATION-MEMO.md`, `CITATION.cff`, `STATUS.md`, `DECISIONS.md`, the rest of
`notes/`, the rest of `reviews/`, the rest of `scripts/`, and `submission/` minus the one
file named in 2a. `correspondence/` stays here pending Brett's call (see
`open-questions.md`, item 2) -- default to leaving it if undecided, since moving it is
reversible and leaving a portfolio-level folder in place is not a public-facing risk.

`README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and `Makefile` all currently reference
`assurance/delegation/`, `assurance/evidentiary/`, `sections-delegation/`,
`sections-evidentiary/`, `delegation-assurance`, and `evidentiary-assurance` in Repo 1
(confirmed by reading each). After Phase C these references go stale and need edits to
drop the DA/EA build targets, layout lines, and "two related framework papers" language.
**I did not draft these edits**: `Makefile` and `CLAUDE.md` are both mid-edit by other
sessions right now, and editing them is outside this task's file ownership. Whoever runs
Phase C should re-grep for `delegation`, `evidentiary`, `sections-delegation`, and
`sections-evidentiary` across `README.md`, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, and
`Makefile` once the Makefile refactor lands, and strip what no longer applies.

## 3. Step-by-step procedure

### Phase A -- Build Repo 2 locally (no GitHub yet; reversible; no authorization needed)

```bash
REPO1=/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/adversarial-pragmatics-for-ai-safety-evaluation
REPO2=/Users/brettreynolds/projects/LLM-CLI-projects/papers/development/REPO2_NAME
mkdir -p "$REPO2"

# 2a: moves (copy for now -- Repo 1 is only touched in Phase C)
rsync -av "$REPO1/delegation-assurance.tex" "$REPO2/"
rsync -av "$REPO1/evidentiary-assurance.tex" "$REPO2/"
rsync -av "$REPO1/sections-delegation/" "$REPO2/sections-delegation/"
rsync -av "$REPO1/sections-evidentiary/" "$REPO2/sections-evidentiary/"
rsync -av "$REPO1/assurance/delegation/" "$REPO2/assurance/delegation/"
rsync -av "$REPO1/assurance/evidentiary/" "$REPO2/assurance/evidentiary/"
rsync -av "$REPO1/figure-plan.md" "$REPO2/"
mkdir -p "$REPO2/submission"
rsync -av "$REPO1/submission/venue-decision-2026-07-22.md" "$REPO2/submission/"
mkdir -p "$REPO2/notes/plans"
for f in delegation-assurance-introduction-draft.md delegation-assurance-paper-sketch.md \
         secure-delegation-new-paper-plan.md secure-delegation-positioning.md \
         secure-delegation-thesis-memo.md; do
  rsync -av "$REPO1/notes/$f" "$REPO2/notes/"
done
for f in 2026-07-17-delegation-category-level-terminology-pass.md \
         2026-07-17-delegation-lakoffian-metaphor-pass.md \
         2026-07-17-delegation-projectibility-harmonization.md; do
  rsync -av "$REPO1/notes/plans/$f" "$REPO2/notes/plans/"
done
mkdir -p "$REPO2/reviews"
rsync -av "$REPO1/reviews/delegation-assurance-referee-triage-2026-07-22.md" "$REPO2/reviews/"
mkdir -p "$REPO2/scripts"
for f in validate_delegation_artifacts.py analyze_delegation_programs.py design_analysis.py \
         test_validate_delegation_artifacts.py test_analyze_delegation_programs.py \
         test_design_analysis.py validate_evidentiary_artifacts.py \
         analyze_evidentiary_calibration.py stamp_evidentiary_artifacts.py \
         build_evidentiary_new_fixtures.py test_stamp_evidentiary_artifacts.py; do
  rsync -av "$REPO1/scripts/$f" "$REPO2/scripts/"
done

# 2b: copy to both (Repo 1 untouched)
rsync -av "$REPO1/assurance/shared/" "$REPO2/assurance/shared/"
rsync -av "$REPO1/scripts/validate_claim_register.py" "$REPO2/scripts/"

# 2c: historical context, new subfolder
mkdir -p "$REPO2/notes/pre-split-history"
for f in cross-paper-claims-matrix-2026-07-18.md claude-code-security-mapping.md \
         pairwise-section-audit-2026-07-22.md advisory-board.md; do
  rsync -av "$REPO1/notes/$f" "$REPO2/notes/pre-split-history/"
done
for f in 2026-07-18-implementation-baseline.md \
         2026-07-18-commitment-causation-selection-integration-plan.md \
         2026-07-21-projectibility-validity-excellence-revision-plan.md \
         2026-07-22-paper-filename-renames.md; do
  rsync -av "$REPO1/notes/plans/$f" "$REPO2/notes/pre-split-history/"
done
for f in 2026-07-18-cross-paper-integration-review.md \
         2026-07-21-projectibility-validity-executable-stress-test.md; do
  rsync -av "$REPO1/reviews/$f" "$REPO2/notes/pre-split-history/"
done

# 2d: fresh infra
rsync -av "$REPO1/.house-style/" "$REPO2/.house-style/"
cp "$REPO1/.house-style-version" "$REPO2/.house-style-version"
cp "$REPO1/LICENSE" "$REPO2/LICENSE"
cp "$REPO1/LICENSE.md" "$REPO2/LICENSE.md"
rsync -av "$REPO1/LICENSES/" "$REPO2/LICENSES/"
cp "$REPO1/notes/split-prep/repo2-README.md" "$REPO2/README.md"
cp "$REPO1/notes/split-prep/repo2-CLAUDE.md" "$REPO2/CLAUDE.md"
cp "$REPO1/notes/split-prep/repo2-CLAUDE.md" "$REPO2/AGENTS.md"
cp "$REPO1/notes/split-prep/repo2-CLAUDE.md" "$REPO2/GEMINI.md"
cp "$REPO1/notes/split-prep/repo2-Makefile-draft" "$REPO2/Makefile"
cp "$REPO1/notes/split-prep/repo2-CITATION.cff" "$REPO2/CITATION.cff"
# write $REPO2/.gitignore and $REPO2/references-local.bib fresh (see 2d above; both are
# small enough to hand-write at execution time rather than script here)
# then, from inside $REPO2, with CENTRAL_BIB pointed correctly:
#   make vendor-bib
```

Rebuild `benchmark/study-a/materials/outreach/` was not listed above and should not be --
those files are AP's Study A outreach drafts, unrelated to DA/EA. Do not let a broad glob
on `notes/` or `reviews/` sweep in anything beyond the explicit lists above; both
directories hold far more AP/Study A material than DA/EA material.

### Phase B -- Verify Repo 2 builds clean (still local, still no git repo, no authorization needed)

```bash
cd "$REPO2"
xelatex delegation-assurance.tex && biber delegation-assurance && xelatex delegation-assurance.tex && xelatex delegation-assurance.tex
xelatex evidentiary-assurance.tex && biber evidentiary-assurance && xelatex evidentiary-assurance.tex && xelatex evidentiary-assurance.tex
python3 scripts/validate_delegation_artifacts.py
python3 scripts/analyze_delegation_programs.py --validate-specs
python3 -m unittest scripts.test_validate_delegation_artifacts scripts.test_analyze_delegation_programs scripts.test_design_analysis
python3 scripts/validate_evidentiary_artifacts.py
python3 scripts/analyze_evidentiary_calibration.py --self-test
python3 -m unittest scripts.test_stamp_evidentiary_artifacts
python3 scripts/validate_claim_register.py --self-test
python3 scripts/validate_claim_register.py assurance/delegation/projective-claim-register.json
python3 scripts/validate_claim_register.py assurance/evidentiary/projective-claim-register.json
python3 .house-style/check-style.py delegation-assurance.tex evidentiary-assurance.tex
```

Do not proceed to Phase D until every one of these passes, both PDFs build with 0
undefined references, and page counts match what `STATUS.md` currently reports for DA (39
pp.) and EA (34 pp.) as of the 2026-07-24 session notes -- a mismatch means a file got
missed in the manifest above.

### Phase C -- Remove DA/EA from Repo 1 (outward-facing in effect, even before any push: this
changes the public repo's tracked file set on the next push. **Requires Brett's explicit
authorization**, and requires Section 0's interpretation to be confirmed first.)

```bash
cd "$REPO1"
git rm delegation-assurance.tex evidentiary-assurance.tex figure-plan.md
git rm -r sections-delegation/ sections-evidentiary/ assurance/delegation/ assurance/evidentiary/
git rm submission/venue-decision-2026-07-22.md
git rm notes/delegation-assurance-introduction-draft.md notes/delegation-assurance-paper-sketch.md \
       notes/secure-delegation-new-paper-plan.md notes/secure-delegation-positioning.md \
       notes/secure-delegation-thesis-memo.md
git rm notes/plans/2026-07-17-delegation-category-level-terminology-pass.md \
       notes/plans/2026-07-17-delegation-lakoffian-metaphor-pass.md \
       notes/plans/2026-07-17-delegation-projectibility-harmonization.md
git rm reviews/delegation-assurance-referee-triage-2026-07-22.md
git rm scripts/validate_delegation_artifacts.py scripts/analyze_delegation_programs.py \
       scripts/design_analysis.py scripts/test_validate_delegation_artifacts.py \
       scripts/test_analyze_delegation_programs.py scripts/test_design_analysis.py \
       scripts/validate_evidentiary_artifacts.py scripts/analyze_evidentiary_calibration.py \
       scripts/stamp_evidentiary_artifacts.py scripts/build_evidentiary_new_fixtures.py \
       scripts/test_stamp_evidentiary_artifacts.py
# THEN, separately and by hand (not scripted here -- these need real edits, not deletes):
#   - Makefile: drop $(DELEGATION)/$(EVIDENTIARY) targets, all-papers, clean/distclean lines,
#     validate-delegation, and the DA/EA parts of assurance-check and the general `test` target
#     (which currently runs scripts.test_stamp_evidentiary_artifacts -- an EA test living inside
#     AP's own `make test`; this coupling must be cut, not just have its script deleted, or
#     `make test` breaks on a fresh clone)
#   - README.md, CLAUDE.md, AGENTS.md, GEMINI.md: drop DA/EA layout lines and "two related
#     framework papers" framing
git commit -m "Split delegation-assurance and evidentiary-assurance into their own repository"
```

Do not run `make test` or `make assurance-check` in Repo 1 between the `git rm` calls and
the Makefile edit -- both targets currently invoke DA/EA scripts and will fail until the
Makefile is repaired to match.

### Phase D -- Create the Repo 2 GitHub repository. **Requires Brett's explicit authorization.**

```bash
cd "$REPO2"
git init
git add -A
git commit -m "Initial commit: split from adversarial-pragmatics-for-ai-safety-evaluation"
gh repo create BrettRey/REPO2_NAME --public --source=. --remote=origin
```

Per the global default (new projects default to public GitHub under `BrettRey/`), and
confirm the exact name from `open-questions.md` item 1 first.

### Phase E -- First push. **Requires Brett's explicit authorization**, separate from Phase D's.

```bash
git push -u origin main
```

### Phase F -- Push Repo 1's removal commit. **Requires Brett's explicit authorization**,
separate from every prior gate. This is the step that can break the arXiv-linked public
history's *current* tree (not its past commits) -- anyone who clones Repo 1 fresh after
this point no longer gets DA/EA source. Confirm Phase B passed cleanly and Phase E's push
succeeded before running this.

```bash
cd "$REPO1"
git push origin main
```

### Phase G -- Tags, releases, DOIs. **Each of these is its own authorization gate; do not
bundle them.**

- A numbered GitHub release tag on Repo 2 at the commit that matches the verified-clean
  build from Phase B.
- Whether to recreate the tag name `evidentiary-assurance-r2` inside Repo 2's fresh
  history, or start Repo 2's tag numbering at r1 for both papers (open question -- see
  `open-questions.md` item 5, and `artifact-statement-rewrites.md` for the wording this
  feeds).
- An archival DOI (Zenodo or similar) if external citation is expected, minted only after
  the tag is stable.
- A parallel decision for Repo 1: whether the DA/EA removal itself warrants a release note
  or CHANGELOG entry, given the arXiv record for AP must keep resolving.

## 4. Reverse steps (undo)

- **Undo Phase C (before Phase F's push):** `git reset --hard HEAD~1` in Repo 1 restores
  the removed files locally; since nothing was pushed yet, no public trace exists. If the
  Makefile/README/CLAUDE.md hand-edits already happened as separate commits, revert those
  commits individually instead of a blanket hard reset.
- **Undo Phase C (after Phase F's push):** revert the removal commit with `git revert
  <sha>` rather than force-pushing history away; Repo 1's GitHub URL is cited by the arXiv
  record and by external readers, so rewriting pushed history is out of bounds regardless
  of how the split goes.
- **Undo Phase D/E:** `gh repo delete BrettRey/REPO2_NAME` (only if nothing external has
  linked to it yet -- check for forks/stars/issues first) or simply stop maintaining it and
  mark it archived; a public repo that existed briefly is a much smaller problem than
  broken history on Repo 1.
- **Undo Phase G's tag/DOI:** a minted DOI cannot be un-minted (Zenodo DOIs are permanent
  once assigned); this is precisely why Phase G is gated separately and last.

## 5. Post-split verification checklist

- [ ] Repo 2 builds both PDFs clean from a fresh clone with no network access beyond
      `make vendor-bib`'s one-time central-bib copy.
- [ ] Repo 2's `make assurance-check`-equivalent (validate-claims, validate-delegation,
      validate-evidentiary) all pass from a fresh clone.
- [ ] Repo 1's `make test` and `make assurance-check` still pass after the Makefile is
      repaired to drop DA/EA targets.
- [ ] `grep -rl "delegation-assurance\|evidentiary-assurance\|sections-delegation\|sections-evidentiary\|assurance/delegation\|assurance/evidentiary"` across Repo 1's remaining tracked files returns only expected historical mentions (DECISIONS.md/STATUS.md prose, cross-paper notes copied to both) and no live build dependency.
- [ ] The arXiv record for AP (`arXiv:2607.01153`) still resolves and its linked GitHub
      URL still serves the AP paper's own files.
- [ ] DA §8 and EA's artifact-availability section are rewritten per
      `artifact-statement-rewrites.md` and no longer point at a commit/tag that only
      exists in Repo 1's history.
- [ ] `CITATION.cff` in both repos validates (`cffconvert --validate` or the GitHub
      citation-file-format action).

## 6. Coupling risks to re-verify at execution time, not accepted as final here

1. `make test` in Repo 1 currently runs `scripts.test_stamp_evidentiary_artifacts` (an EA
   test) as part of AP's own general test target -- confirmed by reading the Makefile.
   This must be cut in the Makefile refactor, or Repo 1's `make test` breaks after Phase C.
2. `scripts/check_cited_source_archive.py` globs `delegation-assurance.tex`,
   `sections-delegation/*.tex`, `evidentiary-assurance.tex`, and `sections-evidentiary/*.tex`
   alongside AP's own files (confirmed by reading it). After Phase C this script will
   silently find nothing at those globs rather than erroring, which could mask a real
   problem if someone expects it to still validate DA/EA sources. It needs its own edit
   (owned by the agent currently on `notes/cited-source-local-archive.md`) to drop those
   globs, and Repo 2 needs its own equivalent script plus its own
   `cited-source-local-archive.md`, seeded from the DA/EA entries in Repo 1's current one.
3. `assurance/shared/load-bearing-claim-audit.csv` is mid-edit by another session right
   now (`git status` shows it modified). Whatever change lands there needs to be re-copied
   into Repo 2 after Phase A, not just copied once early.
4. `notes/arxiv-v3-abstract-draft.md` and the Makefile's `vendor-bib`/arXiv-bundle targets
   are both mid-edit; re-check whether either now references DA/EA before treating this
   runbook's Phase A file lists as final.
