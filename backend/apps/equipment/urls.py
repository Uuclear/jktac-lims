from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LaboratoryViewSet, EquipmentViewSet, CalibrationRecordViewSet, EquipmentUsageLogViewSet

router = DefaultRouter()
router.register('laboratories', LaboratoryViewSet, basename='laboratory')
router.register('calibrations', CalibrationRecordViewSet, basename='calibration')
router.register('usage-logs', EquipmentUsageLogViewSet, basename='usage-log')
router.register('', EquipmentViewSet, basename='equipment')

urlpatterns = [path('', include(router.urls))]
