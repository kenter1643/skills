# -*- coding: utf-8 -*-
"""
文档生成器
根据合并后的字段生成 Markdown 接口文档
"""

import os
import sys

_skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _skill_root not in sys.path:
    sys.path.insert(0, _skill_root)

from config import Config
from merger.merge_fields import (
    get_list_fields,
    get_fuzzy_search_fields,
    get_advanced_search_fields,
    get_enum_fields,
)
import utils


# 列表出参中需要过滤掉的通用框架字段
EXCLUDED_LIST_FIELDS = {
    "id",
    "billStatus",
    "billType",
    "createUserId",
    "createUserName",
    "createDate",
    "isPromoter",
    "initiateType",
    "initiateId",
    "initiateName",
    "initiateDeptId",
    "initiateDeptName",
    "initiateProjectId",
    "initiateProjectName",
    "initiateUserId",
    "rowNo",
}

# 详情、保存、检查参数接口中需要过滤掉的通用框架字段（来自公共基类，无需在业务文档中列出）
EXCLUDED_FIELDS = {
    "instanceId",
    "auditRecordDBVO",
    "flowKey",
    "startTaskName",
    "auditType",
    "billDate",
    "auditDate",
    "billCode",
    "isDraft",
    "qyhtmb",
    "hasInitiateUserNull",
    "initiateId",
    "initiateName",
    "initiateType",
    "initiateUserId",
    "initiateUserName",
    "initiateDeptId",
    "initiateDeptName",
    "initiateProjectId",
    "initiateProjectName",
    "title",
    "isPermission",
    "budgetYear",
    "isDeleted",
    "billDeptId",
    "billDeptName",
    "printNum",
    "auditUserId",
    "auditUserName",
    "deptId",
    "gmtCreate",
    "gmtModified",
}


def get_flow_key():
    api_prefix = Config.API_PREFIX or "/fam/bill"
    bill_code = Config.BILL_CODE or "03"
    path = api_prefix.rstrip("/") + "/" + bill_code
    return utils.path_to_camelcase(path) + "Approval"


def generate_field_row(
    field_name, field_info, prefix="", add_str=False, required=False
):
    """生成字段行"""
    name = field_name
    if prefix:
        name = prefix + name[0].upper() + name[1:] if name else ""
    if add_str:
        name = name + "Str"

    java_type = field_info["java_type"]
    if add_str:
        java_type = "String"

    comment = field_info["comment"]
    if add_str:
        comment = comment + "文本"

    if field_info["enum_values"]:
        enum_text = field_info["enum_values"].replace("\n", "、").strip()
        comment = comment + "：" + enum_text

    required_str = "是" if required else "否"
    return (
        "| " + name + " | " + java_type + " | " + required_str + " | " + comment + " |"
    )


def generate_output_field_row(field_name, field_info):
    """生成出参字段行"""
    comment = field_info["comment"]
    if field_info["enum_values"]:
        enum_text = field_info["enum_values"].replace("\n", "、").strip()
        comment = comment + "：" + enum_text
    return "| " + field_name + " | " + field_info["java_type"] + " | " + comment + " |"


def get_info_list_field_names(info_lists):
    names = set()
    for info_list in info_lists:
        for field in info_list.get("fields", []):
            names.add(field["name"])
    return names


def generate_output_info_list_rows(info_lists):
    doc = ""
    for info_list in info_lists:
        doc += f"| {info_list['name']} | List | {info_list['comment']} |\n"
        doc += "| id | Long | 明细id |\n"
        doc += "| headId | Long | 主单id |\n"
        for field in info_list.get("fields", []):
            if field['name'] in ('id', 'headId', 'head_id'):
                continue
            doc += f"| {field['name']} | {field['java_type']} | {field['comment']} |\n"
    return doc


def generate_input_info_list_rows(info_lists):
    doc = ""
    for info_list in info_lists:
        doc += f"| {info_list['name']} | List |  | {info_list['comment']} |\n"
        doc += "| id | Long | 否 | 明细id |\n"
        doc += "| headId | Long | 否 | 主单id |\n"
        for field in info_list.get("fields", []):
            if field['name'] in ('id', 'headId', 'head_id'):
                continue
            doc += f"| {field['name']} | {field['java_type']} | 否 | {field['comment']} |\n"
    return doc


