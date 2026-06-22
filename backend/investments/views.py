from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from .models import InvestmentCategory, InvestmentPlatform, InvestmentSnapshot
from .serializers import InvestmentCategorySerializer, InvestmentPlatformSerializer, InvestmentSnapshotSerializer

class InvestmentCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InvestmentCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentPlatformViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentPlatformSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InvestmentPlatform.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return InvestmentSnapshot.objects.filter(user=self.request.user).select_related('category', 'platform')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def allocation(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not (month and year):
            return Response({'error': 'month and year are required'}, status=400)
            
        qs = self.get_queryset().filter(month=month, year=year)
        
        total_portfolio = qs.aggregate(total=Sum('current_balance'))['total'] or 0
        total_invested = qs.aggregate(total=Sum('total_invested'))['total'] or 0
        
        # By Category
        cat_qs = qs.values(name=F('category__name')).annotate(total=Sum('current_balance'))
        by_category = []
        for c in cat_qs:
            weight = (c['total'] / total_portfolio * 100) if total_portfolio > 0 else 0
            by_category.append({'category': c['name'], 'balance': c['total'], 'weight_percentage': round(weight, 2)})
            
        # By Platform
        plat_qs = qs.values(name=F('platform__name')).annotate(total=Sum('current_balance'))
        by_platform = []
        for p in plat_qs:
            weight = (p['total'] / total_portfolio * 100) if total_portfolio > 0 else 0
            by_platform.append({'platform': p['name'], 'balance': p['total'], 'weight_percentage': round(weight, 2)})
            
        return Response({
            'total_invested': total_invested,
            'total_portfolio_balance': total_portfolio,
            'total_absolute_profit': total_portfolio - total_invested,
            'total_profit_percentage': round(((total_portfolio - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0,
            'allocation_by_category': by_category,
            'allocation_by_platform': by_platform
        })
