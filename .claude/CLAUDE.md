# CLAUDE.md

## Purpose

This repository contains the code examples for a book on **Machine Learning Engineering and AI Engineering with Python**.

The repository is a large monorepo, but it should **not** be treated as one large application. Each chapter is a largely self-contained project containing the code, infrastructure, tests, and runnable examples associated with that chapter.

Typical structure:

```text
.
├── .devcontainer/
├── .github/
├── chapter-01/
├── chapter-02/
├── chapter-03/
├── ...
└── .claude/CLAUDE.md
```

When working in this repository, optimise for:

1. **Pedagogical clarity**
2. **Correctness**
3. **Simplicity**
4. **Reproducibility**
5. **Good software engineering practice**
6. **Portability**

The code is intended to be read and run by people learning ML and AI engineering.

**Production-quality does not mean production-complex.**

Avoid unnecessary abstraction, framework complexity, infrastructure ceremony, or cleverness.

---

# Repository Model

## Chapters are self-contained projects

Treat each `chapter-XX/` directory as an independent project unless explicitly told otherwise.

Do not introduce dependencies between chapters simply to reduce duplication. Some duplication is acceptable — and often desirable — when it makes an individual chapter easier to understand and run independently.

A reader should ideally be able to:

```bash
cd chapter-XX
make setup
make test
make run
```

without needing to understand or configure unrelated chapters.

Each substantial chapter should therefore contain its own:

- source code
- tests
- configuration
- dependency definition
- `Makefile`
- Dockerfile(s), where appropriate
- infrastructure definitions, where appropriate
- concise README or usage instructions where useful

Small illustrative snippets do not need unnecessary scaffolding.

---

# Python

Python is the primary programming language throughout the repository.

Prefer modern, idiomatic Python.

## General conventions

Use:

- explicit type hints
- small, focused functions and classes
- Pydantic models for validated application, configuration, and API data
- dataclasses for simple internal structured data
- dependency injection where it genuinely improves testability
- composition over deep inheritance
- clear interfaces between components

Object-oriented design is a reasonable default for substantial components, but **do not create classes where a simple function is clearer**.

Prefer explicit code over metaprogramming or clever abstractions.

Avoid:

- unnecessary inheritance hierarchies
- premature abstraction
- global mutable state
- giant classes
- giant functions
- hidden side effects
- overly generic utility modules
- unnecessary framework wrappers

Code should be easy to explain in a book.

---

# Dependency and Package Management

Use **uv** as the default Python dependency and package management tool.

The standard local development pattern is:

1. Create a standard Python virtual environment.
2. Use `uv` to resolve and install dependencies.
3. Run applications through normal Python entry points.

Prefer the appropriate modern `uv` workflow, for example:

```bash
uv sync
```

Each chapter should maintain its own dependency configuration and, where appropriate:

```text
chapter-XX/
├── pyproject.toml
└── uv.lock
```

Do not create a single giant Python environment containing the dependencies of every chapter.

## Runtime portability

Containerised applications should retain ordinary Python entry points rather than depending on `uv` being present at runtime.

For example:

```bash
python -m app
```

or an appropriate standard server command.

This is intentional:

> **Use `uv` for development and package management, but keep runtime artefacts interoperable with standard Python environments.**

Do not make runtime containers unnecessarily dependent on package-management tooling.

## Exceptions

Some ML examples may require:

- CUDA-specific packages
- custom kernels
- system packages
- specialised installation sequences
- dependencies incompatible with the normal `uv` workflow

For these examples, a conventional `venv` + `pip` workflow is acceptable.

Make the reason for deviating from the normal `uv` pattern explicit.

---

# Documentation

Use concise **Google-style docstrings** for public classes, methods, and functions where they add value.

Example:

```python
def create_embedding(text: str, model_id: str) -> list[float]:
    """Create an embedding for the supplied text.

    Args:
        text: Text to embed.
        model_id: Identifier of the embedding model.

    Returns:
        Embedding vector for the supplied text.
    """
```

Do not write verbose docstrings that merely restate obvious code.

Comments should primarily explain **why**, not narrate **what** the next line does.

---

# Code Quality

New or modified code should aim to pass:

```bash
ruff check .
ruff format --check .
pyright
pytest
```

Use:

- **pytest** for testing
- **Ruff** for linting and formatting
- **Pyright** for static type checking

Prefer strict typing where practical without making educational examples unreadable.

Do not silence linting or type errors merely to make checks pass. Fix the underlying issue unless there is a legitimate reason for an exception.

