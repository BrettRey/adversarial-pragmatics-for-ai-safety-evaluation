# Open Questions for Brett
<!-- SUMMARY: decisions the split runbook cannot make on its own; needs Brett before Phase C/D/G of runbook.md - status: awaiting decisions - updated: 2026-07-24 -->

## 1. New repo name

Three options, in order of my preference:

**a. `delegation-and-evidentiary-assurance`** (my default). Names both papers directly, so
anyone finding the repo via search or a citation immediately knows what's in it. Matches
this repository's own naming convention (a long, descriptive kebab-case folder name rather
than an acronym or brand). Costs nothing if a third paper joins the repo later; it would
just be a repo whose name undersells its contents, same as this repo already undersells
itself slightly by not naming the supplement.

**b. `authorization-assurance-for-ai-systems`**. An umbrella name built from the shared
thread (typed authorization, evidentiary review of delegated authority) rather than either
paper's title. Worth considering because DECISIONS.md (2026-07-10) records a deferred idea
for a third, "authority accounting" paper at AI-2040 governance scale, explicitly parked
"until after public cleanup and further operationalization of the existing papers" -- i.e.,
roughly now. If that paper gets written, it would belong in this repo, and an umbrella name
would already fit it without a second rename. Costs some immediate discoverability: a
reader can't tell from the name alone that Delegation Assurance and Evidentiary Assurance
are the two papers inside.

**c. `delegation-evidentiary-assurance`**. A shorter fusion of (a). Reads slightly awkwardly
(three nouns in a row with no connective), and I don't think the four saved characters are
worth the readability cost, but it's a real option if (a) feels too long next to this
repo's own already-long name.

I'd pick (a) unless the "authority accounting" extension is actually likely to happen soon,
in which case (b) saves a future rename.

## 2. Fate of `correspondence/`

Three files, all portfolio-level rather than paper-specific:

- `2026-07-15-ravi-ummadisetti-touch-base.md` -- a sent LinkedIn/email note that mentions
  the AP arXiv link, not DA or EA.
- `2026-07-16-nutan-naik-linkedin.md` -- an inbound connection request that references
  "your Adversarial Pragmatics for AI Safety Evaluation paper," not DA or EA.
- `2026-07-22-trustai-founder-outreach.md` -- a draft pitch built around AP's Permission
  Compliance verdict-checking angle, not DA or EA specifically (though it touches
  delegation-assurance-style reasoning about authorization).

None of the three actually needs DA/EA content to make sense, and none is cited from DA or
EA. My default is: leave `correspondence/` in Repo 1 unchanged. It's a low-cost default
(nothing public depends on its location, and it's reversible -- copying it to Repo 2 later
costs nothing lost by waiting), and its content skews toward the AP paper specifically. If
Brett expects outreach specifically about DA/EA (e.g., to Minds and Machines readers, or to
governance/assurance-focused contacts) to start accumulating soon, a `correspondence/`
folder in Repo 2 from day one might be worth creating empty, ready for that traffic, while
leaving the three existing files where they are.

## 3. `DECISIONS.md` / `STATUS.md` history

**Recommended: start both fresh in Repo 2, with a one-line pointer back to Repo 1 for
pre-split history.** Reasoning:

- Repo 1's `DECISIONS.md` is 194 lines covering AP, Study A, Study B, and DA/EA
  interleaved by date, not separable into "DA/EA decisions" without either duplicating most
  of the file or cutting entries that reference AP context DA/EA decisions depended on
  (e.g., the 2026-07-13 through 2026-07-16 entries move between DA's comparative-test
  design and Study A's schema revisions in the same date range, because they were being
  worked in the same sessions).
- A fresh start avoids carrying forward AP-specific decisions (Study A ethics posture,
  pilot-model choices, arXiv font-bundling fixes) that would read as noise in a DA/EA-only
  repo and could mislead a new reader into thinking they're relevant precedent for this
  repo's own choices.
- The alternative (copy the whole file, or hand-split it into "DA/EA-relevant" and
  "AP-relevant" halves) is exactly the kind of manual, judgment-heavy split this task was
  scoped to avoid doing live; hand-splitting a 194-line interleaved decision log risks
  silently dropping a decision whose DA/EA relevance isn't obvious out of context.
