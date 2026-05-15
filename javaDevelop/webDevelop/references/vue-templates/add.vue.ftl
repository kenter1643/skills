<template>
    <div>
        <#if allTablesInfos?? && allTablesInfos?size gt 0>
            <zy-order-form ref="form" :templates="['baseInfo']" :page-name="title" @beforeLayout="beforeLayout">
                <#-- 常规业务列 -->
                <#-- 可以创建一个同时处理括号和分号的函数 -->
                <#function cleanLabel text>
                    <#if !text?has_content>
                        <#return "">
                    </#if>

                    <#local result = text>

                    <#-- 先处理分号 -->
                    <#if result?contains("；")>
                        <#local result = result?substring(0, result?index_of("；"))>
                    <#elseif result?contains(";")>
                        <#local result = result?substring(0, result?index_of(";"))>
                    </#if>

                    <#-- 再处理括号 -->
                    <#if result?contains("（") && result?contains("）")>
                        <#local startIdx = result?index_of("（")>
                        <#local endIdx = result?index_of("）")>
                        <#if startIdx < endIdx>
                            <#local result = result?substring(0, startIdx)>
                        </#if>
                    <#elseif result?contains("(") && result?contains(")")>
                        <#local startIdx = result?index_of("(")>
                        <#local endIdx = result?index_of(")")>
                        <#if startIdx < endIdx>
                            <#local result = result?substring(0, startIdx)>
                        </#if>
                    </#if>

                    <#-- 清理多余空格 -->
                    <#local result = result?trim>

                    <#-- 如果清理后为空，返回原始值 -->
                    <#if !result?has_content>
                        <#return text>
                    </#if>

                    <#return result>
                </#function>
                <#-- 定义一个函数将字符串转换为PascalCase -->
                <#function toPascalCase str>
                    <#if !str?has_content>
                        <#return str>
                    </#if>
                    <#-- 将字符串按非字母数字字符分割，然后将每个单词首字母大写 -->
                    <#local words = str?split("[^a-zA-Z0-9]")>
                    <#local result = "">
                    <#list words as word>
                        <#if word?has_content>
                            <#local result = result + word?cap_first>
                        </#if>
                    </#list>
                    <#return result>
                </#function>
                <#function getAfterLastUnderscore str>
                    <#if !str?has_content>
                        <#return str>
                    </#if>
                    <#-- 从右往左找到最后一个下划线的位置 -->
                    <#local lastIndex = str?last_index_of("_")>

                    <#if lastIndex != -1>
                        <#-- 截取下划线之后的部分 -->
                        <#return str?substring(lastIndex + 1)>
                    <#else>
                        <#-- 没有下划线，返回原字符串 -->
                        <#return str>
                    </#if>
                </#function>
                <#list allTablesInfos as table>
                    <#if getAfterLastUnderscore(table.name) == 'detail'>
                        <zy-order-form-group title="项目信息">
                            <zy-order-form-row label="项目编号" placeholder="自动带出" prop="fxmbh" disabled required></zy-order-form-row>
                            <zy-order-form-row label="项目名称" placeholder="自动带出" prop="fxmmc" disabled required></zy-order-form-row>
                            <zy-order-form-row label="账套名称" placeholder="自动带出" prop="fztmc" disabled required></zy-order-form-row>
                            <zy-order-form-row label="所属组织" placeholder="自动带出" prop="fsszz" disabled required></zy-order-form-row>
                        </zy-order-form-group>
                        <!-- todo:需处理表单自定义部分 -->
                        <zy-order-form-group title="其他信息">
                            <#assign excludedFieldNames = ["isDeleted", "headId", "rowNo", "fxmbh", "fxmmc", "fztmc", "fxmlx", "fcontractType", "fsszz", "projectProperties"]>
                            <#list table.fields as field>
                                <#if field.keyFlag == false && !excludedFieldNames?seq_contains(field.propertyName)
                                    && field.propertyName?index_of("Id") == -1 && field.propertyName?index_of("id") == -1>
                                    <#assign fieldLabel = field.comment!field.propertyName>
                                    <#assign processedLabel = cleanLabel(fieldLabel)>
                                    <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                                        <zy-order-form-row label="${processedLabel}" prop="${field.propertyName}" row-key="date" valueFormat="yyyy-MM-dd" required></zy-order-form-row>
                                    <#elseif field.propertyType == "BigDecimal">
                                        <zy-order-form-row label="${processedLabel}" prop="${field.propertyName}" row-key="number" required>
                                            <template #append>元</template>
                                        </zy-order-form-row>
