"""
试验室能力管理数据模型

管理检测标准、检测参数、参数价格等
"""

from django.db import models
from common.models import BaseModel


class TestStandard(BaseModel):
    """
    检测标准模型
    
    存储检测依据的标准规范
    """
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='标准编号',
        help_text='如 GB/T 50081-2019'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='标准名称'
    )
    category = models.CharField(
        max_length=50,
        verbose_name='标准分类',
        help_text='如：水泥、混凝土、钢筋等'
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='版本/年份'
    )
    effective_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='实施日期'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否有效'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='标准文件路径'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='标准描述'
    )
    
    class Meta:
        db_table = 'lims_test_standard'
        verbose_name = '检测标准'
        verbose_name_plural = '检测标准列表'
        ordering = ['category', 'code']
    
    def __str__(self):
        return f"{self.code} {self.name}"


class TestParameter(BaseModel):
    """
    检测参数模型
    
    定义可检测的参数项目
    """
    name = models.CharField(
        max_length=100,
        verbose_name='参数名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='参数编码'
    )
    standard = models.ForeignKey(
        TestStandard,
        on_delete=models.PROTECT,
        related_name='parameters',
        verbose_name='所属标准'
    )
    unit = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='计量单位'
    )
    method = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='检测方法'
    )
    detection_limit = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='检出限'
    )
    uncertainty = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='不确定度'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否可检'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_test_parameter'
        verbose_name = '检测参数'
        verbose_name_plural = '检测参数列表'
        ordering = ['standard', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.standard.code})"


class ParameterPrice(BaseModel):
    """
    参数价格模型
    
    管理检测参数的收费标准
    """
    parameter = models.ForeignKey(
        TestParameter,
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name='检测参数'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='单价',
        help_text='元'
    )
    price_type = models.CharField(
        max_length=20,
        choices=[
            ('normal', '普通'),
            ('urgent', '加急'),
            ('special', '特殊')
        ],
        default='normal',
        verbose_name='价格类型'
    )
    effective_date = models.DateField(
        verbose_name='生效日期'
    )
    expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='失效日期'
    )
    
    class Meta:
        db_table = 'lims_parameter_price'
        verbose_name = '参数价格'
        verbose_name_plural = '参数价格列表'
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.parameter.name} - ¥{self.price}"
