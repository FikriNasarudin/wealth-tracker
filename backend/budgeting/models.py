from django.db import models
from django.conf import settings

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

class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(TransactionCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.category.name if self.category else 'Uncategorized'} - {self.amount}"
