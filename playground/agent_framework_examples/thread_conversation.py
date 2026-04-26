#!/usr/bin/env python
# coding=utf-8
import asyncio

from agent_framework_journey.agent_framework_util import get_agent
from utils.util import DOUBAO_1_5_VISION_LITE

agent = get_agent(DOUBAO_1_5_VISION_LITE)

async def main():
    thread1 = agent.get_new_thread()
    thread2 = agent.get_new_thread()

    result1 = await agent.run("讲一个关于海盗的笑话，50 字以内。", thread=thread1)
    print(result1.text)

    result2 = await agent.run("讲一个关于机器人的笑话，50 字以内。", thread=thread2)
    print(result2.text)

    result3 = await agent.run("再增加一些表情符号", thread=thread1)
    print(result3.text)

    result4 = await agent.run("再增加一些表情符号", thread=thread2)
    print(result4.text)

asyncio.run(main())