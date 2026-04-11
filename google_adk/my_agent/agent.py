import os
from typing import Optional

from dotenv import load_dotenv

# 配置 OpenTelemetry SkyWalking - 使用 gRPC 协议
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://localhost:11800"
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"
os.environ["OTEL_LOGS_EXPORTER"] = "otlp"
os.environ["OTEL_TRACES_EXPORTER"] = "otlp"
os.environ["OTEL_METRICS_EXPORTER"] = "otlp"

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.models import LlmRequest, LlmResponse

from google_adk.adk_utils import ark_ds_model

os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "127.0.0.1:4318"
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = "127.0.0.1:4318"
#OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
#OTEL_EXPORTER_OTLP_LOGS_PROTOCOL="grpc"
#OTEL_EXPORTER_OTLP_TRACES_PROTOCOL="grpc"

# Mock tool implementation
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}

def my_sync_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    print(f"--- 发送给模型的请求 ---")
    print(f"Agent: {callback_context.agent_name}")
    print(f"内容：{llm_request.contents}")
    return None # 返回 None 表示继续正常执行

root_agent = Agent(
    model=ark_ds_model,
    name='root_agent',
    description="Tells the current time in a specified city.",
    instruction="You are a helpful assistant that tells the current time in cities. Use the 'get_current_time' tool for this purpose.",
    tools=[get_current_time],
    before_model_callback=my_sync_callback,
)

"""
测试 Context Artifact
"""

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types


async def log_query(tool_context: ToolContext, query: str):
    """Saves the provided query string as a 'text/plain' artifact named 'query'."""
    query_bytes = query.encode('utf-8')
    artifact_part = types.Part(
        inline_data=types.Blob(mime_type='text/plain', data=query_bytes)
    )
    await tool_context.save_artifact('query', artifact_part)

    # 使用相对路径获取文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.normpath(f"{current_dir}/../../../yingshin.github.io/_posts/2026-04-05-sdpxz-reading-c.markdown")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    artifact_part = types.Part.from_text(text=content)
    version = await tool_context.save_artifact("document_to_summarize.txt", artifact_part)
    print(f"Saved document reference '{file_path}' as artifact version {version}")



root_agent = Agent(
    model=ark_ds_model,
    name='log_agent',
    description='Log user query.',
    instruction="""Always log the user query and reply "kk, I've logged."
    """,
    tools=[log_query],
    generate_content_config=types.GenerateContentConfig(
        safety_settings=[
            types.SafetySetting(  # avoid false alarm about rolling dice.
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.OFF,
            ),
        ]
    ),
)
