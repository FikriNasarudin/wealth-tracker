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
        qs = LiabilityCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LenderViewSet(viewsets.ModelViewSet):
    serializer_class = LenderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Lender.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LiabilitySnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = LiabilitySnapshotSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = LiabilitySnapshot.objects.filter(user=self.request.user).select_related('category', 'lender')
        lender_id = self.request.query_params.get('lender_id') or self.request.query_params.get('lender')
        if lender_id:
            qs = qs.filter(lender_id=lender_id)
        month = self.request.query_params.get('month')
        if month:
            qs = qs.filter(month=month)
        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)
        return qs

    def perform_create(self, serializer):
        lender = serializer.validated_data.get('lender')
        category = lender.category if lender else None
        
        original_loan_amount = serializer.validated_data.get('original_loan_amount')
        remaining_principal = serializer.validated_data.get('remaining_principal')
        monthly_payment = serializer.validated_data.get('monthly_payment', 0)
        month = serializer.validated_data.get('month')
        year = serializer.validated_data.get('year')

        if original_loan_amount is None:
            original_loan_amount = lender.original_loan_amount if lender else 0

        if remaining_principal is None:
            prev_snapshot = LiabilitySnapshot.objects.filter(
                user=self.request.user,
                lender=lender
            ).filter(
                Q(year__lt=year) | Q(year=year, month__lt=month)
            ).order_by('-year', '-month').first()

            if prev_snapshot:
                remaining_principal = prev_snapshot.remaining_principal - monthly_payment
            else:
                is_credit_card = category and category.name.lower() == 'credit cards'
                remaining_principal = 0 if is_credit_card else (original_loan_amount - monthly_payment)

        serializer.save(
            user=self.request.user, 
            category=category,
            original_loan_amount=original_loan_amount,
            remaining_principal=remaining_principal
        )

    def perform_update(self, serializer):
        lender = serializer.validated_data.get('lender', serializer.instance.lender)
        category = lender.category if lender else None
        
        original_loan_amount = serializer.validated_data.get('original_loan_amount')
        remaining_principal = serializer.validated_data.get('remaining_principal')
        monthly_payment = serializer.validated_data.get('monthly_payment', serializer.instance.monthly_payment)
        month = serializer.validated_data.get('month', serializer.instance.month)
        year = serializer.validated_data.get('year', serializer.instance.year)

        kwargs = {'category': category}

        if 'original_loan_amount' not in serializer.validated_data or original_loan_amount is None:
            kwargs['original_loan_amount'] = lender.original_loan_amount if lender else 0

        if 'remaining_principal' not in serializer.validated_data or remaining_principal is None:
            prev_snapshot = LiabilitySnapshot.objects.filter(
                user=self.request.user,
                lender=lender
            ).filter(
                Q(year__lt=year) | Q(year=year, month__lt=month)
            ).order_by('-year', '-month').first()

            if prev_snapshot:
                kwargs['remaining_principal'] = prev_snapshot.remaining_principal - monthly_payment
            else:
                is_credit_card = category and category.name.lower() == 'credit cards'
                kwargs['remaining_principal'] = 0 if is_credit_card else (kwargs.get('original_loan_amount', serializer.instance.original_loan_amount) - monthly_payment)

        serializer.save(**kwargs)

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
            
        prev_month = int(month) - 1
        prev_year = int(year)
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
            
        prev_qs = self.get_queryset().filter(month=prev_month, year=prev_year)
        prev_total_remaining = prev_qs.aggregate(total=Sum('remaining_principal'))['total'] or 0
        prev_total_original = prev_qs.aggregate(total=Sum('original_loan_amount'))['total'] or 0
        prev_total_debt_reduced = prev_total_original - prev_total_remaining

        return Response({
            'total_remaining_principal': total_remaining,
            'total_original_loan_amount': total_original,
            'total_monthly_payment': total_monthly,
            'total_debt_reduced': total_original - total_remaining,
            'prev_total_remaining_principal': prev_total_remaining,
            'prev_total_original_loan_amount': prev_total_original,
            'prev_total_debt_reduced': prev_total_debt_reduced,
            'distribution_by_category': by_category,
        })
