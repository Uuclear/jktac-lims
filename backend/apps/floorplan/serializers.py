"""平面图序列化器"""
from rest_framework import serializers
from .models import FloorPlan, FloorPlanNode


class FloorPlanNodeSerializer(serializers.ModelSerializer):
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    room_number = serializers.CharField(source='laboratory.room_number', read_only=True)
    
    class Meta:
        model = FloorPlanNode
        fields = [
            'id', 'floor_plan', 'laboratory', 'laboratory_name', 'room_number',
            'x', 'y', 'width', 'height', 'label', 'color', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class FloorPlanSerializer(serializers.ModelSerializer):
    nodes = FloorPlanNodeSerializer(many=True, read_only=True)
    
    class Meta:
        model = FloorPlan
        fields = [
            'id', 'name', 'building', 'floor', 'image_path',
            'image_width', 'image_height', 'is_active', 'nodes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
