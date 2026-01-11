"""云查询视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission, IsAdminUser
from .models import QueryApplication, QueryLog
from .serializers import (
    QueryApplicationSerializer, QueryApplicationCreateSerializer,
    ApprovalSerializer, QueryLogSerializer
)


class QueryApplicationViewSet(viewsets.ModelViewSet):
    """
    查看申请视图集
    
    接口列表：
    - GET /applications/ - 获取申请列表
    - POST /applications/ - 提交申请
    - GET /applications/{id}/ - 获取申请详情
    - POST /applications/{id}/approve/ - 审批申请
    - GET /applications/my/ - 获取我的申请
    """
    queryset = QueryApplication.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'applicant_role', 'applicant']
    ordering_fields = ['created_at', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QueryApplicationCreateSerializer
        return QueryApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = QueryApplication.objects.filter(is_deleted=False)
        
        # 管理员可看所有，其他用户只能看自己的申请
        if user.role != 'admin':
            return queryset.filter(applicant=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(
            applicant=self.request.user,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """审批申请"""
        application = self.get_object()
        
        if application.status != 'pending':
            return error_response('该申请已处理')
        
        serializer = ApprovalSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        data = serializer.validated_data
        approved = data['approved']
        
        if approved:
            application.status = 'approved'
            application.valid_from = timezone.now()
            application.valid_until = timezone.now() + timedelta(days=data.get('valid_days', 30))
        else:
            application.status = 'rejected'
        
        application.reviewer = request.user
        application.review_time = timezone.now()
        application.review_remark = data.get('remark', '')
        application.save()
        
        return success_response(
            QueryApplicationSerializer(application).data,
            '审批完成'
        )
    
    @action(detail=False, methods=['get'])
    def my(self, request):
        """获取我的申请"""
        applications = QueryApplication.objects.filter(
            applicant=request.user,
            is_deleted=False
        ).order_by('-created_at')
        
        serializer = QueryApplicationSerializer(applications, many=True)
        return success_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """获取待审批的申请（管理员）"""
        if request.user.role != 'admin':
            return error_response('权限不足', code=403)
        
        applications = QueryApplication.objects.filter(
            status='pending',
            is_deleted=False
        ).order_by('created_at')
        
        serializer = QueryApplicationSerializer(applications, many=True)
        return success_response(serializer.data)


class QueryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """查询日志视图集（只读）"""
    queryset = QueryLog.objects.all()
    serializer_class = QueryLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['application', 'query_user']
    ordering_fields = ['created_at']


class CloudDataView(viewsets.ViewSet):
    """
    云数据查询视图
    
    供外部用户查询数据（需要已批准的申请）
    """
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """
        查询数据
        
        根据用户的申请权限返回可查看的数据
        """
        user = request.user
        
        # 检查是否有有效的申请
        valid_application = QueryApplication.objects.filter(
            applicant=user,
            status='approved',
            valid_until__gte=timezone.now(),
            is_deleted=False
        ).first()
        
        if not valid_application:
            return error_response('没有有效的查询权限，请先提交申请', code=403)
        
        # 根据申请范围返回数据
        query_scope = valid_application.query_scope
        query_type = valid_application.query_type
        
        result = {}
        
        if query_type == 'report':
            # 查询检测报告
            from apps.ocr.models import Report
            reports = Report.objects.filter(
                status='issued',
                is_deleted=False
            )
            # 根据 scope 过滤
            if query_scope.get('client_id'):
                reports = reports.filter(
                    workflow__sample_receive__commission__client_id=query_scope['client_id']
                )
            
            from apps.ocr.serializers import ReportListSerializer
            result['reports'] = ReportListSerializer(reports[:50], many=True).data
        
        # 记录查询日志
        QueryLog.objects.create(
            application=valid_application,
            query_user=user,
            query_content=query_type,
            query_params=request.query_params.dict(),
            ip_address=self._get_client_ip(request),
            created_by=user
        )
        
        return success_response(result)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
