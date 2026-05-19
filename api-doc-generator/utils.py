# -*- coding: utf-8 -*-
"""
工具函数库
提供通用的工具函数，消除代码重复
"""
import re
import os
from typing import Optional, List
import translators as ts
from pypinyin import lazy_pinyin, Style


FIELD_NAME_ALIASES = {
    '所属组织名称': '所属组织',
    '账套': '账套名称',
    '所属账套': '账套名称',
    '账套名': '账套名称',
    '制单日期': '制单时间',
}

EXCEL_ONLY_FIELD_NAME_MAP = {
    '承办项目/部门': 'initiateName',
    '制单人': 'initiateUserName',
}


def normalize_brackets(text: str) -> str:
    if not text:
        return text
    return re.sub(r'[（）]', lambda m: '(' if m.group() == '（' else ')', str(text).strip())


def extract_filename_info(filename: str) -> tuple[str, str]:
    name = os.path.splitext(filename)[0]
    bill_code = "XX"

    numbers = re.findall(r'\d+', name)
    if numbers:
        bill_code = numbers[0]

    if bill_code == "XX":
        if name[:2].isdigit():
            bill_code = name[:2]
            name = name[2:].lstrip('.')
        elif name[:1].isdigit():
            bill_code = name[:1]
            name = name[1:].lstrip('.')

    return name, bill_code


def validate_file_path(file_path: str) -> bool:
    if not file_path:
        return False
    if not os.path.exists(file_path):
        return False
    return True


def normalize_api_path(api_prefix: str, bill_code: str) -> str:
    api_prefix = api_prefix.replace('C:/Program Files/Git/', '')
    api_prefix = api_prefix.replace('C:\\Program Files\\Git\\', '')
    api_prefix = api_prefix.rstrip('/')

    if bill_code == 'XX' or not bill_code:
        return f"{api_prefix}"

    return f"{api_prefix}/{bill_code}"


def detect_file_encoding(file_path: str) -> str:
    try:
        import chardet
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)
            result = chardet.detect(raw_data)
            return result.get('encoding', 'utf-8') or 'utf-8'
    except ImportError:
        return 'utf-8'
    except Exception:
        return 'utf-8'


def safe_read_file(file_path: str, encoding: Optional[str] = None) -> str:
    if not validate_file_path(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if encoding is None:
        encoding = detect_file_encoding(file_path)

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except UnicodeDecodeError:
        for enc in ['utf-8', 'gbk', 'gb2312', 'latin1']:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError(f"无法解码文件: {file_path}")


def get_excel_sheet_names(file_path: str) -> List[str]:
    try:
        import openpyxl
        wb = openpyxl.load_workbook(file_path, data_only=True)
        return wb.sheetnames
    except Exception as e:
        raise RuntimeError(f"读取Excel文件失败: {file_path} - {str(e)}")


def create_output_dir(output_dir: str) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def format_api_path(base_path: str, endpoint: str, method: str = 'GET') -> str:
    base_path = base_path.replace('//', '/')
    if base_path.endswith('/'):
        base_path = base_path[:-1]
    full_path = f"{base_path}/{endpoint}"
    return f"{method} {full_path}"


def is_valid_api_prefix(api_prefix: str) -> bool:
    if not api_prefix:
        return False
    if not api_prefix.startswith('/'):
        return False
    if ' ' in api_prefix:
        return False
    return True


def get_filed_sub_date(s: str):
    return re.sub(r"(Date|Time)$", "", s)


def path_to_camelcase(path):
    parts = [p for p in path.split('/') if p]
    if not parts:
        return ""
    return parts[0] + ''.join(w.capitalize() for w in parts[1:])


def _norm(s):
    return re.sub(r'[（）]', lambda m: '(' if m.group() == '（' else ')', str(s).strip())


def canonicalize_field_name(name: str) -> str:
    normalized = _norm(name)
    return FIELD_NAME_ALIASES.get(normalized, normalized)


def to_pascal_case(text: str) -> str:
    tokens = re.findall(r'[A-Za-z0-9]+', text)
    return ''.join(token[:1].upper() + token[1:] for token in tokens if token)


def to_camel_case(text: str) -> str:
    tokens = re.findall(r'[A-Za-z0-9]+', text)
    if not tokens:
        return ''
    return tokens[0].lower() + ''.join(token[:1].upper() + token[1:].lower() for token in tokens[1:])


def zh_to_camel(text: str) -> str:
    normalized = re.sub(r'[/（）()\-\s]+', ' ', text).strip()
    pins = []
    for seg in normalized.split():
        pins.extend(lazy_pinyin(seg, style=Style.NORMAL))
    if not pins:
        return ''
    return pins[0].lower() + ''.join(p.capitalize() for p in pins[1:])


def build_excel_only_field_name(comment: str) -> str:
    canonical_name = canonicalize_field_name(comment)
    mapped = EXCEL_ONLY_FIELD_NAME_MAP.get(canonical_name)
    if mapped:
        return mapped
    try:
        en = ts.translate_text(canonical_name, translator='youdao', from_language='zh', to_language='en')
        camel_name = to_camel_case(en)
        if camel_name:
            return camel_name
    except Exception:
        pass
    return zh_to_camel(canonical_name) or 'excelField'
