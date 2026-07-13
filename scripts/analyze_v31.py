"""分析 v3.1 各章节的角色出现次数"""
files = [
    ("scripts/abyss_v31_ch1.txt", "第1章"),
    ("scripts/abyss_v31_ch2.txt", "第2章"),
    ("scripts/abyss_v31_ch3.txt", "第3章"),
]

allowed = ["林深", "陈霜", "赵海", "深渊之眼", "米兰"]
banned = ["王磊", "陈丽", "李薇"]

for fpath, label in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    wc = len(text.replace('\n','').replace(' ',''))
    print(f"\n{'='*50}")
    print(f"  {label} (字数: {wc})")
    print(f"{'='*50}")
    for name in allowed:
        if name == "米兰":
            c = text.count("米兰") + text.count("索菲娅")
            flag = " *** 缺场!" if c == 0 else ""
            print(f"  Dr.索菲娅·米兰: {c}次{flag}")
        else:
            c = text.count(name)
            flag = " *** 缺场!" if c == 0 else ""
            print(f"  {name}: {c}次{flag}")
    for name in banned:
        c = text.count(name)
        flag = " *** 违规!" if c > 0 else ""
        print(f"  {name}: {c}次{flag}")
