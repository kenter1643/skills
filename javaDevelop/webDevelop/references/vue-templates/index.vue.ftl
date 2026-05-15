<template>
    <div>
        <!-- todo:需处理表单自定义部分 -->
        <columns-template ref="columnsV2"<#if flowConfig??> @cusFlowConfig="flowConfig"</#if>>
            <#assign excludedFieldNames = ["isDeleted", "headId", "rowNo", "fxmbh", "fxmmc", "fztmc", "fxmlx", "fcontractType", "fsszz", "projectProperties"]>
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
                    <#list table.fields as field>
                        <#if field.keyFlag == false && field.propertyName?index_of("Status") == -1 && field.propertyName?index_of("Id") == -1
                            && field.propertyName?index_of("id") == -1 && !excludedFieldNames?seq_contains(field.propertyName)>
                            <#-- 处理label，去掉括号内容 -->
                            <#assign fieldLabel = field.comment!field.propertyName>
                            <#assign processedLabel = cleanLabel(fieldLabel)>
                            <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                                <zy-ag-table-column
                                    label="${processedLabel}"
                                    prop="${field.propertyName}Str"
                                    :width="180"
                                    filter
                                    filter-type="daterange"
                                    filter-prop="${field.propertyName}">
                                </zy-ag-table-column>
                            <#elseif field.propertyType == "BigDecimal">
                                <zy-ag-table-column
                                    label="${processedLabel}(元)"
                                    prop="${field.propertyName}Str"
                                    :width="160">
                                </zy-ag-table-column>
                            <#else>
                                <zy-ag-table-column
                                    label="${processedLabel}"
                                    prop="${field.propertyName}"
                                    :width="150"
                                    filter>
                                </zy-ag-table-column>
                            </#if>
                        </#if>
                    </#list>
                </#if>
            </#list>
        </columns-template>
    </div>
</template>

<script>
    import ColumnsTemplate from '@/views/common/agGrid/template/columnsV2'
    export default {
        name: '${toPascalCase(territory + "Bill" + territoryCode + "Approval")}',
        components: { ColumnsTemplate },
        methods: {
            <#if flowConfig??>
            flowConfig() {
                return new Promise((resolve) => {
                    const config = {
                        flowConfig: {
                            form: [
                                <#-- 流程表单配置 -->
                            ]
                        }
                    }
                    resolve(config)
                })
            }
            </#if>
        }
    }
</script>
