"""Agent 抽象基类模块."""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
from backend.services.llm_client import LLMClient


class BaseAgent(ABC):
    """所有智能体的抽象基类。

    定义了智能体的基本接口，所有具体智能体都应继承此类并实现 run 方法。

    Attributes:
        llm: LLM 客户端实例，用于调用大语言模型
        name: 智能体名称，用于日志和标识
        temperature: 模型温度参数，控制输出随机性
        logger: 日志记录器
    """

    def __init__(self, llm_client: LLMClient, name: str, temperature: float = 0.7):
        """初始化智能体。

        Args:
            llm_client: LLM 客户端实例
            name: 智能体名称
            temperature: 模型温度参数，默认 0.7
        """
        self.llm = llm_client
        self.name = name
        self.temperature = temperature
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行智能体核心任务。

        Args:
            context: 上游智能体传递的上下文数据，包含请求参数和前置结果

        Returns:
            当前智能体的处理结果，以字典形式返回供下游智能体使用
        """
        pass