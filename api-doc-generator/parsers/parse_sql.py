# -*- coding: utf-8 -*-
"""
SQL 解析器
解析 SQL 文件，提取字段信息并转换为 Java 类型
"""

import re
import sys
import os

_skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _skill_root not in sys.path:
    sys.path.insert(0, _skill_root)

from config import Config
import utils


def to_camel_case(s):
    """下划线转驼峰，全部转为小写"""
    s_lower = s.lower()
    parts = s_lower.split('_')
    if len(parts) == 1:
        return parts[0]
    return parts[0] + ''.join(p.title() for p in parts[1:])


def map_sql_type(sql_type):
    """
    映射 SQL 类型到 Java 类型

    Args:
        sql_type: SQL 类型字符串，如 'varchar(30)', 'decimal(10,2)'

    Returns:
        Java 类型，如 'String', 'BigDecimal'
    """
    base_type = re.sub(r'\([^)]*\)', '', sql_type.lower().strip())
    return Config.SQL_TYPE_MAPPING.get(base_type, 'String')


def clean_sql_comment(full_comment):
    """清洗 SQL 注释中的字段 key 后缀"""
    comment_clean = re.sub(r'[\[\(][A-Za-z_][A-Za-z0-9_]*[\]\)]\s*$', '', full_comment).strip()
    return comment_clean or full_comment


def build_sql_field_info(db_field, sql_type, full_comment):
    """构建统一的 SQL 字段信息结构"""
    comment_clean = clean_sql_comment(full_comment.strip())
    return {
        'db_field': db_field,
        'name': to_camel_case(db_field),
        'java_type': map_sql_type(sql_type),
        'comment': comment_clean,
    }


def parse_sql_file(sql_path):
    """
    解析 SQL 文件，提取所有字段信息

    Args:
        sql_path: SQL 文件路径

    Returns:
        dict: 字段字典 {中文注释: 字段信息}
    """
    fields = {}

    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'`(\w+)`\s+(\S+)\s*(.*?)\s*COMMENT\s*\'([^\']*)\''
    matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
    for match in matches:
        db_field = match.group(1)
        sql_type = match.group(2)
        full_comment = match.group(4).strip()
        field_info = build_sql_field_info(db_field, sql_type, full_comment)
        fields[field_info['comment']] = field_info

    return fields


def get_table_suffix(table_name):
    """获取表后缀类型，供优先级判断使用"""
    table_name = table_name.lower()
    if table_name.endswith('_info'):
        return 'info'
    if table_name.endswith('_detail'):
        return 'detail'
    if table_name.endswith('_head'):
        return 'head'
    if re.match(r'_re_\d+$', table_name):
        return 're'
    return 'other'


def get_info_list_name(table_name):
    """
    获取 infoList 的命名
    - _info 结尾 -> infoList
    - _re_数字 结尾 -> re数字List
    - 其他非 head/detail 的表 -> 根据后缀自动生成
    """
    table_name_lower = table_name.lower()
    if table_name_lower.endswith('_info'):
        return 'infoList'
    re_match = re.match(r'.*_re_(\d+)$', table_name_lower)
    if re_match:
        return f're{re_match.group(1)}List'
    parts = table_name_lower.rsplit('_', 1)
    if len(parts) >= 2:
        return f'{parts[-1]}List'
    return 'infoList'


def is_head_or_detail_table(table_name):
    """判断是否为 head 或 detail 表"""
    table_name_lower = table_name.lower()
    return table_name_lower.endswith('_head') or table_name_lower.endswith('_detail')


def get_table_priority(table_name):
    """表优先级：info > detail > head > other"""
    suffix = get_table_suffix(table_name)
    priority_map = {
        'info': 0,
        'detail': 1,
        'head': 2,
        'other': 3,
    }
    return priority_map.get(suffix, 99)


def parse_sql_tables(sql_path):
    """按表解析 SQL，保留每张表的字段结构"""
    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()

    tables = []
    # 匹配表定义和表注释
    table_pattern = r'CREATE\s+TABLE\s+`?(\w+)`?\s*\((.*?)\)\s*ENGINE=[^;]*?COMMENT\s*=\s*\'([^\']*)\''
    field_pattern = r'`(\w+)`\s+(\S+)\s*(.*?)\s*COMMENT\s*\'([^\']*)\''

    for table_match in re.finditer(table_pattern, content, re.IGNORECASE | re.DOTALL):
        table_name = table_match.group(1)
        table_body = table_match.group(2)
        table_comment = table_match.group(3).strip()
        fields_by_comment = {}
        fields_by_name = {}

        for field_match in re.finditer(field_pattern, table_body, re.IGNORECASE | re.MULTILINE):
            db_field = field_match.group(1)
            sql_type = field_match.group(2)
            full_comment = field_match.group(4).strip()
            field_info = build_sql_field_info(db_field, sql_type, full_comment)
            fields_by_comment[field_info['comment']] = field_info
            fields_by_name[field_info['name']] = field_info

        tables.append({
            'table_name': table_name,
            'table_comment': table_comment,
            'table_suffix': get_table_suffix(table_name),
            'info_list_name': get_info_list_name(table_name),
            'is_head_or_detail': is_head_or_detail_table(table_name),
            'fields_by_comment': fields_by_comment,
            'fields_by_name': fields_by_name,
        })

    return tables


def extract_table_info(sql_path):
    """
    从 SQL 文件中提取表名信息，获取 API 前缀和单据编号

    Args:
        sql_path: SQL 文件路径

    Returns:
        dict: 包含 api_prefix 和 bill_code 的字典
    """
    with open(sql_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'CREATE\s+TABLE\s+`?(\w+)`?'
    match = re.search(pattern, content, re.IGNORECASE)

    if not match:
        return None

    table_name = match.group(1)
    module_prefix = None
    bill_code = None
    if '_' in table_name:
        parts = table_name.split('_')
        if len(parts) >= 3:
            module_prefix = '/' + '/'.join(parts[:2]) + '/'
            bill_code = parts[2]
        else:
            raise ValueError("字符串格式不符合预期")
    return {
        'api_prefix': module_prefix,
        'bill_code': bill_code
    }


def parse_sql(sql_path):
    """解析 SQL 文件（对外接口）"""
    return parse_sql_file(sql_path)


def parse_sql_head_detail(sql_path):
    """
    只解析 head 和 detail 表的字段，用于与 Excel 合并
    infoList 表的字段不参与合并，但会通过 build_info_lists 生成
    """
    tables = parse_sql_tables(sql_path)
    fields = {}
    for table in tables:
        if not table.get('is_head_or_detail'):
            continue
        for comment, field_info in table['fields_by_comment'].items():
            fields[comment] = field_info
    return fields


if __name__ == '__main__':
    sql_path = r'D:\ZY\code\api-doc-generator\output\固资报损_智云.sql'
    fields = parse_sql(sql_path)
    print(f"解析到 {len(fields)} 个字段")
    for comment, info in list(fields.items())[:]:
        print(f"{comment}: {info['name']} ({info['java_type']})")
