"""
完整重新生成星际余晖第1-3章（v0.4.0 进度锚点约束）
- 删除旧作品
- 创建新作品
- 依次生成第1、2、3章
- 验证连贯性
"""
import requests, json, sys, time, re

BASE = 'http://127.0.0.1:8080'

# 作品设定
NEW_WORK = {
    "title": "星际余晖：最后的地球舰队",
    "world_setting": "公元3157年，太阳即将膨胀为红巨星，人类建造了十艘世代飞船驶向比邻星。然而在航行途中，舰队发现了一个神秘的中微子信号源——它来自一个远超人类科技的古老文明，正位于舰队航线的前方。舰队内部因此分裂为主战派与探索派。",
    "genre": "科幻",
    "style": "硬科幻",
    "outline": "地球舰队在星际航行中遭遇未知文明信号，内部矛盾激化，最终在危机中重新凝聚的故事。",
    "foreshadowings": [
        "中微子信号中隐藏着一段古老的警告信息",
        "舰队首席科学家发现信号源的位置与古籍中记载的'宇宙灯塔'高度吻合",
        "主战派舰长私下截获了一段未解密的信息片段"
    ]
}

WORK_ID = None
VOLUME_ID = None

def log(msg):
    print(msg)

# ======== 1. 清理旧作品 ========
log('\n===== 1. 删除旧作品 =====')
r = requests.get(f'{BASE}/api/v1/works/')
for w in r.json().get('works', []):
    if w['title'] == NEW_WORK['title']:
        old_id = w['id']
        log(f'找到旧作品: {old_id}')
        requests.delete(f'{BASE}/api/v1/works/{old_id}')
        log(f'已删除')

# 也删之前可能残留的第4章等
r = requests.get(f'{BASE}/api/v1/works/')
log(f'当前作品数: {len(r.json().get("works", []))}')

# ======== 2. 创建新作品 ========
log('\n===== 2. 创建新作品 =====')
r = requests.post(f'{BASE}/api/v1/works/', json=NEW_WORK)
WORK_ID = r.json().get('work_id')
log(f'新作品ID: {WORK_ID}')

r = requests.get(f'{BASE}/api/v1/works/{WORK_ID}')
work = r.json().get('work', {})
if not work.get('volumes'):
    # 创建默认卷
    r = requests.post(f'{BASE}/api/v1/works/{WORK_ID}/volumes', json={"title": "第一卷"})
    work = r.json().get('work', {})
    log('已创建默认卷')
VOLUME_ID = work.get('volumes', [{}])[0].get('id', '')
log(f'卷ID: {VOLUME_ID}')
log(f'作品: {work.get("title")} ({work.get("genre")}/{work.get("style")})')

# ======== 生成函数 ========
def gen_chapter(ch_num, prev_story_id=None):
    """生成指定章节"""
    mode_str = '首次生成' if ch_num == 1 else f'续写(prev={prev_story_id[:8]})'
    log(f'\n{"="*60}')
    log(f'生成第{ch_num}章 [{mode_str}]')
    log(f'{"="*60}')

    payload = {
        "theme": NEW_WORK["title"],
        "genre": NEW_WORK["genre"],
        "style": NEW_WORK["style"],
        "length": 2500,
        "background": NEW_WORK["world_setting"],
        "perspective": "第三人称全知",
        "mood": "悬疑壮丽",
        "conflict": "人与人/人与未知",
        "characters": [],
        "foreshadowing": NEW_WORK["foreshadowings"],
        "template_id": None,
        "continuation_mode": "next_chapter" if prev_story_id else "",
        "previous_story_id": prev_story_id or "",
        "work_id": WORK_ID,
        "chapter_number": ch_num,
        "volume_id": VOLUME_ID
    }

    collected = []
    r = requests.post(f'{BASE}/api/v1/story/generate', json=payload, stream=True, timeout=300)
    if r.status_code != 200:
        log(f'请求失败: {r.status_code}')
        log(r.text[:500])
        return None

    for line in r.iter_lines(decode_unicode=True):
        if not line: continue
        if line.startswith('data: '):
            raw = line[6:]
            if raw == '[DONE]': break
            try:
                parsed = json.loads(raw)
                if 'text' in parsed:
                    collected.append(parsed['text'])
                elif parsed.get('agent') == 'writer' and parsed.get('status') == 'writing':
                    d = parsed.get('data', '')
                    if d: collected.append(d)
                elif parsed.get('status') and parsed.get('agent'):
                    icon = {'running': '>', 'writing': 'W', 'complete': 'OK', 'error': 'XX'}.get(parsed['status'], '?')
                    msg = parsed.get('message', '')
                    if msg: log(f'[{icon} {parsed["agent"]}] {msg}')
            except json.JSONDecodeError:
                pass

    text = ''.join(collected)
    first_line = text.strip().split('\n')[0] if text else '(空)'
    log(f'生成完成！{len(text)} 字')
    log(f'首行: {first_line[:120]}')
    return text


