#!/usr/bin/env python3
"""
自动检查生成的SKILL.md是否通过Phase 4质量标准。
对照通过标准表格逐项检查，输出通过/不通过和具体原因。

用法:
    python3 quality_check.py [--profile general|investment|auto] <SKILL.md路径>

示例:
    python3 quality_check.py .claude/skills/elon-musk-perspective/SKILL.md
"""

import sys
import re
from pathlib import Path


def check_mental_models(content: str) -> tuple[bool, str]:
    """检查心智模型数量（3-7个）"""
    # 匹配 ### 模型N: 或 ### N. 等模式
    models = re.findall(r'^###\s+(?:模型|Model|心智模型)\s*\d', content, re.MULTILINE)
    if not models:
        # fallback: 数「### 」开头的行在心智模型section中
        in_section = False
        count = 0
        for line in content.split('\n'):
            if re.match(r'^##\s+.*心智模型|Mental Model', line, re.IGNORECASE):
                in_section = True
                continue
            if in_section and re.match(r'^##\s+', line) and '心智模型' not in line:
                break
            if in_section and re.match(r'^###\s+', line):
                count += 1
        if count > 0:
            passed = 3 <= count <= 7
            return passed, f"{count}个心智模型 {'✅' if passed else '❌ (应为3-7个)'}"

    count = len(models)
    if count == 0:
        return False, "未检测到心智模型section"
    passed = 3 <= count <= 7
    return passed, f"{count}个心智模型 {'✅' if passed else '❌ (应为3-7个)'}"


def check_limitations(content: str) -> tuple[bool, str]:
    """检查每个模型是否有局限性"""
    has_limitation = bool(re.search(r'局限|失效|不适用|盲区|limitation|blind spot', content, re.IGNORECASE))
    return has_limitation, "有局限性标注 ✅" if has_limitation else "❌ 未找到局限性描述"


def check_expression_dna(content: str) -> tuple[bool, str]:
    """检查表达DNA辨识度"""
    dna_section = bool(re.search(r'表达DNA|Expression DNA|表达风格', content, re.IGNORECASE))
    if not dna_section:
        return False, "❌ 未找到表达DNA section"

    # 检查是否有具体的风格描述（句式、词汇等）
    style_markers = len(re.findall(r'句式|词汇|语气|幽默|节奏|确定性|引用|口头禅', content))
    passed = style_markers >= 3
    return passed, f"表达DNA特征: {style_markers}项 {'✅' if passed else '❌ (应≥3项)'}"


