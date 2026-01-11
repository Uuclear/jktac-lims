"""试验室能力管理序列化器"""
from rest_framework import serializers
from .models import TestStandard, TestParameter, ParameterPrice


class TestStandardSerializer(serializers.ModelSerializer):
    parameter_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TestStandard
        fields = [
            'id', 'code', 'name', 'category', 'version', 'effective_date',
            'is_active', 'file_path', 'description', 'parameter_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_parameter_count(self, obj):
        return obj.parameters.filter(is_active=True).count()


class TestParameterSerializer(serializers.ModelSerializer):
    standard_code = serializers.CharField(source='standard.code', read_only=True)
    standard_name = serializers.CharField(source='standard.name', read_only=True)
    current_price = serializers.SerializerMethodField()
    
    class Meta:
        model = TestParameter
        fields = [
            'id', 'name', 'code', 'standard', 'standard_code', 'standard_name',
            'unit', 'method', 'detection_limit', 'uncertainty',
            'is_active', 'remarks', 'current_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_current_price(self, obj):
        from django.utils import timezone
        price = obj.prices.filter(
            effective_date__lte=timezone.now().date(),
            price_type='normal'
        ).order_by('-effective_date').first()
        return float(price.price) if price else None


class ParameterPriceSerializer(serializers.ModelSerializer):
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)
    type_display = serializers.CharField(source='get_price_type_display', read_only=True)
    
    class Meta:
        model = ParameterPrice
        fields = [
            'id', 'parameter', 'parameter_name', 'price', 'price_type',
            'type_display', 'effective_date', 'expiry_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
