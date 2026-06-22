import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from investments.models import InvestmentSnapshot
print("INVESTMENTS:")
for s in InvestmentSnapshot.objects.all():
    print(f"User: {s.user.username}, Month: {s.month}, Year: {s.year}, Balance: {s.current_balance}")
