---
name: front-code-generator
description: 根据 Excel 需求文档和接口文档，自动生成列表页、录入页、审批详情页等前端代码。自动调用 excel-parser 解析 Excel。适用于已有业务模块参考代码的场景。
---

# 前端代码生成器

根据 Excel 需求文档 + 接口文档 + 参考代码模式，生成标准化的前端业务页面代码。

**Excel 会自动调用 excel-parser 解析，无需单独执行 `/excel-parser`。**

## 交互流程

当用户调用此 skill 时，**必须先询问用户以下两个文件路径**，不要直接执行命令：

1. **Excel 需求文档路径**（.xlsx 文件，须包含「字段说明」sheet）
2. **接口文档路径**（.md 文件，包含 list/detail/save/delete/audit 等接口定义）

用户提供路径后，确认文件存在，再执行生成命令。

## 执行方式

```bash
# 推荐：直接传 Excel（自动调用 excel-parser 解析）
python .claude/skills/front-code-generator/generate.py \
  --excel "<Excel需求文档.xlsx>" \
  --api "<接口文档md>"

# 或者：传已解析的 JSON
python .claude/skills/front-code-generator/generate.py \
  --json "<excel-parser输出的JSON>" \
  --api "<接口文档md>"
```

参数说明：
- `--excel` / `-e`：Excel 需求文档路径（推荐，自动调用 excel-parser 解析）
- `--json` / `-j`：excel-parser 输出的 JSON 文件路径（手动解析时使用）
- `--api` / `-a`：接口文档 Markdown 文件路径（必填）
- `--output` / `-o`：代码输出根目录（可选，默认输出到项目 `src/views`）
- `--business-name` / `-b`：业务名称（可选，默认从 Excel 文件名提取）

## 工作流程

1. 如果传入 `--excel`，自动调用 excel-parser 的 `parse_excel()` 解析 Excel，生成结构化 JSON
2. 从接口文档中提取流程 Key、API 路径、入参/出参映射
3. 建立 Excel 字段中文名 ↔ API 参数名的映射表
4. 根据映射 + 模板生成列表页、录入页、审批详情页代码

## 前提条件

1. Excel 文件必须包含「字段说明」sheet（名称含"字段说明"）
2. 接口文档需包含 list/detail/save/delete/audit 等接口定义
3. 接口文档中需有流程 Key（格式 `{col}Bill{code}Approval`）以提取路径参数
4. 项目使用 `zy-order-form` 和 `columnsV2` 框架

## 输入来源

### 1. Excel 需求文档（自动解析）

直接传入 `.xlsx` 文件，内部调用 excel-parser 提取以下数据：

| 字段 | 用途 |
|------|------|
| `fuzzy_search` | 列表页模糊查询列 |
| `advanced_search` | 列表页高级查询列 |
| `list_order_fields` | 列表页显示列 |
| `field_info` | 字段属性（类型、展现、必填、枚举等） |
| `input_style.main` | 录入页主表分组和字段 |
| `input_style.details` | 录入页明细表字段 |
| `input_style.drawers` | 录入页抽屉组件 |

### 2. 接口文档

提取以下信息：

| 信息 | 来源 | 用途 |
|------|------|------|
| 单据编码 | 流程Key `{col}Bill{code}Approval` | 目录命名、API 路径 |
| 列表接口 | `GET /{col}/bill/{code}/list` | 列表页 API |
| 详情接口 | `GET /{col}/bill/{code}/detail` | 录入页编辑回填 |
| 保存接口 | `POST /{col}/bill/{code}/save` | 录入页提交 |
| 删除接口 | `POST /{col}/bill/{code}/delete` | 列表页删除 |
| 审核接口 | `POST /{col}/bill/{code}/audit` | 审批详情页 |
| 校验接口 | `POST /{col}/bill/{code}/checkParam` | 提交前校验 |
| 导出接口 | `GET /{col}/bill/{code}/export` | 列表导出 |
| 模糊查询入参 | `firstXxx` 前缀的参数 | 列表页模糊查询 prop |
| 高级查询入参 | 不带 `first` 前缀的参数 | 列表页高级查询 prop |
| 列表出参 | 列表接口出参 | 列表页列 prop |
| 详情出参 | 详情接口出参 | 录入页字段 prop、审批页 list.js |
| 保存入参 | 保存接口入参 | 录入页字段 prop |

