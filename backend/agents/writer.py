"""写作智能体模块 - 生成故事正文。"""

import json
from typing import Dict, Any, AsyncIterator
from backend.agents.base import BaseAgent
from backend.config import WRITER_TEMPERATURE


class WriterAgent(BaseAgent):
    """写作智能体 - 根据大纲和角色设定生成故事正文。

    支持分段/分章节写作，严格遵循大纲中的阶段占比和情节节点，
    保持角色言行与设定一致，支持流式输出。
    """

    def __init__(self, llm_client):
        """初始化写作智能体。"""
        super().__init__(llm_client, "writer", WRITER_TEMPERATURE)
        self.full_draft = ""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成故事初稿（非流式）。

        Args:
            context: 包含大纲、角色设定和用户请求的上下文数据

        Returns:
            包含故事初稿的字典，格式为 {"draft": "..."}
        """
        request = context["request"]
        outline = context.get("outline", {})
        characters = context.get("characters", [])

        outline_str = json.dumps(outline, ensure_ascii=False)
        chars_str = json.dumps(characters, ensure_ascii=False)

        prompt = self._build_prompt(request, outline_str, chars_str)

        messages = [{"role": "system", "content": f"你是专业{request.genre}作家"}, {"role": "user", "content": prompt}]
        result = await self.llm.chat(messages, temperature=self.temperature, max_tokens=4096)

        self.full_draft = result
        self.logger.info("[Writer] Draft generated, %d characters", len(result))
        return {"draft": result}

    async def run_streaming(self, context: Dict[str, Any]) -> AsyncIterator[str]:
        """流式生成故事初稿。"""
        try:
            request = context["request"]
            outline = context.get("outline", {})
            characters = context.get("characters", [])
            previous_story = context.get("previous_story")
            chapter_number = context.get("chapter_number")
            volume_plan = context.get("volume_plan")

            outline_str = json.dumps(outline, ensure_ascii=False)
            chars_str = json.dumps(characters, ensure_ascii=False)

            # 安全处理续写上下文：如果 previous_story 没有有效内容，降级为非续写模式
            prev_story_str = ""
            if previous_story:
                try:
                    prev_content = previous_story.get('content', '') or ''
                    if len(prev_content.strip()) > 50:
                        prev_story_str = json.dumps(previous_story, ensure_ascii=False)
                except Exception:
                    self.logger.warning("[Writer] Invalid previous_story, falling back to non-continuation mode")

            max_tokens_value = 8192 if request.genre == "诗歌" else 4096

            system_prompt = self._build_system_context(request, outline_str, chars_str, prev_story_str, chapter_number, volume_plan)
            num_info = f"第{chapter_number}章" if chapter_number else "故事"
            user_prompt = f"请创作{num_info}的正文。严格按照上述要求的格式和规范输出，禁止输出任何非正文内容。"
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

            self.full_draft = ""
            async for chunk in self.llm.chat_streaming(messages, temperature=self.temperature, max_tokens=max_tokens_value):
                self.full_draft += chunk
                yield chunk

            if not self.full_draft:
                self.logger.error("[Writer] Streaming completed but full_draft is empty!")
            self.logger.info("[Writer] Streaming draft complete, %d characters", len(self.full_draft))
        except Exception as e:
            self.logger.error(f"[Writer] Streaming failed: {e}")
            raise

    def get_full_draft(self) -> str:
        """获取完整的故事初稿。

        Returns:
            完整的故事文本
        """
        return self.full_draft

    def _build_system_context(self, request, outline_str, chars_str, prev_story_str="", chapter_number=None, volume_plan=None) -> str:
        """构建系统提示词，承载所有上下文信息。

        采用"三层层级控制"：
        - 战略层（大纲）: 本章必须覆盖的剧情节拍 → 最高优先级
        - 战术层（过渡）: 仅控制新章第一段（约200字）的衔接 → 超强约束但限范围
        - 自由层（风格）: 上章完整结尾作为文风参考 → 弱约束，不强制复现

        Args:
            request: 用户请求对象
            outline_str: 大纲JSON字符串
            chars_str: 角色设定JSON字符串
            prev_story_str: 前一篇故事JSON字符串（续写时使用）
            chapter_number: 当前章节号（续写时使用）
            volume_plan: 卷规划数据（包含职责/大纲/人物/伏笔）
        """
        genre = request.genre
        style = request.style
        perspective = getattr(request, 'perspective', '第三人称全知')
        mood = getattr(request, 'mood', '轻松愉快')
        background = getattr(request, 'background', '')
        length = request.length

        parts = [f"你是专业{genre}作家，擅长{style}风格。\n叙事视角：{perspective}，情感基调：{mood}"]
        if background:
            parts.append(f"故事背景：{background}")

        # ========== 三层控制 — 续写上下文 ==========
        if prev_story_str:
            prev_data = json.loads(prev_story_str)
            prev_content = prev_data.get('content', '') or ''

            # Layer 1 (战术层): 400字强制过渡 — 仅控制新章第一段（~200字）的衔接
            forced_ending = prev_content[-400:] if len(prev_content) > 400 else prev_content

            # Layer 3 (自由层): 1500字完整结尾 — 仅作为文风和环境细节参考
            style_ref = prev_content[-1500:] if len(prev_content) > 1500 else prev_content

            parts.append(f"""
