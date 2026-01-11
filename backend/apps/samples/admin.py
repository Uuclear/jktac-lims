"""
委托收样模块Admin配置
"""

from django.contrib import admin
from .models import Client, Commission, SampleReceive


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_person', 'contact_phone', 'credit_level', 'created_at']
    list_filter = ['credit_level', 'created_at']
    search_fields = ['name', 'code', 'contact_person']
    ordering = ['-created_at']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['code', 'client', 'project_name', 'sample_name', 'status', 'commission_date']
    list_filter = ['status', 'commission_date', 'client']
    search_fields = ['code', 'project_name', 'sample_name']
    ordering = ['-commission_date']


@admin.register(SampleReceive)
class SampleReceiveAdmin(admin.ModelAdmin):
    list_display = ['receive_code', 'commission', 'receiver', 'receive_time', 'sample_condition']
    list_filter = ['sample_condition', 'receive_time']
    search_fields = ['receive_code', 'commission__code']
    ordering = ['-receive_time']
