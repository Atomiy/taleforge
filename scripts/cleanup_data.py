"""
清理脚本：恢复三部作品 + 仅保留10条有效故事
三部曲：
  1. 深渊回响 v3.4 (fe46dd64) — 3章
  2. 星际余晖 (bba506fe) — 4章
  3. 苍狼传说 (0fd71cda) — 3章（更新为脚本生成版故事ID）
"""

import json, shutil, os
from datetime import datetime

BACKUP_DIR = r'backend\data'
STORIES_FILE = os.path.join(BACKUP_DIR, 'stories.json')
WORKS_FILE = os.path.join(BACKUP_DIR, 'works.json')
WORKS_BAK = os.path.join(BACKUP_DIR, 'works.json.bak')

# === 1. 备份当前 stories.json ===
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
stories_bak = os.path.join(BACKUP_DIR, f'stories.json.bak.{ts}')
shutil.copy2(STORIES_FILE, stories_bak)
print(f'[1/5] stories.json 已备份 → {stories_bak}')

# === 2. 恢复三部作品到 works.json ===
with open(WORKS_BAK, 'r', encoding='utf-8') as f:
    bak_works = json.load(f)

target_ids = {'fe46dd64', 'bba506fe', '0fd71cda'}
restored = [w for w in bak_works if w['id'] in target_ids]

print(f'[2/5] 从备份中找到 {len(restored)} 部目标作品:')
for w in restored:
    ch = len(w.get('chapter_ids', []))
    print(f'       [{w["id"][:8]}] {w["title"]} — {ch}章')

# === 3. 更新苍狼传说的 chapter_ids 为脚本生成版（更好的质量）===
# 旧版: 7ee311d4, 9868d67d, d5e822f5 (1366, 2320, 1683字)
# 新版: 05b03488, df2d7356, d72317e3 (2897, 3215, 4489字)
NEW_WOLF_CHAPTERS = ['05b03488', 'df2d7356', 'd72317e3']

for w in restored:
    if w['id'] == '0fd71cda':
        old_ids = w.get('chapter_ids', [])
        print(f'[3/5] 苍狼传说 chapter_ids: {old_ids} → {NEW_WOLF_CHAPTERS}')
        w['chapter_ids'] = NEW_WOLF_CHAPTERS.copy()
        # 同时更新 volume 中的 chapter_ids
        for vol in w.get('volumes', []):
            if 'chapter_ids' in vol:
                print(f'       卷[{vol.get("volume_number",1)}] chapter_ids: {vol["chapter_ids"]} → {NEW_WOLF_CHAPTERS}')
                vol['chapter_ids'] = NEW_WOLF_CHAPTERS.copy()

# 写入 works.json
with open(WORKS_FILE, 'w', encoding='utf-8') as f:
    json.dump(restored, f, ensure_ascii=False, indent=2)
print(f'[3/5] works.json 已写入 {len(restored)} 部作品')

# === 4. 清理 stories.json：只保留三部曲的 10 条有效故事 ===
KEEP_IDS = {
    'fe46dd64': ['a55344cd', 'd6857fa8', '9dcf4afe'],
    'bba506fe': ['733d4362', '0fa36211', 'db5f18d5', '97ceb274'],
    '0fd71cda': NEW_WOLF_CHAPTERS,
}
# 收集所有要保留的 story_id
keep_set = set()
for sid, ids in KEEP_IDS.items():
    keep_set.update(ids)

with open(STORIES_FILE, 'r', encoding='utf-8') as f:
    all_stories = json.load(f)

total_before = len(all_stories)
kept_stories = [s for s in all_stories if s['id'] in keep_set]
deleted_count = total_before - len(kept_stories)

# 验证保留的故事是否齐全
assert len(kept_stories) == len(keep_set), \
    f'预期保留 {len(keep_set)} 条，实际找到 {len(kept_stories)} 条（story_ids可能存在差异）'

# 按作品分组排序
kept_stories.sort(key=lambda x: (
    list(KEEP_IDS.keys()).index(x.get('series_id', '')) if x.get('series_id', '') in KEEP_IDS else 99,
    x.get('created_at', '')
))

with open(STORIES_FILE, 'w', encoding='utf-8') as f:
    json.dump(kept_stories, f, ensure_ascii=False, indent=2)

print(f'[4/5] stories.json 已清理: {total_before} → {len(kept_stories)}（删除 {deleted_count} 条）')
print(f'       保留列表:')
for s in kept_stories:
    series_name = ''
    for w in restored:
        if w['id'] == s.get('series_id', ''):
            series_name = w['title']
            break
    print(f'       [{s["id"][:8]}] {series_name} → {s.get("title","?")[:25]} ({s.get("word_count",0)}字)')

# === 5. 验证 ===
print(f'\n[5/5] 最终验证:')
with open(WORKS_FILE, 'r', encoding='utf-8') as f:
    final_works = json.load(f)
print(f'   works.json: {len(final_works)} 部作品')
for w in final_works:
    print(f'     [{w["id"][:8]}] {w["title"]} — {len(w["chapter_ids"])}章')

with open(STORIES_FILE, 'r', encoding='utf-8') as f:
    final_stories = json.load(f)
print(f'   stories.json: {len(final_stories)} 条故事')
for s in final_stories:
    print(f'     [{s["id"][:8]}] {s.get("series_id","?")[:8]} → {s.get("title","?")[:20]}')

print(f'\n✅ 清理完成！')