【前章过渡衔接 — 范围：仅限新章第一段（约200字）】
标题：{prev_data.get('title', '')}

【强制衔接段（400字）】
{forced_ending}

【第一段过渡规则】
1. 角色位置、伤势、疲劳度、情感状态必须与上章结尾完全一致（硬约束）
2. 若上章结尾有"入睡/昏迷/约定明日"等铺垫，允许时间跳跃；否则禁止
3. 若上章结尾有未解决的对话/冲突，第一段应展现其"余波"（可冷暴力、可转移话题），不要求继续争吵
4. 第一段末尾应通过环境细节（灯火燃尽、天色变化、血迹干涸等）自然暗示时间流逝，为后文跳跃做铺垫

【第二段起 — 过渡限制解除，大纲为最高优先级】
从第二段开始：
- 立即推进本章大纲要求的剧情节拍，无需再顾及衔接
- 若大纲需要时间跳跃（第二天/数日后/切换场景），直接执行
- 大纲优先级 > 过渡约束，过渡仅为工具

【规则7 — 进度锚点（硬约束，所有段落适用）】
1. 新章节的起始状态，必须等于或晚于上章末尾最后一句所述的状态。严禁任何形式的"时间回溯"或"场景重置"
2. 如果上章结尾主角已经坐进逃生舱，本章就不能开篇还让主角站在侦察船指挥室里
3. 本章结尾时，主角/核心冲突的位置和状态必须比本章开头有明显推进
4. 本章标题不能与上一章重复

【完整结尾参考 — 仅用于文风和细节一致性，不要求在前200字中复现】
{style_ref}""")

        # ========== 卷规划（最高优先级参考） ==========
        if volume_plan:
            vol_fw = "\n".join(f"  - {f}" for f in volume_plan.get("foreshadowings", [])) if volume_plan.get("foreshadowings") else "  无"
            vol_chars = "\n".join(f"  - {c.get('name','')}（{c.get('identity','')}）：{c.get('brief','')}" for c in volume_plan.get("characters", [])) if volume_plan.get("characters") else "  无"
            # 跨章人物出场表 + 参与类型
            chapter_chars = volume_plan.get("chapter_characters", [])
            participation = volume_plan.get("chapter_participation", {})
            purpose = volume_plan.get("chapter_purpose", {})
            if chapter_chars:
                cc_rows = "\n".join(f"  | 第{cc.get('chapter_num','?')}章 {cc.get('title','')} | {'、'.join(cc.get('characters',[])) or '（无）'} |" for cc in chapter_chars)
                # 参与类型表 + 出场目的表
                part_rows = []
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
                        part_rows.append(f"  | 第{cn}章 | {'、'.join(parts)} |")
                part_str = "\n".join(part_rows) if part_rows else ""
                cc_section = f"""
跨章人物出场表：
| 章节 | 出场角色 |
|------|----------|
{cc_rows}{f"""

角色参与类型与出场目的（主动=须有对话/动作/决策，被动=仅通过他人转述或数据/痕迹，本人不出场不发声）：
| 章节 | 参与类型(目的) |
|------|----------------|
{part_str}""" if part_str else ""}"""
            else:
                cc_section = ""
            parts.append(f"""
【卷规划 — 优先级高于本章大纲】
卷职责：{volume_plan.get('responsibility', '未定义')}
卷大纲：{volume_plan.get('outline', '未定义')}
与上卷衔接：{volume_plan.get('connection_to_prev', '无')}
对下卷铺垫：{volume_plan.get('connection_to_next', '无')}
本卷出场人物：
{vol_chars}
本卷伏笔：
{vol_fw}{cc_section}

本章内容必须服务于本卷的职责和进度，不能偏离卷的大方向。

