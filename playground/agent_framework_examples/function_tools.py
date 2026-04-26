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
    print(f"调用 get_weather:{location}")
    return f"The weather in {location} is cloudy with a high of 15°C."


agent = get_agent(tools=get_weather)

async def main():
    result = await agent.run("北京天气怎么样？适合穿什么衣服？")
    print(result.text)

asyncio.run(main())