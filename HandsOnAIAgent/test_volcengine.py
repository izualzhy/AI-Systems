#!/usr/bin/env python
# coding=utf-8


import os

from misc import getArkClient

print(os.environ.get("OPENAI_API_KEY"))
print(os.environ.get("ARK_API_KEY"))

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = getArkClient()

response = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="ep-20250612180931-z9sd6",
    messages=[
        {
            "role": "user",
            "content": [
                # {
                #     "type": "image_url",
                #     "image_url": {
                #         "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                #     },
                # },
                {"type": "text", "text": "今天是哪天?"},
            ],
        }
    ],
)
print(response)
print(response.choices[0])