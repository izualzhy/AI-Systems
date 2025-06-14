#!/usr/bin/env python
# coding=utf-8
import os
import sys

os.environ["HTTP_PROXY"] = "http://127.0.0.1:1087"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1087"

print(os.environ.get("OPENAI_API_KEY"))
print(os.environ.get("ARK_API_KEY"))
print(os.environ.get("SERPAPI_API_KEY"))

# 导入LangChain Hub
from langchain import hub
# 从LangChain Hub中获取ReAct的提示
prompt = hub.pull("hwchase17/react")
print(prompt)
# 导入OpenAI
from langchain_openai import OpenAI
# 选择要使用的大模型
llm = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY")
)

# 导入SerpAPIWrapper即工具包
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
# 实例化SerpAPIWrapper
search = SerpAPIWrapper()
# 准备工具列表
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="当大模型没有相关知识时，用于搜索知识"
    ),
]
# 导入create_react_agent功能
from langchain.agents import create_react_agent
# 构建ReAct Agent
agent = create_react_agent(llm, tools, prompt)
# 导入AgentExecutor
from langchain.agents import AgentExecutor
# 创建Agent执行器并传入Agent和工具
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# 调用AgentExecutor
agent_executor.invoke({"input": "当前Agent最新研究进展是什么？"})