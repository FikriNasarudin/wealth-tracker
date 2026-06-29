from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialGoalViewSet

router = DefaultRouter()
router.register(r'', FinancialGoalViewSet, basename='financial-goal')

urlpatterns = [
    path('', include(router.urls)),
]
