"""检查 stories.json 中深渊回响相关章节。"""
import json

with open(r'backend\data\stories.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total stories: {len(data)}")

# 找深渊回响相关的
for s in reversed(data):
    title = s.get('title', '?')
    theme = s.get('theme', '?')
    content = s.get('content', '') or ''
    sid = s.get('id', '?')
    if '深渊' in title or '深渊' in theme:
        print(f"\n  [{sid}] {title}")
        print(f"    theme={theme}")
        print(f"    content_len={len(content)}")
        print(f"    genre={s.get('genre','')}, style={s.get('style','')}")
        print(f"    world_setting={s.get('world_setting','')[:50]}...")
        print(f"    foreshadowings={s.get('foreshadowings',[])}")
        print(f"    series_id={s.get('series_id','')}, series_order={s.get('series_order','')}")
        if content:
            print(f"    preview={content[:80]}...")
