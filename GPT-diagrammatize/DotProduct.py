#!/usr/bin/env python
# coding=utf-8

import torch # 导入torch
import torch.nn.functional as F # 导入nn.functional

# 1. 创建两个张量 x1 和 x2
x1 = torch.randn(2, 3, 4) # 形状(batch_size, seq_len1, feature_dim)
x2 = torch.randn(2, 5, 4) # 形状(batch_size, seq_len2, feature_dim)
print(x1)
print(x2)

# 2. 计算原始权重
raw_weights = torch.bmm(x1, x2.transpose(1, 2)) # 形状 (batch_size, seq_len1, seq_len2)
print(raw_weights)

# 3. 用softmax函数对原始权重进行归一化
attn_weights = F.softmax(raw_weights, dim=2) # 形状 (batch_size, seq_len1, seq_len2)
print(attn_weights)

# 4. 将注意力权重与 x2 相乘，计算加权和
attn_output = torch.bmm(attn_weights, x2)  # 形状 (batch_size, seq_len1, feature_dim)
print(attn_output)