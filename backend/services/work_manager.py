import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from backend.models.work import Work, Volume
from backend.config import PROJECT_ROOT as _PROJECT_ROOT

_works_file = os.environ.get("WORKS_FILE")
if _works_file:
    WORKS_FILE = _works_file if os.path.isabs(_works_file) else os.path.join(_PROJECT_ROOT, _works_file)
else:
    WORKS_FILE = os.path.join(_PROJECT_ROOT, "backend", "data", "works.json")


class WorkManager:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        os.makedirs(os.path.dirname(WORKS_FILE), exist_ok=True)
        if not os.path.exists(WORKS_FILE):
            with open(WORKS_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save_work(self, work: Work) -> None:
        works = self.get_all_works()
        works.insert(0, work)
        with open(WORKS_FILE, "w", encoding="utf-8") as f:
            json.dump([w.model_dump() for w in works], f, ensure_ascii=False, default=str)

    def get_all_works(self) -> List[Work]:
        try:
            with open(WORKS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [Work(**w) for w in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_work_by_id(self, work_id: str) -> Optional[Work]:
        works = self.get_all_works()
        return next((w for w in works if w.id == work_id), None)

    def delete_work(self, work_id: str) -> bool:
        works = self.get_all_works()
        new_works = [w for w in works if w.id != work_id]
        if len(new_works) != len(works):
            self._save_all(new_works)
            return True
        return False

    def update_work(self, work_id: str, data: dict) -> Optional[Work]:
        works = self.get_all_works()
        for i, w in enumerate(works):
            if w.id == work_id:
                work_dict = w.model_dump()
                work_dict.update(data)
                work_dict["id"] = w.id
                work_dict["created_at"] = w.created_at
                work_dict["updated_at"] = datetime.now().isoformat()
                works[i] = Work(**work_dict)
                self._save_all(works)
                return works[i]
        return None

    def add_chapter_to_work(self, work_id: str, story_id: str, volume_id: str = "") -> Optional[Work]:
        """追加 chapter_id 到指定卷（或末卷）。"""
        works = self.get_all_works()
        for i, w in enumerate(works):
            if w.id == work_id:
                work_dict = w.model_dump()
                updated_work = Work(**work_dict)

                # 确定目标卷
                if volume_id:
                    target = next((v for v in updated_work.volumes if v.id == volume_id), None)
                else:
                    target = updated_work.volumes[-1] if updated_work.volumes else None

                if not target:
                    # 没有卷则创建第一卷
                    target = Volume(id=f"v{uuid.uuid4().hex[:8]}", number=1, title="第一卷", chapter_ids=[])
                    updated_work.volumes.append(target)

                if story_id not in target.chapter_ids:
                    target.chapter_ids.append(story_id)

                # model_validator 会自动同步 chapter_ids
                updated_work.updated_at = datetime.now().isoformat()
                works[i] = updated_work
                self._save_all(works)
                return works[i]
        return None

    def remove_chapter_from_work(self, work_id: str, story_id: str) -> Optional[Work]:
        """从所属卷中移除指定 chapter_id。"""
        works = self.get_all_works()
        for i, w in enumerate(works):
            if w.id == work_id and any(story_id in v.chapter_ids for v in w.volumes):
                work_dict = w.model_dump()
                updated_work = Work(**work_dict)
                for v in updated_work.volumes:
                    v.chapter_ids = [cid for cid in v.chapter_ids if cid != story_id]
                # 移除空卷
                updated_work.volumes = [v for v in updated_work.volumes if v.chapter_ids]
                updated_work.updated_at = datetime.now().isoformat()
                works[i] = updated_work
                self._save_all(works)
                return works[i]
        return None

    # --- 卷管理 ---

    def add_volume(self, work_id: str, title: str = "") -> Optional[Work]:
        """为作品添加新卷。"""
        works = self.get_all_works()
        for i, w in enumerate(works):
            if w.id == work_id:
                next_num = max((v.number for v in w.volumes), default=0) + 1
                new_vol = Volume(
                    id=f"v{uuid.uuid4().hex[:8]}",
                    number=next_num,
                    title=title or f"第{['一','二','三','四','五','六','七','八','九','十'][min(next_num-1,9)]}卷",
                    chapter_ids=[]
                )
                work_dict = w.model_dump()
                work_dict["volumes"] = [v.model_dump() for v in w.volumes] + [new_vol.model_dump()]
                work_dict["updated_at"] = datetime.now().isoformat()
                works[i] = Work(**work_dict)
                self._save_all(works)
                return works[i]
        return None

    def remove_volume(self, work_id: str, volume_id: str) -> Optional[Work]:
        """删除作品中的卷（不删除卷内的章节，章节会移入前一卷或末卷）。"""
        works = self.get_all_works()
        for i, w in enumerate(works):
            target = next((v for v in w.volumes if v.id == volume_id), None)
            if not target:
                continue
            work_dict = w.model_dump()
            remaining = [v for v in w.volumes if v.id != volume_id]
            # 将被删卷的章节并入前一卷（或末卷）
            if target.chapter_ids and remaining:
                if len(remaining) >= target.number:
                    remaining[target.number - 1].chapter_ids.extend(target.chapter_ids)
                else:
                    remaining[-1].chapter_ids.extend(target.chapter_ids)
            work_dict["volumes"] = [v.model_dump() for v in remaining]
            work_dict["updated_at"] = datetime.now().isoformat()
            works[i] = Work(**work_dict)
            self._save_all(works)
            return works[i]
        return None

    def update_volume(self, work_id: str, volume_id: str, data: dict) -> Optional[Work]:
        """更新卷信息（标题等）。"""
        works = self.get_all_works()
        for i, w in enumerate(works):
            target = next((v for v in w.volumes if v.id == volume_id), None)
            if not target:
                continue
            work_dict = w.model_dump()
            for v in work_dict["volumes"]:
                if v["id"] == volume_id:
                    v.update(data)
                    break
            work_dict["updated_at"] = datetime.now().isoformat()
            works[i] = Work(**work_dict)
            self._save_all(works)
            return works[i]
        return None

    def generate_work_id(self) -> str:
        return str(uuid.uuid4())[:8]

    def _save_all(self, works: List[Work]):
        with open(WORKS_FILE, "w", encoding="utf-8") as f:
            json.dump([w.model_dump() for w in works], f, ensure_ascii=False, default=str)
