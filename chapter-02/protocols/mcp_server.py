"""
mcp_server.py

The same stubbed data lake tool, implemented against the low-level
mcp.Server class rather than FastMCP.

This is what FastMCP is abstracting. Compare with minimal_server.py
to see exactly what the framework buys you.

Dependencies:
    uv pip install mcp anyio
"""

import anyio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# ---------------------------------------------------------------------------
# Tool definition
# At the low level, tools are plain dicts describing a JSON Schema.
# There is no decorator, no type-hint inference — you write the schema
# by hand and wire the handler yourself.
# ---------------------------------------------------------------------------
DATA_LAKE_STATUS_TOOL = types.Tool(
    name="get_data_lake_status",
    description="Returns the current status of the enterprise data lake.",
    input_schema={
        "type": "object",
        "properties": {},   # no arguments for this stub
        "required": [],
    },
)


# ---------------------------------------------------------------------------
# Request handlers
# The low-level Server dispatches to these explicitly.
# Each handler maps to one JSON-RPC method in the MCP spec.
# ---------------------------------------------------------------------------

async def handle_list_tools(ctx, params) -> types.ListToolsResult:
    """Responds to tools/list — tells the client what tools exist."""
    return types.ListToolsResult(tools=[DATA_LAKE_STATUS_TOOL])


async def handle_call_tool(ctx, params: types.CallToolRequestParams) -> types.CallToolResult:
    """Responds to tools/call — executes the named tool and returns a result."""
    if params.name != "get_data_lake_status":
        raise ValueError(f"Unknown tool: {params.name}")

    # Stubbed response — same payload as the FastMCP version
    result = {"status": "healthy", "tables": 42, "last_updated": "2025-07-24"}

    return types.CallToolResult(
        content=[types.TextContent(type="text", text=str(result))]
    )


# ---------------------------------------------------------------------------
# Server wiring
# FastMCP's @mcp.tool decorator does all of this registration implicitly.
# Here it's explicit: create the server, attach handlers, run the transport.
# ---------------------------------------------------------------------------

async def main():
    app = Server(
        "RawDemoServer",
        on_list_tools=handle_list_tools,
        on_call_tool=handle_call_tool,
    )

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    anyio.run(main)