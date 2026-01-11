"""
样品流转模块视图

提供样品流转状态管理、任务分配等API接口
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from .models import SampleWorkflow, WorkflowLog, TestTask, WorkflowStatus
from .serializers import (
    SampleWorkflowListSerializer, SampleWorkflowDetailSerializer,
    WorkflowLogSerializer, WorkflowTransitionSerializer, WorkflowAssignSerializer,
    TestTaskSerializer, TestTaskCreateSerializer
)


class SampleWorkflowViewSet(viewsets.ModelViewSet):
    """
    样品流转管理视图集
    
    接口列表：
    - GET /workflows/ - 获取流转列表
    - GET /workflows/{id}/ - 获取流转详情
    - POST /workflows/{id}/transition/ - 状态变更
    - POST /workflows/{id}/assign/ - 分配负责人
    - GET /workflows/my_tasks/ - 获取我的任务
    - GET /workflows/status_options/ - 获取状态选项
    
    权限：
    - 收样人员可以分配任务
    - 试验人员可以更新试验相关状态
    - 审核人员可以审核
    - 批准人员可以批准
    """
    queryset = SampleWorkflow.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['current_status', 'assigned_to', 'priority']
    search_fields = ['sample_receive__receive_code', 'sample_receive__commission__code']
    ordering_fields = ['priority', 'expected_complete_date', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'transition': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'assign': ['admin', 'receiver'],
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SampleWorkflowListSerializer
        return SampleWorkflowDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = SampleWorkflow.objects.filter(is_deleted=False)
        
        # 试验人员只能看到分配给自己的任务
        if user.role == 'tester':
            return queryset.filter(assigned_to=user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        """
        状态变更
        
        根据流转规则变更样品状态
        """
        workflow = self.get_object()
        serializer = WorkflowTransitionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        to_status = serializer.validated_data['to_status']
        remarks = serializer.validated_data.get('remarks', '')
        
        # 检查是否可以流转
        if not workflow.can_transition_to(to_status):
            return error_response(
                f'当前状态 "{workflow.get_current_status_display()}" '
                f'不能流转到 "{dict(WorkflowStatus.CHOICES).get(to_status)}"'
            )
        
        # 记录日志
        WorkflowLog.objects.create(
            workflow=workflow,
            from_status=workflow.current_status,
            to_status=to_status,
            operator=request.user,
            action=self._get_action_type(to_status),
            remarks=remarks,
            created_by=request.user
        )
        
        # 更新状态
        old_status = workflow.current_status
        workflow.current_status = to_status
        
        # 如果完成，记录实际完成日期
        if to_status == WorkflowStatus.COMPLETED:
            workflow.actual_complete_date = timezone.now().date()
            # 同步更新委托单状态
            workflow.sample_receive.commission.status = 'completed'
            workflow.sample_receive.commission.save(update_fields=['status', 'updated_at'])
        
        workflow.save(update_fields=['current_status', 'actual_complete_date', 'updated_at'])
        
        return success_response(
            SampleWorkflowDetailSerializer(workflow).data,
            f'状态已更新为 "{workflow.get_current_status_display()}"'
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        分配负责人
        """
        workflow = self.get_object()
        serializer = WorkflowAssignSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        from apps.users.models import User
        try:
            assignee = User.objects.get(pk=serializer.validated_data['assigned_to'])
        except User.DoesNotExist:
            return error_response('指定的用户不存在')
        
        # 更新分配信息
        workflow.assigned_to = assignee
        workflow.priority = serializer.validated_data.get('priority', workflow.priority)
        if serializer.validated_data.get('expected_complete_date'):
            workflow.expected_complete_date = serializer.validated_data['expected_complete_date']
        
        # 更新状态为已分配
        if workflow.current_status == WorkflowStatus.RECEIVED:
            old_status = workflow.current_status
            workflow.current_status = WorkflowStatus.ASSIGNED
            
            # 记录日志
            WorkflowLog.objects.create(
                workflow=workflow,
                from_status=old_status,
                to_status=WorkflowStatus.ASSIGNED,
                operator=request.user,
                action='assign',
                remarks=serializer.validated_data.get('remarks', f'分配给 {assignee.username}'),
                created_by=request.user
            )
        
        workflow.save()
        
        return success_response(
            SampleWorkflowDetailSerializer(workflow).data,
            f'已分配给 {assignee.username}'
        )
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """
        获取当前用户的任务
        """
        user = request.user
        queryset = SampleWorkflow.objects.filter(
            is_deleted=False,
            assigned_to=user,
            current_status__in=[
                WorkflowStatus.ASSIGNED,
                WorkflowStatus.TESTING,
                WorkflowStatus.TEST_COMPLETED,
                WorkflowStatus.REPORT_EDITING,
                WorkflowStatus.UNDER_REVIEW,
                WorkflowStatus.UNDER_APPROVAL,
            ]
        ).order_by('-priority', 'expected_complete_date')
        
        serializer = SampleWorkflowListSerializer(queryset, many=True)
        return success_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def status_options(self, request):
        """
        获取状态选项
        """
        return success_response([
            {'value': status[0], 'label': status[1]}
            for status in WorkflowStatus.CHOICES
        ])
    
    def _get_action_type(self, to_status):
        """根据目标状态获取操作类型"""
        action_map = {
            WorkflowStatus.ASSIGNED: 'assign',
            WorkflowStatus.TESTING: 'start',
            WorkflowStatus.TEST_COMPLETED: 'complete',
            WorkflowStatus.REPORT_EDITING: 'submit',
            WorkflowStatus.UNDER_REVIEW: 'submit',
            WorkflowStatus.UNDER_APPROVAL: 'review',
            WorkflowStatus.COMPLETED: 'approve',
            WorkflowStatus.REJECTED: 'reject',
        }
        return action_map.get(to_status, 'other')


class WorkflowLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    流转日志视图集（只读）
    """
    queryset = WorkflowLog.objects.all()
    serializer_class = WorkflowLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['workflow', 'operator', 'action']
    ordering_fields = ['created_at']


class TestTaskViewSet(viewsets.ModelViewSet):
    """
    试验任务视图集
    
    接口列表：
    - GET /tasks/ - 获取任务列表
    - POST /tasks/ - 创建任务
    - POST /tasks/{id}/start/ - 开始任务
    - POST /tasks/{id}/complete/ - 完成任务
    """
    queryset = TestTask.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['workflow', 'tester', 'status']
    ordering_fields = ['created_at', 'start_time']
    
    role_permissions = {
        'list': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin', 'receiver'],
        'start': ['admin', 'tester'],
        'complete': ['admin', 'tester'],
    }
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TestTaskCreateSerializer
        return TestTaskSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = TestTask.objects.filter(is_deleted=False)
        
        if user.role == 'tester':
            return queryset.filter(tester=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """开始任务"""
        task = self.get_object()
        
        if task.status != 'pending':
            return error_response('只有待开始的任务可以开始')
        
        task.status = 'in_progress'
        task.start_time = timezone.now()
        task.save(update_fields=['status', 'start_time', 'updated_at'])
        
        return success_response(TestTaskSerializer(task).data, '任务已开始')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成任务"""
        task = self.get_object()
        
        if task.status != 'in_progress':
            return error_response('只有进行中的任务可以完成')
        
        task.status = 'completed'
        task.end_time = timezone.now()
        task.save(update_fields=['status', 'end_time', 'updated_at'])
        
        return success_response(TestTaskSerializer(task).data, '任务已完成')
