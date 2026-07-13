"""
深渊回响 v3.1 - Planner + Character + Writer 全链路约束版本
叙事调整：陈霜(前海军少校)承担安保职能，索菲娅承担科学家职能
"""
import json
import uuid
from datetime import datetime

WORKS_FILE = r'backend\data\works.json'

with open(WORKS_FILE, 'r', encoding='utf-8') as f:
    works = json.load(f)

now = datetime.now().isoformat()
new_id = uuid.uuid4().hex[:8]
vol_id = f"v{uuid.uuid4().hex[:8]}"

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
    },
    {
        "chapter_num": 3,
        "title": "裂痕",
        "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]
    }
]

# 角色描述强化：陈霜承担安保判断职能，索菲娅承担科学分析职能
characters_narrative = [
    {
        "name": "林深",
        "identity": "深海地质学家，深渊计划首席科学家",
        "brief": "理性派，坚信科学能解释一切，但深渊之眼的存在动摇了他的世界观"
    },
    {
        "name": "陈霜",
        "identity": "前海军少校，深海潜航员兼任务安保负责人",
        "brief": "技术顶尖，极度警惕，既负责潜航操作也负责团队安全决策，军事背景让她天然怀疑未知事物"
    },
    {
        "name": "Dr.索菲娅·米兰",
        "identity": "符号学家兼生物学家，跨学科研究员",
        "brief": "语言学家兼生物学家，兼具符号破译和生物样本分析能力，团队中的理性调解者"
    },
    {
        "name": "赵海",
        "identity": "通讯工程师，精神链接装置操作员",
        "brief": "最敏感，最先与深渊之眼建立深度链接，精神受到侵蚀"
    },
    {
        "name": "深渊之眼",
        "identity": "马里亚纳海沟深处的未知意识体",
        "brief": "古老意识，对不同人展现不同面貌，动机不明"
    }
]

new_work = {
    "id": new_id,
    "title": "深渊回响 v3.1（全链路约束版）",
    "world_setting": (
        "2124年，人类首次与来自马里亚纳海沟深渊的未知意识体建立微弱的精神链接。"
        "该意识体自称「深渊之眼」，声称地球的板块运动并非自然现象，而是某种被封印的古老机制在苏醒。"
        "深海探测队发现海沟底部存在非自然的巨大结构体，表面覆盖着无法解析的符号。"
        "随着全球各地深海地震频发，各大国秘密组建「深渊计划」，派遣精英团队潜入深渊调查真相。"
    ),
    "foreshadowings": [
        "深渊意识并非善意",
        "板块运动与封印有关",
        "巨大结构体上的符号在缓慢变化",
        "赵海的精神被深渊之眼侵蚀，成为深渊传递信息的通道"
    ],
    "outline": "",
    "summary": "",
    "chapter_ids": [],
    "volumes": [
        {
            "id": vol_id,
            "number": 1,
            "title": "第一卷：深渊之眼",
            "chapter_ids": [],
            "outline": (
                "第1章「寂静深海」：深渊计划组建完毕，林深(首席地质学家)、陈霜(前海军少校，负责潜航与安保)、"
                "索菲娅(符号学家兼生物学家)、赵海(通讯工程师)四人乘深海探测器下潜至马里亚纳海沟8000米深处。"
                "首次接触深渊意识体——深渊之眼。陈霜出于军事本能保持极度警惕，主张限制链接深度；"
                "林深则想深入探索。团队内部因对未知的态度分歧产生裂痕。赵海的精神率先受到轻微影响。"
                "\n\n"
                "第2章「符号密语」：索菲娅发现结构体上的符号与古苏美尔文字存在部分对应关系，"
                "翻译出一句警告——「不要让它完整地听见你」。赵海因精神侵蚀加重被隔离在医疗舱。"
                "陈霜主张切断链接，林深和索菲娅认为需要继续研究才能应对危机。"
                "陈霜以安保负责人的身份建立严格的链接协议。"
                "\n\n"
                "第3章「裂痕」：深渊之眼对不同队员展现出不同的「面孔」——"
                "林深看到古老的海洋文明历史，陈霜看到军事灾难的预言场景，"
                "索菲娅看到符号的完整含义，赵海则完全被深渊占据成为传声筒。"
                "团队分裂为「探索派」(林深、索菲娅)与「警惕派」(陈霜)。"
                "陈霜以任务安全为由试图摧毁精神链接装置，"
                "林深和索菲娅阻止了她。赵海的状态成为双方争论的焦点。"
            ),
            "responsibility": (
                "引出核心悬念（深渊意识体与板块封印），"
                "建立人物关系和团队内部冲突（探索vs警惕），"
                "赵海精神侵蚀作为贯穿线索，为第二卷揭示深渊真相做铺垫"
            ),
            "connection_to_prev": "第一卷，无前卷",
            "connection_to_next": (
                "陈霜与林深的冲突成为第二卷的核心驱动力，"
                "赵海的完全深渊化是第二卷的开端"
            ),
            "characters": characters_narrative,
            "foreshadowings": [
                "深渊之眼对不同人展现不同面孔",
                "结构体符号包含警告信息",
                "赵海精神异常是深渊侵蚀的前兆",
                "陈霜的军事判断与林深的科学探索之间的矛盾"
            ],
            "chapter_characters": chapter_characters
        }
    ],
    "created_at": now,
    "updated_at": now,
    "genre": "科幻",
    "style": "克苏鲁+硬科幻"
}

