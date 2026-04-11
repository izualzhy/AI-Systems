#!/usr/bin/env python
# coding=utf-8
import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LiteLlm, LlmRequest, LlmResponse

ark_ds_model = LiteLlm(
    model=os.environ["ARK_DS32_WITH_PROVIDER"],
    api_key=os.environ["ARK_API_KEY"],
    api_base=os.environ["ARK_API_URL"]
)

silicon_ds_model = LiteLlm(
    model=os.environ["SILICON_FLOW_DSR1_WITH_PROVIDER"],
    api_key=os.environ["SILICON_API_KEY"],
    api_base=os.environ["SILICON_API_URL"]
)

ark_db20_code_model = LiteLlm(
    model=os.environ["ARK_DB20_CODE_WITH_PROVIDER"],
    api_key=os.environ["ARK_API_KEY"],
    api_base=os.environ["ARK_API_URL"]
)

ark_seed20_model = LiteLlm(
    model=os.environ["ARK_SEED20_PRO_WITH_PROVIDER"],
    api_key=os.environ["ARK_API_KEY"],
    api_base=os.environ["ARK_API_URL"]
)

def log_before_call_llm(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    print(f"\n====== --- 发送给模型的请求 ---\n")
    print(f"\n====== callback_context\n: {callback_context}")
    print(f"\n====== llm_request\n：{llm_request}")

    return None # 返回 None 表示继续正常执行

def log_after_call_llm(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    print(f"--- 模型返回的响应 ---")
    print(f"callback_context: {callback_context}")
    print(f"llm_response：{llm_response}")

    return None