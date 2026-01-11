"""
OCR模块序列化器
"""

from rest_framework import serializers
from .models import ScanFile, OCRResult, Report


class ScanFileSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ScanFile
        fields = [
            'id', 'file_name', 'file_path', 'file_type', 'file_size',
            'workflow', 'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OCRResultSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(source='scan_file.file_name', read_only=True)
    
    class Meta:
        model = OCRResult
        fields = [
            'id', 'scan_file', 'file_name', 'raw_text', 'structured_data',
            'confidence', 'details', 'process_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ReportListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    editor_name = serializers.CharField(source='editor.username', read_only=True)
    sample_name = serializers.CharField(source='workflow.sample_receive.commission.sample_name', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'report_code', 'workflow', 'title', 'sample_name',
            'status', 'status_display', 'editor', 'editor_name',
            'issue_date', 'created_at'
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    editor_name = serializers.CharField(source='editor.username', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    approver_name = serializers.CharField(source='approver.username', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'report_code', 'workflow', 'title', 'content', 'conclusion',
            'file_path', 'status', 'status_display',
            'editor', 'editor_name', 'reviewer', 'reviewer_name',
            'approver', 'approver_name', 'review_date', 'approve_date',
            'issue_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'report_code', 'created_at', 'updated_at']
