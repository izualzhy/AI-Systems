#!/usr/bin/env python
# coding=utf-8

import argparse
import random
from faker import Faker
import pandas as pd

# 支持的数据生成器（避免全用同一种类型）
def get_fake_value(fake, generator_name):
    try:
        return getattr(fake, generator_name)()
    except AttributeError:
        return fake.word()

def main():
    parser = argparse.ArgumentParser(description="生成带假数据的 Excel 文件")
    parser.add_argument("--cols", type=int, default=10, help="列数（默认 10）")
    parser.add_argument("--rows", type=int, default=100, help="行数（默认 100）")
    parser.add_argument("--output", type=str, default=None, help="输出文件名")
    args = parser.parse_args()

    num_cols = args.cols
    num_rows = args.rows

    if num_cols <= 0 or num_rows <= 0:
        raise ValueError("列数和行数必须大于 0")

    if args.output is None:
        args.output = f"fake_data_{num_cols}_{num_rows}.xlsx"
    output_file = args.output

    fake = Faker('zh_CN')
    # 可选的 Faker 方法列表（尽量多样化）
    generators = [
        'name', 'email', 'address', 'phone_number', 'company',
        'job', 'text', 'sentence', 'word', 'url',
        'ipv4', 'mac_address', 'user_name', 'domain_name',
        'random_number', 'random_int', 'pyfloat',
        'date_this_year', 'date_of_birth', 'iso8601'
    ]

    # 如果列数超过生成器数量，循环使用
    selected_generators = [generators[i % len(generators)] for i in range(num_cols)]

    # 生成表头：col_1, col_2, ..., col_N 或用生成器名
    headers = [f"col_{i+1}" for i in range(num_cols)]

    print(f"正在生成 {num_rows} 行 × {num_cols} 列 的假数据...")

    data = []
    for _ in range(num_rows):
        row = []
        for gen in selected_generators:
            if gen in ('random_number', 'random_int'):
                val = fake.random_int(min=1, max=10000)
            elif gen == 'pyfloat':
                val = round(fake.pyfloat(), 2)
            elif gen in ('date_this_year', 'date_of_birth', 'iso8601'):
                val = str(getattr(fake, gen)())
            else:
                val = get_fake_value(fake, gen)
            row.append(val)
        data.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(data, columns=headers)

    # 写入 Excel
    df.to_excel(output_file, index=False)

    print(f"✅ 成功生成文件: {output_file}")
    print(f"   行数: {num_rows}, 列数: {num_cols}")

if __name__ == "__main__":
    main()