---

# Testing

Tests are part of the teaching material and should themselves be clear and readable.

Prefer:

- focused unit tests
- Arrange / Act / Assert structure where useful
- pytest fixtures for reusable setup
- explicit assertions
- mocks or fakes at external system boundaries

Do not require real cloud resources, paid APIs, GPUs, externally hosted models, or external observability services for ordinary unit tests.

Mock or replace external dependencies such as:

- AWS APIs
- Amazon Bedrock
- OpenAI
- Anthropic
- Hugging Face downloads
- external databases
- telemetry backends
- network services

Integration and end-to-end tests may use real infrastructure where explicitly appropriate, but they must be clearly separated from the default unit-test path.

Aim for **>80% test coverage** where practical.

Coverage is a quality signal, **not a hard CI gate**.

Do not fail CI solely because coverage falls below 80%.

---

# Makefiles

Each substantial chapter should expose a simple Makefile interface.

Prefer consistent targets such as:

```text
make setup
make lint
make format
make typecheck
make test
make run
make build
make clean
```

Only include targets that make sense for that chapter.

Where infrastructure exists, additional targets may include:

```text
make infra-plan
make infra-deploy
make infra-destroy
```

Where Kubernetes is involved:

```text
make docker-build
make helm-template
make k8s-deploy
make k8s-delete
```

The Makefile should provide the reader with a small, memorable interface rather than requiring knowledge of every underlying command.

`make test` should run that chapter's default unit tests without requiring cloud credentials or expensive external services.

---

# Development Containers

Use a **shared repository-level `.devcontainer/` as the default development environment** for the monorepo.

Typical structure:

```text
.
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── chapter-01/
├── chapter-02/
├── chapter-03/
│   └── .devcontainer/    # only when genuinely required
└── ...
```

The root devcontainer represents the standard development workstation for the book.

It should provide common tooling used across chapters, such as:

- Python
- `uv`
- Git
- Make
- AWS CLI
- Docker tooling
- Terraform
- `kubectl`
- Helm
- common development utilities

**Do not install or aggregate every chapter's Python dependencies into the root devcontainer.**

Each chapter remains an independent Python project and should manage its own dependencies through its own `pyproject.toml`, `uv.lock`, and virtual environment.

The normal pattern is therefore:

> **shared development environment + chapter-local Python environment + application-specific runtime containers**

These concepts should remain distinct:

- **Root devcontainer** — reproducible development workstation
- **Chapter virtual environment** — chapter-specific Python dependencies
- **Application Docker image** — portable application runtime
- **Helm chart / IaC** — deployment configuration

## Chapter-specific devcontainers

Do **not** create a `.devcontainer/` inside every chapter by default.

A chapter-specific devcontainer is justified only when that chapter has materially different development requirements that would make the shared environment inappropriate or unnecessarily complicated.

Examples include:

- CUDA or GPU-specific development
- specialised compilers or native libraries
- unusual non-Python system dependencies
- custom kernels
- specialised local services or Docker Compose environments
- substantially different runtime or toolchain requirements

Prefer using the shared root environment when the difference is minor.

Do not add heavyweight or specialised dependencies to the root devcontainer merely because one chapter requires them.

When deciding whether to create a chapter-specific devcontainer, default to:

> **Use the root devcontainer unless there is a clear technical reason not to.**

Readers should not normally need to rebuild or switch development containers when moving between chapters.

---

# Application Containers

Portability is a core requirement.

Use containers for applications and services wherever practical.

Application Dockerfiles should:

- use appropriate lightweight base images
- pin important dependencies
- minimise unnecessary layers and packages
- use multi-stage builds where beneficial
- avoid running applications as root where practical
- keep runtime images reasonably small
- expose clear entrypoints
- use standard Python runtime commands

Do not require `uv` in the final runtime image unless the example specifically teaches that pattern.

## Local hardware constraint

The primary development machine is an:

**Apple Silicon M2 MacBook with 8 GB RAM.**

Therefore:

- keep local development lightweight
- avoid requiring large models locally
- avoid assuming NVIDIA/CUDA locally
- avoid memory-heavy local clusters
- prefer remote compute for GPU/heavy workloads
- make architecture assumptions explicit when relevant
- ensure Docker examples are compatible with Apple Silicon where practical

Heavy workloads belong on appropriate remote infrastructure.

---

# Cloud Platform

**AWS is the primary and only deployment cloud provider used by the book.**

Do not introduce Azure or GCP infrastructure unless explicitly requested for a specific comparison.

