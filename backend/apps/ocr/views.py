"""
OCR识别与报告生成模块视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from common.services import get_ocr_service, get_minio_service
from .models import ScanFile, OCRResult, Report
from .serializers import (
    ScanFileSerializer, OCRResultSerializer,
    ReportListSerializer, ReportDetailSerializer
)


class ScanFileViewSet(viewsets.ModelViewSet):
    """
    扫描件管理视图集
    
    接口列表：
    - GET /scans/ - 获取扫描件列表
    - POST /scans/upload/ - 上传扫描件
    - POST /scans/{id}/recognize/ - 触发OCR识别
    """
    queryset = ScanFile.objects.filter(is_deleted=False)
    serializer_class = ScanFileSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    parser_classes = [MultiPartParser, FormParser]
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'upload': ['admin', 'tester'],
        'recognize': ['admin', 'tester'],
    }
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        上传扫描件
        
        支持上传图片和PDF文件
        """
        file = request.FILES.get('file')
        workflow_id = request.data.get('workflow_id')
        
        if not file:
            return error_response('请选择要上传的文件')
        
        # 验证文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/tiff', 'application/pdf']
        if file.content_type not in allowed_types:
            return error_response('不支持的文件类型')
        
        # 上传到MinIO
        minio_service = get_minio_service()
        from common.utils import generate_file_path
        file_path = generate_file_path('scans', file.name)
        
        url = minio_service.upload_bytes(
            file.read(),
            file_path,
            file.content_type
        )
        
        # 创建记录
        scan_file = ScanFile.objects.create(
            file_name=file.name,
            file_path=file_path,
            file_type=file.content_type,
            file_size=file.size,
            workflow_id=workflow_id if workflow_id else None,
            created_by=request.user
        )
        
        return success_response(
            ScanFileSerializer(scan_file).data,
            '文件上传成功'
        )
    
    @action(detail=True, methods=['post'])
    def recognize(self, request, pk=None):
        """
        触发OCR识别
        
        调用PaddleOCR服务进行识别
        """
        scan_file = self.get_object()
        
        if scan_file.status == 'processing':
            return error_response('文件正在识别中')
        
        if scan_file.status == 'completed':
            # 已有识别结果，直接返回
            result = OCRResult.objects.filter(scan_file=scan_file).first()
            if result:
                return success_response(
                    OCRResultSerializer(result).data,
                    '获取已有识别结果'
                )
        
        # 更新状态为识别中
        scan_file.status = 'processing'
        scan_file.save(update_fields=['status', 'updated_at'])
        
        # 调用OCR服务
        ocr_service = get_ocr_service()
        
        import time
        start_time = time.time()
        result = ocr_service.recognize(scan_file.file_path)
        process_time = time.time() - start_time
        
        if result.get('success'):
            # 保存识别结果
            ocr_result = OCRResult.objects.create(
                scan_file=scan_file,
                raw_text=result.get('text', ''),
                structured_data=result.get('structured_data', {}),
                confidence=result.get('confidence', 0),
                details=result.get('details', []),
                process_time=process_time,
                created_by=request.user
            )
            
            scan_file.status = 'completed'
            scan_file.save(update_fields=['status', 'updated_at'])
            
            return success_response(
                OCRResultSerializer(ocr_result).data,
                '识别完成'
            )
        else:
            scan_file.status = 'failed'
            scan_file.save(update_fields=['status', 'updated_at'])
            return error_response(f"识别失败: {result.get('message', '未知错误')}")


class OCRResultViewSet(viewsets.ReadOnlyModelViewSet):
    """OCR识别结果视图集（只读）"""
    queryset = OCRResult.objects.all()
    serializer_class = OCRResultSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['scan_file']


class ReportViewSet(viewsets.ModelViewSet):
    """
    检测报告视图集
    
    接口列表：
    - GET /reports/ - 获取报告列表
    - POST /reports/ - 创建报告
    - GET /reports/{id}/ - 获取报告详情
    - PUT /reports/{id}/ - 更新报告
    - POST /reports/{id}/review/ - 审核报告
    - POST /reports/{id}/approve/ - 批准报告
    - POST /reports/{id}/generate_pdf/ - 生成PDF
    """
    queryset = Report.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['workflow', 'status', 'editor']
    search_fields = ['report_code', 'title']
    ordering_fields = ['created_at', 'issue_date']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver', 'client'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver', 'client'],
        'create': ['admin', 'tester'],
        'update': ['admin', 'tester'],
        'review': ['admin', 'reviewer'],
        'approve': ['admin', 'approver'],
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        return ReportDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(
            editor=self.request.user,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """审核报告"""
        report = self.get_object()
        
        if report.status != 'draft':
            return error_response('只有草稿状态的报告可以审核')
        
        approved = request.data.get('approved', True)
        remarks = request.data.get('remarks', '')
        
        if approved:
            report.status = 'approved'
            report.reviewer = request.user
            report.review_date = timezone.now()
            report.save()
            return success_response(ReportDetailSerializer(report).data, '报告审核通过')
        else:
            report.status = 'draft'
            report.save()
            return success_response(message=f'报告被退回: {remarks}')
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """批准报告"""
        report = self.get_object()
        
        if report.status != 'approved':
            return error_response('只有已审核的报告可以批准')
        
        report.status = 'issued'
        report.approver = request.user
        report.approve_date = timezone.now()
        report.issue_date = timezone.now().date()
        report.save()
        
        return success_response(ReportDetailSerializer(report).data, '报告已批准发放')
    
    @action(detail=True, methods=['post'])
    def generate_pdf(self, request, pk=None):
        """
        生成PDF报告
        
        预留接口，后续实现PDF生成逻辑
        """
        report = self.get_object()
        
        # TODO: 实现PDF生成逻辑
        # 可使用 reportlab 或 weasyprint 库
        
        return success_response(message='PDF生成功能待实现')
