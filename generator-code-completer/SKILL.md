---
name: generator-code-completer
description: >-
  当用户需要补充/调整 MyBatisPlusGeneratorV2 生成的代码，或用户提供接口文档 markdown 文件来对齐生成代码时，使用此技能。
  本技能处理：补充 HeadServiceImpl 中缺失的方法，根据接口文档（含排序号列）调整 getBillList/getBillDetail 的 SQL 和 VO 字段，
  从 headSql.sql 中添加枚举值到 BillTypeEnum/SysSerialNumEnum/CboFileEnum，
  为 Date/Integer/BigDecimal 类型创建带 @ExcelProperty 注解的 Str 字段，
  以及用 saveOperateFile/getOperateFile 方法补全 OperateFileService。
---

# Generator Code Completer

本 Skill 用于在 MyBatisPlusGeneratorV2 生成初始代码后，根据接口文档(.md)批量补充和调整代码。

## 使用说明

### 第一步：创建数据表

在数据库中执行 `单据.sql` 文件，生成对应的数据表（head 表和 detail 表）。

### 第二步：生成初始代码

在 `MyBatisPlusGeneratorV2` 中调整对应的领域（territory）、表名、编号（code），然后执行 `MyBatisPlusGeneratorV2` 中的 `main` 方法，生成初始的 Service、Controller、VO、Mapper XML 等代码。

### 第三步：执行代码补充技能

准备好对应的 `单据接口文档.md` 文件，输入文档路径并执行 `/generator-code-completer` 技能，即可根据接口文档自动补充和调整生成的代码。

---

## 前置条件

确保当前项目有以下目录结构（MyBatisPlusGeneratorV2 生成后的标准结构）：
- `construct-star-contract/src/main/java/com/construct/<territory>/service/impl/*HeadServiceImpl.java`
- `construct-star-contract/src/main/java/com/construct/<territory>/service/*HeadService.java`
- `construct-star-contract/src/main/java/com/construct/<territory>/service/*OperateFileService.java`
- `construct-star-contract/src/main/java/com/construct/<territory>/service/impl/*OperateFileServiceImpl.java`
- `construct-star-contract/src/main/java/com/construct/<territory>/vo/`
- `construct-star-contract/src/main/java/com/construct/<territory>/sqlData/headSql.sql`
- `construct-star-contract/src/main/resources/mapper/<territory>/*DetailMapper.xml`
- `construct-star-admin/src/main/java/com/construct/web/controller/<territory>/*HeadController.java`
- `construct-star-common/src/main/java/com/construct/common/enums/BillTypeEnum.java`
- `construct-star-common/src/main/java/com/construct/common/enums/SysSerialNumEnum.java`
- `construct-star-common/src/main/java/com/construct/common/enums/cbo/CboFileEnum.java`
- `construct-star-common/src/main/java/com/construct/common/enums/<territory>/<Territory>Bill<code>Enum.java`

## 工作流程

按以下顺序执行每个步骤。每步完成后报告结果再继续。

---

### Step 0: 获取输入文件

1. 如果用户已在消息中提供了接口文档 .md 文件路径，直接使用；否则**提示用户输入接口文档 .md 文件的路径**
2. 使用 Read 工具读取接口文档 .md 内容

---

### Step 1: 解析接口文档

从接口文档中提取以下信息：

**1a. 提取元信息：**
- **流程Key**: 从 `## 流程Key：xxx` 行提取（如 `cmBill2806Approval`）
- **领域 territory**: 从第一个 URL 的路径段提取（如 `/cm/bill/2806/list` → `cm`）
- **编号 code**: 从 URL 路径中提取（如 `/cm/bill/2806/list` → `2806`）
- **首字母大写的领域**: 用于类名前缀（如 `cm` → `Cm`）

**1b. 提取接口列表：**
遍历每个 `###` 标题区块（如 `### 单据列表`），解析：
- HTTP 方法和 URL 路径（如 `GET /cm/bill/2806/list`）
- URL 的最后一段作为接口名（如 `list`, `detail`, `save`, `yesOrNoLabel`）
- `#### 入参说明` 下的表格：字段名、类型、备注
- `#### 出参说明` 下的表格：字段名、类型、备注
- **对于"单据列表"区块的出参表**，额外解析 **排序号** 列（第4列），用于后续 `@ExcelProperty(index = N)` 的生成

注意：
- 跳过 `#### 出参示例` 代码块（内容通常为空）
- 模糊查询和高级查询都属于入参，注意表格中的分组标题行（如 `模糊查询 |  |  |`）

---

### Step 2: 定位所有生成的文件

根据 Step 1 提取的 territory 和 code，使用 Glob 搜索定位以下文件：

