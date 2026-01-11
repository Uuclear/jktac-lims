from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StatisticsReportViewSet, StatisticsView, DashboardView, ExportView

router = DefaultRouter()
router.register('saved', StatisticsReportViewSet, basename='statistics-report')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/', StatisticsView.as_view(), name='statistics'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('export/', ExportView.as_view(), name='export'),
]
