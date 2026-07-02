from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db.models import Sum, F
from django.db.models.query_utils import Q
from decimal import Decimal
from .models import TransactionCategory, Transaction, BudgetTarget, Subscription
from .serializers import TransactionCategorySerializer, TransactionSerializer, BudgetTargetSerializer, SubscriptionSerializer

class TransactionCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionCategory.objects.filter(Q(user=self.request.user) | Q(is_default=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.is_default:
            raise ValidationError("Cannot modify default categories.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.is_default:
            raise ValidationError("Cannot delete default categories.")
        instance.delete()

class BudgetTargetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetTargetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BudgetTarget.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def pause_month(self, request, pk=None):
        target = self.get_object()
        month_str = request.data.get('month')
        if not month_str:
            return Response({'error': 'month required'}, status=400)
        
        paused = target.paused_months or []
        if month_str not in paused:
            paused.append(month_str)
            target.paused_months = paused
            target.save()
        return Response({'status': 'paused', 'paused_months': paused})

    @action(detail=True, methods=['post'])
    def resume_month(self, request, pk=None):
        target = self.get_object()
        month_str = request.data.get('month')
        if not month_str:
            return Response({'error': 'month required'}, status=400)
        
        paused = target.paused_months or []
        if month_str in paused:
            paused.remove(month_str)
            target.paused_months = paused
            target.save()
        return Response({'status': 'resumed', 'paused_months': paused})
        
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        target = self.get_object()
        target.status = 'ARCHIVED'
        target.save()
        return Response({'status': 'archived'})


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def log_month(self, request, pk=None):
        import datetime
        subscription = self.get_object()
        month_str = request.data.get('month')
        if not month_str:
            return Response({'error': 'month required'}, status=400)
            
        y_str, m_str = month_str.split('-')
        year, month = int(y_str), int(m_str)
        
        dt = datetime.date(year, month, 1)
        if Transaction.objects.filter(subscription=subscription, date__year=year, date__month=month).exists():
            return Response({'error': 'Already logged'}, status=400)
            
        txn = Transaction.objects.create(
            user=request.user,
            category=subscription.category,
            name=subscription.name,
            type=subscription.type,
            subscription=subscription,
            amount=subscription.amount,
            date=dt,
            description=f"{subscription.name} (Recurring)" + (f" - Account: {subscription.payment_account}" if subscription.payment_account else "")
        )
        return Response({'status': 'logged', 'transaction_id': txn.id})

    @action(detail=True, methods=['post'])
    def pause_month(self, request, pk=None):
        subscription = self.get_object()
        month_str = request.data.get('month')
        if not month_str:
            return Response({'error': 'month required'}, status=400)
        
        paused = subscription.paused_months or []
        if month_str not in paused:
            paused.append(month_str)
            subscription.paused_months = paused
            subscription.save()
        return Response({'status': 'paused', 'paused_months': paused})

    @action(detail=True, methods=['post'])
    def resume_month(self, request, pk=None):
        subscription = self.get_object()
        month_str = request.data.get('month')
        if not month_str:
            return Response({'error': 'month required'}, status=400)
        
        paused = subscription.paused_months or []
        if month_str in paused:
            paused.remove(month_str)
            subscription.paused_months = paused
            subscription.save()
        return Response({'status': 'resumed', 'paused_months': paused})
        
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'ARCHIVED'
        subscription.save()
        return Response({'status': 'archived'})


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
        
        if month and year:
            import datetime
            import calendar
            
            req_y = int(year)
            req_m = int(month)
            month_str = f"{req_y}-{req_m:02d}"
            today = datetime.date.today()
            
            period_start = datetime.date(req_y, req_m, 1)
            days_in_month = calendar.monthrange(req_y, req_m)[1]
            period_end = datetime.date(req_y, req_m, days_in_month)
            
            subs = Subscription.objects.filter(user=request.user, status='ACTIVE', auto_log_day__isnull=False)
            for s in subs:
                should_log = False
                if req_y < today.year or (req_y == today.year and req_m < today.month):
                    should_log = True
                elif req_y == today.year and req_m == today.month and today.day >= s.auto_log_day:
                    should_log = True
                    
                if should_log:
                    if month_str not in (s.paused_months or []):
                        if not (s.start_date and s.start_date > period_end):
                            if not (s.end_date and s.end_date < period_start):
                                logged = Transaction.objects.filter(
                                    user=request.user, 
                                    subscription=s,
                                    date__year=req_y,
                                    date__month=req_m
                                ).exists()
                                if not logged:
                                    log_day = min(s.auto_log_day, days_in_month)
                                    Transaction.objects.create(
                                        user=request.user,
                                        category=s.category,
                                        name=s.name,
                                        type=s.type,
                                        subscription=s,
                                        amount=s.amount,
                                        date=datetime.date(req_y, req_m, log_day),
                                        description=f"Auto-logged: {s.name}" + (f" (Account: {s.payment_account})" if s.payment_account else ""),
                                        payment_account=s.payment_account
                                    )

        qs = self.get_queryset()
        if month and year:
            qs = qs.filter(date__month=month, date__year=year)
            
        income = qs.filter(type='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        expenses = qs.filter(type='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        
        # We will build the breakdowns strictly based on active targets.
        # But we still need to calculate the raw income/expenses totals from the DB.
        
        targets_qs = BudgetTarget.objects.filter(user=request.user).select_related('category')
        
        active_targets = []
        for t in targets_qs:
            if t.status == 'ARCHIVED':
                continue
            if month and year:
                y_int = int(year)
                m_int = int(month)
                month_str = f"{y_int}-{m_int:02d}"
                
                import datetime
                import calendar
                period_start = datetime.date(y_int, m_int, 1)
                days_in_month = calendar.monthrange(y_int, m_int)[1]
                period_end = datetime.date(y_int, m_int, days_in_month)
                
                if month_str in (t.paused_months or []):
                    continue
                if t.start_date and t.start_date > period_end:
                    continue
                if t.end_date and t.end_date < period_start:
                    continue
            active_targets.append(t)
            
        forecast_income = sum(t.amount for t in active_targets if t.type == 'INCOME')
        forecast_expenses = sum(t.amount for t in active_targets if t.type == 'EXPENSE')
            
        recent_transactions = TransactionSerializer(
            qs.order_by('-date', '-id')[:5], many=True
        ).data

        subs = Subscription.objects.filter(user=request.user, status='ACTIVE').select_related('category')
        monthly_fixed_costs = Decimal('0.00')
        monthly_fixed_income = Decimal('0.00')
        logged_sub_ids = set()

        if month and year:
            import datetime
            import calendar
            
            y_int = int(year)
            m_int = int(month)
            month_str = f"{y_int}-{m_int:02d}"
            
            period_start = datetime.date(y_int, m_int, 1)
            days_in_month = calendar.monthrange(y_int, m_int)[1]
            period_end = datetime.date(y_int, m_int, days_in_month)

            logged_sub_ids = set(Transaction.objects.filter(
                user=request.user, 
                subscription__isnull=False, 
                date__year=y_int, 
                date__month=m_int
            ).values_list('subscription_id', flat=True))
            
            all_subs = list(subs)  # keep full list for budget limit computation
            active_subs = []
            for s in subs:
                paused = s.paused_months or []
                if s.id in logged_sub_ids or month_str in paused:
                    continue
                
                if s.start_date and s.start_date > period_end:
                    continue
                if s.end_date and s.end_date < period_start:
                    continue
                    
                active_subs.append(s)
            subs = active_subs
        else:
            all_subs = list(subs)

        for s in subs:
            monthly_amt = s.amount if s.billing_cycle == 'MONTHLY' else s.amount / Decimal('12.0')
            if s.type == 'INCOME':
                monthly_fixed_income += monthly_amt
                income += monthly_amt
            else:
                monthly_fixed_costs += monthly_amt
                expenses += monthly_amt

        # Now build the target breakdowns
        expense_breakdown = []
        income_breakdown = []
        
        for t in active_targets:
            if t.category_id:
                txn_sum = qs.filter(type=t.type, category_id=t.category_id).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            elif t.name:
                txn_sum = qs.filter(type=t.type, name__iexact=t.name).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            else:
                txn_sum = Decimal('0.00')
                
            sub_sum = Decimal('0.00')
            for s in subs:
                if s.type == t.type:
                    monthly_amt = s.amount if s.billing_cycle == 'MONTHLY' else s.amount / Decimal('12.0')
                    if t.category_id and s.category_id == t.category_id:
                        sub_sum += monthly_amt
                    elif t.name and s.name.lower() == t.name.lower():
                        sub_sum += monthly_amt
                        
            total_amt = txn_sum + sub_sum
            cname = t.category.name if t.category else t.name
            
            entry = {
                'category_id': t.category_id or t.name,
                'category': cname,
                'amount': total_amt,
                'weight_percentage': 0, # will calculate below
                'budget_limit': t.amount
            }
            
            if t.type == 'INCOME':
                income_breakdown.append(entry)
            else:
                expense_breakdown.append(entry)

        # --- Default entries: recurring subs with no explicit target ---
        # Collect category_ids already covered by explicit targets
        covered_expense_cats = set(t.category_id for t in active_targets if t.type == 'EXPENSE' and t.category_id)
        covered_expense_names = set(t.name.lower() for t in active_targets if t.type == 'EXPENSE' and t.name)
        covered_income_cats  = set(t.category_id for t in active_targets if t.type == 'INCOME' and t.category_id)
        covered_income_names = set(t.name.lower() for t in active_targets if t.type == 'INCOME' and t.name)

        # Aggregate uncovered subs by category
        default_expense_cats = {}  # category_id -> {name, total}
        default_income_cats  = {}

        for s in all_subs:
            monthly_amt = s.amount if s.billing_cycle == 'MONTHLY' else s.amount / Decimal('12.0')
            if s.type == 'EXPENSE':
                if s.category_id and s.category_id not in covered_expense_cats:
                    if s.category_id not in default_expense_cats:
                        default_expense_cats[s.category_id] = {'name': s.category.name if s.category else 'Uncategorized', 'total': Decimal('0.00')}
                    default_expense_cats[s.category_id]['total'] += monthly_amt
            else:
                if s.category_id and s.category_id not in covered_income_cats:
                    if s.category_id not in default_income_cats:
                        default_income_cats[s.category_id] = {'name': s.category.name if s.category else 'Uncategorized', 'total': Decimal('0.00')}
                    default_income_cats[s.category_id]['total'] += monthly_amt

        for cat_id, info in default_expense_cats.items():
            txn_sum = qs.filter(type='EXPENSE', category_id=cat_id).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            total_amt = txn_sum + info['total']
            expense_breakdown.append({
                'category_id': cat_id,
                'category': info['name'],
                'amount': total_amt,
                'weight_percentage': 0,
                'budget_limit': info['total'],
                'budget_source': 'default',
            })

        for cat_id, info in default_income_cats.items():
            txn_sum = qs.filter(type='INCOME', category_id=cat_id).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            total_amt = txn_sum + info['total']
            income_breakdown.append({
                'category_id': cat_id,
                'category': info['name'],
                'amount': total_amt,
                'weight_percentage': 0,
                'budget_limit': info['total'],
                'budget_source': 'default',
            })

        # Re-calculate weights
        for b in income_breakdown:
            b['weight_percentage'] = round((b['amount'] / income * 100) if income > 0 else 0, 2)
        for b in expense_breakdown:
            b['weight_percentage'] = round((b['amount'] / expenses * 100) if expenses > 0 else 0, 2)

        # Include default targets in forecasts
        forecast_expenses += sum(info['total'] for info in default_expense_cats.values())
        forecast_income += sum(info['total'] for info in default_income_cats.values())

        return Response({
            'total_income': income,
            'total_expenses': expenses,
            'forecast_income': forecast_income,
            'forecast_expenses': forecast_expenses,
            'monthly_fixed_costs': monthly_fixed_costs,
            'monthly_fixed_income': monthly_fixed_income,
            'net_cash_flow': income - expenses,
            'expense_breakdown': expense_breakdown,
            'income_breakdown': income_breakdown,
            'recent_transactions': recent_transactions,
            'logged_subscription_ids': list(logged_sub_ids),
            'targets': BudgetTargetSerializer(active_targets, many=True).data
        })

    @action(detail=False, methods=['get'])
    def trend(self, request):
        import datetime
        import calendar
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        year_str = request.query_params.get('year')
        
        today = datetime.date.today()
        
        if start_date_str and end_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m').date().replace(day=1)
                    temp_end = datetime.datetime.strptime(end_date_str, '%Y-%m').date()
                    days_in_month = calendar.monthrange(temp_end.year, temp_end.month)[1]
                    end_date = temp_end.replace(day=days_in_month)
                except ValueError:
                    start_date = None
                    end_date = None
        elif year_str:
            try:
                yr = int(year_str)
                start_date = datetime.date(yr, 1, 1)
                end_date = datetime.date(yr, 12, 31)
            except ValueError:
                start_date = None
                end_date = None
        else:
            start_date = datetime.date(today.year, 1, 1)
            end_date = datetime.date(today.year, 12, 31)
            
        if not start_date or not end_date:
            start_date = datetime.date(today.year, 1, 1)
            end_date = datetime.date(today.year, 12, 31)

        qs = self.get_queryset().filter(date__gte=start_date, date__lte=end_date)
        
        trend_data = {}
        curr = start_date.replace(day=1)
        months_list = []
        while curr <= end_date:
            key = curr.strftime('%b %Y')
            month_key = curr.strftime('%Y-%m')
            
            period_start = curr
            days_in_month = calendar.monthrange(curr.year, curr.month)[1]
            period_end = curr.replace(day=days_in_month)
            
            trend_data[key] = {
                'income': 0, 'expense': 0, 'label': key, 
                '_year': curr.year, '_month': curr.month, 
                '_start': period_start, '_end': period_end, '_month_key': month_key
            }
            months_list.append(key)
            # increment to next month safely
            if curr.month == 12:
                curr = curr.replace(year=curr.year + 1, month=1)
            else:
                curr = curr.replace(month=curr.month + 1)

        for txn in qs:
            key = txn.date.strftime('%b %Y')
            if key in trend_data:
                if txn.type == 'INCOME':
                    trend_data[key]['income'] += txn.amount
                elif txn.type == 'EXPENSE':
                    trend_data[key]['expense'] += txn.amount

        subs = Subscription.objects.filter(user=request.user, status='ACTIVE')
        for key in months_list:
            m_data = trend_data[key]
            
            logged_sub_ids = set(Transaction.objects.filter(
                user=request.user, 
                subscription__isnull=False, 
                date__year=m_data['_year'], 
                date__month=m_data['_month']
            ).values_list('subscription_id', flat=True))
            
            for s in subs:
                if s.id in logged_sub_ids or m_data['_month_key'] in (s.paused_months or []):
                    continue
                if s.start_date and s.start_date > m_data['_end']:
                    continue
                if s.end_date and s.end_date < m_data['_start']:
                    continue
                    
                monthly_amt = s.amount if s.billing_cycle == 'MONTHLY' else s.amount / Decimal('12.0')
                if s.type == 'INCOME':
                    m_data['income'] += monthly_amt
                else:
                    m_data['expense'] += monthly_amt
                    
            del m_data['_year'], m_data['_month'], m_data['_start'], m_data['_end'], m_data['_month_key']

        return Response(list(trend_data.values()))
