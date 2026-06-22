from django.db import models
from django.conf import settings

class InvestmentCategory(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='investment_categories')
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Investment categories"

    def __str__(self):
        return self.name

class InvestmentPlatform(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='investment_platforms')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class InvestmentSnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='investment_snapshots')
    month = models.IntegerField()
    year = models.IntegerField()
    category = models.ForeignKey(InvestmentCategory, on_delete=models.SET_NULL, null=True)
    platform = models.ForeignKey(InvestmentPlatform, on_delete=models.SET_NULL, null=True)
    total_invested = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'month', 'year', 'category', 'platform'], name='unique_investment_snapshot')
        ]
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
        ]

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year} - {self.category} - {self.platform}"
