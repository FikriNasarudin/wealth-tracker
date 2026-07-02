from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentCategoryViewSet, InvestmentPlatformViewSet, InvestmentSnapshotViewSet, AssetViewSet

router = DefaultRouter()
router.register(r'categories', InvestmentCategoryViewSet, basename='investment-category')
router.register(r'platforms', InvestmentPlatformViewSet, basename='investment-platform')
router.register(r'snapshots', InvestmentSnapshotViewSet, basename='investment-snapshot')
router.register(r'assets', AssetViewSet, basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]
