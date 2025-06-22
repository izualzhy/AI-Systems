#!/usr/bin/env python
# coding=utf-8

import os

import numpy as np
from langchain_openai import ChatOpenAI
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from constants import CHAT_MODEL_ID, ARK_API_URL, EMBEDDINGS_MODEL_ID


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
        verbose=True
    )

    return model


def encode(documents):
    client = Ark(api_key=os.environ.get("ARK_API_KEY"))

    resp = client.embeddings.create(
        model=EMBEDDINGS_MODEL_ID,
        input=documents,
        encoding_format="float",
    )
    vectors = [np.array(e.embedding, dtype=np.float32) for e in resp.data]
    return vectors