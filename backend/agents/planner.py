"""策划智能体模块 - 生成故事大纲。"""

import json
from typing import Dict, Any
from backend.agents.base import BaseAgent
from backend.config import PLANNER_TEMPERATURE


STRUCTURE_TEMPLATES = {
    "短篇小说": "冲突驱动四阶段：引子与触发(20%)→发展与深入(40%)→高潮与抉择(25%)→结局与回响(15%)",
    "中篇小说": "冲突驱动四阶段：引子与触发(20%)→发展与深入(40%)→高潮与抉择(25%)→结局与回响(15%)",
    "日常小短文": "场景切片结构：场景铺陈(30%)→细节观察(35%)→情感流动(25%)→意境收束(10%)",
    "散文": "场景切片结构：场景铺陈(30%)→细节观察(35%)→情感流动(25%)→意境收束(10%)",
    "剧本": "三幕结构：铺垫(25%)→对抗(50%)→解决(25%)",
    "童话": "简化英雄之旅：平凡世界(15%)→冒险召唤(15%)→考验与盟友(40%)→最终考验(20%)→归来与馈赠(10%)",
    "诗歌": "诗歌意象结构：起兴(开篇点题，奠定基调20%)→展开(层层递进，丰富意象50%)→收束(升华主题，余韵悠长30%)",
    "史诗": "英雄之旅十二阶段（约瑟夫·坎贝尔）：\n启程(30%)-1.平凡世界→2.冒险召唤→3.拒绝召唤→4.遇见导师→5.跨越门槛→6.鲸鱼之腹\n启蒙(40%)-7.试炼之路→8.遇见女神→9.诱惑考验→10.与天父和解→11.神化→12.终极恩赐\n回归(30%)-13.拒绝回归→14.魔法飞行→15.外界救援→16.跨越回归门槛→17.两个世界主宰→18.自由生活",
    "悬疑推理": "悬念结构：谜团呈现(15%)→调查推进(35%)→反转与危机(30%)→真相揭露(20%)",
    "科幻": "探索发现结构：异常发现(20%)→深入探索(35%)→危机爆发(25%)→领悟与抉择(20%)",
    "奇幻": "弗莱塔格金字塔五幕结构（古斯塔夫·弗莱塔格）：\n1.开端(Exposition 15%)-介绍背景、人物、初始冲突\n2.发展(Rising Action 35%)-情节推进、矛盾激化、伏笔埋设\n3.高潮(Climax 25%)-最紧张时刻、决定性对抗\n4.回落(Falling Action 15%)-高潮后果、伏笔回收\n5.结局(Denouement 10%)-新平衡建立、余韵悠长"
}

CONFLICT_TYPES = {
    "成长": "自我对抗",
    "选择": "自我对抗",
    "友情": "人际冲突",
    "亲情": "人际冲突",
    "爱情": "人际冲突",
    "冒险": "环境挑战",
    "生存": "环境挑战",
    "梦想": "理想与现实",
    "悬疑": "秘密与真相",
    "推理": "秘密与真相"
}


class PlannerAgent(BaseAgent):
    """策划智能体 - 根据用户输入生成故事大纲。

    根据用户提供的主题、体裁、风格，选择合适的叙事结构模板和冲突类型，
    生成结构化的故事大纲，包含标题、阶段划分、章节列表等。
    """

    def __init__(self, llm_client):
        """初始化策划智能体。"""
        super().__init__(llm_client, "planner", PLANNER_TEMPERATURE)

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成故事大纲。

        Args:
            context: 包含用户请求的上下文数据

        Returns:
            包含大纲信息的字典，格式为 {"outline": {...}}
        """
        request = context["request"]
        theme = request.theme
        genre = request.genre
        style = request.style
        length = request.length
        background = getattr(request, 'background', '')
        perspective = getattr(request, 'perspective', '第三人称全知')
        conflict = getattr(request, 'conflict', '人与人')
        mood = getattr(request, 'mood', '轻松愉快')
        outline = getattr(request, 'outline', '')
        continuation_mode = getattr(request, 'continuation_mode', 'next_chapter')
        world_setting = getattr(request, 'world_setting', '')
        foreshadowings = getattr(request, 'foreshadowings', [])

        previous_story = context.get("previous_story")
        is_continuation = bool(previous_story)

        structure_template = STRUCTURE_TEMPLATES.get(genre.strip(), STRUCTURE_TEMPLATES["短篇小说"])
        conflict_type = conflict

        background_info = f"\n- 故事背景：{background}" if background else ""
        outline_info = f"\n- 故事梗概：{outline}" if outline else ""
        world_setting_info = f"\n- 世界观设定：{world_setting}" if world_setting else ""
        foreshadowings_info = f"\n- 伏笔清单：{', '.join(foreshadowings)}" if foreshadowings else ""

        # 卷规划信息
        volume_plan = context.get("volume_plan")
        volume_plan_info = ""
        if volume_plan:
            vol_fw = "\n".join(f"  - {f}" for f in volume_plan.get("foreshadowings", [])) if volume_plan.get("foreshadowings") else "  无"
            vol_chars = "\n".join(f"  - {c.get('name','')}（{c.get('identity','')}）：{c.get('brief','')}" for c in volume_plan.get("characters", [])) if volume_plan.get("characters") else "  无"
            # 跨章人物出场表
            chapter_chars = volume_plan.get("chapter_characters", [])
            if chapter_chars:
                cc_rows = "\n".join(f"  | 第{cc.get('chapter_num','?')}章 {cc.get('title','')} | {'、'.join(cc.get('characters',[])) or '（无）'} |" for cc in chapter_chars)
                cc_table = f"""
