"""
深渊回响 v2 重生成脚本
对比验证：旧版(无出场表) vs 新版(含跨章人物出场表硬约束)
"""
import json
import uuid
import os
from datetime import datetime

WORKS_FILE = r'backend\data\works.json'
STORIES_FILE = r'backend\data\stories.json'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 读取现有数据 ==========
works = load_json(WORKS_FILE)
stories = load_json(STORIES_FILE)

# ========== 创建新作品 v2 ==========
now = datetime.now().isoformat()
new_id = uuid.uuid4().hex[:8]

# 角色出场表（按章节分配）
chapter_characters = [
    {
        "chapter_num": 1,
        "title": "寂静深海",
        "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]
    },
    {
        "chapter_num": 2,
        "title": "符号密语",
        "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "深渊之眼"]
        # 赵海在本章不出场（精神异常被隔离）
    },
    {
        "chapter_num": 3,
        "title": "裂痕",
        "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]
        # 赵海回归，但精神已被深渊影响
    }
]

new_work = {
    "id": new_id,
    "title": "深渊回响 v2（跨章出场表验证）",
    "world_setting": "2124年，人类首次与来自马里亚纳海沟深渊的未知意识体建立微弱的精神链接。该意识体自称\"深渊之眼\"，声称地球的板块运动并非自然现象，而是某种被封印的古老机制在苏醒。深海探测队发现海沟底部存在非自然的巨大结构体，表面覆盖着无法解析的符号。随着全球各地深海地震频发，各大国秘密组建\"深渊计划\"，派遣精英团队潜入深渊调查真相。",
    "foreshadowings": [
        "深渊意识并非善意",
        "板块运动与封印有关",
        "巨大结构体上的符号在缓慢变化"
    ],
    "outline": "",
    "summary": "",
    "chapter_ids": [],
    "volumes": [
        {
            "id": f"v{uuid.uuid4().hex[:8]}",
            "number": 1,
            "title": "第一卷：深渊之眼",
            "chapter_ids": [],
            "outline": "第1章「寂静深海」：深渊计划组建完毕，主角团队乘深海探测器下潜至马里亚纳海沟8000米深处，首次接触深渊意识体，团队内部因对未知的态度分歧产生裂痕。第2章「符号密语」：科学家发现结构体上的符号与古苏美尔文字存在部分对应关系，翻译出一句警告——\"不要让它完整地听见你\"。第3章「裂痕」：深渊意识体对不同队员展现出不同的\"面孔\"，有人听到已故亲人的呼唤，有人听到未来灾难的预言。团队分裂为相信派与怀疑派，怀疑派试图摧毁精神链接装置。",
            "responsibility": "引出核心悬念（深渊意识体与板块封印），建立人物关系和团队内部冲突，为后续揭示深渊真相做铺垫",
            "connection_to_prev": "第一卷，无前卷",
            "connection_to_next": "深渊真相应在第二卷逐步揭示，本卷结束时留下至少两个未解答的核心谜题",
            "characters": [
                {"name": "林深", "identity": "深海地质学家", "brief": "深渊计划首席科学家，理性派"},
                {"name": "陈霜", "identity": "海军深海潜航员", "brief": "前海军少校，技术顶尖，极度警惕"},
                {"name": "Dr.索菲娅·米兰", "identity": "符号学家", "brief": "语言学家，性格谨慎，调解者"},
                {"name": "赵海", "identity": "通讯工程师", "brief": "最先出现精神异常"},
                {"name": "深渊之眼", "identity": "未知意识体", "brief": "古老意识，动机不明"}
            ],
            "foreshadowings": [
                "深渊意识体对不同人展现不同面孔",
                "结构体符号包含警告信息",
                "通讯工程师赵海精神异常"
            ],
            "chapter_characters": chapter_characters
        }
    ],
    "created_at": now,
    "updated_at": now,
    "genre": "科幻",
    "style": "克苏鲁+硬科幻"
}

# ========== 写入 ==========
works.insert(0, new_work)
save_json(WORKS_FILE, works)

print("[OK] 已创建新作品: 深渊回响 v2 (跨章出场表验证)")
print(f"   work_id: {new_id}")
print(f"   volume_id: {new_work['volumes'][0]['id']}")
print(f"   跨章人物出场表已配置: {len(chapter_characters)} 章")
for cc in chapter_characters:
    print(f"     第{cc['chapter_num']}章《{cc['title']}》: {', '.join(cc['characters'])}")

# 输出配置信息供后续使用
config = {
    "work_id": new_id,
    "volume_id": new_work['volumes'][0]['id'],
    "work_title": "深渊回响 v2 (跨章出场表验证)",
    "genre": "科幻",
    "style": "克苏鲁+硬科幻",
    "world_setting": new_work["world_setting"],
    "foreshadowings": new_work["foreshadowings"],
    "characters": [
        {"name": "林深", "age": "35", "identity": "深海地质学家", "appearance": "中等身材，深邃的眼神中透着学者的敏锐", "personality": "理性、冷静、执着"},
        {"name": "陈霜", "age": "32", "identity": "海军深海潜航员", "appearance": "身材精悍，眼神锐利如鹰", "personality": "警惕、果敢、寡言"},
        {"name": "Dr.索菲娅·米兰", "age": "40", "identity": "符号学家", "appearance": "金发盘起，戴着细框眼镜", "personality": "谨慎、细致、善于调停"},
        {"name": "赵海", "age": "28", "identity": "通讯工程师", "appearance": "年轻，面色略显苍白", "personality": "敏感、好奇、易受影响"}
    ],
    "chapters": [
        {
            "chapter_num": 1,
            "title": "寂静深海",
            "theme": "深渊计划组建完毕，主角团队首次接触深渊意识体",
            "key_events": ["团队下潜至8000米", "首次接触深渊之眼", "团队内部产生分歧"]
        },
        {
            "chapter_num": 2,
            "title": "符号密语",
            "theme": "结构体符号破译，发现警告信息",
            "key_events": ["符号与古苏美尔文字对应", "翻译出警告", "赵海精神异常被隔离"]
        },
        {
            "chapter_num": 3,
            "title": "裂痕",
            "theme": "深渊意识体展现不同面孔，团队分裂",
            "key_events": ["不同队员看到不同幻象", "相信派vs怀疑派", "试图摧毁链接装置"]
        }
    ]
}

config_path = r'scripts\abyss_v2_config.json'
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)
print(f"\n[OK] 配置文件已保存: {config_path}")
print(f"\n下一步：启动服务器后，依次生成3章内容")
print(f"  python start.py")
