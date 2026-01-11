"""
委托收样模块应用配置
"""
from django.apps import AppConfig


class SamplesConfig(AppConfig):
    """委托收样模块配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.samples'
    verbose_name = '委托收样管理'
