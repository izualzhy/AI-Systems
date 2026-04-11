import asyncio
from google.adk.agents.llm_agent import Agent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.genai import types

from google_adk.adk_utils import ark_ds_model, ark_seed20_model
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer

# 定义用于总结事件的模型
summarization_llm = ark_seed20_model

# 创建自定义总结器
my_summarizer = LlmEventSummarizer(llm=summarization_llm)

def get_weather() -> dict:
    """Returns the weather anywhere."""
    return {"status": "success", "weather": "晴，31 度"}

# 创建根 agent - 一个简单的对话助手
root_agent = Agent(
    model=ark_ds_model,
    name='summarizer_root_agent',
    description='百科全书',
    instruction='回答问题需要在 20 个字以内，简洁。如果用户咨询天气的问题，请直接调用 get_weather 工具。',
    tools=[get_weather],
)

# 配置应用，启用上下文压缩功能
app = App(
    name='summarizer_agent_app',
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # 每3次新调用触发压缩
        overlap_size=1,         # 包含上一次窗口中的最后1次调用
        summarizer=my_summarizer,  # 使用自定义总结器
    ),
)

# 会话服务
# session_service = InMemorySessionService()
db_url = "mysql+aiomysql://root:1234@localhost:3306/adk_sessions"
session_service = DatabaseSessionService(db_url=db_url)

APP_NAME = 'summarizer_agent_app'
USER_ID = 'test_user'
SESSION_ID = 'test_session_compaction'

async def get_events_count(session_service, app_name, user_id, session_id):
    """获取当前会话的事件数量"""
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    return len(session.events) if session and hasattr(session, 'events') else 0

async def print_events_detail(session_service, app_name, user_id, session_id):
    """打印事件详情，区分普通事件和摘要事件"""
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    if not session or not hasattr(session, 'events'):
        print("\n⚠️ 无法获取事件列表")
        return 0
    
    events = session.events
    print(f"\n📋 事件列表 (共 {len(events)} 个):")
    for i, event in enumerate(events, 1):
        # 检查是否是摘要事件
        is_summary = False
        if hasattr(event, 'metadata') and event.metadata:
            if event.metadata.get('is_summary') or event.metadata.get('type') == 'summary':
                is_summary = True
        
        if not is_summary and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'metadata') and part.metadata:
                    if part.metadata.get('is_summary') or part.metadata.get('type') == 'summary':
                        is_summary = True
                        break
        
        # 获取事件内容预览
        content_preview = ""
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    content_preview = part.text[:50].replace('\n', ' ')
                    break
        
        event_type = "🔖 [摘要]" if is_summary else "💬 [对话]"
        author = event.author if hasattr(event, 'author') else 'unknown'
        print(f"  {i}. {event_type} by {author}: {content_preview}...")
    
    return len(events)

async def run_conversation():
    """运行多轮对话以验证上下文压缩效果"""
    
    # 创建会话
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"✅ 会话 '{SESSION_ID}' 已创建\n")
    
    # 创建 runner
    runner = Runner(
        app=app,
        session_service=session_service
    )
    
    # 测试消息列表 - 模拟多轮对话
    test_messages = [
        "你好，请介绍一下你自己",
        "你能帮我做什么？",
        "今天天气怎么样？",
        "给我讲个笑话吧",
        "Python 是什么？",
        "机器学习有哪些应用场景？",
        "推荐一本好书",
        "如何学习编程？",
        "什么是人工智能？",
        "谢谢你的帮助！"
    ]
    
    print("="*80)
    print("开始多轮对话测试（将触发上下文压缩）")
    print("配置: compaction_interval=3, overlap_size=1")
    print("="*80)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*80}")
        print(f"第 {i} 轮对话")
        print(f"{'='*80}")
        print(f"👤 用户: {message}")
        
        # 记录压缩前的事件数
        events_before = await get_events_count(session_service, APP_NAME, USER_ID, SESSION_ID)
        print(f"\n📊 run_async 前事件数: {events_before}")
        
        # 运行 agent
        response_text = ""
        content = types.Content(role='user', parts=[types.Part(text=message)])
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content
        ):
            if event.is_final_response() and event.content:
                response_text = "".join(
                    part.text for part in event.content.parts if part.text
                )
        
        print(f"🤖 Agent: {response_text[:100]}..." if len(response_text) > 100 else f"🤖 Agent: {response_text}")
        
        # 记录压缩后的事件数
        events_after = await get_events_count(session_service, APP_NAME, USER_ID, SESSION_ID)
        print(f"📊 run_async 事件数: {events_after}")

        print(f"⚡ 打印当前所有 event：")
        await print_events_detail(session_service, APP_NAME, USER_ID, SESSION_ID)

        # 每轮之间稍微延迟，便于观察
        await asyncio.sleep(0.5)
        input("按回车继续...")
    
    print("\n" + "="*80)
    print("✅ 对话测试完成")
    print("="*80)
    
    # 最终统计
    final_events = await get_events_count(session_service, APP_NAME, USER_ID, SESSION_ID)
    print(f"\n📈 最终统计:")
    print(f"   - 总对话轮数: {len(test_messages)}")
    print(f"   - 最终事件数: {final_events}")
    print(f"   - 如果没有压缩，预期事件数: {len(test_messages) * 2}")
    print(f"   - 压缩节省的事件数: {len(test_messages) * 2 - final_events}")

if __name__ == '__main__':
    asyncio.run(run_conversation())
