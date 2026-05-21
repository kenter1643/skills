# -*- coding: utf-8 -*-
"""
前端代码生成器
根据 Excel 需求文档 + 接口文档 → 生成列表页/录入页/审批详情页

用法:
    # 方式1：直接传 Excel（推荐，自动解析）
    python generate.py --excel "<excel路径>" --api "<接口文档md>" [--output "<输出目录>"]

    # 方式2：传已解析的 JSON
    python generate.py --json "<json路径>" --api "<接口文档md>" [--output "<输出目录>"]
"""

import argparse
import json
import os
import re
import sys

from config import (
    COL as _DEFAULT_COL,
    CODE as _DEFAULT_CODE,
    BUILTIN_LIST_COLUMNS,
    BUILTIN_FORM_GROUPS,
    FIXED_FIELD_MAPPINGS,
    SKIP_DETAIL_FIELDS,
    FIELD_NAME_ALIASES,
    FIELD_PAIR_MAPPINGS,
    NAMING_RULES,
    WIDTH_ESTIMATES,
    WIDTH_DEFAULT,
)


# ---------------------------------------------------------------------------
# 1. 参数解析
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='前端代码生成器（支持直接传 Excel 自动解析）')
    parser.add_argument('--json', '-j', default=None, help='excel-parser 输出的 JSON 文件路径')
    parser.add_argument('--excel', '-e', default=None, help='Excel 需求文档路径（自动调用 excel-parser 解析）')
    parser.add_argument('--api', '-a', required=True, help='接口文档 Markdown 文件路径')
    parser.add_argument('--output', '-o', default=None, help='代码输出根目录（默认项目 src/views）')
    parser.add_argument('--business-name', '-b', default=None, help='业务名称（默认从 Excel 文件名提取）')
    args = parser.parse_args()
    if not args.json and not args.excel:
        parser.error('必须提供 --json 或 --excel 中的一个')
    return args


# ---------------------------------------------------------------------------
# 2. 接口文档解析
# ---------------------------------------------------------------------------

