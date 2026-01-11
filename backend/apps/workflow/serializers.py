"""
样品流转模块序列化器
"""

from rest_framework import serializers
from .models import SampleWorkflow, WorkflowLog, TestTask


class WorkflowLogSerializer(serializers.ModelSerializer):
    """流转日志序列化器"""
    from_status_display = serializers.CharField(source='get_from_status_display', read_only=True)
    to_status_display = serializers.CharField(source='get_to_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = WorkflowLog
        fields = [
            'id', 'workflow', 'from_status', 'from_status_display',
            'to_status', 'to_status_display', 'operator', 'operator_name',
            'action', 'action_display', 'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SampleWorkflowListSerializer(serializers.ModelSerializer):
    """样品流转列表序列化器"""
    receive_code = serializers.CharField(source='sample_receive.receive_code', read_only=True)
    sample_name = serializers.CharField(source='sample_receive.commission.sample_name', read_only=True)
    commission_code = serializers.CharField(source='sample_receive.commission.code', read_only=True)
    status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    
    class Meta:
        model = SampleWorkflow
        fields = [
            'id', 'sample_receive', 'receive_code', 'sample_name',
            'commission_code', 'current_status', 'status_display',
            'assigned_to', 'assigned_to_name', 'priority', 'priority_display',
            'expected_complete_date', 'created_at'
        ]


class SampleWorkflowDetailSerializer(serializers.ModelSerializer):
    """样品流转详情序列化器"""
    receive_code = serializers.CharField(source='sample_receive.receive_code', read_only=True)
    sample_name = serializers.CharField(source='sample_receive.commission.sample_name', read_only=True)
    commission_code = serializers.CharField(source='sample_receive.commission.code', read_only=True)
    client_name = serializers.CharField(source='sample_receive.commission.client.name', read_only=True)
    status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    logs = WorkflowLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = SampleWorkflow
        fields = [
            'id', 'sample_receive', 'receive_code', 'sample_name',
            'commission_code', 'client_name', 'current_status', 'status_display',
            'assigned_to', 'assigned_to_name', 'priority', 'priority_display',
            'expected_complete_date', 'actual_complete_date', 'notes',
            'logs', 'created_at', 'updated_at'
        ]


class WorkflowTransitionSerializer(serializers.Serializer):
    """流转状态变更序列化器"""
    to_status = serializers.CharField(required=True, help_text='目标状态')
    remarks = serializers.CharField(required=False, allow_blank=True, help_text='备注')


class WorkflowAssignSerializer(serializers.Serializer):
    """任务分配序列化器"""
    assigned_to = serializers.IntegerField(required=True, help_text='负责人用户ID')
    priority = serializers.IntegerField(required=False, default=1, help_text='优先级')
    expected_complete_date = serializers.DateField(required=False, help_text='预计完成日期')
    remarks = serializers.CharField(required=False, allow_blank=True, help_text='备注')


class TestTaskSerializer(serializers.ModelSerializer):
    """试验任务序列化器"""
    receive_code = serializers.CharField(source='workflow.sample_receive.receive_code', read_only=True)
    sample_name = serializers.CharField(source='workflow.sample_receive.commission.sample_name', read_only=True)
    tester_name = serializers.CharField(source='tester.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TestTask
        fields = [
            'id', 'workflow', 'receive_code', 'sample_name',
            'tester', 'tester_name', 'test_items', 'status', 'status_display',
            'start_time', 'end_time', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TestTaskCreateSerializer(serializers.ModelSerializer):
    """试验任务创建序列化器"""
    class Meta:
        model = TestTask
        fields = ['workflow', 'tester', 'test_items', 'notes']
