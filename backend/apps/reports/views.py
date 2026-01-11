"""数据汇总视图"""
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from .models import StatisticsReport
from .serializers import StatisticsReportSerializer, StatisticsQuerySerializer


class StatisticsReportViewSet(viewsets.ModelViewSet):
    """统计报表视图集"""
    queryset = StatisticsReport.objects.filter(is_deleted=False)
    serializer_class = StatisticsReportSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['report_type']
    ordering_fields = ['created_at', 'start_date']
    
    role_permissions = {
        'list': ['admin', 'reviewer', 'approver'],
        'retrieve': ['admin', 'reviewer', 'approver'],
        'create': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class StatisticsView(APIView):
    """
    统计查询视图
    
    提供各维度的统计接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        获取统计数据
        
        查询参数：
        - start_date: 开始日期
        - end_date: 结束日期
        - dimension: 统计维度
        """
        serializer = StatisticsQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        data = serializer.validated_data
        start_date = data['start_date']
        end_date = data['end_date']
        dimension = data.get('dimension', 'sample_type')
        
        result = {}
        
        # 委托单统计
        from apps.samples.models import Commission
        commissions = Commission.objects.filter(
            commission_date__gte=start_date,
            commission_date__lte=end_date,
            is_deleted=False
        )
        
        result['commission_count'] = commissions.count()
        result['commission_by_status'] = list(
            commissions.values('status').annotate(count=Count('id'))
        )
        
        # 按日期统计
        result['commission_by_date'] = list(
            commissions.annotate(date=TruncDate('commission_date'))
            .values('date').annotate(count=Count('id')).order_by('date')
        )
        
        # 按委托方统计
        if dimension == 'client':
            result['by_client'] = list(
                commissions.values('client__name').annotate(count=Count('id'))
            )
        
        # 收入统计
        result['total_revenue'] = commissions.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        return success_response(result)


class DashboardView(APIView):
    """
    仪表盘统计视图
    
    提供首页仪表盘所需的统计数据
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        result = {}
        
        # 委托单统计
        from apps.samples.models import Commission
        result['total_commissions'] = Commission.objects.filter(is_deleted=False).count()
        result['month_commissions'] = Commission.objects.filter(
            commission_date__gte=month_start,
            is_deleted=False
        ).count()
        result['pending_commissions'] = Commission.objects.filter(
            status__in=['submitted', 'received', 'testing'],
            is_deleted=False
        ).count()
        
        # 流转统计
        from apps.workflow.models import SampleWorkflow
        result['in_progress_workflows'] = SampleWorkflow.objects.filter(
            current_status__in=['assigned', 'testing', 'report_editing'],
            is_deleted=False
        ).count()
        
        # 设备统计
        from apps.equipment.models import Equipment
        result['total_equipments'] = Equipment.objects.filter(is_deleted=False).count()
        result['need_calibration'] = 0  # 需要根据校准记录计算
        
        return success_response(result)


class ExportView(APIView):
    """
    导出视图
    
    提供Excel/PDF导出功能
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        导出统计数据
        
        请求参数：
        - export_type: 导出类型 (excel/pdf)
        - data: 要导出的数据
        """
        export_type = request.data.get('export_type', 'excel')
        data = request.data.get('data', {})
        
        # TODO: 实现导出逻辑
        # 可使用 openpyxl 导出 Excel
        # 可使用 reportlab 导出 PDF
        
        return success_response(message='导出功能待实现')
