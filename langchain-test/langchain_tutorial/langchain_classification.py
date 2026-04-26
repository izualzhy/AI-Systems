#!/usr/bin/env python
# coding=utf-8

# https://python.langchain.com/docs/tutorials/classification/

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from util import getDoubaoSeed16


def v1():
    tagging_prompt = ChatPromptTemplate.from_template(
        """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    )


    class Classification(BaseModel):
        sentiment: str = Field(description="The sentiment of the text")
        aggressiveness: int = Field(
            description="How aggressive the text is on a scale from 1 to 10"
        )
        language: str = Field(description="The language the text is written in")

    llm = getDoubaoSeed16()
    # Structured LLM
    structured_llm = llm.with_structured_output(Classification)


    inp = "我非常高兴认识你！我相信我们会成为非常好的朋友！"
    prompt = tagging_prompt.invoke({"input": inp})
    response = structured_llm.invoke(prompt)

    print(response)
    print(response.model_dump())

    inp = "我对你非常生气！我会让你得到应有的惩罚！"
    prompt = tagging_prompt.invoke({"input": inp})
    response = structured_llm.invoke(prompt)

    print(response)
    print(response.model_dump())


def finerControl():
    class Classification(BaseModel):
        sentiment: str = Field(..., enum=["happy", "neutral", "sad", "angry"])
        aggressiveness: int = Field(
            ...,
            description="describes how aggressive the statement is, the higher the number the more aggressive",
            enum=[1, 2, 3, 4, 5],
        )
        language: str = Field(
            ..., enum=["spanish", "english", "french", "german", "italian", "chinese"]
        )

    tagging_prompt = ChatPromptTemplate.from_template(
        """
    Extract the desired information from the following passage.

    Only extract the properties mentioned in the 'Classification' function.

    Passage:
    {input}
    """
    )

    llm = getDoubaoSeed16().with_structured_output(
        Classification
    )

    inp = "我非常高兴认识你！我相信我们会成为非常好的朋友！"
    prompt = tagging_prompt.invoke({"input": inp})
    print(llm.invoke(prompt))

    inp = "我对你非常生气！我会让你得到应有的惩罚！"
    prompt = tagging_prompt.invoke({"input": inp})
    print(llm.invoke(prompt))

    inp = "Weather is ok here, I can go outside without much more than a coat"
    prompt = tagging_prompt.invoke({"input": inp})
    print(llm.invoke(prompt))


if __name__ == "__main__":
    # v1()
    finerControl()
