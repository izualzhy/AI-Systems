#!/usr/bin/env python
# coding=utf-8


import shelve

# 注意：路径不带 .db 后缀（shelve 会自动处理扩展名）
with shelve.open('celerybeat-schedule', flag='r') as db:
    for key in db:
        print(f"Key: {key}")
        print(f"Value type: {type(db[key])}")
        print(f"Value: {db[key]}\n")