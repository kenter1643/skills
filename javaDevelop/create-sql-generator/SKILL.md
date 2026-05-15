---
name: sql表设计生成器
description: 根据 Excel 需求文档生成 MySQL 数据库表设计（建表 SQL + 字段注释 + 索引），输出到 output 目录。当用户说"帮我根据 Excel 生成建表 SQL"、"根据需求文档设计表结构"、"生成单据表 SQL"、"生成 head/detail/info 表"，或提供了 .xlsx 需求文档并要求生成数据库设计时，务必使用此 skill。即使用户只说"生成 SQL"并提供了 Excel 路径，也应触发此 skill。
---

# SQL 表设计生成器

根据 Excel 需求文档中的"字段说明" sheet，生成标准的 MySQL 建表 SQL，包含 head 主表、detail 明细表，以及所有 `明细表#XXX` 分区对应的 info 表。

## 工作流程（共 4 步，严格按顺序执行）

---

### 第 1 步：确认领域和编号

**必须先获取以下两个参数，再执行后续步骤：**

| 参数 | 说明 | 示例 |
|------|------|------|
| 领域（domain） | 业务模块英文前缀 | `fam`（固定资产）、`plm`（项目）、`con`（合同） |
| 编号（bill_no） | 单据编号，4位数字 | `1735` |

**处理规则：**
- 如果用户已在消息中提供了领域和编号，直接使用，跳到第 2 步。
- 如果用户未提供，**必须明确提示用户输入**，不要猜测或使用默认值：

```
请提供以下信息后再继续：
- 领域（domain）：业务模块英文前缀，例如 fam、plm、con
- 编号（bill_no）：单据编号，例如 1735
```

- 如果用户明确表示不知道或不需要，**中断 skill**，提示：

```
领域和编号未确定，无法生成表名。请确认后重试。
```

---

### 第 2 步：读取 Excel 字段说明

**找到用户提供的 Excel 文件路径**（可能在用户消息中直接给出，或在当前目录下）。

运行 `parse_excel.py` 脚本读取 Excel：

```bash
python <skill_dir>/scripts/parse_excel.py "<excel_path>" > <skill_dir>/temp/fields.json
```

其中 `<skill_dir>` 是本 skill 目录的绝对路径（即 SKILL.md 所在目录）。执行前确保 `temp/` 目录存在：

```bash
mkdir -p <skill_dir>/temp
```

**脚本行为：**
- 自动查找所有包含"字段说明"的 sheet（支持多个 sheet）
- 识别分区标题行，据此将字段归类：
  - `主表` / `head` → head 表
  - `明细表` / `detail` → detail 表
  - `明细表#XXX` / `明细表（XXX）` → info 表（命名为 明细表#XXX）
  - `附表N-XXX`（如 `附表1-合同项目明细`）→ 自动识别为 info 分区（明细表#XXX）
- 无独立分区标题时，按分组列关键词归类：
  - `表头`/`单头`/`基础信息`/`基本信息` → 主表（head）
  - 其余分组（如`项目信息`/`合同信息`/`其他信息`等）→ 明细表（detail）
  - `附表N-XXX` 标题行之后的字段 → info 表（明细表#XXX）
- 自动推断 MySQL 字段类型（参见脚本内 `resolve_type` 函数）
- 输出 JSON 到 stdout

**如果脚本报错：**
- 提示用户检查 Excel 文件路径是否正确
- 提示确认是否存在包含"字段说明"的 sheet
- 如果 `openpyxl` 未安装，提示：`pip install openpyxl`

**读取成功后，向用户展示字段统计摘要：**
```
[OK] 读取到 XX 个字段：
  - 主表：X 个业务字段
  - 明细表：X 个业务字段
  - 明细表#资产信息：X 个字段
  ...
```

---

### 第 3 步：生成建表 SQL

运行 `generate_sql.py` 脚本：

```bash
python <skill_dir>/scripts/generate_sql.py "<domain>" "<bill_no>" "<business_name>" "<skill_dir>/temp/fields.json"
```

其中 `<business_name>` 从 Excel 文件名中提取（去掉路径和扩展名），例如 `固定资产销售.xlsx` → `固定资产销售`。

