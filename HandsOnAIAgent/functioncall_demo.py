#!/usr/bin/env python
# coding=utf-8
import sys

from langchain_core.tools import tool
from langchain.agents import create_openai_functions_agent, initialize_agent, AgentType
from langchain.agents import AgentExecutor
from langchain_core.prompts.structured import StructuredPrompt



from misc import getChatOpenAI


@tool
def get_current_weather(location: str) -> str:
    """获取指定城市的当前天气. Get the weather by location."""
    return f"{location} 今天天气晴，25°C"

print(get_current_weather.description)

llm = getChatOpenAI()

def custom_fc():
    from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

    function_call_prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are a helpful assistant with access to tools."
        ),
        HumanMessagePromptTemplate.from_template(
            "Question: {input}\nThought:{agent_scratchpad}"
        )
    ])

    print(f"function_call_prompt : \n{function_call_prompt}")
    print(f"function_call_prompt : \n{function_call_prompt.to_json()}")
    print(f"function_call_prompt : \n{function_call_prompt.to_json_not_implemented()}")
    agent = create_openai_functions_agent(
        llm=llm,
        tools=[get_current_weather],
        prompt=function_call_prompt
    )
    executor = AgentExecutor(agent=agent, tools=[get_current_weather], verbose=True)
    result = executor.invoke({"input": "请问上海天气怎么样？"})
    print(result)

def call_fc():
    tools = [get_current_weather]
    agent = initialize_agent(tools,
                             llm,
                             agent = AgentType.OPENAI_FUNCTIONS,
                             verbose=True,
                             temperature=0)

    def run():
        # 用户提问
        result = agent.run("请问上海的天气怎么样？")
        print(result)

    # debug()
    run()

call_fc()
# custom_fc()