```
# HeadServiceImpl
construct-star-contract/**/service/impl/*Bill<code>HeadServiceImpl.java

# HeadService 接口
construct-star-contract/**/service/*Bill<code>HeadService.java

# DetailMapper.xml
construct-star-contract/**/mapper/<territory>/*Bill<code>DetailMapper.xml

# Controller
construct-star-admin/**/controller/<territory>/*Bill<code>HeadController.java

# ListVO
construct-star-contract/**/vo/*Bill<code>HeadListVO.java

# ListParam
construct-star-contract/**/vo/*Bill<code>HeadListParam.java

# DetailVO (可能是 *DetailVO.java 或 *HeadDetailVO.java)
construct-star-contract/**/vo/*Bill<code>*DetailVO.java

# headSql.sql
construct-star-contract/**/sqlData/headSql.sql

# OperateFileService 接口和实现
construct-star-contract/**/service/*OperateFileService.java
construct-star-contract/**/service/impl/*OperateFileServiceImpl.java

# 枚举文件（固定路径）
construct-star-common/**/enums/BillTypeEnum.java
construct-star-common/**/enums/SysSerialNumEnum.java
construct-star-common/**/enums/cbo/CboFileEnum.java

# 领域业务枚举（Step 6d 创建）
construct-star-common/**/enums/<territory>/<Territory>Bill<code>Enum.java
```

使用 Read 工具读取所有定位到的文件。

---

### Step 3: 补充 HeadServiceImpl 方法

**目标**: 找出接口文档中有但 HeadServiceImpl 中缺失的接口，为其生成方法骨架。

**操作步骤：**

1. 列出接口文档中所有接口的 URL 最后一段（如 `list`, `detail`, `save`, `delete`, `revocation`, `audit`, `deliver`, `export`, `checkParam`, `yesOrNoLabel`）

2. 建立 URL 路径到方法名的映射规则：
   - `list` → `getBillList`
   - `detail` → `getBillDetail`
   - `save` → `saveBill`
   - `delete` → `deleteBill`
   - `revocation` → `revocation`
   - `audit` → `auditBill`
   - `deliver` → `deliver`
   - `export` → `export`
   - `checkParam` → `checkParam`
   - 其他（如 `yesOrNoLabel`）→ 直接使用该名称作为方法名

3. 检查 HeadServiceImpl 中是否已存在对应方法（搜索方法签名），找出缺失的方法

4. 对于每个缺失的方法，在 HeadServiceImpl 类中生成方法骨架。**同时也要在 HeadService 接口中添加方法声明。**

**生成方法骨架的规则：**
- 如果接口是 GET 类型且有入参表：生成带参数的方法，参数类型根据入参确定
- 如果接口是 POST 类型且有入参表：生成接收对应 VO 参数的方法
- 如果接口无入参：生成无参方法
- 方法体需要：
  - 添加 `// todo: 根据接口文档实现业务逻辑` 注释
  - 如果有返回值，返回 `null` 或合适的默认值
- 参考 HeadServiceImpl 中已有方法的注解风格（`@Override`, `@Transactional` 等）

**重要：区分接口类型 — 下拉接口 vs 业务接口**

根据接口文档的出参判断接口类型：
- **下拉/标签类接口**（出参为 id/label 键值对列表，如 `yesOrNoLabel`、`receiveStatusLabel`）
  → 直接写在 **Controller** 中，**不在 HeadServiceImpl/HeadService 中添加**
- **业务逻辑类接口**（如 `saveBill`、`auditBill`、`deleteBill`）
  → 写在 **HeadServiceImpl** 中，同时在 **HeadService** 接口中声明

**下拉接口示例（yesOrNoLabel）— 写在 Controller**：
```java
/**
 * 下拉-是否
 *
 * @return
 */
@GetMapping("/yesOrNoLabel")
public AjaxResult yesOrNoLabel() {
    return AjaxResult.success(CommonEnum.YesOrNoEnum.getIdLabelList());
}
```

参照 `MmsBill1673HeadController` 中的 `receiveStatusLabel`、`hasPushLabel` 等下拉接口模式。

> **Controller 路径**：`construct-star-admin/src/main/java/com/construct/web/controller/<territory>/`  
> 使用 Glob 搜索定位：`construct-star-admin/**/controller/<territory>/*Bill<code>HeadController.java`

---

### Step 4: 调整 getBillList

根据接口文档中 "单据列表" 区块的出参表（含排序号列）进行调整。涉及三个文件的修改。

#### 4a. 确定 ListVO 需要的字段

**字段来源**：接口文档"单据列表"出参表。

1. 遍历出参表中的每个字段
2. **有排序号**的字段 → 需要 `@ExcelProperty` 导出，保留对应的原始字段和 Str 字段
3. **无排序号**的字段 → 不加 `@ExcelProperty`，保留原始字段声明供 SQL 数据映射

