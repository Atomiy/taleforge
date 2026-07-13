#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TaleForge 三部曲生成验证 - 含连贯性、章节编号、逻辑审查"""
import requests, json, sys, time, os

os.environ["PYTHONIOENCODING"] = "utf-8"
# 禁用 GBK 编码问题
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = "http://127.0.0.1:8080/api/v1"
KEY = "sk-your-deepseek-api-key"
REPORT = r"C:\Users\33173\Desktop\study\taleforge\guide file\三部曲验证报告.md"

def log(m): 
    with open(REPORT, "a", encoding="utf-8") as f: 
        f.write(m + "\n")
    print(m)

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("# 苍狼传说 - 三部曲生成验证报告\n\n")

# 配置 Key
requests.post(f"{BASE}/config/api-key", json={"api_key": KEY})

# 清理旧数据（如果有）
log("## 0. 准备工作")
r = requests.get(f"{BASE}/works/")
for w in r.json().get("works", []):
    requests.delete(f"{BASE}/works/{w['id']}")
    log(f"- 清理旧作品: {w['id']}")

WORLD = "北境大陆——终年被冰雪覆盖的蛮荒之地。狼神是这片土地的守护者，每个部落都有狼灵守护。霜狼部落世代守护着狼神祭坛。传说中狼神之子将在部落危难时觉醒。"
WORK_TITLE = "苍狼传说"

log(f"\n## 1. 创建作品「{WORK_TITLE}」")
r = requests.post(f"{BASE}/works/", json={
    "title": WORK_TITLE, "genre": "奇幻", "style": "史诗",
    "world_setting": WORLD,
    "outline": "第一章：霜狼之子的觉醒——废柴少年意外唤醒狼神之力。\n第二章：炎龙入侵——铁山率领部落抵御龙族铁骑。\n第三章：狼神的试炼——铁山面临最后的抉择：成为狼神还是守护人性。",
    "foreshadowings": ["狼神祭坛的共鸣", "狼神之力会侵蚀人性", "炎龙帝国的真实动机"]
})
WORK_ID = r.json().get("work_id")
log(f"- 作品ID: {WORK_ID} | HTTP {r.status_code}")
log("")

def gen_chapter(theme, outline, bg, prev_id, ch_label):
    log(f"### {ch_label}")
    log(f"- 主题: {theme}")
    payload = {
        "theme": theme, "genre": "奇幻", "style": "史诗", "length": 1000,
        "background": bg, "perspective": "第三人称有限",
        "conflict": "人与社会", "mood": "紧张刺激",
        "outline": outline, "world_setting": WORLD,
        "foreshadowings": [], "characters": [], "api_key": "",
        "previous_story_id": prev_id or "", "continuation_mode": "next_chapter"
    }
    r = requests.post(f"{BASE}/story/generate", json=payload, stream=True, timeout=300)
    if r.status_code != 200:
        log(f"- 错误: HTTP {r.status_code}")
        return None, None
    content, title = "", ""
    agent_events = 0
    writer_chunks = 0
    for line in r.iter_lines():
        if not line: continue
        t = line.decode("utf-8")
        if not t.startswith("data: "): continue
        try:
            d = json.loads(t[6:])
            agent_events += 1
            a, s = d.get("agent",""), d.get("status","")
            if a == "writer" and s == "writing" and d.get("data"):
                content += d["data"]
                writer_chunks += 1
            if a == "orchestrator" and s == "complete":
                title = d["data"].get("title","")
                content = d["data"].get("content",content)
        except: pass
    log(f"- 智能体事件: {agent_events} | Writer数据块: {writer_chunks}")
    log(f"- 标题: {title or '(未命名)'}")
    log(f"- 字数: {len(content)}")
    if len(content) < 100:
        log(f"- 警告: 内容过短! 前50字: {content[:50]}")
    return title, content

def save_chapter(t, c, prev_id):
    d = {"title":t,"content":c,"theme":WORK_TITLE,"genre":"奇幻","style":"史诗",
         "world_setting":WORLD,"foreshadowings":[],"previous_story_id":prev_id or ""}
    r = requests.post(f"{BASE}/story/save", json=d)
    sid = r.json().get("story_id","?")
    log(f"- 保存故事: ID={sid}")
    r2 = requests.post(f"{BASE}/works/{WORK_ID}/chapters", json={"story_id": sid})
    log(f"- 关联作品: HTTP {r2.status_code}")
    return sid

def extract_chapter_num(content):
    """从内容中提取章节编号（支持中文数字和阿拉伯数字）"""
    import re
    CN_NUMS = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,"十":10}
    # 先尝试匹配阿拉伯数字: # 第2章 或 ## 第2章
    m = re.search(r'#{1,4}\s*第(\d+)章', content or "")
    if m:
        return int(m.group(1))
    # 再尝试匹配中文数字: # 第一章 或 ## 第六章
    m = re.search(r'#{1,4}\s*第([一二三四五六七八九十]+)章', content or "")
    if m:
        return CN_NUMS.get(m.group(1), None)
    # 最后尝试匹配星号变体: **第2章**
    m = re.search(r'\*{0,2}#{0,4}\*{0,2}\s*第(\d+)章', content or "")
    if m:
        return int(m.group(1))
    return None

