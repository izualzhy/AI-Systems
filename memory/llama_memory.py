#!/usr/bin/env python
# coding=utf-8
import os

from langchain_core.messages import HumanMessage
from llama_index import ServiceContext

from utils.doubao_embeddings_lc import DoubaoLlamaEmbeddingWrapper

VOLCENGINE_API_KEY = os.environ.get("ARK_API_KEY")
VOLCENGINE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 火山引擎 API 端点


def test2():
    from utils.doubao_embeddings import DoubaoEmbedding
    from utils.util import getDeepSeekV31
    # from llama_index.core import VectorStoreIndex, StorageContext
    # from llama_index.core.schema import Document
    from llama_index import VectorStoreIndex, StorageContext, Document

    from llama_index.embeddings.openai import OpenAIEmbedding


    # -----------------------------
    # 1. 初始化 LLM 与 embedding
    # -----------------------------
    llm = getDeepSeekV31()

    doc = Document(text="测试文档")

    # 1. 初始化 embedding
    embedding = DoubaoLlamaEmbeddingWrapper()

    # 2. 初始化 StorageContext（默认，不带 embed_model）
    storage_context = StorageContext.from_defaults()

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embedding)

    # 3. 初始化 VectorStoreIndex 时指定 embedding
    memory_index = VectorStoreIndex(
        nodes=[],
        documents=[doc],
        storage_context=storage_context,
        service_context=service_context,
    )

    print("初始化完成")

    # -----------------------------
    # 2. 一次 LLM 交互流程函数（购物场景）
    # -----------------------------
    def llm_interaction(user_input: str, top_k: int = 3):
        # 1. 读取购物记忆片段
        query_engine = memory_index.as_query_engine(similarity_top_k=top_k)

        print("用户输入:", user_input)
        response = query_engine.query(user_input)

        print("memory_index 回复:", response)

        # 提取召回内容
        recalled_texts = []
        if hasattr(response, "source_nodes"):
            recalled_texts = [n.node.text for n in response.source_nodes]
        elif hasattr(response, "text"):
            recalled_texts = [response.text]

        # 2. 构造购物助手 prompt
        prompt = "你是一个智能购物助手，请根据以下用户的购物记忆片段生成个性化回复：\n"
        if recalled_texts:
            prompt += "已知购物记忆:\n" + "\n".join(f"- {t}" for t in recalled_texts) + "\n"
        else:
            prompt += "暂无购物记忆\n"
        prompt += f"\n用户输入: {user_input}\n\n助手回复:"

        # 3. 调用 LLM
        messages = [HumanMessage(content=prompt)]
        print("messages:", messages)
        response = llm.invoke(messages)

        print("助手回复:", response)

        # 4. 存储购物相关记忆（直接存储用户输入）
        new_doc = Document(text=user_input)
        memory_index.insert(new_doc)
        print("已保存新的购物记忆片段。\n---\n")

    # -----------------------------
    # 3. 使用示例（购物场景对话）
    # -----------------------------
    llm_interaction("我喜欢买耐克的运动鞋，一般穿42码。")
    llm_interaction("今天天气真好")
    llm_interaction("我想买个蓝牙耳机，预算在500元左右。")
    llm_interaction("之前买的阿迪达斯外套质量不错，还想再买一件。")
    llm_interaction("我不太喜欢网购，更喜欢去实体店试穿后再买。")

    # -----------------------------
    # 4. 查询购物记忆片段
    # -----------------------------
    query = "你记得我的购物偏好吗？"
    retriever = memory_index.as_retriever(similarity_top_k=5)
    results = retriever.retrieve(query)

    print("检索到的购物记忆片段:")
    for r in results:
        print(f"- {r.text} (score: {r.score:.3f})")

    query_engine = memory_index.as_query_engine(similarity_top_k=5)
    ai_response = query_engine.query("用户说：" + query + "。请记住这条信息。")
    print("AI 回复:", ai_response)


if __name__ == "__main__":
    test2()
