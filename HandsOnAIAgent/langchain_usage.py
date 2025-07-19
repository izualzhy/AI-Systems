#!/usr/bin/env python
# coding=utf-8


# 导入所需的库
from langchain_core.output_parsers import StrOutputParser # 用于将输出结果解析为字符串
from langchain_core.prompts import ChatPromptTemplate # 用于创建聊天提示模板

from constants import DOUBAO_SEED_1_6_THINKING
from misc import getDoubaoSeed16Thinking

# 创建一个聊天提示模板，其中{topic}是占位符，用于后续插入具体的话题
prompt = ChatPromptTemplate.from_template("请讲一个关于 {topic} 的故事")
# 初始化ChatOpenAI对象，指定使用的模型为“gpt-4”
model = getDoubaoSeed16Thinking()

# 初始化一个输出解析器，用于将模型的输出解析成字符串
output_parser = StrOutputParser()
'''通过管道操作符(|)连接各个处理步骤，以创建一个处理链
   其中，prompt用于生成具体的提示文本，model用于根据提示文本生成回应，output_parser用于处理回应并将其转换为字符串'''
chain = prompt | model | output_parser
# 调用处理链，传入话题“互联网员工跳槽到国企”，执行生成故事的操作
message = chain.invoke({"topic": "互联网员工跳槽到国企"})
# 打印链的输出结果
print(message)