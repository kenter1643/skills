<script>
import base from "../index.vue";
export default {
    extends: base,
    data() {
        return {
            showPrint: true, //是否展示打印 todo:没有打印需删除，需处理子表自定义部分
            <#if allTablesInfos?? && allTablesInfos?size gt 0>
            renderMap: [
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
                <#if getAfterLastUnderscore(table.name) != 'detail'>
                {
                    slot: 'subTable${table_index}',
                    render: (h, ctx) => {
                        return (
                            <div>
                                <div ref="columns">
                                    <#assign excludedFieldNames = ["isDeleted", "headId", "rowNo"]>
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
                                    <#assign fields = table.fields![]>
                                    <#if fields?size gt 0>
                                    <#list fields as field>
                                        <#if field.keyFlag == false && field.propertyName?index_of("Status") == -1 && field.propertyName?index_of("Id") == -1
                                        && field.propertyName?index_of("id") == -1 && !excludedFieldNames?seq_contains(field.propertyName)>
                                        <#-- 处理label，去掉括号内容 -->
                                        <#assign fieldLabel = field.comment!field.propertyName>
                                        <#assign processedLabel = cleanLabel(fieldLabel)>
                                        <#if field.propertyType == "LocalDateTime" || field.propertyType == "Date">
                                            <el-table-column label="${processedLabel}" prop="${field.propertyName}Str" width="140"></el-table-column>
                                        <#elseif field.propertyType == "BigDecimal">
                                            <el-table-column label="${processedLabel}(元)" prop="${field.propertyName}Str" width="150"></el-table-column>
                                        <#else>
                                        <el-table-column label="${processedLabel}" prop="${field.propertyName}" width="160"></el-table-column>
                                        </#if>
                                        </#if>
                                    </#list>
                                    </#if>
                                </div>
                            </div>
                        )
                    }
                }<#if table_has_next>,</#if>
                </#if>
                </#list>
            ],
            </#if>
        }
    }
}
</script>