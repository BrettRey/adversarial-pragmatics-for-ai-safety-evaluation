# Makefile for LaTeX paper compilation and benchmark checks
# Adversarial Pragmatics for AI Safety Evaluation

# Configuration
LATEX = xelatex
BIBER = biber
MAIN = main
SUPPLEMENT = supplement
DELEGATION = delegation-assurance
EVIDENTIARY = evidentiary-assurance
OUTDIR = .
SECTION_TEX = $(wildcard sections/*.tex)
DELEGATION_SECTION_TEX = $(wildcard sections-delegation/*.tex)
EVIDENTIARY_SECTION_TEX = $(wildcard sections-evidentiary/*.tex)
PILOT_MODELS ?= qwen3:8b gemma3:12b glm-4.7-flash:q4_K_M
PILOT_SMOKE_RUN_ID = smoke-$(shell date +%Y%m%d-%H%M%S)
JUDGE_MODEL ?= glm-4.7-flash:q4_K_M
JUDGE_PROMPT_VARIANT ?= compact
FAKE_DEV_ITEMS ?= 96
FAKE_DEV_SEED ?= 20260701
STUDY_A_RUN ?= benchmark/study-a/_runs/synthetic
STUDY_A_SELF_PILOT_SOURCE ?= benchmark/results/local-pilot-20260630-185417/outputs.csv
STUDY_A_SELF_PILOT_RUN ?= private/study-a/self-pilot
STUDY_A_SELF_PILOT_RESPONSES ?= $(STUDY_A_SELF_PILOT_RUN)/responses
STUDY_A_SELF_PILOT_REPORT ?= $(STUDY_A_SELF_PILOT_RUN)/report
DISCOVERY_RUN ?= private/discovery/synthetic
RUN_DIR ?=
RESPONSES ?=
SUMMARY_DIR ?= benchmark/results/summaries
RUN_DIR_ARG = $(if $(RUN_DIR),--run-dir $(RUN_DIR),)
RESPONSES_ARG = $(if $(RESPONSES),--responses $(RESPONSES),)
SUMMARY_DIR_ARG = $(if $(SUMMARY_DIR),--summary-dir $(SUMMARY_DIR),)

# Targets
.PHONY: all all-papers clean distclean view view-supplement view-delegation view-evidentiary delegation evidentiary help test validate-items privacy-check phase1-check pilot-local pilot-smoke pilot-diagnose pilot-review-app pilot-ingest-adjudication pilot-adjudication-report pilot-figures pilot-judge-validation fake-dev-calibration study-a-synthetic study-a-self-pilot study-a-self-pilot-report discovery-synthetic

# Default target: build the paper and supplement PDFs
all: $(MAIN).pdf $(SUPPLEMENT).pdf

# Full build sequence with bibliography
$(MAIN).pdf: $(MAIN).tex $(SECTION_TEX) references.bib references-local.bib
	@echo "==> First LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN).tex
	@echo "==> Running Biber..."
	$(BIBER) $(MAIN)
	@echo "==> Second LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN).tex
	@echo "==> Third LaTeX pass (finalizing)..."
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN).tex
	@echo "==> Build complete: $(MAIN).pdf"

$(SUPPLEMENT).pdf: $(SUPPLEMENT).tex
	@echo "==> First supplement LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(SUPPLEMENT).tex
	@echo "==> Running Biber for supplement..."
	$(BIBER) $(SUPPLEMENT)
	@echo "==> Second supplement LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(SUPPLEMENT).tex
	@echo "==> Third supplement LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(SUPPLEMENT).tex
	@echo "==> Build complete: $(SUPPLEMENT).pdf"

$(DELEGATION).pdf: $(DELEGATION).tex $(DELEGATION_SECTION_TEX) references.bib references-local.bib
	@echo "==> First delegation-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(DELEGATION).tex
	@echo "==> Running Biber for delegation-assurance..."
	$(BIBER) $(DELEGATION)
	@echo "==> Second delegation-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(DELEGATION).tex
	@echo "==> Third delegation-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(DELEGATION).tex
	@echo "==> Build complete: $(DELEGATION).pdf"

delegation: $(DELEGATION).pdf

$(EVIDENTIARY).pdf: $(EVIDENTIARY).tex $(EVIDENTIARY_SECTION_TEX) references.bib references-local.bib
	@echo "==> First evidentiary-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(EVIDENTIARY).tex
	@echo "==> Running Biber for evidentiary-assurance..."
	$(BIBER) $(EVIDENTIARY)
	@echo "==> Second evidentiary-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(EVIDENTIARY).tex
	@echo "==> Third evidentiary-assurance LaTeX pass..."
	$(LATEX) -output-directory=$(OUTDIR) $(EVIDENTIARY).tex
	@echo "==> Build complete: $(EVIDENTIARY).pdf"

evidentiary: $(EVIDENTIARY).pdf

all-papers: $(MAIN).pdf $(DELEGATION).pdf $(EVIDENTIARY).pdf

# Quick build (single pass, no bibliography update)
quick: $(MAIN).tex $(SECTION_TEX)
	@echo "==> Quick build (single pass)..."
	$(LATEX) -output-directory=$(OUTDIR) $(MAIN).tex

# Use LuaLaTeX instead of XeLaTeX (not recommended - breaks PDF text layer)
lualatex: LATEX = lualatex
lualatex: all

# Clean build artifacts (keep PDF)
clean:
	@echo "==> Cleaning build artifacts..."
	rm -f $(MAIN).aux $(MAIN).bbl $(MAIN).bcf $(MAIN).blg $(MAIN).log
	rm -f $(MAIN).out $(MAIN).run.xml $(MAIN).toc $(MAIN).fdb_latexmk
	rm -f $(MAIN).fls $(MAIN).synctex.gz
	rm -f $(SUPPLEMENT).aux $(SUPPLEMENT).bbl $(SUPPLEMENT).bcf $(SUPPLEMENT).blg $(SUPPLEMENT).log
	rm -f $(SUPPLEMENT).out $(SUPPLEMENT).run.xml $(SUPPLEMENT).toc $(SUPPLEMENT).fdb_latexmk
	rm -f $(SUPPLEMENT).fls $(SUPPLEMENT).synctex.gz
	rm -f $(DELEGATION).aux $(DELEGATION).bbl $(DELEGATION).bcf $(DELEGATION).blg $(DELEGATION).log
	rm -f $(DELEGATION).out $(DELEGATION).run.xml $(DELEGATION).toc $(DELEGATION).fdb_latexmk
	rm -f $(DELEGATION).fls $(DELEGATION).synctex.gz
	rm -f $(EVIDENTIARY).aux $(EVIDENTIARY).bbl $(EVIDENTIARY).bcf $(EVIDENTIARY).blg $(EVIDENTIARY).log
	rm -f $(EVIDENTIARY).out $(EVIDENTIARY).run.xml $(EVIDENTIARY).toc $(EVIDENTIARY).fdb_latexmk
	rm -f $(EVIDENTIARY).fls $(EVIDENTIARY).synctex.gz
	@echo "==> Clean complete"

# Clean everything including PDF
distclean: clean
	@echo "==> Removing PDF..."
	rm -f $(MAIN).pdf $(SUPPLEMENT).pdf
	@echo "==> Deep clean complete"

# Open PDF viewer (macOS)
view: $(MAIN).pdf
	@echo "==> Opening PDF..."
	open $(MAIN).pdf

view-supplement: $(SUPPLEMENT).pdf
	@echo "==> Opening supplement PDF..."
	open $(SUPPLEMENT).pdf

view-delegation: $(DELEGATION).pdf
	@echo "==> Opening delegation-assurance PDF..."
	open $(DELEGATION).pdf

view-evidentiary: $(EVIDENTIARY).pdf
	@echo "==> Opening evidentiary-assurance PDF..."
	open $(EVIDENTIARY).pdf

# Validate the benchmark seed file
test:
	@echo "==> Validating benchmark seed items..."
	python3 scripts/validate_items.py benchmark/items/seed-items.csv

validate-items: test

# Verify the frozen historical pilot and local-only data boundary before Study A.
privacy-check:
	@echo "==> Checking private-data boundaries..."
	python3 scripts/check_private_boundaries.py

phase1-check: test privacy-check
	@echo "==> Verifying frozen local pilot..."
	python3 scripts/check_pilot_integrity.py

# Run the seed benchmark against the default local Ollama model set
pilot-local: test
	@echo "==> Running local Ollama pilot..."
	python3 scripts/run_local_pilot.py --models $(PILOT_MODELS)

# Run a two-item smoke test without committing generated outputs
pilot-smoke: test
	@echo "==> Running local Ollama pilot smoke test..."
	python3 scripts/run_local_pilot.py --limit 2 --run-id $(PILOT_SMOKE_RUN_ID) --out-dir benchmark/results/_scratch --models $(PILOT_MODELS)

# Prepare adjudication and diagnostic files for the latest local pilot run
pilot-diagnose:
	@echo "==> Preparing local pilot diagnostic readout..."
	python3 scripts/diagnose_local_pilot.py $(RUN_DIR_ARG)

# Build an offline browser app for human adjudication of pilot rows
pilot-review-app:
	@echo "==> Building local adjudication review app..."
	python3 scripts/build_adjudication_review_app.py $(RUN_DIR_ARG)

# Merge downloaded adjudication JSON files into pilot tables
pilot-ingest-adjudication:
	@echo "==> Ingesting local adjudication responses..."
	python3 scripts/ingest_adjudication_responses.py $(RUN_DIR_ARG) $(RESPONSES_ARG)

# Summarize adjudicated pilot labels for manuscript use
pilot-adjudication-report:
	@echo "==> Summarizing adjudicated local pilot results..."
	python3 scripts/summarize_adjudication_pilot.py $(RUN_DIR_ARG) $(SUMMARY_DIR_ARG)

# Generate manuscript and supplement figures from sanitized pilot summaries
pilot-figures:
	@echo "==> Generating local pilot figures..."
	python3 scripts/plot_pilot_results.py --summary-dir $(SUMMARY_DIR)

# Validate LLM-judge labels against adjudicated local pilot labels
pilot-judge-validation:
	@echo "==> Running LLM-judge validation on adjudicated pilot rows..."
	python3 scripts/run_llm_judge_validation.py $(RUN_DIR_ARG) $(SUMMARY_DIR_ARG) --model $(JUDGE_MODEL) --prompt-variant $(JUDGE_PROMPT_VARIANT)

# Generate fake data for development-pass design calibration
fake-dev-calibration:
	@echo "==> Generating fake development-pass calibration data..."
	python3 scripts/simulate_dev_pass.py --items $(FAKE_DEV_ITEMS) --seed $(FAKE_DEV_SEED) --summary-dir $(SUMMARY_DIR)

# Run the complete blinded Study A workflow using synthetic source rows,
# synthetic rater responses, and synthetic judge labels. No empirical result is
# created by this target.
study-a-synthetic: privacy-check
	@echo "==> Running synthetic Study A re-adjudication workflow..."
	python3 scripts/simulate_independent_reassessment.py --out-dir $(STUDY_A_RUN) --overwrite

# Build a local-only package for Brett to time and inspect the real 54-row form.
# Its study ID is deliberately rejected by independent-rating ingestion.
study-a-self-pilot: phase1-check
	@echo "==> Building local Study A interface self-pilot..."
	python3 scripts/build_independent_reassessment.py --source $(STUDY_A_SELF_PILOT_SOURCE) --out-dir $(STUDY_A_SELF_PILOT_RUN)/package --private-dir $(STUDY_A_SELF_PILOT_RUN)/private --self-pilot --overwrite

study-a-self-pilot-report:
	@echo "==> Summarizing local Study A self-pilot timing..."
	python3 scripts/summarize_study_a_self_pilot.py --responses $(STUDY_A_SELF_PILOT_RESPONSES) --out-dir $(STUDY_A_SELF_PILOT_REPORT)

# Mine only the tracked synthetic conversation fixture and build an offline
# review page. Real histories belong under private/ and are never read here.
discovery-synthetic: privacy-check
	@echo "==> Building synthetic repair-episode discovery workflow..."
	python3 scripts/mine_repair_episodes.py --input data/fixtures/synthetic-repair-history.jsonl --source synthetic-fixture --out-dir $(DISCOVERY_RUN) --overwrite
	python3 scripts/build_repair_episode_review.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --out-dir $(DISCOVERY_RUN)/review --overwrite
	python3 scripts/simulate_repair_episode_decisions.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --out $(DISCOVERY_RUN)/synthetic-decisions.json
	python3 scripts/ingest_repair_episode_decisions.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --decisions $(DISCOVERY_RUN)/synthetic-decisions.json --out-dir $(DISCOVERY_RUN)/processed

# Show available targets
help:
	@echo "Available targets:"
	@echo "  make          - Build PDF with full bibliography (default)"
	@echo "  make supplement.pdf - Build supplementary material PDF"
	@echo "  make quick    - Quick build (single pass, no bib update)"
	@echo "  make lualatex - Build using LuaLaTeX (not recommended)"
	@echo "  make clean    - Remove build artifacts (keep PDF)"
	@echo "  make distclean- Remove everything including PDF"
	@echo "  make view     - Open PDF (macOS only)"
	@echo "  make view-supplement - Open supplementary material PDF"
	@echo "  make delegation - Build delegation-assurance paper PDF"
	@echo "  make view-delegation - Open delegation-assurance paper PDF"
	@echo "  make evidentiary - Build evidentiary-assurance paper PDF"
	@echo "  make view-evidentiary - Open evidentiary-assurance paper PDF"
	@echo "  make all-papers - Build all three paper PDFs"
	@echo "  make test     - Validate benchmark seed items"
	@echo "  make privacy-check - Verify local-only research paths are Git-protected"
	@echo "  make phase1-check - Verify the frozen historical 54-row pilot"
	@echo "  make pilot-local - Run seed items on local Ollama models"
	@echo "  make pilot-smoke - Run two-item local Ollama smoke test"
	@echo "  make pilot-diagnose - Build adjudication/readout files for latest pilot"
	@echo "  make pilot-review-app - Build offline adjudication app for latest pilot"
	@echo "  make pilot-ingest-adjudication - Merge downloaded adjudication JSON"
	@echo "  make pilot-adjudication-report - Summarize adjudicated pilot labels"
	@echo "  make pilot-figures - Generate figures from sanitized pilot summaries"
	@echo "  make pilot-judge-validation - Validate local LLM judge against expert labels"
	@echo "  make fake-dev-calibration - Generate fake design-calibration summaries"
	@echo "  make study-a-synthetic - Run the synthetic blinded re-adjudication workflow"
	@echo "  make study-a-self-pilot - Build the local, non-ingestible 54-row interface self-pilot"
	@echo "  make study-a-self-pilot-report - Summarize local self-pilot timing only"
	@echo "  make discovery-synthetic - Build the synthetic local repair-discovery workflow"
	@echo "  make help     - Show this help message"
