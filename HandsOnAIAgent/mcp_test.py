#!/usr/bin/env python
# coding=utf-8

# 安装包
# pip install langchain-mcp-adapters langchain langgraph

# 客户端示例
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import ChatOpenAI  # 或 Claude

def foo1():
    client = MultiServerMCPClient({
        "mytools": {
            "url": "http://localhost:8080",
            "transport": "streamable_http"
        }
    })

    tools = client.get_tools()

    agent = create_react_agent(ChatOpenAI(model="gpt-4"), tools)
    response = agent.ainvoke({
        "messages": [{"role":"user", "content":"get_time tool 给我服务器时间"}]
    })
    print(response)

def foo2():
    from langchain_mcp_tools import convert_mcp_to_langchain_tools
    from langchain.chat_models import ChatOpenAI
    from langgraph.prebuilt import create_react_agent

    mcp_servers = {
        "localhost": { "url": "http://localhost:8080" }
    }
    tools, cleanup = convert_mcp_to_langchain_tools(mcp_servers)
    agent = create_react_agent(ChatOpenAI(model="gpt-4"), tools)
    response = agent.ainvoke({"messages":[{"role":"user","content":"使用 get_time"}]})

