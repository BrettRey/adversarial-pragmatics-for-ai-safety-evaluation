# arXiv Submission Metadata

## Next revision (v3) target metadata

Title: Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control

Authors: Brett Reynolds

Primary category: cs.CL

Cross-list: cs.AI, cs.SE

Comments (draft, verified 2026-07-24 -- reverify at build time, sections are still being edited): 32-page main paper plus 13-page supplement; 6 figures and 17 tables total; code and data artifact available at the linked repository.

Repository: https://github.com/BrettRey/adversarial-pragmatics-for-ai-safety-evaluation

Public arXiv identifier: 2607.01153 (unchanged on a replacement)

**arXiv rule:** the primary category cannot be changed on a replacement without moderator intervention. v3 must keep cs.CL as primary. This corrects an earlier version of this file, which had the primary/cross-list pair inverted (cs.AI primary, cs.CL cross-list) relative to the live arXiv record. Cross-list categories can be changed on a replacement, but do it deliberately, not by default.

Notes for submission:

- Submit as original empirical benchmark/evaluation work, not as a review article or position paper.
- Use `submission/arxiv/adversarial-pragmatics-arxiv-source.tar.gz` as the single source-package upload after running `scripts/build_arxiv_bundle.sh`.
- The source package includes `adversarial-pragmatics-for-ai-safety-evaluation.tex` and `supplement.tex` as XeLaTeX top-level files using TeX Live 2025, so arXiv should assemble the paper and supplement into one generated PDF.
- Table count methodology: the main paper's 8 tables use the `table` environment; the supplement's 9 tables all use `longtable` (for page-breaking) but are captioned and numbered like ordinary tables. A grep for `\begin{table}` alone returns 0 for the supplement and undercounts the true total. Count both environments when citing a table total.

## Live arXiv record (v3, verified against arxiv.org/abs/2607.01153 on 2026-07-30)

Title (v3, live -- now matches the target title above; the v2 title lag is closed): Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control

Primary category: cs.CL

Cross-list: cs.AI, cs.SE

Comments (v3, exact, as rendered on the abs page): 32-page main paper plus 13-page supplement; 6 figures and 17 tables total; code and data artifact available at the linked repository

DOI: https://doi.org/10.48550/arXiv.2607.01153

Submission history (copied from the abs page's submission-history block):
- v1: 2026-07-01 16:33:14 UTC, 2,733 KB
- v2: 2026-07-15 18:56:34 UTC, 2,741 KB; announced 2026-07-16
- v3: 2026-07-29 15:40:42 UTC, 942 KB; announced in the 2026-07-30 mailing

Submission-system identifiers: submit/7776593 (v1), submit/7830880 (v2), submit/7884568 (v3). Each is historical and tied to its own submission transaction; the public identifier 2607.01153 stays the same across versions.

Abstract wording to respect on downstream surfaces: the v3 abstract does **not** claim multi-turn agent-transcript coverage. It says the framework "is designed to extend to multi-turn agent transcripts, but the seed set represents that family with a single-turn tool-result contrast." Any mirror, website description, or llms.txt entry that lists multi-turn agent transcripts among the covered phenomena is asserting what v3 deliberately pulled back.

## v3 replacement checklist

Must change:
- Title (from the v2 live title above to the current draft title)
- Abstract (`abstract.txt` -- confirm it matches the current draft, not the v2 abstract)
- Comments field (page/figure/table counts above; reverify against a fresh build before submitting, since sections are still being edited by other agents)

Must NOT change:
- Primary category (cs.CL; arXiv blocks a primary-category change on replacement without moderator action)
- DOI (https://doi.org/10.48550/arXiv.2607.01153; permanent once minted)
- Public arXiv identifier (2607.01153)

Discretionary (change only deliberately):
- Cross-list categories (currently cs.AI, cs.SE)

## v3 submission (2026-07-29)

- **Submission id:** `submit/7884568` -- Replacement of `2607.01153`.
- **Title submitted:** Adversarial Pragmatics for AI Safety Evaluation: A Diagnostic Framework and Seed Benchmark for Language-Mediated Control
- **Status:** ANNOUNCED public 2026-07-29. Paper password recorded in `private/arxiv-credentials.md`.
- **Source package:** built from commit `9181b71`; AP 32 pp, supplement 13 pp, 6 figures, 17 tables.
- **Unchanged, deliberately:** primary category cs.CL with cs.AI and cs.SE cross-listed; CC BY 4.0 licence (JAIR publishes CC BY, so the Springer preprint clause that ruled out Language Resources and Evaluation never applies); DOI `10.48550/arXiv.2607.01153`.
- **Package hygiene, changed after this submission:** the bundle shipped ten font files, four of them Charis SIL backing an `\ipafont` this submission never calls. `scripts/build_arxiv_bundle.sh` now detects `\ipafont` use in the document bodies and ships Charis SIL only when it is used, dropping the declaration with the files. Package fell from 2.7 MB to 1.3 MB. **The v3 upload used the older 2.7 MB package**; the slimmer one applies from v4 on.
