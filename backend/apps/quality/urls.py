from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentCategoryViewSet, QualityDocumentViewSet, DocumentVersionViewSet

router = DefaultRouter()
router.register('categories', DocumentCategoryViewSet, basename='document-category')
router.register('documents', QualityDocumentViewSet, basename='quality-document')
router.register('versions', DocumentVersionViewSet, basename='document-version')

urlpatterns = [path('', include(router.urls))]
