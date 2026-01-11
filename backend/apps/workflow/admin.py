"""
样品流转模块Admin配置
"""

from django.contrib import admin
from .models import SampleWorkflow, WorkflowLog, TestTask


@admin.register(SampleWorkflow)
class SampleWorkflowAdmin(admin.ModelAdmin):
    list_display = ['sample_receive', 'current_status', 'assigned_to', 'priority', 'expected_complete_date']
    list_filter = ['current_status', 'priority']
    search_fields = ['sample_receive__receive_code']
    ordering = ['-created_at']


@admin.register(WorkflowLog)
class WorkflowLogAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'from_status', 'to_status', 'operator', 'action', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['workflow__sample_receive__receive_code']
    ordering = ['-created_at']


@admin.register(TestTask)
class TestTaskAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'tester', 'status', 'start_time', 'end_time']
    list_filter = ['status', 'tester']
    ordering = ['-created_at']
