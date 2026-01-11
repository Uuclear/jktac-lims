"""
Django项目配置文件

本配置文件包含JKTAC LIMS系统的所有核心配置项，支持通过环境变量进行配置分离。
配置分为以下几个部分：
1. 基础配置 - DEBUG、SECRET_KEY等
2. 数据库配置 - MariaDB连接配置
3. 缓存配置 - Redis缓存配置
4. 认证配置 - JWT认证配置
5. 存储配置 - MinIO对象存储配置
6. 第三方服务配置 - OCR、AI等服务配置
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==================== 基础配置 ====================

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全密钥（生产环境必须修改）
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# 调试模式
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# 云服务器模式（用于云查询子系统）
CLOUD_MODE = os.getenv('CLOUD_MODE', 'False').lower() == 'true'

# ==================== 应用配置 ====================

# Django内置应用
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# 第三方应用
THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
]

# 本地应用（12大模块）
LOCAL_APPS = [
    'apps.users',           # 用户权限管理
    'apps.samples',         # 委托收样管理
    'apps.workflow',        # 样品流转管理
    'apps.records',         # 原始记录管理
    'apps.ocr',             # OCR识别模块
    'apps.quality',         # 质量体系管理
    'apps.capability',      # 能力管理
    'apps.equipment',       # 设备管理
    'apps.floorplan',       # 平面图管理
    'apps.reports',         # 数据汇总
    'apps.ai_verify',       # AI校验
    'apps.cloud_query',     # 云查询
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ==================== 中间件配置 ====================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS必须在最前面
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ==================== 模板配置 ====================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==================== 数据库配置 ====================

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DB_NAME', 'jktac_lims'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ==================== 缓存配置 ====================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://:{os.getenv('REDIS_PASSWORD', '')}@{os.getenv('REDIS_HOST', '127.0.0.1')}:{os.getenv('REDIS_PORT', '6379')}/{os.getenv('REDIS_DB', '0')}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session使用Redis存储
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ==================== 密码验证配置 ====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# ==================== 国际化配置 ====================

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# ==================== 静态文件配置 ====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ==================== DRF配置 ====================

REST_FRAMEWORK = {
    # 认证方式
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # 权限控制
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # 分页配置
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    # 过滤配置
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    # 异常处理
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
    # 响应渲染
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    # 日期时间格式
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}

# ==================== JWT配置 ====================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME', '1440'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.getenv('JWT_SECRET_KEY', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# ==================== CORS配置 ====================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
]

CORS_ALLOW_CREDENTIALS = True

# ==================== MinIO配置 ====================

MINIO_CONFIG = {
    'ENDPOINT': os.getenv('MINIO_ENDPOINT', '127.0.0.1:9000'),
    'ACCESS_KEY': os.getenv('MINIO_ACCESS_KEY', 'minioadmin'),
    'SECRET_KEY': os.getenv('MINIO_SECRET_KEY', 'minioadmin'),
    'BUCKET_NAME': os.getenv('MINIO_BUCKET_NAME', 'lims-files'),
    'SECURE': os.getenv('MINIO_SECURE', 'False').lower() == 'true',
}

# ==================== OCR配置 ====================

OCR_CONFIG = {
    'ENABLED': os.getenv('OCR_ENABLED', 'False').lower() == 'true',
    'API_URL': os.getenv('OCR_API_URL', 'http://127.0.0.1:8866'),
}

# ==================== AI大模型配置 ====================

AI_CONFIG = {
    'ENABLED': os.getenv('AI_ENABLED', 'False').lower() == 'true',
    'API_URL': os.getenv('AI_API_URL', 'http://127.0.0.1:11434'),
    'MODEL_NAME': os.getenv('AI_MODEL_NAME', 'qwen2:7b'),
    'API_KEY': os.getenv('AI_API_KEY', ''),
}

# ==================== 云服务配置 ====================

CLOUD_CONFIG = {
    'API_SECRET': os.getenv('CLOUD_API_SECRET', ''),
}

# ==================== 日志配置 ====================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/lims.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / LOG_FILE,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# ==================== 默认主键类型 ====================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
