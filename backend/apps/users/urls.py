"""
用户模块路由配置

所有用户相关的API路由
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, DepartmentViewSet, UserLoginLogViewSet

# 创建路由器
router = DefaultRouter()
router.register('', UserViewSet, basename='user')
router.register('departments', DepartmentViewSet, basename='department')
router.register('login-logs', UserLoginLogViewSet, basename='login-log')

urlpatterns = [
    # 认证相关接口（不需要登录）
    path('auth/login/', AuthViewSet.as_view({'post': 'login'}), name='auth-login'),
    path('auth/logout/', AuthViewSet.as_view({'post': 'logout'}), name='auth-logout'),
    path('auth/register/', AuthViewSet.as_view({'post': 'register'}), name='auth-register'),
    
    # 其他用户管理接口
    path('', include(router.urls)),
]
