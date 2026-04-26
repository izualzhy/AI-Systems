#!/usr/bin/env python
# coding=utf-8


import asyncio
import os

from agent_framework import ChatMessage, TextContent, UriContent, Role, DataContent
from agent_framework.openai import OpenAIChatClient

from agent_framework_journey.agent_framework_util import get_agent
from utils.util import ARK_API_URL, DOUBAO_SEED_1_6_VISION, DOUBAO_1_5_VISION_LITE

DEFAULT_QUERY = '你是谁？'

async def explicit_config_example():
    agent = OpenAIChatClient(
        model_id=DOUBAO_SEED_1_6_VISION,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
    ).create_agent(
        instructions="You are a helpful assistant.",
    )

    result = await agent.run(DEFAULT_QUERY)
    print(result.text)

async def streaming_example():
    agent = OpenAIChatClient(
        model_id=DOUBAO_SEED_1_6_VISION,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
    ).create_agent(
        instructions="You are a creative storyteller.",
    )

    print("Assistant: ", end="", flush=True)
    async for chunk in agent.run_stream(DEFAULT_QUERY):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print()  # New line after streaming


async def chat_message_example():

    agent = OpenAIChatClient(
        # model_id=DEEPSEEK_V31,
        model_id=DOUBAO_SEED_1_6_VISION,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
    ).create_agent(
        instructions="You are a helpful assistant.",
    )

    message = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(text="告诉我这个图片里有什么"),
            UriContent(uri="https://izualzhy.cn/assets/images/hands-on-llm/memory.jpg",
                       media_type="image/jpeg"
                       )
        ]
    )
    result = await agent.run(message)
    print(result)

async def chat_message_local_image_example():
    with open('../data/SZ_daxue.jpeg', 'rb') as f:
        image_bytes = f.read()

    message = ChatMessage(
        role=Role.USER,
        contents=[
            TextContent(text="告诉我这个图片里有什么"),
            DataContent(data=image_bytes, media_type="image/jpeg")
        ]
    )
    result = await get_agent().run(message)
    # result = await get_agent(model_id=DOUBAO_1_5_VISION_LITE).run(message)
    print(result)

if __name__ == "__main__":
    # asyncio.run(explicit_config_example())
    # asyncio.run(streaming_example())
    # asyncio.run(chat_message_example())
    asyncio.run(chat_message_local_image_example())