确定字段后，判断每个字段的类型：
- 字段在 Head 实体或 Detail 实体中 → 记录其 Java 类型（Date / Integer / BigDecimal / String）
- String 类型 → 直接作为导出字段
- **Date / Integer / BigDecimal 类型 → 必须创建对应的 `*Str` 字段**（见 4c）

**4a-补充：检查 BaseListVO 基类字段（避免重复声明）**

为避免在子类 ListVO 中重复声明，在确定字段列表后必须检查 BaseListVO 基类：

1. 使用 Read 工具读取 BaseListVO（路径：`construct-star-system/src/main/java/com/construct/component/service/vo/BaseListVO.java`），获取其声明的所有字段名
2. 对每个待添加的字段，将文档字段名转 camelCase 后，在 BaseListVO 字段列表中搜索
3. 如果 BaseListVO 已有同名 field → **不重复声明**，直接复用基类字段
4. 常见已存于 BaseListVO 的字段（勿重复声明）：
   - `id`, `billStatus`, `billType`, `createUserId`, `createUserName`, `createDate`, `isPromoter`
   - `initiateType`, `initiateId`, `initiateName`, `initiateDeptId`, `initiateDeptName`
   - `initiateProjectId`, `initiateProjectName`, `initiateUserId`, `projectId`, `rowNo`
5. **重要例外**：`billStatus` 在 BaseListVO 中已有，但 `billStatusStr`（含 `@ExcelProperty` 注解）仍需在子类 ListVO 中声明。其他 `*Str` 字段同理——原始字段在基类，Str 字段在子类。

#### 4b. 调整 Mapper XML 的 getBillList SQL 输出字段

根据 4a 确定的字段列表，重新构建 `<select id="getBillList">` 的 SELECT 子句。

**规则：**
1. `*Str` 类型字段（如 `billDateStr`、`billStatusStr`）→ **不需要在 SQL 中查出**，VO 中通过 getter 从原始字段格式化得到
2. 为每个非 Str 字段确定数据库列来源和别名：
   - 读取 Head 实体和 Detail 实体的字段，找到匹配的属性
   - 字段名转 snake_case 后匹配数据库列名（如 `billCode` → `bill_code`）
   - 字段在 Head 实体中 → 来源 `h.<column> AS <fieldName>`
   - 字段在 Detail 实体中 → 来源 `d.<column> AS <fieldName>`
3. 必须保留的辅助字段：`isPromoter` 计算列、各 Integer/Date/BigDecimal 原始字段（用于其 Str getter 格式化）
4. 如果文档中的字段在实体中找不到对应列，在 VO 中标记 `// todo: 确认数据来源`

#### 4c. 调整 ListVO 字段和 @ExcelProperty 注解

**参照文件**：`NrmBill1612HeadListVO`（详见 `references/nrm-bill1612-listvo.md`）

**核心原则**：所有用于 Excel 导出的 `@ExcelProperty` 注解**全部放在 `*Str` 字段上**，原始 Date/Integer/BigDecimal 字段**不加 `@ExcelProperty`**，仅用于 SQL 数据映射。

**排序号来源**：从接口文档"单据列表"出参表的 **排序号** 列获取。该列只有列表出参表才有（第4列），详情和其他接口的出参表没有此列。

**排序号重映射规则（98/99/100 固定末尾列处理）**：

1. 从出参表中提取所有排序号，分为两组：
   - **自定义排序号**：< 98 的数值（如 1, 2, 3, ..., 10）
   - **固定末尾列**：98, 99, 100（固定最后3列）
2. 计算 `maxCustom` = 自定义排序号中的最大值（如 10）
3. 映射到 `@ExcelProperty(index)`：
   - 排序号 < 98 → `index = 排序号`（直接使用）
   - 排序号 = 98 → `index = maxCustom + 1`
   - 排序号 = 99 → `index = maxCustom + 2`
   - 排序号 = 100 → `index = maxCustom + 3`
4. 排序号为空的字段 → **不加 `@ExcelProperty`**

**处理流程**：
1. 根据接口文档出参表的**备注**列设置 `@ExcelProperty(value = "备注内容")`
2. 根据上述重映射规则计算 `@ExcelProperty(index = N)`
3. 对于长文本列（编号、名称、金额等）添加 `@ColumnWidth(21)`，普通列使用类级别 `@ColumnWidth(14)`
4. 根据字段类型生成对应的原始字段 + Str 字段 + getter（见下方规则表）

**字段类型处理规则**：

