#!/usr/bin/env python
# coding=utf-8


import os

import faiss
import numpy as np
from volcenginesdkarkruntime import Ark

from constants import EMBEDDINGS_MODEL_ID, CHAT_MODEL_ID
from misc import getArkClient, encode

client = Ark(api_key=os.environ.get("ARK_API_KEY"))

def test():
    resp = client.embeddings.create(
        model=EMBEDDINGS_MODEL_ID,
        input=[
            " 天很蓝",
            "海很深",
        ],
        encoding_format="float",
    )
    print(resp)

def demo():
    documents = [
        "人工智能是研究如何让计算机像人一样思考的科学。",
        "向量检索是通过比较文本语义向量之间的相似度来查找信息。",
        "豆包 embedding 是字节跳动推出的语义向量模型。",
        "大模型可以用于语言生成、问答系统、代码生成等多种任务。",
        "FAISS 是一种高效的相似向量检索工具，由 Meta 提出。",
    ]
    vectors = encode(documents)
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.stack(vectors))  # 添加向量

    # 用户输入问题 → 向量化
    query = "什么是 FAISS？"
    query_embedding = encode([query])

    # 在向量库中搜索最相关的文档
    top_k = 2
    distances, indices = index.search(np.array(query_embedding), top_k)

    # 组织 prompt（RAG） → 提供检索到的上下文 + 用户问题
    retrieved_context = "\n".join([documents[i] for i in indices[0]])
    prompt = f"""你是一个专业问答助手，请根据以下内容回答问题：

    【内容】
    {retrieved_context}

    【问题】
    {query}

    【回答】
    """

    print("prompt: " + prompt)
    # 调用大模型生成答案（以 GPT 为例）
    response = getArkClient().chat.completions.create(
        model=CHAT_MODEL_ID,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    # 输出结果
    print("🤖 回答：", response.choices[0].message.content)

if __name__ == "__main__":
    demo()
    # test()