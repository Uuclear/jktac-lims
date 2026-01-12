## 部署与运维指南

1Panel部署配置
环境准备
# 1Panel安装（CentOS/Ubuntu）
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh && bash quick_start.sh

# 基础环境配置
- MariaDB 11.4：1Panel应用商店一键安装
- Redis 7.2：1Panel应用商店一键安装  
- Docker：1Panel内置容器管理
- Nginx：1Panel内置Web服务器
容器化部署配置
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=mariadb
      - REDIS_HOST=redis
    depends_on:
      - mariadb
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  mariadb:
    image: mariadb:11.4
    environment:
      MYSQL_ROOT_PASSWORD: your_password
      MYSQL_DATABASE: lims_db
    volumes:
      - mariadb_data:/var/lib/mysql
  
  redis:
    image: redis:7.2-alpine
    volumes:
      - redis_data:/data

volumes:
  mariadb_data:
  redis_data:
运维监控策略
1. 系统监控
性能监控：CPU、内存、磁盘使用率
服务监控：Django、Vue、MariaDB、Redis服务状态
日志监控：应用日志、错误日志、访问日志
2. 数据备份
# 1Panel自动备份配置
- 数据库备份：每日凌晨2点自动备份
- 文件备份：每周备份上传文件和报告
- 配置备份：每月备份系统配置
3. 安全策略
访问控制：IP白名单、VPN访问
数据加密：HTTPS传输、数据库字段加密
权限审计：操作日志、权限变更记录
总结：本文档提供了工地试验室LIMS系统的完整技术架构设计，包含最新版本的兼容性分析、详细的实施指南和专用的Cursor Agents提示词。技术栈选择经过充分验证，具备高度可行性和长期维护性，能够满足试验室信息化管理的全部需求。

建议：建议按照本文档的架构设计和提示词，使用Cursor Agents生成系统框架，然后基于框架逐步完善各模块的业务逻辑，确保系统的稳定性和可扩展性。 ## 部署与运维指南

1Panel部署配置详解
1.1 环境准备与系统要求
硬件配置要求
最小配置（开发/测试环境）：
- CPU：4核心 2.0GHz
- 内存：8GB RAM
- 存储：100GB SSD
- 网络：100Mbps带宽

推荐配置（生产环境）：
- CPU：8核心 2.4GHz
- 内存：16GB RAM
- 存储：500GB SSD + 2TB HDD（数据存储）
- 网络：1Gbps带宽

高性能配置（大型试验室）：
- CPU：16核心 3.0GHz
- 内存：32GB RAM
- 存储：1TB NVMe SSD + 5TB HDD
- 网络：10Gbps带宽
操作系统安装
# 支持的操作系统
- CentOS 7.6+ / CentOS Stream 8+
- Ubuntu 18.04+ / Ubuntu 20.04 LTS / Ubuntu 22.04 LTS
- Debian 10+ / Debian 11+
- Rocky Linux 8+
- AlmaLinux 8+

# 1Panel安装（推荐使用官方脚本）
curl -sSL https://resource.fit2cloud.com/1panel/package/quick_start.sh -o quick_start.sh
sudo bash quick_start.sh

# 手动安装（如果自动安装失败）
wget https://github.com/1Panel-dev/1Panel/releases/download/v1.8.3/1panel-v1.8.3-linux-amd64.tar.gz
tar -zxvf 1panel-v1.8.3-linux-amd64.tar.gz
cd 1panel-v1.8.3-linux-amd64
sudo ./1pctl install

# 验证安装
sudo 1pctl status
基础环境配置
# 系统优化配置
# 1. 调整系统参数
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 2. 优化内核参数
cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
vm.swappiness = 10
EOF

sysctl -p

# 3. 配置防火墙
# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=10086/tcp  # 1Panel管理端口
sudo firewall-cmd --permanent --add-port=80/tcp     # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp    # HTTPS
sudo firewall-cmd --permanent --add-port=3306/tcp   # MariaDB
sudo firewall-cmd --permanent --add-port=6379/tcp   # Redis
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 10086/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3306/tcp
sudo ufw allow 6379/tcp
sudo ufw enable
1.2 数据库服务部署
MariaDB 11.4 安装配置
# 通过1Panel应用商店安装MariaDB
# 1. 登录1Panel管理界面 (http://your-server-ip:10086)
# 2. 进入"应用商店" -> "数据库" -> "MariaDB"
# 3. 选择版本11.4，配置参数

