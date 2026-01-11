from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VerifyRecordViewSet, VerifyRuleViewSet, VerifyView

router = DefaultRouter()
router.register('records', VerifyRecordViewSet, basename='verify-record')
router.register('rules', VerifyRuleViewSet, basename='verify-rule')

urlpatterns = [
    path('', include(router.urls)),
    path('verify/', VerifyView.as_view(), name='verify'),
]
