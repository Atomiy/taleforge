import math
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from backend.models.work import Work, Volume
from backend.services.work_manager import WorkManager
from backend.services.history_manager import HistoryManager
from backend.services.llm_client import LLMClient
from backend.config import DEEPSEEK_API_KEY

logger = logging.getLogger(__name__)

router = APIRouter()

work_manager = WorkManager()
history_manager = HistoryManager()


def _get_llm_client():
    import backend.config as cfg
    return LLMClient(api_key=cfg.DEEPSEEK_API_KEY, base_url=cfg.DEEPSEEK_BASE_URL)


@router.post("/")
async def create_work(data: dict = Body(...)):
    """创建新作品。"""
    now = datetime.now().isoformat()
    work = Work(
        id=work_manager.generate_work_id(),
        title=data.get("title", "未命名作品"),
        world_setting=data.get("world_setting", ""),
        foreshadowings=data.get("foreshadowings", []),
        outline=data.get("outline", ""),
        genre=data.get("genre", "奇幻"),
        style=data.get("style", "史诗"),
        characters=data.get("characters", []),
        created_at=now,
        updated_at=now,
    )
    work_manager.save_work(work)
    return {"work_id": work.id}


@router.get("/")
async def list_works():
    """获取所有作品列表。"""
    works = work_manager.get_all_works()
    return {"works": works}


@router.get("/{work_id}")
async def get_work(work_id: str):
    """获取作品详情，包含章节内容。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    # 加载每个章节的故事内容
    chapters = []
    for cid in work.chapter_ids:
        story = history_manager.get_story_by_id(cid)
        if story:
            chapters.append(story)
        else:
            chapters.append({"id": cid, "error": "故事未找到"})

    return {"work": work, "chapters": chapters}


@router.put("/{work_id}")
async def update_work(work_id: str, data: dict = Body(...)):
    """更新作品字段。"""
    work = work_manager.update_work(work_id, data)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return work


@router.delete("/{work_id}")
async def delete_work(work_id: str):
    """删除作品。"""
    success = work_manager.delete_work(work_id)
    if not success:
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"success": True}


# ---- 卷管理 ----

@router.post("/{work_id}/volumes")
async def create_volume(work_id: str, data: dict = Body(...)):
    """为作品添加新卷。"""
    title = data.get("title", "")
    work = work_manager.add_volume(work_id, title)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"work": work}


@router.put("/{work_id}/volumes/{volume_id}")
async def update_volume(work_id: str, volume_id: str, data: dict = Body(...)):
    """更新卷信息。"""
    work = work_manager.update_volume(work_id, volume_id, data)
    if not work:
        raise HTTPException(status_code=404, detail="作品或卷不存在")
    return {"work": work}


@router.delete("/{work_id}/volumes/{volume_id}")
async def delete_volume(work_id: str, volume_id: str):
    """删除卷（章节并入前卷）。"""
    work = work_manager.remove_volume(work_id, volume_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品或卷不存在")
    return {"work": work}


# ---- 章节管理 ----

@router.post("/{work_id}/chapters")
async def add_chapter(work_id: str, data: dict = Body(...)):
    """添加章节到作品。可指定 volume_id，否则加入末卷。"""
    story_id = data.get("story_id")
    if not story_id:
        raise HTTPException(status_code=400, detail="缺少 story_id")

    story = history_manager.get_story_by_id(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")

    volume_id = data.get("volume_id", "")
    work = work_manager.add_chapter_to_work(work_id, story_id, volume_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return work


@router.delete("/{work_id}/chapters/{story_id}")
async def remove_chapter(work_id: str, story_id: str):
    """从作品中移除章节，并删除对应的故事数据。"""
    work = work_manager.remove_chapter_from_work(work_id, story_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品或章节不存在")
    # 同时删除对应的故事数据
    history_manager.delete_story(story_id)
    return work


# ---- AI 卷规划辅助 ----

@router.post("/{work_id}/volumes/{volume_id}/ai-plan")
async def ai_volume_plan(work_id: str, volume_id: str, data: dict = Body(...)):
    """AI辅助生成多章规划内容。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    vol = next((v for v in work.volumes if v.id == volume_id), None)
    if not vol:
        raise HTTPException(status_code=404, detail="卷不存在")
    api_key = data.get("api_key") or DEEPSEEK_API_KEY
    if not api_key:
        return {"success": False, "error": "请配置 API Key"}
    tips = data.get("tips", "")
    num_chapters = data.get("num_chapters", 5)
    try:
        llm = LLMClient(api_key)

        # 角色卡片信息
        character_cards = []
        for c in work.characters:
            card_parts = [f"名称：{c.get('name', '')}"]
            if c.get('identity'):
                card_parts.append(f"身份：{c['identity']}")
            if c.get('personality'):
                card_parts.append(f"性格：{c['personality']}")
            if c.get('motivation'):
                card_parts.append(f"动机：{c['motivation']}")
            if c.get('brief'):
                card_parts.append(f"简介：{c['brief']}")
            if c.get('background'):
                card_parts.append(f"背景：{c['background']}")
            character_cards.append(" | ".join(card_parts))
        characters_text = "\n".join(character_cards) if character_cards else "无"

        # 已有卷信息（用于衔接）
        vol_index = next((i for i, v in enumerate(work.volumes) if v.id == volume_id), -1)
        prev_vol_title = work.volumes[vol_index - 1].title if vol_index > 0 else "无（第一卷）"
        next_vol_title = work.volumes[vol_index + 1].title if vol_index < len(work.volumes) - 1 else "无（最后一卷）"

        # 该卷已有规划数据
        vol_chapter_outlines = getattr(vol, 'chapter_outlines', []) or []
        vol_characters = getattr(vol, 'characters', []) or []

        prompt = f"""你是一位专业的创作策划师，擅长为小说作品构思多章规划。

作品信息：
- 标题：{work.title}
- 类型：{work.genre}
- 风格：{work.style}
- 世界观：{work.world_setting[:500] if work.world_setting else '无'}
- 故事大纲：{work.outline[:500] if work.outline else '无'}
- 作品概要：{work.summary[:300] if work.summary else '无'}

作品级角色卡片（请优先使用并尊重这些角色设定）：
{characters_text}

卷信息：
- 卷标题：{vol.title or '未命名'}
- 上一卷：{prev_vol_title}
- 下一卷：{next_vol_title}
- 卷已有大纲：{vol.outline[:200] if vol.outline else '无'}
- 卷已有章节规划：{('规划了 ' + str(len(vol_chapter_outlines)) + ' 章') if vol_chapter_outlines else '无'}

用户补充要求：{tips if tips else '无'}

请为该卷规划 {num_chapters} 章的内容，以 JSON 格式输出以下规划建议：

{{
  "outline": "本卷的整体故事脉络和发展方向（100-200字）",
  "responsibility": "本卷在整部作品中的职责和作用（50-100字）",
  "connection_to_prev": "本卷与上一卷的衔接方式",
  "connection_to_next": "本卷为下一卷做的铺垫",
  "chapters": [
    {{"title": "第1章标题", "outline": "本章大纲（50-100字）", "key_events": ["关键事件1", "关键事件2", "关键事件3"]}},
    ...（共{num_chapters}章）
  ],
  "characters": [
    {{"name": "角色名", "identity": "在本卷中的身份/作用", "brief": "在本卷中的简要说明"}}
  ],
  "foreshadowings": [
    {{"item": "伏笔内容", "purpose": "该伏笔的目的/作用"}}
  ]
}}

要求：
1. 严格使用作品级角色卡片中的角色，不要凭空创造新角色
2. 各章之间要有连贯的情节递进
3. 伏笔应与本卷故事发展贴合
4. 请结合作品故事大纲和卷已有大纲来规划，确保各卷内容合理衔接
5. 只输出JSON，不要其他内容"""

        messages = [{"role": "system", "content": "你是专业创作策划师"}, {"role": "user", "content": prompt}]
        result = await llm.chat(messages, temperature=0.8, max_tokens=4096)
        result = result.strip()
        if result.startswith("```"):
            first_newline = result.find("\n")
            if first_newline != -1:
                result = result[first_newline+1:]
            else:
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
        import re, json as json_mod
        result = re.sub(r',\s*([\]}])', r'\1', result)
        parsed = json_mod.loads(result)
        return {"success": True, "data": parsed}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/{work_id}/volumes/{volume_id}/smart-char-assign")
