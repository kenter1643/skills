# -*- coding: utf-8 -*-
"""
字段合并器
将 SQL 字段与 Excel 字段进行映射
"""

import sys
import os
import utils

_skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _skill_root not in sys.path:
    sys.path.insert(0, _skill_root)

from config import Config
from parsers.parse_sql import parse_sql_tables


EXCLUDE_FIELDS = {'is_deleted', 'gmt_create', 'gmt_modified', 'isDeleted', 'gmtCreate', 'gmtModified'}


def build_info_lists(sql_path, excel_data):
    """
    构建 infoList 结构，字段从 SQL 建表语句获取
    - 排除 head、detail 表
    - 排除 is_deleted、gmt_create、gmt_modified 字段
    - 中文括号转为英文括号
    """
    if not sql_path:
        return []

    sql_tables = parse_sql_tables(sql_path)
    if not sql_tables:
        return []

    info_lists = []
    for table in sql_tables:
        if table.get('is_head_or_detail'):
            continue

        fields = []
        seen_names = set()
        for field_name, field_info in table['fields_by_name'].items():
            if field_name.lower() in {f.lower() for f in EXCLUDE_FIELDS}:
                continue
            if field_name in seen_names:
                continue
            seen_names.add(field_name)
            # 中文括号转英文括号
            comment = field_info['comment'].replace('（', '(').replace('）', ')')
            fields.append({
                'name': field_name,
                'java_type': field_info['java_type'],
                'comment': comment,
            })

        if fields:
            info_lists.append({
                'title': table['table_name'],
                'name': table.get('info_list_name', 'infoList'),
                'comment': table.get('table_comment', table['table_name']),
                'fields': fields,
            })

    return info_lists


def merge_fields(sql_fields, excel_data, sql_path=None):
    """
    合并 SQL 字段和 Excel 数据

    Args:
        sql_fields: SQL 解析结果 {中文注释: {name, java_type, comment}}
        excel_data: Excel 解析结果 {fuzzy_search, advanced_search, list_fields, field_info}
        sql_path: SQL 文件路径，用于构建 infoList

    Returns:
        dict: {
            'fields': 合并后的字段 {field_name: {字段信息}},
            'info_lists': [{title, name, comment, fields}],
            'drawers': [],
            'has_attachment': bool,
            'field_order': [field_name, ...],
        }
    """
    merged = {}

    # list_fields 现在是 [(中文名, 顺序), ...]
    list_fields_tuples = excel_data['list_fields']
    list_names = [name for name, _ in list_fields_tuples]
    fuzzy_names = excel_data['fuzzy_search']
    advanced_names = excel_data['advanced_search']

    fuzzy_set = set(fuzzy_names)
    advanced_set = set(advanced_names)
    list_set = set(list_names)

    # 构建列表顺序映射 {中文名: 顺序}
    list_order_map = {}
    for name, order in list_fields_tuples:
        if order is not None:
            list_order_map[name] = order

    excel_candidate_names = []
    for name in list_names + fuzzy_names + advanced_names:
        if name not in excel_candidate_names:
            excel_candidate_names.append(name)

    details_set = set()
    matched_excel_names = set()

    def match_excel_name(sql_comment):
        """用 SQL 注释匹配 Excel 字段名（Excel名是SQL注释的前缀），忽略括号全半角差异"""
        norm_comment = utils.canonicalize_field_name(sql_comment)
        for excel_name in excel_candidate_names:
            norm_excel = utils.canonicalize_field_name(excel_name)
            if (
                norm_comment == norm_excel
                or norm_comment.startswith(norm_excel + '，')
                or norm_comment.startswith(norm_excel + ',')
                or norm_comment.startswith(norm_excel + '（')
                or norm_comment.startswith(norm_excel + '(')
            ):
                return excel_name
        return None

    for comment, sql_info in sql_fields.items():
        field_name = sql_info['name']
        java_type = sql_info['java_type']

        matched_name = match_excel_name(comment)
        display_comment = utils.canonicalize_field_name(matched_name if matched_name else comment)
        if matched_name:
            matched_excel_names.add(display_comment)

        is_list = display_comment in list_set
        is_fuzzy = display_comment in fuzzy_set
        is_advanced = display_comment in advanced_set
        with_str = (field_name != 'isDeleted') and (field_name != 'projectProperties') and (java_type in Config.NEED_STR_TYPES)

        field_info_data = excel_data['field_info'].get(display_comment, {})
        is_enum = field_info_data.get('is_enum', False)
        enum_values = field_info_data.get('enum_values', '')
        is_required = field_info_data.get('is_required', False)
        is_detail_section = field_info_data.get('is_detail_section', False)

        merged[field_name] = {
            'java_type': java_type,
            'comment': display_comment,
            'is_fuzzy': is_fuzzy,
            'is_advanced': is_advanced,
            'is_list': is_list,
            'list_order': list_order_map.get(display_comment),
            'is_enum': is_enum,
            'enum_values': enum_values,
            'with_str': with_str,
            'is_required': is_required,
            'section': 'detail' if is_detail_section else 'main',
            'source': 'sql',
        }

    for excel_name in excel_candidate_names:
        display_comment = utils.canonicalize_field_name(excel_name)
        if display_comment in matched_excel_names:
            continue

        field_info_data = excel_data['field_info'].get(display_comment, {})
        is_enum = field_info_data.get('is_enum', False)
        enum_values = field_info_data.get('enum_values', '')
        is_required = field_info_data.get('is_required', False)
        generated_field_name = utils.build_excel_only_field_name(display_comment)

        merged[generated_field_name] = {
            'java_type': 'String',
            'comment': display_comment,
            'is_fuzzy': display_comment in fuzzy_set,
            'is_advanced': display_comment in advanced_set,
            'is_list': display_comment in list_set,
            'list_order': list_order_map.get(display_comment),
            'is_enum': is_enum,
            'enum_values': enum_values,
            'with_str': False,
            'is_required': is_required,
            'section': 'main',
            'source': 'excel',
        }

    # 构建字段顺序列表
    field_order = []
    seen_comments = set()

    # 1. 按字段说明中的顺序
    for excel_name in excel_data.get('field_order', []):
        display_comment = utils.canonicalize_field_name(excel_name)
        if display_comment in seen_comments:
            continue
        for field_name, field_info in merged.items():
            if field_info['comment'] == display_comment:
                field_order.append(field_name)
                seen_comments.add(display_comment)
                break

    # 2. 剩余未排序的字段（追加到末尾）
    for field_name in merged.keys():
        if field_name not in field_order:
            field_order.append(field_name)

    return {
        'fields': merged,
        'info_lists': build_info_lists(sql_path, excel_data),
        'drawers': [],
        'has_attachment': excel_data.get('has_attachment', False),
        'field_order': field_order,
    }


