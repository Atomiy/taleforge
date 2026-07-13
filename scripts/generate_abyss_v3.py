"""
深渊回响 v3 生成脚本 (Character Agent + Writer 双重约束)
依次生成 3 章，每章依赖前一章作为续写上下文
"""
import json
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8080"

with open(r'scripts\abyss_v3_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

work_id = config['work_id']
volume_id = config['volume_id']

def generate_chapter(chapter, previous_story_id=None):
    print(f"\n{'='*60}")
    print(f"  生成第{chapter['chapter_num']}章: {chapter['title']}")
    print(f"{'='*60}")

    payload = {
        "theme": chapter['theme'],
        "genre": config['genre'],
        "style": config['style'],
        "length": 3000,
        "background": config['world_setting'],
        "perspective": "第三人称有限",
        "conflict": "人与超自然",
        "mood": "悬疑压抑",
        "outline": '\n'.join(chapter['key_events']),
        "characters": config['characters'],
        "world_setting": config['world_setting'],
        "foreshadowings": config['foreshadowings'],
        "work_id": work_id,
        "volume_id": volume_id,
        "chapter_number": chapter['chapter_num'],
        "continuation_mode": "next_chapter",
    }
    if previous_story_id:
        payload["previous_story_id"] = previous_story_id

    resp = requests.post(f"{BASE_URL}/api/v1/story/generate", json=payload, stream=True, timeout=300)

    full_content = ""
    story_title = ""
    story_id = None

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data: '):
            continue
        try:
            data = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        agent = data.get('agent', '')
        status = data.get('status', '')
        msg = data.get('message', '')

        if status in ('running', 'done', 'error'):
            print(f"  [{agent}] {status}: {msg[:80]}")

        if agent == 'writer' and status == 'writing':
            full_content += data.get('data', '')
        if agent == 'orchestrator' and status == 'complete':
            story_title = data['data'].get('title', chapter['title'])
            if data['data'].get('content'):
                full_content = data['data']['content']

    if not full_content:
        print(f"  [WARN] 内容为空，跳过")
        return None, None, None

    print(f"  保存故事... (content_len={len(full_content)})")
    save_resp = requests.post(f"{BASE_URL}/api/v1/story/save", json={
        "title": story_title or chapter['title'],
        "content": full_content,
        "theme": chapter['theme'],
        "genre": config['genre'],
        "style": config['style'],
        "world_setting": config['world_setting'],
        "foreshadowings": config['foreshadowings'],
        "series_id": work_id,
        "series_order": chapter['chapter_num'],
    })
    saved = save_resp.json()
    saved_id = saved.get('id') or saved.get('story_id')
    print(f"  保存成功: id={saved_id}, title={story_title}")

    if saved_id and work_id:
        requests.post(f"{BASE_URL}/api/v1/works/{work_id}/chapters", json={
            "story_id": saved_id,
            "volume_id": volume_id
        })

    out_path = f"scripts/abyss_v3_ch{chapter['chapter_num']}.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"## 第{chapter['chapter_num']}章 {story_title or chapter['title']}\n\n")
        f.write(full_content)
    print(f"  已备份到: {out_path}")
    return story_title, full_content, saved_id


def main():
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"服务器状态: OK ({r.status_code})")
    except requests.ConnectionError:
        print("错误: 服务器未启动！请先运行 python start.py")
        sys.exit(1)

    previous_id = None
    results = []
    for ch in config['chapters']:
        title, content, sid = generate_chapter(ch, previous_id)
        if sid:
            previous_id = sid
            results.append({
                "chapter": ch['chapter_num'],
                "title": title or ch['title'],
                "word_count": len(content) if content else 0,
                "story_id": sid
            })
        print(f"  等待 30 秒冷却...")
        time.sleep(30)

    print(f"\n{'='*60}")
    print(f"  生成完成!")
    print(f"{'='*60}")
    total_words = 0
    for r in results:
        total_words += r['word_count']
        print(f"  第{r['chapter']}章《{r['title']}》 - {r['word_count']}字")
    print(f"  总计: {total_words}字 / {len(results)}章")
    print(f"  作品ID: {work_id}")

if __name__ == '__main__':
    main()
