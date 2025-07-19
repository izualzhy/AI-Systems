#!/usr/bin/env python
# coding=utf-8
from typing import List

# https://python.langchain.com/docs/tutorials/retrievers/


from langchain_core.documents import Document
from langchain_core.runnables import chain

from doubao_embeddings import DoubaoEmbedding
from util import embed_query

documents = [
    Document(
        page_content="Dogs are great companions, known for their loyalty and friendliness.",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="Cats are independent pets that often enjoy their own space.",
        metadata={"source": "mammal-pets-doc"},
    ),
]

from langchain_community.document_loaders import PyPDFLoader

file_path = "/Users/yingzhang/Desktop/1.pdf"
loader = PyPDFLoader(file_path)

docs = loader.load()

print(len(docs))

print(f"{docs[0].page_content[:200]}\n")
print(docs[0].metadata)

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000, chunk_overlap=200, add_start_index=True
)
all_splits = text_splitter.split_documents(docs)

print(f"len(all_splits): {len(all_splits)}")

from langchain_openai import OpenAIEmbeddings

# embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_1 = embed_query([all_splits[0].page_content])[0]
vector_2 = embed_query([all_splits[1].page_content])[0]

assert len(vector_1) == len(vector_2)
print(f"Generated vectors of length {len(vector_1)}\n")
print(vector_1[:10])


from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(DoubaoEmbedding())
ids = vector_store.add_documents(documents=all_splits)

results = vector_store.similarity_search(
    "北京资源池 ARM 集群"
)

print("results[0]:")
print(results[0])

embedding = embed_query("北京资源池 ARM 集群")[0]

results = vector_store.similarity_search_by_vector(embedding)
print("results[0]:")
print(results[0])

@chain
def retriever(query: str) -> List[Document]:
    return vector_store.similarity_search(query, k=1)

print("retriever.batch")
print(retriever.batch(
    [
        "北京资源池 ARM 集群",
    ],
))