"""检查当前作品和章节状态"""
import requests, json

BASE = 'http://127.0.0.1:8080'

# 1. 查作品
r = requests.get(f'{BASE}/api/v1/works/')
works = r.json().get('works', [])
print(f'共 {len(works)} 个作品:\n')
for w in works:
    print(f'  【{w["title"]}】')
    vols = w.get('volumes', [])
    for v in vols:
        print(f'    卷: {v.get("title","?")} — {len(v.get("chapter_ids",[]))} 章')
        for cid in v.get('chapter_ids', []):
            cr = requests.get(f'{BASE}/api/v1/works/{w["id"]}/chapters/{cid}')
            if cr.ok:
                c = cr.json()
                print(f'      ├─ 第{c.get("chapter_number","?")}章: {c.get("title","?")} ({len(c.get("content",""))}字)')
    print()

# 2. 查历史
r = requests.get(f'{BASE}/api/v1/history/?page=1&page_size=5')
h = r.json()
print(f'历史记录: 共{h.get("total",0)}条')
for s in h.get('stories', [])[:3]:
    print(f'  - {s.get("title","?")} ({len(s.get("content",""))}字)')
