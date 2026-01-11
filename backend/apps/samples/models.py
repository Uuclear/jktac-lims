"""
委托收样数据模型

定义委托方、委托单、收样记录相关的数据表结构
"""

from django.db import models
from django.conf import settings
from common.models import BaseModel
from common.utils import generate_code


class Client(BaseModel):
    """
    委托方模型
    
    存储委托方的基本信息
    
    Attributes:
        name: 委托方名称（单位名称）
        code: 委托方编码
        contact_person: 联系人
        contact_phone: 联系电话
        address: 地址
        user: 关联的用户账户
    """
    name = models.CharField(
        max_length=200,
        verbose_name='委托方名称',
        help_text='单位全称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='委托方编码',
        help_text='系统自动生成的唯一编码'
    )
    contact_person = models.CharField(
        max_length=50,
        verbose_name='联系人'
    )
    contact_phone = models.CharField(
        max_length=20,
        verbose_name='联系电话'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='邮箱'
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='地址'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_info',
        verbose_name='关联用户',
        help_text='委托方登录账户'
    )
    credit_level = models.CharField(
        max_length=10,
        choices=[('A', 'A级'), ('B', 'B级'), ('C', 'C级')],
        default='B',
        verbose_name='信用等级'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_client'
        verbose_name = '委托方'
        verbose_name_plural = '委托方列表'
        indexes = [
            models.Index(fields=['code'], name='idx_client_code'),
            models.Index(fields=['name'], name='idx_client_name'),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code('CL', 6)
        super().save(*args, **kwargs)


class Commission(BaseModel):
    """
    委托单模型
    
    记录检测委托的详细信息
    
    Attributes:
        code: 委托单编号
        client: 委托方
        project_name: 工程名称
        sample_name: 样品名称
        sample_model: 样品型号/规格
        sample_quantity: 样品数量
        test_parameters: 检测参数（关联能力管理模块）
        commission_date: 委托日期
        required_date: 要求完成日期
        status: 委托单状态
    """
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('received', '已收样'),
        ('testing', '试验中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='委托单编号',
        help_text='系统自动生成'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='commissions',
        verbose_name='委托方'
    )
    project_name = models.CharField(
        max_length=200,
        verbose_name='工程名称'
    )
    project_location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='工程地点'
    )
    sample_name = models.CharField(
        max_length=200,
        verbose_name='样品名称'
    )
    sample_model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='样品型号/规格'
    )
    sample_quantity = models.IntegerField(
        default=1,
        verbose_name='样品数量'
    )
    sample_unit = models.CharField(
        max_length=20,
        default='组',
        verbose_name='样品单位'
    )
    sample_source = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='样品来源',
        help_text='生产厂家或产地'
    )
    sample_batch = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='样品批号'
    )
    test_basis = models.TextField(
        blank=True,
        null=True,
        verbose_name='检测依据',
        help_text='检测标准或规范'
    )
    test_parameters = models.TextField(
        verbose_name='检测参数',
        help_text='需要检测的参数，JSON格式存储'
    )
    commission_date = models.DateField(
        verbose_name='委托日期'
    )
    required_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='要求完成日期'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='状态',
        db_index=True
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='总费用'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_commission'
        verbose_name = '委托单'
        verbose_name_plural = '委托单列表'
        ordering = ['-commission_date', '-created_at']
        indexes = [
            models.Index(fields=['code'], name='idx_commission_code'),
            models.Index(fields=['status'], name='idx_commission_status'),
            models.Index(fields=['client', 'status'], name='idx_commission_client_status'),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.sample_name}"
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_code('WT', 8)
        super().save(*args, **kwargs)


class SampleReceive(BaseModel):
    """
    收样记录模型
    
    记录样品接收的详细信息
    
    Attributes:
        commission: 关联的委托单
        receive_code: 收样编号
        receiver: 收样人
        receive_time: 收样时间
        sample_condition: 样品状态
        storage_location: 存放位置
    """
    
    CONDITION_CHOICES = [
        ('normal', '正常'),
        ('damaged', '破损'),
        ('insufficient', '数量不足'),
        ('other', '其他'),
    ]
    
    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name='receive_records',
        verbose_name='委托单'
    )
    receive_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='收样编号'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='received_samples',
        verbose_name='收样人'
    )
    receive_time = models.DateTimeField(
        verbose_name='收样时间'
    )
    actual_quantity = models.IntegerField(
        verbose_name='实收数量'
    )
    sample_condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='normal',
        verbose_name='样品状态'
    )
    condition_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='状态说明'
    )
    storage_location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='存放位置'
    )
    photos = models.JSONField(
        default=list,
        blank=True,
        verbose_name='样品照片',
        help_text='存储照片URL列表'
    )
    
    class Meta:
        db_table = 'lims_sample_receive'
        verbose_name = '收样记录'
        verbose_name_plural = '收样记录列表'
        ordering = ['-receive_time']
    
    def __str__(self):
        return f"{self.receive_code} - {self.commission.sample_name}"
    
    def save(self, *args, **kwargs):
        if not self.receive_code:
            self.receive_code = generate_code('SY', 8)
        super().save(*args, **kwargs)
