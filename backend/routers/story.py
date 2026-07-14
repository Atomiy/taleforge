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
    """根据作品主题/世界观，用 AI 生成各类创作灵感。支持传入作品角色信息进行适配。"""
    theme = data.get("theme", "")
    world_setting = data.get("world_setting", "")
    genre = data.get("genre", "")
    style = data.get("style", "")
    existing_foreshadowings = data.get("existing_foreshadowings", [])
    existing_outline = data.get("existing_outline", "")
    existing_characters = data.get("existing_characters", "")
    user_request = data.get("user_request", "")
    api_key = data.get("api_key") or DEEPSEEK_API_KEY
    if not api_key:
        return {"error": "请配置 API Key"}

    inspire_types = data.get("types", ["plot_points", "characters", "foreshadowings"])
    count = data.get("count", 3)
    temperature = data.get("temperature", 0.8)

    existing_fw = "\n".join(f"- {f}" for f in existing_foreshadowings) if existing_foreshadowings else "无"

    type_configs = {
        "plot_points": {
            "label": "剧情发展",
            "format": '{"title": "情节点子标题", "description": "简要描述"}',
            "prompt": f"给出 {count} 个剧情发展方向，要有创意、有新意，适合{genre}体裁"
        },
        "characters": {
            "label": "角色灵感",
            "format": '{"name": "角色名", "identity": "身份", "appearance": "外貌", "personality": "性格", "brief": "一句话简介", "motivation": "核心动机"}',
            "prompt": f"给出 {count} 个角色建议，每个角色要有鲜明的身份和特点，包含核心动机"
        },
        "foreshadowings": {
            "label": "伏笔建议",
            "format": '{"content": "伏笔内容", "type": "悬念/预言/秘密/线索", "reveal": "预期揭示时机"}',
            "prompt": f"给出 {count} 个伏笔建议，类型可以是悬念/预言/秘密/线索，避免与已有伏笔重复。已有伏笔：{existing_fw}"
        },
        "world_building": {
            "label": "世界观设定",
            "format": '{"aspect": "设定方面", "detail": "详细描述"}',
            "prompt": f"给出 {count} 个世界观设定细节，丰富当前世界。现有设定：{world_setting or '无'}"
        },
        "titles": {
            "label": "标题创意",
            "format": '{"title": "标题", "subtitle": "副标题（可选）", "style": "风格"}',
            "prompt": f"给出 {count} 个故事标题创意，风格匹配{style}"
        },
        "scenes": {
            "label": "场景描述",
            "format": '{"title": "场景名称", "description": "场景描述", "mood": "氛围"}',
            "prompt": f"给出 {count} 个场景描述，包含详细的视觉画面和氛围营造"
        },
        "dialogues": {
            "label": "对话灵感",
            "format": '{"character": "说话者", "dialogue": "对话内容", "context": "上下文"}',
            "prompt": f"给出 {count} 段对话灵感，展现角色性格和推动剧情"
        }
    }

    type_items = [t for t in inspire_types if t in type_configs]
    if not type_items:
        type_items = ["plot_points", "characters", "foreshadowings"]

    type_prompts = []
    type_formats = []
    for t in type_items:
        cfg = type_configs[t]
        type_prompts.append(f"- {cfg['label']}：{cfg['prompt']}")
        type_formats.append(f'  "{t}": [\n    {cfg["format"]}\n  ]')

    format_str = "{\n" + ",\n".join(type_formats) + "\n}"
    prompt_str = "\n".join(type_prompts)

    llm = LLMClient(api_key=api_key)
    prompt = f"""你是一个创意灵感助手。请根据以下故事设定，提供创作建议。

【故事设定】
主题：{theme}
体裁：{genre}
风格：{style}
世界观：{world_setting}
现有大纲：{existing_outline or '无'}
已有角色：{existing_characters or '无'}
用户要求：{user_request or '无'}

【生成要求】
{prompt_str}

请输出 JSON（不要其他内容），格式如下：
{format_str}

要求：
- 每个类别给出 {count} 个建议
- 内容要有创意，避免陈词滥调
- 与现有设定保持一致
- 如果已有角色不为空，剧情发展和对话灵感要考虑这些角色的性格和动机，让他们自然地参与剧情
- 角色灵感可以是对已有角色的深化，也可以是新增角色建议
- 如果用户有具体要求，请优先满足用户的要求
"""
    try:
        messages = [{"role": "user", "content": prompt}]
        result = await llm.chat(messages, temperature=temperature, max_tokens=3072)
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
        # 智能 JSON 修复：处理 AI 常见错误
        import re
        # 移除注释（// 或 # 开头的行）
        result = re.sub(r'(?m)^\s*(//|#).*$', '', result)
        # 移除尾随逗号（在 } 或 ] 前）
        result = re.sub(r',\s*([\]}])', r'\1', result)
        # 尝试修复单引号导致的 JSON 错误
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            # 如果还是失败，尝试更激进的修复
            # 替换所有单引号为双引号（但需避开已转义的）
            fixed = result
            # 仅替换 JSON 值中的单引号
            fixed = re.sub(r"(?<=:)\s*'([^']*)'(?=\s*[,}\]])", r'"\1"', fixed)
            try:
                parsed = json.loads(fixed)
            except json.JSONDecodeError:
                # 提取最外层的 {} 块
                brace_start = fixed.find('{')
                brace_end = fixed.rfind('}')
                if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
                    fixed = fixed[brace_start:brace_end+1]
                    parsed = json.loads(fixed)
                else:
                    raise
        return {"success": True, "data": parsed}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"AI 返回格式错误: {e}", "raw": result if 'result' in dir() else ""}
    except Exception as e:
        return {"success": False, "error": str(e), "raw": result if 'result' in dir() else ""}