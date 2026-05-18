package com.construct.generator.start;

import cn.hutool.core.util.ObjectUtil;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.po.TableInfo;
import com.baomidou.mybatisplus.generator.engine.FreemarkerTemplateEngine;

import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

/**
 * 对自定义的类处理，即other里生成的类
 * 支持生成DTO/VO类以及Vue和JS文件
 * 支持在同一个Vue模板中处理多张表的属性
 */
public class VueFreemarkerTemplateEngine extends FreemarkerTemplateEngine {

    private static List<TableInfo> allTablesInfosTemp = new ArrayList<>();


    @Override
    protected void outputCustomFile(Map<String, String> customFile, TableInfo tableInfo, Map<String, Object> objectMap) {

        // 可以调用 tableInfo 的getFieldNames方法获得所有的列
        this.printTableColumn(tableInfo);

        // 在objectMap中维护所有表的TableInfo列表
//        @SuppressWarnings("unchecked")
//        allTablesInfosTemp = (List<TableInfo>) objectMap.get("allTablesInfos");
//        if (allTablesInfosTemp == null) {
//            allTablesInfosTemp = new ArrayList<>();
//            objectMap.put("allTablesInfos", allTablesInfosTemp);
//        }
        objectMap.put("allTablesInfos", allTablesInfosTemp);
        allTablesInfosTemp.add(tableInfo);
        
        // 获取表总数（从objectMap中获取，在VueJsCodeGenerator中设置）
        Integer totalCount = (Integer) objectMap.get("totalTablesCount");
        if (totalCount == null) {
            // 如果未设置，尝试从allTablesInfo获取
            Object allTablesInfoObj = objectMap.get("allTablesInfo");
            if (allTablesInfoObj instanceof List) {
                totalCount = ((List<?>) allTablesInfoObj).size();
            }else {
                totalCount = 1; // 默认值
            }
        }


        // 将当前表索引和是否最后一张表的信息添加到objectMap中
        final int tablesCount = allTablesInfosTemp.size();
        objectMap.put("currentTableIndex", tablesCount - 1);

        boolean isLastTable = tablesCount >= totalCount;
        objectMap.put("isLastTable", isLastTable);
        
        // 将当前表信息也添加到objectMap中（保持向后兼容）
        objectMap.put("table", tableInfo);

        // objectMap 里的key可以在ftl文件中直接引用
        // https://copyfuture.com/blogs-details/20210404114118659h
        String entityName = tableInfo.getEntityName();
        String otherPath = this.getPathInfo(OutputFile.other);

        // 从objectMap中获取Vue/JS相关配置
        String vuePagePath = (String) objectMap.get("vuePagePath");
        String vueJsPath = (String) objectMap.get("vueJsPath");
        String vueDetailPath = (String) objectMap.get("vueDetailPath");
        String territory = (String) objectMap.get("territory");
        String territoryCode = (String) objectMap.get("territoryCode");

        // 判断是否是最后一张表（使用final变量以便在lambda中使用）
//        boolean isLastTable = tablesCount >= totalCount;
//        List<TableInfo> allTablesInfos = allTablesInfosTemp;

        for (String key : customFile.keySet()) {
            String value = customFile.get(key);


            String fileName = null;

            // 判断是否为Vue或JS文件
            if (key.endsWith(".vue") || key.endsWith(".js")) {
                // 对于Vue和JS文件，只在最后一张表处理时生成，以便能够访问所有表的信息
                if (isLastTable) {
                    fileName = getVueJsFilePath(key, vuePagePath, vueJsPath, vueDetailPath, territory, territoryCode);
                    if (fileName != null) {
                        System.out.println("生成Vue/JS文件: " + fileName + " (处理了 " + allTablesInfosTemp.size() + " 张表)");
                        File file = new File(fileName);
                        // 确保目录存在
                        if (!file.getParentFile().exists()) {
                            file.getParentFile().mkdirs();
                        }
                        this.outputFile(file, objectMap, value);
                        continue; // 跳过后续Java文件处理
                    }
                } else {
                    // 不是最后一张表，跳过Vue/JS文件的生成
                    continue;
                }
            }


            File file = new File(fileName);
            // 确保目录存在
            if (!file.getParentFile().exists()) {
                file.getParentFile().mkdirs();
            }

            System.out.println(fileName);
            this.outputFile(file, objectMap, value);
        };
    }

    /**
     * 获得所有的表列名
     *
     * @param tableInfo 表信息
     */
    private void printTableColumn(TableInfo tableInfo) {
        System.out.println("所有的列名：" + tableInfo.getFieldNames());
    }

    /**
     * 获取Vue或JS文件的生成路径
     *
     * @param fileName 文件名（如 index.vue, api.js）
     * @param vuePagePath Vue页面路径
     * @param vueJsPath Vue API路径
     * @param vueDetailPath Vue详情页面路径
     * @param territory 领域名
     * @param territoryCode 业务编号
     * @return 文件完整路径，如果不是Vue/JS文件则返回null
     */
    private String getVueJsFilePath(String fileName, String vuePagePath, String vueJsPath,
                                    String vueDetailPath, String territory, String territoryCode) {
        if (fileName.endsWith(".vue")) {
            if (fileName.equals("index.vue") || fileName.equals("add.vue")) {
                // 页面文件生成到 page 目录
                if (vuePagePath != null) {
                    return vuePagePath + File.separator + fileName;
                }
            } else if (fileName.equals("detailIndex.vue")) {
                // 详情页面文件生成到 detail 目录
                if (vueDetailPath != null) {
                    return vueDetailPath + File.separator + "index.vue";
                }
            } else {
                // 其他Vue文件，默认生成到page目录
                if (vuePagePath != null) {
                    return vuePagePath + File.separator + fileName;
                }
            }
        } else if (fileName.endsWith(".js")) {
            // API文件生成到 detail 目录
            if (vueJsPath != null) {
                return vueJsPath + File.separator + fileName;
            }
        }
        return null;
    }

}