def check_honest_boundary(content: str) -> tuple[bool, str]:
    """检查诚实边界（至少3条）"""
    # 找诚实边界section
    boundary_match = re.search(r'(?:##\s+.*诚实边界|## Honest Boundary)(.*?)(?=\n##\s|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not boundary_match:
        return False, "❌ 未找到诚实边界section"

    boundary_text = boundary_match.group(1)
    # 计算列表项
    items = re.findall(r'^[-*]\s+', boundary_text, re.MULTILINE)
    count = len(items)
    passed = count >= 3
    return passed, f"诚实边界: {count}条 {'✅' if passed else '❌ (应≥3条)'}"


def check_tensions(content: str) -> tuple[bool, str]:
    """检查内在张力（至少2对）"""
    tension_markers = len(re.findall(r'张力|矛盾|tension|paradox|一方面.*另一方面|既.*又', content, re.IGNORECASE))
    passed = tension_markers >= 2
    return passed, f"内在张力: {tension_markers}处 {'✅' if passed else '❌ (应≥2处)'}"


def check_primary_sources(content: str) -> tuple[bool, str]:
    """检查一手来源占比"""
    # 找调研来源section
    source_section = re.search(r'(?:##\s+.*来源|## Source|## Reference)(.*?)(?=\n##\s|\Z)', content, re.DOTALL | re.IGNORECASE)
    if not source_section:
        return True, "未找到来源section（跳过检查）"

    source_text = source_section.group(1)
    primary = len(re.findall(r'一手|primary|本人著作|原始', source_text, re.IGNORECASE))
    secondary = len(re.findall(r'二手|secondary|转述|评论', source_text, re.IGNORECASE))
    total = primary + secondary
    if total == 0:
        return True, "未标记来源类型（跳过检查）"

    ratio = primary / total
    passed = ratio > 0.5
    return passed, f"一手来源占比: {primary}/{total} ({ratio:.0%}) {'✅' if passed else '❌ (应>50%)'}"


def section_present(content: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)


def count_evidence_labels(content: str) -> int:
    return len(re.findall(r'\[(?:P1|P2|S1|S2|I|U)\]', content))


def count_invalidation_items(content: str) -> int:
    matches = re.findall(r'失效条件|证伪条件|假设失效', content)
    list_items = 0
    for match in re.finditer(r'(?:##|###)\s+.*(?:失效|证伪)(.*?)(?=\n##|\Z)', content, re.DOTALL):
        list_items += len(re.findall(r'^[-*\d]+[.)、]?\s+', match.group(1), re.MULTILINE))
    return max(len(matches), list_items)


def count_case_sections(content: str) -> int:
    return len(re.findall(r'^#{2,4}\s+.*案例', content, re.MULTILINE))


def count_failure_cases(content: str) -> int:
    explicit = re.findall(
        r'^#{2,4}\s+失败案例\s*[一二三四五六七八九十\d]+',
        content,
        re.MULTILINE,
    )
    section = re.search(
        r'^##\s+.*(?:失败|争议)(.*?)(?=^##\s+|\Z)',
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        return 0
    headings = re.findall(r'^#{3,4}\s+', section.group(1), re.MULTILINE)
    list_items = re.findall(r'^[-*]\s+', section.group(1), re.MULTILINE)
    return max(len(explicit), len(headings), len(list_items))


def count_research_sources(skill_path: Path, content: str) -> int:
    corpus = content
    research_dir = skill_path.parent / "references" / "research"
    if research_dir.exists():
        corpus += "\n" + "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(research_dir.glob("*.md"))
        )
    urls = re.findall(r'https?://[^\s)>]+', corpus)
    return len(set(urls))


def investment_checks(content: str, skill_path: Path) -> list[tuple[str, bool, str]]:
    checks = []
    required_sections = {
        "投资身份卡": [r'投资身份卡', r'主要市场与资产'],
        "研究操作系统": [r'研究操作系统', r'研究流程'],
        "估值与预期": [r'估值与市场预期', r'估值锚'],
        "组合与仓位": [r'组合与仓位', r'初始仓位', r'最大仓位'],
        "买卖与退出": [r'买卖与退出', r'退出纪律'],
        "市场环境适配": [r'市场环境适配', r'适用环境'],
        "失败与争议": [r'失败.*争议', r'失败案例', r'争议案例'],
        "标准回答协议": [r'标准回答协议'],
    }
    for name, patterns in required_sections.items():
        passed = section_present(content, patterns)
        checks.append((name, passed, "存在" if passed else "缺失"))

    evidence_count = count_evidence_labels(content)
    checks.append(("证据标签", evidence_count >= 5, f"{evidence_count}处（应≥5）"))

    invalidation_count = count_invalidation_items(content)
    checks.append(("证伪条件", invalidation_count >= 3, f"{invalidation_count}处（应≥3）"))

    case_count = count_case_sections(content)
    checks.append(("案例复原", case_count >= 3, f"{case_count}个（应≥3）"))

    failure_count = count_failure_cases(content)
    checks.append(("失败案例", failure_count >= 2, f"{failure_count}个（应≥2）"))

    source_count = count_research_sources(skill_path, content)
    checks.append(("独立来源", source_count >= 15, f"{source_count}个（应≥15）"))

    has_cutoff = bool(re.search(r'调研截止时间|research-cutoff', content))
    checks.append(("研究截止日期", has_cutoff, "存在" if has_cutoff else "缺失"))

    boundary = bool(re.search(
        r'本人.*(?:表达|观点)|框架推演|可核验行为|不冒充本人',
        content,
        re.IGNORECASE,
    ))
    checks.append(("推演边界", boundary, "已区分" if boundary else "未明确区分"))
    return checks


def main():
    args = sys.argv[1:]
    profile = "auto"
    if len(args) >= 2 and args[0] == "--profile":
        profile = args[1]
        args = args[2:]
    if len(args) != 1 or profile not in {"auto", "general", "investment"}:
        print("用法: python3 quality_check.py [--profile general|investment|auto] <SKILL.md路径>")
        sys.exit(1)

    skill_path = Path(args[0])
    if not skill_path.exists():
        print(f"❌ 文件不存在: {skill_path}")
        sys.exit(1)

    content = skill_path.read_text(encoding='utf-8')

    checks = [
        ("心智模型数量", check_mental_models),
        ("模型局限性", check_limitations),
        ("表达DNA辨识度", check_expression_dna),
        ("诚实边界", check_honest_boundary),
        ("内在张力", check_tensions),
        ("一手来源占比", check_primary_sources),
    ]

    if profile == "auto":
        profile = "investment" if re.search(
            r'profile:\s*investor-v2|投资人 V2|投资操作系统', content, re.IGNORECASE
        ) else "general"

    print(f"质量检查: {skill_path.name}（{profile}）")
    print("=" * 50)

    passed_count = 0
    total = len(checks)

    for name, check_fn in checks:
        passed, detail = check_fn(content)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:<12} {status}  {detail}")
        if passed:
            passed_count += 1

    if profile == "investment":
        extra_checks = investment_checks(content, skill_path)
        total += len(extra_checks)
        for name, passed, detail in extra_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {name:<12} {status}  {detail}")
            if passed:
                passed_count += 1

    print("=" * 50)
    print(f"结果: {passed_count}/{total} 通过")

    if profile == "investment":
        ratio = passed_count / total
        grade = "A 可实战调用" if ratio == 1 else "B 研究视角" if ratio >= 0.7 else "C 人物理解"
        print(f"投资证据等级: {grade}")

    if passed_count == total:
        print("🎉 全部通过，可以交付")
    elif passed_count >= total - 1:
        print("⚠️ 基本通过，建议修复不通过项后交付")
    else:
        print("❌ 多项不通过，建议回到Phase 2迭代")

    sys.exit(0 if passed_count == total else 1)


if __name__ == '__main__':
    main()
