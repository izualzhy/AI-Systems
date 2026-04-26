import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.models import LlmRequest, LlmResponse

from google_adk.adk_utils import ark_ds_model, log_before_call_llm

def get_weather(city: str) -> dict:
    """Returns the weather in a specified city."""
    print(f'=========== {os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"]}')
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

    exporter = OTLPSpanExporter()
    print(f"=========== Exporter actual endpoint: {exporter._endpoint}")   # 打印实际使用的 endpoint
    return {"status": "success", "city": city, "weather": "晴，31 度"}

def test_before_call_llm(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    print(f"--- 发送给模型的请求 ---")
    print(f"callback_context: {callback_context}")
    print(f"llm_request：{llm_request}")

    return None # 返回 None 表示继续正常执行

def test_after_call_llm(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    print(f"--- 模型返回的响应 ---")
    print(f"callback_context: {callback_context}")
    print(f"llm_response：{llm_response}")

    return None


weather_agent = Agent(
    model=ark_ds_model,
    name='root_agent',
    description="回答如何穿衣的的问题.",
    instruction="你是一个穿衣助手，如果需要知道城市的天气，可以调用 get_weather",
    tools=[get_weather],
    before_model_callback=test_before_call_llm,
    after_model_callback=test_after_call_llm
)
root_agent = weather_agent

from typing import Literal
from pydantic import BaseModel, Field

class BookRecommendation(BaseModel):
    """书籍推荐结果"""
    recommendation_level: Literal["highly_recommended", "recommended", "optional"] = Field(
        description="推荐程度：highly_recommended(强烈推荐), recommended(推荐), optional(可选)"
    )
    books: list[str] = Field(
        default_factory=list,
        description="推荐的书籍列表",
    )
    reason: str = Field(description="推荐理由")


book_recommendation_agent = Agent(
    model=ark_ds_model,
    name='book_recommendation_agent',
    description="根据用户偏好推荐书籍",
    instruction="你是一个书籍推荐助手，根据用户的具体需求，推荐合适的书籍。",
    output_schema=BookRecommendation,
    before_model_callback=test_before_call_llm,
    after_model_callback=test_after_call_llm,
)

# root_agent = book_recommendation_agent
