import requests
import time

print("Testing HTTP request logging...")

# Test home page
print("1. Testing home page...")
response = requests.get('http://127.0.0.1:8000/')
print(f"Home page status: {response.status_code}")
time.sleep(1)

# Test admin login page
print("2. Testing admin login page...")
response = requests.get('http://127.0.0.1:8000/admin-login/')
print(f"Admin login page status: {response.status_code}")
time.sleep(1)

# Test employee login page
print("3. Testing employee login page...")
response = requests.get('http://127.0.0.1:8000/employee-login/')
print(f"Employee login page status: {response.status_code}")

print("Test completed. Check Django terminal for request logs.")