### 3. 参考代码模式

代码生成时直接使用下方模板填充，在这个基础上实现字段的其他逻辑要求，以满足json中的要求。

## 输出文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 列表页 | `src/views/business/{{col}}/bill{{code}}Page/index.vue` | AG Grid 列表 |
| 录入页 | `src/views/business/{{col}}/bill{{code}}Page/add.vue` | zy-order-form 表单（含逻辑） |
| API 文件 | `src/api/business/{{col}}/bill{{code}}Page.js` | 接口函数（downloadTemplate 等） |
| 审批页 | `src/views/approvalManagement/business/{{col}}Bill{{code}}Approval/index.vue` | 审批详情 |
| 字段布局 | `src/views/approvalManagement/business/{{col}}Bill{{code}}Approval/js/list.js` | 详情页完整版字段配置 |
| 字段布局 | `src/views/approvalManagement/business/{{col}}Bill{{code}}Approval/js/ellipsis.js` | 详情页简略版字段配置 |

## 生成模板

> 模板使用 `{{placeholder}}` 表示需要填充的变量。`{{#each}}` / `{{/each}}` 表示循环。`{{#if}}` / `{{/if}}` 表示条件。

---

### 模板零：API 文件 `src/api/business/{{col}}/bill{{code}}Page.js`

> 遍历接口文档中所有 `METHOD /path` 格式的 API 路径，跳过标准单据操作（list/detail/save/delete/audit/revocation/deliver/export/checkParam），其余逐个生成请求函数。
> JS 保留字自动映射：`delete` → `remove`、`export` → `exportData`。
> GET 方法参数名为 `params`，POST 方法参数名为 `data`。
> 无自定义端点时生成 TODO 占位。

```javascript
import request from "@/utils/request";

// 下载导入模板（仅当接口文档包含 download 路径时生成）
export function downloadTemplate(data) {
  return request({
    url: '/cm/bill/2804/download',
    method: 'get',
    data
  });
}
```

---

### 模板一：列表页 `index.vue`

```vue
<template>
  <columns-template>
    <!-- 列表显示列：来自 JSON list_order_fields，跳过内置字段，按顺序排列 -->
{{#each listColumns}}
{{#if isLink}}
    <zy-ag-table-column label="{{label}}" prop="{{prop}}" width="{{width}}"{{#if hasFilter}} {{filterAttrs}}{{/if}}>
      <template slot-scope="{ data }">
        <el-button v-if="data.{{prop}}" type="text" @click="$goDetailView(data, '{{idKey}}', '{{navCode}}', true)">{{ "{{ data." + prop + " }}" }}</el-button>
        <span v-else>——</span>
      </template>
    </zy-ag-table-column>
{{else}}
    <zy-ag-table-column label="{{label}}" prop="{{prop}}" width="{{width}}"{{#if hasFilter}} {{filterAttrs}}{{/if}}></zy-ag-table-column>
{{/if}}
{{/each}}
  </columns-template>
</template>

<script>
import ColumnsTemplate from "@/views/common/agGrid/template/columnsV2"
export default {
  name: "{{col}}Bill{{code}}Approval",
  components: { ColumnsTemplate },
}
</script>
```

**生成规则**：

1. **跳过内置字段**：ColumnsTemplate 已渲染的字段不重复生成
2. **按 `list_order_fields` 顺序**：排列显示列
3. **filter 只在特殊类型时添加**：普通文本由 ColumnsTemplate 内置搜索覆盖，只有日期（`filter-type="daterange"`）和枚举（`filter-type="select"`）才显式加 filter
4. **prop 映射**：金额/状态/日期字段 prop 加 `Str` 后缀
5. **可跳转字段**（display_type=drawer）：用 slot-scope 渲染链接，idKey 规则 `xxxCode → xxxId`
**内置字段列表**（ColumnsTemplate 自动渲染，不重复生成）：

| 中文名 | prop | 
|--------|------|
| 单据编号 | `billCode` |
| 单据状态 | `billStatusStr` |
| 承办项目/部门 | `initiateName` |
| 项目编号 | `fxmbh` |
| 项目名称 | `fxmmc` |
| 所属组织 | `fsszz` |
| 制单人 | `initiateUserName` |
| 制单时间 | `billDate` |
| 账套名称 | `fztmc` |

