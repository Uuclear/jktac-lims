"""
OCR模块路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScanFileViewSet, OCRResultViewSet, ReportViewSet

router = DefaultRouter()
router.register('scans', ScanFileViewSet, basename='scan-file')
router.register('results', OCRResultViewSet, basename='ocr-result')
router.register('reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
