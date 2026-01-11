from django.contrib import admin
from .models import StatisticsReport

@admin.register(StatisticsReport)
class StatisticsReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'start_date', 'end_date', 'created_at']
    list_filter = ['report_type', 'created_at']
