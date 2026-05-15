---
name: webDevelop
description: 专业的Vue前端开发工程师skill。当用户说"生成前端代码"、"运行Vue代码生成器"、"根据接口文档补全前端代码"、"生成Vue页面"、"前端代码生成"，或提供了接口文档要求完善Vue前端代码，或需要填充前端接口URL时，务必使用此skill。即使用户只说"生成前端"或"跑一下生成器"并处于construct-star-server项目中，也应触发此skill。
---

# webDevelop — Vue前端代码生成工程师

本skill分两个阶段完成工作：
1. **代码生成**：运行 `VueJsCodeGenerator.java` 生成Vue/JS模板代码
2. **接口填充**：根据用户提供的接口文档，在生成代码中补全接口URL及相关逻辑

---

## 前置说明：关键文件位置

所有参考文件已内置在本skill的 `references/` 目录下：

```
references/
├── generator-java/
│   ├── VueJsCodeGenerator.java        # 生成器入口，包含所有可调参数
│   └── VueFreemarkerTemplateEngine.java  # 自定义模板引擎（输出路径路由逻辑）
├── vue-templates/
│   ├── index.vue.ftl     # 审批列表列组件模板
│   ├── add.vue.ftl       # 新增/编辑表单页模板
│   └── detailIndex.vue.ftl  # 详情页subTable渲染模板
└── js-templates/
    ├── ellipsis.js.ftl   # 详情展示数据结构模板（核心）
    └── list.js.ftl       # 列表页JS入口（require ellipsis）
```

在开始任何操作前，先读取 `references/generator-java/VueJsCodeGenerator.java` 了解当前配置的参数（territory、territoryCode、tableName、数据库连接等）。

---

## 阶段一：运行代码生成器

### Step 1 — 确认/修改生成器参数

读取 `VueJsCodeGenerator.java`，向用户展示当前的关键参数：

| 参数 | 当前值 | 说明 |
|------|--------|------|
| `territory` | cbo | 领域名，影响包名和路径 |
| `territoryCode` | 1699 | 业务编号，影响路径和组件名 |
| `tableName[]` | cbo_bill_1699_detail/sub/info | 要扫描的数据库表 |
| `url` | jdbc:mysql://... | 数据库连接地址 |
| `frontendProjectPath` | ../construct-star-web | 前端项目相对路径 |

如果用户提供了新的参数（新的业务编号、新的表名等），**先修改源文件**中对应的常量，再执行生成。

### Step 2 — 执行生成器

在 `construct-star-generator` 模块根目录下，用Maven运行 `VueJsCodeGenerator` 的 main 方法：

```bash
cd /path/to/construct-star-generator
mvn compile exec:java \
  -Dexec.mainClass="com.construct.generator.start.VueJsCodeGenerator" \
  -Dexec.classpathScope="compile"
```

**也可以直接在IDE中右键运行 `VueJsCodeGenerator.java` 的 main 方法。**

若用户更倾向于IDE运行，提示：
> 请在IDEA中打开 `VueJsCodeGenerator.java`，直接运行 main 方法。运行完成后将控制台输出粘贴给我。

### Step 3 — 处理错误

若生成器报错，**立即中断**后续流程，向用户说明：
- 报错的完整原因（从控制台输出中提取）
- 最可能的原因（数据库连接失败、表名不存在、路径找不到等）
- 建议的修复方式

**常见错误及处理：**

| 错误关键字 | 原因 | 建议 |
|-----------|------|------|
| `Communications link failure` / `Connection refused` | 数据库无法连接 | 检查数据库IP、端口、是否启动 |
| `Table 'xxx' doesn't exist` | 表名配置错误或表未创建 | 确认tableName[]与数据库实际表名一致 |
| `Unknown column` | 表结构与代码不匹配 | 检查addIgnoreColumns配置 |
| `FileNotFoundException` | 前端项目路径不存在 | 检查frontendProjectPath配置 |
| `ClassNotFoundException` | 编译问题 | 先执行`mvn compile` |

### Step 4 — 确认生成结果

生成成功后，告知用户生成了哪些文件及其路径：

