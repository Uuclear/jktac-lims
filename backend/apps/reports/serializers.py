"""报表序列化器"""
from rest_framework import serializers
from .models import StatisticsReport


class StatisticsReportSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    
    class Meta:
        model = StatisticsReport
        fields = [
            'id', 'name', 'report_type', 'type_display',
            'start_date', 'end_date', 'statistics_data',
            'file_path', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StatisticsQuerySerializer(serializers.Serializer):
    """统计查询参数序列化器"""
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    dimension = serializers.ChoiceField(
        choices=['sample_type', 'client', 'tester', 'status'],
        required=False,
        default='sample_type'
    )