**脚本生成规则（严格遵守）：**

#### 字段名规范（snake_case 英文翻译）
字段名使用 `field_label`（中文名）的**英文语义翻译**，格式为小写 snake_case：
- 由 Excel 原始字段翻译英文后缩写转 snake_case，批量翻译，简洁准确，反映字段业务含义
- 例：`入库类型` → `storage_in_type`，`含税金额（元）` → `tax_incl_amt`，`推送反馈` → `push_feedback`
- 常见缩写保留：id、no、qty、amt、tax、type、code、name、status、date、flag

#### COMMENT 规则
- 只使用 `field_label`（中文名称列）作为注释内容，简洁清晰
- 若字段是枚举型，在中文名后拼接枚举值：`'入库类型，1、采购入库 2、加工入库...'`
- 不拼接备注、说明等冗余信息
- COMMENT 内容中的换行符（`\n`、`\r`）一律替换为空格，避免 SQL 语法错误

#### Head 表（主表）
- 表名格式：`{domain}_bill_{bill_no}_head`
- **完整保留 28 个标准字段，一字不改**
- Excel 中"主表"分区的业务字段**不添加到 head 表**（head 表纯标准字段）

#### Detail 表（明细表）
- 表名格式：`{domain}_bill_{bill_no}_detail`
- 前 12 个标准字段完整保留（id、head_id、project_id、FXMBH、FXMMC、FZTMCID、FZTMC、FXMLX、fcontract_type、FSSZZID、FSSZZ、project_properties）
- Excel 中"明细表"分区的业务字段插入标准字段之后、尾部字段之前
- **字段名去重规则（双重过滤）**：
  1. 字段名（小写）已在标准字段集中 → 跳过
  2. `field_label`（中文名）语义与标准字段相同 → 跳过。标准字段已覆盖的语义：项目编号、项目名称、账套编号、账套名称、项目类型、合同类型、所属组织编号、所属组织、项目属性
  3. 例：Excel 中的 `FGSMCID（所属组织编号）` 和 `FGSMC（所属组织）`，因语义与标准字段 `FSSZZID`/`FSSZZ` 重复，**不生成**
- 尾部固定：`is_deleted`、`gmt_create`、`gmt_modified`、`PRIMARY KEY (id)`
- 末尾添加：`CREATE INDEX index_head_id ON {table} (head_id);`

#### Info 表（明细表#XXX）
- 每个 `明细表#XXX` 分区生成一张 info 表
- 表名格式：`{domain}_bill_{bill_no}_info`（若有多个 info 表，在 skill 外协商命名后缀）
- 结构：id、head_id、业务字段、is_deleted、gmt_create、gmt_modified、PRIMARY KEY
- 末尾添加：`CREATE INDEX index_head_id ON {table} (head_id);`
- **过滤规则**：head 标准字段不重复添加

**字段冲突处理：**
若 Excel 字段名与标准模板字段功能相同但命名不同（如 Excel 有 `create_time`，标准是 `gmt_create`），保留标准字段，忽略 Excel 字段。

---

### 第 4 步：输出 SQL 文件

脚本自动将 SQL 写入：

```
<skill_dir>/output/<bill_no>.<business_name>.sql
```

**向用户报告结果：**

```
[OK] SQL 已生成：<输出文件绝对路径>

生成内容：
  - {domain}_bill_{bill_no}_head（主表，28个标准字段）
  - {domain}_bill_{bill_no}_detail（明细表，12个标准字段 + X个业务字段）
  - {domain}_bill_{bill_no}_info（info表，X个字段）  ← 如有
```

同时在对话中展示生成的 SQL 内容，方便用户直接预览。

---

### 第 5 步：历史表关联字段分析

SQL 文件生成后，运行 `check_history.py` 脚本自动扫描历史表并输出关联分析报告：

```bash
python <skill_dir>/scripts/check_history.py "<output_sql_path>"
```

历史目录默认为 `database/V1.0相关版本/0-已发版/`，也可手动指定：

```bash
python <skill_dir>/scripts/check_history.py "<output_sql_path>" "<history_dir>"
```

**脚本处理逻辑：**
1. 解析目标 SQL 中 detail/info 表的业务字段（跳过标准字段）
2. 扫描历史目录下所有 `.sql` 文件，按字段 `COMMENT` 中文名做精确子串匹配
3. 对匹配到的字段：
   - 若历史表中存在配对的 `_id bigint` 关联字段（如 `contract_id`），建议在当前字段前插入
   - 若当前字段名与历史统一命名不同（如 `paper_contract_no` vs `paper_contract_number`、`line_no` vs `row_no`），建议对齐
4. 向用户展示匹配结果，**等待确认后**写入 SQL 文件

**输出示例：**
```
[历史关联分析] 以下字段在历史表中存在关联，建议添加或对齐：

Detail 表：
  ✓ 承包合同编号（contract_no）
    → 建议在其前添加：`contract_id` bigint DEFAULT NULL COMMENT '承包合同id，来源：cms_contact_base.id'
  ✓ 纸质合同编号（paper_contract_no）
    → 字段名建议对齐历史：`paper_contract_no` → `paper_contract_number`

Info 表：
  ✓ 行号（line_no）
    → 字段名建议对齐历史：`line_no` → `row_no`

请确认是否执行以上所有建议？（回复"是"/"全部"执行全部，或指定编号）
```

**已内置的关联规则（`KNOWN_ID_FIELDS`）：**
| 中文名 | 插入的关联字段 | 来源说明 |
|--------|--------------|---------|
| 承包合同编号 | `contract_id bigint` | `cms_contact_base.id` |

**已内置的字段名对齐规则（`FIELD_NAME_ALIGN`）：**
| 当前字段名 | 对齐为 |
|-----------|--------|
| `paper_contract_no` | `paper_contract_number` |
| `line_no` | `row_no` |

> 若后续发现新的关联规则或命名对齐需求，直接更新 `check_history.py` 中的 `KNOWN_ID_FIELDS` 和 `FIELD_NAME_ALIGN` 两个字典即可。

---

## 脚本说明

脚本位于 `scripts/` 目录：

| 脚本 | 作用 |
|------|------|
| `parse_excel.py` | 读取 Excel，提取字段说明，输出 JSON |
| `generate_sql.py` | 读取 JSON，按标准模板生成建表 SQL |
| `check_history.py` | 扫描历史 SQL，分析关联字段并建议添加/对齐，写入 SQL 文件 |
| `inspect_excel.py` | 调试用：打印 Excel 所有 sheet 及字段说明内容 |

**依赖：**
```bash
pip install openpyxl
```

---

## 字段类型推断规则

`parse_excel.py` 按以下优先级推断 MySQL 类型：

1. Excel 中已填写标准类型（如 `varchar(50)`、`decimal(24,8)`）→ 直接使用
2. Excel 中填写类型关键词（如 `datetime`、`金额`、`整型`）→ 映射到对应 MySQL 类型
3. 根据字段中文名推断：
   - 含"金额/价格/税率/数量" → `decimal(24,8)`
   - 含"时间/日期/年月" → `datetime`
   - 含"是否/状态/类型/属性"（≤6字） → `tinyint`
   - 含"id/编号/编码"（不含"名"） → `varchar(50)`
   - 含"名称/姓名" → `varchar(200)`
   - 含"说明/备注/描述" → `varchar(2000)`
4. 默认 → `varchar(200)`

---

## 常见问题

**Q: Excel 中没有"字段说明" sheet 怎么办？**
提示用户确认 sheet 名称，或手动指定包含字段清单的 sheet 名。

**Q: 字段没有分区标题，全在一个 sheet 里怎么办？**
`parse_excel.py` 默认将所有字段归为"明细表"分区，detail 表会包含这些字段。

**Q: 需要生成多个 info 表怎么办？**
在 Excel 字段说明 sheet 中用 `明细表#资产信息`、`明细表#变更明细` 等分区标题区分，每个分区自动生成一张 info 表。生成时命名规则需与用户确认（如 `_info`、`_info2` 等后缀）。
