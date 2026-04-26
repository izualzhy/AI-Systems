#!/usr/bin/env python
# coding=utf-8

# https://github.com/dorianbrown/rank_bm25

from rank_bm25 import BM25Okapi

corpus = [
    "Hello there good man!",
    "It is quite windy in London",
    "How is the weather today?"
]

tokenized_corpus = [doc.split(" ") for doc in corpus]

bm25 = BM25Okapi(tokenized_corpus)
# <rank_bm25.BM25Okapi at 0x1047881d0>
query = "windy London"
tokenized_query = query.split(" ")

doc_scores = bm25.get_scores(tokenized_query)
# array([0.        , 0.93729472, 0.        ])
print(doc_scores)

print(bm25.get_top_n(tokenized_query, corpus, n=1))
# ['It is quite windy in London']

from rank_bm25 import BM25Okapi
import jieba

# 1. 待检索的文档集合（多个文档）
documents = [
    "我爱吃苹果",
    "苹果手机很好用",
    "苹果很甜",
    "北京今天天气不错"
]

# 2. 预处理：对每个文档分词
tokenized_docs = []
for doc in documents:
    tokens = jieba.lcut(doc)  # 中文分词
    # 可选：小写化、去停用词
    tokenized_docs.append(tokens)

# tokenized_docs 格式：
# [['我', '爱', '吃', '苹果'],
#  ['苹果', '手机', '很', '好用'],
#  ['北京', '今天', '天气', '不错']]

# 3. 创建 BM25 索引
bm25 = BM25Okapi(tokenized_docs)

# 4. 查询语句（也需要同样的预处理）
query = "苹果好吃吗"
tokenized_query = jieba.lcut(query)  # ['苹果', '好吃', '吗']

# 5. 计算相关性分数
scores = bm25.get_scores(tokenized_query)
print(scores)
# 输出示例: [0.85, 0.42, 0.00]
# 文档1（我爱吃苹果）得分最高，因为包含"苹果"

# 6. 获取最相关的 Top-K 文档
top_docs = bm25.get_top_n(tokenized_query, documents, n=2)
# ['我爱吃苹果', '苹果手机很好用']
print(top_docs)