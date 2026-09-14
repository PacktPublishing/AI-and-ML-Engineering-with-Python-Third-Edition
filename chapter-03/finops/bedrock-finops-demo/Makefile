# ---------------------------------------------------------------------------
# Bedrock FinOps demo.
#
# Self-contained: every target runs against this directory's own .venv,
# created by uv from pyproject.toml and uv.lock. Nothing here depends on
# another example or on the repository root.
#
# `uv run` syncs the environment before it runs anything, so `make run` works
# from a clean checkout; `make setup` is there when you want that step to be
# explicit.
# ---------------------------------------------------------------------------

UV ?= uv

.DEFAULT_GOAL := help
.PHONY: help setup lint format typecheck test run cost build clean

help:
	@echo "  setup       create .venv and install the locked dependencies"
	@echo "  lint        Ruff lint rules + format check"
	@echo "  format      reformat the code with Ruff"
	@echo "  typecheck   Pyright"
	@echo "  test        unit tests"
	@echo "  run         generate Bedrock traffic, print per-call token usage"
	@echo "  cost        turn the observed token totals into illustrative cost"
	@echo "  clean       remove the virtual environment and tool caches"
	@echo
	@echo "run/cost need AWS credentials — see AWS_CREDENTIALS.md"

setup:
	$(UV) sync

lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format:
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

typecheck:
	$(UV) run pyright

test:
	@if [ -d tests ]; then $(UV) run pytest -q; \
	else echo "(no tests in this example yet)"; fi

run:
	$(UV) run python run_demo.py

cost:
	$(UV) run python calculate_cost.py

build:
	@echo "(no container image: this example is a local script)"

clean:
	rm -rf .venv .pytest_cache .ruff_cache __pycache__ token_usage.json
