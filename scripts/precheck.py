"""
预生成校验器（防呆设计）
在 Planner 生成前检测配置层矛盾，确保角色约束与剧情设计不自相矛盾。
"""
import re

# ===== 常量 =====
F1_RESTRICTED = {"信息提供", "冲突制造", "催化事件"}
F1_MAIN = "推进剧情"
VALID_FAMILIES = {"推进剧情", "塑造人物", "表达主题", "营造氛围"}
# 所有合法子类型（含四大类的全部子类）
VALID_SUBTYPES = {
    "主动推动", "信息提供", "冲突制造", "催化事件",
    "衬托主角", "揭示关系", "自身弧线", "情感锚点",
    "主题载体", "象征隐喻", "道德困境",
    "氛围渲染", "世界观展示", "悬念制造",
}
VALID_ALL = VALID_FAMILIES | VALID_SUBTYPES

# 明显矛盾的动词（用于检测自定义描述）
ACTIVE_VERBS = ["说", "道", "决定", "命令", "走", "跑", "拿", "推", "操作", "控制"]


def run_precheck(chapter_characters, chapter_participation, chapter_purpose, key_events_str):
    """
    预生成校验器主入口
    参数：
      chapter_characters: list[dict] 每章出场人物列表
      chapter_participation: dict 每章每角色参与类型
      chapter_purpose: dict 每章每角色出场目的
      key_events_str: dict[ch_num] -> list[str] 每章大纲关键剧情
    返回：
      {ch_num: [{"rule": "C1", "severity": "ERROR", "detail": "..."}, ...]}
    """
    results = {}

    # 构建角色名→章节的查找表
    char_to_chapters = {}
    for entry in chapter_characters:
        cn = entry["chapter_num"]
        for cname in entry.get("characters", []):
            char_to_chapters.setdefault(cname, []).append(cn)

    for entry in chapter_characters:
        cn = entry["chapter_num"]
        chapter_results = []

        for cname in entry.get("characters", []):
            role_type = chapter_participation.get(cn, {}).get(cname, "主动")
            purposes = chapter_purpose.get(cn, {}).get(cname, [])
            kevs = key_events_str.get(cn, [])

            # --- C1: 被动 + 目的为推进剧情(不含受限子类) ---
            if role_type == "被动":
                has_f1_main = any(p.startswith(F1_MAIN) or p == F1_MAIN for p in purposes)
                has_restricted = any(p in F1_RESTRICTED for p in purposes)
                if has_f1_main and not has_restricted:
                    chapter_results.append({
                        "rule": "C1",
                        "severity": "ERROR",
                        "detail": f"[{cname}] 标记为被动但目的为'推进剧情'(不含受限子类: 信息提供/冲突制造/催化事件)",
                        "suggestion": "方案A: 将参与类型改为'主动'; 方案B: 将目的改为'信息提供/冲突制造/催化事件'之一"
                    })

            # --- C1b: 被动 + F1 受限子类重叠（2+个） ---
            if role_type == "被动":
                overlap = [p for p in purposes if p in F1_RESTRICTED]
                if len(overlap) >= 2:
                    chapter_results.append({
                        "rule": "C1b",
                        "severity": "WARN",
                        "detail": f"[{cname}] 受限子类存在语义重叠: {'+'.join(overlap)}。建议只选一个，避免混乱",
                        "suggestion": "建议保留最主要的子类，删除其余"
                    })

            # --- C2: 缺席 + 出场目的非空 ---
            if role_type == "缺席" and purposes:
                chapter_results.append({
                    "rule": "C2",
                    "severity": "WARN",
                    "detail": f"[{cname}] 标记为缺席，但出场目的非空: {purposes}",
                    "suggestion": "缺席角色无需出场目的，请清空"
                })

            # --- C4: 主动 + 无出场目的 ---
            if role_type == "主动" and not purposes:
                chapter_results.append({
                    "rule": "C4",
                    "severity": "INFO",
                    "detail": f"[{cname}] 主动但出场目的为空，将使用默认值'推进剧情'",
                    "suggestion": "可选: 手动填写具体目的"
                })

            # --- C6: 目的不在白名单中 ---
            for p in purposes:
                if p in VALID_ALL:
                    continue
                # 额外检测：自定义描述是否含主动动词
                has_active = any(re.search(re.escape(v), p) for v in ACTIVE_VERBS)
                if has_active and role_type == "被动":
                    chapter_results.append({
                        "rule": "C6",
                        "severity": "WARN",
                        "detail": f"[{cname}] 自定义目的'{p}'含主动动词，与被动类型矛盾",
                        "suggestion": "请将目的描述修改为被动视角"
                    })
                else:
                    chapter_results.append({
                        "rule": "C6",
                        "severity": "INFO",
                        "detail": f"[{cname}] 自定义目的'{p}'不在标准分类中，已跳过校验",
                        "suggestion": "无"
                    })

        # --- C3: key_event 含缺席角色名 ---
        for kev in kevs:
            for cname in entry.get("characters", []):
                role_type = chapter_participation.get(cn, {}).get(cname, "主动")
                if role_type == "缺席" and cname in kev:
                    chapter_results.append({
                        "rule": "C3",
                        "severity": "ERROR",
                        "detail": f"[{cname}] 标记为缺席，但出现在 key_event 中: '{kev[:50]}...'",
                        "suggestion": "方案A: 将参与类型改为'被动'; 方案B: 改写 key_event, 不用角色名"
                    })

        # --- C5: 被动角色在 key_event 中有主动动词 ---
        for kev in kevs:
            for cname in entry.get("characters", []):
                role_type = chapter_participation.get(cn, {}).get(cname, "主动")
                if role_type == "被动":
                    for verb in ACTIVE_VERBS:
                        if re.search(re.escape(cname) + verb, kev):
                            chapter_results.append({
                                "rule": "C5",
                                "severity": "ERROR",
                                "detail": f"[{cname}] 被动角色在 key_event 中出现主动动词'{verb}': '{kev[:50]}...'",
                                "suggestion": "修改 key_event 措辞，被动角色仅通过他人转述/数据体现"
                            })
                            break

        if chapter_results:
            results[cn] = chapter_results

    return results


