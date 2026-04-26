# Celery 示例

此目录包含一个 Celery 示例，用于演示其多种功能。

## 特性

- **普通任务**: 被显式调用的简单任务。
- **周期性任务**: 按计划运行的任务。
- **任务链**: 将任务链接在一起，其中一个任务的输出是下一个任务的输入。
- **自动重试**: 任务在失败时会自动重试。
- **文件日志**: 所有任务输出都记录在 `logs/tasks.log` 中。
- **任务确认 (Ack)**: 演示任务的确认机制，确保任务在成功执行后才从队列中移除。

## 结构

- `app/celery_app.py`: 定义 Celery 应用程序、配置和周期性任务计划。
- `app/tasks.py`: 包含所有任务的定义。
- `trigger_tasks.py`: 用于手动触发不同类型任务的脚本。
- `run_worker.sh`: 用于启动 Celery worker 进程的脚本。worker 执行任务。
- `run_beat.sh`: 用于启动 Celery beat 进程的脚本。beat 是一个触发周期性任务的调度器。
- `logs/`: 存储日志文件的目录。

## 如何运行

### 先决条件

1.  **安装 Celery 和消息代理。** 本示例使用 Redis。

    ```bash
    pip install "celery[redis]"
    ```

2.  **确保 Redis 正在运行。**

### 运行示例

1.  **启动 Celery worker。**
    打开一个终端并运行：

    ```bash
    ./run_worker.sh
    ```
    这将启动一个 worker，它会监听 `default` 和 `periodic_tasks` 队列上的任务。

2.  **启动 Celery beat 调度器 (用于周期性任务)。**
    打开第二个终端并运行：

    ```bash
    ./run_beat.sh
    ```
    这将启动调度器。您将在 worker 的日志中看到 `periodic_task` 每 30 秒被触发一次。

3.  **手动触发任务。**
    打开第三个终端并运行：

    ```bash
    python trigger_tasks.py
    ```
    这将分派简单的 `add` 任务、任务链和失败的任务。

### 观察输出

- `trigger_tasks.py` 脚本的输出将显示其直接调用的任务的结果。
- worker (`run_worker.sh`) 的输出将显示所有任务的执行情况，包括周期性任务。
- 所有任务日志也保存在 `py3_journey/demo_celery/logs/tasks.log` 中。

### 关于任务确认 (Ack) 的说明

`ack_task` 任务通过设置 `acks_late=True` 来演示延迟确认。这意味着只有在任务成功执行后，消息才会从队列中移除。

模拟一个 worker 在执行任务中途崩溃的场景：
1.  运行 `trigger_tasks.py` 来分派 `ack_task`。
2.  在 worker 的日志中看到任务开始执行的日志后，立即停止 worker (Ctrl+C)。
3.  重新启动 worker。
4.  发现 worker 会重新执行该任务，因为之前的任务没有被确认。