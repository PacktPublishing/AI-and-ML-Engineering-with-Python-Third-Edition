"""
a2a_client.py — minimal A2A client.

The flow MCP doesn't have: fetch the Agent Card FIRST (discovery),
then build a client from it. Discovery is first-class in A2A because
agents are peers you find and vet, not tools you've hard-wired.

Run a2a_server.py first, then this in a separate terminal.

Dependencies: uv pip install a2a-sdk httpx
"""

import asyncio

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import new_text_message
from a2a.types import Role, SendMessageRequest


async def main():
    async with httpx.AsyncClient() as http:
        # 1. Discovery
        resolver = A2ACardResolver(httpx_client=http, base_url="http://127.0.0.1:9999")
        card = await resolver.get_agent_card()
        print(f"Discovered: {card.name}\n")

        # 2. Build client from the card
        client = await create_client(
            agent=card, client_config=ClientConfig(streaming=False)
        )

        # 3. Send a message
        request = SendMessageRequest(
            message=new_text_message("hi", role=Role.ROLE_USER)
        )
        async for chunk in client.send_message(request):
            print(chunk)


if __name__ == "__main__":
    asyncio.run(main())
