# MCP and A2A, side by side

Minimal working servers and clients for both protocols, kept in one place so
the two can be compared directly.

```text
protocols/
├── fastmcp_server.py   # MCP server via FastMCP — one decorator
├── fastmcp_client.py   # MCP client; spawns the server over stdio
├── mcp_server.py       # the same tool against the low-level mcp.Server
├── a2a_server.py       # A2A echo agent: agent card + executor + task store
├── a2a_client.py       # A2A client: discover the card first, then call
├── Dockerfile          # container image for the A2A agent
└── pyproject.toml      # Python 3.12, managed with uv
```

The contrast the files are meant to draw out:

| | MCP | A2A |
| --- | --- | --- |
| Discovery | client is told where the server is | fetch the Agent Card first |
| Unit of work | a tool call | a stateful task |
| Server needs | a tool | an agent card, an executor **and** a task store |
| Transport here | stdio | HTTP (JSON-RPC) |

## Setup

```bash
make setup
```

Requires [uv](https://docs.astral.sh/uv/). `uv` provisions Python 3.12 itself,
so no other Python setup is needed.

## Run the MCP examples

```bash
make run
```

The client starts `fastmcp_server.py` as a subprocess over stdio and calls its
one tool, so this single command exercises both halves. To read what FastMCP
is abstracting away, compare `fastmcp_server.py` with `mcp_server.py` — the
same tool, written against the low-level `mcp.Server` API.

## Run the A2A examples

A2A is an HTTP protocol, so the agent is a real server. In one terminal:

```bash
make run-a2a-server
```

In a second terminal:

```bash
make run-a2a-client
```

The client fetches `/.well-known/agent-card.json` before it sends anything —
discovery is a first-class step in A2A, not an assumption.

## Run the A2A agent in a container

```bash
make build
make docker-run
```

`make run-a2a-client` then works unchanged against the containerised agent.

The image is built in two stages: `uv` installs the locked dependencies into a
virtual environment in the builder stage, and the runtime stage copies that
environment and runs it with a plain `python` entry point. The runtime image
has no package manager in it and runs as an unprivileged user (uid 10001).

The server reads three environment variables so the same file works in both
places. Inside the container it binds `0.0.0.0`, but the Agent Card still has
to advertise a URL the *client* can reach:

| Variable | Local default | Set in the image |
| --- | --- | --- |
| `A2A_HOST` | `127.0.0.1` | `0.0.0.0` |
| `A2A_PORT` | `9999` | `9999` |
| `A2A_PUBLIC_URL` | `http://127.0.0.1:9999` | `http://127.0.0.1:9999` |

`A2A_PUBLIC_URL` is correct as-is when the port is published to your machine
with `-p 9999:9999`. Deploying the agent anywhere else means setting it to the
address clients actually use.

## Checks

```bash
make lint
make typecheck
make test
```
