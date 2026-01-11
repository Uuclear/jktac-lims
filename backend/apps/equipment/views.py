"""设备管理视图"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from common.response import success_response, error_response
from common.permissions import RoleBasedPermission
from .models import Laboratory, Equipment, CalibrationRecord, EquipmentUsageLog
from .serializers import (
    LaboratorySerializer, EquipmentListSerializer, EquipmentDetailSerializer,
    CalibrationRecordSerializer, EquipmentUsageLogSerializer
)


class LaboratoryViewSet(viewsets.ModelViewSet):
    """试验室视图集"""
    queryset = Laboratory.objects.filter(is_deleted=False)
    serializer_class = LaboratorySerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['is_active', 'responsible_person']
    search_fields = ['name', 'room_number']
    ordering_fields = ['room_number', 'name']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EquipmentViewSet(viewsets.ModelViewSet):
    """设备视图集"""
    queryset = Equipment.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['laboratory', 'status', 'custodian']
    search_fields = ['name', 'code', 'model']
    ordering_fields = ['code', 'name', 'created_at']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EquipmentListSerializer
        return EquipmentDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def need_calibration(self, request):
        """获取需要校准的设备"""
        today = timezone.now().date()
        from django.db.models import Max
        
        equipments = Equipment.objects.filter(
            is_deleted=False, status='normal'
        ).annotate(
            latest_valid_until=Max('calibrations__valid_until')
        ).filter(
            latest_valid_until__lte=today
        )
        
        return success_response(EquipmentListSerializer(equipments, many=True).data)


class CalibrationRecordViewSet(viewsets.ModelViewSet):
    """校准记录视图集"""
    queryset = CalibrationRecord.objects.filter(is_deleted=False)
    serializer_class = CalibrationRecordSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['equipment', 'result']
    ordering_fields = ['calibration_date', 'valid_until']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin'],
        'update': ['admin'],
        'destroy': ['admin'],
    }
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EquipmentUsageLogViewSet(viewsets.ModelViewSet):
    """设备使用记录视图集"""
    queryset = EquipmentUsageLog.objects.filter(is_deleted=False)
    serializer_class = EquipmentUsageLogSerializer
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    filterset_fields = ['equipment', 'user']
    ordering_fields = ['start_time']
    
    role_permissions = {
        'list': ['admin', 'tester', 'reviewer', 'approver'],
        'retrieve': ['admin', 'tester', 'reviewer', 'approver'],
        'create': ['admin', 'tester'],
        'update': ['admin', 'tester'],
    }
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, created_by=self.request.user)
