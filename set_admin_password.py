#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth.models import User

# Set admin password
admin_user = User.objects.get(username='admin')
admin_user.set_password('admin123')
admin_user.save()

print("Admin password set to: admin123")