Primary AWS services include:

- Amazon Bedrock
- Amazon EKS
- AWS Lambda
- Amazon CloudWatch
- Amazon EC2
- IAM
- supporting AWS networking, storage, container registry, and load-balancing services where required

Follow AWS security best practices.

Never:

- hard-code AWS credentials
- commit secrets
- embed account IDs unnecessarily
- grant broad IAM permissions when narrower permissions are practical

Prefer least-privilege IAM policies while keeping educational examples understandable.

---

# Infrastructure as Code

Infrastructure should be defined as code.

Preferred technologies:

- **Terraform**
- **AWS CloudFormation**

Keep infrastructure examples modular but understandable.

Avoid building elaborate internal IaC frameworks around simple examples.

Infrastructure should expose required values through variables or parameters rather than hard-coded environment-specific configuration.

Where practical, infrastructure examples should have an obvious lifecycle:

```bash
make infra-plan
make infra-deploy
make infra-destroy
```

Be particularly careful that examples involving expensive resources can be destroyed cleanly.

---

# Kubernetes

Kubernetes is an important deployment target in the book.

Use Kubernetes to demonstrate realistic deployment of applications such as:

- FastAPI services
- chat applications
- MCP servers
- A2A services
- agent services
- model-serving components
- AI gateways and proxies
- observability components

AWS deployments should use **Amazon EKS**.

## Helm

Use **Helm** as the preferred packaging and deployment mechanism for Kubernetes applications.

Charts should be:

- small
- readable
- conventional
- configurable
- easy to explain

Demonstrate important Kubernetes concepts without turning examples into full platform-engineering frameworks.

Useful concepts include:

- Deployments
- Services
- ConfigMaps
- Secrets
- resource requests and limits
- readiness probes
- liveness probes
- rolling deployments
- Horizontal Pod Autoscaling
- ingress and load balancing where appropriate
- namespaces where useful

Show clean examples of concepts such as HPA configuration rather than attempting to create a comprehensive production platform.

Avoid Kubernetes operators unless they are genuinely required by the technology being demonstrated or the operator itself is part of the lesson.

Prefer:

> **ordinary container + Deployment + Service + Helm**

over unnecessary Kubernetes complexity.

---

# LLM Providers

Remotely hosted LLM examples may use:

- Amazon Bedrock
- Anthropic Claude
- OpenAI

Provider-specific code should be isolated behind clean boundaries when the example benefits from doing so.

Do **not** build elaborate provider abstraction layers unless provider portability is itself part of the lesson.

API keys and credentials must come from environment variables, secret stores, or appropriate AWS authentication mechanisms.

Never commit secrets.

---

# Open-Weight Models

Use **Hugging Face** as the primary source for open-weight models.

Use **vLLM** as the preferred serving technology for open-weight LLMs.

Heavy model inference should not be designed to run on the local M2/8 GB development machine.

Use:

- AWS EC2 GPU instances, or
- Google Colab when a chapter specifically requires an accessible GPU notebook environment

AWS remains the deployment cloud platform.

Google Colab is acceptable as a teaching and experimentation environment for GPU workloads.

When using Hugging Face models:

- specify the model clearly
- pin revisions where reproducibility matters
- document hardware requirements
- avoid downloading very large models as part of ordinary tests
- respect model licences and usage restrictions

---

# Web APIs

Use **FastAPI** for HTTP APIs and web services.

Prefer:

- Pydantic request and response models
- explicit response types
- dependency injection where useful
- small route handlers
- application logic outside route handlers
- health endpoints for deployable services
- structured error handling

A typical separation might be:

```text
app/
├── main.py
├── api/
├── models/
├── services/
└── config.py
```

Do not force this structure onto tiny examples where it would add noise.

---

# MCP

Use **FastMCP** for Model Context Protocol servers.

Keep MCP tools:

- small
- typed
- deterministic where possible
- clearly documented
- independently testable

Separate business logic from MCP transport and tool registration when doing so improves clarity.

MCP servers should be containerisable and, where relevant, deployable to Kubernetes using the same clean application patterns used elsewhere in the repository.

---

# A2A

Use **FastA2A** for Agent-to-Agent servers and examples.

Keep protocol and transport concerns separate from application or agent logic where practical.

Examples should make interactions between agents explicit and understandable.

---

# Agentic Workflows

Preferred frameworks are:

1. **AWS Strands Agents**
2. **Google Agent Development Kit (ADK)**

