#!/usr/bin/env python
# coding=utf-8
import asyncio
from typing import Annotated
from agent_framework import ai_function, ChatMessage, Role

from agent_framework_journey.agent_framework_util import get_agent


@ai_function
def get_weather(location: Annotated[str, "The city and state, e.g. San Francisco, CA"]) -> str:
    """Get the current weather for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C."


@ai_function(approval_mode="always_require")
def get_weather_detail(location: Annotated[str, "The city and state, e.g. San Francisco, CA"]) -> str:
    """Get detailed weather information for a given location."""
    return f"The weather in {location} is cloudy with a high of 15°C, humidity 88%."


agent = get_agent(tools=[
    # get_weather,
    get_weather_detail
])

async def sample():
    result = await agent.run("What is the detailed weather like in Amsterdam?")
    print(f"result: {result}")

    if result.user_input_requests:
        for user_input_needed in result.user_input_requests:
            print(f"Function: {user_input_needed.function_call.name}")
            print(f"Arguments: {user_input_needed.function_call.arguments}")

async def handle_approvals(query: str, agent) -> str:
    """Handle function call approvals in a loop."""
    current_input = query

    while True:
        result = await agent.run(current_input)

        if not result.user_input_requests:
            # No more approvals needed, return the final result
            return result.text

        # Build new input with all context
        new_inputs = [query]

        for user_input_needed in result.user_input_requests:
            print(f"Approval needed for: {user_input_needed.function_call.name}")
            print(f"Arguments: {user_input_needed.function_call.arguments}")

            # Add the assistant message with the approval request
            new_inputs.append(ChatMessage(role=Role.ASSISTANT, contents=[user_input_needed]))

            # Get user approval (in practice, this would be interactive)
            # user_approval = True  # Replace with actual user input
            user_approval = False

            # Add the user's approval response
            new_inputs.append(
                ChatMessage(role=Role.USER, contents=[user_input_needed.create_response(user_approval)])
            )

        # Continue with all the context
        current_input = new_inputs

async def sample2():
    # Usage
    result_text = await handle_approvals("Get detailed weather for Seattle and Portland", agent)
    print(result_text)

# asyncio.run(sample())
asyncio.run(sample2())
