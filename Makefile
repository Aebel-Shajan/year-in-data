.PHONY: help install install-python install-node up down console setup-r2 pipeline sync-screentime install-screentime uninstall-screentime test dev build lint format clean

PLIST_LABEL = com.yearindata.screentime
PLIST_PATH  = ~/Library/LaunchAgents/$(PLIST_LABEL).plist
PROJECT_DIR = $(shell pwd)

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ── Dependencies ──────────────────────────────────────────────────────────────

install: install-python install-node ## Install all dependencies

install-python: ## Install Python dependencies
	uv sync

install-node: ## Install Node dependencies
	cd website && npm install

# ── Local environment ─────────────────────────────────────────────────────────

up: ## Start MinIO and set up local bucket
	uv run python scripts/setup_local.py

down: ## Stop MinIO and remove data
	docker compose down
	rm -rf .minio-data

console: ## Open MinIO web console in browser
	open http://localhost:9001

# ── Pipeline ──────────────────────────────────────────────────────────────────

setup-r2: ## Create R2 bucket, apply public-read policy and CORS (run once)
	uv run python scripts/setup_r2.py

pipeline: ## Sync from Drive and run the data pipeline
	uv run python scripts/sync_drive.py
	uv run python -m pipeline.main

sync-macos: ## Sync screen time to R2 (run manually or via launchd)
	uv run python scripts/sync_macos.py

install-macos-cron: ## Install launchd job to sync screen time daily at 9 AM
	mkdir -p $(PROJECT_DIR)/logs
	sed -e "s|__UV__|$$(which uv)|g" \
	    -e "s|__PROJECT_DIR__|$(PROJECT_DIR)|g" \
	    scripts/com.yearindata.screentime.plist > $(PLIST_PATH)
	launchctl load $(PLIST_PATH)
	@echo "Installed: $(PLIST_LABEL)"

uninstall-macos-cron: ## Remove launchd job
	launchctl unload $(PLIST_PATH)
	rm -f $(PLIST_PATH)
	@echo "Removed: $(PLIST_LABEL)"

test: ## Run end-to-end test with fake data
	uv run python scripts/sync_drive.py
	uv run python scripts/test_e2e.py

# ── Website ───────────────────────────────────────────────────────────────────

notebook: ## Start Jupyter in the notebooks folder
	uv run jupyter notebook notebooks/

dev: ## Start the Vite dev server
	cd website && npm run dev

build: ## Build the website for production
	cd website && npm run build

# ── Code quality ──────────────────────────────────────────────────────────────

lint: ## Check code with ruff
	uv run ruff check pipeline/
	uv run ruff format --check pipeline/

format: ## Auto-fix and format with ruff
	uv run ruff check --fix pipeline/
	uv run ruff format pipeline/

# ── Cleanup ───────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and __pycache__
	rm -rf website/dist
	find . -type d -name __pycache__ -exec rm -rf {} +
