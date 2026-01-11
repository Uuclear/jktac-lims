"""
用户模块序列化器

定义API数据的序列化和反序列化规则
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Department, UserLoginLog


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    
    用于用户信息的展示，不包含敏感信息
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'role', 'role_display',
            'department', 'department_name',
            'avatar', 'employee_id', 'position',
            'first_name', 'last_name',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    
    用于注册新用户，包含密码验证
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text='密码，至少8位'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        help_text='确认密码'
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'password', 'password_confirm',
            'role', 'department', 'first_name', 'last_name',
            'employee_id', 'position'
        ]
    
    def validate(self, attrs):
        """验证两次密码是否一致"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({'password_confirm': '两次密码不一致'})
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户更新序列化器
    
    用于更新用户信息，不允许修改用户名和密码
    """
    class Meta:
        model = User
        fields = [
            'email', 'phone', 'role', 'department',
            'avatar', 'employee_id', 'position',
            'first_name', 'last_name', 'is_active'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """
    old_password = serializers.CharField(required=True, help_text='原密码')
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        help_text='新密码'
    )
    new_password_confirm = serializers.CharField(required=True, help_text='确认新密码')
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': '两次密码不一致'})
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('原密码错误')
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    密码重置序列化器（管理员重置）
    """
    user_id = serializers.IntegerField(required=True, help_text='用户ID')
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        help_text='新密码'
    )


class LoginSerializer(serializers.Serializer):
    """
    登录序列化器
    """
    username = serializers.CharField(required=True, help_text='用户名')
    password = serializers.CharField(required=True, help_text='密码')


class DepartmentSerializer(serializers.ModelSerializer):
    """
    部门序列化器
    """
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = [
            'id', 'name', 'code', 'parent', 'parent_name',
            'description', 'sort_order', 'is_active',
            'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """获取子部门列表"""
        children = obj.children.filter(is_active=True)
        return DepartmentSerializer(children, many=True).data if children.exists() else []


class UserLoginLogSerializer(serializers.ModelSerializer):
    """
    登录日志序列化器
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserLoginLog
        fields = [
            'id', 'user', 'username', 'ip_address',
            'user_agent', 'login_time', 'status', 'failure_reason'
        ]
        read_only_fields = ['id', 'login_time']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户个人信息序列化器
    
    用于用户查看和更新自己的信息
    """
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone',
            'role', 'role_display',
            'department', 'department_name',
            'avatar', 'first_name', 'last_name',
            'employee_id', 'position',
            'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'role', 'department',
            'date_joined', 'last_login'
        ]