- 跨章人物出场表（硬约束）：
  | 章节 | 出场角色 |
  |------|----------|
{cc_rows}

  出场规则：
  - 角色首次登场前必须在前面章节有"埋线"（被他人提及、留下痕迹等）
  - 未在出场表中列出的角色不能在该章出现
  - 若出场表与卷出场人物列表冲突，以出场表为准"""
            else:
                cc_table = ""
            # 构建角色硬约束区块（含方案B：参与类型 + 出场目的 + 角色弧线）
            if chapter_chars:
                allowed_set = set()
                for entry in chapter_chars:
                    for name in entry.get("characters", []):
                        allowed_set.add(name)
                allowed_list = "、".join(sorted(allowed_set))
                # 参与类型表 + 出场目的表
                participation = volume_plan.get("chapter_participation", {})
                purpose = volume_plan.get("chapter_purpose", {})
                part_lines = []
                for cc in chapter_chars:
                    cn = cc.get('chapter_num', '?')
                    p_map = participation.get(cn, {})
                    purpose_map = purpose.get(cn, {})
                    if p_map:
                        parts = []
                        for n, t in p_map.items():
                            purpose_str = purpose_map.get(n, [])
                            purpose_str = "/".join(purpose_str) if purpose_str else "-"
                            parts.append(f"{n}({t},目的={purpose_str})")
                        part_lines.append(f"    - 第{cn}章：{'、'.join(parts)}")
                part_block = "\n".join(part_lines) if part_lines else ""
                # 角色弧线表
                char_arcs = volume_plan.get("character_arcs", {})
                arc_lines = []
                for cname, arc_map in char_arcs.items():
                    arc_str = " → ".join(f"第{k}章: {v}" for k, v in sorted(arc_map.items()))
                    arc_lines.append(f"    - {cname}：{arc_str}")
                arc_block = "\n".join(arc_lines) if arc_lines else ""
                scope_block = f"""
## *** 硬约束：角色使用范围 + 参与类型 + 出场目的（优先级最高）***

本卷可出场的全部角色（完整名单，共{len(allowed_set)}人）：
{allowed_list}
{f"""
- 角色弧线（状态变化轨迹）：
{arc_block}
""" if arc_block else ""}
角色参与类型与出场目的（主动=须有对话/动作/决策，被动=仅可被他人提及，本人不出场不发声，缺席=不得出现）：
{part_block if part_block else '  全主动（默认）'}

**写作规则（必须遵守）**：
1. **只允许使用上述名单中的角色**。不得创建或提及名单之外的新角色。
2. **主动角色**：本章必须有至少一段主动描写（对话、动作、决策、内心活动）。
3. **被动角色**：本人不出场，不发出任何声音，不做出任何主动行为。其存在和状态变化**仅允许**通过以下方式体现：
   - 其他角色口头提及（如"赵海的脑波又异常了"）
   - 监控数据/屏幕显示/仪器读数
   - 环境痕迹（录音回放、视频记录、留下的文字）
   禁止：本人出场（无论现实还是幻觉）、发出任何声音（包括呓语/梦话/破碎音节）、被控制下的动作或说话。
   **关键：被动角色的名字不得出现在本章大纲的「关键剧情」和「场景描述」中。** 被动角色的状态只能通过主动角色的视角间接呈现。
4. **被动角色按出场目的分类约束**：
   - 推进剧情(信息提供): 状态数据被他人观察/分析，不得本人说话传递
   - 推进剧情(冲突制造): 状态变化引发他人争论，不得本人主动制造
   - 推进剧情(催化事件): 状态恶化/好转促使他人决策，不得本人做决策
   - 塑造人物/表达主题/营造氛围: 作为被观察客体呈现即可