<#--                                    <#elseif field.propertyName?index_of("Type") != -1 || field.propertyName?index_of("Status") != -1>-->
<#--                                        <zy-order-form-row-->
<#--                                                label="${processedLabel}"-->
<#--                                                prop="${field.propertyName}"-->
<#--                                                row-key="select"-->
<#--                                                api="${territory}/bill${territoryCode}Page:${field.propertyName}Label"<#if field.propertyName?index_of("Status") != -1> required</#if>>-->
<#--                                        </zy-order-form-row>-->
                                    <#else>
                                        <zy-order-form-row label="${processedLabel}" prop="${field.propertyName}" required></zy-order-form-row>
                                    </#if>
                                </#if>
                            </#list>
                            <zy-order-form-row label="附件上传" prop="fileList" row-key="files" :span="24" required></zy-order-form-row>
                        </zy-order-form-group>
                    </#if>
                </#list>
                <#if allTablesInfos?size == 2>
                    <#list allTablesInfos as table>
                        <#if getAfterLastUnderscore(table.name) != 'detail'>
                            <#assign tableProp = getAfterLastUnderscore(table.name)>
                            <zy-order-form-group title="明细信息" type="table" base="${tableProp}List">
                                <template #header>
                                    <el-button type="primary" size="mini" @click="addRow('${tableProp}List')">新增</el-button>
                                </template>
                                <template #append>
                                    <#list table.fields as field>
                                        <#if field.keyFlag == false && field.propertyName?index_of("Status") == -1 && field.propertyName?index_of("Id") == -1
                                        && field.propertyName?index_of("id") == -1 && !excludedFieldNames?seq_contains(field.propertyName)>
                                        <#-- 处理label，去掉括号内容 -->
                                            <#assign fieldLabel = field.comment!field.propertyName>
                                            <#assign processedLabel = cleanLabel(fieldLabel)>
                                            <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                                                <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="180" required>
                                                    <template slot-scope="{row}">
                                                        <el-date-picker v-model="row.${field.propertyName}" value-format="yyyy-MM-dd" style="width: 100%;" type="date"
                                                                        placeholder="请选择${processedLabel}">
                                                        </el-date-picker>
                                                    </template>
                                                </el-table-column>
                                            <#elseif field.propertyType == "BigDecimal">
                                                <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="160" type="number" required>
                                                    <template #append>元</template>
                                                </el-table-column>
                                            <#else>
                                                <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="150" required></el-table-column>
                                            </#if>
                                        </#if>
                                    </#list>
                                    <el-table-column label="操作" fixed="right" width="80px" align="center">
                                        <template slot-scope="{ $index }">
                                            <el-button type="text" @click="removeRow($index, '${tableProp}List')"> 删除 </el-button>
                                        </template>
                                    </el-table-column>
                                </template>
                            </zy-order-form-group>
                        </#if>
                    </#list>
                </#if>
                <#if allTablesInfos?size gt 2>
                    <zy-order-form-group title="明细信息" type="tableTabs">
                        <#list allTablesInfos as table>
                            <#if getAfterLastUnderscore(table.name) != 'detail'>
                                <#assign tableProp = getAfterLastUnderscore(table.name)>
                                <zy-order-form-group title="页签${table_index}" type="table" value="${table_index}" base="${tableProp}List" rowKey="${tableProp}Id">
                                    <template #header>
                                        <el-button type="primary" size="mini" @click="addRow('${tableProp}List')">新增</el-button>
                                    </template>
                                    <template #append>
                                        <#list table.fields as field>
                                            <#if field.keyFlag == false && field.propertyName?index_of("Status") == -1 && field.propertyName?index_of("Id") == -1
                                            && field.propertyName?index_of("id") == -1 && !excludedFieldNames?seq_contains(field.propertyName)>
                                            <#-- 处理label，去掉括号内容 -->
                                                <#assign fieldLabel = field.comment!field.propertyName>
                                                <#assign processedLabel = cleanLabel(fieldLabel)>
                                                <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                                                    <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="180" required>
                                                        <template slot-scope="{row}">
                                                            <el-date-picker v-model="row.${field.propertyName}" value-format="yyyy-MM-dd" style="width: 100%;" type="date"
                                                                            placeholder="请选择${processedLabel}">
                                                            </el-date-picker>
                                                        </template>
                                                    </el-table-column>
                                                <#elseif field.propertyType == "BigDecimal">
                                                    <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="160" type="number" required>
                                                        <template #append>元</template>
                                                    </el-table-column>
                                                <#else>
                                                    <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="150" required></el-table-column>
                                                </#if>
                                            </#if>
                                        </#list>
                                        <el-table-column label="操作" fixed="right" width="80px" align="center">
                                            <template slot-scope="{ $index }">
                                                <el-button type="text" @click="removeRow($index, '${tableProp}List')"> 删除 </el-button>
                                            </template>
                                        </el-table-column>
                                    </template>
                                </zy-order-form-group>
                            </#if>
                        </#list>
                    </zy-order-form-group>
                </#if>
            </zy-order-form>
        </#if>
    </div>
</template>

<script>
import FormController from '@/components/Basic/orderForm/js/controller'
export default {
    data() {
        return {
            id: '',
            model: {},
        }
    },
    computed: {
        title() {
            if (this.$route.query.id) return '编辑'
            return '新增'
        },
    },
    mounted() {
        let query = this.$route.query
        this.id = query.id
    },
    methods: {
        beforeLayout(model) {
            this.model = FormController.current.model
            return new Promise(async (resolve) => {
                if (!this.id) {
                    try {
                        <#list allTablesInfos as table>
                            <#assign tableProp = getAfterLastUnderscore(table.name)>
                            <#if tableProp != 'detail'>
                                model.${tableProp}List = []
                            </#if>
                        </#list>
                    } catch (_) {}
                } else {
                }
                resolve(true)
            })
        },
        // 新增
        addRow(type) {
            const model = FormController.current.model
            if (!model[type]) {
                model[type] = []
            }
            // 定义字段映射，键为表属性名，值为字段列表
            const fieldMap = {
                <#assign excludedFieldNames = ["isDeleted", "headId", "rowNo"]>
                <#list allTablesInfos as table>
                    <#assign tableProp = getAfterLastUnderscore(table.name)>
                    <#if tableProp != 'detail'>
                        '${tableProp}List': [<#list table.fields as field><#if !excludedFieldNames?seq_contains(field.propertyName)>'${field.propertyName}',</#if></#list>],
                    </#if>
                </#list>
            }
            let data = {}
            let fieldList = fieldMap[type] || []
            fieldList.forEach((p) => {
                data[p] = ''
            })
            model[type].push({...data})
        },
        // 删除行
        removeRow(index, type) {
            const model = FormController.current.model
            if (index != -1) {
                model[type].splice(index, 1)
            }
        },
    }
}
</script>
