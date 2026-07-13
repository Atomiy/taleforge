"""
深渊回响 v3.2 - 全链路约束 + 参与类型区分版本
方案B轻量实施：主动/被动/缺席 三元约束 + 角色弧线
"""
import json, uuid
from datetime import datetime

WORKS_FILE = r'backend\data\works.json'
with open(WORKS_FILE, 'r', encoding='utf-8') as f:
    works = json.load(f)

new_id = uuid.uuid4().hex[:8]
vol_id = f"v{uuid.uuid4().hex[:8]}"
now = datetime.now().isoformat()

# 方案B：角色弧线状态表
character_arcs = {
    "林深": {1: "初探深渊，科学狂热", 2: "主导研究，焦虑加深，内部分歧", 3: "发现封印真相，选择坚守"},
    "陈霜": {1: "极度警惕，主张限制链接", 2: "监控事态发展，立场开始动摇", 3: "决意摧毁链接装置，与林深对立"},
    "Dr.索菲娅·米兰": {1: "中立观察，记录数据", 2: "破译符号，发现警告信息", 3: "理解封印本质，成为调解者"},
    "赵海": {1: "正常操作通讯设备，初次精神链接", 2: "精神被侵蚀，昏迷中发出呓语", 3: "完全被深渊占据，成为传声筒"},
    "深渊之眼": {1: "以发光符号初次接触人类", 2: "通过符号传递警告和诱惑", 3: "展露真面目，试图突破封印"}
}

# 方案B：每章角色参与类型
chapter_participation = {
    1: {
        "林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动",
        "赵海": "主动", "深渊之眼": "主动"
    },
    2: {
        "林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动",
        "赵海": "被动", "深渊之眼": "被动"
    },
    3: {
        "林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动",
        "赵海": "主动", "深渊之眼": "主动"
    }
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
     "brief": "理性派，坚信科学能解释一切，但深渊之眼动摇了他的世界观"},
    {"name": "陈霜", "identity": "前海军少校，深海潜航员兼任务安保负责人",
     "brief": "技术顶尖，极度警惕，军事背景让她天然怀疑未知事物"},
    {"name": "Dr.索菲娅·米兰", "identity": "符号学家兼生物学家，跨学科研究员",
     "brief": "兼具符号破译和生物分析能力，团队中的理性调解者"},
    {"name": "赵海", "identity": "通讯工程师，精神链接装置操作员",
     "brief": "最敏感，最先与深渊之眼建立深度链接，精神受到侵蚀"},
    {"name": "深渊之眼", "identity": "马里亚纳海沟深处的未知意识体",
     "brief": "古老意识，对不同人展现不同面貌，动机不明"}
]

new_work = {
    "id": new_id,
    "title": "深渊回响 v3.2（参与类型约束版）",
    "world_setting": (
        "2124年，人类首次与来自马里亚纳海沟深渊的未知意识体建立微弱的精神链接。"
        "该意识体自称「深渊之眼」，声称地球的板块运动并非自然现象，而是某种被封印的古老机制在苏醒。"
        "深海探测队发现海沟底部存在非自然的巨大结构体，表面覆盖着无法解析的符号。"
        "各大国秘密组建「深渊计划」，派遣精英团队潜入深渊调查真相。"
    ),
    "foreshadowings": [
        "深渊意识并非善意",
        "板块运动与封印有关",
        "巨大结构体上的符号在缓慢变化",
        "赵海的精神被深渊之眼侵蚀"
    ],
    "outline": "", "summary": "", "chapter_ids": [],
    "volumes": [{
        "id": vol_id, "number": 1, "title": "第一卷：深渊之眼",
        "chapter_ids": [],
        "outline": (
            "第1章「寂静深海」：深渊计划下潜至马里亚纳海沟8000米深处。"
            "林深、陈霜、索菲娅、赵海四人首次接触深渊之眼。"
            "陈霜出于军事本能保持警惕，主张限制链接深度；林深想深入探索。"
            "赵海的精神率先受到轻微影响。"
            "第2章「符号密语」：索菲娅破译结构体符号，发现警告——「不要让它完整地听见你」。"
            "赵海因精神侵蚀加重被隔离在医疗舱。陈霜主张切断链接，林深和索菲娅认为需继续研究。"
            "陈霜以安保负责人身份建立严格链接协议。赵海的状态仅通过索菲娅的监控数据和录音回放呈现。"
            "第3章「裂痕」：深渊之眼对不同队员展现不同面孔。"
            "林深看到远古海洋文明，陈霜看到军事灾难预言，索菲娅看到符号完整序列。"
            "赵海完全被深渊占据成为传声筒。"
            "陈霜试图摧毁链接装置，林深和索菲娅阻止。"
            "以陈霜退出任务、赵海被永久隔离收尾。"
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

config = {
    "work_id": new_id, "volume_id": vol_id,
    "work_title": "深渊回响 v3.2 (参与类型约束版)",
    "genre": "科幻", "style": "克苏鲁+硬科幻",
    "world_setting": new_work["world_setting"],
    "foreshadowings": new_work["foreshadowings"],
    "characters": [
        {"name": c["name"], "age": {"林深":"35","陈霜":"32","Dr.索菲娅·米兰":"40","赵海":"28","深渊之眼":"?"}.get(c["name"],""),
         "identity": c["identity"],
         "appearance": {"林深":"中等身材，深邃的眼神","陈霜":"身材精悍，眼神锐利，军人气质",
           "Dr.索菲娅·米兰":"金发盘起，戴细框眼镜","赵海":"年轻，面色苍白","深渊之眼":"发光符号形态"}.get(c["name"],""),
         "personality": {"林深":"理性、冷静、执着","陈霜":"警惕、果敢、寡言",
           "Dr.索菲娅·米兰":"谨慎、细致、善于调停","赵海":"敏感、好奇、精神脆弱"}.get(c["name"],"")}
        for c in characters_narrative
    ],
    "chapters": [
        {"chapter_num": 1, "title": "寂静深海",
         "theme": "首次下潜，接触深渊之眼",
         "key_events": ["下潜至8000米", "首次接触深渊之眼", "团队产生分歧", "赵海首次链接异常"]},
        {"chapter_num": 2, "title": "符号密语",
         "theme": "符号破译与赵海的精神恶化",
         "key_events": ["索菲娅破译符号发现警告", "赵海精神恶化被隔离", "陈霜要求切断链接遭反对",
                        "陈霜建立强制链接协议", "通过监控/录音回放体现赵海状态"]},
        {"chapter_num": 3, "title": "裂痕",
         "theme": "深渊之眼展露真面，团队彻底分裂",
         "key_events": ["不同队员看到不同幻象", "赵海成为传声筒", "陈霜试图摧毁装置",
                        "林深和索菲娅阻止", "陈霜退出任务"]}
    ]
}

with open(r'scripts\abyss_v32_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"[OK] 深渊回响 v3.2 (参与类型约束版)")
print(f"  work_id: {new_id}")
print(f"  volume_id: {vol_id}")
print(f"  角色弧线:")
for cname, arc in character_arcs.items():
    print(f"    {cname}: {' → '.join(f'第{k}章 {v}' for k,v in sorted(arc.items()))}")
print(f"  Ch2 参与类型:")
for n, t in chapter_participation[2].items():
    print(f"    {n}: {t}")
