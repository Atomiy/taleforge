"""LLM 客户端模块 - 封装大语言模型 API 调用。"""

import json
import logging
import requests
from sseclient import SSEClient
from typing import AsyncIterator, Dict, Any

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端 - 封装 DeepSeek API 调用。

    支持流式和非流式两种调用模式，所有智能体共用同一客户端，
    统一处理错误和超时，每个智能体可独立配置 temperature 和 max_tokens。

    Attributes:
        api_key: API Key
        base_url: API 基础地址
        headers: 请求头，包含 Authorization 和 Content-Type
    """

    def __init__(self, api_key: str = "", base_url: str = "https://api.deepseek.com/v1"):
        """初始化 LLM 客户端。

        Args:
            api_key: DeepSeek API Key
            base_url: API 基础地址，默认 https://api.deepseek.com/v1
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat(self, messages: list, model: str = "deepseek-chat",
                   temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """非流式调用 LLM API。

        Args:
            messages: 消息列表，格式为 [{"role": "...", "content": "..."}]
            model: 模型名称，默认 deepseek-chat
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大输出 token 数

        Returns:
            模型返回的完整文本

        Raises:
            Exception: 网络错误或 API 调用失败
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            raise

    async def chat_streaming(self, messages: list, model: str = "deepseek-chat",
                             temperature: float = 0.7, max_tokens: int = 4096) -> AsyncIterator[str]:
        """流式调用 LLM API。

        Args:
            messages: 消息列表，格式为 [{"role": "...", "content": "..."}]
            model: 模型名称，默认 deepseek-chat
            temperature: 温度参数，控制输出随机性
            max_tokens: 最大输出 token 数

        Yields:
            文本片段，逐块返回

        Raises:
            Exception: 网络错误或 API 调用失败
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }

        try:
            logger.info(f"LLM streaming request: model={model}, messages_count={len(messages)}, max_tokens={max_tokens}")
            logger.info(f"System: {(messages[0]['content'][:100] if messages else '')}")
            logger.info(f"User msg (first 500): {(messages[-1]['content'][:500] if len(messages)>1 else '')}")
            response = requests.post(url, headers=self.headers, json=payload,
                                     stream=True, timeout=120)
            response.raise_for_status()
            logger.info(f"LLM streaming response status: {response.status_code}")
            client = SSEClient(response)
            event_count = 0
            for event in client.events():
                event_count += 1
                if event.data == "[DONE]":
                    break
                try:
                    data = json.loads(event.data)
                    content = data["choices"][0]["delta"].get("content", "")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError):
                    continue
            logger.info(f"LLM streaming complete: {event_count} SSE events received")
        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            raise