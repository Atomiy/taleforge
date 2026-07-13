"""
v3.3 自动化验收脚本 — 与 v3.3 数据配置对齐
"""
import re, sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

# ====== 配置：每章角色参与类型（与 v3.3 chapter_participation 对齐）======
# v3.3 中赵海不在 Ch2 的 chapter_characters 中，等价于缺席
PARTICIPATION = {
    1: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
    2: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "缺席", "深渊之眼": "主动"},
    3: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
}

BANNED_NAMES = ["王磊", "陈丽", "李薇"]
NAME_ALIASES = {"Dr.索菲娅·米兰": ["索菲娅", "米兰", "Dr.索菲娅"]}


def count_name(text: str, name: str) -> int:
    total = text.count(name)
    for alias in NAME_ALIASES.get(name, []):
        total += text.count(alias)
    return total


def _name_variants(name: str) -> list:
    variants = [name]
    for alias in NAME_ALIASES.get(name, []):
        variants.append(alias)
    return variants


def has_direct_dialogue(text: str, name: str) -> bool:
    dialogue_verbs = ['说', '道', '问', '喊', '叫', '嚷', '回答', '低语', '开口']
    for variant in _name_variants(name):
        for verb in dialogue_verbs:
            if re.search(re.escape(variant) + verb, text):
                return True
        if re.search(re.escape(variant) + r'[：:]', text):
            return True
    return False


def has_action_verbs(text: str, name: str) -> bool:
    action_verbs = ['着', '了', '看', '站', '走', '坐', '握', '抓',
                    '推', '拉', '拿', '放', '转', '抬', '低', '沉思',
                    '想', '觉得', '感到', '意识到', '决定',
                    '冲', '指', '调出', '打开']
    for variant in _name_variants(name):
        for verb in action_verbs:
            if re.search(re.escape(variant) + r'.*?' + re.escape(verb), text[:2500]):
                return True
        for verb in ['说', '道', '问']:
            if re.search(re.escape(variant) + verb, text):
                return True
    return False


def validate_chapter(text: str, chapter_num: int, participation: dict) -> tuple:
    errors = []
    warnings = []
    # 移除标题行避免噪声
    body = '\n'.join(l for l in text.split('\n')
                     if not l.strip().startswith('## 第'))

    for banned in BANNED_NAMES:
        c = count_name(body, banned)
        if c > 0:
            errors.append(f"[回归失败] 溢出角色「{banned}」出现了 {c} 次")

    for name, role_type in participation.items():
        cnt = count_name(body, name)

        if role_type == "缺席":
            if cnt > 0:
                errors.append(f"[{name}] 缺席，但出现了 {cnt} 次")
            continue

        if role_type == "被动":
            if cnt == 0:
                errors.append(f"[{name}] 被动，但正文完全未提及（状态未体现）")
            elif cnt > 2:
                errors.append(f"[{name}] 被动，但被提及 {cnt} 次（应 ≤2）")
            elif has_direct_dialogue(body, name):
                errors.append(f"[{name}] 被动，但出现了主动说话或直接引语！")
            continue

        if role_type == "主动":
            if cnt < 3 and cnt > 0:
                warnings.append(f"[{name}] 主动，仅出现 {cnt} 次，戏份可能不足")
            elif cnt == 0:
                warnings.append(f"[{name}] 主动，但正文未出现！")
            elif cnt >= 3 and not has_action_verbs(body, name):
                warnings.append(f"[{name}] 主动，出现 {cnt} 次但缺乏明确的动作/对话检测")
            continue

    return errors, warnings


def print_report(all_results: dict):
    total_errors = 0
    total_warnings = 0
    print("\n" + "=" * 60)
    print("  v3.3 全链路严格约束 — 自动化验收报告")
    print("=" * 60)
    for ch_num in sorted(all_results.keys()):
        errors, warnings, wc = all_results[ch_num]
        total_errors += len(errors)
        total_warnings += len(warnings)
        status = "PASS" if not errors else "FAIL"
        print(f"\n  第{ch_num}章 ({wc}字) [{status}]")
        print(f"  {'-'*40}")
        for e in errors:
            print(f"    [ERROR] {e}")
        for w in warnings:
            print(f"    [WARN]  {w}")
        if not errors and not warnings:
            print(f"    零违规")
    print(f"\n  {'='*40}")
    print(f"  总计: {total_errors} errors, {total_warnings} warnings")
    if total_errors == 0:
        print(f"  结果: PASS -- 全链路约束硬性过关!")
    else:
        print(f"  结果: FAIL -- 需修复 {total_errors} 个违规")
    print(f"  {'='*40}\n")
    return total_errors


if __name__ == "__main__":
    results = {}
    for ch_num in [1, 2, 3]:
        fpath = SCRIPTS_DIR / f"abyss_v33_ch{ch_num}.txt"
        if not fpath.exists():
            print(f"[ERROR] 文件缺失: {fpath}")
            results[ch_num] = ([f"文件缺失: {fpath}"], [], 0)
            continue
        text = fpath.read_text(encoding='utf-8')
        wc = len(text.replace('\n', '').replace(' ', ''))
        errors, warnings = validate_chapter(text, ch_num, PARTICIPATION.get(ch_num, {}))
        results[ch_num] = (errors, warnings, wc)

    ec = print_report(results)
    sys.exit(0 if ec == 0 else 1)
