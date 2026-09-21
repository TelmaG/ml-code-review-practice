PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin
CASE ?=
NOTES ?=

.PHONY: setup setup-tools lint lint-all score list help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

$(BIN)/ml_smell_detector:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install --quiet --upgrade pip
	$(BIN)/pip install --quiet -r requirements.txt

setup: $(BIN)/ml_smell_detector ## Create venv and install tooling
	@echo "Done. Run: source .venv/bin/activate"

lint: ## Run ml_smell_detector on one case: make lint CASE=case-01-model-loading
	$(BIN)/ml_smell_detector analyze cases/$(CASE)/src --output-dir reports/$(CASE)/
	@cat reports/$(CASE)/analysis_report.txt

lint-all: ## Run ml_smell_detector on all cases
	$(BIN)/ml_smell_detector analyze cases --output-dir reports/all/ --ignore reference_fix __pycache__
	@cat reports/all/analysis_report.txt | tail -40

score: ## Score your notes: make score CASE=case-01-model-loading NOTES=notes/case-01.md
	$(BIN)/python tools/score_review.py --case cases/$(CASE) --notes $(NOTES)

list: ## List all cases
	@ls -d cases/case-*/
