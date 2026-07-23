# Makefile for LaTeX paper compilation and benchmark checks
# Adversarial Pragmatics for AI Safety Evaluation

# Configuration
LATEX = xelatex
BIBER = biber
MAIN = adversarial-pragmatics-for-ai-safety-evaluation
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
STUDY_A_PRODUCTION_ROOT ?= private/study-a/production
STUDY_A_OPERATIONAL_CONFIG ?= $(STUDY_A_PRODUCTION_ROOT)/operational-config.json
STUDY_A_MANIFEST ?= benchmark/study-a/FREEZE-MANIFEST.json
STUDY_A_AUTHOR_SNAPSHOT ?= data/provisional/local-pilot-20260630-185417-provisional-author-labels.csv
DISCOVERY_RUN ?= private/discovery/synthetic
NATURALISTIC_DISCOVERY_RUN ?= private/discovery/naturalistic-pragmatic-extremes-synthetic
NATURALISTIC_DISCOVERY_RESTRICTED ?= private/restricted/naturalistic-pragmatic-extremes-synthetic
RUN_DIR ?=
RESPONSES ?=
SUMMARY_DIR ?= benchmark/results/summaries
RUN_DIR_ARG = $(if $(RUN_DIR),--run-dir $(RUN_DIR),)
RESPONSES_ARG = $(if $(RESPONSES),--responses $(RESPONSES),)
SUMMARY_DIR_ARG = $(if $(SUMMARY_DIR),--summary-dir $(SUMMARY_DIR),)

# Targets
.PHONY: all all-papers clean distclean view view-supplement view-delegation view-evidentiary delegation evidentiary help test validate-items validate-study-b analyze-study-b validate-claims validate-delegation validate-sources assurance-check privacy-check public-check phase1-check pilot-local pilot-smoke pilot-diagnose pilot-review-app pilot-ingest-adjudication pilot-adjudication-report pilot-figures pilot-judge-validation fake-dev-calibration study-a-synthetic study-a-self-pilot study-a-self-pilot-report study-a-judge-audit study-a-production-build study-a-manifest-stamp1 study-a-manifest-stamp2 study-a-manifest-verify study-a-freeze-ready study-a-collection-ready discovery-synthetic discovery-naturalistic-synthetic design-analysis vendor-bib

# Central house bibliography, vendored into this repo as references.bib so the
# public/arXiv build is self-contained.
CENTRAL_BIB ?= ../../../.house-style/references.bib

# Default target: build the paper and supplement PDFs
all: $(MAIN).pdf $(SUPPLEMENT).pdf

# Refresh the vendored references.bib from the portfolio central bib. Run this
# (a maintainer action, in Brett's portfolio checkout) after /push-bib moves
# entries into the central bib, so the self-contained build can resolve them.
# references-local.bib should hold only entries not yet pushed to central.
vendor-bib:
	@test -f "$(CENTRAL_BIB)" || { echo "central bib not found at $(CENTRAL_BIB); set CENTRAL_BIB=..."; exit 1; }
	cp "$(CENTRAL_BIB)" references.bib
	@echo "==> Vendored references.bib refreshed: $$(grep -c '^@' references.bib) entries from $(CENTRAL_BIB)"

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
	@echo "==> Evidentiary stamper freeze-guard tests..."
	python3 -m unittest scripts.test_stamp_evidentiary_artifacts

validate-items: test

# Validate the Study B development design and the production-result contract.
validate-study-b:
	@echo "==> Validating Study B development fixtures..."
	python3 scripts/validate_study_b.py
	python3 -m unittest scripts.test_validate_study_b
	python3 -m unittest scripts.test_validate_study_b_excellence
	python3 -m unittest scripts.test_analyze_study_b
	$(MAKE) analyze-study-b

# The committed record intentionally contains no target observations. This target
# validates schema v1.1 and must report NOT_ESTIMATED until target data exist;
# production-shaped inputs are rejected unless all frozen object and repeat hashes bind.
analyze-study-b:
	@echo "==> Checking Study B production-result record..."
	python3 scripts/analyze_study_b.py benchmark/study-b/production-results.no-target-data.json

