"""
用户模块应用配置
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """用户模块配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = '用户权限管理'
    
    def ready(self):
        """
        应用就绪时执行
        
        可在此注册信号处理器等
        """
        pass