def parse_api_doc(md_path):
    """解析接口文档，提取 code, col, 以及入参/出参映射"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'code': None,
        'col': None,
        'flow_key': None,
        'list_fuzzy_params': {},     # 中文名 → API参数名 (firstXxx)
        'list_advanced_params': {},   # 中文名 → API参数名 (非first)
        'list_response_fields': {},   # 中文名 → API参数名 (出参)
        'detail_response_fields': {}, # 中文名 → API参数名 (详情出参)
        'save_fields': {},            # 中文名 → API参数名 (保存入参)
        'info_list_fields': {},       # 子表明细字段
        'drawer_apis': [],            # 抽屉 API：{title, url, method, response_fields}
        'api_paths': {},              # 接口文档中所有 API 路径 → {method, title}
    }

    # 提取所有 API 路径（从 ```plaintext 代码块中解析 HTTP 方法 + URL，向上查找所属标题）
    for m_block in re.finditer(r'```plaintext\s*\n(.*?)```', content, re.DOTALL):
        block = m_block.group(1)
        block_start = m_block.start()
        # 向上查找最近的 ### 或 ## 标题
        title = ''
        before = content[:block_start]
        for m_h in re.finditer(r'^#{2,4}\s+(.+)$', before, re.MULTILINE):
            title = m_h.group(1).strip()
        for m in re.finditer(
            r'(GET|POST|PUT|DELETE)\s+(/\S+)',
            block,
            re.IGNORECASE
        ):
            url = m.group(2)
            method = m.group(1).upper()
            if url not in result['api_paths']:
                result['api_paths'][url] = {'method': method, 'title': title}

    # 提取流程 Key → code, col（找不到时使用 config 默认值）
    m = re.search(r'流程Key[：:]\s*(\w+)', content)
    if not m:
        m = re.search(r'(\w*Bill\d+Approval)', content)
    if m:
        flow_key = m.group(1)
        result['flow_key'] = flow_key
        m2 = re.match(r'(\w+)Bill(\d+)Approval', flow_key)
        if m2:
            result['col'] = m2.group(1)
            result['code'] = m2.group(2)
    if not result['col']:
        result['col'] = _DEFAULT_COL
    if not result['code']:
        result['code'] = _DEFAULT_CODE

    # 解析所有 markdown 表格
    tables = _parse_md_tables(content)

    # 识别各表格用途并提取字段映射
    for title, rows in tables:
        if not rows:
            continue

        # 判断表格类型
        is_param_table = any(
            k in str(rows[0]).lower()
            for k in ['名称', '类型', '是否必传', '备注', '入参', '出参']
        )

        if not is_param_table:
            continue

        # 找到列索引
        header = rows[0]
        name_col = _find_col(header, ['名称', '字段名', '参数名'])
        remark_col = _find_col(header, ['备注', '说明', '字段说明'])
        type_col = _find_col(header, ['类型'])
        required_col = _find_col(header, ['是否必传', '是否必填', '必传', '必填'])

        if name_col is None:
            continue

        # 识别表格所属接口类型
        title_lower = (title or '').lower()

        for row in rows[1:]:
            if name_col >= len(row):
                continue
            param_name = str(row[name_col]).strip() if row[name_col] else ''
            if not param_name or param_name in ('名称', '---'):
                continue

            remark = str(row[remark_col]).strip() if remark_col is not None and remark_col < len(row) and row[remark_col] else ''

            # 去掉黄色字体标记
            remark = re.sub(r'（黄色字体含Str）', '', remark)

            # 按接口类型归类
            # 先判断是否是 firstXxx 模糊查询参数（跨 section 兼容）
            if param_name.startswith('first') and param_name != 'firstKeyWord':
                result['list_fuzzy_params'][remark] = param_name
                continue

            if '列表' in title_lower or 'list' in title_lower:
                if '入参' in title_lower:
                    if '分页' not in remark and '分页' not in param_name:
                        result['list_advanced_params'][remark] = param_name
                elif '出参' in title_lower:
                    result['list_response_fields'][remark] = param_name
            elif '详情' in title_lower or 'detail' in title_lower:
                if '出参' in title_lower and 'infoList' not in remark and '明细' not in remark:
                    result['detail_response_fields'][remark] = param_name
                elif ('出参' in title_lower or '入参' in title_lower) and ('明细' in remark or 'infoList' in remark or '行号' in remark):
                    result['info_list_fields'][remark] = param_name
            elif '保存' in title_lower or 'save' in title_lower:
                if '入参' in title_lower and 'infoList' not in remark and '明细' not in remark:
                    result['save_fields'][remark] = param_name
                elif '入参' in title_lower and ('明细' in remark or 'infoList' in remark or '行号' in remark):
                    result['info_list_fields'][remark] = param_name

        # 解析抽屉 API（弹窗/选择器）—— 匹配所有 ### 标题含"弹窗"的段落
        seen_titles = set()
        for m in re.finditer(r'^### (.+?弹窗.*)$', content, re.MULTILINE):
            section_title = m.group(1).strip()
            if section_title in seen_titles:
                continue
            seen_titles.add(section_title)
            section_start = m.end() + 1

            # 提取 API URL（在 section 后的 ```plaintext 代码块中）
            url = ''
            url_match = re.search(
                r'```(?:plaintext)?\s*\n\s*(?:GET|POST|PUT|DELETE)\s+(/\S+)',
                content[section_start:section_start + 400]
            )
            if url_match:
                url = url_match.group(1)

            # 提取出参说明表格字段
            response_fields = {}
            table_match = re.search(
                r'####\s+出参说明[\s\S]*?\n\|(.*?)\n\|[-|\s]*\n((?:\|.*?\n)+)',
                content[section_start:section_start + 1000]
            )
            if table_match:
                for row in table_match.group(2).strip().split('\n'):
                    cells = [c.strip() for c in row.split('|')[1:-1]]
                    if len(cells) >= 3 and cells[0] and cells[0] not in ('名称', '---'):
                        remark = re.sub(r'（黄色字体含Str）', '', cells[2])
                        if remark:
                            response_fields[remark] = cells[0]

            result['drawer_apis'].append({
                'title': section_title,
                'url': url,
                'method': 'GET',
                'response_fields': response_fields,
            })

    return result


def _parse_md_tables(content):
    """解析 markdown 中的所有表格，返回 [(标题, [行列表]), ...]"""
    tables = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 检测表格头（以 | 开头，下一行是 |---| 分隔符）
        if line.startswith('|') and '---' not in line:
            # 往前查找最近的标题：H4 是子标题，H2/H3 是父标题（区域归属）
            title = ''
            parent_title = ''
            for j in range(i - 1, max(i - 200, -1), -1):
                prev = lines[j].strip()
                if prev.startswith('## ') or prev.startswith('### '):
                    if not title:
                        title = prev.lstrip('#').strip()
                    if not parent_title:
                        parent_title = prev.lstrip('#').strip()
                    break
                elif prev.startswith('#### '):
                    if not title:
                        title = prev.lstrip('#').strip()
                    # 不 break，继续向上找 H2/H3 父标题
                elif prev and not prev.startswith('|') and not prev.startswith('```'):
                    if not title:
                        title = prev
            # 如果没有子标题，用父标题作为上下文
            if not title:
                title = parent_title
            elif parent_title and ('入参' in title or '出参' in title):
                # 把父标题作为上下文前缀，如 "单据列表 入参说明"
                title = parent_title + ' ' + title

            rows = []
            # 解析表头
            header = [c.strip() for c in line.split('|')[1:-1]]
            rows.append(header)

            i += 1
            # 跳过分隔行
            if i < len(lines) and '---' in lines[i]:
                i += 1

            # 解析数据行
            while i < len(lines):
                row_line = lines[i].strip()
                if not row_line.startswith('|'):
                    break
                cells = [c.strip() for c in row_line.split('|')[1:-1]]
                if cells and not all(c == '' for c in cells):
                    rows.append(cells)
                i += 1

            tables.append((title, rows))
        else:
            i += 1

    return tables


def _find_col(header, keywords):
    """在表头行中查找匹配关键字的列索引"""
    for idx, cell in enumerate(header):
        cell_lower = cell.lower().replace(' ', '')
        for kw in keywords:
            if kw.lower().replace(' ', '') in cell_lower:
                return idx
    return None


# ---------------------------------------------------------------------------
# 3. 字段映射构建
# ---------------------------------------------------------------------------

def build_field_mapping(json_data, api_data):
    """建立中文名 → API参数名的完整映射表，同时反向建立 API参数名 → 中文名"""
    mapping = {}   # 中文名 → API参数名
    reverse = {}   # API参数名 → 中文名

    # 汇总所有 API 参数（参数名 → 中文描述），排除模糊查询参数（firstXxx 是查询参数不是数据字段）
    all_params = {}
    for src in ['detail_response_fields', 'save_fields', 'list_response_fields',
                'list_advanced_params']:
        for remark, param_name in api_data.get(src, {}).items():
            if param_name and not param_name.startswith('first'):
                all_params[param_name] = remark

    # 策略1a：精确匹配（字段名 == API备注）
    field_names = list(json_data.get('field_info', {}).keys())
    for fname in field_names:
        clean = fname.strip()
        for param_name, remark in all_params.items():
            if clean == remark:
                mapping[clean] = param_name
                reverse[param_name] = clean
                break

    # 策略1b：子串匹配（字段名 in API备注），仅对未匹配字段
    for fname in field_names:
        clean = fname.strip()
        if clean in mapping:
            continue
        for param_name, remark in all_params.items():
            if clean in remark:
                mapping[clean] = param_name
                reverse[param_name] = clean
                break

    # 策略2：模糊匹配（字段关键词在备注中出现）
    for fname in field_names:
        clean = fname.strip()
        if clean in mapping:
            continue
        keywords = re.split(r'[（）()]', clean)
        main_kw = keywords[0].strip()
        for param_name, remark in all_params.items():
            if main_kw and main_kw in remark:
                mapping[clean] = param_name
                reverse[param_name] = clean
                break

    # 策略3：对于仍未匹配的，用命名规则推断
    naming_rules = NAMING_RULES

    # 已知固定映射（从 config.py 读取）
    fixed_mappings = FIXED_FIELD_MAPPINGS

    for fname in field_names:
        clean = fname.strip()
        if clean in mapping:
            continue
        if clean in fixed_mappings:
            mapping[clean] = fixed_mappings[clean]
            reverse[fixed_mappings[clean]] = clean
            continue
        # 尝试用已知映射推断
        for cn, en in fixed_mappings.items():
            if clean in cn or cn in clean:
                mapping[clean] = en
                reverse[en] = clean
                break

    return mapping, reverse


# ---------------------------------------------------------------------------
# 4. 字段属性判断辅助函数
# ---------------------------------------------------------------------------

def get_field_info(json_data, field_name):
    return json_data.get('field_info', {}).get(field_name, {})


def is_auto_generated(info):
    """判断是否为自动生成字段"""
    dg = info.get('data_generation', '')
    return '自动生成' in dg or '系统自动' in dg


def is_calculated(info):
    """判断是否为自动计算字段"""
    dg = info.get('data_generation', '')
    return '自动计算' in dg


def is_editable(info):
    """判断是否可编辑"""
    if not info.get('is_editable', True):
        return False
    if is_auto_generated(info) and not is_calculated(info):
        return False
    return True


def get_display_attrs(info, field_name, mapping):
    """根据 field_info 返回表单行属性

    规则：
    1. drawer + 不可编辑 → 普通文本禁用
    2. 其他类型按 display_type 映射到 row-key
    """
    attrs = {}
    dt = info.get('display_type', '')
    ft = info.get('field_type', '')

    # 规则1：drawer 且不可编辑 → 普通文本禁用
    if dt == 'drawer':
        if not is_editable(info):
            return {'disabled': True, 'placeholder': '自动带出'}
        # drawer 且可编辑 → select 形态，带抽屉按钮（在模板中生成 #append 插槽）
        attrs['_drawer_select'] = True
        attrs['row_key'] = 'select'
        if info.get('is_required'):
            attrs['required'] = True
        return attrs

    # 规则2：display_type → row-key 映射
    if dt in ('select', '下拉', '下拉选择框', '分级选择框'):
        attrs['row_key'] = 'select'
    elif dt in ('date', '时间选择框', '时间'):
        attrs['row_key'] = 'date'
    elif dt in ('number', '数值框', '数字'):
        attrs['row_key'] = 'number'
    elif dt in ('textarea', '多行文本'):
        attrs['row_key'] = 'textarea'
        attrs['_bind_span'] = '24'
    elif dt in ('file', '附件'):
        attrs['row_key'] = 'files'
        attrs['_bind_span'] = '24'
    # dt == 'text' 或空 → 普通输入框，不需要 row-key

    if info.get('is_required'):
        attrs['required'] = True

    if not is_editable(info):
        attrs['disabled'] = True
        attrs['placeholder'] = '自动带出'

    # 数值字段自动追加单位：字段名含「金额」或以「(元)」结尾
    if attrs.get('row_key') == 'number' and (field_name.endswith('(元)') or '金额' in field_name):
        attrs['_unit'] = '元'

    # 枚举字段
    if info.get('is_enum'):
        attrs['row_key'] = 'select'

    # data_check 属性提取：限制输入N字/支持小数位/不可输入负数/不可输入0
    dc = info.get('data_check', '')
    if dc:
        m = re.search(r'限制输入(\d+)字', dc)
        if m:
            attrs['_bind_maxLength'] = m.group(1)
        m = re.search(r'支持输入小数(?:点)?后(\d+)位', dc)
        if m and attrs.get('row_key') == 'number':
            attrs['_bind_decimal'] = m.group(1)
        if '不可输入负数' in dc or '不可输入负值' in dc:
            attrs['_bind_negative'] = 'false'
        if re.search(r'不可输入\s*0|不能为\s*0', dc):
            attrs['_bind_zero'] = 'false'

    return attrs


# data_check 中已映射为属性的关键词，自定义规则生成时跳过
_DATA_CHECK_ATTR_PATTERNS = [
    re.compile(r'限制输入\d+字'),
    re.compile(r'支持输入小数(?:点)?后\d+位'),
    re.compile(r'不可输入负数|不可输入负值'),
    re.compile(r'不可输入\s*0|不能为\s*0'),
    re.compile(r'必填'),
]


def _strip_data_check_remaining(text):
    """清理 data_check 提取属性后残留的标点和编号字符"""
    text = re.sub(r'\d+[、，]', '', text)
    text = re.sub(r'[；;。，,]$', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_data_check_rules(info):
    """从 data_check 中提取自定义校验规则

    属性类（decimal/negative/zero/maxLength）由 get_display_attrs 处理，
    此函数只生成需要自定义 validator 方法的规则。
    返回 (规则列表, 是否需要生成 validator 方法)
    """
    dc = info.get('data_check', '')
    if not dc:
        return [], False
    # 去掉已被属性映射覆盖的模式，检查是否有剩余校验内容
    remaining = dc
    for pat in _DATA_CHECK_ATTR_PATTERNS:
        remaining = pat.sub('', remaining)
    remaining = _strip_data_check_remaining(remaining)
    if not remaining:
        return [], False
    return [], True


def get_detail_column_attrs(info, field_name):
    """根据 field_info 返回明细表列属性，对齐 fam/bill1723Page 模式"""
    attrs = {}
    dt = info.get('display_type', '')
    ft = info.get('field_type', '')
    editable = is_editable(info)

    # 可编辑数值 → type="number"
    if (dt in ('number', '数值框') or '数值' in ft) and editable:
        attrs['type'] = 'number'
    # 不可编辑的文本列 → type="text"（纯展示）
    elif not editable and ft not in ('按钮',):
        attrs['type'] = 'text'
    # 可编辑文本区域
    elif dt in ('textarea', '多行文本'):
        attrs['type'] = 'textarea'

    # 金额列加单位和汇总
    if '元' in field_name or '金额' in field_name:
        if attrs.get('type') in ('number', 'text'):
            attrs['summary'] = True

    if info.get('is_required'):
        attrs['required'] = True

    if not editable:
        attrs['disabled'] = True

    return attrs


# ---------------------------------------------------------------------------
# 5. 代码生成器
# ---------------------------------------------------------------------------

def _load_detail_router(project_root):
    """解析 src/constriant/detailRouter.js，返回 {中文关键词: navCode, ...} 映射"""
    router_path = os.path.join(project_root, 'src', 'constriant', 'detailRouter.js')
    mapping = {}

    if not os.path.exists(router_path):
        return mapping

    with open(router_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 // 中文注释 后紧跟的 KEY: { 模式
    # 例如: // 承包合同列表\n    CBHTCS: {
    pattern = re.compile(r'//\s*(.+?)\s*\n\s*(\w+)\s*:\s*\{')
    for m in pattern.finditer(content):
        comment = m.group(1).strip()
        key = m.group(2).strip()
        # 提取注释中与业务相关的关键词（去掉"列表"等后缀）
        kw = comment.replace('列表', '').replace('详情', '').replace('页面', '').strip()
        if kw and kw not in mapping:
            mapping[kw] = key

    # 补充直接匹配（注释行中直接包含关键词的）
    # 例如: // 承包合同评审 → CBPS, // 承包合同 → CBHTCS
    for m in pattern.finditer(content):
        comment = m.group(1).strip()
        key = m.group(2).strip()
        mapping[comment] = key

    return mapping


class CodeGenerator:
    def __init__(self, json_data, api_data, mapping, reverse_mapping, output_dir):
        self.json = json_data
        self.api = api_data
        self.mapping = mapping
        self.reverse = reverse_mapping
        self.output_dir = output_dir
        self.code = api_data['code']
        self.col = api_data['col']

        # 计算项目根目录并加载 detailRouter
        _script_dir = os.path.dirname(os.path.abspath(__file__))
        self._project_root = os.path.dirname(os.path.dirname(os.path.dirname(_script_dir)))
        self._detail_router_map = _load_detail_router(self._project_root)

    def generate_all(self):
        # API 文件
        api_dir = os.path.join(self._project_root, 'src', 'api', 'business', self.col)
        os.makedirs(api_dir, exist_ok=True)
        api_path = os.path.join(api_dir, f'bill{self.code}Page.js')
        with open(api_path, 'w', encoding='utf-8') as f:
            f.write(self._gen_api_js())
        print(f"[生成] {api_path}")

        files = [
            ('index.vue', self._gen_index_vue),
            ('add.vue', self._gen_add_vue),
        ]
        business_dir = os.path.join(self.output_dir, 'business', self.col, f'bill{self.code}Page')
        os.makedirs(business_dir, exist_ok=True)
        for filename, gen_func in files:
            path = os.path.join(business_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(gen_func())
            print(f"[生成] {path}")

        # 审批详情页
        approval_dir = os.path.join(self.output_dir, 'approvalManagement', 'business',
                                     f'{self.col}Bill{self.code}Approval')
        approval_js_dir = os.path.join(approval_dir, 'js')
        os.makedirs(approval_js_dir, exist_ok=True)

        with open(os.path.join(approval_dir, 'index.vue'), 'w', encoding='utf-8') as f:
            f.write(self._gen_approval_index_vue())
        print(f"[生成] {os.path.join(approval_dir, 'index.vue')}")

        with open(os.path.join(approval_js_dir, 'ellipsis.js'), 'w', encoding='utf-8') as f:
            f.write(self._gen_approval_list_js())
        print(f"[生成] {os.path.join(approval_js_dir, 'ellipsis.js')}")

        with open(os.path.join(approval_js_dir, 'list.js'), 'w', encoding='utf-8') as f:
            f.write("module.exports = require('./ellipsis');\n")
        print(f"[生成] {os.path.join(approval_js_dir, 'list.js')}")

    # ---- 列表页 ----

    def _gen_index_vue(self):
        lines = ['<template>', '  <columns-template>']

        builtin = BUILTIN_LIST_COLUMNS

        def _filter_prop(fname, prop, info):
            ft = info.get('field_type', '')
            dt = info.get('display_type', '')
            if '日期' in ft:
                return 'bill'
            if info.get('is_enum') or dt == 'select':
                return prop.replace('Str', '')
            return prop

        def _display_prop(fname, prop, info):
            ft = info.get('field_type', '')
            if '金额' in fname or '元' in fname or '税率' in fname:
                return prop + 'Str'
            if '状态' in fname:
                return prop + 'Str'
            if '日期' in ft or '时间' in fname:
                return prop + 'Str'
            if info.get('is_enum') or info.get('display_type') == 'select':
                return prop + 'Str'
            return prop

        def _build_column(fname):
            """构建单个列的 HTML 行列表"""
            prop = self.mapping.get(fname, self._guess_prop(fname))
            info = get_field_info(self.json, fname)
            dprop = _display_prop(fname, prop, info)
            width = self._estimate_width(fname, info)
            is_drawer = info.get('display_type') == 'drawer'

            filter_attrs = ''
            ft = info.get('field_type', '')
            dt = info.get('display_type', '')
            in_fuzzy = fname in fuzzy_set
            in_advanced = fname in advanced_set

            if '日期' in ft:
                fp = _filter_prop(fname, prop, info) or prop
                filter_attrs = f' filter filter-type="daterange" filter-format="yyyy-MM-dd" filter-prop="{fp}"'
            elif info.get('is_enum') or dt == 'select':
                fp = _filter_prop(fname, prop, info) or prop
                filter_attrs = f' filter filter-type="select" filter-prop="{fp}" filter-api="business/{self.col}/bill{self.code}Page:{fp}Label"'
            elif is_drawer:
                filter_attrs = ' filter'
                if in_fuzzy:
                    filter_attrs += ' filter-nimble'
            elif in_fuzzy:
                filter_attrs = ' filter filter-nimble'
            elif in_advanced:
                filter_attrs = ' filter'

            col_lines = []
            if is_drawer:
                id_key = self._guess_id_key(fname, prop)
                nav_code = self._guess_nav_code(fname)
                col_lines.append(f'    <zy-ag-table-column label="{fname}" prop="{prop}" width="{width}"{filter_attrs}>')
                col_lines.append(f'      <template slot-scope="{{ data }}">')
                col_lines.append(f'        <el-button v-if="data.{prop}" type="text" '
                                 f'@click="$goDetailView(data, \'{id_key}\', \'{nav_code}\', true)">')
                col_lines.append(f'          {{{{ data.{prop} }}}}')
                col_lines.append(f'        </el-button>')
                col_lines.append(f'        <span v-else>——</span>')
                col_lines.append(f'      </template>')
                col_lines.append(f'    </zy-ag-table-column>')
            else:
                col_lines.append(f'    <zy-ag-table-column label="{fname}" prop="{dprop}" width="{width}"{filter_attrs}></zy-ag-table-column>')
            return col_lines

        fuzzy_set = set(self.json.get('fuzzy_search', []))
        advanced_set = set(self.json.get('advanced_search', []))

        list_fields = self.json.get('list_order_fields', [])

        # 找出 auto slot 区域的边界（单据状态之后，承办项目/部门之前）
        auto_start = None
        auto_end = None
        for i, fname in enumerate(list_fields):
            if fname == '单据状态':
                auto_start = i
            elif fname == '承办项目/部门':
                auto_end = i

        # 收集各 slot 区域的列
        auto_columns = []    # <template slot="auto"> 包裹
        default_columns = []  # 默认 slot（无需包裹）

        for i, fname in enumerate(list_fields):
            if fname in builtin:
                continue
            col_lines = _build_column(fname)
            in_auto_zone = (auto_start is not None and auto_end is not None
                            and auto_start < i < auto_end)
            if in_auto_zone:
                auto_columns.extend(col_lines)
            else:
                default_columns.extend(col_lines)

        # 输出 auto slot（包裹在 <template slot="auto"> 中）
        if auto_columns:
            lines.append('    <template slot="auto">')
            lines.extend(auto_columns)
            lines.append('    </template>')

        # 输出默认 slot 的列
        lines.extend(default_columns)

        lines.append('  </columns-template>')
        lines.append('</template>')
        lines.append('')
        lines.append('<script>')
        lines.append('import ColumnsTemplate from "@/views/common/agGrid/template/columnsV2"')
        lines.append('export default {')
        lines.append(f'  name: "{self.col}Bill{self.code}Approval",')
        lines.append('  components: { ColumnsTemplate },')
        lines.append('}')
        lines.append('</script>')

        return '\n'.join(lines) + '\n'

    # ---- 录入页 ----

    def _gen_add_vue(self):
        business_name = self.json.get('business_name', '单据')
        detail_cfg = self.json.get('input_style', {}).get('details', {})
        detail_title = detail_cfg.get('title', '明细') if isinstance(detail_cfg, dict) else '明细'
        detail_fields = detail_cfg.get('fields', []) if isinstance(detail_cfg, dict) else detail_cfg
        drawers = self.json.get('input_style', {}).get('drawers', [])

        # 从明细字段中提取按钮型字段（排除"操作"）
        detail_buttons = []
        for fname in detail_fields:
            info = get_field_info(self.json, fname)
            if info.get('field_type') == '按钮' and fname != '操作':
                detail_buttons.append({'name': fname, 'info': info})

        # 导入按钮：detail_buttons 中含"导入"
        has_import = any('导入' in bf['name'] for bf in detail_buttons)
        # 接口文档是否包含 download 端点
        api_paths = self.api.get('api_paths', {})
        has_download = any('download' in url for url in api_paths)

        # 从 data_check 中提取校验规则，生成 rules 数据和自定义 validator 方法
        field_rules = {}       # {prop: [rule_objs]}
        custom_validators = [] # [{prop, method_name, label, data_check}]
        # 内置组字段（基础信息、表头）由模板渲染，不生成校验规则
        builtin_fields = set()
        for group in self.json.get('input_style', {}).get('main', []):
            if group.get('title', '') in BUILTIN_FORM_GROUPS:
                for f in group.get('fields', []):
                    builtin_fields.add(f)
        for fname, info in self.json.get('field_info', {}).items():
            if fname in builtin_fields:
                continue
            # 跳过按钮类字段（如"新增"、"导入"），它们不需要表单校验规则
            if info.get('field_type') == '按钮':
                continue
            rules, needs_validator = parse_data_check_rules(info)
            prop = self.mapping.get(fname, self._guess_prop(fname))
            # 跳过中文 prop（映射失败回退），否则生成 check新增 之类的方法名
            if re.search(r'[一-鿿]', prop):
                continue
            if rules:
                field_rules[prop] = rules
            if needs_validator:
                method_name = 'check' + prop[0].upper() + prop[1:]
                custom_validators.append({
                    'prop': prop,
                    'method_name': method_name,
                    'label': fname,
                    'data_check': info.get('data_check', ''),
                })
                # 添加 validator 引用到 rules
                rule_obj = {
                    'validator': f'this.{method_name}',
                    'trigger': ['change', 'blur'],
                }
                if prop in field_rules:
                    field_rules[prop].append(rule_obj)
                else:
                    field_rules[prop] = [rule_obj]

        # 抽屉按钮：按钮字段 display_type=drawer 且匹配 drawer 配置
        drawer_buttons = []
        for bf in detail_buttons:
            if bf['info'].get('display_type') == 'drawer':
                for d in drawers:
                    if d.get('title') == bf['name'] and d.get('list_fields'):
                        drawer_buttons.append({'name': bf['name'], 'drawer': d})
                        break

        # 需要 wrapper div（有 select-drawer 在 form 外）
        needs_wrapper = bool(drawer_buttons)

        # 缩进层级
        W1 = '  '                                          # wrapper div
        B1 = '    ' if needs_wrapper else '  '              # zy-order-form / select-drawer 级
        B2 = '      ' if needs_wrapper else '    '          # form-group 级
        B3 = '        ' if needs_wrapper else '      '      # form-row / template header 级
        B4 = '          ' if needs_wrapper else '        '  # 内容级
        B5 = '            ' if needs_wrapper else '          '

        lines = ['<template>']
        if needs_wrapper:
            lines.append(f'{W1}<div>')

        lines.append(f'{B1}<zy-order-form :page-name="title" ref="form" '
                     f':templates="[\'baseInfo\']" @beforeLayout="beforeLayout" :watch="watch">')

        # 主表分组（跳过组件内置的模板组）
        for group in self.json.get('input_style', {}).get('main', []):
            title = group.get('title', '')
            if title in BUILTIN_FORM_GROUPS:
                continue
            if not title:
                title = '基本信息'
            lines.append(f'{B2}<zy-order-form-group title="{title}">')
            for fname in group.get('fields', []):
                info = get_field_info(self.json, fname)
                prop = self.mapping.get(fname, self._guess_prop(fname))
                attrs = self._build_form_row_attrs(fname, info, prop)
                if attrs is None:
                    continue
                # data_check 校验规则
                rule_attr = ''
                if prop in field_rules:
                    rule_attr = f' :rule="rules.{prop}"'
                _raw_attrs = get_display_attrs(info, fname, self.mapping)
                label = fname.replace('(元)', '') if _raw_attrs and _raw_attrs.get('_unit') else fname
                slots = self._build_form_row_slots(fname, info, prop)
                if slots:
                    lines.append(f'{B3}<zy-order-form-row label="{label}" prop="{prop}"{attrs}{rule_attr}>')
                    lines.append(slots)
                    lines.append(f'{B3}</zy-order-form-row>')
                else:
                    lines.append(f'{B3}<zy-order-form-row label="{label}" prop="{prop}"{attrs}{rule_attr}></zy-order-form-row>')
            lines.append(f'{B2}</zy-order-form-group>')

        # 明细表
        if detail_fields:
            lines.append(f'{B2}<zy-order-form-group title="{detail_title}" type="table" base="infoList" :useAgGrid="true">')
            lines.append(f'{B3}<template #header>')

            # 遍历 detail_buttons 渲染按钮
            for bf in detail_buttons:
                dt = bf['info'].get('display_type', '')
                if dt == 'drawer':
                    for db in drawer_buttons:
                        if db['name'] == bf['name']:
                            safe = self._safe_var_name(db['name'], db['drawer'].get('list_fields', []))
                            var = safe[0].lower() + safe[1:]
                            lines.append(f'{B4}<el-button size="mini" type="primary" '
                                         f'@click="addRow(\'{var}Drawer\')">{db["name"]}</el-button>')
                            break
                elif '导入' in bf['name']:
                    lines.append(f'{B4}<el-button size="mini" @click="showImport">导入</el-button>')

            lines.append(f'{B3}</template>')
            lines.append(f'{B3}<template #append>')

            skip_detail_fields = SKIP_DETAIL_FIELDS
            has_operate = any('操作' in fname for fname in detail_fields)
            for fname in detail_fields:
                if fname in skip_detail_fields:
                    continue
                info = get_field_info(self.json, fname)
                dt = info.get('display_type', '')
                ft = info.get('field_type', '')
                if dt in ('button', 'drawer', 'dialog') or ft == '按钮':
                    continue
                prop = self.mapping.get(fname, self._guess_prop(fname))
                col_attrs = self._build_detail_col_attrs(fname, info)
                lines.append(f'{B4}<el-table-column label="{fname}" prop="{prop}"{col_attrs}></el-table-column>')

            if has_operate:
                lines.append(f'{B4}<el-table-column label="操作" align="center" fixed="right" '
                             f'width="100" type="operate" @removeRow="removeRow" '
                             f':options="[\'delete\']"></el-table-column>')
            lines.append(f'{B3}</template>')
            lines.append(f'{B2}</zy-order-form-group>')

        # plugins（仅 import-list）
        if has_import:
            lines.append(f'{B2}<template #plugins>')
            lines.append(f'{B3}<import-list v-bind="importConfig" ref="importList" '
                         f'@importResult="importResult"></import-list>')
            lines.append(f'{B2}</template>')

        lines.append(f'{B1}</zy-order-form>')

        # select-drawer 组件（form 外部，对齐 bill1721Page 模式）
        for db in drawer_buttons:
            safe = self._safe_var_name(db['name'], db['drawer'].get('list_fields', []))
            var = safe[0].lower() + safe[1:]
            title = db['drawer'].get('title', db['name'])
            lines.append(f'{B1}<select-drawer ref="{var}Drawer" title="{title}"')
            lines.append(f'{B1}  :api="{var}Api"')
            lines.append(f'{B1}  :columns="{var}Columns"')
            lines.append(f'{B1}  :searchParams="{{}}"')
            lines.append(f'{B1}  rowKey="id"')
            lines.append(f'{B1}  size="60%"')
            lines.append(f'{B1}  @save="on{safe}Select"></select-drawer>')

        if needs_wrapper:
            lines.append(f'{W1}</div>')
        lines.append(f'</template>')
        lines.append(f'')
        lines.append(f'<script>')
        lines.append(f"import FormController from '@/components/Basic/orderForm/js/controller'")
        if drawer_buttons:
            lines.append(f"import SelectDrawer from "
                         f"'@/views/business/fm/bill1721Page/components/SelectDrawer.vue'")
        if has_import:
            lines.append(f"import ImportList from '@/views/components/common/importInfo/importList.vue'")
        if has_import and has_download:
            lines.append(f"import {{ downloadTemplate }} from "
                         f"'@/api/business/{self.col}/bill{self.code}Page'")
        lines.append(f'import request from "@/utils/request"')
        lines.append(f'')
        lines.append(f'export default {{')
        comps = []
        if drawer_buttons:
            comps.append('SelectDrawer')
        if has_import:
            comps.append('ImportList')
        if comps:
            lines.append(f'  components: {{ {", ".join(comps)} }},')
        else:
            lines.append(f'  components: {{}},')
        lines.append(f'  data() {{')
        lines.append(f'    return {{')

        # 枚举字段 Options
        for fname, info in self.json.get('field_info', {}).items():
            if fname in builtin_fields:
                continue
            if info.get('field_type') == '按钮':
                continue
            if info.get('is_enum'):
                prop = self.mapping.get(fname, self._guess_prop(fname))
                # 跳过中文 prop
                if not re.search(r'[一-鿿]', prop):
                    lines.append(f'      {prop}Options: [],')

        if has_import:
            lines.append(f'      importConfig: {{}},')
        # 抽屉列配置
        drawer_api_infos = self.api.get('drawer_apis', [])
        for db in drawer_buttons:
            safe = self._safe_var_name(db['name'], db['drawer'].get('list_fields', []))
            var = safe[0].lower() + safe[1:]

            # 匹配 API 文档中的抽屉接口
            matched_api = {}
            for info in drawer_api_infos:
                if db['name'] in info.get('title', ''):
                    matched_api = info
                    break

            # 列配置：从 list_fields 生成，根据 fuzzy_search/advanced_search 区分 filter
            list_fields = db['drawer'].get('list_fields', [])
            fuzzy_set = set(db['drawer'].get('fuzzy_search', []))
            advanced_set = set(db['drawer'].get('advanced_search', []))
            if list_fields:
                lines.append(f'      {var}Columns: [')
                for fname in list_fields:
                    prop = self.mapping.get(fname, self._guess_prop(fname))
                    filters = []
                    if fname in advanced_set:
                        filters.append('filter: true')
                    if fname in fuzzy_set:
                        filters.append('filterNimble: true')
                    filter_str = ', ' + ', '.join(filters) if filters else ''
                    lines.append(f'        {{ label: \'{fname}\', prop: \'{prop}\'{filter_str} }},')
                lines.append(f'      ],')
                lines.append(f'      {var}Api: \'{matched_api.get("url", "")}\',')
            else:
                lines.append(f'      {var}Columns: [],  // TODO: 配置抽屉列表列')
                lines.append(f'      {var}Api: null,  // TODO: 配置抽屉列表接口')
        # data_check 校验规则
        if field_rules:
            lines.append(f'      rules: {{')
            for prop, rules in field_rules.items():
                rule_str = self._rules_to_js(rules)
                lines.append(f'        {prop}: {rule_str},')
            lines.append(f'      }},')
        lines.append(f'      watch: {{}}')
        lines.append(f'    }}')
        lines.append(f'  }},')
        lines.append(f'  computed: {{')
        lines.append(f'    title() {{')
        lines.append(f"      if (this.$route.query.id) return '编辑{business_name}'")
        lines.append(f"      return '新增{business_name}'")
        lines.append(f'    }},')
        lines.append(f'  }},')
        lines.append(f'  created() {{')
        for fname, info in self.json.get('field_info', {}).items():
            if fname in builtin_fields:
                continue
            if info.get('field_type') == '按钮':
                continue
            if info.get('is_enum'):
                prop = self.mapping.get(fname, self._guess_prop(fname))
                # 跳过中文 prop（映射失败回退）
                if not re.search(r'[一-鿿]', prop):
                    lines.append(f'    this.get{prop[0].upper() + prop[1:]}Options()')
        if has_import:
            lines.append(f"    const path = window.location.pathname")
            lines.append(f"    const list = path.split('/')")
            lines.append(f"    const index = list.indexOf('bill')")
            lines.append(f'    const code = list[index + 1]')
            lines.append(f'    this.importConfig = {{')
            lines.append(f"      title: '导入明细',")
            lines.append(f"      fileName: 'multipartFile',")
            lines.append(f"      uploadText: '上传导入明细',")
            lines.append(f"      fileApi: `/{self.col}/bill/${{code}}/detail/import`,")
            lines.append(f'      column: {{')
            lines.append(f'        columns: [')
            lines.append(f'          {{ type: "index", label: "序号", width: "80", align: "center" }},')
            lines.append(f'          {{ prop: "errorMsg", label: "失败原因", minWidth: "200", '
                         f'"show-overflow-tooltip": false, visible: true, custom: true }}')
            lines.append(f'        ]')
            lines.append(f'      }},')
            if has_download:
                lines.append(f'      downloadTemplate: downloadTemplate,')
            else:
                lines.append(f'      downloadTemplate: () => {{')
                lines.append(f"        return request({{ url: `/{self.col}/bill/${{code}}/detail/import/template`, "
                             f"method: 'GET' }})")
                lines.append(f'      }}')
            lines.append(f'    }}')
        lines.append(f'  }},')
        lines.append(f'  methods: {{')
        lines.append(f'    beforeLayout(model) {{')
        lines.append(f'      return new Promise(async resolve => {{')
        lines.append(f'        resolve(true)')
        lines.append(f'      }})')
        lines.append(f'    }},')
        if has_import:
            lines.append(f'    importResult(val) {{')
            lines.append(f'      if (val.errorList.length) return')
            lines.append(f'      const model = FormController.current?.model || {{}}')
            lines.append(f'      const list = model.infoList || []')
            lines.append(f'      const successList = val?.successList || []')
            lines.append(f'      model.infoList = [...list, ...successList]')
            lines.append(f'    }},')
        lines.append(f'    removeRow(index, ref) {{')
        lines.append(f'      ref.removeRow(index)')
        lines.append(f'    }},')
        if has_import:
            lines.append(f'    showImport() {{')
            lines.append(f'      if (this.$refs.importList) this.$refs.importList.open()')
            lines.append(f'    }},')
        # 抽屉方法（对齐 bill1721Page addRow 模式）
        if drawer_buttons:
            lines.append(f'    addRow(refName) {{')
            lines.append(f'      const model = FormController.current?.model || {{}}')
            lines.append(f'      const selections = (model.infoList || []).map(v => v.id).filter(Boolean)')
            lines.append(f'      this.$refs[refName].show({{}}, selections)')
            lines.append(f'    }},')
        for db in drawer_buttons:
            safe = self._safe_var_name(db['name'], db['drawer'].get('list_fields', []))
            lines.append(f'    on{safe}Select(selection) {{')
            lines.append(f'      const model = FormController.current?.model || {{}}')
            lines.append(f'      model.infoList = [...(model.infoList || []), ...selection]')
            lines.append(f'    }},')
        for fname, info in self.json.get('field_info', {}).items():
            if fname in builtin_fields:
                continue
            if info.get('field_type') == '按钮':
                continue
            if info.get('is_enum'):
                prop = self.mapping.get(fname, self._guess_prop(fname))
                if not re.search(r'[一-鿿]', prop):
                    method = f'get{prop[0].upper() + prop[1:]}Options'
                    lines.append(f'    {method}() {{')
                    lines.append(f'      // TODO: 替换为实际枚举接口')
                    lines.append(f'    }},')
        # data_check 自定义校验方法
        for cv in custom_validators:
            lines.append(f'    {cv["method_name"]}(rule, value, callback) {{')
            dc_comment = cv['data_check'].replace('\n', ' ')
            lines.append(f'      // TODO: {cv["label"]}校验 - {dc_comment}')
            lines.append(f'      callback()')
            lines.append(f'    }},')
        lines.append(f'  }}')
        lines.append(f'}}')
        lines.append(f'</script>')

        return '\n'.join(lines) + '\n'

    # ---- mixins.js ----

    # ---- 审批详情页 ----

    def _gen_approval_index_vue(self):
        detail_cfg = self.json.get('input_style', {}).get('details', {})
        detail_fields = detail_cfg.get('fields', []) if isinstance(detail_cfg, dict) else detail_cfg
        lines = ['<script>',
                 "import base from '../index.vue'",
                 'export default {',
                 '  extends: base,',
                 '  data() {',
                 '    return {',
                 '      showPrint: true,',
                 '      renderMap: [']

        if detail_fields:
            lines.append('        {')
            lines.append("          slot: 'subTable',")
            lines.append('          render: (h, ctx) => {')
            lines.append('            const { model } = ctx.props')
            lines.append('            return (')
            lines.append('              <div>')
            lines.append('                <div ref="columns">')
            skip_detail_fields = SKIP_DETAIL_FIELDS
            for fname in detail_fields:
                if fname in skip_detail_fields:
                    continue
                info = get_field_info(self.json, fname)
                dt = info.get('display_type', '')
                if dt in ('button', 'drawer', 'dialog') or info.get('field_type', '') == '按钮':
                    continue
                prop = self.mapping.get(fname, self._guess_prop(fname))
                # 使用显示 prop（金额/日期/状态字段加 Str 后缀）
                ft = info.get('field_type', '')
                dprop = prop
                if '金额' in fname or '元' in fname or '税率' in fname:
                    dprop = prop + 'Str'
                elif '日期' in ft or '时间' in fname:
                    dprop = prop + 'Str'
                elif '状态' in fname:
                    dprop = prop + 'Str'
                col = f'                  <el-table-column label="{fname}" prop="{dprop}"'
                if info.get('display_type') == 'number' or '数值' in info.get('field_type', ''):
                    col += ' type="number"'
                    if '元' in fname or '金额' in fname:
                        col += ' summary'
                col += ' min-width="200"></el-table-column>'
                lines.append(col)
            lines.append('                </div>')
            lines.append('              </div>')
            lines.append('            )')
            lines.append('          }')
            lines.append('        },')

        lines.append('      ],')
        lines.append(f'      billCode: {self.code}')
        lines.append('    }')
        lines.append('  },')
        lines.append('  methods: {')
        lines.append('  }')
        lines.append('}')
        lines.append('</script>')

        return '\n'.join(lines) + '\n'

    # ---- 审批详情 js/ellipsis.js ----

    def _gen_approval_list_js(self):
        lines = ['module.exports = [']

        for group in self.json.get('input_style', {}).get('main', []):
            title = group.get('title', '基本信息')
            # 表头由审批基础组件渲染，不需要在 list.js 中重复
            if title == '表头':
                continue
            fields = group.get('fields', [])

            # 每行放 4 个字段
            rows = []
            row = []
            for fname in fields:
                info = get_field_info(self.json, fname)
                prop = self.mapping.get(fname, self._guess_prop(fname))
                cell = {'label': fname, 'value': prop}

                # 判断是否为可跳转字段（仅「xxx编号」可点击跳转）
                if '编号' in fname:
                    cell['type'] = 'router'
                    cell['idKey'] = self._guess_id_key(fname, prop)
                    cell['code'] = self._guess_nav_code(fname)

                # 多行文本 → 独占一行
                dt = info.get('display_type', '')
                if dt in ('textarea', '多行文本'):
                    if row:
                        rows.append(row)
                    cell['colSpan'] = 24
                    rows.append([cell])
                    row = []
                    continue

                # 附件
                if fname == '附件':
                    cell['type'] = 'files'
                    cell['value'] = 'fileList'
                    row.append(cell)
                    if len(row) >= 4:
                        rows.append(row)
                        row = []
                    continue

                # 金额/日期/状态字段 → 使用 Str 后缀的显示值
                ft = info.get('field_type', '')
                if '金额' in fname or '元' in fname or '税率' in fname:
                    cell['value'] = prop + 'Str'
                elif '日期' in ft or '时间' in fname:
                    cell['value'] = prop + 'Str'
                elif '状态' in fname:
                    cell['value'] = prop + 'Str'

                row.append(cell)
                if len(row) >= 4:
                    rows.append(row)
                    row = []
            if row:
                if len(row) == 1:
                    row[0]['colSpan'] = 24
                rows.append(row)

            lines.append(f'  {{')
            lines.append(f'    title: "{title}",')
            lines.append(f'    tableData: [')
            for row in rows:
                cells_str = ',\n        '.join(self._format_cell(c) for c in row)
                lines.append(f'      [\n        {cells_str}\n     ],')
            lines.append(f'    ],')
            lines.append(f'  }},')

        # 明细子表
        detail_cfg = self.json.get('input_style', {}).get('details', {})
        detail_title = detail_cfg.get('title', '明细') if isinstance(detail_cfg, dict) else '明细'
        detail_fields = detail_cfg.get('fields', []) if isinstance(detail_cfg, dict) else detail_cfg
        if detail_fields:
            lines.append(f'  {{')
            lines.append(f'    title: "{detail_title}",')
            lines.append(f"    customFloor: 'subTable',")
            lines.append(f"    base: 'infoList',")
            lines.append(f"    type: 'table',")
            lines.append(f'  }}')

        lines.append('];')
        return '\n'.join(lines) + '\n'

    # ---- API 文件 ----

    def _gen_api_js(self):
        """生成 src/api/business/{col}/bill{code}Page.js（遍历接口文档中所有 API 路径）"""
        api_paths = self.api.get('api_paths', {})
        lines = [
            'import request from "@/utils/request";',
            '',
        ]

        # JS 保留字映射
        _reserved = {'delete': 'remove', 'export': 'exportData'}

        # 标准单据操作端点（由框架处理，不生成 API 函数）
        _skip_segments = {
            'list', 'detail', 'save', 'delete', 'audit',
            'revocation', 'deliver', 'export', 'checkparam',
        }

        if not api_paths:
            lines.append('// TODO: 根据接口文档补充 API 函数')
            lines.append('')
        else:
            generated = 0
            for url, info in api_paths.items():
                seg = url.rstrip('/').rsplit('/', 1)[-1]
                # 跳过标准操作
                if seg.lower() in _skip_segments:
                    continue
                generated += 1
                method = info['method']
                title = info.get('title', url)
                # 驼峰分段
                parts = re.split(r'(?=[A-Z])', seg)
                func_name = parts[0].lower() + ''.join(p[0].upper() + p[1:].lower() for p in parts[1:]) if len(parts) > 1 else seg.lower()
                # 处理 JS 保留字
                func_name = _reserved.get(func_name, func_name)
                # 含数字前缀补下划线
                if func_name and func_name[0].isdigit():
                    func_name = '_' + func_name

                param_name = 'params' if method == 'GET' else 'data'
                lines.append(f'// {title}')
                lines.append(f'export function {func_name}({param_name}) {{')
                lines.append(f'  return request({{')
                lines.append(f"    url: '{url}',")
                lines.append(f"    method: '{method.lower()}',")
                lines.append(f'    {param_name}')
                lines.append(f'  }});')
                lines.append(f'}}')
                lines.append('')

            if generated == 0:
                lines.append('// TODO: 根据接口文档补充 API 函数')
                lines.append('')

        return '\n'.join(lines) + '\n'

    # ---- 辅助方法 ----

    def _rules_to_js(self, rules):
        """将规则列表转为 JS 对象字面量字符串，处理 validator: this.xxx 引用不加引号"""
        parts = []
        for r in rules:
            items = []
            for k, v in r.items():
                if k == 'validator' and isinstance(v, str) and v.startswith('this.'):
                    items.append(f'{k}: {v}')
                elif k == 'trigger':
                    triggers = ', '.join(f"'{t}'" for t in v)
                    items.append(f'{k}: [{triggers}]')
                elif isinstance(v, bool):
                    items.append(f'{k}: {str(v).lower()}')
                elif isinstance(v, int):
                    items.append(f'{k}: {v}')
                else:
                    items.append(f'{k}: \'{v}\'')
            parts.append('{ ' + ', '.join(items) + ' }')
        if len(parts) == 1:
            return parts[0]
        return '[' + ', '.join(parts) + ']'

    def _safe_var_name(self, title, list_fields=None):
        """将中文标题转为安全的变量名片段（如「承包合同编号」→ ContractCode）

        优先用 title 对应的 prop，其次用 list_fields[0] 对应的 prop
        """
        prop = self.mapping.get(title) or self._guess_prop(title)
        if prop and prop != title:
            return prop[0].upper() + prop[1:]
        # title 无可用 prop 时，尝试从 list_fields 的第一个字段推断
        if list_fields:
            first = list_fields[0]
            prop = self.mapping.get(first) or self._guess_prop(first)
            if prop and prop != first:
                return prop[0].upper() + prop[1:]
        # 最终 fallback
        import re as _re
        return _re.sub(r'[^a-zA-Z]', '', title)

    def _find_fuzzy_param(self, fname):
        """根据中文名查找对应的模糊查询参数名"""
        for remark, param in self.api.get('list_fuzzy_params', {}).items():
            if fname in remark or remark in fname:
                return param
        return None

    def _find_advanced_param(self, fname):
        """根据中文名查找对应的高级查询参数名"""
        for remark, param in self.api.get('list_advanced_params', {}).items():
            if fname in remark or remark in fname:
                return param
        return None

    def _guess_prop(self, fname):
        """猜测字段名对应的 prop"""
        if fname in FIXED_FIELD_MAPPINGS:
            return FIXED_FIELD_MAPPINGS[fname]
        # 用已有映射推断
        for cn, en in self.mapping.items():
            if cn in fname or fname in cn:
                return en
        # 拼音猜测
        return self._cn_to_camel(fname)

    def _cn_to_camel(self, cn):
        """中文名简单转驼峰（fallback）"""
        # 去掉括号内容
        cn = re.sub(r'[（）()（）].*$', '', cn)
        return cn

    def _estimate_width(self, fname, info):
        for keyword, width in WIDTH_ESTIMATES:
            if keyword in fname:
                return width
        return WIDTH_DEFAULT

    def _guess_id_key(self, fname, prop):
        """根据字段名推断关联ID字段：contractCode → contractId"""
        # 汇集所有已知 API prop（包括未映射的字段）
        all_api_props = set()
        for src in ['list_response_fields', 'detail_response_fields', 'save_fields',
                     'list_advanced_params']:
            for p in self.api.get(src, {}).values():
                if p:
                    all_api_props.add(p)

        # 1. 精确规则
        candidates = []
        if prop.endswith('Code'):
            candidates.append(prop[:-4] + 'Id')
        if prop.endswith('Number'):
            candidates.append(prop[:-6] + 'Id')
        candidates.append(prop + 'Id')

        for c in candidates:
            if c in all_api_props:
                return c

        # 2. 模糊匹配：寻找共享词干的 Id 字段
        #    例 paperContractNumber → contractId（共享 "contract"）
        for api_prop in all_api_props:
            if api_prop.endswith('Id') or api_prop.endswith('id'):
                stem = api_prop[:-2]
                if len(stem) >= 4 and stem.lower() in prop.lower():
                    return api_prop

        # 3. 中文字段名关键词 → API Id 字段匹配
        #    例 项目编号 → projectId（"项目" 关联 "project"）
        _id_stem_map = {
            '项目': 'project',
            '合同': 'contract',
        }
        for cn_kw, en_stem in _id_stem_map.items():
            if cn_kw in fname:
                for api_prop in all_api_props:
                    if api_prop.lower().endswith('id') and en_stem in api_prop.lower():
                        return api_prop

        return candidates[-1]

    def _guess_nav_code(self, fname):
        """根据字段中文名在 detailRouter.js 中查找对应的跳转编码。

        匹配策略：
        1. 精确匹配注释内容
        2. 关键词在注释中出现（如「承包合同编号」匹配「承包合同列表」的 CBHTCS）
        3. 项目类字段统一返回 XM
        """
        # 项目类字段固定映射
        if any(k in fname for k in ['项目编号', '项目名称', '项目']):
            # 先尝试在 detailRouter 中精确匹配
            pass

        # 去除常见后缀，提取核心业务关键词
        core = re.sub(r'(编号|名称|金额.*|税率|时间|列表|详情)$', '', fname).strip()

        # 策略1：精确匹配 detailRouter 注释
        for comment, nav_code in self._detail_router_map.items():
            if core == comment or fname == comment:
                return nav_code

        # 策略2：关键词包含匹配
        for comment, nav_code in self._detail_router_map.items():
            if core and (core in comment or comment in core):
                return nav_code

        # 策略3：字段名关键词在 comment 中（更宽松）
        for comment, nav_code in self._detail_router_map.items():
            if fname and any(kw for kw in re.split(r'[（）()]', fname) if kw.strip() and kw.strip() in comment):
                return nav_code

        # fallback：项目默认跳 XM
        if any(k in fname for k in ['项目']):
            return 'XM'
        # 合同默认跳 CBHTCS（承包合同列表）
        if '合同' in fname:
            return 'CBHTCS'

        return 'XM'

    def _build_form_row_attrs(self, fname, info, prop):
        """将 get_display_attrs 返回的属性字典转为 Vue 属性字符串"""
        attrs = get_display_attrs(info, fname, self.mapping)
        if attrs is None:
            return None
        parts = []
        for k, v in attrs.items():
            if k.startswith('_') and not k.startswith('_bind_'):
                continue  # 内部标记，不输出为属性
            if k.startswith('_bind_'):
                out_key = k[6:]  # _bind_span → span
                parts.append(f' :{out_key}="{v}"')
            else:
                out_key = k.replace('_', '-')  # row_key → row-key
                if isinstance(v, bool):
                    if v:
                        parts.append(f' {out_key}')
                else:
                    parts.append(f' {out_key}="{v}"')
        return ''.join(parts)

    def _build_form_row_slots(self, fname, info, prop):
        """返回表单行内部的插槽内容（如单位追加、抽屉选择按钮等）"""
        attrs = get_display_attrs(info, fname, self.mapping)
        if attrs is None:
            return ''
        slots = []
        # 单位追加插槽
        if attrs.get('_unit'):
            slots.append(f'          <template #append>{attrs["_unit"]}</template>')
        # 可编辑抽屉 → 选择按钮
        if attrs.get('_drawer_select'):
            slots.append(f'          <template #append>'
                        f'<el-button type="text" @click="show{prop[0].upper() + prop[1:]}Drawer">选择</el-button>'
                        f'</template>')
        return '\n'.join(slots) if slots else ''

    def _build_detail_col_attrs(self, fname, info):
        attrs = get_detail_column_attrs(info, fname)
        parts = []
        for k, v in attrs.items():
            if isinstance(v, bool):
                if v:
                    parts.append(f' {k}')
            else:
                parts.append(f' {k}="{v}"')
        return ''.join(parts)

    def _format_cell(self, cell):
        parts = [f'{{ label: "{cell["label"]}", value: "{cell["value"]}"']
        if cell.get('type'):
            parts.append(f', type: \'{cell["type"]}\'')
        if cell.get('idKey'):
            parts.append(f', idKey: \'{cell["idKey"]}\'')
        if cell.get('code'):
            parts.append(f', code: \'{cell["code"]}\'')
        if cell.get('colSpan'):
            parts.append(f', colSpan: {cell["colSpan"]}')
        parts.append(' }')
        return ''.join(parts)


# ---------------------------------------------------------------------------
# 6. 主流程
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # ── 如果传了 Excel，先调用 excel-parser 解析 ──
    if args.excel:
        print(f"[excel-parser] 开始解析 Excel: {args.excel}")
        # 添加 excel-parser 目录到 sys.path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        excel_parser_dir = os.path.join(script_dir, 'excel-parser')
        if excel_parser_dir not in sys.path:
            sys.path.insert(0, excel_parser_dir)
        from parse_excel import parse_excel as parse_excel_file

        business_name = args.business_name
        if not business_name:
            # 从 Excel 文件名 + API 文档流程 Key 生成业务名称
            code = None
            with open(args.api, 'r', encoding='utf-8') as f:
                content = f.read()
            m = re.search(r'流程Key[：:]\s*(\w+)', content)
            if not m:
                m = re.search(r'(\w*Bill\d+Approval)', content)
            if m:
                flow_key = m.group(1)
                m2 = re.match(r'(\w+)Bill(\d+)Approval', flow_key)
                if m2:
                    code = m2.group(2)
            excel_name = os.path.splitext(os.path.basename(args.excel))[0]
            business_name = f"{excel_name}" if not code else excel_name

        json_data = parse_excel_file(args.excel, business_name)
        print(f"[excel-parser] 解析完成，字段: {len(json_data.get('field_info', {}))} 个")
    else:
        # 读取 JSON
        with open(args.json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

    # 解析接口文档
    api_data = parse_api_doc(args.api)

    if not api_data['code'] and not _DEFAULT_CODE:
        print("[错误] 无法从接口文档或 config.py 获取单据编码（流程Key）", file=sys.stderr)
        sys.exit(1)

    code_source = "API文档" if api_data.get('flow_key') else "config.py"
    print(f"[信息] 单据编码: {api_data['code']}（来源: {code_source}）")
    print(f"[信息] 业务领域: {api_data['col']}（来源: {code_source}）")
    if api_data.get('flow_key'):
        print(f"[信息] 流程Key: {api_data['flow_key']}")

    # 建立字段映射
    mapping, reverse = build_field_mapping(json_data, api_data)
    print(f"[信息] 字段映射: {len(mapping)} 个")

    # 输出目录：默认输出到项目 src/views 下
    if args.output:
        output_dir = args.output
    else:
        # 从当前脚本位置推导项目根目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
        output_dir = os.path.join(project_root, 'src', 'views')

    print(f"[信息] 输出目录: {output_dir}")

    # 生成代码
    gen = CodeGenerator(json_data, api_data, mapping, reverse, output_dir)
    gen.generate_all()

    print("\n[完成] 代码生成完毕!")


if __name__ == '__main__':
    main()
