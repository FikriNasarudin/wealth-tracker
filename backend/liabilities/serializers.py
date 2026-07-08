from rest_framework import serializers
from .models import LiabilityCategory, Lender, LiabilitySnapshot, LenderItem
import datetime
from decimal import Decimal

try:
    from budgeting.models import Transaction, Subscription
except ImportError:
    Transaction = None
    Subscription = None

class LiabilityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LiabilityCategory
        fields = '__all__'
        extra_kwargs = {'user': {'read_only': True}}

class LenderItemSerializer(serializers.ModelSerializer):
    remaining_balance = serializers.SerializerMethodField()
    monthly_payment = serializers.SerializerMethodField()

    class Meta:
        model = LenderItem
        fields = [
            'id', 'lender', 'name', 'value', 'interest_rate', 
            'start_date', 'end_date', 'is_fixed_interest', 
            'transaction_id', 'subscription_id', 'remaining_balance', 'monthly_payment'
        ]

    def get_remaining_balance(self, obj):
        request = self.context.get('request')
        month = request.query_params.get('month') if request else None
        year = request.query_params.get('year') if request else None
        if not month or not year:
            today = datetime.date.today()
            month, year = today.month, today.year
        return obj.calculate_remaining_balance(int(month), int(year))

    def get_monthly_payment(self, obj):
        request = self.context.get('request')
        month = request.query_params.get('month') if request else None
        year = request.query_params.get('year') if request else None
        if not month or not year:
            today = datetime.date.today()
            month, year = today.month, today.year
        return obj.calculate_monthly_payment(int(month), int(year))

class LenderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    calculated_remaining_principal = serializers.SerializerMethodField()
    calculated_monthly_payment = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Lender
        fields = [
            'id', 'name', 'category', 'category_name', 'original_loan_amount', 'interest_rate', 
            'is_default', 'is_active', 'start_date', 'end_date', 'items', 
            'calculated_remaining_principal', 'calculated_monthly_payment', 'progress_percentage'
        ]
        extra_kwargs = {'user': {'read_only': True}}

    def _get_month_year(self):
        request = self.context.get('request')
        month = request.query_params.get('month') if request else None
        year = request.query_params.get('year') if request else None
        if not month or not year:
            today = datetime.date.today()
            return today.month, today.year
        return int(month), int(year)

    def get_items(self, obj):
        month, year = self._get_month_year()
        manual_items = LenderItem.objects.filter(lender=obj)
        items_list = []
        is_credit_card = obj.category and 'credit card' in obj.category.name.lower()
        
        # Map manual items
        for mi in manual_items:
            if mi.transaction_id or mi.subscription_id:
                continue
            items_list.append({
                'id': f"manual_{mi.id}",
                'db_id': mi.id,
                'type': 'manual',
                'name': mi.name,
                'value': mi.value,
                'interest_rate': mi.interest_rate,
                'start_date': mi.start_date,
                'end_date': mi.end_date,
                'is_fixed_interest': mi.is_fixed_interest,
                'remaining_balance': mi.calculate_remaining_balance(month, year),
                'monthly_payment': mi.calculate_monthly_payment(month, year)
            })

        # Map budgeting items
        if is_credit_card and Subscription is not None and Transaction is not None:
            # Recurring subs
            subs = Subscription.objects.filter(user=obj.user, payment_account=obj.name, status='ACTIVE')
            for sub in subs:
                override = manual_items.filter(subscription_id=sub.id).first()
                if override:
                    items_list.append({
                        'id': f"sub_{sub.id}",
                        'db_id': override.id,
                        'type': 'recurring',
                        'name': sub.name,
                        'value': sub.amount,
                        'interest_rate': override.interest_rate,
                        'start_date': override.start_date or sub.start_date,
                        'end_date': override.end_date or sub.end_date,
                        'is_fixed_interest': override.is_fixed_interest,
                        'remaining_balance': override.calculate_remaining_balance(month, year),
                        'monthly_payment': override.calculate_monthly_payment(month, year)
                    })
                else:
                    monthly_val = sub.amount if sub.billing_cycle == 'MONTHLY' else sub.amount / Decimal('12')
                    items_list.append({
                        'id': f"sub_{sub.id}",
                        'db_id': None,
                        'type': 'recurring',
                        'name': sub.name,
                        'value': monthly_val,
                        'interest_rate': Decimal('0'),
                        'start_date': sub.start_date,
                        'end_date': sub.end_date,
                        'is_fixed_interest': True,
                        'remaining_balance': monthly_val,
                        'monthly_payment': monthly_val
                    })

            # Non-recurring txns
            txns = Transaction.objects.filter(
                user=obj.user, 
                payment_account=obj.name,
                date__year=year,
                date__month=month
            )
            for txn in txns:
                override = manual_items.filter(transaction_id=txn.id).first()
                if override:
                    items_list.append({
                        'id': f"txn_{txn.id}",
                        'db_id': override.id,
                        'type': 'non-recurring',
                        'name': txn.name,
                        'value': txn.amount,
                        'interest_rate': override.interest_rate,
                        'start_date': override.start_date or txn.date,
                        'end_date': override.end_date or txn.date,
                        'is_fixed_interest': override.is_fixed_interest,
                        'remaining_balance': override.calculate_remaining_balance(month, year),
                        'monthly_payment': override.calculate_monthly_payment(month, year)
                    })
                else:
                    items_list.append({
                        'id': f"txn_{txn.id}",
                        'db_id': None,
                        'type': 'non-recurring',
                        'name': txn.name,
                        'value': txn.amount,
                        'interest_rate': Decimal('0'),
                        'start_date': txn.date,
                        'end_date': txn.date,
                        'is_fixed_interest': True,
                        'remaining_balance': txn.amount,
                        'monthly_payment': txn.amount
                    })
                    
        return items_list

    def get_calculated_remaining_principal(self, obj):
        month, year = self._get_month_year()
        items = self.get_items(obj)
        is_credit_card = obj.category and 'credit card' in obj.category.name.lower()
        if is_credit_card and not items:
            snap = LiabilitySnapshot.objects.filter(user=obj.user, lender=obj, month=month, year=year).first()
            if snap:
                return snap.remaining_principal
            return Decimal('0')
        return sum(item['remaining_balance'] for item in items)

    def get_calculated_monthly_payment(self, obj):
        month, year = self._get_month_year()
        items = self.get_items(obj)
        is_credit_card = obj.category and 'credit card' in obj.category.name.lower()
        if is_credit_card and not items:
            snap = LiabilitySnapshot.objects.filter(user=obj.user, lender=obj, month=month, year=year).first()
            if snap:
                return snap.monthly_payment
            return Decimal('0')
        return sum(item['monthly_payment'] for item in items)

    def get_progress_percentage(self, obj):
        items = self.get_items(obj)
        if not items:
            return 0.0
        total_value = sum(item['value'] for item in items)
        if total_value == 0:
            return 100.0
        total_remaining = sum(item['remaining_balance'] for item in items)
        progress = ((total_value - total_remaining) / total_value) * 100
        return round(float(max(0.0, min(100.0, progress))), 2)

class LiabilitySnapshotSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    lender_name = serializers.CharField(source='lender.name', read_only=True)
    debt_reduced = serializers.SerializerMethodField()

    class Meta:
        model = LiabilitySnapshot
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'category': {'required': False},
            'original_loan_amount': {'required': False},
            'remaining_principal': {'required': False}
        }

    def get_debt_reduced(self, obj):
        return obj.original_loan_amount - obj.remaining_principal