## *** 强制约束：角色出场规则 + 参与类型（硬约束，违规即重写）***
### 规则A：名单约束（优先级最高）
1. 本章正文中**只能出现**「跨章人物出场表」中本章列出的角色
2. ⚠️ **特别注意**：如果一个角色不在本章的出场表中，即使他是故事核心角色（如本故事共5个角色，但有1个不在本章出场表中），本章也**不可以用任何方式出现他的名字**。包括：被主动角色在对话中提及、作为观察对象被描写、出现在监控数据标签上等。所有引用都必须去掉名字（如「通讯操作员的脑波数据」而不是「赵海的脑波数据」）。
3. 禁止在前置章节引入本该在后置章节才首次登场的角色

### 规则B：参与类型约束（区分主动/被动角色，含出场目的细则）
3. **主动角色**：本章必须有至少一段主动描写（对话、动作、决策、内心活动）
4. **被动角色**：本人不出场，不发出任何声音，不作出任何主动行为。其存在和状态变化**仅允许**通过以下方式体现：
   - 其他角色口头提及（如"林深看了一眼监控，赵海的脑波又出现了一次异常尖峰"）
   - 监控数据/屏幕显示/仪器读数
   - 环境痕迹（录音回放中传出模糊背景音、留下的文字记录）
   禁止的呈现方式：
   - 本人出场（无论现实还是幻觉）
   - 发出任何声音（包括呓语、梦话、破碎音节）
   - 被控制状态下的动作或说话
   - 主导情节走向

   被动角色按**出场目的**分类约束（与「跨章人物出场表」中的目的标注对齐）：

| 出场目的 | 允许的呈现方式 | 禁止的呈现方式 |
|---------|--------------|--------------|
| 信息提供 | 他人分析状态数据、报告监控结果 | 本人说话传递信息 |
| 冲突制造 | 他人因角色状态产生争论分歧 | 本人主动制造冲突 |
| 催化事件 | 状态恶化/好转促使他人做决策 | 本人做决策 |
| 塑造人物 | 成为他人观察/讨论/情感投射的对象 | 本人主动展示性格 |
| 表达主题 | 作为"被体验的客体"呈现 | 本人讲述主题 |
| 营造氛围 | 被观察的状态引发情绪反应 | 本人主动渲染气氛 |

5. **缺席角色**：本章正文中不得出现该角色的任何痕迹（名字、数据、音容）""")

        # ========== 战略层：大纲（最高优先级） ==========
        parts.append(f"""
【故事大纲 — 本章必须覆盖的核心剧情】
{outline_str}

【大纲执行规则】
1. 本章必须推进大纲中指定的剧情节拍，这是最高优先级
2. 如果大纲要求"离开城市前往森林"而过渡很生硬，优先推进大纲
3. 大纲未提及的内容（如赶路过程、睡眠、吃饭等）禁止填充，直接跳过或一笔带过""")

        # ========== 章节编号约束 ==========
        if chapter_number:
            parts.append(f"""
【章节编号——必须绝对遵守】
本章是全书的第 {chapter_number} 章。

---- 正确写法（必须照抄）----
正文第一行必须写成：
## 第{chapter_number}章 [你的标题]

例如：## 第{chapter_number}章 炎龙入侵

---- 以下全是错误写法（严格禁止）----
× 第{chapter_number-1}章          ← 不要用上一章的编号！
× 第{chapter_number+1}章          ← 不要用下一章的编号！
× 第一章 / 第二章 / 第三章         ← 禁止中文数字！
× # 第{chapter_number}章           ← 必须用 ## 双井号！
× 第{chapter_number}节             ← 必须是"章"不是"节"

