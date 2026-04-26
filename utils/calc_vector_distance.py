#!/usr/bin/env python
# coding=utf-8


import numpy as np

v1 = np.array([1, 2, 3])
v2 = np.array([2, 1, 0])

def calc_distance(v1, v2):
    vec1 = np.array(v1, dtype=np.float32)
    vec2 = np.array(v2, dtype=np.float32)

    dist = np.linalg.norm(vec1 - vec2)

    cos_sim = np.dot(vec1, vec2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    return dist, cos_sim

import os
from openai import OpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("ARK_API_KEY"),
    base_url="https://ark.cn-beijing.volces.com/api/v3",
)

def embedding_func(query: str):
    print("----- embeddings request -----")
    resp = client.embeddings.create(
        model="ep-20251001202400-vlv9s",
        input=[query],
        encoding_format="float"
    )
    # print(resp)
    return resp.data[0].embedding

queries = [
    "霜叶红于二月花",
    "远上寒山石径斜",
    "过江千尺浪",
    "入竹万竿斜",
    "危楼高百尺",
    "手可摘星辰",
    "不敢高声语",
    "恐惊天上人",
    "天气怎么样",
    "下雨了"
]

embeddings = [embedding_func(query) for query in queries]
for i, v1 in enumerate(embeddings):
    for j, v2 in enumerate(embeddings):
        print(f"{i} - {j} : ", calc_distance(v1, v2))
