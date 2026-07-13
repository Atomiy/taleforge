from fastapi import APIRouter, Body
from backend.config import DEEPSEEK_API_KEY, COMFYUI_ENABLED, save_api_key

router = APIRouter()

@router.get("/")
async def get_config():
    return {
        "api_key_configured": bool(DEEPSEEK_API_KEY),
        "comfyui_enabled": COMFYUI_ENABLED,
        "available_genres": ["短篇小说", "中篇小说", "日常小短文", "散文", "剧本", "童话", "诗歌", "悬疑推理", "科幻", "奇幻"],
        "available_styles": ["温馨", "悬疑", "科幻", "古风", "奇幻", "幽默", "伤感", "浪漫"],
        "available_perspectives": ["第三人称全知", "第三人称有限", "第一人称", "第二人称"],
        "available_conflicts": ["人与自然", "人与社会", "人与人", "内心冲突"],
        "available_moods": ["轻松愉快", "紧张刺激", "温馨感人", "深沉思考", "神秘诡异", "浪漫唯美"]
    }

@router.post("/api-key")
async def set_api_key(api_key: str = Body(..., embed=True)):
    success = save_api_key(api_key)
    if success:
        return {"success": True, "message": "API Key 保存成功"}
    return {"success": False, "message": "保存失败，请检查权限"}