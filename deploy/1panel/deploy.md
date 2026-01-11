# JKTAC LIMS 1Panel 部署指南

## 一、环境准备

### 1.1 服务器要求
- 操作系统：CentOS 7+/Ubuntu 20.04+
- 内存：建议 4GB 以上
- 硬盘：建议 50GB 以上
- 已安装 1Panel

### 1.2 在 1Panel 中安装基础服务

1. **MariaDB**
   - 进入 1Panel → 应用商店 → 数据库
   - 安装 MariaDB 10.6+
   - 创建数据库：`jktac_lims`
   - 创建用户：`lims_user`，并授权

2. **Redis**
   - 进入 1Panel → 应用商店 → 缓存
   - 安装 Redis 7.0+

3. **MinIO**（可选）
   - 进入 1Panel → 应用商店 → 存储
   - 安装 MinIO
   - 创建存储桶：`lims-files`

## 二、后端部署

### 2.1 上传代码

```bash
# 上传 backend 目录到服务器
scp -r backend/ root@your-server:/opt/jktac_lims/
```

### 2.2 创建 Python 环境

```bash
cd /opt/jktac_lims/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 2.3 配置环境变量

```bash
# 复制配置文件
cp env.example .env

# 编辑配置
vi .env
```

主要配置项：
```
DEBUG=False
SECRET_KEY=your-secret-key-here
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=jktac_lims
DB_USER=lims_user
DB_PASSWORD=your-password
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### 2.4 数据库迁移

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 2.5 配置 Gunicorn 服务

创建 systemd 服务文件：

```bash
sudo vi /etc/systemd/system/lims-backend.service
```

内容：
```ini
[Unit]
Description=JKTAC LIMS Backend
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/opt/jktac_lims/backend
Environment="PATH=/opt/jktac_lims/backend/venv/bin"
ExecStart=/opt/jktac_lims/backend/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start lims-backend
sudo systemctl enable lims-backend
```

## 三、前端部署

### 3.1 构建前端

```bash
cd frontend
npm install
npm run build
```

### 3.2 上传到服务器

```bash
scp -r dist/ root@your-server:/opt/jktac_lims/frontend/
```

### 3.3 配置 Nginx

在 1Panel 中：
1. 进入 网站 → 创建网站
2. 选择 静态网站
3. 目录指向：`/opt/jktac_lims/frontend/dist`
4. 配置反向代理：

```nginx
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

location /admin {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 四、Docker 部署（推荐）

### 4.1 使用 Docker Compose

```bash
cd deploy/docker
docker-compose up -d
```

### 4.2 在 1Panel 中管理

1. 进入 1Panel → 容器 → 编排
2. 导入 docker-compose.yml
3. 启动服务

## 五、验证部署

1. 访问前端：`http://your-server`
2. 访问后端API：`http://your-server/api/v1/`
3. 访问Django Admin：`http://your-server/admin/`

## 六、常见问题

### 6.1 静态文件 404
```bash
python manage.py collectstatic --noinput
```

### 6.2 数据库连接失败
检查 .env 中的数据库配置，确保：
- 数据库服务已启动
- 用户名密码正确
- 用户有访问权限

### 6.3 跨域问题
确保 settings.py 中 CORS_ALLOWED_ORIGINS 包含前端域名

## 七、备份策略

### 7.1 数据库备份
```bash
mysqldump -u lims_user -p jktac_lims > backup_$(date +%Y%m%d).sql
```

### 7.2 文件备份
```bash
tar -czvf media_backup_$(date +%Y%m%d).tar.gz /opt/jktac_lims/backend/media
```

建议使用 1Panel 的备份功能进行定期自动备份。
