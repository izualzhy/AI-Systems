#!/usr/bin/env python
# coding=utf-8

import os

from langchain_openai import ChatOpenAI  # 用于调用OpenAI公司的GPT模型
from openai import OpenAI

from constants import CHAT_MODEL_ID, ARK_API_URL


def getArkClient():
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url=ARK_API_URL,
        # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
        api_key=os.environ.get("ARK_API_KEY"),
    )

    return client


def getChatOpenAI():
    model = ChatOpenAI(
        model=CHAT_MODEL_ID,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
    )

    return model
