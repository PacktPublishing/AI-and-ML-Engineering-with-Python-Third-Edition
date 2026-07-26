import asyncio
from fastmcp import Client

async def main():
    async with Client("minimal_server.py") as client:
        result = await client.call_tool("get_data_lake_status", {})
        print(result.data)

asyncio.run(main())