def generate_check_param_info_list_rows(info_lists):
    doc = ""
    for info_list in info_lists:
        doc += f"| {info_list['name']} | List | {info_list['comment']} |\n"
        doc += "| id | Long | 明细id |\n"
        doc += "| headId | Long | 主单id |\n"
        for field in info_list.get("fields", []):
            if field['name'] in ('id', 'headId', 'head_id'):
                continue
            doc += f"| {field['name']} | {field['java_type']} | {field['comment']} |\n"
    return doc


def generate_list_interface(merged_fields, path):
    """生成列表接口"""
    doc = (
        """### 单据列表

```plaintext
GET   """
        + path
        + """/list
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| 分页参数 |  |  |  |
|  |  |  |  |
| 模糊查询 |  |  |  |
"""
    )

    fuzzy_fields = get_fuzzy_search_fields(merged_fields)
    for field_name in fuzzy_fields:
        # if field_name in EXCLUDED_QUERY_FIELDS:
        #     continue
        field_info = merged_fields[field_name]
        doc += generate_field_row(field_name, field_info, prefix="first") + "\n"
    doc += "| firstKeyWord | String | 否 | 全部 |\n"

    doc += "| 高级查询 |  |  |  |\n"

    advanced_fields = get_advanced_search_fields(merged_fields)
    for field_name in advanced_fields:
        # if field_name in EXCLUDED_QUERY_FIELDS:
        #     continue
        field_info = merged_fields[field_name]
        if field_info["java_type"] == "Date":
            field_name = utils.get_filed_sub_date(field_name)
            doc += (
                "| "
                + field_name
                + "BeginDate | Date | 否 | "
                + field_info["comment"]
                + "开始 |\n"
            )
            doc += (
                "| "
                + field_name
                + "EndDate | Date | 否 | "
                + field_info["comment"]
                + "结束 |\n"
            )
        else:
            doc += generate_field_row(field_name, field_info) + "\n"

    doc += """
#### 出参示例

```plaintext
{

}
```

#### 出参说明（黄色字体含Str）

| 名称 | 类型 | 备注 | 导出排序 |
| --- | --- | --- | --- |
| id | Long | 单据id |  |
"""

    # 列表出参中需要额外带出的 ID 字段映射 {目标字段: 前置ID字段}
    extra_id_before = {
        "fxmbh": "projectId",
        "fsszz": "fsszzid",
        "fztmc": "fztmcid",
        "contractCode": "contractId",
        "paperContractNumber": "contractId",
        "contractName": "contractId",
    }
    extra_id_added = set()

    list_fields = get_list_fields(merged_fields)
    export_sort_index = 1
    for field_name in list_fields:
        if field_name in EXCLUDED_LIST_FIELDS:
            continue
        field_info = merged_fields[field_name]
        comment = field_info["comment"]
        if field_info["enum_values"]:
            comment = comment + "：" + field_info["enum_values"]

        # 在指定字段前插入对应的 ID 字段（每个ID只输出一次）
        if field_name in extra_id_before:
            id_field = extra_id_before[field_name]
            if id_field in merged_fields and id_field not in EXCLUDED_LIST_FIELDS and id_field not in extra_id_added:
                extra_id_added.add(id_field)
                id_info = merged_fields[id_field]
                id_comment = id_info["comment"]
                if id_info["enum_values"]:
                    id_comment = id_comment + "：" + id_info["enum_values"]
                doc += (
                    "| "
                    + id_field
                    + " | "
                    + id_info["java_type"]
                    + " | "
                    + id_comment
                    + " |  |\n"
                )

        if field_info["java_type"] == "String":
            export_sort = str(export_sort_index)
            export_sort_index += 1
        else:
            export_sort = ""

        doc += (
            "| "
            + field_name
            + " | "
            + field_info["java_type"]
            + " | "
            + comment
            + " | "
            + export_sort
            + " |\n"
        )
        if field_info["with_str"]:
            doc += (
                "| "
                + field_name
                + "Str | String | "
                + comment
                + "文本 | "
                + str(export_sort_index)
                + " |\n"
            )
            export_sort_index += 1

    return doc


