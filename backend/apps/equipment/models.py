"""
试验室与设备管理数据模型
"""

from django.db import models
from django.conf import settings
from common.models import BaseModel


class Laboratory(BaseModel):
    """
    试验室模型
    
    存储试验室房间信息
    """
    name = models.CharField(
        max_length=100,
        verbose_name='试验室名称'
    )
    room_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='房间号'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='位置描述'
    )
    area = models.FloatField(
        blank=True,
        null=True,
        verbose_name='面积(m²)'
    )
    temperature_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='温度要求',
        help_text='如 20±2℃'
    )
    humidity_range = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='湿度要求',
        help_text='如 50%±10%'
    )
    responsible_person = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_labs',
        verbose_name='负责人'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_laboratory'
        verbose_name = '试验室'
        verbose_name_plural = '试验室列表'
        ordering = ['room_number']
    
    def __str__(self):
        return f"{self.room_number} - {self.name}"


class Equipment(BaseModel):
    """
    设备模型
    
    存储设备基本信息
    """
    
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('calibrating', '校准中'),
        ('maintenance', '维修中'),
        ('disabled', '停用'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='设备名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='设备编号'
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='型号规格'
    )
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='生产厂家'
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='出厂编号'
    )
    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='equipments',
        verbose_name='所在试验室'
    )
    purchase_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='购置日期'
    )
    commissioning_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='启用日期'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='normal',
        verbose_name='设备状态'
    )
    accuracy = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='准确度/精度'
    )
    measurement_range = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='测量范围'
    )
    custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='custodied_equipments',
        verbose_name='保管人'
    )
    photo = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='设备照片'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_equipment'
        verbose_name = '设备'
        verbose_name_plural = '设备列表'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class CalibrationRecord(BaseModel):
    """
    校准记录模型
    """
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='calibrations',
        verbose_name='设备'
    )
    calibration_date = models.DateField(
        verbose_name='校准日期'
    )
    valid_until = models.DateField(
        verbose_name='有效期至'
    )
    calibration_org = models.CharField(
        max_length=200,
        verbose_name='校准机构'
    )
    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='证书编号'
    )
    certificate_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='证书文件路径'
    )
    result = models.CharField(
        max_length=20,
        choices=[('qualified', '合格'), ('unqualified', '不合格')],
        default='qualified',
        verbose_name='校准结果'
    )
    calibration_data = models.JSONField(
        default=dict,
        verbose_name='校准数据',
        help_text='校准参数及结果'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='校准费用'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_calibration_record'
        verbose_name = '校准记录'
        verbose_name_plural = '校准记录列表'
        ordering = ['-calibration_date']
    
    def __str__(self):
        return f"{self.equipment.code} - {self.calibration_date}"


class EquipmentUsageLog(BaseModel):
    """
    设备使用记录模型
    """
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        verbose_name='设备'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='equipment_usage',
        verbose_name='使用人'
    )
    start_time = models.DateTimeField(
        verbose_name='开始时间'
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='结束时间'
    )
    purpose = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='使用目的'
    )
    sample_info = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='相关样品'
    )
    condition_before = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='使用前状态'
    )
    condition_after = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='使用后状态'
    )
    remarks = models.TextField(
        blank=True,
        null=True,
        verbose_name='备注'
    )
    
    class Meta:
        db_table = 'lims_equipment_usage_log'
        verbose_name = '设备使用记录'
        verbose_name_plural = '设备使用记录列表'
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.equipment.code} - {self.user.username} - {self.start_time}"
