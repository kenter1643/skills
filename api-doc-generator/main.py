# -*- coding: utf-8 -*-
"""
API 接口文档生成器 - 主程序入口
"""

import argparse
import os
import sys

# 添加父目录到路径，以便导入 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from parsers.parse_sql import parse_sql, extract_table_info
from parsers.parse_excel import parse_excel
from merger.merge_fields import merge_fields
from generator.generate_doc import generate_doc, save_doc
import utils


def extract_business_name(filename):
    """
    从文件名提取业务名称

    例如：固定资产入库.xlsx → 固定资产入库
          03.固定资产入库.sql → 固定资产入库
    """
    business_name, _ = utils.extract_filename_info(filename)
    return business_name


def main():
    parser = argparse.ArgumentParser(description='API 接口文档生成器')
    parser.add_argument('sql_file', help='SQL 文件路径')
    parser.add_argument('excel_file', help='Excel 文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录（默认：output）')
    args = parser.parse_args()

    # 检查文件是否存在
    if not utils.validate_file_path(args.sql_file):
        print(f"[错误] SQL 文件不存在: {args.sql_file}")
        sys.exit(1)
    if not utils.validate_file_path(args.excel_file):
        print(f"[错误] Excel 文件不存在: {args.excel_file}")
        sys.exit(1)

    # 配置
    Config.INPUT_SQL_PATH = args.sql_file
    Config.INPUT_EXCEL_PATH = args.excel_file
    Config.OUTPUT_DIR = args.output

    # 提取业务信息（优先使用 Excel 文件名）
    excel_filename = os.path.basename(args.excel_file)
    Config.BUSINESS_NAME = extract_business_name(excel_filename)

    # # 提取单据编号（从 SQL 建表语句中提取）
    # Config.BILL_CODE = extract_bill_code_from_sql(args.sql_file)

    print(f"[配置] 业务名称: {Config.BUSINESS_NAME}")
    print(f"[配置] 单据编号: {Config.BILL_CODE}")
    print(f"[配置] 输出目录: {Config.OUTPUT_DIR}")

    # 1. 先从 SQL 中提取表信息（获取 API 前缀和单据编号）
    print(f"\n[1/5] 从 SQL 提取表信息: {args.sql_file}")
    try:
        from parsers.parse_sql import extract_table_info
        table_info = extract_table_info(Config.INPUT_SQL_PATH)
        if table_info:
            Config.API_PREFIX = table_info['api_prefix']
            Config.BILL_CODE = table_info['bill_code']
            print(f"      [OK] API 前缀: {Config.API_PREFIX}")
            print(f"      [OK] 单据编号: {Config.BILL_CODE}")
        else:
            print(f"      [WARNING] 未能从表名提取信息，使用默认值")
            Config.API_PREFIX = '/api/bill'
            Config.BILL_CODE = '01'
    except Exception as e:
        print(f"      [WARNING] 表信息提取失败: {e}")
        Config.API_PREFIX = '/api/bill'
        Config.BILL_CODE = '01'

    # 2. 解析 SQL 字段（仅解析 head 和 detail 表）
    print(f"\n[2/5] 解析 SQL 字段: {args.sql_file}")
    try:
        from parsers.parse_sql import parse_sql_head_detail
        sql_fields = parse_sql_head_detail(Config.INPUT_SQL_PATH)
        print(f"      [OK] 解析到 {len(sql_fields)} 个字段")
    except Exception as e:
        print(f"      [ERROR] SQL 解析失败: {e}")
        sys.exit(1)

    # 3. 解析 Excel（仅从字段说明sheet获取）
    print(f"[3/5] 解析 Excel 文件: {args.excel_file}")
    try:
        excel_data = parse_excel(Config.INPUT_EXCEL_PATH)
        print(f"      [OK] 模糊查询: {len(excel_data['fuzzy_search'])} 个")
        print(f"      [OK] 高级查询: {len(excel_data['advanced_search'])} 个")
        print(f"      [OK] 列表字段: {len(excel_data['list_fields'])} 个")
        print(f"      [OK] 字段说明: {len(excel_data['field_info'])} 个")
    except Exception as e:
        print(f"      [ERROR] Excel 解析失败: {e}")
        sys.exit(1)

    # 4. 合并字段
    print(f"[4/5] 合并字段...")
    try:
        merged_result = merge_fields(sql_fields, excel_data, sql_path=Config.INPUT_SQL_PATH)
        print(f"      [OK] 合并后字段数: {len(merged_result['fields'])} 个")
        print(f"      [OK] infoList 数量: {len(merged_result.get('info_lists', []))} 个")
        print(f"      [OK] 抽屉数量: {len(merged_result.get('drawers', []))} 个")
    except Exception as e:
        print(f"      [ERROR] 字段合并失败: {e}")
        sys.exit(1)

    # 5. 生成文档
    print(f"[5/5] 生成文档...")
    try:
        doc_content = generate_doc(merged_result, Config)
        output_path = save_doc(doc_content, Config)
        print(f"      [OK] 文档已生成: {output_path}")
    except Exception as e:
        print(f"      [ERROR] 文档生成失败: {e}")
        sys.exit(1)

    print(f"\n[OK] 完成！")


if __name__ == '__main__':
    main()
