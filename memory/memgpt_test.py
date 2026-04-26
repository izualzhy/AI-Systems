#!/usr/bin/env python
# coding=utf-8
import os

from letta_client import Letta

from utils.util import DEEPSEEK_V31, EMBEDDINGS_MODEL_ID

VOLCENGINE_API_KEY = os.environ.get("ARK_API_KEY")
VOLCENGINE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 火山引擎 API 端点


def test():
    client = Letta(token=VOLCENGINE_API_KEY, base_url=VOLCENGINE_BASE_URL)

    agent_state = client.agents.create(
        model=DEEPSEEK_V31,
        embedding=EMBEDDINGS_MODEL_ID,
        memory_blocks=[
            {
                "label": "human",
                "value": "The human's name is Chad. They like vibe coding."
            },
            {
                "label": "persona",
                "value": "My name is Sam, a helpful assistant."
            }
        ],
    )

    print(agent_state.id)

    response = client.agents.messages.create(
        agent_id='123',
        messages=[
            {
                "role": "user",
                "content": "Hey, nice to meet you, my name is Brad."
            }
        ]
    )
    print(response)

if __name__ == "__main__":
    test()
