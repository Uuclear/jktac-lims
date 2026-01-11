"""平面图视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from common.response import success_response
from common.permissions import RoleBasedPermission
from .models import FloorPlan, FloorPlanNode
from .serializers import FloorPlanSerializer, FloorPlanNodeSerializer


class FloorPlanViewSet(viewsets.ModelViewSet):
    """平面图视图集"""
    queryset = FloorPlan.objects.filter(is_deleted=False)
    serializer_class = FloorPlanSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['building', 'is_active']
    search_fields = ['name', 'building']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def with_equipment(self, request, pk=None):
        """获取平面图及其节点关联的设备信息"""
        floor_plan = self.get_object()
        data = FloorPlanSerializer(floor_plan).data
        
        # 为每个节点添加设备信息
        for node in data.get('nodes', []):
            from apps.equipment.models import Equipment
            from apps.equipment.serializers import EquipmentListSerializer
            equipments = Equipment.objects.filter(
                laboratory_id=node['laboratory'],
                is_deleted=False
            )
            node['equipments'] = EquipmentListSerializer(equipments, many=True).data
        
        return success_response(data)


class FloorPlanNodeViewSet(viewsets.ModelViewSet):
    """平面图节点视图集"""
    queryset = FloorPlanNode.objects.filter(is_deleted=False)
    serializer_class = FloorPlanNodeSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['floor_plan', 'laboratory']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
