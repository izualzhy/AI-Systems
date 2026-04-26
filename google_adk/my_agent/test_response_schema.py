#!/usr/bin/env python
# coding=utf-8


from google.adk.models.lite_llm import LiteLlm
from google.adk.models import LlmRequest
from google.genai.types import Content, Part
import asyncio
import json

from google_adk.adk_utils import *


async def test_json_output():
    models = [ark_ds_model, silicon_ds_model, ark_db20_code_model, ark_seed20_model, ark_glm47_model,
              ark_db15_lite_32k_model]

    for model in models:
        print(f"Testing model: {model}")
        try:
            llm_request = LlmRequest(
                contents=[Content(parts=[Part(text="Return a JSON object with key 'test' and value 'hello'")])],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": {"type": "object", "properties": {"test": {"type": "string"}}}
                }
            )
            async for response in model.generate_content_async(llm_request=llm_request):
                if response.content and response.content.parts:
                    for part in response.content.parts:
                        if part.text:
                            print(part.text)
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test_json_output())