# Validate the shared prospective projective-claim protocol. The negative
# fixture must fail; the validator's self-test checks both directions.
validate-claims:
	@echo "==> Validating prospective projective-claim protocol..."
	python3 scripts/validate_claim_register.py --self-test
	python3 scripts/validate_claim_register.py benchmark/study-b/claim-register.json
	python3 scripts/validate_claim_register.py assurance/delegation/projective-claim-register.json
	python3 scripts/validate_claim_register.py assurance/evidentiary/projective-claim-register.json

# Validate the Delegation Assurance semantics and all three frozen prospective
# empirical programmes. Synthetic tests exercise pass, fail, noncompensation,
# manifest integrity, split leakage, oracle masking, and zero-data output.
validate-delegation:
	@echo "==> Validating Delegation Assurance artifacts..."
	python3 scripts/validate_delegation_artifacts.py
	python3 scripts/analyze_delegation_programs.py --validate-specs
	python3 -m unittest scripts.test_validate_delegation_artifacts
	python3 -m unittest scripts.test_analyze_delegation_programs
	python3 -m unittest scripts.test_design_analysis

design-analysis:
	@echo "==> Running delegation design analysis (standard profile)..."
	python3 scripts/design_analysis.py --profile standard

validate-sources:
	@echo "==> Verifying cited-source local archive and hashes..."
	python3 scripts/check_cited_source_archive.py

# Run the projectibility/assurance artifacts for all three papers. These checks
# use only tracked schemas and harmless synthetic fixtures.
assurance-check: validate-claims validate-sources validate-study-b validate-delegation
	@echo "==> Validating excellence-revision assurance artifacts..."
	python3 scripts/validate_study_b_excellence.py
	python3 scripts/stamp_evidentiary_artifacts.py --check
	python3 scripts/validate_evidentiary_artifacts.py
	python3 scripts/analyze_evidentiary_calibration.py --self-test
	python3 scripts/analyze_evidentiary_calibration.py

# Verify the frozen historical pilot and local-only data boundary before Study A.
privacy-check:
	@echo "==> Checking private-data boundaries..."
	python3 scripts/check_private_boundaries.py

# Verify only tracked artifacts so this target works from a fresh clone.
public-check: test privacy-check
	@echo "==> Verifying tracked pilot artifact integrity..."
	python3 scripts/check_pilot_integrity.py --public-only

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

# Verify the retained comparator files and their actual role-separated,
# outcome-only prompt condition. Visible-rule mismatches remain diagnostics.
study-a-judge-audit:
	@echo "==> Verifying the Study A judge condition and diagnostic sentinels..."
	python3 scripts/audit_study_a_judge_condition.py --verify-output

# Build the ignored, local production package. The builder owns the two
# deterministic role-isolated ZIPs and retains its random row salt privately.
study-a-production-build: phase1-check study-a-judge-audit
	@echo "==> Building local Study A production packages..."
	python3 scripts/build_independent_reassessment.py --source $(STUDY_A_SELF_PILOT_SOURCE) --out-dir $(STUDY_A_PRODUCTION_ROOT)/package --private-dir $(STUDY_A_PRODUCTION_ROOT)/private --author-labels $(STUDY_A_AUTHOR_SNAPSHOT) --block-size 18

# Stamp 1 is a mutable pre-freeze checkpoint, not a completed freeze.
study-a-manifest-stamp1: study-a-judge-audit
	@echo "==> Writing semantic Study A checkpoint 1 (returns remain closed)..."
	python3 scripts/build_study_a_manifest.py --write --stamp 1 --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT)

# Stamp 2 records an already-built production package and becomes ready for an
# explicit commit/tag decision. It does not create that commit or tag.
study-a-manifest-stamp2: study-a-judge-audit
	@echo "==> Writing and verifying semantic Study A stamp-2 candidate..."
	python3 scripts/build_study_a_manifest.py --write --stamp 2 --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT)
	python3 scripts/check_study_a_freeze_ready.py --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT)

study-a-manifest-verify:
	@echo "==> Semantically verifying the active Study A manifest..."
	python3 scripts/build_study_a_manifest.py --verify --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT)

study-a-freeze-ready: study-a-judge-audit
	@echo "==> Checking whether Study A is ready for an explicit commit/tag decision..."
	python3 scripts/check_study_a_freeze_ready.py --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT)

