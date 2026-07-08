from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from .models import LiabilityCategory, Lender, LiabilitySnapshot, LenderItem
from .serializers import LiabilityCategorySerializer, LenderSerializer, LiabilitySnapshotSerializer, LenderItemSerializer

class LiabilityCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = LiabilityCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Dynamically seed default categories if they don't exist
        defaults = ['Pay Later', 'Loan', 'Credit Card']
        for name in defaults:
            LiabilityCategory.objects.get_or_create(name=name, is_default=True, defaults={'user': None})
            
        qs = LiabilityCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))
        if self.request.query_params.get('active_only') == 'true':
            qs = qs.filter(is_active=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.is_default:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot modify default categories.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_default:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot delete default categories.")
        instance.delete()

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

    def perform_destroy(self, instance):
        if instance.items.exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Cannot delete a lender that has active items. Please delete or reassign its items first.")
        instance.delete()

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

        # check for dynamic items metrics
        if lender:
            metrics = lender.get_calculated_metrics(month, year, self.request.user)
            if metrics:
                original_loan_amount = metrics['original_loan_amount']
                remaining_principal = metrics['remaining_principal']
                if 'monthly_payment' not in serializer.validated_data:
                    monthly_payment = metrics['monthly_payment']

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
                is_credit_card = category and 'credit card' in category.name.lower()
                is_pay_later = category and ('pay later' in category.name.lower() or 'bnpl' in category.name.lower())
                remaining_principal = 0 if (is_credit_card or is_pay_later) else (original_loan_amount - monthly_payment)

        serializer.save(
            user=self.request.user, 
            category=category,
            original_loan_amount=original_loan_amount,
            remaining_principal=remaining_principal,
            monthly_payment=monthly_payment
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

        # check for dynamic items metrics
        if lender:
            metrics = lender.get_calculated_metrics(month, year, self.request.user)
            if metrics:
                kwargs['original_loan_amount'] = metrics['original_loan_amount']
                kwargs['remaining_principal'] = metrics['remaining_principal']
                if 'monthly_payment' not in serializer.validated_data:
                    kwargs['monthly_payment'] = metrics['monthly_payment']
                    monthly_payment = metrics['monthly_payment']
                else:
                    monthly_payment = serializer.validated_data['monthly_payment']
                
                # Apply these to local variables as well for the fallback check below
                original_loan_amount = metrics['original_loan_amount']
                remaining_principal = metrics['remaining_principal']

        if 'original_loan_amount' not in kwargs:
            if 'original_loan_amount' not in serializer.validated_data or original_loan_amount is None:
                kwargs['original_loan_amount'] = lender.original_loan_amount if lender else 0

        if 'remaining_principal' not in kwargs:
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
                    is_credit_card = category and 'credit card' in category.name.lower()
                    is_pay_later = category and ('pay later' in category.name.lower() or 'bnpl' in category.name.lower())
                    kwargs['remaining_principal'] = 0 if (is_credit_card or is_pay_later) else (kwargs.get('original_loan_amount', serializer.instance.original_loan_amount) - monthly_payment)

        serializer.save(**kwargs)

    def _calculate_summary_for_period(self, user, month, year):
        from decimal import Decimal
        qs = self.get_queryset().filter(month=month, year=year)
        
        total_remaining = Decimal('0')
        total_original = Decimal('0')
        total_monthly = Decimal('0')
        by_category_dict = {}
        
        # Calculate dynamic metrics for each snapshot in Python
        for snap in qs:
            lender = snap.lender
            original = snap.original_loan_amount
            remaining = snap.remaining_principal
            monthly = snap.monthly_payment
            
            if lender:
                metrics = lender.get_calculated_metrics(month, year, user)
                if metrics:
                    original = metrics['original_loan_amount']
                    remaining = metrics['remaining_principal']
                    monthly = metrics['monthly_payment']
            
            total_remaining += remaining
            total_monthly += monthly
            
            is_term = True
            if snap.category:
                cat_name_lower = snap.category.name.lower()
                if 'credit card' in cat_name_lower or 'pay later' in cat_name_lower or 'bnpl' in cat_name_lower:
                    is_term = False
                    
            if is_term:
                total_original += original
                
            cat_name = snap.category.name if snap.category else "Uncategorized"
            by_category_dict[cat_name] = by_category_dict.get(cat_name, Decimal('0')) + remaining
            
        by_category = []
        for cat_name, bal in by_category_dict.items():
            weight = (bal / total_remaining * 100) if total_remaining > 0 else 0
            by_category.append({'category': cat_name, 'balance': bal, 'weight_percentage': round(weight, 2)})
            
        # term remaining for debt reduction calculations
        term_remaining = Decimal('0')
        for snap in qs:
            lender = snap.lender
            remaining = snap.remaining_principal
            if lender:
                metrics = lender.get_calculated_metrics(month, year, user)
                if metrics:
                    remaining = metrics['remaining_principal']
            
            is_term = True
            if snap.category:
                cat_name_lower = snap.category.name.lower()
                if 'credit card' in cat_name_lower or 'pay later' in cat_name_lower or 'bnpl' in cat_name_lower:
                    is_term = False
            if is_term:
                term_remaining += remaining
                
        total_debt_reduced = total_original - term_remaining
        
        return {
            'total_remaining_principal': total_remaining,
            'total_original_loan_amount': total_original,
            'total_monthly_payment': total_monthly,
            'total_debt_reduced': total_debt_reduced,
            'distribution_by_category': by_category
        }

    @action(detail=False, methods=['get'])
    def summary(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not (month and year):
            return Response({'error': 'month and year are required'}, status=400)
            
        m = int(month)
        y = int(year)
        
        current = self._calculate_summary_for_period(request.user, m, y)
        
        prev_month = m - 1
        prev_year = y
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
            
        prev = self._calculate_summary_for_period(request.user, prev_month, prev_year)

        return Response({
            'total_remaining_principal': current['total_remaining_principal'],
            'total_original_loan_amount': current['total_original_loan_amount'],
            'total_monthly_payment': current['total_monthly_payment'],
            'total_debt_reduced': current['total_debt_reduced'],
            'prev_total_remaining_principal': prev['total_remaining_principal'],
            'prev_total_original_loan_amount': prev['total_original_loan_amount'],
            'prev_total_debt_reduced': prev['total_debt_reduced'],
            'distribution_by_category': current['distribution_by_category'],
        })

class LenderItemViewSet(viewsets.ModelViewSet):
    serializer_class = LenderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LenderItem.objects.filter(lender__user=self.request.user)

    def perform_create(self, serializer):
        lender = serializer.validated_data.get('lender')
        if lender and lender.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not own this lender.")
        serializer.save()
