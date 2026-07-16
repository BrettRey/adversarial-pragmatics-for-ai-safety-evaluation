# Draft Privacy and Release Boundary

**Status:** working policy draft, not a legal opinion or an approved data plan.

## Local-Only Material

The following stays under ignored `private/` paths and is never committed by
default:

- raw ChatGPT, Codex, and Claude Code exports;
- candidate repair episodes, unredacted context, and provenance maps;
- real evaluator response JSON, identity mappings, contact records, and
  evaluator-agreement administration;
- the private assignment registry, identifier-only byte attestation, and
  identity-side roster review, including rater-to-person, role, and package-ID
  bindings;
- blind-package maps linking opaque rows to model/item metadata;
- every individual first-pass vote, confidence value, and rationale, whether or
  not it appears identifying in isolation.

## Potentially Shareable Material

Only after manual review may the project share benign hand-authored prompts,
synthetic fixtures, public-safe schemas and protocols, aggregate results, and
sanitized object-level panel aggregates that create no reasonable privacy,
security, or re-identification concern. Individual-vote rows, confidence
values, and rationale language are not release candidates.

## Release Review Questions

1. Does the material contain a real person, organization, student, client,
   colleague, account, file path, secret, or third-party text?
2. Could surrounding context re-identify a conversation or reconstruct a
   private workflow?
3. Does a response reveal evaluator identity or enable linkage across studies?
4. Is the public artifact necessary to support a stated claim, or would an
   aggregate or synthetic representation suffice?

When in doubt, keep the material private, aggregate it, or make a controlled
synthetic derivative. Authenticity is not a reason to publish a private record.

Any real study should set a retention period, access roles, encrypted storage
practice, secure transfer route, deletion procedure, and role-based review path
before collecting outside ratings. Study A's transfer route will be the
access-controlled channel permitted by the final written scope determination
and data plan. Returned JSON files will be moved promptly and unchanged to the
local private study store; the transfer channel will not be the long-term
record store.

For Study A, the planned deletion rule is: a returned block is retained unless
the evaluator asks, through the stated contact route and pseudonymous rater ID,
for deletion before the published collection-close and analysis-start cutoff.
Before that cutoff, remove the corresponding private source files and rebuild
derived private tables. After the cutoff, returned data may already have
informed de-identified analysis or aggregate reporting, so deletion is not
promised. The actual cutoff, retention period, and secure transfer route remain
to be set before recruitment.
