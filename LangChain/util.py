#!/usr/bin/env python
# coding=utf-8
import os

import numpy as np
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from volcenginesdkarkruntime import Ark

DOUBAO_SEED_1_6="ep-20250623173924-pzkz9"
DOUBAO_1_5_VISION_LITE="ep-20250627151830-czb6d"
DEEPSEEK_R1="ep-20250624171255-z8cgd"
EMBEDDINGS_MODEL_ID="doubao-embedding-text-240715"

ARK_API_URL="https://ark.cn-beijing.volces.com/api/v3"


def getDoubaoSeed16ChatModel():
    model = init_chat_model(
        DOUBAO_SEED_1_6,
        model_provider = 'openai',
        base_url = ARK_API_URL
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

def embed_query(documents):
    client = Ark(api_key=os.environ.get("ARK_API_KEY"))

    resp = client.embeddings.create(
        model=EMBEDDINGS_MODEL_ID,
        input=documents,
        encoding_format="float",
    )
    vectors = [np.array(e.embedding, dtype=np.float32) for e in resp.data]
    return vectors