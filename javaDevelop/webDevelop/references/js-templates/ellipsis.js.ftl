<#-- 清理label的函数 -->
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
<#assign otherFields = []>

<#list allTablesInfos as table>
    <#if getAfterLastUnderscore(table.name) == 'detail'>
        <#list table.fields as field>
            <#assign excludedFieldNames = ["isDeleted", "headId", "rowNo", "fxmbh", "fxmmc", "fztmc", "fxmlx", "fcontractType", "fsszz", "projectProperties"]>
            <#if field.keyFlag == false && field.propertyName?index_of("Status") == -1 && field.propertyName?index_of("Id") == -1
            && field.propertyName?index_of("id") == -1 && !excludedFieldNames?seq_contains(field.propertyName)>
                <#assign fieldLabel = cleanLabel(field.comment!field.propertyName)>
                <#assign propertyName = field.propertyName>
                <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                    <#assign fieldLabel = fieldLabel>
                    <#assign displayName = propertyName + "Str">
                <#elseif field.propertyType == "BigDecimal">
                    <#assign fieldLabel = fieldLabel + "(元)">
                    <#assign displayName = propertyName + "Str">
                <#else>
                    <#assign fieldLabel = fieldLabel>
                    <#assign displayName = propertyName>
                </#if>
                <#assign fieldInfo = {
                "propertyName": displayName,
                "comment": field.comment!field.propertyName,
                "type": field.propertyType,
                "label": fieldLabel
                }>
                <#-- 根据字段名分类 -->
                <#assign otherFields = otherFields + [fieldInfo]>
            </#if>
        </#list>
    </#if>
</#list>
// todo:需处理表单自定义部分
module.exports = [
{
    title: "基础信息",
    tableData: [
        { label: "承办项目/部门", value: "initiateName" },
        { label: "制单日期", value: "billDate" },
        { label: "制单人", value: "initiateUserName", colSpan: 12 }
    ],
},
{
    title: "项目信息",
    tableData: [
        [
            { label: "项目编号", value: "fxmbh", type: 'router', idKey:'projectId', code: 'XM' },
            { label: "项目名称", value: "fxmmc" },
            { label: "账套名称", value: "fztmc" },
            { label: "所属组织", value: "fsszz" },
        ],
    ],
},
<#list allTablesInfos as table>
    <#if getAfterLastUnderscore(table.name) == 'detail'>
        {
            title: "其他信息",
            tableData: [<#-- 将字段分组，每行最多4个 -->
            <#list otherFields as field>
                <#if field_index % 4 == 0>
                    <#if field_index != 0>],</#if>
                    [
                    </#if>{ label: "${field.label}", value: "${field.propertyName}" }<#if field_has_next && field_index % 4 != 3>,</#if><#if !field_has_next>],</#if>
            </#list>
            [
            { label: "附件", value: "fileList", type: 'files' },
            ],
        ],
        },
    </#if>
</#list>
    <#-- 第六部分：子表信息 -->
<#if allTablesInfos?? && allTablesInfos?size gt 0 && allTablesInfos?size == 2>
    <#list allTablesInfos as table>
        <#if getAfterLastUnderscore(table.name) != 'detail'>
            {
            title: "明细信息",
            customFloor: 'subTable${table_index}',
            base: '${getAfterLastUnderscore(table.name)}List',
            type: 'table'
            },
        </#if>
    </#list>
<#elseif allTablesInfos?? && allTablesInfos?size gt 0 && allTablesInfos?size gt 2>
    {
    title: "明细信息",
    type: 'tableTabs',
    tableTabs: [
    <#list allTablesInfos as table>
        <#if getAfterLastUnderscore(table.name) != 'detail'>
            {
            title: '页签${table_index}',
            value: '${table_index}',
            base: '${getAfterLastUnderscore(table.name)}List',
            customFloor: 'subTable${table_index}',
            },
        </#if>
    </#list>
    ]
    },
</#if>
];