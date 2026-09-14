# AI and ML Engineering with Python — Third Edition

Code examples for *AI and ML Engineering with Python, Third Edition*,
published by Packt.

## Getting started

Install [uv](https://docs.astral.sh/uv/) — that is the only prerequisite for
most of the examples, and it provisions Python for you. Then pick an example
and run it:

```bash
cd chapter-02/protocols
make setup
make run
```

- **[docs/PRE-REQS.md](docs/PRE-REQS.md)** — what to install
- **[docs/REPO-SETUP.md](docs/REPO-SETUP.md)** — how the repository is laid out
  and how to add a new example
- **[.devcontainer/README.md](.devcontainer/README.md)** — the ready-made
  development container

## How it is organised

Each example is an independent project with its own dependencies, virtual
environment and `Makefile`. You never need to set up a chapter you are not
working on, and one example's dependencies can never affect another's.

```bash
make list      # every example in the repository
make -C chapter-02/protocols run
make help      # in any directory, to see what it offers
```

Every example exposes the same interface: `setup`, `lint`, `format`,
`typecheck`, `test`, `run`, `build` and `clean`.

## Contents

| Chapter | Examples |
| --- | --- |
| 2 | [MCP and A2A protocols, side by side](chapter-02/protocols) · architecture diagrams |
| 3 | [Bedrock token usage and cost](chapter-03/finops/bedrock-finops-demo) · [context compression](chapter-03/finops/headroom-compression-demo) · OpenTelemetry token accounting |
| 4 | Agentic RAG · the anatomy of context |

## Licence

See [LICENSE](LICENSE).
