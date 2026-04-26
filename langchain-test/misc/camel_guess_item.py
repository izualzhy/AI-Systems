#!/usr/bin/env python
# coding=utf-8
from langchain_core.messages import SystemMessage

from util import ARK_API_URL, getDoubaoSeed16, DOUBAO_SEED_1_6

import os

from camel.societies import RolePlaying
from camel.models import ModelFactory
from camel.configs import ChatGPTConfig
from camel.types import ModelPlatformType, ModelType, TaskType

# 创建模型对象
doubao_config = ChatGPTConfig(
    temperature=0.0,
    top_p=None,
    max_tokens=None,
    stream=False,
    stop=None,
)
model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI_COMPATIBLE_MODEL,
    model_type=DOUBAO_SEED_1_6,
    model_config_dict=doubao_config.as_dict(),
    url=ARK_API_URL,
    api_key=os.environ["ARK_API_KEY"]
)

# 设置要猜的中文物品词语
target_word = "袋鼠"
role_a = "猜词者"
role_b = "回答者"

task_prompt = f"""
你将参与一个猜词游戏，游戏中有两个角色：{role_a} 和 {role_b}。{role_b} 负责选定一个词，{role_a} 要通过询问物品特征的问题来猜出这个词。
以下是选定的目标物品： <target_word>{target_word}</target_word>
以下是两个角色的具体要求：
<role_a>
你将参与一个猜物品名字的游戏。你不知道物品是什么，需要通过不断提出‘是/不是’的问题来逐步猜出这个物品。
以下是游戏的规则：
- 每次只能提出一个‘是/不是’的问题。不要一次提多个问题。
- 当你认为你知道这个物品是什么时，请直接说出：‘这个词是___’。
- 只有当对方说“恭喜你猜对了！”，才说明你猜对了。
- 如果你的问题是“是/不是”类型，对方只回答“是”或“不是”或“有”或“没有”。
- 如果你说出的词是目标词的父类型，对方会回答：“是这个类型，但是词不对”
</role_a>
<role_b>
你正在参与一个猜物品名字的游戏，注意物品名字可能细化到品牌、分类等。你的任务是根据对方提出的“是/不是”问题，以特定方式回应，帮助对方猜出目标物品。
目标词是： {target_word}
对方会通过问“是/不是”问题来尝试猜出这个词。你只能按照以下规则回答：
- 如果对方的问题是“是/不是”类型，你只能回答“是”或“不是”或“有”或“没有”。
- 如果对方说出的词就是目标词，你要回答：“恭喜你猜对了！”
- 如果对方说出的词是目标词的父类型，你需要回答：“是这个类型，但是词不对”
- 除此之外不能泄露任何信息。
</role_b>
请 {role_a} {role_b} 都是用中文对话。

现在游戏从{role_a}提问开始。
"""

role_play = RolePlaying(
    assistant_role_name=role_a,
    assistant_agent_kwargs=dict(model=model),
    user_role_name=role_b,
    user_agent_kwargs=dict(model=model),
    task_prompt=task_prompt,
    with_task_specify=False,
    task_type=TaskType.ROLE_DESCRIPTION,
)


# 初始化聊天
init_msg = role_play.init_chat()
print(f"init_msg: {init_msg}")

assistant_msg = init_msg  # first goes to assistant as input
assistant_response, user_response = role_play.step(assistant_msg)
for step in range(20):
    assistant_response, user_response = role_play.step(assistant_msg)

    print(f"\n【第 {step+1} 轮】")
    print("猜词者问：", assistant_msg.content.strip())
    print("猜词者答：", assistant_response.msg.content.strip())
    print("回答者答：", user_response.msg.content.strip())

    # 如果猜中（中文判断）
    if "恭喜你猜对了" in user_response.msg.content:
        print("🎉 游戏结束，猜词成功！")
        break

    assistant_msg = assistant_response.msg