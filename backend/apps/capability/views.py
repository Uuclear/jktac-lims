"""试验室能力管理视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from common.response import success_response
from common.permissions import RoleBasedPermission
from .models import TestStandard, TestParameter, ParameterPrice
from .serializers import TestStandardSerializer, TestParameterSerializer, ParameterPriceSerializer


class TestStandardViewSet(viewsets.ModelViewSet):
    """检测标准视图集"""
    queryset = TestStandard.objects.filter(is_deleted=False)
    serializer_class = TestStandardSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['category', 'is_active']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """获取标准分类列表"""
        categories = TestStandard.objects.filter(
            is_deleted=False, is_active=True
        ).values_list('category', flat=True).distinct()
        return success_response(list(categories))


class TestParameterViewSet(viewsets.ModelViewSet):
    """检测参数视图集"""
    queryset = TestParameter.objects.filter(is_deleted=False)
    serializer_class = TestParameterSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['standard', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'client', 'receiver', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ParameterPriceViewSet(viewsets.ModelViewSet):
    """参数价格视图集"""
    queryset = ParameterPrice.objects.filter(is_deleted=False)
    serializer_class = ParameterPriceSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['parameter', 'price_type']
    ordering_fields = ['effective_date', 'price']
    
    role_permissions = {
        'list': ['admin', 'client', 'receiver'],
        'retrieve': ['admin', 'client', 'receiver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
