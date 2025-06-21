#!/usr/bin/env python
# coding=utf-8
import os

# 导入相关的工具
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)

# 设置OpenAI网站和SerpApi网站提供的API密钥
from dotenv import load_dotenv  # 用于加载环境变量

from misc import getChatOpenAI

load_dotenv()  # 加载.env文件中的环境变量
# 导入LangChain 工具
from langchain.tools import tool
# 库存查询
@tool
def check_inventory(flower_type: str) -> int:
    """
    查询特定类型花的库存数量。
    参数:
    - flower_type: 花的类型
    返回:
    - 库存数量 (暂时返回一个固定的数字)
    """

    print("check_inventory")
    # 实际应用中这里应该是数据库查询或其他形式的库存检查
    return 100  # 假设每种花都有100个单位
# 定价函数
@tool
def calculate_price(base_price: float, markup: float) -> float:
    """
    根据基础价格和加价百分比计算最终价格。
    参数:
    - base_price: 基础价格
    - markup: 加价百分比
    返回:
    - 最终价格
    """

    print("calculate price")
    return base_price * (1 + markup)

# 调度函数
@tool
def schedule_delivery(order_id: int, delivery_date: str):
    """
    安排订单的配送。
    参数:
    - order_id: 订单编号
    - delivery_date: 配送日期
    返回:
    - 配送状态或确认信息
    """

    print("enter schedule_delivery")
    # 在实际应用中这里应该是对接配送系统的过程
    return f"订单 {order_id} 已安排在 {delivery_date} 配送"
tools = [check_inventory,calculate_price]

os.environ["HTTP_PROXY"] = "http://127.0.0.1:1087"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:1087"

# 设置大模型
model = getChatOpenAI()
# 设置计划者和执行者
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
planner = load_chat_planner(model)
executor = load_agent_executor(model, tools, verbose=True)
# 初始化Plan-and-Execute Agent
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)
# 运行Agent解决问题
agent.run("查查玫瑰的库存然后给出出货方案！")

