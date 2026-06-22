from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LiabilityCategoryViewSet, LenderViewSet, LiabilitySnapshotViewSet

router = DefaultRouter()
router.register(r'categories', LiabilityCategoryViewSet, basename='liability-category')
router.register(r'lenders', LenderViewSet, basename='lender')
router.register(r'snapshots', LiabilitySnapshotViewSet, basename='liability-snapshot')

urlpatterns = [
    path('', include(router.urls)),
]
