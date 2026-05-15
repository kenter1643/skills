# -*- coding: utf-8 -*-
"""
扫描历史 SQL 文件，分析目标 SQL 中 detail/info 表业务字段是否与历史表存在关联。

用法:
    python check_history.py <target_sql_path> [history_dir]

参数:
    target_sql_path  生成的目标 SQL 文件路径（如 output/2809.合同内施工图预算变更.sql）
    history_dir      历史 SQL 目录，默认为 database/V1.0相关版本/0-已发版

输出: 关联分析报告到 stdout
"""

import sys
import os
import re
import glob


# ── 历史表字段名对齐规则 ───────────────────────────────────────────────────────
# key: 当前生成的字段名, value: 历史统一字段名
FIELD_NAME_ALIGN = {
    "paper_contract_no": "paper_contract_number",
    "line_no": "row_no",
}

# 历史表中已知的关联 id 字段（字段名 → id字段定义）
# 当 comment 匹配到这些关键词时，自动推断需要添加的 _id 字段
KNOWN_ID_FIELDS = {
    "承包合同编号": ("contract_id", "bigint DEFAULT NULL", "承包合同id，来源：cms_contact_base.id"),
}


def parse_target_fields(sql_content: str) -> dict[str, list[dict]]:
    """
    从目标 SQL 中提取 detail/info 表的业务字段。
    返回 { "detail": [...], "info": [...] }，每项含 field_name, comment, full_line。
    跳过标准字段（id、head_id、project_id、FXMBH 等）和尾部字段。
    """
    STANDARD_SKIP = {
        "id", "head_id", "project_id", "fxmbh", "fxmmc", "fztmcid", "fztmc",
        "fxmlx", "fcontract_type", "fsszzid", "fsszz", "project_properties",
        "is_deleted", "gmt_create", "gmt_modified",
    }

    result = {"detail": [], "info": []}
    current_table = None

    for line in sql_content.splitlines():
        # 检测当前表类型
        if re.search(r"CREATE TABLE.*_detail", line, re.IGNORECASE):
            current_table = "detail"
            continue
        if re.search(r"CREATE TABLE.*_info", line, re.IGNORECASE):
            current_table = "info"
            continue
        if re.match(r"\s*\)\s*ENGINE", line):
            current_table = None
            continue

        if current_table not in ("detail", "info"):
            continue

        # 解析字段行：`field_name` type ... COMMENT 'xxx'
        m = re.match(r"\s+`(\w+)`\s+\S+.*?COMMENT\s+'([^']*)'", line)
        if not m:
            continue

        field_name = m.group(1)
        comment = m.group(2)

        if field_name.lower() in STANDARD_SKIP:
            continue

        result[current_table].append({
            "field_name": field_name,
            "comment": comment,
            "full_line": line.rstrip(",").strip(),
        })

    return result


