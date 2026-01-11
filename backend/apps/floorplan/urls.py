from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FloorPlanViewSet, FloorPlanNodeViewSet

router = DefaultRouter()
router.register('nodes', FloorPlanNodeViewSet, basename='floor-plan-node')
router.register('', FloorPlanViewSet, basename='floor-plan')

urlpatterns = [path('', include(router.urls))]
