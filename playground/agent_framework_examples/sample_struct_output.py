#!/usr/bin/env python
# coding=utf-8
import asyncio

from pydantic import BaseModel

from agent_framework_journey.agent_framework_util import get_agent


class PersonInfo(BaseModel):
    """Information about a person."""
    name: str | None = None
    age: int | None = None
    occupation: str | None = None


agent = get_agent(
    instructions="You are a helpful assistant that extracts person information from text."
)

async def main():
    response = await agent.run(
        "Please provide information about John Smith, who is a 35-year-old software engineer.",
        response_format=PersonInfo
    )

    if response.value:
        person_info = response.value
        print(f"Structured data found in response, value: {person_info}")
        print(f"Name: {person_info.name}, Age: {person_info.age}, Occupation: {person_info.occupation}")
    else:
        print("No structured data found in response")

asyncio.run(main())
