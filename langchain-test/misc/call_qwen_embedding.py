#!/usr/bin/env python
# coding=utf-8


import dashscope
from http import HTTPStatus

resp = dashscope.TextEmbedding.call(
    model="text-embedding-v4",
    input='衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买',
    dimension=1024,  # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
    output_type="dense&sparse"
)

print(resp) if resp.status_code == HTTPStatus.OK else print(resp)

import dashscope
from http import HTTPStatus

resp = dashscope.TextEmbedding.call(
    model="text-embedding-v4",
    input='衣服的质量杠杠的，很漂亮，不枉我等了这么久啊，喜欢，以后还来这里买',
    dimension=1024,  # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
    output_type="dense&sparse"
)

print(resp) if resp.status_code == HTTPStatus.OK else print(resp)