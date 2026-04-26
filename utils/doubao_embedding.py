#!/usr/bin/env python
# coding=utf-8
import os

from langchain_core.embeddings import Embeddings
from volcenginesdkarkruntime import Ark

from utils.util import EMBEDDINGS_MODEL_ID


class DoubaoEmbedding(Embeddings):
    def __init__(self):
        self.client = Ark(api_key=os.environ.get("ARK_API_KEY"))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if texts is not None and len(texts) == 0:
            return []

        """用于批量文档嵌入"""
        resp = self.client.embeddings.create(
            model=EMBEDDINGS_MODEL_ID,
            input=texts,
            encoding_format="float",
        )
        return [i.embedding for i in resp.data]
        # vectors = [np.array(e.embedding, dtype=np.float32) for e in resp.data]
        # return vectors

    def embed_query(self, text: str) -> list[float]:
        if not text:
            return None
        """用于单条查询嵌入"""
        resp = self.client.embeddings.create(
            model=EMBEDDINGS_MODEL_ID,
            input=[text],
            encoding_format="float",
        )
        return resp.data[0].embedding