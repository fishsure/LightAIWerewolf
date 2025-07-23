# This module provides a real interface for LLM API calls using OpenAI GPT-4o.
# 该模块为LLM API调用的真实接口，使用OpenAI GPT-4o。

import os
import openai

# 可自定义API Key和Base URL，留空则使用环境变量或默认
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
MODEL_NAME = "gpt-4o"

def call_llm_api(prompt: str) -> str:
    """
    Call the OpenAI GPT-4o API with the given prompt and return the response.
    prompt: 英文prompt
    return: 英文回复
    """
    try:
        # 新版openai>=1.0.0的用法
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY or None,
            base_url=OPENAI_BASE_URL or None
        )
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM API ERROR] {e}")
        return "Sorry, I cannot respond right now." 