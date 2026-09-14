# syntax=docker/dockerfile:1
#
# Container image for the A2A echo agent.
#
# Two stages, for two different reasons:
#
#   builder  uv resolves and installs the locked dependencies into /app/.venv
#   runtime  copies that .venv and runs it with a plain `python` entry point
#
# uv is a development and packaging tool, so it exists only in the builder.
# The runtime image is an ordinary Python environment, which keeps it small and
# means the image does not depend on the package manager to start.

# --- builder ---------------------------------------------------------------
FROM python:3.12-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.8.0 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies are installed before the source is copied, so that editing a
# script does not invalidate the cached dependency layer.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# --- runtime ---------------------------------------------------------------
FROM python:3.12-slim-bookworm AS runtime

# An unprivileged user with a fixed UID: Kubernetes can then assert
# runAsNonRoot without needing to look the name up inside the image.
RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    A2A_HOST=0.0.0.0 \
    A2A_PORT=9999 \
    A2A_PUBLIC_URL=http://127.0.0.1:9999

USER app
EXPOSE 9999

# A plain Python entry point: no uv, no shell wrapper, so signals reach the
# process directly and the container stops cleanly.
CMD ["python", "a2a_server.py"]
