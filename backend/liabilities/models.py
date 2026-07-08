from django.db import models
from django.conf import settings

class LiabilityCategory(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='liability_categories')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Liability categories"

    def __str__(self):
        return self.name

class Lender(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='lenders')
    category = models.ForeignKey(LiabilityCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='lenders')
    original_loan_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_calculated_metrics(self, month, year, user):
        from decimal import Decimal
        manual_items = self.items.all()
        items_list = []
        is_credit_card = self.category and 'credit card' in self.category.name.lower()
        
        # Manual items
        for mi in manual_items:
            if mi.transaction_id or mi.subscription_id:
                continue
            items_list.append({
                'value': mi.value,
                'remaining': mi.calculate_remaining_balance(month, year),
                'monthly': mi.calculate_monthly_payment(month, year)
            })

        # Budgeting items if Credit Card
        if is_credit_card:
            try:
                from budgeting.models import Transaction, Subscription
                subs = Subscription.objects.filter(user=user, payment_account=self.name, status='ACTIVE')
                for sub in subs:
                    override = manual_items.filter(subscription_id=sub.id).first()
                    if override:
                        items_list.append({
                            'value': sub.amount,
                            'remaining': override.calculate_remaining_balance(month, year),
                            'monthly': override.calculate_monthly_payment(month, year)
                        })
                    else:
                        monthly_val = sub.amount if sub.billing_cycle == 'MONTHLY' else sub.amount / Decimal('12')
                        items_list.append({
                            'value': monthly_val,
                            'remaining': monthly_val,
                            'monthly': monthly_val
                        })
                txns = Transaction.objects.filter(user=user, payment_account=self.name, date__year=year, date__month=month)
                for txn in txns:
                    override = manual_items.filter(transaction_id=txn.id).first()
                    if override:
                        items_list.append({
                            'value': txn.amount,
                            'remaining': override.calculate_remaining_balance(month, year),
                            'monthly': override.calculate_monthly_payment(month, year)
                        })
                    else:
                        items_list.append({
                            'value': txn.amount,
                            'remaining': txn.amount,
                            'monthly': txn.amount
                        })
            except Exception:
                pass
                
        if not items_list:
            return None
            
        total_original = sum(item['value'] for item in items_list)
        if is_credit_card:
            total_original = self.original_loan_amount
            
        total_remaining = sum(item['remaining'] for item in items_list)
        total_monthly = sum(item['monthly'] for item in items_list)
        
        return {
            'original_loan_amount': total_original,
            'remaining_principal': total_remaining,
            'monthly_payment': total_monthly
        }

class LiabilitySnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='liability_snapshots')
    month = models.IntegerField()
    year = models.IntegerField()
    category = models.ForeignKey(LiabilityCategory, on_delete=models.SET_NULL, null=True)
    lender = models.ForeignKey(Lender, on_delete=models.SET_NULL, null=True)
    original_loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_principal = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'month', 'year', 'category', 'lender'], name='unique_liability_snapshot')
        ]
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
        ]

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year} - {self.category} - {self.lender}"

class LenderItem(models.Model):
    lender = models.ForeignKey(Lender, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_fixed_interest = models.BooleanField(default=True)
    transaction_id = models.IntegerField(null=True, blank=True)
    subscription_id = models.IntegerField(null=True, blank=True)

    def calculate_remaining_balance(self, month, year):
        import datetime
        from decimal import Decimal
        
        if not self.start_date or not self.end_date:
            return self.value

        start = self.start_date
        end = self.end_date
        target = datetime.date(year, month, 1)
        
        if target < start.replace(day=1):
            if self.is_fixed_interest:
                return self.value * (Decimal('1') + Decimal(str(self.interest_rate or 0)) / Decimal('100'))
            return self.value
            
        if target > end.replace(day=1):
            return Decimal('0')
            
        N = (end.year - start.year) * 12 + end.month - start.month
        if N <= 0:
            N = 1
            
        elapsed = (year - start.year) * 12 + month - start.month
        if elapsed < 0:
            elapsed = 0
            
        if self.is_fixed_interest:
            total_to_pay = self.value * (Decimal('1') + Decimal(str(self.interest_rate or 0)) / Decimal('100'))
            monthly = total_to_pay / Decimal(str(N))
            remaining = total_to_pay - Decimal(str(elapsed)) * monthly
            return max(Decimal('0'), remaining)
        else:
            r = Decimal(str(self.interest_rate or 0)) / Decimal('100') / Decimal('12')
            if r == 0:
                monthly = self.value / Decimal(str(N))
                remaining = self.value - Decimal(str(elapsed)) * monthly
                return max(Decimal('0'), remaining)
            else:
                try:
                    num = (1 + r)**N - (1 + r)**elapsed
                    den = (1 + r)**N - 1
                    remaining = self.value * Decimal(str(num)) / Decimal(str(den))
                    return max(Decimal('0'), remaining)
                except Exception:
                    monthly = self.value / Decimal(str(N))
                    remaining = self.value - Decimal(str(elapsed)) * monthly
                    return max(Decimal('0'), remaining)

    def calculate_monthly_payment(self, month, year):
        import datetime
        from decimal import Decimal
        
        if not self.start_date or not self.end_date:
            return Decimal('0')

        start = self.start_date
        end = self.end_date
        target = datetime.date(year, month, 1)
        
        if target < start.replace(day=1) or target > end.replace(day=1):
            return Decimal('0')
            
        N = (end.year - start.year) * 12 + end.month - start.month
        if N <= 0:
            N = 1
            
        if self.is_fixed_interest:
            total_to_pay = self.value * (Decimal('1') + Decimal(str(self.interest_rate or 0)) / Decimal('100'))
            return total_to_pay / Decimal(str(N))
        else:
            r = Decimal(str(self.interest_rate or 0)) / Decimal('100') / Decimal('12')
            if r == 0:
                return self.value / Decimal(str(N))
            else:
                try:
                    pmt = self.value * (r * (1 + r)**N) / ((1 + r)**N - 1)
                    return pmt
                except Exception:
                    return self.value / Decimal(str(N))

    def __str__(self):
        return f"{self.name} - {self.value}"
