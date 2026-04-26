#!/usr/bin/env python
# coding=utf-8

import os

import numpy as np
# from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from constants import DOUBAO_SEED_1_6_THINKING, ARK_API_URL, EMBEDDINGS_MODEL_ID, DEEPSEEK_V3, \
    DEEPSEEK_R1_DISTILL_QWEN_32B, DOUBAO_1_5_VISION_PRO
from misc.util import DOUBAO_1_5_VISION_LITE, DOUBAO_SEED_1_6, DEEPSEEK_R1, DOUBAO_SEED_1_6_FLASH, DEEPSEEK_V31


def getArkClient():
    client = OpenAI(
        # 此为默认路径，您可根据业务所在地域进行配置
        base_url=ARK_API_URL,
        # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
        api_key=os.environ.get("ARK_API_KEY"),
    )

    return client


def getDoubaoSeed16Thinking():
    model = ChatOpenAI(
        model=DOUBAO_SEED_1_6_THINKING,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True
    )

    return model

def getDoubaoSeed16(**kwargs):
    model = ChatOpenAI(
        model=DOUBAO_SEED_1_6,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True,
        **kwargs
    )

    return model
def getDoubao15VisionPro(**kwargs):
    model = ChatOpenAI(
        model=DOUBAO_1_5_VISION_PRO,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True,
        **kwargs
    )

    return model
def getDoubao15VisionLite(**kwargs):
    model = ChatOpenAI(
        model=DOUBAO_1_5_VISION_LITE,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True,
        **kwargs
    )

    return model

def getDeepSeekV31():
    model = ChatOpenAI(
        model=DEEPSEEK_V31,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True
    )

    return model

def getDeepSeekV3():
    model = ChatOpenAI(
        model=DEEPSEEK_V3,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True
    )

    return model

def getDeepSeekR1():
    model = ChatOpenAI(
        model=DEEPSEEK_R1,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True
    )

    return model

def getDeepSeekR1DistillQwen32B():
    model = ChatOpenAI(
        model=DEEPSEEK_R1_DISTILL_QWEN_32B,
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