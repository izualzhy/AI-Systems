#!/usr/bin/env python
# coding=utf-8

# 设置OpenAI API密钥
import os
import sys

from misc import getDoubaoSeed16, getDeepSeekV3

# 导入所需的库
from typing import List
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

session_record_file = open("./camel_session_record.txt", "a")

# 定义CAMELAgent类
class CAMELAgent:
    def __init__(
        self,
        system_message: SystemMessage,
        model: ChatOpenAI,
    ) -> None:
        self.system_message = system_message
        self.model = model
        self.init_messages()
    def reset(self) -> None:
        """重置对话消息"""
        self.init_messages()
        return self.stored_messages
    def init_messages(self) -> None:
        """初始化对话消息"""
        self.stored_messages = [self.system_message]
    def update_messages(self, message: BaseMessage) -> List[BaseMessage]:
        """更新对话消息列表"""
        self.stored_messages.append(message)
        return self.stored_messages
    def step(self, input_message: HumanMessage) -> AIMessage:
        """与大模型进行交互"""
        messages = self.update_messages(input_message)
        print("*" * 50 + " step " + "*" * 50, file = session_record_file)
        print(f"* input_message:{input_message}", file = session_record_file)
        print(f"* messages:{messages}", file = session_record_file)
        print(f"* stored_messages:{self.stored_messages}", file = session_record_file)
        output_message = self.model(messages)
        self.update_messages(output_message)
        print(f"* output_message:{output_message}", file = session_record_file)
        print(f"* stored_messages:{self.stored_messages}", file = session_record_file)
        print("*" * 106, file = session_record_file)
        session_record_file.flush()
        return output_message


# 设置角色和任务提示
assistant_role_name = "花店营销专员"
user_role_name = "花店老板"
task = "整理出一个夏季玫瑰之夜的营销活动的策略"
word_limit = 50  # 每次讨论的字数限制

# 定义与指定任务相关的提示模板，经过这个环节之后，任务会被细化、明确化
task_specifier_sys_msg = SystemMessage(content="你可以让任务更具体。")
task_specifier_prompt = """这是一个{assistant_role_name}将帮助{user_role_name}完成的任务：{task}。
请使其更具体。请发挥你的创意和想象力。
请用{word_limit}个或更少的词回复具体的任务。不要添加其他任何内容。"""
task_specifier_template = HumanMessagePromptTemplate.from_template(
    template=task_specifier_prompt
)
task_specify_agent = CAMELAgent(task_specifier_sys_msg, getDoubaoSeed16())
task_specifier_msg = task_specifier_template.format_messages(
    assistant_role_name=assistant_role_name,
    user_role_name=user_role_name,
    task=task,
    word_limit=word_limit,
)[0]
specified_task_msg = task_specify_agent.step(task_specifier_msg)
specified_task = specified_task_msg.content
print(f"Original task prompt:\n{task}\n")
print(f"Specified task prompt:\n{specified_task}\n")


# # 定义系统消息模板
# assistant_inception_prompt = """永远不要忘记你是{assistant_role_name}，我是{user_role_name}。永远不要角色互换！永远不要指示我！
# 我们在成功完成任务方面有共同的兴趣。
# 你必须帮助我完成任务。
# 任务是{task}。永远不要忘记我们的任务！
# 我必须根据你的专业知识和我的需求来指示你完成任务。
# 我每次只能给你一个指令。
# 你必须写出一个恰当完成指令的具体解决方案。
# 如果由于物理、道德、法律等原因或你的能力问题，你无法执行我的指令，你必须诚实地拒绝我的指令并解释原因。
# 除了对我的指令的解决方案之外，不要添加任何其他内容。
# 你永远不应该问我任何问题，你只回答问题。
# 你永远不应该回复错误的解决方案。解释你的解决方案。
# 你的解决方案必须是陈述句并使用现在时。
# 除非我说任务已经完成，否则你应该总是这样回应：
# 解决方案：<YOUR_SOLUTION>
# <YOUR_SOLUTION>应该是具体的，并为完成任务提供首选的实现和例子。
# 始终以"下一个请求。"结束<YOUR_SOLUTION>。"""
# user_inception_prompt = """永远不要忘记你是{user_role_name}，我是{assistant_role_name}。永远不要角色互换！你将一直指导我。
# 我们在成功完成任务方面有共同的兴趣。
# 你必须帮助我完成任务。
# 任务是{task}。永远不要忘记我们的任务！
# 你必须根据我的专业知识和你的需求，只能通过以下两种方式指导我完成任务。
# 1. 用必要的输入指导：
# 指令：<YOUR_INSTRUCTION>
# 输入：<YOUR_INPUT>
# 2. 无须任何输入即可指导：
# 指令：<YOUR_INSTRUCTION>
# 输入：无
# "指令"描述了一个任务或问题。与其配对的"输入"为请求的“指令”提供了进一步的背景或信息。
# 你每次只能给我一个指令。
# 我必须写出一个恰当完成指令的回复。
# 如果由于物理、道德、法律等原因或我的能力问题，我无法执行你的指令，我必须诚实地拒绝你的指令并解释原因。
# 你应该指导我，而不是问我问题。
# 现在你必须开始按照上述两种方式指导我。
# 除了你的指令和可选的相应输入之外，不要添加任何其他内容！
# 继续给我指令和必要的输入，直到你认为任务已经完成。
# 当任务完成时，你只须回复一个单词<CAMEL_TASK_DONE>。
# 除非我的回答能使你完成你的任务，否则永远不要说<CAMEL_TASK_DONE>。"""

