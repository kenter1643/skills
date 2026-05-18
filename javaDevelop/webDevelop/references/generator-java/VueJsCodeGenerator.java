package com.construct.generator.start;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.rules.NamingStrategy;
import com.construct.common.core.controller.BaseController;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author: admin
 * @Date 2023/03/15
 * @Desc: Vue和JS文件代码生成器
 */
public class VueJsCodeGenerator {


    /**
     * 是否为单据detail表，于单据使用，用于生成单据列表、详情、编辑页的单据模版
     **/
    private final static boolean isDetailTable = true;
    /**
     * 领域名
     **/
    private final static String territory = "cm";

    /**
     * 领域业务编号
     **/
    private final static String territoryCode = "2809";

    /**
     * 表名 , "nrm_bill_1813_info"
     **/
    private final static String tableName[] = {"cm_bill_2809_head", "cm_bill_2809_detail","cm_bill_2809_info"
//            ,"cbo_bill_1699_sub", "cbo_bill_1699_info"
    };
    /**
     * 数据库url
     **/
    private final static String url = "jdbc:mysql://192.168.16.101:3306/construct_star_dev_0921?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8";

    /**
     * 数据库账号
     **/
    private final static String username = "root";

    /**
     * 数据库密码
     **/
    private final static String password = "mysql@3344";

    /**
     * 定位当前项目路径
     **/
    private final static String finalProjectPath = System.getProperty("user.dir").replaceAll("\\\\", "/");

    /**
     * 前端项目路径（相对于后端项目的路径）
     **/
    private final static String frontendProjectPath = finalProjectPath + "/../construct-star-web";