| 类型 | 原始字段（不加注解） | Str 字段（加 @ExcelProperty） | getter 实现 |
|------|---------------------|------------------------------|-------------|
| Date | `private Date billDate;` | `@ExcelProperty private String billDateStr;` | 见日期 getter 模板 |
| BigDecimal | `private BigDecimal htje;` | `@ExcelProperty private String htjeStr;` | 见金额 getter 模板 |
| Integer(单据状态) | `private Integer billStatus;` | `@ExcelProperty private String billStatusStr;` | `WFAuditStatusEnum.get(billStatus).getName()` |
| Integer(是否) | `private Integer sfyfk;` | `@ExcelProperty private String sfyfkStr;` | `CommonEnum.YesOrNoEnum.get(...).getName()` |
| Integer(自定义枚举) | `private Integer payStatus;` | `@ExcelProperty private String payStatusStr;` | `XxxEnum.PayStatusEnum.get(...).getName()` |
| String | — | `@ExcelProperty private String xxx;` | 直接使用，不需要 Str |

**注意**：`billStatus` 来自 BaseListVO，不在子类中重复声明；但 `billStatusStr` 需要在子类中声明并加 `@ExcelProperty`。

**日期 getter 模板**：
```java
public String getBillDateStr() {
    if (ObjectUtil.isNotEmpty(billDate)) {
        SimpleDateFormat sf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return sf.format(billDate);
    }
    return StringUtils.NOT_DATA;
}
```

**金额 getter 模板**：
```java
public String getHtjeStr() {
    if (ObjectUtil.isNotEmpty(this.htje)) {
        return ParameterUtils.amountStrHandler(htje);
    }
    return StringUtils.NOT_DATA;
}
```

**Integer 枚举 getter 模板**：
```java
public String getPayStatusStr() {
    if (ObjectUtil.isNotEmpty(payStatus)) {
        XxxEnum.PayStatusEnum anEnum = XxxEnum.PayStatusEnum.get(payStatus);
        return anEnum != null ? anEnum.getName() : StringUtils.NOT_DATA;
    }
    return StringUtils.NOT_DATA;
}
```

#### 4d. 调整 ListParam 字段和 Mapper XML 查询条件

以文档入参表（模糊查询 + 高级查询）为准。

**4d-0：检查基类字段（避免重复声明）**

在向子类 ListParam 添加字段前，必须先检查 BaseListParam 和 BaseEntity 基类：

1. 使用 Read 工具读取：
   - BaseListParam（路径：`construct-star-system/src/main/java/com/construct/component/service/vo/BaseListParam.java`）
   - BaseEntity（路径：`construct-star-common/src/main/java/com/construct/common/core/domain/BaseEntity.java`）
2. 记录两个基类中声明的所有字段名（包括 Lombok `@Data` 生成的字段和手动声明的字段）
3. 对接口文档入参表的每个字段，将文档字段名转 camelCase 后，在基类字段列表中搜索
4. 如果基类已有同名 field → **不重复声明**，直接复用基类字段
5. 常见已存于 BaseListParam/BaseEntity 的字段（勿重复声明）：
   - `billCode`, `billType`, `billStatus`, `billBeginDate`, `billEndDate`
   - `createUserName`, `initiateName`, `initiateUserName`
   - `fxmmc`, `fxmbh`, `fztmcid`, `fztmc`, `fsszz`, `fsszzid`
   - `createBeginDate`, `createEndDate`, `updateBeginDate`, `updateEndDate`
   - `searchValue`, `createBy`, `createTime`, `updateBy`, `updateTime`, `remark`, `params`, `prop`, `order`

**特殊注意**：`billBeginDate`/`billEndDate` 在 BaseListParam 中已声明并配有 `beginOfDay`/`endOfDay` 的 getter 方法，子类直接继承即可，**不需要重写字段或 getter**，除非子类需要不同的日期粒度。

1. **调整 ListParam**: 添加文档入参中有但 ListParam 中没有的查询参数字段（已排除基类已有的字段）
2. **调整 Mapper XML 查询条件**: 根据入参中的每个字段，在 `<select id="getBillList">` 中生成对应的 `<if>` 条件块：
   - 模糊查询字段（`first*`）→ 放在 `<choose>` 块中
   - 高级查询字段 → 放在对应的 `<if>` 块中
   - String 类型用 `LIKE CONCAT('%',#{param},'%')`
   - 删除文档入参中没有的查询条件

