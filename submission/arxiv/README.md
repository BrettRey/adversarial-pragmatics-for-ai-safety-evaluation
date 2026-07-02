# arXiv Submission Package

Recommended categories:

- Primary: `cs.AI`
- Cross-list: `cs.CL`

Build the source package from the repository root:

```bash
bash scripts/build_arxiv_bundle.sh
```

The generated archive is:

```text
submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz
```

The bundle is generated from tracked source files. It flattens the house-style preamble to `preamble.tex`, keeps section files under `sections/`, includes the PDF figures used by the paper, includes both `.bib` sources, bundles the open font files needed by XeLaTeX, and writes a `00README.json` that tells arXiv to compile `main.tex` and `supplement.tex` as XeLaTeX top-level files in that order using TeX Live 2025. The generated archive and build directory are intentionally ignored by git.

Upload notes:

- Submit the paper as original empirical benchmark/evaluation work.
- Use the text in `abstract.txt` for the arXiv abstract field.
- Public arXiv identifier: `2607.01153`.
- Use the category and comment fields in `metadata.md`.
- Upload the single generated `.tar.gz` source package. Do not upload the generated PDFs unless arXiv explicitly routes the submission through PDF-only processing.
