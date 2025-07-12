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
    api_key=os.environ["ARK_API_KEY"]                   # 若 ModelFactory 用到 api_key 参数
)

# 设置要猜的中文物品词语
target_item = "袋鼠"
role_a = "猜词者"
role_b = "回答者"

task_prompt = f"""
你将参与一个猜词游戏，游戏中有两个角色：{role_a} 和 {role_b}。{role_b} 负责选定一个词，{role_a} 要通过询问物品特征的问题来猜出这个词。
以下是选定的目标物品： <target_item>{target_item}</target_item>
以下是两个角色的具体要求：
<role_a>
你不知道目标物品是什么，只能通过问一些物品特征的问题来逐步猜测。每次只能问一个问题，根据 {role_b} 的回答，不断缩小范围进一步猜测。当你知道这个词是什么时，请直接说出：‘这个词是___’，然后结束会话。
</role_a>
<role_b>
如果你准确说出了词语，请回答‘恭喜你猜对了！’。否则，只回答‘是’或‘不是’，不能提供任何额外信息。
</role_b>
现在游戏开始，{role_a} 请开始提问，{role_b} 已选好物品，请准备回答问题。
"""

# 然后传入 RolePlaying 的对应参数 assistant_sys_msg, user_sys_msg，千万不要放到 agent_kwargs 中
role_play = RolePlaying(
    assistant_role_name=role_a,
    assistant_agent_kwargs=dict(model=model),
    user_role_name=role_b,
    user_agent_kwargs=dict(model=model),
    task_prompt=task_prompt,
    with_task_specify=False
)


# 初始化聊天
init_msg = role_play.init_chat()

assistant_msg = init_msg  # first goes to assistant as input
for step in range(20):
    assistant_response, user_response = role_play.step(assistant_msg)

    print(f"\n【第 {step+1} 轮】")
    print("猜词者问：", assistant_response.msg.content.strip())
    print("回答者答：", user_response.msg.content.strip())

    # 如果猜中（中文判断）
    if "恭喜你猜对了" in user_response.msg.content:
        print("🎉 游戏结束，猜词成功！")
        break

    assistant_msg = assistant_response.msg