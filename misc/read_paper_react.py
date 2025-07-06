#!/usr/bin/env python
# coding=utf-8
import logging

from langchain.agents import Tool, initialize_agent, AgentType, ZeroShotAgent, AgentExecutor, create_react_agent
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate

from util import *

# logging.basicConfig(level=logging.DEBUG)

# 工具函数
def get_current_weather(location: str):
    print(f"\n** [函数被调用] location = {location} **\n")
    return f"{location} 今天天气晴，25°C."

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
# llm = getDoubaoSeed16()
llm = getDoubao15VisionLite()
# llm = getDeepSeekR1()

def v1():
    # llm = getDeepSeekR1()
    agent = initialize_agent(tools,
                             llm,
                             agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                             # agent_type="openai-tools",
                             verbose=True,
                             temperature=0,
                             handle_parsing_errors=True)

    def debug():
        print("------ template:")
        print(agent.agent.llm_chain.prompt.template)
        print("------ prompt")
        print(agent.agent.llm_chain.prompt)
        response = agent.invoke("请问上海的天气怎么样？", return_intermediate_steps=True)
        print(response["intermediate_steps"])

    def run():
        print(agent.agent.llm_chain.prompt.template)
        # 用户提问
        result = agent.invoke("请问上海的天气怎么样？")
        print(result)
    # debug()
    run()

def v2():
    template = """Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format exactly. You must either output an Action or a Final Answer, but not both at the same time.

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    {agent_scratchpad}"""

    # 生成 Prompt 对象
    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=template,
        input_variables=["input", "agent_scratchpad"]
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools)

    # 创建 Agent 执行器
    agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
    question = "请问上海的天气怎么样？"
    inputs = {
        "input": question,
        "agent_scratchpad": "",
        "tools": "\n".join(f"{t.name}: {t.description}" for t in tools),
        "tool_names": ", ".join(t.name for t in tools)
    }

    result = agent_executor.invoke(inputs)
    print(result)

def v3():
    react_template = """Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}"""

    prompt = PromptTemplate(
        template=react_template,
        input_variables=["tools", "tool_names", "input", "agent_scratchpad"]
    )

    aTools = [Tool(
        name="get_current_weather",
        func=get_current_weather,
        description="获取城市当前天气",
        handle_parsing_errors=True
    )]
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=aTools, verbose=True, handle_parsing_errors=True
    )
    agent_executor.invoke(
        {
            "input": "上海天气如何？"
        }
    )

if __name__ == '__main__':
    print("v1")
    v1()
    print("v2")
    # v2()
    print("v3")
    # v3()