3. **为 ListParam 每个字段添加 Javadoc 注释**: 从接口文档入参表的"备注"列提取中文描述，以多行格式添加到每个字段上方：
   ```java
   /**
    * 单据编号
    */
   private String firstBillCode;
   ```

   注释规则：
   - 模糊查询字段（`first*`）和高级查询字段（同名不带 `first`）使用相同的备注文本
   - `billBeginDate`/`billEndDate` 分别使用各自的备注（如"制单时间开始"/"制单时间结束"）
   - `billStatus` 等枚举字段的注释需包含完整枚举值映射（从接口文档入参表或 save 入参表中获取，如 `单据状态：-1-审批不通过；0-草稿；1-审批中；2-已完成；3-撤回`）
   - 注释文本直接取自对应接口入参说明表格的"备注"列值，不做额外处理

**4d-Date：Date 字段时间处理 getter**

对于 ListParam 中每个 Date 类型的查询字段（格式 `xxxBeginDate`/`xxxEndDate`），必须添加时间处理 getter 方法，确保前端传入的日期字符串被正确转换为当天/当月的起止时间，以便 SQL BETWEEN 查询能覆盖完整范围。

**参照模板**：`FmBill1702HeadListParam`（路径：`construct-star-contract/src/main/java/com/construct/fm/vo/FmBill1702HeadListParam.java`）中的 `getBelongBeginDate()` / `getBelongEndDate()` 方法结构。

**操作步骤**：

1. 检查 ListParam 子类中新增的 Date 字段（已在基类中存在且有 getter 的字段不重复处理，如 `billBeginDate`/`billEndDate` 在 BaseListParam 中已有 `beginOfDay`/`endOfDay` getter）
2. 为每对 Date 字段生成 getter 方法，**默认使用天级别粒度**：

```java
public Date getXxxBeginDate() {
    if (ObjectUtil.isNotEmpty(xxxBeginDate)) {
        return DateUtil.beginOfDay(xxxBeginDate);
    }
    return null;
}

public Date getXxxEndDate() {
    if (ObjectUtil.isNotEmpty(xxxEndDate)) {
        return DateUtil.endOfDay(xxxEndDate);
    }
    return null;
}
```

**规则**：
- 默认统一使用 `DateUtil.beginOfDay()` / `DateUtil.endOfDay()`（天级别）
- 如果 Date 字段已在 BaseListParam 或 BaseEntity 中存在且有对应的 getter 方法 → **不重写**，直接继承
- 新增的 import：`import cn.hutool.core.date.DateUtil;` 和 `import cn.hutool.core.util.ObjectUtil;`（检查是否已存在）

**getter 方法必须放在 Lombok `@Data` 注解之外**（因为 `@Data` 只生成字段的默认 getter/setter，手动编写的 getter 会覆盖 Lombok 生成的默认 getter）。

---

### Step 5: 调整 getBillDetail

根据接口文档中 "单据详情" 区块的出参表进行调整。

#### 5a. 调整 Mapper XML 的 getBillDetail SQL 输出字段

与 Step 4a 类似的规则：
1. 解析文档出参表，区分主表字段和嵌套字段（如 `infoList` 是嵌套列表，`fileList` 是文件列表）
2. 为每个主表出参字段确定数据库列来源（head 表或 detail 表）
3. `fileList`、`infoList`、`cmBill2806Info`、`alter` 等不是数据库直接列出的字段不放入 SQL SELECT
4. 重新构建 SELECT 列表，只包含文档列出的数据库字段

#### 5b. 调整 DetailVO 字段

以接口文档 "单据详情" 出参表为准，判断 DetailVO 是否缺少字段。

1. 比较 DetailVO 已有字段与文档出参
2. 文档中有的保留/新增，文档中没有的删除（注意：不能删除基类 BaseDetailVO 中的字段）
3. **Str 字段规则**（参照 Step 4c ListVO 规则）：

   **重要：每个 `*Str` 字段必须同时添加字段声明和 getter 方法，缺一不可！**
   字段声明写在类体中，getter 方法写在类体中——两者都需要显式声明。

   以 billDate（Date 类型）为例，完整处理方式：
   ```java
   private Date billDate;              // 原始字段，检查 BaseDetailVO 后确认已有，不需重复
   private String billDateStr;         // ← 必须声明 Str 字段
   public String getBillDateStr() {    // ← 必须实现 getter
       if (ObjectUtil.isNotEmpty(billDate)) {
           SimpleDateFormat sf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
           return sf.format(billDate);
       }
       return StringUtils.NOT_DATA;
   }
   ```

   以 billStatus（Integer 枚举类型）为例：
   ```java
   private Integer billStatus;         // 原始字段 — DetailVO 继承链中无此字段，必须显式声明！
   private String billStatusStr;       // ← 必须声明 Str 字段
   public String getBillStatusStr() {  // ← 必须实现 getter
       if (ObjectUtil.isNotEmpty(billStatus)) {
           WFAuditStatusEnum anEnum = WFAuditStatusEnum.get(billStatus);
           return anEnum != null ? anEnum.getName() : StringUtils.NOT_DATA;
       }
       return StringUtils.NOT_DATA;
   }
   ```

   各类型的完整处理：

   | 类型 | 字段声明 | getter 实现 |
   |------|---------|-------------|
   | Date | `private Date xxx;` + `private String xxxStr;` | `SimpleDateFormat("yyyy-MM-dd HH:mm:ss")` |
   | BigDecimal | `private BigDecimal xxx;` + `private String xxxStr;` | `ParameterUtils.amountStrHandler()` |
   | Integer 枚举 | `private Integer xxx;` + `private String xxxStr;` | `XxxEnum.get(xxx).getName()` |
   | Integer 是否 | `private Integer xxx;` + `private String xxxStr;` | `CommonEnum.YesOrNoEnum.get(xxx).getName()` |

   getter 均返回 `StringUtils.NOT_DATA` 而非 null。
