"""AI校验数据模型"""

from django.db import models
from django.conf import settings
from common.models import BaseModel


class VerifyRecord(BaseModel):
    """
    AI校验记录模型
    """
    
    TYPE_CHOICES = [
        ('typo', '错别字校验'),
        ('data', '数据合理性校验'),
        ('format', '格式校验'),
        ('comprehensive', '综合校验'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待校验'),
        ('processing', '校验中'),
        ('completed', '已完成'),
        ('failed', '校验失败'),
    ]
    
    document_type = models.CharField(
        max_length=50,
        verbose_name='文档类型',
        help_text='如：原始记录、检测报告等'
    )
    document_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='关联文档ID'
    )
    content = models.TextField(
        verbose_name='校验内容'
    )
    verify_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='comprehensive',
        verbose_name='校验类型'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    issues = models.JSONField(
        default=list,
        verbose_name='发现的问题',
        help_text='问题列表'
    )
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name='校验总结'
    )
    model_used = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='使用的模型'
    )
    process_time = models.FloatField(
        default=0,
        verbose_name='处理时间',
        help_text='秒'
    )
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verify_records',
        verbose_name='操作人'
    )
    
    class Meta:
        db_table = 'lims_verify_record'
        verbose_name = 'AI校验记录'
        verbose_name_plural = 'AI校验记录列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document_type} - {self.get_verify_type_display()}"


class VerifyRule(BaseModel):
    """
    校验规则模型
    
    存储自定义的校验规则
    """
    name = models.CharField(
        max_length=100,
        verbose_name='规则名称'
    )
    rule_type = models.CharField(
        max_length=50,
        verbose_name='规则类型'
    )
    rule_content = models.JSONField(
        default=dict,
        verbose_name='规则内容'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='规则描述'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    class Meta:
        db_table = 'lims_verify_rule'
        verbose_name = '校验规则'
        verbose_name_plural = '校验规则列表'
    
    def __str__(self):
        return self.name
