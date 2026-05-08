#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

def create_admin_profile():
    try:
        admin_user = User.objects.get(username='admin')
        if not hasattr(admin_user, 'employee'):
            Employee.objects.create(
                user=admin_user,
                employee_id='ADMIN001',
                phone='1234567890',
                position='Administrator',
                is_manager=True,
                salary=100000.00
            )
            print('Admin employee profile created successfully!')
        else:
            print('Admin already has employee profile')
    except User.DoesNotExist:
        print('Admin user not found')

if __name__ == '__main__':
    create_admin_profile()