4. 确保 `fileList` 和 `infoList` 字段存在

**注意**：DetailVO 不涉及 `@ExcelProperty` 注解（导出在 ListVO 处理）。

**关键规则：ListVO 与 DetailVO 的继承链不同，不可混淆！**
- **ListVO** → `BaseListVO`（含 `billStatus`）→ billStatus **不需**在 ListVO 子类中重复声明
- **DetailVO** → `BaseDetailVO` → `AuditPublicVO` → `BaseEntity`（**均不含** `billStatus`）→ billStatus **必须**在 DetailVO 子类中显式声明
- 生成 DetailVO 的 `*Str` getter 前，**必须先读取完整的父类继承链**，确认原始字段是否存在。不能仅凭 ListVO 的经验来推断 DetailVO。

---

### Step 5.5: 补充 saveBill 的 checkParam 字段必填校验

**目标**: 将 HeadServiceImpl 中 `checkParam` 方法里的 `// todo:处理需数据校验参数` 替换为具体的字段必填校验代码。

**参照文件**：`FamBill2732HeadServiceImpl.checkParam`（位于 `construct-star-contract/**/fam/service/impl/FamBill2732HeadServiceImpl.java`）

**校验模式（参照 FamBill2732HeadServiceImpl）**：

| 校验方式 | 工具方法 | 使用场景 |
|---------|---------|---------|
| 多字段组校验 | `ObjectUtil.hasEmpty(...)` | 多个字段共享同一个错误信息时，如"请先进行项目立项再做单" |
| 单字段校验 | `AssertUtils.notNull(field, "错误提示")` | 每个字段独立错误信息 |
| 嵌套列表校验 | `for` 循环 + `AssertUtils.notNull` | infoList 子字段逐项校验 |

**操作步骤**：

1. **解析接口文档"单据保存"入参表**，提取所有标记为"是"（必传）的字段及其备注：
   - 只看 `#### 入参说明` 下的表格，"是否必传" 列为 "是" 的行
   - 跳过 `filesList`（附件一般标记为"否"，无需校验）
   - 区分主表字段和 `infoList` 子字段

2. **生成错误提示文案**：以备注为基准，去掉末尾的 "id"、"编号" 等后缀，加"不能为空"：
   - "承包合同id" → "承包合同不能为空"
   - "成本科目编号" → "成本科目编号不能为空"
   - "成本科目名称" → "成本科目名称不能为空"

3. **生成校验代码**，插入到 `checkParam` 方法中 `// todo:处理需数据校验参数` 的位置：
   - 每个必填字段：`AssertUtils.notNull(param.getXxx(), "备注不能为空");`
   - infoList 列表本身：`AssertUtils.notNull(param.getInfoList(), "计划明细不能为空");`
   - infoList 子字段：放在 `for (XxxInfoVO info : param.getInfoList())` 循环内

4. **不修改已有的校验逻辑**（initiateId/initiateType 和项目立项校验保持不动）

5. **添加必要的 import**：`import com.construct.common.utils.AssertUtils;`

**示例 — 针对 2806 单据保存入参**：

对于入参表：

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| contractId | Long | 是 | 承包合同id |
| contractCode | String | 是 | 承包合同编号 |
| paperContractNumber | String | 是 | 纸质合同编号 |
| contractName | String | 是 | 合同名称 |
| htje | BigDecimal | 是 | 合同总金额 |
| infoList | List | 是 | 计划明细 |
| subjectId | Long | 是 | 成本科目id |
| subjectCode | String | 是 | 成本科目编号 |
| subjectName | String | 是 | 成本科目名称 |
| content | String | 是 | 成本科目备注 |

生成的校验代码应插入到 `checkParam` 方法的 `// todo:处理需数据校验参数` 位置：

