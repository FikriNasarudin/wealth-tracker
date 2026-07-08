from django.db import migrations

def clean_and_map_categories(apps, schema_editor):
    LiabilityCategory = apps.get_model('liabilities', 'LiabilityCategory')
    Lender = apps.get_model('liabilities', 'Lender')
    LiabilitySnapshot = apps.get_model('liabilities', 'LiabilitySnapshot')
    
    pay_later, _ = LiabilityCategory.objects.get_or_create(name='Pay Later', is_default=True, defaults={'user': None})
    loan, _ = LiabilityCategory.objects.get_or_create(name='Loan', is_default=True, defaults={'user': None})
    credit_card, _ = LiabilityCategory.objects.get_or_create(name='Credit Card', is_default=True, defaults={'user': None})
    
    for cat in LiabilityCategory.objects.all():
        if cat.is_default:
            continue
            
        cat_name_lower = cat.name.lower()
        if 'credit card' in cat_name_lower:
            target = credit_card
        elif 'pay later' in cat_name_lower or 'bnpl' in cat_name_lower:
            target = pay_later
        else:
            target = loan
            
        Lender.objects.filter(category=cat).update(category=target)
        LiabilitySnapshot.objects.filter(category=cat).update(category=target)
        
    LiabilityCategory.objects.filter(is_default=False).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('liabilities', '0007_lenderitem'),
    ]

    operations = [
        migrations.RunPython(clean_and_map_categories),
    ]
