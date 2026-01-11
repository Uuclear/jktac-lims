"""
样品流转模块路由配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SampleWorkflowViewSet, WorkflowLogViewSet, TestTaskViewSet

router = DefaultRouter()
router.register('', SampleWorkflowViewSet, basename='workflow')
router.register('logs', WorkflowLogViewSet, basename='workflow-log')
router.register('tasks', TestTaskViewSet, basename='test-task')

urlpatterns = [
    path('', include(router.urls)),
]
