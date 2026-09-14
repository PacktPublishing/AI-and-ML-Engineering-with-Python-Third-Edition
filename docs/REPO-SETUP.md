# How this repository is laid out

This is a monorepo, but it is not one application. Each example is an
independent project with its own dependencies, its own virtual environment and
its own `Makefile`. Nothing is shared at runtime, so one example can never
break another, and you never have to read a chapter you are not working on.

## The unit of work is an example, not a chapter

```text
.
├── Makefile                       # recurses into everything below
├── .devcontainer/                 # the shared development workstation
├── docs/
├── chapter-02/
│   ├── Makefile                   # recurses into chapter-02's examples
│   └── protocols/                 # <- an example: this is the unit
│       ├── Makefile               # the real targets live here
│       ├── pyproject.toml
│       ├── uv.lock
│       ├── Dockerfile             # only where the example is a service
│       └── README.md
└── chapter-03/
    ├── Makefile
    └── finops/
        ├── Makefile               # levels nest as deeply as a chapter needs
        ├── bedrock-finops-demo/
        └── headroom-compression-demo/
```

A chapter is free to group its examples however it likes. Every directory
between the root and an example holds the same small aggregating `Makefile`,
which recurses into any immediate subdirectory that has a `Makefile` of its
own. A new example is picked up automatically as soon as it has one — there is
no list to keep up to date.

## Running an example

Change into it and use its own `Makefile`:

```bash
cd chapter-02/protocols
make setup
make test
make run
```

Or drive it from anywhere:

```bash
make -C chapter-02/protocols run
```

Every example exposes the same core targets:

| Target | Does |
| --- | --- |
| `setup` | create `.venv` and install the locked dependencies |
| `lint` | Ruff lint rules and format check |
| `format` | reformat with Ruff |
| `typecheck` | Pyright |
| `test` | unit tests, with no cloud credentials required |
| `run` | run the example |
| `build` | build the container image, where the example has one |
| `clean` | remove the virtual environment and tool caches |

`make help` in any directory lists what is actually available there — examples
add their own targets where it is useful, such as `run-a2a-server` in
`chapter-02/protocols`.

## Running everything

From the root, the aggregating targets fan out across every example:

```bash
make list        # every example project in the repository
make setup       # create all the environments
make lint
make typecheck
make test
```

`run` is deliberately *not* aggregated: running every example at once is not a
meaningful thing to do.

## Environments

Dependencies are managed with [uv](https://docs.astral.sh/uv/). Each example
has a `pyproject.toml` and a committed `uv.lock`, and `make setup` runs
`uv sync` to build `.venv` from that lock file — so you get the same versions
the example was written against.

`uv run` syncs before it runs, so `make run` works from a clean checkout
without `make setup` first. `setup` exists for when you want that step to be
explicit, or want to install ahead of being offline.

Examples may pin different Python versions (chapter 3's compression demo pins
3.10, everything else uses 3.12). `uv` reads `.python-version` and downloads
the right interpreter, so this needs nothing from you.

## Containers

Examples that are *services* carry a `Dockerfile`. Plain scripts do not — they
are meant to be read and run locally, and wrapping them in an image would add
ceremony without teaching anything.

Where an image does exist, it follows the same shape:

- a **builder** stage where `uv` installs the locked dependencies into a
  virtual environment
- a **runtime** stage that copies that environment and starts it with an
  ordinary `python` entry point

The runtime image therefore contains no package manager, which keeps it small
and means the container does not depend on development tooling to start. It
runs as an unprivileged user with a fixed UID, so a Kubernetes deployment can
assert `runAsNonRoot` without inspecting the image.

`chapter-02/protocols/Dockerfile` is the reference to copy.

## Snippets

Some files are illustrations rather than runnable demos — they need
infrastructure that only you can point them at, such as a live gateway
endpoint or your own knowledge base ID. These stay as single files with no
`Makefile` or environment of their own, because scaffolding they cannot use
would only get in the way:

- `chapter-03/finops/instrument_inference_otel.py`
- `chapter-04/agentic-rag/agentic_retrieval.py`

If one of these later grows into something you can actually run, give it a
directory of its own next to the other examples and it joins the build
automatically.

## Adding a new example

```bash
mkdir -p chapter-05/my-example && cd chapter-05/my-example
uv init --python 3.12
uv add <runtime deps>
uv add --dev ruff pytest pyright
cp ../../chapter-02/protocols/Makefile .   # then trim it to fit
```

Add a `Makefile` to `chapter-05/` too, if it does not have one — copy any of
the existing aggregating Makefiles, they are identical apart from the comment
at the top. The root picks the chapter up from there.
