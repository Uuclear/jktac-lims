"""AI校验序列化器"""
from rest_framework import serializers
from .models import VerifyRecord, VerifyRule


class VerifyRecordSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_verify_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    operator_name = serializers.CharField(source='operator.username', read_only=True)
    
    class Meta:
        model = VerifyRecord
        fields = [
            'id', 'document_type', 'document_id', 'content',
            'verify_type', 'type_display', 'status', 'status_display',
            'issues', 'summary', 'model_used', 'process_time',
            'operator', 'operator_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class VerifyRequestSerializer(serializers.Serializer):
    """校验请求序列化器"""
    content = serializers.CharField(required=True, help_text='要校验的内容')
    verify_type = serializers.ChoiceField(
        choices=['typo', 'data', 'format', 'comprehensive'],
        default='comprehensive'
    )
    document_type = serializers.CharField(required=False, default='')
    document_id = serializers.IntegerField(required=False)


class VerifyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifyRule
        fields = [
            'id', 'name', 'rule_type', 'rule_content',
            'description', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
