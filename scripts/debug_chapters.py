"""测试续写连贯性 - 详细版"""
import requests, json, sys

BASE = 'http://127.0.0.1:8080'

# 1. 获取作品信息
r = requests.get(f'{BASE}/api/v1/works/')
print(f'作品API: {r.status_code}')
data = r.json()
works = data.get('works', [])
if not works:
    print('无作品，创建测试作品')
    sys.exit(1)

work = works[0]
print(f'作品: {work["title"]}')
print(f'作品字段: {list(work.keys())}')
print(f'volumes: {work.get("volumes", [])}')

# 2. 获取章节 - 用不同的API
# 尝试直接从作品的 chapter_ids 获取
ch_ids = work.get('chapter_ids', [])
print(f'\nchapter_ids: {ch_ids}')

if not ch_ids:
    # 从 volumes 中获取
    for v in work.get('volumes', []):
        ch_ids.extend(v.get('chapter_ids', []))
    print(f'从volumes获取: {ch_ids}')

# 3. 获取每个章节
chapters = []
for cid in ch_ids:
    url = f'{BASE}/api/v1/works/{work["id"]}/chapters/{cid}'
    print(f'\n请求: GET {url}')
    cr = requests.get(url)
    print(f'状态: {cr.status_code}')
    if cr.ok:
        chap = cr.json()
        print(f'章节: {chap.get("chapter_number")} - {chap.get("title")} ({len(chap.get("content",""))}字)')
        chapters.append(chap)
    else:
        print(f'响应: {cr.text[:200]}')

if not chapters:
    print('\n没有可续写的章节！')
    sys.exit(1)

chapters.sort(key=lambda c: c.get('chapter_number', 0))
last_ch = chapters[-1]
print(f'\n上一章: 第{last_ch["chapter_number"]}章「{last_ch.get("title")}」')
content = last_ch.get('content', '') or ''
print(f'字数: {len(content)}')
print(f'结尾200字: ...{content[-200:]}')
