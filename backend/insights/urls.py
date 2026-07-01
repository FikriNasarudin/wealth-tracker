from django.urls import path
from . import views

urlpatterns = [
    path('<str:dashboard_type>/', views.get_insights, name='get_insights'),
]