# 第1章
log("\n## 2. 第1章：霜狼之子的觉醒\n")
t1, c1 = gen_chapter(
    "苍狼传说：霜狼之子的觉醒",
    "铁山是霜狼部落最弱的少年，在成人礼上无法召唤狼灵，受尽嘲讽。深夜他独自前往狼神祭坛祈求力量，意外引发千年未见的异象——所有狼灵虚影同时向他臣服。大祭司震惊地称他为'狼神之子'，但警告这股力量可能带来灾难。与此同时，北境深处的血红色眼睛正在苏醒。",
    "霜狼部落的少年铁山在成人礼上触发了狼神祭坛的共鸣，古老的狼灵在他体内苏醒。",
    None, "第1章"
)
if c1 and len(c1) > 100:
    ch1 = extract_chapter_num(c1)
    log(f"- 章节编号检查: 第{ch1}章 {'OK' if ch1 == 1 else f'WARN:应为第1章'}")
    s1 = save_chapter(t1, c1, None)
else:
    log("FAIL: 第1章生成失败"); sys.exit(1)
time.sleep(3)

# 第2章（续写）
log("\n## 3. 第2章：炎龙入侵（续写）\n")
t2, c2 = gen_chapter(
    "苍狼传说：炎龙入侵",
    "炎龙帝国的先锋部队抵达霜狼部落，要求交出'狼神之子'。铁山为了保护族人站出来，独自迎战炎龙将领。战斗中他体内的狼神之力首次完全爆发——化身为巨大的霜狼撕碎敌军，但他发现自己正在逐渐失去人性。与此同时，部落中的叛徒正在暗中破坏防线。",
    "炎龙帝国铁骑越过边境，霜狼部落面临灭顶之灾。铁山必须带领族人抵御入侵，但他体内的狼神之力还在失控。",
    s1, "第2章（续写）"
)
if c2 and len(c2) > 100:
    ch2 = extract_chapter_num(c2)
    log(f"- 章节编号检查: 第{ch2}章 {'OK' if ch2 == 2 else f'WARN:应为第2章'}")
    s2 = save_chapter(t2, c2, s1)
else:
    log("FAIL: 第2章续写失败")
    s2 = None
time.sleep(3)

# 第3章（续写 - 如果第2章成功，从第2章续写）
log("\n## 4. 第3章：狼神的试炼（续写）\n")
prev = s2 or s1
t3, c3 = gen_chapter(
    "苍狼传说：狼神的试炼",
    "铁山最终来到狼神祭坛前，面对龙王的终极决战。狼神的灵魂出现，揭示了一个残酷的真相——要完全掌控狼神之力，就必须献祭自己的人类身份。铁山必须在力量与人性之间做出终极抉择，而龙王的铁骑已经踏破了最后的防线。",
    "铁山面临最终的抉择——完全接受狼神之力成为新的狼神，但代价是永远失去人类身份；或者放弃力量，让部落被炎龙帝国吞并。",
    prev, "第3章（续写）"
)
if c3 and len(c3) > 100:
    ch3 = extract_chapter_num(c3)
    log(f"- 章节编号检查: 第{ch3}章 {'OK' if ch3 == 3 else f'WARN:应为第3章'}")
    s3 = save_chapter(t3, c3, prev)
else:
    log("FAIL: 第3章续写失败")
    s3 = None

# ========== 验证 ==========
log("\n## 5. 章节编号验证\n")
chapters = []
r = requests.get(f"{BASE}/works/{WORK_ID}")
if r.status_code == 200:
    chapters = r.json().get("chapters", [])
    for i, ch in enumerate(chapters):
        cn = extract_chapter_num(ch.get("content",""))
        wc = ch.get("word_count",0)
        status = "OK" if cn == i+1 else f"WARN:显示为第{cn}章"
        log(f"  第{i+1}章: {ch['title']} ({wc}字) 编号检查: {status}")

log("\n## 6. 完整故事内容\n")
for i, ch in enumerate(chapters):
    log(f"### 第{i+1}章: {ch['title']}")
    log(f"**字数**: {ch.get('word_count',0)}\n")
    log(ch.get("content","(空)"))
    log("")

# 逻辑审查
log("\n## 7. 剧情逻辑审查\n")
checks = [
    "第1章 铁山从被欺凌到觉醒狼神之力，有完整的\"弱者→觉醒\"弧线",
    "第2章 承接第1章，外部冲突（炎龙帝国入侵）+ 内部冲突（狼神之力失控）",
    "第3章 收束全局，铁山面临力量与人性的终极抉择",
    "角色一致性：铁山身份一致、大祭司身份一致、部落场景一致",
    "世界观一致性：北境雪原、狼神祭坛、炎龙帝国",
    "情节递进合理：觉醒→冲突→抉择 三幕式结构",
]
log("| 审查项 | 结果 |")
log("|--------|:----:|")
for c in checks:
    log(f"| {c} | ⚠️ 待确认 |")

log(f"\n## 8. 测试结论\n")
log(f"| 项目 | 状态 |")
log(f"|------|:----:| ")
log(f"| 第1章生成 ({len(c1) if c1 else 0}字) | {'PASS' if c1 and len(c1)>500 else 'FAIL'} |")
log(f"| 第2章续写 ({len(c2) if c2 else 0}字) | {'PASS' if c2 and len(c2)>500 else 'FAIL'} |")
log(f"| 第3章续写 ({len(c3) if c3 else 0}字) | {'PASS' if c3 and len(c3)>500 else 'FAIL'} |")
log(f"| 章节编号连续 | {'PASS' if all([extract_chapter_num(chapters[i].get('content',''))==i+1 for i in range(len(chapters))]) else 'WARN:见编号检查'} |")
log(f"| 作品关联完整 | {'PASS' if len(chapters)>=2 else 'FAIL'} |")
log(f"| 剧情逻辑 | 见第7节逐项审查 |")
log(f"\n报告时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
log("\n---\n*报告由 AI 自动生成*")
print(f"\n验证完成! 报告: {REPORT}")
