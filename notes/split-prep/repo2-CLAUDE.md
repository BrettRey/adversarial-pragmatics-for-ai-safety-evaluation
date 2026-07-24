# Delegation Assurance and Evidentiary Assurance
<!-- SUMMARY: draft project instructions for the new DA+EA repo, rewritten from the AP-framed CLAUDE.md - status: draft - updated: 2026-07-24 -->

This repository contains two companion papers by Brett Reynolds on authorization and
evidence standards for delegated machine action:

**Delegation Assurance for AI Systems: Typed Authorization Semantics and Comparative
Evaluation** (`delegation-assurance.tex`)

**Evidentiary Assurance for Delegated Authority in AI Systems**
(`evidentiary-assurance.tex`)

## Project Frame

These are conceptual and framework papers in AI governance and assurance, not empirical
evaluation papers. Neither reports a target-study result: both build executable artifacts
(versioned schemas, matched fixtures, validators, analysers with self-tests) to show that
their typed distinctions are representable and survive controlled attack, but the fixtures
are test fixtures, not calibration data, and every reported number in either paper is a
synthetic-regression or design-analysis output. Do not let AI-generated drafting default
to empirical framing ("we evaluated," "results show") where the honest claim is
conceptual, definitional, or about what an unexercised artifact can represent.

Delegation Assurance targets *Minds and Machines* (philosophy of computer science; see
`submission/venue-decision-2026-07-22.md`). Evidentiary Assurance targets an AI-governance
journal and has already been through two external-review rounds (major to minor revision).
Both are read by philosophers of computer science, AI-governance scholars, and technical
AI-safety/assurance practitioners, not primarily by corpus linguists or NLP evaluators.

## Central Thesis

