"""四版本数据对比"""
import re
from pathlib import Path
d = Path('scripts')

def an(path):
    if not path.exists(): return None
    text = path.read_text('utf-8')
    body = '\n'.join(l for l in text.split('\n') if not l.strip().startswith('## '))
    n = {'林深':0,'陈霜':0,'索菲娅':0,'米兰':0,'赵海':0,'深渊之眼':0,'王磊':0,'陈丽':0,'李薇':0}
    for k in n: n[k] = body.count(k)
    active = any(re.search(r'赵海'+v, body) for v in ['说','道','问','喊','叫','嚷','回答','低语','开口'])
    return (len(body), n['赵海'], active, sum(n[b] for b in ['王磊','陈丽','李薇']))

for v in ['v32','v33','v34']:
    print(f'--- {v.upper()} ---')
    for ch in [1,2,3]:
        r = an(d/f'abyss_{v}_ch{ch}.txt')
        if r:
            print(f'  Ch{ch}: {r[0]:>4}字 | 赵海{r[1]:>3}次 | 主动对话={"Y" if r[2] else "n"} | 溢出{r[3]}')
