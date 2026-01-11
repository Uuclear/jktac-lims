"""
样品流转模块应用配置
"""
from django.apps import AppConfig


class WorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workflow'
    verbose_name = '样品流转管理'