def print_report(results):
    """打印校验报告"""
    if not results:
        print("预生成校验: PASS (零冲突)")
        return 0

    total_errors = sum(1 for rr in results.values() for r in rr if r["severity"] == "ERROR")
    total_warns = sum(1 for rr in results.values() for r in rr if r["severity"] == "WARN")
    total_infos = sum(1 for rr in results.values() for r in rr if r["severity"] == "INFO")

    print(f"\n{'='*60}")
    print(f"  预生成校验报告")
    print(f"{'='*60}")
    for cn in sorted(results.keys()):
        print(f"\n  第{cn}章:")
        print(f"  {'-'*40}")
        for r in results[cn]:
            tag = {"ERROR": "X", "WARN": "!", "INFO": ">"}[r["severity"]]
            print(f"  [{tag}] [{r['rule']}] {r['detail']}")
            print(f"      建议: {r['suggestion']}")
    print(f"\n  {'='*40}")
    print(f"  统计: {total_errors} ERROR, {total_warns} WARN, {total_infos} INFO")
    if total_errors == 0:
        print(f"  结论: PASS — 配置无矛盾，可安全生成")
    else:
        print(f"  结论: FAIL — 请先修复 {total_errors} 个 ERROR 后再生成")
    print(f"  {'='*40}\n")
    return total_errors


if __name__ == "__main__":
    # 测试用例：v3.5 配置
    test_config = {
        "chapter_characters": [
            {"chapter_num": 1, "title": "寂静深海",
             "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
            {"chapter_num": 2, "title": "符号密语",
             "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
            {"chapter_num": 3, "title": "裂痕",
             "characters": ["林深", "陈霜", "Dr.索菲娅·米兰", "赵海", "深渊之眼"]},
        ],
        "chapter_participation": {
            1: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
            2: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "被动", "深渊之眼": "主动"},
            3: {"林深": "主动", "陈霜": "主动", "Dr.索菲娅·米兰": "主动", "赵海": "主动", "深渊之眼": "主动"},
        },
        "chapter_purpose": {
            2: {"赵海": ["信息提供", "情感锚点", "主题载体"]},
        },
        "key_events_str": {
            1: ["下潜至8000米", "首次接触深渊之眼", "团队产生分歧", "赵海首次链接异常"],
            2: [
                "结构体符号肉眼可见地流动重组",
                "索菲娅发现符号有编码信息，正在实时变化",
                "深渊之眼通过符号向不同人展现不同信息",
                "陈霜设备12小时后间歇性失灵",
                "通讯操作员的监控数据出现异常模式",
                "陈霜要求撤离被林深和索菲娅反对",
            ],
            3: ["不同队员看到不同幻象", "赵海成为传声筒", "陈霜试图摧毁装置"],
        }
    }

    results = run_precheck(**test_config)
    print_report(results)
