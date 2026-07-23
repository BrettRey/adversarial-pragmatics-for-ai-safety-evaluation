# Captured: Claude Code security docs (2026-07-23)

**Fidelity note:** these are WebFetch-captured extractions (near-verbatim doc text with
exact quotes), not raw HTML. Before any final citation, take a proper HTML/PDF archive of
each page. Docs are versioned and change; access date 2026-07-23.

---

## Page 1 — Claude Code security
URL: https://code.claude.com/docs/en/security · accessed 2026-07-23

Permission-based architecture: "Claude Code uses strict read-only permissions by default.
When additional actions are needed (editing files, running tests, executing commands),
Claude Code requests explicit permission." Read-only commands (`ls`, `cat`, `git status`)
run without a prompt.

Working directory boundary: "Claude Code can only write to the folder where it was started
and its subfolders, and cannot modify files in parent directories without explicit
permission."

Prompt-injection core protections: "Permission system: Sensitive operations require
explicit approval"; "Context-aware analysis: Detects potentially harmful instructions by
analyzing the full request"; "Input sanitization"; "Network command approval" — `curl`/`wget`
not auto-approved.

Additional safeguards: "Isolated context windows: Web fetch uses a separate context window
to avoid injecting potentially malicious prompts"; "Trust verification: First-time codebase
runs and new MCP servers require trust verification"; "Command injection detection:
Suspicious bash commands require manual approval even if previously allowlisted";
"Fail-closed matching: Unmatched commands default to requiring manual approval"; "Secure
credential storage" (macOS Keychain).

MCP security: allowed-server list checked into source control; Anthropic "reviews connectors
against its listing criteria before adding them to the Anthropic Directory, but does not
security-audit or manage any MCP server."

Cloud execution: "Isolated virtual machines"; "Network access controls"; "Credential
protection: Authentication is handled through a secure proxy that uses a scoped credential
inside the sandbox, which is then translated to your actual GitHub authentication token";
"Branch restrictions: Git push operations are restricted to the current working branch";
"Audit logging: All operations in cloud environments are logged for compliance and audit
purposes." Remote Control: "multiple short-lived, narrowly scoped credentials, each limited
to a specific purpose and expiring independently, to limit the blast radius of any single
compromised credential."

User responsibility: "Claude Code only has the permissions you grant it. You're responsible
for reviewing proposed code and commands for safety before approval."

---

## Page 2 — Claude Security plugin (multi-agent scan)
URL: https://code.claude.com/docs/en/claude-security · accessed 2026-07-23

"A team of Claude agents maps your architecture, builds a threat model, hunts for
vulnerabilities, and independently reviews every finding before writing the report."

Revision stamp: `CLAUDE-SECURITY-REVISION-<commit>.json` "recording which commit was scanned,
at what effort, whether uncommitted changes were part of the scanned tree, and how thoroughly
the run was verified, so a report is always tied to the code it describes." "Scans are
nondeterministic: two scans of the same code can surface different findings... use the
revision stamps to attribute each report to the exact code and settings it covered."

Findings "only appear in the report after independent verifier agents analyze them."

Patch review: "each patch is reviewed by an agent independent of the one that wrote it...
A patch is written only when that review can vouch that the change addresses the one finding,
introduces no new vulnerability, and leaves behavior otherwise unchanged. When it can't vouch
for all three, you get a short note explaining why instead of a patch." "Patches are never
applied automatically."

Defense-in-depth stack: in-session security guidance / `/security-review` single pass /
plugin deep scan / PR-time Code Review / managed Claude Security / CI scanners.