async def smart_character_assignment(work_id: str, volume_id: str, data: dict = Body(...)):
    """AI智能分析每章出场角色。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    vol = next((v for v in work.volumes if v.id == volume_id), None)
    if not vol:
        raise HTTPException(status_code=404, detail="卷不存在")

    api_key = data.get("api_key") or DEEPSEEK_API_KEY
    if not api_key:
        return {"success": False, "error": "请配置 API Key"}

    chapters = data.get("chapters", [])
    characters = data.get("characters", [])

    if not chapters or not characters:
        return {"success": False, "error": "缺少章节信息或角色列表"}

    chapter_lines = []
    for i, ch in enumerate(chapters):
        title = ch.get("title", f"第{i+1}章")
        outline = ch.get("outline", "") or ""
        key_events = ch.get("key_events", [])
        events_str = "；".join(key_events) if key_events else "无"
        chapter_lines.append(f"第{i+1}章【{title}】：{outline[:200]}（关键事件：{events_str}）")

    char_lines = []
    for c in characters:
        name = c.get("name", "")
        identity = c.get("identity", "") or ""
        brief = c.get("brief", "") or ""
        char_lines.append(f"{name}（{identity}，{brief}）" if identity or brief else name)

    prompt = f"""你是一位专业的故事角色策划师。请根据以下章节规划，为每一章分析并安排最合理的出场角色。

章节规划：
{chr(10).join(chapter_lines)}

可用角色：
{chr(10).join(char_lines)}

角色安排原则：
1. 主角/核心角色应在大部分章节出场
2. 仅与特定情节相关的角色只在对应章节出场
3. 首章应引入核心角色，后续章节逐步引入新角色
4. 不要安排与本章情节完全无关的角色出场
5. 如果角色与本章情节的关键事件或主题无关，不应安排出场

