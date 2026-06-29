import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
              AND table_name = %s
        """, [table_name])
        return cursor.fetchone()[0] > 0

def add_column_if_not_exists(table_name, column_name, column_def):
    if not table_exists(table_name):
        return
        
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
              AND table_name = %s 
              AND column_name = %s
        """, [table_name, column_name])
        if cursor.fetchone()[0] == 0:
            print(f"Adding {column_name} to {table_name}")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            except Exception as e:
                print(f"Error adding {column_name} to {table_name}: {e}")
        else:
            print(f"Column {column_name} already exists in {table_name}")

if __name__ == "__main__":
    print("Aligning budgeting schema to fix migration resets...")
    
    # Transaction
    add_column_if_not_exists("budgeting_transaction", "name", "VARCHAR(255) NULL")
    add_column_if_not_exists("budgeting_transaction", "type", "VARCHAR(10) NOT NULL DEFAULT 'EXPENSE'")
    add_column_if_not_exists("budgeting_transaction", "category_id", "BIGINT NULL")
    add_column_if_not_exists("budgeting_transaction", "subscription_id", "BIGINT NULL")
    add_column_if_not_exists("budgeting_transaction", "description", "LONGTEXT NULL")
    
    # Subscription
    add_column_if_not_exists("budgeting_subscription", "name", "VARCHAR(255) NULL")
    add_column_if_not_exists("budgeting_subscription", "type", "VARCHAR(10) NOT NULL DEFAULT 'EXPENSE'")
    add_column_if_not_exists("budgeting_subscription", "category_id", "BIGINT NULL")
    add_column_if_not_exists("budgeting_subscription", "status", "VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'")
    add_column_if_not_exists("budgeting_subscription", "billing_cycle", "VARCHAR(10) NOT NULL DEFAULT 'MONTHLY'")
    add_column_if_not_exists("budgeting_subscription", "start_date", "DATE NULL")
    add_column_if_not_exists("budgeting_subscription", "end_date", "DATE NULL")
    add_column_if_not_exists("budgeting_subscription", "auto_log_day", "INT NULL")
    add_column_if_not_exists("budgeting_subscription", "payment_account", "VARCHAR(255) NULL")
    add_column_if_not_exists("budgeting_subscription", "paused_months", "JSON NULL")
    
    # BudgetTarget
    add_column_if_not_exists("budgeting_budgettarget", "name", "VARCHAR(255) NULL")
    add_column_if_not_exists("budgeting_budgettarget", "type", "VARCHAR(10) NOT NULL DEFAULT 'EXPENSE'")
    add_column_if_not_exists("budgeting_budgettarget", "category_id", "BIGINT NULL")
    add_column_if_not_exists("budgeting_budgettarget", "status", "VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'")
    add_column_if_not_exists("budgeting_budgettarget", "start_date", "DATE NULL")
    add_column_if_not_exists("budgeting_budgettarget", "end_date", "DATE NULL")
    add_column_if_not_exists("budgeting_budgettarget", "paused_months", "JSON NULL")

    print("Schema alignment complete.")
