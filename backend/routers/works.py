import math
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
from backend.models.work import Work, Volume
from backend.services.work_manager import WorkManager
from backend.services.history_manager import HistoryManager
from backend.services.llm_client import LLMClient

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
    """从作品中移除章节。"""
    work = work_manager.remove_chapter_from_work(work_id, story_id)
    if not work:
        raise HTTPException(status_code=404, detail="作品或章节不存在")
    return work


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