    public static void main(String[] args) {

        // Vue和JS文件生成路径
        String vuePagePath = frontendProjectPath + "/src/views/business/" + territory + "/bill" + territoryCode + "Page";
        String vueDetailPath = frontendProjectPath + "/src/views/approvalManagement/business/" + territory + "Bill" + territoryCode + "Approval";
        String vueJsPath = vueDetailPath +"/js";

        // 存储所有表的信息
        List<Map<String, Object>> allTablesInfo = new ArrayList<>();

        // 为每张表获取信息
        for (String tableName : tableName) {
            Map<String, Object> tableInfo = new HashMap<>();
            tableInfo.put("tableName", tableName);
            tableInfo.put("entityName", convertToCamelCase(tableName));
            tableInfo.put("simpleName", getSimpleName(tableName));
            tableInfo.put("originalIndex", allTablesInfo.size()); // 添加原始索引
            allTablesInfo.add(tableInfo);
        }

        Map<OutputFile, String> outputFileStringMap = new HashMap<>();

        //生成规则配置
        FastAutoGenerator fastAutoGenerator = FastAutoGenerator.create(url, username, password)
                //全局配置(GlobalConfig)
                .globalConfig(builder -> {
//                    builder.author("admin"); // 设置作者，可以写自己名字
                            builder.fileOverride(); //开启文件覆盖
//                            .dateType(DateType.ONLY_DATE) //时间策略
//                            .disableOpenDir()//禁止打开输出目录
//                            .commentDate("yyyy-MM-dd") //注释日期
//                            .outputDir(path); // 指定输出目录，一般指定到java目录
                })
                //包配置(PackageConfig)
                .packageConfig(builder -> {
                    builder.parent("com.construct") // 设置父包名
                            .entity(territory + ".domain") // 设置实现类包名
                            .service(territory + ".service") // 设置服务类包名
                            .serviceImpl(territory + ".service.impl") // 设置服务实现类包名
                            .mapper(territory + ".mapper") //
                            .other(territory + ".dto")
//                            .other(territory + ".vo")

                            .controller("web.controller." + territory)
                            .pathInfo(outputFileStringMap); // 设置mapperXml和Controller生成路径
                })
                //策略配置(StrategyConfig)
                .strategyConfig(builder -> {
                    // 使用 LinkedHashSet 保持顺序
                    java.util.Set<String> tableNameSet = new java.util.LinkedHashSet<>();
                    for (String table : tableName) {
                        tableNameSet.add(table);
                    }
                    builder.addInclude(tableName); // 设置需要生成的表名

                    //实体类配置策略
                    builder.entityBuilder()
                            .enableLombok() //开启 lombok 模型
                            .logicDeletePropertyName("isDeleted") // 逻辑删除属性名(实体)
                            .logicDeleteColumnName("is_deleted") // 逻辑删除字段名(数据库)
                            .addIgnoreColumns("gmt_create", "gmt_modified") // 添加忽略字段
                            .naming(NamingStrategy.underline_to_camel)
                            .idType(IdType.ASSIGN_ID); //全局主键类型,雪花算法

                    //服务类配置策略
                    builder.serviceBuilder()
//                            .convertServiceFileName()
                            .formatServiceFileName("%sService") //设置service的命名策略,没有这个配置的话，生成的service和serviceImpl类前面会有一个I，比如IUserService和IUserServiceImpl
                            .formatServiceImplFileName("%sServiceImpl"); //设置serviceImpl的命名策略

                    //控制器类配置策略
                    builder.controllerBuilder()
                            .superClass(BaseController.class)
                            .enableRestStyle(); // 开启生成@RestController 控制器，不配置这个默认是Controller注解，RestController是返回Json字符串的，多用于前后端分离项目。

                    //Mapper配置策略
                    builder.mapperBuilder()
                            .enableBaseResultMap() // 启用 BaseResultMap 生成
                            .enableBaseColumnList(); // 启用 BaseColumnList
                })
                .injectionConfig(consumer -> {
                    Map<String, String> customFile = new HashMap<>();

                    // Vue和JS文件生成配置
                    // Vue页面文件
                    if (isDetailTable) {
                        customFile.put("index.vue", "templates/vue/index.vue.ftl");
                        // 详情JS
                        customFile.put("ellipsis.js", "templates/js/ellipsis.js.ftl");
                        customFile.put("list.js", "templates/js/list.js.ftl");
                    }
                    customFile.put("add.vue", "templates/vue/add.vue.ftl");
                    // Vue详情页面文件
                    customFile.put("detailIndex.vue", "templates/vue/detailIndex.vue.ftl");

                    consumer.customFile(customFile);

                    Map<String, Object> customMap = new HashMap<>();
                    customMap.put("vo", "vo");
                    customMap.put("voPkg", territory + ".vo");
                    customMap.put("territory", territory);
                    customMap.put("territoryCode", territoryCode);
                    customMap.put("isDetailTable", isDetailTable);

                    // 传递多表信息
                    customMap.put("allTablesInfo", allTablesInfo);
                    // 传递表的总数，用于判断是否是最后一张表
                    customMap.put("totalTablesCount", tableName.length);

                    // Vue和JS相关配置
                    customMap.put("vuePagePath", vuePagePath);
                    customMap.put("vueJsPath", vueJsPath);
                    customMap.put("vueDetailPath", vueDetailPath);
                    customMap.put("catalog", "business"); // 业务目录
                    consumer.customMap(customMap);

//                    consumer.beforeOutputFile(())

                })
                .templateEngine(new VueFreemarkerTemplateEngine()) // 使用Freemarker引擎模板，默认的是Velocity引擎模板
                .templateConfig(f -> {
                });
        fastAutoGenerator.execute(); //执行以上配置

    }

    /**
     * 将表名转换为驼峰命名的实体类名
     */
    private static String convertToCamelCase(String tableName) {
        String[] parts = tableName.split("_");
        StringBuilder result = new StringBuilder();
        for (String part : parts) {
            if (!part.isEmpty()) {
                result.append(part.substring(0, 1).toUpperCase())
                        .append(part.substring(1).toLowerCase());
            }
        }
        return result.toString();
    }

    /**
     * 获取表名的简单名称（去掉前缀）
     */
    private static String getSimpleName(String tableName) {
        // 从右往左查找第一个下划线
        int lastUnderscoreIndex = tableName.lastIndexOf('_');
        if (lastUnderscoreIndex != -1 && lastUnderscoreIndex < tableName.length() - 1) {
            // 截取下划线后面的部分
            return tableName.substring(lastUnderscoreIndex + 1);
        }
        // 如果没有下划线或者下划线在末尾，返回原表名
        return tableName;
    }
}
