"""深渊回响 v3.1 - 全链路约束版生成脚本"""
import json, sys, time, requests

BASE_URL = "http://127.0.0.1:8080"
with open(r'scripts\abyss_v31_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

work_id, volume_id = config['work_id'], config['volume_id']

def generate_chapter(ch, prev_id=None):
    print(f"\n{'='*60}")
    print(f"  生成第{ch['chapter_num']}章: {ch['title']}")
    print(f"{'='*60}")
    payload = {
        "theme": ch['theme'], "genre": config['genre'], "style": config['style'],
        "length": 3000, "background": config['world_setting'],
        "perspective": "第三人称有限", "conflict": "人与超自然", "mood": "悬疑压抑",
        "outline": '\n'.join(ch['key_events']),
        "characters": config['characters'],
        "world_setting": config['world_setting'],
        "foreshadowings": config['foreshadowings'],
        "work_id": work_id, "volume_id": volume_id,
        "chapter_number": ch['chapter_num'], "continuation_mode": "next_chapter",
    }
    if prev_id: payload["previous_story_id"] = prev_id

    resp = requests.post(f"{BASE_URL}/api/v1/story/generate", json=payload, stream=True, timeout=300)
    full_content, story_title, story_id = "", "", None

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data: '): continue
        try: data = json.loads(line[6:])
        except json.JSONDecodeError: continue
        agent, status, msg = data.get('agent',''), data.get('status',''), data.get('message','')
        if status in ('running','done','error'):
            print(f"  [{agent}] {status}: {msg[:80]}")
        if agent == 'writer' and status == 'writing':
            full_content += data.get('data', '')
        if agent == 'orchestrator' and status == 'complete':
            story_title = data['data'].get('title', ch['title'])
            if data['data'].get('content'): full_content = data['data']['content']

    if not full_content:
        print(f"  [WARN] 内容为空"); return None,None,None

    print(f"  保存故事... ({len(full_content)}字)")
    save_resp = requests.post(f"{BASE_URL}/api/v1/story/save", json={
        "title": story_title or ch['title'], "content": full_content,
        "theme": ch['theme'], "genre": config['genre'], "style": config['style'],
        "world_setting": config['world_setting'], "foreshadowings": config['foreshadowings'],
        "series_id": work_id, "series_order": ch['chapter_num'],
    })
    saved = save_resp.json()
    saved_id = saved.get('id') or saved.get('story_id')
    print(f"  保存成功: id={saved_id}")

    if saved_id and work_id:
        requests.post(f"{BASE_URL}/api/v1/works/{work_id}/chapters", json={
            "story_id": saved_id, "volume_id": volume_id
        })

    out_path = f"scripts/abyss_v31_ch{ch['chapter_num']}.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"## 第{ch['chapter_num']}章 {story_title or ch['title']}\n\n{full_content}")
    print(f"  已备份: {out_path}")
    return story_title, full_content, saved_id

def main():
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"服务器: OK ({r.status_code})")
    except:
        print("错误: 请先启动服务器 python start.py"); sys.exit(1)

    prev_id, results = None, []
    for ch in config['chapters']:
        title, content, sid = generate_chapter(ch, prev_id)
        if sid:
            prev_id = sid
            results.append({"ch": ch['chapter_num'], "title": title or ch['title'],
                            "wc": len(content) if content else 0, "id": sid})
        print("  冷却 30 秒..."); time.sleep(30)

    print(f"\n{'='*60}\n  生成完成!\n{'='*60}")
    total = 0
    for r in results:
        total += r['wc']
        print(f"  第{r['ch']}章《{r['title']}》 - {r['wc']}字")
    print(f"  总计: {total}字 / {len(results)}章\n  作品ID: {work_id}")

if __name__ == '__main__':
    main()