For Google ADK, use versions **>2.0** where workflow functionality is required.

Choose the framework that makes the chapter's concept clearest.

Do not mix agent frameworks in the same example unless comparison or interoperability is specifically the lesson.

Agent code should make important concepts visible, including where relevant:

- model selection
- tools
- state
- context
- workflow structure
- error handling
- observability
- human approval boundaries

Avoid hiding core concepts behind excessive helper abstractions.

---

# AI Gateways and Proxies

The repository will include examples demonstrating AI gateway and proxy patterns.

Primary technologies are:

- **LiteLLM Proxy**
- **Envoy AI Gateway / proxy capabilities**

Examples should show how to build and configure these components clearly rather than hiding configuration behind custom wrappers.

Depending on the chapter, examples may demonstrate:

- model routing
- provider abstraction
- authentication
- retries
- rate limiting
- metadata propagation
- observability
- model and provider selection
- fallback behaviour
- cost or usage tracking

Keep gateway configuration explicit and pedagogically useful.

Containerise gateway components and provide Kubernetes/Helm deployment examples where appropriate.

---

# MLflow

Use **MLflow >3.15** for ML and AI lifecycle examples.

MLflow may be used for:

- experiment tracking
- metrics
- parameters
- artefacts
- model management
- model registry
- AI application observability
- tracing
- evaluation capabilities available in modern MLflow releases

Prefer current MLflow APIs and patterns rather than legacy approaches when newer APIs provide the intended functionality.

MLflow examples should make clear which role MLflow is playing in the architecture rather than treating it as an opaque all-purpose platform.

Where appropriate, containerise MLflow services and provide clear configuration for local or AWS-hosted deployments.

---

# Observability

Observability is a first-class engineering concern throughout the repository.

The book uses two complementary approaches:

1. **AWS-native observability with CloudWatch**
2. **Vendor-neutral telemetry with OpenTelemetry**

## AWS-native observability

For applications deployed natively to AWS, demonstrate appropriate use of **Amazon CloudWatch**.

Depending on the example, this may include:

- application logs
- infrastructure logs
- metrics
- dashboards
- alarms
- traces where relevant

Keep AWS-native examples idiomatic to the AWS service being demonstrated.

## OpenTelemetry

Use **OpenTelemetry (OTEL)** to demonstrate portable observability patterns.

Examples may use both direct instrumentation and framework integrations.

### Direct instrumentation

Instrument Python applications directly using the OpenTelemetry SDK where this best demonstrates the underlying concepts.

### Framework integrations

Use supported OpenTelemetry integrations from frameworks and libraries where appropriate, including integrations available from technologies such as:

- AWS Strands
- Google ADK
- FastAPI
- other libraries used by the examples

Prefer native framework instrumentation when the lesson is about instrumenting a realistic application.

Prefer direct SDK instrumentation when the lesson is specifically about understanding OpenTelemetry.

## OTEL Collector

The repository will include tutorials demonstrating how to deploy and configure an **OpenTelemetry Collector**.

Collector examples may demonstrate:

```text
Application
    │
    ▼
OTEL Collector
    │
    ├── enrich / transform / tag telemetry
    │
    ▼
Downstream observability platform
```

In particular, demonstrate how the collector can enrich AI telemetry with useful metadata before forwarding it downstream.

Examples may include metadata such as:

- application
- service
- environment
- model
- provider
- agent
- workflow
- request identifiers
- trace identifiers
- relevant AI/ML metadata

Use standard OpenTelemetry semantic conventions where available rather than inventing custom conventions unnecessarily.

Collector configuration should remain explicit and readable.

Avoid building unnecessarily elaborate telemetry pipelines when a small processor/exporter example communicates the concept.

Where useful, demonstrate containerised and Kubernetes deployment of the collector.

## Observability architecture

Keep instrumentation loosely coupled from downstream observability products.

Prefer architectures conceptually similar to:

```text
Application
    │
    ├── logs
    ├── metrics
    └── traces
          │
          ▼
    OpenTelemetry
          │
          ▼
    OTEL Collector
          │
          ▼
Observability backend
```

This allows examples to teach telemetry architecture independently from a specific observability vendor.

---

# Configuration and Secrets

Use environment variables and typed configuration objects.

Prefer Pydantic settings/models where appropriate.

Provide `.env.example` files where environment configuration is required.

`.env.example` must contain placeholders, never real credentials.

Never commit:

- API keys
- AWS credentials
- tokens
- passwords
- private keys
- sensitive endpoints