---- 记住 ----
当前必须使用「## 第{chapter_number}章」开头，数字必须是阿拉伯数字 {chapter_number}。""")
        else:
            parts.append(f"""
【章节编号】
这是全书的第一章。
正文建议用「## 第1章 [标题]」格式开头。""")

        parts.append(f"""
【角色设定】{chars_str}
【目标字数】{length}字

【创作规范】
1. 直接创作全新正文，不要复读或回顾已有内容
2. 保持世界观、人物设定、写作风格一致
3. 使用中文，语言生动细腻，对话自然
4. 大纲 > 过渡 > 风格参考（按优先级执行）
5. 回收已有伏笔并设置新伏笔
6. 不要输出任何说明、解释或开场白，直接输出故事正文""")

        return "\n".join(parts)

    def _build_prompt(self, request, outline_str, chars_str, prev_story_str="", chapter_number=None) -> str:
        """构建写作提示词。

        Args:
            request: 用户请求对象
            outline_str: 大纲JSON字符串
            chars_str: 角色设定JSON字符串
            prev_story_str: 前一篇故事JSON字符串（续写时使用）
            chapter_number: 当前章节号（续写时使用）

        Returns:
            完整的提示词文本
        """
        background = getattr(request, 'background', '')
        perspective = getattr(request, 'perspective', '第三人称全知')
        mood = getattr(request, 'mood', '轻松愉快')
        continuation_mode = getattr(request, 'continuation_mode', 'next_chapter')

        background_info = f"\n{background}" if background else ""

        continuation_info = ""
        if prev_story_str:
            prev_data = json.loads(prev_story_str)
            prev_content = prev_data.get('content', '') or ''
            forced_ending = prev_content[-400:] if len(prev_content) > 400 else prev_content
            style_ref = prev_content[-1500:] if len(prev_content) > 1500 else prev_content
            continuation_info = f"""

【前章过渡衔接 — 仅限新章第一段（约200字）】
- 上一章标题：{prev_data.get('title', '')}

【强制衔接段（400字）】
{forced_ending}

【第一段过渡规则】
1. 角色位置、伤势、疲劳度、情感状态必须与上章结尾一致（硬约束）
2. 若上章有"入睡/昏迷/约定明日"等铺垫，允许时间跳跃
3. 若上章有未解决的对话/冲突，第一段应展现其"余波"而非继续争吵
4. 第一段末尾应用环境细节暗示时间流逝，为后文跳跃做铺垫

【第二段起 — 过渡限制解除，大纲优先】
从第二段开始立即推进大纲要求的剧情节拍。若大纲需要时间跳跃或场景切换，直接执行。

【规则7 — 进度锚点（硬约束，所有段落适用）】
1. 新章节的起始状态必须等于或晚于上章末尾最后一句所述的状态。严禁时间回溯或场景重置
2. 本章结尾时，主角/核心冲突的位置和状态必须比本章开头有明显推进
3. 本章标题不能与上一章重复

【完整结尾参考 — 仅用于文风一致性】
{style_ref}"""
        if chapter_number:
            continuation_info += f"""

## ⚠️ 章节编号 — 必须严格遵守
本章是第 **{chapter_number}** 章。
正文**第一行**必须按照以下格式书写：
## 第{chapter_number}章 [你的章节标题]
例如：## 第{chapter_number}章 炎龙入侵
禁止使用任何其他章节编号！"""

        if request.genre == "诗歌":
            return f"""你是一位专业的 {request.style} 风格诗人，擅长创作长篇史诗诗歌，风格庄重典雅，如《贝奥武夫》《伊利亚特》般恢弘壮丽。

## 创作主题
{request.theme}{background_info}

## 创作要求
- 体裁：诗歌
- 风格：{request.style}
- 情感基调：{mood}
- 目标字数：{request.length} 字
- 章节数量：至少6个章节，每个章节至少8节诗
- 每节诗：4-8行，注重韵律和节奏

{continuation_info}

## 诗歌大纲
{outline_str}

## 角色设定（如有）
{chars_str}

## 创作规范
1. 严格遵循大纲中的结构和意象要求，确保内容充实
2. 使用中文写作，语言庄重典雅，符合史诗风格
3. 分行排版，每句独立一行
4. 运用丰富的意象和隐喻，如雷霆、战斧、王座、战旗等
5. 每个章节要有完整的叙事推进，包含具体的战斗场景、人物对话和心理描写
6. 注重押韵和节奏感，增强诗歌的音乐性
7. 避免口语化表达，使用古典庄严的语言风格
8. 必须达到目标字数要求，内容要详尽丰富
9. 如果是续写，确保情节连贯，适当回收前作伏笔并设置新伏笔

请开始创作完整诗歌，直接输出诗歌内容，不要添加任何说明。"""
        else:
            return f"""你是一位专业的 {request.genre} 作家，擅长 {request.style} 风格。

## 创作要求
- 叙事视角：{perspective}
- 情感基调：{mood}{background_info}

{continuation_info}

## 故事大纲
{outline_str}

## 角色设定
{chars_str}

## 创作规范
1. 严格遵循大纲中的阶段划分和占比
2. 保持角色言行与设定一致
3. 使用中文写作，语言生动细腻
4. 对话自然，符合角色身份
5. 避免说教，通过情节传达主题
6. 目标字数：{request.length} 字
7. 如果是续写，确保情节连贯，适当回收前作伏笔并设置新伏笔

## 输出规则（必须遵守）
- 直接输出故事正文，不要加任何开场白、解释或说明
- 不要对话、不要道歉、不要询问用户
- 开头直接写故事第一句话"""