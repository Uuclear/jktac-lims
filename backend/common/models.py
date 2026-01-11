"""
基础模型类

提供所有模型共用的基础字段和方法
"""

from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    """
    基础模型抽象类
    
    所有业务模型都应继承此类，自动包含以下字段：
    - created_at: 创建时间
    - updated_at: 更新时间
    - created_by: 创建人
    - is_deleted: 软删除标记
    
    Attributes:
        created_at: 创建时间，自动填充
        updated_at: 更新时间，自动更新
        created_by: 创建人，关联用户模型
        is_deleted: 软删除标记，默认False
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='记录创建的时间戳'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='记录最后更新的时间戳'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        verbose_name='创建人',
        help_text='创建此记录的用户'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除',
        help_text='软删除标记，True表示已删除'
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """
        软删除
        
        将is_deleted标记设为True，而不是真正删除数据
        """
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        """
        恢复删除
        
        将is_deleted标记设为False
        """
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])


class SoftDeleteManager(models.Manager):
    """
    软删除管理器
    
    自动过滤掉已软删除的记录
    
    用法：
        class MyModel(BaseModel):
            objects = SoftDeleteManager()
            all_objects = models.Manager()  # 包含已删除记录
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class TimeStampedModel(models.Model):
    """
    时间戳模型抽象类
    
    只包含创建时间和更新时间，适用于不需要创建人和软删除的场景
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        abstract = True
