from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class TransactionCategory(models.Model):
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='transaction_categories')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.type})"


class Subscription(models.Model):
    BILLING_CHOICES = (
        ('MONTHLY', 'Monthly'),
        ('YEARLY', 'Yearly'),
    )
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EXPENSE')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES, default='MONTHLY')
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], default='ACTIVE')
    
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    auto_log_day = models.IntegerField(blank=True, null=True)
    payment_account = models.CharField(max_length=255, blank=True, null=True)
    paused_months = models.JSONField(blank=True, null=True) # store ["2026-06", "2026-07"]

    def __str__(self):
        return f"{self.name} - {self.amount} ({self.billing_cycle})"


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EXPENSE')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')

    def __str__(self):
        return f"{self.user} - {self.name} - {self.amount}"


class BudgetTarget(models.Model):
    TYPE_CHOICES = (
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_targets')
    
    # Target can be on a category OR a specific name
    category = models.ForeignKey(TransactionCategory, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='EXPENSE')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=[('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], default='ACTIVE')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    paused_months = models.JSONField(blank=True, null=True)

    def clean(self):
        if not self.category and not self.name:
            raise ValidationError("Target must have either a category or a name.")
        if self.category and self.name:
            raise ValidationError("Target cannot have both a category and a name.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        target_entity = self.category.name if self.category else self.name
        return f"{self.user} - {target_entity} Target: {self.amount}"
