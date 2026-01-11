from django.contrib import admin
from .models import Laboratory, Equipment, CalibrationRecord, EquipmentUsageLog

@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'name', 'responsible_person', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'room_number']

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'model', 'laboratory', 'status']
    list_filter = ['status', 'laboratory']
    search_fields = ['code', 'name']

@admin.register(CalibrationRecord)
class CalibrationRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'calibration_date', 'valid_until', 'result']
    list_filter = ['result', 'calibration_date']

@admin.register(EquipmentUsageLog)
class EquipmentUsageLogAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'user', 'start_time', 'end_time']
    list_filter = ['equipment', 'user']
