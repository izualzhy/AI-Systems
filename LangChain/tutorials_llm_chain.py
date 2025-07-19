#!/usr/bin/env python
# coding=utf-8

# https://python.langchain.com/docs/tutorials/llm_chain/

from langchain_core.messages import HumanMessage, SystemMessage

from util import getDoubaoSeed16ChatModel

messages = [
    SystemMessage("Translate the following from English into Chinese"),
    HumanMessage("This is the way to learn LangChain."),
]


model = getDoubaoSeed16ChatModel()

print("model.invoke(messages)")
print(model.invoke(messages))

print("model.stream")
for token in model.stream(messages):
    print(token.content, end="|")
print("")

from langchain_core.prompts import ChatPromptTemplate

system_template = "Translate the following from English into {language}"

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template), ("user", "{text}")]
)

prompt = prompt_template.invoke({"language": "Chinese", "text": "To be or not to be, that's a question"})

print("prompt")
print(prompt)
print("prompt.to_messages()")
print(prompt.to_messages())
print("prompt.to_json()")
print(prompt.to_json())

print("model.invoke(prompt)")
print(model.invoke(prompt))

