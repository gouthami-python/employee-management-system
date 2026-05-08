"""
Comprehensive tests for payroll module
"""
from decimal import Decimal
from django.test import TestCase, TransactionTestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Employee, Department, SalaryPayment, PayrollBatch, SalaryHistory, Bonus
from .payroll_service import PayrollService
from unittest.mock import Mock


class PayrollServiceTests(TransactionTestCase):
    """Test payroll service functionality"""
    
    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        
        # Create department
        self.dept = Department.objects.create(name='Engineering')
        
        # Create employees
        self.emp1_user = User.objects.create_user(
            username='emp1',
            first_name='John',
            last_name='Doe'
        )
        self.emp1 = Employee.objects.create(
            user=self.emp1_user,
            employee_id='EMP001',
            department=self.dept,
            salary=Decimal('5000.00')
        )
        
        self.emp2_user = User.objects.create_user(
            username='emp2',
            first_name='Jane',
            last_name='Smith'
        )
        self.emp2 = Employee.objects.create(
            user=self.emp2_user,
            employee_id='EMP002',
            department=self.dept,
            salary=Decimal('6000.00')
        )
        
        # Mock request
        self.mock_request = Mock()
        self.mock_request.META = {
            'REMOTE_ADDR': '127.0.0.1',
            'HTTP_USER_AGENT': 'Test Browser'
        }
    
    def test_bulk_payment_success(self):
        """Test successful bulk payment"""
        results = PayrollService.process_bulk_payment(
            employee_ids=[self.emp1.id, self.emp2.id],
            month=1,
            year=2024,
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertEqual(len(results['successful']), 2)
        self.assertEqual(len(results['failed']), 0)
        self.assertEqual(len(results['skipped']), 0)
        
        # Verify payments created
        payment1 = SalaryPayment.objects.get(employee=self.emp1, month=1, year=2024)
        self.assertEqual(payment1.amount, Decimal('5000.00'))
        self.assertEqual(payment1.status, 'paid')
        self.assertIsNotNone(payment1.idempotency_key)
        
        payment2 = SalaryPayment.objects.get(employee=self.emp2, month=1, year=2024)
        self.assertEqual(payment2.amount, Decimal('6000.00'))
    
    def test_duplicate_payment_prevention(self):
        """Test that duplicate payments are prevented"""
        # First payment
        results1 = PayrollService.process_bulk_payment(
            employee_ids=[self.emp1.id],
            month=1,
            year=2024,
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertEqual(len(results1['successful']), 1)
        
        # Attempt duplicate payment
        results2 = PayrollService.process_bulk_payment(
            employee_ids=[self.emp1.id],
            month=1,
            year=2024,
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertEqual(len(results2['successful']), 0)
        self.assertEqual(len(results2['skipped']), 1)
        
        # Verify only one payment exists
        payments = SalaryPayment.objects.filter(employee=self.emp1, month=1, year=2024)
        self.assertEqual(payments.count(), 1)
    
    def test_idempotency_key_uniqueness(self):
        """Test idempotency key prevents duplicates"""
        key1 = PayrollService.generate_idempotency_key(1, 1, 2024, 'BATCH123')
        key2 = PayrollService.generate_idempotency_key(1, 1, 2024, 'BATCH123')
        
        # Same parameters should generate same key
        self.assertEqual(key1, key2)
        
        # Different parameters should generate different keys
        key3 = PayrollService.generate_idempotency_key(2, 1, 2024, 'BATCH123')
        self.assertNotEqual(key1, key3)
    
    def test_batch_creation(self):
        """Test payroll batch creation"""
        batch = PayrollService.create_batch(1, 2024, self.admin, 'Test batch')
        
        self.assertIsNotNone(batch.batch_id)
        self.assertEqual(batch.month, 1)
        self.assertEqual(batch.year, 2024)
        self.assertEqual(batch.status, 'draft')
        self.assertEqual(batch.created_by, self.admin)
    
    def test_salary_update_with_history(self):
        """Test salary update creates history"""
        old_salary = self.emp1.salary
        new_salary = Decimal('5500.00')
        
        history = PayrollService.update_employee_salary(
            employee=self.emp1,
            new_salary=new_salary,
            reason='Annual increment',
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertIsNotNone(history)
        self.assertEqual(history.old_salary, old_salary)
        self.assertEqual(history.new_salary, new_salary)
        self.assertEqual(history.change_type, 'increment')
        
        # Verify employee salary updated
        self.emp1.refresh_from_db()
        self.assertEqual(self.emp1.salary, new_salary)
    
    def test_bonus_creation(self):
        """Test bonus creation"""
        bonus = PayrollService.add_bonus(
            employee=self.emp1,
            amount=Decimal('1000.00'),
            bonus_type='performance',
            reason='Excellent work',
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertEqual(bonus.employee, self.emp1)
        self.assertEqual(bonus.amount, Decimal('1000.00'))
        self.assertEqual(bonus.bonus_type, 'performance')
        self.assertEqual(bonus.given_by, self.admin)
    
    def test_payment_with_zero_salary(self):
        """Test payment fails for employee with zero salary"""
        emp3_user = User.objects.create_user(username='emp3')
        emp3 = Employee.objects.create(
            user=emp3_user,
            employee_id='EMP003',
            salary=Decimal('0.00')
        )
        
        results = PayrollService.process_bulk_payment(
            employee_ids=[emp3.id],
            month=1,
            year=2024,
            user=self.admin,
            request=self.mock_request
        )
        
        self.assertEqual(len(results['successful']), 0)
        self.assertEqual(len(results['failed']), 1)
    
    def test_concurrent_payment_prevention(self):
        """Test concurrent payment attempts are handled"""
        from threading import Thread
        
        def make_payment():
            PayrollService.process_bulk_payment(
                employee_ids=[self.emp1.id],
                month=2,
                year=2024,
                user=self.admin,
                request=self.mock_request
            )
        
        # Simulate concurrent requests
        thread1 = Thread(target=make_payment)
        thread2 = Thread(target=make_payment)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Only one payment should exist
        payments = SalaryPayment.objects.filter(employee=self.emp1, month=2, year=2024)
        self.assertEqual(payments.count(), 1)
    
    def test_batch_statistics(self):
        """Test batch tracks statistics correctly"""
        results = PayrollService.process_bulk_payment(
            employee_ids=[self.emp1.id, self.emp2.id],
            month=3,
            year=2024,
            user=self.admin,
            request=self.mock_request
        )
        
        batch = results['batch']
        self.assertEqual(batch.employee_count, 2)
        self.assertEqual(batch.successful_count, 2)
        self.assertEqual(batch.failed_count, 0)
        self.assertEqual(batch.total_amount, Decimal('11000.00'))
        self.assertEqual(batch.status, 'completed')


class PayrollViewTests(TestCase):
    """Test payroll views"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.dept = Department.objects.create(name='IT')
        
        emp_user = User.objects.create_user(username='emp1')
        self.emp = Employee.objects.create(
            user=emp_user,
            employee_id='EMP001',
            department=self.dept,
            salary=Decimal('5000.00')
        )
    
    def test_salary_management_access(self):
        """Test salary management requires admin"""
        # Without login
        response = self.client.get('/admin-panel/salary/')
        self.assertEqual(response.status_code, 302)
        
        # With admin login
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin-panel/salary/')
        self.assertEqual(response.status_code, 200)
    
    def test_bulk_payment_via_view(self):
        """Test bulk payment through view"""
        self.client.login(username='admin', password='admin123')
        
        response = self.client.post('/admin-panel/salary/', {
            'pay_salary': '1',
            'month': '1',
            'year': '2024',
            'employees': [self.emp.id]
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify payment created
        payment = SalaryPayment.objects.filter(employee=self.emp, month=1, year=2024).first()
        self.assertIsNotNone(payment)
    
    def test_csv_export(self):
        """Test CSV export"""
        # Create payment
        SalaryPayment.objects.create(
            employee=self.emp,
            amount=Decimal('5000.00'),
            month=1,
            year=2024,
            status='paid',
            idempotency_key='test-key-123',
            created_by=self.admin
        )
        
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin-panel/payroll/export-csv/?month=1&year=2024')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('payroll_1_2024.csv', response['Content-Disposition'])


class PayrollIntegrationTests(TransactionTestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.dept = Department.objects.create(name='Sales')
        
        # Create multiple employees
        for i in range(5):
            user = User.objects.create_user(
                username=f'emp{i}',
                first_name=f'Employee{i}'
            )
            Employee.objects.create(
                user=user,
                employee_id=f'EMP00{i}',
                department=self.dept,
                salary=Decimal(f'{3000 + i * 500}.00')
            )
    
    def test_full_payroll_cycle(self):
        """Test complete payroll cycle"""
        self.client.login(username='admin', password='admin123')
        
        # Get all employees
        employees = Employee.objects.all()
        employee_ids = [e.id for e in employees]
        
        # Process payroll
        response = self.client.post('/admin-panel/salary/', {
            'pay_salary': '1',
            'month': '1',
            'year': '2024',
            'employees': employee_ids
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify all payments created
        payments = SalaryPayment.objects.filter(month=1, year=2024)
        self.assertEqual(payments.count(), 5)
        
        # Verify batch created
        batch = PayrollBatch.objects.first()
        self.assertIsNotNone(batch)
        self.assertEqual(batch.successful_count, 5)
        
        # Test reports
        response = self.client.get('/admin-panel/payroll/reports/?month=1&year=2024')
        self.assertEqual(response.status_code, 200)
        
        # Test export
        response = self.client.get('/admin-panel/payroll/export-csv/?month=1&year=2024')
        self.assertEqual(response.status_code, 200)


# Payroll tests ready
