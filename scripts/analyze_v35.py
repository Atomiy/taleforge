"""分析 v3.5 各版本"""
import re
for ver in ['v35']:
    print(f'--- {ver.upper()} ---')
    for ch in [1,2,3]:
        try:
            text = open(f'scripts/abyss_{ver}_ch{ch}.txt', encoding='utf-8').read()
            body = '\n'.join(l for l in text.split('\n') if not l.strip().startswith('## '))
            n = {'林深':0,'陈霜':0,'索菲娅':0,'米兰':0,'赵海':0,'深渊之眼':0,'王磊':0,'陈丽':0,'李薇':0}
            for k in n: n[k] = body.count(k)
            active = any(re.search(r'赵海'+v, body) for v in ['说','道','问','喊','叫','嚷','回答','低语','开口'])
            ov = sum(n[b] for b in ['王磊','陈丽','李薇'])
            print(f'  Ch{ch}: {len(body)}字 | 赵海{n["赵海"]:>2}次 | 主动对话={"Y" if active else "n"} | 溢出={ov}')
            if ch == 2:
                for i, line in enumerate(body.split('\n')):
                    if '赵海' in line: print(f'    L{i}: {line.strip()[:80]}')
        except Exception as e:
            print(f'  Ch{ch}: {e}')
