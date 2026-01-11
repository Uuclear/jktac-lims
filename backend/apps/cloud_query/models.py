"""云查询数据模型"""

from django.db import models
from django.conf import settings
from common.models import BaseModel


class QueryApplication(BaseModel):
    """
    查看申请模型
    
    记录外部用户（委托方/业主方/监理方）的数据查看申请
    """
    
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('expired', '已过期'),
    ]
    
    ROLE_CHOICES = [
        ('client', '委托方'),
        ('owner', '业主方'),
        ('supervisor', '监理方'),
    ]
    
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='query_applications',
        verbose_name='申请人'
    )
    applicant_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='申请人角色'
    )
    organization = models.CharField(
        max_length=200,
        verbose_name='所属单位'
    )
    query_type = models.CharField(
        max_length=50,
        verbose_name='查询类型',
        help_text='如：检测报告、试验数据等'
    )
    query_scope = models.JSONField(
        default=dict,
        verbose_name='查询范围',
        help_text='可查询的数据范围定义'
    )
    reason = models.TextField(
        verbose_name='申请理由'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    valid_from = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='有效期起'
    )
    valid_until = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='有效期止'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications',
        verbose_name='审批人'
    )
    review_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='审批时间'
    )
    review_remark = models.TextField(
        blank=True,
        null=True,
        verbose_name='审批备注'
    )
    
    class Meta:
        db_table = 'lims_query_application'
        verbose_name = '查看申请'
        verbose_name_plural = '查看申请列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.query_type}"


class QueryLog(BaseModel):
    """
    查询日志模型
    
    记录外部用户的查询操作
    """
    application = models.ForeignKey(
        QueryApplication,
        on_delete=models.CASCADE,
        related_name='query_logs',
        verbose_name='关联申请'
    )
    query_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cloud_query_logs',
        verbose_name='查询用户'
    )
    query_content = models.CharField(
        max_length=500,
        verbose_name='查询内容'
    )
    query_params = models.JSONField(
        default=dict,
        verbose_name='查询参数'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址'
    )
    
    class Meta:
        db_table = 'lims_query_log'
        verbose_name = '查询日志'
        verbose_name_plural = '查询日志列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.query_user.username} - {self.query_content}"
