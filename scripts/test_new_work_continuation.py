"""
为「星际余晖：最后的地球舰队」生成第2章和第3章
- 第1章已有 (story_id=eb8f380f)
- 第2章：续写第1章
- 第3章：续写第2章
- 保存所有结果供对比
"""
import requests, json, sys

BASE = 'http://127.0.0.1:8080'
WORK_ID = 'db22accc'

# 获取作品信息，找到volume_id
r = requests.get(f'{BASE}/api/v1/works/{WORK_ID}')
work_data = r.json().get('work', {})
volumes = work_data.get('volumes', [])
volume_id = volumes[0]['id'] if volumes else ''
print(f'作品: {work_data.get("title")}')
print(f'卷ID: {volume_id}')

# 获取已有章节列表，确认chapter_id映射
chapters_list = work_data.get('chapter_ids', [])
print(f'已有章节IDs: {chapters_list}')

# 第1章 story_id
ch1_story_id = 'eb8f380f'

# 验证第1章存在
r = requests.get(f'{BASE}/api/v1/history/{ch1_story_id}')
if r.ok:
    ch1 = r.json()
    print(f'第1章: {ch1.get("title")} ({len(ch1.get("content","") or "")}字)')
else:
    print(f'第1章未找到: {ch1_story_id}')
    sys.exit(1)


def generate_chapter(prev_story_id, chapter_num):
    """生成指定章节（续写模式）"""
    print(f'\n{"="*60}')
    print(f'生成第{chapter_num}章 (previous_story_id={prev_story_id})')
    print(f'{"="*60}')

    payload = {
        "theme": "星际余晖：最后的地球舰队",
        "genre": "科幻",
        "style": "硬科幻",
        "length": 2500,
        "background": "公元3157年，太阳即将膨胀为红巨星，人类建造了十艘世代飞船驶向比邻星。然而在航行途中，舰队发现了一个神秘的中微子信号源——它来自一个远超人类科技的古老文明，正位于舰队航线的前方。舰队内部因此分裂为主战派与探索派。",
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
        "previous_story_id": prev_story_id,
        "work_id": WORK_ID,
        "chapter_number": chapter_num,
        "volume_id": volume_id
    }

    collected = []
    r = requests.post(
        f'{BASE}/api/v1/story/generate',
        json=payload,
        stream=True,
        timeout=300
    )
    if r.status_code != 200:
        print(f'请求失败: {r.status_code}')
        print(r.text[:500])
        return None

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
    print(f'首行: {first_line[:100]}')
    return full_text


# ========== 生成第2章 ==========
ch2_text = generate_chapter(ch1_story_id, 2)

if ch2_text:
    # 提取标题
    title_line = ch2_text.strip().split('\n')[0] if ch2_text else '第2章'
    ch2_title = title_line.replace('## ', '').replace('# ', '').strip()
    
    # 保存到 history
    save_payload = {
        "title": ch2_title,
        "content": ch2_text,
        "theme": "星际余晖：最后的地球舰队",
        "genre": "科幻",
        "style": "硬科幻",
        "series_id": WORK_ID,
        "series_order": 2,
        "world_setting": "公元3157年，太阳即将膨胀为红巨星...",
        "previous_story_id": ch1_story_id,
    }
    r = requests.post(f'{BASE}/api/v1/story/save', json=save_payload)
    if r.status_code == 200:
        ch2_story_id = r.json().get('story_id')
        print(f'第2章已保存: {ch2_story_id}')
        # 添加到作品
        requests.post(f'{BASE}/api/v1/works/{WORK_ID}/chapters', json={
            "story_id": ch2_story_id, "volume_id": volume_id
        })
        print(f'第2章已添加到作品')
    else:
        print(f'第2章保存失败: {r.status_code}')
        ch2_story_id = None

    # 保存到本地
    with open('scripts/星际余晖_第2章.txt', 'w', encoding='utf-8') as f:
        f.write(ch2_text)
    print(f'已保存到 scripts/星际余晖_第2章.txt')
else:
    ch2_story_id = None
    print('第2章生成失败！')


# ========== 生成第3章 ==========
if ch2_story_id:
    ch3_text = generate_chapter(ch2_story_id, 3)

    if ch3_text:
        title_line = ch3_text.strip().split('\n')[0] if ch3_text else '第3章'
        ch3_title = title_line.replace('## ', '').replace('# ', '').strip()

        save_payload = {
            "title": ch3_title,
            "content": ch3_text,
            "theme": "星际余晖：最后的地球舰队",
            "genre": "科幻",
            "style": "硬科幻",
            "series_id": WORK_ID,
            "series_order": 3,
            "world_setting": "公元3157年，太阳即将膨胀为红巨星...",
            "previous_story_id": ch2_story_id,
        }
        r = requests.post(f'{BASE}/api/v1/story/save', json=save_payload)
        if r.status_code == 200:
            ch3_story_id = r.json().get('story_id')
            print(f'第3章已保存: {ch3_story_id}')
            requests.post(f'{BASE}/api/v1/works/{WORK_ID}/chapters', json={
                "story_id": ch3_story_id, "volume_id": volume_id
            })
            print(f'第3章已添加到作品')

        with open('scripts/星际余晖_第3章.txt', 'w', encoding='utf-8') as f:
            f.write(ch3_text)
        print(f'已保存到 scripts/星际余晖_第3章.txt')


print('\n' + '='*60)
print('全部完成！生成的文件：')
print('  - scripts/星际余晖_第1章.txt')
print('  - scripts/星际余晖_第2章.txt')
print('  - scripts/星际余晖_第3章.txt')
print('')
print('对比：苍狼传说 第1-3章  vs  星际余晖 第1-3章')
print('='*60)
