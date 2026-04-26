#!/usr/bin/env python
# coding=utf-8


from typing import Annotated
from agent_framework.openai import OpenAIResponsesClient

from agent_framework_journey.agent_framework_util import get_agent


def get_specials() -> Annotated[str, "Returns the specials from the menu."]:
    print("get_specials")
    return """
        Special Soup: Clam Chowder
        Special Salad: Cobb Salad
        Special Drink: Chai Tea
        """

def get_item_price(
        menu_item: Annotated[str, "The name of the menu item."],
) -> Annotated[str, "Returns the price of the menu item."]:
    print("get_item_price")
    return "$9.99"

agent = get_agent(
    name="RestaurantAgent",
    description="Answer questions about the menu.",
    tools=[get_specials, get_item_price]
)

# Expose the agent as an MCP server
server = agent.as_mcp_server()

import anyio
from mcp.server.stdio import stdio_server

async def run():
    async def handle_stdin():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    await handle_stdin()

if __name__ == "__main__":
    anyio.run(run)