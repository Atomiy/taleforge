"""验证苍狼传说第一卷角色出场约束"""
import re, os

chars = ['铁山', '雪莉', '霜牙', '赤焰', '狼灵']
participation = {
    1: {'铁山': '主动', '雪莉': '主动', '霜牙': '被动', '狼灵': '被动'},
    2: {'铁山': '主动', '雪莉': '主动', '霜牙': '被动', '赤焰': '主动', '狼灵': '主动'},
    3: {'铁山': '主动', '雪莉': '主动', '赤焰': '主动', '狼灵': '主动'},
}

results = {}
for ch_num in [1, 2, 3]:
    fpath = f'scripts/wolf_ch{ch_num}.txt'
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    wc = len(text.replace('\n', '').replace(' ', ''))
    ch_errors = []
    print(f'\n=== 第{ch_num}章 ({wc}字) ===')
    for name, role in participation[ch_num].items():
        cnt = text.count(name)
        has_dial = bool(re.search(rf'{re.escape(name)}[说喊道叫嚷问答]', text))
        status = 'PASS'
        if role == '被动':
            if cnt == 0:
                ch_errors.append(f'  [WARN] {name}: 被动但完全未被提及')
                status = 'WARN'
            elif has_dial:
                ch_errors.append(f'  [FAIL] {name}: 被动但有主动对话 (出现{cnt}次)')
                status = 'FAIL'
            else:
                print(f'  [PASS] {name}: 被动合规 (出现{cnt}次, 无主动对话)')
        elif role == '主动':
            if cnt == 0:
                ch_errors.append(f'  [FAIL] {name}: 主动但完全未出现')
                status = 'FAIL'
            elif cnt < 3 and not has_dial:
                print(f'  [PASS] {name}: 主动合规 (仅{cnt}次, 戏份较少)')
            else:
                print(f'  [PASS] {name}: 主动合规 (出现{cnt}次)')
        elif role == '缺席' and cnt > 0:
            ch_errors.append(f'  [FAIL] {name}: 缺席但出现{cnt}次')
            status = 'FAIL'
    # 溢出角色检测
    for c in chars:
        if c not in participation[ch_num]:
            cnt = text.count(c)
            if cnt > 0:
                ch_errors.append(f'  [INFO] {c}: 未在出场表中但被提及{cnt}次')
    for e in ch_errors:
        print(e)
    if not ch_errors:
        print('  全部合规!')
    results[ch_num] = {'wc': wc, 'errors': len(ch_errors)}

print('\n' + '='*50)
print(f'苍狼传说 第一卷 验证汇总')
print('='*50)
total_errors = sum(r['errors'] for r in results.values())
for n, r in results.items():
    print(f'  第{n}章: {r["wc"]}字, {r["errors"]}个问题')
print(f'  总计: {total_errors}个问题')
print(f'  状态: {"PASS" if total_errors == 0 else "见上方详情"}')
