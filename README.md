# JKTAC LIMS - 工地试验室信息管理系统

## 项目简介

基于 Django + DRF + Vue3 + Element Plus 的工地试验室 LIMS 系统框架，采用前后端分离、模块化、易扩展的架构设计。

## 技术栈

### 后端
- Python 3.9+
- Django 4.2+
- Django REST Framework 3.14+
- MariaDB 10.6+
- Redis 7.0+
- MinIO (对象存储)

### 前端
- Vue 3.4+
- Element Plus 2.4+
- Vue Router 4
- Pinia 2
- Axios
- ECharts (图表)

### 部署
- 1Panel
- Docker & Docker Compose
- Nginx

## 系统模块

| 模块 | 说明 | 后端App | 前端路由 |
|------|------|---------|----------|
| 用户权限管理 | 用户、角色、权限管理 | users | /users |
| 委托收样管理 | 委托单、收样记录 | samples | /samples |
| 样品流转管理 | 样品状态跟踪 | workflow | /workflow |
| 原始记录管理 | 记录模板生成 | records | /records |
| OCR识别模块 | 扫描件识别、报告生成 | ocr | /ocr |
| 质量体系管理 | 体系文件管理 | quality | /quality |
| 能力管理 | 检测标准、参数管理 | capability | /capability |
| 设备管理 | 设备、校准管理 | equipment | /equipment |
| 平面图管理 | 试验室可视化 | floorplan | /floorplan |
| 数据汇总 | 报表统计 | reports | /reports |
| AI校验 | 文档智能校验 | ai_verify | /ai-verify |
| 云查询 | 外部查询系统 | cloud_query | /cloud |

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-repo/jktac_lims.git
cd jktac_lims

# 后端环境
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 前端环境
cd ../frontend
npm install
```

### 2. 配置数据库

```bash
# 复制环境配置文件
cp backend/.env.example backend/.env

# 修改数据库配置
# 执行数据库迁移
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 3. 启动服务

```bash
# 后端
cd backend
python manage.py runserver

# 前端
cd frontend
npm run dev
```

## 项目结构

```
jktac_lims/
├── backend/                    # Django后端
│   ├── config/                 # 项目配置
│   ├── apps/                   # 应用模块
│   │   ├── users/              # 用户权限
│   │   ├── samples/            # 委托收样
│   │   ├── workflow/           # 样品流转
│   │   ├── records/            # 原始记录
│   │   ├── ocr/                # OCR识别
│   │   ├── quality/            # 质量体系
│   │   ├── capability/         # 能力管理
│   │   ├── equipment/          # 设备管理
│   │   ├── floorplan/          # 平面图
│   │   ├── reports/            # 数据汇总
│   │   ├── ai_verify/          # AI校验
│   │   └── cloud_query/        # 云查询
│   ├── common/                 # 公共组件
│   └── requirements.txt
├── frontend/                   # Vue3前端
│   ├── src/
│   │   ├── api/                # API接口
│   │   ├── components/         # 公共组件
│   │   ├── views/              # 页面视图
│   │   ├── stores/             # Pinia状态
│   │   ├── router/             # 路由配置
│   │   └── utils/              # 工具函数
│   └── package.json
├── deploy/                     # 部署配置
│   ├── docker/
│   ├── nginx/
│   └── 1panel/
├── docs/                       # 文档
└── sql/                        # 数据库脚本
```

## 开发规范

1. **后端**: 遵循 PEP8 规范，使用类型注解
2. **前端**: 遵循 Vue3 Composition API 风格
3. **Git**: 使用 Conventional Commits 规范
4. **注释**: 所有函数/类必须添加文档字符串

## License

MIT License
