from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionCategoryViewSet, TransactionViewSet, BudgetTargetViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register(r'categories', TransactionCategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'targets', BudgetTargetViewSet, basename='target')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
