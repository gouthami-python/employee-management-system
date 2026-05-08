#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Department, Role, Employee

# Create sample departments
hr_dept, created = Department.objects.get_or_create(
    name='Human Resources',
    defaults={'description': 'Manages employee relations and policies'}
)

it_dept, created = Department.objects.get_or_create(
    name='Information Technology',
    defaults={'description': 'Manages technology infrastructure'}
)

finance_dept, created = Department.objects.get_or_create(
    name='Finance',
    defaults={'description': 'Manages financial operations'}
)

# Create sample roles
manager_role, created = Role.objects.get_or_create(
    title='Manager',
    defaults={'description': 'Department manager', 'level': 3}
)

employee_role, created = Role.objects.get_or_create(
    title='Employee',
    defaults={'description': 'Regular employee', 'level': 1}
)

# Create admin employee profile if it doesn't exist
admin_user = User.objects.get(username='admin')
admin_employee, created = Employee.objects.get_or_create(
    user=admin_user,
    defaults={
        'employee_id': 'EMP0001',
        'department': hr_dept,
        'role': manager_role,
        'phone': '123-456-7890',
        'position': 'System Administrator',
        'is_manager': True,
        'salary': 75000.00
    }
)

print("Sample data created successfully!")
print("Admin credentials: username=admin, password=admin123")
print("You can now test the system with sample departments and roles.")