#!/usr/bin/env python
# coding=utf-8
# https://python.langchain.com/docs/tutorials/extraction/

from typing import Optional, List

from pydantic import BaseModel, Field

from util import getDoubaoSeed16


class Person(BaseModel):
    """Information about a person."""

    # ^ Doc-string for the entity Person.
    # This doc-string is sent to the LLM as the description of the schema Person,
    # and it can help to improve extraction results.

    # Note that:
    # 1. Each field is an `optional` -- this allows the model to decline to extract it!
    # 2. Each field has a `description` -- this description is used by the LLM.
    # Having a good description can help improve extraction results.
    name: Optional[str] = Field(default=None, description="The name of the person")
    hair_color: Optional[str] = Field(
        default=None, description="The color of the person's hair if known"
    )
    height_in_meters: Optional[str] = Field(
        default=None, description="Height measured in meters"
    )

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Define a custom prompt to provide instructions and any additional context.
# 1) You can add examples into the prompt template to improve extraction quality
# 2) Introduce additional parameters to take context into account (e.g., include metadata
#    about the document from which the text was extracted.)
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert extraction algorithm. "
            "Only extract relevant information from the text. "
            "If you do not know the value of an attribute asked to extract, "
            "return null for the attribute's value.",
        ),
        # Please see the how-to about improving performance with
        # reference examples.
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)

llm = getDoubaoSeed16()

structured_llm = llm.with_structured_output(schema=Person)

text = "Alan Smith is 6 feet tall and has blond hair."
prompt = prompt_template.invoke({"text": text})
# 官网返回的结果，不同大模型还是结果差异大，豆包就没有计算出height_in_meters
# Person(name='Alan Smith', hair_color='blond', height_in_meters='1.83')
print(structured_llm.invoke(prompt))

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "你是一个专业的信息抽取算法。"
            "仅从文本中提取相关信息。"
            "如果你不知道被要求提取的某个属性的值，"
            "请将该属性的值设为null。"
        ),
        # 请参考关于如何通过参考示例提高性能的指南。
        # MessagesPlaceholder('examples'),
        ("human", "{text}"),
    ]
)
text = "邹忌修八尺有余而形貌昳丽，发乌如漆，间有星霜"
prompt = prompt_template.invoke({"text": text})
# 豆包的遵从性还是一般，height_in_meters 有时有有时没有
# name='邹忌' hair_color='black with some gray' height_in_meters='more than 1.848 meters'
print(structured_llm.invoke(prompt))


class Data(BaseModel):
    """Extracted data about people."""

    # Creates a model so that we can extract multiple entities.
    people: List[Person]

structured_llm = llm.with_structured_output(schema=Data)
text = "My name is Jeff, my hair is black and i am 6 feet tall. Anna has the same color hair as me."
prompt = prompt_template.invoke({"text": text})
print(structured_llm.invoke(prompt))

messages = [
    {"role": "user", "content": "2 🦜 2"},
    {"role": "assistant", "content": "4"},
    {"role": "user", "content": "2 🦜 3"},
    {"role": "assistant", "content": "5"},
    {"role": "user", "content": "3 🦜 4"},
]

response = llm.invoke(messages)
print(response.content)

from langchain_core.utils.function_calling import tool_example_to_messages

examples = [
    (
        "The ocean is vast and blue. It's more than 20,000 feet deep.",
        Data(people=[]),
    ),
    (
        "Fiona traveled far from France to Spain.",
        Data(people=[Person(name="Fiona", height_in_meters=None, hair_color=None)]),
    ),
]


messages = []

for txt, tool_call in examples:
    if tool_call.people:
        # This final message is optional for some providers
        ai_response = "Detected people."
    else:
        ai_response = "Detected no people."
    messages.extend(tool_example_to_messages(txt, [tool_call], ai_response=ai_response))

for message in messages:
    message.pretty_print()

message_no_extraction = {
    "role": "user",
    "content": "The solar system is large, but earth has only 1 moon.",
}

structured_llm = llm.with_structured_output(schema=Data)
print(structured_llm.invoke([message_no_extraction]))


print(structured_llm.invoke(messages + [message_no_extraction]))