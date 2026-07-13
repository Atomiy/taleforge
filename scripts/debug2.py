import requests
BASE = 'http://127.0.0.1:8080'

# 获取作品
r = requests.get(f'{BASE}/api/v1/works/')
work = r.json()['works'][0]
print(f'作品: {work["title"]}')
print(f'chapter_ids: {work.get("chapter_ids",[])}')

# 获取每个章节
chapters = []
for cid in work.get('chapter_ids', []):
    url = f'{BASE}/api/v1/history/{cid}'
    print(f'\nGET {url}')
    cr = requests.get(url)
    print(f'status={cr.status_code}')
    if cr.ok:
        ch = cr.json()
        print(f'  id字段: {list(ch.keys())}')
        print(f'  title={ch.get("title","?")}')
        chapters.append(ch)
    else:
        print(f'  error={cr.text[:200]}')

print(f'\nchapters count: {len(chapters)}')
if chapters:
    chapters.sort(key=lambda c: c.get('chapter_number', 0) or 0)
    last = chapters[-1]
    print(f'last: ch{last.get("chapter_number")} {last.get("title","?")} ({len(last.get("content","") or "")}字)')