study-a-collection-ready: study-a-judge-audit
	@echo "==> Checking tag-after-scope, stamp-2 bytes, assignments, identity-side roster review, finalized materials, and operational config v3..."
	python3 scripts/check_study_a_collection_ready.py --manifest $(STUDY_A_MANIFEST) --production-root $(STUDY_A_PRODUCTION_ROOT) --config $(STUDY_A_OPERATIONAL_CONFIG)

# Mine only the tracked synthetic conversation fixture and build an offline
# review page. Real histories belong under private/ and are never read here.
discovery-synthetic: privacy-check
	@echo "==> Building synthetic repair-episode discovery workflow..."
	python3 scripts/mine_repair_episodes.py --input data/fixtures/synthetic-repair-history.jsonl --source synthetic-fixture --out-dir $(DISCOVERY_RUN) --overwrite
	python3 scripts/build_repair_episode_review.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --out-dir $(DISCOVERY_RUN)/review --overwrite
	python3 scripts/simulate_repair_episode_decisions.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --out $(DISCOVERY_RUN)/synthetic-decisions.json
	python3 scripts/ingest_repair_episode_decisions.py --candidates $(DISCOVERY_RUN)/candidates.jsonl --decisions $(DISCOVERY_RUN)/synthetic-decisions.json --out-dir $(DISCOVERY_RUN)/processed

# Exercise both naturalistic-log adapters, the contrastive retrieval rules, and
# the expanded offline review page using synthetic records only.
discovery-naturalistic-synthetic: privacy-check
	@echo "==> Testing synthetic naturalistic pragmatic-extremes workflow..."
	python3 scripts/test_build_naturalistic_pragmatic_corpus.py
	python3 scripts/test_pragmatic_extremes_review.py
	python3 scripts/test_audit_naturalistic_corpus_privacy.py
	python3 scripts/test_validate_naturalistic_pragmatic_corpus_v2.py
	python3 scripts/build_naturalistic_pragmatic_corpus.py --codex-root data/fixtures/naturalistic-corpus/codex --claude-root data/fixtures/naturalistic-corpus/claude --out-dir $(NATURALISTIC_DISCOVERY_RUN) --restricted-dir $(NATURALISTIC_DISCOVERY_RESTRICTED) --review-limit 20 --minimum-source-age-minutes 0 --overwrite
	python3 scripts/build_pragmatic_extremes_review.py --candidates $(NATURALISTIC_DISCOVERY_RUN)/review-corpus.jsonl --out-dir $(NATURALISTIC_DISCOVERY_RUN)/review --overwrite
	python3 scripts/audit_naturalistic_corpus_privacy.py --corpus-dir $(NATURALISTIC_DISCOVERY_RUN) --restricted-dir $(NATURALISTIC_DISCOVERY_RESTRICTED) --output $(NATURALISTIC_DISCOVERY_RUN)/reports/privatization-audit.json
	python3 scripts/validate_naturalistic_pragmatic_corpus.py --corpus-dir $(NATURALISTIC_DISCOVERY_RUN) --restricted-dir $(NATURALISTIC_DISCOVERY_RESTRICTED)

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
	@echo "  make validate-study-b - Validate Study B design, pair/balance invariants, and result harness"
	@echo "  make analyze-study-b - Verify the manifest-bound target record (currently NOT_ESTIMATED)"
	@echo "  make privacy-check - Verify local-only research paths are Git-protected"
	@echo "  make public-check - Verify tracked benchmark and pilot artifacts from a fresh clone"
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
	@echo "  make study-a-judge-audit - Verify comparator structure and diagnostic sentinels"
	@echo "  make study-a-production-build - Build ignored role-isolated production packages"
	@echo "  make study-a-manifest-stamp1 - Write mutable semantic checkpoint 1"
	@echo "  make study-a-manifest-stamp2 - Record an existing production build as stamp 2"
	@echo "  make study-a-manifest-verify - Semantically verify the active manifest"
	@echo "  make study-a-freeze-ready - Check stamp 2 before an explicit commit/tag decision"
	@echo "  make study-a-collection-ready - Require tag-after-scope, stamp-2 bytes, assignments/roster review, finalized materials, and config v3"
	@echo "  make discovery-synthetic - Build the synthetic local repair-discovery workflow"
	@echo "  make discovery-naturalistic-synthetic - Test both private corpus adapters on synthetic logs"
	@echo "  make help     - Show this help message"
