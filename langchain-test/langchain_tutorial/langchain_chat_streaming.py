#!/usr/bin/env python
# coding=utf-8
import asyncio
import threading

# https://python.langchain.com/docs/how_to/chat_streaming/

from util import getDoubaoSeed16ChatModel

chat = getDoubaoSeed16ChatModel()

input = "写一首夏天的古诗。"

def sync_chat():
    for chunk in chat.stream(input):
        print(chunk.content, end="|", flush=True)

async def async_chat():
    print(f"async_chat in thread: {threading.current_thread().name}")
    async for chunk in chat.astream(input):
        # print(chunk, end="|", flush=True)
        print(chunk.content, end="|", flush=True)

async def async_chat_event():
    idx = 0
    async for event in chat.astream_events(
            "Write me a 1 verse song about goldfish on the moon"
    ):
        idx += 1
        # if idx >= 5:  # Truncate the output
        #     print("...Truncated")
        #     break
        print(event)

if __name__ == "__main__":
    # sync_chat()
    # asyncio.run(async_chat())
    asyncio.run(async_chat_event())
