"""
v3.5 全链路出场目的约束版
基于叙事功能分类体系（推进剧情/塑造人物/表达主题/营造氛围）
"""
import json, uuid
from datetime import datetime

WORKS_FILE = r'backend\data\works.json'
with open(WORKS_FILE, 'r', encoding='utf-8') as f:
    works = json.load(f)

new_id = uuid.uuid4().hex[:8]
vol_id = f"v{uuid.uuid4().hex[:8]}"
now = datetime.now().isoformat()

# ===== 角色弧线（无矛盾措辞） =====
character_arcs = {
    "林深": {1: "初探深渊，科学狂热", 2: "主导研究符号，质疑封印", 3: "发现真相，选择坚守"},
    "陈霜": {1: "极度警惕，主张限制链接", 2: "设备异常加剧不信任", 3: "决意摧毁装置，与林深对立"},
    "Dr.索菲娅·米兰": {1: "中立观察，记录数据", 2: "破译符号，见证动态变化", 3: "理解封印本质，成为调解者"},
    # 赵海 Ch2：纯被动措辞，不出现"呓语/说话"等主动词汇
    "赵海": {1: "正常操作通讯设备，初次链接异常",
             2: "精神被侵蚀处于深度昏迷，状态仅通过监控数据体现",
             3: "完全被深渊占据成为传声筒"},
    "深渊之眼": {1: "以发光符号初次接触",
                  2: "通过结构体符号主动发送信号，对不同人展现不同面孔",
                  3: "展露真面目，试图突破封印"},
}

# ===== 参与类型 + 出场目的（完全自洽） =====
chapter_participation = {
    1: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
    # Ch2: 赵海=被动，目的=信息提供+情感锚点+主题载体
    2: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "被动", "深渊之眼": "主动"},
    3: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
}

chapter_purpose = {
    2: {
        "赵海": ["信息提供", "情感锚点", "主题载体"],
        "深渊之眼": ["冲突制造", "氛围渲染"],
    },
    3: {
        "深渊之眼": ["冲突制造", "主题载体"],
    },
}

