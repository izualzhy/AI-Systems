#!/usr/bin/env python
# coding=utf-8


import os

from constants import DOUBAO_SEED_1_6_THINKING
from misc import getArkClient

print(os.environ.get("OPENAI_API_KEY"))
print(os.environ.get("ARK_API_KEY"))

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = getArkClient()

def test():
    response = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model="ep-20250612180931-z9sd6",
        messages=[
            {
                "role": "user",
                "content": [
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    #     },
                    # },
                    {"type": "text", "text": "今天是哪天?"},
                ],
            }
        ],
    )
    print(response)
    print(response.choices[0])


def call_function():
    response = client.chat.completions.create(
        # 创建一个函数调用，指定函数名称和参数
        model=DOUBAO_SEED_1_6_THINKING,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to tools."
            },
            {
                "role": "user",
                "content": "Question: 请问上海天气怎么样？\nThought:[]"
            }
        ],
        functions=[
            {
                "name": "get_current_weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string"
                        }
                    },
                    "required": ["location"]
                },
                "description": "获取城市当前天气"
            }
        ]
    )

    print(response)
    print(response.choices[0])

def call_react_1st():
    response = client.chat.completions.create(
        model=DOUBAO_SEED_1_6_THINKING,
        messages=[
            {
                "role": "user",
                "content": "Answer the following questions as best you can. You have access to the following tools:\n\nget_current_weather(location: str) - 获取城市当前天气\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [get_current_weather]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: 请问上海的天气怎么样？\nThought:"
            }
        ],
        # stop=["\nObservation:", "\n\tObservation:"],
        stream=False
    )

    print(response)
    print(response.choices[0])

def call_react_2nd():
    response = client.chat.completions.create(
        model=DOUBAO_SEED_1_6_THINKING,
        messages=[
            {
                "role": "user",
                "content": "Answer the following questions as best you can. You have access to the following tools:\n\nget_current_weather(location: str) - 获取城市当前天气\n\nUse the following format:\n\nQuestion: the input question you must answer\nThought: you should always think about what to do\nAction: the action to take, should be one of [get_current_weather]\nAction Input: the input to the action\nObservation: the result of the action\n... (this Thought/Action/Action Input/Observation can repeat N times)\nThought: I now know the final answer\nFinal Answer: the final answer to the original input question\n\nBegin!\n\nQuestion: 请问上海的天气怎么样？\nThought:Thought: 我需要回答用户关于上海当前天气的问题，根据可用工具，应该调用get_current_weather函数来获取上海的天气信息。\nAction: get_current_weather\nAction Input: {\"location\": \"上海\"}\nObservation: {\"location\": \"上海\"} 今天天气晴，25°C\nThought:"
            }
        ],
        # stop=["\nObservation:", "\n\tObservation:"],
        stream=False
    )

    print(response)
    print(response.choices[0])

def call_function_v2():
    """not worked currently."""
    response = client.chat.completions.create(
        # 创建一个函数调用，指定函数名称和参数
        model=DOUBAO_SEED_1_6_THINKING,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant with access to tools.",
                # "content": "You are a helpful AI assistant.",
            },
            {
                "role": "user",
                "content": "请问上海的天气怎么样？"
            }
        ],
        # functions=[
        #     {
        #         "name": "get_current_weather",
        #         "parameters": {
        #             "location": "上海"  # 补全location参数（原JSON中未填写，需手动补充）
        #         }
        #     }
        # ],
        # tools =[
        functions = [
        {
                "name": "get_current_weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string"
                        }
                    },
                    "required": ["location"]
                },
                "description": "获取城市当前天气"
            }
        ],
        stream=False
    )

    print(response)
    print(response.choices[0])

def call_camel_agents_demo():
    response = client.chat.completions.create(
        # 创建一个函数调用，指定函数名称和参数
        model=DOUBAO_SEED_1_6_THINKING,
        messages=[
            {
                "role": "system",
                "content": "你是 花店营销专员，我是 花店老板。我们各自扮演固定角色，不得互换。\n\n我们在完成以下任务方面有共同目标：\n任务是：策划夏季茉莉夜营销：布置、互动、促销、推广方案。\n\n你必须始终根据我的指令提供帮助，且每次仅回应一个具体、可行的解决方案。必须符合以下要求：\n\n1. 不得反过来指示我；\n2. 不得提出任何问题；\n3. 不得提供与指令无关的内容；\n4. 不得生成错误或无法执行的方案，如遇物理、道德、法律或能力限制，应明确拒绝并解释原因；\n5. 必须给出回复\n6. 回复必须使用陈述句和现在时态；\n7. 回复结构必须如下：\n\n解决方案：<YOUR_SOLUTION>  \n<YOUR_SOLUTION> 应该是具体实现，包括推荐方法与例子。  \n始终以 “下一个请求。” 结尾。\n\n除非我明确告知任务已完成，你始终应按上述格式回应。"
            },
            {
                "role": "user",
                "content": "现在开始逐一给我介绍。只回复指令和输入。"
            }
        ],
        # functions=[
        #     {
        #         "name": "get_current_weather",
        #         "parameters": {
        #             "location": "上海"  # 补全location参数（原JSON中未填写，需手动补充）
        #         }
        #     }
        # ],
        # tools =[
        functions = [
            {
                "name": "get_current_weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string"
                        }
                    },
                    "required": ["location"]
                },
                "description": "获取城市当前天气"
            }
        ],
        stream=False
    )

    print(response)
    print(response.choices[0])

print("call_function")
call_function()

print("\n" * 2 + "call_function_v2")
call_function_v2()
# call_react_1st()
# call_react_2nd()
