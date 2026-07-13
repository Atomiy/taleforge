from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class Character(BaseModel):
    name: str
    age: str = Field(default="", description="年龄")
    identity: str = Field(description="身份/职业")
    appearance: str = Field(default="", description="外貌特征")
    personality: str = Field(default="", description="性格特点")
    background: str = Field(default="", description="背景故事")
    motivation: str = Field(default="", description="角色动机/目标")
    relationships: List[Dict[str, str]] = Field(default_factory=list, description="角色关系")
    drive: str = Field(default="", description="驱动层：核心动机和恐惧")
    contradiction: str = Field(default="", description="矛盾层：表面与内心的冲突")
    arc: str = Field(default="", description="弧线层：从XX到XX的变化")
    stage_states: Dict[str, str] = Field(default_factory=dict)
    speaking_style: str = Field(default="")

class Stage(BaseModel):
    name: str
    ratio: str
    plot_points: List[str] = Field(default_factory=list)
    word_count: str = Field(default="")

class Chapter(BaseModel):
    chapter_num: int
    title: str
    stage: str
    key_events: List[str] = Field(default_factory=list)

class Outline(BaseModel):
    title: str
    structure_type: str
    conflict_type: str
    stages: List[Stage] = Field(default_factory=list)
    chapters: List[Chapter] = Field(default_factory=list)

class StoryRequest(BaseModel):
    theme: str = Field(description="故事主题")
    genre: str = Field(default="短篇小说", description="体裁：小说、剧本、童话、诗歌等")
    style: str = Field(default="温馨", description="风格：悬疑、温馨、科幻、古风等")
    length: int = Field(default=2000, description="目标字数")
    background: str = Field(default="", description="故事背景/世界观")
    perspective: str = Field(default="第三人称全知", description="叙事视角")
    conflict: str = Field(default="人与人", description="冲突类型")
    mood: str = Field(default="轻松愉快", description="情感基调")
    outline: str = Field(default="", description="故事梗概")
    characters: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="角色设定")
    api_key: Optional[str] = Field(default="", description="API Key")
    previous_story_id: Optional[str] = Field(default="", description="续写的前一篇故事ID")
    continuation_mode: str = Field(default="next_chapter", description="续写模式：next_chapter(下一章)/continuation(继续)/expansion(扩展)")
    world_setting: Optional[str] = Field(default="", description="世界观设定")
    foreshadowings: Optional[List[str]] = Field(default_factory=list, description="伏笔清单")
    work_id: Optional[str] = Field(default="", description="关联作品ID")
    volume_id: Optional[str] = Field(default="", description="关联卷ID")
    chapter_number: Optional[int] = Field(default=0, description="章节序号")

class Story(BaseModel):
    id: str
    title: str
    content: str
    theme: str
    genre: str
    style: str
    outline: Optional[Outline] = None
    characters: Optional[List[Character]] = None
    created_at: datetime
    word_count: int = Field(default=0)
    series_id: Optional[str] = Field(default="", description="系列故事ID")
    series_order: int = Field(default=1, description="系列中的顺序")
    world_setting: Optional[str] = Field(default="", description="世界观设定")
    foreshadowings: Optional[List[str]] = Field(default_factory=list, description="伏笔清单")
    previous_story_id: Optional[str] = Field(default="", description="前一篇故事ID")
    favorite: bool = Field(default=False, description="是否收藏")

class StoryHistoryResponse(BaseModel):
    stories: List[Story]
    total: int