"""
> Entering new PlanAndExecute chain...
steps=[Step(value='Retrieve current rose inventory data, including key details such as total quantity, varieties (e.g., color, type), storage locations (e.g., warehouses), and freshness/expiration status (critical for perishable items).'), Step(value='Analyze the inventory to filter out unavailable stock (e.g., damaged, expired, or pre-allocated roses) and confirm the actual available quantity for shipping.'), Step(value='Gather essential shipping requirements from the user or relevant sources, including customer demand (quantity needed), desired delivery date, preferred shipping method (e.g., express, standard), and any special instructions (e.g., temperature control, packaging).'), Step(value='Compare the available inventory with the shipping requirements to assess feasibility: check if the stock quantity is sufficient to meet demand and if the delivery timeline can be achieved given storage locations and shipping methods.'), Step(value='If feasible, allocate stock using a logical strategy (e.g., FIFO for freshness, closest warehouse for faster delivery) and draft a shipping plan with details like origin warehouse, carrier, estimated delivery time, tracking information, and handling instructions.'), Step(value='If not feasible (e.g., insufficient stock, unable to meet delivery date), propose alternatives such as backordering, substituting with similar rose varieties, or adjusting the delivery timeline, and revise the plan accordingly.'), Step(value='Compile the inventory check results (available stock, key constraints) and the final shipping plan (or revised alternatives) into a clear, actionable response for the user.\n<END_OF_PLAN>')]

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "check_inventory",
  "action_input": {
    "flower_type": "rose"
  }
}
```check_inventory

Observation: 100
Thought:Action:
```
{
  "action": "Final Answer",
  "action_input": "The current inventory data for roses includes a total quantity of 100. However, details such as varieties (color/type), storage locations (warehouses), and freshness/expiration status are not available through the current check_inventory tool, which only returns stock quantity."
}
```

> Finished chain.
*****

Step: Retrieve current rose inventory data, including key details such as total quantity, varieties (e.g., color, type), storage locations (e.g., warehouses), and freshness/expiration status (critical for perishable items).

Response: The current inventory data for roses includes a total quantity of 100. However, details such as varieties (color/type), storage locations (warehouses), and freshness/expiration status are not available through the current check_inventory tool, which only returns stock quantity.

> Entering new AgentExecutor chain...

Action:
```
{
  "action": "Final Answer",
  "action_input": "无法完成库存分析以过滤不可用玫瑰（如损坏、过期或预分配）并确认实际可发货数量，因为当前`check_inventory`工具仅返回玫瑰总库存数量（100），未提供品种、存储位置、新鲜度/过期状态或预分配情况等关键细节。"
}
```

> Finished chain.
*****

Step: Analyze the inventory to filter out unavailable stock (e.g., damaged, expired, or pre-allocated roses) and confirm the actual available quantity for shipping.

Response: 无法完成库存分析以过滤不可用玫瑰（如损坏、过期或预分配）并确认实际可发货数量，因为当前`check_inventory`工具仅返回玫瑰总库存数量（100），未提供品种、存储位置、新鲜度/过期状态或预分配情况等关键细节。

> Entering new AgentExecutor chain...

Action:
```
{
  "action": "Final Answer",
  "action_input": "为了完成运输安排，请提供以下信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。"
}
```

> Finished chain.
*****

Step: Gather essential shipping requirements from the user or relevant sources, including customer demand (quantity needed), desired delivery date, preferred shipping method (e.g., express, standard), and any special instructions (e.g., temperature control, packaging).

Response: 为了完成运输安排，请提供以下信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。

> Entering new AgentExecutor chain...

Action:
```
{
  "action": "Final Answer",
  "action_input": "为了评估库存与运输需求的可行性，请您提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。"
}
```

> Finished chain.
*****

Step: Compare the available inventory with the shipping requirements to assess feasibility: check if the stock quantity is sufficient to meet demand and if the delivery timeline can be achieved given storage locations and shipping methods.

Response: 为了评估库存与运输需求的可行性，请您提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Final Answer",
  "action_input": "为了推进库存分配及运输计划制定，请提供以下运输需求信息：1. 客户所需玫瑰数量；2. 期望交货日期；3. 首选运输方式（如快递、标准）；4. 特殊说明（如温度控制、包装要求）。待获取这些信息后，方可评估可行性并执行后续步骤。"
}
```

> Finished chain.
*****

Step: If feasible, allocate stock using a logical strategy (e.g., FIFO for freshness, closest warehouse for faster delivery) and draft a shipping plan with details like origin warehouse, carrier, estimated delivery time, tracking information, and handling instructions.

Response: 为了推进库存分配及运输计划制定，请提供以下运输需求信息：1. 客户所需玫瑰数量；2. 期望交货日期；3. 首选运输方式（如快递、标准）；4. 特殊说明（如温度控制、包装要求）。待获取这些信息后，方可评估可行性并执行后续步骤。

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Final Answer",
  "action_input": "为了评估库存与运输需求的可行性并处理可能的不可行情况，请您提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。待获取这些信息后，方可进一步分析并提出替代方案（如延期交货、替换品种或调整时间）。"
}
```

> Finished chain.
*****

Step: If not feasible (e.g., insufficient stock, unable to meet delivery date), propose alternatives such as backordering, substituting with similar rose varieties, or adjusting the delivery timeline, and revise the plan accordingly.

Response: 为了评估库存与运输需求的可行性并处理可能的不可行情况，请您提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。待获取这些信息后，方可进一步分析并提出替代方案（如延期交货、替换品种或调整时间）。

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Final Answer",
  "action_input": "当前玫瑰库存总数量为100，但缺少品种（颜色/类型）、存储位置（仓库）、新鲜度/过期状态及预分配情况等关键细节，无法过滤不可用库存（如损坏、过期或预分配）以确认实际可发货数量。为了评估库存与运输需求的可行性并制定最终运输计划（或修订替代方案），请提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。待获取这些信息后，方可进一步分析并给出清晰、可操作的响应。"
}
```

> Finished chain.
*****

Step: Compile the inventory check results (available stock, key constraints) and the final shipping plan (or revised alternatives) into a clear, actionable response for the user.
<END_OF_PLAN>

Response: 当前玫瑰库存总数量为100，但缺少品种（颜色/类型）、存储位置（仓库）、新鲜度/过期状态及预分配情况等关键细节，无法过滤不可用库存（如损坏、过期或预分配）以确认实际可发货数量。为了评估库存与运输需求的可行性并制定最终运输计划（或修订替代方案），请提供以下运输需求信息：1. 客户需要的玫瑰数量；2. 期望的交货日期；3. 首选的运输方式（如快递、标准）；4. 任何特殊说明（如温度控制、包装要求）。待获取这些信息后，方可进一步分析并给出清晰、可操作的响应。
> Finished chain.
"""

