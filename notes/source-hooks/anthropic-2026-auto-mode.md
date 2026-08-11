# Source hook: Anthropic auto mode (2026-08-07)
<!-- SUMMARY: A shipping classifier that authorizes agent tool calls; lands on DA's one surviving claim and supplies the live industrial case the venue record said DA lacked · status: archived, uncited, DA is held · updated: 2026-08-08 -->

**Central note:** `literature/anthropic2026autoModeDefault-note.md`
**Archive:** `literature/anthropic2026autoModeDefault.html` (canonical, hashed) and `.md` derivative.
**Key:** `anthropic2026autoModeDefault`. Uncited. No pagination; cite by section heading.

## What it is

Anthropic, "Auto mode is now the default in Claude Code," 2026-08-07. A
classifier evaluates each proposed tool call and permits or blocks it instead of
prompting the user. Default for new Pro/Max/Team sessions from **2026-08-14**, so
it is an *announced* change, not yet an observed deployment. Includes a
controlled study (n=1,053), first-party telemetry, commissioned red-teaming, and
a commissioned competitor comparison.

## Why this project cares

**DA is held as of 2026-08-08** pending Brett's direction call after the canon
audit and priority sweep. This source bears directly on that call, in the paper's
favour, for two reasons.

**1. It is a live industrial instance of the one claim that survived.** The
priority sweep found category 1 open: no authorization semantics makes
classification of a natural-language string an input to the authorization
decision. Auto mode does exactly that, in production, at frontier scale, and
without a semantics. Tool results "are scanned by probes for potentially
malicious instructions, and auto mode checks that actions are aligned with user
intent." **The distinction DA can draw is sharp and favourable:** the probe's
output is *advisory* ~-- "a warning is added to Claude's context" ~-- not a typed
input to a verdict. Status is detected and then handed to a model to weigh, which
is precisely the un-semanticized handling DA argues needs typing.

**2. It fixes the venue record's weakest point.** `submission/venue-decision-2026-08-08.md`'s
Evidence and Motivation Test flags that the procurement case is constructed. This
is a real, dated, first-party, named-incident case at industrial scale.

## Claims it may support, by DA construct

Each maps onto vocabulary already defined in the paper, which is the useful part.

- **Tool gate** (§1 defines this term): the classifier *is* one, and Anthropic describes it in those terms.
- **Priority** (conflict rule among directives with relevant standing): "Permission rules still fire before the classifier in auto mode, except for allow rules broad enough to grant arbitrary code execution (e.g. `python:*`). These arbitrary rules are set aside while in auto mode." A user-conferred grant is overridden by the regime because honouring it would bypass the gate ~-- and "Settings files aren't modified," so the grant persists while being made inoperative. That is a standing/priority distinction, deployed.
- **Non-delegable limits**: hard denies, where "Data exfiltration … sits in a category the classifier is designed to never approve. To run an action like that, you have to switch out of auto mode or run the command yourself." Non-delegable *to the agent*, overridable *by the principal*. DA has the vocabulary for that asymmetry; the source has the case.
- **Regime-relative authorization**, in Anthropic's own words: the classifier "checks whether the destination of a git push or pull request is public, private, or trusted before the action runs. The same push can be routine or an exfiltration depending on where it lands."
- **Payload–scope fit**: the internal incident where "Asked to provision read-only billing access, Claude reached for a cloud role that grants full administrative control at the account root. Auto mode caught the mismatch between what was requested and what roles would have been granted."
- **Cumulative limit / trajectory**: "three blocks in a row, or twenty across a session" triggers fallback to manual. **Use as illustration only, not novelty** ~-- UCON owns cumulative limits (see `notes/canon-audit/claim-disposition.md`, (C-i) does not survive).

## What must be verified or decided before citation

- **Announced vs deployed.** Published 2026-08-07, effective 2026-08-14. State both dates; do not write that Anthropic "ships" or "runs" this as of today.
- **Re-fetch after 2026-08-14.** Corporate blog posts are mutable and this one has no version history. The archived HTML is the 2026-08-08 state and its hash is in the central note.
- **Type the claims.** This is a first-party vendor announcement about its own product, the same epistemic class as the OpenAI long-horizon report already handled in `DECISIONS.md` (2026-07-21). It supports construct motivation and attributed case description. It does **not** support prevalence, safeguard efficacy, or comparative model performance: no confidence intervals anywhere, the observational arm is doubly selected (safety-flagged sessions from training-opt-in accounts only), the severity and explicitness scales are model-graded with no validation or codebook, and the competitor comparison is harness- and version-bound with the competitor's own browser safeguards excluded by design.
- **The 89% vs 13.6% figure is the tempting one and the most misusable.** It is Anthropic evaluating its own feature against a human baseline it also characterizes as habituated. If used, report the design honestly: one swapped prompt per tester, purpose-built environment, participants aware they were being evaluated.

## Cross-references

- Blocks nothing. DA remains held; this is a hook for when the direction call is made.
- Also hooks the AP flagship (the 1,053-tester blinded design, and the two model-graded 0–10 scales as an unvalidated judge instrument) and EA (Apollo's held-out set with its explicit non-projection, which *supports* EA's projective-claim discipline). Both are described in the central note.
- Related: `notes/canon-audit/claim-disposition.md` for what DA can still claim; `notes/claude-code-security-mapping.md` for the earlier Claude Code security-docs routing, whose fidelity warning this note deliberately answers by archiving raw HTML.
