from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TestStandardViewSet, TestParameterViewSet, ParameterPriceViewSet

router = DefaultRouter()
router.register('standards', TestStandardViewSet, basename='test-standard')
router.register('parameters', TestParameterViewSet, basename='test-parameter')
router.register('prices', ParameterPriceViewSet, basename='parameter-price')

urlpatterns = [path('', include(router.urls))]
