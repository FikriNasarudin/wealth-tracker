from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankAccountViewSet, BankAccountSnapshotViewSet, AccountTypeViewSet

router = DefaultRouter()
router.register(r'accounts', BankAccountViewSet, basename='bank-account')
router.register(r'snapshots', BankAccountSnapshotViewSet, basename='bank-snapshot')
router.register(r'account-types', AccountTypeViewSet, basename='account-type')

urlpatterns = [
    path('', include(router.urls)),
]
