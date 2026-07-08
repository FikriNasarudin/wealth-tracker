from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LiabilityCategoryViewSet, LenderViewSet, LiabilitySnapshotViewSet, LenderItemViewSet

router = DefaultRouter()
router.register(r'categories', LiabilityCategoryViewSet, basename='liability-category')
router.register(r'lenders', LenderViewSet, basename='lender')
router.register(r'snapshots', LiabilitySnapshotViewSet, basename='liability-snapshot')
router.register(r'items', LenderItemViewSet, basename='lender-item')

urlpatterns = [
    path('', include(router.urls)),
]
