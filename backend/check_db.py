import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from liabilities.models import LiabilitySnapshot
print("COUNT:", LiabilitySnapshot.objects.count())
for s in LiabilitySnapshot.objects.all():
    print(f"User: {s.user.username}, Month: {s.month}, Year: {s.year}, Remaining: {s.remaining_principal}")
