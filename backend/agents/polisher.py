"""润色智能体模块 - 提升故事质量。"""

import json
from typing import Dict, Any
from backend.agents.base import BaseAgent
from backend.config import POLISHER_TEMPERATURE


class PolisherAgent(BaseAgent):
    """润色智能体 - 对初稿进行语言润色和质量把控。

    负责修正错别字和语病，提升语言表现力，确保风格统一，
    增强段落连贯性，并进行闭环一致性校验，检查角色言行是否符合设定。
    """

    def __init__(self, llm_client):
        """初始化润色智能体。"""
        super().__init__(llm_client, "polisher", POLISHER_TEMPERATURE)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """润色故事初稿。

        Args:
            context: 包含初稿、大纲、角色设定和用户请求的上下文数据

        Returns:
            包含润色后文本的字典，格式为 {"final": "..."}
        """
        draft = context.get("draft", "")
        # 如果草稿为空或太短，跳过润色，直接返回草稿
        if not draft or len(draft.strip()) < 50:
            self.logger.warning(f"[Polisher] Draft too short ({len(draft)} chars) or empty, skipping polish")
            return {"final": draft}
        request = context["request"]
        outline = context.get("outline", {})
        characters = context.get("characters", [])

        outline_str = json.dumps(outline, ensure_ascii=False)
        chars_str = json.dumps(characters, ensure_ascii=False)

        prompt = f"""你是一位资深的文学编辑，擅长文本润色和质量把控。

## 待润色文本
{draft}

## 风格要求
{request.style}

## 故事大纲（用于上下文校验）
{outline_str}

## 角色设定（用于一致性检查）
{chars_str}

## 润色任务
1. 修正错别字和语病
2. 提升语言表现力（修辞、句式多样性）
3. 确保全文风格统一
4. 增强段落间的连贯性
5. 检查角色言行是否符合设定
6. 闭环一致性校验：对照角色设定和前情摘要，检查全文是否存在逻辑矛盾或设定偏离。如发现矛盾，必须在润色后的文本中直接修正。

## 输出要求
- 直接输出润色后的完整文本
- 不要添加评论或修改标记
- 保持原有格式"""

        messages = [{"role": "system", "content": "你是资深文学编辑"}, {"role": "user", "content": prompt}]
        result = await self.llm.chat(messages, temperature=self.temperature, max_tokens=4096)

        self.logger.info("[Polisher] Polishing complete")
        return {"final": result}