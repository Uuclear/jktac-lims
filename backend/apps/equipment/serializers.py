"""设备管理序列化器"""
from rest_framework import serializers
from .models import Laboratory, Equipment, CalibrationRecord, EquipmentUsageLog


class LaboratorySerializer(serializers.ModelSerializer):
    responsible_person_name = serializers.CharField(source='responsible_person.username', read_only=True)
    equipment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Laboratory
        fields = [
            'id', 'name', 'room_number', 'location', 'area',
            'temperature_range', 'humidity_range', 'responsible_person',
            'responsible_person_name', 'is_active', 'remarks',
            'equipment_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_equipment_count(self, obj):
        return obj.equipments.filter(is_deleted=False).count()


class EquipmentListSerializer(serializers.ModelSerializer):
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'code', 'model', 'laboratory', 'laboratory_name',
            'status', 'status_display', 'custodian', 'created_at'
        ]


class EquipmentDetailSerializer(serializers.ModelSerializer):
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    custodian_name = serializers.CharField(source='custodian.username', read_only=True)
    latest_calibration = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'code', 'model', 'manufacturer', 'serial_number',
            'laboratory', 'laboratory_name', 'purchase_date', 'commissioning_date',
            'status', 'status_display', 'accuracy', 'measurement_range',
            'custodian', 'custodian_name', 'photo', 'remarks',
            'latest_calibration', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_latest_calibration(self, obj):
        calibration = obj.calibrations.order_by('-calibration_date').first()
        if calibration:
            return {
                'calibration_date': calibration.calibration_date,
                'valid_until': calibration.valid_until,
                'result': calibration.result
            }
        return None


class CalibrationRecordSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    result_display = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = CalibrationRecord
        fields = [
            'id', 'equipment', 'equipment_name', 'equipment_code',
            'calibration_date', 'valid_until', 'calibration_org',
            'certificate_number', 'certificate_path', 'result', 'result_display',
            'calibration_data', 'cost', 'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EquipmentUsageLogSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = EquipmentUsageLog
        fields = [
            'id', 'equipment', 'equipment_name', 'equipment_code',
            'user', 'user_name', 'start_time', 'end_time',
            'purpose', 'sample_info', 'condition_before', 'condition_after',
            'remarks', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
