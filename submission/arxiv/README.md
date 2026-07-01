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

The bundle is generated from tracked source files. It flattens the house-style preamble to `preamble.tex`, keeps section files under `sections/`, includes the PDF figures used by the paper, and includes both bibliography files. The generated archive and build directory are intentionally ignored by git.

Upload notes:

- Submit the paper as original empirical benchmark/evaluation work.
- Use the text in `abstract.txt` for the arXiv abstract field.
- Use the category and comment fields in `metadata.md`.
- If arXiv allows ancillary files for the submission, attach `supplement.pdf`; otherwise the supplement source remains in the source package and the compiled supplement is available from the linked repository.
