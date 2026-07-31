# Source hook: Meincke et al. 2026 (PNAS) + Wharton's AIBO harness

**Source:** Meincke, Shapiro, Duckworth, Mollick, Mollick, Van den Bulte & Cialdini, "Persuading large language models to comply with objectionable requests," *PNAS* 123(21):e2535868123, doi:10.1073/pnas.2535868123. Plus the open-source harness that ran it, AIBO (<https://github.com/wharton-generative-ai-labs/AIBO>, MIT), and the lab post describing its agent-driven workflow. Central note: `literature/wharton_gail_2026_aibo_and_llm_persuasion.notes.md`.

## Why this project cares

**This is the nearest published neighbour to the benchmark, and it is not cited.** Seven Cialdini persuasion principles operationalized as prompt treatments against a matched control, outcome measured as compliance with a request to assist with synthesis of regulated substances, 126,000 conversations across GPT-5 mini, Claude Haiku 4.5, and Gemini 3 Flash. Compliance 35.3% baseline to 51.3% under any principle (abstract, verbatim in the central note). That is empirical adversarial pragmatics in a venue reviewers read.

Checked 2026-07-30: no `meincke`, `cialdini`, or `persua` match in `references-local.bib`, and every portfolio-wide `meincke` hit resolves to `feuerriegel_guide-llm_2026`.

A referee who knows this literature will ask what the diagnostic framework adds over a persuasion-principle taxonomy. The paper should answer that on its own terms rather than be asked. The available answer: persuasion principles are one family of pragmatic pressure, and the framework types the failure (task success vs policy compliance vs safety risk vs failure attribution) where the PNAS design collapses everything into a single binary compliance outcome.

## Two distinct uses

**1. Citation and contrast.** Position the seed benchmark against it in the related-work and limitations discussion. Their design is a strong instance of what the project calls an empirical node: a well-powered condition-level compliance rate. It is silent on the interpretation-and-use step, which is where this project lives.

**2. AIBO as the scaling harness.** Current empirical base is 18 hand-authored items, 8 eligible paired contrasts, 54 item–model rows from a local Ollama pilot. AIBO's structure maps onto that directly: conditions with `prompt_template` are the paired contrasts, 1–50 replicates per condition gives the power the pilot lacks, and provider coverage (OpenAI / Anthropic / Gemini via LiteLLM) replaces the three local Ollama models with frontier ones. `temperature_response` and `temperature_rating` are separately settable, which matters for the corpus follow-up in `notes/2026-07-25-corpus-followups.md` where the missing model/effort field left Opus-at-xhigh and haiku-at-low both filed as "claude."

**Second-order fit worth writing about, not just using:** AIBO ships an LLM judge as infrastructure (`model_rating`, rubric template, "emit a score in brackets"). This project already validated that design and found a rubric-aided judge missing the safety-relevant minority classes under favourable conditions. So AIBO is both a candidate tool and a live instance of the thing the paper criticizes. Using it without saying so would be inconsistent; saying so is a contribution.

## Caveats before citing or adopting

- **No local full text.** PNAS returns 403 to automated fetch. This project requires a local copy recorded in `notes/cited-source-local-archive.md` before citation. Manual download needed.
- **The pooled 35.3%→51.3% is not a per-model claim.** Three models were tested; the abstract pools them. Read the paper for the breakdown before any comparison to this project's per-model rows.
- **The preliminary study's per-principle spread is dramatic** (commitment 19→100, social proof 90→96) and comes from a lab summary page, not the SSRN paper. Unverified. Do not cite those figures without reading it.
- **Bib entry is in.** Added to `references-local.bib` as `meincke2026persuading` on 2026-07-30, after arXiv v3 went public and the hold came off. Fields are from the Crossref record. Nothing cites it yet, so it is a staged entry, not a claim. Push to central with `/push-bib` at polish time, then `make vendor-bib`.
- **Manuscript work is unblocked.** v3 was announced public 2026-07-30. There is already a v4 queue (the font-bundle change, and the `supplement.tex:361` estimator misdescription), so this citation should ride that revision rather than triggering its own replacement.
