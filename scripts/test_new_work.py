"""
测试全新作品生成 - 创建一个与"苍狼传说"不同的新作品
- 创建一个新作品（科幻题材）
- 生成其第一章
- 保存结果供对比
"""
import requests, json, sys, time

BASE = 'http://127.0.0.1:8080'

# ========== 1. 创建新作品 ==========
print('='*60)
print('1. 创建新作品（科幻题材）')
print('='*60)

new_work_payload = {
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

r = requests.post(f'{BASE}/api/v1/works/', json=new_work_payload)
if r.status_code != 200:
    print(f'创建作品失败: {r.status_code}')
    print(r.text[:500])
    sys.exit(1)

work_id = r.json().get('work_id')
print(f'作品创建成功! work_id: {work_id}')

# 获取作品信息
r = requests.get(f'{BASE}/api/v1/works/{work_id}')
work_data = r.json().get('work', {})
print(f'作品: {work_data.get("title")}')
print(f'体裁: {work_data.get("genre")}')
print(f'风格: {work_data.get("style")}')
volumes = work_data.get('volumes', [])
if volumes:
    print(f'默认卷: {volumes[0].get("id")} - {volumes[0].get("title")}')

# ========== 2. 生成第一章 ==========
print('\n' + '='*60)
print('2. 生成第一章')
print('='*60)

generation_payload = {
    "theme": "星际余晖：最后的地球舰队",
    "genre": "科幻",
    "style": "硬科幻",
    "length": 2500,
    "background": new_work_payload["world_setting"],
    "perspective": "第三人称全知",
    "mood": "悬疑壮丽",
    "conflict": "人与人/人与未知",
    "characters": [],
    "foreshadowing": new_work_payload["foreshadowings"],
    "template_id": None,
    "continuation_mode": "",
    "previous_story_id": "",
    "work_id": work_id,
    "chapter_number": 1,
    "volume_id": volumes[0]["id"] if volumes else ""
}
print(f'生成参数: 字数={generation_payload["length"]}, 题材={generation_payload["genre"]}')

# 调用流式生成
print('\n生成中...\n' + '-'*60)
collected = []
r = requests.post(
    f'{BASE}/api/v1/story/generate',
    json=generation_payload,
    stream=True,
    timeout=300
)
if r.status_code != 200:
    print(f'请求失败: {r.status_code}')
    print(r.text[:1000])
    sys.exit(1)

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
                print(parsed['text'], end='', flush=True)
            elif parsed.get('agent') == 'writer' and parsed.get('status') == 'writing':
                data = parsed.get('data', '')
                if data:
                    collected.append(data)
                    print(data, end='', flush=True)
            elif 'status' in parsed and parsed.get('agent'):
                icon = {'running': '>', 'writing': 'W', 'complete': 'OK', 'error': 'XX'}.get(parsed['status'], '?')
                msg = parsed.get('message', '')
                if msg:
                    print(f'\n[{icon} {parsed["agent"]}] {msg}')
                else:
                    print(f'\n[{icon} {parsed["agent"]}]')
        except json.JSONDecodeError:
            pass

full_text = ''.join(collected)
print('\n' + '-'*60)
print(f'\n生成完成！{len(full_text)} 字')

# 提取标题
first_line = full_text.strip().split('\n')[0] if full_text else '(空)'
print(f'首行: {first_line[:100]}')

# ========== 3. 保存故事到作品 ==========
print('\n' + '='*60)
print('3. 保存结果')
print('='*60)

# 先保存故事到 history
title = first_line.replace('## ', '').replace('# ', '').strip() if full_text else '第一章'
save_payload = {
    "title": title,
    "content": full_text,
    "theme": "星际余晖：最后的地球舰队",
    "genre": "科幻",
    "style": "硬科幻",
    "outline": None,
    "characters": None,
    "series_id": work_id,
    "series_order": 1,
    "world_setting": new_work_payload["world_setting"],
    "foreshadowings": new_work_payload["foreshadowings"],
}
r = requests.post(f'{BASE}/api/v1/story/save', json=save_payload)
if r.status_code != 200:
    print(f'保存故事失败: {r.status_code}')
    print(r.text[:500])
    story_id = None
else:
    story_id = r.json().get('story_id')
    print(f'故事已保存: story_id={story_id}')

# 将章节添加到作品
if story_id:
    r = requests.post(f'{BASE}/api/v1/works/{work_id}/chapters', json={
        "story_id": story_id,
        "volume_id": volumes[0]["id"] if volumes else ""
    })
    if r.status_code == 200:
        print(f'章节已添加到作品')
    else:
        print(f'添加章节到作品失败: {r.status_code}')

# 保存到本地文件
output_path = 'scripts/新作品_星际余晖_第一章.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(full_text)
print(f'\n已保存到本地: {output_path}')

print('\n' + '='*60)
print('完成！请对比苍狼传说 第1-3章 vs 星际余晖 第1章')
print('='*60)