**prop/filter 规则**：

| 字段类型 | 显示 prop | filter |
|---------|-----------|--------|
| 金额/税率 | `xxxStr` | — |
| 日期型 | `xxxStr` | `filter-type="daterange"` |
| 枚举/select | `xxxStr` | `filter-type="select"` |
| drawer（可跳转） | `xxx`（原值） | — |
| 普通文本 | `xxx`（原值） | — |

---

### 模板二：录入页 `add.vue`

```vue
<template>
  <zy-order-form @created="created" :page-name="title" :templates="['baseInfo']" @beforeLayout="beforeLayout" :watch="watch">
    <!-- 主表分组：来自 JSON input_style.main，跳过内置组（表头、基础信息） -->
{{#each mainGroups}}
    <zy-order-form-group title="{{title}}">
{{#each fields}}
      <zy-order-form-row label="{{label}}" prop="{{prop}}"{{#if disabled}} disabled{{/if}}{{#if required}} required{{/if}}{{#if rowKey}} row-key="{{rowKey}}"{{/if}}{{#if placeholder}} placeholder="{{placeholder}}"{{/if}}>
{{#if unitSlot}}
        <template #append>{{unit}}</template>
{{/if}}
{{#if drawerButton}}
        <template #append>
          <el-button type="text" @click="show{{DrawerName}}Drawer">选择</el-button>
        </template>
{{/if}}
      </zy-order-form-row>
{{/each}}
    </zy-order-form-group>
{{/each}}
    <!-- 明细表：来自 JSON input_style.details -->
{{#if details.length}}
    <zy-order-form-group title="明细" type="table" base="infoList" :useAgGrid="true">
      <template #header="{ model, ref }">
{{#if hasDrawerSelect}}
        <el-button size="mini" type="primary" @click="showSelectDrawer(ref)">明细选择</el-button>
{{/if}}
        <el-button size="mini" type="primary" @click="ref.addRow">新增</el-button>
        <el-button size="mini" @click="showImport">导入</el-button>
        <el-button size="mini" @click="exportSubTable">导出</el-button>
      </template>
      <template #append>
{{#each detailColumns}}
        <el-table-column label="{{label}}" prop="{{prop}}"{{#if width}} width="{{width}}"{{/if}}{{#if type}} type="{{type}}"{{/if}}{{#if required}} required{{/if}}{{#if summary}} summary{{/if}}{{#if disabled}} disabled{{/if}}{{#if unit}} unit="{{unit}}"{{/if}}{{#if decimal}} :decimal="{{decimal}}"{{/if}}{{#if options}} :options="{{options}}"{{/if}}{{#if onChange}} @change="{{onChange}}"{{/if}}></el-table-column>
{{/each}}
        <el-table-column label="操作" align="center" fixed="right" width="100" type="operate" @removeRow="removeRow" :options="['delete']"></el-table-column>
      </template>
    </zy-order-form-group>
{{/if}}
    <!-- 抽屉/弹窗插件：来自 JSON input_style.drawers -->
    <template #plugins="{ model }">
{{#each drawers}}
      <{{componentName}} ref="{{refName}}"{{#each props}} :{{key}}="{{value}}"{{/each}} @save="{{saveHandler}}"></{{componentName}}>
{{/each}}
      <import-list v-bind="importConfig" ref="importList" @importResult="importResult"></import-list>
    </template>
  </zy-order-form>
</template>

<script>
import FormController from '@/components/Basic/orderForm/js/controller'
import ImportList from '@/views/components/common/importInfo/importList.vue'
import { downloadTemplate } from '@/api/business/{{col}}/bill{{code}}Page'
import request from "@/utils/request"

export default {
  components: { ImportList },
  data() {
    return {
{{#each dataFields}}
      {{key}}: {{value}},
{{/each}}
      importConfig: {},
      watch: {}
    }
  },
  computed: {
    title() {
      if (this.$route.query.id) return '编辑{{businessName}}'
      return '新增{{businessName}}'
    },
  },
  created() {
{{#each initOptionsCalls}}
    this.{{method}}()
{{/each}}
    const path = window.location.pathname
    const list = path.split('/')
    const index = list.indexOf('bill')
    const code = list[index + 1]
    this.importConfig = {
      title: '导入明细',
      fileName: 'multipartFile',
      uploadText: '上传导入明细',
      fileApi: `/{{col}}/bill/${code}/detail/import`,
      column: {
        columns: [
          { type: "index", label: "序号", width: "80", align: "center" },
          { prop: "errorMsg", label: "失败原因", minWidth: "200", "show-overflow-tooltip": false, visible: true, custom: true }
        ]
      },
      downloadTemplate: downloadTemplate,
    }
  },
  methods: {
    created(model) {
      return new Promise(resolve => {
{{#each modelInit}}
        model.{{key}} = {{value}}
{{/each}}
        resolve(true)
      })
    },
    beforeLayout(model) {
      return new Promise(async resolve => {
        if (!this.$route.query.id) model.billDate = new Date()
        resolve(true)
      })
    },
    refresh() {},
    importResult(val) {
      if (val.errorList.length) return
      const model = FormController.current?.model || {}
      const list = model.infoList || []
      const successList = val?.successList || []
      model.infoList = [...list, ...successList]
      this.refresh()
    },
    exportSubTable() {
      const vc = FormController.current
      const list = vc.model.infoList || []
      request({
        url: `/{{col}}/bill/${vc.billCode}/detail/export`,
        method: 'POST',
        data: { infoList: list }
      }).then(res => window.open(res.data, '_blank')).catch(_ => { })
    },
    removeRow(index, ref) {
      ref.removeRow(index)
      this.refresh()
    },
    showImport() {
      if (this.$refs.importList) this.$refs.importList.open()
    },
{{#each optionGetters}}
    {{method}}() {
      // TODO: 替换为实际枚举接口
      // request({ url: '/{{col}}/bill/{{code}}/enum/...', method: 'GET' })
      //   .then(res => { this.{{optionsKey}} = res.data || [] })
      //   .catch(_ => { })
    },
{{/each}}
  }
}
</script>
```

