# -*- coding: utf-8 -*-
"""
根据解析后的字段数据生成 MySQL 建表 SQL。

用法:
    python generate_sql.py <domain> <bill_no> <business_name> <fields_json_path>

参数:
    domain          领域前缀，例如 fam
    bill_no         单据编号，例如 1735
    business_name   业务名称，例如 固定资产销售
    fields_json_path  parse_excel.py 输出的 JSON 文件路径

输出: 写入 output/<bill_no>.<business_name>.sql
"""

import sys
import json
import os
from datetime import date

# ── 标准模板字段（不可修改、不可删除）────────────────────────────────────────

HEAD_STANDARD_FIELDS = """\
    `id` bigint NOT NULL COMMENT 'ID',
    `instance_id` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '实例ID',
    `bill_code` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '单据编号',
    `bill_type` varchar(10) COLLATE utf8mb4_general_ci NOT NULL COMMENT '单据类型，默认CBHA',
    `bill_status` tinyint NOT NULL DEFAULT '0' COMMENT '单据状态，-1-审批不通过；0-草稿；1-审批中；2-审批通过；3-撤回',
    `bill_date` datetime DEFAULT NULL COMMENT '制单时间',
    `rel_bill_id` bigint DEFAULT NULL COMMENT '关联单据ID',
    `rel_bill_type` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '关联单据类型',
    `rel_bill_code` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '关联单据编码',
    `bill_dept_id` bigint DEFAULT NULL COMMENT '制单（业务）部门ID',
    `bill_dept_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '制单（业务）部门名称',
    `print_num` int DEFAULT NULL COMMENT '打印次数',
    `audit_user_id` bigint DEFAULT NULL COMMENT '审核人id，来源sys_user.user_id',
    `audit_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人名称',
    `audit_date` datetime DEFAULT NULL COMMENT '审批时间',
    `flow_key` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '流程key',
    `dept_id` bigint DEFAULT NULL COMMENT '创建部门id,来源：sys_dept.dept_id',
    `create_user_id` bigint DEFAULT NULL COMMENT '创建人,来源：sys_user.user_id',
    `create_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人姓名.来源：sys_suer.nick_name',
    `create_date` datetime DEFAULT NULL COMMENT '创建时间',
    `initiate_user_id` bigint DEFAULT NULL COMMENT '发起人ID(制单人ID)',
    `initiate_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发起人姓名（制单人姓名）',
    `initiate_dept_id` bigint DEFAULT NULL COMMENT '发起人部门Id(承办部门Id)',
    `initiate_dept_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发起人部门名称(承办部门名称)',
    `initiate_project_id` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '承包项目id',
    `initiate_project_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '承包项目名称',
    `bill_display_date` datetime DEFAULT NULL COMMENT '呈文日期',
    `update_user_id` bigint DEFAULT NULL COMMENT '最后编辑人,来源：sys_user.user_id',
    `update_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '最后编辑人姓名.来源：sys_suer.nick_name',
    `update_date` datetime DEFAULT NULL COMMENT '编辑时间',
    `is_deleted` tinyint DEFAULT '0' COMMENT '是否删除：0否1是',
    `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间戳',
    `gmt_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间戳',
    PRIMARY KEY (`id`)"""

DETAIL_STANDARD_FIELDS = """\
    `id` bigint NOT NULL COMMENT 'ID',
    `head_id` bigint NOT NULL COMMENT '主单ID',
    `project_id` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目id',
    `FXMBH` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目编号',
    `FXMMC` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目名称',
    `FZTMCID` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账套编号',
    `FZTMC` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账套名称',
    `FXMLX` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目类型',
    `fcontract_type` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '合同类型',
    `FSSZZID` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属组织编号',
    `FSSZZ` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属组织',
    `project_properties` tinyint DEFAULT NULL COMMENT '项目属性',"""

TAIL_FIELDS = """\
    `is_deleted` tinyint DEFAULT '0' COMMENT '是否删除：0否1是',
    `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间戳',
    `gmt_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间戳',
    PRIMARY KEY (`id`)"""

