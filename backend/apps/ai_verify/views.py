"""AI校验视图"""
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import time
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from common.services import get_ai_service
from .models import VerifyRecord, VerifyRule
from .serializers import VerifyRecordSerializer, VerifyRequestSerializer, VerifyRuleSerializer


class VerifyRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """校验记录视图集（只读）"""
    queryset = VerifyRecord.objects.filter(is_deleted=False)
    serializer_class = VerifyRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['document_type', 'verify_type', 'status', 'operator']
    ordering_fields = ['created_at']


class VerifyRuleViewSet(viewsets.ModelViewSet):
    """校验规则视图集"""
    queryset = VerifyRule.objects.filter(is_deleted=False)
    serializer_class = VerifyRuleSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['rule_type', 'is_active']
    
    role_permissions = {
        'list': ['admin', 'reviewer', 'approver'],
        'retrieve': ['admin', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VerifyView(APIView):
    """
    AI校验视图
    
    提供文档校验功能
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        触发AI校验
        
        请求参数：
        - content: 要校验的内容
        - verify_type: 校验类型
        - document_type: 文档类型（可选）
        - document_id: 文档ID（可选）
        """
        serializer = VerifyRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        data = serializer.validated_data
        content = data['content']
        verify_type = data['verify_type']
        
        # 创建校验记录
        record = VerifyRecord.objects.create(
            document_type=data.get('document_type', ''),
            document_id=data.get('document_id'),
            content=content,
            verify_type=verify_type,
            status='processing',
            operator=request.user,
            created_by=request.user
        )
        
        # 调用AI服务
        ai_service = get_ai_service()
        
        start_time = time.time()
        result = ai_service.verify_document(content)
        process_time = time.time() - start_time
        
        if result.get('success'):
            record.status = 'completed'
            record.issues = result.get('data', {}).get('issues', [])
            record.summary = result.get('data', {}).get('summary', '')
            record.model_used = ai_service.model_name
        else:
            record.status = 'failed'
            record.summary = result.get('message', '校验失败')
        
        record.process_time = process_time
        record.save()
        
        return success_response(
            VerifyRecordSerializer(record).data,
            '校验完成' if record.status == 'completed' else '校验失败'
        )
