#!/usr/bin/env python
# coding=utf-8
import os

import litellm

query = input("请输入你的问题：")
response = litellm.completion(
    model=os.environ.get('ARK_DS32_WITH_PROVIDER'),
    api_base=os.environ.get('ARK_API_URL'),
    api_key=os.environ.get('ARK_API_KEY'),
    messages=[{"role": "user", "content": "Hello"}]
)

print(response)