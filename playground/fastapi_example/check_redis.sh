#!/bin/bash

# 连接 Redis DB 3，获取所有 key，然后逐个获取其值
echo "正在连接 Redis DB 3 并读取所有 string 类型的 key 和 value..."

# 使用 redis-cli 获取 DB 3 中的所有 keys
keys=$(redis-cli -n 3 KEYS "*")

# 检查是否有 key
if [ -z "$keys" ]; then
    echo "数据库 3 中没有找到任何 key。"
    exit 0
fi

# 遍历每个 key，获取其值
for key in $keys; do
    # 获取 key 的类型（虽然你说都是 string，但加个保险）
    type=$(redis-cli -n 3 TYPE "$key" | tr -d '\r')
    if [ "$type" = "string" ]; then
        value=$(redis-cli -n 3 GET "$key")
        echo "Key: $key"
        echo "Value: $value"
        value=$(redis-cli -n 3 TTL "$key")
        echo "TTL: $value"
        echo "------------------------"
    else
        echo "跳过非 string 类型的 key: $key (类型: $type)"
    fi
done
