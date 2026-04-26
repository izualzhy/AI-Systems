#!/usr/bin/env python
# coding=utf-8

import os
import glob
import tiktoken

# 配置
ENCODING_NAME = "cl100k_base"  # 适用于 gpt-3.5-turbo / gpt-4 / qwen / claude 等
encoder = tiktoken.get_encoding(ENCODING_NAME)

# 常见可读文本文件后缀（可根据需要增减）
TEXT_EXTENSIONS = {
    '.txt', '.md', '.markdown', '.py', '.js', '.ts',
    '.html', '.css', '.json', '.xml', '.csv', '.log',
    '.rst', '.tex', '.sh', '.yaml', '.yml', '.ini',
    '.toml', '.cfg', '.cpp', '.c', '.h', '.java', '.go',
    '.rs', '.swift', '.kt', '.scala'
}

def count_tokens_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        tokens = encoder.encode(text)
        return len(tokens)
    except UnicodeDecodeError:
        print(f"⚠️ 跳过非文本文件（编码错误）: {file_path}")
        return 0
    except Exception as e:
        print(f"❌ 读取失败: {file_path}, 错误: {e}")
        return 0

def estimate_tokens_recursive(directory, extensions=None):
    if extensions is None:
        extensions = TEXT_EXTENSIONS

    total_tokens = 0
    file_count = 0

    for ext in extensions:
        # 使用 ** 表示任意层级子目录，recursive=True 启用递归
        pattern = os.path.join(directory, f"**/*{ext}")
        matched_files = glob.glob(pattern, recursive=True)

        for file_path in matched_files:
            if os.path.isfile(file_path):  # 再次确认是文件
                tokens = count_tokens_in_file(file_path)
                print(f"{file_path} -> {tokens:,} tokens")
                total_tokens += tokens
                file_count += 1

    print(f"\n📊 总结：共扫描到 {file_count} 个文本文件，总计约 {total_tokens:,} tokens")
    return total_tokens

# === 使用示例 ===
if __name__ == "__main__":
    directory_path = "/Users/yingz/Documents/work/code/github.com/izualzhy/ying"  # 替换为你自己的目录路径
    estimate_tokens_recursive(directory_path)
