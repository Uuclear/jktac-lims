"""
委托收样模块路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, CommissionViewSet, SampleReceiveViewSet

router = DefaultRouter()
router.register('clients', ClientViewSet, basename='client')
router.register('commissions', CommissionViewSet, basename='commission')
router.register('receives', SampleReceiveViewSet, basename='sample-receive')

urlpatterns = [
    path('', include(router.urls)),
]
