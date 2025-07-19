#!/usr/bin/env python
# coding=utf-8
import os
from typing import Literal

# https://python.langchain.com/docs/tutorials/rag/


import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict, Annotated

from doubao_embeddings import DoubaoEmbedding
from util import getDoubaoSeed16

# Load and chunk contents of the blog
os.environ['HTTP_PROXY']='http://127.0.0.1:1087'
os.environ['HTTPS_PROXY']='http://127.0.0.1:1087'

loader = WebBaseLoader(
    web_paths=("https://izualzhy.cn/llm-paper-read-camel-autogen",),
    encoding = "utf-8",
    # web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    # bs_kwargs=dict(
    #     parse_only=bs4.SoupStrainer(
    #         class_=("post-content", "post-title", "post-header")
    #     )
    # ),
)
docs = loader.load()
print(f"len(docs): {len(docs)}")
print(f"metadata: {docs[0].metadata}")
print(f"metadata: {docs[0].page_content}")
print(f"docs: {docs}")


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200
                                               , separators=["\n\n", "\n", " ", "。", "？", "！", "；", "，"])
all_splits = text_splitter.split_documents(docs)
print(f"len(all_splits): {len(all_splits)}")
for split in all_splits:
    print(f"split: {split}")

# Update metadata (illustration purposes)
total_documents = len(all_splits)
third = total_documents // 3

for i, document in enumerate(all_splits):
    if i < third:
        document.metadata["section"] = "beginning"
    elif i < 2 * third:
        document.metadata["section"] = "middle"
    else:
        document.metadata["section"] = "end"

# Index chunks
vector_store = InMemoryVectorStore(DoubaoEmbedding())
ids = vector_store.add_documents(documents=all_splits)
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
# N.B. for non-US LangSmith endpoints, you may need to specify
# api_url="https://api.smith.langchain.com" in hub.pull.
prompt = hub.pull("rlm/rag-prompt")
"""
prompt: input_variables=['context', 'question'] input_types={} partial_variables={} metadata={'lc_hub_owner': 'rlm', 'lc_hub_repo': 'rag-prompt', 'lc_hub_commit_hash': '50442af133e61576e74536c6556cefe1fac147cad032f4377b60c436e6cdcb6e'} messages=[HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context', 'question'], input_types={}, partial_variables={}, template="You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.\nQuestion: {question} \nContext: {context} \nAnswer:"), additional_kwargs={})]
"""
print(f"prompt: {prompt}")

# Define schema for search
class Search(TypedDict):
    """Search query."""

    query: Annotated[str, ..., "Search query to run."]
    section: Annotated[
        Literal["beginning", "middle", "end"],
        ...,
        "Section to query.",
    ]

# Define state for application
class State(TypedDict):
    question: str
    query: Search
    context: List[Document]
    answer: str

def analyze_query(state: State):
    structured_llm = llm.with_structured_output(Search)
    query = structured_llm.invoke(state["question"])
    return {"query": query}

# Define application steps
def retrieve(state: State):
    query = state["query"]
    retrieved_docs = vector_store.similarity_search(
        query["query"],
        filter=lambda doc: doc.metadata.get("section") == query["section"],
    )
    return {"context": retrieved_docs}

llm = getDoubaoSeed16(temperature=0)
def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    print(f"docs_content: {docs_content}")
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    print(f"messages: {messages}")
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([analyze_query, retrieve, generate])
graph_builder.add_edge(START, "analyze_query")
graph = graph_builder.compile()

from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))

response = graph.invoke({"question": "什么是 CAMEL"})
print("问题: " + response["question"])
print(f"上下文: {response["context"]}")
print("回答: " + response["answer"])
