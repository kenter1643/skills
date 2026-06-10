#!/usr/bin/env python3
"""Audit an existing perspective skill for Investor V2 migration gaps."""

import re
import sys
from pathlib import Path


CHECKS = {
    "投资身份卡": (r"投资身份卡|主要市场与资产|适用范围", "structure"),
    "投资世界观": (r"投资世界观|错误定价|优势来源|风险定义", "research"),
    "研究操作系统": (r"研究操作系统|回答工作流|收集事实|研究流程", "structure"),
    "估值与市场预期": (r"估值与市场预期|估值锚|市场预期|安全边际|赔率", "research"),
    "组合与仓位": (r"组合与仓位|初始仓位|最大仓位|集中度|风险预算", "research"),
    "买卖与退出": (r"买卖与退出|退出纪律|建仓|加仓|减仓|退出方案", "research"),
    "证伪条件": (r"证伪条件|失效条件|假设失效", "structure"),
    "市场环境适配": (r"市场环境适配|适用环境|牛市|熊市|流动性", "research"),
    "案例复原": (r"案例复原|案例：|案例\d|已知测试", "research"),
    "失败与争议": (r"失败|争议|处罚|错误|反面课", "research"),
    "证据标签": (r"\[(?:P1|P2|S1|S2|I|U)\]", "structure"),
    "研究截止日期": (r"调研截止时间|research-cutoff", "structure"),
}

INVESTMENT_MARKERS = re.compile(
    r"投资|交易|股票|期货|基金|组合|仓位|估值|资本配置|宏观趋势"
)


def count_case_blocks(content: str) -> int:
    headings = re.findall(r"^#{2,4}\s+.*案例", content, re.MULTILINE)
    numbered = re.findall(r"(?:案例|case)\s*[一二三四五六七八九十\d]+", content, re.IGNORECASE)
    return max(len(headings), len(set(numbered)))


def count_failure_blocks(content: str) -> int:
    explicit = re.findall(
        r'^#{2,4}\s+失败案例\s*[一二三四五六七八九十\d]+',
        content,
        re.MULTILINE,
    )
    section = re.search(
        r"^##\s+.*(?:失败|争议|反模式|边界)(.*?)(?=^##\s+|\Z)",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not section:
        return len(explicit)
    section_items = re.findall(r"^[-*]|\|.*\|", section.group(1), re.MULTILINE)
    return max(len(explicit), len(section_items))


def main() -> int:
    if len(sys.argv) != 2:
        print("用法: python3 investor_v2_audit.py <Skill目录或SKILL.md>")
        return 2

    target = Path(sys.argv[1])
    skill_path = target / "SKILL.md" if target.is_dir() else target
    if not skill_path.exists():
        print(f"错误: 找不到 {skill_path}")
        return 2

    content = skill_path.read_text(encoding="utf-8")
    if not INVESTMENT_MARKERS.search(content):
        print("迁移等级: M0 无需迁移")
        print("原因: 未检测到足够的投资、交易或资本配置特征。")
        return 0

    results = {}
    for label, (pattern, gap_type) in CHECKS.items():
        results[label] = (bool(re.search(pattern, content, re.IGNORECASE)), gap_type)

    case_count = count_case_blocks(content)
    failure_count = count_failure_blocks(content)
    results["三个完整案例"] = (case_count >= 3, "research")
    results["两个失败案例"] = (failure_count >= 2, "research")

    missing = [name for name, (passed, _) in results.items() if not passed]
    research_gaps = [
        name for name, (passed, gap_type) in results.items()
        if not passed and gap_type == "research"
    ]

    research_content = ""
    research_dir = skill_path.parent / "references" / "research"
    if research_dir.exists():
        research_content = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(research_dir.glob("*.md"))
        )

    evidence_corpus = f"{content}\n{research_content}"
    source_urls = set(re.findall(r"https?://[^\s)>]+", evidence_corpus))
    has_source_markers = bool(re.search(
        r"一手|官方|原文|监管|本人|primary", evidence_corpus, re.IGNORECASE
    ))
    weak_source_signals = len(source_urls) == 0 and not has_source_markers

    if not missing:
        level = "V2 已完成"
    elif weak_source_signals and len(missing) >= 8:
        level = "M3 重新蒸馏"
    elif research_gaps:
        level = "M2 增量补研"
    elif missing:
        level = "M1 结构升级"
    else:
        level = "M1 结构升级"

    print(f"投资人 V2 迁移审计: {skill_path}")
    print("=" * 64)
    for name, (passed, _) in results.items():
        print(f"{'PASS' if passed else 'GAP ':<4}  {name}")
    print("=" * 64)
    print(f"检测到URL: {len(source_urls)}")
    print(f"案例块: {case_count}，失败/争议条目: {failure_count}")
    print(f"迁移等级: {level}")

    if missing:
        print("\n缺口:")
        for name in missing:
            print(f"- {name}")
    else:
        print("\n未发现明显字段缺口；仍需人工核对证据质量。")

    if level.startswith("V2"):
        print("\n建议: 无结构缺口；继续人工复核证据质量和时效性。")
    elif level.startswith("M1"):
        print("\n建议: 保留旧研究，只补V2结构、证据标签和标准回答协议。")
    elif level.startswith("M2"):
        print("\n建议: 复用已有内容，仅对上述研究缺口定向补研。")
    elif level.startswith("M3"):
        print("\n建议: 先重建来源账本，再决定哪些旧结论可以保留。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
