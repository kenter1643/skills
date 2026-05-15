package com.construct.generator.start;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.rules.DateType;
import com.baomidou.mybatisplus.generator.config.rules.NamingStrategy;
import com.construct.common.core.controller.BaseController;
import com.construct.common.domain.BaseBillHead;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * @author: admin
 * @Date 2023/03/15
 * @Desc: 代码生成器
 */
public class MyBatisPlusGeneratorV2 {

    /**
     * 包路径
     */
    private final static String projectPath = "construct-star-contract";
    /**
     * 领域名
     **/
    private final static String territory = "cm";

    /**
     * 是否为单据主表，于单据使用，用于生成单据Controller、Service、Impl的单据模版，若只需默认模板，使用false即可
     **/
    private final static boolean isBillTable = true;
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
     * 菜单参数配置
     **/ // 菜单父级id：需数据库查询父级菜单id
    private final static String parentMenuId = "6010101";
         // 当前菜单名称
    private final static String menuName = "施工图预算变更";
    private final static String pathSuffix = territory+"/bill/"+territoryCode+"/approval";
    private final static String componentPrefix = "business/"+territory+"/bill"+territoryCode+"Page";
    private final static String permsType = territory+":"+territoryCode;
    /**
     * 枚举参数配置
     **/
    private final static String enumKey = "HNTYS";
    private final static String enumName = "施工图预算变更";
    private final static String flowKey = territory+"Bill"+territoryCode+"Approval";

    /**
     * 子表后缀 , 对需要生成保存语列表查询的Service层进行配置（与head，detail后缀互斥）
     **/
    private final static List<String> infoSuffix = Arrays.asList("_info", "_sub");

    /** ******************************* ******************************* ******************************* **/

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

