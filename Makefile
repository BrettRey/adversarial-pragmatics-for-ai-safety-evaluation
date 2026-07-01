# Makefile for LaTeX paper compilation and benchmark checks
# Adversarial Pragmatics for AI Safety Evaluation

# Configuration
LATEX = xelatex
BIBER = biber
MAIN = main
SUPPLEMENT = supplement
OUTDIR = .
SECTION_TEX = $(wildcard sections/*.tex)
PILOT_MODELS ?= qwen3:8b gemma3:12b glm-4.7-flash:q4_K_M
PILOT_SMOKE_RUN_ID = smoke-$(shell date +%Y%m%d-%H%M%S)
JUDGE_MODEL ?= glm-4.7-flash:q4_K_M
JUDGE_PROMPT_VARIANT ?= compact
FAKE_DEV_ITEMS ?= 96
FAKE_DEV_SEED ?= 20260701
RUN_DIR ?=
RESPONSES ?=
SUMMARY_DIR ?= benchmark/results/summaries
RUN_DIR_ARG = $(if $(RUN_DIR),--run-dir $(RUN_DIR),)
RESPONSES_ARG = $(if $(RESPONSES),--responses $(RESPONSES),)
SUMMARY_DIR_ARG = $(if $(SUMMARY_DIR),--summary-dir $(SUMMARY_DIR),)

# Targets
.PHONY: all clean distclean view view-supplement help test validate-items pilot-local pilot-smoke pilot-diagnose pilot-review-app pilot-ingest-adjudication pilot-adjudication-report pilot-figures pilot-judge-validation fake-dev-calibration

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

# Validate the benchmark seed file
test:
	@echo "==> Validating benchmark seed items..."
	python3 scripts/validate_items.py benchmark/items/seed-items.csv

validate-items: test

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
	@echo "  make test     - Validate benchmark seed items"
	@echo "  make pilot-local - Run seed items on local Ollama models"
	@echo "  make pilot-smoke - Run two-item local Ollama smoke test"
	@echo "  make pilot-diagnose - Build adjudication/readout files for latest pilot"
	@echo "  make pilot-review-app - Build offline adjudication app for latest pilot"
	@echo "  make pilot-ingest-adjudication - Merge downloaded adjudication JSON"
	@echo "  make pilot-adjudication-report - Summarize adjudicated pilot labels"
	@echo "  make pilot-figures - Generate figures from sanitized pilot summaries"
	@echo "  make pilot-judge-validation - Validate local LLM judge against expert labels"
	@echo "  make fake-dev-calibration - Generate fake design-calibration summaries"
	@echo "  make help     - Show this help message"
