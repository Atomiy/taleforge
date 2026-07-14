import json
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models import StoryRequest, Story
from backend.services import LLMClient, HistoryManager, StoryOrchestrator
from backend.config import DEEPSEEK_API_KEY

router = APIRouter()

history_manager = HistoryManager()

async def generate_story_stream(request: StoryRequest):
    api_key = request.api_key or DEEPSEEK_API_KEY
    if not api_key:
        yield json.dumps({"error": "请配置 API Key"})
        return

    llm_client = LLMClient(api_key=api_key)
    orchestrator = StoryOrchestrator(llm_client)

    async for event in orchestrator.generate_story(request):
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

@router.post("/generate")
async def generate_story(request: StoryRequest):
    return StreamingResponse(
        generate_story_stream(request),
        media_type="text/event-stream"
    )

@router.get("/{story_id}")
async def get_story(story_id: str):
    story = history_manager.get_story_by_id(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return story

@router.post("/save")
async def save_story(story_data: dict):
    try:
        story = Story(
            id=story_data.get("id") or history_manager.generate_id(),
            title=story_data.get("title", "未命名"),
            content=story_data.get("content", ""),
            theme=story_data.get("theme", ""),
            genre=story_data.get("genre", "短篇小说"),
            style=story_data.get("style", "温馨"),
            outline=story_data.get("outline"),
            characters=story_data.get("characters"),
            created_at=datetime.now(),
            word_count=history_manager._calculate_word_count(story_data.get("content", "")),
            series_id=story_data.get("series_id", ""),
            series_order=story_data.get("series_order", 1),
            world_setting=story_data.get("world_setting", ""),
            foreshadowings=story_data.get("foreshadowings", []),
            previous_story_id=story_data.get("previous_story_id", "")
        )
        history_manager.save_story(story)
        return {"success": True, "story_id": story.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_story_by_id(story_id: str) -> Story:
    story = history_manager.get_story_by_id(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="故事不存在")
    return story


@router.post("/inspire")
async def inspire(data: dict):
    """根据作品主题/世界观，用 AI 生成剧情点子、伏笔和角色建议。"""
    theme = data.get("theme", "")
    world_setting = data.get("world_setting", "")
    genre = data.get("genre", "")
    style = data.get("style", "")
    existing_foreshadowings = data.get("existing_foreshadowings", [])
    existing_outline = data.get("existing_outline", "")
    api_key = data.get("api_key") or DEEPSEEK_API_KEY
    if not api_key:
        return {"error": "请配置 API Key"}

    existing_fw = "\n".join(f"- {f}" for f in existing_foreshadowings) if existing_foreshadowings else "无"
    llm = LLMClient(api_key=api_key)
    prompt = f"""你是一个创意灵感助手。请根据以下故事设定，分别从三个维度提供创作建议。

【故事设定】
主题：{theme}
体裁：{genre}
风格：{style}
世界观：{world_setting}
现有大纲：{existing_outline or '无'}
已有伏笔：{existing_fw}

请输出 JSON（不要其他内容），格式如下：
{{
  "plot_points": [
    {{"title": "情节点子标题", "description": "简要描述"}}
  ],
  "foreshadowings": [
    {{"content": "伏笔内容", "type": "悬念/预言/秘密/线索"}}
  ],
  "characters": [
    {{"name": "角色名", "identity": "身份", "appearance": "外貌", "personality": "性格", "brief": "一句话简介"}}
  ]
}}

要求：
- plot_points：给出 3 个剧情发展方向，要有创意、有新意
- foreshadowings：给出 3 个伏笔建议，类型可以是悬念/预言/秘密/线索，避免与已有伏笔重复
- characters：给出 2-3 个角色建议，每个角色要有鲜明的身份和特点，适合这个设定
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        result = await llm.chat(messages, temperature=0.8, max_tokens=2048)
        # 清理可能的 markdown 代码块标记
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[1] if "\n" in result else result[3:]
            if result.endswith("```"):
                result = result[:-3]
            result = result.strip()
        parsed = json.loads(result)
        return {"success": True, "data": parsed}
    except Exception as e:
        return {"success": False, "error": str(e), "raw": result if 'result' in dir() else ""}