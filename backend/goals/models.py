from django.db import models
from django.conf import settings

class FinancialGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_date = models.DateField(blank=True, null=True)
    color = models.CharField(max_length=20, default='#3B82F6') # Default blue
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"
