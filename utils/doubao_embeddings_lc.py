#!/usr/bin/env python
# coding=utf-8


from llama_index.core.embeddings.base import BaseEmbedding
from pydantic import PrivateAttr
from utils.util import EMBEDDINGS_MODEL_ID
from volcenginesdkarkruntime import Ark
import os
from typing import List

class DoubaoEmbeddingLC:
    """直接调用 Ark SDK 的 Embedding"""
    def __init__(self):
        self.client = Ark(api_key=os.environ.get("ARK_API_KEY"))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        print(f"[DoubaoEmbeddingLC] embed_documents {texts}")
        resp = self.client.embeddings.create(
            model=EMBEDDINGS_MODEL_ID,
            input=texts,
            encoding_format="float",
        )
        return [i.embedding for i in resp.data]

    def embed_query(self, text: str) -> List[float]:
        print(f"[DoubaoEmbeddingLC] embed_query {text}")
        resp = self.client.embeddings.create(
            model=EMBEDDINGS_MODEL_ID,
            input=[text],
            encoding_format="float",
        )
        return resp.data[0].embedding


class DoubaoLlamaEmbeddingWrapper(BaseEmbedding):
    """适配 LlamaIndex 的豆包 Embedding"""
    _lc_embed: DoubaoEmbeddingLC = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "_lc_embed", DoubaoEmbeddingLC())

    def _get_text_embedding(self, text: str) -> List[float]:
        print(f"[DoubaoLlamaEmbeddingWrapper] _get_text_embedding: {text}")
        return self._lc_embed.embed_query(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        print(f"[DoubaoLlamaEmbeddingWrapper] _get_query_embedding: {query}")
        return self._lc_embed.embed_query(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        print(f"[DoubaoLlamaEmbeddingWrapper] _aget_query_embedding: {query}")
        return self._get_query_embedding(query)

    # def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
    #     print(f"[DoubaoLlamaEmbeddingWrapper] get_text_embedding_batch: {texts}")
    #     return self._lc_embed.embed_documents(texts)

    def get_text_embedding_batch(
            self, texts: List[str], show_progress: bool = False
    ) -> List[List[float]]:
        """
        llama_index 会调用这个方法，并可能传入 show_progress=True
        所以你必须接受这个参数
        """
        # 你可以选择是否显示进度条
        if show_progress:
            print(f"正在为 {len(texts)} 个文本生成嵌入...")

        # 调用你的实际嵌入逻辑
        embeddings = []
        for text in texts:
            emb = self.get_text_embedding(text)
            embeddings.append(emb)
        return embeddings

    def get_agg_embedding_from_queries(self, queries: List[str]) -> List[float]:
        """聚合多个 query 的向量，用平均作为默认策略"""
        vectors = [self._get_query_embedding(q) for q in queries]
        # 简单平均
        agg = [sum(col)/len(col) for col in zip(*vectors)]
        return agg
