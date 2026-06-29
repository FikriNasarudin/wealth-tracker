from django.db import models
from django.conf import settings

class BankAccount(models.Model):
    ACCOUNT_TYPES = (
        ('CHECKING', 'Checking'),
        ('SAVINGS', 'Savings'),
        ('CASH', 'Cash'),
        ('OTHER', 'Other'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='CHECKING')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.institution})" if self.institution else self.name

class BankAccountSnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_account_snapshots')
    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='snapshots')
    month = models.IntegerField()
    year = models.IntegerField()
    balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'account', 'month', 'year'], name='unique_bank_snapshot')
        ]
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
        ]

    def __str__(self):
        return f"{self.account.name} - {self.month}/{self.year}: {self.balance}"
