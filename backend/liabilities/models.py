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
