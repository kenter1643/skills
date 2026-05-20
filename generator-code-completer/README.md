
# Generator Code Completer 代码补充器

本 Skill 用于在 MyBatisPlusGeneratorV2 生成初始代码后，根据接口文档(.md)批量补充和调整代码。

## 使用说明

### 第一步：创建数据表

在数据库中执行 `单据.sql` 文件，生成对应的数据表（head 表和 detail 表）。

### 第二步：生成初始代码

在 `MyBatisPlusGeneratorV2` 中调整对应的领域（territory）、表名、编号（code），然后执行 `MyBatisPlusGeneratorV2` 中的 `main` 方法，生成初始的 Service、Controller、VO、Mapper XML 等代码。

### 第三步：执行代码补充技能

准备好对应的 `单据接口文档.md` 文件，输入文档路径并执行 `/generator-code-completer` 技能，即可根据接口文档自动补充和调整生成的代码。