#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试续写功能"""
import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://127.0.0.1:8080/api/v1"
requests.post(f"{BASE}/config/api-key", json={"api_key":"sk-your-deepseek-api-key"})

# 1. 先保存一篇故事
r = requests.post(f"{BASE}/story/save", json={
    "title": "森林守护者",
    "content": "# 第一章 森林的召唤\n\n古老的森林深处住着一位年轻的守护者阿木。他从小与动物为伴，拥有与自然沟通的能力。一天，一只受伤的银狼带来了一则警告——北方的黑暗正在蔓延。阿木决定踏上征途。\n\n他穿过密林，越过溪流，最终在月光下发现了一座被遗忘的祭坛。祭坛上刻着一行古老的文字：\"当森林之子的血滴落在祭坛上，守护者的力量将完全觉醒。\"\n\n阿木咬破手指，一滴鲜血落在祭坛上。大地开始震颤，绿色的光芒从祭坛中涌出，包裹住他的身体。他感到一股强大的力量在血脉中奔涌——森林之灵选中了他。",
    "theme": "森林守护者", "genre": "奇幻", "style": "史诗"
})
sid1 = r.json().get("story_id")
print(f"故事1 ID: {sid1}")

# 2. 尝试续写（核心测试）
print("\n=== 续写测试 ===")
r = requests.post(f"{BASE}/story/generate", json={
    "theme": "森林守护者：黑暗降临",
    "genre": "奇幻", "style": "史诗", "length": 500,
    "background": "阿木觉醒森林之力后，黑暗势力开始向森林边界逼近。",
    "perspective": "第三人称有限", "conflict": "人与社会", "mood": "紧张刺激",
    "outline": "阿木获得森林之力后回到村庄，却发现村民们视他为异类。与此同时，黑暗生物已经入侵了森林外围。阿木必须在族人的敌意和外敌入侵之间做出抉择。",
    "world_setting": "", "foreshadowings": [], "characters": [],
    "api_key": "", "previous_story_id": sid1, "continuation_mode": "next_chapter"
}, stream=True, timeout=120)

content = ""; title = ""; evts = 0
for line in r.iter_lines():
    if not line: continue
    t = line.decode("utf-8")
    if not t.startswith("data: "): continue
    evts += 1
    try:
        d = json.loads(t[6:])
        a, s = d.get("agent",""), d.get("status","")
        if a == "writer" and s == "writing" and d.get("data"):
            content += d["data"]
        if a == "orchestrator" and s == "complete":
            title = d["data"].get("title","")
    except: pass

status = "PASS" if len(content) > 100 else "FAIL"
print(f"事件: {evts}, 内容: {len(content)}字")
print(f"状态: {status}")
if content:
    print(f"前100字: {content[:100]}")
    import re
    m = re.search(r'第(\d+)章', content)
    if m:
        print(f"章节编号: 第{m.group(1)}章 {'OK' if m.group(1)=='2' else 'WARN: 应为第2章'}")
