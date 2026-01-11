"""
原始记录模块视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from .models import RecordTemplate, OriginalRecord, RecordAttachment
from .serializers import (
    RecordTemplateSerializer,
    OriginalRecordListSerializer, OriginalRecordDetailSerializer, OriginalRecordCreateSerializer,
    RecordAttachmentSerializer
)


class RecordTemplateViewSet(viewsets.ModelViewSet):
    """
    原始记录模板视图集
    
    接口列表：
    - GET /templates/ - 获取模板列表
    - POST /templates/ - 创建模板
    - GET /templates/{id}/ - 获取模板详情
    - PUT /templates/{id}/ - 更新模板
    - DELETE /templates/{id}/ - 删除模板
    - GET /templates/categories/ - 获取模板分类
    """
    queryset = RecordTemplate.objects.filter(is_deleted=False, is_active=True)
    serializer_class = RecordTemplateSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'code', 'category']
    ordering_fields = ['name', 'category', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'partial_update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取所有模板分类"""
        categories = RecordTemplate.objects.filter(
            is_deleted=False, is_active=True
        ).values_list('category', flat=True).distinct()
        return success_response(list(categories))


class OriginalRecordViewSet(viewsets.ModelViewSet):
    """
    原始记录视图集
    
    接口列表：
    - GET /records/ - 获取记录列表
    - POST /records/ - 创建记录
    - GET /records/{id}/ - 获取记录详情
    - PUT /records/{id}/ - 更新记录
    - POST /records/{id}/submit/ - 提交记录
    - POST /records/{id}/approve/ - 审核记录
    - POST /records/generate/ - 根据委托单生成记录
    """
    queryset = OriginalRecord.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['template', 'workflow', 'status', 'tester']
    search_fields = ['record_code']
    ordering_fields = ['test_date', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin', 'tester'],
        'update': ['admin', 'tester'],
        'partial_update': ['admin', 'tester'],
        'destroy': ['admin'],
        'submit': ['admin', 'tester'],
        'approve': ['admin', 'reviewer'],
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OriginalRecordListSerializer
        elif self.action == 'create':
            return OriginalRecordCreateSerializer
        return OriginalRecordDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = OriginalRecord.objects.filter(is_deleted=False)
        
        if user.role == 'tester':
            return queryset.filter(tester=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            tester=self.request.user,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交记录"""
        record = self.get_object()
        
        if record.status != 'draft':
            return error_response('只有草稿状态的记录可以提交')
        
        record.status = 'submitted'
        record.save(update_fields=['status', 'updated_at'])
        
        return success_response(
            OriginalRecordDetailSerializer(record).data,
            '记录已提交'
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核记录"""
        record = self.get_object()
        
        if record.status != 'submitted':
            return error_response('只有已提交的记录可以审核')
        
        record.status = 'approved'
        record.reviewer = request.user
        record.review_date = timezone.now()
        record.save(update_fields=['status', 'reviewer', 'review_date', 'updated_at'])
        
        return success_response(
            OriginalRecordDetailSerializer(record).data,
            '记录审核通过'
        )
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """
        根据流转记录生成原始记录
        
        请求参数：
        - workflow_id: 流转记录ID
        - template_id: 模板ID
        """
        workflow_id = request.data.get('workflow_id')
        template_id = request.data.get('template_id')
        
        if not workflow_id or not template_id:
            return error_response('缺少必要参数')
        
        try:
            from apps.workflow.models import SampleWorkflow
            workflow = SampleWorkflow.objects.get(pk=workflow_id)
            template = RecordTemplate.objects.get(pk=template_id)
        except (SampleWorkflow.DoesNotExist, RecordTemplate.DoesNotExist):
            return error_response('流转记录或模板不存在')
        
        # 生成初始数据
        commission = workflow.sample_receive.commission
        initial_data = {
            'sample_name': commission.sample_name,
            'sample_model': commission.sample_model,
            'commission_code': commission.code,
            'project_name': commission.project_name,
        }
        
        record = OriginalRecord.objects.create(
            template=template,
            workflow=workflow,
            data=initial_data,
            tester=request.user,
            test_date=timezone.now().date(),
            created_by=request.user
        )
        
        return success_response(
            OriginalRecordDetailSerializer(record).data,
            '原始记录生成成功'
        )


class RecordAttachmentViewSet(viewsets.ModelViewSet):
    """记录附件视图集"""
    queryset = RecordAttachment.objects.filter(is_deleted=False)
    serializer_class = RecordAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['record']
