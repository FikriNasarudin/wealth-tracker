import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from liabilities.models import LiabilitySnapshot

snaps = LiabilitySnapshot.objects.filter(category__name__iexact='credit cards')
for s in snaps:
    if s.remaining_principal == s.original_loan_amount:
        print(f"Fixing {s.lender.name if s.lender else 'Unknown'} snapshot: {s.remaining_principal} -> 0")
        s.remaining_principal = 0
        s.save()
print("Done fixing credit card snapshots.")
