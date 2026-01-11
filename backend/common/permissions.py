"""
自定义权限控制

提供基于角色和数据的权限控制机制
"""

from rest_framework import permissions
from functools import wraps


class IsAdminUser(permissions.BasePermission):
    """
    系统管理员权限
    
    只有系统管理员角色可以访问
    """
    message = "需要系统管理员权限"
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsLabStaff(permissions.BasePermission):
    """
    试验室工作人员权限
    
    试验人员、收样人员、审核人员、批准人员可以访问
    """
    message = "需要试验室工作人员权限"
    
    ALLOWED_ROLES = ['tester', 'receiver', 'reviewer', 'approver', 'admin']
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in self.ALLOWED_ROLES
        )


class IsClient(permissions.BasePermission):
    """
    委托方权限
    
    委托方人员可以访问
    """
    message = "需要委托方权限"
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'client'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    数据所有者或管理员权限
    
    只有数据创建者或管理员可以修改数据
    需要视图中定义 owner_field 属性指定所有者字段名
    """
    message = "只有数据所有者或管理员可以操作"
    
    def has_object_permission(self, request, view, obj):
        # 管理员拥有所有权限
        if request.user.role == 'admin':
            return True
        
        # 获取所有者字段名，默认为 'created_by'
        owner_field = getattr(view, 'owner_field', 'created_by')
        
        # 检查是否为所有者
        owner = getattr(obj, owner_field, None)
        if owner:
            return owner == request.user
        
        return False


class RoleBasedPermission(permissions.BasePermission):
    """
    基于角色的权限控制
    
    在视图中定义 role_permissions 字典来配置不同操作所需的角色：
    
    class SampleViewSet(viewsets.ModelViewSet):
        role_permissions = {
            'list': ['admin', 'tester', 'client'],
            'create': ['admin', 'receiver'],
            'update': ['admin', 'tester'],
            'destroy': ['admin'],
        }
    """
    message = "无权执行此操作"
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 获取视图中定义的角色权限配置
        role_permissions = getattr(view, 'role_permissions', {})
        
        # 获取当前操作
        action = getattr(view, 'action', None)
        if not action:
            return True
        
        # 获取当前操作所需的角色列表
        allowed_roles = role_permissions.get(action, [])
        
        # 如果没有配置，默认允许访问
        if not allowed_roles:
            return True
        
        # 检查用户角色是否在允许列表中
        return request.user.role in allowed_roles


class DataPermission(permissions.BasePermission):
    """
    数据权限控制
    
    根据用户角色限制可查看的数据范围：
    - admin: 可查看所有数据
    - client: 只能查看自己创建的委托单
    - tester: 只能查看分配给自己的试验任务
    
    需要在视图中实现 get_queryset_for_user 方法
    """
    message = "无权访问此数据"
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # 管理员拥有所有权限
        if user.role == 'admin':
            return True
        
        # 检查视图是否实现了自定义权限检查方法
        if hasattr(view, 'check_object_permission'):
            return view.check_object_permission(request, obj)
        
        # 默认检查是否为创建者
        if hasattr(obj, 'created_by'):
            return obj.created_by == user
        
        return False


def require_roles(*roles):
    """
    装饰器：要求用户具有指定角色之一
    
    用法：
        @require_roles('admin', 'tester')
        def my_view(request):
            ...
    
    Args:
        *roles: 允许的角色列表
        
    Returns:
        装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from rest_framework.response import Response
                return Response({'code': 401, 'message': '请先登录'}, status=401)
            
            if request.user.role not in roles:
                from rest_framework.response import Response
                return Response({'code': 403, 'message': '权限不足'}, status=403)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
