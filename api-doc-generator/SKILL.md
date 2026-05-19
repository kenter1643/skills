---
name: api-doc-generator
description: 根据 SQL 建表语句和 Excel 需求文档生成 Markdown 格式接口文档。
---

# API 接口文档生成器

执行顺序：

1. **询问用户**：Excel 需求文档路径？SQL 建表语句路径？
2. 未提供任一文件则停止并提示补充。
3. 验证文件存在后执行：

使用方式：

### 方式一：通过 Claude Code Skill（推荐）                                 
    在 Claude Code 中直接调用该 skill，它会引导你输入文件路径并自动生成。例：生成接口文档

### 方式二：
```bash
python main.py "<sql_file>" "<excel_file>" --output "<skill_dir>/output"
```

4. 输出到 `output/业务名称.md`。

## 关键规则

- API 前缀/单据编号从 SQL 表名提取（如 `cm_bill_2808_head` → `/cm/bill/2808`）
- 仅使用"字段说明"sheet，通过中文名匹配 SQL 注释
- SQL 只合并 head/detail 表，info 表用于生成 infoList
- 列表出参 String 类型自动分配导出排序
- 主表包含 `id`（ID）和 `headId`（主单id）
- 明细区域（Excel 第一列以"明细"开头的合并单元格）不参与主信息输出
- infoList 备注使用表 COMMENT，中文括号自动转英文

详见 [README.md](README.md)。
