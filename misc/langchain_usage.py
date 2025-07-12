#!/usr/bin/env python
# coding=utf-8
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence, RunnableLambda

from util import getDoubaoSeed16


def test():
    llm = getDoubaoSeed16()

    prompt_1 = PromptTemplate(
        input_variables=["question"],
        template="解答问题: {question}"
    )
    prompt_2 = PromptTemplate(
        input_variables=["answer"],
        template="基于答案：{answer}，生成50字以内的描述"
    )

    def debug_input(x):
        print(f"[DEBUG] prompt_2 received: {x}")
        return x
        # return {"answer": x}

    chain = (prompt_1 | llm
             | RunnableLambda(debug_input)
             # | RunnableLambda(lambda output: {"answer": output})
             | prompt_2 | llm)

    response = chain.invoke({"question": "如何搭建智能体构建平台"})
    print(response)


if __name__ == "__main__":
    test()