# MariaDB配置优化
# 编辑 /opt/1panel/apps/mariadb/mariadb/conf/my.cnf
[mysqld]
# 基础配置
port = 3306
socket = /var/run/mysqld/mysqld.sock
datadir = /var/lib/mysql
pid-file = /var/run/mysqld/mysqld.pid

# 字符集配置
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
init_connect = 'SET NAMES utf8mb4'

# 性能优化配置
# 内存配置（根据服务器内存调整）
innodb_buffer_pool_size = 4G          # 设置为物理内存的60-70%
innodb_log_file_size = 256M
innodb_log_buffer_size = 64M
innodb_flush_log_at_trx_commit = 2

# 连接配置
max_connections = 500
max_connect_errors = 1000
wait_timeout = 28800
interactive_timeout = 28800

# 查询缓存
query_cache_type = 1
query_cache_size = 256M
query_cache_limit = 2M

# 临时表配置
tmp_table_size = 256M
max_heap_table_size = 256M

# 慢查询日志
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# 二进制日志（用于主从复制）
log-bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7

# InnoDB配置
innodb_file_per_table = 1
innodb_flush_method = O_DIRECT
innodb_lock_wait_timeout = 120
innodb_io_capacity = 2000

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
Redis 7.2 安装配置
# 通过1Panel应用商店安装Redis
# 配置文件路径：/opt/1panel/apps/redis/redis/conf/redis.conf

# Redis配置优化
# 基础配置
bind 127.0.0.1 0.0.0.0
port 6379
timeout 300
tcp-keepalive 300

# 内存配置
maxmemory 2gb                    # 根据服务器内存调整
maxmemory-policy allkeys-lru     # 内存不足时的淘汰策略

# 持久化配置
save 900 1                       # 900秒内至少1个key变化时保存
save 300 10                      # 300秒内至少10个key变化时保存
save 60 10000                    # 60秒内至少10000个key变化时保存

# AOF配置
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# 安全配置
requirepass your_redis_password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG "CONFIG_9f2e8a1b3c4d5e6f"

# 日志配置
loglevel notice
logfile /var/log/redis/redis-server.log

# 客户端连接配置
maxclients 10000
1.3 应用容器部署
Docker环境配置
# Docker已通过1Panel自动安装，进行优化配置

# 1. 配置Docker镜像加速器
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker

# 2. 验证Docker安装
docker --version
docker-compose --version
应用容器编排配置
# docker-compose.yml（完整生产版本）
version: '3.8'

services:
  # 后端服务
  lims-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: lims-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=core.settings.production
      - DATABASE_URL=mysql://lims_user:${DB_PASSWORD}@mariadb:3306/lims_db
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - DEBUG=False
    volumes:
      - ./backend/media:/app/media
      - ./backend/static:/app/static
      - ./backend/logs:/app/logs
      - ./backend/uploads:/app/uploads
    depends_on:
      - mariadb
      - redis
    networks:
      - lims-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # 前端服务
  lims-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    container_name: lims-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    environment:
      - NODE_ENV=production
      - VUE_APP_API_BASE_URL=http://lims-backend:8000/api
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./frontend/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - lims-backend
    networks:
      - lims-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 移动端服务
  lims-mobile:
    build:
      context: ./mobile
      dockerfile: Dockerfile
    container_name: lims-mobile
    restart: unless-stopped
    ports:
      - "3001:80"
    environment:
      - NODE_ENV=production
      - VUE_APP_API_BASE_URL=http://lims-backend:8000/api
    depends_on:
      - lims-backend
    networks:
      - lims-network

  # Celery异步任务处理
  lims-celery:
    build:
环境变量配置
# .env文件（生产环境）
# 数据库配置
DB_PASSWORD=your_secure_db_password
REDIS_PASSWORD=your_secure_redis_password

# Django配置
SECRET_KEY=your_very_long_and_random_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost,127.0.0.1
DEBUG=False

# MinIO配置
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_minio_password

# InfluxDB配置
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=your_secure_influxdb_password
INFLUXDB_ORG=lims-org
INFLUXDB_BUCKET=environment-data
INFLUXDB_TOKEN=your_influxdb_admin_token

