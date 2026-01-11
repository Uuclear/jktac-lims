"""
委托收样模块视图

提供委托方、委托单、收样记录的API接口
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission, DataPermission
from .models import Client, Commission, SampleReceive
from .serializers import (
    ClientSerializer,
    CommissionListSerializer, CommissionDetailSerializer, CommissionCreateSerializer,
    SampleReceiveSerializer, SampleReceiveCreateSerializer
)


class ClientViewSet(viewsets.ModelViewSet):
    """
    委托方管理视图集
    
    接口列表：
    - GET /clients/ - 获取委托方列表
    - POST /clients/ - 创建委托方
    - GET /clients/{id}/ - 获取委托方详情
    - PUT /clients/{id}/ - 更新委托方
    - DELETE /clients/{id}/ - 删除委托方
    
    权限：
    - 管理员可管理所有委托方
    - 委托方用户只能查看自己的信息
    """
    queryset = Client.objects.filter(is_deleted=False)
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['credit_level']
    search_fields = ['name', 'code', 'contact_person', 'contact_phone']
    ordering_fields = ['name', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'receiver', 'tester', 'reviewer', 'approver', 'client'],
        'create': ['admin'],
        'update': ['admin'],
        'partial_update': ['admin'],
        'destroy': ['admin'],
    }
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'client':
            return Client.objects.filter(user=user, is_deleted=False)
        return Client.objects.filter(is_deleted=False)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CommissionViewSet(viewsets.ModelViewSet):
    """
    委托单管理视图集
    
    接口列表：
    - GET /commissions/ - 获取委托单列表
    - POST /commissions/ - 创建委托单
    - GET /commissions/{id}/ - 获取委托单详情
    - PUT /commissions/{id}/ - 更新委托单
    - DELETE /commissions/{id}/ - 删除委托单
    - POST /commissions/{id}/submit/ - 提交委托单
    - POST /commissions/{id}/cancel/ - 取消委托单
    
    权限：
    - 委托方只能查看和管理自己的委托单
    - 收样人员可以查看所有委托单
    - 管理员可以管理所有委托单
    """
    queryset = Commission.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['client', 'status']
    search_fields = ['code', 'project_name', 'sample_name']
    ordering_fields = ['commission_date', 'created_at', 'status']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin', 'client'],
        'update': ['admin', 'client'],
        'partial_update': ['admin', 'client'],
        'destroy': ['admin'],
        'submit': ['admin', 'client'],
        'cancel': ['admin', 'client'],
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CommissionListSerializer
        elif self.action == 'create':
            return CommissionCreateSerializer
        return CommissionDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Commission.objects.filter(is_deleted=False)
        
        if user.role == 'client':
            # 委托方只能看自己的委托单
            return queryset.filter(client__user=user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        提交委托单
        
        将委托单状态从草稿改为已提交
        """
        commission = self.get_object()
        
        if commission.status != 'draft':
            return error_response('只有草稿状态的委托单可以提交')
        
        commission.status = 'submitted'
        commission.save(update_fields=['status', 'updated_at'])
        
        return success_response(
            CommissionDetailSerializer(commission).data,
            '委托单提交成功'
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        取消委托单
        """
        commission = self.get_object()
        
        if commission.status in ['completed', 'cancelled']:
            return error_response('已完成或已取消的委托单无法再次取消')
        
        commission.status = 'cancelled'
        commission.save(update_fields=['status', 'updated_at'])
        
        return success_response(message='委托单已取消')


class SampleReceiveViewSet(viewsets.ModelViewSet):
    """
    收样记录视图集
    
    接口列表：
    - GET /receives/ - 获取收样记录列表
    - POST /receives/ - 创建收样记录
    - GET /receives/{id}/ - 获取收样记录详情
    
    权限：
    - 收样人员可以创建和查看收样记录
    - 委托方可以查看自己的收样记录
    """
    queryset = SampleReceive.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['commission', 'receiver', 'sample_condition']
    search_fields = ['receive_code', 'commission__code']
    ordering_fields = ['receive_time', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin', 'receiver'],
        'update': ['admin', 'receiver'],
        'partial_update': ['admin', 'receiver'],
        'destroy': ['admin'],
    }
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SampleReceiveCreateSerializer
        return SampleReceiveSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = SampleReceive.objects.filter(is_deleted=False)
        
        if user.role == 'client':
            return queryset.filter(commission__client__user=user)
        
        return queryset
    
    def perform_create(self, serializer):
        receive = serializer.save(
            receiver=self.request.user,
            created_by=self.request.user
        )
        # 更新委托单状态为已收样
        commission = receive.commission
        if commission.status == 'submitted':
            commission.status = 'received'
            commission.save(update_fields=['status', 'updated_at'])
