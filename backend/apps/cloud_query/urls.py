from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QueryApplicationViewSet, QueryLogViewSet, CloudDataView

router = DefaultRouter()
router.register('applications', QueryApplicationViewSet, basename='query-application')
router.register('logs', QueryLogViewSet, basename='query-log')
router.register('data', CloudDataView, basename='cloud-data')

urlpatterns = [path('', include(router.urls))]