# HEAD 表中已有的标准字段名集合（business 字段不应重复添加到 detail/info）
HEAD_STANDARD_FIELD_NAMES = {
    "id", "instance_id", "bill_code", "bill_type", "bill_status", "bill_date",
    "rel_bill_id", "rel_bill_type", "rel_bill_code", "bill_dept_id", "bill_dept_name",
    "print_num", "audit_user_id", "audit_user_name", "audit_date", "flow_key",
    "dept_id", "create_user_id", "create_user_name", "create_date",
    "initiate_user_id", "initiate_user_name", "initiate_dept_id", "initiate_dept_name",
    "initiate_project_id", "initiate_project_name", "bill_display_date",
    "update_user_id", "update_user_name", "update_date",
    "is_deleted", "gmt_create", "gmt_modified",
}

DETAIL_STANDARD_FIELD_NAMES = HEAD_STANDARD_FIELD_NAMES | {
    "head_id", "project_id", "fxmbh", "fxmmc", "fztmcid", "fztmc",
    "fxmlx", "fcontract_type", "fsszzid", "fsszz", "project_properties",
    # 语义别名：detail 标准字段覆盖的中文含义对应的常见外部字段名（小写）
    "fgsmcid", "fgsmc",   # 所属组织编号/所属组织（与 FSSZZID/FSSZZ 同义）
}

# detail 标准字段覆盖的中文语义标签集合，用于按 field_label 去重
DETAIL_STANDARD_LABELS = {
    "项目id", "项目编号", "项目名称", "账套编号", "账套名称",
    "项目类型", "合同类型", "所属组织编号", "所属组织", "项目属性",
}


# ── 辅助函数 ─────────────────────────────────────────────────────────────────

def build_field_line(f: dict, indent: int = 4) -> str:
    """将一个字段 dict 转换为 SQL 字段行。"""
    name = f["field_name"]
    ftype = f["field_type"]
    required = f.get("required", False)
    label = f.get("field_label", "") or name
    enum_values = f.get("enum_values", "")

    # comment：中文名 + 枚举值（若有）
    comment = label
    if enum_values and str(enum_values).strip():
        comment = f"{label}，{str(enum_values).strip()}"

    # 清理注释中的换行符和单引号
    comment = comment.replace("\n", " ").replace("\r", " ")
    comment = comment.replace("'", "\\'")

    null_clause = "NOT NULL" if required else "DEFAULT NULL"
    pad = " " * indent
    return f"{pad}`{name}` {ftype} {null_clause} COMMENT '{comment}',"


def filter_business_fields(fields: list, exclude_set: set, exclude_labels: set = None) -> list:
    """
    过滤掉标准模板中已存在的字段：
    1. 字段名（小写）命中 exclude_set → 跳过
    2. field_label 命中 exclude_labels（语义去重）→ 跳过
    3. 剩余字段中重复字段名自动加数字后缀
    """
    if exclude_labels is None:
        exclude_labels = set()
    seen_names = set()
    result = []
    for f in fields:
        if f["field_name"].lower() in {n.lower() for n in exclude_set}:
            continue
        label = (f.get("field_label") or "").strip()
        if label and label in exclude_labels:
            continue
        # 重复字段名加后缀
        unique_name = f["field_name"]
        if unique_name.lower() in seen_names:
            suffix = 2
            while f"{unique_name}_{suffix}".lower() in seen_names:
                suffix += 1
            unique_name = f"{unique_name}_{suffix}"
        seen_names.add(unique_name.lower())
        result.append({**f, "field_name": unique_name})
    return result


# ── SQL 生成 ──────────────────────────────────────────────────────────────────

def gen_head(domain, bill_no, business_name) -> str:
    table = f"`{domain}_bill_{bill_no}_head`"
    return f"""\
-- ----------------------------
-- Table structure for {domain}_bill_{bill_no}_head
-- ----------------------------
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
{HEAD_STANDARD_FIELDS}
) ENGINE=InnoDB  COMMENT='{business_name}';
"""