# 运行Agent解决新问题（完善需求）
# agent.run("查查玫瑰花的库存然后给出50朵玫瑰花的价格和当天的配送方案！")
"""
> Entering new PlanAndExecute chain...
steps=[Step(value='Check the current inventory of玫瑰花 to confirm if there are at least 50 units available.'), Step(value='If the inventory is sufficient (≥50), retrieve the pricing information for 50朵玫瑰花 (accounting for any bulk discounts or standard per-unit rates).'), Step(value='Retrieve the same-day delivery方案, including key details such as cut-off times for placing orders, available delivery slots, coverage areas, and any additional delivery fees.'), Step(value="Compile the inventory status, price for 50朵玫瑰花, and same-day delivery details to respond to the user's original question.\n<END_OF_PLAN>")]

> Entering new AgentExecutor chain...

Action:
```
{
  "action": "check_inventory",
  "action_input": {
    "flower_type": "玫瑰花"
  }
}
```check_inventory

Observation: 100
Thought:
Action:
```
{
  "action": "Final Answer",
  "action_input": "The current inventory of玫瑰花 is 100 units, which is at least 50 units available."
}
```

> Finished chain.
*****

Step: Check the current inventory of玫瑰花 to confirm if there are at least 50 units available.

Response: The current inventory of玫瑰花 is 100 units, which is at least 50 units available.

> Entering new AgentExecutor chain...

Action:
```
{
  "action": "Final Answer",
  "action_input": "To calculate the pricing for 50朵玫瑰花, please provide the base price per unit and any applicable markup percentage (or bulk discount rate, which can be input as a negative markup). This information is required to use the calculate_price tool and retrieve the final cost."
}
```

> Finished chain.
*****

Step: If the inventory is sufficient (≥50), retrieve the pricing information for 50朵玫瑰花 (accounting for any bulk discounts or standard per-unit rates).

Response: To calculate the pricing for 50朵玫瑰花, please provide the base price per unit and any applicable markup percentage (or bulk discount rate, which can be input as a negative markup). This information is required to use the calculate_price tool and retrieve the final cost.

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Final Answer",
  "action_input": "无法通过现有工具（check_inventory 库存查询、calculate_price 价格计算）获取当天配送方案的细节（下单截止时间、可用配送时段、覆盖区域、额外配送费）。建议直接联系供应商或查看其配送政策文档以获取准确信息。"
}
```

> Finished chain.
*****

Step: Retrieve the same-day delivery方案, including key details such as cut-off times for placing orders, available delivery slots, coverage areas, and any additional delivery fees.

Response: 无法通过现有工具（check_inventory 库存查询、calculate_price 价格计算）获取当天配送方案的细节（下单截止时间、可用配送时段、覆盖区域、额外配送费）。建议直接联系供应商或查看其配送政策文档以获取准确信息。

> Entering new AgentExecutor chain...
Action:
```
{
  "action": "Final Answer",
  "action_input": "Inventory status: The current inventory of玫瑰花 is 100 units, which is sufficient for 50 units.\nPrice for 50朵玫瑰花: Cannot be calculated as the base price per unit and applicable markup percentage (or bulk discount rate) are not provided. Please provide these details to use the calculate_price tool.\nSame-day delivery details: Cannot be retrieved via existing tools (check_inventory, calculate_price).建议直接联系供应商或查看其配送政策文档以获取准确信息（包括下单截止时间、可用配送时段、覆盖区域、额外配送费等）。"
}
```

> Finished chain.
*****

Step: Compile the inventory status, price for 50朵玫瑰花, and same-day delivery details to respond to the user's original question.
<END_OF_PLAN>

Response: Inventory status: The current inventory of玫瑰花 is 100 units, which is sufficient for 50 units.
Price for 50朵玫瑰花: Cannot be calculated as the base price per unit and applicable markup percentage (or bulk discount rate) are not provided. Please provide these details to use the calculate_price tool.
Same-day delivery details: Cannot be retrieved via existing tools (check_inventory, calculate_price).建议直接联系供应商或查看其配送政策文档以获取准确信息（包括下单截止时间、可用配送时段、覆盖区域、额外配送费等）。
> Finished chain.
"""