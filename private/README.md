# Local-Only Research Boundary

Everything in this directory except this notice is intentionally ignored by Git.

Use it for material that must remain on Brett's machine, including:

- raw ChatGPT, Codex, or Claude Code history exports;
- repair-episode candidates and provenance maps derived from those exports;
- real Study A blind-package maps, evaluator response files, and any mapping
  between a pseudonymous rater ID and a real person;
- unredacted contacts, consent records, and recruitment administration.

Do not place private material in `benchmark/`, `data/`, `notes/`, or a tracked
results summary. Public outputs must be synthetic, controlled, or thoroughly
sanitized before they leave this directory.

The repository's `make privacy-check` target verifies that this boundary and
the ignored Study A run location remain protected. It cannot determine whether
an individual file is safe to share; Brett must make that release decision.
