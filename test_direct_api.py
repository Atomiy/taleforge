#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接测试 DeepSeek API 续写能力（绕过服务端代码）"""
import os, json, requests, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

API_KEY = "sk-5307150833c94e6995fc8996daa557b4"
BASE = "https://api.deepseek.com/v1"

# 模拟续写 prompt
system_prompt = "你是专业奇幻作家。你的任务是直接创作故事正文，不要输出任何说明或解释。如果你是续写，直接展开新一章的剧情，不要复述上一章的内容。"

user_prompt = """你是一位专业的 奇幻 作家，擅长 史诗 风格。创作一个关于"森林守护者：黑暗降临"的故事。

## 创作要求
- 叙事视角：第三人称有限
- 情感基调：紧张刺激

## 前情提要（故事背景参考）
- 上一章的标题：森林守护者
- 上一章的结尾内容（衔接用）：
阿木咬破手指，一滴鲜血落在祭坛上。大地开始震颤，绿色的光芒从祭坛中涌出，包裹住他的身体。他感到一股强大的力量在血脉中奔涌——森林之灵选中了他。

## 本章创作要求
- 创作类型：全新的下一章内容（不要复述或改写上一章，直接展开新剧情）
- 保持与上一章一致的风格、人物设定和世界观
- 与上一章情节自然衔接，延续剧情走向
- 适当回收上章伏笔，同时设置新的伏笔

## 故事大纲
{"title": "森林守护者：黑暗降临", "phases": [{"name": "回归", "description": "阿木获得力量后回到村庄..."}]}

## 角色设定
[]

## 创作规范
1. 严格遵循大纲中的阶段划分和占比
2. 保持角色言行与设定一致
3. 使用中文写作，语言生动细腻
4. 对话自然，符合角色身份
5. 避免说教，通过情节传达主题
6. 目标字数：500 字
7. 如果是续写，确保情节连贯，适当回收前作伏笔并设置新伏笔

## 输出规则（必须遵守）
- 直接输出故事正文，不要加任何开场白、解释或说明
- 不要对话、不要道歉、不要询问用户
- 开头直接写故事第一句话"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
]

print(f"Prompt total length: {len(system_prompt) + len(user_prompt)} chars")
print(f"User prompt line 1: {user_prompt.split(chr(10))[0]}")
print()

r = requests.post(
    f"{BASE}/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    json={"model": "deepseek-chat", "messages": messages, "temperature": 0.7, "max_tokens": 4096, "stream": True},
    stream=True, timeout=120
)

print(f"HTTP: {r.status_code}")
if r.status_code != 200:
    print(f"Error: {r.text[:500]}")
    exit()

content = ""
for line in r.iter_lines():
    if not line: continue
    t = line.decode("utf-8")
    if t.startswith("data: "):
        d = t[6:]
        if d == "[DONE]": break
        try:
            data = json.loads(d)
            c = data["choices"][0]["delta"].get("content", "")
            if c: content += c
        except: pass

print(f"Content: {len(content)} chars")
print(f"---\n{content[:300]}\n---")
print("PASS" if len(content) > 100 else "FAIL")
