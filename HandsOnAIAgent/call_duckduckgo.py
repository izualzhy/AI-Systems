#!/usr/bin/env python
# coding=utf-8


from duckduckgo_search import DDGS

def search_duckduckgo(query):
    with DDGS() as ddgs:
        results = ddgs.text(query)
        return list(results)

print(search_duckduckgo("ChatGPT 是什么？")[0])