def save_chapter(ch_num, text, prev_id=None):
    """保存章节到后端和本地"""
    first_line = text.strip().split('\n')[0] if text else f'第{ch_num}章'
    title = first_line.replace('## ', '').replace('# ', '').strip()

    save = {
        "title": title,
        "content": text,
        "theme": NEW_WORK["title"],
        "genre": NEW_WORK["genre"],
        "style": NEW_WORK["style"],
        "series_id": WORK_ID,
        "series_order": ch_num,
        "world_setting": NEW_WORK["world_setting"],
        "previous_story_id": prev_id or "",
    }
    r = requests.post(f'{BASE}/api/v1/story/save', json=save)
    if r.status_code != 200:
        log(f'保存失败: {r.status_code} {r.text[:200]}')
        return None
    
    sid = r.json().get('story_id')
    requests.post(f'{BASE}/api/v1/works/{WORK_ID}/chapters', json={
        "story_id": sid, "volume_id": VOLUME_ID
    })
    log(f'已保存: story_id={sid}')

    path = f'scripts/星际余晖_第{ch_num}章_final.txt'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    log(f'已写入: {path}')
    return sid


# ======== 3. 生成第1章 ========
log('\n\n===== 3. 生成第1章 =====')
ch1 = gen_chapter(1)
if not ch1: sys.exit(1)
s1 = save_chapter(1, ch1)
if not s1: sys.exit(1)

# ======== 4. 生成第2章 ========
log('\n\n===== 4. 生成第2章 =====')
ch2 = gen_chapter(2, s1)
if not ch2: sys.exit(1)
s2 = save_chapter(2, ch2, s1)
if not s2: sys.exit(1)

# ======== 5. 生成第3章 ========
log('\n\n===== 5. 生成第3章 =====')
ch3 = gen_chapter(3, s2)
if not ch3: sys.exit(1)
s3 = save_chapter(3, ch3, s2)

# ======== 6. 验证连贯性 ========
log('\n\n' + '='*60)
log('连贯性验证')
log('='*60)

chapters_data = []
for sid, num in [(s1, 1), (s2, 2), (s3, 3)]:
    r = requests.get(f'{BASE}/api/v1/history/{sid}')
    if r.ok:
        ch = r.json()
        chapters_data.append(ch)
        content = ch.get('content', '') or ''
        log(f'第{num}章: {ch.get("title")} ({len(content)}字)')
        log(f'  首句: {content[:80]}...')
        log(f'  尾句: ...{content[-80:]}')

# 检查标题是否重复
titles = [c.get('title', '') for c in chapters_data]
if len(titles) != len(set(titles)):
    log(f'\n❌ 标题重复: {titles}')
else:
    log(f'\n✅ 三章标题均不重复: {titles}')

# 检查第2章首句是否接续第1章尾句
if len(chapters_data) >= 2:
    for i in range(1, len(chapters_data)):
        prev_end = (chapters_data[i-1].get('content', '') or '')[-100:]
        curr_start = (chapters_data[i].get('content', '') or '')[:100]
        log(f'\n第{i}章结尾 → 第{i+1}章开头:')
        log(f'  [尾] ...{prev_end.strip()}')
        log(f'  [首] {curr_start.strip()}')

# 打印总字数
total = sum(len((c.get('content','') or '')) for c in chapters_data)
log(f'\n{"="*60}')
log(f'三部曲完成！总计 {total} 字')
log(f'{"="*60}')
