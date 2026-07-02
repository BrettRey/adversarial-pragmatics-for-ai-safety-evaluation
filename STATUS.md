# Adversarial Pragmatics for AI Safety Evaluation

Status: active scaffold created 2026-06-26.

Working title: *Adversarial Pragmatics for AI Safety Evaluation: A Benchmark for Instruction Conflict, Embedded Commands, and Policy Ambiguity*.

arXiv submission: assigned public identifier `arXiv:2607.01153` on 2026-07-01. Submission-system identifier: `submit/7776593`.

Core aim: write an empirical evaluation paper, not another primarily conceptual paper. The project should create a benchmark, annotation protocol, scoring framework, and policy/eval memo showing how linguistic judgment methodology can make AI safety evaluations more reliable and auditable.

Current assets:
- LaTeX paper skeleton with section files.
- Benchmark seed file with benign minimal-pair items.
- Taxonomy and annotation protocol drafts.
- Source-verification queue for the provided strategic links.
- Initial pressure test and objection matrix.

Next actions:
- Verify the external sources listed in `notes/source-verification.md`.
- Expand `benchmark/items/seed-items.csv` from 12 seed rows toward a 300--800 item benchmark plan.
- Decide the first model set and whether API outputs may be stored locally, summarized only, or excluded from git.
- Draft the policy/eval memo once the taxonomy and seed metrics are stable.
- Replace scaffold prose in `sections/` with sourced argument and preliminary results.

### 2026-07-01 Session Notes
- arXiv assigned the permanent identifier `2607.01153` to submission `submit/7776593`.
- arXiv metadata used: CC BY license; primary `cs.AI`; secondary `cs.CL`; third category `cs.SE`; comments field: `15-page main paper plus 9-page supplement; 6 figures and 8 tables total; code and data artifact available at the linked repository`.
- Final arXiv route is source upload, not PDF upload. `submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz` is the upload artifact.
- `scripts/build_arxiv_bundle.sh` now writes `00README.json`, orders `main.tex` then `supplement.tex` as XeLaTeX top-level files, declares bibliography resources directly in generated top-level TeX files, omits local `.bbl` files, strips macOS AppleDouble/xattrs, and bundles the open font files required by the generated arXiv preamble.
- arXiv processing succeeded under TeX Live 2025 with bundled fonts, compiled `main.tex` to 15 pages and `supplement.tex` to 9 pages, and merged them into one PDF.
- Fixed raw single-quote prompt fragments in `sections/03-taxonomy.tex` by replacing them with `\enquote{}` inside the relevant `\mention{}` examples.
