# Delegation Assurance and Evidentiary Assurance
<!-- SUMMARY: draft README for the new DA+EA repo; not yet placed at its final path - status: draft - updated: 2026-07-24 -->

This repository holds two companion papers by Brett Reynolds on authorization and
evidence for delegated machine action:

- **Delegation Assurance for AI Systems: Typed Authorization Semantics and Comparative
  Evaluation** (`delegation-assurance.tex`)
- **Evidentiary Assurance for Delegated Authority in AI Systems**
  (`evidentiary-assurance.tex`)

Both were written as a pair (their first commits in the parent repository landed the same
day, 2026-07-07) and split out here together because Evidentiary Assurance depends on
Delegation Assurance's typed vocabulary directly: its sufficiency test imports the
authority regime \(R\), the standing predicate \(\operatorname{Stand}_R(x,o,q,t)\), the
authorization-state and permitted-action functions \(Q_R(t)\) and \(A_R(t)\), and the six
named authority operations (grant, amend, suspend, revoke, override, release) from
Delegation Assurance before restating what it needs to be read on its own. Splitting them
from each other would buy nothing; splitting them out of the flagship benchmark repository
keeps that repository's own history and arXiv-linked build self-contained while giving
these two framework papers their own home.

## What each paper does

**Delegation Assurance** asks how an evaluator should represent and test whether an
operation or bounded trajectory executed through an AI deployment stayed within delegated
authority. It treats a single action as the trajectory case with \(n=1\), separates the
normative proposition from the record that represents it, separates item-level findings
and sample-level results from any claim about unobserved cases, and distinguishes a
closed-world stipulated authorization regime from an institutional regime whose identity
and applicability may themselves require adjudication. For language-mediated authority it
separates four fields: independently adjudicated **status** (is a string occurrence a
command, a quotation, a policy example, or something else), **authorization standing**
(does the source have the competence to act), **priority** (which directive controls under
conflict), and **licensing** (what the resolution of the first three actually authorizes).
A versioned closed-world engine and three frozen empirical programme specifications
(local-discrimination, predictive-ablation, reviewer-reconstruction) are executable today;
no target-study outcome is reported yet.

**Evidentiary Assurance** asks what a preserved record warrants about whether a contested
action was authorized, under a declared review procedure. A bad record does not make an
authorized action historically unauthorized, and a pristine record can document an invalid
delegation, so the historical question and the evidentiary one are answered separately. It
keeps four review outputs distinct rather than collapsing them into one assurance score:
what the record warrants about authorization (\(J_A\)), whether the record is adequate for
the declared review (\(J_R\)), whether an identifiable, dutied, reachable bearer exists to
answer for the action (\(J_B\)), and whether any forum has the access, competence,
independence, and remedial power to review it (\(J_C\)). \(J_B\) and \(J_C\) are evaluated
against named candidates, not abstractly, because properties satisfied piecemeal across
different parties describe no bearer and no route. An executable artifact (twenty matched
and adversarial fixtures, a validator, an analyser with in-memory self-tests, and a binding
stamper) tries to break the distinctions; because no reviewer has yet answered the
fixtures, the procedure is a research hypothesis, not a validated instrument.

## Relationship between the two papers

Read Delegation Assurance first if you are new to the stack: it supplies the authorization
claim, the regime, and the standing/status/priority/licensing vocabulary that Evidentiary
Assurance's sufficiency test (`sections-evidentiary/05-sufficiency-test.tex`) explicitly
imports and restates in miniature. Evidentiary Assurance does not redefine standing or
valid transition; it adds the evidentiary question on top, asking what a preserved record
lets a reviewer conclude about a claim Delegation Assurance already typed. Neither paper
proposes an enforcement, compensation, or deterrence mechanism; both are explicit that
authorization, record adequacy, answerability, and remedial capacity are separate
properties that a declared use may require jointly, but which the frameworks refuse to
collapse into one score.

## Build

Use XeLaTeX, not pdfLaTeX or LuaLaTeX.

```bash
make                  # builds both PDFs
make delegation       # delegation-assurance.pdf only
make evidentiary      # evidentiary-assurance.pdf only
make view-delegation  # open delegation-assurance.pdf (macOS)
make view-evidentiary # open evidentiary-assurance.pdf (macOS)
make assurance-check  # validate both executable artifacts and the shared claim protocol
```

`references.bib` is a vendored snapshot of the portfolio's central bibliography so this
repository builds independently; refresh it with `make vendor-bib` (maintainer action,
inside Brett's portfolio checkout). Project-only entries not yet pushed to the central bib
belong in `references-local.bib`.

## Layout

```text
delegation-assurance.tex           # Delegation Assurance entry point
sections-delegation/                # its section files
evidentiary-assurance.tex          # Evidentiary Assurance entry point
sections-evidentiary/               # its section files
assurance/delegation/               # regimes, traces, fixtures, frozen empirical specs
assurance/evidentiary/              # evidence bundles, applicability maps, matched cases
assurance/shared/                   # typed-claim vocabulary and projective-claim schema
                                     # shared with the flagship benchmark repository
notes/                              # working notes specific to these two papers
notes/pre-split-history/            # cross-paper notes and reviews inherited from the
                                     # repository these papers split out of; frozen record,
                                     # not synced with that repository going forward
reviews/                            # review-board and external-referee notes
scripts/                            # validators and analysers for both artifacts
submission/                         # venue-decision records and (later) submission packages
```

## Pre-split history

These two papers were developed inside
[`adversarial-pragmatics-for-ai-safety-evaluation`](https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation)
alongside the flagship *Adversarial Pragmatics* benchmark from 2026-07-07 until this split.
That repository's git history holds every commit from their creation forward, including
the commits and review cycles referenced in this repository's own `DECISIONS.md` history
before the split date. It also holds the flagship language-mediated-control benchmark,
annotation protocol, and pilot evidence that both papers cite
(`\citep{reynolds2026adversarialPragmatics}`) as their measurement layer. Consult it for
that prior history and for the benchmark itself; this repository does not duplicate either.

## License

Manuscript text, notes, and documentation are licensed under the Creative Commons
Attribution 4.0 International License (`CC-BY-4.0`). Source code, scripts, and build files
are licensed under the MIT License. See `LICENSE.md` and `LICENSES/`.
