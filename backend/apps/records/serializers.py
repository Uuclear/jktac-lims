"""
原始记录模块序列化器
"""

from rest_framework import serializers
from .models import RecordTemplate, OriginalRecord, RecordAttachment


class RecordTemplateSerializer(serializers.ModelSerializer):
    """原始记录模板序列化器"""
    class Meta:
        model = RecordTemplate
        fields = [
            'id', 'name', 'code', 'category', 'description',
            'fields', 'header_info', 'footer_info', 'version',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class RecordAttachmentSerializer(serializers.ModelSerializer):
    """记录附件序列化器"""
    class Meta:
        model = RecordAttachment
        fields = [
            'id', 'record', 'file_name', 'file_path',
            'file_type', 'file_size', 'description', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OriginalRecordListSerializer(serializers.ModelSerializer):
    """原始记录列表序列化器"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    tester_name = serializers.CharField(source='tester.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sample_name = serializers.CharField(source='workflow.sample_receive.commission.sample_name', read_only=True)
    
    class Meta:
        model = OriginalRecord
        fields = [
            'id', 'record_code', 'template', 'template_name',
            'workflow', 'sample_name', 'tester', 'tester_name',
            'test_date', 'status', 'status_display', 'created_at'
        ]


class OriginalRecordDetailSerializer(serializers.ModelSerializer):
    """原始记录详情序列化器"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_fields = serializers.JSONField(source='template.fields', read_only=True)
    tester_name = serializers.CharField(source='tester.username', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    sample_info = serializers.SerializerMethodField()
    attachments = RecordAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = OriginalRecord
        fields = [
            'id', 'record_code', 'template', 'template_name', 'template_fields',
            'workflow', 'sample_info', 'data', 'tester', 'tester_name',
            'test_date', 'test_location', 'equipment_info', 'environment_info',
            'status', 'status_display', 'reviewer', 'reviewer_name', 'review_date',
            'remarks', 'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'record_code', 'created_at', 'updated_at']
    
    def get_sample_info(self, obj):
        commission = obj.workflow.sample_receive.commission
        return {
            'commission_code': commission.code,
            'sample_name': commission.sample_name,
            'client_name': commission.client.name
        }


class OriginalRecordCreateSerializer(serializers.ModelSerializer):
    """原始记录创建序列化器"""
    class Meta:
        model = OriginalRecord
        fields = [
            'template', 'workflow', 'data', 'test_date',
            'test_location', 'equipment_info', 'environment_info', 'remarks'
        ]
