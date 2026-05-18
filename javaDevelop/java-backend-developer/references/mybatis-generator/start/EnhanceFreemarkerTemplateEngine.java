package com.construct.generator.start;

import cn.hutool.core.util.ObjectUtil;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.po.TableInfo;
import com.baomidou.mybatisplus.generator.engine.FreemarkerTemplateEngine;

import java.io.File;
import java.util.Map;
import java.util.Objects;

/**
 * 对自定义的类处理，即other里生成的类
 */
public class EnhanceFreemarkerTemplateEngine extends FreemarkerTemplateEngine {


    @Override
    public void writer( Map<String, Object> objectMap,  String templatePath,  File outputFile) throws Exception {
        // 获取表类型
        String tableType = (String) objectMap.get("tableType");

        // 根据表类型和模板类型动态选择模板
        if (tableType != null && !tableType.isEmpty()) {
            // 根据原始路径判断文件类型，返回对应的模板路径
            if (templatePath.contains("entity.java.ftl")) {
                // 检查是否设置了自定义实体模板路径
                String customPath = (String) objectMap.get("entityTemplatePath");
                templatePath =  customPath != null ? customPath : templatePath;

            } else if (templatePath.contains("service.java.ftl")) {
                String customPath = (String) objectMap.get("serviceTemplatePath");
                templatePath = customPath != null ? customPath : templatePath;

            } else if (templatePath.contains("serviceImpl.java.ftl")) {
                String customPath = (String) objectMap.get("serviceImplTemplatePath");
                templatePath = customPath != null ? customPath : templatePath;
            } else if (templatePath.contains("mapper.java.ftl")) {
                String customPath = (String) objectMap.get("mapperTemplatePath");
                templatePath = customPath != null ? customPath : templatePath;
            } else if (templatePath.contains("mapper.xml.ftl")) {
                String customPath = (String) objectMap.get("xmlTemplatePath");
                templatePath = customPath != null ? customPath : templatePath;
            } else if (templatePath.contains("controller.java.ftl")) {
                String customPath = (String) objectMap.get("controllerTemplatePath");
                templatePath = customPath != null ? customPath : templatePath; }
        }

        super.writer(objectMap, templatePath, outputFile);
    }

    @Override
    protected void outputCustomFile(Map<String, String> customFile, TableInfo tableInfo, Map<String, Object> objectMap) {

        // 可以调用 tableInfo 的getFieldNames方法获得所有的列
        this.printTableColumn(tableInfo);

        // objectMap 里的key可以在ftl文件中直接引用
        // https://copyfuture.com/blogs-details/20210404114118659h
        String entityName = tableInfo.getEntityName();
        String otherPath = this.getPathInfo(OutputFile.other);
        customFile.forEach((key, value) -> {
            // 拼接路径
            String fileName = null;

            if (!key.contains("DTO") && !key.equals("headSql.sql")) {
                if (ObjectUtil.isNotEmpty(objectMap.get("vo"))) {
                    String vo = String.valueOf(objectMap.get("vo"));
                    String substring = Objects.requireNonNull(otherPath).substring(0, otherPath.length() - 3);
                    fileName = String.format(substring+ vo + File.separator + entityName + "%s", key);
                }
            } else if (key.equals("headSql.sql")) {
                if (ObjectUtil.isNotEmpty(objectMap.get("sqlData"))) {
                    String sqlData = String.valueOf(objectMap.get("sqlData"));
                    String substring = Objects.requireNonNull(otherPath).substring(0, otherPath.length() - 3);
                    fileName = String.format(substring+ sqlData + File.separator +  key);
                }
            }
            if (ObjectUtil.isEmpty(fileName)) {
                fileName = String.format(otherPath + File.separator + entityName + "%s", key);
            }
            System.out.println(fileName);
            this.outputFile(new File(fileName), objectMap, value);

        });
    }

    /**
     * 获得所有的表列名
     *
     * @param tableInfo 表信息
     */
    private void printTableColumn(TableInfo tableInfo) {
        System.out.println("所有的列名：" + tableInfo.getFieldNames());
    }
}
