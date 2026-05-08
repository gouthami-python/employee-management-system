#!/usr/bin/env python
import os
import sys
import subprocess
import time

def restart_server():
    print("Stopping any existing Django processes...")
    try:
        # Kill any existing python processes (Windows)
        subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass
    
    print("Starting Django development server...")
    os.system('python manage.py runserver')

if __name__ == '__main__':
    restart_server()