def get_list_fields(merged_fields):
    """获取列表字段，按 list_order 排序（有顺序的在前，无顺序的在后）"""
    fields_with_order = []
    fields_without_order = []
    for f, info in merged_fields.items():
        if info['is_list']:
            if info.get('list_order') is not None:
                fields_with_order.append((f, info['list_order']))
            else:
                fields_without_order.append(f)
    fields_with_order.sort(key=lambda x: x[1])
    return [f for f, _ in fields_with_order] + fields_without_order


def get_fuzzy_search_fields(merged_fields):
    """获取模糊查询字段"""
    return [f for f, info in merged_fields.items() if info['is_fuzzy']]


def get_advanced_search_fields(merged_fields):
    """获取高级查询字段"""
    return [f for f, info in merged_fields.items() if info['is_advanced']]


def get_enum_fields(merged_fields):
    """获取枚举字段"""
    return [f for f, info in merged_fields.items() if info['is_enum']]


if __name__ == '__main__':
    from parsers.parse_sql import parse_sql
    from parsers.parse_excel import parse_excel

    sql_path = r'D:\ZY\code\api-doc-generator\output\03.固定资产入库.sql'
    excel_path = r'D:\ZY\code\jx\construct-star-server-v1.10.9sp9\product\项目收入科目登记.xlsx'
    business_name = '项目收入科目登记'

    sql_fields = parse_sql(sql_path)
    excel_data = parse_excel(excel_path, business_name)

    merged_result = merge_fields(sql_fields, excel_data, sql_path=sql_path)
    merged = merged_result['fields']

    print(f"合并后字段数: {len(merged)}")
    for name, info in list(merged.items()):
        print(f"{name} ({info['comment']}): 类型={info['java_type']}, 模糊={info['is_fuzzy']}, 高级={info['is_advanced']}, 列表={info['is_list']}, Str={info['with_str']}")
    print(f"infoList 数量: {len(merged_result['info_lists'])}")
