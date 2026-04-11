#!/usr/bin/env python
# coding=utf-8
"""
验证 State Prefix 隔离效果 - Agent 自动学习用户偏好

流程：
1. user1 聊天说喜欢红色、火锅 → Agent 自动保存到 state['user1']
2. user2 聊天说喜欢蓝色、烧烤 → Agent 自动保存到 state['user2']
3. user1 再次聊天问喜欢什么 → Agent 从 state 读取并回答
"""
import asyncio
import random
import warnings

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from google_adk.adk_utils import ark_ds_model

db_url = "mysql+aiomysql://root:1234@localhost:3306/adk_sessions"

APP_NAME = 'state_learning_app'

def update_initial_state(callback_context: CallbackContext):
    """Ensure 'favorite_sport' is set in state before pipeline starts."""
    callback_context.state['favorite_sport'] = callback_context.state.get('favorite_sport', '皮球')


def create_session_service():
    """创建新的 session service 实例"""
    return DatabaseSessionService(db_url=db_url)


def save_user_preference(color: str, food: str, tool_context: ToolContext):
    """保存用户偏好到 state"""
    user_id = tool_context.user_id
    
    tool_context.state['user:color'] = color
    tool_context.state['user:food'] = food

    tool_context.state['app:color'] = 'app>' + color
    tool_context.state['app:food'] = 'app>' + food

    return f"✅ 已保存 {user_id} 的偏好：颜色={color}, 食物={food}"


def get_user_preference(tool_context: ToolContext):
    """获取用户偏好"""
    user_id = tool_context.user_id
    color = tool_context.state.get('user:color', '未知')
    food = tool_context.state.get('user:food', '未知')
    
    return f"{user_id} 的偏好：颜色={color}, 食物={food}"


root_agent = Agent(
    model=ark_ds_model,
    name='preference_learning_agent',
    description='学习并记住用户偏好的助手',
#     instruction='''你是一个助手，可以学习和记住用户的偏好。
#
# 重要：当用户告诉你喜好时，立即调用 save_user_preference 工具保存。
# - 提取用户提到的颜色和食物
# - 调用工具保存（user_id 会自动从上下文获取）
#
# 当用户询问自己的偏好时，从 state[user_id] 中读取并回答。
#
# 示例：
# 用户说“我喜欢红色和火锅” → 调用 save_user_preference(color="红色", food="火锅")
# 用户问“我喜欢什么颜色” → 从 state[user_id]["color"] 读取并回答
# ''',
    instruction='''你是一个助手，可以学习和记住用户的偏好。

重要：
1. 当用户告诉你颜色和食物的喜好时，立即调用 save_user_preference 工具保存。
- 提取用户提到的颜色和食物
- 调用工具保存（user_id 会自动从上下文获取）
当用户询问自己的颜色和食物的偏好时，调用 get_user_preference 工具获取。

示例：
用户说“我喜欢红色和火锅” → 调用 save_user_preference(color="红色", food="火锅")
用户问“我喜欢什么颜色” → 调用 get_user_preference()

2. 当用户告诉你喜爱的运动时，请存储到 state 里的 {favorite_sport} 
当用户询问自己喜爱的运动时，请读取 state 里的 {favorite_sport}

示例：
用户说“喜欢羽毛球这个运动” -> 存储到 state 里的 {favorite_sport} 
用户问“我喜欢什么运动” -> 读取 state 里的 {favorite_sport} 
''',
    tools=[save_user_preference, get_user_preference],
    before_agent_callback=update_initial_state,
)


async def chat_with_user(user_id: str, session_id: str, message: str):
    """与指定用户对话"""
    session_service = create_session_service()
    
    # 确保 session 存在
    session = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if not session:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
    
    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        auto_create_session=False,
    )
    
    content = types.Content(role='user', parts=[types.Part(text=message)])
    
    print(f"\n💬 {user_id}: {message}")
    response_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        print(f" event:\n{event}\n")
        if event.is_final_response() and event.content:
            response_text = "".join(part.text for part in event.content.parts if part.text)
    
    print(f"🤖 Agent: {response_text}")
    
    # 关闭数据库连接
    if hasattr(session_service, 'engine') and session_service.engine:
        await session_service.engine.dispose()
    
    return response_text


async def get_user_state(user_id: str, session_id: str):
    """查看当前 state"""
    session_service = create_session_service()
    try:
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )
        if session and session.state:
            print(f"📋 State: {session.state}")
            return session.state
        return {}
    finally:
        if hasattr(session_service, 'engine') and session_service.engine:
            await session_service.engine.dispose()


async def main():
    print("="*80)
    print("测试 State Prefix - Agent 自动学习用户偏好")
    print("="*80)

    # 步骤1: user1 告诉 Agent 自己的偏好
    print("\n--- 步骤 1: user1 告诉 Agent 偏好 ---")
    await chat_with_user(
        user_id="user1",
        session_id="session_user1",
        message="我喜欢红色和火锅，喜欢电子竞技这个运动"
    )
    input("请按 Enter 继续...")
    
    # 查看 state
    print("\n--- 查看当前 state ---")
    await get_user_state("user1", "session_user1")
    input("请按 Enter 继续...")

    # 步骤2: user2 告诉 Agent 自己的偏好
    print("\n--- 步骤 2: user2 告诉 Agent 偏好 ---")
    await chat_with_user(
        user_id="user2",
        session_id="session_user2",
        message="我喜欢蓝色和烧烤，喜欢羽毛球这个运动"
    )
    input("请按 Enter 继续...")

    # 查看 state
    print("\n--- 查看当前 state ---")
    await get_user_state("user2", "session_user2")
    input("请按 Enter 继续...")

    # 步骤3: user1 用新的 session 询问偏好（验证是否记住）
    print("\n--- 步骤 3: user1 用新 session 询问偏好 ---")
    await chat_with_user(
        user_id="user1",
        session_id="session_user1_new",
        message="我喜欢什么颜色、食物和运动？"
    )
    input("请按 Enter 继续...")

    # 步骤4: user2 用新的 session 询问偏好
    print("\n--- 步骤 4: user2 用新 session 询问偏好 ---")
    await chat_with_user(
        user_id="user2",
        session_id="session_user2_new",
        message="我喜欢吃什么？喜欢什么运动？"
    )
    input("请按 Enter 继续...")

    # 最终 state
    print("\n--- 最终 state ---")
    await get_user_state("user1", "session_user1_new")
    await get_user_state("user2", "session_user2_new")
    input("请按 Enter 继续...")

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
