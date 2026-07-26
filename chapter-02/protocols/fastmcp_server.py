from fastmcp import FastMCP

mcp = FastMCP("DemoServer")

@mcp.tool
def get_data_lake_status() -> dict:
    """Returns the current status of the enterprise data lake."""
    return {"status": "healthy", "tables": 42, "last_updated": "2025-07-24"}

if __name__ == "__main__":
    mcp.run()