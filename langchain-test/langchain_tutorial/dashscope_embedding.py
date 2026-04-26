#!/usr/bin/env python
# coding=utf-8
import os

from langchain_community.embeddings import DashScopeEmbeddings
# embeddings = DashScopeEmbeddings(dashscope_api_key=os.environ.get("DASHSCOPE_API_KEY"))

embeddings = DashScopeEmbeddings(
    model="text-embedding-v4",
)
text = "衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买"
query_result = embeddings.embed_query(text)

print(query_result)