def generate_detail_interface(merged_fields, info_lists, path, has_attachment=False, field_order=None):
    """生成详情接口"""
    doc = (
        """

### 单据详情

```plaintext
GET """
        + path
        + """/detail
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 是 | 单据id |

#### 出参示例

```plaintext
{

}
```

#### 出参说明（黄色字体含Str）

| 名称 | 类型 | 备注 |
| --- | --- | --- |
| id | Long | ID |
| headId | Long | 主单id |
"""
    )

    # 添加附件列表字段（如果有附件）
    if has_attachment:
        doc += "| fileList | List<BaseFile> | 附件列表 |\n"

    info_list_field_names = get_info_list_field_names(info_lists)
    # 按 field_order 顺序遍历字段，排除明细区域
    ordered_fields = field_order if field_order else list(merged_fields.keys())

    # 收集主信息字段用于重复检测
    main_field_names = []
    for field_name in ordered_fields:
        if field_name not in merged_fields:
            continue
        field_info = merged_fields[field_name]
        if field_name in EXCLUDED_FIELDS:
            continue
        if field_name == "id":
            continue
        if field_info.get("section") == "detail":
            continue
        if (
            field_name in info_list_field_names
            and field_info.get("section") == "details"
        ):
            continue
        main_field_names.append(field_name)

    # 重复字段检测
    if len(main_field_names) != len(set(main_field_names)):
        from collections import Counter
        duplicates = [name for name, count in Counter(main_field_names).items() if count > 1]
        print(f"[WARNING] 详情接口存在重复字段: {duplicates}")

    # 需要前置的 ID 字段映射
    detail_extra_id_before = {"fxmbh": "projectId"}
    detail_extra_id_added = set()

    for field_name in main_field_names:
        # 在 fxmbh 前插入 projectId
        if field_name in detail_extra_id_before:
            id_field = detail_extra_id_before[field_name]
            if id_field in merged_fields and id_field not in EXCLUDED_FIELDS and id_field not in detail_extra_id_added:
                detail_extra_id_added.add(id_field)
                doc += generate_output_field_row(id_field, merged_fields[id_field]) + "\n"
                if merged_fields[id_field]["with_str"]:
                    doc += (
                        "| "
                        + id_field
                        + "Str | String | "
                        + merged_fields[id_field]["comment"]
                        + "文本 |\n"
                    )

        field_info = merged_fields[field_name]
        doc += generate_output_field_row(field_name, field_info) + "\n"
        if field_info["with_str"]:
            doc += (
                "| "
                + field_name
                + "Str | String | "
                + field_info["comment"]
                + "文本 |\n"
            )

    doc += "|  |  |  |\n"
    doc += generate_output_info_list_rows(info_lists)
    return doc


