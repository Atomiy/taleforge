import requests
r = requests.get('http://127.0.0.1:8080/api/v1/history/?page=1&page_size=10')
data = r.json()
items = data.get('stories',[])
for s in items[:5]:
    print(f'id={s.get("id","?")} story_id={s.get("story_id","?")} title={s.get("title","?")[:40]} content_len={len(s.get("content","") or "")}')
