import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from liabilities.models import LiabilitySnapshot

for s in LiabilitySnapshot.objects.all():
    print(f"Lender: {s.lender.name if s.lender else 'None'}, Limit/Orig: {s.original_loan_amount}, Remaining: {s.remaining_principal}, Cat: {s.category.name if s.category else 'None'}")