def generate_save_interface(merged_fields, info_lists, path, has_attachment=False, field_order=None):
    """生成保存接口，按 section 分组：主信息在前，明细以 details 数组呈现"""
    doc = (
        """

### 单据保存

```plaintext
post """
        + path
        + """/save
```

#### 出参示例

```plaintext
{

}
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 否 | ID |
| headId | Long | 否 | 主单id |
"""
    )

    # 添加附件列表字段（如果有附件）
    if has_attachment:
        doc += "| fileList | List<BaseFile> | 是 | 附件列表 |\n"

    info_list_field_names = get_info_list_field_names(info_lists)
    savable_fields = {
        k: v
        for k, v in merged_fields.items()
        if k not in info_list_field_names or v.get("section") != "details"
    }

    # 按 field_order 顺序输出主信息区字段，排除明细区域
    ordered_fields = field_order if field_order else list(merged_fields.keys())
    detail_field_names = []
    main_field_names = []

    for field_name in ordered_fields:
        if field_name not in savable_fields:
            continue
        if field_name in EXCLUDED_FIELDS:
            continue
        if field_name == "id":
            continue
        field_info = savable_fields[field_name]
        if field_info.get("section") == "detail":
            continue
        if field_info.get("section", "main") == "main":
            main_field_names.append(field_name)
        elif field_info.get("section") == "details" and field_name not in info_list_field_names:
            detail_field_names.append(field_name)

    # 重复字段检测
    if len(main_field_names) != len(set(main_field_names)):
        from collections import Counter
        duplicates = [name for name, count in Counter(main_field_names).items() if count > 1]
        print(f"[WARNING] 保存接口存在重复字段: {duplicates}")

    # 需要前置的 ID 字段映射
    save_extra_id_before = {"fxmbh": "projectId"}
    save_extra_id_added = set()

    for field_name in main_field_names:
        # 在 fxmbh 前插入 projectId
        if field_name in save_extra_id_before:
            id_field = save_extra_id_before[field_name]
            if id_field in savable_fields and id_field not in EXCLUDED_FIELDS and id_field not in save_extra_id_added:
                save_extra_id_added.add(id_field)
                required = savable_fields[id_field].get("is_required", False)
                doc += generate_field_row(id_field, savable_fields[id_field], required=required) + "\n"

        field_info = savable_fields[field_name]
        required = field_info.get("is_required", False)
        doc += generate_field_row(field_name, field_info, required=required) + "\n"

    if detail_field_names:
        doc += "| details | List |  | 明细列表 |\n"
        for field_name in detail_field_names:
            field_info = savable_fields[field_name]
            required = field_info.get("is_required", False)
            doc += (
                generate_field_row(
                    field_name, field_info, prefix="details", required=required
                )
                + "\n"
            )

    doc += "|  |  |  |  |\n"
    doc += generate_input_info_list_rows(info_lists)
    return doc


def generate_delete_interface(path):
    """生成删除接口"""
    return (
        """

### 删除单据

```plaintext
POST  """
        + path
        + """/delete
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 是 | 单据ID |

#### 出参示例

```plaintext
{

}
```

#### 出参说明

| 名称 | 类型 | 备注 |
| --- | --- | --- |
"""
    )


def generate_revocation_interface(path):
    """生成撤回接口"""
    return (
        """

### 撤回

```plaintext
Post """
        + path
        + """/revocation
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 是 | 单据ID |

#### 出参示例

```plaintext
{

}
```

#### 出参说明

| 名称 | 类型 | 备注 |
| --- | --- | --- |
"""
    )


def generate_audit_interface(path):
    """生成审核接口"""
    return (
        """

### 审核

```plaintext
  """
        + path
        + """/audit
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 是 | 单据ID |
| instanceId | String |  | 流程实例ID |
| taskId | String | 是 | 任务ID |
| taskDefKey | String | 是 | 任务DefKey |
| auditStatus | Integer | 是 | 审批类型，0-审批不通过，1-审批通过 |
| auditFile | List<BaseFile> | 否 | 文件 |
| auditRemark | String | 是 | 审批意见 |
| auditType | String |  | 审批类型 |
| assigneeUserIds | String |  | 重新指定审批人ID |
| isAddSignUser | Integer |  | 该用户是否加签人员 |
| signatureUrl | String |  | 签名Url |"""
    )


def generate_deliver_interface(path):
    """生成转交接口"""
    return (
        """

### 转交

```plaintext
POST """
        + path
        + """/deliver
```

#### 入参说明

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| id | Long | 是 | 单据ID |
| receiveUserId | String | 是 | 转交人ID |
| receiveUserName | String | 是 | 转交人姓名 |
| receiveDeptId | Integer | 是 | 转交人部门ID |
| receiveDeptName | String | 是 | 转交人部门名称 |

#### 出参说明

| 名称 | 类型 | 备注 |
| --- | --- | --- |
"""
    )


