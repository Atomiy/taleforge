import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from backend.models import Story
from backend.config import STORIES_FILE

class HistoryManager:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(STORIES_FILE):
            with open(STORIES_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_story(self, story: Story) -> None:
        stories = self.get_all_stories()
        stories.insert(0, story)
        with open(STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in stories], f, ensure_ascii=False, default=str)

    def get_all_stories(self) -> List[Story]:
        try:
            with open(STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Story(**s) for s in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_story_by_id(self, story_id: str) -> Optional[Story]:
        stories = self.get_all_stories()
        return next((s for s in stories if s.id == story_id), None)

    def delete_story(self, story_id: str) -> bool:
        stories = self.get_all_stories()
        new_stories = [s for s in stories if s.id != story_id]
        if len(new_stories) != len(stories):
            with open(STORIES_FILE, "w", encoding="utf-8") as f:
                json.dump([s.model_dump() for s in new_stories], f, ensure_ascii=False, default=str)
            return True
        return False

    def _calculate_word_count(self, content: str) -> int:
        """计算文本的字数（中文字数 + 英文单词数）。"""
        import re
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        return chinese_chars + english_words

    def update_story(self, story_id: str, updated_data: dict) -> Optional[Story]:
        """更新故事内容。返回更新后的 Story 对象，若未找到则返回 None。"""
        stories = self.get_all_stories()
        for i, s in enumerate(stories):
            if s.id == story_id:
                story_dict = s.model_dump()
                # 如果更新了 content，自动重新计算 word_count
                if "content" in updated_data:
                    updated_data["word_count"] = self._calculate_word_count(updated_data["content"])
                story_dict.update(updated_data)
                # 保持 id 和 created_at 不变
                story_dict["id"] = s.id
                story_dict["created_at"] = s.created_at
                stories[i] = Story(**story_dict)
                with open(STORIES_FILE, "w", encoding="utf-8") as f:
                    json.dump([st.model_dump() for st in stories], f, ensure_ascii=False, default=str)
                return stories[i]
        return None

    def toggle_favorite(self, story_id: str) -> Optional[Story]:
        """切换故事的收藏状态。返回更新后的 Story 对象，若未找到则返回 None。"""
        stories = self.get_all_stories()
        for i, s in enumerate(stories):
            if s.id == story_id:
                stories[i].favorite = not s.favorite
                with open(STORIES_FILE, "w", encoding="utf-8") as f:
                    json.dump([st.model_dump() for st in stories], f, ensure_ascii=False, default=str)
                return stories[i]
        return None

    def generate_id(self) -> str:
        return str(uuid.uuid4())[:8]