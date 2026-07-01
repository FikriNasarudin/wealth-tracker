from rest_framework import viewsets, permissions
from .models import FinancialGoal
from .serializers import FinancialGoalSerializer

class FinancialGoalViewSet(viewsets.ModelViewSet):
    serializer_class = FinancialGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = FinancialGoal.objects.filter(user=self.request.user)
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() in ['true', '1']
            qs = qs.filter(is_active=is_active)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
