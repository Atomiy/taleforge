import uuid
from pydantic import BaseModel, model_validator
from typing import List, Optional
from datetime import datetime


class Volume(BaseModel):
    """卷 - 作品与章节之间的中间层级。"""
    id: str = ""
    number: int = 1
    title: str = "第一卷"
    chapter_ids: List[str] = []  # 本卷包含的章节ID
    # 卷规划字段
    outline: str = ""  # 卷的故事大纲
    responsibility: str = ""  # 本卷在整部作品中的职责（如：引入冲突、推进高潮、收束结局）
    connection_to_prev: str = ""  # 与上一卷的衔接
    connection_to_next: str = ""  # 对下一卷的铺垫
    characters: List[dict] = []  # 本卷出场人物（含状态描述）
    foreshadowings: List[str] = []  # 本卷伏笔清单
    # 跨章人物出场表
    chapter_characters: List[dict] = []  # 每章出场人物列表
    # 格式: [
    #   {"chapter_num": 1, "title": "深渊低语", "characters": ["林深", "陈霜", "赵海"]},
    #   {"chapter_num": 2, "title": "隐藏信息", "characters": ["林深", "陈霜", "索菲娅"]},
    # ]
    character_appearance_map: dict = {}  # 角色→章节映射，自动生成
    # 格式: {"林深": [1,2,3], "陈霜": [1,2,3], "王磊": [3]}
    # 角色弧线状态表（方案B：每角色每章的剧情状态）
    character_arcs: dict = {}
    # {"赵海": {1: "正常操作，初次链接", 2: "昏迷被侵蚀，仅呓语", 3: "成为深渊传声筒"}}
    # 每章角色参与类型（方案B：主动/被动/缺席）
    chapter_participation: dict = {}
    # {1: {"林深":"主动", "赵海":"主动"}, 2: {"林深":"主动", "赵海":"被动"}}
    # 每章角色出场目的（v0.4.0 叙事功能分类）
    chapter_purpose: dict = {}
    # {1: {"赵海": ["信息提供", "情感锚点"]}, 2: {"深渊之眼": ["冲突制造", "氛围渲染"]}}
    # 可用功能类型: 推进剧情/塑造人物/表达主题/营造氛围
    # 推进剧情受限子类: 信息提供/冲突制造/催化事件

    @model_validator(mode='after')
    def ensure_id(self):
        if not self.id:
            self.id = f"v{uuid.uuid4().hex[:8]}"
        # 自动从 chapter_characters 同步 character_appearance_map
        if self.chapter_characters:
            mapping = {}
            for entry in self.chapter_characters:
                cn = entry.get("chapter_num", 0)
                for cname in entry.get("characters", []):
                    mapping.setdefault(cname, []).append(cn)
            self.character_appearance_map = mapping
        # 自动推断未设置的出场目的（保存时触发）
        if self.chapter_characters:
            for entry in self.chapter_characters:
                cn = entry.get("chapter_num", 0)
                p_map = self.chapter_participation.get(cn, {})
                purpose_map = self.chapter_purpose.get(cn, {})
                changed = False
                for cname in entry.get("characters", []):
                    if cname in purpose_map and purpose_map[cname]:
                        continue  # 用户已填写，不覆盖
                    role_type = p_map.get(cname, "主动")
                    if role_type == "主动":
                        purpose_map[cname] = ["推进剧情"]
                        changed = True
                    elif role_type == "被动":
                        purpose_map[cname] = ["塑造人物", "表达主题", "营造氛围"]
                        changed = True
                if changed:
                    self.chapter_purpose[cn] = purpose_map
        return self


class Work(BaseModel):
    id: str
    title: str
    world_setting: str = ""
    foreshadowings: List[str] = []
    outline: str = ""  # 完整大纲
    summary: str = ""  # 内容概要
    chapter_ids: List[str] = []  # 有序的章节ID列表（兼容旧数据+同步用）
    volumes: List[Volume] = []   # 作品-卷-章节三级结构
    characters: List[dict] = []  # 作品级角色卡片
    # 角色格式: {"name": "角色名", "identity": "身份", "personality": "性格", "motivation": "动机", "brief": "简介"}
    created_at: str = ""
    updated_at: str = ""
    genre: str = "奇幻"
    style: str = "史诗"

    @model_validator(mode='after')
    def sync_volumes(self):
        """双向同步 volumes 和 chapter_ids。
        - 旧数据（volumes空, chapter_ids有值）：自动创建第一卷
        - 新数据（volumes有值）：自动从volumes同步chapter_ids
        """
        if self.volumes:
            # 从 volumes 同步 chapter_ids
            self.chapter_ids = [cid for v in self.volumes for cid in v.chapter_ids]
        elif self.chapter_ids:
            # 旧数据兼容：创建默认第一卷第 N 章
            self.volumes = [Volume(
                id=f"v{uuid.uuid4().hex[:8]}",
                number=1,
                title="第一卷",
                chapter_ids=list(self.chapter_ids)
            )]
        return self