**Delegation Assurance:** authorization is regime-relative and trajectory-scoped. A
complete, internally consistent trace of a machine action is compatible with that action
being unauthorized; a valid authorization can leave no trace at all; and per-action
authorization does not compose into authorization of a bounded sequence (step-local
permission at every step doesn't entail trajectory authorization). For language-mediated
authority the framework separates four fields: independently adjudicated **status** (is a
string occurrence a command, a quotation, a policy example, a tool result, or content for
analysis), **authorization standing** (does the source have the competence to perform a
specified authority operation), **priority** (which eligible directive controls under
conflict), and **licensing** (what that resolution authorizes). "Typed" means claim and
record objects are partitioned by bearer, inferential role, and machine-readable schema,
so moving from one to another has to be argued rather than read off a shared label; it is
not a static type system or a proof calculus.

**Evidentiary Assurance:** a preserved record and the historical fact of authorization are
different questions that must be answered separately. A bad record does not make an
authorized action historically unauthorized; a pristine record can document an invalid
delegation. The framework keeps four review outputs distinct rather than merging them into
one assurance score: authorization verdicts (\(J_A\)), record-adequacy verdicts (\(J_R\)),
answerability-bearer verdicts (\(J_B\)), and object-forum-capacity verdicts (\(J_C\)). The
last two are evaluated against named candidates, not in the abstract, because properties
satisfied piecemeal across different parties describe no bearer and no route. Five
evidentiary statuses (support, substantive defeat, not established, record gap, conflict)
replace a binary pass/fail, with an explicit precedence rule so "the record was never kept"
(a \(J_R\) gap) and "the record was kept and still doesn't support the claim" (not
established) are never collapsed into one finding.

## Required Project Shape

- Keep normative reference claims, recorded representations, item-level findings,
  sample-level results, assessment interpretations/uses, projective claims, and causal
  claims typed separately (`assurance/shared/claim-types.md` is the shared vocabulary both
  papers use; it is duplicated from the sibling flagship-benchmark repository and should be
  kept in sync with it, not treated as this repository's alone to evolve).
- Every nontrivial projection declares its bearer, unit, population, conditions,
  transformations, time/version, tolerance, use, warrant plan, and prospective revision
  rule. A post hoc scope restriction creates a new claim; it does not rescue the failed one.
- Treat validity (of an assessment interpretation and use) and authority validity (under a
  regime) as different properties. Neither is established by schema conformance alone.
- No target-study outcome exists yet for either paper's empirical programme. State this
  plainly rather than letting illustrative fixtures read as findings.
- A tolerance decision against a small sample gets an interval, not a point estimate
  compared to a cliff (see EA's Jeffreys-interval treatment in
  `sections-evidentiary/05-research-program.tex` and DA's design-analysis-by-simulation
  treatment in `scripts/design_analysis.py`); do not reintroduce a PASS/FAIL threshold
  where the underlying question is a rate with sampling uncertainty.

## Repository Layout

```text
delegation-assurance.tex           # Delegation Assurance entry point
sections-delegation/                # its section files
evidentiary-assurance.tex          # Evidentiary Assurance entry point
sections-evidentiary/               # its section files
assurance/delegation/               # regimes, traces, fixtures, frozen empirical specs
assurance/evidentiary/              # evidence bundles, applicability maps, matched cases
assurance/shared/                   # typed-claim vocabulary and projective-claim schema,
                                     # duplicated from the flagship-benchmark repository
notes/                              # working notes specific to these two papers
notes/pre-split-history/            # cross-paper notes inherited from the repository these
                                     # papers split out of; historical record, not synced
reviews/                            # review-board and external-referee notes
scripts/                            # validators and analysers for both artifacts
submission/                         # venue-decision records and submission packages
```

## Source Discipline

- Do not cite the setup prompt as if it verifies its linked claims.
- Before adding a citation or factual claim about an organization, law, regulation, safety
  report, or research agenda, verify the source and record it in the equivalent of
  `notes/source-verification.md` (port that file's discipline here if it does not yet
  exist at split time).
- New bibliographic entries belong in `references-local.bib` unless Brett explicitly asks
  for a central-bib update.
- Every cited external source should have genuine local full text or a complete local copy
  of the cited page recorded in an equivalent of `notes/cited-source-local-archive.md`.
  Both papers currently rely on the flagship repository's single archive file, which also
  covers *Adversarial Pragmatics*'s sources; this repository needs its own, seeded from the
  DA/EA entries in that file at split time.
- Do not leave project sources in `Downloads`; move verified copies into the shared
  literature archive and record their exact path and hash.
- Legal and governance sources (agency law, administrative-law record review,
  jurisdiction-specific doctrine) get the same source-grounding treatment as any other
  citation: read the primary text, do not reconstruct a doctrine from memory, and mark the
  legal survey's purposive (not systematic, not doctrinal-coverage) scope explicitly in
  prose, matching what both papers already say about their own method.

### Bibliography workflow

`references.bib` is a vendored full mirror of the portfolio's central bibliography, kept as
a real file (not a symlink) so this repository's build is self-contained. `/push-bib`
moves local entries into the central bib but does **not** refresh this vendored copy;
after any `/push-bib` run, `make vendor-bib` (refreshes `references.bib` from central;
`CENTRAL_BIB` overridable) must be run or every build in this repository silently loses
access to the moved entries, since they then live only in central. This exact failure mode
broke the sibling flagship repository's build on 2026-07-24 before `make vendor-bib` was
added there; do not repeat it here by skipping the step.

## Build and Checks

Use XeLaTeX, not pdfLaTeX or LuaLaTeX.

```bash
make                  # both PDFs
make delegation       # delegation-assurance.pdf only
make evidentiary      # evidentiary-assurance.pdf only
make assurance-check  # validate both executable artifacts and the shared claim protocol
```

Before any submission or public preprint:

- Run the central style checker on both top-level `.tex` files.
- Verify all sources in the source-verification note.
- Ensure no target-study outcomes are claimed anywhere in either manuscript; both are
  currently pre-empirical frameworks with executable-but-uncalibrated artifacts.

## Writing Priorities

- Engage the authorization, agency-law, and AI-governance literatures on their own terms;
  do not lead with linguistics or benchmark framing (that belongs to the sibling flagship
  repository, which these two papers cite as `\citep{reynolds2026adversarialPragmatics}`
  for the language-mediated-control measurement layer, not the other way round).
- Keep the formal apparatus honest about what it is: a meta-model at the normative and
  representational layers (DA), or a typed review architecture (EA), not a complete
  authorization language, a proof calculus, or a validated instrument.
- State plainly, every time it is true, that no target-study outcome exists yet and that a
  reported number is synthetic-regression or design-analysis output.
- Follow Rapoport's Rules when engaging a specific author's position (agency law, Santoni
  de Sio, Sterz et al., Novelli et al., Rashid, and similar): restate fairly, note genuine
  agreement, then critique.
- Make the distinctions reusable for model-policy teams, frontier-risk evaluators,
  red-teamers, system-card authors, and external assurance/legal-review teams, the same
  audience the sibling flagship repository's benchmark serves operationally.

## Key Terms

- Use `\term{}` for analytic terms and constructs.
- Use `\mention{}` for strings and prompt text.
- Use `\enquote{}` for quoted natural-language content.
- Keep `pdfkeywords` and the visible keyword line synchronized.
- `\textcite{}` for citations where the author is the grammatical subject performing an
  act (argues, shows, distinguishes); `\citep{}` for propositional or multi-source
  citation. Both papers currently use `\parencite{}` throughout, a known deviation from the
  portfolio's `\citep{}` house standard; normalize at the next polish pass rather than
  introducing more `\parencite{}` calls.