# RabbitMQ配置
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your_secure_rabbitmq_password

# SSL证书配置
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/private.key

# 邮件配置
EMAIL_HOST=smtp.your-domain.com
EMAIL_PORT=587
EMAIL_HOST_USER=noreply@your-domain.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True

# 短信配置
SMS_API_KEY=your_sms_api_key
SMS_API_SECRET=your_sms_api_secret

# AI服务配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
1.4 Nginx配置优化
主配置文件
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    '$request_time $upstream_response_time';

    access_log /var/log/nginx/access.log main;

    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # 文件上传配置
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    client_header_buffer_size 32k;
    large_client_header_buffers 4 32k;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 缓存配置
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g 
                     inactive=60m use_temp_path=off;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
站点配置文件
# nginx/conf.d/lims.conf
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS主站点
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # 现代SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # 前端静态文件
    location / {
        proxy_pass http://lims-frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API接口
    location /api/ {
        # 限流
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://lims-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # 缓存API响应
        proxy_cache my_cache;
        proxy_cache_valid 200 302 10m;
        proxy_cache_valid 404 1m;
        proxy_cache_bypass $http_pragma;
        proxy_cache_revalidate on;
        proxy_cache_min_uses 1;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    }

    # 登录接口特殊限流
    location /api/auth/login/ {
        limit_req zone=login burst=5 nodelay;
        
        proxy_pass http://lims-backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 文件上传接口
    location /api/upload/ {
        client_max_body_size 500M;
        proxy_pass http://lims-backend:8000;
        proxy_set_header Host $host;
运维监控策略
1. 系统监控配置
Prometheus + Grafana监控
# monitoring/docker-compose.yml
version: '3.8'

services:
  # Prometheus监控
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: lims-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - monitoring

  # Grafana可视化
  grafana:
    image: grafana/grafana:10.0.0
    container_name: lims-grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring

  # Node Exporter系统监控
  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: lims-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

  # cAdvisor容器监控
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.0
    container_name: lims-cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
Prometheus配置
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus自身监控
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # 系统监控
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # 容器监控
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # Django应用监控
  - job_name: 'lims-backend'
    static_configs:
      - targets: ['lims-backend:8000']
告警规则配置
# prometheus/rules/lims-alerts.yml
groups:
  - name: lims-system-alerts
    rules:
      # 系统资源告警
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"
2. 日志管理配置
ELK Stack部署
# logging/docker-compose.yml
version: '3.8'

services:
  # Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: lims-elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - logging

  # Logstash
  logstash:
    image: docker.elastic.co/logstash/logstash:8.8.0
    container_name: lims-logstash
    restart: unless-stopped
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
3. 备份策略配置
自动备份脚本
#!/bin/bash
# backup.sh - LIMS系统自动备份脚本

# 配置变量
BACKUP_DIR="/opt/lims-backup"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 数据库备份配置
DB_HOST="localhost"
DB_PORT="3306"
DB_NAME="lims_db"
DB_USER="backup_user"
DB_PASSWORD="backup_password"

# 创建备份目录
mkdir -p ${BACKUP_DIR}/{database,files,config}

# 1. 数据库备份
echo "开始数据库备份..."
mysqldump -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASSWORD} \
    --single-transaction \
    --routines \
    --triggers \
    --events \
    --hex-blob \
    --opt \
    ${DB_NAME} | gzip > ${BACKUP_DIR}/database/lims_db_${DATE}.sql.gz

if [ $? -eq 0 ]; then
    echo "数据库备份完成: lims_db_${DATE}.sql.gz"
else
    echo "数据库备份失败!"
    exit 1
fi

# 2. 文件备份
echo "开始文件备份..."
tar -czf ${BACKUP_DIR}/files/lims_files_${DATE}.tar.gz \
    /opt/1panel/apps/lims/media \
    /opt/1panel/apps/lims/uploads \
    /opt/1panel/apps/lims/static

if [ $? -eq 0 ]; then
    echo "文件备份完成: lims_files_${DATE}.tar.gz"
else
    echo "文件备份失败!"
    exit 1
fi

# 3. 配置备份
echo "开始配置备份..."
tar -czf ${BACKUP_DIR}/config/lims_config_${DATE}.tar.gz \
    /opt/1panel/apps/lims/docker-compose.yml \
    /opt/1panel/apps/lims/.env \
    /etc/nginx/conf.d/lims.conf \
    /opt/1panel/apps/mariadb/mariadb/conf/my.cnf \
    /opt/1panel/apps/redis/redis/conf/redis.conf

if [ $? -eq 0 ]; then
    echo "配置备份完成: lims_config_${DATE}.tar.gz"
else
    echo "配置备份失败!"
    exit 1
fi

# 4. 清理过期备份
echo "清理过期备份文件..."
find ${BACKUP_DIR} -name "*.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "备份任务完成: ${DATE}"

# 5. 备份到云存储（可选）
if [ -n "$CLOUD_BACKUP_ENABLED" ]; then
    echo "开始云存储备份..."
    # 这里可以添加云存储备份逻辑
    # 例如：rsync到远程服务器、上传到OSS等
fi

# 6. 发送备份报告
echo "发送备份报告..."
BACKUP_SIZE=$(du -sh ${BACKUP_DIR} | cut -f1)
echo "备份完成报告
时间: ${DATE}
备份大小: ${BACKUP_SIZE}
备份位置: ${BACKUP_DIR}
保留天数: ${RETENTION_DAYS}天" | mail -s "LIMS系统备份报告" admin@your-domain.com
定时任务配置
# 添加到crontab
crontab -e

# 每日凌晨2点执行完整备份
0 2 * * * /opt/scripts/backup.sh >> /var/log/lims-backup.log 2>&1

# 每4小时执行增量备份（仅数据库）
0 */4 * * * /opt/scripts/incremental-backup.sh >> /var/log/lims-backup.log 2>&1

# 每周日凌晨3点执行完整系统备份
0 3 * * 0 /opt/scripts/full-system-backup.sh >> /var/log/lims-backup.log 2>&1

# 每月1号凌晨4点执行备份验证
0 4 1 * * /opt/scripts/backup-verify.sh >> /var/log/lims-backup.log 2>&1
4. 安全策略配置
防火墙配置
#!/bin/bash
# firewall-setup.sh - 防火墙安全配置

# 清空现有规则
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# 设置默认策略
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# 允许本地回环
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 允许已建立的连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH访问（限制IP）
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT

# HTTP/HTTPS访问
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 1Panel管理端口（限制IP）
iptables -A INPUT -p tcp --dport 10086 -s 192.168.1.0/24 -j ACCEPT

# 数据库端口（仅内网）
iptables -A INPUT -p tcp --dport 3306 -s 172.20.0.0/16 -j ACCEPT
iptables -A INPUT -p tcp --dport 6379 -s 172.20.0.0/16 -j ACCEPT

# 监控端口（仅内网）
iptables -A INPUT -p tcp --dport 9090 -s 192.168.1.0/24 -j ACCEPT  # Prometheus
iptables -A INPUT -p tcp --dport 3000 -s 192.168.1.0/24 -j ACCEPT   # Grafana

# 防止DDoS攻击
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# 防止端口扫描
iptables -A INPUT -m recent --name portscan --rcheck --seconds 86400 -j DROP
iptables -A INPUT -m recent --name portscan --remove
iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j LOG --log-prefix "portscan:"
iptables -A INPUT -p tcp -m tcp --dport 139 -m recent --name portscan --set -j DROP

# 保存规则
iptables-save > /etc/iptables/rules.v4

echo "防火墙配置完成"
SSL证书自动更新
#!/bin/bash
# ssl-renew.sh - SSL证书自动更新脚本

DOMAIN="your-domain.com"
EMAIL="admin@your-domain.com"
WEBROOT="/var/www/html"

# 使用Let's Encrypt获取证书
certbot certonly \
    --webroot \
    --webroot-path=${WEBROOT} \
    --email ${EMAIL} \
    --agree-tos \
    --no-eff-email \
    --domains ${DOMAIN},www.${DOMAIN},m.${DOMAIN}

# 复制证书到Nginx目录
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /etc/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /etc/nginx/ssl/private.key

# 重新加载Nginx配置
nginx -t && nginx -s reload

# 添加到crontab，每月自动更新
# 0 3 1 * * /opt/scripts/ssl-renew.sh >> /var/log/ssl-renew.log 2>&1
