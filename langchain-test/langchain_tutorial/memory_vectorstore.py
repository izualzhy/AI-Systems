#!/usr/bin/env python
# coding=utf-8
from azure.ai.documentintelligence.models import DocumentFormula
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

from utils.doubao_embeddings import DoubaoEmbedding

vector_store = InMemoryVectorStore(DoubaoEmbedding())

documents = [
]

ids = vector_store.add_documents(documents=[Document(i) for i in documents])
print(ids)

result = vector_store.similarity_search("", k=1)
print(result)
