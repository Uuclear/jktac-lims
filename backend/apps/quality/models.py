"""
质量体系管理数据模型
"""

from django.db import models
from common.models import BaseModel


class QualityDocument(BaseModel):
    """
    质量体系文件模型
    
    存储质量体系相关的文档信息
    """
    
    TYPE_CHOICES = [
        ('manual', '质量手册'),
        ('procedure', '程序文件'),
        ('instruction', '作业指导书'),
        ('record', '记录表格'),
        ('standard', '技术标准'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '有效'),
        ('obsolete', '作废'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='文件名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='文件编号'
    )
    doc_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='文件类型'
    )
    version = models.CharField(
        max_length=20,
        default='1.0',
        verbose_name='版本号'
    )
    category = models.ForeignKey(
        'DocumentCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='文件分类'
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name='文件路径'
    )
    file_size = models.IntegerField(
        default=0,
        verbose_name='文件大小'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='文件描述'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    effective_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='生效日期'
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='失效日期'
    )
    download_count = models.IntegerField(
        default=0,
        verbose_name='下载次数'
    )
    
    class Meta:
        db_table = 'lims_quality_document'
        verbose_name = '质量体系文件'
        verbose_name_plural = '质量体系文件列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class DocumentCategory(BaseModel):
    """文件分类模型"""
    name = models.CharField(
        max_length=100,
        verbose_name='分类名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='分类编码'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级分类'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序'
    )
    
    class Meta:
        db_table = 'lims_document_category'
        verbose_name = '文件分类'
        verbose_name_plural = '文件分类列表'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class DocumentVersion(BaseModel):
    """文件版本历史模型"""
    document = models.ForeignKey(
        QualityDocument,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='文件'
    )
    version = models.CharField(
        max_length=20,
        verbose_name='版本号'
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name='文件路径'
    )
    change_log = models.TextField(
        blank=True,
        null=True,
        verbose_name='修改说明'
    )
    
    class Meta:
        db_table = 'lims_document_version'
        verbose_name = '文件版本'
        verbose_name_plural = '文件版本列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.document.name} v{self.version}"
