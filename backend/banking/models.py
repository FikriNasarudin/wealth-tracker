from django.db import models
from django.conf import settings

class AccountType(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_types')
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='unique_user_account_type')
        ]

    def __str__(self):
        return self.name

class BankAccount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_accounts')
    name = models.CharField(max_length=255)
    institution = models.CharField(max_length=255, blank=True, null=True)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts')
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