def gen_detail(domain, bill_no, business_name, fields: list) -> str:
    table_base = f"{domain}_bill_{bill_no}_detail"
    table = f"`{table_base}`"

    biz_fields = filter_business_fields(fields, DETAIL_STANDARD_FIELD_NAMES, DETAIL_STANDARD_LABELS)
    biz_lines = "\n".join(build_field_line(f) for f in biz_fields)
    biz_section = f"\n{biz_lines}\n" if biz_lines else "\n"

    return f"""\
-- ----------------------------
-- Table structure for {domain}_bill_{bill_no}_detail
-- ----------------------------
DROP TABLE IF EXISTS {table};
CREATE TABLE {table} (
{DETAIL_STANDARD_FIELDS}
{biz_section}{TAIL_FIELDS}
) ENGINE=InnoDB  COMMENT='{business_name}单据详情';

-- ----------------------------
-- Indexes for {table_base}
-- ----------------------------
CREATE INDEX index_head_id ON {table_base} (head_id);
"""


def gen_info(domain, bill_no, business_name, section_label: str, fields: list) -> str:
    """
    生成一张 info 表。section_label 是"明细表#XXX"中的 XXX 部分。
    """
    # 将 section_label 简化为表名后缀（去掉特殊字符）
    import re
    suffix_raw = re.sub(r"[^\w一-鿿]", "_", section_label)
    table_base = f"{domain}_bill_{bill_no}_info"
    table = f"`{table_base}`"

    biz_fields = filter_business_fields(fields, HEAD_STANDARD_FIELD_NAMES | {"head_id"})
    biz_lines = "\n".join(build_field_line(f) for f in biz_fields)
    biz_section = f"\n{biz_lines}\n" if biz_lines else "\n"

    comment = f"{business_name}{section_label}" if section_label else f"{business_name}单据明细信息"

    return f"""\
-- ================================================================================
-- Info表 - {section_label or '明细'}
-- ================================================================================
DROP TABLE IF EXISTS {table_base};
CREATE TABLE {table} (
    `id` bigint NOT NULL COMMENT 'ID',
    `head_id` bigint NOT NULL COMMENT '主单ID',
{biz_section}{TAIL_FIELDS}
) ENGINE=InnoDB  COMMENT='{comment}';

CREATE INDEX index_head_id ON {table_base} (head_id);
"""


def generate_sql(domain: str, bill_no: str, business_name: str, fields: list) -> str:
    """主生成函数，返回完整 SQL 字符串。"""

    # 按 table_type 分组
    head_fields = [f for f in fields if f["table_type"] == "主表"]
    detail_fields = [f for f in fields if f["table_type"] == "明细表"]
    # 收集所有 info 分区（明细表#xxx）
    info_sections: dict[str, list] = {}
    for f in fields:
        tt = f["table_type"]
        if tt.startswith("明细表#"):
            label = tt[len("明细表#"):]
            info_sections.setdefault(label, []).append(f)

    today = date.today().strftime("%Y-%m-%d")
    parts = [
        f"""\
-- =====================================================
-- {business_name} - 单据表结构设计
-- 领域: {domain}
-- 编号: {bill_no}
-- 模块: {business_name}
-- 创建时间: {today}
-- =====================================================
""",
        gen_head(domain, bill_no, business_name),
        gen_detail(domain, bill_no, business_name, detail_fields),
    ]

    for label, info_fields in info_sections.items():
        parts.append(gen_info(domain, bill_no, business_name, label, info_fields))

    return "\n".join(parts)


# ── 主入口 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python generate_sql.py <domain> <bill_no> <business_name> <fields_json_path>",
            file=sys.stderr,
        )
        sys.exit(1)

    domain = sys.argv[1]
    bill_no = sys.argv[2]
    business_name = sys.argv[3]
    json_path = sys.argv[4]

    with open(json_path, "r", encoding="utf-8") as fh:
        fields = json.load(fh)

    sql = generate_sql(domain, bill_no, business_name, fields)

    # 输出到 output 目录
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, f"{bill_no}.{business_name}.sql")

    with open(out_file, "w", encoding="utf-8") as fh:
        fh.write(sql)

    print(f"[OK] SQL 已生成: {out_file}")
