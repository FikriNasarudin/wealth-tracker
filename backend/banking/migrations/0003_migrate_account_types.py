from django.db import migrations

def migrate_account_types(apps, schema_editor):
    BankAccount = apps.get_model('banking', 'BankAccount')
    AccountType = apps.get_model('banking', 'AccountType')

    # Iterate over all bank accounts
    for account in BankAccount.objects.all():
        old_type = account.type  # e.g. CHECKING, SAVINGS, CASH, OTHER
        
        # Map uppercase codes to user-friendly titles
        name_map = {
            'CHECKING': 'Checking',
            'SAVINGS': 'Savings',
            'CASH': 'Cash',
            'OTHER': 'Other',
        }
        type_name = name_map.get(old_type, old_type.title() if old_type else 'Other')

        # Get or create AccountType for this user and name
        account_type, created = AccountType.objects.get_or_create(
            user=account.user,
            name=type_name,
            defaults={'is_active': True}
        )

        account.account_type = account_type
        account.save()

class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0002_accounttype_bankaccount_account_type_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_account_types),
    ]
