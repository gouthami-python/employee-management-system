#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create a test client
client = Client()

# Test home page
print("Testing home page...")
response = client.get('/')
print(f"Home page status: {response.status_code}")

# Test admin login page
print("Testing admin login page...")
response = client.get('/admin-login/')
print(f"Admin login page status: {response.status_code}")

# Test admin login with credentials
print("Testing admin login with credentials...")
response = client.post('/admin-login/', {
    'username': 'admin',
    'password': 'admin123'
})
print(f"Admin login POST status: {response.status_code}")
print(f"Redirect location: {response.get('Location', 'No redirect')}")

print("Admin login test completed!")