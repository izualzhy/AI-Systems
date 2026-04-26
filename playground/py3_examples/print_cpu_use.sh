#!/bin/bash

MAIN_PID=$1

echo "Main PID: $MAIN_PID"

# 每秒打印主进程及其子进程 / 线程的 CPU
while true; do
    echo "==== $(date) ===="

    # 1. 打印主进程 CPU
    ps -o pid,ppid,%cpu,comm -p $MAIN_PID

    # 2. 打印所有子进程 CPU
    CHILD_PIDS=$(pgrep -P $MAIN_PID)
    for pid in $CHILD_PIDS; do
        ps -o pid,ppid,%cpu,comm -p $pid
    done

    # 3. 打印线程（TID）CPU
    # macOS 上用 ps -M <pid> 可以列出线程
    for pid in $MAIN_PID $CHILD_PIDS; do
        echo "-- Threads of PID $pid --"
        ps -M $pid -o pid,tid,%cpu,comm
    done

    sleep 1
done

