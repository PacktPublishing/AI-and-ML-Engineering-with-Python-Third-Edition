# Development container

The standard development workstation for the book: Python 3.12, `uv`, Make,
Git, the AWS CLI, Docker, Terraform, `kubectl`, Helm and the GitHub CLI.

Open the repository root in VS Code and choose **Reopen in Container**.

## What is deliberately *not* in here

Chapter dependencies. Each example is an independent Python project with its
own `pyproject.toml`, `uv.lock` and `.venv`:

```bash
cd chapter-02/protocols
make setup
```

Keeping the two separate means you never rebuild the container to move between
chapters, and one example's dependency pin can never break another's. Examples
that pin a different Python version work as-is, because `uv` downloads the
interpreter they ask for.

There is no chapter-specific devcontainer in this repository. Add one only if a
chapter genuinely needs different system-level tooling — CUDA, a native
toolchain, or its own local services.

## AWS credentials

Nothing is mounted by default, so the container starts on a machine with no AWS
configuration. Pick whichever suits you:

- run `aws configure sso` (or `aws configure`) inside the container, or
- share the credentials you already have on the host by adding this to
  `devcontainer.json` and rebuilding:

  ```jsonc
  "mounts": [
    "source=${localEnv:HOME}/.aws,target=/home/vscode/.aws,type=bind,consistency=cached"
  ]
  ```

Verify with `aws sts get-caller-identity`.

## Apple Silicon

Every image and feature used here has an arm64 build, so the container runs
natively on an M-series Mac. Examples needing a GPU are meant for remote
compute, not this container.
