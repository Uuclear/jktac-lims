from django.contrib import admin
from .models import FloorPlan, FloorPlanNode

@admin.register(FloorPlan)
class FloorPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'floor', 'is_active']

@admin.register(FloorPlanNode)
class FloorPlanNodeAdmin(admin.ModelAdmin):
    list_display = ['floor_plan', 'laboratory', 'label', 'x', 'y']