```java
AssertUtils.notNull(param.getContractId(), "承包合同不能为空");
AssertUtils.notNull(param.getContractCode(), "承包合同编号不能为空");
AssertUtils.notNull(param.getPaperContractNumber(), "纸质合同编号不能为空");
AssertUtils.notNull(param.getContractName(), "合同名称不能为空");
AssertUtils.notNull(param.getHtje(), "合同总金额不能为空");
AssertUtils.notNull(param.getInfoList(), "计划明细不能为空");
for (CmBill2806InfoVO info : param.getInfoList()) {
    AssertUtils.notNull(info.getSubjectId(), "成本科目不能为空");
    AssertUtils.notNull(info.getSubjectCode(), "成本科目编号不能为空");
    AssertUtils.notNull(info.getSubjectName(), "成本科目名称不能为空");
    AssertUtils.notNull(info.getContent(), "成本科目备注不能为空");
}
```

**注意事项**：
- 如果 infoList 子 VO 类型名不确定，从 `DetailVO` 的 `infoList` 字段声明中获取泛型类型
- 如果接口文档的 save 入参表中没有标记为"是"的业务字段（除项目立项相关外），则此步骤不需要修改 checkParam
- 此步骤在 Step 5（DetailVO 最终确定）之后执行，保证所有字段引用正确

---

### Step 6: 添加枚举值

#### 6a. 从 headSql.sql 解析枚举定义

headSql.sql 文件中有三行枚举定义（在 SQL 注释后面）：
```
-- BillTypeEnum
CBKMDJ("CBKMDJ", "项目成本科目登记单", "项目成本科目登记单单", "cmBill2806Approval","cm_bill_2806_head", "2806"),
-- SysSerialNumEnum
CBKMDJ_CODE(2806, "CBKMDJ", "项目成本科目登记单"),
-- CboFileEnum
CBKMDJ_BILL_BID("CBKMDJ_BILL_BID", "项目成本科目登记单-附件上传", "cm_bill_2806_head"),
```

从这三行中提取：
- BillTypeEnum 的枚举名称（如 `CBKMDJ`）和完整参数
- SysSerialNumEnum 的枚举名称（如 `CBKMDJ_CODE`）和完整参数
- CboFileEnum 的枚举名称（如 `CBKMDJ_BILL_BID`）和完整参数

请注意 headSql.sql 实际上是一个 Java 类文件（有 package 声明），枚举定义在类体中的注释里。

#### 6b. 添加到三个枚举文件

**警告：此步骤不可跳过！** 必须用 Grep 工具分别搜索三个枚举文件，实际确认枚举值是否存在。**不要依赖记忆或之前运行的印象**，枚举值可能已被 linter/IDE 自动移除。

对每个枚举值执行以下操作：

1. **使用 Grep 工具搜索**枚举类中是否已存在同名的枚举常量（搜索 headSql.sql 中提取的枚举名称，如 `CBKMDJ`）：
   ```
   Grep pattern="CBKMDJ" path="<枚举文件路径>" output_mode="content"
   ```
2. 如果搜索结果为 **No matches found**，则在枚举类的最后一个有效值之后、分号 `;` 之前添加
3. 如果搜索结果**已有匹配**，跳过该枚举值
4. 添加完成后，**再次用 Grep 验证**新枚举值确实已写入

**BillTypeEnum 添加格式**（在末尾 `;` 前）：
```java
<ENUM_NAME>("<key>", "<name>", "<title>", "<flowKey>", "<headTable>", "<objectCode>"),
```

**SysSerialNumEnum 添加格式**（在末尾 `;` 前）：
```java
<ENUM_NAME>(<key>, "<code>", "<name>"),
```

**CboFileEnum 添加格式**（在末尾 `;` 前）：
```java
<ENUM_NAME>("<key>", "<name>", "<tableName>"),
```

#### 6c. 验证 HeadServiceImpl 中的枚举引用

**同样不可跳过！** 必须读取 HeadServiceImpl 文件，检查以下三个字段的值：

```java
private BillTypeEnum serviceEnum = BillTypeEnum.<ENUM_NAME>;
private SysSerialNumEnum billCodeEnum = SysSerialNumEnum.<ENUM_NAME>_CODE;
private String fileEnumKey = CboFileEnum.<ENUM_NAME>_BILL_BID.getKey();
```

验证规则：
1. 读取 HeadServiceImpl，找到这三个字段的声明行
2. 如果字段值使用了 `todo` 占位符或不正确的枚举名，替换为 headSql.sql 中对应的枚举引用
3. 如果字段值已正确，确认并报告

#### 6d. 创建领域业务枚举（参照 MmsBill1673Enum）

当出现以下场景时需要创建领域专属的业务枚举类：
1. ListVO/DetailVO 中存在 Integer 类型的枚举字段（如 `printStatus`、`payStatus`）
2. Controller 中需要下拉接口（如 `orderStatusLabel`），但现有通用枚举中找不到对应类型