5. **缺席角色**：本章不得以任何形式出现。
6. 上述名单之外的任何角色名出现在大纲中，均视为无效大纲，必须重写。"""
            else:
                scope_block = ""
            vol_plan_info = f"""
## 卷规划（最高优先级参考）
- 卷职责：{volume_plan.get('responsibility', '未定义')}
- 卷大纲：{volume_plan.get('outline', '未定义')}
- 与上卷衔接：{volume_plan.get('connection_to_prev', '无')}
- 对下卷铺垫：{volume_plan.get('connection_to_next', '无')}
- 本卷出场人物：
{vol_chars}
- 本卷伏笔：
{vol_fw}
{cc_table}
{scope_block}
注意：卷规划优先级高于所有其他信息。生成的章节必须服务于本卷的职责和进度。"""

        continuation_info = ""
        if is_continuation and previous_story:
            prev_content = previous_story.get('content', '') or ''
            prev_end = prev_content[-400:] if len(prev_content) > 400 else prev_content
            prev_start = prev_content[:300] if len(prev_content) > 300 else prev_content
            prev_title = previous_story.get('title', '')
            continuation_info = f"""
## 前一篇故事信息
- 上章标题：{prev_title}
- 上章开头（300字）：{prev_start}
- **上章结尾（400字）—— 新章节必须从这点之后开始**：{prev_end}
- 已有角色：{', '.join([c['name'] if isinstance(c, dict) else c.name for c in previous_story.get('characters', [])]) if previous_story.get('characters') else '无'}
- 世界观设定：{previous_story.get('world_setting', '')}
- 伏笔清单：{', '.join(previous_story.get('foreshadowings', [])) if previous_story.get('foreshadowings') else '无'}

## 续写模式
- 模式：{continuation_mode}
- 要求：延续前一篇的情节和风格，保持人物一致性，适当回收伏笔并设置新伏笔

## *** 硬约束：进度锚点（优先级最高）***
1. 新章节的起始状态，必须**等于或晚于**上章末尾最后一句所述的状态。新章节开篇时，主角在哪里、在做什么、冲突进行到什么程度——都必须以上章结尾为准。
2. 严禁任何形式的"**时间回溯**"或"**场景重置**"。如果上章结尾主角已经坐进逃生舱出发，新章节就不能再写"主角还在侦察船指挥室"。如果上章结尾主角已经昏倒，新章节就不能让主角还站着。
3. 本章结尾时，主角/核心冲突的位置和状态必须比本章开头有明显推进。
4. 新章节的标题**不能与上一章重复**。"""

        if genre == "诗歌":
            prompt = f"""你是一位专业的诗歌创作策划师，擅长设计 {style} 风格的诗歌结构，尤其擅长史诗诗歌的续写。

## 用户输入
- 主题：{theme}
- 体裁：诗歌
- 风格：{style}
- 目标字数：{length} 字
- 情感基调：{mood}{background_info}{outline_info}{world_setting_info}{foreshadowings_info}{volume_plan_info}

{continuation_info}

## 可用结构模板
{structure_template}

## 叙事理论指导
史诗创作遵循约瑟夫·坎贝尔的「英雄之旅」十二阶段：
- 启程阶段(30%)：英雄离开平凡世界，踏入冒险
- 启蒙阶段(40%)：经历试炼、蜕变、获得终极力量
- 回归阶段(30%)：带着智慧重返日常，救赎世界

## 伏笔管理规则
1. 每首诗至少设置3个伏笔，在不同章节埋设
2. 伏笔必须有回收计划，明确在哪个章节回收
3. 伏笔要自然融入情节，不显得突兀
4. 续写时要回收前作伏笔并设置新伏笔

## 任务
请为这首诗歌设计一份详细的创作大纲，以 JSON 格式输出：

{{
  "title": "诗歌标题",
  "structure_type": "{style}诗歌结构",
  "conflict_type": "{conflict_type}",
  "stages": [
    {{
      "name": "阶段名称",
      "ratio": "占比（如20%）",
      "plot_points": ["关键意象", "情感表达"],
      "word_count": "建议字数"
    }}
  ],
  "chapters": [
    {{
      "chapter_num": 1,
      "title": "诗篇标题",
      "stage": "所属阶段",
      "key_events": ["主要意象", "情感基调"],
      "foreshadowings": ["本章设置的伏笔"]
    }}
  ],
  "poetic_elements": {{
    "main_images": ["核心意象1", "核心意象2"],
    "rhyme_pattern": "押韵方式",
    "rhythm": "节奏特点",
    "metaphor": "主要隐喻"
  }},
  "foreshadowings": ["本诗设置的伏笔清单"],
  "foreshadowing_map": [
    {{
      "foreshadowing": "伏笔内容",
      "plant_chapter": "埋设章节",
      "reveal_chapter": "回收章节",
      "significance": "伏笔意义"
    }}
  ]
}}