chapter_characters = [
    {"chapter_num": 1, "title": "寂静深海",
     "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
    {"chapter_num": 2, "title": "符号密语",
     "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
    {"chapter_num": 3, "title": "裂痕",
     "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
]

characters_narrative = [
    {"name": "林深", "identity": "深海地质学家，深渊计划首席科学家",
     "brief": "理性派，坚信科学能解释一切"},
    {"name": "陈霜", "identity": "前海军少校，深海潜航员兼安保负责人",
     "brief": "技术顶尖，极度警惕，军事背景让她怀疑未知事物"},
    {"name": "Dr.索菲娅·米兰", "identity": "符号学家兼生物学家",
     "brief": "兼具符号破译和生物分析能力，理性调解者"},
    {"name": "赵海", "identity": "通讯工程师，精神链接装置操作员",
     "brief": "最敏感，最先被深渊之眼侵蚀精神"},
    {"name": "深渊之眼", "identity": "马里亚纳海沟深处的未知意识体",
     "brief": "古老意识，动机不明，对每个人展现不同面貌"},
]

new_works = [
    {
        "id": new_id, "title": "深渊回响 v3.5（出场目的约束版）",
        "world_setting": (
            "2124年，人类首次与马里亚纳海沟深渊的未知意识体建立精神链接。"
            "该意识体自称「深渊之眼」，声称板块运动并非自然现象，而是某种古老封印在苏醒。"
            "深海探测队在海底发现非自然巨大结构体，表面覆盖无法解析的符号。"
            "各大国秘密组建「深渊计划」，派遣精英团队潜入深渊调查真相。"
        ),
        "foreshadowings": [
            "深渊意识并非善意",
            "板块运动与封印有关",
            "符号在缓慢变化",
            "赵海精神被深渊侵蚀"
        ],
        "outline": "", "summary": "", "chapter_ids": [],
        "volumes": [{
            "id": vol_id, "number": 1, "title": "第一卷：深渊之眼",
            "chapter_ids": [],
            "outline": (
                "第1章「寂静深海」：深渊计划下潜至马里亚纳海沟8000米深处。"
                "林深、陈霜、索菲娅、赵海四人首次接触深渊之眼。"
                "陈霜主张限制链接深度；林深想深入探索。赵海的精神率先受到轻微影响。"
                "\n\n"
                "第2章「符号密语」：结构体符号发生肉眼可见的变化，索菲娅发现它们在缓慢流动重组。"
                "深渊之眼通过符号向每个人发送不同信息——林深看到远古文明蓝图，"
                "陈霜看到未来灾难的片段，索菲娅看到警告字符。"
                "陈霜的设备在接触符号12小时后开始间歇性失灵。"
                "陈霜主张切断所有链接并撤离，林深和索菲娅认为需继续研究。"
                "通讯操作员因精神链接后遗症在医疗舱静养——他的脑波数据成为团队决策的关键参考。"
                "\n\n"
                "第3章「裂痕」：深渊之眼对不同队员展现不同面孔。"
                "林深看到远古海洋文明，陈霜看到军事灾难预言，索菲娅看到符号完整序列。"
                "赵海完全被深渊占据成为传声筒。"
                "陈霜试图摧毁链接装置，林深和索菲娅阻止。以陈霜退出任务收尾。"
            ),
            "responsibility": "引出核心悬念，建立探索vs警惕的团队冲突，赵海侵蚀线贯穿三章",
            "connection_to_prev": "第一卷，无前卷",
            "connection_to_next": "陈霜与林深的冲突成为第二卷核心驱动力",
            "characters": characters_narrative,
            "foreshadowings": [
                "深渊之眼对不同人展现不同面孔",
                "结构体符号包含警告",
                "赵海精神异常是侵蚀前兆",
                "陈霜与林深的矛盾"
            ],
            "chapter_characters": chapter_characters,
            "character_appearance_map": {},
            "character_arcs": character_arcs,
            "chapter_participation": chapter_participation,
            "chapter_purpose": chapter_purpose,
        }],
        "created_at": now, "updated_at": now,
        "genre": "科幻", "style": "克苏鲁+硬科幻",
    }
]

for w in new_works:
    works.insert(0, w)

with open(WORKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(works, f, ensure_ascii=False, indent=2)

# ===== 生成配置 =====
config = {
    "work_id": new_id, "volume_id": vol_id,
    "work_title": "深渊回响 v3.5 (出场目的约束版)",
    "genre": "科幻", "style": "克苏鲁+硬科幻",
    "world_setting": new_works[0]["world_setting"],
    "foreshadowings": new_works[0]["foreshadowings"],
    "characters": [
        {"name": c["name"], "identity": c["identity"], "brief": c["brief"]}
        for c in characters_narrative
    ],
    "chapters": [
        {"chapter_num": 1, "title": "寂静深海",
         "theme": "首次下潜，接触深渊之眼",
         "key_events": [
             "下潜至8000米", "首次接触深渊之眼",
             "团队产生分歧", "赵海首次链接异常"
         ]},
        # Ch2 key_events 不依赖赵海名字
        {"chapter_num": 2, "title": "符号密语",
         "theme": "结构体符号动态变化，深渊之眼主动发送信号",
         "key_events": [
             "结构体符号肉眼可见地流动重组",
             "索菲娅发现符号有编码信息，正在实时变化",
             "深渊之眼通过符号向不同人展现不同信息",
             "陈霜设备12小时后间歇性失灵",
             "通讯操作员的监控数据出现异常模式",
             "陈霜要求撤离被林深和索菲娅反对",
             "陈霜单方面建立链接安全协议",
         ]},
        {"chapter_num": 3, "title": "裂痕",
         "theme": "深渊之眼展露真面，团队彻底分裂",
         "key_events": [
             "不同队员看到不同幻象",
             "赵海成为传声筒",
             "陈霜试图摧毁装置",
             "林深和索菲娅阻止",
             "陈霜退出任务"
         ]}
    ]
}

import os
os.makedirs('scripts', exist_ok=True)
with open(r'scripts\abyss_v35_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"[OK] 深渊回响 v3.5 (出场目的约束版)")
print(f"  work_id: {new_id}  volume_id: {vol_id}")
for cc in chapter_characters:
    print(f"  第{cc['chapter_num']}章《{cc['title']}》: {', '.join(cc['characters'])}")
print(f"  赵海 Ch2 参与: 被动(信息提供,情感锚点,主题载体)")
print(f"  Ch2 key_events 不写赵海名: [已对齐]")
