"""
测试续写连贯性 - 生成第4章
- 使用 history API 获取上一章内容
- 用 generate-stream 续写
- 保存结果供对比
"""
import requests, json, sys

BASE = 'http://127.0.0.1:8080'

# 1. 获取作品
r = requests.get(f'{BASE}/api/v1/works/')
works = r.json().get('works', [])
work = works[0]
print(f'作品: {work["title"]}')

# 2. 从 history API 获取章节内容
chapters = []
for cid in work.get('chapter_ids', []):
    cr = requests.get(f'{BASE}/api/v1/history/{cid}')
    if cr.ok:
        ch = cr.json()
        chapters.append(ch)
        print(f'  第{ch.get("chapter_number","?")}章: {ch.get("title","?")} ({len(ch.get("content","") or "")}字)')

chapters.sort(key=lambda c: (c.get('chapter_number') or c.get('series_order', 0) or 0))
last_ch = chapters[-1]
content = last_ch.get('content', '') or ''
ch_num = last_ch.get('chapter_number') or last_ch.get('series_order', len(chapters))
print(f'\n续写起点: 第{ch_num}章「{last_ch.get("title")}」')
print(f'结尾300字: ...{content[-300:]}\n')

# 3. 构建续写请求
payload = {
    "theme": work.get("title", "苍狼传说"),
    "genre": work.get("genre", "奇幻"),
    "style": work.get("style", "史诗"),
    "length": 2000,
    "background": work.get("world_setting", ""),
    "perspective": "第三人称全知",
    "mood": "热血激昂",
    "conflict": "人与自然",
    "characters": [],
    "foreshadowing": [],
    "template_id": None,
    "continuation_mode": "next_chapter",
    "previous_story_id": last_ch.get("id") or last_ch.get("story_id", ""),
    "work_id": work["id"],
    "chapter_number": (last_ch.get('chapter_number') or last_ch.get('series_order') or len(chapters)) + 1,
    "volume_id": work["volumes"][0]["id"]
}
print(f'续写参数: chapter_number={payload["chapter_number"]}, previous_story_id={payload["previous_story_id"]}')

# 4. 调用流式生成
print('\n生成中...\n' + '-'*60)
collected = []
r = requests.post(
    f'{BASE}/api/v1/story/generate',
    json=payload,
    stream=True,
    timeout=300
)
if r.status_code != 200:
    print(f'请求失败: {r.status_code}')
    print(r.text[:1000])
    sys.exit(1)

for line in r.iter_lines(decode_unicode=True):
    if not line:
        continue
    if line.startswith('data: '):
        raw = line[6:]
        if raw == '[DONE]':
            break
        try:
            parsed = json.loads(raw)
            if 'text' in parsed:
                collected.append(parsed['text'])
                print(parsed['text'], end='', flush=True)
            elif 'status' in parsed and parsed.get('agent'):
                # 打印 agent 状态
                icon = {'running': '>', 'writing': 'W', 'complete': 'OK', 'error': 'XX'}.get(parsed['status'], '?')
                if parsed['status'] == 'writing':
                    # writer 流式输出data
                    data = parsed.get('data', '')
                    if data:
                        collected.append(data)
                        print(data, end='', flush=True)
                else:
                    print(f'\n[{icon} {parsed["agent"]}] {parsed.get("message","")}')
        except json.JSONDecodeError:
            pass

full_text = ''.join(collected)
print('\n' + '-'*60)
print(f'\n生成完成！{len(full_text)} 字')

# 5. 提取标题
first_line = full_text.strip().split('\n')[0] if full_text else '(空)'
print(f'首行: {first_line[:80]}')

# 6. 保存
output_path = 'scripts/第4章_续写结果_v0.3.2.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_text)
print(f'\n已保存: {output_path}')
