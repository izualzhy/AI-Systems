#!/usr/bin/env python
# coding=utf-8


#!/usr/bin/env python
# coding=utf-8
import os

# 导入autogen包
import autogen

from util import ARK_API_URL, DOUBAO_SEED_1_6
# !/usr/bin/env python
# coding=utf-8
import os

# 导入autogen包
import autogen

from util import ARK_API_URL, DOUBAO_SEED_1_6

#配置大模型
llm_config = {
    "config_list": [
        {
            "model": DOUBAO_SEED_1_6,
            "api_key": os.environ.get("ARK_API_KEY"),
            "base_url": ARK_API_URL
        }
    ],
}

# 设置目标词
target_word = "袋鼠"

responder = autogen.AssistantAgent(
    name="回答者",
    llm_config= llm_config,
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("恭喜你猜对了"),
    system_message=f"""
    你正在参与一个猜物品名字的游戏，注意物品名字可能细化到品牌、分类等。你的任务是根据对方提出的“是/不是”问题，以特定方式回应，帮助对方猜出目标物品。
    目标词是： {target_word}
    对方会通过问“是/不是”问题来尝试猜出这个词。你只能按照以下规则回答：
    - 如果对方的问题是“是/不是”类型，你只能回答“是”或“不是”或“有”或“没有”。
    - 如果对方说出的词就是目标词，你要回答：“恭喜你猜对了！”
    - 如果对方说出的词是目标词的父类型，你需要回答：“是这个类型，但是词不对”
    - 除此之外不能泄露任何信息。
    """
)

guesser = autogen.AssistantAgent(
    name="猜词者",
    llm_config=llm_config,
    system_message="""
    你正在玩一个猜物品名字的游戏，你不知道目标词是什么，需要通过提出‘是/不是’的问题来逐步缩小范围，直到猜中。
    游戏规则如下：
    - 每次只能提出一个‘是/不是’的问题。
    - 如果你认为你知道答案，可以说“这个词是___”。
    - 如果你猜对了，对方会说“恭喜你猜对了！”。
    - 如果你说出了父类，对方会说“是这个类型，但是词不对”。
    - 请你根据之前的提问和回答合理地提出下一个问题，直到你猜中或者你说“结束”。
    """
)

# 创建用户代理
# user_proxy = autogen.UserProxyAgent(
#     name="用户代理",
#     human_input_mode="ALWAYS",
#     is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("结束"),
#     code_execution_config={
#         "last_n_messages": 1,
#         "work_dir": "tasks",
#         "use_docker": False,
#     },
#     system_message="""
#     你将参与一个猜物品名字的游戏。你不知道物品是什么，需要通过不断提出‘是/不是’的问题来逐步猜出这个物品。
#     以下是游戏的规则：
#     - 每次只能提出一个‘是/不是’的问题。不要一次提多个问题。
#     - 当你认为你知道这个物品是什么时，请直接说出：‘这个词是___’。
#     - 只有当对方说“恭喜你猜对了！”，才说明你猜对了。
#     - 如果你的问题是“是/不是”类型，对方只回答“是”或“不是”或“有”或“没有”。
#     - 如果你说出的词是目标词的父类型，对方会回答：“是这个类型，但是词不对”
#     """
# )

if __name__ == '__main__':
    # 发起对话
    chat_results = autogen.initiate_chats(
        [
            {
                "sender": guesser,
                "recipient": responder,
                "message": "请问这是一个生活用品吗？",
                "carryover": "你需要根据过去问的问题及答案，询问一个新的问题，这个新的问题需要有助于你最终猜到物品。",
            }
        ]
    )