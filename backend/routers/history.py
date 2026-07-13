from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import PlainTextResponse
from backend.services import HistoryManager
from backend.models import Story, StoryHistoryResponse
from typing import Optional

router = APIRouter()

history_manager = HistoryManager()

@router.get("/")
async def get_history(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(default="", description="搜索关键词"),
    genre: Optional[str] = Query(default="", description="按体裁筛选"),
    favorite: Optional[str] = Query(default="", description="按收藏筛选，值为 \"true\" 或 \"false\""),
):
    """获取历史记录列表（支持分页、搜索、筛选）。"""
    stories = history_manager.get_all_stories()
    
    if search:
        search = search.lower()
        stories = [s for s in stories if search in s.title.lower() or search in s.content.lower()]
    
    if genre:
        stories = [s for s in stories if s.genre == genre]

    if favorite:
        if favorite.lower() == "true":
            stories = [s for s in stories if s.favorite]
        elif favorite.lower() == "false":
            stories = [s for s in stories if not s.favorite]
    
    total = len(stories)
    start = (page - 1) * page_size
    paged_stories = stories[start:start + page_size]
    
    return {
        "stories": paged_stories,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total > 0 else 0
    }

@router.delete("/{story_id}")
async def delete_story(story_id: str):
    """删除指定故事。"""
    success = history_manager.delete_story(story_id)
    if not success:
        raise HTTPException(status_code=404, detail="故事不存在")
    return {"success": True}

@router.get("/{story_id}")
async def get_story(story_id: str):
    """获取单个故事详情。"""
    story = history_manager.get_story_by_id(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return story

@router.get("/export/{story_id}")
async def export_story(story_id: str, format: str = Query(default="markdown", description="导出格式")):
    """导出故事为 Markdown 格式。"""
    story = history_manager.get_story_by_id(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    
    if format == "markdown":
        md = f"""# {story.title}

> **体裁**：{story.genre} | **风格**：{story.style} | **字数**：{story.word_count}
> **创建时间**：{story.created_at.strftime('%Y-%m-%d %H:%M')}

---

{story.content}

---

*由 TaleForge AI 故事生成器创作*
"""
        return PlainTextResponse(content=md, media_type="text/markdown; charset=utf-8")
    elif format == "text":
        txt = f"【{story.title}】\n\n体裁：{story.genre} | 风格：{story.style} | 字数：{story.word_count}\n\n{story.content}\n\n—— TaleForge AI 创作"
        return PlainTextResponse(content=txt, media_type="text/plain; charset=utf-8")
    else:
        raise HTTPException(status_code=400, detail=f"不支持的导出格式: {format}")

@router.put("/{story_id}")
async def update_story(story_id: str, updated_data: dict = Body(..., description="要更新的字段")):
    """更新故事内容（支持更新 content、title、theme 等字段）。"""
    story = history_manager.update_story(story_id, updated_data)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return story

@router.put("/{story_id}/favorite")
async def toggle_favorite(story_id: str):
    """切换故事的收藏状态。"""
    story = history_manager.toggle_favorite(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return {"story": story, "favorite": story.favorite}