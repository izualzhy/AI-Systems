#!/usr/bin/env python
#coding=utf-8


import time
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Milvus, FAISS

from utils.doubao_embedding import DoubaoEmbedding
from utils.util import getDeepSeekV31

# ========= 1️⃣ 购物记忆提炼 Prompt =========
EXTRACT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
你是一个购物记忆提炼助手。
请仅根据用户在对话中【明确表达或确认】的购物相关信息，

### 提取记忆的原则：
1. **只关注购物相关内容**：提取商品偏好、购买意向、品牌喜好、价格敏感度、购物习惯、尺寸尺码、颜色偏好等与购物直接相关的信息。
2. **忽略无关内容**：直接忽略和购物无关的内容，例如闲聊、天气、问候、非购物类计划等。
3. **简洁且信息丰富**：确保每条记忆都简短而富有信息量。
4. **整合事件**：将相关的购物行为整合成一条记忆，避免创建过多行的记忆。例如，"在某月某日购买了某品牌的某商品，价格为XX元"。
5. **直接表述**：避免冗余的前缀，如"这个人喜欢耐克"。而是直接表述为"喜欢耐克品牌"。
6. **具体细节**：保留关键细节如品牌、型号、价格区间、尺寸、颜色等。
不要提炼任何由助手假设、推测、安慰或鼓励性语言产生的内容。

输出严格遵循 JSON 数组格式，不添加解释性文字。
如果没有可提炼内容，请输出空数组 []。

每个对象包含以下字段：
- content: 提炼的内容（不超过150字）
- tag: 分类，必须严格从以下四类中选择一个：
  「商品偏好」「购买意向」「品牌喜好」「购物习惯」
- source: 来源（user 或 assistant）
- confidence: 置信度
  - high：用户明确表达或确认的事实。
  - medium：用户暗示、模糊或助手提及但用户未否认的内容。
"""),
    ("user", "用户: {user_input}\n助手: {assistant_reply}")
])


# ========= 2️⃣ 购物回复生成 Prompt =========
REPLY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """
你是一个智能购物助手，请基于以下购物记忆片段和用户输入生成自然回复。
记忆片段中包含了用户的商品偏好、品牌喜好、购买意向或购物习惯。
如果记忆为空，也要尽量礼貌回应。

输出时保持自然，不引用记忆的字段名或格式。
可以根据用户的购物偏好提供个性化建议。
"""),
    ("user", "记忆片段:\n{memory_context}\n\n用户: {user_input}")
])

# ========= 3️⃣ 记忆存储封装 =========
class MemoryStore:
    def __init__(self, mode="memory", milvus_host="localhost", milvus_port="19530"):
        self.embedding = DoubaoEmbedding()
        self.mode = mode

        if mode == "milvus":
            print("[MemoryStore] Using Milvus vector store.")
            self.store = Milvus(
                embedding_function=self.embedding,
                collection_name="memory_fragments",
                connection_args={"host": milvus_host, "port": milvus_port},
            )
        else:
            print("[MemoryStore] Using in-memory FAISS store.")
            self.store = FAISS.from_texts(["init doc"], self.embedding)

        self.confidence_weight = {"high": 1.0, "medium": 0.6, "low": 0.3}

    def add_fragments(self, fragments: List[Dict]):
        docs, metas = [], []
        for frag in fragments:
            text = f"[{frag['confidence']}] {frag['content']}"
            meta = {
                "tag": frag["tag"],
                "source": frag["source"],
                "confidence": frag["confidence"],
                "weight": self.confidence_weight.get(frag["confidence"], 0.5),
                "timestamp": time.time()
            }
            docs.append(text)
            metas.append(meta)

        if isinstance(self.store, Milvus):
            self.store.add_texts(docs, metadatas=metas)
        else:
            for d, m in zip(docs, metas):
                self.store.add_texts([d], metadatas=[m])

    def query(self, query_text, top_k=10, final_k=5):
        results = self.store.similarity_search_with_score(query_text, k=top_k)

        def weighted_score(doc, score):
            w_conf = doc.metadata.get("weight", 1.0)
            recency = 1.0 / (1.0 + (time.time() - doc.metadata.get("timestamp", time.time())) / 86400 / 30)
            return score * w_conf * recency

        reranked = sorted(results, key=lambda x: weighted_score(x[0], x[1]), reverse=True)
        return reranked[:final_k]

# ========= 4️⃣ 统一的智能体类 =========
class MemoryAgent:
    def __init__(self, memory_mode="memory"):
        self.llm = getDeepSeekV31()
        self.memory_store = MemoryStore(mode=memory_mode)

    # 生成助手回复
    def generate_reply(self, user_input: str) -> str:
        # 检索记忆
        results = self.memory_store.query(user_input)
        memory_context = "\n".join([r[0].page_content for r in results]) or "（暂无记忆）"

        prompt = REPLY_PROMPT.format_messages(
            memory_context=memory_context,
            user_input=user_input
        )
        print(f"[MemoryAgent] Prompt: {prompt}")
        resp = self.llm.invoke(prompt)
        print(f"[MemoryAgent] Response: {resp}")
        return resp.content.strip()

    # 提炼记忆并保存
    def extract_and_store_memory(self, user_input: str, assistant_reply: str):
        prompt = EXTRACT_PROMPT.format_messages(
            user_input=user_input,
            assistant_reply=assistant_reply
        )
        resp = self.llm.invoke(prompt)
        try:
            fragments = eval(resp.content)
            assert isinstance(fragments, list)
            if fragments:
                self.memory_store.add_fragments(fragments)
            return fragments
        except Exception:
            return []

    # 完整一轮对话：生成 + 提炼
    def chat(self, user_input: str):
        reply = self.generate_reply(user_input)
        fragments = self.extract_and_store_memory(user_input, reply)
        return reply, fragments


# ========= 5️⃣ 示例运行 =========
if __name__ == "__main__":
    agent = MemoryAgent(memory_mode="memory")  # 改为 "milvus" 即切换生产模式

    # 模拟多轮购物对话
    user_inputs = [
        "我喜欢买耐克的运动鞋，一般穿42码。",
        "今天天气真好",
        "我想买个蓝牙耳机，预算在500元左右。",
        "之前买的阿迪达斯外套质量不错，还想再买一件。",
        "我不太喜欢网购，更喜欢去实体店试穿后再买。",
    ]

    for u in user_inputs:
        reply, fragments = agent.chat(u)
        print(f"\n🧍 用户: {u}")
        print(f"🤖 助手: {reply}")
        print(f"🧩 记忆提炼: {fragments}")
        input("Press Enter to continue...")

    # 测试召回
    print("\n=== 查询: 我的购物偏好 ===")
    results = agent.memory_store.query("购物偏好")
    for doc, score in results:
        print(f"- {doc.page_content} | {doc.metadata} | {score:.3f}")
