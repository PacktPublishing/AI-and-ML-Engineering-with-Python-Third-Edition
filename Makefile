# ---------------------------------------------------------------------------
# Repository root.
#
# This Makefile builds nothing itself. Every example owns its own Makefile,
# its own dependencies and its own virtual environment; this file just
# recurses into each immediate subdirectory that has a Makefile of its own.
#
# The same aggregating Makefile appears at each intermediate level, so a new
# example is picked up automatically as soon as it has a Makefile.
#
#   make setup                                       # all examples
#   make -C chapter-03/finops/bedrock-finops-demo run  # one example
# ---------------------------------------------------------------------------

SUBPROJECTS := $(patsubst %/Makefile,%,$(wildcard */Makefile))

.DEFAULT_GOAL := help
.PHONY: help list setup lint format typecheck test build clean

help:
	@echo "Aggregating targets (run in every example below):"
	@echo "  setup       create each .venv and install locked dependencies"
	@echo "  lint        Ruff lint + format check"
	@echo "  format      reformat with Ruff"
	@echo "  typecheck   Pyright"
	@echo "  test        unit tests"
	@echo "  build       container image, where the example has one"
	@echo "  clean       remove virtual environments and tool caches"
	@echo "  list        list every example project"
	@echo
	@echo "Recurses into: $(SUBPROJECTS)"
	@echo "Run a single example with: make -C <example-path> run"

list:
	@find . -mindepth 2 -name pyproject.toml -not -path '*/.venv/*' \
	  -exec dirname {} \; | sort

setup lint format typecheck test build clean:
	@for project in $(SUBPROJECTS); do \
	  printf '\n==> %s: %s\n' "$$project" "$@"; \
	  $(MAKE) --no-print-directory -C "$$project" $@ || exit 1; \
	done