- `{frontendProjectPath}/src/views/business/{territory}/bill{territoryCode}Page/index.vue` — 审批列表列组件
- `{frontendProjectPath}/src/views/business/{territory}/bill{territoryCode}Page/add.vue` — 新增/编辑表单
- `{frontendProjectPath}/src/views/approvalManagement/business/{territory}Bill{territoryCode}Approval/index.vue` — 详情页
- `{frontendProjectPath}/src/views/approvalManagement/business/{territory}Bill{territoryCode}Approval/js/ellipsis.js` — 详情展示配置
- `{frontendProjectPath}/src/views/approvalManagement/business/{territory}Bill{territoryCode}Approval/js/list.js` — 列表JS入口

---

## 阶段二：根据接口文档补全接口URL

### 前置条件

用户必须提供接口文档（Markdown格式或描述接口的文本）。文档应包含：
- 列表查询接口（getBillList）的URL
- 详情查询接口（getBillDetail）的URL
- 保存/提交接口的URL
- 其他业务接口的URL

### Step 1 — 解析接口文档

从接口文档中提取以下关键接口（以此业务为例，实际根据文档调整）：

```
GET  /cbo/bill1699/getBillList       列表查询
GET  /cbo/bill1699/getBillDetail     详情查询
POST /cbo/bill1699/save              保存单据
POST /cbo/bill1699/submit            提交审批
POST /cbo/bill1699/withdraw          撤回
POST /cbo/bill1699/cancel            取消
```

### Step 2 — 填充 add.vue 中的接口

读取生成的 `add.vue` 文件，在 `<script>` 部分找到以下位置并补全：

**保存接口**（在 `mounted` 或表单提交方法中）：
```javascript
// 查找类似注释或空的url配置，填入实际接口
api: '/cbo/bill1699/save'
// 或
this.$api.post('/cbo/bill1699/save', this.model)
```

**详情查询接口**（在 `mounted` 的 `else` 分支，即有id时加载详情）：
```javascript
// 填入详情接口
const res = await this.$api.get('/cbo/bill1699/getBillDetail', { id: this.id })
```

### Step 3 — 填充 ellipsis.js 中的接口

读取生成的 `ellipsis.js` 文件。该文件定义了详情页展示的数据结构，通常在顶部或专门的 `api` 字段中需要填充：

根据接口文档，在对应位置补充接口URL，例如：
```javascript
// 如文件中有类似 apiUrl 或 detailApi 的占位
module.exports = {
  apiUrl: '/cbo/bill1699/getBillDetail',  // 填入实际详情接口
  // ...其余生成内容保持不变
}
```

> 注意：`list.js` 仅是 `require('./ellipsis')` 的转发，无需修改。

### Step 4 — 检查 index.vue 中的接口

读取生成的 `index.vue`（审批列表列组件），确认是否需要填充列表接口URL。如有 `api` 或 `url` 字段留空，根据文档填入列表查询接口。

### Step 5 — 汇报修改结果

完成所有接口填充后，向用户汇报：
- 修改了哪些文件
- 每个文件填入了哪些接口URL
- 是否有无法确定的接口（需要用户确认）

---

## 注意事项

- 生成的代码中带有 `// todo:` 注释的位置，表示需要人工处理自定义逻辑，主动提示用户关注
- 接口文档中若有字段名与生成代码中的字段名不一致，主动指出并询问用户如何处理
- 不要自动修改 Freemarker 模板文件（`.ftl`），这些是生成逻辑的核心，修改需谨慎
- 如需了解模板生成逻辑，读取 `references/vue-templates/` 或 `references/js-templates/` 中对应的 `.ftl` 文件

---

## References 目录索引

| 文件 | 用途 | 何时读取 |
|------|------|---------|
| `references/generator-java/VueJsCodeGenerator.java` | 生成器入口和所有可配参数 | 阶段一开始前必读 |
| `references/generator-java/VueFreemarkerTemplateEngine.java` | 输出路径路由和多表处理逻辑 | 排查生成路径问题时 |
| `references/vue-templates/index.vue.ftl` | 审批列表列组件模板 | 理解index.vue结构时 |
| `references/vue-templates/add.vue.ftl` | 新增/编辑表单模板 | 理解add.vue结构和接口填充位置时 |
| `references/vue-templates/detailIndex.vue.ftl` | 详情页subTable渲染模板 | 理解详情页结构时 |
| `references/js-templates/ellipsis.js.ftl` | 详情展示数据结构模板 | 理解ellipsis.js结构和接口填充位置时 |
| `references/js-templates/list.js.ftl` | 列表JS模板 | 排查list.js问题时 |
