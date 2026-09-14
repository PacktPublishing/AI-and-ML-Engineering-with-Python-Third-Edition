# Prerequisites

You need very little installed on your own machine, because each example
brings its own Python environment.

## The short version

| Tool | Why | Install |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | creates every example's environment, and downloads the Python version each one pins | `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | cloning the repository | usually already present |
| Make | the `make` interface every example exposes | present on macOS with the Xcode command line tools; `apt install make` on Debian/Ubuntu |

You do **not** need to install Python yourself. `uv` provisions the interpreter
each example asks for.

## Optional, per chapter

| Tool | Needed for |
| --- | --- |
| [Docker](https://docs.docker.com/get-docker/) | examples with a `Dockerfile`, and the development container |
| AWS CLI + an AWS account | Bedrock, Lambda, EKS and CloudWatch examples |
| Terraform | chapters that provision infrastructure |
| `kubectl` and Helm | chapters that deploy to Kubernetes |

The [development container](../.devcontainer/README.md) contains all of these
already, so it is the quickest way to get a machine that can run everything.

## Hardware

The examples are written to run on an ordinary laptop — they were developed on
an Apple Silicon MacBook with 8 GB of RAM. Nothing in the default path
downloads a large model or expects a local GPU.

Chapters that need a GPU say so, and point at remote compute (an EC2 GPU
instance, or Google Colab) rather than assuming you have one locally.

## Costs

Examples that call a paid API or create cloud resources say so in their own
README, and keep the amount of traffic they generate small. Read an example's
README before running it if you want to know what it will cost. Nothing runs
against real infrastructure unless you explicitly ask it to.
