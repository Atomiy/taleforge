"""
深渊回响 v2 - 跨章人物出场表验证生成脚本
通过 API 依次生成 3 章，每章依赖前一章作为续写上下文
"""
import json
import os
import sys
import time
import requests

BASE_URL = "http://127.0.0.1:8080"

# 载入配置
with open(r'scripts\abyss_v2_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

work_id = config['work_id']
volume_id = config['volume_id']

def generate_chapter(chapter, previous_story_id=None):
    """生成一章内容，返回 (title, content, story_id)"""
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

    # 调 API
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

        # 显示进度
        if status in ('running', 'done', 'error'):
            print(f"  [{agent}] {status}: {msg[:60]}")

        # 收集 writer 输出的内容
        if agent == 'writer' and status == 'writing':
            full_content += data.get('data', '')

        # 收集最终结果
        if agent == 'orchestrator' and status == 'complete':
            story_title = data['data'].get('title', chapter['title'])
            if data['data'].get('content'):
                full_content = data['data']['content']

        # 收集 story_id（从保存后得知）
        if agent == 'orchestrator' and status == 'complete':
            story_id = data['data'].get('story_id')

    if not full_content:
        print(f"  [WARN] 内容为空，跳过保存")
        return None, None, None

    # 保存故事
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

    # 关联到作品
    if saved_id and work_id:
        attach_resp = requests.post(f"{BASE_URL}/api/v1/works/{work_id}/chapters", json={
            "story_id": saved_id,
            "volume_id": volume_id
        })
        if attach_resp.ok:
            print(f"  已关联到作品卷")

    # 写本地备份
    out_path = f"scripts/abyss_v2_ch{chapter['chapter_num']}.txt"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"## 第{chapter['chapter_num']}章 {story_title or chapter['title']}\n\n")
        f.write(full_content)
    print(f"  已备份到: {out_path}")

    return story_title, full_content, saved_id


def main():
    # 先检查服务器
    try:
        r = requests.get(f"{BASE_URL}/api/v1/health", timeout=5)
        print(f"服务器状态: {r.status_code}")
    except requests.ConnectionError:
        print("错误: 服务器未启动！请先运行 python start.py")
        sys.exit(1)

    previous_id = None
    results = []

    for ch in config['chapters']:
        title, content, sid = generate_chapter(ch, previous_id)
        if sid:
            previous_id = sid
            word_count = len(content) if content else 0
            results.append({
                "chapter": ch['chapter_num'],
                "title": title,
                "word_count": word_count,
                "story_id": sid
            })
        print(f"  等待 30 秒，让 API 冷却...")
        time.sleep(30)

    print(f"\n{'='*60}")
    print(f"  生成完成!")
    print(f"{'='*60}")
    for r in results:
        print(f"  第{r['chapter']}章《{r['title']}》 - {r['word_count']}字 (id={r['story_id']})")
    print(f"\n  总计: {sum(r['word_count'] for r in results)}字 / {len(results)}章")
    print(f"  作品ID: {work_id}")
    print(f"  config: scripts/abyss_v2_config.json")

if __name__ == '__main__':
    main()
