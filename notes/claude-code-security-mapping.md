# Claude Code security docs — mapping to AP / DA / EA
<!-- SUMMARY: what the two Claude Code security pages give the three papers, framed as gap-setup not validation; candidate insertions + citability record · status: draft-for-placement · updated: 2026-07-23 -->

Sources (captured 2026-07-23, versioned docs — re-verify before final cite):
- `anthropic2026claudeCodeSecurity` — Claude Code security (trust, permissions, safeguards), https://code.claude.com/docs/en/security
- `anthropic2026claudeSecurityPlugin` — Claude Security plugin (multi-agent scan), https://code.claude.com/docs/en/claude-security

Local capture: `notes/sources/claude-code-security-2026-07-23.md`. bib: `references-local.bib`.

## Framing decision (see conversation 2026-07-23)
Use the convergence as **gap-setup, not validation**. The outer assurance shell (bind
results to versioned objects, independent verification, non-compensatory verdicts,
abstain-not-force, tool gates, fail-closed, scoped credentials) is now standard first-party
practice; cite it as mature background, never as a contribution. The papers' contribution is
the **typed semantic core the deployed systems lack**: linguistic status (AP), typed
authorization semantics (DA), typed evidentiary statuses (EA), and the four projectibility
bearers. Lead there.

## Candidate insertion — DA (§ agent security or language-mediated authority)
> Anthropic's own coding agent shows both the maturity of the tool-gate layer and its limit.
> Claude Code gates actions through explicit permissions, defaults to read-only, fails closed
> on unmatched commands, requires fresh approval for suspicious commands even under a broad
> allowlist, and, in its cloud form, issues each session a short-lived, narrowly scoped
> credential to limit the blast radius of a compromise \parencite{anthropic2026claudeCodeSecurity}.
> These are the confused-deputy defences Hardy anticipated \parencite{hardy1988confusedDeputy},
> now standard practice. What the model doesn't supply is the typed authorization proposition
> the gate is meant to enforce: it screens commands by class and path, not by the contextual
> status or standing of the language that requested them, and its record binds an action to a
> command and a directory rather than to a governing grant and an adjudicated verdict. The gate
> decides; it doesn't establish that the decision was authorized under \(R\), or leave a record
> from which that could be reconstructed. Delegation assurance supplies the proposition and the
> evidence the gate presupposes.

## Candidate insertion — AP (§ pass/fail or judge validation, one or two sentences)
> The discipline isn't peculiar to benchmarks. First-party agent tooling separates verdicts the
> same way: a code-scanning agent reports a patch only when an independent reviewer can vouch,
> non-compensatorily, that it fixes the one finding, adds no new vulnerability, and changes
> nothing else, and it returns an explicit abstention rather than a patch when it can't
> \parencite{anthropic2026claudeSecurityPlugin}. What deployed tooling still lacks is a typing
> of the linguistic criteria a safety judgment turns on, and of the distinct ways a result fails
> to generalize.

## Candidate insertion — EA (§ evidence primitives or record adequacy)
> Deployed assurance tooling already binds a result to the object it describes: a code scan
> stamps each report with the commit, the effort, whether the working tree was clean, and how
> thoroughly the run was verified, and states that repeated scans of the same code can differ
> \parencite{anthropic2026claudeSecurityPlugin}. That is record adequacy in practice. It stops
> short of typing what the record warrants: the stamp is one blob, not the separation of
> support, not-established, record gap, and defeat that an action-level review needs.

## Smaller documented mechanisms (for tables / footnotes, all from the security page)
- Web fetch runs in an isolated context window to avoid injected prompts → AP embedded-command / source-role separation, a deployed defence.
- `curl`/`wget` not auto-approved; push restricted to current branch → AP confidentiality/exfiltration + DA egress/persistence licensing.
- "Context-aware analysis detects potentially harmful instructions" → an unaudited safety-classifier; cite as a thing to validate, not evidence.
- MCP: reviewed against listing criteria but "does not security-audit or manage" → EA "not established"; answerability-route ≠ remedy-forum.
- Cloud audit logging of all operations → EA reconstruction record.

## What NOT to claim
- Do not present provenance-binding, judge-validation, gating, or verification as novel; they are cited background.
- The security page has no instruction-vs-data *semantics* — it can't validate mention/use or standing-vs-priority; it exemplifies the gap.
- "Detects harmful instructions" is black-box; do not cite as evidence a distinction is solved.
