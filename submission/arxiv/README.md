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

The bundle is generated from tracked source files. It flattens the house-style preamble to `preamble.tex` (and rewrites both toplevels to `\input{preamble.tex}`, never `.house-style/`), keeps section files under `sections/`, includes the PDF figures used by the paper, includes both `.bib` sources, and writes a `00README.json` that tells arXiv to compile `main.tex` and `supplement.tex` as XeLaTeX top-level files in that order using TeX Live 2025. The generated archive and build directory are intentionally ignored by git.

Fonts are bundled at the package top level (not a `fonts/` subdir) and referenced by bare filename with no `Path=`. Top-level + bare filename means kpathsea finds the bundled copy in the build directory; if arXiv strips the uploaded font binaries, the same bare filenames still resolve against TeX Live's `ebgaramond` / `inconsolata` / `charissil`. Do NOT reintroduce a `fonts/` subdir with `Path=fonts/`: that combination is what failed on arXiv (`The font "EBGaramond-Regular" cannot be found`). Verified: both toplevels build from a clean extraction (main 18pp, supplement 10pp, no font errors, no undefined citations).

Upload notes:

- Submit the paper as original empirical benchmark/evaluation work.
- Use the text in `abstract.txt` for the arXiv abstract field.
- Public arXiv identifier: `2607.01153`.
- Use the category and comment fields in `metadata.md`.
- For the next public revision, confirm that the generated PDF matches the
  repaired paired-contrast readout: P008 excluded and 12/24 eligible
  paired-contrast passes, with no claim that the seed materials are uniformly
  strict minimal pairs.
- Upload the single generated `.tar.gz` source package. Do not upload the generated PDFs unless arXiv explicitly routes the submission through PDF-only processing.
