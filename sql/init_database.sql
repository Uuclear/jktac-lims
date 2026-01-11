-- ============================================
-- JKTAC LIMS 数据库初始化脚本
-- 数据库: MariaDB 10.6+
-- 编码: UTF8MB4
-- ============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS jktac_lims
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE jktac_lims;

-- ============================================
-- 1. 用户权限管理模块
-- ============================================

-- 部门表
CREATE TABLE IF NOT EXISTS lims_department (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '部门名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '部门代码',
    parent_id BIGINT NULL COMMENT '上级部门ID',
    description TEXT COMMENT '部门描述',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by_id BIGINT NULL COMMENT '创建人ID',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    FOREIGN KEY (parent_id) REFERENCES lims_department(id) ON DELETE SET NULL,
    INDEX idx_department_parent (parent_id),
    INDEX idx_department_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';

-- 用户表（继承Django auth_user）
CREATE TABLE IF NOT EXISTS lims_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) DEFAULT '',
    last_name VARCHAR(150) DEFAULT '',
    email VARCHAR(254) DEFAULT '',
    is_staff BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) NOT NULL DEFAULT 'client' COMMENT '用户角色',
    phone VARCHAR(20) NULL UNIQUE COMMENT '手机号',
    department_id BIGINT NULL COMMENT '所属部门',
    avatar VARCHAR(255) NULL COMMENT '头像',
    employee_id VARCHAR(50) NULL COMMENT '工号',
    position VARCHAR(50) NULL COMMENT '职位',
    FOREIGN KEY (department_id) REFERENCES lims_department(id) ON DELETE SET NULL,
    INDEX idx_user_role (role),
    INDEX idx_user_phone (phone),
    INDEX idx_user_department (department_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 用户登录日志表
CREATE TABLE IF NOT EXISTS lims_user_login_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL COMMENT '用户ID',
    ip_address VARCHAR(45) NOT NULL COMMENT 'IP地址',
    user_agent TEXT COMMENT '浏览器信息',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    status VARCHAR(20) DEFAULT 'success' COMMENT '登录状态',
    failure_reason VARCHAR(255) NULL COMMENT '失败原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES lims_user(id) ON DELETE CASCADE,
    INDEX idx_login_user_time (user_id, login_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录日志表';

-- ============================================
-- 2. 委托收样管理模块
-- ============================================

-- 委托方表
CREATE TABLE IF NOT EXISTS lims_client (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '委托方名称',
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '委托方编码',
    contact_person VARCHAR(50) NOT NULL COMMENT '联系人',
    contact_phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    email VARCHAR(254) NULL COMMENT '邮箱',
    address TEXT NULL COMMENT '地址',
    user_id BIGINT NULL UNIQUE COMMENT '关联用户ID',
    credit_level VARCHAR(10) DEFAULT 'B' COMMENT '信用等级',
    notes TEXT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES lims_user(id) ON DELETE SET NULL,
    INDEX idx_client_code (code),
    INDEX idx_client_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='委托方表';

-- 委托单表
CREATE TABLE IF NOT EXISTS lims_commission (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL UNIQUE COMMENT '委托单编号',
    client_id BIGINT NOT NULL COMMENT '委托方ID',
    project_name VARCHAR(200) NOT NULL COMMENT '工程名称',
    project_location VARCHAR(200) NULL COMMENT '工程地点',
    sample_name VARCHAR(200) NOT NULL COMMENT '样品名称',
    sample_model VARCHAR(100) NULL COMMENT '样品型号/规格',
    sample_quantity INT DEFAULT 1 COMMENT '样品数量',
    sample_unit VARCHAR(20) DEFAULT '组' COMMENT '样品单位',
    sample_source VARCHAR(200) NULL COMMENT '样品来源',
    sample_batch VARCHAR(100) NULL COMMENT '样品批号',
    test_basis TEXT NULL COMMENT '检测依据',
    test_parameters TEXT NOT NULL COMMENT '检测参数JSON',
    commission_date DATE NOT NULL COMMENT '委托日期',
    required_date DATE NULL COMMENT '要求完成日期',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态',
    total_price DECIMAL(10,2) DEFAULT 0 COMMENT '总费用',
    remarks TEXT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (client_id) REFERENCES lims_client(id) ON DELETE RESTRICT,
    INDEX idx_commission_code (code),
    INDEX idx_commission_status (status),
    INDEX idx_commission_client_status (client_id, status),
    INDEX idx_commission_date (commission_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='委托单表';

-- 收样记录表
CREATE TABLE IF NOT EXISTS lims_sample_receive (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    commission_id BIGINT NOT NULL COMMENT '委托单ID',
    receive_code VARCHAR(50) NOT NULL UNIQUE COMMENT '收样编号',
    receiver_id BIGINT NOT NULL COMMENT '收样人ID',
    receive_time DATETIME NOT NULL COMMENT '收样时间',
    actual_quantity INT NOT NULL COMMENT '实收数量',
    sample_condition VARCHAR(20) DEFAULT 'normal' COMMENT '样品状态',
    condition_notes TEXT NULL COMMENT '状态说明',
    storage_location VARCHAR(100) NULL COMMENT '存放位置',
    photos JSON DEFAULT '[]' COMMENT '样品照片',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (commission_id) REFERENCES lims_commission(id) ON DELETE CASCADE,
    FOREIGN KEY (receiver_id) REFERENCES lims_user(id) ON DELETE RESTRICT,
    INDEX idx_receive_code (receive_code),
    INDEX idx_receive_time (receive_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收样记录表';

-- ============================================
-- 3. 样品流转管理模块
-- ============================================

-- 样品流转表
CREATE TABLE IF NOT EXISTS lims_sample_workflow (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sample_receive_id BIGINT NOT NULL UNIQUE COMMENT '收样记录ID',
    current_status VARCHAR(30) DEFAULT 'received' COMMENT '当前状态',
    assigned_to_id BIGINT NULL COMMENT '当前负责人ID',
    priority INT DEFAULT 1 COMMENT '优先级',
    expected_complete_date DATE NULL COMMENT '预计完成日期',
    actual_complete_date DATE NULL COMMENT '实际完成日期',
    notes TEXT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sample_receive_id) REFERENCES lims_sample_receive(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to_id) REFERENCES lims_user(id) ON DELETE SET NULL,
    INDEX idx_workflow_status (current_status),
    INDEX idx_workflow_assignee (assigned_to_id, current_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='样品流转表';

-- 流转日志表
CREATE TABLE IF NOT EXISTS lims_workflow_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    workflow_id BIGINT NOT NULL COMMENT '流转ID',
    from_status VARCHAR(30) NOT NULL COMMENT '变更前状态',
    to_status VARCHAR(30) NOT NULL COMMENT '变更后状态',
    operator_id BIGINT NOT NULL COMMENT '操作人ID',
    action VARCHAR(20) NOT NULL COMMENT '操作类型',
    remarks TEXT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (workflow_id) REFERENCES lims_sample_workflow(id) ON DELETE CASCADE,
    FOREIGN KEY (operator_id) REFERENCES lims_user(id) ON DELETE RESTRICT,
    INDEX idx_workflow_log_workflow (workflow_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='流转日志表';

-- 试验任务表
CREATE TABLE IF NOT EXISTS lims_test_task (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    workflow_id BIGINT NOT NULL COMMENT '流转ID',
    tester_id BIGINT NOT NULL COMMENT '试验人员ID',
    test_items JSON DEFAULT '[]' COMMENT '试验项目',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '任务状态',
    start_time DATETIME NULL COMMENT '开始时间',
    end_time DATETIME NULL COMMENT '完成时间',
    notes TEXT NULL COMMENT '备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id BIGINT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (workflow_id) REFERENCES lims_sample_workflow(id) ON DELETE CASCADE,
    FOREIGN KEY (tester_id) REFERENCES lims_user(id) ON DELETE RESTRICT,
    INDEX idx_task_tester (tester_id),
    INDEX idx_task_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='试验任务表';

-- ============================================
-- 初始数据
-- ============================================

-- 插入默认管理员用户（密码: admin123）
-- 密码使用Django的PBKDF2加密
INSERT INTO lims_user (username, password, email, is_superuser, is_staff, is_active, role, date_joined)
VALUES ('admin', 'pbkdf2_sha256$600000$salt$hash', 'admin@example.com', TRUE, TRUE, TRUE, 'admin', NOW())
ON DUPLICATE KEY UPDATE username = username;

-- 插入默认部门
INSERT INTO lims_department (name, code, sort_order)
VALUES 
    ('试验室', 'LAB', 1),
    ('质量管理部', 'QM', 2),
    ('综合办公室', 'OFFICE', 3)
ON DUPLICATE KEY UPDATE name = name;

COMMIT;
