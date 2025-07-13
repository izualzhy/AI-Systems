#!/usr/bin/env python
# coding=utf-8


# 初始化大模型
from openai import OpenAI

from misc import getArkClient, getDoubaoSeed16Thinking

llm = getDoubaoSeed16Thinking()

# 设置工具
# from langchain.agents import load_tools
# tools = load_tools(["bing-search", "llm-math"], llm=llm)
from langchain_community.agent_toolkits.load_tools import load_tools
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# 设计提示模板
from langchain.prompts import PromptTemplate
template = (
    """尽你所能回答以下问题。如果能力不够，你可以使用以下工具:\n\n
    {tools}\n\n
    Use the following format:\n\n
    'Question: the input question you must answer\n'
    'Thought: you should always think about what to do\n'
    'Action: the action to take, should be one of [{tool_names}]\n'
    'Action Input: the input to the action\n'
    'Observation: the result of the action\n'
    '... (this Thought/Action/Action Input/Observation can repeat N times)\n'
    'Thought: I now know the final answer\n'
    'Final Answer: the final answer to the original input question\n\n'
    'Begin!\n\n'
    'Question: {input}\n'
    'Thought:{agent_scratchpad}'"""
)
prompt = PromptTemplate.from_template(template)

# 初始化Agent
from langchain.agents import create_react_agent
agent = create_react_agent(llm, tools, prompt)

# 用Agent和Tools初始化一个AgentExecutor
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 通过AgentExecutor执行任务
agent_executor.invoke({"input":
                       """目前市场上玫瑰花的一般进货价格是多少？\n
                       如果我在此基础上加价5%，应该如何定价？"""})
