from django.contrib import admin
from .models import ScanFile, OCRResult, Report


@admin.register(ScanFile)
class ScanFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'status', 'created_at']
    list_filter = ['status', 'file_type']


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ['scan_file', 'confidence', 'process_time', 'created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_code', 'title', 'status', 'editor', 'issue_date']
    list_filter = ['status', 'issue_date']
    search_fields = ['report_code', 'title']
