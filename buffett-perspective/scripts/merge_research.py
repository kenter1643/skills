#!/usr/bin/env python3
"""
合并通用人物6维或投资人V2十维调研结果，生成Phase 1.5摘要表格。

用法:
    python3 merge_research.py <skill目录路径>

示例:
    python3 merge_research.py .claude/skills/elon-musk-perspective

输出: 打印markdown格式的摘要表格到stdout
"""

import sys
import re
from pathlib import Path

GENERAL_AGENTS = {
    '01-writings': '著作',
    '02-conversations': '对话',
    '03-expression-dna': '表达',
    '04-external-views': '他者',
    '05-decisions': '决策',
    '06-timeline': '时间线',
}

INVESTOR_AGENTS = {
    '01-primary-sources': '一手来源',
    '02-investment-philosophy': '投资哲学',
    '03-research-system': '研究系统',
    '04-valuation-and-expectations': '估值预期',
    '05-portfolio-and-positioning': '组合仓位',
    '06-trading-and-exit': '交易退出',
    '07-cases-and-decisions': '案例决策',
    '08-failures-and-contradictions': '失败争议',
    '09-expression-dna': '表达DNA',
    '10-timeline-and-regimes': '时间环境',
}

MIGRATED_INVESTOR_AGENTS = {
    **GENERAL_AGENTS,
    '07-v2-evidence-ledger': 'V2证据账本',
    '08-v2-portfolio-and-cases': 'V2仓位案例',
}


def count_sources(content: str) -> dict:
    """统计来源数量和一手/二手占比"""
    # 计算URL数量作为来源数
    urls = re.findall(r'https?://[^\s\)]+', content)

    # 检测一手/二手标记
    primary_markers = len(re.findall(r'一手|primary|本人|原文|原始|直接引用', content, re.IGNORECASE))
    secondary_markers = len(re.findall(r'二手|secondary|转述|总结|评论|分析', content, re.IGNORECASE))

    return {
        'url_count': len(urls),
        'unique_urls': len(set(urls)),
        'primary_markers': primary_markers,
        'secondary_markers': secondary_markers,
    }


def extract_key_findings(content: str, max_items: int = 3) -> list[str]:
    """提取关键发现（取前几个二级标题或加粗项）"""
    # 尝试提取##标题
    headings = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    if headings:
        return headings[:max_items]

    # fallback: 提取加粗项
    bolds = re.findall(r'\*\*(.+?)\*\*', content)
    if bolds:
        return bolds[:max_items]

    # fallback: 取前3个非空行
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    return [l[:50] + '...' if len(l) > 50 else l for l in lines[:max_items]]


def find_contradictions(files: dict[str, str], agents: dict[str, str]) -> list[str]:
    """简单检测跨文件矛盾（同一关键词出现不同判断）"""
    contradictions = []
    # 检测「但是」「然而」「相反」「矛盾」等矛盾标记
    for name, content in files.items():
        matches = re.findall(r'(?:矛盾|相反|但实际上|然而.*?不同|争议).{0,100}', content)
        for m in matches:
            contradictions.append(f"{agents.get(name, name)}: {m[:80]}")
    return contradictions[:5]  # 最多5条


def main():
    if len(sys.argv) < 2:
        print("用法: python3 merge_research.py <skill目录路径>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    research_dir = skill_dir / 'references' / 'research'

    if not research_dir.exists():
        print(f"❌ 目录不存在: {research_dir}")
        sys.exit(1)

    files = {}
    rows = []
    total_sources = 0
    total_primary = 0
    total_secondary = 0
    missing = []

    skill_file = skill_dir / "SKILL.md"
    skill_content = skill_file.read_text(encoding="utf-8") if skill_file.exists() else ""
    investor_mode = any((research_dir / f"{key}.md").exists() for key in INVESTOR_AGENTS)
    migrated_mode = bool(re.search(r'profile:\s*investor-v2', skill_content, re.IGNORECASE))
    if investor_mode:
        agents = INVESTOR_AGENTS
        mode_label = "投资人 V2"
    elif migrated_mode:
        agents = MIGRATED_INVESTOR_AGENTS
        mode_label = "投资人 V2 兼容迁移"
    else:
        agents = GENERAL_AGENTS
        mode_label = "通用人物"

    print(f"研究模式: {mode_label}")

    for key, label in agents.items():
        md_file = research_dir / f"{key}.md"
        if not md_file.exists():
            missing.append(label)
            rows.append(f"│ {label:<12} │ {'❌ 缺失':<8} │ {'—':<24} │")
            continue

        content = md_file.read_text(encoding='utf-8')
        files[key] = content
        stats = count_sources(content)
        findings = extract_key_findings(content)

        total_sources += stats['unique_urls']
        total_primary += stats['primary_markers']
        total_secondary += stats['secondary_markers']

        findings_str = ', '.join(findings) if findings else '—'
        if len(findings_str) > 40:
            findings_str = findings_str[:37] + '...'

        rows.append(f"│ {label:<12} │ {stats['unique_urls']:<8} │ {findings_str:<24} │")

    # 矛盾检测
    contradictions = find_contradictions(files, agents)

    # 输出
    print("┌──────────────┬──────────┬──────────────────────────┐")
    print("│ Agent        │ 来源数量  │ 关键发现                  │")
    print("├──────────────┼──────────┼──────────────────────────┤")
    for row in rows:
        print(row)
    print("├──────────────┼──────────┼──────────────────────────┤")

    primary_ratio = f"{total_primary}/{total_primary + total_secondary}" if (total_primary + total_secondary) > 0 else "未标记"
    print(f"│ 总来源数      │ {total_sources:<8} │ 一手占比: {primary_ratio:<15} │")

    if contradictions:
        print(f"│ 矛盾点        │ {len(contradictions)}处      │ {contradictions[0][:24]:<24} │")
    else:
        print(f"│ 矛盾点        │ 0处      │ {'—':<24} │")

    if missing:
        print(f"│ 信息不足维度   │ {len(missing)}个      │ {', '.join(missing):<24} │")
    else:
        print(f"│ 信息不足维度   │ 无       │ {'—':<24} │")

    print("└──────────────┴──────────┴──────────────────────────┘")

    # 总结
    if total_sources < 10:
        print("\n⚠️ 总来源数 <10，建议降低期望或补充调研")
    if (investor_mode or migrated_mode) and total_sources < 15:
        print("\n⚠️ 投资人 V2 建议至少15个独立来源")
    if missing:
        print(f"\n⚠️ 缺失维度: {', '.join(missing)}，建议补充或在诚实边界中标注")


if __name__ == '__main__':
    main()