**录入表单组件规则**（根据 `display_type` 映射 `row-key`）：

> 根据表单展现列的显示类型，生成对应的录入表单组件。

| `display_type` | `row-key` | 附加属性 | 说明 |
|---------------|-----------|---------|------|
| `text` / 空 | — | — | 普通输入框 |
| `时间选择框` / `date` | `date` | `type="datetime"` 或 `type="month"` | 日期/时间选择器 |
| `数值框` / `number` | `number` | 金额字段加 `<template #append>元</template>` | 数值输入框 |
| `下拉` / `分级选择框` / `select` | `select` | `:api` 或自定义 slot | 下拉选择器 |
| `多行文本` / `textarea` | `textarea` | `:span`, `:maxLength` | 多行文本域 |
| `file` / `附件` | `files` | `:span` | 文件上传 |
| **`drawer` + 不可编辑** | — | `disabled` | **普通文本禁用**（不显示选择按钮） |
| `drawer` + 可编辑 | `select` | `<template #append>` 放选择按钮 | 带抽屉选择的下拉框 |

**通用属性规则**：

| `field_info` 条件 | 属性 |
|-------------------|------|
| `is_required = true` | `required` |
| `is_editable = false` | `disabled`, `placeholder="自动带出"` |
| `is_enum = true` | `row-key="select"` |

**明细列生成规则**（对齐 `fam/bill1723Page` 模式）：

| 条件 | 列属性 |
|------|--------|
| `display_type = 数值框` 且可编辑 | `type="number"` |
| 不可编辑文本列 | `type="text"` |
| 可编辑文本域 | `type="textarea"` |
| 金额字段 | `summary`（汇总） |
| `is_required` | `required` |
| `is_editable = false` | `disabled` |

**表结构模式**：

| 场景 | 属性 |
|------|------|
| 单明细表 | `type="table" base="infoList"` |
| 多标签明细表 | `type="tableTabs"` 包裹多个 `type="table" value="1" base="xxxList"` |

**明细表操作列**（参考 fam 模式）：
```html
<el-table-column label="操作" fixed="right" width="80px" align="center">
  <template slot-scope="{ $index }">
    <el-button type="text" @click="removeRow('baseName', $index)"> 删除 </el-button>
  </template>
</el-table-column>
```

