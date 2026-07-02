from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from decimal import Decimal
from collections import defaultdict
from .models import InvestmentCategory, InvestmentPlatform, InvestmentSnapshot, Asset, InvestmentSnapshotAsset
from .serializers import (
    InvestmentCategorySerializer, 
    InvestmentPlatformSerializer, 
    InvestmentSnapshotSerializer,
    AssetSerializer
)

class AssetViewSet(viewsets.ModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Asset.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs.select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = InvestmentCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentPlatformViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentPlatformSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = InvestmentPlatform.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class InvestmentSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = InvestmentSnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = InvestmentSnapshot.objects.filter(user=self.request.user).select_related('category', 'platform')
        platform_id = self.request.query_params.get('platform_id')
        if platform_id:
            qs = qs.filter(platform_id=platform_id)
        return qs.prefetch_related('snapshot_assets__asset__category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'])
    def allocation(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not (month and year):
            return Response({'error': 'month and year are required'}, status=400)
            
        qs = self.get_queryset().filter(month=month, year=year)
        
        total_portfolio = qs.aggregate(total=Sum('current_balance'))['total'] or Decimal('0.00')
        total_invested = qs.aggregate(total=Sum('total_invested'))['total'] or Decimal('0.00')
        
        # Calculate dynamic Category allocation based on Snapshot Assets and falling back to direct Snapshot Categories
        category_allocations = defaultdict(Decimal)
        platform_allocations = defaultdict(Decimal)
        
        for snap in qs:
            snap_assets = snap.snapshot_assets.all()
            snap_balance = Decimal(str(snap.current_balance))
            
            # Map platform
            plat_name = snap.platform.name if snap.platform else 'Unknown Platform'
            platform_allocations[plat_name] += snap_balance
            
            if snap_assets.exists():
                # Process weighted allocations
                for snap_asset in snap_assets:
                    # Calculate asset's share of value
                    asset_val = Decimal(str(snap_asset.value or 0))
                    cat_name = snap_asset.asset.category.name if snap_asset.asset.category else 'Uncategorized'
                    category_allocations[cat_name] += asset_val
            else:
                # Fallback to the direct category of the snapshot
                cat_name = 'Uncategorized'
                if snap.category:
                    cat_name = snap.category.name
                category_allocations[cat_name] += snap_balance

        # Format allocation response list
        by_category = []
        for cat_name, bal in category_allocations.items():
            weight = (bal / total_portfolio * 100) if total_portfolio > 0 else Decimal('0.00')
            by_category.append({
                'category': cat_name, 
                'balance': float(bal), 
                'weight_percentage': round(float(weight), 2)
            })
            
        by_platform = []
        for plat_name, bal in platform_allocations.items():
            weight = (bal / total_portfolio * 100) if total_portfolio > 0 else Decimal('0.00')
            by_platform.append({
                'platform': plat_name, 
                'balance': float(bal), 
                'weight_percentage': round(float(weight), 2)
            })
            
        prev_month = int(month) - 1
        prev_year = int(year)
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
            
        prev_qs = self.get_queryset().filter(month=prev_month, year=prev_year)
        prev_total_portfolio = prev_qs.aggregate(total=Sum('current_balance'))['total'] or Decimal('0.00')
        prev_total_invested = prev_qs.aggregate(total=Sum('total_invested'))['total'] or Decimal('0.00')
        prev_absolute_profit = prev_total_portfolio - prev_total_invested
        prev_profit_percentage = round((prev_absolute_profit / prev_total_invested) * 100, 2) if prev_total_invested > 0 else Decimal('0.00')

        return Response({
            'total_invested': float(total_invested),
            'total_portfolio_balance': float(total_portfolio),
            'total_absolute_profit': float(total_portfolio - total_invested),
            'total_profit_percentage': round(float((total_portfolio - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0.00,
            'prev_total_invested': float(prev_total_invested),
            'prev_total_portfolio_balance': float(prev_total_portfolio),
            'prev_total_absolute_profit': float(prev_absolute_profit),
            'prev_total_profit_percentage': float(prev_profit_percentage),
            'allocation_by_category': by_category,
            'allocation_by_platform': by_platform
        })
