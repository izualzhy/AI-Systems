#!/usr/bin/env python
# coding=utf-8

import os
import threading
from multiprocessing import Process


def cpu_bound_task(name):
    print(f"Thread {name} started")
    x = 0
    while True:
        x += 1  # 纯 Python 字节码，吃 GIL
        if x % 10_000_000 == 0:
            pass

def cpu_test_use_thread():
    print("PID:", os.getpid())

    t1 = threading.Thread(target=cpu_bound_task, args=("A",))
    t2 = threading.Thread(target=cpu_bound_task, args=("B",))

    t1.start()
    t2.start()

    t1.join()
    t2.join()


def cpu_test_use_process():
    print("Main PID:", os.getpid())

    p1 = Process(target=cpu_bound_task, args=("A",))
    p2 = Process(target=cpu_bound_task, args=("B",))

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == "__main__":
    cpu_test_use_process()