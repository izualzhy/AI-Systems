#!/usr/bin/env python
# coding=utf-8
import os
import random
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import chromadb
# from neo4j import GraphDatabase

from mem0 import Memory

from misc.util import DEEPSEEK_V32

#mem0 configuration

VOLCENGINE_API_KEY = os.environ.get("ARK_API_KEY")
VOLCENGINE_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 火山引擎 API 端点


custom_prompt = """
你是一个内容提炼助手，必须严格按以下规则提取用户信息：

输入内容中提取与用户相关的个性化信息，输出为 JSON 对象。

这个 JSON 对象应该有一个 key "facts"，其 value 是一个数组。数组中的每个元素都是一个字符串，格式为：**content=..., tag=...**。

值的解释：
- "content": 总结内容（不超过200字）
- "tag": 分类标签（仅限：画像信息、兴趣爱好、时间计划、特色经验）

要求：
1. 输出必须是**严格可解析的 JSON 对象，格式与上述输出要求一致**。
2. 不要包含任何额外文本、说明、前缀、后缀。
3. 不要使用代码块标记（如 ```json）。
4. 不要换行或缩进（使用紧凑 JSON）。
5. 如果无信息可提取，返回空的 JSON 对象 {}。

示例输入：我的名字叫izualzhy，今年15岁，喜欢喜欢代码，喜欢阅读。
示例输出：{"facts":["content=名字叫izualzhy, tag=画像信息","content=今年15岁, tag=画像信息","content=爱好是喜欢代码，喜欢阅读, tag=兴趣爱好"]}

"""

# mem0 配置：使用火山引擎，通过 OpenAI 兼容接口
config = {
    "version": "v1.1",
    # "custom_update_memory_prompt": custom_prompt,
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "test_mem0_20260315",  # 使用新的集合名，避免维度不匹配
            "path": "./memory/mem0/db",
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": VOLCENGINE_API_KEY,
            "model": DEEPSEEK_V32,
            "openai_base_url": VOLCENGINE_BASE_URL,
            # "temperature": 0.1,
            # "max_tokens": 2048,
            # "top_p": 1.0,
            # "top_k": 10,
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": os.environ.get("SILICON_API_KEY"),
            "model": os.environ.get("SILICON_BAAI_BGE_M3"),
            "openai_base_url": "https://api.siliconflow.cn/v1",
        }
    },
    "history_db_path": "./history.db",  # 修正路径
    "version": "v1.1",
    "user_email": "AA",
}

def test_mem0_opensource():
    mem_client = Memory.from_config(config)

    user_id = 'user_' + str(random.randint(1, 999999999))
    messages = [
        {"role": "assistant", "content": "你好呀！能先告诉我你叫什么名字吗？"},
        {"role": "user", "content": "我叫李明。今年30岁了。"},
        {"role": "assistant", "content": "很高兴认识你，李明！看您资料是来自北京对吧？为了能更好地为您服务，想了解一下您的饮食偏好，比如您吃辣吗？"},
        {"role": "user", "content": "是休闲旅游。我穿衣嘛，平时基本都穿黑色或灰色的衣服，比较喜欢简约休闲的风格，舒服最重要。"}
    ]
    result = mem_client.add(messages, user_id=user_id)
    print(f"1st result:\n {result}")

    messages = [
        {"role": "assistant", "content": "你好呀！能先告诉我你叫什么名字吗？"},
        {"role": "user", "content": "我叫白给。今年31岁了。"},
    ]
    result = mem_client.add(messages, user_id=user_id)
    print(f"2nd result:\n {result}")

    all_memories = mem_client.get_all(user_id=user_id)
    print(f"all_memories for {user_id}:\n {all_memories}")

    # results = mem_client.search("What do you know about me?", filters={"user_id": f"{user_id}"})
    results = mem_client.search("What do you know about me?", user_id=f"{user_id}")
    print(results)


def test_mem0_platform():
    from mem0 import MemoryClient
    mem0_api_key = os.environ.get('MEM0_API_KEY')
    print(f"mem0_api_key: {mem0_api_key}")

    client = MemoryClient(api_key=mem0_api_key)

    user_id = 'user_' + str(random.randint(1, 999999999))
    print(f"user_id: {user_id}")
    messages = [
        {"role": "assistant", "content": "你好呀！能先告诉我你叫什么名字吗？"},
        {"role": "user", "content": "我叫李明。今年30岁了。"},
        {"role": "assistant", "content": "很高兴认识你，李明！看您资料是来自北京对吧？为了能更好地为您服务，想了解一下您的饮食偏好，比如您吃辣吗？"},
        {"role": "user", "content": "是休闲旅游。我穿衣嘛，平时基本都穿黑色或灰色的衣服，比较喜欢简约休闲的风格，舒服最重要。"}
    ]
    result = client.add(messages, user_id=user_id)
    print(f"1st result:\n {result}")
    input("Press Enter to continue...")

    messages = [
        {"role": "assistant", "content": "你好呀！能先告诉我你叫什么名字吗？"},
        {"role": "user", "content": "我叫白给。今年31岁了。"},
    ]
    result = client.add(messages, user_id=user_id)
    print(f"2nd result:\n {result}")
    input("Press Enter to continue...")

    results = client.search("What do you know about me?", filters={"user_id": f"{user_id}"})
    # results = client.search("What do you know about me?", user_id=f"{user_id}")
    print(results)

if __name__ == "__main__":
    # test_mem0_opensource()
    test_mem0_platform()