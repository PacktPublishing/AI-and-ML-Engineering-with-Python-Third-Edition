# ---------------------------------------------------------------------------
# MCP and A2A protocol examples.
#
# Self-contained: every target runs against this directory's own .venv,
# created by uv from pyproject.toml and uv.lock.
#
# The A2A example is a long-running HTTP service, so it is also the example
# that carries a Dockerfile. The MCP examples speak stdio and are launched by
# their client, so they are only ever run from the local environment.
# ---------------------------------------------------------------------------

UV ?= uv
IMAGE ?= a2a-echo-agent
TAG   ?= dev
PORT  ?= 9999

.DEFAULT_GOAL := help
.PHONY: help setup lint format typecheck test run \
        run-mcp run-mcp-lowlevel run-a2a-server run-a2a-client \
        build docker-run clean

help:
	@echo "  setup             create .venv and install the locked dependencies"
	@echo "  lint              Ruff lint rules + format check"
	@echo "  format            reformat the code with Ruff"
	@echo "  typecheck         Pyright"
	@echo "  test              unit tests"
	@echo "  run               run the FastMCP client (it starts the server itself)"
	@echo "  run-mcp           same as run"
	@echo "  run-mcp-lowlevel  run the low-level MCP server on stdio"
	@echo "  run-a2a-server    run the A2A echo agent on port $(PORT)"
	@echo "  run-a2a-client    call a running A2A agent (needs run-a2a-server)"
	@echo "  build             build the A2A agent container image"
	@echo "  docker-run        run that image, published on port $(PORT)"
	@echo "  clean             remove the virtual environment and tool caches"

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

# The MCP client spawns fastmcp_server.py over stdio, so this one command
# exercises both halves of the example.
run: run-mcp

run-mcp:
	$(UV) run python fastmcp_client.py

run-mcp-lowlevel:
	$(UV) run python mcp_server.py

run-a2a-server:
	$(UV) run python a2a_server.py

# Run in a second terminal, once run-a2a-server is up.
run-a2a-client:
	$(UV) run python a2a_client.py

build:
	docker build -t $(IMAGE):$(TAG) .

docker-run:
	docker run --rm -p $(PORT):9999 $(IMAGE):$(TAG)

clean:
	rm -rf .venv .pytest_cache .ruff_cache __pycache__
