"""角色智能体模块 - 细化角色设定。"""

import json
from typing import Dict, Any
from backend.agents.base import BaseAgent
from backend.config import CHARACTER_TEMPERATURE


class CharacterAgent(BaseAgent):
    """角色智能体 - 细化角色设定，维护角色一致性。

    根据用户提供的简略角色信息或故事大纲，自动扩充为完整的角色深度模型，
    包含身份、驱动、矛盾、弧线四个维度，并标注角色在各阶段的状态变化。
    支持跨章人物出场表约束：只生成出场表中允许的角色。
    """

    def __init__(self, llm_client):
        """初始化角色智能体。"""
        super().__init__(llm_client, "character", CHARACTER_TEMPERATURE)

    def _build_scope_block(self, chapter_characters: list) -> str:
        """构建跨章人物出场表约束区块。

        Args:
            chapter_characters: 跨章人物出场表，格式为
                [{"chapter_num":1, "title":"x", "characters":["A","B"]}, ...]

        Returns:
            约束提示文本，若无可返回空字符串
        """
        if not chapter_characters:
            return ""

        # 从全部章节的出场表中提取去重的允许角色名
        allowed = set()
        for entry in chapter_characters:
            for name in entry.get("characters", []):
                allowed.add(name)

        # 生成按章节排列的表格
        rows = []
        for entry in chapter_characters:
            cn = entry.get("chapter_num", "?")
            title = entry.get("title", "")
            chars = "、".join(entry.get("characters", [])) or "（无）"
            rows.append(f"    | 第{cn}章 {title} | {chars} |")

        table = "\n".join(rows)
        allowed_list = sorted(allowed)

        return f"""
## *** 硬约束：角色出场范围（优先级最高）***
本卷设定了「跨章人物出场表」，只有下表列出的角色允许出场：

| 章节 | 出场角色 |
|------|----------|
{table}

本卷允许出场的全部角色（去重）：{', '.join(allowed_list)}

**规则（必须遵守）**：
1. 你**只能**设计上表「允许出场的全部角色」中存在的角色
2. 严禁创造任何不在该列表中的新角色
3. 如果上表中没有某角色，即使大纲暗示了它，也必须忽略
4. 已有角色中如果有不在该列表中的，必须从输出中移除"""

    def _filter_chars_by_scope(self, chars: list, chapter_characters: list) -> list:
        """根据出场表过滤角色，移除不在允许范围内的角色。

        Args:
            chars: LLM 返回的角色列表
            chapter_characters: 跨章人物出场表

        Returns:
            过滤后的角色列表
        """
        if not chapter_characters or not chars:
            return chars

        allowed = set()
        for entry in chapter_characters:
            for name in entry.get("characters", []):
                allowed.add(name)

        filtered = []
        for c in chars:
            name = c.get("name", "")
            if name in allowed:
                filtered.append(c)
            else:
                self.logger.warning("[Character] 移除超出出场表的角色: %s", name)
        return filtered

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """细化角色设定。

        Args:
            context: 包含用户请求和大纲信息的上下文数据

        Returns:
            包含角色设定列表的字典，格式为 {"characters": [...]}
        """
        request = context["request"]
        outline = context.get("outline", {})
        chapter_characters = context.get("chapter_characters", [])

        user_chars = request.characters or []
        existing_chars = context.get("existing_characters", [])
        outline_str = json.dumps(outline, ensure_ascii=False)
        scope_block = self._build_scope_block(chapter_characters)

        if existing_chars:
            existing_str = json.dumps(existing_chars, ensure_ascii=False)
            user_chars_str = json.dumps(user_chars, ensure_ascii=False) if user_chars else ""
            user_chars_block = f"""
## 用户自定义角色设定（包含详细的性格/动机/背景，必须优先保留）
{user_chars_str}
""" if user_chars_str else ""
            prompt = f"""你是一位专业的角色设计师，擅长创造立体、真实的角色。

## 已有角色（来自前文，必须保留）
{existing_str}
{user_chars_block}
## 故事大纲
{outline_str}
{scope_block}
## 任务
保留已有角色的全部设定（名称、身份、性格等不变），如有新角色出现则补充加入。
以 JSON 格式输出完整的角色设定表（包含所有已有角色和新角色）。

{{
  "characters": [
    {{
      "name": "角色名",
      "identity": "身份层：姓名、年龄、职业、外貌",
      "drive": "驱动层：核心动机和恐惧",
      "contradiction": "矛盾层：表面与内心的冲突",
      "arc": "弧线层：从XX到XX的变化",
      "stage_states": {{"阶段1": "该阶段角色的心理状态"}},
      "speaking_style": "说话风格特征"
    }}
  ]
}}

只输出JSON，不要其他内容。"""
        elif user_chars:
            chars_str = json.dumps(user_chars, ensure_ascii=False)
            prompt = f"""你是一位专业的角色设计师，擅长创造立体、真实的角色。

## 用户输入的角色
{chars_str}

## 故事大纲
{outline_str}
{scope_block}
## 任务
请完善角色设定，为每个角色增加深度，以 JSON 格式输出角色设定表：

{{
  "characters": [
    {{
      "name": "角色名",
      "identity": "身份层：姓名、年龄、职业、外貌",
      "drive": "驱动层：核心动机和恐惧",
      "contradiction": "矛盾层：表面与内心的冲突",
      "arc": "弧线层：从XX到XX的变化",
      "stage_states": {{"阶段1": "该阶段角色的心理状态"}},
      "speaking_style": "说话风格特征"
    }}
  ]
}}

只输出JSON，不要其他内容。"""
        else:
            prompt = f"""你是一位专业的角色设计师，擅长创造立体、真实的角色。

## 故事大纲
{outline_str}
{scope_block}
## 任务
请根据大纲主题设计合适的角色，以 JSON 格式输出角色设定表：

{{
  "characters": [
    {{
      "name": "角色名",
      "identity": "身份层：姓名、年龄、职业、外貌",
      "drive": "驱动层：核心动机和恐惧",
      "contradiction": "矛盾层：表面与内心的冲突",
      "arc": "弧线层：从XX到XX的变化",
      "stage_states": {{"阶段1": "该阶段角色的心理状态"}},
      "speaking_style": "说话风格特征"
    }}
  ]
}}

只输出JSON，不要其他内容。"""

        messages = [{"role": "system", "content": "你是专业角色设计师"}, {"role": "user", "content": prompt}]
        result = await self.llm.chat(messages, temperature=self.temperature, max_tokens=2000)

        try:
            data = json.loads(result)
            chars = data.get("characters", [])
            # 后置过滤：移除超出出场表的角色
            filtered = self._filter_chars_by_scope(chars, chapter_characters)
            removed = len(chars) - len(filtered)
            if removed > 0:
                self.logger.warning("[Character] 出场表过滤移除了 %d 个角色", removed)
            self.logger.info("[Character] Generated %d characters (filtered from %d)", len(filtered), len(chars))
            return {"characters": filtered}
        except json.JSONDecodeError:
            self.logger.warning("[Character] JSON parse failed")
            return {"characters": []}