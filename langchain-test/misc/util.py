#!/usr/bin/env python
# coding=utf-8
import os

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from misc.util import DOUBAO_1_5_VISION_LITE, DOUBAO_SEED_1_6, DEEPSEEK_R1, DOUBAO_SEED_1_6_FLASH, DOUBAO_1_5_VISION_PRO, DEEPSEEK_V31


ARK_API_URL="https://ark.cn-beijing.volces.com/api/v3"

def getDoubaoSeed16(**kwargs):
    model = ChatOpenAI(
        model=DOUBAO_SEED_1_6,
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

def getDeepSeekR1():
    model = ChatOpenAI(
        model=DEEPSEEK_R1,
        base_url=ARK_API_URL,
        api_key=os.environ.get("ARK_API_KEY"),
        verbose=True
    )

    return model
def invokeLLM(llm: ChatOpenAI, question: str):
    prompt = HumanMessage(content=question)
    response = llm.invoke([prompt])
    return response.content