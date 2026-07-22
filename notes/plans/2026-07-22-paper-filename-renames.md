# Paper filename rename plan
**Date:** 2026-07-22 **Scope:** The three paper entry points and their generated build artifacts in this repository.
## Rename map
| Paper | Current entry point | Useful entry point |
| --- | --- | --- |
| *Adversarial Pragmatics for AI Safety Evaluation* | `main.tex` | `adversarial-pragmatics-for-ai-safety-evaluation.tex` |
| *Delegation Assurance* | `delegation-assurance.tex` | unchanged |
| *Evidentiary Assurance* | `evidentiary-assurance.tex` | unchanged |

The Adversarial Pragmatics build will consequently produce `adversarial-pragmatics-for-ai-safety-evaluation.pdf` and matching auxiliary files. The old generated `main.*` files will be removed. `supplement.tex` and `supplement.pdf` remain unchanged because the requested problem is the generic `main.*` name, not the supplement's role.
## Dependencies to update
1. Rename the tracked TeX entry point while preserving Git history.
  
2. Change the Makefile's primary-paper stem so `make`, `make quick`, `make all-papers`, `make view`, `make clean`, and `make distclean` use the new name.
  
3. Update the Study B excellence validator and cited-source archive scanner to inspect the renamed entry point.
  
4. Update the arXiv bundler, its `00README.json`, and the submission README and metadata so the generated package contains the useful top-level filename rather than `main.tex`.
  
5. Update project instructions, status records, workflow examples, and source hooks that name the old entry point. Historical prose that merely says "main paper" remains unchanged; references to an unrelated external project's `main.tex` remain unchanged.
  
6. Remove stale ignored `main.*` build outputs and regenerate the paper-specific PDF and arXiv source bundle.
  
## Verification
- No project-owned file or generated artifact remains at `main.*`.
  
- No active build, validation, style, or arXiv instruction refers to `main.tex` or `main.pdf`.
  
- All three papers build under their useful filenames.
  
- The style checker passes on all three papers and the supplement.
  
- `make assurance-check` passes.
  
- The regenerated arXiv bundle names `adversarial-pragmatics-for-ai-safety-evaluation.tex` as its top-level source and compiles from a clean extraction.
  
- Unrelated untracked correspondence, Study A notes, archived material, and version history remain untouched.
