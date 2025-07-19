#!/usr/bin/env python
# coding=utf-8


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

from misc import getDoubaoSeed16, getDoubao15VisionLite, getDoubao15VisionPro

llm = getDoubao15VisionPro(temperature=0)

# question = """汤姆有 3 盒糖果，每盒有 5 颗，他又买了 7 颗。他现在总共有多少颗糖果？"""
# question = """Tom has 3 boxes of candy, each containing 5 pieces. He bought 7 more pieces. How many pieces does he have now?"""
# question = """Alice has twice as many apples as Bob. Bob has 3 more apples than Carol. If Carol has 5 apples, how many apples does Alice have?"""
question = "Mary’s father has five daughters: Nana, Nene, Nini, Nono. What is the name of the fifth daughter?"
prompt = HumanMessage(content=question)
response = llm([prompt])
print(response.content)

print("------ Let's think step by step. ------")
prompt = HumanMessage(content=(question + "\n" + "Let's think step by step."))
response = llm([prompt])
print(response.content)
