# Artifact Statement Rewrites for the Split
<!-- SUMMARY: replacement wording for DA sec8 and EA's artifact-availability passage, both currently pinned to the AP repo; drafted text only, no .tex edited - status: draft - updated: 2026-07-24 -->

Both passages below currently pin to `github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation`
(this repository, Repo 1) and to git objects (a commit hash for DA, a tag for EA) that live
in *this* repository's history. After the split, Repo 2 gets fresh history with no
`git filter-repo`, so neither the commit hash nor the tag will exist there automatically --
they have to be recreated or replaced. I read both passages in full before drafting
replacements; I have not edited either `.tex` file. `REPO2_NAME` and the split date are
placeholders; fill them in once `open-questions.md` item 1 is settled and the split
actually happens.

## 1. Delegation Assurance §8 (`sections-delegation/08-code-data-availability.tex`)

### Current text (first paragraph only; the rest of §8 does not name the repo or a commit)

> \href{https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation}{The project repository} carries the delegation-assurance artifact under \path{assurance/delegation/}. The state described here is commit \texttt{95e927b}. A numbered release and an archival DOI are pending; until they exist, cite the commit rather than the branch.

### What's wrong with it after the split

- The URL points at Repo 1, which will no longer hold `assurance/delegation/` after Phase C
  of the runbook.
- Commit `95e927b` is real and does contain the DA schemas as of 2026-07-21 (verified: `git
  log -1 95e927b` resolves, and `git show --stat 95e927b` lists the DA schema files among
  ~450 changed lines touching all three papers together). But it is a commit in *Repo 1's*
  history. Repo 2's history starts fresh, so no commit with that hash -- or any hash tied to
  this repository's object database -- will exist there. Citing it after the split would
  send a reader to either the wrong repository or a 404.
- DA has never had its own release tag (unlike EA, which already uses
  `evidentiary-assurance-r2`). The split is a natural point to start one.

### Proposed replacement

> \href{https://github.com/BrettRey/REPO2_NAME}{The project repository} carries the delegation-assurance artifact under \path{assurance/delegation/}. This repository holds this paper together with the companion evidentiary-assurance paper; both were developed inside \href{https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation}{the flagship benchmark repository} until their split into this repository on [SPLIT DATE], whose history remains the record of this artifact's development before the split. The state described here is tag \texttt{delegation-assurance-r1}. A numbered release and an archival DOI are pending; until they exist, cite the tag rather than the branch.

### Open decision this rewrite depends on

Whether `delegation-assurance-r1` is the right tag name, and whether it should be created
at the moment of the split (fixing exactly the schema/fixture/analyser versions this paper
currently describes) or held until after a further revision. I default to creating it at
split time, matching the pattern EA already set (a tag fixes the artifact at the versions a
specific manuscript revision describes), and starting at `r1` since this is DA's first
tagged state. See `open-questions.md` item 5. Tag creation is gated in the runbook (Phase
G) and needs Brett's explicit authorization; it is not implied by anything here.

## 2. Evidentiary Assurance, "Artifact availability" (`sections-evidentiary/05-research-program.tex`, the subsection beginning `\subsection*{Artifact availability}`)

### Current text (first two sentences; the rest of the subsection describes the substrate's contents and does not name the repo again)

> The executable substrate is released under \href{https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation}{\path{github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation}}, in \path{assurance/evidentiary/}, with the schemas, applicability map, and fixtures at the versions named in this section. Code is MIT-licensed and the scholarly content CC~BY~4.0. The repository state cited here is the immutable tag \texttt{evidentiary-assurance-r2}, which fixes the schemas, map, fixtures, and analyser at the versions this paper describes, and which is archived with a DOI at publication; a validator, an analyser with in-memory self-tests, and a binding stamper are included so that every hash and cross-reference in the artifact can be checked from a clean clone with no network access.

### What's wrong with it after the split

- Same URL problem as DA: `assurance/evidentiary/` will not live at this repository's path
  after Phase C.
- The tag `evidentiary-assurance-r2` exists today in *this* repository's history (per
  `STATUS.md`'s 2026-07-24 entry: "Tag `evidentiary-assurance-r2`"). Git tags do not
  transfer between repositories on their own; Repo 2 needs the same tag name recreated
  against its own (different) commit, pointing at the same schema/map/fixture/analyser
  content. Recreating the name is safe and unambiguous, since the repository URL
  disambiguates which tag is meant, but it is a real action someone has to take, not
  something that happens automatically because the .tex says so.
- "archived with a DOI at publication" is unchanged by the split (it was already a forward
  promise, not a completed step) and needs no rewrite on that count, but it should not be
  read as a promise this move keeps automatically -- the DOI, when minted, must point at
  Repo 2, not Repo 1.

### Proposed replacement

> The executable substrate is released under \href{https://github.com/BrettRey/REPO2_NAME}{\path{github.com/BrettRey/REPO2_NAME}}, in \path{assurance/evidentiary/}, with the schemas, applicability map, and fixtures at the versions named in this section. This repository holds the paper together with the companion delegation-assurance paper; both were developed inside \href{https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation}{the flagship benchmark repository} until their split into this repository on [SPLIT DATE], whose history remains the record of this artifact's development before the split. Code is MIT-licensed and the scholarly content CC~BY~4.0. The repository state cited here is the immutable tag \texttt{evidentiary-assurance-r2}, recreated in this repository at the same schema, map, fixture, and analyser versions the tag fixed before the split, and archived with a DOI at publication; a validator, an analyser with in-memory self-tests, and a binding stamper are included so that every hash and cross-reference in the artifact can be checked from a clean clone with no network access.

### Open decision this rewrite depends on

Whether to recreate `evidentiary-assurance-r2` verbatim (my default, for continuity with
what the paper already says and what reviewers may already have seen cited) or renumber it
as part of the new repository's own tag sequence. If DA starts at `r1` and EA keeps `r2`,
the two tags carry different, paper-specific meanings (count of review-driven artifact
revisions), which is accurate but could read as an odd asymmetry to a reader who does not
know EA has been through more review rounds than DA. State that asymmetry's reason once,
in the repository README or a footnote, if it is kept. See `open-questions.md` item 5.

## Shared framing sentence, if Brett wants one instead of repeating the lineage clause twice

Both rewrites above add a near-identical clause ("This repository holds ... together with
the companion ... paper; both were developed inside ... until their split ..."). An
alternative is to state that lineage once, prominently, in the repository README (already
drafted, see `repo2-README.md`'s "Pre-split history" section) and drop it from both
artifact-availability passages, keeping each passage to its original length and just
swapping the URL, commit-to-tag, and tag name. I left both options open rather than
picking one; it's a house-style call about whether artifact-availability sections should be
self-contained or may defer to the README for lineage.
