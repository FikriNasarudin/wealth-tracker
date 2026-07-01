from django.db import models
from django.conf import settings

class InsightCache(models.Model):
    DASHBOARD_CHOICES = [
        ('MAIN', 'Main Dashboard'),
        ('LIABILITIES', 'Liabilities Dashboard'),
        ('BUDGETING', 'Budgeting Dashboard'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insights')
    dashboard_type = models.CharField(max_length=20, choices=DASHBOARD_CHOICES)
    month = models.IntegerField()
    year = models.IntegerField()
    health_score = models.CharField(max_length=10)
    recommendations = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'dashboard_type', 'month', 'year')
        
    def __str__(self):
        return f"{self.user} - {self.dashboard_type} - {self.month}/{self.year}"
