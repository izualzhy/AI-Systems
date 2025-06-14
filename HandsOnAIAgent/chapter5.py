#!/usr/bin/env python
# coding=utf-8
import json

from constants import CHAT_MODEL_ID
from misc import getArkClient


client = getArkClient()

# 鼓励函数
def get_encouragement(name, mood):
    # 基础鼓励消息
    messages = {
        "happy": "继续保持积极的心态，做得好！",
        "sad": "记住，即使在最黑暗的日子里，也会有阳光等着你。",
        "tired": "你做得足够好，现在是时候休息一下了。",
        "stressed": "深呼吸，一切都会好起来。"
    }
    # 获取对应心情的鼓励消息
    message = messages.get(mood.lower(), "你今天感觉如何？我总是在这里支持你！")
    # 返回定制化的鼓励消息
    return f"亲爱的{name}，{message}"
# 使用示例
print(get_encouragement("小雪", "tired"))

def function_call_mood():
    response = client.chat.completions.create(
        # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
        model=CHAT_MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [
                    # {"type": "text", "text": "你好，请和我随便说句话吧。"},
                    {"type": "text", "text": "你好，我觉得有点疲惫。"},
                ],
            }
        ],
        tools=[
            {
            "type": "function",
            "function": {
                "name": "get_encouragement",
                "description": "根据用户的心情提供鼓励信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "mood": {
                            "type": "string",
                            "description": "用户当前的心情，例如：开心，难过，压力大，疲倦"
                        },
                        "name": {
                            "type": "string",
                            "description": "用户的名字，用来个性化鼓励信息"
                        }
                    },
                    "required": ["mood"]
                }
            }},
        ]
    )
    print(response)
    print(response.choices[0])
    # TODO: 根据返回值调用本地方法

def function_call_flower_inventory():
    # 定义查询鲜花库存的函数
    def get_flower_inventory(city):
        """获取指定城市的鲜花库存"""
        if "北京" in city:
            return json.dumps({"city": "北京", "inventory": "玫瑰: 100, 郁金香: 150"})
        elif "上海" in city:
            return json.dumps({"city": "上海", "inventory": "百合: 80, 康乃馨: 120"})
        elif "深圳" in city:
            return json.dumps({"city": "深圳", "inventory": "向日葵: 200, 玉兰: 90"})
        else:
            return json.dumps({"city": city, "inventory": "未知"})
    # 定义工具列表（函数元数据）
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_flower_inventory",
                "description": "获取指定城市的鲜花库存",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，如北京、上海或深圳"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    # 初始化对话内容
    messages = [{"role": "user", "content": "北京、上海和深圳的鲜花库存是多少？"}]
    print("message:", messages)
    # 第一次对话响应
    first_response = client.chat.completions.create(
        model=CHAT_MODEL_ID,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    # 打印响应的内容
    print(first_response)
    response_message = first_response.choices[0].message
    # 检查是否需要调用工具
    tool_calls = response_message.tool_calls
    if tool_calls:
        messages.append(response_message)
        # 如果需要调用工具，调用工具并添加库存查询结果
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            # TODO: 直接调用修改为反射
            function_response = get_flower_inventory(
                city=function_args.get("city")
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
    # 打印当前消息列表
    print("message:", messages)


    # 第二次向大模型发送对话以获取最终响应
    second_response = client.chat.completions.create(
        model=CHAT_MODEL_ID,
        messages=messages
    )
    # 打印最终响应
    final_response = second_response.choices[0].message
    print(final_response)

function_call_flower_inventory()