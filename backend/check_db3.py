import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liabilities.models import LiabilitySnapshot
print("LIABILITIES:")
for s in LiabilitySnapshot.objects.all():
    print(f"ID: {s.id}, Cat: {s.category}, Lender: {s.lender}")
