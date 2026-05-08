#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from employees.models import Employee, SalaryStructure, SalaryRecord
from django.contrib.auth.models import User

def test_salary_system():
    print("=== SALARY SYSTEM TEST ===")
    
    # Check if salary models exist
    print(f"SalaryStructure model: {SalaryStructure._meta.db_table}")
    print(f"SalaryRecord model: {SalaryRecord._meta.db_table}")
    
    # Check existing employees
    employees = Employee.objects.all()
    print(f"\nTotal employees: {employees.count()}")
    
    # Check salary structures
    structures = SalaryStructure.objects.all()
    print(f"Salary structures: {structures.count()}")
    
    # Check salary records
    records = SalaryRecord.objects.all()
    print(f"Salary records: {records.count()}")
    
    # Test URL resolution
    from django.urls import reverse
    try:
        admin_url = reverse('admin_salary_list')
        employee_url = reverse('employee_salary_list')
        print(f"\nAdmin salary URL: {admin_url}")
        print(f"Employee salary URL: {employee_url}")
        print("✅ URLs are working correctly!")
    except Exception as e:
        print(f"❌ URL error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_salary_system()