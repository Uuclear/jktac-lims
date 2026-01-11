"""
原始记录模块路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecordTemplateViewSet, OriginalRecordViewSet, RecordAttachmentViewSet

router = DefaultRouter()
router.register('templates', RecordTemplateViewSet, basename='record-template')
router.register('attachments', RecordAttachmentViewSet, basename='record-attachment')
router.register('', OriginalRecordViewSet, basename='original-record')

urlpatterns = [
    path('', include(router.urls)),
]
