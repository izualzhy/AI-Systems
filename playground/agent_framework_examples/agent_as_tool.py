#!/usr/bin/env python
# coding=utf-8
import asyncio
from typing import Annotated
from pydantic import Field

from agent_framework_journey.agent_framework_util import get_agent


def get_weather(
        location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."

weather_agent = get_agent(tools=[get_weather])

main_agent = get_agent(tools=weather_agent.as_tool(name="new tool from agent"))


async def main():
    result = await main_agent.run("What is the weather like in Amsterdam?")
    print(result.text)

asyncio.run(main())