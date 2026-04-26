import time

from google.adk.agents.llm_agent import Agent
from opentelemetry import trace

from google_adk.adk_utils import ark_ds_model

# 工具：查询天气
def get_weather(city: str) -> dict:
    """查询指定城市的天气"""
    time.sleep(2.5)
    span = trace.get_current_span()
    span.set_attribute("custom_key", "current tool is get_weather")
    print(f"--- Tool: get_weather called for {city} ---")
    return {"city": city, "weather": "晴天", "temperature": "25°C"}

# 工具：穿衣建议
def get_clothing_advice(temperature: str) -> dict:
    """根据温度提供穿衣建议"""
    time.sleep(1.5)
    print(f"--- Tool: get_clothing_advice called for {temperature} ---")
    return {"temperature": temperature, "advice": "建议穿短袖"}

# Agent A：查天气
agent_a = Agent(
    model=ark_ds_model,
    name='weather_agent',
    description='查询城市天气',
    instruction='使用 get_weather 工具查询天气',
    tools=[get_weather],
)

# Agent B：穿衣建议
agent_b = Agent(
    model=ark_ds_model,
    name='clothing_agent',
    description='提供穿衣建议',
    instruction='使用 get_clothing_advice 工具提供穿衣建议',
    tools=[get_clothing_advice],
)

# 主 Agent：协调调用 A 和 B
root_agent = Agent(
    model=ark_ds_model,
    name='root_agent',
    description='助手，可以查询天气和穿衣建议',
    instruction='根据用户问题，调用 weather_agent 查询天气，或调用 clothing_agent 获取穿衣建议',
    sub_agents=[agent_a, agent_b],
)
