"""分析 v3 各章节的角色出现次数"""
import re, json

files = [
    ("scripts/abyss_v3_ch1.txt", "第1章"),
    ("scripts/abyss_v3_ch2.txt", "第2章"),
    ("scripts/abyss_v3_ch3.txt", "第3章"),
]

allowed = ["林深", "陈霜", "索菲娅", "赵海", "深渊之眼", "米兰"]
banned = ["王磊", "陈丽", "李薇"]

for fpath, label in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    wc = len(text.replace('\n','').replace(' ',''))
    print(f"\n{'='*50}")
    print(f"  {label} (字数: {wc})")
    print(f"{'='*50}")
    
    for name in allowed + banned:
        count = text.count(name)
        marker = " *** 违规!" if name in banned and count > 0 else \
                 " *** 缺场!" if name in allowed[:4] and count == 0 else ""
        if name == "米兰":
            count = text.count("米兰") + text.count("索菲娅")  # 合并统计
            name_display = "Dr.索菲娅·米兰"
        else:
            name_display = name
        print(f"  {name_display}: {count}次{marker}")
