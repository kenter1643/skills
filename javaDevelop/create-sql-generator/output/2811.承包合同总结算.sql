-- =====================================================
-- 承包合同总结算 - 单据表结构设计
-- 领域: cm
-- 编号: 2811
-- 模块: 承包合同总结算
-- 创建时间: 2026-05-15
-- =====================================================

-- ----------------------------
-- Table structure for cm_bill_2811_head
-- ----------------------------
DROP TABLE IF EXISTS `cm_bill_2811_head`;
CREATE TABLE `cm_bill_2811_head` (
    `id` bigint NOT NULL COMMENT 'ID',
    `instance_id` varchar(64) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '实例ID',
    `bill_code` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '单据编号',
    `bill_type` varchar(10) COLLATE utf8mb4_general_ci NOT NULL COMMENT '单据类型，默认CBHA',
    `bill_status` tinyint NOT NULL DEFAULT '0' COMMENT '单据状态，-1-审批不通过；0-草稿；1-审批中；2-审批通过；3-撤回',
    `bill_date` datetime DEFAULT NULL COMMENT '制单时间',
    `rel_bill_id` bigint DEFAULT NULL COMMENT '关联单据ID',
    `rel_bill_type` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '关联单据类型',
    `rel_bill_code` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '关联单据编码',
    `bill_dept_id` bigint DEFAULT NULL COMMENT '制单（业务）部门ID',
    `bill_dept_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '制单（业务）部门名称',
    `print_num` int DEFAULT NULL COMMENT '打印次数',
    `audit_user_id` bigint DEFAULT NULL COMMENT '审核人id，来源sys_user.user_id',
    `audit_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '审核人名称',
    `audit_date` datetime DEFAULT NULL COMMENT '审批时间',
    `flow_key` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '流程key',
    `dept_id` bigint DEFAULT NULL COMMENT '创建部门id,来源：sys_dept.dept_id',
    `create_user_id` bigint DEFAULT NULL COMMENT '创建人,来源：sys_user.user_id',
    `create_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人姓名.来源：sys_suer.nick_name',
    `create_date` datetime DEFAULT NULL COMMENT '创建时间',
    `initiate_user_id` bigint DEFAULT NULL COMMENT '发起人ID(制单人ID)',
    `initiate_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发起人姓名（制单人姓名）',
    `initiate_dept_id` bigint DEFAULT NULL COMMENT '发起人部门Id(承办部门Id)',
    `initiate_dept_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发起人部门名称(承办部门名称)',
    `initiate_project_id` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '承包项目id',
    `initiate_project_name` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '承包项目名称',
    `bill_display_date` datetime DEFAULT NULL COMMENT '呈文日期',
    `update_user_id` bigint DEFAULT NULL COMMENT '最后编辑人,来源：sys_user.user_id',
    `update_user_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '最后编辑人姓名.来源：sys_suer.nick_name',
    `update_date` datetime DEFAULT NULL COMMENT '编辑时间',
    `is_deleted` tinyint DEFAULT '0' COMMENT '是否删除：0否1是',
    `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间戳',
    `gmt_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间戳',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  COMMENT='承包合同总结算';

-- ----------------------------
-- Table structure for cm_bill_2811_detail
-- ----------------------------
DROP TABLE IF EXISTS `cm_bill_2811_detail`;
CREATE TABLE `cm_bill_2811_detail` (
    `id` bigint NOT NULL COMMENT 'ID',
    `head_id` bigint NOT NULL COMMENT '主单ID',
    `project_id` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目id',
    `FXMBH` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目编号',
    `FXMMC` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目名称',
    `FZTMCID` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账套编号',
    `FZTMC` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '账套名称',
    `FXMLX` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目类型',
    `fcontract_type` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '合同类型',
    `FSSZZID` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属组织编号',
    `FSSZZ` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '所属组织',
    `project_properties` tinyint DEFAULT NULL COMMENT '项目属性',

    `contract_id` bigint DEFAULT NULL COMMENT '承包合同id，来源：cms_contact_base.id',
    `contract_no` varchar(50) NOT NULL COMMENT '承包合同编号',
    `paper_contract_number` varchar(50) NOT NULL COMMENT '纸质合同编号',
    `contract_name` varchar(200) NOT NULL COMMENT '合同名称',
    `contract_total_amt_tax_incl` decimal(24,8) NOT NULL COMMENT '合同总金额（含税）(元)',
    `contract_total_amt_tax_excl` decimal(24,8) NOT NULL COMMENT '合同总金额（不含税）(元)',
    `project_tax_rate` decimal(24,8) NOT NULL COMMENT '项目税率',
    `provisional_sum_amt` decimal(24,8) DEFAULT NULL COMMENT '暂列金额(元)',
    `declare_date` datetime NOT NULL COMMENT '申报日期',
    `floor_area` decimal(24,8) DEFAULT NULL COMMENT '建筑面积（㎡）',
    `is_first_review` tinyint NOT NULL COMMENT '是否一审，是 否',
    `is_final_review` tinyint NOT NULL COMMENT '是否终审，是 否',
    `ref_settlement_bill_id` bigint DEFAULT NULL COMMENT '引用承包总结算单',
    `ref_settlement_bill_code` varchar(50) DEFAULT NULL COMMENT '引用承包总结算单编号',
    `actual_completion_date` datetime NOT NULL COMMENT '实际竣工日期',
    `handover_date` datetime NOT NULL COMMENT '工程移交日期',
    `civil_warranty_expire_date` datetime NOT NULL COMMENT '土建质保金到期日',
    `civil_warranty_amt` decimal(24,8) NOT NULL COMMENT '土建质保金金额(元)',
    `civil_warranty_rate` decimal(24,8) NOT NULL COMMENT '土建质保金比例',
    `waterproof_warranty_expire_date` datetime DEFAULT NULL COMMENT '防水质保金到期日',
    `waterproof_warranty_amt` decimal(24,8) DEFAULT NULL COMMENT '防水质保金金额(元)',
    `waterproof_warranty_rate` decimal(24,8) DEFAULT NULL COMMENT '防水质保金比例',
    `received_progress_amt` decimal(24,8) NOT NULL COMMENT '已收进度款(元)',
    `deduction_penalty_amt` decimal(24,8) NOT NULL COMMENT '扣罚款(元)',
    `actual_total_cost` decimal(24,8) NOT NULL COMMENT '实际总成本(元)',
    `target_profit_rate` decimal(24,8) NOT NULL COMMENT '目标利润率',
    `reported_settlement_amt` decimal(24,8) NOT NULL COMMENT '上报结算金额(元)',
    `approved_settlement_amt` decimal(24,8) NOT NULL COMMENT '总结算审批金额(元)',
    `settlement_amt_analysis` varchar(2000) DEFAULT NULL COMMENT '结算金额分析',
    `remark` varchar(2000) DEFAULT NULL COMMENT '备注',
    `is_deleted` tinyint DEFAULT '0' COMMENT '是否删除：0否1是',
    `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间戳',
    `gmt_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间戳',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  COMMENT='承包合同总结算单据详情';

-- ----------------------------
-- Indexes for cm_bill_2811_detail
-- ----------------------------
CREATE INDEX index_head_id ON cm_bill_2811_detail (head_id);

-- ================================================================================
-- Info表 - 关键事项明细
-- ================================================================================
DROP TABLE IF EXISTS cm_bill_2811_info;
CREATE TABLE `cm_bill_2811_info` (
    `id` bigint NOT NULL COMMENT 'ID',
    `head_id` bigint NOT NULL COMMENT '主单ID',

    `row_no` int NOT NULL COMMENT '行号',
    `key_item` varchar(500) NOT NULL COMMENT '关键事项',
    `proposed_submit_amt` decimal(24,8) NOT NULL COMMENT '拟报出金额(万元)',
    `estimated_settlement_amt` decimal(24,8) NOT NULL COMMENT '预计结算金额(万元)',
    `estimated_risk_deduction_amt` decimal(24,8) NOT NULL COMMENT '预计风险核减金额(万元)',
    `risk_reason` varchar(500) DEFAULT NULL COMMENT '风险原因',
    `proposed_measures` varchar(500) DEFAULT NULL COMMENT '拟采取措施',
    `is_deleted` tinyint DEFAULT '0' COMMENT '是否删除：0否1是',
    `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间戳',
    `gmt_modified` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后修改时间戳',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB  COMMENT='承包合同总结算关键事项明细';

CREATE INDEX index_head_id ON cm_bill_2811_info (head_id);
