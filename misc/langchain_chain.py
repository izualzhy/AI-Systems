#!/usr/bin/env python
# coding=utf-8
from langchain.chains.llm import LLMChain
from langchain.chains.sequential import SequentialChain
from langchain_core.prompts import PromptTemplate

from util import getDoubaoSeed16

if __name__ == '__main__':
    llm = getDoubaoSeed16()

    prompt_1 = PromptTemplate(
        input_variables=["question"],
        template="解答问题: {question}"
    )
    prompt_2 = PromptTemplate(
        input_variables=["answer"],
        template="基于答案：{answer}，生成50字以内的描述"
    )

    chain1 = LLMChain(llm=llm, prompt=prompt_1, output_key="answer")
    chain2 = LLMChain(llm=llm, prompt=prompt_2, output_key="simple_answer")

    sequential_chain = SequentialChain(
        chains=[chain1, chain2],
        input_variables=["question"],
        output_variables=["answer", "simple_answer"],
        verbose=True
    )

    response = sequential_chain.invoke({"question": "如何搭建智能体构建平台"})
    print(response)