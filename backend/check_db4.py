import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.db.models import Sum
from liabilities.models import LiabilitySnapshot

qs = LiabilitySnapshot.objects.filter(month=5, year=2026)
print("Count:", qs.count())
print("Total Remaining:", qs.aggregate(total=Sum('remaining_principal'))['total'] or 0)
