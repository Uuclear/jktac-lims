"""
样品流转数据模型

定义样品流转状态、任务分配相关的数据表结构
"""

from django.db import models
from django.conf import settings
from common.models import BaseModel


class WorkflowStatus:
    """
    样品流转状态枚举
    
    定义样品在试验室中的完整流程状态
    """
    RECEIVED = 'received'           # 已收样
    ASSIGNED = 'assigned'           # 已分配
    TESTING = 'testing'             # 试验中
    TEST_COMPLETED = 'test_completed'  # 试验完成
    REPORT_EDITING = 'report_editing'  # 报告编制中
    UNDER_REVIEW = 'under_review'   # 审核中
    UNDER_APPROVAL = 'under_approval'  # 批准中
    COMPLETED = 'completed'         # 已完成
    REJECTED = 'rejected'           # 被退回
    
    CHOICES = [
        (RECEIVED, '已收样'),
        (ASSIGNED, '已分配'),
        (TESTING, '试验中'),
        (TEST_COMPLETED, '试验完成'),
        (REPORT_EDITING, '报告编制中'),
        (UNDER_REVIEW, '审核中'),
        (UNDER_APPROVAL, '批准中'),
        (COMPLETED, '已完成'),
        (REJECTED, '被退回'),
    ]
    
    # 状态流转规则：当前状态 -> 可流转到的状态列表
    TRANSITIONS = {
        RECEIVED: [ASSIGNED],
        ASSIGNED: [TESTING, REJECTED],
        TESTING: [TEST_COMPLETED, REJECTED],
        TEST_COMPLETED: [REPORT_EDITING, REJECTED],
        REPORT_EDITING: [UNDER_REVIEW],
        UNDER_REVIEW: [UNDER_APPROVAL, REJECTED],
        UNDER_APPROVAL: [COMPLETED, REJECTED],
        REJECTED: [ASSIGNED],
    }


class SampleWorkflow(BaseModel):
    """
    样品流转主表
    
    跟踪每个收样记录的流转状态
    
    Attributes:
        sample_receive: 关联的收样记录
        current_status: 当前状态
        assigned_to: 当前负责人
        priority: 优先级
    """
    
    PRIORITY_CHOICES = [
        (1, '普通'),
        (2, '加急'),
        (3, '特急'),
    ]
    
    sample_receive = models.OneToOneField(
        'samples.SampleReceive',
        on_delete=models.CASCADE,
        related_name='workflow',
        verbose_name='收样记录'
    )
    current_status = models.CharField(
        max_length=30,
        choices=WorkflowStatus.CHOICES,
        default=WorkflowStatus.RECEIVED,
        verbose_name='当前状态',
        db_index=True
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_workflows',
        verbose_name='当前负责人'
    )
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1,
        verbose_name='优先级'
    )
    expected_complete_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='预计完成日期'
    )
    actual_complete_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='实际完成日期'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_sample_workflow'
        verbose_name = '样品流转'
        verbose_name_plural = '样品流转列表'
        ordering = ['-priority', 'expected_complete_date', '-created_at']
        indexes = [
            models.Index(fields=['current_status'], name='idx_workflow_status'),
            models.Index(fields=['assigned_to', 'current_status'], name='idx_workflow_assignee'),
        ]
    
    def __str__(self):
        return f"{self.sample_receive.receive_code} - {self.get_current_status_display()}"
    
    def can_transition_to(self, new_status: str) -> bool:
        """
        检查是否可以流转到指定状态
        
        Args:
            new_status: 目标状态
            
        Returns:
            bool: 是否可以流转
        """
        allowed = WorkflowStatus.TRANSITIONS.get(self.current_status, [])
        return new_status in allowed


class WorkflowLog(BaseModel):
    """
    流转日志模型
    
    记录每次状态变更的详细信息
    
    Attributes:
        workflow: 关联的流转记录
        from_status: 变更前状态
        to_status: 变更后状态
        operator: 操作人
        action: 操作类型
        remarks: 备注
    """
    
    ACTION_CHOICES = [
        ('assign', '分配'),
        ('start', '开始试验'),
        ('complete', '完成试验'),
        ('submit', '提交'),
        ('review', '审核'),
        ('approve', '批准'),
        ('reject', '退回'),
        ('other', '其他'),
    ]
    
    workflow = models.ForeignKey(
        SampleWorkflow,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name='流转记录'
    )
    from_status = models.CharField(
        max_length=30,
        choices=WorkflowStatus.CHOICES,
        verbose_name='变更前状态'
    )
    to_status = models.CharField(
        max_length=30,
        choices=WorkflowStatus.CHOICES,
        verbose_name='变更后状态'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='workflow_operations',
        verbose_name='操作人'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='操作类型'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_workflow_log'
        verbose_name = '流转日志'
        verbose_name_plural = '流转日志列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workflow.sample_receive.receive_code}: {self.get_from_status_display()} -> {self.get_to_status_display()}"


class TestTask(BaseModel):
    """
    试验任务模型
    
    记录分配给试验人员的具体任务
    
    Attributes:
        workflow: 关联的流转记录
        tester: 试验人员
        test_items: 试验项目
        status: 任务状态
    """
    
    STATUS_CHOICES = [
        ('pending', '待开始'),
        ('in_progress', '进行中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    workflow = models.ForeignKey(
        SampleWorkflow,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='流转记录'
    )
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='test_tasks',
        verbose_name='试验人员'
    )
    test_items = models.JSONField(
        default=list,
        verbose_name='试验项目',
        help_text='需要完成的试验项目列表'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='任务状态'
    )
    start_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='开始时间'
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='完成时间'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_test_task'
        verbose_name = '试验任务'
        verbose_name_plural = '试验任务列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workflow.sample_receive.receive_code} - {self.tester.username}"
