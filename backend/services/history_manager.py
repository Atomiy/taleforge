import json
import os
import uuid
import threading
from datetime import datetime
from typing import List, Optional
from backend.models import Story
from backend.config import STORIES_FILE

_lock = threading.Lock()


class HistoryManager:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        with _lock:
            if not os.path.exists(STORIES_FILE):
                with open(STORIES_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f)

    def save_story(self, story: Story) -> None:
        with _lock:
            stories = self._read_unlocked()
            stories.insert(0, story)
            self._write_unlocked(stories)

    def get_all_stories(self) -> List[Story]:
        with _lock:
            return self._read_unlocked()

    def get_story_by_id(self, story_id: str) -> Optional[Story]:
        with _lock:
            stories = self._read_unlocked()
            return next((s for s in stories if s.id == story_id), None)

    def delete_story(self, story_id: str) -> bool:
        with _lock:
            stories = self._read_unlocked()
            new_stories = [s for s in stories if s.id != story_id]
            if len(new_stories) != len(stories):
                self._write_unlocked(new_stories)
                return True
            return False

    def _calculate_word_count(self, content: str) -> int:
        import re
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        english_words = len(re.findall(r'[a-zA-Z]+', content))
        return chinese_chars + english_words

    def update_story(self, story_id: str, updated_data: dict) -> Optional[Story]:
        with _lock:
            stories = self._read_unlocked()
            for i, s in enumerate(stories):
                if s.id == story_id:
                    story_dict = s.model_dump()
                    if "content" in updated_data:
                        updated_data["word_count"] = self._calculate_word_count(updated_data["content"])
                    story_dict.update(updated_data)
                    story_dict["id"] = s.id
                    story_dict["created_at"] = s.created_at
                    stories[i] = Story(**story_dict)
                    self._write_unlocked(stories)
                    return stories[i]
            return None

    def toggle_favorite(self, story_id: str) -> Optional[Story]:
        with _lock:
            stories = self._read_unlocked()
            for i, s in enumerate(stories):
                if s.id == story_id:
                    stories[i].favorite = not s.favorite
                    self._write_unlocked(stories)
                    return stories[i]
            return None

    def generate_id(self) -> str:
        return str(uuid.uuid4())[:8]

    def _read_unlocked(self) -> List[Story]:
        try:
            with open(STORIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Story(**s) for s in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_unlocked(self, stories: List[Story]) -> None:
        with open(STORIES_FILE, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in stories], f, ensure_ascii=False, default=str)
