#!/usr/bin/env python
# coding=utf-8

import os

from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.models import ModelFactory
from camel.types import ModelPlatformType
from colorama import Fore

from util import DOUBAO_SEED_1_6, ARK_API_URL

# 设置目标词
target_word = "袋鼠"

doubao_config = ChatGPTConfig(
    temperature=0.0,
    top_p=None,
    max_tokens=None,
    stream=False,
    stop=None,
)
doubao_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type=DOUBAO_SEED_1_6,
    model_config_dict=doubao_config.as_dict(),
    url=ARK_API_URL,
    api_key=os.environ["ARK_API_KEY"]
)

# 设置猜词者 system message（不能包含目标词）
guesser_sys_msg = """
你将参与一个猜物品名字的游戏。你不知道物品是什么，需要通过不断提出‘是/不是’的问题来逐步猜出这个物品。
以下是游戏的规则：
- 每次只能提出一个‘是/不是’的问题。不要一次提多个问题。
- 当你认为你知道这个物品是什么时，请直接说出：‘这个词是___’。
- 只有当对方说“恭喜你猜对了！”，才说明你猜对了。
- 如果你的问题是“是/不是”类型，对方只回答“是”或“不是”或“有”或“没有”。
- 如果你说出的词是目标词的父类型，对方会回答：“是这个类型，但是词不对”
"""

# 设置回答者 system message（包含目标词）
responder_sys_msg = f"""
你正在参与一个猜物品名字的游戏，注意物品名字可能细化到品牌、分类等。你的任务是根据对方提出的“是/不是”问题，以特定方式回应，帮助对方猜出目标物品。
目标词是： {target_word}
对方会通过问“是/不是”问题来尝试猜出这个词。你只能按照以下规则回答：
- 如果对方的问题是“是/不是”类型，你只能回答“是”或“不是”或“有”或“没有”。
- 如果对方说出的词就是目标词，你要回答：“恭喜你猜对了！”
- 如果对方说出的词是目标词的父类型，你需要回答：“是这个类型，但是词不对”
- 除此之外不能泄露任何信息。
"""

# 创建两个 Agent
guesser = ChatAgent(system_message=guesser_sys_msg, model=doubao_model, output_language="zh-CN")
responder = ChatAgent(system_message=responder_sys_msg, model=doubao_model, output_language="zh-CN")

# 初始化对话
guesser.reset()
responder.reset()

print(f"开始游戏：{guesser} 和 {responder}")
print(f"{guesser} 的系统信息：{guesser.role_name} {guesser.role_type} {guesser.chat_history} ")
print(f"{responder} 的系统信息：{responder.role_name} {responder.role_type} {responder.chat_history} ")

# 启动对话循环
responder_reply = None

for step in range(100):
    print(Fore.BLUE + f"\n🌀 第 {step} 轮对话")

    # 猜词者提问
    if step == 0:
        guesser_reply = guesser.step("开始")
    else:
        guesser_reply = guesser.step(responder_reply.msg)
    print(Fore.YELLOW + f"猜词者：{guesser_reply.msg.content.strip()}")
    print(Fore.CYAN + str(guesser_reply.info.get('usage')))
    # print(f"{guesser} 的历史信息：{guesser.chat_history} ")
    # print(f"{guesser} 的记忆：{guesser.memory.get_context()}")

    # 回答者回应
    responder_reply = responder.step(guesser_reply.msg)
    print(Fore.GREEN + f"回答者：{responder_reply.msg.content.strip()}")
    print(Fore.CYAN + str(responder_reply.info.get('usage')))
    # print(f"{responder} 的历史信息：{responder.chat_history} ")
    # print(f"{responder} 的记忆：{responder.memory.get_context()}")

    # 判断是否猜对
    if "恭喜你猜对了" in responder_reply.msg.content:
        print("\n🎉 游戏结束：猜词成功！")
        break

    # 更新对话输入
    responder_msg = responder_reply.msg
