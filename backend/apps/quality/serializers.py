"""质量体系模块序列化器"""
from rest_framework import serializers
from .models import QualityDocument, DocumentCategory, DocumentVersion


class DocumentCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentCategory
        fields = ['id', 'name', 'code', 'parent', 'sort_order', 'children', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_children(self, obj):
        children = obj.children.filter(is_deleted=False)
        return DocumentCategorySerializer(children, many=True).data if children.exists() else []


class QualityDocumentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = QualityDocument
        fields = [
            'id', 'name', 'code', 'doc_type', 'type_display', 'version',
            'category', 'category_name', 'file_path', 'file_size', 'description',
            'status', 'status_display', 'effective_date', 'expiry_date',
            'download_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'download_count', 'created_at', 'updated_at']


class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = ['id', 'document', 'version', 'file_path', 'change_log', 'created_at']
        read_only_fields = ['id', 'created_at']
