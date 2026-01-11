"""
JKTAC LIMS URL配置

所有API路由按模块划分，统一使用 /api/v1/ 前缀
每个模块的详细路由在各自的 urls.py 中定义
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

# API版本前缀
API_V1_PREFIX = 'api/v1/'

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),
    
    # ==================== API路由 ====================
    
    # 用户认证与权限管理
    path(f'{API_V1_PREFIX}users/', include('apps.users.urls')),
    
    # 委托收样管理
    path(f'{API_V1_PREFIX}samples/', include('apps.samples.urls')),
    
    # 样品流转管理
    path(f'{API_V1_PREFIX}workflow/', include('apps.workflow.urls')),
    
    # 原始记录管理
    path(f'{API_V1_PREFIX}records/', include('apps.records.urls')),
    
    # OCR识别模块
    path(f'{API_V1_PREFIX}ocr/', include('apps.ocr.urls')),
    
    # 质量体系管理
    path(f'{API_V1_PREFIX}quality/', include('apps.quality.urls')),
    
    # 能力管理
    path(f'{API_V1_PREFIX}capability/', include('apps.capability.urls')),
    
    # 设备管理
    path(f'{API_V1_PREFIX}equipment/', include('apps.equipment.urls')),
    
    # 平面图管理
    path(f'{API_V1_PREFIX}floorplan/', include('apps.floorplan.urls')),
    
    # 数据汇总报表
    path(f'{API_V1_PREFIX}reports/', include('apps.reports.urls')),
    
    # AI校验
    path(f'{API_V1_PREFIX}ai-verify/', include('apps.ai_verify.urls')),
    
    # 云查询
    path(f'{API_V1_PREFIX}cloud/', include('apps.cloud_query.urls')),
    
    # JWT Token刷新
    path(f'{API_V1_PREFIX}token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# 开发环境下提供媒体文件访问
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
