#!/usr/bin/env python
# coding=utf-8


import asyncio
import json
import re
from urllib.parse import unquote
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# 1. 数据库连接配置
db_url = "mysql+aiomysql://root:1234@localhost:3306/adk_sessions"

# 2. Unicode 转中文的处理函数
def unicode_unescape(s):
    r"""
    处理两种情况：
    1. 普通的 \u 转义符 (如: \\u4e2d\\u6587)
    2. URL 编码的 Unicode (如: %u4E2D%u6587)
    3. JSON 字符串中可能存在的双重转义
    """

    if not s or not isinstance(s, str):
        return s

    try:
        # 情况 A: 尝试直接作为 JSON 解析 (处理双重转义最稳妥的方法)
        # 如果字符串是合法的 JSON 格式（比如被引号包围的字符串），直接用 json.loads
        if s.startswith('"') and s.endswith('"'):
            return json.loads(s)

        # 情况 B: 处理 %u 开头的编码
        if '%u' in s:
            # 先处理 %uXXXX 格式
            s = re.sub(r'%u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)
            # 然后处理普通的 % 编码
            s = unquote(s)
            return s

        # 情况 C: 处理标准的 \uXXXX 格式
        # 使用正则替换 \u 后跟4位16进制数
        # flags=re.DOTALL 确保换行符也能被处理
        def replace_unicode(match):
            try:
                return chr(int(match.group(1), 16))
            except:
                return match.group(0) # 如果转换失败，返回原样

        # 这个正则匹配 \u 后面紧跟4个十六进制字符
        result = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, s, flags=re.DOTALL)

        # 额外尝试：如果上面没变，但字符串里有引号，尝试用 json.loads 修复可能存在的引号问题
        if result == s:
            try:
                # 尝试包裹在列表中解析，以防字符串本身包含特殊结构
                temp = json.loads(f'["{s}"]')
                return temp[0]
            except:
                pass

        return result

    except Exception as e:
        print(f"转换时发生错误 (可能已经是正常文本): {e}")
        return s # 如果报错，说明可能已经是正常中文，直接返回

async def fetch_events_table_and_convert():
    # 创建异步引擎
    engine: AsyncEngine = create_async_engine(db_url, echo=False)

    try:
        async with engine.connect() as conn:
            # 执行查询
            result = await conn.execute(
                text("SELECT * FROM `events` ORDER BY `timestamp`"),
            )

            rows = result.fetchall()

            print(f"共查询到 {len(rows)} 条记录。处理后的结果：\n")

            for row in rows:
                # 将 Row 对象转换为字典，方便处理
                row_dict = row._asdict()

                # 检查并处理 event_data 字段
                raw_data = row_dict.get('event_data')
                if raw_data:
                    # 调用转换函数
                    row_dict['event_data'] = unicode_unescape(raw_data)

                # 输出处理后的行
                print(f"ID: {row_dict['id']}")
                print(f"App: {row_dict['app_name']}")
                print(f"User: {row_dict['user_id']}")
                print(f"Session: {row_dict['session_id']}")
                print(f"Time: {row_dict['timestamp']}")
                # 完整打印数据（不截断）
                print(f"Data (转换后): {row_dict['event_data']}")
                print("-" * 50)
    finally:
        # 确保引擎被正确关闭
        await engine.dispose()


async def dump_all_tables():
    """导出数据库中所有表的数据（原样导出）"""
    engine: AsyncEngine = create_async_engine(db_url, echo=False)

    try:
        async with engine.connect() as conn:
            # 获取所有表名
            result = await conn.execute(
                text("SHOW TABLES")
            )
            tables = [row[0] for row in result.fetchall()]
            
            print(f"数据库中共有 {len(tables)} 个表: {tables}\n")
            if not tables:
                print("(无表)\n")
                sys.exit(0)

            for table_name in tables:
                if table_name == 'events':
                    continue
                print(f"{'='*80}")
                print(f"表名: {table_name}")
                print(f"{'='*80}")
                
                # 查询表的所有数据
                query_result = await conn.execute(
                    text(f"SELECT * FROM `{table_name}`")
                )
                rows = query_result.fetchall()
                
                if not rows:
                    print("(空表)\n")
                    continue
                
                # 获取列名
                columns = query_result.keys()
                print(f"列名: {list(columns)}")
                print(f"记录数: {len(rows)}\n")
                
                # 打印每行数据
                for i, row in enumerate(rows, 1):
                    row_dict = row._asdict()
                    print(f"--- 记录 {i} ---")
                    for col, value in row_dict.items():
                        print(f"  {col}: {value}")
                    print()
                
                print()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    import sys
    
    # 导出所有表
    asyncio.run(dump_all_tables())
    asyncio.run(fetch_events_table_and_convert())