def load_history_comments(history_dir: str) -> list[dict]:
    """
    读取历史目录下所有 .sql 文件，提取每个字段行的 comment 和字段名。
    返回列表，每项含 file, table_name, field_name, comment, id_field（若存在配对 id）。
    """
    pattern = os.path.join(history_dir, "**", "*.sql")
    sql_files = glob.glob(pattern, recursive=True)

    records = []
    for fpath in sql_files:
        try:
            with open(fpath, encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            continue

        current_table = None
        lines = content.splitlines()
        for i, line in enumerate(lines):
            # 检测表名
            tm = re.search(r"(?:CREATE TABLE|ALTER TABLE)\s+`?(\w+)`?", line, re.IGNORECASE)
            if tm:
                current_table = tm.group(1)

            # 解析字段行
            fm = re.match(r"\s+`?(\w+)`?\s+\S+.*?[Cc][Oo][Mm][Mm][Ee][Nn][Tt]\s+'([^']*)'", line)
            if not fm or not current_table:
                continue

            field_name = fm.group(1)
            comment = fm.group(2)

            # 找同表中紧邻的 _id 配对字段（向前扫描5行）
            id_field = None
            for j in range(max(0, i - 5), i):
                im = re.match(r"\s+`?(\w+)`?\s+bigint.*?[Cc][Oo][Mm][Mm][Ee][Nn][Tt]\s+'([^']*)'", lines[j])
                if im and im.group(1).endswith("_id"):
                    id_field = (im.group(1), im.group(2))
                    break

            records.append({
                "file": os.path.relpath(fpath, history_dir),
                "table": current_table,
                "field_name": field_name,
                "comment": comment,
                "id_field": id_field,
            })

    return records


def match_fields(target_fields: list[dict], history_records: list[dict]) -> list[dict]:
    """
    对目标字段列表，在历史记录中按 comment 做精确子串匹配。
    返回匹配到的结果列表。
    """
    matches = []
    for tf in target_fields:
        label = tf["comment"].split("，")[0].strip()  # 取逗号前的中文名
        if not label:
            continue

        # 在历史记录中搜索
        found = {}
        for hr in history_records:
            if label in hr["comment"]:
                key = hr["field_name"]
                if key not in found:
                    found[key] = hr

        if found:
            matches.append({
                "target": tf,
                "history_matches": list(found.values()),
            })

    return matches


def build_report(target_fields_by_table: dict, history_records: list[dict]) -> str:
    """生成关联分析报告文本。"""
    lines = []
    has_any = False

    suggest_add = []     # 需要添加关联 id 字段
    suggest_rename = []  # 需要字段名对齐

    for table_type in ("detail", "info"):
        fields = target_fields_by_table.get(table_type, [])
        if not fields:
            continue

        matches = match_fields(fields, history_records)
        if not matches:
            continue

        has_any = True
        lines.append(f"\n{'Detail' if table_type == 'detail' else 'Info'} 表：")

        for m in matches:
            tf = m["target"]
            label = tf["comment"].split("，")[0].strip()
            fn = tf["field_name"]

            # 检查是否需要添加关联 id
            if label in KNOWN_ID_FIELDS:
                id_name, id_type, id_comment = KNOWN_ID_FIELDS[label]
                suggest_add.append({
                    "table": table_type,
                    "before_field": fn,
                    "id_field": f"`{id_name}` {id_type} COMMENT '{id_comment}'",
                    "label": label,
                    "field_name": fn,
                })
                lines.append(f"  ✓ {label}（{fn}）")
                lines.append(f"    → 建议在其前添加：`{id_name}` {id_type} COMMENT '{id_comment}'")
            else:
                # 仅展示历史匹配，无 id 关联
                sample = m["history_matches"][0]
                lines.append(f"  ✓ {label}（{fn}）")
                lines.append(f"    → 历史表 {sample['table']} 中存在同义字段 `{sample['field_name']}`")

            # 检查字段名是否需要对齐
            if fn in FIELD_NAME_ALIGN:
                new_name = FIELD_NAME_ALIGN[fn]
                suggest_rename.append({
                    "table": table_type,
                    "old_name": fn,
                    "new_name": new_name,
                    "label": label,
                })
                lines.append(f"    → 字段名建议对齐历史：`{fn}` → `{new_name}`")

    if not has_any:
        return "[历史关联分析] 未找到与历史表存在关联的字段，无需处理。\n"

    report = "[历史关联分析] 以下字段在历史表中存在关联，建议添加或对齐：\n"
    report += "\n".join(lines)
    report += '\n\n请确认是否执行以上所有建议？（回复"是"/"全部"执行全部，或指定编号）\n'
    return report, suggest_add, suggest_rename


def apply_suggestions(sql_path: str, suggest_add: list, suggest_rename: list):
    """将建议的修改写入 SQL 文件。"""
    with open(sql_path, encoding="utf-8") as f:
        content = f.read()

    # 1. 插入关联 id 字段（在 before_field 所在行前插入）
    for s in suggest_add:
        pattern = rf"(\s+`{re.escape(s['before_field'])}`\s)"
        replacement = f"    {s['id_field']},\n\\1"
        content = re.sub(pattern, replacement, content, count=1)

    # 2. 字段名对齐
    for s in suggest_rename:
        content = content.replace(f"`{s['old_name']}`", f"`{s['new_name']}`")

    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] SQL 文件已更新：{sql_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python check_history.py <target_sql_path> [history_dir]", file=sys.stderr)
        sys.exit(1)

    sql_path = sys.argv[1]
    # 默认历史目录：相对于项目根（脚本在 skills/create-sql-generator/scripts/）
    default_history = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "database", "V1.0相关版本", "0-已发版")
    )
    history_dir = sys.argv[2] if len(sys.argv) >= 3 else default_history

    if not os.path.isfile(sql_path):
        print(f"[ERROR] 目标 SQL 文件不存在：{sql_path}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isdir(history_dir):
        print(f"[ERROR] 历史 SQL 目录不存在：{history_dir}", file=sys.stderr)
        sys.exit(1)

    with open(sql_path, encoding="utf-8") as f:
        sql_content = f.read()

    print(f"[INFO] 解析目标 SQL：{sql_path}", file=sys.stderr)
    target_fields = parse_target_fields(sql_content)
    detail_cnt = len(target_fields["detail"])
    info_cnt = len(target_fields["info"])
    print(f"[INFO] 业务字段：detail={detail_cnt}，info={info_cnt}", file=sys.stderr)

    print(f"[INFO] 扫描历史 SQL 目录：{history_dir}", file=sys.stderr)
    history_records = load_history_comments(history_dir)
    print(f"[INFO] 历史字段记录数：{len(history_records)}", file=sys.stderr)

    result = build_report(target_fields, history_records)

    # build_report 在有匹配时返回 tuple，无匹配时返回 str
    if isinstance(result, tuple):
        report, suggest_add, suggest_rename = result
        print(report)

        # 等待用户确认
        answer = input("请输入确认（是/全部/n）：").strip().lower()
        if answer in ("是", "y", "yes", "全部", "all"):
            apply_suggestions(sql_path, suggest_add, suggest_rename)
        else:
            print("[跳过] 未对 SQL 文件做任何修改。")
    else:
        print(result)


if __name__ == "__main__":
    main()
