#!/usr/bin/env python
# coding=utf-8

# https://python.langchain.com/docs/how_to/summarize_stuff/#invoke-chain


from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate

from utils.util import getDoubaoSeed16

open_source_agent_readme = [
    'https://raw.githubusercontent.com/jd-opensource/joyagent-jdgenie/refs/heads/main/README.md',
    'https://raw.githubusercontent.com/coze-dev/coze-studio/refs/heads/main/README.zh_CN.md',
    'https://raw.githubusercontent.com/langgenius/dify/refs/heads/main/README_CN.md',
    'https://raw.githubusercontent.com/dataelement/bisheng/refs/heads/main/README_CN.md'
]

open_source_agent_readme_documents = []
for url in open_source_agent_readme:
    proxies = {
        "http": "http://127.0.0.1:1087",  # HTTP 代理
        "https": "http://127.0.0.1:1087",  # HTTPS 代理
    }
    loader = WebBaseLoader(url, proxies=proxies, verify_ssl=False)
    documents = loader.load()
    open_source_agent_readme_documents.append(documents[0])

llm = getDoubaoSeed16()

prompt = ChatPromptTemplate.from_template("这是开源的智能体框架文档: {context}，请你对比给出优劣势分析。")
chain = create_stuff_documents_chain(llm, prompt)
result = chain.invoke({"context": open_source_agent_readme_documents})
print(result)



