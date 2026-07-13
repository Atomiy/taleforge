"""完整版本对比"""
import re
from pathlib import Path

versions = {'v32':'原始跨章出场表','v33':'角色过滤+缺席','v34':'无矛盾剧情','v35':'出场目的约束'}

def an(path):
    if not path.exists(): return None
    text = path.read_text('utf-8')
    body = '\n'.join(l for l in text.split('\n') if not l.strip().startswith('## '))
    n = {'林深':0,'陈霜':0,'索菲娅':0,'赵海':0,'深渊之眼':0,'王磊':0,'陈丽':0,'李薇':0}
    for k in n: n[k] = body.count(k)
    active = any(re.search(r'赵海'+v, body) for v in ['说','道','问','喊','叫','嚷','回答','低语','开口'])
    ov = sum(n[b] for b in ['王磊','陈丽','李薇'])
    return (len(body), n['赵海'], active, ov)

print(f'{"版本":>6} {"Ch字数":>6} {"赵海":>3} {"对话":>3} {"溢出":>4}')
print('-'*28)
for ver, desc in versions.items():
    for ch in [1,2,3]:
        r = an(Path(f'scripts/abyss_{ver}_ch{ch}.txt'))
        if r:
            a = 'Y' if r[2] else 'n'
            print(f'{ver}Ch{ch}: {r[0]:>4}字 | {r[1]:>2}次 | {a} | {r[3]}')
