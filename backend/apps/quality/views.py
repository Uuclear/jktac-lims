"""质量体系管理模块视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from common.services import get_minio_service
from .models import QualityDocument, DocumentCategory, DocumentVersion
from .serializers import QualityDocumentSerializer, DocumentCategorySerializer, DocumentVersionSerializer


class DocumentCategoryViewSet(viewsets.ModelViewSet):
    """文件分类视图集"""
    queryset = DocumentCategory.objects.filter(is_deleted=False)
    serializer_class = DocumentCategorySerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取分类树形结构"""
        root_categories = DocumentCategory.objects.filter(
            parent__isnull=True, is_deleted=False
        ).order_by('sort_order')
        return success_response(DocumentCategorySerializer(root_categories, many=True).data)


class QualityDocumentViewSet(viewsets.ModelViewSet):
    """质量体系文件视图集"""
    queryset = QualityDocument.objects.filter(is_deleted=False)
    serializer_class = QualityDocumentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [MultiPartParser, FormParser]
    filterset_fields = ['doc_type', 'category', 'status']
    search_fields = ['name', 'code']
    ordering_fields = ['created_at', 'name']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
        'upload': ['admin'],
        'download': ['admin', 'tester', 'reviewer', 'approver'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """上传质量体系文件"""
        file = request.FILES.get('file')
        if not file:
            return error_response('请选择要上传的文件')
        
        minio_service = get_minio_service()
        from common.utils import generate_file_path
        file_path = generate_file_path('quality', file.name)
        
        minio_service.upload_bytes(file.read(), file_path, file.content_type)
        
        document = QualityDocument.objects.create(
            name=request.data.get('name', file.name),
            code=request.data.get('code', ''),
            doc_type=request.data.get('doc_type', 'other'),
            file_path=file_path,
            file_size=file.size,
            description=request.data.get('description', ''),
            created_by=request.user
        )
        
        return success_response(QualityDocumentSerializer(document).data, '文件上传成功')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """获取文件下载链接"""
        document = self.get_object()
        
        minio_service = get_minio_service()
        url = minio_service.get_presigned_url(document.file_path)
        
        if url:
            document.download_count += 1
            document.save(update_fields=['download_count'])
            return success_response({'url': url}, '获取下载链接成功')
        return error_response('获取下载链接失败')


class DocumentVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """文件版本视图集（只读）"""
    queryset = DocumentVersion.objects.filter(is_deleted=False)
    serializer_class = DocumentVersionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['document']
