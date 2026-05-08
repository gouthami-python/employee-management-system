"""
Quick script to add bank accounts for all employees
Run: python manage.py shell < add_bank_accounts.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from employees.models import Employee, BankAccount
from django.utils import timezone

# Sample bank names
banks = ['Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank', 'US Bank']
routing_codes = ['021000021', '026009593', '121000248', '021000089', '042000013']

count = 0
for emp in Employee.objects.all():
    if not hasattr(emp, 'bank_account'):
        bank_index = emp.id % len(banks)
        
        bank = BankAccount.objects.create(
            employee=emp,
            account_holder_name=emp.user.get_full_name(),
            bank_name=banks[bank_index],
            branch_name=f"{banks[bank_index]} Main Branch",
            routing_code=routing_codes[bank_index],
            account_type='checking',
            verification_status='verified',  # Auto-verify for demo
            verification_date=timezone.now(),
            verification_method='manual',
            consent_given=True,
            consent_date=timezone.now(),
        )
        
        # Set encrypted account number
        account_num = f"{emp.id:04d}567890"
        bank.set_account_number(account_num)
        bank.save()
        
        count += 1
        print(f"Added bank account for {emp.user.get_full_name()} - {bank.get_masked_account()}")

print(f"\nTotal: {count} bank accounts added!")
print(f"All accounts marked as VERIFIED for demo purposes")
