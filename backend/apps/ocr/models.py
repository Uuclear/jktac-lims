"""
OCR识别与报告生成数据模型
"""

from django.db import models
from django.conf import settings
from common.models import BaseModel
from common.utils import generate_code


class ScanFile(BaseModel):
    """
    扫描件模型
    
    存储上传的扫描件信息
    """
    
    STATUS_CHOICES = [
        ('pending', '待识别'),
        ('processing', '识别中'),
        ('completed', '识别完成'),
        ('failed', '识别失败'),
    ]
    
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
        verbose_name='文件大小'
    )
    workflow = models.ForeignKey(
        'workflow.SampleWorkflow',
        on_delete=models.CASCADE,
        related_name='scan_files',
        verbose_name='关联流转',
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='识别状态'
    )
    
    class Meta:
        db_table = 'lims_scan_file'
        verbose_name = '扫描件'
        verbose_name_plural = '扫描件列表'
    
    def __str__(self):
        return self.file_name


class OCRResult(BaseModel):
    """
    OCR识别结果模型
    """
    scan_file = models.OneToOneField(
        ScanFile,
        on_delete=models.CASCADE,
        related_name='ocr_result',
        verbose_name='扫描件'
    )
    raw_text = models.TextField(
        verbose_name='原始识别文本'
    )
    structured_data = models.JSONField(
        default=dict,
        verbose_name='结构化数据',
        help_text='解析后的结构化数据'
    )
    confidence = models.FloatField(
        default=0,
        verbose_name='识别置信度'
    )
    details = models.JSONField(
        default=list,
        verbose_name='识别详情',
        help_text='每行文字的详细信息'
    )
    process_time = models.FloatField(
        default=0,
        verbose_name='处理时间',
        help_text='秒'
    )
    
    class Meta:
        db_table = 'lims_ocr_result'
        verbose_name = 'OCR识别结果'
        verbose_name_plural = 'OCR识别结果列表'
    
    def __str__(self):
        return f"OCR结果 - {self.scan_file.file_name}"


class Report(BaseModel):
    """
    检测报告模型
    """
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('reviewing', '审核中'),
        ('approved', '已审核'),
        ('issued', '已发放'),
    ]
    
    report_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='报告编号'
    )
    workflow = models.ForeignKey(
        'workflow.SampleWorkflow',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='关联流转'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='报告标题'
    )
    content = models.JSONField(
        default=dict,
        verbose_name='报告内容'
    )
    conclusion = models.TextField(
        blank=True,
        null=True,
        verbose_name='检测结论'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='PDF文件路径'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态'
    )
    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='edited_reports',
        verbose_name='编制人'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
        verbose_name='审核人'
    )
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports',
        verbose_name='批准人'
    )
    review_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='审核时间'
    )
    approve_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='批准时间'
    )
    issue_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='发放日期'
    )
    
    class Meta:
        db_table = 'lims_report'
        verbose_name = '检测报告'
        verbose_name_plural = '检测报告列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.report_code} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.report_code:
            self.report_code = generate_code('BG', 8)
        super().save(*args, **kwargs)
