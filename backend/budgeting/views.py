from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from .models import TransactionCategory, Transaction
from .serializers import TransactionCategorySerializer, TransactionSerializer

class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))

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
        
        # Expenses weight by category
        expenses_qs = qs.filter(category__type='EXPENSE').values(
            name=F('category__name')
        ).annotate(total=Sum('amount'))
        
        expense_breakdown = []
        for e in expenses_qs:
            weight = (e['total'] / expenses * 100) if expenses > 0 else 0
            expense_breakdown.append({
                'category': e['name'],
                'amount': e['total'],
                'weight_percentage': round(weight, 2)
            })
            
        return Response({
            'total_income': income,
            'total_expenses': expenses,
            'net_cash_flow': income - expenses,
            'expense_breakdown': expense_breakdown
        })