    public static void main(String[] args) {

        //代码生成路径位置
        String path = finalProjectPath + "/"+projectPath+"/src/main/java";
        String controllerPath = finalProjectPath + "/"+projectPath+"/src/main/java/com/construct/web/controller/" + territory;
        String mapperXmlPath = finalProjectPath  + "/"+projectPath+"/src/main/resources/mapper/" + territory;
        Map<OutputFile, String> outputFileStringMap = new HashMap();
        outputFileStringMap.put(OutputFile.controller, controllerPath);
        outputFileStringMap.put(OutputFile.mapperXml, mapperXmlPath);

        //生成规则配置
        FastAutoGenerator fastAutoGenerator = FastAutoGenerator.create(url, username, password)
                //全局配置(GlobalConfig)
                .globalConfig(builder -> {
                    builder.author("admin") // 设置作者，可以写自己名字
                            .fileOverride() //开启文件覆盖
                            .dateType(DateType.ONLY_DATE) //时间策略
                            .disableOpenDir()//禁止打开输出目录
                            .commentDate("yyyy-MM-dd") //注释日期
                            .outputDir(path); // 指定输出目录，一般指定到java目录
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
                    builder.addInclude(tableName); // 设置需要生成的表名

                    //实体类配置策略
                    builder.entityBuilder()
                            .enableLombok() //开启 lombok 模型
                            .logicDeletePropertyName("isDeleted") // 逻辑删除属性名(实体)
                            .logicDeleteColumnName("is_deleted") // 逻辑删除字段名(数据库)
                            .addIgnoreColumns("gmt_create", "gmt_modified") // 添加忽略字段
                            .naming(NamingStrategy.underline_to_camel)
                            .idType(IdType.ASSIGN_ID); //全局主键类型,雪花算法
//                    if (isBillTable) {
//                        builder.entityBuilder().superClass(BaseBillHead.class);
//                    }

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
                    // DTO 下面的key会作为类名后缀，进而生成新类
                    customFile.put("DTO.java", "templates/dto/dto.java.ftl");

                    consumer.customFile(customFile);

                    Map<String, Object> customMap = new HashMap<>();
                    customMap.put("vo", "vo");
                    customMap.put("sqlData", "sqlData");
                    customMap.put("voPkg", territory + ".vo");
                    customMap.put("sqlDataPkg", territory + ".sqlData");
                    customMap.put("territory", territory);
                    customMap.put("territoryCode", territoryCode);

                    // 菜单参数
                    customMap.put("menuName", menuName);
                    customMap.put("parentMenuId", parentMenuId);
                    customMap.put("pathSuffix", pathSuffix);
                    customMap.put("componentPrefix", componentPrefix);
                    customMap.put("permsType", permsType);
                    customMap.put("enumKey", enumKey);
                    customMap.put("enumName", enumName);
                    customMap.put("flowKey", flowKey);

                    List<String> tableNameList = Arrays.asList(tableName);

                    consumer.customMap(customMap);

                    consumer.beforeOutputFile((tableInfo, objectMap) -> {
                        // 获取表名
                        String tableName = tableInfo.getName();
                        // 根据后缀判断
                        if (isBillTable && tableName.endsWith("_head")) {
                            objectMap.put("controllerTemplatePath", "/templates/v2/head/controller.java.ftl");
                            objectMap.put("serviceTemplatePath", "/templates/v2/head/service.java.ftl");
                            objectMap.put("serviceImplTemplatePath", "/templates/v2/head/serviceImpl.java.ftl");
                            objectMap.put("mapperTemplatePath", "/templates/v2/head/mapper.java.ftl");
                            objectMap.put("xmlTemplatePath", "/templates/v2/head/mapper.xml.ftl");
                            objectMap.put("entityTemplatePath", "/templates/v2/head/entity.java.ftl");
                            objectMap.put("tableType", "head");
                            String baseName = tableName.replace("_head", "");
                            boolean hasInfoTable = false;
                            for (String f : infoSuffix) {
                                if (tableNameList.contains(baseName+f)) {
                                    hasInfoTable = true;
                                    objectMap.put("hasInfoTable", hasInfoTable);
                                }
                            }

                            customFile.put("ListVO.java", "templates/v2/vo/listVO.java.ftl");
                            customFile.put("ListParam.java", "templates/v2/vo/listParam.java.ftl");
                            customFile.put("headSql.sql", "templates/v2/head/head_sql.sql.ftl");
                            customFile.remove("VO.java");

                        }else if (isBillTable && tableName.endsWith("_detail")) {
                            // 设置明细表模板
                            objectMap.put("serviceTemplatePath", "/templates/v2/detail/service.java.ftl");
                            objectMap.put("serviceImplTemplatePath", "/templates/v2/detail/serviceImpl.java.ftl");
                            objectMap.put("mapperTemplatePath", "/templates/v2/detail/mapper.java.ftl");
                            objectMap.put("xmlTemplatePath", "/templates/v2/detail/mapper.xml.ftl");
                            objectMap.put("tableType", "detail");

                            customFile.put("VO.java", "templates/v2/detail/detailVO.java.ftl");
                            customFile.remove("ListVO.java");
                            customFile.remove("ListParam.java");
                            customFile.remove("entityTemplatePath");
                            customFile.remove("headSql.sql");
                        } else if (isBillTable ) {
                            for (String infoSuffix : infoSuffix) {
                                if (tableName.endsWith(infoSuffix)) {
                                    objectMap.put("serviceTemplatePath", "/templates/v2/info/service.java.ftl");
                                    objectMap.put("serviceImplTemplatePath", "/templates/v2/info/serviceImpl.java.ftl");
                                    objectMap.put("mapperTemplatePath", "/templates/v2/info/mapper.java.ftl");
                                    objectMap.put("xmlTemplatePath", "/templates/v2/info/mapper.xml.ftl");
                                    objectMap.put("tableType", "info");

                                    customFile.put("VO.java", "templates/v2/vo/InfoVO.java.ftl");
                                    customFile.remove("ListVO.java");
                                    customFile.remove("ListParam.java");
                                    customFile.remove("entityTemplatePath");
                                    customFile.remove("headSql.sql");

                                }

                            }

                        }
                    });


                })
                .templateEngine(new EnhanceFreemarkerTemplateEngine()) // 使用Freemarker引擎模板，默认的是Velocity引擎模板
        ;
        fastAutoGenerator.execute(); //执行以上配置

    }

}
