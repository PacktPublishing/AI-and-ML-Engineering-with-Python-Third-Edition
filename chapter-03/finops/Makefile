# ---------------------------------------------------------------------------
# Chapter 3 — FinOps examples.
#
# Aggregating Makefile: recurses into every immediate subdirectory that has a
# Makefile of its own. It holds no dependencies and builds nothing itself.
#
#   make -C <example> run    # to run one example
# ---------------------------------------------------------------------------

SUBPROJECTS := $(patsubst %/Makefile,%,$(wildcard */Makefile))

.DEFAULT_GOAL := help
.PHONY: help setup lint format typecheck test build clean

help:
	@echo "Targets (applied to every example below):"
	@echo "  setup lint format typecheck test build clean"
	@echo
	@echo "Recurses into: $(SUBPROJECTS)"
	@echo "Run a single example with: make -C <example-path> run"

setup lint format typecheck test build clean:
	@for project in $(SUBPROJECTS); do \
	  printf '\n==> %s: %s\n' "$$project" "$@"; \
	  $(MAKE) --no-print-directory -C "$$project" $@ || exit 1; \
	done