以 JSON 格式输出，格式如下：
{{"assignments": {{"0": ["角色名1", "角色名2"], "1": ["角色名1", "角色名3"], ...}}}}
其中 key 为章节索引（0 开始的数字），value 为该章应该出场的角色名数组。只输出 JSON，不要任何额外内容。"""

    try:
        llm = LLMClient(api_key)
        messages = [{"role": "system", "content": "你是专业故事角色策划师。"}, {"role": "user", "content": prompt}]
        result = await llm.chat(messages, temperature=0.3, max_tokens=2048)
        result = result.strip()
        if result.startswith("```"):
            first_newline = result.find("\n")
            if first_newline != -1:
                result = result[first_newline+1:]
            else:
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
        import re, json as json_mod
        result = re.sub(r',\s*([\]}])', r'\1', result)
        parsed = json_mod.loads(result)
        return {"success": True, "data": parsed}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ---- 角色管理 ----

@router.get("/{work_id}/characters")
async def get_work_characters(work_id: str):
    """获取作品的角色列表。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    return {"characters": work.characters}


@router.post("/{work_id}/characters")
async def add_work_character(work_id: str, data: dict = Body(...)):
    """添加角色到作品。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    character = {
        "name": data.get("name", ""),
        "age": data.get("age", ""),
        "identity": data.get("identity", ""),
        "personality": data.get("personality", ""),
        "motivation": data.get("motivation", ""),
        "brief": data.get("brief", ""),
        "appearance": data.get("appearance", ""),
        "background": data.get("background", ""),
        "relationships": data.get("relationships", []),
    }
    work.characters.append(character)
    work_manager.save_work(work)
    return {"work": work}


@router.put("/{work_id}/characters/{char_index}")
async def update_work_character(work_id: str, char_index: int, data: dict = Body(...)):
    """更新作品中的角色。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if char_index < 0 or char_index >= len(work.characters):
        raise HTTPException(status_code=404, detail="角色不存在")
    
    work.characters[char_index].update(data)
    work_manager.save_work(work)
    return {"work": work}


@router.delete("/{work_id}/characters/{char_index}")
async def delete_work_character(work_id: str, char_index: int):
    """删除作品中的角色。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if char_index < 0 or char_index >= len(work.characters):
        raise HTTPException(status_code=404, detail="角色不存在")
    
    work.characters.pop(char_index)
    work_manager.save_work(work)
    return {"work": work}


# ---- 概要生成 ----

@router.post("/{work_id}/summary")
async def update_summary(work_id: str, data: dict = Body(...)):
    """生成或更新作品概要（长度随章节数动态变化）。"""
    work = work_manager.get_work_by_id(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")

    summary = data.get("summary", "")
    if not summary:
        chapter_count = len(work.chapter_ids)
        # 动态目标长度：sqrt 曲线，避免线性膨胀
        target_len = min(80 + round(math.sqrt(chapter_count) * 40), 500)
        logger.info(f"生成概要: 共{chapter_count}章, 目标长度约{target_len}字")

        # 为每个卷生成概要，再汇总
        volume_summaries = []
        for vol in work.volumes:
            if not vol.chapter_ids:
                continue
            vol_chapters = []
            for cid in vol.chapter_ids:
                story = history_manager.get_story_by_id(cid)
                if story and story.content:
                    preview = story.content[:600]
                    vol_chapters.append(f"章节「{story.title or '无标题'}」：{preview}")

            if vol_chapters:
                chapters_text = "\n\n".join(vol_chapters)
                try:
                    messages = [
                        {"role": "system", "content": f"你是一个专业的文学编辑。请用简洁的语言（约{max(60, target_len // max(len(work.volumes), 1))}字）概括以下章节的核心情节，保留关键冲突和转折。"},
                        {"role": "user", "content": f"请概括「{vol.title}」中各章节的核心情节：\n\n{chapters_text}"}
                    ]
                    v_summary = await _get_llm_client().chat(messages, temperature=0.3, max_tokens=512)
                    volume_summaries.append(f"【{vol.title}】{v_summary.strip()}")
                except Exception as e:
                    logger.warning(f"卷 {vol.id} 概要生成失败: {e}")
                    volume_summaries.append(f"【{vol.title}】（概要生成失败）")

        if volume_summaries:
            combined = "\n".join(volume_summaries)
            try:
                messages = [
                    {"role": "system", "content": f"你是一个专业的文学编辑。请将各卷概要汇总为一段连贯、精炼的作品内容概要（约{target_len}字）。"},
                    {"role": "user", "content": f"请汇总为一段连贯的作品概要：\n\n{combined}"}
                ]
                summary = await _get_llm_client().chat(messages, temperature=0.3, max_tokens=1024)
                summary = summary.strip()
            except Exception as e:
                logger.warning(f"汇总概要生成失败: {e}")
                summary = combined
        else:
            summary = "（暂无章节内容）"

    work_manager.update_work(work_id, {"summary": summary})
    updated_work = work_manager.get_work_by_id(work_id)
    return updated_work