Fail clearly when required configuration is missing.

---

# CI/CD

Keep CI/CD simple and understandable.

At minimum, CI should run the repository's unit tests on:

- pushes to `main`
- pull/merge requests targeting `main`

The repository owner frequently works directly on `main`, so CI **must not assume that all changes arrive through pull requests**.

The baseline repository CI should run unit tests across all relevant chapters.

Where practical it should also run:

```bash
ruff check .
ruff format --check .
pyright
```

Coverage should be reported where practical, with a target of **>80%**, but falling below this threshold must **not block pushes or fail CI solely because of coverage**.

Do not run the following automatically on every push unless explicitly configured:

- cloud integration tests
- GPU tests
- large model downloads
- expensive end-to-end tests
- AWS infrastructure deployments
- paid LLM integration tests

Keep the baseline CI fast enough to remain useful.

---

# Pedagogical Design

This is book code, not merely production code.

A technically sophisticated implementation is worse if it makes the concept harder to teach.

Prefer code where a reader can answer:

> **What is happening here, and why?**

after reading it once.

Good examples should generally:

- introduce one major concept at a time
- use meaningful names
- expose important implementation decisions
- avoid unexplained magic
- be runnable
- be testable
- demonstrate realistic engineering practice

Production practices should be demonstrated **without overwhelming the lesson**.

When forced to choose between a highly abstract reusable implementation and a small explicit implementation, prefer the explicit implementation unless abstraction is itself being taught.

---

# Working With Existing Chapters

Before modifying a chapter:

1. Inspect that chapter's existing structure.
2. Read its README, Makefile, dependency configuration, and tests if present.
3. Understand the educational goal of the existing example.
4. Preserve the chapter's established conventions unless there is a strong reason to improve them.
5. Keep changes scoped to the requested chapter wherever possible.

Do not perform repository-wide refactors as a side effect of solving a chapter-specific problem.

Do not automatically modernise working examples unless requested.

---

# Adding New Examples

When creating a substantial new example, aim for the smallest complete vertical slice that demonstrates the concept.

A typical chapter or substantial example may include:

```text
chapter-XX/
├── README.md
├── Makefile
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── src/
│   └── ...
└── tests/
    └── ...
```

Add infrastructure only when required:

```text
infra/
├── terraform/
└── cloudformation/
```

Add Kubernetes deployment artefacts only when appropriate:

```text
helm/
└── example-name/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
```

Remember that `.devcontainer/` belongs at the repository root by default, not inside each chapter.

Do not mechanically create every directory for every example.

---

# Commands and External Side Effects

Be conservative with destructive or expensive operations.

Do not automatically:

- deploy AWS infrastructure
- destroy AWS infrastructure
- create expensive AWS resources
- invoke large numbers of paid LLM requests
- download multi-GB models
- start expensive GPU instances
- push container images
- modify remote repositories
- change CI/CD secrets

without explicit instruction.

Generating the code or configuration for these operations is fine.

Prefer showing or validating an infrastructure plan before deployment.

---

# Definition of Done

For a normal code change, aim to leave the affected chapter in a state where:

```bash
make lint
make typecheck
make test
```

pass.

Where applicable:

```bash
make build
```

should also succeed.

Before declaring work complete:

- check that code is readable
- check type hints
- check tests
- check formatting and linting
- check that secrets are not present
- check that documentation matches the implementation
- check that commands shown to readers actually work
- check that the example remains understandable in isolation
- check that unnecessary dependencies or abstractions have not been introduced

---

# Claude Code Behaviour

When working in this repository:

- **inspect before editing**
- make focused changes
- prefer small diffs
- preserve chapter independence
- use the root devcontainer by default
- keep Python dependencies chapter-local
- run relevant tests after changes
- run Ruff after Python changes
- run Pyright where configured
- update tests when behaviour changes
- update documentation when commands or interfaces change
- avoid speculative refactoring
- avoid adding unnecessary dependencies
- never invent credentials or infrastructure identifiers
- never hide failures simply to obtain a green test suite
- avoid expensive cloud or LLM operations unless explicitly requested
- do not assume local GPU or large-memory availability

When introducing a new technology, prefer a **minimal working implementation first**. Add production concepts incrementally where they are relevant to the lesson.

If a requirement is ambiguous, prefer the implementation that is:

**simpler, more explicit, easier to test, easier to run, and easier to explain in the book.**

Above all, remember:

> **This repository should demonstrate excellent ML and AI engineering without making excellent engineering look unnecessarily complicated.**
