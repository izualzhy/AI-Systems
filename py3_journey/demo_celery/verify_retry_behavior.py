#!/usr/bin/env python
# coding=utf-8

from py3_journey.demo_celery.app.tasks import failing_task, add
import time

if __name__ == '__main__':
    print("Dispatching failing_task...")
    # 触发将会失败并重试的任务
    failing_task.delay()

    # 短暂等待，确保 failing_task 优先被 worker 接收
    time.sleep(0.5)

    print("Dispatching add(2, 2) task...")
    # 触发一个正常的、可以立即执行的任务
    add.delay(2, 2)

    print("\nTasks dispatched. Check your Celery worker logs.")
    print("You should see the 'add' task executing between the retries of 'failing_task'.")
