"""试验室平面图数据模型"""

from django.db import models
from common.models import BaseModel


class FloorPlan(BaseModel):
    """
    平面图模型
    """
    name = models.CharField(
        max_length=100,
        verbose_name='平面图名称'
    )
    building = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='所属建筑'
    )
    floor = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='楼层'
    )
    image_path = models.CharField(
        max_length=500,
        verbose_name='图片路径'
    )
    image_width = models.IntegerField(
        default=0,
        verbose_name='图片宽度'
    )
    image_height = models.IntegerField(
        default=0,
        verbose_name='图片高度'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    class Meta:
        db_table = 'lims_floor_plan'
        verbose_name = '平面图'
        verbose_name_plural = '平面图列表'
    
    def __str__(self):
        return self.name


class FloorPlanNode(BaseModel):
    """
    平面图节点模型
    
    存储平面图上的可点击区域信息
    """
    floor_plan = models.ForeignKey(
        FloorPlan,
        on_delete=models.CASCADE,
        related_name='nodes',
        verbose_name='平面图'
    )
    laboratory = models.ForeignKey(
        'equipment.Laboratory',
        on_delete=models.CASCADE,
        related_name='floor_nodes',
        verbose_name='关联试验室'
    )
    x = models.FloatField(
        verbose_name='X坐标',
        help_text='相对于图片宽度的百分比'
    )
    y = models.FloatField(
        verbose_name='Y坐标',
        help_text='相对于图片高度的百分比'
    )
    width = models.FloatField(
        default=5,
        verbose_name='宽度',
        help_text='相对于图片宽度的百分比'
    )
    height = models.FloatField(
        default=5,
        verbose_name='高度',
        help_text='相对于图片高度的百分比'
    )
    label = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='显示标签'
    )
    color = models.CharField(
        max_length=20,
        default='#409EFF',
        verbose_name='节点颜色'
    )
    
    class Meta:
        db_table = 'lims_floor_plan_node'
        verbose_name = '平面图节点'
        verbose_name_plural = '平面图节点列表'
    
    def __str__(self):
        return f"{self.floor_plan.name} - {self.laboratory.name}"
