---
name: excel-parser
description: 解析 Excel 需求文档（字段说明），输出结构化 JSON 数据。适用于用户提供 .xlsx 文件，希望提取模糊查询、高级查询、列表字段、字段说明、录入样式等信息的场景。
---

# Excel 解析器

将 Excel 需求文档解析为结构化 JSON 数据。

## 执行方式

在 skill 目录执行：

```bash
python parse_excel.py "<excel_file>" [--output "<output_dir>"]
```

参数说明：
- `excel_file`：必填，Excel 文件路径
- `--output` / `-o`：输出目录，默认 `output`
- `--business-name` / `-b`：业务名称，默认从文件名提取
- `--compact` / `-c`：紧凑 JSON 输出（不美化）


## 前提条件

- Excel 文件必须包含「字段说明」sheet（名称含"字段说明"）

## 输出说明

解析完成后输出到 `output/` 目录：
- `<业务名称>.json`：完整的结构化 JSON 数据

## JSON 输出结构

```json
{
  "business_name": "业务名称",
  "fuzzy_search": ["字段1", "字段2"],
  "advanced_search": ["字段1", "字段2", "字段3"],
  "list_order_fields": ["字段1", "字段2", "字段3", "字段4"],
  "field_info": {
    "字段名": {
      "is_required": true,
      "is_enum": false,
      "enum_values": "",
      "field_type": "文本型",
      "display_type": "选择框",
      "data_generation": "系统自动生成；",
      "data_check": "数据格式要求",
      "field_requirement": "字段说明"
    }
  },
  "input_style": {
    "main": [
      {
        "title": "分组标题",
        "fields": ["字段1", "字段2"]
      }
    ],
    "details": ["明细区字段"],
    "info_lists": [
      {
        "title": "区域标题",
        "fields": ["字段1", "字段2"]
      }
    ],
    "drawers": [
      {
        "title": "抽屉标题",
        "fuzzy_search": [],
        "advanced_search": [],
        "list_fields": []
      }
    ]
  }
}
```

## 解析规则

- **字段说明 sheet**：
动态扫描表头列，提取文档列字段(分组信息	字段名称	字段类型	表单展现	数据生成方式	数据检查要求(校验规则）	字段说明	是否列表字段	列表顺序	查询方式	是否可编辑	是否必填	是否枚举	枚举内容
)，表单展现列为隐藏的行过滤掉，用分组信息列区分主表和明细表，
特殊列规则：
1、分组信息列：对所有字段进行分组，是input_style.main的分组标题；
2、表单展现列：值包含"隐藏"的行过滤掉，值包含"下拉"的行display_type输出为select，值包含“文本”的行输出为text，值包含"日期"的行输出为date，值包含"数字"的行输出为number，值包含"复选框"的行输出为checkbox，值包含"单选框"的行输出为radio，值包含"多行文本"的行输出为textarea，值包含"附件"的行输出为file，值包含"按钮"的行输出为button，值包含“抽屉”的行输出为drawer，值包含“弹窗”的行输出为dialog，值包含“导入”的行输出为import；
3、根据是否列表列和列表排序列输出列字段名数组list_order_fields，取列表字段为是的列字段名，根据列表顺序排序输出；
4、查询方式列：值包含"模糊"的行输出为fuzzy_search，值包含"高级"的行输出为advanced_search；
5、是否可编辑列：是为true，否为false，输出到field_info.字段名.is_editable；
6、是否必填列：是为true，否为false，输出到field_info.字段名.is_required；
7、是否枚举列：是为true，否为false，输出到field_info.字段名.is_enum；
