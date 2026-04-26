#!/usr/bin/env python
# coding=utf-8
import os

import numpy as np
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from openai import OpenAI
from volcenginesdkarkruntime import Ark

from util import *


def testCOT(llm: ChatOpenAI):
    question = """Q: Roger has 5 tennis balls. He buys 2 more cans of
tennis balls. Each can has 3 tennis balls. How many
tennis balls does he have now?
A: The answer is 11.
Q: The cafeteria had 23 apples. If they used 20 to
make lunch and bought 6 more, how many apples
do they have?"""
    print('-'*32 + ' not cot ' + '-'*32)
    print(invokeLLM(llm, question))

    question = """"Q: Roger has 5 tennis balls. He buys 2 more cans of
tennis balls. Each can has 3 tennis balls. How many
tennis balls does he have now?
A: Roger started with 5 balls. 2 cans of 3 tennis balls
each is 6 tennis balls. 5 + 6 = 11. The answer is 11.
Q: The cafeteria had 23 apples. If they used 20 to
make lunch and bought 6 more, how many apples
do they have?"""
    print('-'*32 + ' cot ' + '-'*32)
    print(invokeLLM(llm, question))

    question = """Mary’s father has five daughters: Nana, Nene, Nini, Nono. What is the name of the fifth daughter?"""
    print('-'*32 + ' not cot ' + '-'*32)
    print(invokeLLM(llm, question))

    question += "\n" + "Let's think step by step."
    print('-'*32 + ' cot ' + '-'*32)
    print(invokeLLM(llm, question))

    question = """Mike plays ping pong for 40 minutes. In the first 20 minutes, he scores 4 points. In the second 20 minutes, he scores 25% more points. How many total points did he score?"""
    print('-'*32 + ' not cot ' + '-'*32)
    print(invokeLLM(llm, question))


if __name__ == "__main__":
    print('Using getDoubaoSeed16')
    testCOT(getDoubaoSeed16())

    print('Using Doubao15VisionLite')
    testCOT(getDoubao15VisionLite())

    print('Using getDeepSeekR1')
    testCOT(getDeepSeekR1())
