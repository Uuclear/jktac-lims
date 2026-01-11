from django.contrib import admin
from .models import TestStandard, TestParameter, ParameterPrice

@admin.register(TestStandard)
class TestStandardAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']

@admin.register(TestParameter)
class TestParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'standard', 'unit', 'is_active']
    list_filter = ['standard', 'is_active']
    search_fields = ['name', 'code']

@admin.register(ParameterPrice)
class ParameterPriceAdmin(admin.ModelAdmin):
    list_display = ['parameter', 'price', 'price_type', 'effective_date']
    list_filter = ['price_type', 'effective_date']
