#!/usr/bin/env python
# coding=utf-8
import asyncio
from typing import Callable, Awaitable

from agent_framework import AgentRunContext

from agent_framework_journey.agent_framework_util import get_agent


async def logging_agent_middleware(
        context: AgentRunContext,
        next: Callable[[AgentRunContext], Awaitable[None]],
) -> None:
    """Simple middleware that logs agent execution."""
    print("Agent starting...")

    # Continue to agent execution
    await next(context)

    print("Agent finished!")

from agent_framework import FunctionInvocationContext

def get_time():
    """Get the current time."""
    print("call get_time function.")
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

async def logging_function_middleware(
        context: FunctionInvocationContext,
        next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Middleware that logs function calls."""
    print(f"Calling function: {context.function.name}")

    await next(context)

    print(f"Function result: {context.result}")

async def using_logging_agent_middleware():
    async with get_agent(middleware=[logging_agent_middleware]) as agent:
        result = await agent.run("你是谁？")
        print(f"result: {result}")

async def using_logging_agent_middleware_run_level():
    async with get_agent() as agent:
        result = await agent.run("第一次问你是谁？")
        print(f"1st, result: {result}")
        result = await agent.run("第二次问你是谁？", middleware=[logging_agent_middleware])
        print(f"2nd, result: {result}")

async def using_logging_function_middleware():
    async with get_agent(
        tools=[get_time],
        middleware=[logging_function_middleware]
    ) as agent:
        result = await agent.run("现在几点钟？")
        print(f"result: {result}")



if __name__ == "__main__":
    # asyncio.run(using_logging_agent_middleware())
    asyncio.run(using_logging_agent_middleware_run_level())
    # asyncio.run(using_logging_function_middleware())
