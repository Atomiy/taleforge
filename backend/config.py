"""项目配置模块 - 读取环境变量和配置参数。"""

import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_FILE)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8080"))

PLANNER_TEMPERATURE = float(os.environ.get("PLANNER_TEMPERATURE", "0.5"))
CHARACTER_TEMPERATURE = float(os.environ.get("CHARACTER_TEMPERATURE", "0.5"))
WRITER_TEMPERATURE = float(os.environ.get("WRITER_TEMPERATURE", "0.8"))
POLISHER_TEMPERATURE = float(os.environ.get("POLISHER_TEMPERATURE", "0.3"))

COMFYUI_ENABLED = os.environ.get("COMFYUI_ENABLED", "false").lower() == "true"
COMFYUI_API_URL = os.environ.get("COMFYUI_API_URL", "http://127.0.0.1:8188")

_story_output_dir = os.environ.get("STORY_OUTPUT_DIR")
if _story_output_dir:
    STORY_OUTPUT_DIR = _story_output_dir if os.path.isabs(_story_output_dir) else os.path.join(PROJECT_ROOT, _story_output_dir)
else:
    STORY_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

_stories_file = os.environ.get("STORIES_FILE")
if _stories_file:
    STORIES_FILE = _stories_file if os.path.isabs(_stories_file) else os.path.join(PROJECT_ROOT, _stories_file)
else:
    STORIES_FILE = os.path.join(PROJECT_ROOT, "backend", "data", "stories.json")

os.makedirs(STORY_OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STORIES_FILE), exist_ok=True)


def save_api_key(api_key: str) -> bool:
    """保存API Key到.env文件。"""
    try:
        if os.path.exists(ENV_FILE):
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'DEEPSEEK_API_KEY=' in content:
                old_value = content.split('DEEPSEEK_API_KEY=')[1].split('\n')[0]
                content = content.replace(
                    'DEEPSEEK_API_KEY=' + old_value,
                    'DEEPSEEK_API_KEY=' + api_key
                )
            else:
                content = content.rstrip() + '\nDEEPSEEK_API_KEY=' + api_key + '\n'
        else:
            content = 'DEEPSEEK_API_KEY=' + api_key + '\n'

        with open(ENV_FILE, 'w', encoding='utf-8') as f:
            f.write(content)

        global DEEPSEEK_API_KEY
        DEEPSEEK_API_KEY = api_key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        return True
    except Exception as e:
        print(f"Failed to save API key: {e}")
        return False
