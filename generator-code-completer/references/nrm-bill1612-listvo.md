# NrmBill1612HeadListVO 参考

以下是在调整 ListVO 时需要参考的模板。关键规则：

1. **`@ExcelProperty` 全部放在 `*Str` 字段上**，原始 Date/Integer/BigDecimal 字段不加注解
2. 列头文字对应 `@ExcelProperty(value)`
3. 列顺序对应 `@ExcelProperty(index)`
4. `@ColumnWidth` 单独加在需要宽列的字段上（如单据编号、名称类）

## 参考代码 (NrmBill1612HeadListVO.java)

```java
package com.construct.nrm.vo;

import com.alibaba.excel.annotation.ExcelIgnoreUnannotated;
import com.construct.common.enums.nrm.NrmBillEnum;
import com.construct.common.utils.ParameterUtils;
import lombok.Data;
import io.swagger.annotations.ApiModel;
import com.construct.component.service.vo.BaseListVO;
import com.construct.common.enums.WFAuditStatusEnum;
import com.construct.common.utils.StringUtils;
import cn.hutool.core.util.ObjectUtil;
import com.alibaba.excel.annotation.ExcelProperty;
import com.alibaba.excel.annotation.write.style.ColumnWidth;

import java.math.BigDecimal;
import java.util.Date;

@Data
@ExcelIgnoreUnannotated
@ApiModel(value = "NrmBill1612HeadListVO对象", description = "列表方法出参VO")
public class NrmBill1612HeadListVO extends BaseListVO {

    /************* 承办项目/部门入参  ***************/
    @ExcelProperty(value = "承办项目/部门", index = 4)
    @ColumnWidth(21)
    private String initiateName;

    @ExcelProperty(value = "单据编号", index = 1)
    @ColumnWidth(21)
    private String billCode;

    @ExcelProperty(value = "单据状态", index = 2)
    @ColumnWidth(14)
    private String billStatusStr;

    /**
     * 支付状态
     */
    private Integer paymentStatus;

    @ExcelProperty(value = "支付状态", index = 3)
    @ColumnWidth(14)
    private String paymentStatusStr;

    @ExcelProperty(value = "制单人", index = 11)
    @ColumnWidth(14)
    private String initiateUserName;

    @ExcelProperty(value = "制单日期", index = 12)
    @ColumnWidth(14)
    private Date billDate;

    private String projectId;

    @ExcelProperty(value = "项目编号", index = 5)
    @ColumnWidth(14)
    private String fxmbh;

    @ExcelProperty(value = "项目名称", index = 6)
    @ColumnWidth(14)
    private String fxmmc;

    @ExcelProperty(value = "账套编号", index = 13)
    @ColumnWidth(14)
    private String fztmcid;

    @ExcelProperty(value = "账套名称", index = 14)
    @ColumnWidth(14)
    private String fztmc;

    @ExcelProperty(value = "所属组织编号", index = 15)
    @ColumnWidth(14)
    private String fsszzid;

    @ExcelProperty(value = "所属组织", index = 7)
    @ColumnWidth(14)
    private String fsszz;

    @ExcelProperty(value = "借款人", index = 8)
    @ColumnWidth(14)
    private String accountName;

    @ExcelProperty(value = "借款类型", index = 9)
    @ColumnWidth(14)
    private String jklx;

    @ExcelProperty(value = "借款金额(元)", index = 10)
    @ColumnWidth(14)
    private BigDecimal jkje;

    private String jkjeStr;

    public String getBillStatusStr() {
        if (ObjectUtil.isNotEmpty(this.getBillStatus())) {
            WFAuditStatusEnum anEnum = WFAuditStatusEnum.get(this.getBillStatus());
            this.billStatusStr = anEnum != null ? anEnum.getName() : "";
        }
        return this.billStatusStr;
    }

    public String getPaymentStatusStr() {
        if (ObjectUtil.isNotEmpty(this.getPaymentStatus())) {
            NrmBillEnum.PaymentStatusEnum anEnum = NrmBillEnum.PaymentStatusEnum.get(this.getPaymentStatus());
            this.paymentStatusStr = anEnum != null ? anEnum.getName() : "";
        }
        return this.paymentStatusStr;
    }

    public String getJkjeStr() {
        if (ObjectUtil.isNotEmpty(jkje)) {
            return ParameterUtils.amountStrHandler(jkje);
        }
        return StringUtils.NOT_DATA;
    }
}
```

## 字段类型处理规则

| 数据库类型 | Java 类型 | 原始字段（不导出） | Str 字段（导出） | getter 格式化方式 |
|-----------|----------|------------------|-----------------|-----------------|
| datetime | Date | `private Date billDate;` | `@ExcelProperty private String billDateStr;` | `SimpleDateFormat("yyyy-MM-dd HH:mm:ss")` |
| decimal | BigDecimal | `private BigDecimal jkje;` | `@ExcelProperty private String jkjeStr;` | `ParameterUtils.amountStrHandler()` |
| int(enum) | Integer | `private Integer paymentStatus;` | `@ExcelProperty private String paymentStatusStr;` | `XxxEnum.get(value).getName()` |
| int(是否) | Integer | `private Integer sfyfk;` | `@ExcelProperty private String sfyfkStr;` | `CommonEnum.YesOrNoEnum.get(value).getName()` |
| varchar | String | — | `@ExcelProperty private String xxx;` | 直接使用，不需要 Str |
