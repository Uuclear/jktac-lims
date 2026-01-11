"""
用户模块视图

提供用户管理相关的API接口
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from common.response import success_response, error_response, created_response
from common.permissions import IsAdminUser, RoleBasedPermission
from .models import User, Department, UserLoginLog
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, LoginSerializer,
    DepartmentSerializer, UserLoginLogSerializer, UserProfileSerializer
)


class AuthViewSet(viewsets.ViewSet):
    """
    认证视图集
    
    提供登录、登出、Token刷新等接口
    
    接口列表：
    - POST /login/ - 用户登录
    - POST /logout/ - 用户登出
    - POST /register/ - 用户注册（如开放注册）
    
    扩展点：
    - 可添加第三方登录接口（微信、钉钉等）
    - 可添加短信验证码登录
    - 可添加多因素认证
    """
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        
        请求参数：
        - username: 用户名
        - password: 密码
        
        返回：
        - access: JWT访问令牌
        - refresh: JWT刷新令牌
        - user: 用户信息
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # 认证用户
        user = authenticate(username=username, password=password)
        
        # 获取客户端IP
        ip_address = self._get_client_ip(request)
        
        if user is None:
            # 记录失败日志
            try:
                user_obj = User.objects.get(username=username)
                UserLoginLog.objects.create(
                    user=user_obj,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    status='failed',
                    failure_reason='密码错误'
                )
            except User.DoesNotExist:
                pass
            return error_response('用户名或密码错误', code=401)
        
        if not user.is_active:
            return error_response('账户已被禁用', code=403)
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        
        # 记录成功日志
        UserLoginLog.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status='success'
        )
        
        return success_response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        }, '登录成功')
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        用户登出
        
        将refresh token加入黑名单
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return success_response(message='登出成功')
        except Exception:
            return success_response(message='登出成功')
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """
        用户注册
        
        注意：生产环境可能需要关闭此接口，由管理员创建用户
        """
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        user = serializer.save()
        return created_response(
            UserSerializer(user).data,
            '注册成功'
        )
    
    def _get_client_ip(self, request):
        """获取客户端真实IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集
    
    提供用户的CRUD操作
    
    接口列表：
    - GET /users/ - 获取用户列表
    - POST /users/ - 创建用户
    - GET /users/{id}/ - 获取用户详情
    - PUT /users/{id}/ - 更新用户
    - DELETE /users/{id}/ - 删除用户
    - GET /users/me/ - 获取当前用户信息
    - POST /users/{id}/change_password/ - 修改密码
    - POST /users/{id}/reset_password/ - 重置密码（管理员）
    
    权限配置：
    - list/retrieve: 管理员可查看所有，其他用户只能查看自己
    - create/update/destroy: 仅管理员
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['role', 'department', 'is_active']
    search_fields = ['username', 'email', 'phone', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'last_login', 'username']
    
    # 角色权限配置
    role_permissions = {
        'list': ['admin'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'partial_update': ['admin'],
        'destroy': ['admin'],
    }
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        根据用户角色过滤查询集
        
        管理员可查看所有用户，其他用户只能查看自己
        """
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        获取/更新当前用户信息
        """
        user = request.user
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(user)
            return success_response(serializer.data)
        
        # 更新个人信息
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return success_response(serializer.data, '更新成功')
        return error_response(serializer.errors)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改当前用户密码
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return success_response(message='密码修改成功')
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reset_password(self, request, pk=None):
        """
        重置用户密码（管理员专用）
        """
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return error_response('用户不存在', code=404)
        
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors)
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return success_response(message='密码重置成功')


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    部门管理视图集
    
    接口列表：
    - GET /departments/ - 获取部门列表
    - POST /departments/ - 创建部门
    - GET /departments/{id}/ - 获取部门详情
    - PUT /departments/{id}/ - 更新部门
    - DELETE /departments/{id}/ - 删除部门
    - GET /departments/tree/ - 获取部门树形结构
    """
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['parent', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['sort_order', 'name', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'partial_update': ['admin'],
        'destroy': ['admin'],
    }
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        获取部门树形结构
        """
        # 获取顶级部门
        root_departments = Department.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('sort_order')
        
        serializer = DepartmentSerializer(root_departments, many=True)
        return success_response(serializer.data)


class UserLoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    登录日志视图集
    
    只读，仅管理员可访问
    """
    queryset = UserLoginLog.objects.all()
    serializer_class = UserLoginLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['user', 'status']
    search_fields = ['user__username', 'ip_address']
    ordering_fields = ['login_time']
