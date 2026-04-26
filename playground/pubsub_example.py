# pubsub_example.py

from celery import Celery
from kombu import Queue, Exchange

# --- 运行说明 ---
# 这个例子将演示如何通过一次任务发布，将消息发送到多个队列。
#
# 1. 确保您的 Redis 服务正在运行。
# 2. 打开【三个】独立的终端窗口。
#
# 3. 在【终端1】，启动数据分析服务的 worker:
#    celery -A pubsub_example.app worker -l info -Q analytics_queue -n analytics_worker@%h
#
# 4. 在【终端2】，启动邮件服务的 worker:
#    celery -A pubsub_example.app worker -l info -Q email_queue -n email_worker@%h
#
# 5. 在【终端3】，启动审计服务的 worker:
#    celery -A pubsub_example.app worker -l info -Q audit_queue -n audit_worker@%h
#
# 6. 打开【终端4】，运行此脚本来发送一条事件:
#    python pubsub_example.py
#
# 观察结果:
# 您会发现，当您只发送了【一条】'user.signup' 事件后，
# 【所有三个】worker 都会接收到这个任务并执行它。
# 这证明了消息被成功“广播”到了所有相关的队列，这是仅指定 queue 无法做到的。
# --------------------------------------------------------------------


# 1. 定义一个 "topic" 类型的交换机
# "topic" 类型的交换机允许使用通配符进行更灵活的路由。
#   - `*` (星号) 能替代一个单词。
#   - `#` (井号) 能替代零个或多个单词。

events_exchange = Exchange('events_exchange', type='topic')


# 2. 配置 Celery 应用
app = Celery(
    'pubsub_example',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

app.conf.update(
    # 3. 定义队列和它们与交换机的绑定关系
    # 这是实现广播的关键：多个队列绑定到同一个 topic 交换机，
    # 并使用不同的、但可能重叠的路由键模式。
    task_queues=(
        # 数据分析队列：关心所有和用户相关的事件 (user.*)
        Queue('analytics_queue', events_exchange, routing_key='user.*'),
        
        # 邮件队列：只关心用户注册事件 (user.signup)
        Queue('email_queue', events_exchange, routing_key='user.signup'),
        
        # 审计队列：关心系统中的所有事件 (#)
        Queue('audit_queue', events_exchange, routing_key='#'),
    )
)


# 4. 定义一个通用的事件处理任务
@app.task(bind=True)
def handle_event(self, event_data):
    """
    一个通用的事件处理器。
    它会打印出自己是哪个 worker 以及收到的事件数据。
    """
    # self.request.hostname 会返回 worker 的名称 (例如: analytics_worker@hostname)
    worker_name = self.request.hostname.split('@')[0]
    message = f"[{worker_name}] 正在处理事件: {event_data}"
    print(message)
    return message


# 5. 主程序逻辑：发布一个事件
if __name__ == '__main__':
    print("正在发布一个 'user.signup' 事件...")

    # 我们只调用一次 apply_async，发布一个“用户注册”事件。
    # 它的路由键是 'user.signup'。
    # 这个路由键同时匹配了三个队列的绑定规则：
    #   - 'user.signup' 匹配 'user.*' (analytics_queue)
    #   - 'user.signup' 匹配 'user.signup' (email_queue)
    #   - 'user.signup' 匹配 '#' (audit_queue)
    #
    # 因此，Broker 会将这条消息的一个副本发送给所有这三个队列。
    handle_event.apply_async(
        args=[{'user_id': 123, 'email': 'test@example.com'}],
        exchange='events_exchange',
        routing_key='user.signup'
    )

    print("\n事件已发布！请检查所有三个 worker 终端的输出。")
    print("您应该会看到 analytics_worker, email_worker, 和 audit_worker 都处理了这条事件。")