assistant_inception_prompt = """你是 {assistant_role_name}，我是 {user_role_name}。我们各自扮演固定角色，不得互换。

我们在完成以下任务方面有共同目标：
任务是：{task}。

你必须始终根据我的指令提供帮助，且每次仅回应一个具体、可行的解决方案。必须符合以下要求：

1. 不得反过来指示我；
2. 不得提出任何问题；
3. 不得提供与指令无关的内容；
4. 不得生成错误或无法执行的方案，如遇物理、道德、法律或能力限制，应明确拒绝并解释原因；
5. 必须给出回复
6. 回复必须使用陈述句和现在时态；
7. 回复结构必须如下：

解决方案：<YOUR_SOLUTION>  
<YOUR_SOLUTION> 应该是具体实现，包含推荐方法与例子。  
始终以 “下一个请求。” 结尾。

除非我明确告知任务已完成，你始终应按上述格式回应。
"""

user_inception_prompt = """你是 {user_role_name}，我是 {assistant_role_name}。我们各自扮演固定角色，不得互换。

我们在完成以下任务方面有共同目标：
任务是：{task}。

你将持续指导我完成任务，每次只能给出一个指令。必须使用以下格式之一：

1. **需要输入时：**  
指令：<YOUR_INSTRUCTION>  
输入：<YOUR_INPUT>

2. **无需输入时：**  
指令：<YOUR_INSTRUCTION>  
输入：无

说明：
- 指令是你给我的任务或问题；
- 输入为该指令提供必要的背景信息；
- 除指令与输入外，不应包含其他内容；
- 你不得向我提问，只能指导我；
- 我将根据指令提供回应，若因物理、道德、法律或能力限制无法完成，将如实说明并拒绝。

你应持续指导，直到认为任务完成。此时只回复一个词：

<CAMEL_TASK_DONE>

除非我的回应已经达成你的任务目标，否则不要提前结束。
"""
# 根据设置的角色和任务提示生成系统消息
def get_sys_msgs(assistant_role_name: str, user_role_name: str, task: str):
    assistant_sys_template = SystemMessagePromptTemplate.from_template(
        template=assistant_inception_prompt
    )
    assistant_sys_msg = assistant_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]
    user_sys_template = SystemMessagePromptTemplate.from_template(
        template=user_inception_prompt
    )
    user_sys_msg = user_sys_template.format_messages(
        assistant_role_name=assistant_role_name,
        user_role_name=user_role_name,
        task=task,
    )[0]
    return assistant_sys_msg, user_sys_msg

assistant_sys_msg, user_sys_msg = get_sys_msgs(
    assistant_role_name, user_role_name, specified_task
)
print(f"assistant_sys_msg:\n{assistant_sys_msg}")
print(f"user_sys_msg:\n{user_sys_msg}")
# 创建助手和用户的CAMELAgent实例
# assistant_agent = CAMELAgent(assistant_sys_msg, getDoubaoSeed16())
# user_agent = CAMELAgent(user_sys_msg, getDoubaoSeed16())
assistant_agent = CAMELAgent(assistant_sys_msg, getDeepSeekV3())
user_agent = CAMELAgent(user_sys_msg, getDeepSeekV3())

# 重置两个agent
assistant_agent.reset()
user_agent.reset()

# 初始化对话互动
assistant_msg = HumanMessage(
    content=(
        f"{user_sys_msg.content}。"
        "现在开始逐一给我介绍。"
        "只回复指令和输入。"
    )
)

user_msg = HumanMessage(content=f"{assistant_sys_msg.content}")
user_msg = assistant_agent.step(user_msg)

# 模拟对话交互，直到达到对话轮次上限或任务完成
chat_turn_limit, n = 30, 0
while n < chat_turn_limit:
    n += 1
    user_ai_msg = user_agent.step(assistant_msg)
    user_msg = HumanMessage(content=user_ai_msg.content)
    print(f"AI User ({user_role_name}):\n\n{user_msg.content}\n\n")

    assistant_ai_msg = assistant_agent.step(user_msg)
    assistant_msg = HumanMessage(content=assistant_ai_msg.content)
    print(f"AI Assistant ({assistant_role_name}):\n\n{assistant_msg.content}\n\n")
    if "<CAMEL_TASK_DONE>" in user_msg.content:
        print(f"{n}/{chat_turn_limit} 任务完成！")
        break