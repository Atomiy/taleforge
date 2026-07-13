"""检查 v3.5 配置中 key_events 是否含赵海"""
import json
with open('scripts/abyss_v35_config.json', encoding='utf-8') as f:
    cfg = json.load(f)
for ch in cfg['chapters']:
    for ke in ch['key_events']:
        if '赵海' in ke:
            print(f'WARN: Ch{ch["chapter_num"]} key_event 含赵海: {ke}')
print('key_events 校验完成')