注意：大纲要具体、可执行，写作Agent能直接根据此大纲创作诗歌。如果是续写，请确保情节连贯，适当回收前作伏笔。只输出JSON，不要其他内容。"""
        else:
            prompt = f"""你是一位专业的故事策划师，擅长为 {genre} 设计故事结构，尤其擅长长篇故事的续写。

## 用户输入
- 主题：{theme}
- 体裁：{genre}
- 风格：{style}
- 目标字数：{length} 字
- 叙事视角：{perspective}
- 冲突类型：{conflict}
- 情感基调：{mood}{background_info}{outline_info}{world_setting_info}{foreshadowings_info}{volume_plan_info}

{continuation_info}

## 可用结构模板
{structure_template}

## 叙事理论指导
{'' if genre != '奇幻' else '奇幻创作遵循弗莱塔格金字塔五幕结构（古斯塔夫·弗莱塔格）：\n- 开端(Exposition)：介绍背景、人物、初始冲突\n- 发展(Rising Action)：情节推进、矛盾激化、伏笔埋设\n- 高潮(Climax)：最紧张时刻、决定性对抗\n- 回落(Falling Action)：高潮后果、伏笔回收\n- 结局(Denouement)：新平衡建立、余韵悠长\n\n'}故事创作应遵循因果逻辑：每个事件都应有合理的动机和后果。角色的行为必须与其性格和处境相符。

## 伏笔管理规则
1. 每个故事至少设置3个伏笔，在不同章节埋设
2. 伏笔必须有回收计划，明确在哪个章节回收
3. 伏笔要自然融入情节，不显得突兀
4. 伏笔的回收要有情感冲击力，不能草草了事
5. 续写时要回收前作伏笔并设置新伏笔

## 章节驱动力设计原则
每章的核心推动力应来自**事件或外部变化**，而非某个角色的内部状态。

- 好的驱动力：「发生了一件事 → 所有角色对此做出反应 → 自然引出各自的行动和对话」
- 不好的驱动力：「某个角色生病/情绪变化 → 其他角色围着他转 → 叙事变得被动」
- 规划每章时，先问「这章发生了一件什么事」，而不是「这章某某做了什么」

这条原则适用于所有体裁。具体的结构形态请根据当前故事的风格自由调整。

## 任务
请为这个故事设计一份详细的大纲，以 JSON 格式输出：

{{
  "title": "故事标题",
  "structure_type": "{genre}结构",
  "conflict_type": "{conflict_type}",
  "stages": [
    {{
      "name": "阶段名称",
      "ratio": "占比（如20%）",
      "plot_points": ["关键情节节点1", "关键情节节点2"],
      "word_count": "建议字数"
    }}
  ],
  "chapters": [
    {{
      "chapter_num": 1,
      "title": "章节标题",
      "stage": "所属阶段",
      "key_events": ["本章关键事件"],
      "foreshadowings": ["本章设置的伏笔"]
    }}
  ],
  "foreshadowings": ["本故事设置的伏笔清单"],
  "foreshadowing_map": [
    {{
      "foreshadowing": "伏笔内容",
      "plant_chapter": "埋设章节",
      "reveal_chapter": "回收章节",
      "significance": "伏笔意义"
    }}
  ]
}}

注意：大纲要具体、可执行，写作Agent能直接根据此大纲创作。如果是续写，请确保情节连贯，适当回收前作伏笔。只输出JSON，不要其他内容。"""

        messages = [{"role": "system", "content": "你是专业故事策划师，擅长长篇故事的构思和续写，能够巧妙设置和回收伏笔"}, {"role": "user", "content": prompt}]
        result = await self.llm.chat(messages, temperature=self.temperature, max_tokens=2000)

        try:
            outline = json.loads(result)
            self.logger.info("[Planner] Outline generated: %s", outline.get("title"))
            return {"outline": outline}
        except json.JSONDecodeError:
            self.logger.warning("[Planner] JSON parse failed, using fallback")
            return {"outline": {"title": theme, "structure_type": genre, "conflict_type": conflict_type, "stages": [], "chapters": []}}