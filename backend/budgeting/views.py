from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from decimal import Decimal
from django.db.models.query_utils import Q
from .models import TransactionCategory, Transaction, BudgetTarget, Subscription
from .serializers import TransactionCategorySerializer, TransactionSerializer, BudgetTargetSerializer, SubscriptionSerializer

class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BudgetTargetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetTargetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BudgetTarget.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        qs = self.get_queryset()
        if month and year:
            qs = qs.filter(date__month=month, date__year=year)
            
        income = qs.filter(category__type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        expenses = qs.filter(category__type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        
        # Aggregate income and expenses by category
        expenses_qs = qs.filter(category__type='EXPENSE').values(
            'category_id',
            name=F('category__name')
        ).annotate(total=Sum('amount'))
        
        income_qs = qs.filter(category__type='INCOME').values(
            'category_id',
            name=F('category__name')
        ).annotate(total=Sum('amount'))
        
        targets_qs = BudgetTarget.objects.filter(user=request.user).select_related('category')
        targets = {t.category_id: t.amount for t in targets_qs}
        
        forecast_income = sum(t.amount for t in targets_qs if t.category.type == 'INCOME')
        forecast_expenses = sum(t.amount for t in targets_qs if t.category.type == 'EXPENSE')

        expense_breakdown = []
        for e in expenses_qs:
            weight = (e['total'] / expenses * 100) if expenses > 0 else 0
            expense_breakdown.append({
                'category_id': e['category_id'],
                'category': e['name'],
                'amount': e['total'],
                'weight_percentage': round(weight, 2),
                'budget_limit': targets.get(e['category_id'])
            })
            
        income_breakdown = []
        for inc in income_qs:
            weight = (inc['total'] / income * 100) if income > 0 else 0
            income_breakdown.append({
                'category_id': inc['category_id'],
                'category': inc['name'],
                'amount': inc['total'],
                'weight_percentage': round(weight, 2),
                'budget_limit': targets.get(inc['category_id'])
            })
            
        recent_transactions = TransactionSerializer(
            qs.order_by('-date', '-id')[:5], many=True
        ).data

        subs = Subscription.objects.filter(user=request.user, is_active=True)
        total_monthly_subs = sum((s.amount for s in subs if s.billing_cycle == 'MONTHLY'), Decimal('0.00'))
        total_yearly_subs = sum((s.amount for s in subs if s.billing_cycle == 'YEARLY'), Decimal('0.00'))
        monthly_fixed_costs = total_monthly_subs + (total_yearly_subs / Decimal('12.0'))

        return Response({
            'total_income': income,
            'total_expenses': expenses,
            'forecast_income': forecast_income,
            'forecast_expenses': forecast_expenses,
            'monthly_fixed_costs': monthly_fixed_costs,
            'net_cash_flow': income - expenses,
            'expense_breakdown': expense_breakdown,
            'income_breakdown': income_breakdown,
            'recent_transactions': recent_transactions
        })

    @action(detail=False, methods=['get'])
    def trend(self, request):
        import datetime
        import calendar
        
        end_date = datetime.date.today()
        start_date = end_date.replace(day=1)
        for _ in range(5):
            start_date = (start_date - datetime.timedelta(days=1)).replace(day=1)

        qs = self.get_queryset().filter(date__gte=start_date)
        
        trend_data = {}
        curr = start_date
        for _ in range(6):
            key = curr.strftime('%b %Y')
            trend_data[key] = {'income': 0, 'expense': 0, 'label': key}
            days_in_month = calendar.monthrange(curr.year, curr.month)[1]
            curr += datetime.timedelta(days=days_in_month)

        for txn in qs:
            key = txn.date.strftime('%b %Y')
            if key in trend_data:
                if txn.category and txn.category.type == 'INCOME':
                    trend_data[key]['income'] += txn.amount
                elif txn.category and txn.category.type == 'EXPENSE':
                    trend_data[key]['expense'] += txn.amount

        return Response(list(trend_data.values()))