---

### 模板三：审批详情页 `index.vue`

```javascript
import base from '../index.vue'
export default {
  extends: base,
  data() {
    return {
      showPrint: true,
      renderMap: [
        {
          slot: 'subTable',
          render: (h, ctx) => {
            const { model } = ctx.props
            return (
              <div>
                <div ref="columns">
{{#each detailColumns}}
                  <el-table-column label="{{label}}" prop="{{prop}}"{{#if width}} width="{{width}}"{{/if}}{{#if type}} type="{{type}}"{{/if}}{{#if unit}} unit="{{unit}}"{{/if}}{{#if summary}} summary{{/if}}{{#if rewrite}} rewrite onChange={this.{{changeHandler}}}{{/if}}></el-table-column>
{{/each}}
                </div>
              </div>
            )
          }
        }
      ],
      customColumns: {
{{#each customColumns}}
        {{key}}: () => {
          return (<el-table-column label="{{label}}" minWidth="{{minWidth}}" prop="{{prop}}" show-overflow-tooltip></el-table-column>)
        },
{{/each}}
      },
      billCode: {{code}}
    }
  },
  watch: {
    'model.billDetail': {
      handler(val) {
{{#if hasInitLogic}}
        if (val && this.model.billHead.billStatus == 1) this.initData()
{{/if}}
      }
    }
  },
  methods: {
{{#each approvalMethods}}
    {{name}}(val, scoped) {
      {{body}}
    },
{{/each}}
  }
}
```

---

### 模板五：审批详情页 `js/list.js`

```javascript
module.exports = [
{{#each mainGroups}}
  {
    title: "{{title}}",
    tableData: [
{{#each rows}}
      [
{{#each cells}}
        { label: "{{label}}", value: "{{value}}"{{#if type}}, type: '{{type}}'{{/if}}{{#if idKey}}, idKey: '{{idKey}}'{{/if}}{{#if code}}, code: '{{code}}'{{/if}}{{#if colSpan}}, colSpan: {{colSpan}}{{/if}} },
{{/each}}
      ],
{{/each}}
    ],
  },
{{/each}}
{{#if details.length}}
  {
    title: "明细",
    customFloor: 'subTable',
    base: 'infoList',
    type: 'table',
    fixedRight: (h, ctx) => {
      return (
        <div>
          <el-button class="position" size="mini" onClick={ctx.$parent.showOperationLog}>
            修改记录
          </el-button>
        </div>
      )
    }
  }
{{/if}}
];
```

**list.js 字段排版规则**：
- 每行 3-4 个字段（`colSpan: 12` 表示占半行占位）
- 可跳转字段：`type: 'router'`, `idKey`: 关联 ID 字段, `code`: 跳转单据类型
- 附件字段：`type: 'files'`
- 字段按 `input_style.main` 分组顺序排列

---

### 模板六：prop 映射速查

生成代码前，先从接口文档建立 **中文名 → API参数名** 映射表：

| 中文名关键词 | API 参数名模式 | 示例 |
|-------------|---------------|------|
| xxx编号 | `xxxCode` | 单据编号 → `billCode` |
| xxx名称 | `xxxName` | 合同名称 → `contractName` |
| xxx时间/日期 | `xxxDate` + `xxxDateStr` | 制单时间 → `billDate` / `billDateStr` |
| xxx金额(元) | `xxx` (BigDecimal) + `xxxStr` | 合同总金额 → `qyje` / `qyjeStr` |
| xxx状态 | `xxxStatus` + `xxxStatusStr` | 单据状态 → `billStatus` / `billStatusStr` |
| xxx人 | `xxxUserName` | 制单人 → `initiateUserName` |
| 附件 | `fileList` | |
| 项目编号 | `fxmbh` | (固定命名) |
| 项目名称 | `fxmmc` | (固定命名) |
| 所属组织 | `fsszz` + `fsszzid` | (固定命名) |
| 账套名称 | `fztmc` + `fztmcid` | (固定命名) |
| 模糊查询参数 | `first` + 驼峰 | `firstBillCode` |
| 全部关键词 | `firstKeyWord` | 搜索所有字段 |
