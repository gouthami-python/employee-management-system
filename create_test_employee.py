#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee, Department

# Create a test employee
try:
    # Create user
    user = User.objects.create_user(
        username='testemployee',
        email='employee@test.com',
        password='test123',
        first_name='Test',
        last_name='Employee'
    )
    
    # Create employee profile
    employee = Employee.objects.create(
        user=user,
        employee_id='EMP0002',
        phone='123-456-7890',
        position='Software Developer',
        salary=50000.00
    )
    
    print("Test employee created successfully!")
    print("Username: testemployee")
    print("Password: test123")
    
except Exception as e:
    print(f"Error: {e}")
    print("Employee might already exist")