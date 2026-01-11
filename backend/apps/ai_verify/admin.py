from django.contrib import admin
from .models import VerifyRecord, VerifyRule

@admin.register(VerifyRecord)
class VerifyRecordAdmin(admin.ModelAdmin):
    list_display = ['document_type', 'verify_type', 'status', 'operator', 'created_at']
    list_filter = ['verify_type', 'status']

@admin.register(VerifyRule)
class VerifyRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active']
    list_filter = ['rule_type', 'is_active']
