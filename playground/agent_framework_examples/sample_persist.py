#!/usr/bin/env python
# coding=utf-8
import asyncio
import json
import os.path
import sys
import tempfile

from agent_framework_journey.agent_framework_util import get_agent

agent = get_agent()

file_path = os.path.join("/tmp", "agent_thread.json")

async def persist():
    thread = agent.get_new_thread()

    response = await agent.run("给我讲一个互联网笑话。", thread=thread)

    print(response)

    serialized_thread = await thread.serialize()

    with open(file_path, "w") as f:
        json.dump(serialized_thread, f)

async def recover():
    with open(file_path, "r") as f:
        reloaded_data = json.load(f)
        resumed_thread = await agent.deserialize_thread(reloaded_data)

        response = await agent.run("请加一些表情符号。", thread=resumed_thread)
        print(response)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "persist":
            asyncio.run(persist())
        elif sys.argv[1] == "recover":
            asyncio.run(recover())
        else:
            print("Usage: python thread_conversation.py persist|recover")
    else:
        print("Usage: python thread_conversation.py persist|recover")