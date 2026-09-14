# Development workstation for the whole repository.
#
# This image deliberately contains no chapter dependencies. Each example owns
# its own virtual environment, created by uv from that example's uv.lock, so
# moving between chapters never means rebuilding this container.

FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

# uv manages every example in the repository. Copying the binary out of the
# official image pins the version, and avoids piping an installer into a shell.
COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /uvx /usr/local/bin/

# uv provisions its own interpreters on demand, so an example that pins a
# different Python version (chapter 3's compression demo pins 3.10) works here
# without changing this image.
ENV UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=managed

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*
