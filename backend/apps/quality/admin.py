from django.contrib import admin
from .models import QualityDocument, DocumentCategory, DocumentVersion

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent', 'sort_order']

@admin.register(QualityDocument)
class QualityDocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'doc_type', 'version', 'status', 'created_at']
    list_filter = ['doc_type', 'status']
    search_fields = ['name', 'code']

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version', 'created_at']
