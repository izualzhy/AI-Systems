#!/usr/bin/env python
# coding=utf-8

import asyncio
from saq import Queue, Worker, Job
from saq.types import Context, Function

def get_test_job_name_for_index(index: int) -> str:
    return f"test_job_index_{index}"

# 任务函数
async def my_attribution_logic(ctx: Context, user_id: str, amount: float):
    """
    这是实际干活的函数。
    注意：它不需要知道自己是 index_0 还是 index_1，
    但可以通过 ctx['job'].name 知道当前执行的是哪个名字的任务
    """
    job_name = ctx["job"].function
    print(f"🚀 [Worker] 开始执行任务: {job_name}")
    print(f"   👤 用户: {user_id}, 💰 金额: {amount}")

    # 模拟耗时操作
    await asyncio.sleep(1)

    result = f"处理完成 (由 {job_name} 处理)"
    print(f"✅ [Worker] 任务 {job_name} 完成: {result}")
    return result

# 配置 SAQ Settings (核心部分)
async def create_settings():
    # 初始化队列 (连接本地 Redis)
    queue = Queue.from_url("redis://localhost")

    # 假设我们要支持两个不同的逻辑索引
    indices = [0, 1]

    functions_list = []

    for idx in indices:
        # 1. 动态生成任务名称 (例如: "test_job_index_0")
        task_name = get_test_job_name_for_index(idx)

        # 2. 构建元组: (任务名称字符串, 实际函数对象)
        mapping = (task_name, my_attribution_logic)

        functions_list.append(mapping)
        print(f"🔧 注册映射: 任务名 '{task_name}' -> 函数 'my_attribution_logic'")

    settings = {
        "queue": queue,
        "functions": functions_list, # 这里传入列表
        "concurrency": 1,
    }
    return settings

# 外部提交任务 (Producer)
async def producer(queue: Queue):
    print("\n--- 📮 Producer 开始提交任务 ---")

    # 场景 A: 提交给 index 0
    name_0 = get_test_job_name_for_index(0)
    job_0 = await queue.enqueue(name_0, user_id="Alice", amount=100.0)
    print(f"提交了任务 ID: {job_0.id}, 目标名称: {name_0}")

    # 场景 B: 提交给 index 1
    name_1 = get_test_job_name_for_index(1)
    job_1 = await queue.enqueue(name_1, user_id="Bob", amount=200.5)
    print(f"提交了任务 ID: {job_1.id}, 目标名称: {name_1}")

    # 场景 C: 故意提交一个错误的名字 (测试失败情况)
    # job_err = await queue.enqueue("test_job_index_999", user_id="Error", amount=0)

    print("--- 📮 提交完毕，等待 Worker 处理 ---\n")

# 主程序入口
async def main():
    settings = await create_settings()
    queue = settings["queue"]

    # 启动 Worker (在后台运行)
    worker = Worker(**settings)
    worker_task = asyncio.create_task(worker.start())

    # 给 Worker 一点时间连接 Redis
    await asyncio.sleep(0.5)

    # 运行生产者提交任务
    await producer(queue)

    # 等待任务处理完成 (简单等待 3 秒，实际生产中通常不会这样写)
    await asyncio.sleep(3)

    # 停止 Worker
    await worker.stop()
    print("\n🛑 Worker 已停止")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass