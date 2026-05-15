---
name: javaDevelop
description: 专业的 Java 后端开发工程师 skill。当用户说"生成后端代码"、"运行代码生成器"、"根据接口文档补全代码"、"补全 ListVO/ListParam/xml 查询条件"，或提供了接口文档要求完善后端代码时，使用此 skill。
---

# javaDevelop后端开发

专业 Java 后端开发 skill，分两个阶段执行：
1. 运行 MyBatis Plus 代码生成器生成骨架代码
2. 根据用户提供的接口文档，补全 `/list` 接口相关的 XML 查询条件、ListVO 出参字段、ListParam 入参字段

---

## 前置说明

本 skill 的核心文件已整合在 `references/mybatis-generator/` 目录下，结构如下：

```
references/mybatis-generator/
├── start/
│   ├── MyBatisPlusGeneratorV2.java      # 代码生成器入口（唯一需要修改配置的文件）
│   └── EnhanceFreemarkerTemplateEngine.java  # 自定义 Freemarker 引擎（不需修改）
└── templates/
    ├── dto/dto.java.ftl
    ├── v2/
    │   ├── head/   controller / service / serviceImpl / mapper / mapper.xml / entity / head_sql.sql
    │   ├── detail/ service / serviceImpl / mapper / mapper.xml / detailVo
    │   ├── info/   service / serviceImpl / mapper / mapper.xml
    │   └── vo/     listVo / listParam / detailVo / InfoVo
```

实际执行时，生成器读取的是项目中的文件（`construct-star-generator/src/main/resources/templates/`），references 目录仅作为阅读参考，展示模板结构供 AI 分析。

---

## 阶段一：运行代码生成器

### 第 1 步：收集配置参数

在执行之前，**必须**确认 `MyBatisPlusGeneratorV2.java` 中以下静态变量已由用户正确配置：

| 变量 | 说明 | 示例 |
|------|------|------|
| `projectPath` | 生成包路径（代码输出到哪个子模块） | `construct-star-contract`、`construct-star-system` |
| `territory` | 领域名（英文模块前缀） | `cbo`、`fam`、`plm` |
| `territoryCode` | 业务单据编号（4 位数字） | `1699`、`1813` |
| `tableName[]` | 需要生成代码的表名数组 | `{"cbo_bill_1699_head", "cbo_bill_1699_detail"}` |
| `isBillTable` | 是否为单据主表模式 | `true` / `false` |
| `url` | 数据库连接 JDBC URL | `jdbc:mysql://...` |
| `username` | 数据库账号 | `root` |
| `password` | 数据库密码 | — |
| `parentMenuId` | 菜单父级 ID | `100` |
| `menuName` | 菜单名称 | `协同办公其他类` |
| `enumKey` | 业务枚举 Key（用于流程、待办、导出等） | `HNTYS`、`JTFSQ` |

**如果用户没有提供上述信息，询问用户需要修改哪些参数，待确认后再执行。**

如果用户明确说"直接运行"且配置已存在，跳过此步。

### 第 2 步：同步 references 副本到实际生成器文件

**在运行生成器之前，必须先将 references 副本的内容覆盖写入实际生成器文件。**

两个文件路径：
- **副本（用户维护的配置）**：`<skill_dir>/references/mybatis-generator/start/MyBatisPlusGeneratorV2.java`
- **实际生成器文件**：`<project_root>/construct-star-generator/src/main/java/com/construct/generator/start/MyBatisPlusGeneratorV2.java`

执行覆盖写入：读取副本文件的完整内容，原样写入实际生成器文件（完全覆盖）。

写入完成后，向用户确认：
```
[同步完成] references 副本已同步到实际生成器文件：
  territory     = <值>
  territoryCode = <值>
  tableName[]   = <值>
  projectPath   = <值>
```

**如果写入失败（权限问题或路径不存在），立即中断并提示用户手动复制。**

---

### 第 3 步：运行生成器

同步完成后，通知用户在 IDE 中打开实际生成器文件并运行 `main` 方法：

```
请在 IDE 中打开以下文件，右键运行 main 方法：
<project_root>/construct-star-generator/src/main/java/com/construct/generator/start/MyBatisPlusGeneratorV2.java

运行完成后，请告知我执行结果（成功/报错信息），再继续下一步。
```

等待用户回复执行结果：

- **用户回复成功**：询问用户生成了哪些文件路径，或根据 `projectPath` / `territory` / `territoryCode` 推断，进入阶段二。
- **用户回复报错**：**立即中断**，将错误信息分析后提示用户可能原因：
  - 数据库连接失败：检查副本中的 `url` / `username` / `password`
  - 表不存在：确认 `tableName[]` 中的表名在数据库中存在
  - 编译错误：检查依赖或 JDK 版本
  - 端口/网络问题：确认数据库服务可访问

  ```
  ❌ 代码生成器执行失败，错误信息：
  <用户提供的错误堆栈>

  可能原因：<分析原因>
  请修复 references 副本后重新执行第 2 步。
  ```

其中 `<project_root>` 为项目根目录（含 `pom.xml` 的目录）。

**执行结果处理：**

- **成功**：向用户报告生成了哪些文件，列出文件路径，进入阶段二。
- **报错**：**立即中断**，将完整错误信息展示给用户，提示可能原因：
  - 数据库连接失败：检查 `url` / `username` / `password`
  - 表不存在：确认 `tableName[]` 中的表名拼写正确
  - 编译错误：检查依赖或 JDK 版本
  - 端口/网络问题：确认数据库服务可访问

  ```
  ❌ 代码生成器执行失败，错误信息：
  <完整错误堆栈>

  可能原因：<分析原因>
  请修复后重新执行。
  ```

---

## 阶段二：根据接口文档补全代码

**触发条件**：用户提供了接口文档（Markdown / 文字描述 / 截图文字），要求补全 `/list` 接口相关代码。

阶段一成功生成代码后自动进入；或用户单独触发（已有生成代码，只需补全）。

---

### 第 3 步：定位生成的文件

根据 `projectPath`、`territory`、`territoryCode` 以及表名（`_head` 表），定位以下四个文件并**全部读取**：

| 文件                   | 路径规律                                                                                                      |
|----------------------|-----------------------------------------------------------------------------------------------------------|
| `*ListVO.java`       | `<project_root>/{projectPath}/src/main/java/com/construct/{territory}/vo/{EntityName}ListVO.java`         |
| `*ListParam.java`    | `<project_root>/{projectPath}/src/main/java/com/construct/{territory}/vo/{EntityName}ListParam.java`      |
| `*DetailMapper.xml`  | `<project_root>/{projectPath}/src/main/resources/mapper/{territory}/{EntityName}DetailMapper.xml`（`getBillList` 在此文件） |
| `BaseListParam.java` | `construct-star-system/src/main/java/com/construct/component/service/vo/BaseListParam.java`（用于排重）         |

> **注意**：`getBillList` 查询方法生成在 `DetailMapper.xml` 中，不在 `HeadMapper.xml` 中。

---

### 第 4 步：解析接口文档

从用户提供的接口文档中提取：

**`/list` 接口入参字段（对应 `ListParam`）：**
- 字段名（Java camelCase）
- 字段类型（Java 类型）
- 字段说明/注释
- 是否为模糊查询字段（含 `like`、`模糊` 关键词）
- 是否为范围查询字段（含 `开始/结束`、`begin/end`、`Between` 等）

**`/list` 接口出参字段（对应 `ListVO`）：**
- 字段名（Java camelCase）
- 字段类型（Java 类型）
- 字段说明/注释
- 是否需要 Excel 导出（接口文档标注导出列）

---

### 第 5 步：差异对比与缺失识别

**以接口文档为准**，逐一对比：

#### 5a. ListParam 入参对比

**必须先读取 `BaseListParam.java` 的字段列表**，路径：`construct-star-system/src/main/java/com/construct/component/service/vo/BaseListParam.java`。

检查接口文档中的每个入参字段是否已存在于 `ListParam.java` 或 `BaseListParam.java`：
- 已存在于任一父类 → 标记 `✓（父类已有）`，**不生成**
- 不存在 → 标记为**待补充**，记录字段名、类型、注释

#### 5b. ListVO 出参对比

**以接口文档出参字段为准，全量对比**（不考虑继承关系，接口文档有的都要补）：
- 字段已存在于 `ListVO.java` → 标记 `✓`
- 不存在 → 标记为**待补充**，记录字段名、类型、注释
- `*Str` 文本字段（如 `billDateStr`、`declareDateStr`、`isFirstReviewStr`）也需一并补充，不能遗漏

#### 5c. XML 查询条件对比

`getBillList` 方法位于 `DetailMapper.xml`，不在 `HeadMapper.xml`。

对比范围仅限两处，**其余 SQL 结构不得修改**：
1. `<!--todo:动态生成detail表其他字段的查询条件-->` 区块：补充接口文档中属于 detail 表的业务字段查询条件
2. `<!--生成模糊查询-->` 的 `<choose>` 块：补充接口文档中业务专属的模糊查询字段 `<when>` 分支

**查询方式判断规则：**
- String 字段（模糊）→ `LIKE CONCAT('%',#{fieldName},'%')`，`<if>` 条件加 `and fieldName != ''`
- String 字段（精确/状态/枚举）→ `= #{fieldName}`，`<if>` 条件只判 `!= null`
- Integer/tinyint → `= #{fieldName}`，`<if>` 条件只判 `!= null`
- Date 范围字段（beginXxx/endXxx）→ `BETWEEN #{beginXxx} and #{endXxx}`，两个字段同在一个 `<if>` 中判断
- head 表字段用 `h.` 前缀，detail 表字段用 `d.` 前缀

**`<choose>` 模糊查询补充规则：**
- BaseListParam 已有的模糊字段（`firstBillCode`、`firstFsszz`、`firstFxmmc`、`firstKeyWord`）已在模板中生成，**不重复添加**
- 接口文档中业务专属的模糊字段（如 `firstContractCode`、`firstContractName`）在 `firstKeyWord` 的 `<when>` **之前**插入新 `<when>` 分支

向用户展示对比报告后询问确认：

```
[差异分析报告]

ListParam 缺失字段（X 个）：
  - String createUserName  // 创建人姓名（模糊查询）
  - ...

ListVO 缺失字段（X 个）：
  - String projectName  // 项目名称（需导出：@ExcelProperty）
  - ...

XML 缺失查询条件（X 个）：
  - createUserName → LIKE 模糊查询
  - ...

是否执行以上全部补全？（回复"是"/"全部"执行全部，或指定字段名单独处理）
```

---

### 第 6 步：执行补全

用户确认后，依次修改三个文件：

#### 补全 ListParam.java

在 `// todo: 维护列表查询入参--业务字段` 注释下方，按区块添加**业务专属**缺失字段：
- 模糊查询区块（`/*********模糊查询字段****************/`）：只添加 BaseListParam 中没有的模糊字段（如 `firstContractCode`、`firstContractName`）
- 高级查询区块（`/*********高级查询字段*******************/`）：添加精确/范围查询的业务字段
- **BaseListParam 已有的字段一律不写**（已有：`firstKeyWord`、`firstBillCode`、`firstFsszz`、`firstFxmmc`、`billCode`、`billStatus`、`createUserName`、`initiateName`、`initiateUserName`、`billBeginDate`、`billEndDate`、`fxmmc`、`fxmbh`、`fztmcid`、`fztmc`、`fsszz`、`fsszzid` 等）
- 需要 `Date` 类型字段时，确认文件顶部已有 `import java.util.Date`，没有则补上

每个字段加 Javadoc 注释：
```java
/**
 * 字段说明
 */
private FieldType fieldName;
```

#### 补全 ListVO.java

在已有字段末尾（`/******************* *******************/` 区块之后）添加缺失字段：
- 接口文档出参有的字段，当前文件没有的，全部补充
- `*Str` 文本字段（如 `billDateStr`、`declareDateStr`）也要补，紧跟对应原始字段之后
- 需要 Excel 导出的字段加 `@ExcelProperty(value = "列名", index = N)`，index 从当前最大值 +1 递增
- 普通字段只加 Javadoc 注释

#### 补全 XML 查询条件（DetailMapper.xml）

**只修改以下两处，其余 SQL 不动：**

**① `<!--todo:动态生成detail表其他字段的查询条件-->` 区块**

在此注释下方，按接口文档入参补充 detail 表的业务字段查询，格式示例：

```xml
<!-- String 模糊查询 -->
<if test="contractCode != null and contractCode != ''">
    and d.contract_code LIKE CONCAT('%',#{contractCode},'%')
</if>

<!-- Integer 精确查询 -->
<if test="isFirstReview != null">
    and d.is_first_review = #{isFirstReview}
</if>

<!-- String 精确查询（状态/枚举） -->
<if test="validStatus != null and validStatus != ''">
    and d.valid_status = #{validStatus}
</if>

<!-- Date 范围查询 -->
<if test="declareBeginDate != null and declareEndDate != null">
    and d.declare_date BETWEEN #{declareBeginDate} and #{declareEndDate}
</if>
```

**② `<!--生成模糊查询-->` 的 `<choose>` 块**

在 `firstKeyWord` 的 `<when>` 之前，插入业务专属模糊字段的 `<when>` 分支：

```xml
<when test="firstContractCode != null and firstContractCode != ''">
    AND d.contract_code LIKE CONCAT('%',#{firstContractCode},'%')
</when>
```

---

### 第 7 步：输出结果

所有修改完成后，向用户汇报：

```
[完成] 已补全以下内容：

ListParam.java（+X 个字段）：
  ✓ String createUserName  // 创建人姓名
  ...

ListVO.java（+X 个字段）：
  ✓ String projectName  // 项目名称
  ...

mapper.xml（+X 个查询条件）：
  ✓ createUserName → LIKE 模糊查询
  ...

文件路径：
  - <ListParam 绝对路径>
  - <ListVO 绝对路径>
  - <Mapper XML 绝对路径>
```

---

## 阶段二·续：补全 checkParam 必传校验

阶段二完成后自动执行；或用户单独触发。

在 `*HeadServiceImpl.java` 的 `checkParam` 方法中，`// todo:处理需数据校验参数` 注释下方补充必传字段校验。

---

### 第 7.5 步：解析 /save 接口必传字段

从接口文档的 `/save` 入参表格中，提取 `是否必传 = 是` 的字段，分两类处理：

**顶层必传字段（直接校验 `param.getXxx()`）：**
- `BigDecimal` / `Long` / `Integer` 等非 String 类型 → `AssertUtils.notNull(param.getXxx(), "Xxx不能为空")`
- `String` 类型 → `AssertUtils.notBlank(param.getXxx(), "Xxx不能为空")`

**infoList 子项必传字段（循环校验）：**
- 若 `infoList` 子项中有业务关键字段（如 `subjectId`、`subjectCode`、`subjectName`），即使接口文档标注 `否`，也需按业务语义判断是否加入循环校验
- 循环模式固定写法：
```java
for ({EntityName}InfoVO info : param.getInfoList()) {
    AssertUtils.notNull(info.getXxx(), "Xxx不能为空");
    AssertUtils.notBlank(info.getXxx(), "Xxx不能为空");
}
```

校验代码插入位置：`// todo:处理需数据校验参数` 注释**下方**，紧接已有校验行之后。

示例（以 2809 为例）：
```java
// todo:处理需数据校验参数
AssertUtils.notNull(param.getProjectRate(), "项目税率不能为空");
AssertUtils.notBlank(param.getFxmlx(), "项目类型不能为空");
for (CmBill2809InfoVO info : param.getInfoList()) {
    AssertUtils.notNull(info.getSubjectId(), "收入科目不能为空");
    AssertUtils.notBlank(info.getSubjectCode(), "收入科目编号不能为空");
    AssertUtils.notBlank(info.getSubjectName(), "收入科目名称不能为空");
}
```

**注意事项：**
- `AssertUtils` 需已导入，若未导入则在文件顶部添加对应 import
- `{EntityName}InfoVO` 需已导入，若未导入则补充 import
- 循环体内只校验业务上真正必填的字段，不盲目校验所有字段

---

## 阶段三：生成枚举

阶段二完成后自动执行；或用户单独触发。

需要在以下三个枚举文件的 `// todo-start: skill生成数据区` 与 `// todo-end: skill生成数据区` 之间插入枚举值，**严禁写到 todo 区域以外**。

---

### 枚举 Key 构成规则

`enumKey` 由 `MyBatisPlusGeneratorV2.java` 中的 `enumKey` 变量直接取得（如 `HNTYS`）。

各枚举参数含义：

| 参数 | 来源 / 规则 |
|------|-----------|
| `enumKey` | 直接取自生成器配置的 `enumKey` 变量 |
| `enumName` | 直接取自生成器配置的 `enumName` 变量（业务中文名） |
| `billTitle` | `enumName + "单"`，即业务名称加"单"字 |
| `flowKey` | 生成规则：`{territory}Bill{territoryCode}Approval`（首字母不大写，驼峰拼接），例：`cmBill2809Approval` |
| `headTable` | 主表表名：`{territory}_bill_{territoryCode}_head` |
| `territoryCode` | 直接取自生成器配置的 `territoryCode` 变量（4 位数字） |
| `serialCode` | 与 `territoryCode` 相同（整型） |
| `fileEnumKey` | 格式：`{enumKey}_BILL_BID` |
| `fileDesc` | 格式：`{enumName}-附件上传` |

---

### 第 8 步：写入 BillTypeEnum

文件：`construct-star-common/src/main/java/com/construct/common/enums/BillTypeEnum.java`

在 `// todo-start: skill生成数据区` 与 `// todo-end: skill生成数据区` 之间插入：

```java
{enumKey}("{enumKey}", "{enumName}", "{billTitle}", "{flowKey}", "{headTable}", "{territoryCode}"),
```

示例：
```java
HNTYS("HNTYS", "施工图预算变更", "施工图预算变更单", "cmBill2809Approval", "cm_bill_2809_head", "2809"),
```

---

### 第 9 步：写入 SysSerialNumEnum

文件：`construct-star-common/src/main/java/com/construct/common/enums/SysSerialNumEnum.java`

在 `// todo-start: skill生成数据区` 与 `// todo-end: skill生成数据区` 之间插入：

```java
{enumKey}_CODE({territoryCode}, "{enumKey}", "{enumName}"),
```

示例：
```java
HNTYS_CODE(2809, "HNTYS", "施工图预算变更"),
```

---

### 第 10 步：写入 CboFileEnum

文件：`construct-star-common/src/main/java/com/construct/common/enums/cbo/CboFileEnum.java`

在 `// todo-start: skill生成数据区` 与 `// todo-end: skill生成数据区` 之间插入：

```java
{enumKey}_BILL_BID("{enumKey}_BILL_BID", "{enumName}-附件上传", "{headTable}"),
```

示例：
```java
HNTYS_BILL_BID("HNTYS_BILL_BID", "施工图预算变更-附件上传", "cm_bill_2809_head"),
```

---

### 第 11 步：输出结果

```
[完成] 枚举已写入：

BillTypeEnum：
  ✓ {enumKey}("{enumKey}", "{enumName}", "{billTitle}", "{flowKey}", "{headTable}", "{territoryCode}")

SysSerialNumEnum：
  ✓ {enumKey}_CODE({serialCode}, "{enumKey}", "{enumName}")

CboFileEnum：
  ✓ {enumKey}_BILL_BID("{enumKey}_BILL_BID", "{fileDesc}", "{headTable}")
```

---

## 注意事项

- 阶段一若执行失败，**严禁继续执行阶段二**，必须先让用户修复报错。
- 补全时以接口文档为准：接口文档有而代码没有 → 补；代码有而接口文档没有 → **不删除**（可能是框架内置字段）。
- **ListParam 严禁重复添加 BaseListParam 已有字段**，每次执行前必须读取 BaseListParam 做排重。
- **ListVO 以接口文档出参为全量基准**，`*Str` 文本字段不能遗漏，无需考虑父类排重。
- **XML 只改两处**：`<!--todo:动态生成detail表其他字段的查询条件-->` 区块 和 `<choose>` 模糊查询块，其余 SQL 结构一律不动。
- `getBillList` 方法在 `DetailMapper.xml` 中，不在 `HeadMapper.xml` 中。
- XML 中 head 表字段用 `h.` 前缀，detail 表字段用 `d.` 前缀，根据字段来源正确区分。
- `<choose>` 中业务专属模糊字段的 `<when>` 插在 `firstKeyWord` 之前，保证 `firstKeyWord` 作为兜底分支。
- **XML 补全后须做反向校验**：逐一检查 `<!--todo:动态生成detail表其他字段的查询条件-->` 区块中每个 `<if>` 的参数名，若该参数在 `ListParam`（含 `BaseListParam`）中不存在，则**删除该 `<if>` 块**，避免运行时参数绑定失败。
- **checkParam 必传校验**：从 `/save` 接口入参表格提取 `是否必传 = 是` 的字段，在 `// todo:处理需数据校验参数` 下方添加 `AssertUtils` 校验；infoList 子项的业务关键字段（`subjectId`、`subjectCode`、`subjectName` 等）须用 for 循环遍历 `param.getInfoList()` 逐项校验。