def generate_export_interface(path):
    """生成导出接口"""
    return (
        """

### 导出

```plaintext
get  """
        + path
        + """/export
```

| 名称 | 类型 | 是否必传 | 备注 |
| --- | --- | --- | --- |
| 跟列表查询参数一致 |  |  |  |

#### 出参示例

```plaintext
{

}
```

#### 出参说明

| 名称 | 类型 | 备注 |
| --- | --- | --- |
"""
    )


def generate_check_param_interface(merged_fields, info_lists, path, has_attachment=False, field_order=None):
    """生成校验参数接口"""
    doc = (
        """

### 保存--校验参数(提交前调用)

```plaintext
POST  """
        + path
        + """/checkParam
```

#### 入参说明

| 名称 | 类型 | 备注 |
| --- | --- | --- |
| id | Long | ID |
| headId | Long | 主单id |
"""
    )

    # 添加附件列表字段（如果有附件）
    if has_attachment:
        doc += "| fileList | List<BaseFile> | 附件列表 |\n"

    info_list_field_names = get_info_list_field_names(info_lists)
    # 按 field_order 顺序遍历字段，排除明细区域
    ordered_fields = field_order if field_order else list(merged_fields.keys())

    # 收集主信息字段用于重复检测
    main_field_names = []
    for field_name in ordered_fields:
        if field_name not in merged_fields:
            continue
        field_info = merged_fields[field_name]
        if field_name in EXCLUDED_FIELDS:
            continue
        if field_name == "id":
            continue
        if field_info.get("section") == "detail":
            continue
        if (
            field_name in info_list_field_names
            and field_info.get("section") == "details"
        ):
            continue
        main_field_names.append(field_name)

    # 重复字段检测
    if len(main_field_names) != len(set(main_field_names)):
        from collections import Counter
        duplicates = [name for name, count in Counter(main_field_names).items() if count > 1]
        print(f"[WARNING] 检查参数接口存在重复字段: {duplicates}")

    # 需要前置的 ID 字段映射
    check_extra_id_before = {"fxmbh": "projectId"}
    check_extra_id_added = set()

    for field_name in main_field_names:
        # 在 fxmbh 前插入 projectId
        if field_name in check_extra_id_before:
            id_field = check_extra_id_before[field_name]
            if id_field in merged_fields and id_field not in EXCLUDED_FIELDS and id_field not in check_extra_id_added:
                check_extra_id_added.add(id_field)
                doc += generate_output_field_row(id_field, merged_fields[id_field]) + "\n"
                if merged_fields[id_field]["with_str"]:
                    doc += (
                        "| "
                        + id_field
                        + "Str | String | "
                        + merged_fields[id_field]["comment"]
                        + "文本 |\n"
                    )

        field_info = merged_fields[field_name]
        doc += generate_output_field_row(field_name, field_info) + "\n"

    doc += "|  |  |  |\n"
    doc += generate_check_param_info_list_rows(info_lists)

    doc += """
#### 出参示例

```plaintext
{

}
```
"""
    return doc


def generate_doc(merged_result, config):
    """生成完整的接口文档"""
    merged_fields = merged_result["fields"]
    info_lists = merged_result.get("info_lists", [])
    has_attachment = merged_result.get("has_attachment", False)
    field_order = merged_result.get("field_order", [])
    bill_code = config.BILL_CODE
    api_prefix = config.API_PREFIX

    if not api_prefix.endswith("/"):
        api_prefix += "/"

    path = api_prefix + bill_code

    doc = f"## 流程Key：{get_flow_key()}\n"
    doc += generate_list_interface(merged_fields, path)
    doc += generate_detail_interface(merged_fields, info_lists, path, has_attachment, field_order)
    doc += generate_save_interface(merged_fields, info_lists, path, has_attachment, field_order)
    doc += generate_delete_interface(path)
    doc += generate_revocation_interface(path)
    doc += generate_audit_interface(path)
    doc += generate_deliver_interface(path)
    doc += generate_export_interface(path)
    doc += generate_check_param_interface(
        merged_fields, info_lists, path, has_attachment, field_order
    )
    return doc


def save_doc(content, config):
    """保存文档到文件"""
    output_dir = config.OUTPUT_DIR
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename = config.BUSINESS_NAME + ".md"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return output_path
