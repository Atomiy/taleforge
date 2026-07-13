"""协调器模块 - 调度多智能体协作生成故事。"""

import logging
from typing import AsyncIterator, Dict, Any
from backend.agents import PlannerAgent, CharacterAgent, WriterAgent, PolisherAgent, ImageAgent
from backend.services.llm_client import LLMClient
from backend.services.history_manager import HistoryManager
from backend.services.work_manager import WorkManager
from backend.config import COMFYUI_ENABLED


class StoryOrchestrator:
    """多智能体协调器 - 负责调度各智能体协作完成故事生成。

    按顺序调度 Planner、Character、Writer、Polisher 智能体，
    管理智能体间的数据传递，向前端推送实时状态事件，
    处理异常并优雅降级。

    Attributes:
        planner: 策划智能体
        character: 角色智能体
        writer: 写作智能体
        polisher: 润色智能体
        image: 配图智能体（可选）
    """

    def __init__(self, llm_client: LLMClient):
        """初始化协调器，创建各智能体实例。

        Args:
            llm_client: LLM 客户端实例，所有智能体共用
        """
        self.logger = logging.getLogger(__name__)
        self.planner = PlannerAgent(llm_client)
        self.character = CharacterAgent(llm_client)
        self.writer = WriterAgent(llm_client)
        self.polisher = PolisherAgent(llm_client)
        self.image = ImageAgent(llm_client)

    async def generate_story(self, request) -> AsyncIterator[Dict[str, Any]]:
        """生成故事，返回智能体状态事件流。

        按顺序执行：Planner → Character → Writer → Polisher → (Image)，
        每步完成后推送状态事件，支持流式输出写作过程。
        支持续写模式：根据前一篇故事继续生成新内容。

        Args:
            request: 用户故事生成请求对象

        Yields:
            智能体状态事件，包含 agent 名称、status、message 和 data
        """
        previous_story = None
        chapter_number = None
        if request.previous_story_id:
            yield {"agent": "orchestrator", "status": "running", "message": "Loading previous story for continuation..."}
            try:
                history_manager = HistoryManager()
                story_obj = history_manager.get_story_by_id(request.previous_story_id)
                if story_obj:
                    previous_story = story_obj.dict()
                    # 检测前一篇故事的章节编号（第N章），支持中文数字和阿拉伯数字
                    import re
                    CN_NUMS = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
                    match = re.search(r'#{1,4}\s*第(\d+)章', story_obj.content or "")
                    if match:
                        chapter_number = int(match.group(1)) + 1
                    else:
                        match = re.search(r'#{1,4}\s*第([一二三四五六七八九十]+)章', story_obj.content or "")
                        if match:
                            chapter_number = CN_NUMS.get(match.group(1), 0) + 1
                    yield {"agent": "orchestrator", "status": "done", "message": f"Loaded previous story: {previous_story.get('title')}"}
                else:
                    yield {"agent": "orchestrator", "status": "warning", "message": f"Previous story not found: {request.previous_story_id}"}
            except Exception as e:
                yield {"agent": "orchestrator", "status": "warning", "message": f"Failed to load previous story: {str(e)}"}

        yield {"agent": "planner", "status": "running", "message": "Generating story outline..."}

        try:
            context = {"request": request}
            if previous_story:
                context["previous_story"] = {
                    "title": previous_story.get("title", ""),
                    "content": previous_story.get("content", ""),
                    "characters": previous_story.get("characters", []),
                    "world_setting": previous_story.get("world_setting", ""),
                    "foreshadowings": previous_story.get("foreshadowings", []),
                }
            # 加载卷规划数据（局部变量，不存实例变量，避免并发状态泄漏）
            volume_plan = None
            if request.work_id and request.volume_id:
                try:
                    wm = WorkManager()
                    work_obj = wm.get_work_by_id(request.work_id)
                    if work_obj:
                        vol = next((v for v in work_obj.volumes if v.id == request.volume_id), None)
                        if vol:
                            plan = {
                                "outline": vol.outline or "",
                                "responsibility": vol.responsibility or "",
                                "connection_to_prev": vol.connection_to_prev or "",
                                "connection_to_next": vol.connection_to_next or "",
                                "characters": vol.characters or [],
                                "foreshadowings": vol.foreshadowings or [],
                                "chapter_characters": getattr(vol, 'chapter_characters', []) or [],
                                "character_appearance_map": getattr(vol, 'character_appearance_map', {}) or {},
                                "character_arcs": getattr(vol, 'character_arcs', {}) or {},
                                "chapter_participation": getattr(vol, 'chapter_participation', {}) or {},
                                "chapter_purpose": getattr(vol, 'chapter_purpose', {}) or {},
                            }
                            volume_plan = plan
                            context["volume_plan"] = plan
                            yield {"agent": "orchestrator", "status": "running", "message": f"Loaded volume plan: {vol.title}"}
                except Exception as e:
                    self.logger.warning(f"Failed to load volume plan: {e}")
            outline_result = await self.planner.run(context)
            outline = outline_result.get("outline", {})
            yield {"agent": "planner", "status": "done", "data": outline, "message": f"Outline ready: {outline.get('title', 'Untitled')}"}
        except Exception as e:
            yield {"agent": "planner", "status": "error", "message": f"Outline generation failed: {str(e)}"}
            outline = {}

        yield {"agent": "character", "status": "running", "message": "Developing characters..."}

        try:
            context = {"request": request, "outline": outline}
            if previous_story and previous_story.get("characters"):
                context["existing_characters"] = previous_story["characters"]
            # 卷规划人物作为已有角色（局部变量显式传递）
            if volume_plan and volume_plan.get("characters"):
                existing = list(context.get("existing_characters", []))
                existing_names = {c.get("name", "") for c in existing}
                for pc in volume_plan["characters"]:
                    if pc.get("name", "") not in existing_names:
                        existing.append(pc)
                context["existing_characters"] = existing
            # 跨章人物出场表传给 Character Agent，用于约束角色生成范围
            if volume_plan:
                cc = volume_plan.get("chapter_characters", [])
                if cc:
                    context["chapter_characters"] = cc
            char_result = await self.character.run(context)
            characters = char_result.get("characters", [])
            char_names = ", ".join([c.get("name", "") for c in characters])
            yield {"agent": "character", "status": "done", "data": characters, "message": f"Characters ready: {char_names or 'None'}"}
        except Exception as e:
            yield {"agent": "character", "status": "error", "message": f"Character development failed: {str(e)}"}
            characters = []

        yield {"agent": "writer", "status": "running", "message": "Writing story..."}

        try:
            context = {
                "request": request,
                "outline": outline,
                "characters": characters,
            }
            if chapter_number:
                context["chapter_number"] = chapter_number
            if volume_plan:
                context["volume_plan"] = volume_plan
            if previous_story:
                context["previous_story"] = {
                    "title": previous_story.get("title", ""),
                    "content": previous_story.get("content", ""),
                }
            self.logger.info(f"[Orchestrator] Writer context: chapter_number={chapter_number}, has_prev_story={'yes' if previous_story else 'no'}, outline_type={type(outline).__name__}, chars_count={len(characters)}")
            async for chunk in self.writer.run_streaming(context):
                yield {"agent": "writer", "status": "writing", "data": chunk}

            draft = self.writer.get_full_draft()
            self.logger.info(f"[Orchestrator] Writer full_draft: {len(draft)} chars")
            yield {"agent": "writer", "status": "done", "data": draft, "message": f"Writing complete, {len(draft)} characters"}
        except Exception as e:
            self.logger.error(f"[Orchestrator] Writer streaming failed: {e}")
            yield {"agent": "writer", "status": "error", "message": f"Writing failed: {str(e)}"}
            draft = ""

        yield {"agent": "polisher", "status": "running", "message": "Polishing story..."}

        try:
            polish_result = await self.polisher.run({
                "draft": draft,
                "request": request,
                "outline": outline,
                "characters": characters,
            })
            final = polish_result.get("final", draft)
            yield {"agent": "polisher", "status": "done", "data": final, "message": "Polishing complete"}
        except Exception as e:
            yield {"agent": "polisher", "status": "error", "message": f"Polishing failed, using draft: {str(e)}"}
            final = draft

        if COMFYUI_ENABLED:
            yield {"agent": "image", "status": "running", "message": "Generating images..."}
            try:
                image_result = await self.image.run({
                    "final": final,
                    "request": request,
                })
                images = image_result.get("images", [])
                yield {"agent": "image", "status": "done", "data": images, "message": f"Images generated: {len(images)}"}
            except Exception as e:
                yield {"agent": "image", "status": "error", "message": f"Image generation failed: {str(e)}"}
                images = []
        else:
            images = []

        yield {"agent": "orchestrator", "status": "complete", "data": {
            "title": outline.get("title", request.theme),
            "content": final,
            "outline": outline,
            "characters": characters,
            "images": images,
            "previous_story_id": request.previous_story_id,
        }}