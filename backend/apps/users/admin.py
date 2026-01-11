"""
用户模块Django Admin配置
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, UserLoginLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """用户管理后台"""
    list_display = ['username', 'email', 'phone', 'role', 'department', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'department']
    search_fields = ['username', 'email', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {
            'fields': ('role', 'phone', 'department', 'avatar', 'employee_id', 'position')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('扩展信息', {
            'fields': ('role', 'phone', 'department')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """部门管理后台"""
    list_display = ['name', 'code', 'parent', 'sort_order', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'code']
    ordering = ['sort_order', 'name']


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    """登录日志管理后台"""
    list_display = ['user', 'ip_address', 'status', 'login_time']
    list_filter = ['status', 'login_time']
    search_fields = ['user__username', 'ip_address']
    ordering = ['-login_time']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'login_time', 'status', 'failure_reason']
