#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.core.cache import cache
from django.template.loader import get_template

def clear_template_cache():
    """Clear Django template cache"""
    try:
        # Clear Django cache
        cache.clear()
        print("Django cache cleared successfully!")
        
        # Force reload of base template
        try:
            get_template('base.html')
            print("Base template reloaded successfully!")
        except Exception as e:
            print(f"Template reload error: {e}")
            
    except Exception as e:
        print(f"Cache clear error: {e}")

if __name__ == '__main__':
    clear_template_cache()