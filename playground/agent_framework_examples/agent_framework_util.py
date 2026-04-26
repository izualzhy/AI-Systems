#!/usr/bin/env python
# coding=utf-8

import asyncio
import os

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient, OpenAIResponsesClient

from utils.util import DEEPSEEK_V31, ARK_API_URL, DOUBAO_SEED_1_6, DOUBAO_SEED_1_6_VISION

def get_agent(
        model_id: str = DOUBAO_SEED_1_6_VISION,
        name: str | None = None,
        instructions: str | None = None,
        description: str | None = None,
        tools = None,
        middleware = None,
        chat_message_store_factory = None,):
    agent = OpenAIChatClient(
        # model_id=DEEPSEEK_V31,
        model_id=model_id,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
    ).create_agent(
        name=name or "Agent",
        instructions= instructions or "You are a helpful assistant.",
        description=description or "You are a helpful assistant.",
        tools=tools,
        middleware=middleware,
        chat_message_store_factory=chat_message_store_factory
    )

    return agent