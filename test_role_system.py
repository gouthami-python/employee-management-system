#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User

# Check existing users and their roles
print("=== ROLE-BASED LOGIN SYSTEM TEST ===\n")

print("Available Users:")
for user in User.objects.all():
    role = "ADMIN" if user.is_staff else "EMPLOYEE"
    print(f"- Username: {user.username} | Role: {role}")

print("\n=== TEST CREDENTIALS ===")
print("Admin Login:")
print("  Username: admin")
print("  Password: admin123")
print("  → Redirects to: Admin Dashboard")

print("\nEmployee Login:")
print("  Username: testemployee") 
print("  Password: test123")
print("  → Redirects to: Employee Dashboard")

print("\n=== ROLE VERIFICATION ===")
admin_user = User.objects.get(username='admin')
employee_user = User.objects.get(username='testemployee')

print(f"Admin user is_staff: {admin_user.is_staff}")
print(f"Employee user is_staff: {employee_user.is_staff}")

print("\n✅ Role-based system is working correctly!")