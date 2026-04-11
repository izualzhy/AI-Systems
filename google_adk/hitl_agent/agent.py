# Conceptual Code: Using a Tool for Human Approval
from google.adk import Runner
from google.adk.agents import LlmAgent, SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, ToolContext
import asyncio

from google_adk.adk_utils import ark_ds_model, log_after_call_llm, log_before_call_llm, silicon_ds_model
from google_adk.adk_instructions import (
    get_hitl_initial_writer_instruction,
    get_hitl_story_branch_instruction,
    get_hitl_story_continuer_instruction
)
from typing import Literal
from pydantic import BaseModel, Field

CURRENT_STORY = "current_story"
CURRENT_BRANCH = "current_branch"

CHAT_MODEL = ark_ds_model

class StoryBranch(BaseModel):
    """故事情节分支选项"""
    branch_options: list[str] = Field(
        default_factory=list,
        description="两个可能的后续情节发展方向，每个 20 字以内",
        min_length=2,
        max_length=2,
    )

initial_writer_agent = LlmAgent(
    name="InitialWriterAgent",
    model=CHAT_MODEL,
    include_contents='none',
    instruction=get_hitl_initial_writer_instruction(),
    description="基于故事主题创作吸引人的故事开头",
    output_key=CURRENT_STORY,
)

story_branch_agent = LlmAgent(
    name="StoryBranchAgent",
    model=CHAT_MODEL,
    include_contents='none',
    instruction=get_hitl_story_branch_instruction(),
    description="基于已有故事创作两个不同的后续情节选项",
    output_schema=StoryBranch,
    output_key=CURRENT_BRANCH,
)

def select_story_branch(current_branch: dict, tool_context: ToolContext) -> str:
    """展示情节分支选项供用户选择，并返回用户选择的剧情方向。
    
    Args:
        current_branch (dict): 包含 branch_options 列表的字典，格式为 {'branch_options': ['选项 1', '选项 2']}
        tool_context (ToolContext): 工具上下文对象，用于访问会话状态等信息
    
    Returns:
        str: 用户选择的情节描述文本。如果用户输入 1 或 2，返回对应的选项内容；
             否则返回用户的自定义输入
    
    Note:
        该函数会在终端打印当前状态信息和两个情节选项，等待用户输入选择。
        有效输入为 '1' 或 '2'，其他输入会被视为自定义剧情方向。
    """
    print("====== STATE ======")
    state_dict = tool_context.state.to_dict()
    for k,v in state_dict.items():
        print(f"\t{k}: {v}")
    branch_options = current_branch.get('branch_options', [])

    print(f"\n=== 情节分支选项 ===")
    for i, option in enumerate(branch_options, 1):
        print(f"{i}. {option}")

    choice = input("\n请选择剧情发展 (输入 1 或 2): ")

    if choice.strip() in ('1', '2'):
        return branch_options[int(choice.strip()) - 1]
    else:
        return choice

story_continuer_agent = LlmAgent(
    name="StoryContinuerAgent",
    model=CHAT_MODEL,
    include_contents='none',
    instruction=get_hitl_story_continuer_instruction(),
    description="根据用户选择的情节分支续写故事",
    tools=[select_story_branch],
    output_key=CURRENT_STORY, # 复用 state['current_story']
    before_model_callback=log_before_call_llm,
)

story_loop = LoopAgent(
    name="StoryLoop",
    sub_agents=[story_branch_agent, story_continuer_agent],
)

# def update_initial_topic_state(callback_context: CallbackContext):
#     """Ensure 'initial_topic' is set in state before pipeline starts."""
#     callback_context.state['initial_topic'] = callback_context.state.get('initial_topic', input("请输入故事主题："))


novel_workflow = SequentialAgent(
    name="NovelWorkflow",
    sub_agents=[initial_writer_agent, story_loop],
    # before_agent_callback=update_initial_topic_state
)

root_agent = novel_workflow

if __name__ == "__main__":
    import asyncio
    from google.adk import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    async def main():
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            session_service=session_service,
            app_name="NovelApp",
            auto_create_session=True,
        )
        
        user_id = "test_user"
        session_id = "test_session"
        
        print("--- 启动故事生成 ---")
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=types.Content(
                parts=[types.Part(text=input("请开始写一个故事:"))],
                role="user"
            )
        ):
            print(f"\n============== event:\n {event}")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text, end="", flush=True)
            elif hasattr(event, 'tool_code') and event.tool_code:
                # This is likely the human approval step
                print(f"Agent called tool: {event.tool_code}")

    asyncio.run(main())

