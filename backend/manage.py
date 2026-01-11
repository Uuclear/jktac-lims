#!/usr/bin/env python
"""
Django命令行工具入口

用法:
    python manage.py runserver     - 启动开发服务器
    python manage.py migrate       - 执行数据库迁移
    python manage.py createsuperuser - 创建超级用户
    python manage.py shell         - 进入Django shell
"""
import os
import sys


def main():
    """Django管理命令入口函数"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "无法导入Django。请确认已安装Django并已激活虚拟环境。"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
