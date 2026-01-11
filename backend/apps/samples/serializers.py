"""
委托收样模块序列化器
"""

from rest_framework import serializers
from .models import Client, Commission, SampleReceive


class ClientSerializer(serializers.ModelSerializer):
    """委托方序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'code', 'contact_person', 'contact_phone',
            'email', 'address', 'user', 'user_name', 'credit_level',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_at', 'updated_at']


class CommissionListSerializer(serializers.ModelSerializer):
    """委托单列表序列化器"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'code', 'client', 'client_name', 'project_name',
            'sample_name', 'sample_quantity', 'commission_date',
            'required_date', 'status', 'status_display', 'total_price',
            'created_at'
        ]


class CommissionDetailSerializer(serializers.ModelSerializer):
    """委托单详情序列化器"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'code', 'client', 'client_name', 'project_name',
            'project_location', 'sample_name', 'sample_model',
            'sample_quantity', 'sample_unit', 'sample_source',
            'sample_batch', 'test_basis', 'test_parameters',
            'commission_date', 'required_date', 'status', 'status_display',
            'total_price', 'remarks', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'updated_at']


class CommissionCreateSerializer(serializers.ModelSerializer):
    """委托单创建序列化器"""
    class Meta:
        model = Commission
        fields = [
            'client', 'project_name', 'project_location', 'sample_name',
            'sample_model', 'sample_quantity', 'sample_unit', 'sample_source',
            'sample_batch', 'test_basis', 'test_parameters', 'commission_date',
            'required_date', 'remarks'
        ]


class SampleReceiveSerializer(serializers.ModelSerializer):
    """收样记录序列化器"""
    commission_code = serializers.CharField(source='commission.code', read_only=True)
    sample_name = serializers.CharField(source='commission.sample_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    condition_display = serializers.CharField(source='get_sample_condition_display', read_only=True)
    
    class Meta:
        model = SampleReceive
        fields = [
            'id', 'commission', 'commission_code', 'sample_name',
            'receive_code', 'receiver', 'receiver_name', 'receive_time',
            'actual_quantity', 'sample_condition', 'condition_display',
            'condition_notes', 'storage_location', 'photos',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'receive_code', 'created_at', 'updated_at']


class SampleReceiveCreateSerializer(serializers.ModelSerializer):
    """收样记录创建序列化器"""
    class Meta:
        model = SampleReceive
        fields = [
            'commission', 'receive_time', 'actual_quantity',
            'sample_condition', 'condition_notes', 'storage_location', 'photos'
        ]
