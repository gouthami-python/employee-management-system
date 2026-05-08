#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

# Create test employee
try:
    user = User.objects.create_user(
        username='employee1',
        email='employee1@test.com',
        password='emp123',
        first_name='John',
        last_name='Doe'
    )
    
    employee = Employee.objects.create(
        user=user,
        employee_id='EMP1001',
        phone='555-0123',
        position='Developer',
        salary=45000.00
    )
    
    print("Employee created successfully!")
    print("Username: employee1")
    print("Password: emp123")
    
except Exception as e:
    print(f"Error: {e}")