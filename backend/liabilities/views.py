from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from .models import LiabilityCategory, Lender, LiabilitySnapshot
from .serializers import LiabilityCategorySerializer, LenderSerializer, LiabilitySnapshotSerializer

class LiabilityCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = LiabilityCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LiabilityCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LenderViewSet(viewsets.ModelViewSet):
    serializer_class = LenderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Lender.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LiabilitySnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = LiabilitySnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LiabilitySnapshot.objects.filter(user=self.request.user).select_related('category', 'lender')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not (month and year):
            return Response({'error': 'month and year are required'}, status=400)
            
        qs = self.get_queryset().filter(month=month, year=year)
        
        total_remaining = qs.aggregate(total=Sum('remaining_principal'))['total'] or 0
        total_original = qs.aggregate(total=Sum('original_loan_amount'))['total'] or 0
        total_monthly = qs.aggregate(total=Sum('monthly_payment'))['total'] or 0
        
        # By Category
        cat_qs = qs.values(name=F('category__name')).annotate(total=Sum('remaining_principal'))
        by_category = []
        for c in cat_qs:
            weight = (c['total'] / total_remaining * 100) if total_remaining > 0 else 0
            by_category.append({'category': c['name'], 'balance': c['total'], 'weight_percentage': round(weight, 2)})
            
        return Response({
            'total_remaining_principal': total_remaining,
            'total_original_loan_amount': total_original,
            'total_monthly_payment': total_monthly,
            'total_debt_reduced': total_original - total_remaining,
            'distribution_by_category': by_category,
        })
