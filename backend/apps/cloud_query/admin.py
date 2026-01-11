from django.contrib import admin
from .models import QueryApplication, QueryLog

@admin.register(QueryApplication)
class QueryApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'applicant_role', 'query_type', 'status', 'created_at']
    list_filter = ['status', 'applicant_role']
    search_fields = ['applicant__username', 'organization']

@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ['query_user', 'query_content', 'ip_address', 'created_at']
    list_filter = ['created_at']
