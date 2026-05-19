# -*- coding: utf-8 -*-
"""
API 接口文档生成器 - 配置模块
"""

import os


class Config:
    # 获取项目根目录（skill目录向上4层：.claude/skills/api-doc-generator/config.py → 项目根）
    PROJECT_ROOT = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    # 文件路径
    INPUT_SQL_PATH = None  # SQL 文件路径
    INPUT_EXCEL_PATH = None  # Excel 文件路径
    OUTPUT_DIR = os.path.join(
        PROJECT_ROOT, "mdfile"
    )  # 默认输出到项目根目录下的 mdfile 文件夹

    # 业务信息（自动提取）
    BUSINESS_NAME = None  # 业务功能名称，从文件名提取
    BILL_CODE = None  # 单据编号，从文件名或 Sheet 名称提取
    API_PREFIX = None  # API 前缀，从 SQL 表名提取

    # SQL 类型映射到 Java 类型
    SQL_TYPE_MAPPING = {
        "varchar": "String",
        "char": "String",
        "text": "String",
        "int": "Integer",
        "tinyint": "Integer",
        "smallint": "Integer",
        "bigint": "Long",
        "decimal": "BigDecimal",
        "numeric": "BigDecimal",
        "double": "Double",
        "float": "Float",
        "datetime": "Date",
        "date": "Date",
        "timestamp": "Date",
        "boolean": "Boolean",
        "bit": "Boolean",
    }

    # 需要 XxxStr 的类型
    NEED_STR_TYPES = {"Date", "Integer", "BigDecimal"}

    # Excel 显示类型映射到 Java 类型（兜底用）
    EXCEL_DISPLAY_TYPE_MAPPING = {
        "文本型": "String",
        "数值型": "BigDecimal",
        "日期型": "Date",
        "附件型": "List<BaseFile>",
        "": "String",
    }
