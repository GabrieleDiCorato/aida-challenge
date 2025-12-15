.PHONY: help install setup clean test docs all

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

##@ Help
help: ## Display this help message
	@echo "$(BLUE)AIDA Challenge - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Environment Setup
install: ## Install Python dependencies with UV
	@echo "$(BLUE)Installing dependencies...$(NC)"
	uv sync

install-all: ## Install all dependencies including optional ones
	@echo "$(BLUE)Installing all dependencies...$(NC)"
	uv sync --all-extras

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	uv sync --extra dev

install-analysis: ## Install analysis dependencies (jupyter, matplotlib, etc.)
	@echo "$(BLUE)Installing analysis dependencies...$(NC)"
	uv sync --extra analysis

setup: install ## Setup the project (install deps)
	@echo "$(GREEN)✓ Project setup complete!$(NC)"

##@ dbt Commands
dbt-debug: ## Test dbt connection
	@echo "$(BLUE)Testing dbt connection...$(NC)"
	uv run dbt-debug

dbt-deps: ## Install dbt packages
	@echo "$(BLUE)Installing dbt dependencies...$(NC)"
	uv run dbt-deps

dbt-run: ## Run all dbt models
	@echo "$(BLUE)Running all dbt models...$(NC)"
	uv run dbt-run

dbt-test: ## Run all dbt tests
	@echo "$(BLUE)Running dbt tests...$(NC)"
	uv run dbt-test

dbt-build: ## Build and test all dbt models
	@echo "$(BLUE)Building and testing dbt models...$(NC)"
	uv run dbt-build

dbt-clean: ## Clean dbt artifacts
	@echo "$(BLUE)Cleaning dbt artifacts...$(NC)"
	uv run dbt-clean

##@ dbt Model-Specific
dbt-staging: ## Run staging models only
	@echo "$(BLUE)Running staging models...$(NC)"
	uv run dbt-run-staging

dbt-intermediate: ## Run intermediate models only
	@echo "$(BLUE)Running intermediate models...$(NC)"
	uv run dbt-run-intermediate

dbt-marts: ## Run marts models only
	@echo "$(BLUE)Running marts models...$(NC)"
	uv run dbt-run-marts

dbt-test-sources: ## Test source data
	@echo "$(BLUE)Testing source data...$(NC)"
	uv run dbt-test-sources

##@ dbt Documentation
dbt-docs: ## Generate and serve dbt documentation
	@echo "$(BLUE)Generating dbt documentation...$(NC)"
	uv run dbt-docs-generate
	@echo "$(GREEN)Opening documentation server...$(NC)"
	uv run dbt-docs-serve

dbt-docs-generate: ## Generate dbt documentation
	@echo "$(BLUE)Generating dbt documentation...$(NC)"
	uv run dbt-docs-generate

##@ dbt Workflows
dbt-setup: ## Setup dbt (debug + deps)
	@echo "$(BLUE)Setting up dbt...$(NC)"
	uv run dbt-setup

dbt-full-refresh: ## Full refresh all models and test
	@echo "$(BLUE)Running full refresh...$(NC)"
	uv run dbt-full-refresh

dbt-pipeline: ## Run complete dbt pipeline (staging -> intermediate -> marts -> test)
	@echo "$(BLUE)Running complete dbt pipeline...$(NC)"
	@$(MAKE) dbt-staging
	@$(MAKE) dbt-intermediate
	@$(MAKE) dbt-marts
	@$(MAKE) dbt-test
	@echo "$(GREEN)✓ Pipeline complete!$(NC)"

##@ Jupyter
notebook: ## Start Jupyter notebook server
	@echo "$(BLUE)Starting Jupyter notebook...$(NC)"
	uv run --extra analysis jupyter notebook

lab: ## Start Jupyter Lab
	@echo "$(BLUE)Starting Jupyter Lab...$(NC)"
	uv run --extra analysis jupyter lab

##@ Data Management
load-data: ## Run data loading notebook
	@echo "$(BLUE)Loading data into DuckDB...$(NC)"
	uv run --extra analysis jupyter nbconvert --to notebook --execute notebooks/exploratory/00_data_loading.ipynb

##@ Code Quality
format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(NC)"
	uv run --extra dev black src/ notebooks/

lint: ## Lint code with ruff
	@echo "$(BLUE)Linting code...$(NC)"
	uv run --extra dev ruff check src/

type-check: ## Type check with mypy
	@echo "$(BLUE)Type checking...$(NC)"
	uv run --extra dev mypy src/

check: format lint type-check ## Run all code quality checks
	@echo "$(GREEN)✓ All checks passed!$(NC)"

##@ Testing
test: ## Run Python tests
	@echo "$(BLUE)Running Python tests...$(NC)"
	uv run --extra dev pytest tests/

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	uv run --extra dev pytest --cov=src/aida_challenge --cov-report=html tests/

##@ Cleaning
clean: ## Clean all generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@$(MAKE) dbt-clean
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

clean-data: ## Clean DuckDB database (WARNING: deletes data!)
	@echo "$(YELLOW)WARNING: This will delete your DuckDB database!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f data/aida_challenge.duckdb data/aida_challenge.duckdb.wal; \
		echo "$(GREEN)✓ Database cleaned!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

##@ Complete Workflows
init: install-all dbt-setup load-data dbt-pipeline ## Initialize complete project from scratch
	@echo "$(GREEN)✓ Project initialized successfully!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  - Run 'make notebook' to start Jupyter"
	@echo "  - Run 'make dbt-docs' to view dbt documentation"

rebuild: clean load-data dbt-full-refresh ## Clean and rebuild everything
	@echo "$(GREEN)✓ Rebuild complete!$(NC)"

all: install dbt-pipeline test ## Install, run pipeline, and test
	@echo "$(GREEN)✓ All tasks complete!$(NC)"

##@ Default
.DEFAULT_GOAL := help