**枚举类完整路径**：`construct-star-common/src/main/java/com/construct/common/enums/<territory>/<Territory>Bill<code>Enum.java`

例如：`construct-star-common/src/main/java/com/construct/common/enums/cm/CmBill2806Enum.java`

**参照**：`MmsBill1673Enum.java`（路径：`construct-star-common/src/main/java/com/construct/common/enums/mms/MmsBill1673Enum.java`）

**注意**：`<territory>` 目录可能不存在（如 `cm` 目录），需要先通过 `mkdir` 创建目录再创建枚举文件。

**模板结构（参照 MmsBill1673Enum 中的 orderStatusEnum）**：
```java
package com.construct.common.enums.<territory>;

import com.construct.common.domain.IdLabel;
import com.construct.common.enums.IEnum;

import java.util.ArrayList;
import java.util.List;

/**
 * @desc: <业务名称>枚举类
 **/
public class <Territory>Bill<code>Enum {

    /**
     * 订单状态
     */
    public enum orderStatusEnum implements IEnum {

        // todo: 补充具体状态值

        ;

        private Integer key;
        private String name;

        @Override
        public Integer getKey() {
            return this.key;
        }

        @Override
        public String getName() {
            return this.name;
        }

        orderStatusEnum(Integer key, String name) {
            this.key = key;
            this.name = name;
        }

        public static orderStatusEnum get(Integer key) {
            for (orderStatusEnum e : orderStatusEnum.values()) {
                if (e.getKey().equals(key)) {
                    return e;
                }
            }
            return null;
        }

        public static List<IdLabel> getIdLabelList() {
            List list = new ArrayList();
            for (orderStatusEnum e : orderStatusEnum.values()) {
                list.add(new IdLabel(e.getKey(), e.getName()));
            }
            return list;
        }
    }
}
```

**枚举创建决策流程**：
1. 检查文档出参中的 Integer 字段（如 `printStatus`、`payStatus`）或下拉接口
2. 根据 JavaDoc 注释或接口名判断字段含义
3. 搜索项目中是否已有对应枚举（如搜索 `PrintStatusEnum`、`PayStatusEnum`）
4. 如果没有，在枚举目录下创建 `<Territory>Bill<code>Enum.java`（先创建目录）
5. 创建时参照 `MmsBill1673Enum` 的格式：每个内部枚举实现 `IEnum`，包含 key/name/get/getIdLabelList
6. 在 ListVO 和 DetailVO 中添加对应的 import 并使用
7. 在 Controller 中添加对应的下拉接口（参照 Step 3 的下拉接口模式）

---

### Step 7: 补充 OperateFileService

参考 `references/nrm-operate-file-service.md` 中的模板实现。

#### 7a. 检查 OperateFileService 接口

检查 `*OperateFileService.java` 接口是否声明了以下两个方法：
- `void saveOperateFile(String businessType, Long businessId, List<BaseFile> files)`
- `List<BaseFile> getOperateFile(String businessType, Long businessId)`

**如果缺失**，在接口中添加方法声明（含完整 Javadoc 注释）。需要新增 import：
```java
import com.construct.common.domain.BaseFile;
import java.util.List;
```

#### 7b. 检查 OperateFileServiceImpl 实现类

检查 `*OperateFileServiceImpl.java` 是否实现了这两个方法。

**如果缺失**，参照 `references/nrm-operate-file-service.md` 中的完整实现添加：
1. 将模板中的 `NrmOperateFile` 全部替换为当前的实体类名（如 `CmOperateFile`）
2. 需要新增的 import：
   ```java
   import cn.hutool.core.util.ObjectUtil;
   import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
   import com.construct.common.domain.BaseFile;
   import com.construct.common.enums.CommonEnum;
   import org.springframework.beans.BeanUtils;
   import java.util.ArrayList;
   import java.util.List;
   import java.util.Map;
   import java.util.function.Function;
   import java.util.stream.Collectors;
   ```
3. 实现 `saveOperateFile`: 使用差集比对策略（新增的插入，删除的移除，已有的不动）
4. 实现 `getOperateFile`: 按 businessType + businessId 查询，将实体拷贝为 BaseFile 返回

如果方法已存在，跳过此步骤。

---

## 完成报告

所有步骤完成后，总结所做的修改：
1. HeadServiceImpl 新增了哪些方法
2. getBillList 的 SQL/ListVO/ListParam 做了哪些调整
3. getBillDetail 的 SQL/DetailVO 做了哪些调整
4. 在哪些枚举文件中添加了什么值
5. 是否创建了领域业务枚举类
6. OperateFileService 是否补充了方法
