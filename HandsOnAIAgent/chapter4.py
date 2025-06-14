#!/usr/bin/env python
# coding=utf-8


# 导入环境变量
from dotenv import load_dotenv

from constants import CHAT_MODEL_ID
from misc import getArkClient

load_dotenv()
# 创建client
from openai import OpenAI
client = getArkClient()
# 创建assistant
assistant = client.beta.assistants.create(
    name="鲜花价格计算器",
    instructions="你能够帮我计算鲜花的价格",
    tools=[{"type": "code_interpreter"}],
    model=CHAT_MODEL_ID
)
# 打印assistant
print(assistant)