- Precedent already exists in `notes/split-prep/`: this task's own instructions treat
  `notes/pre-split-history/` (Section 2c of `runbook.md`) as the right shape for material
  that needs to survive the split as read-only context without becoming live, editable
  state in the new repo. `DECISIONS.md`/`STATUS.md` are exactly the kind of file that
  should NOT get that treatment, because their whole value is being an actively maintained
  log, not a frozen record -- freezing an actively-maintained log by copying it produces a
  file that looks live but isn't, which is worse than starting empty.

Concretely: seed Repo 2's `DECISIONS.md` and `STATUS.md` with a single dated entry
recording the split itself and pointing to Repo 1's `DECISIONS.md`/`STATUS.md` (at the
split commit) for everything before it, then log new decisions going forward the normal
way.

## 4. Minds and Machines portfolio conflict

Already documented in this repo's own `submission/venue-decision-2026-07-22.md` (which
moves to Repo 2 under the runbook's Section 2a): *Minds and Machines* is Delegation
Assurance's approved target, and is also the stated target for two other Reynolds papers
outside this repository entirely -- Truth-Tracking Profiles
(`papers/retarget/truth-tracking-profiles/`) and the AGI evaluation paper, whose own
`STATUS.md` lists venue choice as its next action and calls M&M "a strong conceptual fit."
The venue-decision record itself already flags the risk plainly: DA and the AGI paper
"share the Messick/Kane validity apparatus and the projectibility vocabulary closely enough
that a reviewer meeting both would fairly ask what is distinct," and notes DA "takes the
M&M slot" as of 2026-07-22, so the other two papers' venue calls need to be made against
that fact, not in isolation. This is not something the split changes or resolves -- moving
DA to a new repo doesn't touch which journal it's submitted to -- but it's a live portfolio
sequencing question independent of the split, and I'm surfacing it here because
`open-questions.md` is where the split runbook parks anything it can't settle itself.
Whoever picks up Truth-Tracking Profiles or the AGI paper's venue decision next should
read `submission/venue-decision-2026-07-22.md` (in Repo 2 after the split) first.

## 5. Artifact-tag naming and numbering (raised while drafting `artifact-statement-rewrites.md`)

DA has never had its own release tag; EA already uses `evidentiary-assurance-r2` (meaning a
second review-round revision). After the split, does Repo 2:

- give DA a fresh `delegation-assurance-r1` and recreate `evidentiary-assurance-r2` under
  the same name (my default in the rewrite draft, preserving each tag's paper-specific
  meaning), or
- renumber both to a shared repo-wide sequence (e.g., both become `r1` at the moment of the
  split, discarding EA's review-round count), or
- hold off tagging either until each paper's next real revision, rather than tagging at the
  split itself?

This is a Phase G decision in `runbook.md` and doesn't block Phases A/B (building and
verifying Repo 2 locally).

## 6. A repo-local cited-source archive for DA/EA

Repo 1's `scripts/check_cited_source_archive.py` and `notes/cited-source-local-archive.md`
currently cover all three papers' cited sources in one file and one script (confirmed by
reading the script's glob list, which names `delegation-assurance.tex`,
`sections-delegation/*.tex`, `evidentiary-assurance.tex`, and `sections-evidentiary/*.tex`
alongside AP's own files). Neither file is something I could touch (both are on this
task's off-limits list, mid-edit by another session). Repo 2 needs its own version of both,
seeded from the DA/EA-relevant entries in Repo 1's current archive file. I flagged this as
a TODO in `repo2-Makefile-draft`'s `validate-sources` target rather than resolving it,
since it depends on files I couldn't read a final version of.

## 7. `AGENTS.md` / `GEMINI.md` in Repo 2

In this repository, `AGENTS.md`, `GEMINI.md`, and `CLAUDE.md` are byte-identical (verified
by reading all three). This task only asked for a `repo2-CLAUDE.md` draft. At execution
time, decide whether Repo 2 keeps that convention (three copies of the same content, one
per agent-CLI naming convention) or switches to one canonical file with the other two as
symlinks. `runbook.md` Phase A defaults to copying, not symlinking, matching Repo 1's
current setup; this is a small enough call that I didn't want to hold up the rest of the
draft on it, but it's worth a deliberate yes/no rather than defaulting silently.
