"""数据汇总模型"""

from django.db import models
from common.models import BaseModel


class StatisticsReport(BaseModel):
    """
    统计报表模型
    
    存储生成的周报、月报等
    """
    
    TYPE_CHOICES = [
        ('daily', '日报'),
        ('weekly', '周报'),
        ('monthly', '月报'),
        ('quarterly', '季报'),
        ('yearly', '年报'),
        ('custom', '自定义'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='报表名称'
    )
    report_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='monthly',
        verbose_name='报表类型'
    )
    start_date = models.DateField(
        verbose_name='统计开始日期'
    )
    end_date = models.DateField(
        verbose_name='统计结束日期'
    )
    statistics_data = models.JSONField(
        default=dict,
        verbose_name='统计数据',
        help_text='统计结果的JSON数据'
    )
    file_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='导出文件路径'
    )
    
    class Meta:
        db_table = 'lims_statistics_report'
        verbose_name = '统计报表'
        verbose_name_plural = '统计报表列表'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} ~ {self.end_date})"
