from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet, BankAccountSnapshotViewSet

router = DefaultRouter()
router.register(r'accounts', BankAccountViewSet, basename='bank-account')
router.register(r'snapshots', BankAccountSnapshotViewSet, basename='bank-snapshot')

urlpatterns = [
    path('', include(router.urls)),
]
