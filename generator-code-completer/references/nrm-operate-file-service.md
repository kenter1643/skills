# NrmOperateFileService 参考实现

以下是在给 OperateFileService 补充 `saveOperateFile` 和 `getOperateFile` 方法时，需要参考的模板。

## 接口定义参考 (NrmOperateFileService.java)

```java
/**
 * 保存经营文件.
 * 逻辑：比较新旧文件差异，新增的插入，删除的移除
 * @param businessType 业务类型，来源枚举
 * @param businessId 业务id
 * @param files 文件列表
 */
void saveOperateFile(String businessType, Long businessId, List<BaseFile> files);

/**
 * 获取经营文件.
 *
 * @param businessType 业务类型，来源枚举
 * @param businessId 业务id
 * @return 经营文件列表
 */
List<BaseFile> getOperateFile(String businessType, Long businessId);
```

## 实现类参考 (NrmOperateFileServiceImpl.java)

```java
@Override
public void saveOperateFile(String businessType, Long businessId, List<BaseFile> files) {
    if(ObjectUtil.isEmpty(files) || files.isEmpty()){
        QueryWrapper<NrmOperateFile> wrapper = new QueryWrapper<>();
        wrapper.lambda().eq(NrmOperateFile::getBusinessType, businessType)
                .eq(NrmOperateFile::getBusinessId, businessId);
        remove(wrapper);
        return;
    }
    //查询之前的文件
    QueryWrapper<NrmOperateFile> wrapper = new QueryWrapper<>();
    wrapper.lambda().eq(NrmOperateFile::getBusinessType, businessType)
            .eq(NrmOperateFile::getBusinessId, businessId)
            .eq(NrmOperateFile::getIsDeleted, CommonEnum.IsDeletedEnum.NOT_DELETE.getKey());
    List<NrmOperateFile> list = list(wrapper);

    Map<String, BaseFile> collect = files.stream()
            .collect(Collectors.toMap(BaseFile::getFileUrl, Function.identity()));

    List<String> newFileUrl = files.stream().map(BaseFile::getFileUrl).collect(Collectors.toList());
    List<String> oldFileUrl = list.stream().map(NrmOperateFile::getFileUrl).collect(Collectors.toList());

    List<String> addList = new ArrayList<>(newFileUrl);
    addList.removeAll(oldFileUrl);

    List<String> deleteList = new ArrayList<>(oldFileUrl);
    deleteList.removeAll(newFileUrl);

    if(!deleteList.isEmpty()){
        QueryWrapper<NrmOperateFile> deleteWrapper = new QueryWrapper<>();
        deleteWrapper.lambda().eq(NrmOperateFile::getBusinessId, businessId)
                .eq(NrmOperateFile::getBusinessType, businessType)
                .in(NrmOperateFile::getFileUrl, deleteList);
        remove(deleteWrapper);
    }

    if(!addList.isEmpty()){
        List<NrmOperateFile> addObjs = new ArrayList<>();
        addList.forEach(fileUrl -> {
            NrmOperateFile addObj = new NrmOperateFile();
            BaseFile baseFile = collect.get(fileUrl);
            BeanUtils.copyProperties(baseFile, addObj);
            addObj.setBusinessType(businessType);
            addObj.setBusinessId(businessId);
            addObjs.add(addObj);
        });
        saveBatch(addObjs);
    }
}

@Override
public List<BaseFile> getOperateFile(String businessType, Long businessId) {
    List<BaseFile> resFiles = new ArrayList<>();
    QueryWrapper<NrmOperateFile> wrapper = new QueryWrapper<>();
    wrapper.lambda().eq(NrmOperateFile::getBusinessType, businessType)
            .eq(NrmOperateFile::getBusinessId, businessId);
    List<NrmOperateFile> list = list(wrapper);

    list.forEach(item -> {
        BaseFile file = new BaseFile();
        BeanUtils.copyProperties(item, file);
        resFiles.add(file);
    });
    return resFiles;
}
```

## 关键注意事项

1. 将模板中的 `NrmOperateFile` 替换为实际的实体类名（如 `CmOperateFile`）
2. 导入必要的类：`BaseFile`, `CommonEnum`, `BeanUtils`, `QueryWrapper`, `ObjectUtil`
3. `saveOperateFile` 使用按文件URL差集比对的方式：新增的插入，删除的移除，已有的不动
4. `getOperateFile` 按 businessType + businessId 查询，将实体拷贝为 BaseFile 返回
