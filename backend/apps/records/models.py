"""
原始记录数据模型

定义原始记录模板、记录实例相关的数据表结构
"""

from django.db import models
from django.conf import settings
from common.models import BaseModel
from common.utils import generate_code


class RecordTemplate(BaseModel):
    """
    原始记录模板模型
    
    定义原始记录的结构和字段配置
    
    Attributes:
        name: 模板名称
        code: 模板编码
        category: 模板分类
        fields: 字段配置（JSON）
        version: 版本号
    """
    name = models.CharField(
        max_length=100,
        verbose_name='模板名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='模板编码'
    )
    category = models.CharField(
        max_length=50,
        verbose_name='模板分类',
        help_text='如：水泥、钢筋、混凝土等'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='模板描述'
    )
    fields = models.JSONField(
        default=list,
        verbose_name='字段配置',
        help_text='''
        字段配置JSON格式示例：
        [
            {"name": "试验编号", "type": "text", "required": true},
            {"name": "试验日期", "type": "date", "required": true},
            {"name": "抗压强度", "type": "number", "unit": "MPa", "required": true}
        ]
        '''
    )
    header_info = models.JSONField(
        default=dict,
        verbose_name='表头信息',
        help_text='模板表头的固定信息'
    )
    footer_info = models.JSONField(
        default=dict,
        verbose_name='表尾信息',
        help_text='模板表尾的固定信息'
    )
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name='版本号'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    class Meta:
        db_table = 'lims_record_template'
        verbose_name = '原始记录模板'
        verbose_name_plural = '原始记录模板列表'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category'], name='idx_template_category'),
            models.Index(fields=['is_active'], name='idx_template_active'),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code('TP', 6)
        super().save(*args, **kwargs)


class OriginalRecord(BaseModel):
    """
    原始记录实例模型
    
    存储每次试验的原始记录数据
    
    Attributes:
        template: 使用的模板
        workflow: 关联的流转记录
        record_code: 记录编号
        data: 记录数据（JSON）
        tester: 试验人员
        test_date: 试验日期
    """
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('approved', '已审核'),
    ]
    
    template = models.ForeignKey(
        RecordTemplate,
        on_delete=models.PROTECT,
        related_name='records',
        verbose_name='使用模板'
    )
    workflow = models.ForeignKey(
        'workflow.SampleWorkflow',
        on_delete=models.CASCADE,
        related_name='original_records',
        verbose_name='关联流转'
    )
    record_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='记录编号'
    )
    data = models.JSONField(
        default=dict,
        verbose_name='记录数据',
        help_text='按模板字段配置存储的数据'
    )
    tester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='tested_records',
        verbose_name='试验人员'
    )
    test_date = models.DateField(
        verbose_name='试验日期'
    )
    test_location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='试验地点'
    )
    equipment_info = models.JSONField(
        default=list,
        verbose_name='使用设备',
        help_text='使用的设备编号列表'
    )
    environment_info = models.JSONField(
        default=dict,
        verbose_name='环境条件',
        help_text='温度、湿度等环境信息'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_records',
        verbose_name='审核人'
    )
    review_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='审核时间'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_original_record'
        verbose_name = '原始记录'
        verbose_name_plural = '原始记录列表'
        ordering = ['-test_date', '-created_at']
        indexes = [
            models.Index(fields=['record_code'], name='idx_record_code'),
            models.Index(fields=['status'], name='idx_record_status'),
            models.Index(fields=['test_date'], name='idx_record_date'),
        ]
    
    def __str__(self):
        return f"{self.record_code} - {self.template.name}"
    
    def save(self, *args, **kwargs):
        if not self.record_code:
            self.record_code = generate_code('YS', 8)
        super().save(*args, **kwargs)


class RecordAttachment(BaseModel):
    """
    记录附件模型
    
    存储原始记录相关的附件文件
    """
    record = models.ForeignKey(
        OriginalRecord,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='原始记录'
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name='文件名'
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name='文件路径'
    )
    file_type = models.CharField(
        max_length=50,
        verbose_name='文件类型'
    )
    file_size = models.IntegerField(
        verbose_name='文件大小',
        help_text='字节数'
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='描述'
    )
    
    class Meta:
        db_table = 'lims_record_attachment'
        verbose_name = '记录附件'
        verbose_name_plural = '记录附件列表'
    
    def __str__(self):
        return self.file_name
