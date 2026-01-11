from django.contrib import admin
from .models import RecordTemplate, OriginalRecord, RecordAttachment


@admin.register(RecordTemplate)
class RecordTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'version', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'code']


@admin.register(OriginalRecord)
class OriginalRecordAdmin(admin.ModelAdmin):
    list_display = ['record_code', 'template', 'tester', 'test_date', 'status']
    list_filter = ['status', 'test_date', 'template']
    search_fields = ['record_code']


@admin.register(RecordAttachment)
class RecordAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'record', 'file_type', 'file_size']
