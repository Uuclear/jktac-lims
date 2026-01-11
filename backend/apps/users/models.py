"""
用户权限管理数据模型

定义用户、角色、权限相关的数据表结构
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from common.models import TimeStampedModel


class User(AbstractUser):
    """
    自定义用户模型
    
    继承Django AbstractUser，扩展以下字段：
    - role: 用户角色
    - phone: 手机号
    - department: 所属部门
    - avatar: 头像URL
    
    Attributes:
        role: 用户角色，决定权限范围
        phone: 手机号，用于登录和找回密码
        department: 所属部门
        avatar: 头像文件路径
        is_active: 账户是否激活
    """
    
    # 角色选项
    ROLE_CHOICES = [
        ('admin', '系统管理员'),
        ('client', '委托方人员'),
        ('receiver', '收样人员'),
        ('tester', '试验人员'),
        ('reviewer', '报告审核人员'),
        ('approver', '报告批准人员'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='client',
        verbose_name='角色',
        help_text='用户角色，决定可访问的功能和数据范围',
        db_index=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True,
        verbose_name='手机号',
        help_text='用于登录和接收通知'
    )
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='所属部门'
    )
    avatar = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='头像',
        help_text='头像文件的存储路径'
    )
    
    # 扩展字段（预留）
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='工号'
    )
    position = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='职位'
    )
    
    class Meta:
        db_table = 'lims_user'
        verbose_name = '用户'
        verbose_name_plural = '用户列表'
        indexes = [
            models.Index(fields=['role'], name='idx_user_role'),
            models.Index(fields=['phone'], name='idx_user_phone'),
        ]
    
    def __str__(self):
        return f"{self.username}({self.get_role_display()})"
    
    @property
    def is_admin(self) -> bool:
        """是否为管理员"""
        return self.role == 'admin' or self.is_superuser
    
    @property
    def is_lab_staff(self) -> bool:
        """是否为试验室工作人员"""
        return self.role in ['receiver', 'tester', 'reviewer', 'approver', 'admin']
    
    def has_role(self, *roles) -> bool:
        """
        检查是否具有指定角色之一
        
        Args:
            *roles: 角色列表
            
        Returns:
            bool: 是否具有指定角色
        """
        return self.role in roles


class Department(TimeStampedModel):
    """
    部门模型
    
    用于组织用户的部门归属
    
    Attributes:
        name: 部门名称
        code: 部门代码
        parent: 上级部门
        description: 部门描述
    """
    name = models.CharField(
        max_length=100,
        verbose_name='部门名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='部门代码'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='上级部门'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='部门描述'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    class Meta:
        db_table = 'lims_department'
        verbose_name = '部门'
        verbose_name_plural = '部门列表'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class UserLoginLog(TimeStampedModel):
    """
    用户登录日志
    
    记录用户登录行为，用于安全审计
    
    Attributes:
        user: 登录用户
        ip_address: 登录IP
        user_agent: 浏览器信息
        login_time: 登录时间
        status: 登录状态（成功/失败）
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='用户'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP地址'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='浏览器信息'
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='登录时间'
    )
    status = models.CharField(
        max_length=20,
        choices=[('success', '成功'), ('failed', '失败')],
        default='success',
        verbose_name='登录状态'
    )
    failure_reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='失败原因'
    )
    
    class Meta:
        db_table = 'lims_user_login_log'
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志列表'
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', 'login_time'], name='idx_login_user_time'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
