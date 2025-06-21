#!/usr/bin/env python
# coding=utf-8


from langchain.agents import Tool, initialize_agent
from langchain_openai import ChatOpenAI

from misc import getChatOpenAI


# 工具函数
def get_current_weather(location: str):
    print(f"[函数被调用] location = {location}")
    return f"{location} 今天天气晴，25°C"

# LangChain Tool
tools = [
    Tool.from_function(
        func=get_current_weather,
        name="get_current_weather",
        description="获取城市当前天气",
        handle_parsing_errors=True
    )
]

# 初始化 Agent
llm = getChatOpenAI()
agent = initialize_agent(tools,
                         llm,
                         # agent_type="openai-tools",
                         verbose=True,
                         temperature=0)

def debug():
    print(agent.agent.llm_chain.prompt)
    response = agent.invoke("请问上海的天气怎么样？", return_intermediate_steps=True)
    print(response["intermediate_steps"])

def run():
    # 用户提问
    result = agent.run("请问上海的天气怎么样？")
    print(result)

# debug()
run()