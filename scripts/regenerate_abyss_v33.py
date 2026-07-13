"""
v3.3 全链路严格约束版
根因修复：character_arcs 无主动措辞 + key_events 不写被动角色名 + Planner 禁止大纲含被动角色名
"""
import json, uuid
from datetime import datetime

WORKS_FILE = r'backend\data\works.json'
with open(WORKS_FILE, 'r', encoding='utf-8') as f:
    works = json.load(f)

new_id = uuid.uuid4().hex[:8]
vol_id = f"v{uuid.uuid4().hex[:8]}"
now = datetime.now().isoformat()

# ===== 根因修复 1：character_arcs 无主动措辞 =====
character_arcs = {
    "林深": {1: "初探深渊，科学狂热", 2: "主导研究，焦虑加深", 3: "发现封印真相，选择坚守"},
    "陈霜": {1: "极度警惕，主张限制链接", 2: "监控事态发展，立场动摇", 3: "决意摧毁装置，与林深对立"},
    "Dr.索菲娅·米兰": {1: "中立观察，记录数据", 2: "破译符号，发现警告信息", 3: "理解封印本质，成为调解者"},
    # 赵海 Ch2：用纯粹被动措辞，不出现"呓语/说话/发声"等主动词汇
    "赵海": {1: "正常操作通讯设备，初次精神链接",
             2: "精神被侵蚀，处于深度昏迷，状态仅通过监控数据体现",
             3: "完全被深渊占据，成为传声筒"},
    "深渊之眼": {1: "以发光符号初次接触", 2: "通过结构体符号传递信息", 3: "展露真面目"}
}

# ===== 根因修复 2：chapter_participation 严格定义 =====
chapter_participation = {
    1: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
    2: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "被动", "深渊之眼": "主动"},
    3: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
}

# chapter_characters：赵海不在 Ch2 出场表中（严格被动 = 不出场）
chapter_characters = [
    {"chapter_num": 1, "title": "寂静深海",
     "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
    {"chapter_num": 2, "title": "符号密语",
     "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "深渊之眼"]},
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

new_work = {
    "id": new_id,
    "title": "深渊回响 v3.3（全链路严格约束版）",
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
        # ===== 根因修复 3：大纲中不出现被动角色名 =====
        "outline": (
            "第1章「寂静深海」：深渊计划下潜至马里亚纳海沟8000米深处。"
            "林深、陈霜、索菲娅、赵海四人首次接触深渊之眼。"
            "陈霜主张限制链接深度；林深想深入探索。赵海的精神率先受到轻微影响。"
            "\n\n"
            "第2章「符号密语」：索菲娅在结构体上发现可破译的符号。"
            "陈霜注意到通讯操作员的脑波数据出现异常，将其隔离在医疗舱进行观察。"
            "索菲娅破译出警告——「不要让它完整地听见你」。"
            "陈霜主张切断所有链接，林深和索菲娅认为需继续研究。"
            "陈霜以安保负责人身份建立严格链接协议。"
            "通讯操作员的状态仅通过监控屏幕上的脑波数据和陈霜的口头报告间接体现。"
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
        "character_arcs": character_arcs,
        "chapter_participation": chapter_participation
    }],
    "created_at": now, "updated_at": now,
    "genre": "科幻", "style": "克苏鲁+硬科幻"
}

works.insert(0, new_work)
with open(WORKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(works, f, ensure_ascii=False, indent=2)

# ===== 生成配置 =====
config = {
    "work_id": new_id, "volume_id": vol_id,
    "work_title": "深渊回响 v3.3 (全链路严格约束版)",
    "genre": "科幻", "style": "克苏鲁+硬科幻",
    "world_setting": new_work["world_setting"],
    "foreshadowings": new_work["foreshadowings"],
    "characters": [
        {"name": c["name"],
         "identity": c["identity"],
         "brief": c["brief"]}
        for c in characters_narrative
    ],
    "chapters": [
        {"chapter_num": 1, "title": "寂静深海",
         "theme": "首次下潜，接触深渊之眼",
         "key_events": [
             "下潜至8000米",
             "首次接触深渊之眼",
             "团队产生分歧",
             "赵海首次链接异常"
         ]},
        # ===== 根因修复 4：key_events 不出现被动角色名 =====
        {"chapter_num": 2, "title": "符号密语",
         "theme": "符号破译与通讯操作员的精神恶化",
         "key_events": [
             "索菲娅破译符号发现警告信息",
             "通讯操作员脑波数据异常，被隔离至医疗舱",
             "陈霜要求切断链接遭林深和索菲娅反对",
             "陈霜建立强制链接协议",
             "通讯操作员的状态仅通过监控数据和陈霜的口头转述体现"
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
with open(r'scripts\abyss_v33_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"[OK] 深渊回响 v3.3 (全链路严格约束版)")
print(f"  work_id: {new_id}")
print(f"  volume_id: {vol_id}")
print(f"  出场表:")
for cc in chapter_characters:
    print(f"    第{cc['chapter_num']}章《{cc['title']}》: {', '.join(cc['characters'])}")
print(f"  赵海 Ch2 弧线: {character_arcs['赵海'][2]}")
print(f"  赵海 Ch2 参与类型: {chapter_participation[2]['赵海']}")
print(f"  Ch2 key_events 不含赵海名: [√ 已修复]")
