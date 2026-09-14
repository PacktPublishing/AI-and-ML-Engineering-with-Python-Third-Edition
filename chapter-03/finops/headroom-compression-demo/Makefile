# ---------------------------------------------------------------------------
# Context-compression demo.
#
# Self-contained: every target runs against this directory's own .venv,
# created by uv from pyproject.toml and uv.lock.
#
# This example pins Python 3.10 (see .python-version) because that is what the
# headroom-ai ML extras support; the rest of the repository uses 3.12. uv reads
# .python-version and provisions the right interpreter for you.
# ---------------------------------------------------------------------------

UV ?= uv

.DEFAULT_GOAL := help
.PHONY: help setup lint format typecheck test run build clean

help:
	@echo "  setup       create .venv and install the locked dependencies"
	@echo "  lint        Ruff lint rules + format check"
	@echo "  format      reformat the code with Ruff"
	@echo "  typecheck   Pyright"
	@echo "  test        unit tests"
	@echo "  run         run the compression demo and write the plots"
	@echo "  clean       remove the virtual environment, caches and plots"

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
	$(UV) run python context_compression_demo.py

build:
	@echo "(no container image: this example is a local script)"

# The plots this demo writes are committed as book figures, so `clean` leaves
# them alone -- `make run` overwrites them in place.
clean:
	rm -rf .venv .pytest_cache .ruff_cache __pycache__
