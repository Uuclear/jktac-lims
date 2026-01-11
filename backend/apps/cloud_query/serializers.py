"""云查询序列化器"""
from rest_framework import serializers
from .models import QueryApplication, QueryLog


class QueryApplicationSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    role_display = serializers.CharField(source='get_applicant_role_display', read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    
    class Meta:
        model = QueryApplication
        fields = [
            'id', 'applicant', 'applicant_name', 'applicant_role', 'role_display',
            'organization', 'query_type', 'query_scope', 'reason',
            'status', 'status_display', 'valid_from', 'valid_until',
            'reviewer', 'reviewer_name', 'review_time', 'review_remark',
            'created_at'
        ]
        read_only_fields = ['id', 'applicant', 'created_at']


class QueryApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryApplication
        fields = [
            'applicant_role', 'organization', 'query_type',
            'query_scope', 'reason'
        ]


class ApprovalSerializer(serializers.Serializer):
    """审批序列化器"""
    approved = serializers.BooleanField(required=True)
    valid_days = serializers.IntegerField(required=False, default=30)
    remark = serializers.CharField(required=False, allow_blank=True)


class QueryLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='query_user.username', read_only=True)
    
    class Meta:
        model = QueryLog
        fields = [
            'id', 'application', 'query_user', 'user_name',
            'query_content', 'query_params', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
