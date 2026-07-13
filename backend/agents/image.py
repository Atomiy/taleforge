import json
import requests
from typing import Dict, Any
from backend.agents.base import BaseAgent
from backend.config import COMFYUI_ENABLED, COMFYUI_API_URL

class ImageAgent(BaseAgent):
    def __init__(self, llm_client):
        super().__init__(llm_client, "image", 0.7)
        self.enabled = COMFYUI_ENABLED

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {"images": []}

        final_text = context.get("final", "")
        request = context["request"]

        prompt = f"""请从以下故事中识别1-3个最具画面感的关键场景，每个场景用50字以内的中文描述：

{final_text[:2000]}

请以JSON格式输出：
{{"scenes": ["场景描述1", "场景描述2"]}}"""

        messages = [{"role": "system", "content": "你是场景提取专家"}, {"role": "user", "content": prompt}]
        result = await self.llm.chat(messages, temperature=0.5, max_tokens=500)

        try:
            data = json.loads(result)
            scenes = data.get("scenes", [])
        except json.JSONDecodeError:
            return {"images": []}

        images = []
        for i, scene in enumerate(scenes):
            try:
                image_url = await self.generate_image(scene, request.style)
                if image_url:
                    images.append({"scene": scene, "url": image_url})
            except Exception as e:
                self.logger.error(f"Image generation failed for scene '{scene}': {e}")

        return {"images": images}

    async def generate_image(self, scene_desc: str, style: str) -> str:
        import time
        
        style_tags = {
            "温馨": "warm, cozy, soft lighting",
            "悬疑": "mysterious, dark, atmospheric",
            "科幻": "sci-fi, futuristic, cyberpunk",
            "古风": "ancient chinese, traditional, elegant",
            "奇幻": "fantasy, magical, ethereal"
        }
        
        prompt = f"{scene_desc}, {style_tags.get(style, '')}, high quality, detailed, cinematic"
        
        workflow = {
            "prompt": {
                "3": {"inputs": {"text": prompt}},
                "4": {"inputs": {"noise_seed": -1, "steps": 20}},
                "5": {"inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
                "6": {"inputs": {"vae_name": "sd_xl_base_1.0.safetensors"}}
            }
        }

        try:
            response = requests.post(f"{COMFYUI_API_URL}/prompt", json={"prompt": workflow, "client_id": "taleforge"}, timeout=30)
            if response.status_code != 200:
                return ""

            prompt_id = response.json().get("prompt_id")
            if not prompt_id:
                return ""

            for _ in range(60):
                history = requests.get(f"{COMFYUI_API_URL}/history/{prompt_id}", timeout=10)
                if history.status_code == 200:
                    data = history.json()
                    if prompt_id in data:
                        outputs = data[prompt_id].get("outputs", {})
                        for node in outputs.values():
                            if "images" in node:
                                return f"{COMFYUI_API_URL}/view?filename={node['images'][0]['filename']}&subfolder=&prompt_id={prompt_id}"
                time.sleep(1)
        except Exception:
            pass

        return ""