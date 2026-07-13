"""LLM 客户端模块 - 封装大语言模型 API 调用。"""

import json
import logging
import httpx
from typing import AsyncIterator, Dict, Any

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端 - 封装 DeepSeek API 调用。

    使用 httpx.AsyncClient 实现真正的异步请求，
    避免阻塞 asyncio 事件循环。

    Attributes:
        api_key: API Key
        base_url: API 基础地址
        headers: 请求头
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url

    def _build_payload(self, messages: list, model: str, temperature: float,
                       max_tokens: int, stream: bool = False) -> dict:
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: list, model: str = "deepseek-chat",
                   temperature: float = 0.7, max_tokens: int = 4096) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = self._build_payload(messages, model, temperature, max_tokens)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, headers=self._headers(), json=payload)
                resp.raise_for_status()
                result = resp.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise

    async def chat_streaming(self, messages: list, model: str = "deepseek-chat",
                             temperature: float = 0.7, max_tokens: int = 4096) -> AsyncIterator[str]:
        url = f"{self.base_url}/chat/completions"
        payload = self._build_payload(messages, model, temperature, max_tokens, stream=True)

        logger.info(f"LLM streaming request: model={model}, messages_count={len(messages)}, max_tokens={max_tokens}")
        if messages:
            logger.info(f"System: {(messages[0]['content'][:100])}")
        if len(messages) > 1:
            logger.info(f"User msg (first 500): {(messages[-1]['content'][:500])}")

        event_count = 0
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", url, headers=self._headers(), json=payload) as resp:
                    resp.raise_for_status()
                    logger.info(f"LLM streaming response status: {resp.status_code}")

                    async for line in resp.aiter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                event_count += 1
                                yield content
                        except (json.JSONDecodeError, KeyError):
                            continue
            logger.info(f"LLM streaming complete: {event_count} SSE events received")
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            raise