works.insert(0, new_work)
with open(WORKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(works, f, ensure_ascii=False, indent=2)

config = {
    "work_id": new_id,
    "volume_id": vol_id,
    "work_title": "深渊回响 v3.1 (全链路约束版)",
    "genre": "科幻",
    "style": "克苏鲁+硬科幻",
    "world_setting": new_work["world_setting"],
    "foreshadowings": new_work["foreshadowings"],
    "characters": [
        {"name": c["name"], "age": {"林深":"35","陈霜":"32","Dr.索菲娅·米兰":"40","赵海":"28"}.get(c["name"],""),
         "identity": c["identity"], "appearance": {"林深":"中等身材，深邃的眼神透着学者的敏锐",
           "陈霜":"身材精悍，眼神锐利如鹰，军人气质",
           "Dr.索菲娅·米兰":"金发盘起，戴着细框眼镜，气质沉稳",
           "赵海":"年轻，面色略显苍白，神情恍惚",
           "深渊之眼":"无固定形态，以发光符号和心灵感应展现"}.get(c["name"],""),
         "personality": {"林深":"理性、冷静、执着",
           "陈霜":"警惕、果敢、寡言，以任务安全为第一原则",
           "Dr.索菲娅·米兰":"谨慎、细致、善于调停，科学至上",
           "赵海":"敏感、好奇、精神脆弱"}.get(c["name"],"")}
        for c in characters_narrative
    ],
    "chapters": [
        {
            "chapter_num": 1, "title": "寂静深海",
            "theme": "深渊计划首次下潜，接触深渊之眼",
            "key_events": [
                "四人乘探测器下潜至8000米",
                "首次接触深渊之眼（以发光符号形式）",
                "陈霜要求限制链接深度，林深主张深入探索",
                "赵海首次尝试链接即感到强烈刺痛",
                "团队以陈霜的安保协议妥协收场"
            ]
        },
        {
            "chapter_num": 2, "title": "符号密语",
            "theme": "符号破译与团队裂痕加深",
            "key_events": [
                "索菲娅破译符号，发现警告信息",
                "赵海精神恶化被隔离在医疗舱",
                "陈霜要求切断链接，林深和索菲娅反对",
                "陈霜以安保负责人身份建立强制链接协议",
                "以「继续研究但严格管控」的折中方案收尾"
            ]
        },
        {
            "chapter_num": 3, "title": "裂痕",
            "theme": "深渊之眼展露真面，团队分裂",
            "key_events": [
                "深渊之眼对四人展现不同面孔",
                "林深看到远古海洋文明历史",
                "陈霜看到军事灾难预言，更坚定切断决心",
                "索菲娅看到符号完整序列，理解封印本质",
                "赵海完全被深渊占据成为传声筒",
                "陈霜试图摧毁装置，林深和索菲娅阻止",
                "以陈霜退出任务、赵海被隔离收尾"
            ]
        }
    ]
}

with open(r'scripts\abyss_v31_config.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print(f"[OK] 已创建: 深渊回响 v3.1 (全链路约束版)")
print(f"  work_id: {new_id}")
print(f"  volume_id: {vol_id}")
print(f"  角色（5人，陈霜兼安保、索菲娅兼科学家）:")
for c in characters_narrative:
    print(f"    {c['name']} - {c['identity']}")
print(f"  出场表:")
for cc in chapter_characters:
    print(f"    第{cc['chapter_num']}章《{cc['title']}》: {'、'.join(cc['characters'])}")
