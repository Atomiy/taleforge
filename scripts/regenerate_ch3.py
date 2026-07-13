"""
重新生成星际余晖第3章（验证进度锚点修复效果）
- 删除旧第3章
- 基于第2章续写生成新第3章
- 保存结果
"""
import requests, json, sys

BASE = 'http://127.0.0.1:8080'
WORK_ID = 'db22accc'

# 1. 获取作品和章节信息
r = requests.get(f'{BASE}/api/v1/works/{WORK_ID}')
work = r.json().get('work', {})
volumes = work.get('volumes', [])
volume_id = volumes[0]['id'] if volumes else ''
chapter_ids = work.get('chapter_ids', [])
print(f'作品: {work.get("title")}')
print(f'当前章节IDs: {chapter_ids}')

# 找到第3章 (旧) 和第2章
old_ch3_id = None
ch2_id = None
for i, cid in enumerate(chapter_ids):
    r = requests.get(f'{BASE}/api/v1/history/{cid}')
    if r.ok:
        ch = r.json()
        ch_num = ch.get('series_order', 0)
        if ch_num == 2:
            ch2_id = cid
            print(f'第2章: {ch.get("title")} (id={cid})')
        elif ch_num == 3:
            old_ch3_id = cid
            print(f'旧第3章: {ch.get("title")} (id={cid})')

if not ch2_id:
    print('第2章未找到!')
    sys.exit(1)

# 2. 删除旧第3章
if old_ch3_id:
    print(f'\n删除旧第3章: {old_ch3_id}')
    r = requests.delete(f'{BASE}/api/v1/works/{WORK_ID}/chapters/{old_ch3_id}')
    if r.ok:
        print('已从作品移除')
    # 从history删除
    r = requests.delete(f'{BASE}/api/v1/history/{old_ch3_id}')
    print(f'从history删除: {r.status_code}')
else:
    print('无旧第3章需删除')

# 3. 生成新第3章
print('\n' + '='*60)
print('生成新第3章 (带进度锚点约束)')
print('='*60)

payload = {
    "theme": "星际余晖：最后的地球舰队",
    "genre": "科幻",
    "style": "硬科幻",
    "length": 2500,
    "background": "公元3157年，太阳即将膨胀为红巨星，人类建造了十艘世代飞船驶向比邻星。然而在航行途中，舰队发现了一个神秘的中微子信号源...",
    "perspective": "第三人称全知",
    "mood": "悬疑壮丽",
    "conflict": "人与人/人与未知",
    "characters": [],
    "foreshadowing": [
        "中微子信号中隐藏着一段古老的警告信息",
        "舰队首席科学家发现信号源的位置与古籍中记载的'宇宙灯塔'高度吻合",
        "主战派舰长私下截获了一段未解密的信息片段"
    ],
    "template_id": None,
    "continuation_mode": "next_chapter",
    "previous_story_id": ch2_id,
    "work_id": WORK_ID,
    "chapter_number": 3,
    "volume_id": volume_id
}

collected = []
r = requests.post(f'{BASE}/api/v1/story/generate', json=payload, stream=True, timeout=300)
if r.status_code != 200:
    print(f'请求失败: {r.status_code}')
    print(r.text[:500])
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
            elif parsed.get('agent') == 'writer' and parsed.get('status') == 'writing':
                data = parsed.get('data', '')
                if data:
                    collected.append(data)
                    print('.', end='', flush=True)
            elif 'status' in parsed and parsed.get('agent'):
                icon = {'running': '>', 'writing': 'W', 'complete': 'OK', 'error': 'XX'}.get(parsed['status'], '?')
                msg = parsed.get('message', '')
                if msg:
                    print(f'\n[{icon} {parsed["agent"]}] {msg}')
        except json.JSONDecodeError:
            pass

full_text = ''.join(collected)
print(f'\n生成完成！{len(full_text)} 字')
first_line = full_text.strip().split('\n')[0] if full_text else '(空)'
print(f'首行: {first_line[:120]}')

# 4. 保存新第3章
if full_text:
    title = first_line.replace('## ', '').replace('# ', '').strip()
    
    save_payload = {
        "title": title,
        "content": full_text,
        "theme": "星际余晖：最后的地球舰队",
        "genre": "科幻",
        "style": "硬科幻",
        "series_id": WORK_ID,
        "series_order": 3,
        "world_setting": "公元3157年，太阳即将膨胀为红巨星...",
        "previous_story_id": ch2_id,
    }
    r = requests.post(f'{BASE}/api/v1/story/save', json=save_payload)
    if r.status_code == 200:
        new_ch3_id = r.json().get('story_id')
        print(f'新第3章已保存: {new_ch3_id}')
        
        # 添加到作品
        r = requests.post(f'{BASE}/api/v1/works/{WORK_ID}/chapters', json={
            "story_id": new_ch3_id, "volume_id": volume_id
        })
        if r.ok:
            print('新第3章已添加到作品')
    else:
        print(f'保存失败: {r.status_code}')

    # 保存到本地
    with open('scripts/星际余晖_第3章_v2.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    print(f'已保存到 scripts/星际余晖_第3章_v2.txt')

# 5. 验证：对比新旧第3章的首句
print('\n' + '='*60)
print('验证：进度锚点检查')
print('='*60)

# 获取第2章结尾
r = requests.get(f'{BASE}/api/v1/history/{ch2_id}')
if r.ok:
    ch2 = r.json()
    ch2_end = (ch2.get('content', '') or '')[-200:]
    print(f'\n第2章结尾200字:')
    print(f'  ...{ch2_end}')
    print(f'\n新第3章首行:')
    print(f'  {first_line}')
    
    # 检查标题是否重复
    ch2_title = ch2.get('title', '')
    if title == ch2_title:
        print(f'\n⚠️ 标题与第2章重复: "{title}"')
    else:
        print(f'\n✅ 标题未重复: "{title}" vs 第2章"{ch2_title}"')
    
    # 检查是否出现了时间回溯关键词
    import re
    backtrack_indicators = ['又回到', '还在', '仍然在', '再次回到']
    for indicator in backtrack_indicators:
        if indicator in full_text[:200]:
            print(f'⚠️ 前200字出现时间回溯关键词: "{indicator}"')
            break
    else:
        print(f'✅ 前200字无时间回溯迹象')

print('\n完成！')
