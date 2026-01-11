#!/usr/bin/env python
# coding=utf-8

import threading
import time

from limits import RateLimitItemPerSecond
from limits.storage import RedisStorage
from limits.strategies import MovingWindowRateLimiter
from loguru import logger

storage = RedisStorage("redis://localhost:6379")
limiter = MovingWindowRateLimiter(storage)

limit = RateLimitItemPerSecond(1)  # 全局 100 QPS

def handle_request(thread_name):
    while True:
        acquired = limiter.hit(limit, "global_api")
        if not acquired:
            wait_second = 1
            logger.debug(f"Rate limit exceeded thread: {thread_name}, wait {wait_second} seconds...")
            time.sleep(wait_second)
        else:
            logger.info(f"Processing request, thread: {thread_name}")
            time.sleep(10)
            logger.info(f"Processing finished, thread: {thread_name}")
            break


if __name__ == "__main__":
    threads = []
    for i in range(5):
        t = threading.Thread(target=handle_request, args=(f"Thread-{i}",))
        threads.append(t)
        t.start()  # 启动线程

    # 等待所有线程完成
    for t in threads:
        t.join()