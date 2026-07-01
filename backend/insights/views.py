from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import InsightCache
from .utils import generate_financial_insights
from datetime import timedelta
from django.utils import timezone
from liabilities.models import LiabilitySnapshot
from budgeting.models import Transaction, TransactionCategory, BudgetTarget
from django.db.models import Sum
from django.db.models.query_utils import Q
import json

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_insights(request, dashboard_type):
    dashboard_type = dashboard_type.upper()
    valid_types = ['MAIN', 'LIABILITIES', 'BUDGETING']
    if dashboard_type not in valid_types:
        return Response({'error': 'Invalid dashboard type'}, status=400)

    month = request.query_params.get('month')
    year = request.query_params.get('year')
    force_refresh = request.query_params.get('force', 'false').lower() == 'true'

    if not month or not year:
        return Response({'error': 'month and year are required'}, status=400)
    
    month = int(month)
    year = int(year)

    # Check cache
    if not force_refresh:
        cache = InsightCache.objects.filter(
            user=request.user,
            dashboard_type=dashboard_type,
            month=month,
            year=year
        ).first()

        # If cache is valid (less than 24 hours old)
        if cache and (timezone.now() - cache.updated_at) < timedelta(hours=24):
            return Response({
                'health_score': cache.health_score,
                'recommendations': cache.recommendations,
                'cached': True,
                'updated_at': cache.updated_at
            })

    # Gather data based on dashboard type
    context_data = {}

    if dashboard_type == 'LIABILITIES' or dashboard_type == 'MAIN':
        # Liabilities data
        liabilities = LiabilitySnapshot.objects.filter(user=request.user, month=month, year=year).select_related('lender', 'category')
        total_debt = liabilities.aggregate(t=Sum('remaining_principal'))['t'] or 0
        total_payment = liabilities.aggregate(t=Sum('monthly_payment'))['t'] or 0
        
        breakdown = []
        for l in liabilities:
            breakdown.append({
                "lender": l.lender.name if l.lender else "Unknown",
                "category": l.category.name if l.category else "Unknown",
                "remaining_principal": float(l.remaining_principal),
                "interest_rate": float(l.lender.interest_rate) if l.lender else 0,
                "monthly_payment": float(l.monthly_payment)
            })
            
        context_data['liabilities'] = {
            "total_debt": float(total_debt),
            "total_monthly_payment": float(total_payment),
            "breakdown": breakdown
        }

    if dashboard_type == 'BUDGETING' or dashboard_type == 'MAIN':
        # Budgeting data
        transactions = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
        total_income = transactions.filter(type='INCOME').aggregate(t=Sum('amount'))['t'] or 0
        total_expense = transactions.filter(type='EXPENSE').aggregate(t=Sum('amount'))['t'] or 0
        
        category_spending = {}
        for t in transactions.filter(type='EXPENSE').select_related('category'):
            cname = t.category.name if t.category else 'Uncategorized'
            category_spending[cname] = category_spending.get(cname, 0) + float(t.amount)
            
        context_data['budgeting'] = {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_cash_flow": float(total_income - total_expense),
            "category_spending": category_spending
        }
        
    # Query AI
    ai_response = generate_financial_insights(dashboard_type, context_data)

    # Save to cache
    cache, created = InsightCache.objects.update_or_create(
        user=request.user,
        dashboard_type=dashboard_type,
        month=month,
        year=year,
        defaults={
            'health_score': ai_response.get('health_score', 'N/A'),
            'recommendations': ai_response.get('recommendations', [])
        }
    )

    return Response({
        'health_score': cache.health_score,
        'recommendations': cache.recommendations,
        'cached': False,
        'updated_at': cache.updated_at
    })
